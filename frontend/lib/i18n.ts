import fr from "../locales/fr.json";
import en from "../locales/en.json";
import es from "../locales/es.json";
import de from "../locales/de.json";
import it from "../locales/it.json";
import pt from "../locales/pt.json";

export type Lang = "fr" | "en" | "es" | "de" | "it" | "pt";

const locales: Record<Lang, any> = { fr, en, es, de, it, pt };

export const LANGUAGES: Record<Lang, { label: string; flag: string }> = {
  fr: { label: "Français",   flag: "🇫🇷" },
  en: { label: "English",    flag: "🇬🇧" },
  es: { label: "Español",    flag: "🇪🇸" },
  de: { label: "Deutsch",    flag: "🇩🇪" },
  it: { label: "Italiano",   flag: "🇮🇹" },
  pt: { label: "Português",  flag: "🇧🇷" },
};

export const COUNTRY_DEFAULTS: Record<string, { lang: Lang; currency: string }> = {
  FR: { lang: "fr", currency: "EUR" },
  BE: { lang: "fr", currency: "EUR" },
  CH: { lang: "fr", currency: "CHF" },
  DE: { lang: "de", currency: "EUR" },
  AT: { lang: "de", currency: "EUR" },
  ES: { lang: "es", currency: "EUR" },
  MX: { lang: "es", currency: "USD" },
  IT: { lang: "it", currency: "EUR" },
  PT: { lang: "pt", currency: "EUR" },
  BR: { lang: "pt", currency: "BRL" },
  GB: { lang: "en", currency: "GBP" },
  US: { lang: "en", currency: "USD" },
  CA: { lang: "en", currency: "CAD" },
  AU: { lang: "en", currency: "AUD" },
};

export const PLAN_PRICES: Record<string, Record<string, number>> = {
  EUR: { starter: 299,  growth: 599,  pro: 999  },
  USD: { starter: 329,  growth: 649,  pro: 1099 },
  GBP: { starter: 249,  growth: 499,  pro: 849  },
  CAD: { starter: 449,  growth: 899,  pro: 1499 },
  AUD: { starter: 499,  growth: 999,  pro: 1699 },
  BRL: { starter: 1690, growth: 3390, pro: 5690 },
  CHF: { starter: 299,  growth: 599,  pro: 999  },
};

export const CURRENCY_SYMBOLS: Record<string, string> = {
  EUR: "€", USD: "$", GBP: "£", CAD: "CA$", AUD: "A$", BRL: "R$", CHF: "Fr.",
};

export function formatPrice(amount: number, currency: string): string {
  const sym = CURRENCY_SYMBOLS[currency] || currency;
  const before = ["USD", "GBP", "CAD", "AUD", "BRL", "CHF"].includes(currency);
  const formatted = amount.toLocaleString();
  return before ? `${sym}${formatted}` : `${formatted} ${sym}`;
}

export function detectLang(): Lang {
  if (typeof window === "undefined") return "fr";
  const stored = localStorage.getItem("lang") as Lang;
  if (stored && locales[stored]) return stored;
  const browser = navigator.language.slice(0, 2) as Lang;
  return locales[browser] ? browser : "fr";
}

export function setLang(lang: Lang) {
  if (typeof window !== "undefined") localStorage.setItem("lang", lang);
}

export function t(lang: Lang, path: string, vars?: Record<string, string>): string {
  const keys = path.split(".");
  let val: any = locales[lang] || locales.fr;
  for (const k of keys) {
    val = val?.[k];
    if (val === undefined) break;
  }
  if (typeof val !== "string") return path;
  if (vars) return Object.entries(vars).reduce((s, [k, v]) => s.replace(`{${k}}`, v), val);
  return val;
}
