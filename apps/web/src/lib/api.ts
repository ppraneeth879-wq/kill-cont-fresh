/**
 * Thin fetch wrapper with bearer-token injection + typed responses.
 * All calls hit `${VITE_API_BASE_URL}<path>`. The token is read from
 * localStorage on every request so a fresh login takes effect immediately.
 */

const BASE: string =
  (import.meta.env.VITE_API_BASE_URL as string | undefined) ??
  "http://localhost:8000/api/v1";

const AUTH_MODE: string =
  (import.meta.env.VITE_AUTH_MODE as string | undefined)?.toLowerCase() ?? "demo";

export const TOKEN_KEY = "killcont-token";
export const USER_KEY = "killcont-user";
export const FIREBASE_ID_TOKEN_KEY = "killcont-firebase-id-token";

export function getToken(): string {
  try {
    return localStorage.getItem(TOKEN_KEY) ?? "";
  } catch {
    return "";
  }
}

export function mediaUrl(relPath: string | null | undefined): string | undefined {
  if (!relPath) return undefined;
  const origin = BASE.replace(/\/api\/v1\/?$/, "");
  return `${origin}/media/${relPath}`;
}

export function apiBase(): string {
  return BASE;
}

export function authMode(): "demo" | "firebase" {
  return AUTH_MODE === "firebase" ? "firebase" : "demo";
}

export class ApiError extends Error {
  status: number;
  body?: string;
  constructor(status: number, message: string, body?: string) {
    super(message);
    this.status = status;
    this.body = body;
  }
}

type Init = Omit<RequestInit, "body"> & {
  body?: BodyInit | Record<string, unknown> | null;
};

export async function api<T>(path: string, init: Init = {}): Promise<T> {
  const headers = new Headers(init.headers ?? {});
  headers.set("Authorization", `Bearer ${getToken()}`);

  let body = init.body as BodyInit | undefined;
  const isPlainObject =
    body !== undefined &&
    body !== null &&
    typeof body === "object" &&
    !(body instanceof FormData) &&
    !(body instanceof Blob) &&
    !(body instanceof ArrayBuffer) &&
    !(body instanceof URLSearchParams);

  if (isPlainObject) {
    body = JSON.stringify(body);
    if (!headers.has("Content-Type")) {
      headers.set("Content-Type", "application/json");
    }
  }

  const res = await fetch(`${BASE}${path}`, {
    ...init,
    headers,
    body,
  });

  if (!res.ok) {
    const text = await res.text().catch(() => "");
    throw new ApiError(res.status, `${res.status} ${res.statusText}`, text);
  }
  if (res.status === 204) return undefined as unknown as T;
  return (await res.json()) as T;
}
