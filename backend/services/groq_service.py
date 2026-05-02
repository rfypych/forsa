import os
from groq import Groq
from dotenv import load_dotenv

load_dotenv() # Load variables from .env

def analyze_threat(data_type: str, raw_data: str, history: list = None):
    """
    Sends raw extraction data to Groq for expert analysis.
    data_type: 'apk', 'url', or 'chat'
    raw_data: The extracted text or user message
    history: List of previous messages [{"role": "user"/"bot", "content": "..."}]
    """
    api_key = os.environ.get("GROQ_API_KEY")
    if not api_key:
        return "Error: GROQ_API_KEY tidak ditemukan di environment variables. Silakan set API Key Anda."

    client = Groq(api_key=api_key)
    
    if data_type == "chat":
        system_prompt = (
            "Kamu adalah FORSA (Forensic Search & Analysis), asisten keamanan siber resmi dari Ditipidsiber Bareskrim Polri. "
            "Tugasmu adalah menjawab pertanyaan warga terkait keamanan siber, phishing, penipuan online, dan APK berbahaya. "
            "Gunakan bahasa Indonesia yang profesional, ramah, tegas, dan mudah dipahami orang awam. "
            "Kamu memiliki ingatan tentang file atau URL yang baru saja kamu analisa di percakapan sebelumnya. "
            "JANGAN menggunakan format [AMAN]/[WASPADA]/[BERBAHAYA] untuk percakapan biasa, jawablah selayaknya asisten chat biasa."
        )
        user_content = raw_data
    else:
        system_prompt = (
            "Kamu adalah analis keamanan siber dari Tim Cyber Crime Polri. "
            "Tugasmu adalah menganalisis data mentah yang diberikan (bisa berupa daftar izin aplikasi Android atau konten website) "
            "dan memberikan penilaian apakah hal tersebut merupakan ancaman keamanan bagi masyarakat (seperti penipuan APK, phishing, dll). "
            "\n\nInstruksi Khusus:\n"
            "1. Berikan status: [AMAN], [WASPADA], atau [BERBAHAYA].\n"
            "2. **Jelaskan Relasi Ancaman Secara Spesifik:** Jika ada kombinasi data yang berbahaya, jelaskan korelasinya. Contoh: 'Izin membaca SMS (READ_SMS) dikombinasikan dengan akses Internet (INTERNET) adalah potensi besar untuk pencurian kode OTP secara diam-diam.'\n"
            "3. Berikan alasan teknis tambahan dengan bahasa yang mudah dipahami orang awam.\n"
            "4. Berikan saran langkah pencegahan yang konkret.\n"
            "5. Gunakan nada bicara yang profesional, tegas, namun tetap menenangkan."
        )
        user_content = f"Tipe Data: {data_type.upper()}\nData Mentah:\n{raw_data}"
    
    messages = [{"role": "system", "content": system_prompt}]
    
    # Implement Sliding Window Memory
    # Keep only the last 6 messages (3 pairs of user-bot interactions) to prevent token exhaustion
    # while preserving immediate context.
    if history:
        # Filter out messages that might be too large (e.g. raw extraction dumps)
        # and only keep standard text interactions to save tokens
        clean_history = []
        for msg in history:
            if isinstance(msg["content"], str) and len(msg["content"]) < 1500:
                clean_history.append(msg)

        # Take the last 6 messages
        windowed_history = clean_history[-6:]

        for msg in windowed_history:
            role = "assistant" if msg["role"] == "bot" else "user"
            messages.append({"role": role, "content": msg["content"]})
            
    messages.append({"role": "user", "content": user_content})
    
    try:
        completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=messages,
            temperature=0.2 if data_type != "chat" else 0.5,
            max_tokens=1024,
        )
        return completion.choices[0].message.content
    except Exception as e:
        return f"Terjadi kesalahan saat menghubungi Otak AI: {str(e)}"
