"use client";

import { useEffect, useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { X, Loader2 } from "lucide-react";
import type { Master, MasterPortfolioPhoto } from "@/lib/api";
import { getMasterPortfolio } from "@/lib/api";
import type { Locale } from "@/lib/i18n";

interface MasterPortfolioModalProps {
  master: Master;
  isOpen: boolean;
  onClose: () => void;
  locale: Locale;
}

export default function MasterPortfolioModal({
  master,
  isOpen,
  onClose,
  locale,
}: MasterPortfolioModalProps) {
  const [photos, setPhotos] = useState<MasterPortfolioPhoto[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [lightbox, setLightbox] = useState<MasterPortfolioPhoto | null>(null);

  const loadErrorMsg =
    locale === "kk" ? "Жүктеу сәтсіз аяқталды" : "Не удалось загрузить";

  const t =
    locale === "kk"
      ? {
          title: "Портфолио",
          empty: "Портфолио әлі қосылмаған",
          close: "Жабу",
        }
      : {
          title: "Портфолио",
          empty: "Портфолио ещё не добавлено",
          close: "Закрыть",
        };

  useEffect(() => {
    if (!isOpen) return;
    let cancelled = false;
    async function load() {
      setLoading(true);
      setError("");
      try {
        const data = await getMasterPortfolio(master.id);
        if (!cancelled) setPhotos(data);
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
  }, [isOpen, master.id, loadErrorMsg]);

  useEffect(() => {
    if (!isOpen) return;
    const onKey = (e: KeyboardEvent) => {
      if (e.key === "Escape") {
        if (lightbox) setLightbox(null);
        else onClose();
      }
    };
    document.addEventListener("keydown", onKey);
    return () => document.removeEventListener("keydown", onKey);
  }, [isOpen, lightbox, onClose]);

  if (!isOpen) return null;

  return (
    <AnimatePresence>
      <motion.div
        className="fixed inset-0 z-[70] flex items-end justify-center sm:items-center"
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        exit={{ opacity: 0 }}
      >
        <motion.div
          className="absolute inset-0 bg-graphite/40 backdrop-blur-sm"
          onClick={onClose}
          aria-hidden="true"
        />
        <motion.div
          role="dialog"
          aria-modal="true"
          className="relative z-[1] w-full max-w-lg max-h-[90vh] bg-bone rounded-t-3xl sm:rounded-3xl shadow-2xl border border-light-gray overflow-hidden flex flex-col"
          initial={{ y: "100%", opacity: 0 }}
          animate={{ y: 0, opacity: 1 }}
          exit={{ y: "100%", opacity: 0 }}
          transition={{ type: "spring", damping: 28, stiffness: 320 }}
        >
          <div className="flex items-start justify-between p-5 border-b border-light-gray">
            <div>
              <h2 className="font-serif text-xl font-bold text-graphite">{t.title}</h2>
              <p className="font-sans text-sm text-graphite/65 mt-0.5">{master.name}</p>
              {master.specialization && (
                <p className="font-sans text-xs text-graphite/50">{master.specialization}</p>
              )}
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
            {loading ? (
              <div className="flex justify-center py-16">
                <Loader2 className="w-8 h-8 animate-spin text-graphite" />
              </div>
            ) : error ? (
              <p className="text-center text-red-600 text-sm py-8">{error}</p>
            ) : photos.length === 0 ? (
              <p className="text-center text-graphite/50 py-12 font-sans text-sm">{t.empty}</p>
            ) : (
              <div className="grid grid-cols-2 sm:grid-cols-3 gap-3">
                {photos.map((p) => (
                  <button
                    key={p.id}
                    type="button"
                    onClick={() => setLightbox(p)}
                    className="rounded-xl overflow-hidden border border-light-gray aspect-square bg-graphite/5 focus:outline-none focus-visible:ring-2 focus-visible:ring-graphite"
                  >
                    {/* eslint-disable-next-line @next/next/no-img-element */}
                    <img
                      src={p.image_url}
                      alt=""
                      className="w-full h-full object-cover hover:scale-105 transition-transform duration-300"
                    />
                  </button>
                ))}
              </div>
            )}
          </div>
        </motion.div>

        {lightbox && (
          <motion.div
            className="fixed inset-0 z-[80] bg-black/85 flex flex-col items-center justify-center p-4"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            onClick={() => setLightbox(null)}
          >
            <button
              type="button"
              className="absolute top-4 right-4 text-white p-2"
              onClick={() => setLightbox(null)}
            >
              <X className="w-8 h-8" />
            </button>
            {/* eslint-disable-next-line @next/next/no-img-element */}
            <img
              src={lightbox.image_url}
              alt=""
              className="max-w-full max-h-[80vh] object-contain rounded-lg"
              onClick={(e) => e.stopPropagation()}
            />
            {lightbox.description && (
              <p className="text-white/90 text-sm mt-4 max-w-md text-center">{lightbox.description}</p>
            )}
          </motion.div>
        )}
      </motion.div>
    </AnimatePresence>
  );
}
