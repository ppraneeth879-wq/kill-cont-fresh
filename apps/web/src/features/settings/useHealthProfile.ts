import { useQuery } from "@tanstack/react-query";
import { api } from "../../lib/api";
import type { HealthProfile } from "../../lib/types";

export function useHealthProfile() {
  return useQuery<HealthProfile>({
    queryKey: ["health", "profile"],
    queryFn: () => api<HealthProfile>("/health/profile"),
    staleTime: 15_000,
    refetchInterval: 30_000,
  });
}
