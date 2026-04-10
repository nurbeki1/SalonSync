"use client";

import { Clock, Sparkles } from "lucide-react";
import type { Service } from "@/lib/api";

interface ServiceCardProps {
  service: Service;
  onSelect: (service: Service) => void;
}

export default function ServiceCard({ service, onSelect }: ServiceCardProps) {
  return (
    <div className="bg-white rounded-2xl p-6 shadow-sm border border-gray-100 hover:shadow-md hover:border-gray-200 transition-all duration-300 group">
      <div className="w-12 h-12 bg-gradient-to-br from-rose-100 to-purple-100 rounded-xl flex items-center justify-center mb-4 group-hover:scale-110 transition-transform">
        <Sparkles className="w-6 h-6 text-rose-500" />
      </div>

      <h3 className="text-lg font-semibold text-gray-900 mb-2">{service.name}</h3>

      {service.description && (
        <p className="text-sm text-gray-500 mb-4 line-clamp-2">{service.description}</p>
      )}

      <div className="flex items-center gap-4 mb-4">
        <div className="flex items-center gap-1.5 text-sm text-gray-600">
          <Clock className="w-4 h-4" />
          <span>{service.duration} мин</span>
        </div>
        <div className="text-lg font-bold text-gray-900">
          {parseInt(service.price).toLocaleString()} ₸
        </div>
      </div>

      <button
        onClick={() => onSelect(service)}
        className="w-full py-3 px-4 bg-gradient-to-r from-rose-500 to-purple-500 text-white font-medium rounded-xl hover:from-rose-600 hover:to-purple-600 transition-all duration-300 shadow-sm hover:shadow-md"
      >
        Выбрать
      </button>
    </div>
  );
}
