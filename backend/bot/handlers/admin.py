from typing import Optional, List
from aiogram import Router, F, Bot
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import Command

import sys
sys.path.append("..")
from database import SessionLocal
from models import Master, MasterStatus, MasterService, Service
from config import ADMIN_CHAT_ID, TELEGRAM_BOT_TOKEN

router = Router()

# Список админов (можно добавить несколько chat_id)
ADMIN_IDS = [ADMIN_CHAT_ID, "1374825128"]  # Добавь свой chat_id


def is_admin(chat_id: int) -> bool:
    """Проверить, является ли пользователь админом"""
    return str(chat_id) in ADMIN_IDS


def get_pending_masters() -> List[dict]:
    """Получить мастеров на модерации"""
    db = SessionLocal()
    try:
        masters = db.query(Master).filter(Master.status == MasterStatus.PENDING).all()
        result = []
        for m in masters:
            # Получаем услуги мастера
            services = db.query(Service).join(MasterService).filter(
                MasterService.master_id == m.id
            ).all()
            service_names = [s.name for s in services]

            result.append({
                "id": m.id,
                "name": m.name,
                "phone": m.phone,
                "specialization": m.specialization,
                "telegram_username": m.telegram_username,
                "telegram_chat_id": m.telegram_chat_id,
                "services": service_names,
                "created_at": m.created_at,
            })
        return result
    finally:
        db.close()


def get_pending_keyboard(master_id: int) -> InlineKeyboardMarkup:
    """Клавиатура для модерации"""
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="✅ Одобрить", callback_data=f"approve_{master_id}"),
            InlineKeyboardButton(text="❌ Отклонить", callback_data=f"reject_{master_id}"),
        ]
    ])


def get_admin_menu() -> InlineKeyboardMarkup:
    """Меню админа"""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📋 Заявки на модерацию", callback_data="admin_pending")],
        [InlineKeyboardButton(text="👥 Все мастера", callback_data="admin_all_masters")],
        [InlineKeyboardButton(text="📊 Статистика", callback_data="admin_stats")],
    ])


@router.message(Command("admin"))
async def cmd_admin(message: Message):
    """Команда /admin"""
    if not is_admin(message.chat.id):
        await message.answer("⛔ У вас нет доступа к админ-панели.")
        return

    await message.answer(
        "🔐 *Админ-панель*\n\nВыберите действие:",
        reply_markup=get_admin_menu(),
        parse_mode="Markdown"
    )


@router.callback_query(F.data == "admin_pending")
async def show_pending(callback: CallbackQuery):
    """Показать заявки на модерацию"""
    if not is_admin(callback.message.chat.id):
        await callback.answer("⛔ Нет доступа")
        return

    masters = get_pending_masters()

    if not masters:
        await callback.message.edit_text(
            "✅ Нет заявок на модерации!",
            reply_markup=get_admin_menu()
        )
        await callback.answer()
        return

    await callback.message.edit_text(f"📋 Заявки на модерации: {len(masters)}")

    for m in masters:
        services_text = ", ".join(m["services"][:3])
        if len(m["services"]) > 3:
            services_text += f" (+{len(m['services']) - 3})"

        text = (
            f"👤 *{m['name']}*\n"
            f"💼 {m['specialization'] or '—'}\n"
            f"📱 {m['phone'] or '—'}\n"
            f"💬 {m['telegram_username'] or '—'}\n"
            f"🛠 Услуги: {services_text or '—'}\n"
        )

        await callback.message.answer(
            text,
            reply_markup=get_pending_keyboard(m["id"]),
            parse_mode="Markdown"
        )

    await callback.answer()


@router.callback_query(F.data.startswith("approve_"))
async def approve_master(callback: CallbackQuery):
    """Одобрить мастера"""
    if not is_admin(callback.message.chat.id):
        await callback.answer("⛔ Нет доступа")
        return

    master_id = int(callback.data.split("_")[1])

    db = SessionLocal()
    try:
        master = db.query(Master).filter(Master.id == master_id).first()
        if not master:
            await callback.answer("Мастер не найден")
            return

        master.status = MasterStatus.APPROVED
        master.is_active = True
        db.commit()

        # Уведомляем мастера
        if master.telegram_chat_id and TELEGRAM_BOT_TOKEN:
            try:
                bot = Bot(token=TELEGRAM_BOT_TOKEN)
                await bot.send_message(
                    chat_id=master.telegram_chat_id,
                    text=(
                        "🎉 *Поздравляем!*\n\n"
                        "Ваша заявка одобрена!\n"
                        "Теперь вы можете:\n"
                        "• Установить график работы\n"
                        "• Получать записи от клиентов\n\n"
                        "Нажмите /start чтобы открыть меню."
                    ),
                    parse_mode="Markdown"
                )
                await bot.session.close()
            except Exception as e:
                print(f"Error notifying master: {e}")

        await callback.message.edit_text(
            f"✅ Мастер *{master.name}* одобрен!",
            parse_mode="Markdown"
        )

    finally:
        db.close()

    await callback.answer("Одобрено!")


@router.callback_query(F.data.startswith("reject_"))
async def reject_master(callback: CallbackQuery):
    """Отклонить мастера"""
    if not is_admin(callback.message.chat.id):
        await callback.answer("⛔ Нет доступа")
        return

    master_id = int(callback.data.split("_")[1])

    db = SessionLocal()
    try:
        master = db.query(Master).filter(Master.id == master_id).first()
        if not master:
            await callback.answer("Мастер не найден")
            return

        master.status = MasterStatus.REJECTED
        master.is_active = False
        db.commit()

        # Уведомляем мастера
        if master.telegram_chat_id and TELEGRAM_BOT_TOKEN:
            try:
                bot = Bot(token=TELEGRAM_BOT_TOKEN)
                await bot.send_message(
                    chat_id=master.telegram_chat_id,
                    text=(
                        "😔 К сожалению, ваша заявка отклонена.\n\n"
                        "Если вы считаете это ошибкой, "
                        "свяжитесь с администрацией."
                    )
                )
                await bot.session.close()
            except Exception as e:
                print(f"Error notifying master: {e}")

        await callback.message.edit_text(
            f"❌ Мастер *{master.name}* отклонён.",
            parse_mode="Markdown"
        )

    finally:
        db.close()

    await callback.answer("Отклонено")


@router.callback_query(F.data == "admin_all_masters")
async def show_all_masters(callback: CallbackQuery):
    """Показать всех мастеров"""
    if not is_admin(callback.message.chat.id):
        await callback.answer("⛔ Нет доступа")
        return

    db = SessionLocal()
    try:
        masters = db.query(Master).all()

        if not masters:
            await callback.message.edit_text(
                "👥 Мастеров пока нет.",
                reply_markup=get_admin_menu()
            )
            await callback.answer()
            return

        text = "👥 *Все мастера:*\n\n"
        for m in masters:
            status_emoji = {
                MasterStatus.PENDING: "⏳",
                MasterStatus.APPROVED: "✅",
                MasterStatus.REJECTED: "❌",
            }.get(m.status, "❓")

            text += f"{status_emoji} {m.name} ({m.specialization or '—'})\n"

        await callback.message.edit_text(
            text,
            reply_markup=get_admin_menu(),
            parse_mode="Markdown"
        )

    finally:
        db.close()

    await callback.answer()


@router.callback_query(F.data == "admin_stats")
async def show_stats(callback: CallbackQuery):
    """Показать статистику"""
    if not is_admin(callback.message.chat.id):
        await callback.answer("⛔ Нет доступа")
        return

    db = SessionLocal()
    try:
        from models import Booking, Client, BookingStatus

        total_masters = db.query(Master).count()
        approved_masters = db.query(Master).filter(Master.status == MasterStatus.APPROVED).count()
        pending_masters = db.query(Master).filter(Master.status == MasterStatus.PENDING).count()

        total_bookings = db.query(Booking).count()
        paid_bookings = db.query(Booking).filter(Booking.status == BookingStatus.PAID).count()

        total_clients = db.query(Client).count()

        text = (
            "📊 *Статистика*\n\n"
            f"👥 Мастера: {total_masters}\n"
            f"   ├ Активных: {approved_masters}\n"
            f"   └ На модерации: {pending_masters}\n\n"
            f"📋 Записей: {total_bookings}\n"
            f"   └ Оплачено: {paid_bookings}\n\n"
            f"👤 Клиентов: {total_clients}"
        )

        await callback.message.edit_text(
            text,
            reply_markup=get_admin_menu(),
            parse_mode="Markdown"
        )

    finally:
        db.close()

    await callback.answer()
