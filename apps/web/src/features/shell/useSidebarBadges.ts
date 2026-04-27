import { useEffect, useRef, useState } from "react";
import { useLocation } from "react-router-dom";
import { useSSE } from "../../lib/sse";

type Badges = { incidents: number; monitor: number };
const FADE_MS = 5000;

/**
 * Bundle E: cross-tab awareness during a live run.
 *
 * Listens to SSE at the Sidebar level so the counters survive navigation
 * between protected routes. Counts increment on `incident.created` and
 * `feed.ingested`; the whole map is reset to zero after FADE_MS of no
 * events. The currently-active route is suppressed (no point telling the
 * operator about the page they're already on).
 */
export function useSidebarBadges(): Badges {
  const [badges, setBadges] = useState<Badges>({ incidents: 0, monitor: 0 });
  const lastEventAt = useRef<number>(0);
  const location = useLocation();

  useSSE((ev) => {
    if (ev.type === "incident.created") {
      lastEventAt.current = Date.now();
      setBadges((b) => ({ ...b, incidents: b.incidents + 1 }));
    }
    if (ev.type === "feed.ingested") {
      lastEventAt.current = Date.now();
      setBadges((b) => ({ ...b, monitor: b.monitor + 1 }));
    }
  });

  useEffect(() => {
    const t = setInterval(() => {
      if (Date.now() - lastEventAt.current > FADE_MS) {
        setBadges((b) =>
          b.incidents === 0 && b.monitor === 0 ? b : { incidents: 0, monitor: 0 },
        );
      }
    }, 1000);
    return () => clearInterval(t);
  }, []);

  return {
    incidents: location.pathname.startsWith("/app/incidents") ? 0 : badges.incidents,
    monitor: location.pathname.startsWith("/app/monitor") ? 0 : badges.monitor,
  };
}
