import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { api } from "../../lib/api";
import type { ActionRecord, IncidentDetail } from "../../lib/types";

export function useIncidentDetail(incidentId: string | undefined) {
  return useQuery<IncidentDetail>({
    queryKey: ["incident", incidentId],
    queryFn: () => api<IncidentDetail>(`/incidents/${incidentId}`),
    enabled: !!incidentId,
    refetchOnWindowFocus: false,
  });
}

export function useIncidentAction(incidentId: string | undefined) {
  const qc = useQueryClient();
  return useMutation<ActionRecord, Error, { type: string; notes?: string }>({
    mutationFn: (body) =>
      api<ActionRecord>(`/incidents/${incidentId}/action`, {
        method: "POST",
        body,
      }),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["incident", incidentId] });
      qc.invalidateQueries({ queryKey: ["incidents"] });
      qc.invalidateQueries({ queryKey: ["dashboard", "overview"] });
    },
  });
}
