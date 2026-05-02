from fastapi import FastAPI, UploadFile, File, HTTPException, Depends, Form, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, HttpUrl, field_validator
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
import uvicorn
import re
import datetime
import magic # Added python-magic for file signature validation

from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

from services.apk_analyzer import extract_apk_info
from services.url_analyzer import extract_url_info
from services.groq_service import analyze_threat
from database import get_db, Conversation, Message

app = FastAPI(title="Cyber-Threat Sandbox Bot API")

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ─── Models (Pydantic Validations) ──────────────────────────────────────────

class URLRequest(BaseModel):
    url: HttpUrl
    user_message: str = None
    conversation_id: int = None

class ChatMessageItem(BaseModel):
    role: str
    content: str

    @field_validator('role')
    @classmethod
    def validate_role(cls, v: str) -> str:
        if v not in ['user', 'bot', 'system']:
            raise ValueError('Role must be user, bot, or system')
        return v

class ChatRequest(BaseModel):
    message: str
    history: list[ChatMessageItem] = []
    conversation_id: int = None

    @field_validator('message')
    @classmethod
    def validate_message(cls, v: str) -> str:
        if len(v) > 2000:
            raise ValueError('Message too long')
        return v

# ─── Helpers ────────────────────────────────────────────────────────────────

def determine_status(analysis_text: str):
    if "[BERBAHAYA]" in analysis_text: return "BERBAHAYA"
    if "[WASPADA]" in analysis_text: return "WASPADA"
    return "AMAN"

def save_message(db: Session, conversation_id: int, role: str, msg_type: str, content: str = None, threat_data: dict = None):
    try:
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
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(status_code=500, detail="Database Error: Gagal menyimpan pesan.")

# ─── Endpoints ──────────────────────────────────────────────────────────────

@app.get("/")
def read_root():
    return {"message": "Cyber-Threat Sandbox Bot API is running."}

@app.post("/api/conversations")
@limiter.limit("10/minute")
async def create_conversation(request: Request, title: str = "Pesan Baru", db: Session = Depends(get_db)):
    try:
        conv = Conversation(title=title)
        db.add(conv)
        db.commit()
        db.refresh(conv)
        return conv
    except SQLAlchemyError:
        db.rollback()
        raise HTTPException(status_code=500, detail="Gagal membuat percakapan.")

@app.get("/api/conversations")
async def list_conversations(db: Session = Depends(get_db)):
    return db.query(Conversation).order_by(Conversation.created_at.desc()).all()

@app.get("/api/conversations/{conv_id}")
async def get_conversation(conv_id: int, db: Session = Depends(get_db)):
    conv = db.query(Conversation).filter(Conversation.id == conv_id).first()
    if not conv:
        raise HTTPException(status_code=404, detail="Percakapan tidak ditemukan.")
    
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
    try:
        db.delete(conv)
        db.commit()
        return {"success": True}
    except SQLAlchemyError:
        db.rollback()
        raise HTTPException(status_code=500, detail="Gagal menghapus percakapan.")

@app.post("/api/analyze/apk")
@limiter.limit("5/minute")
async def analyze_apk(
    request: Request,
    file: UploadFile = File(...), 
    user_message: str = Form(None),
    conversation_id: int = Form(None),
    db: Session = Depends(get_db)
):
    if not file.filename.endswith(".apk"):
        raise HTTPException(status_code=400, detail="Ekstensi file tidak valid. Hanya .apk yang diizinkan.")

    contents = await file.read()

    # Size check (e.g. max 50MB)
    if len(contents) > 50 * 1024 * 1024:
        raise HTTPException(status_code=413, detail="File terlalu besar. Maksimal 50MB.")

    # Signature/Magic byte check
    file_mime = magic.from_buffer(contents, mime=True)
    if file_mime not in ['application/vnd.android.package-archive', 'application/zip', 'application/java-archive']:
        raise HTTPException(status_code=400, detail="File Corrupted atau BUKAN file APK yang valid.")

    extraction = extract_apk_info(contents)
    if not extraction["success"]:
        raise HTTPException(status_code=500, detail=f"Gagal membedah APK: {extraction['error']}")
    
    try:
        analysis = analyze_threat("apk", extraction["summary"])
    except Exception as e:
        raise HTTPException(status_code=504, detail="Server Timeout: AI Analyzer gagal merespons.")

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
        save_message(db, conversation_id, "user", "file_upload", content=file.filename)
        save_message(db, conversation_id, "bot", "threat_result", threat_data=threat_data)
        
        try:
            conv = db.query(Conversation).filter(Conversation.id == conversation_id).first()
            if conv and conv.title == "Pesan Baru":
                conv.title = f"Analisa: {file.filename}"
                db.commit()
        except SQLAlchemyError:
            db.rollback()

    return threat_data

@app.post("/api/analyze/url")
@limiter.limit("10/minute")
async def analyze_url(req_obj: Request, request: URLRequest, db: Session = Depends(get_db)):
    url_str = str(request.url)
    extraction = await extract_url_info(url_str)
    if not extraction["success"]:
        raise HTTPException(status_code=500, detail=f"Gagal membedah URL: {extraction['error']}")
    
    try:
        analysis = analyze_threat("url", extraction["summary"])
    except Exception as e:
         raise HTTPException(status_code=504, detail="Server Timeout: AI Analyzer gagal merespons.")

    status = determine_status(analysis)
    
    threat_data = {
        "status": status,
        "target": url_str,
        "type": "url",
        "analysis_report": analysis,
        "metadata": extraction,
        "created_at": datetime.datetime.utcnow().isoformat()
    }

    if request.conversation_id:
        save_message(db, request.conversation_id, "user", "url_upload", content=url_str)
        save_message(db, request.conversation_id, "bot", "threat_result", threat_data=threat_data)
        
        try:
            conv = db.query(Conversation).filter(Conversation.id == request.conversation_id).first()
            if conv and conv.title == "Pesan Baru":
                domain = re.sub(r'^https?://', '', url_str).split('/')[0]
                conv.title = f"Analisa: {domain}"
                db.commit()
        except SQLAlchemyError:
            db.rollback()

    return threat_data

@app.post("/api/chat")
@limiter.limit("20/minute")
async def chat_endpoint(req_obj: Request, request: ChatRequest, db: Session = Depends(get_db)):
    message = request.message
    
    # Check if it's a raw URL (fallback)
    url_match = re.search(r'(https?:\/\/[^\s]+)|(\b[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+(?:\/[^\s]*)?\b)', message)
    if url_match:
        url = url_match.group(0)
        # Ensure it has http/https
        if not url.startswith('http'):
            url = 'https://' + url

        extraction = await extract_url_info(url)
        if extraction["success"]:
            try:
                analysis = analyze_threat("url", extraction["summary"])
            except Exception:
                raise HTTPException(status_code=504, detail="Server Timeout saat menganalisa URL")

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
    
    try:
        response_content = analyze_threat("chat", message, history_dicts)
    except Exception:
        raise HTTPException(status_code=504, detail="Server Timeout: Otak AI tidak merespons.")

    if request.conversation_id:
        save_message(db, request.conversation_id, "user", "text", content=message)
        save_message(db, request.conversation_id, "bot", "text", content=response_content)
        
        try:
            conv = db.query(Conversation).filter(Conversation.id == request.conversation_id).first()
            if conv and conv.title == "Pesan Baru":
                conv.title = message[:30] + ("..." if len(message) > 30 else "")
                db.commit()
        except SQLAlchemyError:
            db.rollback()

    return {
        "role": "bot",
        "type": "text",
        "content": response_content
    }

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
