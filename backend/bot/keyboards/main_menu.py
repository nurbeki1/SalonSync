from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton


def get_main_menu() -> ReplyKeyboardMarkup:
    """Главное меню мастера"""
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="📅 Установить график")],
            [KeyboardButton(text="📋 Мои записи")],
            [KeyboardButton(text="📊 Экспорт в Excel")],
            [KeyboardButton(text="⚙️ Настройки")],
        ],
        resize_keyboard=True
    )
    return keyboard


def get_not_registered_menu() -> ReplyKeyboardMarkup:
    """Меню для незарегистрированного пользователя"""
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="💇 Зарегистрироваться как мастер")],
        ],
        resize_keyboard=True
    )
    return keyboard


def get_pending_menu() -> ReplyKeyboardMarkup:
    """Меню для мастера на модерации"""
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="🔄 Проверить статус заявки")],
        ],
        resize_keyboard=True
    )
    return keyboard


def get_specializations_keyboard() -> InlineKeyboardMarkup:
    """Клавиатура выбора специализации"""
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="💇‍♀️ Парикмахер", callback_data="spec_hairdresser")],
        [InlineKeyboardButton(text="💅 Мастер маникюра", callback_data="spec_manicure")],
        [InlineKeyboardButton(text="💄 Визажист", callback_data="spec_makeup")],
        [InlineKeyboardButton(text="✂️ Барбер", callback_data="spec_barber")],
        [InlineKeyboardButton(text="🧖‍♀️ Косметолог", callback_data="spec_cosmetologist")],
    ])
    return keyboard


def get_confirmation_keyboard() -> InlineKeyboardMarkup:
    """Клавиатура подтверждения"""
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="✅ Подтвердить", callback_data="confirm_yes"),
            InlineKeyboardButton(text="❌ Отмена", callback_data="confirm_no"),
        ]
    ])
    return keyboard