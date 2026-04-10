"""
Скрипт инициализации базы данных с салонами Алматы.
Запуск: python init_salons.py
"""
from decimal import Decimal
from datetime import date, time, timedelta
from database import SessionLocal, engine, Base
from models import Salon, Service, SalonService, Master, MasterService, MasterSchedule, MasterStatus

# Создаём таблицы
Base.metadata.create_all(bind=engine)


# Данные 10 реальных салонов Алматы
SALONS_DATA = [
    {
        "name": "Main",
        "description": "Современный салон красоты с широким спектром услуг. Профессиональный подход к каждому клиенту, премиальная косметика и уютная атмосфера.",
        "address": "ул. Досмухамедова, 115, Алматы",
        "phone": "+7 (777) 168-69-88",
        "instagram": "@main.almaty",
        "image_url": "/images/salons/main.jpg",
        "rating": Decimal("4.6"),
        "working_hours": "10:00-20:00"
    },
    {
        "name": "Manon",
        "description": "Элегантный салон, специализирующийся на окрашивании волос, маникюре и шугаринге. Авторские техники колорирования.",
        "address": "пр. Аль-Фараби, 21/9, ЖК AFD Plaza, Алматы",
        "phone": "+7 (705) 203-99-91",
        "instagram": "@manon_salon",
        "image_url": "/images/salons/manon.jpg",
        "rating": Decimal("4.8"),
        "working_hours": "10:00-20:00"
    },
    {
        "name": "Mom's beauty",
        "description": "Семейный салон красоты с детской комнатой. Идеальное место для мам, которые хотят уделить время себе. Обслуживание в 4, 6 и 8 рук.",
        "address": "пр. Аль-Фараби, 140а/2, МФК VILLA, Алматы",
        "phone": "+7 (771) 222-39-38",
        "instagram": "@moms_beauty_almaty",
        "image_url": "/images/salons/moms-beauty.jpg",
        "rating": Decimal("4.6"),
        "working_hours": "10:00-21:00"
    },
    {
        "name": "Iris",
        "description": "Специализированная студия маникюра и педикюра. Более 50 оттенков гель-лаков, стерильные инструменты. Лучшая nail-студия 2025.",
        "address": "ул. Розыбакиева, 289/2, ЖК Айгерим, Алматы",
        "phone": "+7 (777) 646-57-88",
        "instagram": "@iris.beauty.kz",
        "image_url": "/images/salons/iris.jpg",
        "rating": Decimal("4.8"),
        "working_hours": "10:00-21:00"
    },
    {
        "name": "Hairroom 213",
        "description": "Бутик-парикмахерская, специализирующаяся исключительно на волосах. Стрижки, укладки, сложное окрашивание.",
        "address": "пр. Достык, 132, ЖК Пионер, 2 этаж, Алматы",
        "phone": "+7 (707) 344-33-26",
        "instagram": "@hairroom213",
        "image_url": "/images/salons/hairroom.jpg",
        "rating": Decimal("4.9"),
        "working_hours": "10:00-20:00"
    },
    {
        "name": "The Soul",
        "description": "Премиальный салон красоты полного цикла. Роскошные интерьеры, VIP-обслуживание, эксклюзивные бренды косметики.",
        "address": "пр. Аль-Фараби, 77/8, Алматы",
        "phone": "+7 (700) 323-33-23",
        "instagram": "@thesoul_beauty_almaty",
        "image_url": "/images/salons/thesoul.jpg",
        "rating": Decimal("4.8"),
        "working_hours": "10:00-22:00"
    },
    {
        "name": "Renome",
        "description": "Эстетическая косметология и люксовый уход. Инъекционные процедуры, аппаратная косметология, премиум-уход.",
        "address": "пр. Назарбаева, 152, 1 этаж, Алматы",
        "phone": "+7 (701) 099-03-30",
        "instagram": "@renome_beautysalon",
        "image_url": "/images/salons/renome.jpg",
        "rating": Decimal("4.6"),
        "working_hours": "10:00-21:00"
    },
    {
        "name": "ÉSTA",
        "description": "Экспресс-салон для занятых людей. Быстрый и качественный сервис в 4 и 6 рук без длительного ожидания.",
        "address": "ул. Розыбакиева, 247, Алматы",
        "phone": "+7 (771) 999-08-08",
        "instagram": "@esta.almaty",
        "image_url": "/images/salons/esta.jpg",
        "rating": Decimal("4.7"),
        "working_hours": "08:00-22:00"
    },
    {
        "name": "MIZU",
        "description": "Студия красоты в японском стиле. Маникюр, шугаринг, ламинирование ресниц с использованием японских технологий.",
        "address": "ул. Тимирязева, 42, Алматы",
        "phone": "+7 (747) 888-42-42",
        "instagram": "@mizu.almaty",
        "image_url": "/images/salons/mizu.jpg",
        "rating": Decimal("4.8"),
        "working_hours": "10:00-21:00"
    },
    {
        "name": "EDITION by Manon",
        "description": "Элитный салон от создателей Manon. Авторские техники, эксклюзивные процедуры, индивидуальный подход.",
        "address": "ул. Зенкова, 59, ЖК Сункар, Алматы",
        "phone": "+7 (777) 631-32-32",
        "instagram": "@edition.by.manon",
        "image_url": "/images/salons/edition.jpg",
        "rating": Decimal("4.5"),
        "working_hours": "10:00-20:00"
    }
]

# Базовые услуги
SERVICES_DATA = [
    {"name": "Женская стрижка", "description": "Стрижка с укладкой", "price": Decimal("8000"), "duration": 60},
    {"name": "Мужская стрижка", "description": "Классическая мужская стрижка", "price": Decimal("5000"), "duration": 45},
    {"name": "Окрашивание", "description": "Однотонное окрашивание", "price": Decimal("15000"), "duration": 120},
    {"name": "Сложное окрашивание", "description": "Балаяж, шатуш, омбре", "price": Decimal("35000"), "duration": 240},
    {"name": "Маникюр", "description": "Классический маникюр", "price": Decimal("5000"), "duration": 60},
    {"name": "Маникюр с покрытием", "description": "Маникюр + гель-лак", "price": Decimal("8000"), "duration": 90},
    {"name": "Педикюр", "description": "Классический педикюр", "price": Decimal("7000"), "duration": 75},
    {"name": "Наращивание ресниц", "description": "Классическое наращивание", "price": Decimal("12000"), "duration": 120},
    {"name": "Ламинирование бровей", "description": "Долговременная укладка бровей", "price": Decimal("8000"), "duration": 60},
    {"name": "Шугаринг ног", "description": "Полная депиляция ног", "price": Decimal("10000"), "duration": 60},
    {"name": "Шугаринг бикини", "description": "Глубокое бикини", "price": Decimal("8000"), "duration": 45},
    {"name": "Укладка волос", "description": "Укладка феном или щипцами", "price": Decimal("5000"), "duration": 45},
]

# 5+ мастеров для каждого салона
MASTERS_DATA = {
    "Main": [
        {"name": "Айгерим Касымова", "specialization": "Топ-колорист", "bio": "8 лет опыта, призёр международных конкурсов"},
        {"name": "Дана Мухамеджанова", "specialization": "Nail-мастер", "bio": "Специалист по nail-art и дизайну"},
        {"name": "Асель Жумабаева", "specialization": "Стилист", "bio": "Эксперт по женским стрижкам"},
        {"name": "Марат Сериков", "specialization": "Барбер", "bio": "Мужские стрижки и укладки"},
        {"name": "Гульмира Оразова", "specialization": "Lash-мастер", "bio": "Наращивание и ламинирование ресниц"},
        {"name": "Динара Алиева", "specialization": "Brow-мастер", "bio": "Архитектура и окрашивание бровей"},
    ],
    "Manon": [
        {"name": "Алия Нурланова", "specialization": "Стилист-колорист", "bio": "Эксперт по сложным окрашиваниям"},
        {"name": "Камила Ахметова", "specialization": "Мастер шугаринга", "bio": "Сертифицированный мастер депиляции"},
        {"name": "Жанар Бекетова", "specialization": "Nail-мастер", "bio": "Аппаратный маникюр и педикюр"},
        {"name": "Томирис Ерланова", "specialization": "Стилист", "bio": "Креативные стрижки и укладки"},
        {"name": "Айнур Сатыбалдиева", "specialization": "Колорист", "bio": "Блондирование и тонирование"},
    ],
    "Mom's beauty": [
        {"name": "Жанна Бекенова", "specialization": "Универсальный мастер", "bio": "Все виды услуг для всей семьи"},
        {"name": "Айым Нурмаганбетова", "specialization": "Детский парикмахер", "bio": "Стрижки для детей любого возраста"},
        {"name": "Сауле Каримова", "specialization": "Nail-мастер", "bio": "Нежный маникюр и педикюр"},
        {"name": "Балжан Турсынова", "specialization": "Стилист", "bio": "Семейные стрижки"},
        {"name": "Меруерт Абдрахманова", "specialization": "Визажист", "bio": "Дневной и вечерний макияж"},
    ],
    "Iris": [
        {"name": "Мадина Сагынбаева", "specialization": "Nail-мастер", "bio": "Призёр чемпионатов по nail-art"},
        {"name": "Асем Токтарова", "specialization": "Подолог", "bio": "Медицинский педикюр"},
        {"name": "Жазира Кенжебаева", "specialization": "Nail-дизайнер", "bio": "Художественная роспись ногтей"},
        {"name": "Назгуль Омарова", "specialization": "Nail-мастер", "bio": "Наращивание и укрепление ногтей"},
        {"name": "Айгуль Сейтжанова", "specialization": "Мастер педикюра", "bio": "SPA-педикюр и уход за стопами"},
    ],
    "Hairroom 213": [
        {"name": "Тимур Әлімжанов", "specialization": "Барбер", "bio": "Мужские стрижки и укладки"},
        {"name": "Дильназ Оспанова", "specialization": "Топ-стилист", "bio": "Авторские стрижки и укладки"},
        {"name": "Ернар Жақсылықов", "specialization": "Колорист", "bio": "Сложные техники окрашивания"},
        {"name": "Аида Муратова", "specialization": "Стилист", "bio": "Трендовые стрижки"},
        {"name": "Руслан Касенов", "specialization": "Барбер", "bio": "Классические и современные стрижки"},
    ],
    "The Soul": [
        {"name": "Карина Ибрагимова", "specialization": "Арт-директор", "bio": "VIP-мастер салона, 15 лет опыта"},
        {"name": "Аружан Есенова", "specialization": "Lash-мастер", "bio": "Объёмное наращивание ресниц"},
        {"name": "Динара Жумабекова", "specialization": "Косметолог", "bio": "Инъекционная косметология"},
        {"name": "Алтынай Серикова", "specialization": "Топ-стилист", "bio": "Премиум стрижки и укладки"},
        {"name": "Жібек Қасымова", "specialization": "Колорист", "bio": "Люксовое окрашивание"},
        {"name": "Нұрай Бақытжанова", "specialization": "Nail-мастер", "bio": "Премиум маникюр"},
    ],
    "Renome": [
        {"name": "Гульнара Шарипова", "specialization": "Врач-косметолог", "bio": "Эстетическая медицина"},
        {"name": "Сания Муратова", "specialization": "Мастер по уходу", "bio": "Премиум-процедуры для лица"},
        {"name": "Айнаш Жолдасова", "specialization": "Lash-мастер", "bio": "Ламинирование и ботокс ресниц"},
        {"name": "Мөлдір Нұрланқызы", "specialization": "Brow-мастер", "bio": "Перманентный макияж бровей"},
        {"name": "Гаухар Темірбекова", "specialization": "Косметолог", "bio": "Аппаратная косметология"},
    ],
    "ÉSTA": [
        {"name": "Лаура Қасымова", "specialization": "Экспресс-мастер", "bio": "Быстрый маникюр и укладки"},
        {"name": "Әсел Мұратбекова", "specialization": "Стилист", "bio": "Экспресс-стрижки"},
        {"name": "Жансая Ержанова", "specialization": "Nail-мастер", "bio": "Быстрый маникюр за 30 минут"},
        {"name": "Нұргүл Сағындықова", "specialization": "Мастер укладок", "bio": "Экспресс-укладки"},
        {"name": "Бақытгүл Оразбаева", "specialization": "Brow-мастер", "bio": "Быстрая коррекция бровей"},
    ],
    "MIZU": [
        {"name": "Юки Танака", "specialization": "Lash-мастер", "bio": "Японская техника наращивания"},
        {"name": "Айжан Серикова", "specialization": "Мастер шугаринга", "bio": "Японские методики депиляции"},
        {"name": "Сакура Ли", "specialization": "Nail-мастер", "bio": "Японский маникюр P-shine"},
        {"name": "Малика Тұрсынбаева", "specialization": "Brow-мастер", "bio": "Японская техника бровей"},
        {"name": "Дәмелі Қайратқызы", "specialization": "Lash-мастер", "bio": "Мега-объём ресниц"},
    ],
    "EDITION by Manon": [
        {"name": "Арман Сулейменов", "specialization": "Арт-директор", "bio": "Креативный директор салона"},
        {"name": "Зарина Қайратқызы", "specialization": "Топ-колорист", "bio": "Авторские техники окрашивания"},
        {"name": "Айдана Бекболатова", "specialization": "Стилист", "bio": "Трендовые стрижки 2024"},
        {"name": "Нұрсұлтан Әбілқасымов", "specialization": "Барбер", "bio": "Премиум мужские стрижки"},
        {"name": "Інжу Мұхамедиярова", "specialization": "Nail-мастер", "bio": "Эксклюзивный дизайн ногтей"},
        {"name": "Аяулым Жанболатқызы", "specialization": "Колорист", "bio": "Сложное окрашивание"},
    ],
}

# Какие услуги в каких салонах
SALON_SERVICE_MAPPING = {
    "Main": ["Женская стрижка", "Мужская стрижка", "Окрашивание", "Сложное окрашивание", "Маникюр", "Маникюр с покрытием", "Наращивание ресниц", "Ламинирование бровей", "Укладка волос"],
    "Manon": ["Женская стрижка", "Окрашивание", "Сложное окрашивание", "Маникюр", "Маникюр с покрытием", "Шугаринг ног", "Шугаринг бикини", "Укладка волос"],
    "Mom's beauty": ["Женская стрижка", "Мужская стрижка", "Окрашивание", "Маникюр", "Маникюр с покрытием", "Педикюр", "Укладка волос"],
    "Iris": ["Маникюр", "Маникюр с покрытием", "Педикюр"],
    "Hairroom 213": ["Женская стрижка", "Мужская стрижка", "Окрашивание", "Сложное окрашивание", "Укладка волос"],
    "The Soul": ["Женская стрижка", "Мужская стрижка", "Окрашивание", "Сложное окрашивание", "Маникюр", "Маникюр с покрытием", "Педикюр", "Наращивание ресниц", "Ламинирование бровей", "Шугаринг ног", "Шугаринг бикини", "Укладка волос"],
    "Renome": ["Наращивание ресниц", "Ламинирование бровей", "Маникюр", "Маникюр с покрытием"],
    "ÉSTA": ["Женская стрижка", "Мужская стрижка", "Маникюр", "Маникюр с покрытием", "Укладка волос", "Ламинирование бровей"],
    "MIZU": ["Маникюр", "Маникюр с покрытием", "Наращивание ресниц", "Ламинирование бровей", "Шугаринг ног", "Шугаринг бикини"],
    "EDITION by Manon": ["Женская стрижка", "Мужская стрижка", "Окрашивание", "Сложное окрашивание", "Маникюр", "Маникюр с покрытием", "Укладка волос"],
}


def init_database():
    db = SessionLocal()

    try:
        # Проверяем, есть ли уже салоны
        existing_salons = db.query(Salon).count()
        if existing_salons > 0:
            print(f"База данных уже содержит {existing_salons} салонов. Пропускаем инициализацию.")
            return

        # 1. Создаём услуги
        services_map = {}
        for service_data in SERVICES_DATA:
            existing = db.query(Service).filter(Service.name == service_data["name"]).first()
            if existing:
                services_map[service_data["name"]] = existing
            else:
                service = Service(
                    name=service_data["name"],
                    description=service_data["description"],
                    price=service_data["price"],
                    duration=service_data["duration"],
                    is_active=True
                )
                db.add(service)
                db.flush()
                services_map[service_data["name"]] = service
                print(f"Создана услуга: {service_data['name']}")

        # 2. Создаём салоны
        salons_map = {}
        for salon_data in SALONS_DATA:
            salon = Salon(
                name=salon_data["name"],
                description=salon_data["description"],
                address=salon_data["address"],
                phone=salon_data["phone"],
                instagram=salon_data["instagram"],
                image_url=salon_data["image_url"],
                rating=salon_data["rating"],
                working_hours=salon_data["working_hours"],
                is_active=True
            )
            db.add(salon)
            db.flush()
            salons_map[salon_data["name"]] = salon
            print(f"Создан салон: {salon_data['name']}")

        # 3. Связываем салоны с услугами
        for salon_name, service_names in SALON_SERVICE_MAPPING.items():
            salon = salons_map.get(salon_name)
            if salon:
                for service_name in service_names:
                    service = services_map.get(service_name)
                    if service:
                        salon_service = SalonService(
                            salon_id=salon.id,
                            service_id=service.id
                        )
                        db.add(salon_service)
        print("Услуги привязаны к салонам")

        # 4. Создаём мастеров для каждого салона
        all_masters = []
        for salon_name, masters in MASTERS_DATA.items():
            salon = salons_map.get(salon_name)
            if salon:
                salon_service_names = SALON_SERVICE_MAPPING.get(salon_name, [])
                for master_data in masters:
                    master = Master(
                        name=master_data["name"],
                        specialization=master_data["specialization"],
                        bio=master_data["bio"],
                        salon_id=salon.id,
                        is_active=True,
                        status=MasterStatus.APPROVED
                    )
                    db.add(master)
                    db.flush()
                    all_masters.append(master)

                    # Привязываем мастеров к услугам салона (все услуги)
                    for service_name in salon_service_names:
                        service = services_map.get(service_name)
                        if service:
                            ms = MasterService(
                                master_id=master.id,
                                service_id=service.id
                            )
                            db.add(ms)

                    print(f"Создан мастер: {master_data['name']} ({salon_name})")

        # 5. Создаём расписание для всех мастеров на 14 дней вперёд
        print("\nСоздание расписания для мастеров...")
        today = date.today()
        for master in all_masters:
            for day_offset in range(1, 15):  # 14 дней вперёд
                work_date = today + timedelta(days=day_offset)

                # Пропускаем воскресенье для некоторых мастеров
                if work_date.weekday() == 6 and master.id % 3 == 0:
                    continue

                schedule = MasterSchedule(
                    master_id=master.id,
                    date=work_date,
                    start_time=time(10, 0),  # 10:00
                    end_time=time(20, 0),    # 20:00
                    is_available=True
                )
                db.add(schedule)

        print(f"Создано расписание на 14 дней для {len(all_masters)} мастеров")

        db.commit()

        total_masters = sum(len(m) for m in MASTERS_DATA.values())
        print("\n" + "="*50)
        print("База данных успешно инициализирована!")
        print(f"Создано салонов: {len(SALONS_DATA)}")
        print(f"Создано услуг: {len(SERVICES_DATA)}")
        print(f"Создано мастеров: {total_masters}")
        print(f"Создано расписаний: ~{total_masters * 14}")
        print("="*50)

    except Exception as e:
        db.rollback()
        print(f"Ошибка при инициализации: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    init_database()
