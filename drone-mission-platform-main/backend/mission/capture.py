from drone.telemetry import fetch_latest_telemetry
from mission.state import is_mission_active, add_point, get_active_order_id

def capture_point_from_thingspeak():
    """
    Fetch latest GPS from ThingSpeak
    If mission is active → store point
    """

    if not is_mission_active():
        return None

    data = fetch_latest_telemetry()
    if not data:
        return None

    lat = data.get("lat")
    lng = data.get("lng")

    if lat is None or lng is None:
        return None

    add_point(lat, lng)

    return {
        "order_id": get_active_order_id(),
        "lat": lat,
        "lng": lng
    }
