from database import db
from datetime import datetime

class DroneTelemetry(db.Model):
    __tablename__ = "drone_telemetry"

    id = db.Column(db.Integer, primary_key=True)

    drone_id = db.Column(db.String(50), default="DRONE_001")
    order_id = db.Column(db.Integer, nullable=True)

    # GPS
    lat = db.Column(db.Float, nullable=False)
    lng = db.Column(db.Float, nullable=False)

    # Core telemetry
    battery = db.Column(db.Integer)
    altitude = db.Column(db.Float)

    # NEW SENSOR DATA
    aqi = db.Column(db.Integer)                 # Air Quality Index
    distance_front = db.Column(db.Float)        # Ultrasonic front (meters)
    distance_bottom = db.Column(db.Float)       # Ultrasonic bottom (meters)

    # Timestamp (sensor time preferred)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
