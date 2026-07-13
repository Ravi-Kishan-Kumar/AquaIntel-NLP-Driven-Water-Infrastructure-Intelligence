"""
app.py — AquaIntel Entry Point
Handles DB init, session state, and routes to the correct portal.
"""
import streamlit as st

# ── Page config (must be first Streamlit call) ─────────────────────────────────
st.set_page_config(
    page_title="AquaIntel — Water Complaint Intelligence",
    page_icon="💧",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ── DB initialisation ──────────────────────────────────────────────────────────
from auth.db import init_db
init_db()

# ── Session state defaults ─────────────────────────────────────────────────────
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "user" not in st.session_state:
    st.session_state.user = None

# ── Routing ────────────────────────────────────────────────────────────────────
if not st.session_state.logged_in:
    from auth.auth_ui import show_auth_page
    show_auth_page()
else:
    role = st.session_state.user["role"]
    if role == "citizen":
        from pages.citizen_portal import show_citizen_portal
        show_citizen_portal()
    else:
        from pages.authority_portal import show_authority_portal
        show_authority_portal()
