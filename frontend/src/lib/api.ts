const API_BASE = process.env.NEXT_PUBLIC_API_BASE || "http://localhost:8000";

export interface Salon {
  id: number;
  name: string;
  description: string | null;
  address: string | null;
  phone: string | null;
  instagram: string | null;
  image_url: string | null;
  rating: number;
  working_hours: string | null;
  is_active: boolean;
}

export interface Service {
  id: number;
  name: string;
  description: string | null;
  price: string;
  duration: number;
  image_url: string | null;
  is_active: boolean;
}

export interface Master {
  id: number;
  name: string;
  specialization: string | null;
  bio: string | null;
  photo_url: string | null;
  phone: string | null;
  is_active: boolean;
  salon_id?: number | null;
}

export interface TimeSlot {
  start_time: string;
  end_time: string;
}

export interface AvailableSlotsResponse {
  master_id: number;
  service_id: number;
  date: string;
  slots: TimeSlot[];
}

export interface BookingRequest {
  master_id: number;
  service_id: number;
  start_time: string;
  client_name: string;
  client_phone: string;
  notes?: string;
}

export interface BookingResponse {
  id: number;
  client_id: number;
  master_id: number;
  service_id: number;
  start_time: string;
  end_time: string;
  status: string;
  total_price: string;
}

export interface PaymentResponse {
  booking_id: number;
  amount: string;
  kaspi_link: string;
  qr_code_base64: string | null;  // QR-код в формате base64
  qr_code_url: string | null;     // Устаревшее поле
}

export interface SalonGalleryPhoto {
  id: number;
  salon_id: number;
  image_url: string;
  caption: string | null;
  sort_order: number;
  created_at: string;
}

export interface AvailableDatesResponse {
  master_id: number;
  service_id: number;
  month: string;
  dates: string[];
}

export interface MasterPortfolioPhoto {
  id: number;
  master_id: number;
  image_url: string;
  description: string | null;
  created_at: string;
}

export interface ClientDetail {
  id: number;
  name: string;
  phone: string;
  email: string | null;
  created_at: string;
}

export interface BookingDetailResponse {
  id: number;
  client_id: number;
  master_id: number;
  service_id: number;
  start_time: string;
  end_time: string;
  status: string;
  total_price: string;
  notes: string | null;
  created_at: string;
  updated_at: string | null;
  client: ClientDetail;
  master: Master;
  service: Service;
}

export interface OTPSendResponse {
  message: string;
  phone: string;
}

export interface OTPVerifyResponse {
  verified: boolean;
  token: string;
  bookings: BookingDetailResponse[];
}

// Получить все услуги
export async function getServices(): Promise<Service[]> {
  const res = await fetch(`${API_BASE}/services/`);
  if (!res.ok) throw new Error("Failed to fetch services");
  return res.json();
}

// Получить всех мастеров
export async function getMasters(): Promise<Master[]> {
  const res = await fetch(`${API_BASE}/masters/`);
  if (!res.ok) throw new Error("Failed to fetch masters");
  return res.json();
}

// Получить мастеров по услуге
export async function getMastersByService(serviceId: number): Promise<Master[]> {
  const masters = await getMasters();
  // Фильтруем мастеров, которые предоставляют эту услугу
  const mastersWithService: Master[] = [];

  for (const master of masters) {
    const res = await fetch(`${API_BASE}/masters/${master.id}/services`);
    if (res.ok) {
      const services: Service[] = await res.json();
      if (services.some(s => s.id === serviceId)) {
        mastersWithService.push(master);
      }
    }
  }

  return mastersWithService;
}

// Получить свободные слоты
export async function getAvailableSlots(
  masterId: number,
  serviceId: number,
  date: string
): Promise<AvailableSlotsResponse> {
  const res = await fetch(
    `${API_BASE}/bookings/available-slots?master_id=${masterId}&service_id=${serviceId}&date=${date}`
  );
  if (!res.ok) throw new Error("Failed to fetch slots");
  return res.json();
}

// Создать бронирование
export async function createBooking(data: BookingRequest): Promise<BookingResponse> {
  const res = await fetch(`${API_BASE}/bookings/`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(data),
  });
  if (!res.ok) {
    const error = await res.json();
    throw new Error(error.detail || "Failed to create booking");
  }
  return res.json();
}

// Получить ссылку на оплату
export async function getPaymentLink(bookingId: number): Promise<PaymentResponse> {
  const res = await fetch(`${API_BASE}/bookings/${bookingId}/pay`, {
    method: "POST",
  });
  if (!res.ok) throw new Error("Failed to get payment link");
  return res.json();
}

// Подтвердить оплату (мок — уведомляет мастера и меняет статус на PAID)
export async function confirmPayment(bookingId: number): Promise<BookingResponse> {
  const res = await fetch(`${API_BASE}/bookings/${bookingId}/confirm-payment`, {
    method: "POST",
  });
  if (!res.ok) throw new Error("Failed to confirm payment");
  return res.json();
}

// ============ Salon API ============

// Получить все салоны
export async function getSalons(): Promise<Salon[]> {
  const res = await fetch(`${API_BASE}/salons/`);
  if (!res.ok) throw new Error("Failed to fetch salons");
  return res.json();
}

// Получить один салон
export async function getSalon(salonId: number): Promise<Salon> {
  const res = await fetch(`${API_BASE}/salons/${salonId}`);
  if (!res.ok) throw new Error("Failed to fetch salon");
  return res.json();
}

// Получить услуги салона
export async function getSalonServices(salonId: number): Promise<Service[]> {
  const res = await fetch(`${API_BASE}/salons/${salonId}/services`);
  if (!res.ok) throw new Error("Failed to fetch salon services");
  return res.json();
}

// Получить мастеров салона
export async function getSalonMasters(salonId: number): Promise<Master[]> {
  const res = await fetch(`${API_BASE}/salons/${salonId}/masters`);
  if (!res.ok) throw new Error("Failed to fetch salon masters");
  return res.json();
}

// Получить мастеров салона по услуге
export async function getSalonMastersByService(salonId: number, serviceId: number): Promise<Master[]> {
  const masters = await getSalonMasters(salonId);
  const mastersWithService: Master[] = [];

  for (const master of masters) {
    const res = await fetch(`${API_BASE}/masters/${master.id}/services`);
    if (res.ok) {
      const services: Service[] = await res.json();
      if (services.some(s => s.id === serviceId)) {
        mastersWithService.push(master);
      }
    }
  }

  return mastersWithService;
}

export async function getSalonGallery(salonId: number): Promise<SalonGalleryPhoto[]> {
  const res = await fetch(`${API_BASE}/salons/${salonId}/gallery`);
  if (!res.ok) throw new Error("Failed to fetch salon gallery");
  return res.json();
}

export async function getAvailableDates(
  masterId: number,
  serviceId: number,
  month: string
): Promise<AvailableDatesResponse> {
  const params = new URLSearchParams({
    master_id: String(masterId),
    service_id: String(serviceId),
    month,
  });
  const res = await fetch(`${API_BASE}/bookings/available-dates?${params}`);
  if (!res.ok) throw new Error("Failed to fetch available dates");
  return res.json();
}

export async function getMasterPortfolio(masterId: number): Promise<MasterPortfolioPhoto[]> {
  const res = await fetch(`${API_BASE}/masters/${masterId}/portfolio`);
  if (!res.ok) throw new Error("Failed to fetch portfolio");
  return res.json();
}

export async function sendOTPCode(phone: string): Promise<OTPSendResponse> {
  const res = await fetch(`${API_BASE}/my-bookings/send-code`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ phone }),
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    const detail = typeof err.detail === "string" ? err.detail : "Failed to send code";
    throw new Error(detail);
  }
  return res.json();
}

export async function verifyOTPCode(phone: string, code: string): Promise<OTPVerifyResponse> {
  const res = await fetch(`${API_BASE}/my-bookings/verify`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ phone, code }),
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    const detail = typeof err.detail === "string" ? err.detail : "Verification failed";
    throw new Error(detail);
  }
  return res.json();
}

export async function getMyBookings(token: string): Promise<BookingDetailResponse[]> {
  const res = await fetch(
    `${API_BASE}/my-bookings/?token=${encodeURIComponent(token)}`
  );
  if (!res.ok) throw new Error("Failed to load bookings");
  return res.json();
}

export async function cancelMyBooking(bookingId: number, token: string): Promise<void> {
  const res = await fetch(
    `${API_BASE}/my-bookings/${bookingId}?token=${encodeURIComponent(token)}`,
    { method: "DELETE" }
  );
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    const detail = typeof err.detail === "string" ? err.detail : "Failed to cancel booking";
    throw new Error(detail);
  }
}
