from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from database import get_db
from models import Master, MasterService, MasterSchedule, MasterPortfolio, Service
from schemas import (
    MasterCreate, MasterUpdate, MasterResponse,
    MasterServiceCreate, MasterServiceResponse,
    MasterScheduleCreate, MasterScheduleUpdate, MasterScheduleResponse,
    MasterPortfolioCreate, MasterPortfolioResponse,
    ServiceResponse
)

router = APIRouter(prefix="/masters", tags=["Masters"])


# ============ Master CRUD ============
@router.get("/", response_model=List[MasterResponse])
def get_masters(
    skip: int = 0,
    limit: int = 100,
    active_only: bool = True,
    db: Session = Depends(get_db)
):
    """Получить список всех мастеров"""
    query = db.query(Master)
    if active_only:
        query = query.filter(Master.is_active == True)
    return query.offset(skip).limit(limit).all()


@router.get("/{master_id}", response_model=MasterResponse)
def get_master(master_id: int, db: Session = Depends(get_db)):
    """Получить мастера по ID"""
    master = db.query(Master).filter(Master.id == master_id).first()
    if not master:
        raise HTTPException(status_code=404, detail="Мастер не найден")
    return master


@router.post("/", response_model=MasterResponse)
def create_master(master: MasterCreate, db: Session = Depends(get_db)):
    """Создать нового мастера"""
    db_master = Master(**master.model_dump())
    db.add(db_master)
    db.commit()
    db.refresh(db_master)
    return db_master


@router.put("/{master_id}", response_model=MasterResponse)
def update_master(
    master_id: int,
    master: MasterUpdate,
    db: Session = Depends(get_db)
):
    """Обновить мастера"""
    db_master = db.query(Master).filter(Master.id == master_id).first()
    if not db_master:
        raise HTTPException(status_code=404, detail="Мастер не найден")

    update_data = master.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_master, key, value)

    db.commit()
    db.refresh(db_master)
    return db_master


@router.delete("/{master_id}")
def delete_master(master_id: int, db: Session = Depends(get_db)):
    """Удалить мастера (soft delete)"""
    db_master = db.query(Master).filter(Master.id == master_id).first()
    if not db_master:
        raise HTTPException(status_code=404, detail="Мастер не найден")

    db_master.is_active = False
    db.commit()
    return {"message": "Мастер деактивирован"}


# ============ Master Services ============
@router.get("/{master_id}/services", response_model=List[ServiceResponse])
def get_master_services(master_id: int, db: Session = Depends(get_db)):
    """Получить услуги мастера"""
    master = db.query(Master).filter(Master.id == master_id).first()
    if not master:
        raise HTTPException(status_code=404, detail="Мастер не найден")

    master_services = db.query(MasterService).filter(
        MasterService.master_id == master_id
    ).all()

    services = []
    for ms in master_services:
        service = db.query(Service).filter(Service.id == ms.service_id).first()
        if service and service.is_active:
            services.append(service)

    return services


@router.post("/{master_id}/services", response_model=MasterServiceResponse)
def add_master_service(
    master_id: int,
    data: MasterServiceCreate,
    db: Session = Depends(get_db)
):
    """Добавить услугу мастеру"""
    master = db.query(Master).filter(Master.id == master_id).first()
    if not master:
        raise HTTPException(status_code=404, detail="Мастер не найден")

    service = db.query(Service).filter(Service.id == data.service_id).first()
    if not service:
        raise HTTPException(status_code=404, detail="Услуга не найдена")

    # Проверяем, не добавлена ли уже эта услуга
    existing = db.query(MasterService).filter(
        MasterService.master_id == master_id,
        MasterService.service_id == data.service_id
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail="Услуга уже добавлена мастеру")

    db_master_service = MasterService(
        master_id=master_id,
        service_id=data.service_id,
        custom_price=data.custom_price,
        custom_duration=data.custom_duration
    )
    db.add(db_master_service)
    db.commit()
    db.refresh(db_master_service)

    # Load service relationship
    db_master_service.service = service
    return db_master_service


@router.delete("/{master_id}/services/{service_id}")
def remove_master_service(
    master_id: int,
    service_id: int,
    db: Session = Depends(get_db)
):
    """Удалить услугу у мастера"""
    master_service = db.query(MasterService).filter(
        MasterService.master_id == master_id,
        MasterService.service_id == service_id
    ).first()
    if not master_service:
        raise HTTPException(status_code=404, detail="Связь мастер-услуга не найдена")

    db.delete(master_service)
    db.commit()
    return {"message": "Услуга удалена у мастера"}


# ============ Master Schedule (date-based) ============
@router.get("/{master_id}/schedule", response_model=List[MasterScheduleResponse])
def get_master_schedule(master_id: int, db: Session = Depends(get_db)):
    """Получить график работы мастера"""
    master = db.query(Master).filter(Master.id == master_id).first()
    if not master:
        raise HTTPException(status_code=404, detail="Мастер не найден")

    return db.query(MasterSchedule).filter(
        MasterSchedule.master_id == master_id
    ).order_by(MasterSchedule.date).all()


@router.post("/{master_id}/schedule", response_model=MasterScheduleResponse)
def set_master_schedule(
    master_id: int,
    schedule: MasterScheduleCreate,
    db: Session = Depends(get_db)
):
    """Установить график работы мастера на дату"""
    master = db.query(Master).filter(Master.id == master_id).first()
    if not master:
        raise HTTPException(status_code=404, detail="Мастер не найден")

    # Удаляем существующий график на эту дату
    db.query(MasterSchedule).filter(
        MasterSchedule.master_id == master_id,
        MasterSchedule.date == schedule.date
    ).delete()

    db_schedule = MasterSchedule(
        master_id=master_id,
        date=schedule.date,
        start_time=schedule.start_time,
        end_time=schedule.end_time,
        is_available=schedule.is_available
    )
    db.add(db_schedule)
    db.commit()
    db.refresh(db_schedule)
    return db_schedule


@router.put("/{master_id}/schedule/{schedule_id}", response_model=MasterScheduleResponse)
def update_master_schedule(
    master_id: int,
    schedule_id: int,
    schedule: MasterScheduleUpdate,
    db: Session = Depends(get_db)
):
    """Обновить график работы"""
    db_schedule = db.query(MasterSchedule).filter(
        MasterSchedule.id == schedule_id,
        MasterSchedule.master_id == master_id
    ).first()
    if not db_schedule:
        raise HTTPException(status_code=404, detail="График не найден")

    update_data = schedule.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_schedule, key, value)

    db.commit()
    db.refresh(db_schedule)
    return db_schedule


# ============ Master Portfolio ============
@router.get("/{master_id}/portfolio", response_model=List[MasterPortfolioResponse])
def get_master_portfolio(master_id: int, db: Session = Depends(get_db)):
    """Мастер жұмыстарының портфолиосы"""
    master = db.query(Master).filter(Master.id == master_id).first()
    if not master:
        raise HTTPException(status_code=404, detail="Мастер табылмады")

    return db.query(MasterPortfolio).filter(
        MasterPortfolio.master_id == master_id
    ).order_by(MasterPortfolio.created_at.desc()).all()


@router.post("/{master_id}/portfolio", response_model=MasterPortfolioResponse, status_code=201)
def add_portfolio_photo(
    master_id: int,
    photo: MasterPortfolioCreate,
    db: Session = Depends(get_db)
):
    """Мастер портфолиосына фото қосу"""
    master = db.query(Master).filter(Master.id == master_id).first()
    if not master:
        raise HTTPException(status_code=404, detail="Мастер табылмады")

    db_photo = MasterPortfolio(
        master_id=master_id,
        image_url=photo.image_url,
        description=photo.description,
    )
    db.add(db_photo)
    db.commit()
    db.refresh(db_photo)
    return db_photo


@router.delete("/{master_id}/portfolio/{photo_id}", status_code=204)
def delete_portfolio_photo(
    master_id: int,
    photo_id: int,
    db: Session = Depends(get_db)
):
    """Портфолио фотосын жою"""
    photo = db.query(MasterPortfolio).filter(
        MasterPortfolio.id == photo_id,
        MasterPortfolio.master_id == master_id
    ).first()
    if not photo:
        raise HTTPException(status_code=404, detail="Фото табылмады")

    db.delete(photo)
    db.commit()