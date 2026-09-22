const API_BASE = import.meta.env.VITE_API_BASE_URL ?? "http://localhost:8000";

export type Profile = {
  id?: string;
  podcast_name: string;
  description: string;
  niche: string;
  target_audience: string;
  audience_level: string;
  brand_voice: string;
  tone: string;
  communication_style: string;
  content_goals: string;
  preferred_platforms: string[];
  clip_style: string;
  preferred_topics: string[];
  excluded_topics: string[];
  cta_style: string;
  language: string;
  website?: string;
  social_handles: Record<string, string>;
  brand_guidelines: string;
};

export function token() {
  return localStorage.getItem("pcf_token");
}

export function setToken(value: string) {
  localStorage.setItem("pcf_token", value);
}

export async function api(path: string, init: RequestInit = {}) {
  const headers = new Headers(init.headers);
  if (!(init.body instanceof FormData)) headers.set("Content-Type", "application/json");
  const auth = token();
  if (auth) headers.set("Authorization", `Bearer ${auth}`);
  const response = await fetch(`${API_BASE}${path}`, { ...init, headers });
  if (!response.ok) throw new Error((await response.json().catch(() => ({}))).detail ?? "Request failed");
  return response.json();
}
