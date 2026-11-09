import Image from "next/image";

import { cn } from "@/lib/utils";

/** Decorative mark. Its parent owns the accessible loading message. */
export function BrandLoader({ compact = false }: { compact?: boolean }) {
  return (
    <span className={cn("brand-loader", compact && "brand-loader--compact")} aria-hidden="true">
      <span className="brand-loader__halo" />
      <span className="brand-loader__orbit" />
      <span className="brand-loader__dot brand-loader__dot--herb" />
      <span className="brand-loader__dot brand-loader__dot--terra" />
      <span className="brand-loader__dot brand-loader__dot--gold" />
      {compact ? (
        <Image
          src="/brand/ratatouille-ai.svg"
          alt=""
          width={128}
          height={128}
          className="brand-loader__logo"
          loading="eager"
        />
      ) : (
        <svg className="brand-loader__scene" viewBox="0 0 160 144" fill="none" focusable="false">
          <ellipse cx="85" cy="132" rx="65" ry="4" fill="var(--herb)" opacity=".08" />
          <image href="/brand/ratatouille-ai.svg" x="0" y="9" width="110" height="110" />
          <g
            className="cooking-steam"
            stroke="var(--primary)"
            strokeWidth="2.5"
            strokeLinecap="round"
          >
            <path d="M108 77c-8-8 5-10-1-20" />
            <path d="M123 75c-7-8 6-12 0-22" />
            <path d="M137 78c-7-7 5-10 0-17" />
          </g>
          <path
            d="M99 91c-14-2-17 8-6 13m52-13c14-2 17 8 6 13"
            stroke="var(--primary)"
            strokeWidth="5"
            strokeLinecap="round"
          />
          <ellipse cx="122" cy="90" rx="29" ry="8" fill="var(--primary)" />
          <ellipse cx="122" cy="89" rx="24" ry="5" fill="#E8BB69" />
          <g
            className="cooking-soup"
            stroke="var(--primary)"
            strokeWidth="1.5"
            strokeLinecap="round"
          >
            <path d="M104 90c7-4 21-4 32-1m-26 3c6 2 15 2 22-1" />
          </g>
          <g className="cooking-arm">
            <path d="m115 60 10 40" stroke="#795600" strokeWidth="4" strokeLinecap="round" />
            <ellipse
              cx="125"
              cy="100"
              rx="4"
              ry="6"
              fill="#795600"
              transform="rotate(-14 125 100)"
            />
            <path
              d="M69 80c15 1 24-9 43-10"
              stroke="var(--herb)"
              strokeWidth="9"
              strokeLinecap="round"
            />
            <path d="m111 70 6-1" stroke="var(--herb)" strokeWidth="11" strokeLinecap="round" />
          </g>
          <path d="M93 91c1 23 9 36 29 36s28-13 29-36c-14 7-44 7-58 0Z" fill="var(--primary)" />
          <path
            d="M102 102c1 8 4 13 10 16"
            stroke="#FAF8F5"
            strokeWidth="3"
            strokeLinecap="round"
            opacity=".55"
          />
          <path
            d="m104 126-2 5m38-5 2 5"
            stroke="var(--primary)"
            strokeWidth="5"
            strokeLinecap="round"
          />
          <g className="cooking-bubbles" fill="#E8BB69">
            <circle cx="105" cy="86" r="2.5" />
            <circle cx="137" cy="85" r="2" />
          </g>
        </svg>
      )}
    </span>
  );
}
