import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from database import engine, Base

logger = logging.getLogger(__name__)
from models import (
    Service, Master, MasterService, MasterSchedule, Client, Booking,
    Salon, SalonService, SalonGallery, MasterPortfolio, OTPCode
)
from routers import services, masters, bookings, salons
from routers import salon_gallery, my_bookings
from init_salons import init_database
from config import CORS_MODE, CORS_ORIGINS, CORS_ORIGIN_REGEX

# Create database tables
Base.metadata.create_all(bind=engine)
# Демо-каталог при пустой БД; не роняем весь процесс, если сид не удался (Railway / лимиты памяти)
try:
    init_database()
except Exception:
    logger.exception("init_database failed; API starts without seeded catalog")

app = FastAPI(
    title="SalonSync - Beauty Salon Aggregator API",
    description="API для платформы-агрегатора салонов красоты Алматы",
    version="2.0.0"
)

# CORS: по умолчанию open — любой сайт может вызывать API (fetch без credentials).
# Строгий список: Railway → Variables → CORS_MODE=strict и задайте CORS_ORIGINS.
if CORS_MODE == "strict":
    app.add_middleware(
        CORSMiddleware,
        allow_origins=CORS_ORIGINS,
        allow_origin_regex=CORS_ORIGIN_REGEX,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
else:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=False,
        allow_methods=["*"],
        allow_headers=["*"],
    )

# Include routers
app.include_router(salons.router)
app.include_router(services.router)
app.include_router(masters.router)
app.include_router(bookings.router)
app.include_router(salon_gallery.router)
app.include_router(my_bookings.router)


@app.get("/")
def read_root():
    return {"message": "Welcome to Beauty Salon API"}


@app.get("/health")
def health_check():
    return {"status": "healthy"}