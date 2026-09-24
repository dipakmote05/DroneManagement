from datetime import datetime

from database import db
from drone.models import DroneTelemetry
from drone.telemetry import fetch_latest_telemetry
from orders.models import DroneOrder

from drone.mission_state import (
    get_active_mission,
    add_mission_point,
    init_navigation,
    MISSION_STATE
)


def fetch_and_store_telemetry():
    data = fetch_latest_telemetry()

    if not data or data.get("lat") is None or data.get("lng") is None:
        print("❌ No GPS data from ThingSpeak")
        return None

    active_mission = get_active_mission()

    # =================================================
    # 🔥 POINT CAPTURE (AUTO INIT FIX)
    # =================================================
    if active_mission:
        print(f"✅ Active mission: {active_mission.id}")
        print(f"📍 Capturing point: {data['lat']}, {data['lng']}")

        # 🔥 VERY IMPORTANT FIX
        if active_mission.id not in MISSION_STATE:
            print("♻️ STATE missing → auto init from DB")
            init_navigation(active_mission)

        add_mission_point(
            active_mission.id,
            data["lat"],
            data["lng"]
        )
    else:
        print("ℹ️ No active mission – skipping point capture")

    # =================================================
    # STORE TELEMETRY (ALWAYS)
    # =================================================
    telemetry = DroneTelemetry(
        order_id=active_mission.id if active_mission else None,
        lat=data["lat"],
        lng=data["lng"],
        battery=data.get("battery"),
        altitude=data.get("altitude"),
        aqi=data.get("aqi"),
        distance_front=data.get("distance_front"),
        distance_bottom=data.get("distance_bottom"),
        timestamp=_parse_timestamp(data.get("timestamp"))
    )

    db.session.add(telemetry)

    if active_mission:
        active_mission.drone_lat = data["lat"]
        active_mission.drone_lng = data["lng"]
        active_mission.last_telemetry_at = datetime.utcnow()

    try:
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        print(f"[DB ERROR] {e}")
        return None

    print(f"📡 Stored GPS: {data['lat']}, {data['lng']} | order={telemetry.order_id}")
    return telemetry


def _parse_timestamp(ts):
    try:
        if ts:
            return datetime.fromisoformat(ts.replace("Z", "+00:00"))
    except Exception:
        pass
    return datetime.utcnow()
