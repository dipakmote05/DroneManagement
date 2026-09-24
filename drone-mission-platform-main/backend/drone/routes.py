from flask import Blueprint, jsonify

# 🔥 REQUIRED IMPORTS
from orders.models import DroneOrder

from drone.telemetry import fetch_latest_telemetry
from drone.telemetry_store import fetch_and_store_telemetry
from drone.mission_state import (
    get_current_waypoint,
    get_points
)

from utils.geo import calculate_polygon_area

drone_bp = Blueprint("drone", __name__)

# =================================================
# DRONE → LATEST TELEMETRY (ThingSpeak only)
# =================================================
@drone_bp.route("/telemetry/latest", methods=["GET"])
def latest_telemetry():
    data = fetch_latest_telemetry()

    if not data:
        return jsonify({
            "status": "error",
            "message": "No telemetry data available"
        }), 404

    return jsonify({
        "status": "success",
        "source": "thingspeak",
        "data": data
    })


# =================================================
# DRONE → FETCH + STORE TELEMETRY (DB + Mission)
# =================================================
@drone_bp.route("/telemetry/store", methods=["POST"])
def store_telemetry():
    """
    Always returns SUCCESS.
    Point capture happens only if mission is active.
    """
    telemetry = fetch_and_store_telemetry()

    if not telemetry:
        return jsonify({
            "status": "success",
            "message": "Telemetry fetched, but no active mission"
        }), 200

    return jsonify({
        "status": "success",
        "order_id": telemetry.order_id,
        "lat": telemetry.lat,
        "lng": telemetry.lng,
        "battery": telemetry.battery,
        "altitude": telemetry.altitude,
        "timestamp": telemetry.timestamp.isoformat()
    })


# =================================================
# CURRENT NAVIGATION WAYPOINT
# =================================================
@drone_bp.route("/navigation/current/<int:order_id>", methods=["GET"])
def current_waypoint(order_id):
    wp = get_current_waypoint(order_id)

    if not wp:
        return jsonify({
            "status": "complete",
            "message": "Mission complete"
        })

    return jsonify({
        "lat": wp[0],
        "lng": wp[1]
    })
@drone_bp.route("/mission/area", methods=["GET"])
def mission_area():
    """
    Shows area for:
    1. Active mission (IN_PROGRESS)
    2. Else last completed mission
    """

    # 1️⃣ Try active mission first
    mission = DroneOrder.query.filter_by(status="IN_PROGRESS").first()
    mission_status = "IN_PROGRESS"

    # 2️⃣ If no active mission, fallback to last completed
    if not mission:
        mission = (
            DroneOrder.query
            .filter_by(status="COMPLETED")
            .order_by(DroneOrder.id.desc())
            .first()
        )
        mission_status = "COMPLETED"

    # 3️⃣ If no mission at all
    if not mission:
        return jsonify({
            "status": "success",
            "mission_status": "NONE",
            "points_captured": 0,
            "area_sq_meters": 0.0,
            "area_acres": 0.0,
            "note": "No mission found"
        }), 200

    # 4️⃣ Get points from memory
    points = get_points(mission.id)
    count = len(points)

    print("🧪 RAW POINTS:", points)

    if count >= 3:
        area = calculate_polygon_area(points)
        note = "Final mission area calculated ✅"
    else:
        area = 0.0
        note = "Not enough points to calculate area"

    return jsonify({
        "status": "success",
        "mission_status": mission_status,
        "points_captured": count,
        "area_sq_meters": round(area, 2),
        "area_acres": round(area * 0.000247105, 4),
        "note": note
    }), 200
