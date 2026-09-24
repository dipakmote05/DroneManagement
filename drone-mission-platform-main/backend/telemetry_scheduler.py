import time
import requests

API = "http://127.0.0.1:5000/api/drone/telemetry/store"

def start_scheduler():
    print("📡 Telemetry scheduler started")

    while True:
        try:
            r = requests.post(API, timeout=5)
            print("📡 Telemetry stored:", r.json())
        except Exception as e:
            print("❌ Telemetry error:", e)

        time.sleep(5)
