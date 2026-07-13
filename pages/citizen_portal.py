"""
pages/citizen_portal.py
-----------------------
Citizen-facing portal:
  • Submit Complaint  — AI analysis + confidence + ticket generation
  • My Complaints     — Full history with status tracking
"""

import streamlit as st
import pandas as pd
from datetime import datetime

from auth.db import (
    submit_complaint, get_complaints_by_user, BANGALORE_REGIONS
)
from utils import load_models, predict_with_confidence

# ── CSS ────────────────────────────────────────────────────────────────────────
PORTAL_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');
html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
.stApp { background: linear-gradient(160deg,#060d1f 0%,#0d2137 60%,#091a2e 100%); }
#MainMenu, footer, header { visibility: hidden; }

/* Sidebar */
[data-testid="stSidebar"] {
    background: rgba(6,13,31,0.95) !important;
    border-right: 1px solid rgba(255,255,255,0.07);
}
[data-testid="stSidebar"] * { color: #cbd5e1 !important; }

/* Page title */
.page-title { font-size:1.9rem; font-weight:800;
    background:linear-gradient(90deg,#38bdf8,#818cf8);
    -webkit-background-clip:text; -webkit-text-fill-color:transparent; margin-bottom:4px; }
.page-sub   { color:#64748b; font-size:.9rem; margin-bottom:24px; }

/* Cards */
.metric-card {
    background:rgba(255,255,255,0.04); border:1px solid rgba(255,255,255,0.09);
    border-radius:14px; padding:20px 18px; text-align:center;
}
.metric-card .val { font-size:2rem; font-weight:700; color:#38bdf8; }
.metric-card .lbl { font-size:.8rem; color:#64748b; margin-top:2px; }

/* Result card */
.result-card {
    background:rgba(255,255,255,0.04); border:1px solid rgba(255,255,255,0.1);
    border-radius:16px; padding:24px; margin-top:18px;
}
.result-card h4 { color:#94a3b8; font-size:.8rem; font-weight:500;
    text-transform:uppercase; letter-spacing:.05em; margin:0 0 4px 0; }
.result-card .big { font-size:1.4rem; font-weight:700; color:#f1f5f9; margin:0; }

/* Ticket badge */
.ticket-badge {
    display:inline-block; background:linear-gradient(135deg,#0ea5e9,#6366f1);
    color:white; font-weight:700; font-size:1rem;
    border-radius:10px; padding:8px 18px; letter-spacing:.04em;
}

/* Priority colours */
.pri-high   { color:#f87171 !important; }
.pri-medium { color:#fbbf24 !important; }
.pri-low    { color:#34d399 !important; }

/* Status badges */
.badge {
    display:inline-block; padding:3px 10px; border-radius:999px;
    font-size:.75rem; font-weight:600;
}
.badge-pending    { background:rgba(251,191,36,.15);  color:#fbbf24; }
.badge-progress   { background:rgba(99,102,241,.15);  color:#818cf8; }
.badge-resolved   { background:rgba(52,211,153,.15);  color:#34d399; }

/* Progress bar wrapper */
.conf-bar-wrap { background:rgba(255,255,255,0.07); border-radius:999px;
    height:8px; width:100%; margin-top:4px; overflow:hidden; }
.conf-bar-fill { height:8px; border-radius:999px;
    background:linear-gradient(90deg,#0ea5e9,#6366f1); }

/* Inputs */
.stTextArea textarea, .stSelectbox > div > div > div {
    background:rgba(255,255,255,0.05) !important;
    border:1px solid rgba(255,255,255,0.1) !important;
    border-radius:10px !important; color:#e2e8f0 !important;
}
.stTextArea label, .stSelectbox label { color:#94a3b8 !important; }

/* Buttons */
.stButton > button {
    background:linear-gradient(135deg,#0ea5e9,#6366f1) !important;
    color:white !important; border:none !important;
    border-radius:12px !important; font-weight:600 !important;
    transition:opacity .2s !important;
}
.stButton > button:hover { opacity:.85 !important; }

/* Table */
.stDataFrame { border-radius:12px; overflow:hidden; }

/* Divider */
hr { border-color:rgba(255,255,255,0.07) !important; }
</style>
"""

# ── Model (cached globally) ────────────────────────────────────────────────────
@st.cache_resource
def _get_models():
    return load_models()


# ── Helpers ────────────────────────────────────────────────────────────────────
def _status_badge(status):
    cls = {"Pending": "badge-pending",
           "In Progress": "badge-progress",
           "Resolved": "badge-resolved"}.get(status, "badge-pending")
    return f'<span class="badge {cls}">{status}</span>'


def _priority_class(p):
    return {"High": "pri-high", "Medium": "pri-medium", "Low": "pri-low"}.get(p, "")


def _conf_bar(pct):
    return (f'<div class="conf-bar-wrap">'
            f'<div class="conf-bar-fill" style="width:{pct:.0f}%"></div>'
            f'</div>')


# ── Main entry ─────────────────────────────────────────────────────────────────
def show_citizen_portal():
    st.markdown(PORTAL_CSS, unsafe_allow_html=True)

    user       = st.session_state.user
    vectorizer, cat_model, pri_model = _get_models()
    models_ok  = vectorizer is not None

    # ── Sidebar ───────────────────────────────────────────────────────────────
    with st.sidebar:
        st.markdown(f"### 👤 {user['full_name']}")
        st.caption(user['email'])
        st.markdown("---")
        page = st.radio("Navigate", ["📝 Submit Complaint", "📋 My Complaints"], label_visibility="collapsed")
        st.markdown("---")
        if st.button("🚪 Logout"):
            st.session_state.logged_in = False
            st.session_state.user      = None
            st.rerun()
        st.markdown("---")
        st.caption("💧 AquaIntel · Citizen Portal\nSmart City Water Governance")

    # ── Page routing ──────────────────────────────────────────────────────────
    if page == "📝 Submit Complaint":
        _page_submit(user, vectorizer, cat_model, pri_model, models_ok)
    else:
        _page_history(user)


# ── Submit Complaint page ──────────────────────────────────────────────────────
def _page_submit(user, vectorizer, cat_model, pri_model, models_ok):
    st.markdown('<p class="page-title">📝 Submit a Complaint</p>', unsafe_allow_html=True)
    st.markdown('<p class="page-sub">Describe your water-related issue. Our AI will classify it and assign priority automatically.</p>', unsafe_allow_html=True)

    if not models_ok:
        st.error("⚠️ AI models not found. Please ask the admin to run the training script.")
        return

    with st.form("complaint_form", clear_on_submit=False):
        complaint_text = st.text_area(
            "Describe your complaint",
            height=160,
            placeholder=(
                "e.g. Water leaking continuously near the main road in our area...\n"
                "     Neeru bartha illa since 2 days...\n"
                "     ನಮ್ಮ ಪ್ರದೇಶದಲ್ಲಿ ನೀರಿನ ಒತ್ತಡ ಕಡಿಮೆಯಾಗಿದೆ."
            )
        )
        location = st.selectbox("📍 Your Location (Bangalore)", BANGALORE_REGIONS)
        submitted = st.form_submit_button("🔍 Analyse & Submit Complaint")

    if submitted:
        if not complaint_text.strip():
            st.warning("Please describe your complaint before submitting.")
            return

        with st.spinner("Analysing complaint with NLP pipeline..."):
            cat, pri, conf_cat, conf_pri, cat_dict, pri_dict = predict_with_confidence(
                complaint_text, vectorizer, cat_model, pri_model
            )

        # Low-confidence warning
        if conf_cat < 55:
            st.warning("⚠️ Low confidence — the model is uncertain. Please add more detail for better classification.")

        # ── Prediction result cards ───────────────────────────────────────────
        st.markdown("### 🤖 AI Analysis Results")
        c1, c2 = st.columns(2)

        with c1:
            st.markdown(f"""
            <div class="result-card">
                <h4>Predicted Category</h4>
                <p class="big">{cat}</p>
                <div style="margin-top:10px; font-size:.8rem; color:#64748b;">Confidence: {conf_cat:.1f}%</div>
                {_conf_bar(conf_cat)}
            </div>""", unsafe_allow_html=True)

        with c2:
            pc = _priority_class(pri)
            st.markdown(f"""
            <div class="result-card">
                <h4>Assigned Priority</h4>
                <p class="big {pc}">{pri}</p>
                <div style="margin-top:10px; font-size:.8rem; color:#64748b;">Confidence: {conf_pri:.1f}%</div>
                {_conf_bar(conf_pri)}
            </div>""", unsafe_allow_html=True)

        # ── Category probability breakdown ────────────────────────────────────
        with st.expander("📊 Full probability breakdown"):
            col_a, col_b = st.columns(2)
            with col_a:
                st.markdown("**Category Probabilities**")
                for label, prob in sorted(cat_dict.items(), key=lambda x: -x[1]):
                    st.markdown(f"`{label}` — **{prob}%**")
                    st.progress(prob / 100)
            with col_b:
                st.markdown("**Priority Probabilities**")
                for label, prob in sorted(pri_dict.items(), key=lambda x: -x[1]):
                    st.markdown(f"`{label}` — **{prob}%**")
                    st.progress(prob / 100)

        # ── Save to database ──────────────────────────────────────────────────
        ticket_id = submit_complaint(
            user_id        = user['id'],
            complaint_text = complaint_text.strip(),
            location       = location,
            category       = cat,
            priority       = pri,
            conf_cat       = round(conf_cat, 2),
            conf_pri       = round(conf_pri, 2)
        )

        st.markdown("---")
        st.success("✅ Complaint submitted successfully!")
        st.markdown(f"""
        <div style="text-align:center; margin:12px 0;">
            <div style="color:#94a3b8; font-size:.85rem; margin-bottom:8px;">Your Ticket ID</div>
            <span class="ticket-badge">{ticket_id}</span>
            <div style="color:#64748b; font-size:.8rem; margin-top:10px;">
                Save this ID to track your complaint status in <b>My Complaints</b>.
            </div>
        </div>
        """, unsafe_allow_html=True)


# ── My Complaints (history) page ───────────────────────────────────────────────
def _page_history(user):
    st.markdown('<p class="page-title">📋 My Complaints</p>', unsafe_allow_html=True)
    st.markdown('<p class="page-sub">Track all complaints you have submitted and their current resolution status.</p>', unsafe_allow_html=True)

    complaints = get_complaints_by_user(user['id'])

    if not complaints:
        st.info("You haven't submitted any complaints yet. Go to **Submit Complaint** to get started.")
        return

    # ── Summary metric row ────────────────────────────────────────────────────
    total    = len(complaints)
    pending  = sum(1 for c in complaints if c['status'] == 'Pending')
    progress = sum(1 for c in complaints if c['status'] == 'In Progress')
    resolved = sum(1 for c in complaints if c['status'] == 'Resolved')

    m1, m2, m3, m4 = st.columns(4)
    for col, val, lbl in [
        (m1, total, "Total Submitted"),
        (m2, pending, "Pending"),
        (m3, progress, "In Progress"),
        (m4, resolved, "Resolved"),
    ]:
        col.markdown(f"""
        <div class="metric-card">
            <div class="val">{val}</div>
            <div class="lbl">{lbl}</div>
        </div>""", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Filter bar ────────────────────────────────────────────────────────────
    fc1, fc2 = st.columns([2, 1])
    with fc1:
        status_filter = st.selectbox("Filter by Status", ["All", "Pending", "In Progress", "Resolved"], key="hist_status")
    with fc2:
        sort_order = st.selectbox("Sort by", ["Newest First", "Oldest First"], key="hist_sort")

    filtered = complaints
    if status_filter != "All":
        filtered = [c for c in filtered if c['status'] == status_filter]
    if sort_order == "Oldest First":
        filtered = list(reversed(filtered))

    st.markdown(f"**{len(filtered)} complaint(s) found**")
    st.markdown("---")

    # ── Individual complaint cards ─────────────────────────────────────────────
    for c in filtered:
        date_str = c['submitted_at'][:10] if c['submitted_at'] else "—"
        pc       = _priority_class(c['priority'])
        badge    = _status_badge(c['status'])

        st.markdown(f"""
        <div style="background:rgba(255,255,255,0.04); border:1px solid rgba(255,255,255,0.08);
                    border-radius:14px; padding:20px; margin-bottom:14px;">
            <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:10px;">
                <span style="font-family:monospace; font-weight:700; color:#38bdf8; font-size:.95rem;">
                    🎫 {c['ticket_id']}
                </span>
                {badge}
            </div>
            <p style="color:#cbd5e1; margin:0 0 10px 0; line-height:1.6;">"{c['complaint_text']}"</p>
            <div style="display:flex; gap:18px; flex-wrap:wrap; font-size:.82rem; color:#64748b;">
                <span>📍 {c['location']}</span>
                <span>🏷️ {c['category']}</span>
                <span class="{pc}">⚡ {c['priority']} Priority</span>
                <span>📅 {date_str}</span>
                <span>🎯 Cat. confidence: {c['confidence_category']:.1f}%</span>
            </div>
            {"" if not c['resolution_note'] else
             f'<div style="margin-top:12px; padding:10px; background:rgba(52,211,153,.08); border-radius:8px; '
             f'border-left:3px solid #34d399; color:#a7f3d0; font-size:.85rem;">'
             f'<b>Resolution Note:</b> {c["resolution_note"]}</div>'}
        </div>
        """, unsafe_allow_html=True)
