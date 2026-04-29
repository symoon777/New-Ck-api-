import os
from dotenv import load_dotenv
load_dotenv()

class Config:
    LIKE_API_100: str    = os.getenv("LIKE_API_100", "")
    LIKE_API_200: str    = os.getenv("LIKE_API_200", "")
    LIKE_API_SECRET: str = os.getenv("LIKE_API_SECRET", "")
    ADMIN_TOKEN: str     = os.getenv("ADMIN_TOKEN", "ams_admin_2024_secret")
    APP_ENV: str         = os.getenv("APP_ENV", "production")

cfg = Config()
