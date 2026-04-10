"use client";

import {
  addMonths,
  eachDayOfInterval,
  endOfMonth,
  endOfWeek,
  format,
  isBefore,
  isSameMonth,
  parse,
  startOfDay,
  startOfMonth,
  startOfWeek,
  subMonths,
} from "date-fns";
import { kk as kkLocale, ru } from "date-fns/locale";
import { ChevronLeft, ChevronRight } from "lucide-react";
import type { Locale } from "@/lib/i18n";

interface CalendarPickerProps {
  month: string;
  onMonthChange: (month: string) => void;
  availableDates: Set<string>;
  selectedDate: string;
  onSelectDate: (isoDate: string) => void;
  locale: Locale;
  loading?: boolean;
}

export default function CalendarPicker({
  month,
  onMonthChange,
  availableDates,
  selectedDate,
  onSelectDate,
  locale,
  loading,
}: CalendarPickerProps) {
  const loc = locale === "kk" ? kkLocale : ru;
  const monthDate = parse(`${month}-01`, "yyyy-MM-dd", new Date());
  const monthStart = startOfMonth(monthDate);
  const monthEnd = endOfMonth(monthDate);
  const gridStart = startOfWeek(monthStart, { weekStartsOn: 1 });
  const gridEnd = endOfWeek(monthEnd, { weekStartsOn: 1 });
  const days = eachDayOfInterval({ start: gridStart, end: gridEnd });
  const today = startOfDay(new Date());

  const labels =
    locale === "kk"
      ? {
          prev: "Алдыңғы ай",
          next: "Келесі ай",
          weekdays: ["Дс", "Сс", "Ср", "Бс", "Жм", "Сн", "Жс"],
        }
      : {
          prev: "Предыдущий месяц",
          next: "Следующий месяц",
          weekdays: ["Пн", "Вт", "Ср", "Чт", "Пт", "Сб", "Вс"],
        };

  const title = format(monthDate, "LLLL yyyy", { locale: loc });

  const goPrev = () => {
    const d = subMonths(monthDate, 1);
    onMonthChange(format(d, "yyyy-MM"));
  };
  const goNext = () => {
    const d = addMonths(monthDate, 1);
    onMonthChange(format(d, "yyyy-MM"));
  };

  const dayKey = (d: Date) => format(d, "yyyy-MM-dd");

  return (
    <div className="space-y-3">
      <div className="flex items-center justify-between gap-2">
        <button
          type="button"
          onClick={goPrev}
          className="p-2 rounded-full border border-light-gray hover:bg-graphite/5 transition"
          aria-label={labels.prev}
        >
          <ChevronLeft className="w-5 h-5" />
        </button>
        <span className="font-serif text-lg font-semibold text-graphite capitalize">
          {title}
        </span>
        <button
          type="button"
          onClick={goNext}
          className="p-2 rounded-full border border-light-gray hover:bg-graphite/5 transition"
          aria-label={labels.next}
        >
          <ChevronRight className="w-5 h-5" />
        </button>
      </div>

      <div className="grid grid-cols-7 gap-1 text-center">
        {labels.weekdays.map((w) => (
          <div key={w} className="text-[11px] font-medium text-graphite/45 py-1">
            {w}
          </div>
        ))}
        {days.map((d) => {
          const key = dayKey(d);
          const inMonth = isSameMonth(d, monthDate);
          const isPast = isBefore(startOfDay(d), today);
          const hasSlot = availableDates.has(key);
          const selected = selectedDate === key;
          const disabled = !inMonth || isPast || !hasSlot || loading;

          return (
            <button
              key={key}
              type="button"
              disabled={disabled}
              onClick={() => !disabled && onSelectDate(key)}
              className={[
                "aspect-square rounded-xl text-sm font-medium transition",
                !inMonth ? "text-graphite/15 cursor-default" : "",
                inMonth && isPast ? "text-graphite/15 cursor-not-allowed" : "",
                inMonth && !isPast && !hasSlot ? "text-graphite/25 cursor-not-allowed" : "",
                inMonth && !isPast && hasSlot && !selected
                  ? "text-graphite hover:bg-graphite/10 cursor-pointer"
                  : "",
                selected ? "bg-graphite text-bone ring-2 ring-graphite ring-offset-2 ring-offset-bone" : "",
              ].join(" ")}
            >
              {format(d, "d")}
            </button>
          );
        })}
      </div>
    </div>
  );
}
