from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from database import engine, Base
from models import (
    Service, Master, MasterService, MasterSchedule, Client, Booking,
    Salon, SalonService, SalonGallery, MasterPortfolio, OTPCode
)
from routers import services, masters, bookings, salons
from routers import salon_gallery, my_bookings

# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="SalonSync - Beauty Salon Aggregator API",
    description="API для платформы-агрегатора салонов красоты Алматы",
    version="2.0.0"
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:3001"],
    allow_credentials=True,
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