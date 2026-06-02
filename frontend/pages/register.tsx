import { useState, useEffect } from "react";
import { useRouter } from "next/router";
import Link from "next/link";
import { auth, billing } from "../lib/api";
import { Lang, detectLang, t, PLAN_PRICES, formatPrice, COUNTRY_DEFAULTS } from "../lib/i18n";
import LanguageSwitcher from "../components/LanguageSwitcher";

const PLAN_LABELS = (lang: Lang, currency: string) => ({
  starter: `${t(lang, "plans.starter.name")} — ${formatPrice(PLAN_PRICES[currency]?.starter || 299, currency)}/mois`,
  growth:  `${t(lang, "plans.growth.name")}  — ${formatPrice(PLAN_PRICES[currency]?.growth  || 599, currency)}/mois`,
  pro:     `${t(lang, "plans.pro.name")}     — ${formatPrice(PLAN_PRICES[currency]?.pro     || 999, currency)}/mois`,
});

const COUNTRIES = [
  { code: "FR", name: "France" }, { code: "DE", name: "Deutschland" },
  { code: "ES", name: "España" }, { code: "IT", name: "Italia" },
  { code: "GB", name: "United Kingdom" }, { code: "US", name: "United States" },
  { code: "CA", name: "Canada" }, { code: "AU", name: "Australia" },
  { code: "BR", name: "Brasil" }, { code: "CH", name: "Schweiz/Suisse" },
  { code: "BE", name: "Belgique" }, { code: "PT", name: "Portugal" },
  { code: "NL", name: "Nederland" }, { code: "MX", name: "México" },
  { code: "AR", name: "Argentina" }, { code: "CO", name: "Colombia" },
  { code: "SG", name: "Singapore" }, { code: "AE", name: "UAE" },
  { code: "ZA", name: "South Africa" }, { code: "IN", name: "India" },
];

export default function Register() {
  const router = useRouter();
  const plan = (router.query.plan as string) || "starter";
  const queryCountry = (router.query.country as string) || "FR";
  const queryLang = router.query.lang as Lang;

  const [lang, setLang] = useState<Lang>("fr");
  const [currency, setCurrency] = useState("EUR");
  const [form, setForm] = useState({ email: "", password: "", full_name: "", country: queryCountry });
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    const l = queryLang || detectLang();
    setLang(l);
    const cfg = COUNTRY_DEFAULTS[queryCountry];
    if (cfg) setCurrency(cfg.currency);
  }, [queryCountry, queryLang]);

  function handleCountryChange(country: string) {
    setForm({ ...form, country });
    const cfg = COUNTRY_DEFAULTS[country];
    if (cfg) {
      setCurrency(cfg.currency);
      setLang(cfg.lang);
    }
  }

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setLoading(true);
    setError("");
    try {
      const res = await auth.register(form.email, form.password, form.full_name, form.country, lang);
      localStorage.setItem("token", res.data.access_token);
      localStorage.setItem("lang", lang);
      const checkout = await billing.checkout(plan);
      window.location.href = checkout.data.checkout_url;
    } catch (err: any) {
      setError(err.response?.data?.detail || "Error during registration.");
    } finally {
      setLoading(false);
    }
  }

  const planLabels = PLAN_LABELS(lang, currency);

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50 py-8 px-4">
      <div className="bg-white w-full max-w-md p-8 rounded-2xl shadow-sm border border-gray-100">
        <div className="flex items-center justify-between mb-6">
          <Link href="/" className="text-xl font-bold text-brand-600">AutoGrowth Pro</Link>
          <LanguageSwitcher current={lang} onChange={setLang} />
        </div>

        <div className="bg-brand-50 border border-brand-100 rounded-lg p-3 mb-6 text-sm text-brand-700 font-medium">
          {planLabels[plan as keyof typeof planLabels] || plan}
        </div>

        <h1 className="text-2xl font-bold mb-6">{t(lang, "auth.register_title")}</h1>
        {error && <div className="bg-red-50 text-red-600 p-3 rounded-lg mb-4 text-sm">{error}</div>}
        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="block text-sm font-medium mb-1">{t(lang, "auth.full_name")}</label>
            <input
              value={form.full_name}
              onChange={(e) => setForm({ ...form, full_name: e.target.value })}
              className="w-full border border-gray-200 rounded-lg px-4 py-2.5 focus:outline-none focus:ring-2 focus:ring-brand-500"
              required
            />
          </div>
          <div>
            <label className="block text-sm font-medium mb-1">{t(lang, "auth.email")}</label>
            <input
              type="email"
              value={form.email}
              onChange={(e) => setForm({ ...form, email: e.target.value })}
              className="w-full border border-gray-200 rounded-lg px-4 py-2.5 focus:outline-none focus:ring-2 focus:ring-brand-500"
              required
            />
          </div>
          <div>
            <label className="block text-sm font-medium mb-1">{t(lang, "auth.password")}</label>
            <input
              type="password"
              value={form.password}
              onChange={(e) => setForm({ ...form, password: e.target.value })}
              className="w-full border border-gray-200 rounded-lg px-4 py-2.5 focus:outline-none focus:ring-2 focus:ring-brand-500"
              required
              minLength={8}
            />
          </div>
          <div>
            <label className="block text-sm font-medium mb-1">
              {lang === "fr" ? "Pays" : lang === "de" ? "Land" : lang === "es" ? "País" : lang === "it" ? "Paese" : lang === "pt" ? "País" : "Country"}
            </label>
            <select
              value={form.country}
              onChange={(e) => handleCountryChange(e.target.value)}
              className="w-full border border-gray-200 rounded-lg px-4 py-2.5 focus:outline-none focus:ring-2 focus:ring-brand-500"
            >
              {COUNTRIES.map((c) => (
                <option key={c.code} value={c.code}>{c.name}</option>
              ))}
            </select>
          </div>
          <button
            type="submit"
            disabled={loading}
            className="w-full bg-brand-600 text-white py-3 rounded-lg font-bold hover:bg-brand-700 disabled:opacity-50 transition"
          >
            {loading ? "..." : t(lang, "auth.register_btn")}
          </button>
        </form>
        <p className="text-center mt-4 text-xs text-gray-400">
          {lang === "fr" ? "En créant un compte vous acceptez nos CGU. Annulable à tout moment." :
           lang === "de" ? "Mit der Anmeldung stimmen Sie unseren AGB zu. Jederzeit kündbar." :
           "By creating an account you agree to our Terms. Cancel anytime."}
        </p>
        <p className="text-center mt-2 text-sm text-gray-500">
          {t(lang, "auth.has_account")}{" "}
          <Link href="/login" className="text-brand-600 font-medium">{t(lang, "auth.login_link")}</Link>
        </p>
      </div>
    </div>
  );
}
