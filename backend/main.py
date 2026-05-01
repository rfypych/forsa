from fastapi import FastAPI, UploadFile, File, HTTPException, Depends, Form
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sqlalchemy.orm import Session
import uvicorn
import re
import datetime

from services.apk_analyzer import extract_apk_info
from services.url_analyzer import extract_url_info
from services.groq_service import analyze_threat
from database import get_db, Conversation, Message

app = FastAPI(title="Cyber-Threat Sandbox Bot API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ─── Models ──────────────────────────────────────────────────────────────────

class URLRequest(BaseModel):
    url: str
    user_message: str = None
    conversation_id: int = None

class ChatMessageItem(BaseModel):
    role: str
    content: str

class ChatRequest(BaseModel):
    message: str
    history: list[ChatMessageItem] = []
    conversation_id: int = None

# ─── Helpers ────────────────────────────────────────────────────────────────

def determine_status(analysis_text: str):
    if "[BERBAHAYA]" in analysis_text: return "BERBAHAYA"
    if "[WASPADA]" in analysis_text: return "WASPADA"
    return "AMAN"

def save_message(db: Session, conversation_id: int, role: str, msg_type: str, content: str = None, threat_data: dict = None):
    msg = Message(
        conversation_id=conversation_id,
        role=role,
        type=msg_type,
        content=content,
        threat_data=threat_data
    )
    db.add(msg)
    db.commit()
    db.refresh(msg)
    return msg

# ─── Endpoints ──────────────────────────────────────────────────────────────

@app.get("/")
def read_root():
    return {"message": "Cyber-Threat Sandbox Bot API is running."}

@app.post("/api/conversations")
async def create_conversation(title: str = "Pesan Baru", db: Session = Depends(get_db)):
    conv = Conversation(title=title)
    db.add(conv)
    db.commit()
    db.refresh(conv)
    return conv

@app.get("/api/conversations")
async def list_conversations(db: Session = Depends(get_db)):
    return db.query(Conversation).order_by(Conversation.created_at.desc()).all()

@app.get("/api/conversations/{conv_id}")
async def get_conversation(conv_id: int, db: Session = Depends(get_db)):
    conv = db.query(Conversation).filter(Conversation.id == conv_id).first()
    if not conv:
        raise HTTPException(status_code=404, detail="Percakapan tidak ditemukan.")
    
    # Return conversation details and all messages
    messages = db.query(Message).filter(Message.conversation_id == conv_id).order_by(Message.timestamp.asc()).all()
    return {
        "id": conv.id,
        "title": conv.title,
        "created_at": conv.created_at,
        "messages": messages
    }

@app.delete("/api/conversations/{conv_id}")
async def delete_conversation(conv_id: int, db: Session = Depends(get_db)):
    conv = db.query(Conversation).filter(Conversation.id == conv_id).first()
    if not conv:
        raise HTTPException(status_code=404, detail="Percakapan tidak ditemukan.")
    db.delete(conv)
    db.commit()
    return {"success": True}

@app.post("/api/analyze/apk")
async def analyze_apk(
    file: UploadFile = File(...), 
    user_message: str = Form(None),
    conversation_id: int = Form(None),
    db: Session = Depends(get_db)
):
    if not file.filename.endswith(".apk"):
        raise HTTPException(status_code=400, detail="Hanya file .apk yang diizinkan.")
    
    contents = await file.read()
    extraction = extract_apk_info(contents)
    if not extraction["success"]:
        raise HTTPException(status_code=500, detail=f"Gagal membedah APK: {extraction['error']}")
    
    analysis = analyze_threat("apk", extraction["summary"])
    status = determine_status(analysis)
    
    threat_data = {
        "status": status,
        "target": file.filename,
        "type": "apk",
        "analysis_report": analysis,
        "metadata": extraction,
        "created_at": datetime.datetime.utcnow().isoformat()
    }

    if conversation_id:
        # Save user message (file upload)
        save_message(db, conversation_id, "user", "file_upload", content=file.filename)
        # Save bot result
        save_message(db, conversation_id, "bot", "threat_result", threat_data=threat_data)
        
        # Update conversation title if it's default
        conv = db.query(Conversation).filter(Conversation.id == conversation_id).first()
        if conv and conv.title == "Pesan Baru":
            conv.title = f"Analisa: {file.filename}"
            db.commit()

    return threat_data

@app.post("/api/analyze/url")
async def analyze_url(request: URLRequest, db: Session = Depends(get_db)):
    extraction = await extract_url_info(request.url)
    if not extraction["success"]:
        raise HTTPException(status_code=500, detail=f"Gagal membedah URL: {extraction['error']}")
    
    analysis = analyze_threat("url", extraction["summary"])
    status = determine_status(analysis)
    
    threat_data = {
        "status": status,
        "target": request.url,
        "type": "url",
        "analysis_report": analysis,
        "metadata": extraction,
        "created_at": datetime.datetime.utcnow().isoformat()
    }

    if request.conversation_id:
        save_message(db, request.conversation_id, "user", "url_upload", content=request.url)
        save_message(db, request.conversation_id, "bot", "threat_result", threat_data=threat_data)
        
        conv = db.query(Conversation).filter(Conversation.id == request.conversation_id).first()
        if conv and conv.title == "Pesan Baru":
            domain = re.sub(r'^https?://', '', request.url).split('/')[0]
            conv.title = f"Analisa: {domain}"
            db.commit()

    return threat_data

@app.post("/api/chat")
async def chat_endpoint(request: ChatRequest, db: Session = Depends(get_db)):
    message = request.message
    
    # Check if it's a raw URL (fallback)
    url_match = re.search(r'(https?:\/\/[^\s]+)|(\b[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+(?:\/[^\s]*)?\b)', message)
    if url_match:
        url = url_match.group(0)
        extraction = await extract_url_info(url)
        if extraction["success"]:
            analysis = analyze_threat("url", extraction["summary"])
            status = determine_status(analysis)
            threat_data = {
                "status": status, "target": url, "type": "url",
                "analysis_report": analysis, "metadata": extraction,
                "created_at": datetime.datetime.utcnow().isoformat()
            }
            if request.conversation_id:
                save_message(db, request.conversation_id, "user", "url_upload", content=url)
                save_message(db, request.conversation_id, "bot", "threat_result", threat_data=threat_data)
            return {"role": "bot", "type": "threat_result", "threatData": threat_data}

    # General Chat
    history_dicts = [{"role": h.role, "content": h.content} for h in request.history]
    response_content = analyze_threat("chat", message, history_dicts)
    
    if request.conversation_id:
        save_message(db, request.conversation_id, "user", "text", content=message)
        save_message(db, request.conversation_id, "bot", "text", content=response_content)
        
        conv = db.query(Conversation).filter(Conversation.id == request.conversation_id).first()
        if conv and conv.title == "Pesan Baru":
            conv.title = message[:30] + ("..." if len(message) > 30 else "")
            db.commit()

    return {
        "role": "bot",
        "type": "text",
        "content": response_content
    }

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)


