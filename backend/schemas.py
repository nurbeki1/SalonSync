from pydantic import BaseModel, Field
from datetime import datetime, time, date
from typing import Optional, List
from decimal import Decimal
from enum import Enum


# Enums
class BookingStatus(str, Enum):
    PENDING = "pending"
    CONFIRMED = "confirmed"
    PAID = "paid"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class DayOfWeek(int, Enum):
    MONDAY = 0
    TUESDAY = 1
    WEDNESDAY = 2
    THURSDAY = 3
    FRIDAY = 4
    SATURDAY = 5
    SUNDAY = 6


# ============ Service Schemas ============
class ServiceBase(BaseModel):
    name: str = Field(..., max_length=100)
    description: Optional[str] = None
    price: Decimal = Field(..., ge=0)
    duration: int = Field(..., ge=15, description="Длительность в минутах")
    image_url: Optional[str] = None


class ServiceCreate(ServiceBase):
    pass


class ServiceUpdate(BaseModel):
    name: Optional[str] = Field(None, max_length=100)
    description: Optional[str] = None
    price: Optional[Decimal] = Field(None, ge=0)
    duration: Optional[int] = Field(None, ge=15)
    image_url: Optional[str] = None
    is_active: Optional[bool] = None


class ServiceResponse(ServiceBase):
    id: int
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True


# ============ Master Schemas ============
class MasterBase(BaseModel):
    name: str = Field(..., max_length=100)
    specialization: Optional[str] = None
    bio: Optional[str] = None
    photo_url: Optional[str] = None
    phone: Optional[str] = None


class MasterCreate(MasterBase):
    pass


class MasterUpdate(BaseModel):
    name: Optional[str] = Field(None, max_length=100)
    specialization: Optional[str] = None
    bio: Optional[str] = None
    photo_url: Optional[str] = None
    phone: Optional[str] = None
    is_active: Optional[bool] = None


class MasterResponse(MasterBase):
    id: int
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True


class MasterWithServices(MasterResponse):
    services: List[ServiceResponse] = []


# ============ MasterService Schemas ============
class MasterServiceCreate(BaseModel):
    master_id: int
    service_id: int
    custom_price: Optional[Decimal] = None
    custom_duration: Optional[int] = None


class MasterServiceResponse(BaseModel):
    id: int
    master_id: int
    service_id: int
    custom_price: Optional[Decimal] = None
    custom_duration: Optional[int] = None
    service: ServiceResponse

    class Config:
        from_attributes = True


# ============ MasterSchedule Schemas (date-based) ============
class MasterScheduleBase(BaseModel):
    date: date
    start_time: time
    end_time: time
    is_available: bool = True


class MasterScheduleCreate(MasterScheduleBase):
    pass


class MasterScheduleUpdate(BaseModel):
    start_time: Optional[time] = None
    end_time: Optional[time] = None
    is_available: Optional[bool] = None


class MasterScheduleResponse(MasterScheduleBase):
    id: int
    master_id: int

    class Config:
        from_attributes = True


# Legacy aliases for backward compatibility
WorkScheduleCreate = MasterScheduleCreate
WorkScheduleUpdate = MasterScheduleUpdate
WorkScheduleResponse = MasterScheduleResponse


# ============ Client Schemas ============
class ClientBase(BaseModel):
    name: str = Field(..., max_length=100)
    phone: str = Field(..., max_length=20)
    email: Optional[str] = None


class ClientCreate(ClientBase):
    pass


class ClientResponse(ClientBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True


# ============ Booking Schemas ============
class BookingBase(BaseModel):
    master_id: int
    service_id: int
    start_time: datetime
    notes: Optional[str] = None


class BookingCreate(BookingBase):
    client_name: str = Field(..., max_length=100)
    client_phone: str = Field(..., max_length=20)
    client_email: Optional[str] = None


class BookingUpdate(BaseModel):
    status: Optional[BookingStatus] = None
    notes: Optional[str] = None


class BookingResponse(BaseModel):
    id: int
    client_id: int
    master_id: int
    service_id: int
    start_time: datetime
    end_time: datetime
    status: BookingStatus
    total_price: Decimal
    notes: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class BookingDetailResponse(BookingResponse):
    client: ClientResponse
    master: MasterResponse
    service: ServiceResponse


# ============ Available Slots ============
class AvailableSlotRequest(BaseModel):
    master_id: int
    service_id: int
    date: datetime  # дата для поиска слотов


class TimeSlot(BaseModel):
    start_time: datetime
    end_time: datetime


class AvailableSlotsResponse(BaseModel):
    master_id: int
    service_id: int
    date: datetime
    slots: List[TimeSlot]


# ============ Payment ============
class PaymentRequest(BaseModel):
    booking_id: int


class PaymentResponse(BaseModel):
    booking_id: int
    amount: Decimal
    kaspi_link: str
    qr_code_base64: Optional[str] = None  # QR-код в формате base64
    qr_code_url: Optional[str] = None  # Устаревшее поле (для обратной совместимости)


# ============ Salon Schemas ============
class SalonBase(BaseModel):
    name: str = Field(..., max_length=100)
    description: Optional[str] = None
    address: Optional[str] = None
    phone: Optional[str] = None
    instagram: Optional[str] = None
    rating: Decimal = Field(default=5.0, ge=0, le=5)
    working_hours: Optional[str] = None


class SalonCreate(SalonBase):
    image_url: Optional[str] = None


class SalonUpdate(BaseModel):
    name: Optional[str] = Field(None, max_length=100)
    description: Optional[str] = None
    address: Optional[str] = None
    phone: Optional[str] = None
    instagram: Optional[str] = None
    image_url: Optional[str] = None
    rating: Optional[Decimal] = Field(None, ge=0, le=5)
    working_hours: Optional[str] = None
    is_active: Optional[bool] = None


class SalonResponse(SalonBase):
    id: int
    image_url: Optional[str] = None
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True


class SalonWithMasters(SalonResponse):
    masters: List[MasterResponse] = []


# ============ SalonService Schemas ============
class SalonServiceCreate(BaseModel):
    service_id: int
    custom_price: Optional[Decimal] = None


class SalonServiceResponse(BaseModel):
    id: int
    salon_id: int
    service_id: int
    custom_price: Optional[Decimal] = None
    service: ServiceResponse

    class Config:
        from_attributes = True


# ============ Salon Gallery Schemas ============
class SalonGalleryCreate(BaseModel):
    image_url: str
    caption: Optional[str] = None
    sort_order: int = 0


class SalonGalleryResponse(BaseModel):
    id: int
    salon_id: int
    image_url: str
    caption: Optional[str] = None
    sort_order: int
    created_at: datetime

    class Config:
        from_attributes = True


# ============ Master Portfolio Schemas ============
class MasterPortfolioCreate(BaseModel):
    image_url: str
    description: Optional[str] = None


class MasterPortfolioResponse(BaseModel):
    id: int
    master_id: int
    image_url: str
    description: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True


# ============ OTP & My Bookings Schemas ============
class OTPRequest(BaseModel):
    phone: str = Field(..., max_length=20)


class OTPVerify(BaseModel):
    phone: str = Field(..., max_length=20)
    code: str = Field(..., max_length=6)


class OTPVerifyResponse(BaseModel):
    verified: bool
    token: str
    bookings: List[BookingDetailResponse] = []


# ============ Available Dates ============
class AvailableDatesResponse(BaseModel):
    master_id: int
    service_id: int
    month: str
    dates: List[str]
