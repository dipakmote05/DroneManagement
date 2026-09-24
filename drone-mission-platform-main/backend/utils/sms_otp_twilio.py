import os
from twilio.rest import Client
from dotenv import load_dotenv

load_dotenv()

def send_sms_otp(mobile, otp):
    client = Client(
        os.getenv("TWILIO_ACCOUNT_SID"),
        os.getenv("TWILIO_AUTH_TOKEN")
    )

    msg = client.messages.create(
        body=f"Your OTP for Drone Platform is {otp}",
        from_=os.getenv("TWILIO_PHONE"),   # 👈 +19787185234
        to=f"+91{mobile}"                 # 👈 verified Indian number
    )

    print("TWILIO SID:", msg.sid)
