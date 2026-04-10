import os
from dotenv import load_dotenv

load_dotenv()

# Telegram Bot
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "YOUR_BOT_TOKEN_HERE")

# Database
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./app.db")

# Admin chat ID для уведомлений о новых мастерах
ADMIN_CHAT_ID = os.getenv("ADMIN_CHAT_ID", "")

# Kaspi Payment
KASPI_PHONE = os.getenv("KASPI_PHONE", "77001234567")  # Номер для приёма платежей

# WhatsApp (WAHA API)
WHATSAPP_API_URL = os.getenv("WHATSAPP_API_URL", "")  # e.g. http://localhost:3002
WHATSAPP_SESSION = os.getenv("WHATSAPP_SESSION", "default")

# JWT (for OTP verification)
JWT_SECRET = os.getenv("JWT_SECRET", "salonsync-secret-key-change-in-production")
