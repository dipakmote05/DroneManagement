from flask import Blueprint, jsonify, g
from auth.jwt_auth import jwt_required
from users.models import User   # ✅ FIX
from database import db

users_bp = Blueprint("users", __name__)

@users_bp.route("/me")
@jwt_required()
def my_profile():
    return jsonify({
        "user_id": g.user_id,
        "role": g.role,
        "message": "You are authenticated"
    })

@users_bp.route("/operators", methods=["GET"])
@jwt_required(role="client")
def list_operators():
    operators = User.query.filter_by(role="operator", is_active=True).all()

    return jsonify([
        {
            "id": op.id,
            "name": op.name,
            "email": op.email
        }
        for op in operators
    ])
