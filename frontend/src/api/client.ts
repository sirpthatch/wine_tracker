import type {
  Wine,
  WineCreate,
  WineUpdate,
  Suggestion,
  LocalRecommendationsResponse,
} from "../types/wine";

const BASE = "/api";

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const res = await fetch(`${BASE}${path}`, {
    headers: { "Content-Type": "application/json" },
    ...init,
  });
  if (!res.ok) {
    const err = await res.text();
    throw new Error(err || `HTTP ${res.status}`);
  }
  if (res.status === 204) return undefined as T;
  return res.json();
}

export const api = {
  wines: {
    list: (params?: { varietal?: string; region?: string }) => {
      const qs = new URLSearchParams();
      if (params?.varietal) qs.set("varietal", params.varietal);
      if (params?.region) qs.set("region", params.region);
      const query = qs.toString() ? `?${qs}` : "";
      return request<Wine[]>(`/wines/${query}`);
    },
    get: (id: number) => request<Wine>(`/wines/${id}`),
    create: (data: WineCreate) =>
      request<Wine>("/wines/", { method: "POST", body: JSON.stringify(data) }),
    update: (id: number, data: WineUpdate) =>
      request<Wine>(`/wines/${id}`, {
        method: "PATCH",
        body: JSON.stringify(data),
      }),
    delete: (id: number) =>
      request<void>(`/wines/${id}`, { method: "DELETE" }),
  },
  suggestions: {
    list: () => request<Suggestion[]>("/suggestions/"),
  },
  localRecommendations: {
    search: (address: string, radius_m: number) =>
      request<LocalRecommendationsResponse>("/local-recommendations/", {
        method: "POST",
        body: JSON.stringify({ address, radius_m }),
      }),
  },
};
