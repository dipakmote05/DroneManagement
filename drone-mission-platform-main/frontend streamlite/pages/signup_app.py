import streamlit as st
import requests

API = "http://127.0.0.1:5000/api/auth"

# -------------------------
# PAGE CONFIG
# -------------------------
st.set_page_config(
    page_title="Drone Platform | Signup",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# -------------------------
# CSS : SAME AS LOGIN (TEXT FIXED)
# -------------------------
st.markdown("""
<style>

/* Hide Streamlit default UI */
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
.signup-card {
    background: rgba(255,255,255,0.12);
    backdrop-filter: blur(16px);
    padding: 38px;
    border-radius: 22px;
    box-shadow: 0 40px 80px rgba(0,0,0,0.55);
}

/* Title */
.signup-title {
    text-align: center;
    font-size: 28px;
    font-weight: 700;
    color: #bfdbfe;
}

.signup-sub {
    text-align: center;
    font-size: 14px;
    color: #c7d2fe;
    margin-bottom: 18px;
}

.step {
    text-align: center;
    font-size: 13px;
    color: #94a3b8;
    margin-bottom: 18px;
}

/* -------- INPUT FIX (MOST IMPORTANT) -------- */
.stTextInput input,
.stSelectbox select {
    background: #ffffff !important;   /* Light background */
    color: #000000 !important;        /* BLACK typed text */
    caret-color: #000000;
    border-radius: 14px;
    padding: 14px;
    font-size: 15px;
    border: 1px solid #cbd5e1;
}

/* Placeholder */
.stTextInput input::placeholder {
    color: #64748b !important;
    opacity: 1;
}

/* Focus */
.stTextInput input:focus,
.stSelectbox select:focus {
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
    font-size: 15px;
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
# SESSION STATE INIT
# -------------------------
if "step" not in st.session_state:
    st.session_state.step = 1

if "signup_data" not in st.session_state:
    st.session_state.signup_data = {}

if "identifier" not in st.session_state:
    st.session_state.identifier = ""

# -------------------------
# CENTER LAYOUT
# -------------------------
st.empty()
col1, col2, col3 = st.columns([1, 2, 1])

with col2:
    st.markdown("""
    <div class="signup-card">
        <div class="signup-title">🚁 Drone Platform</div>
        <div class="signup-sub">Create your account</div>
    </div>
    """, unsafe_allow_html=True)

    # ========================
    # STEP 1 – BASIC DETAILS
    # ========================
    if st.session_state.step == 1:
        st.markdown('<div class="step">Step 1 of 4 · Basic Details</div>', unsafe_allow_html=True)

        name = st.text_input("Full Name", placeholder="Enter your full name")
        email = st.text_input("Email", placeholder="Enter your email address")
        mobile = st.text_input("Mobile Number", placeholder="Enter your mobile number")
        role = st.selectbox("Select Role", ["", "client", "operator"])

        if st.button("Next ➡️"):
            if not name or not email or not mobile or not role:
                st.error("All fields including role are required")
            else:
                st.session_state.signup_data = {
                    "name": name,
                    "email": email,
                    "mobile": mobile,
                    "role": role
                }
                st.session_state.step = 2
                st.rerun()

    # ========================
    # STEP 2 – SEND OTP
    # ========================
    elif st.session_state.step == 2:
        st.markdown('<div class="step">Step 2 of 4 · OTP Verification</div>', unsafe_allow_html=True)

        if st.button("Send OTP via Email 📧"):
            st.session_state.identifier = st.session_state.signup_data["email"]

            with st.spinner("Sending OTP..."):
                res = requests.post(
                    API + "/send-otp",
                    json={"identifier": st.session_state.identifier}
                ).json()

            if "error" in res:
                st.error(res["error"])
            else:
                st.success("OTP sent successfully ✅")
                st.session_state.step = 3
                st.rerun()

    # ========================
    # STEP 3 – VERIFY OTP
    # ========================
    elif st.session_state.step == 3:
        st.markdown('<div class="step">Step 3 of 4 · Enter OTP</div>', unsafe_allow_html=True)

        otp = st.text_input("OTP", placeholder="Enter 6-digit OTP", max_chars=6)

        if st.button("Verify OTP"):
            if not otp:
                st.error("OTP required")
            else:
                with st.spinner("Verifying OTP..."):
                    res = requests.post(
                        API + "/verify-otp",
                        json={
                            "identifier": st.session_state.identifier,
                            "otp": otp
                        }
                    ).json()

                if "error" in res:
                    st.error(res["error"])
                else:
                    st.success("OTP verified ✅")
                    st.session_state.step = 4
                    st.rerun()

    # ========================
    # STEP 4 – PASSWORD
    # ========================
    elif st.session_state.step == 4:
        st.markdown('<div class="step">Step 4 of 4 · Set Password</div>', unsafe_allow_html=True)

        password = st.text_input(
            "Password",
            type="password",
            placeholder="Create a password"
        )
        confirm = st.text_input(
            "Confirm Password",
            type="password",
            placeholder="Re-enter password"
        )

        if st.button("Create Account 🎉"):
            if not password or not confirm:
                st.error("Password required")
            elif password != confirm:
                st.error("Passwords do not match")
            else:
                with st.spinner("Creating account..."):
                    res = requests.post(
                        API + "/signup",
                        json={
                            "name": st.session_state.signup_data["name"],
                            "email": st.session_state.signup_data["email"],
                            "password": password,
                            "role": st.session_state.signup_data["role"]
                        }
                    ).json()

                if "user_id" in res:
                    st.success("Signup successful 🎉")
                    st.balloons()

                    # Reset
                    st.session_state.step = 1
                    st.session_state.signup_data = {}
                    st.session_state.identifier = ""

                    st.switch_page("pages/login_app.py")
                else:
                    st.error(res.get("error", "Signup failed"))

    st.markdown('<div class="hr"></div>', unsafe_allow_html=True)

    if st.button("⬅️ Back to Login"):
        st.switch_page("pages/login_app.py")

st.empty()
