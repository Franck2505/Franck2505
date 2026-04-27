import { useEffect, useState } from "react";
import { useRouter } from "next/router";
import Link from "next/link";
import { analytics, clients as clientsApi, leads as leadsApi, campaigns as campaignsApi, billing } from "../lib/api";
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, LineChart, Line } from "recharts";

interface Stats {
  total_clients: number;
  total_leads: number;
  new_leads_this_month: number;
  total_emails_sent: number;
  open_rate: number;
  reply_rate: number;
  total_converted: number;
}

interface Client {
  id: string;
  business_name: string;
  sector: string;
  is_active: boolean;
}

const METRIC_CARDS = (s: Stats) => [
  { label: "Leads total", value: s.total_leads, color: "bg-indigo-500" },
  { label: "Leads ce mois", value: s.new_leads_this_month, color: "bg-emerald-500" },
  { label: "Emails envoyés", value: s.total_emails_sent, color: "bg-sky-500" },
  { label: "Taux d'ouverture", value: `${s.open_rate}%`, color: "bg-violet-500" },
  { label: "Taux de réponse", value: `${s.reply_rate}%`, color: "bg-amber-500" },
  { label: "Conversions", value: s.total_converted, color: "bg-rose-500" },
];

export default function Dashboard() {
  const router = useRouter();
  const [stats, setStats] = useState<Stats | null>(null);
  const [clients, setClients] = useState<Client[]>([]);
  const [sub, setSub] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!localStorage.getItem("token")) {
      router.push("/login");
      return;
    }
    Promise.all([
      analytics.dashboard(),
      clientsApi.list(),
      billing.subscription(),
    ]).then(([statsRes, clientsRes, subRes]) => {
      setStats(statsRes.data);
      setClients(clientsRes.data);
      setSub(subRes.data);
    }).finally(() => setLoading(false));
  }, []);

  function logout() {
    localStorage.removeItem("token");
    router.push("/login");
  }

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="w-8 h-8 border-4 border-brand-500 border-t-transparent rounded-full animate-spin" />
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Sidebar */}
      <div className="flex">
        <aside className="w-64 bg-white h-screen border-r border-gray-100 fixed flex flex-col">
          <div className="p-6 border-b border-gray-100">
            <span className="text-lg font-bold text-brand-600">AutoGrowth Pro</span>
          </div>
          <nav className="p-4 flex-1 space-y-1">
            {[
              { href: "/dashboard", label: "Dashboard", icon: "📊" },
              { href: "/dashboard/clients", label: "Clients", icon: "🏢" },
              { href: "/dashboard/leads", label: "Leads", icon: "🎯" },
              { href: "/dashboard/campaigns", label: "Campagnes", icon: "✉️" },
              { href: "/dashboard/billing", label: "Abonnement", icon: "💳" },
            ].map((item) => (
              <Link
                key={item.href}
                href={item.href}
                className="flex items-center gap-3 px-3 py-2 rounded-lg text-gray-600 hover:bg-brand-50 hover:text-brand-600 transition text-sm font-medium"
              >
                <span>{item.icon}</span> {item.label}
              </Link>
            ))}
          </nav>
          <div className="p-4 border-t border-gray-100">
            {sub && (
              <div className="bg-brand-50 rounded-lg p-3 mb-3">
                <div className="text-xs text-brand-600 font-bold uppercase">{sub.plan || "No plan"}</div>
                {sub.leads_used_this_month !== undefined && (
                  <div className="text-xs text-gray-500 mt-1">{sub.leads_used_this_month} leads utilisés</div>
                )}
              </div>
            )}
            <button onClick={logout} className="text-sm text-gray-400 hover:text-gray-600 w-full text-left">
              Déconnexion
            </button>
          </div>
        </aside>

        {/* Main */}
        <main className="ml-64 flex-1 p-8">
          {router.query.checkout === "success" && (
            <div className="bg-emerald-50 border border-emerald-200 text-emerald-700 p-4 rounded-xl mb-6 font-medium">
              🎉 Abonnement activé ! Votre machine de croissance est en marche.
            </div>
          )}

          <div className="flex items-center justify-between mb-8">
            <h1 className="text-2xl font-bold">Vue d'ensemble</h1>
            <span className="text-sm text-gray-400">Mis à jour automatiquement</span>
          </div>

          {stats && (
            <>
              <div className="grid grid-cols-3 gap-4 mb-8">
                {METRIC_CARDS(stats).map((card) => (
                  <div key={card.label} className="bg-white rounded-2xl p-6 border border-gray-100 shadow-sm">
                    <div className={`w-10 h-10 ${card.color} rounded-xl mb-4`} />
                    <div className="text-3xl font-extrabold">{card.value}</div>
                    <div className="text-sm text-gray-500 mt-1">{card.label}</div>
                  </div>
                ))}
              </div>
            </>
          )}

          {/* Clients */}
          <div className="bg-white rounded-2xl border border-gray-100 p-6 shadow-sm mb-6">
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-lg font-bold">Mes clients actifs</h2>
              <Link href="/dashboard/clients" className="text-brand-600 text-sm font-medium hover:underline">
                Gérer →
              </Link>
            </div>
            {clients.length === 0 ? (
              <div className="text-center py-8 text-gray-400">
                <p className="mb-3">Aucun client configuré</p>
                <Link href="/dashboard/clients" className="bg-brand-600 text-white px-4 py-2 rounded-lg text-sm font-medium">
                  Ajouter mon premier client
                </Link>
              </div>
            ) : (
              <div className="space-y-3">
                {clients.map((c) => (
                  <div key={c.id} className="flex items-center justify-between py-3 border-b border-gray-50 last:border-0">
                    <div>
                      <div className="font-medium">{c.business_name}</div>
                      <div className="text-xs text-gray-400 capitalize">{c.sector.replace("_", " ")}</div>
                    </div>
                    <span className="text-xs bg-emerald-50 text-emerald-600 px-2 py-1 rounded-full">Actif</span>
                  </div>
                ))}
              </div>
            )}
          </div>

          <div className="bg-brand-50 border border-brand-100 rounded-2xl p-6">
            <h3 className="font-bold text-brand-800 mb-2">🤖 Automatisations actives</h3>
            <div className="grid grid-cols-2 gap-3 text-sm text-brand-700">
              <div className="flex items-center gap-2"><span className="w-2 h-2 bg-green-500 rounded-full"></span> Génération de leads — chaque nuit à 03h00</div>
              <div className="flex items-center gap-2"><span className="w-2 h-2 bg-green-500 rounded-full"></span> Envoi d'emails — toutes les 30 minutes</div>
              <div className="flex items-center gap-2"><span className="w-2 h-2 bg-green-500 rounded-full"></span> Relances automatiques — J+3, J+7, J+14</div>
              <div className="flex items-center gap-2"><span className="w-2 h-2 bg-green-500 rounded-full"></span> Rapport mensuel — 1er du mois</div>
            </div>
          </div>
        </main>
      </div>
    </div>
  );
}
