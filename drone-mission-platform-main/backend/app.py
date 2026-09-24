from flask import Flask, jsonify
from flask_cors import CORS
from config import Config
from database import db

import threading
import os

from auth.routes import auth_bp
from users.routes import users_bp
from orders.routes import orders_bp
from drone.routes import drone_bp
from mission.routes import mission_bp

# 🔥 TELEMETRY SCHEDULER
from telemetry_scheduler import start_scheduler


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    CORS(app)
    db.init_app(app)

    with app.app_context():
        # 🔥 IMPORT ALL MODELS HERE
        from users.models import User
        from orders.models import DroneOrder
        from drone.models import DroneTelemetry

        db.create_all()

    # ================================
    # REGISTER BLUEPRINTS
    # ================================
    app.register_blueprint(auth_bp, url_prefix="/api/auth")
    app.register_blueprint(users_bp, url_prefix="/api/users")
    app.register_blueprint(orders_bp, url_prefix="/api/orders")
    app.register_blueprint(drone_bp, url_prefix="/api/drone")
    app.register_blueprint(mission_bp, url_prefix="/api/mission")

    @app.route("/health")
    def health():
        return jsonify({
            "status": "OK",
            "message": "Drone backend running"
        })

    return app


# =================================================
# 🔥 BACKGROUND TELEMETRY SCHEDULER
# =================================================
def start_background_tasks():
    print("🚀 Starting telemetry scheduler thread...")
    t = threading.Thread(target=start_scheduler)
    t.daemon = True   # Flask बंद झाला तर thread पण बंद
    t.start()


# =================================================
# APP ENTRY POINT
# =================================================
if __name__ == "__main__":
    app = create_app()

    # 🔥 IMPORTANT:
    # Flask debug mode मध्ये duplicate scheduler avoid करण्यासाठी
    if not app.debug or os.environ.get("WERKZEUG_RUN_MAIN") == "true":
        start_background_tasks()

    app.run(debug=True)
