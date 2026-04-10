from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from datetime import datetime, timedelta


def get_dates_keyboard(days: int = 14) -> InlineKeyboardMarkup:
    """Клавиатура выбора даты на ближайшие N дней"""
    buttons = []
    today = datetime.now().date()

    for i in range(days):
        date = today + timedelta(days=i)
        day_names = ["Пн", "Вт", "Ср", "Чт", "Пт", "Сб", "Вс"]
        day_name = day_names[date.weekday()]
        date_str = date.strftime("%d.%m")

        buttons.append([
            InlineKeyboardButton(
                text=f"{day_name}, {date_str}",
                callback_data=f"date_{date.isoformat()}"
            )
        ])

    buttons.append([InlineKeyboardButton(text="❌ Отмена", callback_data="cancel")])

    return InlineKeyboardMarkup(inline_keyboard=buttons)


def get_time_keyboard(start_hour: int = 8, end_hour: int = 22) -> InlineKeyboardMarkup:
    """Клавиатура выбора времени"""
    buttons = []
    row = []

    for hour in range(start_hour, end_hour + 1):
        time_str = f"{hour:02d}:00"
        row.append(InlineKeyboardButton(text=time_str, callback_data=f"time_{time_str}"))

        if len(row) == 4:
            buttons.append(row)
            row = []

    if row:
        buttons.append(row)

    buttons.append([InlineKeyboardButton(text="❌ Отмена", callback_data="cancel")])

    return InlineKeyboardMarkup(inline_keyboard=buttons)


def get_bookings_period_keyboard() -> InlineKeyboardMarkup:
    """Клавиатура выбора периода для просмотра записей"""
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📅 Сегодня", callback_data="bookings_today")],
        [InlineKeyboardButton(text="📅 Завтра", callback_data="bookings_tomorrow")],
        [InlineKeyboardButton(text="📅 Эта неделя", callback_data="bookings_week")],
        [InlineKeyboardButton(text="💰 Ожидают оплаты", callback_data="bookings_pending_payment")],
    ])
    return keyboard


def get_payment_confirmation_keyboard(booking_id: int) -> InlineKeyboardMarkup:
    """Клавиатура подтверждения оплаты"""
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="✅ Подтвердить оплату", callback_data=f"confirm_payment_{booking_id}"),
        ],
        [
            InlineKeyboardButton(text="⬅️ Назад", callback_data="bookings_pending_payment"),
        ],
    ])
    return keyboard


def get_pending_bookings_keyboard(bookings: list) -> InlineKeyboardMarkup:
    """Клавиатура со списком записей, ожидающих оплаты"""
    buttons = []
    for b in bookings:
        time_str = b["start_time"].strftime("%d.%m %H:%M")
        buttons.append([
            InlineKeyboardButton(
                text=f"💰 {time_str} - {b['client_name']} ({b['total_price']} ₸)",
                callback_data=f"view_pending_{b['id']}"
            )
        ])
    buttons.append([InlineKeyboardButton(text="⬅️ Назад", callback_data="back_to_bookings")])
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def get_export_keyboard() -> InlineKeyboardMarkup:
    """Клавиатура выбора периода для экспорта"""
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📊 За день", callback_data="export_day")],
        [InlineKeyboardButton(text="📊 За неделю", callback_data="export_week")],
        [InlineKeyboardButton(text="📊 За месяц", callback_data="export_month")],
    ])
    return keyboard