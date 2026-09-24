import requests
import os
from dotenv import load_dotenv

load_dotenv()

def send_sms_otp(mobile, otp):
    url = "https://www.fast2sms.com/dev/bulkV2"

    payload = {
        "route": "otp",
        "variables_values": otp,
        "numbers": mobile
    }

    headers = {
        "authorization": os.getenv("FAST2SMS_API_KEY"),
        "Content-Type": "application/json"
    }

    response = requests.post(url, json=payload, headers=headers)
    return response.json()
