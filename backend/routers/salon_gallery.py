"""Салон фотогалереясы"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from database import get_db
from models import Salon, SalonGallery
from schemas import SalonGalleryCreate, SalonGalleryResponse

router = APIRouter(prefix="/salons", tags=["Salon Gallery"])


@router.get("/{salon_id}/gallery", response_model=List[SalonGalleryResponse])
def get_salon_gallery(salon_id: int, db: Session = Depends(get_db)):
    """Салон фотогалереясын алу"""
    salon = db.query(Salon).filter(Salon.id == salon_id).first()
    if not salon:
        raise HTTPException(status_code=404, detail="Салон табылмады")

    return db.query(SalonGallery).filter(
        SalonGallery.salon_id == salon_id
    ).order_by(SalonGallery.sort_order).all()


@router.post("/{salon_id}/gallery", response_model=SalonGalleryResponse, status_code=201)
def add_gallery_photo(
    salon_id: int,
    photo: SalonGalleryCreate,
    db: Session = Depends(get_db)
):
    """Салонға фото қосу"""
    salon = db.query(Salon).filter(Salon.id == salon_id).first()
    if not salon:
        raise HTTPException(status_code=404, detail="Салон табылмады")

    db_photo = SalonGallery(
        salon_id=salon_id,
        image_url=photo.image_url,
        caption=photo.caption,
        sort_order=photo.sort_order,
    )
    db.add(db_photo)
    db.commit()
    db.refresh(db_photo)
    return db_photo


@router.delete("/{salon_id}/gallery/{photo_id}", status_code=204)
def delete_gallery_photo(
    salon_id: int,
    photo_id: int,
    db: Session = Depends(get_db)
):
    """Фотоны жою"""
    photo = db.query(SalonGallery).filter(
        SalonGallery.id == photo_id,
        SalonGallery.salon_id == salon_id
    ).first()
    if not photo:
        raise HTTPException(status_code=404, detail="Фото табылмады")

    db.delete(photo)
    db.commit()
