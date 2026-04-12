"use client";

import { useEffect, useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import {
  X,
  MapPin,
  Clock,
  Phone,
  Star,
  Loader2,
  Navigation,
  Sparkles,
} from "lucide-react";
import type { Locale } from "@/lib/i18n";
import type { Salon, SalonGalleryPhoto, Service, Master } from "@/lib/api";
import {
  getSalonGallery,
  getSalonServices,
  getSalonMasters,
} from "@/lib/api";

interface SalonDetailProps {
  salon: Salon;
  onClose: () => void;
  onBooking: () => void;
  locale: Locale;
}

export default function SalonDetail({ salon, onClose, onBooking, locale }: SalonDetailProps) {
  const [gallery, setGallery] = useState<SalonGalleryPhoto[]>([]);
  const [services, setServices] = useState<Service[]>([]);
  const [masters, setMasters] = useState<Master[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [showAllServices, setShowAllServices] = useState(false);

  const loadErrorMsg =
    locale === "kk"
      ? "Деректерді жүктеу сәтсіз"
      : "Не удалось загрузить данные";

  const t =
    locale === "kk"
      ? {
          close: "Жабу",
          route: "Маршрут көрсету",
          services: "Қызметтер",
          masters: "Мастерлер",
          showAll: "Барлығын көру",
          book: "Жазылу",
          noGallery: "Галереяда фото жоқ",
        }
      : {
          close: "Закрыть",
          route: "Маршрут",
          services: "Услуги",
          masters: "Мастера",
          showAll: "Показать все",
          book: "Записаться",
          noGallery: "Нет фото в галерее",
        };

  useEffect(() => {
    let cancelled = false;
    async function load() {
      setLoading(true);
      setError("");
      try {
        const [g, s, m] = await Promise.all([
          getSalonGallery(salon.id).catch(() => [] as SalonGalleryPhoto[]),
          getSalonServices(salon.id),
          getSalonMasters(salon.id),
        ]);
        if (!cancelled) {
          setGallery(g);
          setServices(s);
          setMasters(m);
        }
      } catch {
        if (!cancelled) setError(loadErrorMsg);
      } finally {
        if (!cancelled) setLoading(false);
      }
    }
    load();
    return () => {
      cancelled = true;
    };
  }, [salon.id, loadErrorMsg]);

  useEffect(() => {
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
  }, [onClose]);

  const routeUrl = salon.address
    ? `https://2gis.kz/almaty/search/${encodeURIComponent(salon.address)}`
    : null;

  const displayGallery =
    gallery.length > 0
      ? gallery
      : salon.image_url
        ? [
            {
              id: 0,
              salon_id: salon.id,
              image_url: salon.image_url,
              caption: null,
              sort_order: 0,
              created_at: "",
            } as SalonGalleryPhoto,
          ]
        : [];

  const visibleServices = showAllServices ? services : services.slice(0, 6);

  const renderStars = (rating: number) => {
    const full = Math.floor(rating);
    const half = rating % 1 >= 0.5;
    const empty = 5 - full - (half ? 1 : 0);
    return (
      <div className="flex items-center gap-0.5">
        {[...Array(full)].map((_, i) => (
          <Star key={`f-${i}`} className="w-4 h-4 fill-graphite text-graphite" />
        ))}
        {half && <Star className="w-4 h-4 fill-graphite/50 text-graphite" />}
        {[...Array(empty)].map((_, i) => (
          <Star key={`e-${i}`} className="w-4 h-4 text-graphite/25" />
        ))}
      </div>
    );
  };

  return (
    <AnimatePresence>
      <motion.div
        className="fixed inset-0 z-[55] flex items-end justify-center sm:items-center"
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        exit={{ opacity: 0 }}
      >
        <motion.div
          className="absolute inset-0 bg-graphite/60 backdrop-blur-sm"
          onClick={onClose}
          aria-hidden="true"
        />
        <motion.div
          role="dialog"
          aria-modal="true"
          className="relative w-full max-w-lg max-h-[92vh] bg-bone rounded-t-3xl sm:rounded-3xl shadow-2xl border border-light-gray flex flex-col overflow-hidden"
          initial={{ y: "100%", opacity: 0 }}
          animate={{ y: 0, opacity: 1 }}
          exit={{ y: "100%", opacity: 0 }}
          transition={{ type: "spring", damping: 30, stiffness: 300 }}
        >
          <div className="flex items-center justify-between p-4 border-b border-light-gray bg-white">
            <div className="flex items-center gap-2">
              <Sparkles className="w-5 h-5 text-graphite/70" />
              <span className="font-sans text-sm font-medium text-graphite/80">{salon.name}</span>
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

          <div className="overflow-y-auto flex-1 pb-28">
            {loading ? (
              <div className="flex justify-center py-20">
                <Loader2 className="w-10 h-10 animate-spin text-graphite" />
              </div>
            ) : error ? (
              <p className="text-center text-red-600 p-8 text-sm">{error}</p>
            ) : (
              <>
                {/* Gallery */}
                <div className="px-4 pt-4">
                  {displayGallery.length > 0 ? (
                    <div className="flex gap-3 overflow-x-auto snap-x snap-mandatory pb-2 -mx-1 px-1">
                      {displayGallery.map((item) => (
                        <div
                          key={item.id}
                          className="snap-center flex-shrink-0 w-[85%] sm:w-[60%] rounded-2xl overflow-hidden border border-light-gray aspect-[16/9] bg-graphite/5"
                        >
                          {/* eslint-disable-next-line @next/next/no-img-element */}
                          <img
                            src={item.image_url}
                            alt=""
                            className="w-full h-full object-cover"
                          />
                        </div>
                      ))}
                    </div>
                  ) : (
                    <p className="text-center text-graphite/45 text-sm py-6">{t.noGallery}</p>
                  )}
                  {gallery[0]?.caption && (
                    <p className="font-sans text-sm text-graphite/60 mt-2 px-1">{gallery[0].caption}</p>
                  )}
                </div>

                <div className="px-6 pt-6 space-y-6">
                  <div>
                    <h1 className="heading-lg text-graphite">{salon.name}</h1>
                    <div className="flex items-center gap-3 mt-2">
                      {renderStars(Number(salon.rating))}
                      <span className="font-sans text-sm font-semibold">{salon.rating}</span>
                    </div>
                    {salon.instagram && (
                      <span className="inline-block mt-2 font-sans text-xs text-graphite/70 bg-graphite/5 px-3 py-1 rounded-full border border-black/5">
                        {salon.instagram}
                      </span>
                    )}
                    {salon.description && (
                      <p className="body-md text-graphite/70 mt-4">{salon.description}</p>
                    )}
                  </div>

                  <div className="card p-4 space-y-3">
                    {salon.address && (
                      <div className="flex gap-3">
                        <MapPin className="w-5 h-5 text-graphite/50 flex-shrink-0 mt-0.5" />
                        <p className="font-sans text-sm text-graphite/80">{salon.address}</p>
                      </div>
                    )}
                    {salon.working_hours && (
                      <div className="flex gap-3">
                        <Clock className="w-5 h-5 text-graphite/50 flex-shrink-0 mt-0.5" />
                        <p className="font-sans text-sm text-graphite/80">{salon.working_hours}</p>
                      </div>
                    )}
                    {salon.phone && (
                      <div className="flex gap-3">
                        <Phone className="w-5 h-5 text-graphite/50 flex-shrink-0 mt-0.5" />
                        <a href={`tel:${salon.phone}`} className="font-sans text-sm text-graphite underline">
                          {salon.phone}
                        </a>
                      </div>
                    )}
                    {routeUrl && (
                      <a
                        href={routeUrl}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="btn-secondary w-full justify-center mt-2"
                      >
                        <Navigation className="w-4 h-4" />
                        {t.route}
                      </a>
                    )}
                  </div>

                  <div>
                    <h2 className="font-serif text-lg font-semibold mb-3">{t.services}</h2>
                    <div className="space-y-2">
                      {visibleServices.map((s) => (
                        <div
                          key={s.id}
                          className="flex justify-between items-center rounded-xl border border-light-gray bg-white px-3 py-2.5"
                        >
                          <span className="font-sans text-sm text-graphite">{s.name}</span>
                          <span className="font-sans text-sm font-semibold text-graphite">
                            {parseInt(s.price, 10).toLocaleString()} ₸ · {s.duration}{" "}
                            {locale === "kk" ? "мин" : "мин"}
                          </span>
                        </div>
                      ))}
                    </div>
                    {services.length > 6 && (
                      <button
                        type="button"
                        onClick={() => setShowAllServices(!showAllServices)}
                        className="mt-3 font-sans text-sm text-graphite underline"
                      >
                        {t.showAll}
                      </button>
                    )}
                  </div>

                  <div>
                    <h2 className="font-serif text-lg font-semibold mb-3">{t.masters}</h2>
                    <div className="flex gap-3 overflow-x-auto pb-2 -mx-1 px-1">
                      {masters.map((m) => (
                        <div
                          key={m.id}
                          className="flex-shrink-0 w-36 rounded-2xl border border-light-gray bg-white p-3 text-center"
                        >
                          <div className="w-12 h-12 rounded-full bg-graphite/10 mx-auto flex items-center justify-center font-serif font-bold text-graphite">
                            {m.name.charAt(0)}
                          </div>
                          <p className="font-sans text-sm font-medium text-graphite mt-2 line-clamp-2">
                            {m.name}
                          </p>
                          {m.specialization && (
                            <p className="font-sans text-xs text-graphite/55 line-clamp-2 mt-0.5">
                              {m.specialization}
                            </p>
                          )}
                        </div>
                      ))}
                    </div>
                  </div>
                </div>
              </>
            )}
          </div>

          <div className="absolute bottom-0 left-0 right-0 p-4 bg-bone/95 backdrop-blur-md border-t border-light-gray">
            <button type="button" onClick={onBooking} className="btn-primary w-full justify-center">
              <Sparkles className="w-4 h-4" />
              {t.book}
            </button>
          </div>
        </motion.div>
      </motion.div>
    </AnimatePresence>
  );
}
