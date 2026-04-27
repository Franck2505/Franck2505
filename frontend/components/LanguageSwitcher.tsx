import { useState } from "react";
import { LANGUAGES, Lang, setLang } from "../lib/i18n";

interface Props {
  current: Lang;
  onChange: (lang: Lang) => void;
  dark?: boolean;
}

export default function LanguageSwitcher({ current, onChange, dark = false }: Props) {
  const [open, setOpen] = useState(false);

  function select(lang: Lang) {
    setLang(lang);
    onChange(lang);
    setOpen(false);
  }

  const textColor = dark ? "text-white" : "text-gray-700";
  const bgHover = dark ? "hover:bg-white/10" : "hover:bg-gray-50";
  const dropdownBg = "bg-white border border-gray-100 shadow-lg";

  return (
    <div className="relative">
      <button
        onClick={() => setOpen(!open)}
        className={`flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-sm font-medium ${bgHover} ${textColor} transition`}
      >
        <span className="text-base">{LANGUAGES[current].flag}</span>
        <span className="hidden sm:inline">{LANGUAGES[current].label}</span>
        <svg className="w-3 h-3 opacity-60" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
        </svg>
      </button>

      {open && (
        <div className={`absolute right-0 mt-1 w-44 rounded-xl ${dropdownBg} py-1 z-50`}>
          {(Object.entries(LANGUAGES) as [Lang, { label: string; flag: string }][]).map(([code, meta]) => (
            <button
              key={code}
              onClick={() => select(code)}
              className={`w-full flex items-center gap-3 px-4 py-2 text-sm text-gray-700 hover:bg-brand-50 hover:text-brand-600 transition ${current === code ? "font-bold text-brand-600" : ""}`}
            >
              <span className="text-base">{meta.flag}</span>
              {meta.label}
              {current === code && <span className="ml-auto text-brand-500">✓</span>}
            </button>
          ))}
        </div>
      )}
    </div>
  );
}
