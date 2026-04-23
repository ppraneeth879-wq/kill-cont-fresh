import { useQuery, useQueryClient } from "@tanstack/react-query";
import { api } from "../../lib/api";
import { useSSE } from "../../lib/sse";
import type { DashboardOverview } from "../../lib/types";

export function useDashboardOverview() {
  const qc = useQueryClient();
  const query = useQuery<DashboardOverview>({
    queryKey: ["dashboard", "overview"],
    queryFn: () => api<DashboardOverview>("/dashboard/overview"),
    refetchOnWindowFocus: false,
  });

  useSSE((ev) => {
    if (
      ev.type === "incident.created" ||
      ev.type === "incident.updated" ||
      ev.type === "demo.seeded" ||
      ev.type === "demo.reset"
    ) {
      qc.invalidateQueries({ queryKey: ["dashboard", "overview"] });
    }
  });

  return query;
}
