import type {
  CampaignsResponse,
  MediaMasterRow,
  MetricsResponse,
  OptimizeResponse,
} from "@/lib/types";

/** Empty = same origin (Railway). Local Next.js dev uses NEXT_PUBLIC_API_BASE_URL. */
const API_BASE = (process.env.NEXT_PUBLIC_API_BASE_URL ?? "").replace(/\/$/, "");

async function getJson<T>(path: string, init?: RequestInit): Promise<T> {
  const res = await fetch(`${API_BASE}${path}`, {
    ...init,
    headers: {
      "Content-Type": "application/json",
      ...(init?.headers || {}),
    },
    cache: "no-store",
  });
  if (!res.ok) {
    const body = await res.text();
    throw new Error(`API ${res.status}: ${body || res.statusText}`);
  }
  return res.json() as Promise<T>;
}

export function fetchMetrics(params: {
  startDate: string;
  endDate: string;
  media?: string;
}): Promise<MetricsResponse> {
  const q = new URLSearchParams({
    start_date: params.startDate,
    end_date: params.endDate,
  });
  if (params.media) q.set("media", params.media);
  return getJson(`/api/v1/metrics?${q.toString()}`);
}

export function fetchCampaigns(params: {
  startDate: string;
  endDate: string;
  media?: string;
}): Promise<CampaignsResponse> {
  const q = new URLSearchParams({
    start_date: params.startDate,
    end_date: params.endDate,
  });
  if (params.media) q.set("media", params.media);
  return getJson(`/api/v1/campaigns?${q.toString()}`);
}

export async function fetchMediaList(): Promise<MediaMasterRow[]> {
  const data = await getJson<{ rows: MediaMasterRow[] }>("/api/v1/media");
  return data.rows;
}

export function optimizeBudget(body: {
  start_date: string;
  end_date: string;
  total_budget: number;
  media?: string;
}): Promise<OptimizeResponse> {
  return getJson("/api/v1/ai/optimize", {
    method: "POST",
    body: JSON.stringify(body),
  });
}
