import type { Metadata, Viewport } from "next";
import { Playfair_Display, Inter } from "next/font/google";
import "./globals.css";

// Serif font for headings - elegance & luxury
const playfair = Playfair_Display({
  variable: "--font-playfair",
  subsets: ["latin", "cyrillic"],
  display: "swap",
  weight: ["400", "500", "600", "700"],
});

// Sans-serif font for UI elements - clean & modern
const inter = Inter({
  variable: "--font-inter",
  subsets: ["latin", "cyrillic"],
  display: "swap",
  weight: ["400", "500", "600", "700"],
});

export const metadata: Metadata = {
  title: "SalonSync | Агрегатор салонов красоты",
  description:
    "Откройте мир роскоши и заботы о себе. Профессиональные мастера, индивидуальный подход и безупречный результат.",
  keywords: ["салон красоты", "маникюр", "стрижка", "окрашивание", "Алматы", "премиум"],
  authors: [{ name: "SalonSync" }],
  openGraph: {
    title: "SalonSync | Агрегатор салонов красоты",
    description: "Откройте мир роскоши и заботы о себе",
    type: "website",
    locale: "ru_KZ",
  },
};

export const viewport: Viewport = {
  width: "device-width",
  initialScale: 1,
  themeColor: "#FAF9F6",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html
      lang="ru"
      className={`${playfair.variable} ${inter.variable}`}
    >
      <body className="min-h-screen bg-bone text-graphite font-sans antialiased">
        {children}
      </body>
    </html>
  );
}