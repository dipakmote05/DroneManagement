from flask import Blueprint, request, jsonify, g
from datetime import datetime

from database import db
from users.models import User

from auth.jwt_utils import generate_token
from auth.jwt_auth import jwt_required

from auth.models import OTP
from auth.otp_utils import generate_otp, otp_expiry
from auth.google_auth import verify_google_token

from utils.email_otp import send_email_otp
from utils.sms_otp_twilio import send_sms_otp


auth_bp = Blueprint("auth", __name__)
users_bp = Blueprint("users", __name__)


# =========================
# HELPER: NORMALIZE IDENTIFIER
# =========================
def normalize_identifier(identifier: str) -> str:
    """
    - trims spaces
    - removes +91 / 91 from mobile if present
    - keeps email as-is
    """
    identifier = identifier.strip()

    if identifier.isdigit():
        if identifier.startswith("91") and len(identifier) == 12:
            identifier = identifier[2:]
    return identifier


# =========================
# LOGIN WITH EMAIL + PASSWORD
# =========================
@auth_bp.route("/login", methods=["POST"])
def login():
    data = request.json

    email = data.get("email")
    password = data.get("password")

    if not email or not password:
        return jsonify({"error": "Email and password required"}), 400

    user = User.query.filter_by(email=email).first()
    if not user:
        return jsonify({"error": "User not found"}), 404

    if user.password != password:
        return jsonify({"error": "Invalid password"}), 401

    token = generate_token(user.id, user.role)

    return jsonify({
        "message": "Login successful",
        "token": token,
        "role": user.role,
        "user_id": user.id
    })


# =========================
# SIGNUP (FINAL STEP AFTER OTP)
# =========================
@auth_bp.route("/signup", methods=["POST"])
def signup():
    data = request.json

    name = data.get("name")
    email = data.get("email")
    password = data.get("password")
    role = data.get("role")  # client | operator

    if not all([name, email, password, role]):
        return jsonify({"error": "All fields required"}), 400

    if role not in ["client", "operator"]:
        return jsonify({"error": "Invalid role"}), 400

    if User.query.filter_by(email=email).first():
        return jsonify({"error": "Email already registered"}), 409

    user = User(
        name=name,
        email=email,
        password=password,
        role=role
    )

    db.session.add(user)
    db.session.commit()

    return jsonify({
        "message": "Signup successful",
        "user_id": user.id,
        "role": user.role
    }), 201


# =========================
# SEND OTP (EMAIL / MOBILE)
# =========================
@auth_bp.route("/send-otp", methods=["POST"])
def send_otp():
    data = request.json
    raw_identifier = data.get("identifier")

    if not raw_identifier:
        return jsonify({"error": "Email or mobile required"}), 400

    identifier = normalize_identifier(raw_identifier)

    otp_code = str(generate_otp())  # 🔥 ALWAYS STRING

    otp = OTP(
        identifier=identifier,
        otp=otp_code,
        expires_at=otp_expiry()
    )

    db.session.add(otp)
    db.session.commit()

    # SEND OTP
    if "@" in identifier:
        send_email_otp(identifier, otp_code)
    else:
        send_sms_otp(identifier, otp_code)

    return jsonify({"message": "OTP sent successfully"})


# =========================
# VERIFY OTP (SIGNUP FLOW)
# =========================
@auth_bp.route("/verify-otp", methods=["POST"])
def verify_otp():
    data = request.json

    raw_identifier = data.get("identifier")
    otp_input = str(data.get("otp")).strip()

    identifier = normalize_identifier(raw_identifier)

    print("---- VERIFY OTP DEBUG ----")
    print("RAW IDENTIFIER:", raw_identifier)
    print("NORMALIZED IDENTIFIER:", identifier)
    print("OTP INPUT:", otp_input)

    otp_record = OTP.query.filter_by(
        identifier=identifier
    ).order_by(OTP.id.desc()).first()

    print("DB OTP RECORD:", otp_record.otp if otp_record else None)

    if not otp_record:
        return jsonify({"error": "OTP not found"}), 401

    if otp_record.otp != otp_input:
        return jsonify({"error": "Invalid OTP"}), 401

    if otp_record.expires_at < datetime.utcnow():
        return jsonify({"error": "OTP expired"}), 401

    return jsonify({"message": "OTP verified"})



# =========================
# GOOGLE LOGIN
# =========================
@auth_bp.route("/google-login", methods=["POST"])
def google_login():
    token = request.json.get("token")

    info = verify_google_token(token)
    if not info:
        return jsonify({"error": "Invalid Google token"}), 401

    email = info["email"]
    name = info.get("name", "Google User")

    user = User.query.filter_by(email=email).first()

    if not user:
        user = User(
            name=name,
            email=email,
            password="GOOGLE",
            role="client"
        )
        db.session.add(user)
        db.session.commit()

    jwt_token = generate_token(user.id, user.role)

    return jsonify({
        "message": "Google login successful",
        "token": jwt_token,
        "role": user.role
    })


# =========================
# JWT TEST API
# =========================
@users_bp.route("/me")
@jwt_required()
def my_profile():
    return jsonify({
        "user_id": g.user_id,
        "role": g.role,
        "message": "You are authenticated"
    })
