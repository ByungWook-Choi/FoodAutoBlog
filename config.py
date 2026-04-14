import os
from dotenv import load_dotenv

# Load .env file
load_dotenv()

# Base Directories
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
OUTPUT_DIR = os.path.join(BASE_DIR, 'output')
IMAGES_DIR = os.path.join(OUTPUT_DIR, 'images')
FONTS_DIR = os.path.join(BASE_DIR, 'fonts')

# API Keys & Tokens (Loaded from .env or environment variables)
KAMIS_API_KEY = os.environ.get("KAMIS_API_KEY")
KAMIS_API_ID = os.environ.get("KAMIS_API_ID", "YOUR_KAMIS_ID")
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")

# Telegram Bot
TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")

# Create directories if they don't exist
os.makedirs(IMAGES_DIR, exist_ok=True)
os.makedirs(FONTS_DIR, exist_ok=True)

# Font Configuration
FONT_PATH = os.path.join(FONTS_DIR, 'NanumGothic.ttf')
FONT_URL = "https://github.com/google/fonts/raw/main/ofl/nanumgothic/NanumGothic-Regular.ttf"

