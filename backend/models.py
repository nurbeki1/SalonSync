from sqlalchemy import (
    Column, Integer, String, DateTime, Boolean, Date,
    ForeignKey, Numeric, Text, Time, Enum as SQLEnum
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum

from database import Base


class BookingStatus(enum.Enum):
    PENDING = "pending"
    CONFIRMED = "confirmed"
    PAID = "paid"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class MasterStatus(enum.Enum):
    """Статус регистрации мастера"""
    PENDING = "pending"      # Ожидает модерации
    APPROVED = "approved"    # Одобрен
    REJECTED = "rejected"    # Отклонён


class Salon(Base):
    """Салоны красоты"""
    __tablename__ = "salons"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    address = Column(String(255), nullable=True)
    phone = Column(String(20), nullable=True)
    instagram = Column(String(100), nullable=True)
    image_url = Column(String(255), nullable=True)
    rating = Column(Numeric(2, 1), default=5.0)
    working_hours = Column(String(100), nullable=True)  # "10:00-21:00"
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    salon_services = relationship("SalonService", back_populates="salon")
    masters = relationship("Master", back_populates="salon")


class Service(Base):
    """Услуги салона"""
    __tablename__ = "services"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    price = Column(Numeric(10, 2), nullable=False)
    duration = Column(Integer, nullable=False)  # длительность в минутах
    image_url = Column(String(255), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    master_services = relationship("MasterService", back_populates="service")
    bookings = relationship("Booking", back_populates="service")
    salon_services = relationship("SalonService", back_populates="service")


class SalonService(Base):
    """Связь салон-услуга (какие услуги предоставляет салон)"""
    __tablename__ = "salon_services"

    id = Column(Integer, primary_key=True, index=True)
    salon_id = Column(Integer, ForeignKey("salons.id"), nullable=False)
    service_id = Column(Integer, ForeignKey("services.id"), nullable=False)
    custom_price = Column(Numeric(10, 2), nullable=True)  # Своя цена в салоне

    # Relationships
    salon = relationship("Salon", back_populates="salon_services")
    service = relationship("Service", back_populates="salon_services")


class Master(Base):
    """Мастера салона"""
    __tablename__ = "masters"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    specialization = Column(String(100), nullable=True)
    bio = Column(Text, nullable=True)
    photo_url = Column(String(255), nullable=True)
    phone = Column(String(20), nullable=True)

    # Привязка к салону
    salon_id = Column(Integer, ForeignKey("salons.id"), nullable=True)

    # Telegram интеграция
    telegram_chat_id = Column(String(50), unique=True, nullable=True, index=True)
    telegram_username = Column(String(100), nullable=True)

    # Статус регистрации
    status = Column(SQLEnum(MasterStatus), default=MasterStatus.PENDING)
    is_active = Column(Boolean, default=False)  # Активен только после модерации

    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    salon = relationship("Salon", back_populates="masters")
    master_services = relationship("MasterService", back_populates="master")
    schedules = relationship("MasterSchedule", back_populates="master")
    bookings = relationship("Booking", back_populates="master")


class MasterService(Base):
    """Связь мастер-услуга (какие услуги делает мастер)"""
    __tablename__ = "master_services"

    id = Column(Integer, primary_key=True, index=True)
    master_id = Column(Integer, ForeignKey("masters.id"), nullable=False)
    service_id = Column(Integer, ForeignKey("services.id"), nullable=False)

    # Мастер может иметь свою цену на услугу (опционально)
    custom_price = Column(Numeric(10, 2), nullable=True)
    custom_duration = Column(Integer, nullable=True)

    # Relationships
    master = relationship("Master", back_populates="master_services")
    service = relationship("Service", back_populates="master_services")


class MasterSchedule(Base):
    """График работы мастера на конкретную дату"""
    __tablename__ = "master_schedules"

    id = Column(Integer, primary_key=True, index=True)
    master_id = Column(Integer, ForeignKey("masters.id"), nullable=False)

    # Конкретная дата (не день недели!)
    date = Column(Date, nullable=False, index=True)
    start_time = Column(Time, nullable=False)  # начало работы
    end_time = Column(Time, nullable=False)    # конец работы

    is_available = Column(Boolean, default=True)  # доступен для записи
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    master = relationship("Master", back_populates="schedules")


class Client(Base):
    """Клиенты салона"""
    __tablename__ = "clients"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    phone = Column(String(20), unique=True, nullable=False, index=True)
    email = Column(String(100), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    bookings = relationship("Booking", back_populates="client")


class Booking(Base):
    """Записи на услуги"""
    __tablename__ = "bookings"

    id = Column(Integer, primary_key=True, index=True)
    client_id = Column(Integer, ForeignKey("clients.id"), nullable=False)
    master_id = Column(Integer, ForeignKey("masters.id"), nullable=False)
    service_id = Column(Integer, ForeignKey("services.id"), nullable=False)

    # Время записи
    start_time = Column(DateTime(timezone=True), nullable=False, index=True)
    end_time = Column(DateTime(timezone=True), nullable=False, index=True)

    # Статус и оплата
    status = Column(SQLEnum(BookingStatus), default=BookingStatus.PENDING)
    total_price = Column(Numeric(10, 2), nullable=False)

    # Данные для оплаты Kaspi
    payment_link = Column(String(500), nullable=True)  # Ссылка для оплаты через Kaspi
    payment_confirmed_at = Column(DateTime(timezone=True), nullable=True)  # Дата подтверждения оплаты

    # Комментарий клиента
    notes = Column(Text, nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    client = relationship("Client", back_populates="bookings")
    master = relationship("Master", back_populates="bookings")
    service = relationship("Service", back_populates="bookings")


class SalonGallery(Base):
    """Салон фотогалереясы"""
    __tablename__ = "salon_gallery"

    id = Column(Integer, primary_key=True, index=True)
    salon_id = Column(Integer, ForeignKey("salons.id"), nullable=False)
    image_url = Column(String(500), nullable=False)
    caption = Column(String(255), nullable=True)
    sort_order = Column(Integer, default=0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    salon = relationship("Salon")


class MasterPortfolio(Base):
    """Мастер жұмыстарының портфолиосы"""
    __tablename__ = "master_portfolio"

    id = Column(Integer, primary_key=True, index=True)
    master_id = Column(Integer, ForeignKey("masters.id"), nullable=False)
    image_url = Column(String(500), nullable=False)
    description = Column(String(255), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    master = relationship("Master")


class OTPCode(Base):
    """OTP кодтар — телефон арқылы верификация"""
    __tablename__ = "otp_codes"

    id = Column(Integer, primary_key=True, index=True)
    phone = Column(String(20), nullable=False, index=True)
    code = Column(String(6), nullable=False)
    expires_at = Column(DateTime(timezone=True), nullable=False)
    is_used = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
