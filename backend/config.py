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

# CORS (comma-separated list)
FRONTEND_ORIGINS = [
    origin.strip()
    for origin in os.getenv(
        "FRONTEND_ORIGINS",
        "http://localhost:3000,http://localhost:3001,https://salon-sync-psi.vercel.app",
    ).split(",")
    if origin.strip()
]

# WhatsApp (WAHA API)
WHATSAPP_API_URL = os.getenv("WHATSAPP_API_URL", "")  # e.g. http://localhost:3002
WHATSAPP_SESSION = os.getenv("WHATSAPP_SESSION", "default")

# JWT (for OTP verification)
JWT_SECRET = os.getenv("JWT_SECRET", "salonsync-secret-key-change-in-production")

# CORS: через запятую (для CORS_MODE=strict). Пример: https://app.vercel.app,http://localhost:3000
_cors_raw = os.getenv(
    "CORS_ORIGINS",
    "http://localhost:3000,http://localhost:3001",
)
CORS_ORIGINS = [o.strip() for o in _cors_raw.split(",") if o.strip()]
if not CORS_ORIGINS:
    CORS_ORIGINS = ["http://localhost:3000", "http://localhost:3001"]

# strict: только список + regex; open (по умолчанию): любой Origin (без cookies — как у fetch во фронте)
CORS_MODE = os.getenv("CORS_MODE", "open").strip().lower()

# fullmatch() на заголовок Origin; покрывает все *.vercel.app и localhost с портом
if "CORS_ORIGIN_REGEX" in os.environ:
    _rx = os.environ["CORS_ORIGIN_REGEX"].strip()
    CORS_ORIGIN_REGEX: str | None = _rx if _rx else None
else:
    CORS_ORIGIN_REGEX = r"^https://.+\.vercel\.app$|^http://localhost(:\d+)?$"
