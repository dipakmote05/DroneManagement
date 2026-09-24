from orders.models import DroneOrder
from drone.navigation import generate_square_waypoints
from utils.geo import haversine_distance

# =================================================
# 🔥 SINGLE GLOBAL IN-MEMORY STATE
# =================================================
MISSION_STATE = {}

# 🔥 TEST MODE → ThingSpeak static GPS साठी
# production मध्ये False कर
TESTING_MODE = True


# =================================================
# ACTIVE MISSION (DB = SOURCE OF TRUTH)
# =================================================
def get_active_mission():
    return DroneOrder.query.filter_by(status="IN_PROGRESS").first()


# =================================================
# INIT MISSION (CALL ONLY ON /orders/start)
# =================================================
def init_navigation(order):
    waypoints = generate_square_waypoints(
        order.latitude,
        order.longitude
    )

    MISSION_STATE[order.id] = {
        "waypoints": waypoints,
        "current_index": 0,
        "points": [],
        "active": True
    }

    print("🚀 MISSION INITIALIZED")
    print("🆔 ORDER ID:", order.id)
    print("📦 CURRENT STATE KEYS:", list(MISSION_STATE.keys()))


def add_mission_point(order_id, lat, lng, min_distance=0.5):
    """
    FINAL RULES:
    - First point ALWAYS added
    - Same GPS (duplicate) NEVER added
    - TEST MODE → distance ignore, but duplicate block
    - PROD MODE → min_distance check
    """

    state = MISSION_STATE.get(order_id)

    if not state:
        print("❌ STATE NOT FOUND – order:", order_id)
        return

    if not state["active"]:
        print("❌ MISSION NOT ACTIVE – order:", order_id)
        return

    points = state["points"]

    # -------------------------
    # FIRST POINT
    # -------------------------
    if not points:
        points.append((lat, lng))
        print(f"📍 FIRST POINT ADDED → {lat}, {lng}")
        return

    last_lat, last_lng = points[-1]

    # -------------------------
    # 🔥 DUPLICATE CHECK (VERY IMPORTANT)
    # -------------------------
    lat_diff = abs(lat - last_lat)
    lng_diff = abs(lng - last_lng)

    # ~1 meter tolerance
    if lat_diff < 0.00001 and lng_diff < 0.00001:
        print("⛔ DUPLICATE GPS – skipped")
        return

    # -------------------------
    # TEST MODE
    # -------------------------
    if TESTING_MODE:
        points.append((lat, lng))
        print(f"🧪 TEST MODE UNIQUE POINT ({len(points)}) → {lat}, {lng}")
        return

    # -------------------------
    # PRODUCTION MODE
    # -------------------------
    dist = haversine_distance(last_lat, last_lng, lat, lng)

    if dist >= min_distance:
        points.append((lat, lng))
        print(f"📍 POINT ADDED ({len(points)}) → moved {dist:.2f} m")
    else:
        print(f"⏸ TOO SMALL MOVE ({dist:.2f} m) – skipped")


# =================================================
# GET POINTS (USED BY AREA API)
# =================================================
def get_points(order_id):
    state = MISSION_STATE.get(order_id)
    if not state:
        return []
    return state["points"]


# =================================================
# WAYPOINT HELPERS (OPTIONAL)
# =================================================
def get_current_waypoint(order_id):
    state = MISSION_STATE.get(order_id)
    if not state or not state["active"]:
        return None

    idx = state["current_index"]
    if idx >= len(state["waypoints"]):
        return None

    return state["waypoints"][idx]


def advance_waypoint(order_id):
    state = MISSION_STATE.get(order_id)
    if not state or not state["active"]:
        return None

    state["current_index"] += 1

    if state["current_index"] >= len(state["waypoints"]):
        state["active"] = False
        print(f"✅ MISSION COMPLETED → order {order_id}")
        return None

    return state["waypoints"][state["current_index"]]


# =================================================
# STOP MISSION (CALL ON /orders/end)
# =================================================
def stop_mission(order_id):
    state = MISSION_STATE.get(order_id)
    if state:
        state["active"] = False
        print(f"🛑 MISSION STOPPED → order {order_id}")
