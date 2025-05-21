from dotenv import load_dotenv
import os

load_dotenv()

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
CHECK_INTERVAL = int(os.getenv("CHECK_INTERVAL", 30))
SPREAD_THRESHOLD = float(os.getenv("SPREAD_THRESHOLD", 5))
VOLUME_THRESHOLD = float(os.getenv("VOLUME_THRESHOLD", 100000))
