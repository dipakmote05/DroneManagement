from functools import wraps
from flask import request, jsonify, g
from auth.jwt_utils import decode_token

def jwt_required(role=None):
    def decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            auth_header = request.headers.get("Authorization")

            if not auth_header:
                return jsonify({"error": "Token missing"}), 401

            try:
                token = auth_header.split(" ")[1]
            except IndexError:
                return jsonify({"error": "Invalid token format"}), 401

            payload = decode_token(token)
            if not payload:
                return jsonify({"error": "Invalid or expired token"}), 401

            # user info globally store
            g.user_id = payload["user_id"]
            g.role = payload["role"]

            if role and g.role != role:
                return jsonify({"error": "Unauthorized access"}), 403

            return f(*args, **kwargs)
        return wrapper
    return decorator
