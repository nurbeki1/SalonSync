from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from database import get_db
from models import Salon, SalonService, Service, Master
from schemas import (
    SalonCreate, SalonUpdate, SalonResponse, SalonWithMasters,
    SalonServiceCreate, SalonServiceResponse, ServiceResponse, MasterResponse
)

router = APIRouter(
    prefix="/salons",
    tags=["salons"],
)


@router.get("/", response_model=List[SalonResponse])
def get_salons(
    skip: int = 0,
    limit: int = 100,
    active_only: bool = True,
    db: Session = Depends(get_db)
):
    """Получить список всех салонов"""
    query = db.query(Salon)
    if active_only:
        query = query.filter(Salon.is_active == True)
    salons = query.offset(skip).limit(limit).all()
    return salons


@router.get("/{salon_id}", response_model=SalonResponse)
def get_salon(salon_id: int, db: Session = Depends(get_db)):
    """Получить информацию о конкретном салоне"""
    salon = db.query(Salon).filter(Salon.id == salon_id).first()
    if not salon:
        raise HTTPException(status_code=404, detail="Salon not found")
    return salon


@router.get("/{salon_id}/services", response_model=List[ServiceResponse])
def get_salon_services(salon_id: int, db: Session = Depends(get_db)):
    """Получить услуги салона"""
    salon = db.query(Salon).filter(Salon.id == salon_id).first()
    if not salon:
        raise HTTPException(status_code=404, detail="Salon not found")

    # Получаем услуги через связь salon_services
    salon_services = db.query(SalonService).filter(SalonService.salon_id == salon_id).all()
    services = []
    for ss in salon_services:
        service = db.query(Service).filter(Service.id == ss.service_id).first()
        if service and service.is_active:
            # Если есть кастомная цена салона, используем её
            if ss.custom_price:
                service.price = ss.custom_price
            services.append(service)

    return services


@router.get("/{salon_id}/masters", response_model=List[MasterResponse])
def get_salon_masters(salon_id: int, db: Session = Depends(get_db)):
    """Получить мастеров салона"""
    salon = db.query(Salon).filter(Salon.id == salon_id).first()
    if not salon:
        raise HTTPException(status_code=404, detail="Salon not found")

    masters = db.query(Master).filter(
        Master.salon_id == salon_id,
        Master.is_active == True
    ).all()

    return masters


@router.post("/", response_model=SalonResponse, status_code=status.HTTP_201_CREATED)
def create_salon(salon_data: SalonCreate, db: Session = Depends(get_db)):
    """Создать новый салон (admin only)"""
    salon = Salon(
        name=salon_data.name,
        description=salon_data.description,
        address=salon_data.address,
        phone=salon_data.phone,
        instagram=salon_data.instagram,
        image_url=salon_data.image_url,
        rating=salon_data.rating,
        working_hours=salon_data.working_hours,
        is_active=True
    )
    db.add(salon)
    db.commit()
    db.refresh(salon)
    return salon


@router.put("/{salon_id}", response_model=SalonResponse)
def update_salon(salon_id: int, salon_data: SalonUpdate, db: Session = Depends(get_db)):
    """Обновить информацию о салоне"""
    salon = db.query(Salon).filter(Salon.id == salon_id).first()
    if not salon:
        raise HTTPException(status_code=404, detail="Salon not found")

    update_data = salon_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(salon, field, value)

    db.commit()
    db.refresh(salon)
    return salon


@router.delete("/{salon_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_salon(salon_id: int, db: Session = Depends(get_db)):
    """Удалить салон (мягкое удаление - деактивация)"""
    salon = db.query(Salon).filter(Salon.id == salon_id).first()
    if not salon:
        raise HTTPException(status_code=404, detail="Salon not found")

    salon.is_active = False
    db.commit()
    return None


@router.post("/{salon_id}/services", response_model=SalonServiceResponse, status_code=status.HTTP_201_CREATED)
def add_service_to_salon(
    salon_id: int,
    service_data: SalonServiceCreate,
    db: Session = Depends(get_db)
):
    """Добавить услугу в салон"""
    salon = db.query(Salon).filter(Salon.id == salon_id).first()
    if not salon:
        raise HTTPException(status_code=404, detail="Salon not found")

    service = db.query(Service).filter(Service.id == service_data.service_id).first()
    if not service:
        raise HTTPException(status_code=404, detail="Service not found")

    # Проверяем, не добавлена ли услуга уже
    existing = db.query(SalonService).filter(
        SalonService.salon_id == salon_id,
        SalonService.service_id == service_data.service_id
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail="Service already added to this salon")

    salon_service = SalonService(
        salon_id=salon_id,
        service_id=service_data.service_id,
        custom_price=service_data.custom_price
    )
    db.add(salon_service)
    db.commit()
    db.refresh(salon_service)

    # Загружаем связанный сервис для ответа
    salon_service.service = service
    return salon_service


@router.delete("/{salon_id}/services/{service_id}", status_code=status.HTTP_204_NO_CONTENT)
def remove_service_from_salon(salon_id: int, service_id: int, db: Session = Depends(get_db)):
    """Удалить услугу из салона"""
    salon_service = db.query(SalonService).filter(
        SalonService.salon_id == salon_id,
        SalonService.service_id == service_id
    ).first()
    if not salon_service:
        raise HTTPException(status_code=404, detail="Service not found in this salon")

    db.delete(salon_service)
    db.commit()
    return None
