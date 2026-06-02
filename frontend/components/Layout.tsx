import Link from "next/link";
import { useRouter } from "next/router";

const NAV = [
  { href: "/dashboard", label: "Dashboard", icon: "📊" },
  { href: "/dashboard/clients", label: "Clients", icon: "🏢" },
  { href: "/dashboard/leads", label: "Leads", icon: "🎯" },
  { href: "/dashboard/campaigns", label: "Campaigns", icon: "✉️" },
  { href: "/dashboard/billing", label: "Billing", icon: "💳" },
  { href: "/admin", label: "Admin", icon: "⚙️" },
];

export default function Layout({ children }: { children: React.ReactNode }) {
  const router = useRouter();

  function logout() {
    localStorage.removeItem("token");
    router.push("/login");
  }

  return (
    <div className="min-h-screen bg-gray-50 flex">
      <aside className="w-64 bg-white h-screen border-r border-gray-100 fixed flex flex-col z-10">
        <div className="p-6 border-b border-gray-100">
          <Link href="/dashboard" className="text-lg font-bold text-indigo-600">
            AutoGrowth Pro
          </Link>
        </div>
        <nav className="p-4 flex-1 space-y-1">
          {NAV.map((item) => {
            const active = router.pathname === item.href || router.pathname.startsWith(item.href + "/");
            return (
              <Link
                key={item.href}
                href={item.href}
                className={`flex items-center gap-3 px-3 py-2 rounded-lg text-sm font-medium transition ${
                  active
                    ? "bg-indigo-50 text-indigo-600"
                    : "text-gray-600 hover:bg-indigo-50 hover:text-indigo-600"
                }`}
              >
                <span>{item.icon}</span> {item.label}
              </Link>
            );
          })}
        </nav>
        <div className="p-4 border-t border-gray-100">
          <button
            onClick={logout}
            className="text-sm text-gray-400 hover:text-gray-600 w-full text-left"
          >
            Sign out
          </button>
        </div>
      </aside>
      <main className="ml-64 flex-1 min-h-screen">{children}</main>
    </div>
  );
}
