import { useEffect, useState } from "react";
import Layout from "../../components/Layout";
import { adminApi } from "../../lib/api";

interface Metrics {
  mrr: number;
  arr: number;
  total_users: number;
  active_subscriptions: number;
  churn_rate_30d: number;
  new_users_30d: number;
  plan_distribution: Record<string, number>;
  revenue_by_currency: Record<string, number>;
}

interface CohortRow {
  month: string;
  new_users: number;
  converted: number;
  conversion_rate: number;
  revenue: number;
}

interface UserRow {
  id: string;
  email: string;
  full_name: string;
  country: string;
  plan: string;
  status: string;
  created_at: string;
}

const PLAN_COLORS: Record<string, string> = {
  pro: "bg-purple-100 text-purple-800",
  growth: "bg-blue-100 text-blue-800",
  starter: "bg-green-100 text-green-800",
};

export default function AdminDashboard() {
  const [metrics, setMetrics] = useState<Metrics | null>(null);
  const [cohorts, setCohorts] = useState<CohortRow[]>([]);
  const [users, setUsers] = useState<UserRow[]>([]);
  const [search, setSearch] = useState("");
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    const token = localStorage.getItem("token");
    if (!token) { window.location.href = "/login"; return; }
    loadAll();
  }, []);

  async function loadAll() {
    try {
      const [m, c, u] = await Promise.all([
        adminApi.metrics(),
        adminApi.cohorts(),
        adminApi.users(),
      ]);
      setMetrics(m.data);
      setCohorts(c.data);
      setUsers(u.data);
    } catch (e: any) {
      setError(e?.response?.data?.detail || "Unauthorized");
    } finally {
      setLoading(false);
    }
  }

  const filtered = users.filter(
    (u) =>
      u.email.toLowerCase().includes(search.toLowerCase()) ||
      (u.full_name || "").toLowerCase().includes(search.toLowerCase())
  );

  if (loading) return <Layout><div className="p-8 text-gray-500">Loading admin data…</div></Layout>;
  if (error) return <Layout><div className="p-8 text-red-600">{error}</div></Layout>;

  const mrrTarget = 30000;
  const mrrPct = Math.min(100, Math.round(((metrics?.mrr || 0) / mrrTarget) * 100));

  return (
    <Layout>
      <div className="p-6 max-w-7xl mx-auto space-y-8">
        <h1 className="text-2xl font-bold text-gray-900">Admin Dashboard</h1>

        {/* KPI Cards */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          {[
            { label: "MRR", value: `€${(metrics?.mrr || 0).toLocaleString()}`, sub: `ARR €${((metrics?.arr || 0) / 1000).toFixed(0)}k` },
            { label: "Active Users", value: metrics?.active_subscriptions || 0, sub: `${metrics?.total_users || 0} total` },
            { label: "New (30d)", value: metrics?.new_users_30d || 0, sub: "signups" },
            { label: "Churn 30d", value: `${((metrics?.churn_rate_30d || 0) * 100).toFixed(1)}%`, sub: "monthly churn" },
          ].map((k) => (
            <div key={k.label} className="bg-white rounded-xl p-5 shadow-sm border border-gray-100">
              <p className="text-sm text-gray-500">{k.label}</p>
              <p className="text-2xl font-bold text-gray-900 mt-1">{k.value}</p>
              <p className="text-xs text-gray-400 mt-1">{k.sub}</p>
            </div>
          ))}
        </div>

        {/* MRR Progress */}
        <div className="bg-white rounded-xl p-6 shadow-sm border border-gray-100">
          <div className="flex justify-between mb-2">
            <span className="font-semibold text-gray-700">MRR toward €30,000/month goal</span>
            <span className="text-indigo-600 font-bold">{mrrPct}%</span>
          </div>
          <div className="w-full bg-gray-100 rounded-full h-4">
            <div
              className="bg-indigo-500 h-4 rounded-full transition-all duration-500"
              style={{ width: `${mrrPct}%` }}
            />
          </div>
          <p className="text-sm text-gray-500 mt-2">
            €{(metrics?.mrr || 0).toLocaleString()} / €{mrrTarget.toLocaleString()}
          </p>
        </div>

        {/* Plan Distribution */}
        <div className="bg-white rounded-xl p-6 shadow-sm border border-gray-100">
          <h2 className="font-semibold text-gray-700 mb-4">Plan Distribution</h2>
          <div className="flex gap-6">
            {Object.entries(metrics?.plan_distribution || {}).map(([plan, count]) => (
              <div key={plan} className="flex items-center gap-2">
                <span className={`px-2 py-1 rounded text-xs font-medium ${PLAN_COLORS[plan] || "bg-gray-100 text-gray-700"}`}>
                  {plan}
                </span>
                <span className="text-gray-700 font-bold">{count}</span>
              </div>
            ))}
          </div>
        </div>

        {/* Cohort Table */}
        <div className="bg-white rounded-xl p-6 shadow-sm border border-gray-100">
          <h2 className="font-semibold text-gray-700 mb-4">Monthly Cohorts</h2>
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="text-left text-gray-500 border-b">
                  <th className="pb-2 pr-4">Month</th>
                  <th className="pb-2 pr-4">New Users</th>
                  <th className="pb-2 pr-4">Converted</th>
                  <th className="pb-2 pr-4">Conv. Rate</th>
                  <th className="pb-2">Revenue</th>
                </tr>
              </thead>
              <tbody>
                {cohorts.map((row) => (
                  <tr key={row.month} className="border-b border-gray-50 hover:bg-gray-50">
                    <td className="py-2 pr-4 font-medium">{row.month}</td>
                    <td className="py-2 pr-4">{row.new_users}</td>
                    <td className="py-2 pr-4">{row.converted}</td>
                    <td className="py-2 pr-4">
                      <span className={`font-medium ${row.conversion_rate > 0.3 ? "text-green-600" : "text-orange-500"}`}>
                        {(row.conversion_rate * 100).toFixed(1)}%
                      </span>
                    </td>
                    <td className="py-2">€{row.revenue.toLocaleString()}</td>
                  </tr>
                ))}
                {cohorts.length === 0 && (
                  <tr><td colSpan={5} className="py-4 text-gray-400 text-center">No cohort data yet</td></tr>
                )}
              </tbody>
            </table>
          </div>
        </div>

        {/* Users Table */}
        <div className="bg-white rounded-xl p-6 shadow-sm border border-gray-100">
          <div className="flex justify-between items-center mb-4">
            <h2 className="font-semibold text-gray-700">Users</h2>
            <input
              className="border border-gray-200 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-300"
              placeholder="Search by email or name…"
              value={search}
              onChange={(e) => setSearch(e.target.value)}
            />
          </div>
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="text-left text-gray-500 border-b">
                  <th className="pb-2 pr-4">Name</th>
                  <th className="pb-2 pr-4">Email</th>
                  <th className="pb-2 pr-4">Country</th>
                  <th className="pb-2 pr-4">Plan</th>
                  <th className="pb-2 pr-4">Status</th>
                  <th className="pb-2">Joined</th>
                </tr>
              </thead>
              <tbody>
                {filtered.slice(0, 50).map((u) => (
                  <tr key={u.id} className="border-b border-gray-50 hover:bg-gray-50">
                    <td className="py-2 pr-4 font-medium">{u.full_name || "—"}</td>
                    <td className="py-2 pr-4 text-gray-600">{u.email}</td>
                    <td className="py-2 pr-4">{u.country || "—"}</td>
                    <td className="py-2 pr-4">
                      <span className={`px-2 py-0.5 rounded text-xs font-medium ${PLAN_COLORS[u.plan] || "bg-gray-100 text-gray-700"}`}>
                        {u.plan || "none"}
                      </span>
                    </td>
                    <td className="py-2 pr-4">
                      <span className={`px-2 py-0.5 rounded text-xs font-medium ${u.status === "active" ? "bg-green-100 text-green-700" : "bg-gray-100 text-gray-500"}`}>
                        {u.status || "—"}
                      </span>
                    </td>
                    <td className="py-2 text-gray-500">{u.created_at ? new Date(u.created_at).toLocaleDateString() : "—"}</td>
                  </tr>
                ))}
                {filtered.length === 0 && (
                  <tr><td colSpan={6} className="py-4 text-gray-400 text-center">No users found</td></tr>
                )}
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </Layout>
  );
}
