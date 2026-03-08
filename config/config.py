import os
from dotenv import load_dotenv

load_dotenv()

TG_API_ID = os.getenv("TELEGRAM_API_ID")
TG_API_HASH = os.getenv("TELEGRAM_API_HASH")
SESSION_NAME = os.getenv("SESSION")