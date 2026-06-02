import axios from "axios";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

const api = axios.create({ baseURL: API_URL });

api.interceptors.request.use((config) => {
  const token = typeof window !== "undefined" ? localStorage.getItem("token") : null;
  if (token) config.headers.Authorization = `Bearer ${token}`;
  return config;
});

api.interceptors.response.use(
  (r) => r,
  (err) => {
    if (err.response?.status === 401 && typeof window !== "undefined") {
      localStorage.removeItem("token");
      window.location.href = "/login";
    }
    return Promise.reject(err);
  }
);

export default api;

export const auth = {
  login: (email: string, password: string) =>
    api.post("/auth/login", new URLSearchParams({ username: email, password })),
  register: (email: string, password: string, full_name: string, country = "FR", language = "fr") =>
    api.post("/auth/register", { email, password, full_name, country, language }),
  me: () => api.get("/auth/me"),
  countries: () => api.get("/auth/countries"),
  updateLocale: (country?: string, language?: string) =>
    api.patch("/auth/me/locale", {}, { params: { country, language } }),
};

export const billing = {
  checkout: (plan: string) => api.post("/billing/checkout", { plan }),
  subscription: () => api.get("/billing/subscription"),
};

export const clients = {
  list: () => api.get("/clients/"),
  create: (data: object) => api.post("/clients/", data),
};

export const leads = {
  list: (clientId: string) => api.get(`/leads/${clientId}`),
  generate: (clientId: string) => api.post(`/leads/${clientId}/generate`),
};

export const campaigns = {
  list: (clientId: string) => api.get(`/campaigns/${clientId}`),
  create: (data: object) => api.post("/campaigns/", data),
  activate: (id: string) => api.post(`/campaigns/${id}/activate`),
  pause: (id: string) => api.post(`/campaigns/${id}/pause`),
};

export const analytics = {
  dashboard: () => api.get("/analytics/dashboard"),
};

export const adminApi = {
  metrics: () => api.get("/admin/metrics"),
  cohorts: () => api.get("/admin/cohorts"),
  users: (search?: string) => api.get("/admin/users", { params: search ? { search } : {} }),
  revenue30d: () => api.get("/admin/revenue/30d"),
  setRole: (userId: string, role: string) => api.patch(`/admin/users/${userId}/role`, null, { params: { role } }),
  impersonate: (userId: string) => api.post(`/admin/users/${userId}/impersonate`),
};

export const affiliateApi = {
  join: () => api.post("/affiliate/join"),
  dashboard: () => api.get("/affiliate/dashboard"),
  requestPayout: () => api.post("/affiliate/request-payout"),
};

export const webhooksApi = {
  list: () => api.get("/webhooks/"),
  create: (data: { url: string; events: string[]; secret?: string }) => api.post("/webhooks/", data),
  update: (id: string, data: object) => api.patch(`/webhooks/${id}`, data),
  delete: (id: string) => api.delete(`/webhooks/${id}`),
  events: () => api.get("/webhooks/events"),
};
