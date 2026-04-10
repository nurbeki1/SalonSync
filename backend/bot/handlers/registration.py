from typing import List
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, ContentType
from aiogram.fsm.context import FSMContext

import sys
sys.path.append("..")
from database import SessionLocal
from models import Master, MasterService, MasterStatus, Service
from bot.states import RegistrationStates
from bot.keyboards.main_menu import get_specializations_keyboard, get_confirmation_keyboard, get_pending_menu
from bot.keyboards.services_kb import get_services_keyboard
from config import ADMIN_CHAT_ID

router = Router()

SPECIALIZATIONS = {
    "spec_hairdresser": "Парикмахер",
    "spec_manicure": "Мастер маникюра",
    "spec_makeup": "Визажист",
    "spec_barber": "Барбер",
    "spec_cosmetologist": "Косметолог",
}


def get_all_services() -> List[dict]:
    """Получить все услуги"""
    db = SessionLocal()
    try:
        services = db.query(Service).filter(Service.is_active == True).all()
        return [{"id": s.id, "name": s.name} for s in services]
    finally:
        db.close()


@router.message(F.text == "💇 Зарегистрироваться как мастер")
async def start_registration(message: Message, state: FSMContext):
    """Начало регистрации"""
    await state.set_state(RegistrationStates.waiting_for_name)
    await message.answer(
        "📝 Начинаем регистрацию!\n\n"
        "Шаг 1/5: Введите ваше полное имя:"
    )


@router.message(RegistrationStates.waiting_for_name)
async def process_name(message: Message, state: FSMContext):
    """Обработка имени"""
    name = message.text.strip()
    if len(name) < 2:
        await message.answer("Имя слишком короткое. Попробуйте ещё раз:")
        return

    await state.update_data(name=name)
    await state.set_state(RegistrationStates.waiting_for_photo)
    await message.answer(
        "📸 Шаг 2/5: Отправьте ваше фото:\n\n"
        "(Это фото будет показано клиентам на сайте)"
    )


@router.message(RegistrationStates.waiting_for_photo, F.content_type == ContentType.PHOTO)
async def process_photo(message: Message, state: FSMContext):
    """Обработка фото"""
    photo = message.photo[-1]  # Берём фото максимального размера
    file_id = photo.file_id

    await state.update_data(photo_file_id=file_id)
    await state.set_state(RegistrationStates.waiting_for_specialization)
    await message.answer(
        "💼 Шаг 3/5: Выберите вашу специализацию:",
        reply_markup=get_specializations_keyboard()
    )


@router.message(RegistrationStates.waiting_for_photo)
async def process_photo_invalid(message: Message):
    """Если прислали не фото"""
    await message.answer("Пожалуйста, отправьте фото (не файл).")


@router.callback_query(RegistrationStates.waiting_for_specialization, F.data.startswith("spec_"))
async def process_specialization(callback: CallbackQuery, state: FSMContext):
    """Обработка специализации"""
    spec_key = callback.data
    specialization = SPECIALIZATIONS.get(spec_key, "Другое")

    await state.update_data(specialization=specialization)
    await state.set_state(RegistrationStates.waiting_for_services)

    services = get_all_services()
    await state.update_data(available_services=services, selected_services=set())

    await callback.message.edit_text(
        "🛠 Шаг 4/5: Выберите услуги, которые вы предоставляете:\n\n"
        "(Можно выбрать несколько)",
        reply_markup=get_services_keyboard(services, set())
    )
    await callback.answer()


@router.callback_query(RegistrationStates.waiting_for_services, F.data.startswith("service_"))
async def toggle_service(callback: CallbackQuery, state: FSMContext):
    """Переключение услуги"""
    service_id = int(callback.data.split("_")[1])

    data = await state.get_data()
    selected = data.get("selected_services", set())
    services = data.get("available_services", [])

    if service_id in selected:
        selected.discard(service_id)
    else:
        selected.add(service_id)

    await state.update_data(selected_services=selected)
    await callback.message.edit_reply_markup(
        reply_markup=get_services_keyboard(services, selected)
    )
    await callback.answer()


@router.callback_query(RegistrationStates.waiting_for_services, F.data == "services_done")
async def services_done(callback: CallbackQuery, state: FSMContext):
    """Завершение выбора услуг"""
    data = await state.get_data()
    selected = data.get("selected_services", set())

    if not selected:
        await callback.answer("Выберите хотя бы одну услугу!", show_alert=True)
        return

    await state.set_state(RegistrationStates.waiting_for_phone)
    await callback.message.edit_text(
        "📱 Шаг 5/5: Введите ваш номер телефона:\n\n"
        "Формат: +7 777 123 4567"
    )
    await callback.answer()


@router.message(RegistrationStates.waiting_for_phone)
async def process_phone(message: Message, state: FSMContext):
    """Обработка телефона"""
    phone = message.text.strip()

    # Простая валидация
    if len(phone) < 10:
        await message.answer("Некорректный номер телефона. Попробуйте ещё раз:")
        return

    await state.update_data(phone=phone)
    await state.set_state(RegistrationStates.confirmation)

    data = await state.get_data()
    services_count = len(data.get("selected_services", set()))

    await message.answer(
        f"📋 Проверьте ваши данные:\n\n"
        f"👤 Имя: {data['name']}\n"
        f"💼 Специализация: {data['specialization']}\n"
        f"🛠 Услуги: {services_count} шт.\n"
        f"📱 Телефон: {phone}\n\n"
        f"Всё верно?",
        reply_markup=get_confirmation_keyboard()
    )


@router.callback_query(RegistrationStates.confirmation, F.data == "confirm_yes")
async def confirm_registration(callback: CallbackQuery, state: FSMContext):
    """Подтверждение регистрации"""
    data = await state.get_data()
    chat_id = callback.message.chat.id
    username = callback.from_user.username

    db = SessionLocal()
    try:
        # Создаём мастера
        master = Master(
            name=data["name"],
            specialization=data["specialization"],
            phone=data["phone"],
            photo_url=data.get("photo_file_id"),  # Сохраняем file_id
            telegram_chat_id=str(chat_id),
            telegram_username=f"@{username}" if username else None,
            status=MasterStatus.PENDING,
            is_active=False,
        )
        db.add(master)
        db.commit()
        db.refresh(master)

        # Добавляем услуги
        for service_id in data.get("selected_services", set()):
            ms = MasterService(master_id=master.id, service_id=service_id)
            db.add(ms)
        db.commit()

        await callback.message.edit_text(
            "✅ Заявка успешно отправлена!\n\n"
            "Ожидайте подтверждения от администратора.\n"
            "Обычно это занимает до 24 часов.\n\n"
            "Мы уведомим вас, когда заявка будет рассмотрена."
        )
        await callback.message.answer(
            "Используйте кнопку ниже, чтобы проверить статус:",
            reply_markup=get_pending_menu()
        )

        # TODO: Отправить уведомление админу о новой заявке

    except Exception as e:
        await callback.message.edit_text(f"❌ Ошибка при регистрации: {e}")
    finally:
        db.close()

    await state.clear()
    await callback.answer()


@router.callback_query(RegistrationStates.confirmation, F.data == "confirm_no")
async def cancel_registration(callback: CallbackQuery, state: FSMContext):
    """Отмена регистрации"""
    await state.clear()
    await callback.message.edit_text(
        "❌ Регистрация отменена.\n\n"
        "Вы можете начать заново, нажав кнопку ниже."
    )
    await callback.answer()
