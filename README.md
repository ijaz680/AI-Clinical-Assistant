# 🩺 AI Doctor — Intelligent Medical Assistant

An AI-powered medical assistant with a **ChatGPT-style dark UI**, voice input, multilingual support, PDF report analysis, disease prediction from images, and a full patient dashboard.

---

## ✨ Features

| Feature | Description |
|---|---|
| 💬 **Chat Interface** | ChatGPT-style dark UI with chat history |
| 🎙️ **Voice Input** | Speak your symptoms via Groq Whisper |
| 🖼️ **Image Diagnosis** | Upload X-rays / skin images for AI analysis |
| 📄 **PDF Reports** | Upload medical reports → AI reads & responds |
| 🔍 **Vector Search** | ChromaDB stores PDF chunks for smart retrieval |
| 💊 **Medicine Tracker** | Add, track, stop medicines with timing (morning/night) |
| 📊 **Patient Dashboard** | Full history of diagnoses + medicine log |
| 🌍 **Multilingual** | English, Urdu, Arabic, Hindi, French, Spanish |

---

## 🛠️ Tech Stack

| Tool | Purpose |
|---|---|
| Python | Core language |
| Streamlit | Web UI framework |
| Groq API | Ultra-fast LLM inference |
| LLaMA 3.3 70B | Text diagnosis & Q&A |
| LLaMA 3.2 90B Vision | Medical image analysis |
| Whisper Large v3 | Voice-to-text transcription |
| ChromaDB | Local vector store for PDF embeddings |
| pdfplumber | PDF text extraction |

---

## 📁 Project Structure

```
ai_doctor/
├── app.py                    # Main Streamlit app (ChatGPT UI)
├── groq_chat.py              # Groq API integration (text + vision + voice)
├── requirements.txt          # All Python dependencies
├── .env                      # Your API key (DO NOT COMMIT)
├── .env.example              # Template for .env
├── .gitignore                # Git ignore rules
│
├── vector_store/
│   ├── __init__.py
│   ├── pdf_handler.py        # PDF chunking, embedding, ChromaDB storage
│   └── chroma_db/            # Auto-created: local vector database
│
├── pages/
│   ├── __init__.py
│   ├── dashboard.py          # Patient Dashboard (history + medicine log)
│   └── medicine_page.py      # Medicine Tracker UI
│
├── utils/
│   ├── __init__.py
│   ├── language.py           # Multilingual UI strings
│   ├── medicine_tracker.py   # Medicine CRUD operations
│   ├── patient_db.py         # Diagnosis history storage
│   └── image_analyzer.py     # Image encoding helper
│
└── data/                     # Auto-created: local JSON storage
    ├── patient_db.json
    └── medicines.json
```

---

## ⚙️ Setup & Installation

### 1. Clone the Repository
```bash
git clone https://github.com/your-username/ai_doctor.git
cd ai_doctor
```

### 2. Create Virtual Environment
```bash
python -m venv myvenv

# Windows
myvenv\Scripts\activate

# Mac/Linux
source myvenv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Set Up API Key
```bash
cp .env.example .env
```
Edit `.env` and add your key:
```
GROQ_API_KEY=your_groq_api_key_here
```
Get your free key at [console.groq.com](https://console.groq.com)

### 5. Run the App
```bash
streamlit run app.py
```
Open: **http://localhost:8501**

---

## 🤖 Models Used

| Model | Purpose | Status |
|---|---|---|
| `llama-3.3-70b-versatile` | Medical Q&A, diagnosis | ✅ Active |
| `llama-3.2-90b-vision-preview` | Image analysis | ✅ Active |
| `whisper-large-v3` | Voice transcription | ✅ Active |
| `llama3-70b-8192` | Old model | ❌ Decommissioned |

---

## 💊 Medicine Timing

The AI always specifies medicine timing clearly:
- 🌅 **Morning** — With or before breakfast
- 🌙 **Night** — Before sleep
- 🍽️ **After Meals** — Post-lunch/dinner
- 🔄 **Twice Daily** — Morning + Night

---

## 🌍 Supported Languages

- 🇬🇧 English
- 🇵🇰 اردو (Urdu)
- 🇸🇦 العربية (Arabic)
- 🇮🇳 हिन्दी (Hindi)
- 🇫🇷 Français (French)
- 🇪🇸 Español (Spanish)

The AI automatically responds in the language you write in.

---

## 🔒 Security Notes

- **Never commit** your `.env` file
- `.env` is already in `.gitignore`
- This app is for **informational purposes only**
- Not a substitute for professional medical advice

---

## 📄 License

MIT License — free to use and modify.

---

