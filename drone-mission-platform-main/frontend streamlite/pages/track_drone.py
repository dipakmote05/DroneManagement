import streamlit as st
import requests
import pandas as pd
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

st.title("📍 Track Drone")

status_placeholder = st.empty()
map_placeholder = st.empty()

col1, col2 = st.columns(2)
with col1:
    refresh_btn = st.button("🔄 Refresh Status")
with col2:
    back_btn = st.button("⬅️ Back to Dashboard")

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


# -------------------------
# RENDER MAP
# -------------------------
def render_map(data):
    rows = []

    # 🎯 Target location
    if data.get("target_lat") and data.get("target_lng"):
        rows.append({
            "lat": data["target_lat"],
            "lon": data["target_lng"]
        })

    # 🚁 Drone location
    if data.get("drone_lat") and data.get("drone_lng"):
        rows.append({
            "lat": data["drone_lat"],
            "lon": data["drone_lng"]
        })

    if rows:
        df = pd.DataFrame(rows)
        map_placeholder.map(df, zoom=15)
    else:
        map_placeholder.info("Location data not available")


# -------------------------
# MAIN UI UPDATE
# -------------------------
def update_ui():
    data = load_status()

    if "error" in data:
        status_placeholder.error("No active request")
        map_placeholder.info("Waiting for request...")
        return

    status = data.get("status", "UNKNOWN")

    if status == "IN_PROGRESS":
        status_placeholder.success(f"Status: {status}")
    elif status == "ACCEPTED":
        status_placeholder.warning(f"Status: {status}")
    elif status == "COMPLETED":
        status_placeholder.info(f"Status: {status}")
    else:
        status_placeholder.error(f"Status: {status}")

    render_map(data)


# -------------------------
# INITIAL LOAD (SAFE)
# -------------------------
if "track_loaded" not in st.session_state:
    st.session_state.track_loaded = True
    update_ui()

# -------------------------
# MANUAL REFRESH
# -------------------------
if refresh_btn:
    update_ui()

# -------------------------
# BACK NAVIGATION
# -------------------------
if back_btn:
    st.switch_page("pages/client_dashboard.py")

# -------------------------
# AUTO REFRESH (SAFE)
# -------------------------
time.sleep(5)
st.rerun()
