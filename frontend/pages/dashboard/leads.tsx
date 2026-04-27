import { useEffect, useState } from "react";
import { useRouter } from "next/router";
import Link from "next/link";
import { leads as leadsApi, clients as clientsApi } from "../../lib/api";

const STATUS_COLORS: Record<string, string> = {
  new: "bg-gray-100 text-gray-600",
  contacted: "bg-blue-50 text-blue-600",
  replied: "bg-indigo-50 text-indigo-600",
  interested: "bg-emerald-50 text-emerald-600",
  converted: "bg-green-100 text-green-700",
  not_interested: "bg-red-50 text-red-500",
  bounced: "bg-gray-50 text-gray-400",
};

const STATUS_LABELS: Record<string, string> = {
  new: "Nouveau",
  contacted: "Contacté",
  replied: "A répondu",
  interested: "Intéressé",
  converted: "Converti",
  not_interested: "Pas intéressé",
  bounced: "Bounce",
};

export default function Leads() {
  const router = useRouter();
  const clientId = router.query.client as string;
  const [leadsList, setLeadsList] = useState<any[]>([]);
  const [client, setClient] = useState<any>(null);
  const [generating, setGenerating] = useState(false);

  useEffect(() => {
    if (!localStorage.getItem("token")) { router.push("/login"); return; }
    if (!clientId) return;

    clientsApi.list().then((r) => {
      const found = r.data.find((c: any) => c.id === clientId);
      setClient(found);
    });
    leadsApi.list(clientId).then((r) => setLeadsList(r.data));
  }, [clientId]);

  async function handleGenerate() {
    setGenerating(true);
    try {
      await leadsApi.generate(clientId);
      setTimeout(async () => {
        const r = await leadsApi.list(clientId);
        setLeadsList(r.data);
        setGenerating(false);
      }, 5000);
    } catch {
      setGenerating(false);
    }
  }

  if (!clientId) return (
    <div className="p-8 text-center text-gray-400">
      <Link href="/dashboard/clients">Sélectionnez un client</Link>
    </div>
  );

  return (
    <div className="min-h-screen bg-gray-50 p-8">
      <div className="max-w-5xl mx-auto">
        <div className="flex items-center justify-between mb-8">
          <div>
            <Link href="/dashboard/clients" className="text-sm text-gray-400 hover:text-gray-600">← Clients</Link>
            <h1 className="text-2xl font-bold mt-1">
              Leads {client ? `— ${client.business_name}` : ""}
            </h1>
          </div>
          <button
            onClick={handleGenerate}
            disabled={generating}
            className="bg-brand-600 text-white px-4 py-2 rounded-lg font-medium hover:bg-brand-700 disabled:opacity-50 transition flex items-center gap-2"
          >
            {generating ? (
              <><span className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin" /> Génération en cours…</>
            ) : "⚡ Générer des leads"}
          </button>
        </div>

        <div className="bg-white rounded-2xl border border-gray-100 shadow-sm overflow-hidden">
          <table className="w-full text-sm">
            <thead className="bg-gray-50 border-b border-gray-100">
              <tr>
                <th className="text-left px-6 py-3 font-medium text-gray-500">Entreprise</th>
                <th className="text-left px-6 py-3 font-medium text-gray-500">Email</th>
                <th className="text-left px-6 py-3 font-medium text-gray-500">Téléphone</th>
                <th className="text-left px-6 py-3 font-medium text-gray-500">Score</th>
                <th className="text-left px-6 py-3 font-medium text-gray-500">Statut</th>
              </tr>
            </thead>
            <tbody>
              {leadsList.map((lead) => (
                <tr key={lead.id} className="border-b border-gray-50 hover:bg-gray-50 transition">
                  <td className="px-6 py-4 font-medium">{lead.business_name}</td>
                  <td className="px-6 py-4 text-gray-500">{lead.email || "—"}</td>
                  <td className="px-6 py-4 text-gray-500">{lead.phone || "—"}</td>
                  <td className="px-6 py-4">
                    <div className="flex items-center gap-2">
                      <div className="w-16 h-1.5 bg-gray-100 rounded-full">
                        <div
                          className="h-full bg-brand-500 rounded-full"
                          style={{ width: `${lead.score}%` }}
                        />
                      </div>
                      <span className="text-xs text-gray-400">{lead.score}</span>
                    </div>
                  </td>
                  <td className="px-6 py-4">
                    <span className={`text-xs px-2 py-1 rounded-full font-medium ${STATUS_COLORS[lead.status] || "bg-gray-100 text-gray-600"}`}>
                      {STATUS_LABELS[lead.status] || lead.status}
                    </span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
          {leadsList.length === 0 && (
            <div className="text-center py-16 text-gray-400">
              <p className="text-4xl mb-4">🎯</p>
              <p>Aucun lead pour l'instant. Cliquez sur "Générer des leads" pour démarrer.</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
