from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from typing import List, Set


def get_services_keyboard(
    services: List[dict],
    selected_ids: Set[int]
) -> InlineKeyboardMarkup:
    """Клавиатура выбора услуг (множественный выбор)"""
    buttons = []

    for service in services:
        is_selected = service["id"] in selected_ids
        check = "✅" if is_selected else "⬜"
        text = f"{check} {service['name']}"

        buttons.append([
            InlineKeyboardButton(
                text=text,
                callback_data=f"service_{service['id']}"
            )
        ])

    buttons.append([
        InlineKeyboardButton(text="✅ Готово", callback_data="services_done")
    ])

    return InlineKeyboardMarkup(inline_keyboard=buttons)