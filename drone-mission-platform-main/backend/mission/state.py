# backend/mission/state.py

MISSION_STATE = {
    "active": False,
    "order_id": None,
    "points": [],     # [(lat, lng), ...]
    "started_at": None
}

def start_mission(order_id):
    MISSION_STATE["active"] = True
    MISSION_STATE["order_id"] = order_id
    MISSION_STATE["points"] = []
    MISSION_STATE["started_at"] = True
    return MISSION_STATE

def stop_mission(clear_points=True):
    MISSION_STATE["active"] = False
    MISSION_STATE["order_id"] = None

    if clear_points:
        MISSION_STATE["points"] = []

    return MISSION_STATE

def is_mission_active():
    return MISSION_STATE["active"]

def get_active_order_id():
    return MISSION_STATE["order_id"]

def add_point(lat, lng):
    if MISSION_STATE["active"]:
        MISSION_STATE["points"].append((lat, lng))

def get_points():
    return list(MISSION_STATE["points"])   # safe copy
