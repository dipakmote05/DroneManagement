from flask import Blueprint, jsonify
from mission.capture import capture_point_from_thingspeak
# from auth.decorators import require_role   # conceptual

mission_bp = Blueprint("mission", __name__)

@mission_bp.route("/capture", methods=["POST"])
def capture_point():
    # require_role("operator")  # MUST add in real code

    point = capture_point_from_thingspeak()

    if not point:
        return jsonify({
            "status": "error",
            "message": "No active mission or GPS unavailable"
        }), 400

    return jsonify({
        "status": "success",
        "message": "Point captured",
        "lat": point["lat"],
        "lng": point["lng"]
    })
