import { useState, useEffect } from "react";
import Head from "next/head";
import Link from "next/link";
import LanguageSwitcher from "../components/LanguageSwitcher";
import { Lang, detectLang, t, PLAN_PRICES, formatPrice, COUNTRY_DEFAULTS, CURRENCY_SYMBOLS } from "../lib/i18n";

const COUNTRIES = [
  { code: "FR", name: "France", currency: "EUR" },
  { code: "DE", name: "Deutschland", currency: "EUR" },
  { code: "ES", name: "España", currency: "EUR" },
  { code: "IT", name: "Italia", currency: "EUR" },
  { code: "GB", name: "United Kingdom", currency: "GBP" },
  { code: "US", name: "United States", currency: "USD" },
  { code: "CA", name: "Canada", currency: "CAD" },
  { code: "AU", name: "Australia", currency: "AUD" },
  { code: "BR", name: "Brasil", currency: "BRL" },
  { code: "CH", name: "Schweiz", currency: "CHF" },
  { code: "BE", name: "Belgique", currency: "EUR" },
  { code: "PT", name: "Portugal", currency: "EUR" },
  { code: "NL", name: "Nederland", currency: "EUR" },
];

const PLAN_KEYS = ["starter", "growth", "pro"] as const;

export default function Landing() {
  const [lang, setLang] = useState<Lang>("fr");
  const [currency, setCurrency] = useState("EUR");
  const [country, setCountry] = useState("FR");

  useEffect(() => {
    const detected = detectLang();
    setLang(detected);
    const cd = Object.values(COUNTRY_DEFAULTS).find((_, i) => Object.keys(COUNTRY_DEFAULTS)[i] === "FR");
    const browserLang = detected;
    // Try to guess currency from lang
    const entry = Object.entries(COUNTRY_DEFAULTS).find(([, v]) => v.lang === browserLang);
    if (entry) {
      setCountry(entry[0]);
      setCurrency(entry[1].currency);
    }
  }, []);

  function handleCountryChange(e: React.ChangeEvent<HTMLSelectElement>) {
    const c = e.target.value;
    setCountry(c);
    const cfg = COUNTRY_DEFAULTS[c];
    if (cfg) {
      setCurrency(cfg.currency);
      setLang(cfg.lang);
    }
  }

  const prices = PLAN_PRICES[currency] || PLAN_PRICES["EUR"];

  return (
    <>
      <Head>
        <title>AutoGrowth Pro — {t(lang, "hero.title")}</title>
        <meta name="description" content={t(lang, "hero.subtitle")} />
        <meta name="viewport" content="width=device-width, initial-scale=1" />
        <link rel="alternate" hrefLang="fr" href="/?lang=fr" />
        <link rel="alternate" hrefLang="en" href="/?lang=en" />
        <link rel="alternate" hrefLang="es" href="/?lang=es" />
        <link rel="alternate" hrefLang="de" href="/?lang=de" />
        <link rel="alternate" hrefLang="it" href="/?lang=it" />
        <link rel="alternate" hrefLang="pt" href="/?lang=pt" />
        <link rel="alternate" hrefLang="x-default" href="/" />
      </Head>

      {/* Nav */}
      <nav className="bg-white border-b border-gray-100 sticky top-0 z-50">
        <div className="max-w-6xl mx-auto px-4 py-4 flex items-center justify-between">
          <span className="text-xl font-bold text-brand-600">AutoGrowth Pro</span>
          <div className="flex gap-2 items-center">
            {/* Country + currency picker */}
            <select
              value={country}
              onChange={handleCountryChange}
              className="text-sm border border-gray-200 rounded-lg px-2 py-1.5 focus:outline-none focus:ring-1 focus:ring-brand-500 hidden md:block"
            >
              {COUNTRIES.map((c) => (
                <option key={c.code} value={c.code}>{c.name}</option>
              ))}
            </select>
            <LanguageSwitcher current={lang} onChange={setLang} />
            <Link href="/login" className="text-gray-600 hover:text-gray-900 text-sm px-3 py-1.5">
              {t(lang, "nav.login")}
            </Link>
            <Link href={`/register?country=${country}&lang=${lang}`} className="bg-brand-600 text-white px-4 py-2 rounded-lg text-sm font-medium hover:bg-brand-700 transition">
              {t(lang, "nav.start")}
            </Link>
          </div>
        </div>
      </nav>

      {/* Hero */}
      <section className="bg-gradient-to-br from-brand-600 to-indigo-800 text-white py-24">
        <div className="max-w-4xl mx-auto px-4 text-center">
          <div className="inline-block bg-white/10 text-white text-sm px-4 py-1 rounded-full mb-6">
            🤖 {t(lang, "hero.badge")}
          </div>
          <h1 className="text-4xl md:text-5xl font-extrabold mb-6 leading-tight">
            {t(lang, "hero.title")}
          </h1>
          <p className="text-xl text-indigo-100 mb-10 max-w-2xl mx-auto">
            {t(lang, "hero.subtitle")}
          </p>
          <div className="flex gap-4 justify-center flex-wrap">
            <Link href={`/register?country=${country}&lang=${lang}`} className="bg-white text-brand-600 px-8 py-4 rounded-xl font-bold text-lg hover:shadow-lg transition">
              {t(lang, "hero.cta_primary")}
            </Link>
            <a href="#how-it-works" className="bg-white/10 text-white px-8 py-4 rounded-xl font-bold text-lg hover:bg-white/20 transition">
              {t(lang, "hero.cta_secondary")}
            </a>
          </div>
          <p className="mt-4 text-indigo-200 text-sm">{t(lang, "hero.no_card")}</p>
        </div>
      </section>

      {/* Stats */}
      <section className="bg-white py-16">
        <div className="max-w-4xl mx-auto px-4 grid grid-cols-2 md:grid-cols-4 gap-8">
          {[
            { value: "47%", key: "open_rate" },
            { value: "8.3%", key: "reply_rate" },
            { value: formatPrice(2400, currency), key: "avg_value" },
            { value: "72h", key: "first_lead" },
          ].map((s) => (
            <div key={s.key} className="text-center">
              <div className="text-4xl font-extrabold text-brand-600">{s.value}</div>
              <div className="text-gray-500 mt-1 text-sm">{t(lang, `stats.${s.key}`)}</div>
            </div>
          ))}
        </div>
      </section>

      {/* How it works */}
      <section id="how-it-works" className="py-20 bg-gray-50">
        <div className="max-w-5xl mx-auto px-4">
          <h2 className="text-3xl font-extrabold text-center mb-12">{t(lang, "how.title")}</h2>
          <div className="grid md:grid-cols-2 gap-8">
            {([0, 1, 2, 3] as const).map((i) => (
              <div key={i} className="bg-white p-8 rounded-2xl border border-gray-100 shadow-sm">
                <div className="text-4xl font-extrabold text-brand-100 mb-3">
                  {String(i + 1).padStart(2, "0")}
                </div>
                <h3 className="text-xl font-bold mb-2">{t(lang, `how.steps.${i}.title`)}</h3>
                <p className="text-gray-500">{t(lang, `how.steps.${i}.desc`)}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Pricing */}
      <section id="pricing" className="py-20 bg-white">
        <div className="max-w-5xl mx-auto px-4">
          <h2 className="text-3xl font-extrabold text-center mb-4">{t(lang, "pricing.title")}</h2>
          <p className="text-center text-gray-500 mb-12">{t(lang, "pricing.subtitle")}</p>
          <div className="grid md:grid-cols-3 gap-8">
            {PLAN_KEYS.map((plan, idx) => {
              const highlight = idx === 1;
              return (
                <div
                  key={plan}
                  className={`rounded-2xl p-8 border-2 flex flex-col ${highlight ? "border-brand-500 shadow-xl scale-105" : "border-gray-100"}`}
                >
                  {highlight && (
                    <div className="bg-brand-600 text-white text-xs font-bold px-3 py-1 rounded-full self-start mb-4">
                      {t(lang, "pricing.popular")}
                    </div>
                  )}
                  <h3 className="text-2xl font-bold">{t(lang, `plans.${plan}.name`)}</h3>
                  <div className="mt-2 mb-1">
                    <span className="text-4xl font-extrabold">{formatPrice(prices[plan], currency)}</span>
                    <span className="text-gray-400">{t(lang, "pricing.per_month")}</span>
                  </div>
                  <p className="text-brand-600 font-medium text-sm mb-6">
                    {t(lang, `plans.${plan}.leads`)} · {t(lang, `plans.${plan}.campaigns`)}
                  </p>
                  <ul className="space-y-3 flex-1">
                    {([0, 1, 2, 3, 4] as const).map((fi) => {
                      const feat = t(lang, `plans.${plan}.features.${fi}`);
                      if (feat === `plans.${plan}.features.${fi}`) return null;
                      return (
                        <li key={fi} className="flex items-start gap-2 text-sm text-gray-600">
                          <span className="text-green-500 font-bold mt-0.5">✓</span> {feat}
                        </li>
                      );
                    })}
                  </ul>
                  <Link
                    href={`/register?plan=${plan}&country=${country}&lang=${lang}`}
                    className={`mt-8 text-center py-3 rounded-xl font-bold transition ${
                      highlight ? "bg-brand-600 text-white hover:bg-brand-700" : "bg-gray-100 text-gray-800 hover:bg-gray-200"
                    }`}
                  >
                    {t(lang, "pricing.cta", { plan: t(lang, `plans.${plan}.name`) })}
                  </Link>
                </div>
              );
            })}
          </div>
        </div>
      </section>

      {/* CTA */}
      <section className="bg-brand-600 py-20 text-white text-center">
        <h2 className="text-3xl font-extrabold mb-4">{t(lang, "cta_section.title")}</h2>
        <p className="text-indigo-100 mb-8">{t(lang, "cta_section.subtitle")}</p>
        <Link href={`/register?country=${country}&lang=${lang}`} className="bg-white text-brand-600 px-8 py-4 rounded-xl font-bold text-lg hover:shadow-lg transition">
          {t(lang, "cta_section.button")}
        </Link>
      </section>

      <footer className="bg-gray-900 text-gray-400 py-8 text-center text-sm">
        <p>© 2025 AutoGrowth Pro · <Link href="/?lang=fr" className="hover:text-white">FR</Link> · <Link href="/?lang=en" className="hover:text-white">EN</Link> · <Link href="/?lang=es" className="hover:text-white">ES</Link> · <Link href="/?lang=de" className="hover:text-white">DE</Link> · <Link href="/?lang=it" className="hover:text-white">IT</Link> · <Link href="/?lang=pt" className="hover:text-white">PT</Link></p>
      </footer>
    </>
  );
}
