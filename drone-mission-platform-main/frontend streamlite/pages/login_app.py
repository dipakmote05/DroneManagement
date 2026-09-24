import streamlit as st
import requests
import re

API = "http://127.0.0.1:5000/api/auth"

# -------------------------
# PAGE CONFIG
# -------------------------
st.set_page_config(
    page_title="Drone Platform | Login",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# -------------------------
# CSS (TEXT VISIBILITY FIXED)
# -------------------------
st.markdown("""
<style>

/* Hide Streamlit UI */
[data-testid="stHeader"],
[data-testid="stToolbar"],
footer {
    display: none;
}

/* Background */
html, body, [data-testid="stAppViewContainer"] {
    background: linear-gradient(135deg, #020617, #0f172a);
    font-family: 'Inter', sans-serif;
}

/* Card */
.login-card {
    background: rgba(255,255,255,0.12);
    backdrop-filter: blur(16px);
    padding: 36px;
    border-radius: 22px;
    box-shadow: 0 40px 80px rgba(0,0,0,0.55);
}

/* Title */
.login-title {
    text-align: center;
    font-size: 28px;
    font-weight: 700;
    color: #bfdbfe;
}

.login-sub {
    text-align: center;
    font-size: 14px;
    color: #c7d2fe;
    margin-bottom: 22px;
}

/* -------- INPUT FIX (IMPORTANT) -------- */
.stTextInput input {
    background: #ffffff !important;   /* Light background */
    color: #000000 !important;        /* BLACK typed text */
    caret-color: #000000;             /* Cursor black */
    border-radius: 14px;
    padding: 14px;
    font-size: 15px;
    border: 1px solid #cbd5e1;
}

/* Placeholder */
.stTextInput input::placeholder {
    color: #64748b !important;        /* Grey placeholder */
    opacity: 1;
}

/* Focus */
.stTextInput input:focus {
    outline: none;
    border: 1px solid #2563eb;
    box-shadow: 0 0 0 3px rgba(37,99,235,0.25);
}

/* Buttons */
.stButton {
    display: flex;
    justify-content: center;
}

.stButton button {
    width: 100%;
    border-radius: 14px;
    padding: 14px;
    font-size: 16px;
    font-weight: 600;
    background: linear-gradient(135deg, #2563eb, #1e40af);
    color: white;
    border: none;
}

.hr {
    height: 1px;
    background: rgba(255,255,255,0.25);
    margin: 22px 0;
}

</style>
""", unsafe_allow_html=True)

# -------------------------
# AUTO REDIRECT
# -------------------------
if "token" in st.session_state:
    if st.session_state.role == "client":
        st.switch_page("pages/client_dashboard.py")
    elif st.session_state.role == "operator":
        st.switch_page("pages/operator_dashboard.py")

# -------------------------
# CENTER LAYOUT
# -------------------------
st.empty()
col1, col2, col3 = st.columns([1, 2, 1])

with col2:
    st.markdown("""
    <div class="login-card">
        <div class="login-title">🚁 Drone Platform</div>
        <div class="login-sub">Secure access to your drone operations</div>
    </div>
    """, unsafe_allow_html=True)

    email = st.text_input(
        "Email",
        placeholder="Enter your email address"
    )

    password = st.text_input(
        "Password",
        type="password",
        placeholder="Enter your password"
    )

    if st.button("Login 🔐"):
        if not email or not password:
            st.error("Email and password required")
        elif not re.match(r"^[^@\s]+@[^@\s]+\.[^@\s]+$", email):
            st.error("Invalid email address")
        else:
            with st.spinner("Authenticating..."):
                res = requests.post(
                    API + "/login",
                    json={"email": email, "password": password}
                ).json()

            if "token" not in res:
                st.error("Login failed")
            else:
                st.session_state.token = res["token"]
                st.session_state.role = res["role"]
                st.session_state.user_id = res["user_id"]

                if res["role"] == "client":
                    st.switch_page("pages/client_dashboard.py")
                else:
                    st.switch_page("pages/operator_dashboard.py")

    st.markdown('<div class="hr"></div>', unsafe_allow_html=True)

    if st.button("✨ Create New Account"):
        st.switch_page("pages/signup_app.py")

st.empty()
