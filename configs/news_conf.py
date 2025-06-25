import os
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv("TOKEN")
WEBHOOK_URL = os.getenv("WEBHOOK_URL")
WEBHOOK_PATH = os.getenv("WEBHOOK_PATH")
WEBAPP_HOST = os.getenv("WEBAPP_HOST")
WEBAPP_PORT = os.getenv("WEBAPP_PORT")

BAN_TIME = os.getenv("BAN_TIME")
MAX_MESSAGES = os.getenv("MAX_MESSAGES")
TIME_WINDOW = os.getenv("TIME_WINDOW")

NEWS_SOURCE_URL = os.getenv("NEWS_SOURCE_URL")
HEADERS = {"User-Agent": "Mozilla/5.0"}

HOURS = [7, 9, 11, 14]

AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")
AWS_REGION = os.getenv("AWS_REGION")
