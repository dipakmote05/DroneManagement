import streamlit as st
import requests
import pandas as pd
import time

API_BASE = "http://127.0.0.1:5000/api"

# =================================================
# PAGE CONFIG
# =================================================
st.set_page_config(
    page_title="Client Dashboard",
    layout="wide"
)

# =================================================
# 🔐 CLIENT GUARD
# =================================================
if "token" not in st.session_state or st.session_state.get("role") != "client":
    st.session_state.clear()
    st.switch_page("pages/login_app.py")

HEADERS = {
    "Authorization": f"Bearer {st.session_state.token}"
}

# =================================================
# NAVBAR
# =================================================
nav_left, nav_right = st.columns([8, 1])

with nav_left:
    st.markdown("## 🚁 Drone Platform – Client Dashboard")

with nav_right:
    if st.button("Logout 🔓"):
        st.session_state.clear()
        st.switch_page("pages/login_app.py")

st.markdown("---")

# =================================================
# API CALLS
# =================================================
def fetch_latest_order():
    try:
        r = requests.get(
            f"{API_BASE}/orders/my-latest",
            headers=HEADERS,
            timeout=5
        )
        if r.status_code == 200:
            return r.json()
    except Exception:
        pass
    return None


def fetch_telemetry():
    try:
        r = requests.get(
            f"{API_BASE}/drone/telemetry/latest",
            headers=HEADERS,
            timeout=5
        )
        if r.status_code == 200:
            return r.json()["data"]
    except Exception:
        pass
    return None


def fetch_mission_area():
    try:
        r = requests.get(
            f"{API_BASE}/drone/mission/area",
            headers=HEADERS,
            timeout=5
        )
        if r.status_code == 200:
            return r.json()
    except Exception:
        pass
    return None


# =================================================
# LOAD DATA
# =================================================
order = fetch_latest_order()
telemetry = fetch_telemetry()
area_data = fetch_mission_area()   # 🔥 always hit

# =================================================
# MISSION STATE (DB IS SOURCE OF TRUTH)
# =================================================
mission_active = False
mission_completed = False

if order:
    if order.get("status") == "IN_PROGRESS":
        mission_active = True
    elif order.get("status") == "COMPLETED":
        mission_completed = True

# =================================================
# TOP STATUS CARDS
# =================================================
if mission_active and telemetry:
    c1, c2, c3, c4 = st.columns(4)

    c1.metric("🔋 Battery", f"{telemetry.get('battery', '--')} %")
    c2.metric("🌫 AQI", telemetry.get("aqi", "--"))
    c3.metric("📐 Altitude", f"{telemetry.get('altitude', '--')} m")
    c4.metric("🕒 Last Update", telemetry.get("timestamp", "--"))

elif mission_completed:
    st.success("Mission completed successfully ✅")

else:
    st.info("Mission not started yet 🚁")

st.markdown("---")

# =================================================
# 🗺 LIVE DRONE LOCATION + PATH
# =================================================
st.subheader("🗺 Live Drone Location & Path")

if mission_active and telemetry and telemetry.get("lat") and telemetry.get("lng"):

    # 🔥 store full path
    if "path_points" not in st.session_state:
        st.session_state.path_points = []

    st.session_state.path_points.append({
        "lat": telemetry["lat"],
        "lon": telemetry["lng"]
    })

    map_df = pd.DataFrame(st.session_state.path_points)
    st.map(map_df, zoom=16)

elif mission_active:
    st.info("Waiting for GPS lock...")

else:
    st.info("Mission not active")

# =================================================
# 📈 LIVE TELEMETRY GRAPHS
# =================================================
st.markdown("---")
st.subheader("📈 Live Telemetry")

if mission_active and telemetry:

    if "telemetry_history" not in st.session_state:
        st.session_state.telemetry_history = []

    st.session_state.telemetry_history.append({
        "altitude": telemetry.get("altitude"),
        "battery": telemetry.get("battery")
    })

    df = pd.DataFrame(st.session_state.telemetry_history)

    g1, g2 = st.columns(2)

    with g1:
        st.caption("Altitude (m)")
        st.line_chart(df["altitude"], height=250)

    with g2:
        st.caption("Battery (%)")
        st.line_chart(df["battery"], height=250)

else:
    st.info("Graphs will appear once mission starts 🚀")

# =================================================
# 📐 MISSION COVERAGE AREA (LIVE + FINAL)
# =================================================
st.markdown("---")
st.subheader("📐 Mission Coverage Area")

if area_data and area_data.get("status") == "success":

    a1, a2, a3 = st.columns(3)

    a1.metric("📍 GPS Points", area_data.get("points_captured", 0))
    a2.metric("📐 Area (sq meters)", area_data.get("area_sq_meters", 0))
    a3.metric("🌾 Area (acres)", area_data.get("area_acres", 0))

    if mission_completed:
        st.success("Final mission area calculated ✅")
    else:
        st.info("Area updating live as drone moves ⏳")

elif mission_active:
    st.info("Waiting for sufficient GPS points…")

else:
    st.info("Area will be available after mission starts")

# =================================================
# REQUEST ACTIONS
# =================================================
st.markdown("---")
st.subheader("📦 Requests")

c1, c2 = st.columns(2)

with c1:
    if st.button("➕ Create New Drone Request"):
        st.switch_page("pages/new_request_page.py")

with c2:
    if st.button("📍 Track My Request"):
        st.switch_page("pages/track_drone.py")

# =================================================
# AUTO REFRESH
# =================================================
st.caption("🔄 Auto refresh every 5 seconds")
time.sleep(5)
st.rerun()
