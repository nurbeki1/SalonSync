"use client";

import { Scissors } from "lucide-react";

export default function Header() {
  return (
    <header className="bg-white border-b border-gray-100 sticky top-0 z-50">
      <div className="max-w-6xl mx-auto px-4 py-4 flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 bg-gradient-to-br from-rose-400 to-purple-500 rounded-xl flex items-center justify-center">
            <Scissors className="w-5 h-5 text-white" />
          </div>
          <div>
            <h1 className="text-xl font-semibold text-gray-900">Beauty Studio</h1>
            <p className="text-xs text-gray-500">Премиум салон красоты</p>
          </div>
        </div>
        <nav className="hidden md:flex items-center gap-6">
          <a href="#services" className="text-sm text-gray-600 hover:text-gray-900 transition">
            Услуги
          </a>
          <a href="#masters" className="text-sm text-gray-600 hover:text-gray-900 transition">
            Мастера
          </a>
          <a href="#contacts" className="text-sm text-gray-600 hover:text-gray-900 transition">
            Контакты
          </a>
        </nav>
      </div>
    </header>
  );
}
