"""
Отдельный Telegram Bot для администраторов
Запуск: python -m bot.admin_bot
"""
import asyncio
import logging
from aiogram import Bot, Dispatcher, Router, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import CommandStart, Command
from aiogram.fsm.storage.memory import MemoryStorage
from typing import List

import sys
sys.path.append("..")
from database import SessionLocal
from models import Master, MasterStatus, MasterService, Service, Booking, Client, BookingStatus

# Токен админ-бота
ADMIN_BOT_TOKEN = "8631012199:AAHcJn5Qbj_1BCHxLsn0kjWRLQ8kvf44CRY"

# Токен основного бота (для уведомлений мастерам)
MASTER_BOT_TOKEN = "8790003711:AAHJjNjIegK79MbEdck67I0GHRAd4KQXqAM"

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = Router()


# ============ Keyboards ============
def get_main_menu() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📋 Заявки на модерацию", callback_data="pending")],
        [InlineKeyboardButton(text="👥 Все мастера", callback_data="all_masters")],
        [InlineKeyboardButton(text="📊 Статистика", callback_data="stats")],
        [InlineKeyboardButton(text="🔄 Обновить", callback_data="refresh")],
    ])


def get_master_keyboard(master_id: int) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="✅ Одобрить", callback_data=f"approve_{master_id}"),
            InlineKeyboardButton(text="❌ Отклонить", callback_data=f"reject_{master_id}"),
        ],
        [InlineKeyboardButton(text="◀️ Назад", callback_data="pending")],
    ])


# ============ Handlers ============
@router.message(CommandStart())
async def cmd_start(message: Message):
    await message.answer(
        "🔐 *Админ-панель Beauty Studio*\n\n"
        "Здесь вы можете управлять мастерами и просматривать статистику.",
        reply_markup=get_main_menu(),
        parse_mode="Markdown"
    )


@router.callback_query(F.data == "refresh")
async def refresh(callback: CallbackQuery):
    await callback.message.edit_text(
        "🔐 *Админ-панель Beauty Studio*\n\n"
        "Здесь вы можете управлять мастерами и просматривать статистику.",
        reply_markup=get_main_menu(),
        parse_mode="Markdown"
    )
    await callback.answer("Обновлено!")


@router.callback_query(F.data == "pending")
async def show_pending(callback: CallbackQuery):
    db = SessionLocal()
    try:
        masters = db.query(Master).filter(Master.status == MasterStatus.PENDING).all()

        if not masters:
            await callback.message.edit_text(
                "✅ *Нет заявок на модерации!*\n\n"
                "Все заявки обработаны.",
                reply_markup=get_main_menu(),
                parse_mode="Markdown"
            )
            await callback.answer()
            return

        # Показываем первого мастера
        master = masters[0]
        services = db.query(Service).join(MasterService).filter(
            MasterService.master_id == master.id
        ).all()
        service_names = ", ".join([s.name for s in services[:5]])

        text = (
            f"📋 *Заявка #{master.id}* (всего: {len(masters)})\n\n"
            f"👤 *Имя:* {master.name}\n"
            f"💼 *Специализация:* {master.specialization or '—'}\n"
            f"📱 *Телефон:* {master.phone or '—'}\n"
            f"💬 *Telegram:* {master.telegram_username or '—'}\n"
            f"🛠 *Услуги:* {service_names or '—'}\n"
        )

        await callback.message.edit_text(
            text,
            reply_markup=get_master_keyboard(master.id),
            parse_mode="Markdown"
        )

    finally:
        db.close()

    await callback.answer()


@router.callback_query(F.data.startswith("approve_"))
async def approve_master(callback: CallbackQuery):
    master_id = int(callback.data.split("_")[1])

    db = SessionLocal()
    try:
        master = db.query(Master).filter(Master.id == master_id).first()
        if not master:
            await callback.answer("Мастер не найден!")
            return

        master.status = MasterStatus.APPROVED
        master.is_active = True
        db.commit()

        # Уведомляем мастера через основной бот
        if master.telegram_chat_id:
            try:
                bot = Bot(token=MASTER_BOT_TOKEN)
                await bot.send_message(
                    chat_id=master.telegram_chat_id,
                    text=(
                        "🎉 *Поздравляем!*\n\n"
                        "Ваша заявка одобрена!\n\n"
                        "Теперь вы можете:\n"
                        "📅 Установить график работы\n"
                        "📋 Получать записи от клиентов\n"
                        "📊 Экспортировать данные\n\n"
                        "Нажмите /start чтобы начать!"
                    ),
                    parse_mode="Markdown"
                )
                await bot.session.close()
            except Exception as e:
                logger.error(f"Error notifying master: {e}")

        await callback.answer(f"✅ {master.name} одобрен!")

        # Показываем следующую заявку или меню
        remaining = db.query(Master).filter(Master.status == MasterStatus.PENDING).count()
        if remaining > 0:
            await show_pending(callback)
        else:
            await callback.message.edit_text(
                f"✅ *{master.name}* одобрен!\n\n"
                "Больше заявок нет.",
                reply_markup=get_main_menu(),
                parse_mode="Markdown"
            )

    finally:
        db.close()


@router.callback_query(F.data.startswith("reject_"))
async def reject_master(callback: CallbackQuery):
    master_id = int(callback.data.split("_")[1])

    db = SessionLocal()
    try:
        master = db.query(Master).filter(Master.id == master_id).first()
        if not master:
            await callback.answer("Мастер не найден!")
            return

        master.status = MasterStatus.REJECTED
        master.is_active = False
        db.commit()

        # Уведомляем мастера
        if master.telegram_chat_id:
            try:
                bot = Bot(token=MASTER_BOT_TOKEN)
                await bot.send_message(
                    chat_id=master.telegram_chat_id,
                    text=(
                        "😔 К сожалению, ваша заявка отклонена.\n\n"
                        "Если вы считаете это ошибкой, свяжитесь с администрацией."
                    )
                )
                await bot.session.close()
            except Exception as e:
                logger.error(f"Error notifying master: {e}")

        await callback.answer(f"❌ {master.name} отклонён")

        # Показываем следующую заявку
        remaining = db.query(Master).filter(Master.status == MasterStatus.PENDING).count()
        if remaining > 0:
            await show_pending(callback)
        else:
            await callback.message.edit_text(
                f"❌ *{master.name}* отклонён.\n\n"
                "Больше заявок нет.",
                reply_markup=get_main_menu(),
                parse_mode="Markdown"
            )

    finally:
        db.close()


@router.callback_query(F.data == "all_masters")
async def show_all_masters(callback: CallbackQuery):
    db = SessionLocal()
    try:
        masters = db.query(Master).order_by(Master.created_at.desc()).all()

        if not masters:
            await callback.message.edit_text(
                "👥 Мастеров пока нет.",
                reply_markup=get_main_menu(),
                parse_mode="Markdown"
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

            text += f"{status_emoji} *{m.name}*\n"
            text += f"    └ {m.specialization or 'Не указано'}\n"

        await callback.message.edit_text(
            text,
            reply_markup=get_main_menu(),
            parse_mode="Markdown"
        )

    finally:
        db.close()

    await callback.answer()


@router.callback_query(F.data == "stats")
async def show_stats(callback: CallbackQuery):
    db = SessionLocal()
    try:
        total_masters = db.query(Master).count()
        approved = db.query(Master).filter(Master.status == MasterStatus.APPROVED).count()
        pending = db.query(Master).filter(Master.status == MasterStatus.PENDING).count()
        rejected = db.query(Master).filter(Master.status == MasterStatus.REJECTED).count()

        total_bookings = db.query(Booking).count()
        pending_bookings = db.query(Booking).filter(Booking.status == BookingStatus.PENDING).count()
        paid_bookings = db.query(Booking).filter(Booking.status == BookingStatus.PAID).count()

        total_clients = db.query(Client).count()

        # Сумма оплаченных записей
        paid_sum = db.query(Booking).filter(Booking.status == BookingStatus.PAID).all()
        revenue = sum(float(b.total_price) for b in paid_sum)

        text = (
            "📊 *Статистика*\n\n"
            "👥 *Мастера:*\n"
            f"    ├ Всего: {total_masters}\n"
            f"    ├ ✅ Активных: {approved}\n"
            f"    ├ ⏳ На модерации: {pending}\n"
            f"    └ ❌ Отклонено: {rejected}\n\n"
            "📋 *Записи:*\n"
            f"    ├ Всего: {total_bookings}\n"
            f"    ├ ⏳ Ожидают: {pending_bookings}\n"
            f"    └ 💰 Оплачено: {paid_bookings}\n\n"
            f"👤 *Клиентов:* {total_clients}\n\n"
            f"💵 *Выручка:* {revenue:,.0f} ₸"
        )

        await callback.message.edit_text(
            text,
            reply_markup=get_main_menu(),
            parse_mode="Markdown"
        )

    finally:
        db.close()

    await callback.answer()


async def main():
    bot = Bot(token=ADMIN_BOT_TOKEN)
    dp = Dispatcher(storage=MemoryStorage())
    dp.include_router(router)

    logger.info("🔐 Админ-бот запущен!")

    try:
        await dp.start_polling(bot)
    finally:
        await bot.session.close()


if __name__ == "__main__":
    asyncio.run(main())
