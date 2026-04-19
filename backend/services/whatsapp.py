"""
WhatsApp хабарлама жіберу сервисі.
WAHA (WhatsApp HTTP API) немесе кез келген WhatsApp Business API-мен жұмыс істейді.
Конфигурация: WHATSAPP_API_URL, WHATSAPP_SESSION env vars.
"""
import httpx
import logging
from database import SessionLocal
from models import Booking, Client, Master, Service, Salon
from config import WHATSAPP_API_URL, WHATSAPP_SESSION, WHATSAPP_API_KEY

logger = logging.getLogger("whatsapp")


def _format_phone(phone: str) -> str:
    """Телефон номерін WhatsApp форматына түрлендіру: 7XXXXXXXXXX@c.us"""
    digits = "".join(c for c in phone if c.isdigit())
    if digits.startswith("8") and len(digits) == 11:
        digits = "7" + digits[1:]
    if not digits.startswith("7"):
        digits = "7" + digits
    return digits


async def send_whatsapp_message(phone: str, message: str) -> bool:
    """WhatsApp арқылы хабарлама жіберу"""
    if not WHATSAPP_API_URL:
        logger.info(f"[WhatsApp DEMO] To {phone}:\n{message}")
        return True

    chat_id = _format_phone(phone) + "@c.us"

    headers = {}
    if WHATSAPP_API_KEY:
        headers["X-Api-Key"] = WHATSAPP_API_KEY

    try:
        async with httpx.AsyncClient(timeout=10) as client:
            response = await client.post(
                f"{WHATSAPP_API_URL}/api/sendText",
                headers=headers,
                json={
                    "chatId": chat_id,
                    "text": message,
                    "session": WHATSAPP_SESSION,
                }
            )
            if response.status_code == 200 or response.status_code == 201:
                logger.info(f"WhatsApp sent to {phone}")
                return True
            else:
                logger.error(f"WhatsApp error {response.status_code}: {response.text}")
                return False
    except Exception as e:
        logger.error(f"WhatsApp send failed: {e}")
        logger.info(f"[WhatsApp FALLBACK] To {phone}:\n{message}")
        return False


def _get_booking_details(booking_id: int):
    """Booking деректерін алу"""
    db = SessionLocal()
    try:
        booking = db.query(Booking).filter(Booking.id == booking_id).first()
        if not booking:
            return None

        client = db.query(Client).filter(Client.id == booking.client_id).first()
        master = db.query(Master).filter(Master.id == booking.master_id).first()
        service = db.query(Service).filter(Service.id == booking.service_id).first()
        salon = db.query(Salon).filter(Salon.id == master.salon_id).first() if master and master.salon_id else None

        return {
            "booking": booking,
            "client": client,
            "master": master,
            "service": service,
            "salon": salon,
        }
    finally:
        db.close()


async def notify_client_booking_created(booking_id: int):
    """Клиентке жазылу жасалды деп хабарлама жіберу"""
    data = _get_booking_details(booking_id)
    if not data or not data["client"]:
        return

    booking = data["booking"]
    client = data["client"]
    master = data["master"]
    service = data["service"]
    salon = data["salon"]

    date_str = booking.start_time.strftime("%d.%m.%Y")
    time_str = booking.start_time.strftime("%H:%M")

    salon_info = f"\n📍 Салон: {salon.name} ({salon.address})" if salon else ""

    message = (
        f"✅ SalonSync — Сіздің жазылуыңыз қабылданды!\n"
        f"{salon_info}\n"
        f"💇 Қызмет: {service.name if service else '—'}\n"
        f"👩 Мастер: {master.name if master else '—'}\n"
        f"📅 Күні: {date_str}, {time_str}\n"
        f"💰 Сома: {booking.total_price} ₸\n\n"
        f"⏳ Оплатаны күтуде. Kaspi арқылы төлеңіз."
    )

    await send_whatsapp_message(client.phone, message)


async def notify_client_payment_confirmed(booking_id: int):
    """Клиентке оплата расталды деп хабарлама жіберу"""
    data = _get_booking_details(booking_id)
    if not data or not data["client"]:
        return

    booking = data["booking"]
    client = data["client"]
    master = data["master"]
    service = data["service"]
    salon = data["salon"]

    date_str = booking.start_time.strftime("%d.%m.%Y")
    time_str = booking.start_time.strftime("%H:%M")

    salon_info = f"\n📍 Салон: {salon.name}\n📍 Мекенжай: {salon.address}" if salon else ""

    message = (
        f"✅ SalonSync — Оплата расталды!\n"
        f"{salon_info}\n"
        f"💇 Қызмет: {service.name if service else '—'}\n"
        f"👩 Мастер: {master.name if master else '—'}\n"
        f"📅 Күні: {date_str}, {time_str}\n"
        f"💰 Сома: {booking.total_price} ₸\n\n"
        f"Сізді күтеміз! 💐"
    )

    await send_whatsapp_message(client.phone, message)


async def notify_client_booking_cancelled(booking_id: int):
    """Клиентке жазылу бас тартылды деп хабарлама жіберу"""
    data = _get_booking_details(booking_id)
    if not data or not data["client"]:
        return

    booking = data["booking"]
    client = data["client"]
    service = data["service"]

    date_str = booking.start_time.strftime("%d.%m.%Y")
    time_str = booking.start_time.strftime("%H:%M")

    message = (
        f"❌ SalonSync — Жазылу бас тартылды\n\n"
        f"💇 Қызмет: {service.name if service else '—'}\n"
        f"📅 Күні: {date_str}, {time_str}\n\n"
        f"Қайта жазылу үшін: salonsync.kz"
    )

    await send_whatsapp_message(client.phone, message)


async def notify_client_booking_reminder(booking_id: int):
    """Клиентке жазылуға 2 сағат қалды деп еске салу"""
    data = _get_booking_details(booking_id)
    if not data or not data["client"]:
        return

    booking = data["booking"]
    client = data["client"]
    master = data["master"]
    salon = data["salon"]

    time_str = booking.start_time.strftime("%H:%M")

    salon_info = f"📍 {salon.name}, {salon.address}" if salon else ""

    message = (
        f"⏰ SalonSync — Еске салу!\n\n"
        f"Сіздің жазылуыңызға 2 сағат қалды.\n"
        f"🕐 Уақыт: {time_str}\n"
        f"👩 Мастер: {master.name if master else '—'}\n"
        f"{salon_info}\n\n"
        f"Сізді күтеміз! 💐"
    )

    await send_whatsapp_message(client.phone, message)


async def send_otp_code(phone: str, code: str):
    """OTP кодты WhatsApp арқылы жіберу"""
    message = (
        f"🔐 SalonSync — Сіздің кодыңыз: {code}\n\n"
        f"Код 5 минут ішінде жарамды."
    )
    await send_whatsapp_message(phone, message)
