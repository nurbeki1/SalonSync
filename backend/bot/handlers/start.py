from typing import Optional, List
from aiogram import Router, F
from aiogram.types import Message
from aiogram.filters import CommandStart
from sqlalchemy.orm import Session

import sys
sys.path.append("..")
from database import SessionLocal
from models import Master, MasterStatus
from bot.keyboards.main_menu import get_main_menu, get_not_registered_menu, get_pending_menu

router = Router()


def get_master_by_chat_id(chat_id: int) -> Optional[Master]:
    """Получить мастера по chat_id"""
    db = SessionLocal()
    try:
        return db.query(Master).filter(Master.telegram_chat_id == str(chat_id)).first()
    finally:
        db.close()


@router.message(CommandStart())
async def cmd_start(message: Message):
    """Обработчик команды /start"""
    chat_id = message.chat.id
    master = get_master_by_chat_id(chat_id)

    if master is None:
        # Не зарегистрирован
        await message.answer(
            "👋 Добро пожаловать в Beauty Studio Bot!\n\n"
            "Этот бот предназначен для мастеров салона красоты.\n\n"
            "Здесь вы можете:\n"
            "• Зарегистрироваться как мастер\n"
            "• Управлять своим расписанием\n"
            "• Получать уведомления о записях\n"
            "• Экспортировать записи в Excel\n\n"
            "Нажмите кнопку ниже, чтобы начать регистрацию:",
            reply_markup=get_not_registered_menu()
        )
    elif master.status == MasterStatus.PENDING:
        # На модерации
        await message.answer(
            "⏳ Ваша заявка на модерации.\n\n"
            "Мы проверяем ваши данные и скоро свяжемся с вами.\n"
            "Обычно это занимает до 24 часов.",
            reply_markup=get_pending_menu()
        )
    elif master.status == MasterStatus.REJECTED:
        # Отклонён
        await message.answer(
            "❌ К сожалению, ваша заявка была отклонена.\n\n"
            "Если вы считаете это ошибкой, свяжитесь с администрацией.",
            reply_markup=get_not_registered_menu()
        )
    else:
        # Одобрен
        await message.answer(
            f"👋 Привет, {master.name}!\n\n"
            "Выберите действие:",
            reply_markup=get_main_menu()
        )


@router.message(F.text == "🔄 Проверить статус заявки")
async def check_status(message: Message):
    """Проверка статуса заявки"""
    chat_id = message.chat.id
    master = get_master_by_chat_id(chat_id)

    if master is None:
        await message.answer(
            "Вы ещё не подавали заявку на регистрацию.",
            reply_markup=get_not_registered_menu()
        )
    elif master.status == MasterStatus.PENDING:
        await message.answer(
            "⏳ Ваша заявка всё ещё на модерации.\n"
            "Пожалуйста, подождите.",
            reply_markup=get_pending_menu()
        )
    elif master.status == MasterStatus.APPROVED:
        await message.answer(
            "✅ Ваша заявка одобрена! Добро пожаловать!",
            reply_markup=get_main_menu()
        )
    else:
        await message.answer(
            "❌ Ваша заявка была отклонена.",
            reply_markup=get_not_registered_menu()
        )