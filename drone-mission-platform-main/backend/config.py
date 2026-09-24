import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret")
    SQLALCHEMY_DATABASE_URI = os.getenv(
        "DATABASE_URL",
        "mysql+pymysql://drone_user:drone123@localhost/drone_platform"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
