# SalonSync — Полный технический анализ проекта

> **Платформа-агрегатор салонов красоты с онлайн-записью, оплатой через Kaspi и уведомлениями через Telegram + WhatsApp**

---

## 1. СТРУКТУРА ПРОЕКТА

```
/
├── backend/                          # FastAPI + Telegram Bot
│   ├── main.py                       # FastAPI приложение
│   ├── models.py                     # SQLAlchemy модели БД
│   ├── schemas.py                    # Pydantic валидация
│   ├── config.py                     # Конфигурация окружения
│   ├── database.py                   # Подключение к БД
│   ├── requirements.txt              # Python зависимости
│   ├── routers/
│   │   ├── bookings.py               # Записи на услуги
│   │   ├── salons.py                 # Салоны
│   │   ├── masters.py                # Мастера
│   │   ├── services.py               # Услуги
│   │   ├── salon_gallery.py          # Галерея фото салонов
│   │   └── my_bookings.py            # Мои записи (OTP)
│   ├── services/
│   │   ├── kaspi.py                  # QR-код и ссылка для оплаты Kaspi
│   │   ├── whatsapp.py               # WhatsApp уведомления (WAHA API)
│   │   └── otp.py                    # OTP верификация (JWT)
│   ├── bot/                          # Telegram Bot
│   │   ├── main.py                   # Точка входа бота
│   │   ├── admin_bot.py              # Админ-бот
│   │   ├── states.py                 # FSM состояния (aiogram 3)
│   │   ├── handlers/
│   │   │   ├── registration.py       # Регистрация мастеров (5 шагов)
│   │   │   ├── bookings.py           # Просмотр записей мастером
│   │   │   ├── start.py              # /start команда
│   │   │   ├── admin.py              # Команды администратора
│   │   │   ├── schedule.py           # График работы
│   │   │   └── export.py             # Экспорт записей в Excel
│   │   ├── keyboards/
│   │   │   ├── main_menu.py
│   │   │   ├── schedule_kb.py
│   │   │   └── services_kb.py
│   │   └── services/
│   │       └── notifications.py      # Telegram уведомления мастерам
│   ├── init_salons.py                # Инициализация тестовых данных
│   └── seed.py                       # Сидирование БД
│
├── frontend/                         # Next.js 16 + React 19
│   ├── package.json
│   ├── src/
│   │   ├── app/
│   │   │   ├── page.tsx              # Главная страница
│   │   │   ├── layout.tsx            # Layout
│   │   │   └── globals.css           # Tailwind CSS
│   │   ├── components/
│   │   │   ├── BookingDrawer.tsx     # Многошаговая форма бронирования
│   │   │   ├── BookingModal.tsx      # Модальное окно бронирования
│   │   │   ├── MyBookingsModal.tsx   # Мои записи (по OTP)
│   │   │   ├── SalonCard.tsx         # Карточка салона
│   │   │   ├── SalonDetail.tsx       # Детальная страница салона
│   │   │   ├── MasterCard.tsx        # Карточка мастера
│   │   │   ├── MasterPortfolioModal.tsx  # Портфолио мастера
│   │   │   ├── CalendarPicker.tsx    # Выбор даты
│   │   │   ├── Header.tsx            # Шапка сайта
│   │   │   ├── BrandLogo.tsx         # Логотип
│   │   │   └── ui/                   # shadcn UI компоненты
│   │   └── lib/
│   │       ├── api.ts                # API клиент (fetch)
│   │       ├── i18n.ts               # Локализация (RU/KK)
│   │       ├── phone.ts              # Форматирование номеров
│   │       └── utils.ts              # Утилиты
│   └── public/
│       └── images/salons/            # Фотографии салонов
│
├── Dockerfile                        # Python 3.11 + Uvicorn
├── railway.json                      # Railway CI/CD конфиг
└── .gitignore
```

---

## 2. ТЕХНОЛОГИЧЕСКИЙ СТЕК

### Backend
| Технология | Версия | Назначение |
|-----------|--------|-----------|
| Python | 3.11 | Основной язык |
| FastAPI | ≥0.100.0 | REST API фреймворк |
| SQLAlchemy | ≥2.0.0 | ORM для работы с БД |
| Pydantic | ≥2.0.0 | Валидация данных |
| Uvicorn | ≥0.22.0 | ASGI сервер |
| aiogram | ≥3.0.0 | Telegram Bot |
| httpx | ≥0.25.0 | Async HTTP клиент (WhatsApp) |
| PyJWT | ≥2.8.0 | JWT токены (OTP) |
| qrcode[pil] | ≥7.4.0 | Генерация QR-кодов |
| openpyxl | ≥3.1.0 | Экспорт в Excel |
| psycopg2-binary | ≥2.9.0 | PostgreSQL драйвер |

### Frontend
| Технология | Версия | Назначение |
|-----------|--------|-----------|
| Next.js | 16.2.2 | React фреймворк (App Router) |
| React | 19.2.4 | UI библиотека |
| Tailwind CSS | 4 | Стилизация |
| shadcn/ui | — | Компоненты UI |
| Framer Motion | — | Анимации |
| react-hook-form | — | Формы |
| zod | — | Валидация схем |
| lucide-react | — | Иконки |

### Инфраструктура
| Сервис | Назначение |
|-------|-----------|
| Railway | Хостинг Backend (Docker) |
| Vercel | Хостинг Frontend (Next.js) |
| SQLite / PostgreSQL | База данных |
| WAHA (WhatsApp HTTP API) | WhatsApp уведомления |
| Telegram Bot API | Уведомления мастерам |
| Kaspi | Приём платежей (QR-коды) |

---

## 3. СХЕМА БАЗЫ ДАННЫХ

### Основные таблицы

```
Salon (salons)
├── id, name, description, address, phone, instagram
├── image_url, rating (Numeric 2,1), working_hours
├── is_active (bool), created_at
└── → 1:N Masters, SalonServices, SalonGallery

Service (services)
├── id, name, description, price, duration (мин)
├── image_url, is_active, created_at
└── → M:N Masters (через MasterService)
    M:N Salons (через SalonService)

Master (masters)
├── id, name, specialization, bio, photo_url, phone
├── salon_id (FK), telegram_chat_id (unique), telegram_username
├── status: Enum(PENDING | APPROVED | REJECTED)
├── is_active, created_at
└── → 1:N Bookings, MasterServices, MasterSchedules, MasterPortfolio

MasterService (master_services) — M:M Master ↔ Service
├── id, master_id, service_id
└── custom_price, custom_duration (переопределение цены/длительности)

MasterSchedule (master_schedules) — График работы по датам
├── id, master_id, date (Date), start_time, end_time
└── is_available

Client (clients)
├── id, name, phone (unique), email, created_at
└── → 1:N Bookings

Booking (bookings) — Запись на услугу
├── id, client_id, master_id, service_id
├── start_time, end_time (DateTime timezone-aware)
├── status: Enum(PENDING | CONFIRMED | PAID | COMPLETED | CANCELLED)
├── total_price, payment_link, payment_confirmed_at
├── notes, created_at, updated_at
└── [Центральная таблица всей системы]

OTPCode (otp_codes)
├── id, phone, code (6 цифр), expires_at (5 мин)
└── is_used, created_at

SalonGallery (salon_gallery)
├── id, salon_id, image_url, caption, sort_order, created_at

MasterPortfolio (master_portfolio)
├── id, master_id, image_url, description, created_at

SalonService (salon_services) — M:M Salon ↔ Service
├── id, salon_id, service_id, custom_price
```

---

## 4. API ЭНДПОИНТЫ (FastAPI)

### Салоны
```
GET    /salons                        # Все салоны
GET    /salons/{id}                   # Информация о салоне
GET    /salons/{id}/services          # Услуги салона
GET    /salons/{id}/masters           # Мастера салона
GET    /salons/{id}/gallery           # Фотогалерея
POST   /salons/                       # Создать салон
POST   /salons/{id}/services          # Добавить услугу
POST   /salons/{id}/gallery           # Добавить фото
PUT    /salons/{id}                   # Обновить салон
DELETE /salons/{id}                   # Деактивировать
```

### Мастера
```
GET    /masters                       # Все мастера
GET    /masters/{id}                  # Информация о мастере
GET    /masters/{id}/services         # Услуги мастера
GET    /masters/{id}/schedule         # График работы
GET    /masters/{id}/portfolio        # Портфолио фото
POST   /masters/                      # Создать мастера
POST   /masters/{id}/services         # Добавить услугу
POST   /masters/{id}/schedule         # Добавить дату работы
POST   /masters/{id}/portfolio        # Добавить фото
PUT    /masters/{id}                  # Обновить
DELETE /masters/{id}                  # Деактивировать
```

### Бронирование
```
GET  /bookings/available-dates
     ?master_id=X&service_id=Y&month=YYYY-MM
     → { dates: ["2026-04-25", ...] }

GET  /bookings/available-slots
     ?master_id=X&service_id=Y&date=YYYY-MM-DD
     → { slots: [{ start_time, end_time }, ...] }

POST /bookings/
     Body: { master_id, service_id, start_time,
             client_name, client_phone, notes? }
     → Создаёт запись + уведомления

POST /bookings/{id}/pay
     → { booking_id, amount, kaspi_link, qr_code_base64 }

POST /bookings/{id}/confirm-payment
     → Переводит статус PENDING → PAID + уведомления

PUT  /bookings/{id}           # Обновить статус
DELETE /bookings/{id}         # Отменить запись
```

### Мои записи (OTP авторизация)
```
POST /my-bookings/send-code
     Body: { phone }
     → Отправляет OTP на WhatsApp (rate limit: 1/мин)

POST /my-bookings/verify
     Body: { phone, code }
     → { verified, token (JWT 15мин), bookings[] }

GET  /my-bookings/?token=JWT
     → Список записей клиента

DELETE /my-bookings/{id}?token=JWT
     → Отменить свою запись
```

---

## 5. TELEGRAM BOT

### Команды и возможности

```
/start  →  Главное меню
         ├── 💇 Регистрация мастера (5 шагов)
         ├── 📅 Мои записи (сегодня / неделя / месяц)
         └── 📊 Экспорт в Excel

/approve_master {id}  →  Одобрить мастера (только для ADMIN_CHAT_ID)
```

### Поток регистрации мастера (FSM)

```
STEP 1: Введите имя
STEP 2: Отправьте фото профиля
STEP 3: Выберите специализацию
        (Парикмахер / Маникюр / Визажист / Барбер / Косметолог)
STEP 4: Выберите услуги (мультивыбор)
STEP 5: Подтверждение → сохранение в БД (status=PENDING)
        → уведомление администратору

Администратор: /approve_master {id}
        → status=APPROVED, is_active=True
        → мастер получает уведомление "Вы одобрены!"
```

### Уведомления мастеру

```
🔔 Новая запись!
👤 Клиент: Имя
📱 Телефон: +7 XXX XXX XXXX
💇 Услуга: Стрижка
📅 Дата: 25.04.2026
🕐 Время: 14:30
💰 Сумма: 15 000 ₸
Статус: ⏳ Ожидает оплаты

✅ Запись оплачена!
👤 Клиент: Имя
💇 Услуга: Стрижка
📅 25.04.2026 в 14:30
💰 15 000 ₸
```

---

## 6. WhatsApp ИНТЕГРАЦИЯ (WAHA)

**WAHA (WhatsApp HTTP API)** — self-hosted сервис для отправки WhatsApp сообщений через обычный номер телефона (не Business API).

### Конфигурация

```bash
WHATSAPP_API_URL=https://waha.example.com   # URL WAHA сервера
WHATSAPP_SESSION=default                     # Имя сессии
WHATSAPP_API_KEY=your_api_key               # API ключ (X-Api-Key заголовок)
```

### Формат отправки

```http
POST {WHATSAPP_API_URL}/api/sendText
Headers:
  X-Api-Key: {WHATSAPP_API_KEY}
  Content-Type: application/json
Body:
{
  "chatId": "77081234567@c.us",
  "text": "Сообщение",
  "session": "default"
}
```

### Типы уведомлений клиенту

| Событие | Уведомление |
|--------|------------|
| Запись создана | ✅ Жазылуыңыз қабылданды (салон, мастер, дата, сумма) |
| Оплата подтверждена | ✅ Оплата расталды + "Сізді күтеміз!" |
| Запись отменена | ❌ Жазылу бас тартылды |
| Напоминание | ⏰ 2 сағат қалды (за 2 часа) |
| OTP код | 🔐 Ваш код: XXXXXX (5 мин) |

**Язык уведомлений:** Казахский
**Fallback:** если WAHA недоступен — логирование в консоль, запись не блокируется

---

## 7. KASPI ПЛАТЁЖНАЯ СИСТЕМА

### Принцип работы

Kaspi не предоставляет официальный API для интеграций. SalonSync использует **Kaspi Deep Link** — специальную ссылку, которая открывает приложение Kaspi с предзаполненными данными.

### Генерация ссылки

```
https://kaspi.kz/pay?phone={KASPI_PHONE}&amount={сумма}&comment={описание}

Пример:
https://kaspi.kz/pay?phone=77001234567&amount=15000&comment=Booking+42
```

### QR-код

Та же ссылка кодируется в QR-код (PNG, base64) — клиент сканирует его в приложении Kaspi.

### Поток оплаты

```
1. Клиент создаёт запись (Booking.status = PENDING)
2. POST /bookings/{id}/pay → получает kaspi_link + qr_code_base64
3. Frontend отображает QR-код и кнопку "Оплатить через Kaspi"
4. Клиент оплачивает через приложение Kaspi
5. POST /bookings/{id}/confirm-payment (ручное подтверждение)
6. Booking.status → PAID, уведомления мастеру и клиенту

⚠️ Автоматического вебхука от Kaspi нет.
   Подтверждение оплаты выполняется вручную или через Telegram бот.
```

---

## 8. FRONTEND АРХИТЕКТУРА

### Поток бронирования (BookingDrawer — 5 шагов)

```
STEP 1: Выбор услуги
        └── Список услуг салона (цена, длительность)

STEP 2: Выбор мастера
        └── Мастера, предоставляющие выбранную услугу
            + кнопка "Портфолио"

STEP 3: Выбор даты и времени
        ├── CalendarPicker (доступные даты)
        └── Временные слоты (getAvailableSlots)

STEP 4: Данные клиента
        ├── Имя (обязательно)
        ├── Телефон (обязательно)
        ├── Email (опционально)
        └── Заметка

STEP 5: Оплата
        ├── QR-код (base64 PNG)
        ├── Кнопка "Оплатить через Kaspi"
        └── После оплаты → confirmPayment()
```

### Мои записи (OTP авторизация)

```
Клиент вводит номер телефона
  → POST /my-bookings/send-code
  → OTP код приходит в WhatsApp
Вводит код
  → POST /my-bookings/verify
  → получает JWT токен (15 мин)
  → видит список своих записей
  → может отменить запись
```

### Компоненты

| Компонент | Назначение |
|----------|-----------|
| `BookingDrawer` | Многошаговое бронирование (5 шагов) |
| `SalonCard` | Карточка салона (фото, рейтинг, адрес) |
| `SalonDetail` | Детальная страница (мастера, услуги, галерея) |
| `MasterCard` | Карточка мастера |
| `MasterPortfolioModal` | Просмотр работ мастера |
| `MyBookingsModal` | Мои записи по OTP |
| `CalendarPicker` | Выбор даты с подсветкой доступных дней |
| `Header` | Навигация + переключатель языка (RU/KK) |

### Локализация (i18n)

Поддерживается **два языка**: Русский (RU) и Казахский (KK).
Переключатель в шапке сайта. Все тексты UI переведены.

---

## 9. ПОЛНЫЙ ПОТОК РАБОТЫ СИСТЕМЫ

```
┌─────────────────────────────────────────────────────────┐
│                    КЛИЕНТ (Браузер)                     │
└─────────────────────────────────────────────────────────┘
         │
         │  1. Открывает сайт → видит список салонов
         │  2. Выбирает салон, услугу, мастера, время
         │  3. Вводит имя и телефон
         │  4. Оплачивает через Kaspi QR
         ▼
┌─────────────────────────────────────────────────────────┐
│                  BACKEND (FastAPI)                       │
│                                                         │
│  POST /bookings/     → создаёт Booking (PENDING)        │
│  POST /bookings/pay  → генерирует Kaspi link + QR       │
│  POST /confirm-pay   → Booking.status = PAID            │
└─────────────────────────────────────────────────────────┘
         │                         │
         ▼                         ▼
┌─────────────────┐     ┌────────────────────────┐
│  TELEGRAM BOT   │     │   WhatsApp (WAHA)       │
│                 │     │                        │
│  → Мастеру:    │     │  → Клиенту:            │
│  "Новая запись"│     │  "Запись подтверждена" │
│  "Оплачено"    │     │  "Оплата расталды"     │
│  "Отменено"    │     │  "Напоминание за 2ч"   │
└─────────────────┘     └────────────────────────┘

┌─────────────────────────────────────────────────────────┐
│                  МАСТЕР (Telegram)                       │
│                                                         │
│  /start → Регистрация (5 шагов) → PENDING               │
│  Админ одобряет → APPROVED → мастер появляется на сайте │
│  Получает уведомления о новых записях                   │
│  Просматривает расписание / экспортирует в Excel        │
└─────────────────────────────────────────────────────────┘
```

---

## 10. ПЕРЕМЕННЫЕ ОКРУЖЕНИЯ

### Backend (`backend/.env`)

```bash
# Telegram Bot
TELEGRAM_BOT_TOKEN=xxxxxxxxxx:xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
ADMIN_CHAT_ID=123456789           # Telegram ID администратора

# База данных
DATABASE_URL=sqlite:///./app.db
# Для production:
# DATABASE_URL=postgresql://user:pass@host:5432/salonsync

# Kaspi
KASPI_PHONE=77001234567           # Номер для приёма платежей (без +)

# CORS
FRONTEND_ORIGINS=http://localhost:3000,https://yourapp.vercel.app
CORS_MODE=open                    # или "strict"

# WhatsApp (WAHA)
WHATSAPP_API_URL=https://waha.railway.app
WHATSAPP_SESSION=default
WHATSAPP_API_KEY=your_api_key

# JWT
JWT_SECRET=change_this_in_production
```

### Frontend (`frontend/.env`)

```bash
NEXT_PUBLIC_API_BASE=http://localhost:8000
# Production:
# NEXT_PUBLIC_API_BASE=https://your-backend.railway.app
```

---

## 11. РАЗВЁРТЫВАНИЕ

### Backend → Railway

```
Репозиторий → Railway
├── Dockerfile (Python 3.11, Uvicorn, порт $PORT)
├── railway.json (healthcheck /health, restart on failure)
└── Env Variables через Railway Dashboard
```

### Frontend → Vercel

```
Репозиторий → Vercel
├── Next.js автодетектирование
├── NEXT_PUBLIC_API_BASE = URL Railway бэкенда
└── Автодеплой при каждом push в main
```

### WhatsApp → WAHA на Railway

```
Docker Image: devlikeapro/waha:latest
Port: 8080
Env: WAHA_API_KEY, WAHA_DASHBOARD_USERNAME, WAHA_DASHBOARD_PASSWORD
Dashboard: https://waha.railway.app/dashboard
```

---

## 12. БЕЗОПАСНОСТЬ

| Механизм | Реализация |
|---------|-----------|
| OTP авторизация | 6-значный код через WhatsApp, TTL 5 мин, rate limit 1/мин |
| JWT токены | Токен сессии 15 мин, подписан JWT_SECRET |
| Soft delete | Удаление через is_active флаг (данные не теряются) |
| CORS | Настраиваемый режим: open (разработка) / strict (продакшн) |
| Модерация мастеров | Новые мастера получают статус PENDING до одобрения админом |

---

## 13. РЕЗЮМЕ

**SalonSync** — платформа-агрегатор салонов красоты города Алматы.

**Ключевые возможности:**
- Просмотр салонов с фотогалереей, рейтингом, мастерами и услугами
- Онлайн-запись с выбором мастера, даты и времени (умный алгоритм слотов)
- Оплата через Kaspi QR-код (самая популярная платёжная система Казахстана)
- Уведомления мастеру через Telegram, клиенту через WhatsApp
- Просмотр своих записей через OTP верификацию по номеру телефона
- Регистрация мастеров через Telegram бот с модерацией
- Двуязычный интерфейс (Русский / Казахский)

**Стек:** `Python 3.11` · `FastAPI` · `SQLAlchemy` · `PostgreSQL` · `React 19` · `Next.js 16` · `Tailwind CSS` · `aiogram 3` · `WAHA` · `Docker` · `Railway` · `Vercel`