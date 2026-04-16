"use client";

import { useState, useEffect } from "react";
import Image from "next/image";
import { X, Calendar, Clock, User, Phone, Loader2, CheckCircle, ExternalLink } from "lucide-react";
import type { Service, Master, TimeSlot, PaymentResponse } from "@/lib/api";
import { getMastersByService, getAvailableSlots, createBooking, getPaymentLink } from "@/lib/api";
import MasterCard from "./MasterCard";

interface BookingModalProps {
  service: Service;
  onClose: () => void;
}

type Step = "master" | "datetime" | "form" | "success";

export default function BookingModal({ service, onClose }: BookingModalProps) {
  const [step, setStep] = useState<Step>("master");
  const [masters, setMasters] = useState<Master[]>([]);
  const [selectedMaster, setSelectedMaster] = useState<Master | null>(null);
  const [selectedDate, setSelectedDate] = useState<string>("");
  const [slots, setSlots] = useState<TimeSlot[]>([]);
  const [selectedSlot, setSelectedSlot] = useState<TimeSlot | null>(null);
  const [clientName, setClientName] = useState("");
  const [clientPhone, setClientPhone] = useState("");
  const [loading, setLoading] = useState(false);
  const [payment, setPayment] = useState<PaymentResponse | null>(null);
  const [error, setError] = useState("");

  // Генерируем даты на неделю вперёд
  const dates = Array.from({ length: 7 }, (_, i) => {
    const date = new Date();
    date.setDate(date.getDate() + i + 1);
    return date.toISOString().split("T")[0];
  });

  // Загружаем мастеров при открытии
  useEffect(() => {
    async function loadMasters() {
      setLoading(true);
      try {
        const data = await getMastersByService(service.id);
        setMasters(data);
      } catch {
        setError("Не удалось загрузить мастеров");
      } finally {
        setLoading(false);
      }
    }
    loadMasters();
  }, [service.id]);

  // Загружаем слоты при выборе даты
  useEffect(() => {
    if (!selectedMaster || !selectedDate) return;

    async function loadSlots() {
      setLoading(true);
      setSlots([]);
      try {
        const data = await getAvailableSlots(selectedMaster!.id, service.id, selectedDate);
        setSlots(data.slots);
      } catch {
        setError("Не удалось загрузить доступное время");
      } finally {
        setLoading(false);
      }
    }
    loadSlots();
  }, [selectedMaster, selectedDate, service.id]);

  const handleSelectMaster = (master: Master) => {
    setSelectedMaster(master);
    setStep("datetime");
  };

  const handleSelectSlot = (slot: TimeSlot) => {
    setSelectedSlot(slot);
    setStep("form");
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!selectedMaster || !selectedSlot) return;

    setLoading(true);
    setError("");

    try {
      const booking = await createBooking({
        master_id: selectedMaster.id,
        service_id: service.id,
        start_time: selectedSlot.start_time,
        client_name: clientName,
        client_phone: clientPhone,
      });

      const paymentData = await getPaymentLink(booking.id);
      setPayment(paymentData);
      setStep("success");
    } catch (err: unknown) {
      const error = err as Error;
      setError(error.message || "Ошибка при создании записи");
    } finally {
      setLoading(false);
    }
  };

  const formatDate = (dateStr: string) => {
    const date = new Date(dateStr);
    const days = ["Вс", "Пн", "Вт", "Ср", "Чт", "Пт", "Сб"];
    const months = ["янв", "фев", "мар", "апр", "май", "июн", "июл", "авг", "сен", "окт", "ноя", "дек"];
    return `${days[date.getDay()]}, ${date.getDate()} ${months[date.getMonth()]}`;
  };

  const formatTime = (dateTimeStr: string) => {
    return dateTimeStr.split("T")[1].substring(0, 5);
  };

  return (
    <div className="fixed inset-0 bg-black/50 backdrop-blur-sm z-50 flex items-center justify-center p-4">
      <div className="bg-white rounded-3xl w-full max-w-lg max-h-[90vh] overflow-hidden shadow-2xl">
        {/* Header */}
        <div className="bg-gradient-to-r from-rose-500 to-purple-500 text-white p-6">
          <div className="flex items-start justify-between">
            <div>
              <h2 className="text-xl font-bold">{service.name}</h2>
              <p className="text-white/80 text-sm mt-1">
                {service.duration} мин · {parseInt(service.price).toLocaleString()} ₸
              </p>
            </div>
            <button
              onClick={onClose}
              className="w-8 h-8 rounded-full bg-white/20 flex items-center justify-center hover:bg-white/30 transition"
            >
              <X className="w-5 h-5" />
            </button>
          </div>

          {/* Steps indicator */}
          <div className="flex gap-2 mt-4">
            {["master", "datetime", "form", "success"].map((s, i) => (
              <div
                key={s}
                className={`h-1 flex-1 rounded-full transition ${
                  ["master", "datetime", "form", "success"].indexOf(step) >= i
                    ? "bg-white"
                    : "bg-white/30"
                }`}
              />
            ))}
          </div>
        </div>

        {/* Content */}
        <div className="p-6 overflow-y-auto max-h-[60vh]">
          {error && (
            <div className="mb-4 p-3 bg-red-50 text-red-600 rounded-xl text-sm">{error}</div>
          )}

          {/* Step 1: Select Master */}
          {step === "master" && (
            <div>
              <h3 className="font-semibold text-gray-900 mb-4 flex items-center gap-2">
                <User className="w-5 h-5 text-rose-500" />
                Выберите мастера
              </h3>
              {loading ? (
                <div className="flex items-center justify-center py-8">
                  <Loader2 className="w-8 h-8 animate-spin text-rose-500" />
                </div>
              ) : masters.length > 0 ? (
                <div className="space-y-3">
                  {masters.map((master) => (
                    <MasterCard
                      key={master.id}
                      master={master}
                      onSelect={handleSelectMaster}
                    />
                  ))}
                </div>
              ) : (
                <p className="text-gray-500 text-center py-8">Нет доступных мастеров</p>
              )}
            </div>
          )}

          {/* Step 2: Select Date & Time */}
          {step === "datetime" && (
            <div>
              <button
                onClick={() => setStep("master")}
                className="text-sm text-gray-500 hover:text-gray-700 mb-4"
              >
                ← Назад к выбору мастера
              </button>

              <h3 className="font-semibold text-gray-900 mb-4 flex items-center gap-2">
                <Calendar className="w-5 h-5 text-rose-500" />
                Выберите дату
              </h3>
              <div className="flex gap-2 overflow-x-auto pb-2 mb-6">
                {dates.map((date) => (
                  <button
                    key={date}
                    onClick={() => setSelectedDate(date)}
                    className={`flex-shrink-0 px-4 py-3 rounded-xl text-sm font-medium transition ${
                      selectedDate === date
                        ? "bg-rose-500 text-white"
                        : "bg-gray-100 text-gray-700 hover:bg-gray-200"
                    }`}
                  >
                    {formatDate(date)}
                  </button>
                ))}
              </div>

              {selectedDate && (
                <>
                  <h3 className="font-semibold text-gray-900 mb-4 flex items-center gap-2">
                    <Clock className="w-5 h-5 text-rose-500" />
                    Выберите время
                  </h3>
                  {loading ? (
                    <div className="flex items-center justify-center py-8">
                      <Loader2 className="w-8 h-8 animate-spin text-rose-500" />
                    </div>
                  ) : slots.length > 0 ? (
                    <div className="grid grid-cols-4 gap-2">
                      {slots.map((slot) => (
                        <button
                          key={slot.start_time}
                          onClick={() => handleSelectSlot(slot)}
                          className="px-3 py-2 rounded-lg text-sm font-medium bg-gray-100 text-gray-700 hover:bg-rose-500 hover:text-white transition"
                        >
                          {formatTime(slot.start_time)}
                        </button>
                      ))}
                    </div>
                  ) : (
                    <p className="text-gray-500 text-center py-8">Нет свободного времени на эту дату</p>
                  )}
                </>
              )}
            </div>
          )}

          {/* Step 3: Client Info Form */}
          {step === "form" && (
            <div>
              <button
                onClick={() => setStep("datetime")}
                className="text-sm text-gray-500 hover:text-gray-700 mb-4"
              >
                ← Назад к выбору времени
              </button>

              <div className="bg-gray-50 rounded-xl p-4 mb-6">
                <p className="text-sm text-gray-600">
                  <strong>Мастер:</strong> {selectedMaster?.name}
                </p>
                <p className="text-sm text-gray-600">
                  <strong>Дата:</strong> {selectedDate && formatDate(selectedDate)}
                </p>
                <p className="text-sm text-gray-600">
                  <strong>Время:</strong> {selectedSlot && formatTime(selectedSlot.start_time)}
                </p>
              </div>

              <form onSubmit={handleSubmit} className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    <User className="w-4 h-4 inline mr-1" />
                    Ваше имя
                  </label>
                  <input
                    type="text"
                    value={clientName}
                    onChange={(e) => setClientName(e.target.value)}
                    required
                    placeholder="Введите имя"
                    className="w-full px-4 py-3 rounded-xl border border-gray-200 focus:border-rose-400 focus:ring-2 focus:ring-rose-100 outline-none transition"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    <Phone className="w-4 h-4 inline mr-1" />
                    Телефон
                  </label>
                  <input
                    type="tel"
                    value={clientPhone}
                    onChange={(e) => setClientPhone(e.target.value)}
                    required
                    placeholder="+7 777 123 4567"
                    className="w-full px-4 py-3 rounded-xl border border-gray-200 focus:border-rose-400 focus:ring-2 focus:ring-rose-100 outline-none transition"
                  />
                </div>

                <button
                  type="submit"
                  disabled={loading}
                  className="w-full py-4 bg-gradient-to-r from-rose-500 to-purple-500 text-white font-semibold rounded-xl hover:from-rose-600 hover:to-purple-600 transition disabled:opacity-50 flex items-center justify-center gap-2"
                >
                  {loading ? (
                    <>
                      <Loader2 className="w-5 h-5 animate-spin" />
                      Создание записи...
                    </>
                  ) : (
                    `Забронировать · ${parseInt(service.price).toLocaleString()} ₸`
                  )}
                </button>
              </form>
            </div>
          )}

          {/* Step 4: Success */}
          {step === "success" && payment && (
            <div className="text-center py-4">
              <div className="w-16 h-16 bg-green-100 rounded-full flex items-center justify-center mx-auto mb-4">
                <CheckCircle className="w-8 h-8 text-green-500" />
              </div>

              <h3 className="text-xl font-bold text-gray-900 mb-2">Запись создана!</h3>
              <p className="text-gray-600 mb-4">
                Отсканируйте QR-код в приложении Kaspi для оплаты
              </p>

              {/* QR Code */}
              {payment.qr_code_base64 && (
                <div className="bg-white rounded-xl p-4 mb-4 inline-block border border-gray-200">
                  <Image
                    src={`data:image/png;base64,${payment.qr_code_base64}`}
                    alt="QR код для оплаты через Kaspi"
                    className="w-48 h-48 mx-auto"
                    width={192}
                    height={192}
                    unoptimized
                  />
                </div>
              )}

              <div className="bg-gray-50 rounded-xl p-4 mb-6">
                <p className="text-2xl font-bold text-gray-900">
                  {parseInt(payment.amount).toLocaleString()} ₸
                </p>
                <p className="text-sm text-gray-500 mt-1">
                  После оплаты отправьте скриншот мастеру
                </p>
              </div>

              <a
                href={payment.kaspi_link}
                target="_blank"
                rel="noopener noreferrer"
                className="inline-flex items-center gap-2 px-6 py-3 bg-[#F14635] text-white font-semibold rounded-xl hover:bg-[#d93d2e] transition"
              >
                <ExternalLink className="w-5 h-5" />
                Открыть в Kaspi
              </a>

              <button
                onClick={onClose}
                className="block w-full mt-4 text-gray-500 hover:text-gray-700 transition"
              >
                Закрыть
              </button>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
