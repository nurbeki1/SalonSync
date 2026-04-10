"use client";

import { motion } from "framer-motion";

interface BrandLogoProps {
  compact?: boolean;
  animated?: boolean;
  showText?: boolean;
}

export default function BrandLogo({
  compact = false,
  animated = true,
  showText = true,
}: BrandLogoProps) {
  return (
    <div className="flex items-center gap-3">
      <motion.svg
        width={compact ? 28 : 38}
        height={compact ? 28 : 38}
        viewBox="0 0 44 44"
        fill="none"
        xmlns="http://www.w3.org/2000/svg"
        animate={
          animated
            ? {
                rotate: [0, 2, -2, 0],
                scale: [1, 1.02, 1],
              }
            : undefined
        }
        transition={{ duration: 4.2, repeat: Infinity, ease: "easeInOut" }}
      >
        <circle cx="22" cy="22" r="19" stroke="#C69B25" strokeWidth="2.8" />
        <circle cx="22" cy="22" r="12.5" stroke="#D8B24A" strokeWidth="1.6" opacity="0.7" />
        <path
          d="M14 18.5C14 18.5 16 15.5 22 15.5C28 15.5 30 18.5 30 18.5"
          stroke="#C69B25"
          strokeWidth="2.4"
          strokeLinecap="round"
        />
        <path
          d="M30 25.5C30 25.5 28 28.5 22 28.5C16 28.5 14 25.5 14 25.5"
          stroke="#C69B25"
          strokeWidth="2.4"
          strokeLinecap="round"
        />
        <circle cx="22" cy="22" r="2.2" fill="#C69B25" />
      </motion.svg>
      {showText && (
        <span className={`${compact ? "text-xl" : "text-3xl"} font-serif font-bold tracking-tight text-[#17181c]`}>
          SalonSync
        </span>
      )}
    </div>
  );
}
