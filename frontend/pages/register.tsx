import { useState } from "react";
import { useRouter } from "next/router";
import Link from "next/link";
import { auth, billing } from "../lib/api";

const PLAN_LABELS: Record<string, string> = {
  starter: "Starter — €299/mois",
  growth: "Growth — €599/mois",
  pro: "Pro — €999/mois",
};

export default function Register() {
  const router = useRouter();
  const plan = (router.query.plan as string) || "starter";
  const [form, setForm] = useState({ email: "", password: "", full_name: "" });
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setLoading(true);
    setError("");
    try {
      const res = await auth.register(form.email, form.password, form.full_name);
      localStorage.setItem("token", res.data.access_token);
      const checkout = await billing.checkout(plan);
      window.location.href = checkout.data.checkout_url;
    } catch (err: any) {
      setError(err.response?.data?.detail || "Erreur lors de l'inscription.");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50">
      <div className="bg-white w-full max-w-md p-8 rounded-2xl shadow-sm border border-gray-100">
        <Link href="/" className="text-xl font-bold text-brand-600 block mb-4">AutoGrowth Pro</Link>
        <div className="bg-brand-50 border border-brand-100 rounded-lg p-3 mb-6 text-sm text-brand-700 font-medium">
          Plan sélectionné : {PLAN_LABELS[plan] || plan}
        </div>
        <h1 className="text-2xl font-bold mb-6">Créer votre compte</h1>
        {error && <div className="bg-red-50 text-red-600 p-3 rounded-lg mb-4 text-sm">{error}</div>}
        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="block text-sm font-medium mb-1">Nom complet</label>
            <input
              value={form.full_name}
              onChange={(e) => setForm({ ...form, full_name: e.target.value })}
              className="w-full border border-gray-200 rounded-lg px-4 py-2.5 focus:outline-none focus:ring-2 focus:ring-brand-500"
              required
            />
          </div>
          <div>
            <label className="block text-sm font-medium mb-1">Email professionnel</label>
            <input
              type="email"
              value={form.email}
              onChange={(e) => setForm({ ...form, email: e.target.value })}
              className="w-full border border-gray-200 rounded-lg px-4 py-2.5 focus:outline-none focus:ring-2 focus:ring-brand-500"
              required
            />
          </div>
          <div>
            <label className="block text-sm font-medium mb-1">Mot de passe</label>
            <input
              type="password"
              value={form.password}
              onChange={(e) => setForm({ ...form, password: e.target.value })}
              className="w-full border border-gray-200 rounded-lg px-4 py-2.5 focus:outline-none focus:ring-2 focus:ring-brand-500"
              required
              minLength={8}
            />
          </div>
          <button
            type="submit"
            disabled={loading}
            className="w-full bg-brand-600 text-white py-3 rounded-lg font-bold hover:bg-brand-700 disabled:opacity-50 transition"
          >
            {loading ? "Création…" : "Créer mon compte et payer →"}
          </button>
        </form>
        <p className="text-center mt-4 text-xs text-gray-400">
          En créant un compte vous acceptez nos CGU. Annulable à tout moment.
        </p>
        <p className="text-center mt-2 text-sm text-gray-500">
          Déjà un compte ?{" "}
          <Link href="/login" className="text-brand-600 font-medium">Se connecter</Link>
        </p>
      </div>
    </div>
  );
}
