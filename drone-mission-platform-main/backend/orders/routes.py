from flask import Blueprint, request, jsonify, g
from database import db
from orders.models import DroneOrder
from auth.jwt_auth import jwt_required

# 🔥 DRONE MISSION STATE
from drone.mission_state import init_navigation, stop_mission

orders_bp = Blueprint("orders", __name__)

# =================================================
# CLIENT APIs
# =================================================

@orders_bp.route("/create", methods=["POST"])
@jwt_required(role="client")
def create_order():
    data = request.json

    service = data.get("service_type")
    lat = data.get("lat")
    lng = data.get("lng")

    if not all([service, lat, lng]):
        return jsonify({"error": "All fields required"}), 400

    order = DroneOrder(
        client_id=g.user_id,
        service_type=service,
        latitude=lat,
        longitude=lng,
        status="PENDING"
    )

    db.session.add(order)
    db.session.commit()

    return jsonify({
        "message": "Drone request created",
        "order_id": order.id,
        "status": order.status
    }), 201


# -------------------------------------------------
# CLIENT → LATEST ORDER (PRIORITY BASED)
# -------------------------------------------------
@orders_bp.route("/my-latest", methods=["GET"])
@jwt_required(role="client")
def my_latest_order():

    # 1️⃣ IN_PROGRESS first
    order = DroneOrder.query.filter_by(
        client_id=g.user_id,
        status="IN_PROGRESS"
    ).first()

    # 2️⃣ COMPLETED next
    if not order:
        order = DroneOrder.query.filter_by(
            client_id=g.user_id,
            status="COMPLETED"
        ).order_by(DroneOrder.id.desc()).first()

    # 3️⃣ fallback
    if not order:
        order = DroneOrder.query.filter(
            DroneOrder.client_id == g.user_id,
            DroneOrder.status != "REJECTED"
        ).order_by(DroneOrder.id.desc()).first()

    if not order:
        return jsonify({"error": "No active request"}), 404

    return jsonify({
        "order_id": order.id,
        "status": order.status,
        "target_lat": order.latitude,
        "target_lng": order.longitude,
        "drone_lat": order.drone_lat,
        "drone_lng": order.drone_lng
    })


# =================================================
# OPERATOR APIs
# =================================================

@orders_bp.route("/pending", methods=["GET"])
@jwt_required(role="operator")
def get_pending_orders():
    orders = DroneOrder.query.filter_by(status="PENDING").all()

    return jsonify([
        {
            "order_id": o.id,
            "service": o.service_type,
            "lat": o.latitude,
            "lng": o.longitude,
            "client_id": o.client_id
        }
        for o in orders
    ])


@orders_bp.route("/accept/<int:order_id>", methods=["POST"])
@jwt_required(role="operator")
def accept_order(order_id):
    order = DroneOrder.query.get(order_id)

    if not order:
        return jsonify({"error": "Order not found"}), 404

    if order.status != "PENDING":
        return jsonify({"error": "Order already processed"}), 400

    order.status = "ACCEPTED"
    order.operator_id = g.user_id
    db.session.commit()

    return jsonify({"message": "Order accepted"})


@orders_bp.route("/reject/<int:order_id>", methods=["POST"])
@jwt_required(role="operator")
def reject_order(order_id):
    order = DroneOrder.query.get(order_id)

    if not order:
        return jsonify({"error": "Order not found"}), 404

    if order.status != "PENDING":
        return jsonify({"error": "Order already processed"}), 400

    order.status = "REJECTED"
    db.session.commit()

    return jsonify({"message": "Order rejected"})


# =================================================
# OPERATOR → READY MISSION
# =================================================

@orders_bp.route("/my-ready", methods=["GET"])
@jwt_required(role="operator")
def my_ready_order():
    order = DroneOrder.query.filter_by(
        operator_id=g.user_id,
        status="ACCEPTED"
    ).first()

    if not order:
        return jsonify({"message": "No ready mission"})

    return jsonify({
        "order_id": order.id,
        "status": order.status,
        "client_id": order.client_id,
        "lat": order.latitude,
        "lng": order.longitude
    })


# =================================================
# OPERATOR → START MISSION
# =================================================

@orders_bp.route("/start/<int:order_id>", methods=["POST"])
@jwt_required(role="operator")
def start_mission(order_id):
    order = DroneOrder.query.get(order_id)

    if not order:
        return jsonify({"error": "Order not found"}), 404

    if order.status != "ACCEPTED":
        return jsonify({"error": "Mission cannot be started"}), 400

    if order.operator_id != g.user_id:
        return jsonify({"error": "Not your assigned mission"}), 403

    order.status = "IN_PROGRESS"
    db.session.commit()

    # 🔥 init memory mission
    init_navigation(order)

    return jsonify({
        "message": "Mission started successfully",
        "order_id": order.id
    })


# =================================================
# OPERATOR → ACTIVE MISSION
# =================================================

@orders_bp.route("/my-active", methods=["GET"])
@jwt_required(role="operator")
def my_active_order():
    order = DroneOrder.query.filter_by(
        operator_id=g.user_id,
        status="IN_PROGRESS"
    ).first()

    if not order:
        return jsonify({"message": "No active mission"})

    return jsonify({
        "order_id": order.id,
        "status": order.status,
        "client_id": order.client_id,
        "target_lat": order.latitude,
        "target_lng": order.longitude,
        "drone_lat": order.drone_lat,
        "drone_lng": order.drone_lng
    })


# =================================================
# OPERATOR → END MISSION (SINGLE, FINAL)
# =================================================

@orders_bp.route("/end/<int:order_id>", methods=["POST"])
@jwt_required(role="operator")
def end_mission(order_id):
    order = DroneOrder.query.get(order_id)

    if not order:
        return jsonify({"error": "Order not found"}), 404

    if order.status != "IN_PROGRESS":
        return jsonify({"error": "Mission not active"}), 400

    if order.operator_id != g.user_id:
        return jsonify({"error": "Not your assigned mission"}), 403

    order.status = "COMPLETED"
    db.session.commit()

    # 🔥 stop memory mission
    stop_mission(order.id)

    return jsonify({
        "message": "Mission ended successfully",
        "order_id": order.id
    })
