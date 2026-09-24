import smtplib
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv

load_dotenv()

def send_email_otp(to_email, otp):
    msg = MIMEMultipart()
    msg["From"] = os.getenv("EMAIL_USER")
    msg["To"] = to_email
    msg["Subject"] = "Your Drone Login OTP"

    body = f"""
    Your OTP for Drone Platform Login is: {otp}
    Valid for 5 minutes.
    """

    msg.attach(MIMEText(body, "plain"))

    server = smtplib.SMTP(
        os.getenv("EMAIL_HOST"),
        int(os.getenv("EMAIL_PORT"))
    )
    server.starttls()
    server.login(
        os.getenv("EMAIL_USER"),
        os.getenv("EMAIL_PASS")
    )
    server.send_message(msg)
    server.quit()
