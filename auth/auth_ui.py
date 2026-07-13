"""
auth/auth_ui.py
---------------
Premium Login / Registration page for the Water Complaint Analyzer.
Two roles: Citizen  |  Authority (requires secret code)
"""

import streamlit as st
from auth.db import create_user, verify_login, AUTHORITY_CODE


# ── Shared CSS injected once ───────────────────────────────────────────────────
AUTH_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');

html, body, [class*="css"] { font-family: 'Inter', sans-serif; }

/* Full-page dark gradient */
.stApp {
    background: linear-gradient(135deg, #060d1f 0%, #0d2137 45%, #091a2e 100%);
    min-height: 100vh;
}

/* Hide default Streamlit chrome */
#MainMenu, footer, header { visibility: hidden; }

/* Hero banner */
.auth-hero {
    text-align: center;
    padding: 40px 20px 10px 20px;
}
.auth-hero .brand {
    font-size: 2.8rem;
    font-weight: 800;
    background: linear-gradient(90deg, #38bdf8, #818cf8);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    margin: 0;
}
.auth-hero .tagline {
    color: #64748b;
    font-size: 1rem;
    margin-top: 6px;
}

/* Glass card */
.glass-card {
    background: rgba(255,255,255,0.04);
    border: 1px solid rgba(255,255,255,0.09);
    border-radius: 20px;
    padding: 36px 32px;
    backdrop-filter: blur(18px);
    max-width: 480px;
    margin: 0 auto 40px auto;
}

/* Streamlit tab override */
.stTabs [data-baseweb="tab-list"] {
    background: rgba(255,255,255,0.05);
    border-radius: 12px;
    padding: 4px;
    gap: 4px;
}
.stTabs [data-baseweb="tab"] {
    color: #94a3b8;
    border-radius: 10px;
    font-weight: 500;
    font-size: 0.92rem;
}
.stTabs [aria-selected="true"] {
    background: rgba(56,189,248,0.15) !important;
    color: #38bdf8 !important;
}

/* Input overrides */
.stTextInput > div > div > input,
.stSelectbox > div > div > div {
    background: rgba(255,255,255,0.06) !important;
    border: 1px solid rgba(255,255,255,0.12) !important;
    border-radius: 10px !important;
    color: #e2e8f0 !important;
    font-family: 'Inter', sans-serif !important;
}
.stTextInput label, .stSelectbox label { color: #94a3b8 !important; font-size: 0.85rem !important; }

/* Primary button */
.stButton > button {
    background: linear-gradient(135deg, #0ea5e9, #6366f1) !important;
    color: white !important;
    border: none !important;
    border-radius: 12px !important;
    font-weight: 600 !important;
    font-size: 0.95rem !important;
    padding: 0.6rem 1.5rem !important;
    width: 100% !important;
    transition: opacity 0.2s !important;
}
.stButton > button:hover { opacity: 0.88 !important; }

/* Info / warning / success boxes */
.stAlert { border-radius: 10px !important; }

/* Role badge row */
.role-info {
    display: flex; gap: 10px; margin: 10px 0 18px 0;
}
.role-badge {
    flex: 1; padding: 12px; border-radius: 12px;
    text-align: center; font-size: 0.82rem; font-weight: 500;
    border: 1px solid rgba(255,255,255,0.1);
}
.role-badge.citizen  { background: rgba(16,185,129,0.1); color: #34d399; border-color: #34d39940; }
.role-badge.authority{ background: rgba(99,102,241,0.1); color: #818cf8; border-color: #818cf840; }
</style>
"""


def show_auth_page():
    """Render the full login / registration screen."""
    st.markdown(AUTH_CSS, unsafe_allow_html=True)

    # ── Hero ──────────────────────────────────────────────────────────────────
    st.markdown("""
    <div class="auth-hero">
        <p class="brand">💧 AquaIntel</p>
        <p class="tagline">NLP-Powered Water Complaint Intelligence · Smart City Governance</p>
    </div>
    """, unsafe_allow_html=True)

    # ── Role info badges ──────────────────────────────────────────────────────
    st.markdown("""
    <div class="role-info" style="max-width:480px;margin:0 auto 6px auto;">
        <div class="role-badge citizen">🧑 Citizen<br><span style="opacity:.7">Submit &amp; Track Complaints</span></div>
        <div class="role-badge authority">🏛️ Authority<br><span style="opacity:.7">Manage &amp; Analyse Data</span></div>
    </div>
    """, unsafe_allow_html=True)

    # ── Centred card via columns ──────────────────────────────────────────────
    _, col, _ = st.columns([1, 2, 1])
    with col:
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        tab_login, tab_register = st.tabs(["🔑  Login", "📝  Register"])

        with tab_login:
            _login_form()

        with tab_register:
            _register_form()

        st.markdown('</div>', unsafe_allow_html=True)


# ── Private helpers ────────────────────────────────────────────────────────────

def _login_form():
    st.markdown("<br>", unsafe_allow_html=True)
    email    = st.text_input("Email address", key="li_email",    placeholder="you@example.com")
    password = st.text_input("Password",      key="li_password", type="password", placeholder="••••••••")
    st.markdown("<br>", unsafe_allow_html=True)

    if st.button("Login →", key="btn_login"):
        if not email or not password:
            st.warning("Please fill in all fields.")
            return
        user = verify_login(email.strip(), password)
        if user:
            st.session_state.logged_in = True
            st.session_state.user      = user
            st.rerun()
        else:
            st.error("❌ Invalid email or password.")


def _register_form():
    st.markdown("<br>", unsafe_allow_html=True)
    full_name = st.text_input("Full Name",    key="rg_name",  placeholder="Ravi Kumar")
    email     = st.text_input("Email",        key="rg_email", placeholder="you@example.com")
    phone     = st.text_input("Phone (opt.)", key="rg_phone", placeholder="+91 98XXXXXXXX")
    password  = st.text_input("Password",     key="rg_pass",  type="password", placeholder="Min. 6 characters")
    confirm   = st.text_input("Confirm Password", key="rg_confirm", type="password", placeholder="Repeat password")

    role = st.selectbox("Register As", ["Citizen", "Authority"], key="rg_role")

    auth_code = ""
    if role == "Authority":
        st.info("🏛️ Authority accounts require a secret registration code issued by the department.")
        auth_code = st.text_input("Authority Code", key="rg_authcode", type="password", placeholder="Enter code")

    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("Create Account →", key="btn_register"):
        if not all([full_name, email, password, confirm]):
            st.warning("Please fill in all required fields.")
            return
        if len(password) < 6:
            st.warning("Password must be at least 6 characters.")
            return
        if password != confirm:
            st.error("Passwords do not match.")
            return
        if role == "Authority" and auth_code != AUTHORITY_CODE:
            st.error("❌ Invalid authority code. Contact your department admin.")
            return

        ok, msg = create_user(full_name.strip(), email.strip(),
                              password, role.lower(), phone.strip())
        if ok:
            st.success(f"✅ {msg}")
        else:
            st.error(f"❌ {msg}")
