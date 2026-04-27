import { useEffect, useState } from "react";
import { useRouter } from "next/router";
import Link from "next/link";
import { billing } from "../../lib/api";

const PLANS = [
  { key: "starter", name: "Starter", price: "299", leads: "100 leads/mois", campaigns: "1 campagne" },
  { key: "growth", name: "Growth", price: "599", leads: "500 leads/mois", campaigns: "5 campagnes", highlight: true },
  { key: "pro", name: "Pro", price: "999", leads: "Leads illimités", campaigns: "Campagnes illimitées" },
];

export default function Billing() {
  const router = useRouter();
  const [sub, setSub] = useState<any>(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (!localStorage.getItem("token")) { router.push("/login"); return; }
    billing.subscription().then((r) => setSub(r.data));
  }, []);

  async function handleUpgrade(plan: string) {
    setLoading(true);
    try {
      const res = await billing.checkout(plan);
      window.location.href = res.data.checkout_url;
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="min-h-screen bg-gray-50 p-8">
      <div className="max-w-4xl mx-auto">
        <div className="mb-8">
          <Link href="/dashboard" className="text-sm text-gray-400 hover:text-gray-600">← Dashboard</Link>
          <h1 className="text-2xl font-bold mt-1">Abonnement</h1>
        </div>

        {sub && sub.plan && (
          <div className="bg-white border border-gray-100 rounded-2xl p-6 shadow-sm mb-8">
            <h2 className="text-lg font-bold mb-4">Abonnement actuel</h2>
            <div className="grid grid-cols-3 gap-4 text-sm">
              <div>
                <div className="text-gray-400">Plan</div>
                <div className="font-bold text-xl text-brand-600 capitalize">{sub.plan}</div>
              </div>
              <div>
                <div className="text-gray-400">Statut</div>
                <div className={`font-medium capitalize ${sub.status === "active" ? "text-emerald-600" : "text-red-500"}`}>
                  {sub.status}
                </div>
              </div>
              <div>
                <div className="text-gray-400">Leads ce mois</div>
                <div className="font-bold">{sub.leads_used_this_month}</div>
              </div>
            </div>
          </div>
        )}

        <h2 className="text-xl font-bold mb-4">Changer de plan</h2>
        <div className="grid md:grid-cols-3 gap-6">
          {PLANS.map((plan) => (
            <div
              key={plan.key}
              className={`bg-white border-2 rounded-2xl p-6 ${plan.highlight ? "border-brand-500 shadow-lg" : "border-gray-100"}`}
            >
              {plan.highlight && (
                <div className="bg-brand-600 text-white text-xs font-bold px-2 py-1 rounded-full inline-block mb-3">RECOMMANDÉ</div>
              )}
              <h3 className="text-xl font-bold">{plan.name}</h3>
              <div className="text-3xl font-extrabold mt-1 mb-1">€{plan.price}<span className="text-base font-normal text-gray-400">/mois</span></div>
              <p className="text-sm text-gray-500 mb-2">{plan.leads}</p>
              <p className="text-sm text-gray-500 mb-6">{plan.campaigns}</p>
              <button
                onClick={() => handleUpgrade(plan.key)}
                disabled={loading || sub?.plan === plan.key}
                className={`w-full py-2.5 rounded-xl font-bold transition ${
                  sub?.plan === plan.key
                    ? "bg-gray-100 text-gray-400 cursor-not-allowed"
                    : plan.highlight
                    ? "bg-brand-600 text-white hover:bg-brand-700"
                    : "bg-gray-100 text-gray-700 hover:bg-gray-200"
                }`}
              >
                {sub?.plan === plan.key ? "Plan actuel" : `Passer au ${plan.name}`}
              </button>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
