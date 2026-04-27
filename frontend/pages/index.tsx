import Head from "next/head";
import Link from "next/link";

const PLANS = [
  {
    name: "Starter",
    price: "299",
    leads: "100 leads/mois",
    campaigns: "1 campagne",
    features: ["Génération de leads automatique", "Prospection email IA", "Dashboard analytics", "Support email"],
    cta: "starter",
    highlight: false,
  },
  {
    name: "Growth",
    price: "599",
    leads: "500 leads/mois",
    campaigns: "5 campagnes",
    features: ["Tout Starter +", "Création de contenu IA", "Séquences email multi-étapes", "Rapports mensuels auto", "Support prioritaire"],
    cta: "growth",
    highlight: true,
  },
  {
    name: "Pro",
    price: "999",
    leads: "Leads illimités",
    campaigns: "Campagnes illimitées",
    features: ["Tout Growth +", "Posts LinkedIn automatiques", "Scoring leads IA avancé", "Intégrations CRM", "Support dédié 24/7"],
    cta: "pro",
    highlight: false,
  },
];

const STATS = [
  { value: "47%", label: "Taux d'ouverture moyen" },
  { value: "8.3%", label: "Taux de réponse moyen" },
  { value: "€2,400", label: "Valeur client moyenne" },
  { value: "72h", label: "Délai premier lead" },
];

const HOW_IT_WORKS = [
  { step: "01", title: "Configurez votre cible", desc: "Secteur, zone géographique, mots-clés — notre IA sait exactement où chercher." },
  { step: "02", title: "L'IA génère vos leads", desc: "Google Maps, annuaires, bases de données — scraping automatique chaque nuit." },
  { step: "03", title: "Emails personnalisés envoyés", desc: "Séquences de 4 emails ultra-personnalisés générés et envoyés automatiquement." },
  { step: "04", title: "Vous récoltez les réponses", desc: "Les prospects intéressés répondent directement. Vous n'avez plus qu'à closer." },
];

export default function Landing() {
  return (
    <>
      <Head>
        <title>AutoGrowth Pro — Prospection B2B 100% automatisée</title>
        <meta name="description" content="Générez des leads qualifiés et envoyez des emails de prospection personnalisés en pilote automatique. 30-100 clients actifs. Résultats en 72h." />
      </Head>

      <nav className="bg-white border-b border-gray-100 sticky top-0 z-50">
        <div className="max-w-6xl mx-auto px-4 py-4 flex items-center justify-between">
          <span className="text-xl font-bold text-brand-600">AutoGrowth Pro</span>
          <div className="flex gap-4 items-center">
            <Link href="/login" className="text-gray-600 hover:text-gray-900 text-sm">Connexion</Link>
            <Link href="/register" className="bg-brand-600 text-white px-4 py-2 rounded-lg text-sm font-medium hover:bg-brand-700 transition">
              Démarrer gratuitement
            </Link>
          </div>
        </div>
      </nav>

      {/* Hero */}
      <section className="bg-gradient-to-br from-brand-600 to-indigo-800 text-white py-24">
        <div className="max-w-4xl mx-auto px-4 text-center">
          <div className="inline-block bg-white/10 text-white text-sm px-4 py-1 rounded-full mb-6">
            🤖 100% automatisé — Aucun commercial requis
          </div>
          <h1 className="text-5xl font-extrabold mb-6 leading-tight">
            Votre machine à leads B2B<br />tourne pendant que vous dormez
          </h1>
          <p className="text-xl text-indigo-100 mb-10 max-w-2xl mx-auto">
            AutoGrowth Pro génère des leads qualifiés, envoie des emails de prospection personnalisés
            et relance automatiquement — sans lever le petit doigt.
          </p>
          <div className="flex gap-4 justify-center flex-wrap">
            <Link href="/register" className="bg-white text-brand-600 px-8 py-4 rounded-xl font-bold text-lg hover:shadow-lg transition">
              Essai gratuit 14 jours →
            </Link>
            <Link href="#how-it-works" className="bg-white/10 text-white px-8 py-4 rounded-xl font-bold text-lg hover:bg-white/20 transition">
              Voir comment ça marche
            </Link>
          </div>
          <p className="mt-4 text-indigo-200 text-sm">Sans carte bancaire • Résultats en 72h</p>
        </div>
      </section>

      {/* Stats */}
      <section className="bg-white py-16">
        <div className="max-w-4xl mx-auto px-4 grid grid-cols-2 md:grid-cols-4 gap-8">
          {STATS.map((s) => (
            <div key={s.value} className="text-center">
              <div className="text-4xl font-extrabold text-brand-600">{s.value}</div>
              <div className="text-gray-500 mt-1 text-sm">{s.label}</div>
            </div>
          ))}
        </div>
      </section>

      {/* How it works */}
      <section id="how-it-works" className="py-20 bg-gray-50">
        <div className="max-w-5xl mx-auto px-4">
          <h2 className="text-3xl font-extrabold text-center mb-12">Comment ça fonctionne</h2>
          <div className="grid md:grid-cols-2 gap-8">
            {HOW_IT_WORKS.map((h) => (
              <div key={h.step} className="bg-white p-8 rounded-2xl border border-gray-100 shadow-sm">
                <div className="text-4xl font-extrabold text-brand-100 mb-3">{h.step}</div>
                <h3 className="text-xl font-bold mb-2">{h.title}</h3>
                <p className="text-gray-500">{h.desc}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Pricing */}
      <section id="pricing" className="py-20 bg-white">
        <div className="max-w-5xl mx-auto px-4">
          <h2 className="text-3xl font-extrabold text-center mb-4">Tarifs transparents</h2>
          <p className="text-center text-gray-500 mb-12">Annulez à tout moment. Pas de frais cachés.</p>
          <div className="grid md:grid-cols-3 gap-8">
            {PLANS.map((plan) => (
              <div
                key={plan.name}
                className={`rounded-2xl p-8 border-2 flex flex-col ${
                  plan.highlight
                    ? "border-brand-500 shadow-xl scale-105"
                    : "border-gray-100"
                }`}
              >
                {plan.highlight && (
                  <div className="bg-brand-600 text-white text-xs font-bold px-3 py-1 rounded-full self-start mb-4">
                    PLUS POPULAIRE
                  </div>
                )}
                <h3 className="text-2xl font-bold">{plan.name}</h3>
                <div className="mt-2 mb-1">
                  <span className="text-4xl font-extrabold">€{plan.price}</span>
                  <span className="text-gray-400">/mois</span>
                </div>
                <p className="text-brand-600 font-medium text-sm mb-6">{plan.leads} • {plan.campaigns}</p>
                <ul className="space-y-3 flex-1">
                  {plan.features.map((f) => (
                    <li key={f} className="flex items-start gap-2 text-sm text-gray-600">
                      <span className="text-green-500 font-bold mt-0.5">✓</span> {f}
                    </li>
                  ))}
                </ul>
                <Link
                  href={`/register?plan=${plan.cta}`}
                  className={`mt-8 text-center py-3 rounded-xl font-bold transition ${
                    plan.highlight
                      ? "bg-brand-600 text-white hover:bg-brand-700"
                      : "bg-gray-100 text-gray-800 hover:bg-gray-200"
                  }`}
                >
                  Démarrer — {plan.name}
                </Link>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* CTA */}
      <section className="bg-brand-600 py-20 text-white text-center">
        <h2 className="text-3xl font-extrabold mb-4">Prêt à automatiser votre croissance ?</h2>
        <p className="text-indigo-100 mb-8">Rejoignez les entreprises qui prospectent 24h/24 sans effort.</p>
        <Link href="/register" className="bg-white text-brand-600 px-8 py-4 rounded-xl font-bold text-lg hover:shadow-lg transition">
          Commencer l'essai gratuit →
        </Link>
      </section>

      <footer className="bg-gray-900 text-gray-400 py-8 text-center text-sm">
        © 2025 AutoGrowth Pro — Tous droits réservés
      </footer>
    </>
  );
}
