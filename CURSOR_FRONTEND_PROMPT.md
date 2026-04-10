# SalonSync Frontend — Cursor Prompt

## Жобаның контексті

SalonSync — Алматы қаласының салондар агрегаторы. Backend FastAPI-де жазылған, Frontend Next.js 16 + React 19 + TypeScript + Tailwind CSS 4 + Framer Motion.

**Маңызды:** Клиент платформаға тіркелмейді. Жазылу кезінде тек аты + телефон жазады, Kaspi арқылы төлейді, WhatsApp-ка растау хабарлама алады. Телефон арқылы жазылуларын көре алады (OTP верификация).

## Технологиялар

- **Next.js 16.2.2** (App Router, Turbopack)
- **React 19.2.4**
- **TypeScript 5**
- **Tailwind CSS 4** (custom theme in globals.css)
- **Framer Motion 12** (анимациялар)
- **Lucide React** (иконкалар)
- **date-fns 4** (дата форматтау)
- **Axios** (HTTP client — қазір тек fetch қолданылады api.ts-те)
- **React Hook Form + Zod** (қосылған, бірақ толық қолданылмаған)

## Дизайн жүйесі

**Түстер (globals.css):**
- `bone` (#FAF9F6) — негізгі фон
- `graphite` (#1A1A1A) — негізгі мәтін, кнопкалар
- `light-gray` (#E8E8E8) — шекаралар
- `warm-gray` (#9C9C9C) — екінші деңгейдегі мәтін
- `cream` (#F5F5DC) — екінші фон

**Шрифттар:**
- Playfair Display (serif) — тақырыптар `font-serif`
- Inter (sans-serif) — UI элементтері `font-sans`

**Утилит класстар (globals.css-тен):**
- `.btn-primary` — graphite фон, bone мәтін, uppercase, rounded-full
- `.btn-secondary` — transparent, border, hover bg-graphite/5
- `.card` — white, rounded-3xl, border light-gray/80, shadow-soft
- `.card-glass` — white/90 backdrop-blur, rounded-3xl
- `.container-luxury` — max-w-7xl mx-auto px-6 md:px-8 lg:px-12
- `.heading-xl`, `.heading-lg`, `.heading-md`, `.heading-sm` — тақырып өлшемдері
- `.body-lg`, `.body-md`, `.body-sm` — мәтін өлшемдері
- `.label` — text-xs uppercase tracking-widest
- `.input` — rounded-2xl, border-2, focus border-gold
- `.divider` — w-16 h-0.5 bg-gold

**Анимация стилі:**
- Framer Motion: fadeInUp, staggerContainer, scaleIn variants
- whileInView={{ opacity: 1, y: 0 }} viewport={{ once: true }}
- whileHover={{ y: -10, scale: 1.015 }}
- Spring physics: stiffness 290, damping 22
- Backdrop blur on modals/drawers

## Қазіргі файл құрылымы

```
frontend/src/
├── app/
│   ├── layout.tsx          — Root layout (Playfair + Inter fonts, metadata)
│   ├── page.tsx            — Бірыңғай SPA бет (1116 жол): Header, Hero, Salons, About, Contacts, Footer
│   └── globals.css         — Дизайн токендері + утилит класстар
├── components/
│   ├── BookingDrawer.tsx   — 5 қадамдық жазылу drawer (930 жол)
│   ├── SalonCard.tsx       — Салон карточкасы (фото, рейтинг, мекенжай)
│   ├── BrandLogo.tsx       — SVG логотип компоненті
│   ├── MasterCard.tsx      — Мастер карточкасы
│   ├── ServiceCard.tsx     — Қызмет карточкасы
│   ├── Header.tsx          — (қолданылмайды, page.tsx ішінде)
│   └── ui/button.tsx       — Base UI кнопка
└── lib/
    ├── api.ts              — API клиент (fetch, барлық endpoint-тер)
    ├── i18n.ts             — Locale типі ("ru" | "kk")
    └── utils.ts            — cn() утилит функция
```

## Тілдер жүйесі (i18n)

Қазір қарапайым: `locale` state = `"ru"` | `"kk"`, localStorage-ға сақталады.
Әр компонентте `const t = locale === "kk" ? { ... } : { ... }` жазылады.
Қызмет атаулары `kzServiceDict` regex массивімен аударылады (BookingDrawer.tsx ішінде).

## Backend API (http://localhost:8001)

### Қазіргі (жұмыс істейтін) эндпоинттер:

```
GET  /salons/                        → Salon[]
GET  /salons/{id}                    → Salon
GET  /salons/{id}/services           → Service[]
GET  /salons/{id}/masters            → Master[]

GET  /services/                      → Service[]
GET  /masters/                       → Master[]
GET  /masters/{id}/services/         → Service[]

GET  /bookings/available-slots?master_id=X&service_id=Y&date=YYYY-MM-DD → AvailableSlotsResponse
POST /bookings/                      → BookingResponse (body: BookingRequest)
POST /bookings/{id}/pay              → PaymentResponse
POST /bookings/{id}/confirm-payment  → BookingResponse

GET  /bookings/by-phone/{phone}      → BookingDetailResponse[]
```

### ЖАҢА эндпоинттер (backend-те дайын, frontend-те әлі жоқ):

```
# Салон галереясы
GET  /salons/{id}/gallery            → SalonGalleryResponse[]
  Response: [{ id, salon_id, image_url, caption, sort_order, created_at }]

# Бос күндер (календарь үшін)
GET  /bookings/available-dates?master_id=X&service_id=Y&month=YYYY-MM → AvailableDatesResponse
  Response: { master_id, service_id, month: "2026-04", dates: ["2026-04-11", "2026-04-12", ...] }

# Мастер портфолиосы
GET  /masters/{id}/portfolio         → MasterPortfolioResponse[]
  Response: [{ id, master_id, image_url, description, created_at }]

# Менің жазылуларым (OTP верификация)
POST /my-bookings/send-code          → { message, phone }
  Body: { phone: "77771234567" }

POST /my-bookings/verify             → { verified: true, token: "jwt...", bookings: BookingDetailResponse[] }
  Body: { phone: "77771234567", code: "1234" }

GET  /my-bookings?token=jwt...       → BookingDetailResponse[]

DELETE /my-bookings/{booking_id}?token=jwt...  → { message: "Жазылу бас тартылды" }
```

### TypeScript интерфейстер (api.ts-ке қосу керек):

```typescript
// Қазіргі интерфейстер сақталады, тек жаңалары қосылады:

interface SalonGalleryPhoto {
  id: number;
  salon_id: number;
  image_url: string;
  caption: string | null;
  sort_order: number;
  created_at: string;
}

interface AvailableDatesResponse {
  master_id: number;
  service_id: number;
  month: string;
  dates: string[];  // ["2026-04-11", "2026-04-12", ...]
}

interface MasterPortfolioPhoto {
  id: number;
  master_id: number;
  image_url: string;
  description: string | null;
  created_at: string;
}

interface OTPSendResponse {
  message: string;
  phone: string;
}

interface OTPVerifyResponse {
  verified: boolean;
  token: string;
  bookings: BookingDetailResponse[];
}

interface BookingDetailResponse {
  id: number;
  client_id: number;
  master_id: number;
  service_id: number;
  start_time: string;
  end_time: string;
  status: string;  // "pending" | "confirmed" | "paid" | "completed" | "cancelled"
  total_price: string;
  notes: string | null;
  created_at: string;
  updated_at: string | null;
  client: { id: number; name: string; phone: string; email: string | null };
  master: { id: number; name: string; specialization: string | null; bio: string | null; photo_url: string | null; phone: string | null; is_active: boolean };
  service: { id: number; name: string; description: string | null; price: string; duration: number; image_url: string | null; is_active: boolean };
}
```

---

## ТАПСЫРМАЛАР (кезек бойынша)

---

### Тапсырма 1: Салон детальді бет (галерея + карта + маршрут)

**Не істеу керек:**
Қазір SalonCard басылғанда тікелей BookingDrawer ашылады. Оның орнына алдымен салон детальді бетін көрсету керек — галерея, карта, мастерлер, қызметтер, "Жазылу" батырмасы.

**Техникалық іске асыру:**

1. **Жаңа компонент:** `src/components/SalonDetail.tsx`
   - Props: `{ salon: Salon; onClose: () => void; onBooking: () => void; locale: Locale }`
   - BookingDrawer сияқты modal/drawer стилінде ашылады (AnimatePresence + motion.div)
   - Бөлімдері:

   **a) Галерея секциясы (жоғарғы бөлігі)**
   - `GET /salons/{salon.id}/gallery` арқылы фотолар алу
   - Горизонтальді свайп (overflow-x-auto snap-x) немесе CSS grid
   - Фотолар aspect-[16/9] rounded-2xl object-cover
   - Фото болмаса — salon.image_url көрсету (қазіргі карточкадағы сурет)
   - Фото астында caption бар болса көрсету

   **b) Салон ақпараты**
   - Атауы (heading-lg)
   - Рейтинг жұлдыздары + саны
   - Instagram badge (@salon_handle)
   - Сипаттамасы (body-md)

   **c) Карта секциясы**
   - Мекенжайы (MapPin иконкасы + текст)
   - Жұмыс уақыты (Clock иконкасы + текст)
   - Телефон (Phone иконкасы + clickable tel: link)
   - **"Маршрут көрсету" батырмасы** — btn-secondary стилінде
     - Басылғанда 2ГІС deep link ашу: `https://2gis.kz/almaty/search/${encodeURIComponent(salon.address)}`
     - Немесе Google Maps: `https://maps.google.com/?q=${encodeURIComponent(salon.address)}`
   - **2ГІС карта iframe** (опционалды):
     ```html
     <iframe src="https://widgets.2gis.com/widget?type=firmsonmap&options=%7B%22pos%22%3A%7B%22lat%22%3A43.238949%2C%22lon%22%3A76.945465%2C%22zoom%22%3A16%7D%7D" width="100%" height="300" frameBorder="0"></iframe>
     ```

   **d) Қызметтер тізімі (қысқаша)**
   - `GET /salons/{salon.id}/services` деректерін көрсету
   - Әр қызмет: атау + баға + ұзақтығы (компакт тізім)
   - Максимум 5-6 қызмет, қалғандары "Барлығын көру" батырмасымен

   **e) Мастерлер тізімі**
   - `GET /salons/{salon.id}/masters` деректерін көрсету
   - Горизонтальді scroll (overflow-x-auto)
   - Әр мастер: аватар (initials), аты, мамандығы

   **f) "Жазылу" CTA батырмасы**
   - Беттің төменгі жағында sticky
   - btn-primary стилінде: "Жазылу" / "Жазылу"
   - Басылғанда `onBooking()` шақырылады → BookingDrawer ашылады

2. **page.tsx өзгерту:**
   - Жаңа state: `showSalonDetail: boolean`
   - SalonCard onClick: `setSelectedSalon(salon); setShowSalonDetail(true)`
   - SalonDetail onBooking: `setShowSalonDetail(false)` (BookingDrawer ашылады)
   - SalonDetail onClose: `setSelectedSalon(null); setShowSalonDetail(false)`
   - BookingDrawer: тек `selectedSalon && !showSalonDetail` кезінде mount

3. **api.ts-ке қосу:**
   ```typescript
   export async function getSalonGallery(salonId: number): Promise<SalonGalleryPhoto[]>
   // GET /salons/{salonId}/gallery
   ```

**Стиль:**
- Drawer: `bg-bone rounded-t-3xl sm:rounded-3xl max-h-[92vh] overflow-y-auto`
- Галерея: `flex gap-3 overflow-x-auto snap-x snap-mandatory pb-4`
- Әр фото: `snap-center flex-shrink-0 w-[85%] sm:w-[60%] rounded-2xl`
- Карта контейнер: `rounded-2xl overflow-hidden border border-light-gray`
- i18n: Барлық текстке ru/kk нұсқа қосу

---

### Тапсырма 2: Жазылу процесін жақсарту

**Не өзгерту керек (BookingDrawer.tsx):**

**a) Step 3 (datetime) — Календарь view:**

Қазір тек 7 күн көрсетіледі (бүгін + 6 күн). Оның орнына толық ай календарі:

1. `api.ts`-ке жаңа функция:
   ```typescript
   export async function getAvailableDates(masterId: number, serviceId: number, month: string): Promise<AvailableDatesResponse>
   // GET /bookings/available-dates?master_id={masterId}&service_id={serviceId}&month={month}
   ```

2. Календарь компоненті (BookingDrawer ішінде немесе жеке `CalendarPicker.tsx`):
   - Ай + жыл тақырыбы (< Сәуір 2026 >)
   - 7 бағанды grid (Дс Сс Ср Бс Жм Сн Жс)
   - Бос күндер: graphite фон, cursor-pointer, hover эффект
   - Бос емес күндер: text-graphite/25, cursor-not-allowed
   - Өткен күндер: text-graphite/15
   - Таңдалған күн: graphite фон, bone мәтін, ring-2
   - Алдыңғы/келесі ай батырмалары (< >)
   - Мастер мен қызмет таңдалғанда `getAvailableDates()` шақыру
   - Күн таңдалғанда бұрынғыдай `getAvailableSlots()` шақыру

3. Уақыт слоттары: қазіргідей grid-cols-4 gap-2 қалады

**b) Step 2 (master) — Мастер карточкасын жақсарту:**

1. `api.ts`-ке жаңа функция:
   ```typescript
   export async function getMasterPortfolio(masterId: number): Promise<MasterPortfolioPhoto[]>
   // GET /masters/{masterId}/portfolio
   ```

2. Мастер карточкасына қосу:
   - Рейтинг: қазір hardcoded 5.0, сақтай беру (кейін backend-тен келеді)
   - "Жұмыстарын көру" батырмасы (text-sm, underline)
   - Басылғанда портфолио модалы ашылады:
     - `getMasterPortfolio(master.id)` шақыру
     - Фотолар grid (grid-cols-2 gap-2)
     - Әр фото: rounded-xl, aspect-square, object-cover
     - Фото астында description (бар болса)
     - Портфолио бос болса: "Мастердің портфолиосы әлі жоқ" хабарламасы

**c) Step 4 (form) — Баға бөлшектемесі:**
- Қазіргі summary card-қа қосу:
  - Қызмет ұзақтығы: "⏱ 60 мин" (service.duration)
  - Бағасы: "💰 35 000 ₸" (service.price)
  - Бәрі бір card ішінде компакт тізімде

**d) Step 5 (payment) — Success экранын жақсарту:**
- Қазіргі success хабарламаға қосу:
  - "📱 WhatsApp-қа растау хабарламасы жіберілді" текст (body-sm, graphite/60)
  - Жазылу бөлшектемесін толық көрсету:
    - Салон атауы + мекенжайы
    - Мастер аты
    - Қызмет атауы
    - Күні + уақыты
    - Сомасы
  - "Менің жазылуларым" сілтемесі (кейін 3-тапсырмаға байланысты)

---

### Тапсырма 3: "Менің жазылуларым" модальды терезесі

**Не істеу керек:**
Header-ге "Менің жазылуларым" батырмасын қосу. Басылғанда OTP flow арқылы жазылуларды көрсету.

**Компоненттер:**

1. **Жаңа компонент:** `src/components/MyBookingsModal.tsx`
   - Props: `{ isOpen: boolean; onClose: () => void; locale: Locale }`
   - 3 кезең (state machine):

   **Кезең 1: Телефон енгізу**
   - Тақырып: "Менің жазылуларым" / "Менің жазылуларым"
   - Сипаттама: "Телефон номеріңізді жазыңыз, WhatsApp-қа код жіберілді" / қазақша нұсқа
   - Телефон input (BookingDrawer-дегі форматтау логикасын қайта қолдану)
   - "Код жіберу" btn-primary батырмасы
   - API: `POST /my-bookings/send-code { phone }`
   - Қате: "Кодты 1 минуттан кейін қайта сұраңыз" (429 status)

   **Кезең 2: OTP код енгізу**
   - 4 бөлек input (цифр input, auto-focus next)
   - "Қайта жіберу" countdown таймер (60 секунд)
   - Автоматты verify: 4 цифр жинақталғанда `POST /my-bookings/verify { phone, code }`
   - Қате: "Қате код немесе мерзімі өтті" (400 status)
   - Сәтті: token сақтау (state-ке), bookings алу

   **Кезең 3: Жазылулар тізімі**
   - Тақырып: "Сіздің жазылуларыңыз" + жазылулар саны
   - Таб: "Алдағы" | "Өткен"
   - Алдағы: status = pending, confirmed, paid — уақыт бойынша сұрыптау (жақын → алыс)
   - Өткен: status = completed, cancelled — уақыт бойынша сұрыптау (жаңа → ескі)
   - Әр жазылу карточкасы:
     - Статус badge:
       - pending: "Күтуде" сары фон
       - confirmed: "Расталды" көк фон
       - paid: "Төленді" жасыл фон
       - completed: "Аяқталды" сұр фон
       - cancelled: "Бас тартылды" қызыл фон
     - Қызмет атауы (font-semibold)
     - Мастер аты + мамандығы
     - Күні + уақыты (formatted: "15 сәуір, 14:00")
     - Сомасы
     - "Бас тарту" батырмасы (тек pending/confirmed үшін)
       - Confirmation dialog: "Сіз жазылудан бас тартқыңыз келе ме?"
       - API: `DELETE /my-bookings/{booking_id}?token=jwt...`
   - Жазылу жоқ болса: "Жазылулар табылмады" хабарламасы + "Жазылу" батырмасы
   - "Жаңарту" батырмасы (RefreshCw иконкасы)
     - API: `GET /my-bookings?token=jwt...`

2. **api.ts-ке жаңа функциялар:**
   ```typescript
   export async function sendOTPCode(phone: string): Promise<OTPSendResponse>
   // POST /my-bookings/send-code

   export async function verifyOTPCode(phone: string, code: string): Promise<OTPVerifyResponse>
   // POST /my-bookings/verify

   export async function getMyBookings(token: string): Promise<BookingDetailResponse[]>
   // GET /my-bookings?token={token}

   export async function cancelMyBooking(bookingId: number, token: string): Promise<void>
   // DELETE /my-bookings/{bookingId}?token={token}
   ```

3. **page.tsx Header-ге қосу:**
   - Жаңа state: `showMyBookings: boolean`
   - Desktop nav-қа: "Менің жазылуларым" / "Менің жазылуларым" сілтемесі (User иконкасы)
   - Mobile nav-қа да қосу
   - MyBookingsModal mount: `showMyBookings && <MyBookingsModal ... />`

**Стиль:**
- Modal: modal-overlay + modal-content (globals.css-тен)
- OTP inputs: 4 бөлек `w-14 h-14 text-center text-2xl font-bold rounded-xl border-2`
- Жазылу карточкасы: card стилі, divider between items
- Таб: underline active tab, graphite/50 inactive

---

### Тапсырма 4: Мастер портфолиосы (Step 2 жақсартуына байланысты)

Бұл тапсырма 2-тапсырманың Step 2 бөлімімен бірге жасалады. Жеке компонент:

**Жаңа компонент:** `src/components/MasterPortfolioModal.tsx`
- Props: `{ master: Master; isOpen: boolean; onClose: () => void; locale: Locale }`
- `getMasterPortfolio(master.id)` шақыру
- Тақырып: мастер аты + мамандығы
- Фотолар grid: `grid-cols-2 sm:grid-cols-3 gap-3`
- Әр фото: `rounded-xl aspect-square object-cover cursor-pointer`
- Фото басылғанда: толық экранда көрсету (lightbox эффект)
- Бос болса: "Портфолио әлі қосылмаған" placeholder

---

## ЖАЛПЫ ЕРЕЖЕЛЕР

1. **i18n:** Барлық жаңа текстке ru + kk нұсқаларын жаз. Қазіргі pattern-ді қолдан: `locale === "kk" ? "қазақша" : "русча"`

2. **Анимация:** Framer Motion қолдан. Жаңа компоненттерге fadeInUp, stagger, spring анимациялар қос. BookingDrawer стиліне сай болсын.

3. **Стиль:** globals.css-тегі утилит класстарды қолдан (btn-primary, card, heading-lg, т.б.). Жаңа түстер қоспа — тек қазіргі палитраны қолдан.

4. **Responsive:** Mobile-first. Drawer/Modal мобильде толық экран (rounded-t-3xl), десктопта орталықта (max-w-lg rounded-3xl).

5. **Loading states:** Деректер жүктелгенде анимациялық skeleton немесе spinner көрсет.

6. **Error handling:** API қателерін try-catch-пен ұста, пайдаланушыға хабарлама көрсет.

7. **Қазіргі кодты бұзба:** BookingDrawer-дің қазіргі 5 қадамы жұмыс істеп тұр. Оларды жақсарт, бірақ бұзба. SalonCard onClick логикасын өзгерт (алдымен SalonDetail, содан кейін BookingDrawer).

8. **API Base URL:** `http://localhost:8001` — api.ts-тегі API_BASE константасын қолдан.

9. **Иконкалар:** Тек Lucide React қолдан (`lucide-react` пакетінен).

10. **Дата форматтау:** `date-fns` кітапханасын қолдан (орнатылған). Locale: `ru` және `kk` (date-fns/locale-ден).
