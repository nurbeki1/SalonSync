from typing import List
from aiogram import Router

from .start import router as start_router
from .registration import router as registration_router
from .schedule import router as schedule_router
from .bookings import router as bookings_router
from .export import router as export_router
from .admin import router as admin_router


def get_all_routers() -> List[Router]:
    return [
        start_router,
        registration_router,
        schedule_router,
        bookings_router,
        export_router,
        admin_router,
    ]