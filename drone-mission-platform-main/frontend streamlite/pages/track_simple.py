import streamlit as st
import requests
import time

API = "http://127.0.0.1:5000/api/orders"

st.set_page_config(
    page_title="Track Drone",
    layout="centered"
)

# -------------------------
# 🔐 CLIENT GUARD
# -------------------------
if "token" not in st.session_state or st.session_state.get("role") != "client":
    st.session_state.clear()
    st.switch_page("pages/login_app.py")

token = st.session_state.token

# -------------------------
# UI
# -------------------------
st.title("📍 Track Drone")

status_box = st.empty()
map_box = st.empty()

col1, col2 = st.columns(2)
with col1:
    refresh = st.button("🔄 Refresh Status")
with col2:
    back = st.button("⬅️ Back to Dashboard")

# -------------------------
# LOAD STATUS
# -------------------------
def load_status():
    try:
        res = requests.get(
            API + "/my-latest",
            headers={"Authorization": f"Bearer {token}"}
        )
        return res.json()
    except Exception:
        return {"error": "Server error"}


def render():
    data = load_status()

    if "error" in data:
        status_box.error("No active request")
        map_box.info("Waiting for request...")
        return

    status = data.get("status", "UNKNOWN")

    if status == "IN_PROGRESS":
        status_box.success(f"Status: {status}")
    elif status == "ACCEPTED":
        status_box.warning(f"Status: {status}")
    elif status == "COMPLETED":
        status_box.info(f"Status: {status}")
    else:
        status_box.error(f"Status: {status}")

    if data.get("lat") and data.get("lng"):
        map_box.markdown(
            f"""
            **🚁 Drone Location**
            - **Latitude:** {data['lat']}
            - **Longitude:** {data['lng']}
            """
        )
    else:
        map_box.info("Waiting for drone location...")


# -------------------------
# INITIAL LOAD (SAFE)
# -------------------------
if "track_loaded" not in st.session_state:
    st.session_state.track_loaded = True
    render()

# -------------------------
# MANUAL REFRESH
# -------------------------
if refresh:
    render()

# -------------------------
# BACK NAVIGATION
# -------------------------
if back:
    st.switch_page("pages/client_dashboard.py")

# -------------------------
# AUTO REFRESH (SAFE)
# -------------------------
time.sleep(5)
st.rerun()
