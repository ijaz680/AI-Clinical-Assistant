import streamlit as st
from utils.patient_db import get_history, clear_history
from utils.medicine_tracker import get_medicines


def render_dashboard(ui: dict, lang: str):
    st.markdown(f"<h2 style='color:#ececec;font-family:Sora,sans-serif;padding-bottom:4px;'>{ui['dashboard_title']}</h2>", unsafe_allow_html=True)
    st.markdown("<hr>", unsafe_allow_html=True)

    # ── Metrics ──────────────────────────────────────────────────────────────
    history = get_history(100)
    medicines = get_medicines()
    active_meds = [m for m in medicines if m.get("active", True)]

    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric(ui["total_chats"], len(history))
    with col2:
        st.metric(ui["active_meds"], len(active_meds))
    with col3:
        st.metric(ui["medicine_history"], len(medicines))

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Recent Diagnoses ──────────────────────────────────────────────────────
    col_left, col_right = st.columns([3, 2])

    with col_left:
        st.markdown(f"<h4 style='color:#ececec;font-family:Sora,sans-serif;'>{ui['recent_diagnosis']}</h4>", unsafe_allow_html=True)

        if not history:
            st.markdown(f"<p style='color:#8e8ea0;'>{ui['no_history']}</p>", unsafe_allow_html=True)
        else:
            for entry in history[:10]:
                with st.expander(f"🗓️ {entry['date']}  —  {entry['query'][:60]}...", expanded=False):
                    st.markdown(f"**{ui['query']}:** {entry['query']}", unsafe_allow_html=False)
                    st.markdown("---")
                    st.markdown(f"**{ui['response']}:**\n\n{entry['response']}")
                    st.caption(f"Language: {entry.get('lang', 'English')}")

            st.markdown("<br>", unsafe_allow_html=True)
            if st.button(ui["clear_history"]):
                clear_history()
                st.success("History cleared!")
                st.rerun()

    with col_right:
        st.markdown(f"<h4 style='color:#ececec;font-family:Sora,sans-serif;'>{ui['medicine_history']}</h4>", unsafe_allow_html=True)

        if not medicines:
            st.markdown(f"<p style='color:#8e8ea0;'>{ui['no_meds']}</p>", unsafe_allow_html=True)
        else:
            for med in medicines[:15]:
                status_color = "#19c37d" if med.get("active", True) else "#565869"
                status_text = ui["active"] if med.get("active", True) else ui["stopped"]

                timing_map = {
                    "Morning": ui["morning"],
                    "Night": ui["night"],
                    "After Meals": ui["after_meals"],
                    "Before Meals": ui["before_meals"],
                    "Twice Daily": ui["twice_daily"],
                }
                timing_label = timing_map.get(med.get("timing", ""), med.get("timing", ""))

                st.markdown(f"""
                <div style='background:#171717;border:1px solid #2d2d2d;border-radius:10px;
                     padding:12px 14px;margin-bottom:8px;'>
                    <div style='display:flex;justify-content:space-between;align-items:center;'>
                        <div style='font-weight:600;color:#ececec;font-size:0.9rem;'>💊 {med['name']}</div>
                        <div style='font-size:0.72rem;color:{status_color};font-weight:600;'>{status_text}</div>
                    </div>
                    <div style='margin-top:6px;'>
                        <span class='med-badge'>{med.get('dosage','')}</span>
                        <span class='time-badge'>{timing_label}</span>
                    </div>
                    <div style='font-size:0.75rem;color:#8e8ea0;margin-top:6px;'>
                        📅 {med.get('added_date','')} · ⏱️ {med.get('duration','')}
                    </div>
                </div>
                """, unsafe_allow_html=True)
