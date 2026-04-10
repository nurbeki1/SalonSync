"""
Скрипт для заполнения БД тестовыми данными
Запуск: python seed.py
"""
from datetime import time
from decimal import Decimal

from database import SessionLocal, engine, Base
from models import Service, Master, MasterService, WorkSchedule, DayOfWeek

# Создаём таблицы
Base.metadata.create_all(bind=engine)

db = SessionLocal()

def seed_services():
    """Добавляем услуги"""
    services_data = [
        {
            "name": "Женская стрижка",
            "description": "Профессиональная женская стрижка любой сложности",
            "price": Decimal("5000"),
            "duration": 60,
            "image_url": "/images/services/haircut-women.jpg"
        },
        {
            "name": "Мужская стрижка",
            "description": "Классическая мужская стрижка",
            "price": Decimal("3000"),
            "duration": 45,
            "image_url": "/images/services/haircut-men.jpg"
        },
        {
            "name": "Окрашивание волос",
            "description": "Профессиональное окрашивание с использованием премиум-красок",
            "price": Decimal("15000"),
            "duration": 120,
            "image_url": "/images/services/coloring.jpg"
        },
        {
            "name": "Маникюр",
            "description": "Классический маникюр с покрытием",
            "price": Decimal("4000"),
            "duration": 60,
            "image_url": "/images/services/manicure.jpg"
        },
        {
            "name": "Педикюр",
            "description": "Классический педикюр с покрытием",
            "price": Decimal("5000"),
            "duration": 90,
            "image_url": "/images/services/pedicure.jpg"
        },
        {
            "name": "Укладка волос",
            "description": "Профессиональная укладка для любого события",
            "price": Decimal("4000"),
            "duration": 45,
            "image_url": "/images/services/styling.jpg"
        },
        {
            "name": "Макияж",
            "description": "Профессиональный макияж: дневной, вечерний, свадебный",
            "price": Decimal("8000"),
            "duration": 60,
            "image_url": "/images/services/makeup.jpg"
        },
        {
            "name": "Брови и ресницы",
            "description": "Коррекция и окрашивание бровей, ламинирование ресниц",
            "price": Decimal("3500"),
            "duration": 45,
            "image_url": "/images/services/brows.jpg"
        }
    ]

    for data in services_data:
        existing = db.query(Service).filter(Service.name == data["name"]).first()
        if not existing:
            service = Service(**data)
            db.add(service)

    db.commit()
    print(f"✓ Добавлено услуг: {len(services_data)}")


def seed_masters():
    """Добавляем мастеров"""
    masters_data = [
        {
            "name": "Анна Иванова",
            "specialization": "Стилист-колорист",
            "bio": "10 лет опыта. Специализируется на сложных окрашиваниях и стрижках.",
            "photo_url": "/images/masters/anna.jpg",
            "phone": "+7 777 111 1111"
        },
        {
            "name": "Мария Петрова",
            "specialization": "Мастер маникюра",
            "bio": "Сертифицированный мастер nail-арта. Работает с гель-лаками премиум класса.",
            "photo_url": "/images/masters/maria.jpg",
            "phone": "+7 777 222 2222"
        },
        {
            "name": "Елена Сидорова",
            "specialization": "Визажист",
            "bio": "Профессиональный визажист и бровист. Работала на показах мод.",
            "photo_url": "/images/masters/elena.jpg",
            "phone": "+7 777 333 3333"
        },
        {
            "name": "Алексей Козлов",
            "specialization": "Барбер",
            "bio": "Мастер мужских стрижек и бороды. 5 лет опыта.",
            "photo_url": "/images/masters/alexey.jpg",
            "phone": "+7 777 444 4444"
        }
    ]

    for data in masters_data:
        existing = db.query(Master).filter(Master.name == data["name"]).first()
        if not existing:
            master = Master(**data)
            db.add(master)

    db.commit()
    print(f"✓ Добавлено мастеров: {len(masters_data)}")


def seed_master_services():
    """Связываем мастеров с услугами"""
    # Анна - стрижки и окрашивание
    anna = db.query(Master).filter(Master.name == "Анна Иванова").first()
    haircut_w = db.query(Service).filter(Service.name == "Женская стрижка").first()
    coloring = db.query(Service).filter(Service.name == "Окрашивание волос").first()
    styling = db.query(Service).filter(Service.name == "Укладка волос").first()

    # Мария - маникюр и педикюр
    maria = db.query(Master).filter(Master.name == "Мария Петрова").first()
    manicure = db.query(Service).filter(Service.name == "Маникюр").first()
    pedicure = db.query(Service).filter(Service.name == "Педикюр").first()

    # Елена - макияж и брови
    elena = db.query(Master).filter(Master.name == "Елена Сидорова").first()
    makeup = db.query(Service).filter(Service.name == "Макияж").first()
    brows = db.query(Service).filter(Service.name == "Брови и ресницы").first()

    # Алексей - мужские стрижки
    alexey = db.query(Master).filter(Master.name == "Алексей Козлов").first()
    haircut_m = db.query(Service).filter(Service.name == "Мужская стрижка").first()

    relations = [
        (anna, haircut_w), (anna, coloring), (anna, styling),
        (maria, manicure), (maria, pedicure),
        (elena, makeup), (elena, brows),
        (alexey, haircut_m)
    ]

    count = 0
    for master, service in relations:
        if master and service:
            existing = db.query(MasterService).filter(
                MasterService.master_id == master.id,
                MasterService.service_id == service.id
            ).first()
            if not existing:
                ms = MasterService(master_id=master.id, service_id=service.id)
                db.add(ms)
                count += 1

    db.commit()
    print(f"✓ Добавлено связей мастер-услуга: {count}")


def seed_schedules():
    """Добавляем расписание мастеров"""
    masters = db.query(Master).all()

    # Рабочие дни: Пн-Пт 10:00-20:00, Сб 10:00-18:00
    workdays = [
        (DayOfWeek.MONDAY, time(10, 0), time(20, 0)),
        (DayOfWeek.TUESDAY, time(10, 0), time(20, 0)),
        (DayOfWeek.WEDNESDAY, time(10, 0), time(20, 0)),
        (DayOfWeek.THURSDAY, time(10, 0), time(20, 0)),
        (DayOfWeek.FRIDAY, time(10, 0), time(20, 0)),
        (DayOfWeek.SATURDAY, time(10, 0), time(18, 0)),
    ]

    count = 0
    for master in masters:
        for day, start, end in workdays:
            existing = db.query(WorkSchedule).filter(
                WorkSchedule.master_id == master.id,
                WorkSchedule.day_of_week == day
            ).first()
            if not existing:
                schedule = WorkSchedule(
                    master_id=master.id,
                    day_of_week=day,
                    start_time=start,
                    end_time=end,
                    is_working=True
                )
                db.add(schedule)
                count += 1

    db.commit()
    print(f"✓ Добавлено записей расписания: {count}")


if __name__ == "__main__":
    print("🌱 Заполнение базы данных...")
    print("-" * 40)

    seed_services()
    seed_masters()
    seed_master_services()
    seed_schedules()

    print("-" * 40)
    print("✅ База данных заполнена!")

    db.close()