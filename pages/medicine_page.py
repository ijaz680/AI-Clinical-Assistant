import streamlit as st
from utils.medicine_tracker import save_medicine, get_medicines, toggle_medicine, delete_medicine


def render_medicine_page(ui: dict, lang: str):
    st.markdown(f"<h2 style='color:#ececec;font-family:Sora,sans-serif;padding-bottom:4px;'>{ui['med_tracker_title']}</h2>", unsafe_allow_html=True)
    st.markdown("<hr>", unsafe_allow_html=True)

    col_form, col_list = st.columns([2, 3])

    # ── Add Medicine Form ─────────────────────────────────────────────────────
    with col_form:
        st.markdown(f"<h4 style='color:#ececec;font-family:Sora,sans-serif;'>➕ {ui['add_medicine']}</h4>", unsafe_allow_html=True)

        med_name = st.text_input(ui["med_name"], placeholder="e.g. Paracetamol 500mg")
        dosage = st.text_input(ui["dosage"], placeholder="e.g. 1 tablet / 5ml")

        timing_options = {
            ui["morning"]: "Morning",
            ui["night"]: "Night",
            ui["after_meals"]: "After Meals",
            ui["before_meals"]: "Before Meals",
            ui["twice_daily"]: "Twice Daily",
        }
        timing_label = st.selectbox(ui["timing"], list(timing_options.keys()))
        timing = timing_options[timing_label]

        duration = st.text_input(ui["duration"], placeholder="e.g. 7 days / 2 weeks")
        notes = st.text_area(ui["notes"], placeholder="Any special instructions...", height=80)

        if st.button(f"💾 {ui['save_med']}", use_container_width=True):
            if med_name and dosage and duration:
                save_medicine(med_name, dosage, timing, duration, notes)
                st.success(f"✅ {med_name} saved!")
                st.rerun()
            else:
                st.warning("Please fill Medicine Name, Dosage, and Duration.")

    # ── Medicine List ─────────────────────────────────────────────────────────
    with col_list:
        st.markdown(f"<h4 style='color:#ececec;font-family:Sora,sans-serif;'>📋 {ui['your_medicines']}</h4>", unsafe_allow_html=True)

        meds = get_medicines()
        if not meds:
            st.markdown(f"<p style='color:#8e8ea0;'>{ui['no_meds']}</p>", unsafe_allow_html=True)
        else:
            active = [m for m in meds if m.get("active", True)]
            inactive = [m for m in meds if not m.get("active", True)]

            if active:
                st.markdown(f"<div style='font-size:0.72rem;color:#19c37d;font-weight:600;letter-spacing:0.08em;text-transform:uppercase;margin-bottom:8px;'>● {ui['active']}</div>", unsafe_allow_html=True)
                for med in active:
                    _render_med_card(med, ui)

            if inactive:
                st.markdown(f"<div style='font-size:0.72rem;color:#565869;font-weight:600;letter-spacing:0.08em;text-transform:uppercase;margin:16px 0 8px 0;'>● {ui['stopped']}</div>", unsafe_allow_html=True)
                for med in inactive:
                    _render_med_card(med, ui)


def _render_med_card(med: dict, ui: dict):
    timing_icons = {
        "Morning": "🌅",
        "Night": "🌙",
        "After Meals": "🍽️",
        "Before Meals": "🫙",
        "Twice Daily": "🔄",
    }
    icon = timing_icons.get(med.get("timing", ""), "⏰")
    is_active = med.get("active", True)

    with st.container():
        st.markdown(f"""
        <div style='background:#171717;border:1px solid #2d2d2d;border-radius:12px;padding:14px 16px;margin-bottom:10px;'>
            <div style='display:flex;justify-content:space-between;align-items:flex-start;'>
                <div>
                    <div style='font-weight:600;color:#ececec;font-size:0.95rem;margin-bottom:6px;'>
                        💊 {med['name']}
                    </div>
                    <div>
                        <span class='med-badge'>{med.get('dosage','')}</span>
                        <span class='time-badge'>{icon} {med.get('timing','')}</span>
                    </div>
                    <div style='font-size:0.78rem;color:#8e8ea0;margin-top:8px;'>
                        📅 Started: {med.get('added_date','')} &nbsp;·&nbsp; ⏱️ Duration: {med.get('duration','')}
                    </div>
                    {"<div style='font-size:0.78rem;color:#8e8ea0;margin-top:4px;'>📝 " + med['notes'] + "</div>" if med.get('notes') else ""}
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        btn_col1, btn_col2, _ = st.columns([1, 1, 3])
        with btn_col1:
            btn_label = f"⏹ {ui['stop']}" if is_active else f"▶ Resume"
            if st.button(btn_label, key=f"toggle_{med['id']}", use_container_width=True):
                toggle_medicine(med["id"])
                st.rerun()
        with btn_col2:
            if st.button(f"🗑️ {ui['delete']}", key=f"del_{med['id']}", use_container_width=True):
                delete_medicine(med["id"])
                st.rerun()
