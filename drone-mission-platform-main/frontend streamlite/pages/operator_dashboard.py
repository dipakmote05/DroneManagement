import streamlit as st
import time

# -------------------------
# PAGE CONFIG
# -------------------------
st.set_page_config(
    page_title="Drone Operator Dashboard",
    layout="wide"
)

# -------------------------
# 🔐 OPERATOR GUARD
# -------------------------
if "token" not in st.session_state or st.session_state.get("role") != "operator":
    st.session_state.clear()
    st.switch_page("pages/login_app.py")

# -------------------------
# NAVBAR
# -------------------------
col1, col2 = st.columns([8, 1])

with col1:
    st.markdown("## 🛰️ Drone Operator Dashboard")

with col2:
    if st.button("Logout 🔓"):
        st.session_state.clear()
        st.switch_page("pages/login_app.py")

st.markdown("---")

# -------------------------
# DASHBOARD CARDS
# -------------------------
colA, colB = st.columns(2)

with colA:
    st.markdown(
        """
        <div style="background:white;padding:25px;border-radius:14px;
        box-shadow:0 15px 30px rgba(0,0,0,0.3);">
            <h3>📋 Requests</h3>
            <p>Accept / Reject client requests</p>
        </div>
        """,
        unsafe_allow_html=True
    )
    if st.button("Open Requests"):
        st.switch_page("pages/requests_page.py")

with colB:
    st.markdown(
        """
        <div style="background:white;padding:25px;border-radius:14px;
        box-shadow:0 15px 30px rgba(0,0,0,0.3);">
            <h3>🚁 Mission</h3>
            <p>Active drone mission</p>
        </div>
        """,
        unsafe_allow_html=True
    )
    if st.button("Open Mission"):
        st.switch_page("pages/mission_page.py")

# -------------------------
# LIVE DRONE FEED
# -------------------------
st.markdown("---")
st.markdown("## 📹 Live Drone Feed")

left, right = st.columns([2, 3])

# ---- LEFT : STATUS ----
with left:
    st.markdown(
        """
        <div style="background:#020617;color:white;padding:20px;
        border-radius:16px;box-shadow:0 15px 30px rgba(0,0,0,0.4);">
            <h4>🚁 Drone Status</h4>
            <ul>
                <li>🟢 Connection: Active</li>
                <li>📡 GPS: Locked</li>
                <li>🔋 Battery: 82%</li>
                <li>📏 Altitude: 12 m</li>
                <li>🧭 Mode: AUTO</li>
            </ul>
        </div>
        """,
        unsafe_allow_html=True
    )

# ---- RIGHT : VIDEO (NO IFRAME ❌) ----
with right:
    st.markdown(
        """
        <div style="background:black;padding:15px;border-radius:16px;
        box-shadow:0 15px 30px rgba(0,0,0,0.4);">
        """,
        unsafe_allow_html=True
    )

    video_box = st.empty()

    if "stream_on" not in st.session_state:
        st.session_state.stream_on = True

    colX, colY = st.columns(2)
    with colX:
        if st.button("⏸ Stop Video"):
            st.session_state.stream_on = False
    with colY:
        if st.button("▶ Start Video"):
            st.session_state.stream_on = True

    while st.session_state.stream_on:
        video_box.image(
            "http://192.168.1.13",  # ESP32 snapshot URL
            use_container_width=True
        )
        time.sleep(0.2)  # ~5 FPS
