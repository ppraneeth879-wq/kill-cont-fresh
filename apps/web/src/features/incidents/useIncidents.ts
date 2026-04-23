import { useEffect, useState } from "react";
import { useQuery, useQueryClient } from "@tanstack/react-query";
import { api } from "../../lib/api";
import { useSSE } from "../../lib/sse";
import type { IncidentSummary } from "../../lib/types";

type ListResponse = { items: IncidentSummary[] };

export function useIncidents({ live = false } = {}) {
  const qc = useQueryClient();
  const [freshIds, setFreshIds] = useState<Set<string>>(new Set());

  const query = useQuery<ListResponse>({
    queryKey: ["incidents"],
    queryFn: () => api<ListResponse>("/incidents"),
    refetchOnWindowFocus: false,
  });

  useSSE(
    (ev) => {
      if (ev.type === "incident.created" || ev.type === "incident.updated") {
        const id = (ev.data?.incident_id as string | undefined) ?? "";
        if (ev.type === "incident.created" && id) {
          setFreshIds((prev) => {
            const next = new Set(prev);
            next.add(id);
            return next;
          });
          // Clear the "pulse" flag after animation plays.
          setTimeout(() => {
            setFreshIds((prev) => {
              const next = new Set(prev);
              next.delete(id);
              return next;
            });
          }, 4500);
        }
        qc.invalidateQueries({ queryKey: ["incidents"] });
        qc.invalidateQueries({ queryKey: ["dashboard", "overview"] });
      }
      if (ev.type === "demo.seeded" || ev.type === "demo.reset") {
        setFreshIds(new Set());
        qc.invalidateQueries({ queryKey: ["incidents"] });
      }
    },
    live,
  );

  useEffect(() => {
    return () => setFreshIds(new Set());
  }, []);

  return { ...query, freshIds };
}
