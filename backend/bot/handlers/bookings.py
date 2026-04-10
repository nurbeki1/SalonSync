from typing import Optional, List
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from datetime import datetime, timedelta

import sys
sys.path.append("..")
from database import SessionLocal
from models import Master, Booking, Client, Service, MasterStatus, BookingStatus
from bot.keyboards.main_menu import get_main_menu
from bot.keyboards.schedule_kb import (
    get_bookings_period_keyboard,
    get_payment_confirmation_keyboard,
    get_pending_bookings_keyboard
)

router = Router()


def get_master_by_chat_id(chat_id: int) -> Optional[Master]:
    db = SessionLocal()
    try:
        return db.query(Master).filter(Master.telegram_chat_id == str(chat_id)).first()
    finally:
        db.close()


def get_bookings_for_period(master_id: int, start_date: datetime, end_date: datetime) -> list:
    """Получить записи за период"""
    db = SessionLocal()
    try:
        bookings = db.query(Booking).filter(
            Booking.master_id == master_id,
            Booking.start_time >= start_date,
            Booking.start_time < end_date,
            Booking.status != BookingStatus.CANCELLED
        ).order_by(Booking.start_time).all()

        result = []
        for b in bookings:
            client = db.query(Client).filter(Client.id == b.client_id).first()
            service = db.query(Service).filter(Service.id == b.service_id).first()
            result.append({
                "id": b.id,
                "client_name": client.name if client else "—",
                "client_phone": client.phone if client else "—",
                "service_name": service.name if service else "—",
                "start_time": b.start_time,
                "end_time": b.end_time,
                "status": b.status.value,
                "total_price": str(b.total_price),
            })
        return result
    finally:
        db.close()


def format_bookings(bookings: list, title: str) -> str:
    """Форматировать список записей"""
    if not bookings:
        return f"{title}\n\n😔 Записей нет"

    text = f"{title}\n\n"
    for b in bookings:
        status_emoji = {
            "pending": "⏳",
            "confirmed": "✅",
            "paid": "💰",
            "completed": "✔️",
        }.get(b["status"], "❓")

        time_str = b["start_time"].strftime("%H:%M")
        date_str = b["start_time"].strftime("%d.%m")

        text += (
            f"{status_emoji} {date_str} в {time_str}\n"
            f"   👤 {b['client_name']}\n"
            f"   📱 {b['client_phone']}\n"
            f"   💇 {b['service_name']}\n"
            f"   💰 {b['total_price']} ₸\n\n"
        )

    return text


@router.message(F.text == "📋 Мои записи")
async def show_bookings_menu(message: Message):
    """Меню записей"""
    master = get_master_by_chat_id(message.chat.id)

    if not master or master.status != MasterStatus.APPROVED:
        await message.answer("❌ Эта функция доступна только одобренным мастерам.")
        return

    await message.answer(
        "📋 Выберите период:",
        reply_markup=get_bookings_period_keyboard()
    )


@router.callback_query(F.data == "bookings_today")
async def show_today_bookings(callback: CallbackQuery):
    """Записи на сегодня"""
    master = get_master_by_chat_id(callback.message.chat.id)
    if not master:
        await callback.answer("Ошибка")
        return

    today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    tomorrow = today + timedelta(days=1)

    bookings = get_bookings_for_period(master.id, today, tomorrow)
    text = format_bookings(bookings, "📅 Записи на сегодня")

    await callback.message.edit_text(text)
    await callback.message.answer("Выберите действие:", reply_markup=get_main_menu())
    await callback.answer()


@router.callback_query(F.data == "bookings_tomorrow")
async def show_tomorrow_bookings(callback: CallbackQuery):
    """Записи на завтра"""
    master = get_master_by_chat_id(callback.message.chat.id)
    if not master:
        await callback.answer("Ошибка")
        return

    today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    tomorrow = today + timedelta(days=1)
    day_after = today + timedelta(days=2)

    bookings = get_bookings_for_period(master.id, tomorrow, day_after)
    text = format_bookings(bookings, "📅 Записи на завтра")

    await callback.message.edit_text(text)
    await callback.message.answer("Выберите действие:", reply_markup=get_main_menu())
    await callback.answer()


@router.callback_query(F.data == "bookings_week")
async def show_week_bookings(callback: CallbackQuery):
    """Записи на неделю"""
    master = get_master_by_chat_id(callback.message.chat.id)
    if not master:
        await callback.answer("Ошибка")
        return

    today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    week_later = today + timedelta(days=7)

    bookings = get_bookings_for_period(master.id, today, week_later)
    text = format_bookings(bookings, "📅 Записи на неделю")

    await callback.message.edit_text(text)
    await callback.message.answer("Выберите действие:", reply_markup=get_main_menu())
    await callback.answer()


# ============ Payment Confirmation ============
def get_pending_payment_bookings(master_id: int) -> list:
    """Получить записи, ожидающие оплаты"""
    db = SessionLocal()
    try:
        bookings = db.query(Booking).filter(
            Booking.master_id == master_id,
            Booking.status == BookingStatus.PENDING,
            Booking.start_time >= datetime.now()
        ).order_by(Booking.start_time).all()

        result = []
        for b in bookings:
            client = db.query(Client).filter(Client.id == b.client_id).first()
            service = db.query(Service).filter(Service.id == b.service_id).first()
            result.append({
                "id": b.id,
                "client_name": client.name if client else "—",
                "client_phone": client.phone if client else "—",
                "service_name": service.name if service else "—",
                "start_time": b.start_time,
                "end_time": b.end_time,
                "status": b.status.value,
                "total_price": str(b.total_price),
                "payment_link": b.payment_link,
            })
        return result
    finally:
        db.close()


def get_booking_details(booking_id: int) -> dict:
    """Получить детали записи"""
    db = SessionLocal()
    try:
        b = db.query(Booking).filter(Booking.id == booking_id).first()
        if not b:
            return None

        client = db.query(Client).filter(Client.id == b.client_id).first()
        service = db.query(Service).filter(Service.id == b.service_id).first()

        return {
            "id": b.id,
            "client_name": client.name if client else "—",
            "client_phone": client.phone if client else "—",
            "service_name": service.name if service else "—",
            "start_time": b.start_time,
            "end_time": b.end_time,
            "status": b.status.value,
            "total_price": str(b.total_price),
            "payment_link": b.payment_link,
            "master_id": b.master_id,
        }
    finally:
        db.close()


def confirm_booking_payment(booking_id: int) -> bool:
    """Подтвердить оплату записи"""
    db = SessionLocal()
    try:
        booking = db.query(Booking).filter(Booking.id == booking_id).first()
        if not booking:
            return False

        booking.status = BookingStatus.PAID
        booking.payment_confirmed_at = datetime.now()
        db.commit()
        return True
    finally:
        db.close()


@router.callback_query(F.data == "bookings_pending_payment")
async def show_pending_payment_bookings(callback: CallbackQuery):
    """Показать записи, ожидающие оплаты"""
    master = get_master_by_chat_id(callback.message.chat.id)
    if not master:
        await callback.answer("Ошибка")
        return

    bookings = get_pending_payment_bookings(master.id)

    if not bookings:
        await callback.message.edit_text(
            "💰 *Записи, ожидающие оплаты*\n\n"
            "😊 Нет записей, ожидающих оплаты",
            parse_mode="Markdown"
        )
        await callback.message.answer("Выберите действие:", reply_markup=get_main_menu())
    else:
        await callback.message.edit_text(
            f"💰 *Записи, ожидающие оплаты ({len(bookings)})*\n\n"
            "Выберите запись для подтверждения:",
            parse_mode="Markdown",
            reply_markup=get_pending_bookings_keyboard(bookings)
        )

    await callback.answer()


@router.callback_query(F.data == "back_to_bookings")
async def back_to_bookings_menu(callback: CallbackQuery):
    """Вернуться в меню записей"""
    await callback.message.edit_text(
        "📋 Выберите период:",
        reply_markup=get_bookings_period_keyboard()
    )
    await callback.answer()


@router.callback_query(F.data.startswith("view_pending_"))
async def view_pending_booking(callback: CallbackQuery):
    """Просмотр записи, ожидающей оплаты"""
    booking_id = int(callback.data.split("_")[-1])

    master = get_master_by_chat_id(callback.message.chat.id)
    if not master:
        await callback.answer("Ошибка")
        return

    booking = get_booking_details(booking_id)
    if not booking or booking["master_id"] != master.id:
        await callback.answer("Запись не найдена")
        return

    date_str = booking["start_time"].strftime("%d.%m.%Y")
    time_str = booking["start_time"].strftime("%H:%M")

    text = (
        f"💰 *Запись ожидает оплаты*\n\n"
        f"👤 Клиент: {booking['client_name']}\n"
        f"📱 Телефон: {booking['client_phone']}\n"
        f"💇 Услуга: {booking['service_name']}\n"
        f"📅 Дата: {date_str}\n"
        f"🕐 Время: {time_str}\n"
        f"💵 Сумма: {booking['total_price']} ₸\n\n"
        f"Клиент должен оплатить через Kaspi QR и прислать скриншот.\n"
        f"После получения подтверждения оплаты нажмите кнопку ниже."
    )

    await callback.message.edit_text(
        text,
        parse_mode="Markdown",
        reply_markup=get_payment_confirmation_keyboard(booking_id)
    )
    await callback.answer()


@router.callback_query(F.data.startswith("confirm_payment_"))
async def confirm_payment_handler(callback: CallbackQuery):
    """Подтвердить оплату записи"""
    booking_id = int(callback.data.split("_")[-1])

    master = get_master_by_chat_id(callback.message.chat.id)
    if not master:
        await callback.answer("Ошибка")
        return

    booking = get_booking_details(booking_id)
    if not booking or booking["master_id"] != master.id:
        await callback.answer("Запись не найдена")
        return

    if confirm_booking_payment(booking_id):
        date_str = booking["start_time"].strftime("%d.%m.%Y")
        time_str = booking["start_time"].strftime("%H:%M")

        await callback.message.edit_text(
            f"✅ *Оплата подтверждена!*\n\n"
            f"👤 Клиент: {booking['client_name']}\n"
            f"💇 Услуга: {booking['service_name']}\n"
            f"📅 Дата: {date_str}\n"
            f"🕐 Время: {time_str}\n"
            f"💵 Сумма: {booking['total_price']} ₸",
            parse_mode="Markdown"
        )
        await callback.message.answer("Выберите действие:", reply_markup=get_main_menu())
        await callback.answer("Оплата подтверждена!")
    else:
        await callback.answer("Ошибка при подтверждении оплаты")