import { useQuery, useQueryClient } from "@tanstack/react-query";
import { api } from "../../lib/api";
import { useSSE } from "../../lib/sse";
import type { FeedItem } from "../../lib/types";

type ListResponse = { items: FeedItem[] };

export function useFeeds() {
  const qc = useQueryClient();
  const query = useQuery<ListResponse>({
    queryKey: ["feeds"],
    queryFn: () => api<ListResponse>("/feeds"),
    refetchOnWindowFocus: false,
  });
  useSSE((ev) => {
    if (ev.type === "feed.ingested" || ev.type === "demo.seeded" || ev.type === "demo.reset") {
      qc.invalidateQueries({ queryKey: ["feeds"] });
    }
  });
  return query;
}
