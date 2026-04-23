import { useEffect, useRef } from "react";
import { apiBase, getToken } from "./api";

export type LiveEvent = { type: string; data: Record<string, unknown> };

/**
 * Opens a Server-Sent Events stream to the backend and fires `onEvent`
 * for every incoming message. Re-opens if the connection drops.
 *
 * EventSource can't send a custom Authorization header, so the token is
 * passed via a `?token=...` query param — the FastAPI auth middleware is
 * aware of this.
 */
export function useSSE(onEvent: (ev: LiveEvent) => void, enabled = true) {
  const handlerRef = useRef(onEvent);
  handlerRef.current = onEvent;

  useEffect(() => {
    if (!enabled) return;
    const token = getToken();
    if (!token) return;

    const url = `${apiBase()}/events/stream?token=${encodeURIComponent(
      token,
    )}`;
    const es = new EventSource(url);

    es.onmessage = (m) => {
      try {
        const parsed = JSON.parse(m.data) as LiveEvent;
        handlerRef.current(parsed);
      } catch {
        /* ignore malformed frames */
      }
    };
    es.onerror = () => {
      /* browser will auto-retry; nothing to do */
    };
    return () => es.close();
  }, [enabled]);
}
