import { supabaseBrowser } from "./supabase/client";

const BACKEND = process.env.NEXT_PUBLIC_BACKEND_URL || "http://localhost:8000";

async function authHeaders(): Promise<HeadersInit> {
  const sb = supabaseBrowser();
  const { data } = await sb.auth.getSession();
  const token = data.session?.access_token;
  return token
    ? { "Content-Type": "application/json", Authorization: `Bearer ${token}` }
    : { "Content-Type": "application/json" };
}

export async function apiGet<T>(path: string): Promise<T> {
  const res = await fetch(`${BACKEND}${path}`, { headers: await authHeaders() });
  if (!res.ok) throw new Error((await res.text()) || res.statusText);
  return res.json();
}

export async function apiPost<T>(path: string, body?: unknown): Promise<T> {
  const res = await fetch(`${BACKEND}${path}`, {
    method: "POST",
    headers: await authHeaders(),
    body: body ? JSON.stringify(body) : undefined,
  });
  if (!res.ok) throw new Error((await res.text()) || res.statusText);
  return res.json();
}

export async function apiDownload(path: string): Promise<void> {
  const res = await fetch(`${BACKEND}${path}`, { headers: await authHeaders() });
  if (!res.ok) throw new Error((await res.text()) || res.statusText);
  const blob = await res.blob();
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  const disp = res.headers.get("Content-Disposition") || "";
  const match = disp.match(/filename="([^"]+)"/);
  a.download = match ? match[1] : "export.docx";
  document.body.appendChild(a);
  a.click();
  a.remove();
  URL.revokeObjectURL(url);
}
