"""Менің жазылуларым — телефон + OTP арқылы (тіркелусіз)"""
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks, Query
from sqlalchemy.orm import Session
from typing import List

from database import get_db
from models import Booking, Client, Master, Service, BookingStatus as BookingStatusModel
from schemas import (
    OTPRequest, OTPVerify, OTPVerifyResponse,
    BookingDetailResponse,
)
from services.otp import generate_otp_code, verify_otp_code, create_access_token, verify_access_token

router = APIRouter(prefix="/my-bookings", tags=["My Bookings"])


def _get_client_bookings(db: Session, phone: str) -> list:
    """Клиент жазылуларын алу"""
    client = db.query(Client).filter(Client.phone == phone).first()
    if not client:
        return []

    bookings = db.query(Booking).filter(
        Booking.client_id == client.id
    ).order_by(Booking.start_time.desc()).all()

    result = []
    for booking in bookings:
        booking.client = client
        booking.master = db.query(Master).filter(Master.id == booking.master_id).first()
        booking.service = db.query(Service).filter(Service.id == booking.service_id).first()
        result.append(booking)

    return result


@router.post("/send-code")
async def send_otp_code(
    data: OTPRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """Телефонға OTP код жіберу (WhatsApp арқылы)"""
    phone = "".join(c for c in data.phone if c.isdigit())
    if len(phone) < 10:
        raise HTTPException(status_code=400, detail="Қате телефон номері")

    try:
        code = generate_otp_code(db, phone)
    except ValueError as e:
        raise HTTPException(status_code=429, detail=str(e))

    # WhatsApp арқылы код жіберу (фонда)
    async def send_code():
        try:
            from services.whatsapp import send_otp_code as wa_send_otp
            await wa_send_otp(phone, code)
        except Exception as e:
            print(f"OTP send error: {e}")

    background_tasks.add_task(send_code)

    return {"message": "Код жіберілді", "phone": phone}


@router.post("/verify", response_model=OTPVerifyResponse)
def verify_code(
    data: OTPVerify,
    db: Session = Depends(get_db)
):
    """OTP кодты тексеру, жазылулар тізімін қайтару"""
    phone = "".join(c for c in data.phone if c.isdigit())

    if not verify_otp_code(db, phone, data.code):
        raise HTTPException(status_code=400, detail="Қате код немесе мерзімі өтті")

    token = create_access_token(phone)
    bookings = _get_client_bookings(db, phone)

    return OTPVerifyResponse(
        verified=True,
        token=token,
        bookings=bookings,
    )


@router.get("/", response_model=List[BookingDetailResponse])
def get_my_bookings(
    token: str = Query(..., description="JWT token from verify"),
    db: Session = Depends(get_db)
):
    """Жазылулар тізімі (token арқылы)"""
    phone = verify_access_token(token)
    if not phone:
        raise HTTPException(status_code=401, detail="Токен мерзімі өтті, қайта кіріңіз")

    return _get_client_bookings(db, phone)


@router.delete("/{booking_id}")
async def cancel_my_booking(
    booking_id: int,
    token: str = Query(..., description="JWT token from verify"),
    background_tasks: BackgroundTasks = None,
    db: Session = Depends(get_db)
):
    """Жазылуды бас тарту (тек PENDING/CONFIRMED)"""
    phone = verify_access_token(token)
    if not phone:
        raise HTTPException(status_code=401, detail="Токен мерзімі өтті")

    client = db.query(Client).filter(Client.phone == phone).first()
    if not client:
        raise HTTPException(status_code=404, detail="Клиент табылмады")

    booking = db.query(Booking).filter(
        Booking.id == booking_id,
        Booking.client_id == client.id
    ).first()
    if not booking:
        raise HTTPException(status_code=404, detail="Жазылу табылмады")

    if booking.status not in (BookingStatusModel.PENDING, BookingStatusModel.CONFIRMED):
        raise HTTPException(status_code=400, detail="Бұл жазылуды бас тарту мүмкін емес")

    booking.status = BookingStatusModel.CANCELLED
    db.commit()

    # Хабарлама жіберу
    if background_tasks:
        async def send_cancel():
            try:
                from services.whatsapp import notify_client_booking_cancelled
                await notify_client_booking_cancelled(booking_id)
            except Exception as e:
                print(f"Cancel notification error: {e}")
        background_tasks.add_task(send_cancel)

    return {"message": "Жазылу бас тартылды"}
