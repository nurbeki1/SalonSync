from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from database import get_db
from models import Service
from schemas import ServiceCreate, ServiceUpdate, ServiceResponse

router = APIRouter(prefix="/services", tags=["Services"])


@router.get("/", response_model=List[ServiceResponse])
def get_services(
    skip: int = 0,
    limit: int = 100,
    active_only: bool = True,
    db: Session = Depends(get_db)
):
    """Получить список всех услуг"""
    query = db.query(Service)
    if active_only:
        query = query.filter(Service.is_active == True)
    return query.offset(skip).limit(limit).all()


@router.get("/{service_id}", response_model=ServiceResponse)
def get_service(service_id: int, db: Session = Depends(get_db)):
    """Получить услугу по ID"""
    service = db.query(Service).filter(Service.id == service_id).first()
    if not service:
        raise HTTPException(status_code=404, detail="Услуга не найдена")
    return service


@router.post("/", response_model=ServiceResponse)
def create_service(service: ServiceCreate, db: Session = Depends(get_db)):
    """Создать новую услугу"""
    db_service = Service(**service.model_dump())
    db.add(db_service)
    db.commit()
    db.refresh(db_service)
    return db_service


@router.put("/{service_id}", response_model=ServiceResponse)
def update_service(
    service_id: int,
    service: ServiceUpdate,
    db: Session = Depends(get_db)
):
    """Обновить услугу"""
    db_service = db.query(Service).filter(Service.id == service_id).first()
    if not db_service:
        raise HTTPException(status_code=404, detail="Услуга не найдена")

    update_data = service.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_service, key, value)

    db.commit()
    db.refresh(db_service)
    return db_service


@router.delete("/{service_id}")
def delete_service(service_id: int, db: Session = Depends(get_db)):
    """Удалить услугу (soft delete)"""
    db_service = db.query(Service).filter(Service.id == service_id).first()
    if not db_service:
        raise HTTPException(status_code=404, detail="Услуга не найдена")

    db_service.is_active = False
    db.commit()
    return {"message": "Услуга деактивирована"}