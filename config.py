import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file if present
BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR / ".env")

# Search Parameters
ORIGIN = os.getenv("FLIGHT_ORIGIN", "KNO")  # Kualanamu International Airport (Medan)
DESTINATION = os.getenv("FLIGHT_DESTINATION", "CGK")  # Soekarno-Hatta International Airport (Jakarta)

# Target departure dates (17, 18, 19, 20 September 2026)
TARGET_DATES = os.getenv(
    "FLIGHT_TARGET_DATES", "2026-09-17,2026-09-18,2026-09-19,2026-09-20"
).split(",")

# Price Thresholds (IDR)
MIN_AFFORDABLE_PRICE = int(os.getenv("MIN_AFFORDABLE_PRICE", "1300000"))
MAX_AFFORDABLE_PRICE = int(os.getenv("MAX_AFFORDABLE_PRICE", "1599000"))

# Telegram Settings
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "")
TELEGRAM_STICKER_ID = os.getenv("TELEGRAM_STICKER_ID", "")

# App & Scheduler Settings
CHECK_INTERVAL_MINUTES = int(os.getenv("CHECK_INTERVAL_MINUTES", "30"))
DATABASE_PATH = BASE_DIR / "tickets.db"

