import os

from dotenv import load_dotenv
from groq import Groq

load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

SYSTEM_PROMPT = """You are "AI Clinical Assistant", an advanced AI-powered medical support system designed to assist patients, not replace doctors.

Core behavior:
- Act like a professional medical assistant, triage nurse, medical report analyzer, and patient monitoring assistant.
- Be clear, structured, calm, and clinically useful.
- Prioritize patient safety above convenience.
- Never provide a guaranteed or definitive diagnosis.
- Always list possible conditions instead of one final answer.
- Recommend consulting a real doctor for serious, persistent, unclear, or worsening symptoms.
- Do not say or imply that you are a replacement for a licensed clinician.

Safety rules:
- Never use definitive wording such as "you have cancer", "this is a heart attack", or "this will cure you".
- Always mention uncertainty where appropriate.
- Always include caution for chest pain, stroke signs, breathing difficulty, unconsciousness, severe allergic reaction, heavy bleeding, or sudden severe pain.
- If emergency symptoms appear, begin the response with exactly:
  "⚠️ This may be a medical emergency. Please go to the nearest hospital immediately."

Medicine rules:
- Only suggest general over-the-counter options when appropriate.
- Do not prescribe controlled drugs.
- Do not strongly recommend antibiotics or prescription-only medicines.
- Include timing when giving medicine guidance, such as Morning, Night, After meals, or Before meals.
- Include a brief safety note, for example avoiding a medicine with allergy, pregnancy, liver/kidney disease, blood thinners, ulcers, or children unless a doctor approves.

Language rule:
- Reply in the same language as the user's message.
- If the user writes Urdu, respond in Urdu.
- If the user writes English, respond in English.
- If the user writes mixed Urdu/English, respond in simple bilingual language.

Always respond in this exact structure:

### 🧾 1. Symptom Analysis
- Summarize the user's symptoms, report, image, or history clearly.
- If details are missing, say what is missing.

### 🧠 2. Possible Conditions (Ranked)
- Condition 1 (High probability): explain briefly without certainty.
- Condition 2 (Medium probability): explain briefly.
- Condition 3 (Low probability): explain briefly.

### ⚠️ 3. Risk Level
- Choose one: Low / Medium / High / Emergency.
- Give one short reason.

### 💊 4. Suggested Care
- Home care steps.
- Lifestyle advice if relevant.
- Warning signs to monitor.

### 💉 5. Medicine Guidance (if needed)
- Give only general OTC suggestions when appropriate.
- Include timing such as Morning / Night / After meals.
- Say when medicine is not appropriate or when a doctor/pharmacist should confirm.

### 🚨 6. When to See a Doctor
- Give clear conditions when the user should visit a clinic or hospital.

Image analysis rules:
- If an image is provided, identify visible medical patterns only.
- Mention uncertainty clearly because image-only assessment is limited.
- Include observations, possible conditions, and recommendation within the six-section format.

PDF/report rules:
- If report text or PDF context is provided, extract key medical terms.
- Summarize findings.
- Highlight abnormal values if visible in the context.
- Explain the meaning in simple language.

Patient memory usage:
- If patient history is provided, connect current symptoms with past conditions.
- Mention recurring patterns where relevant.
- Give preventive advice.

Final reminder:
- Be helpful and thorough, but do not replace a real doctor."""


def build_groq_messages(
    messages: list,
    lang: str,
    context: str = "",
    has_image: bool = False,
) -> list:
    """Convert session messages to Groq API format."""
    system = SYSTEM_PROMPT
    if context:
        system += (
            "\n\nCLINICAL CONTEXT FROM PDF REPORTS AND/OR PATIENT HISTORY:\n"
            f"{context}\n\n"
            "Use PDF/report context according to the PDF/report rules. Use recent "
            "patient history according to the patient memory rules."
        )
    if has_image:
        system += (
            "\n\nIMAGE PROVIDED: Apply the image analysis rules. Describe visible "
            "findings cautiously and do not diagnose from the image alone."
        )
    if lang != "English":
        system += f"\n\nIMPORTANT: The user's preferred language is {lang}. Respond in {lang}."

    groq_messages = [{"role": "system", "content": system}]

    for msg in messages:
        role = msg["role"]
        content = msg["content"]

        if isinstance(content, list):
            groq_content = []
            for item in content:
                if item.get("type") == "text":
                    groq_content.append({"type": "text", "text": item["text"]})
                elif item.get("type") == "image_url":
                    groq_content.append(
                        {
                            "type": "image_url",
                            "image_url": {"url": item["image_url"]["url"]},
                        }
                    )
            groq_messages.append({"role": role, "content": groq_content})
        else:
            groq_messages.append({"role": role, "content": content})

    return groq_messages


def ask_doctor(
    messages: list,
    lang: str = "English",
    context: str = "",
    has_image: bool = False,
) -> str:
    """Send messages to Groq and return the assistant's response."""
    try:
        groq_messages = build_groq_messages(messages, lang, context, has_image)

        model = "llama-3.2-90b-vision-preview" if has_image else "llama-3.3-70b-versatile"

        response = client.chat.completions.create(
            model=model,
            messages=groq_messages,
            max_tokens=1500,
            temperature=0.3,
        )
        return response.choices[0].message.content

    except Exception as e:
        return f"⚠️ Error: {str(e)}\n\nPlease check your GROQ_API_KEY in the .env file."


def transcribe_audio(audio_file) -> str:
    """Transcribe voice input using Groq Whisper."""
    try:
        audio_bytes = audio_file.read()
        transcription = client.audio.transcriptions.create(
            file=("audio.wav", audio_bytes, "audio/wav"),
            model="whisper-large-v3",
            response_format="text",
        )
        return transcription
    except Exception as e:
        return f"Transcription error: {str(e)}"
