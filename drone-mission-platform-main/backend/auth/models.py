from database import db
from datetime import datetime

class OTP(db.Model):
    __tablename__ = "otp_codes"

    id = db.Column(db.Integer, primary_key=True)
    identifier = db.Column(db.String(120))  # email or mobile
    otp = db.Column(db.String(6))
    expires_at = db.Column(db.DateTime)
