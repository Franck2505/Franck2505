import { useEffect, useState } from "react";
import { useRouter } from "next/router";
import Link from "next/link";
import { campaigns as campaignsApi, clients as clientsApi } from "../../lib/api";

const STATUS_COLORS: Record<string, string> = {
  draft: "bg-gray-100 text-gray-600",
  active: "bg-emerald-50 text-emerald-600",
  paused: "bg-amber-50 text-amber-600",
  completed: "bg-blue-50 text-blue-600",
};

export default function Campaigns() {
  const router = useRouter();
  const clientId = router.query.client as string;
  const [campaignsList, setCampaignsList] = useState<any[]>([]);
  const [client, setClient] = useState<any>(null);
  const [showForm, setShowForm] = useState(false);
  const [form, setForm] = useState({ name: "", sequence_days: "0,3,7,14" });
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (!localStorage.getItem("token")) { router.push("/login"); return; }
    if (!clientId) return;
    clientsApi.list().then((r) => setClient(r.data.find((c: any) => c.id === clientId)));
    campaignsApi.list(clientId).then((r) => setCampaignsList(r.data));
  }, [clientId]);

  async function handleCreate(e: React.FormEvent) {
    e.preventDefault();
    setLoading(true);
    try {
      await campaignsApi.create({
        client_id: clientId,
        name: form.name,
        sequence_days: form.sequence_days.split(",").map((d) => parseInt(d.trim())),
      });
      const r = await campaignsApi.list(clientId);
      setCampaignsList(r.data);
      setShowForm(false);
    } finally {
      setLoading(false);
    }
  }

  async function handleActivate(id: string) {
    await campaignsApi.activate(id);
    const r = await campaignsApi.list(clientId);
    setCampaignsList(r.data);
  }

  async function handlePause(id: string) {
    await campaignsApi.pause(id);
    const r = await campaignsApi.list(clientId);
    setCampaignsList(r.data);
  }

  return (
    <div className="min-h-screen bg-gray-50 p-8">
      <div className="max-w-5xl mx-auto">
        <div className="flex items-center justify-between mb-8">
          <div>
            <Link href="/dashboard/clients" className="text-sm text-gray-400 hover:text-gray-600">← Clients</Link>
            <h1 className="text-2xl font-bold mt-1">
              Campagnes {client ? `— ${client.business_name}` : ""}
            </h1>
          </div>
          <button
            onClick={() => setShowForm(!showForm)}
            className="bg-brand-600 text-white px-4 py-2 rounded-lg font-medium hover:bg-brand-700 transition"
          >
            + Nouvelle campagne
          </button>
        </div>

        {showForm && (
          <div className="bg-white border border-gray-100 rounded-2xl p-6 mb-6 shadow-sm">
            <h2 className="text-lg font-bold mb-4">Nouvelle campagne</h2>
            <form onSubmit={handleCreate} className="space-y-4">
              <div>
                <label className="block text-sm font-medium mb-1">Nom de la campagne</label>
                <input
                  value={form.name}
                  onChange={(e) => setForm({ ...form, name: e.target.value })}
                  className="w-full border border-gray-200 rounded-lg px-4 py-2.5 focus:outline-none focus:ring-2 focus:ring-brand-500"
                  placeholder="Ex: Prospection Q1 2025"
                  required
                />
              </div>
              <div>
                <label className="block text-sm font-medium mb-1">Séquence de relances (jours, séparés par virgule)</label>
                <input
                  value={form.sequence_days}
                  onChange={(e) => setForm({ ...form, sequence_days: e.target.value })}
                  className="w-full border border-gray-200 rounded-lg px-4 py-2.5 focus:outline-none focus:ring-2 focus:ring-brand-500"
                  placeholder="0,3,7,14"
                />
                <p className="text-xs text-gray-400 mt-1">Email 1 à J0, relance à J3, J7 et J14</p>
              </div>
              <div className="flex gap-3">
                <button type="submit" disabled={loading} className="bg-brand-600 text-white px-6 py-2 rounded-lg font-medium hover:bg-brand-700 disabled:opacity-50 transition">
                  {loading ? "Création…" : "Créer"}
                </button>
                <button type="button" onClick={() => setShowForm(false)} className="px-6 py-2 rounded-lg text-gray-600 hover:bg-gray-100 transition">
                  Annuler
                </button>
              </div>
            </form>
          </div>
        )}

        <div className="space-y-4">
          {campaignsList.map((c) => (
            <div key={c.id} className="bg-white border border-gray-100 rounded-2xl p-6 shadow-sm">
              <div className="flex items-center justify-between mb-4">
                <div>
                  <h3 className="font-bold text-lg">{c.name}</h3>
                  <span className={`text-xs px-2 py-1 rounded-full font-medium ${STATUS_COLORS[c.status]}`}>
                    {c.status === "active" ? "Active — emails en cours d'envoi" : c.status}
                  </span>
                </div>
                <div className="flex gap-2">
                  {c.status !== "active" && (
                    <button onClick={() => handleActivate(c.id)} className="bg-emerald-500 text-white px-3 py-1.5 rounded-lg text-sm font-medium hover:bg-emerald-600 transition">
                      ▶ Activer
                    </button>
                  )}
                  {c.status === "active" && (
                    <button onClick={() => handlePause(c.id)} className="bg-amber-500 text-white px-3 py-1.5 rounded-lg text-sm font-medium hover:bg-amber-600 transition">
                      ⏸ Pause
                    </button>
                  )}
                </div>
              </div>
              <div className="grid grid-cols-4 gap-4 text-center">
                <div className="bg-gray-50 rounded-xl p-3">
                  <div className="text-2xl font-bold">{c.total_sent}</div>
                  <div className="text-xs text-gray-400">Envoyés</div>
                </div>
                <div className="bg-gray-50 rounded-xl p-3">
                  <div className="text-2xl font-bold">{c.open_rate}%</div>
                  <div className="text-xs text-gray-400">Ouvertures</div>
                </div>
                <div className="bg-gray-50 rounded-xl p-3">
                  <div className="text-2xl font-bold">{c.reply_rate}%</div>
                  <div className="text-xs text-gray-400">Réponses</div>
                </div>
                <div className="bg-gray-50 rounded-xl p-3">
                  <div className="text-2xl font-bold">{c.total_replied}</div>
                  <div className="text-xs text-gray-400">Conversations</div>
                </div>
              </div>
            </div>
          ))}
          {campaignsList.length === 0 && (
            <div className="text-center py-16 text-gray-400">
              <p className="text-4xl mb-4">✉️</p>
              <p>Aucune campagne. Créez-en une pour démarrer la prospection automatique.</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
