import { useEffect, useState } from "react";
import { useRouter } from "next/router";
import Link from "next/link";
import { clients as clientsApi } from "../../lib/api";

const SECTORS = [
  { value: "real_estate", label: "Immobilier" },
  { value: "restaurants", label: "Restauration" },
  { value: "healthcare", label: "Santé" },
  { value: "legal", label: "Juridique" },
  { value: "accounting", label: "Comptabilité" },
  { value: "construction", label: "Construction/BTP" },
  { value: "retail", label: "Commerce de détail" },
  { value: "it_services", label: "Services IT" },
  { value: "coaching", label: "Coaching" },
  { value: "other", label: "Autre" },
];

export default function Clients() {
  const router = useRouter();
  const [clientsList, setClientsList] = useState<any[]>([]);
  const [showForm, setShowForm] = useState(false);
  const [form, setForm] = useState({ business_name: "", sector: "real_estate", target_location: "France", target_keywords: "" });
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (!localStorage.getItem("token")) { router.push("/login"); return; }
    clientsApi.list().then((r) => setClientsList(r.data));
  }, []);

  async function handleCreate(e: React.FormEvent) {
    e.preventDefault();
    setLoading(true);
    try {
      await clientsApi.create({
        ...form,
        target_keywords: form.target_keywords.split(",").map((k) => k.trim()).filter(Boolean),
      });
      const r = await clientsApi.list();
      setClientsList(r.data);
      setShowForm(false);
      setForm({ business_name: "", sector: "real_estate", target_location: "France", target_keywords: "" });
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="min-h-screen bg-gray-50 p-8 ml-0">
      <div className="max-w-4xl mx-auto">
        <div className="flex items-center justify-between mb-8">
          <div>
            <Link href="/dashboard" className="text-sm text-gray-400 hover:text-gray-600">← Dashboard</Link>
            <h1 className="text-2xl font-bold mt-1">Clients</h1>
          </div>
          <button
            onClick={() => setShowForm(!showForm)}
            className="bg-brand-600 text-white px-4 py-2 rounded-lg font-medium hover:bg-brand-700 transition"
          >
            + Ajouter un client
          </button>
        </div>

        {showForm && (
          <div className="bg-white border border-gray-100 rounded-2xl p-6 mb-6 shadow-sm">
            <h2 className="text-lg font-bold mb-4">Nouveau client</h2>
            <form onSubmit={handleCreate} className="grid grid-cols-2 gap-4">
              <div className="col-span-2">
                <label className="block text-sm font-medium mb-1">Nom de l'entreprise</label>
                <input
                  value={form.business_name}
                  onChange={(e) => setForm({ ...form, business_name: e.target.value })}
                  className="w-full border border-gray-200 rounded-lg px-4 py-2.5 focus:outline-none focus:ring-2 focus:ring-brand-500"
                  required
                />
              </div>
              <div>
                <label className="block text-sm font-medium mb-1">Secteur</label>
                <select
                  value={form.sector}
                  onChange={(e) => setForm({ ...form, sector: e.target.value })}
                  className="w-full border border-gray-200 rounded-lg px-4 py-2.5 focus:outline-none focus:ring-2 focus:ring-brand-500"
                >
                  {SECTORS.map((s) => <option key={s.value} value={s.value}>{s.label}</option>)}
                </select>
              </div>
              <div>
                <label className="block text-sm font-medium mb-1">Zone géographique</label>
                <input
                  value={form.target_location}
                  onChange={(e) => setForm({ ...form, target_location: e.target.value })}
                  className="w-full border border-gray-200 rounded-lg px-4 py-2.5 focus:outline-none focus:ring-2 focus:ring-brand-500"
                  placeholder="Ex: Paris, Lyon, France"
                />
              </div>
              <div className="col-span-2">
                <label className="block text-sm font-medium mb-1">Mots-clés cibles (séparés par des virgules)</label>
                <input
                  value={form.target_keywords}
                  onChange={(e) => setForm({ ...form, target_keywords: e.target.value })}
                  className="w-full border border-gray-200 rounded-lg px-4 py-2.5 focus:outline-none focus:ring-2 focus:ring-brand-500"
                  placeholder="Ex: agence immobilière, promoteur, chasseur immobilier"
                />
              </div>
              <div className="col-span-2 flex gap-3">
                <button type="submit" disabled={loading} className="bg-brand-600 text-white px-6 py-2 rounded-lg font-medium hover:bg-brand-700 disabled:opacity-50 transition">
                  {loading ? "Création…" : "Créer le client"}
                </button>
                <button type="button" onClick={() => setShowForm(false)} className="px-6 py-2 rounded-lg text-gray-600 hover:bg-gray-100 transition">
                  Annuler
                </button>
              </div>
            </form>
          </div>
        )}

        <div className="space-y-4">
          {clientsList.map((c) => (
            <div key={c.id} className="bg-white border border-gray-100 rounded-2xl p-6 shadow-sm flex items-center justify-between">
              <div>
                <h3 className="font-bold text-lg">{c.business_name}</h3>
                <p className="text-sm text-gray-400 capitalize">{c.sector.replace("_", " ")}</p>
              </div>
              <div className="flex gap-3">
                <Link
                  href={`/dashboard/leads?client=${c.id}`}
                  className="text-sm border border-gray-200 px-3 py-1.5 rounded-lg hover:bg-gray-50 transition"
                >
                  Voir leads
                </Link>
                <Link
                  href={`/dashboard/campaigns?client=${c.id}`}
                  className="text-sm bg-brand-600 text-white px-3 py-1.5 rounded-lg hover:bg-brand-700 transition"
                >
                  Campagnes
                </Link>
              </div>
            </div>
          ))}
          {clientsList.length === 0 && (
            <div className="text-center py-16 text-gray-400">
              <p className="text-4xl mb-4">🏢</p>
              <p>Aucun client encore. Ajoutez votre premier client pour démarrer la prospection automatique.</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
