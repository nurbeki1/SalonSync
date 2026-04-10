from typing import Optional, List
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, BufferedInputFile
from datetime import datetime, timedelta
import io

import sys
sys.path.append("..")
from database import SessionLocal
from models import Master, Booking, Client, Service, MasterStatus, BookingStatus
from bot.keyboards.main_menu import get_main_menu
from bot.keyboards.schedule_kb import get_export_keyboard

router = Router()


def get_master_by_chat_id(chat_id: int) -> Optional[Master]:
    db = SessionLocal()
    try:
        return db.query(Master).filter(Master.telegram_chat_id == str(chat_id)).first()
    finally:
        db.close()


def get_bookings_for_export(master_id: int, start_date: datetime, end_date: datetime) -> list:
    """Получить записи для экспорта"""
    db = SessionLocal()
    try:
        bookings = db.query(Booking).filter(
            Booking.master_id == master_id,
            Booking.start_time >= start_date,
            Booking.start_time < end_date
        ).order_by(Booking.start_time).all()

        result = []
        for b in bookings:
            client = db.query(Client).filter(Client.id == b.client_id).first()
            service = db.query(Service).filter(Service.id == b.service_id).first()
            result.append({
                "date": b.start_time.strftime("%d.%m.%Y"),
                "time": b.start_time.strftime("%H:%M"),
                "client_name": client.name if client else "—",
                "client_phone": client.phone if client else "—",
                "service_name": service.name if service else "—",
                "status": b.status.value,
                "price": str(b.total_price),
            })
        return result
    finally:
        db.close()


def create_excel(bookings: list, period: str) -> bytes:
    """Создать Excel файл (простой CSV для совместимости)"""
    # Используем CSV формат (можно открыть в Excel)
    output = io.StringIO()

    # Заголовки
    output.write("Дата;Время;Клиент;Телефон;Услуга;Статус;Сумма\n")

    # Данные
    for b in bookings:
        output.write(
            f"{b['date']};{b['time']};{b['client_name']};{b['client_phone']};"
            f"{b['service_name']};{b['status']};{b['price']}\n"
        )

    # Итого
    total = sum(float(b['price']) for b in bookings)
    output.write(f"\n;;;;;;Итого: {total} ₸\n")

    return output.getvalue().encode('utf-8-sig')  # BOM для Excel


@router.message(F.text == "📊 Экспорт в Excel")
async def show_export_menu(message: Message):
    """Меню экспорта"""
    master = get_master_by_chat_id(message.chat.id)

    if not master or master.status != MasterStatus.APPROVED:
        await message.answer("❌ Эта функция доступна только одобренным мастерам.")
        return

    await message.answer(
        "📊 Выберите период для экспорта:",
        reply_markup=get_export_keyboard()
    )


@router.callback_query(F.data == "export_day")
async def export_day(callback: CallbackQuery):
    """Экспорт за день"""
    master = get_master_by_chat_id(callback.message.chat.id)
    if not master:
        await callback.answer("Ошибка")
        return

    today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    tomorrow = today + timedelta(days=1)

    bookings = get_bookings_for_export(master.id, today, tomorrow)

    if not bookings:
        await callback.message.edit_text("😔 За сегодня нет записей для экспорта.")
        await callback.answer()
        return

    excel_data = create_excel(bookings, "день")
    filename = f"записи_{today.strftime('%d_%m_%Y')}.csv"

    file = BufferedInputFile(excel_data, filename=filename)
    await callback.message.answer_document(file, caption=f"📊 Записи за {today.strftime('%d.%m.%Y')}")
    await callback.message.delete()
    await callback.message.answer("Выберите действие:", reply_markup=get_main_menu())
    await callback.answer()


@router.callback_query(F.data == "export_week")
async def export_week(callback: CallbackQuery):
    """Экспорт за неделю"""
    master = get_master_by_chat_id(callback.message.chat.id)
    if not master:
        await callback.answer("Ошибка")
        return

    today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    week_ago = today - timedelta(days=7)

    bookings = get_bookings_for_export(master.id, week_ago, today + timedelta(days=1))

    if not bookings:
        await callback.message.edit_text("😔 За неделю нет записей для экспорта.")
        await callback.answer()
        return

    excel_data = create_excel(bookings, "неделя")
    filename = f"записи_неделя_{today.strftime('%d_%m_%Y')}.csv"

    file = BufferedInputFile(excel_data, filename=filename)
    await callback.message.answer_document(file, caption=f"📊 Записи за неделю")
    await callback.message.delete()
    await callback.message.answer("Выберите действие:", reply_markup=get_main_menu())
    await callback.answer()


@router.callback_query(F.data == "export_month")
async def export_month(callback: CallbackQuery):
    """Экспорт за месяц"""
    master = get_master_by_chat_id(callback.message.chat.id)
    if not master:
        await callback.answer("Ошибка")
        return

    today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    month_ago = today - timedelta(days=30)

    bookings = get_bookings_for_export(master.id, month_ago, today + timedelta(days=1))

    if not bookings:
        await callback.message.edit_text("😔 За месяц нет записей для экспорта.")
        await callback.answer()
        return

    excel_data = create_excel(bookings, "месяц")
    filename = f"записи_месяц_{today.strftime('%d_%m_%Y')}.csv"

    file = BufferedInputFile(excel_data, filename=filename)
    await callback.message.answer_document(file, caption=f"📊 Записи за месяц")
    await callback.message.delete()
    await callback.message.answer("Выберите действие:", reply_markup=get_main_menu())
    await callback.answer()