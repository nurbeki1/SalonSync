from fastapi import APIRouter, Depends, HTTPException, Query, BackgroundTasks
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from typing import List
from datetime import datetime, timedelta, date, time
from decimal import Decimal

from database import get_db
from models import (
    Booking, Client, Master, Service, MasterService, MasterSchedule,
    BookingStatus as BookingStatusModel, MasterStatus
)
from schemas import (
    BookingCreate, BookingUpdate, BookingResponse, BookingDetailResponse,
    TimeSlot, AvailableSlotsResponse, AvailableDatesResponse, PaymentResponse,
    BookingStatus
)

router = APIRouter(prefix="/bookings", tags=["Bookings"])


# ============ Telegram Notifications ============
async def send_notifications(booking_id: int, notification_type: str):
    """Отправить уведомления мастеру (Telegram) и клиенту (WhatsApp)"""
    # Мастерге Telegram хабарлама
    try:
        if notification_type == "new":
            from bot.services.notifications import notify_master_new_booking
            await notify_master_new_booking(booking_id)
        elif notification_type == "paid":
            from bot.services.notifications import notify_master_payment_confirmed
            await notify_master_payment_confirmed(booking_id)
    except Exception as e:
        print(f"Telegram notification error: {e}")

    # Клиентке WhatsApp хабарлама
    try:
        from services.whatsapp import (
            notify_client_booking_created,
            notify_client_payment_confirmed,
        )
        if notification_type == "new":
            await notify_client_booking_created(booking_id)
        elif notification_type == "paid":
            await notify_client_payment_confirmed(booking_id)
    except Exception as e:
        print(f"WhatsApp notification error: {e}")


def get_or_create_client(db: Session, name: str, phone: str, email: str = None) -> Client:
    """Получить или создать клиента по телефону"""
    client = db.query(Client).filter(Client.phone == phone).first()
    if not client:
        client = Client(name=name, phone=phone, email=email)
        db.add(client)
        db.commit()
        db.refresh(client)
    return client


def get_service_duration_and_price(
    db: Session, master_id: int, service_id: int
) -> tuple[int, Decimal]:
    """Получить длительность и цену услуги для мастера"""
    master_service = db.query(MasterService).filter(
        MasterService.master_id == master_id,
        MasterService.service_id == service_id
    ).first()

    service = db.query(Service).filter(Service.id == service_id).first()
    if not service:
        raise HTTPException(status_code=404, detail="Услуга не найдена")

    # Используем кастомные значения мастера или стандартные
    duration = master_service.custom_duration if master_service and master_service.custom_duration else service.duration
    price = master_service.custom_price if master_service and master_service.custom_price else service.price

    return duration, price


def check_slot_available(
    db: Session,
    master_id: int,
    start_time: datetime,
    end_time: datetime,
    exclude_booking_id: int = None
) -> bool:
    """Проверить, свободен ли слот"""
    query = db.query(Booking).filter(
        Booking.master_id == master_id,
        Booking.status.notin_([BookingStatusModel.CANCELLED]),
        or_(
            # Новая запись начинается во время существующей
            and_(Booking.start_time <= start_time, Booking.end_time > start_time),
            # Новая запись заканчивается во время существующей
            and_(Booking.start_time < end_time, Booking.end_time >= end_time),
            # Новая запись полностью покрывает существующую
            and_(Booking.start_time >= start_time, Booking.end_time <= end_time)
        )
    )

    if exclude_booking_id:
        query = query.filter(Booking.id != exclude_booking_id)

    return query.first() is None


# ============ Available Dates ============
@router.get("/available-dates", response_model=AvailableDatesResponse)
def get_available_dates(
    master_id: int,
    service_id: int,
    month: str = Query(..., description="Ай форматы: YYYY-MM"),
    db: Session = Depends(get_db)
):
    """Қай күндерде бос слоттар бар екенін қайтару"""
    import calendar

    try:
        year, mon = map(int, month.split("-"))
    except ValueError:
        raise HTTPException(status_code=400, detail="Қате формат. YYYY-MM қолданыңыз")

    _, days_in_month = calendar.monthrange(year, mon)

    # Мастердің осы айдағы жұмыс күндерін алу
    month_start = date(year, mon, 1)
    month_end = date(year, mon, days_in_month)

    schedules = db.query(MasterSchedule).filter(
        MasterSchedule.master_id == master_id,
        MasterSchedule.date >= month_start,
        MasterSchedule.date <= month_end,
        MasterSchedule.is_available == True
    ).all()

    duration, _ = get_service_duration_and_price(db, master_id, service_id)

    available_dates = []
    for schedule in schedules:
        # Әр жұмыс күніне кемінде 1 бос слот бар ма тексеру
        current_time = datetime.combine(schedule.date, schedule.start_time)
        end_of_day = datetime.combine(schedule.date, schedule.end_time)

        has_slot = False
        while current_time + timedelta(minutes=duration) <= end_of_day:
            slot_end = current_time + timedelta(minutes=duration)
            if current_time > datetime.now():
                if check_slot_available(db, master_id, current_time, slot_end):
                    has_slot = True
                    break
            current_time += timedelta(minutes=30)

        if has_slot:
            available_dates.append(schedule.date.isoformat())

    return AvailableDatesResponse(
        master_id=master_id,
        service_id=service_id,
        month=month,
        dates=available_dates,
    )


# ============ Available Slots ============
@router.get("/available-slots", response_model=AvailableSlotsResponse)
def get_available_slots(
    master_id: int,
    service_id: int,
    date: date = Query(..., description="Дата в формате YYYY-MM-DD"),
    db: Session = Depends(get_db)
):
    """Получить свободные слоты для записи"""
    # Проверяем мастера (должен быть активен и одобрен)
    master = db.query(Master).filter(
        Master.id == master_id,
        Master.is_active == True,
        Master.status == MasterStatus.APPROVED
    ).first()
    if not master:
        raise HTTPException(status_code=404, detail="Мастер не найден или не активен")

    # Проверяем услугу
    service = db.query(Service).filter(Service.id == service_id, Service.is_active == True).first()
    if not service:
        raise HTTPException(status_code=404, detail="Услуга не найдена")

    # Проверяем, делает ли мастер эту услугу
    master_service = db.query(MasterService).filter(
        MasterService.master_id == master_id,
        MasterService.service_id == service_id
    ).first()
    if not master_service:
        raise HTTPException(status_code=400, detail="Мастер не предоставляет эту услугу")

    # Получаем длительность услуги
    duration, _ = get_service_duration_and_price(db, master_id, service_id)

    # Получаем график работы на конкретную ДАТУ (не день недели!)
    schedule = db.query(MasterSchedule).filter(
        MasterSchedule.master_id == master_id,
        MasterSchedule.date == date,
        MasterSchedule.is_available == True
    ).first()

    if not schedule:
        return AvailableSlotsResponse(
            master_id=master_id,
            service_id=service_id,
            date=datetime.combine(date, time.min),
            slots=[]
        )

    # Генерируем слоты с шагом 30 минут
    slots = []
    current_time = datetime.combine(date, schedule.start_time)
    end_of_day = datetime.combine(date, schedule.end_time)

    while current_time + timedelta(minutes=duration) <= end_of_day:
        slot_end = current_time + timedelta(minutes=duration)

        # Проверяем, не в прошлом ли слот
        if current_time > datetime.now():
            # Проверяем доступность слота
            if check_slot_available(db, master_id, current_time, slot_end):
                slots.append(TimeSlot(start_time=current_time, end_time=slot_end))

        current_time += timedelta(minutes=30)

    return AvailableSlotsResponse(
        master_id=master_id,
        service_id=service_id,
        date=datetime.combine(date, time.min),
        slots=slots
    )


# ============ Booking CRUD ============
@router.post("/", response_model=BookingResponse)
async def create_booking(
    booking: BookingCreate,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """Создать новую запись"""
    # Проверяем мастера
    master = db.query(Master).filter(
        Master.id == booking.master_id,
        Master.is_active == True,
        Master.status == MasterStatus.APPROVED
    ).first()
    if not master:
        raise HTTPException(status_code=404, detail="Мастер не найден или не активен")

    # Получаем длительность и цену
    duration, price = get_service_duration_and_price(db, booking.master_id, booking.service_id)

    # Вычисляем время окончания
    end_time = booking.start_time + timedelta(minutes=duration)

    # Проверяем доступность слота
    if not check_slot_available(db, booking.master_id, booking.start_time, end_time):
        raise HTTPException(status_code=400, detail="Выбранное время уже занято")

    # Получаем или создаём клиента
    client = get_or_create_client(
        db, booking.client_name, booking.client_phone, booking.client_email
    )

    # Создаём запись
    db_booking = Booking(
        client_id=client.id,
        master_id=booking.master_id,
        service_id=booking.service_id,
        start_time=booking.start_time,
        end_time=end_time,
        total_price=price,
        notes=booking.notes,
        status=BookingStatusModel.PENDING
    )
    db.add(db_booking)
    db.commit()
    db.refresh(db_booking)

    # Отправляем уведомление мастеру в фоне
    background_tasks.add_task(send_notifications, db_booking.id, "new")

    return db_booking


@router.get("/", response_model=List[BookingResponse])
def get_bookings(
    skip: int = 0,
    limit: int = 100,
    master_id: int = None,
    status: BookingStatus = None,
    date_from: date = None,
    date_to: date = None,
    db: Session = Depends(get_db)
):
    """Получить список записей с фильтрами"""
    query = db.query(Booking)

    if master_id:
        query = query.filter(Booking.master_id == master_id)
    if status:
        query = query.filter(Booking.status == BookingStatusModel[status.name])
    if date_from:
        query = query.filter(Booking.start_time >= datetime.combine(date_from, time.min))
    if date_to:
        query = query.filter(Booking.start_time <= datetime.combine(date_to, time.max))

    return query.order_by(Booking.start_time.desc()).offset(skip).limit(limit).all()


@router.get("/by-phone/{phone}", response_model=List[BookingDetailResponse])
def get_bookings_by_phone(phone: str, db: Session = Depends(get_db)):
    """Получить записи клиента по номеру телефона"""
    client = db.query(Client).filter(Client.phone == phone).first()
    if not client:
        return []

    bookings = db.query(Booking).filter(
        Booking.client_id == client.id
    ).order_by(Booking.start_time.desc()).all()

    # Подгружаем связанные данные
    result = []
    for booking in bookings:
        booking.client = client
        booking.master = db.query(Master).filter(Master.id == booking.master_id).first()
        booking.service = db.query(Service).filter(Service.id == booking.service_id).first()
        result.append(booking)

    return result


@router.get("/{booking_id}", response_model=BookingDetailResponse)
def get_booking(booking_id: int, db: Session = Depends(get_db)):
    """Получить запись по ID"""
    booking = db.query(Booking).filter(Booking.id == booking_id).first()
    if not booking:
        raise HTTPException(status_code=404, detail="Запись не найдена")

    # Подгружаем связанные данные
    booking.client = db.query(Client).filter(Client.id == booking.client_id).first()
    booking.master = db.query(Master).filter(Master.id == booking.master_id).first()
    booking.service = db.query(Service).filter(Service.id == booking.service_id).first()

    return booking


@router.patch("/{booking_id}", response_model=BookingResponse)
def update_booking(
    booking_id: int,
    booking: BookingUpdate,
    db: Session = Depends(get_db)
):
    """Обновить статус записи"""
    db_booking = db.query(Booking).filter(Booking.id == booking_id).first()
    if not db_booking:
        raise HTTPException(status_code=404, detail="Запись не найдена")

    update_data = booking.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        if key == "status":
            value = BookingStatusModel[value.name]
        setattr(db_booking, key, value)

    db.commit()
    db.refresh(db_booking)
    return db_booking


@router.delete("/{booking_id}")
async def cancel_booking(
    booking_id: int,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """Отменить запись"""
    db_booking = db.query(Booking).filter(Booking.id == booking_id).first()
    if not db_booking:
        raise HTTPException(status_code=404, detail="Запись не найдена")

    db_booking.status = BookingStatusModel.CANCELLED
    db.commit()

    # Уведомляем мастера и клиента об отмене
    async def send_cancel_notifications():
        try:
            client = db.query(Client).filter(Client.id == db_booking.client_id).first()
            master = db.query(Master).filter(Master.id == db_booking.master_id).first()
            date_str = db_booking.start_time.strftime("%d.%m.%Y")
            time_str = db_booking.start_time.strftime("%H:%M")
            if master and master.telegram_chat_id:
                from bot.services.notifications import notify_master_booking_cancelled
                await notify_master_booking_cancelled(
                    booking_id, client.name if client else "—",
                    date_str, time_str, master.telegram_chat_id
                )
        except Exception as e:
            print(f"Cancel telegram notification error: {e}")
        try:
            from services.whatsapp import notify_client_booking_cancelled
            await notify_client_booking_cancelled(booking_id)
        except Exception as e:
            print(f"Cancel whatsapp notification error: {e}")

    background_tasks.add_task(send_cancel_notifications)

    return {"message": "Запись отменена"}


# ============ Payment ============
@router.post("/{booking_id}/pay", response_model=PaymentResponse)
def generate_payment(booking_id: int, db: Session = Depends(get_db)):
    """Сгенерировать ссылку на оплату Kaspi с QR-кодом"""
    from services.kaspi import generate_kaspi_qr

    booking = db.query(Booking).filter(Booking.id == booking_id).first()
    if not booking:
        raise HTTPException(status_code=404, detail="Запись не найдена")

    if booking.status == BookingStatusModel.PAID:
        raise HTTPException(status_code=400, detail="Запись уже оплачена")

    if booking.status == BookingStatusModel.CANCELLED:
        raise HTTPException(status_code=400, detail="Запись отменена")

    # Генерируем Kaspi ссылку и QR-код
    kaspi_link, qr_base64 = generate_kaspi_qr(float(booking.total_price), booking_id)

    # Сохраняем ссылку в записи
    booking.payment_link = kaspi_link
    db.commit()

    return PaymentResponse(
        booking_id=booking_id,
        amount=booking.total_price,
        kaspi_link=kaspi_link,
        qr_code_base64=qr_base64
    )


@router.post("/{booking_id}/confirm-payment", response_model=BookingResponse)
async def confirm_payment(
    booking_id: int,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """Подтвердить оплату (webhook или ручное подтверждение)"""
    booking = db.query(Booking).filter(Booking.id == booking_id).first()
    if not booking:
        raise HTTPException(status_code=404, detail="Запись не найдена")

    if booking.status == BookingStatusModel.PAID:
        raise HTTPException(status_code=400, detail="Запись уже оплачена")

    booking.status = BookingStatusModel.PAID
    booking.payment_confirmed_at = datetime.now()
    db.commit()
    db.refresh(booking)

    # Уведомляем мастера об оплате
    background_tasks.add_task(send_notifications, booking_id, "paid")

    return booking