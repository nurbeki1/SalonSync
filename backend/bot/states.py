from aiogram.fsm.state import State, StatesGroup


class RegistrationStates(StatesGroup):
    """Состояния регистрации мастера"""
    waiting_for_name = State()
    waiting_for_photo = State()
    waiting_for_specialization = State()
    waiting_for_services = State()
    waiting_for_phone = State()
    confirmation = State()


class ScheduleStates(StatesGroup):
    """Состояния установки расписания"""
    select_date = State()
    select_start_time = State()
    select_end_time = State()
    confirmation = State()
