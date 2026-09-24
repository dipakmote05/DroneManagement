import os
import requests
from dotenv import load_dotenv

load_dotenv()

CHANNEL_ID = os.getenv("THINGSPEAK_CHANNEL_ID")
READ_KEY = os.getenv("THINGSPEAK_READ_KEY")

THINGSPEAK_URL = f"https://api.thingspeak.com/channels/{CHANNEL_ID}/feeds.json"


def fetch_latest_telemetry():
    """
    Fetch latest telemetry from ThingSpeak.
    SAFE: Will not crash backend if ThingSpeak is down.
    """

    params = {
        "api_key": READ_KEY,
        "results": 1
    }

    try:
        response = requests.get(THINGSPEAK_URL, params=params, timeout=5)
        response.raise_for_status()
    except requests.RequestException as e:
        # Log this in real production
        print(f"[Telemetry Error] ThingSpeak fetch failed: {e}")
        return None

    data = response.json()
    feeds = data.get("feeds", [])

    if not feeds:
        return None

    feed = feeds[0]

    # -------------------------
    # TELEMETRY FIELD MAPPING
    # -------------------------
    # field1 -> latitude
    # field2 -> longitude
    # field3 -> battery %
    # field4 -> altitude (meters)
    # field5 -> AQI
    # field6 -> distance_front (meters)
    # field7 -> distance_bottom (meters)

    telemetry = {
        "lat": _safe_float(feed.get("field1")),
        "lng": _safe_float(feed.get("field2")),
        "battery": _safe_int(feed.get("field3")),
        "altitude": _safe_float(feed.get("field4")),
        "aqi": _safe_int(feed.get("field5")),
        "distance_front": _safe_float(feed.get("field6")),
        "distance_bottom": _safe_float(feed.get("field7")),
        "timestamp": feed.get("created_at")
    }

    return telemetry


# -------------------------
# SAFE CAST HELPERS
# -------------------------
def _safe_float(value):
    try:
        return float(value) if value is not None else None
    except (ValueError, TypeError):
        return None


def _safe_int(value):
    try:
        return int(float(value)) if value is not None else None
    except (ValueError, TypeError):
        return None
