"use client";

import { useCallback, useEffect, useRef, useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import {
  X,
  Loader2,
  RefreshCw,
  User,
  Calendar as CalendarIcon,
} from "lucide-react";
import { format, parseISO } from "date-fns";
import { kk as kkLocale, ru } from "date-fns/locale";
import type { Locale } from "@/lib/i18n";
import type { BookingDetailResponse } from "@/lib/api";
import {
  sendOTPCode,
  verifyOTPCode,
  getMyBookings,
  cancelMyBooking,
} from "@/lib/api";
import { formatPhoneInput, phoneToApiDigits, isPhoneCompleteForKz } from "@/lib/phone";

type Phase = "phone" | "otp" | "list";

interface MyBookingsModalProps {
  isOpen: boolean;
  onClose: () => void;
  locale: Locale;
  onOpenBooking?: () => void;
}

export default function MyBookingsModal({
  isOpen,
  onClose,
  locale,
  onOpenBooking,
}: MyBookingsModalProps) {
  const [phase, setPhase] = useState<Phase>("phone");
  const [phone, setPhone] = useState("");
  const [phoneError, setPhoneError] = useState("");
  const [otp, setOtp] = useState(["", "", "", ""]);
  const otpRefs = useRef<(HTMLInputElement | null)[]>([]);
  const [token, setToken] = useState<string | null>(null);
  const [bookings, setBookings] = useState<BookingDetailResponse[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [tab, setTab] = useState<"upcoming" | "past">("upcoming");
  const [resendSec, setResendSec] = useState(0);
  const [confirmId, setConfirmId] = useState<number | null>(null);

  const loc = locale === "kk" ? kkLocale : ru;

  const t =
    locale === "kk"
      ? {
          title: "Менің жазылуларым",
          phoneDesc:
            "Телефон нөміріңізді енгізіңіз. WhatsApp-қа растау коды жіберіледі.",
          sendCode: "Код жіберу",
          otpDesc: "Кодты енгізіңіз",
          resend: "Қайта жіберу",
          resendIn: "сек кейін",
          listTitle: "Сіздің жазылуларыңыз",
          upcoming: "Алдағы",
          past: "Өткен",
          refresh: "Жаңарту",
          empty: "Жазылулар табылмады",
          book: "Жазылу",
          myBookingsLink: "Менің жазылуларым",
          cancel: "Бас тарту",
          confirmCancel: "Жазылудан бас тарту керек пе?",
          close: "Жабу",
          master: "Мастер",
          sum: "Сома",
          rateLimit: "Кодты 1 минуттан кейін қайта сұраңыз",
          wrongCode: "Қате код немесе мерзімі өтті",
          loadErr: "Жүктеу қатесі",
        }
      : {
          title: "Мои записи",
          phoneDesc: "Введите номер телефона. Код подтверждения придёт в WhatsApp.",
          sendCode: "Отправить код",
          otpDesc: "Введите код",
          resend: "Отправить снова",
          resendIn: "через",
          listTitle: "Ваши записи",
          upcoming: "Предстоящие",
          past: "Прошедшие",
          refresh: "Обновить",
          empty: "Записи не найдены",
          book: "Записаться",
          myBookingsLink: "Мои записи",
          cancel: "Отменить",
          confirmCancel: "Отменить запись?",
          close: "Закрыть",
          master: "Мастер",
          sum: "Сумма",
          rateLimit: "Запросите код снова через минуту",
          wrongCode: "Неверный код или срок истёк",
          loadErr: "Ошибка загрузки",
        };

  const reset = useCallback(() => {
    setPhase("phone");
    setPhone("");
    setPhoneError("");
    setOtp(["", "", "", ""]);
    setToken(null);
    setBookings([]);
    setError("");
    setTab("upcoming");
    setResendSec(0);
    setConfirmId(null);
  }, []);

  useEffect(() => {
    if (!isOpen) reset();
  }, [isOpen, reset]);

  useEffect(() => {
    if (resendSec <= 0) return;
    const id = window.setInterval(() => setResendSec((s) => Math.max(0, s - 1)), 1000);
    return () => window.clearInterval(id);
  }, [resendSec]);

  useEffect(() => {
    if (!isOpen) return;
    const onKey = (e: KeyboardEvent) => {
      if (e.key === "Escape") onClose();
    };
    document.addEventListener("keydown", onKey);
    const prev = document.body.style.overflow;
    document.body.style.overflow = "hidden";
    return () => {
      document.removeEventListener("keydown", onKey);
      document.body.style.overflow = prev;
    };
  }, [isOpen, onClose]);

  const handleSendCode = async () => {
    setError("");
    if (!isPhoneCompleteForKz(phone)) {
      setPhoneError(locale === "kk" ? "Толық нөмірді енгізіңіз" : "Введите полный номер");
      return;
    }
    setPhoneError("");
    setLoading(true);
    try {
      const digits = phoneToApiDigits(phone);
      await sendOTPCode(digits);
      setPhase("otp");
      setResendSec(60);
      setOtp(["", "", "", ""]);
      otpRefs.current[0]?.focus();
    } catch (e) {
      const msg = e instanceof Error ? e.message : "";
      setError(msg.includes("минут") || msg.toLowerCase().includes("подожд") ? t.rateLimit : msg);
    } finally {
      setLoading(false);
    }
  };

  const verifyAndLoad = async (code: string) => {
    if (code.length < 4) return;
    setLoading(true);
    setError("");
    try {
      const digits = phoneToApiDigits(phone);
      const res = await verifyOTPCode(digits, code);
      setToken(res.token);
      setBookings(res.bookings);
      setPhase("list");
    } catch {
      setError(t.wrongCode);
      setOtp(["", "", "", ""]);
      otpRefs.current[0]?.focus();
    } finally {
      setLoading(false);
    }
  };

  const handleOtpChange = (i: number, val: string) => {
    const d = val.replace(/\D/g, "").slice(-1);
    const next = [...otp];
    next[i] = d;
    setOtp(next);
    if (d && i < 3) otpRefs.current[i + 1]?.focus();
    const joined = next.join("");
    if (joined.length === 4) verifyAndLoad(joined);
  };

  const handleOtpKeyDown = (i: number, e: React.KeyboardEvent) => {
    if (e.key === "Backspace" && !otp[i] && i > 0) otpRefs.current[i - 1]?.focus();
  };

  const refreshList = async () => {
    if (!token) return;
    setLoading(true);
    setError("");
    try {
      const data = await getMyBookings(token);
      setBookings(data);
    } catch {
      setError(t.loadErr);
    } finally {
      setLoading(false);
    }
  };

  const handleCancel = async (id: number) => {
    if (!token) return;
    setLoading(true);
    setError("");
    try {
      await cancelMyBooking(id, token);
      await refreshList();
      setConfirmId(null);
    } catch (e) {
      setError(e instanceof Error ? e.message : t.loadErr);
    } finally {
      setLoading(false);
    }
  };

  const statusBadge = (status: string) => {
    const s = status.toLowerCase();
    const styles: Record<string, string> = {
      pending: "bg-amber-100 text-amber-900",
      confirmed: "bg-blue-100 text-blue-900",
      paid: "bg-green-100 text-green-900",
      completed: "bg-graphite/10 text-graphite",
      cancelled: "bg-red-100 text-red-800",
    };
    const labelsKk: Record<string, string> = {
      pending: "Күтуде",
      confirmed: "Расталды",
      paid: "Төленді",
      completed: "Аяқталды",
      cancelled: "Бас тартылды",
    };
    const labelsRu: Record<string, string> = {
      pending: "Ожидает",
      confirmed: "Подтверждено",
      paid: "Оплачено",
      completed: "Завершено",
      cancelled: "Отменено",
    };
    const labels = locale === "kk" ? labelsKk : labelsRu;
    return (
      <span
        className={`inline-block px-2 py-0.5 rounded-full text-xs font-medium ${styles[s] || "bg-graphite/10"}`}
      >
        {labels[s] || status}
      </span>
    );
  };

  const filterAndSort = (list: BookingDetailResponse[]) => {
    const upcoming = list.filter((b) =>
      ["pending", "confirmed", "paid"].includes(b.status.toLowerCase())
    );
    const past = list.filter((b) =>
      ["completed", "cancelled"].includes(b.status.toLowerCase())
    );
    upcoming.sort((a, b) => parseISO(a.start_time).getTime() - parseISO(b.start_time).getTime());
    past.sort((a, b) => parseISO(b.start_time).getTime() - parseISO(a.start_time).getTime());
    return { upcoming, past };
  };

  const { upcoming, past } = filterAndSort(bookings);
  const shown = tab === "upcoming" ? upcoming : past;

  if (!isOpen) return null;

  return (
    <AnimatePresence>
      <motion.div
        className="fixed inset-0 z-[65] flex items-center justify-center p-4"
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        exit={{ opacity: 0 }}
      >
        <motion.div className="absolute inset-0 bg-black/45" onClick={onClose} aria-hidden />
        <motion.div
          role="dialog"
          aria-modal="true"
          className="relative w-full max-w-lg max-h-[90vh] overflow-hidden flex flex-col bg-white rounded-3xl shadow-2xl border border-light-gray"
          initial={{ scale: 0.96, opacity: 0 }}
          animate={{ scale: 1, opacity: 1 }}
          exit={{ scale: 0.96, opacity: 0 }}
        >
          <div className="flex items-center justify-between p-5 border-b border-light-gray">
            <div className="flex items-center gap-2">
              <User className="w-5 h-5 text-graphite" />
              <h2 className="font-serif text-xl font-bold">{t.title}</h2>
            </div>
            <button
              type="button"
              onClick={onClose}
              className="w-10 h-10 rounded-full bg-graphite/5 border border-light-gray flex items-center justify-center"
              aria-label={t.close}
            >
              <X className="w-5 h-5" />
            </button>
          </div>

          <div className="p-5 overflow-y-auto flex-1">
            {error && (
              <div className="mb-3 p-3 bg-red-50 text-red-600 rounded-xl text-sm">{error}</div>
            )}

            {phase === "phone" && (
              <div className="space-y-4">
                <p className="font-sans text-sm text-graphite/70">{t.phoneDesc}</p>
                <input
                  type="tel"
                  value={phone}
                  onChange={(e) => {
                    setPhone(formatPhoneInput(e.target.value));
                    if (phoneError) setPhoneError("");
                  }}
                  placeholder="+7 777 123 4567"
                  className={`input ${phoneError ? "input-error" : ""}`}
                />
                {phoneError && <p className="text-sm text-red-500">{phoneError}</p>}
                <button
                  type="button"
                  disabled={loading}
                  onClick={handleSendCode}
                  className="btn-primary w-full justify-center"
                >
                  {loading ? <Loader2 className="w-5 h-5 animate-spin" /> : t.sendCode}
                </button>
              </div>
            )}

            {phase === "otp" && (
              <div className="space-y-4">
                <p className="font-sans text-sm text-graphite/70">{t.otpDesc}</p>
                <div className="flex gap-2 justify-center">
                  {otp.map((digit, i) => (
                    <input
                      key={i}
                      ref={(el) => {
                        otpRefs.current[i] = el;
                      }}
                      type="text"
                      inputMode="numeric"
                      maxLength={1}
                      value={digit}
                      onChange={(e) => handleOtpChange(i, e.target.value)}
                      onKeyDown={(e) => handleOtpKeyDown(i, e)}
                      className="w-14 h-14 text-center text-2xl font-bold rounded-xl border-2 border-light-gray focus:border-graphite outline-none"
                    />
                  ))}
                </div>
                <button
                  type="button"
                  disabled={resendSec > 0 || loading}
                  onClick={handleSendCode}
                  className="font-sans text-sm text-graphite underline w-full"
                >
                  {resendSec > 0 ? `${t.resendIn} ${resendSec} с` : t.resend}
                </button>
                {loading && (
                  <div className="flex justify-center">
                    <Loader2 className="w-6 h-6 animate-spin text-graphite" />
                  </div>
                )}
              </div>
            )}

            {phase === "list" && (
              <div className="space-y-4">
                <div className="flex items-center justify-between gap-2">
                  <h3 className="font-serif font-semibold text-lg">
                    {t.listTitle}{" "}
                    <span className="text-graphite/50 font-sans text-sm">({bookings.length})</span>
                  </h3>
                  <button
                    type="button"
                    onClick={refreshList}
                    className="p-2 rounded-full border border-light-gray hover:bg-graphite/5"
                    aria-label={t.refresh}
                  >
                    <RefreshCw className={`w-4 h-4 ${loading ? "animate-spin" : ""}`} />
                  </button>
                </div>

                <div className="flex border-b border-light-gray">
                  <button
                    type="button"
                    onClick={() => setTab("upcoming")}
                    className={`flex-1 py-2 font-sans text-sm font-medium border-b-2 transition ${
                      tab === "upcoming"
                        ? "border-graphite text-graphite"
                        : "border-transparent text-graphite/50"
                    }`}
                  >
                    {t.upcoming}
                  </button>
                  <button
                    type="button"
                    onClick={() => setTab("past")}
                    className={`flex-1 py-2 font-sans text-sm font-medium border-b-2 transition ${
                      tab === "past"
                        ? "border-graphite text-graphite"
                        : "border-transparent text-graphite/50"
                    }`}
                  >
                    {t.past}
                  </button>
                </div>

                {shown.length === 0 ? (
                  <div className="text-center py-8 space-y-3">
                    <p className="text-graphite/50 text-sm">{t.empty}</p>
                    {onOpenBooking && (
                      <button type="button" onClick={onOpenBooking} className="btn-primary">
                        <CalendarIcon className="w-4 h-4" />
                        {t.book}
                      </button>
                    )}
                  </div>
                ) : (
                  <div className="space-y-3">
                    {shown.map((b) => (
                      <div key={b.id} className="card p-4 space-y-2">
                        <div className="flex justify-between items-start gap-2">
                          {statusBadge(b.status)}
                          {["pending", "confirmed"].includes(b.status.toLowerCase()) && (
                            <button
                              type="button"
                              onClick={() => setConfirmId(b.id)}
                              className="text-xs text-red-600 underline"
                            >
                              {t.cancel}
                            </button>
                          )}
                        </div>
                        <p className="font-sans font-semibold text-graphite">{b.service.name}</p>
                        <p className="font-sans text-sm text-graphite/70">
                          {t.master}: {b.master.name}
                          {b.master.specialization ? ` · ${b.master.specialization}` : ""}
                        </p>
                        <p className="font-sans text-sm text-graphite/70">
                          {format(parseISO(b.start_time), "d MMMM, HH:mm", { locale: loc })}
                        </p>
                        <p className="font-sans text-sm font-medium">
                          {t.sum}: {parseInt(String(b.total_price), 10).toLocaleString()} ₸
                        </p>
                      </div>
                    ))}
                  </div>
                )}

                {confirmId !== null && (
                  <div className="fixed inset-0 z-[90] flex items-center justify-center p-4 bg-black/40">
                    <div className="bg-white rounded-2xl p-6 max-w-sm shadow-xl">
                      <p className="font-sans text-sm text-graphite mb-4">{t.confirmCancel}</p>
                      <div className="flex gap-2">
                        <button
                          type="button"
                          onClick={() => setConfirmId(null)}
                          className="btn-secondary flex-1 justify-center"
                        >
                          {locale === "kk" ? "Жоқ" : "Нет"}
                        </button>
                        <button
                          type="button"
                          onClick={() => handleCancel(confirmId)}
                          className="btn-primary flex-1 justify-center bg-red-600 hover:bg-red-700"
                        >
                          {locale === "kk" ? "Иә" : "Да"}
                        </button>
                      </div>
                    </div>
                  </div>
                )}
              </div>
            )}
          </div>
        </motion.div>
      </motion.div>
    </AnimatePresence>
  );
}
