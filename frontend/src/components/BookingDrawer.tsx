"use client";

import { useState, useEffect, useRef } from "react";
import { motion, AnimatePresence, type Variants } from "framer-motion";
import {
  X,
  Calendar,
  Clock,
  User,
  Phone,
  Loader2,
  CheckCircle,
  ExternalLink,
  Sparkles,
  Star,
  ChevronLeft,
  CreditCard,
  ArrowRight,
} from "lucide-react";
import type { Salon, Service, Master, TimeSlot, PaymentResponse, BookingResponse } from "@/lib/api";
import {
  getSalonServices,
  getSalonMastersByService,
  getAvailableSlots,
  getAvailableDates,
  createBooking,
  getPaymentLink,
} from "@/lib/api";
import type { Locale } from "@/lib/i18n";
import CalendarPicker from "@/components/CalendarPicker";
import MasterPortfolioModal from "@/components/MasterPortfolioModal";

interface BookingDrawerProps {
  salon: Salon;
  onClose: () => void;
  locale: Locale;
  onOpenMyBookings?: () => void;
}

type Step = "service" | "master" | "datetime" | "form" | "payment";

const STEPS: Step[] = ["service", "master", "datetime", "form", "payment"];

const STEP_TITLES: Record<Locale, Record<Step, string>> = {
  ru: {
    service: "Выберите услугу",
    master: "Выберите мастера",
    datetime: "Выберите время",
    form: "Ваши данные",
    payment: "Оплата",
  },
  kk: {
    service: "Қызметті таңдаңыз",
    master: "Мастерді таңдаңыз",
    datetime: "Уақытты таңдаңыз",
    form: "Сіздің деректеріңіз",
    payment: "Төлем",
  },
};

// Backdrop blur animation
const backdropVariants: Variants = {
  hidden: { opacity: 0 },
  visible: { opacity: 1 },
};

// Drawer slide animation
const drawerVariants: Variants = {
  hidden: { y: "100%", opacity: 0 },
  visible: {
    y: 0,
    opacity: 1,
    transition: {
      type: "spring" as const,
      damping: 30,
      stiffness: 300,
    },
  },
  exit: {
    y: "100%",
    opacity: 0,
    transition: {
      duration: 0.3,
    },
  },
};

// Content fade animation
const contentVariants: Variants = {
  hidden: { opacity: 0, x: 20 },
  visible: {
    opacity: 1,
    x: 0,
    transition: { duration: 0.3 },
  },
  exit: {
    opacity: 0,
    x: -20,
    transition: { duration: 0.2 },
  },
};

// Stagger children
const staggerContainer: Variants = {
  hidden: { opacity: 0 },
  visible: {
    opacity: 1,
    transition: {
      staggerChildren: 0.05,
    },
  },
};

const staggerItem: Variants = {
  hidden: { opacity: 0, y: 10 },
  visible: { opacity: 1, y: 0 },
};

const kzServiceDict: Array<[RegExp, string]> = [
  [/Женская стрижка/gi, "Әйелдер шаш қиюы"],
  [/Стрижка с укладкой/gi, "Сәндеумен шаш қию"],
  [/Окрашивание/gi, "Бояу"],
  [/Однотонное окрашивание/gi, "Бір түске бояу"],
  [/Сложное окрашивание/gi, "Күрделі бояу"],
  [/Балаяж/gi, "Балаяж"],
  [/шатуш/gi, "Шатуш"],
  [/омбре/gi, "Омбре"],
  [/Маникюр с покрытием/gi, "Жабынды маникюр"],
  [/Маникюр \+ гель-лак/gi, "Маникюр + гель-лак"],
  [/Маникюр/gi, "Маникюр"],
  [/Классический маникюр/gi, "Классикалық маникюр"],
  [/Наращивание ресниц/gi, "Кірпік өсіру"],
  [/Классическое наращивание/gi, "Классикалық өсіру"],
  [/Ламинирование бровей/gi, "Қас ламинациясы"],
  [/Долговременная укладка бровей/gi, "Қастарды ұзақ уақытқа сәндеу"],
];

function localizeServiceText(value: string, locale: Locale) {
  if (locale !== "kk") return value;
  return kzServiceDict.reduce((acc, [pattern, replacement]) => {
    return acc.replace(pattern, replacement);
  }, value);
}

export default function BookingDrawer({ salon, onClose, locale, onOpenMyBookings }: BookingDrawerProps) {
  const closeButtonRef = useRef<HTMLButtonElement | null>(null);
  const [step, setStep] = useState<Step>("service");
  const [services, setServices] = useState<Service[]>([]);
  const [masters, setMasters] = useState<Master[]>([]);
  const [selectedService, setSelectedService] = useState<Service | null>(null);
  const [selectedMaster, setSelectedMaster] = useState<Master | null>(null);
  const [selectedDate, setSelectedDate] = useState<string>("");
  const [slots, setSlots] = useState<TimeSlot[]>([]);
  const [selectedSlot, setSelectedSlot] = useState<TimeSlot | null>(null);
  const [clientName, setClientName] = useState("");
  const [clientPhone, setClientPhone] = useState("");
  const [phoneError, setPhoneError] = useState("");
  const [loading, setLoading] = useState(false);
  const [payment, setPayment] = useState<PaymentResponse | null>(null);
  const [createdBooking, setCreatedBooking] = useState<BookingResponse | null>(null);
  const [calendarMonth, setCalendarMonth] = useState(() => {
    const d = new Date();
    return `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, "0")}`;
  });
  const [availableDateSet, setAvailableDateSet] = useState<Set<string>>(new Set());
  const [portfolioMaster, setPortfolioMaster] = useState<Master | null>(null);
  const [datesLoading, setDatesLoading] = useState(false);
  const [error, setError] = useState("");
  const t = locale === "kk"
    ? {
        close: "Жабу",
        bookingCreated: "Жазылу жасалды!",
        payWithKaspi: "Kaspi қосымшасымен QR-кодты сканерлеп төлеңіз",
        openKaspi: "Kaspi-ді ашу",
        closeBookingModal: "Жазылу терезесін жабу",
        whatsappNote: "📱 WhatsApp-қа растау хабарламасы жіберілді",
        myBookings: "Менің жазылуларым",
        backServices: "Қызметтерге оралу",
        backMasters: "Мастерлерге оралу",
        backTime: "Уақыт таңдауға оралу",
        pickDate: "Күнді таңдаңыз",
        pickTime: "Уақытты таңдаңыз",
        noSlots: "Бұл күнге бос уақыт жоқ",
        portfolio: "Жұмыстарын көру",
        yourBooking: "Сіздің жазылуыңыз",
        service: "Қызмет",
        master: "Мастер",
        date: "Күні",
        time: "Уақыты",
        duration: "Ұзақтығы",
        price: "Баға",
        name: "Атыңыз",
        namePh: "Атыңызды жазыңыз",
        phone: "Телефон",
        creating: "Жазылу жасалуда...",
        toPay: "Төлемге өту",
        afterPay: "Төлемнен кейін скриншотты мастерге жіберіңіз",
        salon: "Салон",
        address: "Мекенжай",
      }
    : {
        close: "Закрыть",
        bookingCreated: "Запись создана!",
        payWithKaspi: "Отсканируйте QR-код в приложении Kaspi для оплаты",
        openKaspi: "Открыть в Kaspi",
        closeBookingModal: "Закрыть окно записи",
        whatsappNote: "📱 Сообщение с подтверждением отправлено в WhatsApp",
        myBookings: "Мои записи",
        backServices: "Назад к услугам",
        backMasters: "Назад к мастерам",
        backTime: "Назад к выбору времени",
        pickDate: "Выберите дату",
        pickTime: "Выберите время",
        noSlots: "Нет свободного времени на эту дату",
        portfolio: "Посмотреть работы",
        yourBooking: "Ваша запись",
        service: "Услуга",
        master: "Мастер",
        date: "Дата",
        time: "Время",
        duration: "Длительность",
        price: "Стоимость",
        name: "Ваше имя",
        namePh: "Введите имя",
        phone: "Телефон",
        creating: "Создание записи...",
        toPay: "Перейти к оплате",
        afterPay: "После оплаты отправьте скриншот мастеру",
        salon: "Салон",
        address: "Адрес",
      };

  // Load services on mount
  useEffect(() => {
    async function loadServices() {
      setLoading(true);
      try {
        const data = await getSalonServices(salon.id);
        setServices(data);
      } catch {
        setError("Не удалось загрузить услуги");
      } finally {
        setLoading(false);
      }
    }
    loadServices();
  }, [salon.id]);

  // Load masters when service selected
  useEffect(() => {
    if (!selectedService) return;

    async function loadMasters() {
      setLoading(true);
      try {
        const data = await getSalonMastersByService(salon.id, selectedService!.id);
        setMasters(data);
      } catch {
        setError("Не удалось загрузить мастеров");
      } finally {
        setLoading(false);
      }
    }
    loadMasters();
  }, [salon.id, selectedService]);

  // Load slots when date selected
  useEffect(() => {
    if (!selectedMaster || !selectedDate || !selectedService) return;

    async function loadSlots() {
      setLoading(true);
      setSlots([]);
      try {
        const data = await getAvailableSlots(
          selectedMaster!.id,
          selectedService!.id,
          selectedDate
        );
        setSlots(data.slots);
      } catch {
        setError("Не удалось загрузить доступное время");
      } finally {
        setLoading(false);
      }
    }
    loadSlots();
  }, [selectedMaster, selectedDate, selectedService]);

  useEffect(() => {
    if (step !== "datetime" || !selectedMaster || !selectedService) return;
    const master = selectedMaster;
    const service = selectedService;
    let cancelled = false;
    async function loadDates() {
      setDatesLoading(true);
      try {
        const res = await getAvailableDates(
          master.id,
          service.id,
          calendarMonth
        );
        if (!cancelled) setAvailableDateSet(new Set(res.dates));
      } catch {
        if (!cancelled) setAvailableDateSet(new Set());
      } finally {
        if (!cancelled) setDatesLoading(false);
      }
    }
    loadDates();
    return () => {
      cancelled = true;
    };
  }, [step, selectedMaster, selectedService, calendarMonth]);

  useEffect(() => {
    closeButtonRef.current?.focus();
    const onKeyDown = (event: KeyboardEvent) => {
      if (event.key === "Escape") onClose();
    };
    document.addEventListener("keydown", onKeyDown);
    const originalOverflow = document.body.style.overflow;
    document.body.style.overflow = "hidden";
    return () => {
      document.body.style.overflow = originalOverflow;
      document.removeEventListener("keydown", onKeyDown);
    };
  }, [onClose]);

  const currentStepIndex = STEPS.indexOf(step);

  const handleSelectService = (service: Service) => {
    setSelectedService(service);
    setSelectedMaster(null);
    setSelectedSlot(null);
    setStep("master");
  };

  const handleSelectMaster = (master: Master) => {
    setSelectedMaster(master);
    setSelectedSlot(null);
    setSelectedDate("");
    const d = new Date();
    setCalendarMonth(`${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, "0")}`);
    setStep("datetime");
  };

  const handleSelectSlot = (slot: TimeSlot) => {
    setSelectedSlot(slot);
    setStep("form");
  };

  const validatePhone = (phone: string): boolean => {
    // Kazakhstan phone format: +7 XXX XXX XXXX
    const cleaned = phone.replace(/\D/g, "");
    if (cleaned.length < 11) {
      setPhoneError("Введите полный номер телефона");
      return false;
    }
    if (!cleaned.startsWith("7") && !cleaned.startsWith("8")) {
      setPhoneError("Номер должен начинаться с +7");
      return false;
    }
    setPhoneError("");
    return true;
  };

  const formatPhoneInput = (value: string) => {
    // Remove non-digits
    let cleaned = value.replace(/\D/g, "");

    // Ensure starts with 7
    if (cleaned.startsWith("8")) {
      cleaned = "7" + cleaned.slice(1);
    }
    if (!cleaned.startsWith("7") && cleaned.length > 0) {
      cleaned = "7" + cleaned;
    }

    // Format: +7 XXX XXX XXXX
    let formatted = "";
    if (cleaned.length > 0) formatted = "+" + cleaned.slice(0, 1);
    if (cleaned.length > 1) formatted += " " + cleaned.slice(1, 4);
    if (cleaned.length > 4) formatted += " " + cleaned.slice(4, 7);
    if (cleaned.length > 7) formatted += " " + cleaned.slice(7, 11);

    return formatted;
  };

  const handlePhoneChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const formatted = formatPhoneInput(e.target.value);
    setClientPhone(formatted);
    if (phoneError) validatePhone(formatted);
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!selectedMaster || !selectedSlot || !selectedService) return;

    if (!validatePhone(clientPhone)) return;

    setLoading(true);
    setError("");

    try {
      const booking = await createBooking({
        master_id: selectedMaster!.id,
        service_id: selectedService!.id,
        start_time: selectedSlot!.start_time,
        client_name: clientName,
        client_phone: clientPhone.replace(/\D/g, ""),
      });
      setCreatedBooking(booking);

      const paymentData = await getPaymentLink(booking.id);
      setPayment(paymentData);
      setStep("payment");
    } catch (err: unknown) {
      const error = err as Error;
      setError(error.message || "Ошибка при создании записи");
    } finally {
      setLoading(false);
    }
  };

  const goBack = () => {
    const idx = STEPS.indexOf(step);
    if (idx > 0) {
      setStep(STEPS[idx - 1]);
    }
  };

  const formatDate = (dateStr: string) => {
    const [year, month, day] = dateStr.split("-").map(Number);
    const date = new Date(year, month - 1, day);
    const days = ["Вс", "Пн", "Вт", "Ср", "Чт", "Пт", "Сб"];
    const months = [
      "янв",
      "фев",
      "мар",
      "апр",
      "май",
      "июн",
      "июл",
      "авг",
      "сен",
      "окт",
      "ноя",
      "дек",
    ];
    const today = new Date();
    const isToday =
      today.getFullYear() === date.getFullYear() &&
      today.getMonth() === date.getMonth() &&
      today.getDate() === date.getDate();
    return isToday
      ? `Сегодня, ${date.getDate()} ${months[date.getMonth()]}`
      : `${days[date.getDay()]}, ${date.getDate()} ${months[date.getMonth()]}`;
  };

  const formatTime = (dateTimeStr: string) => {
    return dateTimeStr.split("T")[1].substring(0, 5);
  };

  return (
    <>
    <AnimatePresence>
      <motion.div
        className="fixed inset-0 z-50 flex items-end justify-center sm:items-center"
        variants={backdropVariants}
        initial="hidden"
        animate="visible"
        exit="hidden"
      >
        {/* Backdrop */}
        <motion.div
          className="absolute inset-0 bg-graphite/60 backdrop-blur-sm"
          onClick={onClose}
          aria-hidden="true"
        />

        {/* Drawer */}
        <motion.div
          className="relative w-full max-w-lg max-h-[90vh] bg-bone/95 backdrop-blur-xl rounded-t-3xl sm:rounded-3xl shadow-2xl overflow-hidden border border-light-gray/80"
          role="dialog"
          aria-modal="true"
          aria-labelledby="booking-drawer-title"
          variants={drawerVariants}
          initial="hidden"
          animate="visible"
          exit="exit"
        >
          {/* Header */}
          <div className="relative bg-white text-graphite p-6 border-b border-light-gray/80">
            {/* Salon Info */}
            <div className="flex items-start justify-between">
              <div>
                <div className="flex items-center gap-2 mb-1">
                  <Sparkles className="w-5 h-5 text-graphite/70" />
                  <span className="font-sans text-sm font-medium opacity-80">
                    {salon.name}
                  </span>
                </div>
                <h2 id="booking-drawer-title" className="font-serif text-xl font-bold">
                  {STEP_TITLES[locale][step]}
                </h2>
              </div>
              <button
                ref={closeButtonRef}
                onClick={onClose}
                aria-label={t.closeBookingModal}
                className="w-10 h-10 rounded-full bg-graphite/5 border border-light-gray/70 flex items-center justify-center hover:bg-graphite/10 transition"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            {/* Progress Steps */}
            <div className="flex gap-2 mt-6">
              {STEPS.map((s, i) => (
                <motion.div
                  key={s}
                  className={`h-1.5 flex-1 rounded-full transition-all duration-300 ${
                    i <= currentStepIndex ? "bg-graphite" : "bg-light-gray"
                  }`}
                  initial={{ scaleX: 0 }}
                  animate={{ scaleX: 1 }}
                  transition={{ delay: i * 0.1 }}
                />
              ))}
            </div>

            {/* Step Labels */}
            <div className="flex justify-between mt-2">
              {STEPS.map((s, i) => (
                <span
                  key={s}
                  className={`text-[10px] font-medium transition-opacity ${
                    i <= currentStepIndex ? "opacity-100" : "opacity-40"
                  }`}
                >
                  {i + 1}
                </span>
              ))}
            </div>
          </div>

          {/* Content */}
          <div className="p-6 overflow-y-auto max-h-[60vh]">
            {error && (
              <motion.div
                initial={{ opacity: 0, y: -10 }}
                animate={{ opacity: 1, y: 0 }}
                className="mb-4 p-3 bg-red-50 text-red-600 rounded-xl text-sm"
              >
                {error}
              </motion.div>
            )}

            <AnimatePresence mode="wait">
              {/* Step 1: Select Service */}
              {step === "service" && (
                <motion.div
                  key="service"
                  variants={contentVariants}
                  initial="hidden"
                  animate="visible"
                  exit="exit"
                >
                  {loading ? (
                    <div className="flex items-center justify-center py-12">
                      <Loader2 className="w-8 h-8 animate-spin text-graphite" />
                    </div>
                  ) : services.length > 0 ? (
                    <motion.div
                      className="space-y-3"
                      variants={staggerContainer}
                      initial="hidden"
                      animate="visible"
                    >
                      {services.map((service) => (
                        <motion.button
                          type="button"
                          key={service.id}
                          variants={staggerItem}
                          onClick={() => handleSelectService(service)}
                          aria-label={`Выбрать услугу ${service.name}`}
                          className="bg-white rounded-2xl p-4 cursor-pointer hover:shadow-soft transition-all border border-light-gray/80 hover:border-graphite/30"
                          whileHover={{ scale: 1.02 }}
                          whileTap={{ scale: 0.98 }}
                        >
                          <div className="flex items-center justify-between">
                            <div className="flex-1">
                              <h4 className="font-serif font-semibold text-graphite">
                                {localizeServiceText(service.name, locale)}
                              </h4>
                              {service.description && (
                                <p className="font-sans text-sm text-graphite/60 mt-1">
                                  {localizeServiceText(service.description, locale)}
                                </p>
                              )}
                              <div className="flex items-center gap-4 mt-2">
                                <span className="font-serif text-lg font-bold text-graphite">
                                  {parseInt(service.price).toLocaleString()} ₸
                                </span>
                                <span className="flex items-center gap-1 text-graphite/50 text-sm">
                                  <Clock className="w-4 h-4" />
                                  {service.duration} {locale === "kk" ? "мин" : "мин"}
                                </span>
                              </div>
                            </div>
                            <ArrowRight className="w-5 h-5 text-graphite/50" />
                          </div>
                        </motion.button>
                      ))}
                    </motion.div>
                  ) : (
                    <p className="text-center text-graphite/50 py-12">
                      Нет доступных услуг
                    </p>
                  )}
                </motion.div>
              )}

              {/* Step 2: Select Master */}
              {step === "master" && (
                <motion.div
                  key="master"
                  variants={contentVariants}
                  initial="hidden"
                  animate="visible"
                  exit="exit"
                >
                  <button
                    onClick={goBack}
                    className="flex items-center gap-1 text-sm text-graphite/50 hover:text-graphite mb-4 transition"
                  >
                    <ChevronLeft className="w-4 h-4" />
                    {t.backServices}
                  </button>

                  {/* Selected Service Summary */}
                  {selectedService && (
                    <div className="bg-graphite/5 rounded-xl p-3 mb-4">
                      <p className="font-sans text-sm text-graphite/70">
                        <span className="font-semibold">
                          {localizeServiceText(selectedService.name, locale)}
                        </span>
                        {" · "}
                        {parseInt(selectedService.price).toLocaleString()} ₸
                      </p>
                    </div>
                  )}

                  {loading ? (
                    <div className="flex items-center justify-center py-12">
                      <Loader2 className="w-8 h-8 animate-spin text-graphite" />
                    </div>
                  ) : masters.length > 0 ? (
                    <motion.div
                      className="space-y-3"
                      variants={staggerContainer}
                      initial="hidden"
                      animate="visible"
                    >
                      {masters.map((master) => (
                        <motion.div
                          key={master.id}
                          variants={staggerItem}
                          className="bg-white rounded-2xl p-4 border border-light-gray/80 hover:border-graphite/30 hover:shadow-soft transition-all"
                        >
                          <button
                            type="button"
                            onClick={() => handleSelectMaster(master)}
                            aria-label={`${master.name}`}
                            className="w-full text-left"
                          >
                            <div className="flex items-center gap-4">
                              <div className="w-14 h-14 rounded-full bg-graphite/10 flex items-center justify-center flex-shrink-0">
                                <span className="font-serif text-lg font-bold text-graphite/80">
                                  {master.name.charAt(0)}
                                </span>
                              </div>
                              <div className="flex-1 min-w-0">
                                <h4 className="font-serif font-semibold text-graphite">
                                  {master.name}
                                </h4>
                                {master.specialization && (
                                  <p className="font-sans text-sm text-graphite/75">
                                    {master.specialization}
                                  </p>
                                )}
                                {master.bio && (
                                  <p className="font-sans text-xs text-graphite/50 mt-1 line-clamp-1">
                                    {master.bio}
                                  </p>
                                )}
                              </div>
                              <div className="flex items-center gap-1 flex-shrink-0">
                                <Star className="w-4 h-4 text-graphite fill-graphite" />
                                <span className="font-sans text-sm font-medium">5.0</span>
                              </div>
                            </div>
                          </button>
                          <button
                            type="button"
                            onClick={() => setPortfolioMaster(master)}
                            className="mt-3 font-sans text-sm text-graphite underline underline-offset-2"
                          >
                            {t.portfolio}
                          </button>
                        </motion.div>
                      ))}
                    </motion.div>
                  ) : (
                    <p className="text-center text-graphite/50 py-12">
                      Нет доступных мастеров для этой услуги
                    </p>
                  )}
                </motion.div>
              )}

              {/* Step 3: Select Date & Time */}
              {step === "datetime" && (
                <motion.div
                  key="datetime"
                  variants={contentVariants}
                  initial="hidden"
                  animate="visible"
                  exit="exit"
                >
                  <button
                    onClick={goBack}
                    className="flex items-center gap-1 text-sm text-graphite/50 hover:text-graphite mb-4 transition"
                  >
                    <ChevronLeft className="w-4 h-4" />
                    {t.backMasters}
                  </button>

                  {/* Summary */}
                  <div className="bg-graphite/5 rounded-xl p-3 mb-4">
                    <p className="font-sans text-sm text-graphite/70">
                      <span className="font-semibold">
                        {selectedService
                          ? localizeServiceText(selectedService.name, locale)
                          : ""}
                      </span>
                      {" · "}
                      {selectedMaster?.name}
                    </p>
                  </div>

                  <h4 className="font-serif font-semibold text-graphite mb-3 flex items-center gap-2">
                    <Calendar className="w-5 h-5 text-graphite" />
                    {t.pickDate}
                  </h4>
                  <CalendarPicker
                    month={calendarMonth}
                    onMonthChange={(m) => {
                      setCalendarMonth(m);
                      setSelectedDate("");
                      setSelectedSlot(null);
                    }}
                    availableDates={availableDateSet}
                    selectedDate={selectedDate}
                    onSelectDate={(d) => {
                      setSelectedDate(d);
                      setSelectedSlot(null);
                    }}
                    locale={locale}
                    loading={datesLoading}
                  />

                  {/* Time Selection */}
                  {selectedDate && (
                    <>
                      <h4 className="font-serif font-semibold text-graphite mb-3 mt-6 flex items-center gap-2">
                        <Clock className="w-5 h-5 text-graphite" />
                        {t.pickTime}
                      </h4>
                      {loading ? (
                        <div className="flex items-center justify-center py-8">
                          <Loader2 className="w-8 h-8 animate-spin text-graphite" />
                        </div>
                      ) : slots.length > 0 ? (
                        <motion.div
                          className="grid grid-cols-4 gap-2"
                          variants={staggerContainer}
                          initial="hidden"
                          animate="visible"
                        >
                          {slots.map((slot) => (
                            <motion.button
                              key={slot.start_time}
                              variants={staggerItem}
                              onClick={() => handleSelectSlot(slot)}
                              className="px-3 py-2.5 rounded-xl text-sm font-medium bg-white text-graphite/80 hover:bg-graphite hover:text-bone transition shadow-sm border border-light-gray/70"
                              whileHover={{ scale: 1.05 }}
                              whileTap={{ scale: 0.95 }}
                            >
                              {formatTime(slot.start_time)}
                            </motion.button>
                          ))}
                        </motion.div>
                      ) : (
                        <p className="text-center text-graphite/50 py-8">{t.noSlots}</p>
                      )}
                    </>
                  )}
                </motion.div>
              )}

              {/* Step 4: Client Form */}
              {step === "form" && (
                <motion.div
                  key="form"
                  variants={contentVariants}
                  initial="hidden"
                  animate="visible"
                  exit="exit"
                >
                  <button
                    onClick={goBack}
                    className="flex items-center gap-1 text-sm text-graphite/50 hover:text-graphite mb-4 transition"
                  >
                    <ChevronLeft className="w-4 h-4" />
                    {t.backTime}
                  </button>

                  {/* Booking Summary */}
                  <div className="bg-graphite/5 rounded-xl p-4 mb-6">
                    <h4 className="font-serif font-semibold text-graphite mb-2">
                      {t.yourBooking}
                    </h4>
                    <div className="space-y-1 font-sans text-sm text-graphite/70">
                      <p>
                        <span className="text-graphite/50">{t.service}:</span>{" "}
                        {selectedService && localizeServiceText(selectedService.name, locale)}
                      </p>
                      <p>
                        <span className="text-graphite/50">{t.master}:</span>{" "}
                        {selectedMaster?.name}
                      </p>
                      <p>
                        <span className="text-graphite/50">{t.date}:</span>{" "}
                        {selectedDate && formatDate(selectedDate)}
                      </p>
                      <p>
                        <span className="text-graphite/50">{t.time}:</span>{" "}
                        {selectedSlot && formatTime(selectedSlot.start_time)}
                      </p>
                      <p className="flex items-center gap-1.5">
                        <Clock className="w-4 h-4 text-graphite/45" />
                        <span className="text-graphite/50">{t.duration}:</span>{" "}
                        {selectedService?.duration}{" "}
                        {locale === "kk" ? "мин" : "мин"}
                      </p>
                      <p className="pt-2 border-t border-light-gray mt-2">
                        <span className="text-graphite/50">{t.price}:</span>{" "}
                        <span className="font-bold text-graphite">
                          {selectedService &&
                            parseInt(selectedService.price, 10).toLocaleString()}{" "}
                          ₸
                        </span>
                      </p>
                    </div>
                  </div>

                  <form onSubmit={handleSubmit} className="space-y-4">
                    <div>
                      <label className="block font-sans text-sm font-medium text-graphite mb-2">
                        <User className="w-4 h-4 inline mr-1.5 text-graphite" />
                        {t.name}
                      </label>
                      <input
                        type="text"
                        value={clientName}
                        onChange={(e) => setClientName(e.target.value)}
                        required
                        placeholder={t.namePh}
                        className="w-full px-4 py-3 rounded-xl border border-light-gray bg-white focus:border-graphite focus:ring-0 outline-none transition font-sans"
                      />
                    </div>

                    <div>
                      <label className="block font-sans text-sm font-medium text-graphite mb-2">
                        <Phone className="w-4 h-4 inline mr-1.5 text-graphite" />
                        {t.phone}
                      </label>
                      <input
                        type="tel"
                        value={clientPhone}
                        onChange={handlePhoneChange}
                        required
                        placeholder="+7 777 123 4567"
                        className={`w-full px-4 py-3 rounded-xl border-2 bg-white focus:ring-0 outline-none transition font-sans ${
                          phoneError
                            ? "border-red-400 focus:border-red-500"
                            : "border-light-gray focus:border-graphite"
                        }`}
                      />
                      {phoneError && (
                        <p className="mt-1 text-sm text-red-500">{phoneError}</p>
                      )}
                    </div>

                    <motion.button
                      type="submit"
                      disabled={loading}
                      className="w-full py-4 bg-graphite text-bone font-serif font-bold rounded-xl hover:bg-black transition disabled:opacity-50 flex items-center justify-center gap-2 shadow-soft"
                      whileHover={{ scale: 1.02 }}
                      whileTap={{ scale: 0.98 }}
                    >
                      {loading ? (
                        <>
                          <Loader2 className="w-5 h-5 animate-spin" />
                          {t.creating}
                        </>
                      ) : (
                        <>
                          <CreditCard className="w-5 h-5" />
                          {t.toPay}
                        </>
                      )}
                    </motion.button>
                  </form>
                </motion.div>
              )}

              {/* Step 5: Payment */}
              {step === "payment" && payment && (
                <motion.div
                  key="payment"
                  variants={contentVariants}
                  initial="hidden"
                  animate="visible"
                  exit="exit"
                  className="text-center"
                >
                  {/* Success Icon */}
                  <motion.div
                    initial={{ scale: 0 }}
                    animate={{ scale: 1 }}
                    transition={{ type: "spring", delay: 0.2 }}
                    className="w-20 h-20 bg-green-100 rounded-full flex items-center justify-center mx-auto mb-4"
                  >
                    <CheckCircle className="w-10 h-10 text-green-500" />
                  </motion.div>

                  <h3 className="font-serif text-2xl font-bold text-graphite mb-2">
                    {t.bookingCreated}
                  </h3>
                  <p className="font-sans text-graphite/60 mb-2">{t.payWithKaspi}</p>
                  <p className="font-sans text-sm text-graphite/55 mb-4">{t.whatsappNote}</p>

                  <div className="text-left bg-graphite/5 rounded-xl p-4 mb-6 font-sans text-sm text-graphite/80 space-y-1">
                    <p>
                      <span className="text-graphite/50">{t.salon}:</span> {salon.name}
                    </p>
                    {salon.address && (
                      <p>
                        <span className="text-graphite/50">{t.address}:</span> {salon.address}
                      </p>
                    )}
                    <p>
                      <span className="text-graphite/50">{t.master}:</span> {selectedMaster?.name}
                    </p>
                    <p>
                      <span className="text-graphite/50">{t.service}:</span>{" "}
                      {selectedService && localizeServiceText(selectedService.name, locale)}
                    </p>
                    <p>
                      <span className="text-graphite/50">{t.date}:</span>{" "}
                      {selectedDate && formatDate(selectedDate)}
                    </p>
                    <p>
                      <span className="text-graphite/50">{t.time}:</span>{" "}
                      {selectedSlot && formatTime(selectedSlot.start_time)}
                    </p>
                    <p className="font-semibold text-graphite pt-1">
                      {t.price}: {parseInt(payment.amount, 10).toLocaleString()} ₸
                    </p>
                    {createdBooking && (
                      <p className="text-xs text-graphite/45">#{createdBooking.id}</p>
                    )}
                  </div>

                  {/* QR Code */}
                  {payment.qr_code_base64 && (
                    <motion.div
                      initial={{ opacity: 0, scale: 0.9 }}
                      animate={{ opacity: 1, scale: 1 }}
                      transition={{ delay: 0.3 }}
                      className="bg-white rounded-2xl p-6 mb-6 inline-block shadow-soft"
                    >
                      <img
                        src={`data:image/png;base64,${payment.qr_code_base64}`}
                        alt="QR код для оплаты через Kaspi"
                        className="w-48 h-48 mx-auto"
                      />
                    </motion.div>
                  )}

                  {/* Amount */}
                  <div className="bg-graphite/5 rounded-xl p-4 mb-6">
                    <p className="font-serif text-3xl font-bold text-graphite">
                      {parseInt(payment.amount).toLocaleString()} ₸
                    </p>
                    <p className="font-sans text-sm text-graphite/50 mt-1">{t.afterPay}</p>
                  </div>

                  {/* Kaspi Button */}
                  <motion.a
                    href={payment.kaspi_link}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="inline-flex items-center gap-2 px-6 py-3 bg-[#F14635] text-white font-semibold rounded-xl hover:bg-[#d93d2e] transition shadow-soft"
                    whileHover={{ scale: 1.02 }}
                    whileTap={{ scale: 0.98 }}
                  >
                    <ExternalLink className="w-5 h-5" />
                    {t.openKaspi}
                  </motion.a>

                  {onOpenMyBookings && (
                    <button
                      type="button"
                      onClick={() => {
                        onClose();
                        onOpenMyBookings();
                      }}
                      className="block w-full mt-4 font-sans text-sm font-medium text-graphite underline"
                    >
                      {t.myBookings}
                    </button>
                  )}

                  {/* Close Button */}
                  <button
                    onClick={onClose}
                    className="block w-full mt-6 font-sans text-graphite/50 hover:text-graphite transition"
                  >
                    {t.close}
                  </button>
                </motion.div>
              )}
            </AnimatePresence>
          </div>
        </motion.div>
      </motion.div>
    </AnimatePresence>

    {portfolioMaster && (
      <MasterPortfolioModal
        master={portfolioMaster}
        isOpen
        onClose={() => setPortfolioMaster(null)}
        locale={locale}
      />
    )}
    </>
  );
}
