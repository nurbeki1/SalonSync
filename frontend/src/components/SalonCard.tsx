"use client";

import { motion } from "framer-motion";
import Image from "next/image";
import { Star, MapPin, Clock, ChevronRight, Sparkles } from "lucide-react";
import type { Salon } from "@/lib/api";
import type { Locale } from "@/lib/i18n";

interface SalonCardProps {
  salon: Salon;
  onSelect: (salon: Salon) => void;
  index: number;
  locale: Locale;
}

export default function SalonCard({ salon, onSelect, index, locale }: SalonCardProps) {
  const t = locale === "kk"
    ? {
        openBooking: "Жазылуды ашу",
        book: "Жазылу",
      }
    : {
        openBooking: "Открыть запись",
        book: "Записаться",
      };
  // Рендерим звёзды рейтинга
  const renderStars = (rating: number) => {
    const fullStars = Math.floor(rating);
    const hasHalfStar = rating % 1 >= 0.5;
    const emptyStars = 5 - fullStars - (hasHalfStar ? 1 : 0);

    return (
      <div className="flex items-center gap-0.5">
        {[...Array(fullStars)].map((_, i) => (
          <Star key={`full-${i}`} className="w-4 h-4 text-graphite fill-graphite" />
        ))}
        {hasHalfStar && (
          <Star className="w-4 h-4 text-graphite fill-graphite/50" />
        )}
        {[...Array(emptyStars)].map((_, i) => (
          <Star key={`empty-${i}`} className="w-4 h-4 text-graphite/25" />
        ))}
      </div>
    );
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 36 }}
      whileInView={{ opacity: 1, y: 0 }}
      viewport={{ once: true }}
      transition={{ duration: 0.55, delay: index * 0.12, ease: "easeOut" }}
      whileHover={{ y: -8 }}
    >
      <motion.button
        type="button"
        onClick={() => onSelect(salon)}
        aria-label={`${t.openBooking} в ${salon.name}`}
        className="relative bg-white rounded-[28px] overflow-hidden border border-black/10 shadow-soft hover:shadow-card transition-all duration-300 cursor-pointer group text-left w-full [transform:translateZ(0)] [backface-visibility:hidden]"
        whileHover={{ scale: 1.01 }}
        transition={{ type: "spring", stiffness: 290, damping: 22 }}
      >
        {/* Image */}
        <div className="relative aspect-[4/3] overflow-hidden rounded-t-[28px] bg-neutral-100">
          {salon.image_url ? (
            <Image
              src={salon.image_url}
              alt={salon.name}
              className="absolute inset-0 w-full h-full object-cover transition-transform duration-500 group-hover:scale-[1.03] [transform:translateZ(0)] [backface-visibility:hidden]"
              fill
              sizes="(max-width: 768px) 100vw, (max-width: 1200px) 50vw, 33vw"
            />
          ) : (
            <div className="absolute inset-0 bg-gradient-to-br from-[#F8F8F8] via-[#F1F1F1] to-[#E8E8E8]">
              <div className="absolute inset-0 flex items-center justify-center">
                <Sparkles className="w-12 h-12 text-graphite/35" />
              </div>
            </div>
          )}

          {/* Rating Badge */}
          <div className="absolute top-4 right-4">
            <motion.div
              initial={{ scale: 0 }}
              animate={{ scale: 1 }}
              transition={{ delay: index * 0.1 + 0.25, type: "spring" }}
              className="bg-white/95 backdrop-blur-sm rounded-full px-3 py-1.5 flex items-center gap-1.5 border border-black/10 shadow-sm"
            >
              <Star className="w-4 h-4 text-graphite fill-graphite" />
              <span className="font-sans text-sm font-semibold text-graphite">
                {salon.rating}
              </span>
            </motion.div>
          </div>

          {/* Gradient Overlay */}
          <div className="absolute inset-0 bg-gradient-to-t from-black/20 via-transparent to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-300" />
          <motion.div
            className="absolute -inset-x-20 top-0 h-16 bg-white/50 blur-xl"
            initial={{ x: "-120%" }}
            whileHover={{ x: "120%" }}
            transition={{ duration: 0.9, ease: "easeInOut" }}
          />
        </div>

        {/* Content */}
        <div className="p-6">
          {/* Name & Instagram */}
          <div className="flex items-start justify-between mb-3">
            <h3 className="font-sans text-xl font-semibold tracking-tight text-graphite transition-colors">
              {salon.name}
            </h3>
            {salon.instagram && (
              <span className="font-sans text-[11px] text-graphite/70 bg-graphite/5 px-2.5 py-1 rounded-full border border-black/5">
                {salon.instagram}
              </span>
            )}
          </div>

          {/* Description */}
          {salon.description && (
            <p className="font-sans text-sm text-graphite/60 line-clamp-2 mb-4">
              {salon.description}
            </p>
          )}

          {/* Info Row */}
          <div className="flex flex-col gap-2 mb-4">
            {salon.address && (
              <div className="flex items-center gap-2 text-graphite/50">
                <MapPin className="w-4 h-4 flex-shrink-0" />
                <span className="font-sans text-sm truncate">{salon.address}</span>
              </div>
            )}
            {salon.working_hours && (
              <div className="flex items-center gap-2 text-graphite/50">
                <Clock className="w-4 h-4 flex-shrink-0" />
                <span className="font-sans text-sm">{salon.working_hours}</span>
              </div>
            )}
          </div>

          {/* Rating Stars */}
          <div className="flex items-center justify-between pt-4 border-t border-black/10">
            {renderStars(Number(salon.rating))}

            {/* CTA */}
            <motion.div
              className="flex items-center gap-1 text-graphite bg-graphite/5 px-3 py-1.5 rounded-full"
              initial={{ x: 0 }}
              whileHover={{ x: 3 }}
            >
              <span className="font-sans text-sm font-medium">{t.book}</span>
              <ChevronRight className="w-4 h-4" />
            </motion.div>
          </div>
        </div>

        {/* Hover Glow Effect */}
        <motion.div
          className="absolute inset-0 pointer-events-none"
          initial={{ opacity: 0 }}
          whileHover={{ opacity: 1 }}
          transition={{ duration: 0.3 }}
        >
          <div className="absolute inset-0 bg-gradient-to-br from-graphite/6 via-transparent to-graphite/3 rounded-[28px]" />
        </motion.div>
      </motion.button>
    </motion.div>
  );
}
