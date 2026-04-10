from typing import Optional, List
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from datetime import datetime, time

import sys
sys.path.append("..")
from database import SessionLocal
from models import Master, MasterSchedule, MasterStatus
from bot.states import ScheduleStates
from bot.keyboards.main_menu import get_main_menu
from bot.keyboards.schedule_kb import get_dates_keyboard, get_time_keyboard

router = Router()


def get_master_by_chat_id(chat_id: int) -> Optional[Master]:
    db = SessionLocal()
    try:
        return db.query(Master).filter(Master.telegram_chat_id == str(chat_id)).first()
    finally:
        db.close()


@router.message(F.text == "📅 Установить график")
async def set_schedule_start(message: Message, state: FSMContext):
    """Начало установки графика"""
    master = get_master_by_chat_id(message.chat.id)

    if not master or master.status != MasterStatus.APPROVED:
        await message.answer("❌ Эта функция доступна только одобренным мастерам.")
        return

    await state.set_state(ScheduleStates.select_date)
    await message.answer(
        "📅 Выберите дату, на которую хотите установить график работы:",
        reply_markup=get_dates_keyboard(14)
    )


@router.callback_query(ScheduleStates.select_date, F.data.startswith("date_"))
async def process_date(callback: CallbackQuery, state: FSMContext):
    """Обработка выбора даты"""
    date_str = callback.data.replace("date_", "")
    selected_date = datetime.fromisoformat(date_str).date()

    await state.update_data(selected_date=date_str)
    await state.set_state(ScheduleStates.select_start_time)

    day_names = ["Понедельник", "Вторник", "Среда", "Четверг", "Пятница", "Суббота", "Воскресенье"]
    day_name = day_names[selected_date.weekday()]

    await callback.message.edit_text(
        f"📅 Дата: {day_name}, {selected_date.strftime('%d.%m.%Y')}\n\n"
        f"🕐 Выберите время НАЧАЛА работы:",
        reply_markup=get_time_keyboard(8, 20)
    )
    await callback.answer()


@router.callback_query(ScheduleStates.select_start_time, F.data.startswith("time_"))
async def process_start_time(callback: CallbackQuery, state: FSMContext):
    """Обработка времени начала"""
    time_str = callback.data.replace("time_", "")

    await state.update_data(start_time=time_str)
    await state.set_state(ScheduleStates.select_end_time)

    data = await state.get_data()
    start_hour = int(time_str.split(":")[0])

    await callback.message.edit_text(
        f"🕐 Начало: {time_str}\n\n"
        f"🕐 Выберите время ОКОНЧАНИЯ работы:",
        reply_markup=get_time_keyboard(start_hour + 1, 22)
    )
    await callback.answer()


@router.callback_query(ScheduleStates.select_end_time, F.data.startswith("time_"))
async def process_end_time(callback: CallbackQuery, state: FSMContext):
    """Обработка времени окончания и сохранение"""
    time_str = callback.data.replace("time_", "")
    data = await state.get_data()

    date_str = data["selected_date"]
    start_time_str = data["start_time"]
    end_time_str = time_str

    selected_date = datetime.fromisoformat(date_str).date()
    start_time = time(int(start_time_str.split(":")[0]), 0)
    end_time = time(int(end_time_str.split(":")[0]), 0)

    master = get_master_by_chat_id(callback.message.chat.id)

    db = SessionLocal()
    try:
        # Удаляем старое расписание на эту дату
        db.query(MasterSchedule).filter(
            MasterSchedule.master_id == master.id,
            MasterSchedule.date == selected_date
        ).delete()

        # Создаём новое
        schedule = MasterSchedule(
            master_id=master.id,
            date=selected_date,
            start_time=start_time,
            end_time=end_time,
            is_available=True
        )
        db.add(schedule)
        db.commit()

        day_names = ["Понедельник", "Вторник", "Среда", "Четверг", "Пятница", "Суббота", "Воскресенье"]
        day_name = day_names[selected_date.weekday()]

        await callback.message.edit_text(
            f"✅ График установлен!\n\n"
            f"📅 Дата: {day_name}, {selected_date.strftime('%d.%m.%Y')}\n"
            f"🕐 Время: {start_time_str} - {end_time_str}\n\n"
            f"Теперь клиенты могут записаться к вам на это время."
        )
        await callback.message.answer(
            "Выберите действие:",
            reply_markup=get_main_menu()
        )

    except Exception as e:
        await callback.message.edit_text(f"❌ Ошибка: {e}")
    finally:
        db.close()

    await state.clear()
    await callback.answer()


@router.callback_query(F.data == "cancel")
async def cancel_action(callback: CallbackQuery, state: FSMContext):
    """Отмена действия"""
    await state.clear()
    await callback.message.edit_text("❌ Действие отменено.")
    await callback.message.answer(
        "Выберите действие:",
        reply_markup=get_main_menu()
    )
    await callback.answer()
