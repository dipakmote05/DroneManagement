import streamlit as st
import requests

API = "http://127.0.0.1:5000/api/orders"

# -------------------------
# PAGE CONFIG
# -------------------------
st.set_page_config(
    page_title="Mission Control",
    layout="centered"
)

# -------------------------
# 🔐 OPERATOR GUARD
# -------------------------
if "token" not in st.session_state or st.session_state.get("role") != "operator":
    st.session_state.clear()
    st.switch_page("pages/login_app.py")

token = st.session_state.token

st.title("🚁 Mission Control")

# -------------------------
# NAV
# -------------------------
col1, col2 = st.columns(2)
with col1:
    if st.button("⬅️ Back to Dashboard"):
        st.switch_page("pages/operator_dashboard.py")
with col2:
    if st.button("Logout 🔓"):
        st.session_state.clear()
        st.switch_page("pages/login_app.py")

st.markdown("---")

# =================================================
# API CALLS
# =================================================
def load_ready_mission():
    try:
        res = requests.get(
            API + "/my-ready",
            headers={"Authorization": f"Bearer {token}"},
            timeout=5
        )
        return res.json()
    except Exception:
        return None


def load_active_mission():
    try:
        res = requests.get(
            API + "/my-active",
            headers={"Authorization": f"Bearer {token}"},
            timeout=5
        )
        return res.json()
    except Exception:
        return None


# =================================================
# 🔥 LOAD MISSION (READY FIRST, THEN ACTIVE)
# =================================================
mission = load_ready_mission()

if not mission or "order_id" not in mission:
    mission = load_active_mission()

current_order_id = None
mission_status = None

# =================================================
# UI : MISSION DETAILS
# =================================================
if not mission or "order_id" not in mission:
    st.info("No mission assigned yet")
else:
    current_order_id = mission["order_id"]
    mission_status = mission.get("status", "ACCEPTED")

    st.markdown(
        f"""
        <div style="
            background:white;
            color:#020617;
            padding:25px;
            border-radius:14px;
            width:380px;
            margin:auto;
            box-shadow:0 10px 25px rgba(0,0,0,0.25);
        ">
            <h4>Mission Details</h4>
            <p><b>Status:</b> {mission_status}</p>
            <p><b>Client ID:</b> {mission.get('client_id')}</p>
            <p><b>Target:</b> {mission.get('lat') or mission.get('target_lat')},
                               {mission.get('lng') or mission.get('target_lng')}</p>
        </div>
        """,
        unsafe_allow_html=True
    )

st.markdown("")

# =================================================
# 🎯 MISSION ACTIONS
# =================================================
if current_order_id:

    # ---------- START MISSION ----------
    if mission_status == "ACCEPTED":
        st.success("Mission ready to start 🚀")

        if st.button("🚀 Start Mission"):
            try:
                res = requests.post(
                    API + f"/start/{current_order_id}",
                    headers={"Authorization": f"Bearer {token}"},
                    timeout=5
                ).json()

                st.success(res.get("message", "Mission started"))
                st.rerun()

            except Exception:
                st.error("Failed to start mission")

    # ---------- END MISSION ----------
    elif mission_status == "IN_PROGRESS":
        st.warning("Mission in progress…")

        if st.button("🛑 End Mission"):
            try:
                res = requests.post(
                    API + f"/end/{current_order_id}",
                    headers={"Authorization": f"Bearer {token}"},
                    timeout=5
                ).json()

                st.success(res.get("message", "Mission ended"))
                st.rerun()

            except Exception:
                st.error("Failed to end mission")

    # ---------- COMPLETED ----------
    elif mission_status == "COMPLETED":
        st.success("Mission already completed ✅")

else:
    st.info("Waiting for mission assignment…")
