import streamlit as st
import json
import datetime
from groq_chat import ask_doctor, transcribe_audio
from vector_store.pdf_handler import process_pdf, search_context
from utils.medicine_tracker import save_medicine, get_medicines
from utils.patient_db import save_diagnosis, get_history
from utils.image_analyzer import analyze_image
from utils.language import LANGUAGES, translate_ui

# ─── Page Config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="AI Clinical Assistant",
    page_icon="🩺",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─── Session State Init ────────────────────────────────────────────────────────
for key, default in {
    "messages": [],
    "lang": "English",
    "voice_enabled": False,
    "uploaded_pdfs": [],
}.items():
    if key not in st.session_state:
        st.session_state[key] = default

lang = st.session_state["lang"]
ui = translate_ui(lang)


def build_patient_context(query: str) -> str:
    """Collect recent report and patient-history context for safer guidance."""
    context_parts = []

    if st.session_state.uploaded_pdfs:
        report_context = search_context(query)
        if report_context:
            context_parts.append(f"PDF / REPORT CONTEXT:\n{report_context}")

    history = get_history(limit=5)
    if history:
        history_lines = []
        for item in history:
            history_lines.append(
                f"- {item.get('date', 'Unknown date')}: "
                f"Patient asked: {item.get('query', '')} | "
                f"Assistant summary: {item.get('response', '')}"
            )
        context_parts.append("RECENT PATIENT HISTORY:\n" + "\n".join(history_lines))

    return "\n\n---\n\n".join(context_parts)

# ─── Custom CSS (ChatGPT Dark UI) ──────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Sora:wght@300;400;500;600&family=JetBrains+Mono:wght@400;500&display=swap');

:root {
    --bg-primary:    #0d0d0d;
    --bg-secondary:  #171717;
    --bg-tertiary:   #1e1e1e;
    --bg-hover:      #2a2a2a;
    --border:        #2d2d2d;
    --accent:        #19c37d;
    --accent-dim:    rgba(25,195,125,0.15);
    --accent-glow:   rgba(25,195,125,0.4);
    --text-primary:  #ececec;
    --text-secondary:#8e8ea0;
    --text-muted:    #565869;
    --danger:        #ef4444;
    --warning:       #f59e0b;
    --info:          #3b82f6;
}

/* Hide Streamlit chrome */
#MainMenu, footer, header { visibility: hidden; }
.stDeployButton { display: none; }
[data-testid="stToolbar"] { display: none; }

/* Root */
html, body, [data-testid="stAppViewContainer"] {
    background: var(--bg-primary) !important;
    font-family: 'Sora', sans-serif;
    color: var(--text-primary);
}

/* Sidebar */
[data-testid="stSidebar"] {
    background: var(--bg-secondary) !important;
    border-right: 1px solid var(--border);
}
[data-testid="stSidebar"] * { color: var(--text-primary) !important; }

/* Main area */
[data-testid="stMain"] {
    background: var(--bg-primary) !important;
}

/* Chat messages */
.user-msg {
    display: flex;
    justify-content: flex-end;
    margin: 8px 0;
}
.user-bubble {
    background: var(--bg-tertiary);
    border: 1px solid var(--border);
    border-radius: 18px 18px 4px 18px;
    padding: 12px 18px;
    max-width: 75%;
    font-size: 0.95rem;
    line-height: 1.6;
    color: var(--text-primary);
}

.assistant-msg {
    display: flex;
    align-items: flex-start;
    gap: 12px;
    margin: 8px 0;
}
.assistant-avatar {
    width: 36px; height: 36px;
    background: linear-gradient(135deg, var(--accent), #0ea5e9);
    border-radius: 50%;
    display: flex; align-items: center; justify-content: center;
    font-size: 1rem; flex-shrink: 0;
    box-shadow: 0 0 12px var(--accent-glow);
}
.assistant-bubble {
    background: transparent;
    padding: 12px 4px;
    max-width: 85%;
    font-size: 0.95rem;
    line-height: 1.8;
    color: var(--text-primary);
}

/* Input area */
.stTextInput > div > div > input,
.stTextArea textarea {
    background: var(--bg-tertiary) !important;
    border: 1px solid var(--border) !important;
    border-radius: 14px !important;
    color: var(--text-primary) !important;
    font-family: 'Sora', sans-serif !important;
    padding: 14px 18px !important;
    font-size: 0.95rem !important;
}
.stTextInput > div > div > input:focus,
.stTextArea textarea:focus {
    border-color: var(--accent) !important;
    box-shadow: 0 0 0 2px var(--accent-dim) !important;
}

/* Buttons */
.stButton > button {
    background: var(--bg-tertiary) !important;
    border: 1px solid var(--border) !important;
    color: var(--text-primary) !important;
    border-radius: 10px !important;
    font-family: 'Sora', sans-serif !important;
    font-size: 0.88rem !important;
    padding: 8px 16px !important;
    transition: all 0.2s ease !important;
}
.stButton > button:hover {
    border-color: var(--accent) !important;
    color: var(--accent) !important;
    background: var(--accent-dim) !important;
}

/* Primary button */
.primary-btn > button {
    background: var(--accent) !important;
    border-color: var(--accent) !important;
    color: #000 !important;
    font-weight: 600 !important;
}
.primary-btn > button:hover {
    background: #15a86c !important;
    color: #000 !important;
}

/* Selectbox */
.stSelectbox > div > div {
    background: var(--bg-tertiary) !important;
    border: 1px solid var(--border) !important;
    border-radius: 10px !important;
    color: var(--text-primary) !important;
}

/* File uploader */
[data-testid="stFileUploader"] {
    background: var(--bg-tertiary) !important;
    border: 1px dashed var(--border) !important;
    border-radius: 12px !important;
    padding: 12px !important;
}

/* Metrics */
[data-testid="stMetric"] {
    background: var(--bg-secondary);
    border: 1px solid var(--border);
    border-radius: 12px;
    padding: 16px;
}
[data-testid="stMetricValue"] { color: var(--accent) !important; font-weight: 600 !important; }

/* Expander */
.streamlit-expanderHeader {
    background: var(--bg-tertiary) !important;
    border-radius: 10px !important;
    color: var(--text-primary) !important;
}

/* Divider */
hr { border-color: var(--border) !important; margin: 16px 0 !important; }

/* Scrollbar */
::-webkit-scrollbar { width: 5px; }
::-webkit-scrollbar-track { background: transparent; }
::-webkit-scrollbar-thumb { background: var(--border); border-radius: 10px; }
::-webkit-scrollbar-thumb:hover { background: var(--text-muted); }

/* Welcome screen */
.welcome-container {
    display: flex; flex-direction: column;
    align-items: center; justify-content: center;
    padding: 80px 20px; text-align: center;
}
.welcome-logo {
    width: 72px; height: 72px;
    background: linear-gradient(135deg, var(--accent), #0ea5e9);
    border-radius: 20px;
    display: flex; align-items: center; justify-content: center;
    font-size: 2rem; margin-bottom: 24px;
    box-shadow: 0 0 40px var(--accent-glow);
}
.welcome-title {
    font-size: 2rem; font-weight: 600;
    color: var(--text-primary); margin-bottom: 12px;
}
.welcome-sub {
    font-size: 1rem; color: var(--text-secondary);
    max-width: 480px; line-height: 1.7;
}
.suggestion-grid {
    display: grid; grid-template-columns: 1fr 1fr;
    gap: 12px; margin-top: 32px; width: 100%; max-width: 520px;
}
.suggestion-card {
    background: var(--bg-secondary);
    border: 1px solid var(--border);
    border-radius: 12px;
    padding: 16px;
    cursor: pointer;
    text-align: left;
    transition: all 0.2s ease;
    color: var(--text-primary);
    font-size: 0.88rem;
    line-height: 1.5;
}
.suggestion-card:hover {
    border-color: var(--accent);
    background: var(--accent-dim);
}
.suggestion-icon { font-size: 1.2rem; margin-bottom: 8px; display: block; }

/* Medicine badge */
.med-badge {
    display: inline-block;
    background: var(--accent-dim);
    border: 1px solid var(--accent);
    color: var(--accent);
    border-radius: 20px;
    padding: 3px 12px;
    font-size: 0.78rem;
    font-weight: 500;
    margin: 3px;
}
.time-badge {
    display: inline-block;
    background: rgba(59,130,246,0.15);
    border: 1px solid #3b82f6;
    color: #60a5fa;
    border-radius: 20px;
    padding: 3px 12px;
    font-size: 0.78rem;
    margin: 3px;
}

/* Chat container */
.chat-area {
    max-width: 760px;
    margin: 0 auto;
    padding: 20px 0 120px 0;
}
</style>
""", unsafe_allow_html=True)

# ─── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div style='display:flex;align-items:center;gap:10px;padding:12px 0 20px 0;'>
        <div style='width:36px;height:36px;background:linear-gradient(135deg,#19c37d,#0ea5e9);
             border-radius:10px;display:flex;align-items:center;justify-content:center;
             font-size:1.2rem;box-shadow:0 0 12px rgba(25,195,125,0.4);'>🩺</div>
        <div>
            <div style='font-weight:600;font-size:1rem;color:#ececec;'>AI Clinical Assistant</div>
            <div style='font-size:0.72rem;color:#19c37d;'>● Online</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    if st.button("✦  " + ui["new_chat"], use_container_width=True):
        st.session_state.messages = []
        st.rerun()

    st.markdown("<hr>", unsafe_allow_html=True)

    # Navigation
    st.markdown(f"<div style='font-size:0.72rem;color:#565869;font-weight:600;letter-spacing:0.08em;text-transform:uppercase;margin-bottom:8px;'>{ui['navigation']}</div>", unsafe_allow_html=True)
    nav = st.radio(
        "", [ui["chat"], ui["dashboard"], ui["medicine_tracker"]],
        label_visibility="collapsed"
    )

    st.markdown("<hr>", unsafe_allow_html=True)

    # Language selector
    st.markdown(f"<div style='font-size:0.72rem;color:#565869;font-weight:600;letter-spacing:0.08em;text-transform:uppercase;margin-bottom:8px;'>{ui['language']}</div>", unsafe_allow_html=True)
    selected_lang = st.selectbox("", list(LANGUAGES.keys()), index=list(LANGUAGES.keys()).index(lang), label_visibility="collapsed")
    if selected_lang != lang:
        st.session_state["lang"] = selected_lang
        st.rerun()

    # PDF Upload
    st.markdown("<hr>", unsafe_allow_html=True)
    st.markdown(f"<div style='font-size:0.72rem;color:#565869;font-weight:600;letter-spacing:0.08em;text-transform:uppercase;margin-bottom:8px;'>{ui['upload_docs']}</div>", unsafe_allow_html=True)
    pdf_file = st.file_uploader(ui["upload_pdf"], type=["pdf"], label_visibility="collapsed")
    if pdf_file:
        with st.spinner(ui["processing"]):
            msg = process_pdf(pdf_file)
            st.success(msg)

    # Voice toggle
    st.markdown("<hr>", unsafe_allow_html=True)
    st.session_state["voice_enabled"] = st.toggle(f"🎙️ {ui['voice_mode']}", value=st.session_state["voice_enabled"])

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown(f"<div style='font-size:0.72rem;color:#565869;text-align:center;'>{ui['disclaimer']}</div>", unsafe_allow_html=True)

# ─── Main Content ──────────────────────────────────────────────────────────────

# DASHBOARD PAGE
if nav == ui["dashboard"]:
    from pages.dashboard import render_dashboard
    render_dashboard(ui, lang)

# MEDICINE TRACKER PAGE
elif nav == ui["medicine_tracker"]:
    from pages.medicine_page import render_medicine_page
    render_medicine_page(ui, lang)

# CHAT PAGE
else:
    # Header
    st.markdown(f"""
    <div style='text-align:center;padding:20px 0 10px 0;'>
        <div style='font-size:0.78rem;color:#565869;letter-spacing:0.1em;text-transform:uppercase;'>
            {ui['powered_by']}
        </div>
    </div>
    """, unsafe_allow_html=True)

    chat_container = st.container()

    # Welcome screen
    if not st.session_state.messages:
        with chat_container:
            st.markdown(f"""
            <div class="welcome-container">
                <div class="welcome-logo">🩺</div>
                <div class="welcome-title">{ui['welcome_title']}</div>
                <div class="welcome-sub">{ui['welcome_sub']}</div>
            </div>
            """, unsafe_allow_html=True)

            # Suggestion pills
            c1, c2 = st.columns(2)
            suggestions = ui["suggestions"]
            with c1:
                if st.button(suggestions[0], use_container_width=True):
                    st.session_state.messages.append({"role": "user", "content": suggestions[0]})
                if st.button(suggestions[2], use_container_width=True):
                    st.session_state.messages.append({"role": "user", "content": suggestions[2]})
            with c2:
                if st.button(suggestions[1], use_container_width=True):
                    st.session_state.messages.append({"role": "user", "content": suggestions[1]})
                if st.button(suggestions[3], use_container_width=True):
                    st.session_state.messages.append({"role": "user", "content": suggestions[3]})
    else:
        # Render chat history
        with chat_container:
            st.markdown('<div class="chat-area">', unsafe_allow_html=True)
            for msg in st.session_state.messages:
                if msg["role"] == "user":
                    content = msg["content"]
                    if isinstance(content, list):
                        # Has image
                        for item in content:
                            if item.get("type") == "text":
                                st.markdown(f'<div class="user-msg"><div class="user-bubble">{item["text"]}</div></div>', unsafe_allow_html=True)
                            elif item.get("type") == "image_url":
                                st.markdown(f'<div class="user-msg"><img src="{item["image_url"]["url"]}" style="max-width:300px;border-radius:12px;"></div>', unsafe_allow_html=True)
                    else:
                        st.markdown(f'<div class="user-msg"><div class="user-bubble">{content}</div></div>', unsafe_allow_html=True)
                else:
                    st.markdown(f"""
                    <div class="assistant-msg">
                        <div class="assistant-avatar">🩺</div>
                        <div class="assistant-bubble">{msg["content"]}</div>
                    </div>
                    """, unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)

    # ─── Input Area ───────────────────────────────────────────────────────────
    st.markdown("<hr>", unsafe_allow_html=True)

    # Image upload toggle
    with st.expander(f"📎 {ui['attach']}", expanded=False):
        img_col, _ = st.columns([1, 2])
        with img_col:
            uploaded_img = st.file_uploader(ui["upload_image"], type=["jpg", "jpeg", "png"], label_visibility="collapsed")

    # Voice input
    voice_text = ""
    if st.session_state["voice_enabled"]:
        audio = st.audio_input(f"🎙️ {ui['speak_now']}")
        if audio:
            with st.spinner(ui["transcribing"]):
                voice_text = transcribe_audio(audio)
            if voice_text:
                st.success(f"📝 {voice_text}")

    # Text input
    input_col, send_col = st.columns([8, 1])
    with input_col:
        user_input = st.text_input(
            "",
            value=voice_text,
            placeholder=ui["input_placeholder"],
            label_visibility="collapsed",
            key="chat_input"
        )
    with send_col:
        st.markdown('<div class="primary-btn">', unsafe_allow_html=True)
        send = st.button("↑", use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

    # Process input
    if (send or user_input) and (user_input.strip() or uploaded_img):
        # Build message content
        if uploaded_img:
            import base64
            img_bytes = uploaded_img.read()
            b64 = base64.b64encode(img_bytes).decode()
            ext = uploaded_img.name.split(".")[-1].lower()
            mime = "image/jpeg" if ext in ["jpg","jpeg"] else "image/png"
            img_data_url = f"data:{mime};base64,{b64}"

            user_msg_content = [
                {"type": "image_url", "image_url": {"url": img_data_url}},
                {"type": "text", "text": user_input.strip() or ui["analyze_image_prompt"]}
            ]
            display_text = user_input.strip() or ui["analyze_image_prompt"]
        else:
            user_msg_content = user_input.strip()
            display_text = user_input.strip()

        st.session_state.messages.append({"role": "user", "content": user_msg_content})

        # Get report and recent patient-history context.
        extra_context = build_patient_context(display_text)

        # Get AI response
        with st.spinner(ui["thinking"]):
            response = ask_doctor(
                st.session_state.messages,
                lang=lang,
                context=extra_context,
                has_image=(uploaded_img is not None)
            )

        st.session_state.messages.append({"role": "assistant", "content": response})

        # Auto-save diagnosis
        save_diagnosis(display_text, response, lang)

        st.rerun()
