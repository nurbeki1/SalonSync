"use client";

import { User } from "lucide-react";
import type { Master } from "@/lib/api";

interface MasterCardProps {
  master: Master;
  selected?: boolean;
  onSelect?: (master: Master) => void;
}

export default function MasterCard({ master, selected, onSelect }: MasterCardProps) {
  return (
    <div
      onClick={() => onSelect?.(master)}
      className={`bg-white rounded-2xl p-6 shadow-sm border transition-all duration-300 ${
        onSelect ? "cursor-pointer hover:shadow-md" : ""
      } ${
        selected
          ? "border-rose-400 ring-2 ring-rose-100"
          : "border-gray-100 hover:border-gray-200"
      }`}
    >
      <div className="flex items-center gap-4">
        <div className="w-16 h-16 bg-gradient-to-br from-gray-100 to-gray-200 rounded-full flex items-center justify-center flex-shrink-0">
          <User className="w-8 h-8 text-gray-400" />
        </div>

        <div className="flex-1 min-w-0">
          <h3 className="text-lg font-semibold text-gray-900 truncate">{master.name}</h3>
          {master.specialization && (
            <p className="text-sm text-rose-500 font-medium">{master.specialization}</p>
          )}
          {master.bio && (
            <p className="text-sm text-gray-500 mt-1 line-clamp-2">{master.bio}</p>
          )}
        </div>
      </div>
    </div>
  );
}
