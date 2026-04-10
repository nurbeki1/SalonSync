"""Сервис уведомлений для мастеров"""
from aiogram import Bot
from datetime import datetime

import sys
sys.path.append("../..")
from database import SessionLocal
from models import Master, Booking, Client, Service
from config import TELEGRAM_BOT_TOKEN


async def notify_master_new_booking(booking_id: int):
    """Уведомить мастера о новой записи"""
    if not TELEGRAM_BOT_TOKEN or TELEGRAM_BOT_TOKEN == "YOUR_BOT_TOKEN_HERE":
        print("⚠️ Telegram bot token not configured")
        return

    db = SessionLocal()
    try:
        booking = db.query(Booking).filter(Booking.id == booking_id).first()
        if not booking:
            return

        master = db.query(Master).filter(Master.id == booking.master_id).first()
        if not master or not master.telegram_chat_id:
            return

        client = db.query(Client).filter(Client.id == booking.client_id).first()
        service = db.query(Service).filter(Service.id == booking.service_id).first()

        # Форматируем сообщение
        date_str = booking.start_time.strftime("%d.%m.%Y")
        time_str = booking.start_time.strftime("%H:%M")

        message = (
            "🔔 *Новая запись!*\n\n"
            f"👤 Клиент: {client.name if client else '—'}\n"
            f"📱 Телефон: {client.phone if client else '—'}\n"
            f"💇 Услуга: {service.name if service else '—'}\n"
            f"📅 Дата: {date_str}\n"
            f"🕐 Время: {time_str}\n"
            f"💰 Сумма: {booking.total_price} ₸\n\n"
            f"Статус: ⏳ Ожидает оплаты"
        )

        bot = Bot(token=TELEGRAM_BOT_TOKEN)
        await bot.send_message(
            chat_id=master.telegram_chat_id,
            text=message,
            parse_mode="Markdown"
        )
        await bot.session.close()

    except Exception as e:
        print(f"Error sending notification: {e}")
    finally:
        db.close()


async def notify_master_payment_confirmed(booking_id: int):
    """Уведомить мастера об оплате"""
    if not TELEGRAM_BOT_TOKEN or TELEGRAM_BOT_TOKEN == "YOUR_BOT_TOKEN_HERE":
        return

    db = SessionLocal()
    try:
        booking = db.query(Booking).filter(Booking.id == booking_id).first()
        if not booking:
            return

        master = db.query(Master).filter(Master.id == booking.master_id).first()
        if not master or not master.telegram_chat_id:
            return

        client = db.query(Client).filter(Client.id == booking.client_id).first()
        service = db.query(Service).filter(Service.id == booking.service_id).first()

        date_str = booking.start_time.strftime("%d.%m.%Y")
        time_str = booking.start_time.strftime("%H:%M")

        message = (
            "✅ *Запись оплачена!*\n\n"
            f"👤 Клиент: {client.name if client else '—'}\n"
            f"💇 Услуга: {service.name if service else '—'}\n"
            f"📅 Дата: {date_str}\n"
            f"🕐 Время: {time_str}\n"
            f"💰 Сумма: {booking.total_price} ₸"
        )

        bot = Bot(token=TELEGRAM_BOT_TOKEN)
        await bot.send_message(
            chat_id=master.telegram_chat_id,
            text=message,
            parse_mode="Markdown"
        )
        await bot.session.close()

    except Exception as e:
        print(f"Error sending notification: {e}")
    finally:
        db.close()


async def notify_master_booking_cancelled(booking_id: int, client_name: str, date_str: str, time_str: str, master_chat_id: str):
    """Уведомить мастера об отмене записи"""
    if not TELEGRAM_BOT_TOKEN or TELEGRAM_BOT_TOKEN == "YOUR_BOT_TOKEN_HERE":
        return

    try:
        message = (
            "❌ *Запись отменена*\n\n"
            f"👤 Клиент: {client_name}\n"
            f"📅 Дата: {date_str}\n"
            f"🕐 Время: {time_str}"
        )

        bot = Bot(token=TELEGRAM_BOT_TOKEN)
        await bot.send_message(
            chat_id=master_chat_id,
            text=message,
            parse_mode="Markdown"
        )
        await bot.session.close()

    except Exception as e:
        print(f"Error sending notification: {e}")