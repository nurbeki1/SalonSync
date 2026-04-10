"""
Telegram Bot для мастеров салона красоты
Запуск: python -m bot.main
"""
import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage

import sys
sys.path.append("..")
from config import TELEGRAM_BOT_TOKEN
from bot.handlers import get_all_routers

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


async def main():
    """Запуск бота"""
    if not TELEGRAM_BOT_TOKEN or TELEGRAM_BOT_TOKEN == "YOUR_BOT_TOKEN_HERE":
        logger.error("❌ TELEGRAM_BOT_TOKEN не настроен!")
        logger.error("Создайте файл .env и добавьте: TELEGRAM_BOT_TOKEN=your_token")
        return

    # Инициализация бота
    bot = Bot(token=TELEGRAM_BOT_TOKEN)
    storage = MemoryStorage()
    dp = Dispatcher(storage=storage)

    # Регистрация роутеров
    for router in get_all_routers():
        dp.include_router(router)

    logger.info("🚀 Бот запущен!")

    try:
        await dp.start_polling(bot)
    finally:
        await bot.session.close()


if __name__ == "__main__":
    asyncio.run(main())