from database import db
from datetime import datetime


class DroneOrder(db.Model):
    __tablename__ = "drone_orders"

    id = db.Column(db.Integer, primary_key=True)

    # relations
    client_id = db.Column(db.Integer, nullable=False)
    operator_id = db.Column(db.Integer, nullable=True)

    drone_lat = db.Column(db.Float, nullable=True)
    drone_lng = db.Column(db.Float, nullable=True)


    # service details
    service_type = db.Column(db.String(50), nullable=False)
    latitude = db.Column(db.Float, nullable=False)
    longitude = db.Column(db.Float, nullable=False)

    # status lifecycle
    # PENDING → ACCEPTED → IN_PROGRESS → COMPLETED / REJECTED
    status = db.Column(db.String(20), default="PENDING")

    # tracking
    drone_lat = db.Column(db.Float, nullable=True)
    drone_lng = db.Column(db.Float, nullable=True)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<DroneOrder {self.id} {self.status}>"
