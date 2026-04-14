"use client";

import { useState, useEffect, useCallback, useRef } from "react";
import { motion } from "framer-motion";
import Link from "next/link";
import {
  Sparkles,
  Calendar,
  Clock,
  Phone,
  ChevronRight,
  Star,
  Menu,
  X,
  Mail,
  AtSign,
  Search,
  Building2,
  RefreshCw,
  User,
} from "lucide-react";
import { getSalons, Salon } from "@/lib/api";
import SalonCard from "@/components/SalonCard";
import SalonDetail from "@/components/SalonDetail";
import BookingDrawer from "@/components/BookingDrawer";
import MyBookingsModal from "@/components/MyBookingsModal";
import BrandLogo from "@/components/BrandLogo";
import { DEFAULT_LOCALE, localeLabels, type Locale } from "@/lib/i18n";

// Animation variants
const fadeInUp = {
  hidden: { opacity: 0, y: 30 },
  visible: { opacity: 1, y: 0 },
};

const staggerContainer = {
  hidden: { opacity: 0 },
  visible: {
    opacity: 1,
    transition: {
      staggerChildren: 0.1,
      delayChildren: 0.2,
    },
  },
};

const scaleIn = {
  hidden: { opacity: 0, scale: 0.9 },
  visible: { opacity: 1, scale: 1 },
};

function BeautyHeroVisual() {
  return (
    <div className="absolute inset-0 overflow-hidden">
      <motion.div
        className="absolute -top-24 -left-16 w-72 h-72 rounded-full bg-[#f8d8cc]/35 blur-3xl"
        animate={{ x: [0, 18, 0], y: [0, -10, 0] }}
        transition={{ duration: 8, repeat: Infinity, ease: "easeInOut" }}
      />
      <motion.div
        className="absolute -bottom-24 -right-20 w-96 h-96 rounded-full bg-[#d9cfc7]/40 blur-3xl"
        animate={{ x: [0, -16, 0], y: [0, 12, 0] }}
        transition={{ duration: 9.5, repeat: Infinity, ease: "easeInOut" }}
      />

      <motion.div
        className="absolute inset-[22px] rounded-[26px] overflow-hidden border border-white/70 shadow-[0_18px_44px_rgba(0,0,0,0.18)]"
        animate={{ scale: [1, 1.012, 1] }}
        transition={{ duration: 7, repeat: Infinity, ease: "easeInOut" }}
      >
        <div
          className="absolute inset-0 bg-cover bg-center"
          style={{
            backgroundImage:
              "url('https://images.unsplash.com/photo-1487412720507-e7ab37603c6f?auto=format&fit=crop&w=1400&q=80')",
          }}
        />
        <div className="absolute inset-0 bg-gradient-to-t from-black/25 via-black/5 to-white/15" />
        <motion.div
          className="absolute inset-0 bg-[linear-gradient(115deg,transparent_25%,rgba(255,255,255,0.34)_45%,transparent_62%)]"
          animate={{ x: ["-120%", "120%"] }}
          transition={{ duration: 3.8, repeat: Infinity, ease: "easeInOut", repeatDelay: 1.3 }}
        />
      </motion.div>
    </div>
  );
}

// Header Component
function Header({
  onBookingClick,
  onMyBookingsClick,
  activeSection,
  locale,
  onLocaleChange,
  showBrand,
  logoAnchorRef,
}: {
  onBookingClick: () => void;
  onMyBookingsClick: () => void;
  activeSection: "salons" | "about" | "contacts";
  locale: Locale;
  onLocaleChange: (locale: Locale) => void;
  showBrand: boolean;
  logoAnchorRef: React.RefObject<HTMLAnchorElement | null>;
}) {
  const [isMenuOpen, setIsMenuOpen] = useState(false);
  const [isScrolled, setIsScrolled] = useState(false);

  useEffect(() => {
    const handleScroll = () => {
      setIsScrolled(window.scrollY > 50);
    };
    window.addEventListener("scroll", handleScroll);
    return () => window.removeEventListener("scroll", handleScroll);
  }, []);

  return (
    <motion.header
      initial={{ opacity: 0, y: -20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.6 }}
      className="fixed top-0 left-0 right-0 z-50"
    >
      <div
        className={`transition-all duration-300 ${
          isScrolled
            ? "bg-bone/95 backdrop-blur-lg shadow-soft"
            : "bg-transparent"
        }`}
      >
        <div className="container-luxury">
          <div className="flex items-center justify-between h-20">
            {/* Logo */}
            <Link
              href="/"
              ref={logoAnchorRef}
              className={`transition-opacity duration-300 ${showBrand ? "opacity-100" : "opacity-0"}`}
            >
              <BrandLogo compact animated />
            </Link>

            {/* Desktop Navigation */}
            <nav className="hidden md:flex items-center gap-8">
              <a
                href="#salons"
                className={`font-sans text-sm font-medium transition-colors ${
                  activeSection === "salons"
                    ? "text-graphite"
                    : "text-graphite/70 hover:text-graphite"
                }`}
              >
                {locale === "kk" ? "Салондар" : "Салоны"}
              </a>
              <a
                href="#about"
                className={`font-sans text-sm font-medium transition-colors ${
                  activeSection === "about"
                    ? "text-graphite"
                    : "text-graphite/70 hover:text-graphite"
                }`}
              >
                {locale === "kk" ? "Біз туралы" : "О нас"}
              </a>
              <a
                href="#contacts"
                className={`font-sans text-sm font-medium transition-colors ${
                  activeSection === "contacts"
                    ? "text-graphite"
                    : "text-graphite/70 hover:text-graphite"
                }`}
              >
                {locale === "kk" ? "Байланыс" : "Контакты"}
              </a>
            </nav>

            {/* CTA Button */}
            <div className="hidden md:flex items-center gap-3">
              <button
                type="button"
                onClick={onMyBookingsClick}
                className="btn-ghost text-sm font-medium"
              >
                <User className="w-4 h-4" />
                {locale === "kk" ? "Менің жазылуларым" : "Мои записи"}
              </button>
              <div className="bg-white/80 border border-light-gray rounded-full p-1 flex items-center">
                {(["ru", "kk"] as Locale[]).map((lang) => (
                  <button
                    key={lang}
                    onClick={() => onLocaleChange(lang)}
                    className={`px-3 py-1.5 rounded-full text-xs font-semibold transition ${
                      locale === lang ? "bg-graphite text-bone" : "text-graphite/70"
                    }`}
                  >
                    {localeLabels[lang]}
                  </button>
                ))}
              </div>
              <button onClick={onBookingClick} className="btn-primary">
                <Calendar className="w-4 h-4" />
                {locale === "kk" ? "Жазылу" : "Записаться"}
              </button>
            </div>

            {/* Mobile Menu Button */}
            <button
              onClick={() => setIsMenuOpen(!isMenuOpen)}
              aria-label={
                isMenuOpen
                  ? locale === "kk"
                    ? "Мәзірді жабу"
                    : "Закрыть меню"
                  : locale === "kk"
                    ? "Мәзірді ашу"
                    : "Открыть меню"
              }
              className="md:hidden p-2 rounded-full hover:bg-graphite/5 transition-colors"
            >
              {isMenuOpen ? (
                <X className="w-6 h-6" />
              ) : (
                <Menu className="w-6 h-6" />
              )}
            </button>
          </div>
        </div>
      </div>

      {/* Mobile Menu */}
      <motion.div
        initial={false}
        animate={
          isMenuOpen ? { height: "auto", opacity: 1 } : { height: 0, opacity: 0 }
        }
        transition={{ duration: 0.3 }}
        className="md:hidden overflow-hidden bg-bone/95 backdrop-blur-lg border-b border-light-gray/50"
      >
        <nav className="container-luxury py-6 flex flex-col gap-4">
          <a
            href="#salons"
            className="font-sans text-lg font-medium py-2"
            onClick={() => setIsMenuOpen(false)}
          >
            {locale === "kk" ? "Салондар" : "Салоны"}
          </a>
          <a
            href="#about"
            className="font-sans text-lg font-medium py-2"
            onClick={() => setIsMenuOpen(false)}
          >
            {locale === "kk" ? "Біз туралы" : "О нас"}
          </a>
          <a
            href="#contacts"
            className="font-sans text-lg font-medium py-2"
            onClick={() => setIsMenuOpen(false)}
          >
            {locale === "kk" ? "Байланыс" : "Контакты"}
          </a>
          <button
            type="button"
            onClick={() => {
              setIsMenuOpen(false);
              onMyBookingsClick();
            }}
            className="font-sans text-lg font-medium py-2 text-left flex items-center gap-2"
          >
            <User className="w-5 h-5" />
            {locale === "kk" ? "Менің жазылуларым" : "Мои записи"}
          </button>
          <div className="bg-white/80 border border-light-gray rounded-full p-1 flex items-center w-fit">
            {(["ru", "kk"] as Locale[]).map((lang) => (
              <button
                key={lang}
                onClick={() => onLocaleChange(lang)}
                className={`px-3 py-1.5 rounded-full text-xs font-semibold transition ${
                  locale === lang ? "bg-graphite text-bone" : "text-graphite/70"
                }`}
              >
                {localeLabels[lang]}
              </button>
            ))}
          </div>
          <button
            onClick={() => {
              setIsMenuOpen(false);
              onBookingClick();
            }}
            className="btn-primary mt-4 w-full"
          >
            <Calendar className="w-4 h-4" />
            {locale === "kk" ? "Онлайн жазылу" : "Записаться онлайн"}
          </button>
        </nav>
      </motion.div>
    </motion.header>
  );
}

// Hero Section Component
function HeroSection({ onExploreClick, locale }: { onExploreClick: () => void; locale: Locale }) {
  return (
    <section className="relative min-h-screen flex items-center pt-20 overflow-hidden">
      {/* Background Pattern */}
      <div className="absolute inset-0 overflow-hidden">
        <motion.div
          animate={{ y: [0, -16, 0], x: [0, 12, 0] }}
          transition={{ duration: 8, repeat: Infinity, ease: "easeInOut" }}
          className="absolute top-20 right-0 w-96 h-96 bg-graphite/5 rounded-full blur-3xl"
        />
        <motion.div
          animate={{ y: [0, 18, 0], x: [0, -10, 0] }}
          transition={{ duration: 9, repeat: Infinity, ease: "easeInOut" }}
          className="absolute bottom-20 left-0 w-80 h-80 bg-graphite/5 rounded-full blur-3xl"
        />
      </div>

      <div className="container-luxury relative z-10">
        <div className="grid lg:grid-cols-2 gap-12 lg:gap-20 items-center">
          {/* Left Content */}
          <motion.div
            variants={staggerContainer}
            initial="hidden"
            animate="visible"
            className="text-center lg:text-left"
          >
            {/* Badge */}
            <motion.div variants={fadeInUp} className="mb-6">
              <span className="inline-flex items-center gap-2 px-4 py-2 bg-graphite/5 border border-light-gray/80 rounded-full">
                <Building2 className="w-4 h-4 text-graphite" />
                <span className="font-sans text-sm font-medium text-graphite/80">
                  {locale === "kk" ? "Алматыдағы 10+ салон" : "10+ салонов Алматы"}
                </span>
              </span>
            </motion.div>

            {/* Main Heading */}
            <motion.h1 variants={fadeInUp} className="heading-xl mb-6">
              {locale === "kk" ? "Өзіңізге" : "Найдите"}
              <br />
              <span className="underline decoration-graphite/30 underline-offset-8">
                {locale === "kk" ? "лайық" : "идеальный"}
              </span>
              <br />
              {locale === "kk" ? "салонды табыңыз" : "салон"}
            </motion.h1>

            {/* Subtitle */}
            <motion.p
              variants={fadeInUp}
              className="body-lg text-graphite/70 mb-8 max-w-lg mx-auto lg:mx-0"
            >
              {locale === "kk"
                ? "Алматының үздік сұлулық салондары бір жерде. Мастерді, уақытты таңдап, бір минутта онлайн жазылыңыз."
                : "Лучшие салоны красоты Алматы в одном месте. Выбирайте мастера, время и записывайтесь онлайн за минуту."}
            </motion.p>

            {/* CTA Buttons */}
            <motion.div
              variants={fadeInUp}
              className="flex flex-col sm:flex-row gap-4 justify-center lg:justify-start"
            >
              <button onClick={onExploreClick} className="btn-primary">
                <Search className="w-4 h-4" />
                {locale === "kk" ? "Салон таңдау" : "Выбрать салон"}
              </button>
              <a href="tel:+77771234567" className="btn-secondary">
                <Phone className="w-4 h-4" />
                {locale === "kk" ? "Қоңырау шалу" : "Позвонить нам"}
              </a>
            </motion.div>

            <motion.div
              variants={fadeInUp}
              className="mt-8 bg-white rounded-2xl border border-light-gray shadow-soft p-3 flex flex-wrap items-center gap-2 max-w-xl mx-auto lg:mx-0"
            >
              {(locale === "kk"
                ? ["Маникюр", "Бояу", "Массаж", "Қас", "Укладка"]
                : ["Маникюр", "Окрашивание", "Массаж", "Брови", "Укладка"]).map(
                (item, idx) => (
                  <motion.span
                    key={item}
                    initial={{ opacity: 0, y: 8 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: 0.25 + idx * 0.1 }}
                    className="px-3 py-1.5 text-sm rounded-full bg-graphite/5 border border-graphite/10 font-sans text-graphite/80"
                  >
                    {item}
                  </motion.span>
                )
              )}
            </motion.div>

            {/* Stats */}
            <motion.div
              variants={fadeInUp}
              className="mt-12 pt-8 border-t border-light-gray"
            >
              <div className="grid grid-cols-3 gap-8">
                <div className="text-center lg:text-left">
                  <div className="font-serif text-3xl font-bold text-graphite">
                    10+
                  </div>
                  <div className="font-sans text-sm text-graphite/60 mt-1">
                    {locale === "kk" ? "Салон" : "Салонов"}
                  </div>
                </div>
                <div className="text-center lg:text-left">
                  <div className="font-serif text-3xl font-bold text-graphite">
                    50+
                  </div>
                  <div className="font-sans text-sm text-graphite/60 mt-1">
                    {locale === "kk" ? "Мастер" : "Мастеров"}
                  </div>
                </div>
                <div className="text-center lg:text-left">
                  <div className="font-serif text-3xl font-bold text-graphite">
                    4.9
                  </div>
                  <div className="font-sans text-sm text-graphite/60 mt-1">
                    {locale === "kk" ? "Рейтинг" : "Рейтинг"}
                  </div>
                </div>
              </div>
            </motion.div>
          </motion.div>

          {/* Right Content - Hero Image */}
          <motion.div
            variants={scaleIn}
            initial="hidden"
            animate="visible"
            transition={{ duration: 0.8, delay: 0.3 }}
            className="relative"
          >
            {/* Main Image Container */}
            <div className="relative aspect-[4/5] rounded-3xl overflow-hidden shadow-elevated border border-black/10">
              <div className="absolute inset-0 bg-gradient-to-br from-[#f5f5f5] via-[#ececec] to-[#e7e7e7]" />
              <motion.div
                className="absolute inset-0 bg-[radial-gradient(circle_at_30%_20%,rgba(255,255,255,0.9),transparent_40%)]"
                animate={{ opacity: [0.5, 1, 0.5] }}
                transition={{ duration: 5, repeat: Infinity, ease: "easeInOut" }}
              />
              <BeautyHeroVisual />
            </div>

            {/* Floating Card - Stats */}
            <motion.div
              initial={{ opacity: 0, x: 20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ duration: 0.6, delay: 0.8 }}
              className="absolute -bottom-6 -left-6 lg:-left-12"
            >
              <div className="card-glass p-5 border border-black/10">
                <div className="flex items-center gap-4">
                  <div className="w-12 h-12 rounded-full bg-graphite/10 flex items-center justify-center">
                    <Clock className="w-6 h-6 text-graphite" />
                  </div>
                  <div>
                    <div className="font-sans text-sm font-semibold">
                      {locale === "kk" ? "Жылдам жазылу" : "Быстрая запись"}
                    </div>
                    <div className="font-sans text-sm text-graphite/60">
                      Онлайн 24/7
                    </div>
                  </div>
                </div>
              </div>
            </motion.div>

            {/* Rating Card */}
            <motion.div
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ duration: 0.6, delay: 1 }}
              className="absolute -top-4 -right-4 lg:-right-8"
            >
              <div className="card-glass p-4 border border-black/10">
                <div className="flex items-center gap-2">
                  <div className="flex">
                    {[...Array(5)].map((_, i) => (
                      <Star key={i} className="w-4 h-4 text-graphite fill-graphite" />
                    ))}
                  </div>
                  <span className="font-sans text-sm font-semibold">4.9</span>
                </div>
                <div className="font-sans text-xs text-graphite/60 mt-1">
                  {locale === "kk" ? "Орташа рейтинг" : "Средний рейтинг"}
                </div>
              </div>
            </motion.div>
          </motion.div>
        </div>
      </div>

      {/* Scroll Indicator */}
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ delay: 1.5 }}
        className="absolute bottom-8 left-1/2 -translate-x-1/2"
      >
        <motion.div
          animate={{ y: [0, 10, 0] }}
          transition={{ duration: 2, repeat: Infinity }}
          className="flex flex-col items-center gap-2"
        >
          <span className="font-sans text-xs uppercase tracking-widest text-graphite/40">
            {locale === "kk" ? "Төмен сырғытыңыз" : "Листайте вниз"}
          </span>
          <ChevronRight className="w-5 h-5 text-graphite/40 rotate-90" />
        </motion.div>
      </motion.div>
    </section>
  );
}

// Salons Section
function SalonsSection({
  salons,
  onSelectSalon,
  locale,
}: {
  salons: Salon[];
  onSelectSalon: (salon: Salon) => void;
  locale: Locale;
}) {
  return (
    <section id="salons" className="py-24">
      <div className="container-luxury">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          className="text-center mb-16"
        >
          <span className="label">{locale === "kk" ? "Біздің салондар" : "Наши салоны"}</span>
          <h2 className="heading-lg mt-4 mb-6">
            {locale === "kk" ? "Алматының үздік" : "Лучшие салоны"}{" "}
            <span className="text-graphite">{locale === "kk" ? "салондары" : "Алматы"}</span>
          </h2>
          <div className="divider mb-6" />
          <p className="body-md text-graphite/60 max-w-2xl mx-auto">
            {locale === "kk"
              ? "Салонды таңдап, қаладағы үздік мамандарға жазылыңыз. Біз сенімді пікірлері бар үздік студияларды жинадық."
              : "Выберите салон и запишитесь к лучшим мастерам города. Мы собрали топовые студии красоты с проверенными отзывами."}
          </p>
        </motion.div>

        <motion.div
          initial={{ opacity: 0, y: 18 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.45 }}
          className="flex flex-wrap justify-center gap-2 mb-10"
        >
          {(locale === "kk"
            ? ["Үздік рейтинг", "Қазір ашық", "Жақын жерде", "Премиум", "Kaspi QR"]
            : ["Top rated", "Open now", "Near me", "Premium", "Kaspi QR"]).map(
            (chip, idx) => (
              <motion.span
                key={chip}
                initial={{ opacity: 0, y: 10 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true }}
                transition={{ delay: idx * 0.08 }}
                className="px-3 py-1.5 rounded-full text-sm font-sans bg-white border border-black/10 text-graphite/80 shadow-sm"
              >
                {chip}
              </motion.span>
            )
          )}
        </motion.div>

        <motion.div
          variants={staggerContainer}
          initial="hidden"
          whileInView="visible"
          viewport={{ once: true }}
          className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 [perspective:1000px]"
        >
          {salons.map((salon, index) => (
            <SalonCard
              key={salon.id}
              salon={salon}
              onSelect={onSelectSalon}
              index={index}
              locale={locale}
            />
          ))}
        </motion.div>
      </div>
    </section>
  );
}

// About Section
function AboutSection({ locale }: { locale: Locale }) {
  return (
    <section id="about" className="py-24 bg-white/50">
      <div className="container-luxury">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          className="text-center mb-16"
        >
          <span className="label">{locale === "kk" ? "Платформа туралы" : "О платформе"}</span>
          <h2 className="heading-lg mt-4 mb-6">
            {locale === "kk" ? "Бұл қалай" : "Как это"}{" "}
            <span className="text-graphite">{locale === "kk" ? "жұмыс істейді" : "работает"}</span>
          </h2>
          <div className="divider" />
        </motion.div>

        <div className="grid md:grid-cols-3 gap-8">
          {(locale === "kk"
            ? [
                {
                  step: "01",
                  title: "Салонды таңдаңыз",
                  description: "Рейтинг пен пікірлерді қарап, өзіңізге ұнаған салонды таңдаңыз",
                  icon: Building2,
                },
                {
                  step: "02",
                  title: "Қызмет пен мастерді таңдаңыз",
                  description: "Қызметтермен танысып, өзіңізге лайық мастерді таңдаңыз",
                  icon: Star,
                },
                {
                  step: "03",
                  title: "Онлайн жазылыңыз",
                  description: "Ыңғайлы уақытты таңдап, Kaspi QR арқылы төлеңіз",
                  icon: Calendar,
                },
              ]
            : [
                {
                  step: "01",
                  title: "Выберите салон",
                  description: "Просмотрите рейтинги, отзывы и выберите понравившийся салон",
                  icon: Building2,
                },
                {
                  step: "02",
                  title: "Выберите услугу и мастера",
                  description: "Ознакомьтесь с услугами и выберите подходящего мастера",
                  icon: Star,
                },
                {
                  step: "03",
                  title: "Запишитесь онлайн",
                  description: "Выберите удобное время и оплатите через Kaspi QR",
                  icon: Calendar,
                },
              ]).map((item, index) => (
            <motion.div
              key={item.step}
              initial={{ opacity: 0, y: 30 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ delay: index * 0.2 }}
              className="text-center"
            >
              <div className="w-16 h-16 rounded-2xl bg-graphite/10 flex items-center justify-center mx-auto mb-4">
                <item.icon className="w-8 h-8 text-graphite" />
              </div>
              <span className="font-sans text-xs font-bold text-graphite tracking-wider">
                {locale === "kk" ? "ҚАДАМ" : "ШАГ"} {item.step}
              </span>
              <h3 className="font-serif text-xl font-semibold mt-2 mb-3">
                {item.title}
              </h3>
              <p className="font-sans text-sm text-graphite/60">
                {item.description}
              </p>
            </motion.div>
          ))}
        </div>
      </div>
    </section>
  );
}

// Contacts Section
function ContactsSection({ locale }: { locale: Locale }) {
  return (
    <section id="contacts" className="py-24">
      <div className="container-luxury">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          className="text-center mb-16"
        >
          <span className="label">{locale === "kk" ? "Байланыс" : "Контакты"}</span>
          <h2 className="heading-lg mt-4 mb-6">
            {locale === "kk" ? "Бізбен" : "Свяжитесь"}{" "}
            <span className="text-graphite">{locale === "kk" ? "хабарласыңыз" : "с нами"}</span>
          </h2>
          <div className="divider" />
        </motion.div>

        <motion.div
          initial={{ opacity: 0, y: 30 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          className="bg-graphite rounded-3xl p-8 md:p-12 text-bone max-w-3xl mx-auto"
        >
          <div className="grid md:grid-cols-2 gap-8">
            {/* Contact Info */}
            <div className="space-y-6">
              <h3 className="font-serif text-2xl font-semibold mb-6">
                {locale === "kk" ? "Платформа қолдауы" : "Поддержка платформы"}
              </h3>

              <div className="flex items-start gap-4">
                <div className="w-12 h-12 rounded-2xl bg-bone/10 border border-bone/15 flex items-center justify-center flex-shrink-0">
                  <Phone className="w-5 h-5 text-bone" />
                </div>
                <div>
                  <p className="font-sans font-semibold mb-1">
                    {locale === "kk" ? "Телефон" : "Телефон"}
                  </p>
                  <a
                    href="tel:+77771234567"
                    className="font-sans text-bone/70 hover:text-bone transition-colors"
                  >
                    +7 (777) 123-45-67
                  </a>
                </div>
              </div>

              <div className="flex items-start gap-4">
                <div className="w-12 h-12 rounded-2xl bg-bone/10 border border-bone/15 flex items-center justify-center flex-shrink-0">
                  <Mail className="w-5 h-5 text-bone" />
                </div>
                <div>
                  <p className="font-sans font-semibold mb-1">Email</p>
                  <a
                    href="mailto:support@salonsync.kz"
                    className="font-sans text-bone/70 hover:text-bone transition-colors"
                  >
                    support@salonsync.kz
                  </a>
                </div>
              </div>

              <div className="flex items-start gap-4">
                <div className="w-12 h-12 rounded-2xl bg-bone/10 border border-bone/15 flex items-center justify-center flex-shrink-0">
                  <AtSign className="w-5 h-5 text-bone" />
                </div>
                <div>
                  <p className="font-sans font-semibold mb-1">Instagram</p>
                  <a
                    href="https://instagram.com/salonsync_kz"
                    target="_blank"
                    rel="noopener noreferrer"
                    className="font-sans text-bone/70 hover:text-bone transition-colors"
                  >
                    @salonsync_kz
                  </a>
                </div>
              </div>
            </div>

            {/* Working Hours */}
            <div>
              <h3 className="font-serif text-2xl font-semibold mb-6">
                {locale === "kk" ? "Қолдау жұмыс уақыты" : "Часы работы поддержки"}
              </h3>

              <div className="space-y-4">
                <div className="flex justify-between items-center py-3 border-b border-bone/10">
                  <span className="font-sans text-bone/60">
                    {locale === "kk" ? "Дүйсенбі — Жұма" : "Понедельник — Пятница"}
                  </span>
                  <span className="font-sans font-semibold">09:00 — 21:00</span>
                </div>
                <div className="flex justify-between items-center py-3 border-b border-bone/10">
                  <span className="font-sans text-bone/60">
                    {locale === "kk" ? "Сенбі" : "Суббота"}
                  </span>
                  <span className="font-sans font-semibold">10:00 — 18:00</span>
                </div>
                <div className="flex justify-between items-center py-3 border-b border-bone/10">
                  <span className="font-sans text-bone/60">
                    {locale === "kk" ? "Жексенбі" : "Воскресенье"}
                  </span>
                  <span className="font-sans font-semibold">
                    {locale === "kk" ? "Демалыс" : "Выходной"}
                  </span>
                </div>
              </div>

              <p className="font-sans text-sm text-bone/40 mt-6">
                {locale === "kk"
                  ? "Платформа арқылы жазылу 24/7 қолжетімді"
                  : "Запись через платформу доступна 24/7"}
              </p>
            </div>
          </div>
        </motion.div>
      </div>
    </section>
  );
}

// Footer Component
function Footer({ locale }: { locale: Locale }) {
  return (
    <footer className="py-12 bg-bone border-t border-light-gray">
      <div className="container-luxury">
        <div className="flex flex-col md:flex-row items-center justify-between gap-6">
          {/* Logo */}
          <div className="flex items-center gap-2">
            <BrandLogo compact animated={false} />
          </div>

          {/* Copyright */}
          <p className="font-sans text-sm text-graphite/60">
            {locale === "kk"
              ? "© 2024 SalonSync. Алматы сұлулық салондары агрегаторы."
              : "© 2024 SalonSync. Агрегатор салонов красоты Алматы."}
          </p>

          {/* Social Links */}
          <div className="flex items-center gap-4">
            <a
              href="https://instagram.com/salonsync_kz"
              target="_blank"
              rel="noopener noreferrer"
              aria-label="Instagram SalonSync"
              className="w-10 h-10 rounded-full bg-graphite/5 border border-light-gray/70 flex items-center justify-center hover:bg-graphite hover:text-bone transition-all"
            >
              <AtSign className="w-5 h-5" />
            </a>
            <a
              href="tel:+77771234567"
              aria-label="Позвонить в поддержку"
              className="w-10 h-10 rounded-full bg-graphite/5 border border-light-gray/70 flex items-center justify-center hover:bg-graphite hover:text-bone transition-all"
            >
              <Phone className="w-5 h-5" />
            </a>
          </div>
        </div>
      </div>
    </footer>
  );
}

// Loading Screen
function LoadingScreen({ locale }: { locale: Locale }) {
  return (
    <div className="min-h-screen flex items-center justify-center bg-bone">
      <div className="text-center">
        <motion.div
          animate={{ rotate: 360 }}
          transition={{ duration: 2, repeat: Infinity, ease: "linear" }}
        >
          <Sparkles className="w-12 h-12 text-graphite mx-auto" />
        </motion.div>
        <p className="font-sans text-sm text-graphite/60 mt-4">
          {locale === "kk" ? "Жүктелуде..." : "Загрузка..."}
        </p>
      </div>
    </div>
  );
}

// Main Page Component
export default function HomePage() {
  const [salons, setSalons] = useState<Salon[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [selectedSalon, setSelectedSalon] = useState<Salon | null>(null);
  const [showSalonDetail, setShowSalonDetail] = useState(false);
  const [showMyBookings, setShowMyBookings] = useState(false);
  const [activeSection, setActiveSection] = useState<"salons" | "about" | "contacts">(
    "salons"
  );
  const [locale, setLocale] = useState<Locale>(DEFAULT_LOCALE);
  const [showIntro, setShowIntro] = useState(false);
  const [introComplete, setIntroComplete] = useState(false);
  const [introStage, setIntroStage] = useState<"hold" | "move" | "typing" | "done">("hold");
  const [typedLogoText, setTypedLogoText] = useState("");
  const [introTarget, setIntroTarget] = useState({ top: 26, left: 26, scale: 0.74 });
  const logoAnchorRef = useRef<HTMLAnchorElement | null>(null);

  const loadData = useCallback(async () => {
    setLoading(true);
    setError("");
    try {
      const salonsData = await getSalons();
      setSalons(salonsData);
    } catch {
      setError(
        locale === "kk"
          ? "Салондарды жүктеу мүмкін болмады. Қосылымды тексеріп, қайта көріңіз."
          : "Не удалось загрузить салоны. Проверьте подключение и попробуйте снова."
      );
    } finally {
      setLoading(false);
    }
  }, [locale]);

  useEffect(() => {
    const savedLocale = window.localStorage.getItem("locale") as Locale | null;
    if (savedLocale === "ru" || savedLocale === "kk") {
      setLocale(savedLocale);
    }

    // Disable first-visit logo intro animation.
    setShowIntro(false);
    setIntroStage("done");
    setIntroComplete(true);
  }, []);

  useEffect(() => {
    if (introStage !== "typing") return;
    const fullText = "SalonSync";
    setTypedLogoText("");
    let index = 0;
    const typingInterval = window.setInterval(() => {
      index += 1;
      setTypedLogoText(fullText.slice(0, index));
      if (index >= fullText.length) {
        window.clearInterval(typingInterval);
      }
    }, 90);
    return () => window.clearInterval(typingInterval);
  }, [introStage]);

  useEffect(() => {
    if (!showIntro) return;

    const updateTarget = () => {
      if (!logoAnchorRef.current) return;
      const rect = logoAnchorRef.current.getBoundingClientRect();
      setIntroTarget({
        top: rect.top,
        left: rect.left,
        scale: 0.74,
      });
    };

    updateTarget();
    window.addEventListener("resize", updateTarget);
    return () => window.removeEventListener("resize", updateTarget);
  }, [showIntro]);

  useEffect(() => {
    window.localStorage.setItem("locale", locale);
  }, [locale]);

  useEffect(() => {
    loadData();
  }, [loadData]);

  useEffect(() => {
    const sectionIds: Array<"salons" | "about" | "contacts"> = [
      "salons",
      "about",
      "contacts",
    ];
    const observer = new IntersectionObserver(
      (entries) => {
        const visible = entries
          .filter((entry) => entry.isIntersecting)
          .sort((a, b) => b.intersectionRatio - a.intersectionRatio)[0];
        if (visible) {
          setActiveSection(visible.target.id as "salons" | "about" | "contacts");
        }
      },
      { threshold: [0.3, 0.6], rootMargin: "-20% 0px -40% 0px" }
    );

    sectionIds.forEach((id) => {
      const el = document.getElementById(id);
      if (el) observer.observe(el);
    });

    return () => observer.disconnect();
  }, []);

  const handleExploreClick = () => {
    document.getElementById("salons")?.scrollIntoView({ behavior: "smooth" });
  };

  const handleSelectSalon = (salon: Salon) => {
    setSelectedSalon(salon);
    setShowSalonDetail(true);
  };

  if (loading) {
    return <LoadingScreen locale={locale} />;
  }

  if (error) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-bone p-6">
        <div className="card-elevated max-w-md text-center">
          <div className="w-16 h-16 rounded-full bg-red-100 flex items-center justify-center mx-auto mb-4">
            <X className="w-8 h-8 text-red-500" />
          </div>
          <h2 className="font-serif text-xl font-semibold mb-2">
            {locale === "kk" ? "Жүктеу қатесі" : "Ошибка загрузки"}
          </h2>
          <p className="font-sans text-sm text-graphite/60 mb-4">{error}</p>
          <button onClick={loadData} className="btn-primary w-full justify-center">
            <RefreshCw className="w-4 h-4" />
            {locale === "kk" ? "Қайта жүктеу" : "Повторить загрузку"}
          </button>
        </div>
      </div>
    );
  }

  return (
    <>
      {showIntro && (
        <motion.div
          className="fixed inset-0 z-[100] bg-bone"
          initial={{ opacity: 1 }}
          animate={{ opacity: 0 }}
          transition={{ delay: 5.05, duration: 0.5, ease: "easeInOut" }}
        >
          <motion.div
            animate={{
              top: introStage === "hold" ? "50%" : introTarget.top,
              left: introStage === "hold" ? "50%" : introTarget.left,
              x: introStage === "hold" ? "-50%" : 0,
              y: introStage === "hold" ? "-50%" : 0,
              scale: introStage === "hold" ? 1.2 : introTarget.scale,
              opacity: 1,
            }}
            transition={{ duration: introStage === "hold" ? 0.1 : 0.9, ease: [0.22, 1, 0.36, 1] }}
            className="absolute flex items-center gap-3"
          >
            <BrandLogo animated showText={false} />
            {introStage === "typing" && (
              <div className="min-w-[190px]">
                <span className="font-serif text-[40px] font-bold tracking-tight text-[#17181c]">
                  {typedLogoText}
                </span>
                <motion.span
                  className="inline-block ml-1 h-8 w-[2px] bg-[#17181c] align-middle"
                  animate={{ opacity: [1, 0, 1] }}
                  transition={{ duration: 0.8, repeat: Infinity }}
                />
              </div>
            )}
          </motion.div>
        </motion.div>
      )}

      <motion.main
        className="min-h-screen bg-bone"
        initial={false}
        animate={
          introComplete
            ? { opacity: 1, y: 0 }
            : { opacity: 0, y: 20 }
        }
        transition={{ duration: 0.55, ease: "easeOut" }}
      >
      <Header
        onBookingClick={handleExploreClick}
        onMyBookingsClick={() => setShowMyBookings(true)}
        activeSection={activeSection}
        locale={locale}
        onLocaleChange={setLocale}
        showBrand={introComplete}
        logoAnchorRef={logoAnchorRef}
      />
      <HeroSection onExploreClick={handleExploreClick} locale={locale} />

      {salons.length > 0 ? (
        <SalonsSection salons={salons} onSelectSalon={handleSelectSalon} locale={locale} />
      ) : (
        <section id="salons" className="py-24">
          <div className="container-luxury">
            <div className="card-elevated max-w-xl mx-auto text-center">
              <h2 className="heading-sm mb-3">
                {locale === "kk" ? "Каталогта белсенді салондар жоқ" : "В каталоге пока нет салонов"}
              </h2>
              <p className="body-sm text-graphite/70 mb-6">
                {locale === "kk"
                  ? "Деректер жүктелмесе, «Жаңарту» батырмасын басыңыз немесе кейінірек қайта көріңіз."
                  : "Нажмите «Обновить», чтобы запросить список снова. Если салонов нет и позже — возможно, каталог ещё не наполнен на сервере."}
              </p>
              <button onClick={loadData} className="btn-secondary">
                <RefreshCw className="w-4 h-4" />
                {locale === "kk" ? "Жаңарту" : "Обновить"}
              </button>
            </div>
          </div>
        </section>
      )}

      <AboutSection locale={locale} />
      <ContactsSection locale={locale} />
      <Footer locale={locale} />

      {selectedSalon && showSalonDetail && (
        <SalonDetail
          salon={selectedSalon}
          onClose={() => {
            setSelectedSalon(null);
            setShowSalonDetail(false);
          }}
          onBooking={() => setShowSalonDetail(false)}
          locale={locale}
        />
      )}

      {selectedSalon && !showSalonDetail && (
        <BookingDrawer
          salon={selectedSalon}
          onClose={() => {
            setSelectedSalon(null);
            setShowSalonDetail(false);
          }}
          locale={locale}
          onOpenMyBookings={() => setShowMyBookings(true)}
        />
      )}

      <MyBookingsModal
        isOpen={showMyBookings}
        onClose={() => setShowMyBookings(false)}
        locale={locale}
        onOpenBooking={() => {
          setShowMyBookings(false);
          document.getElementById("salons")?.scrollIntoView({ behavior: "smooth" });
        }}
      />
      </motion.main>
    </>
  );
}
