import { useEffect, useState } from "react";
import { useQuery, useQueryClient } from "@tanstack/react-query";
import { api } from "../../lib/api";
import { useSSE } from "../../lib/sse";
import type { FeedItem } from "../../lib/types";

type ListResponse = { items: FeedItem[] };

// Bundle E: how long a freshly-ingested feed_item stays "fresh" in the UI.
const FRESH_WINDOW_MS = 4500;

export function useFeeds() {
  const qc = useQueryClient();
  const [freshIds, setFreshIds] = useState<Set<string>>(new Set());

  const query = useQuery<ListResponse>({
    queryKey: ["feeds"],
    queryFn: () => api<ListResponse>("/feeds"),
    refetchOnWindowFocus: false,
  });

  useSSE((ev) => {
    if (ev.type === "feed.ingested") {
      const id = (ev.data?.feed_item_id as string | undefined) ?? "";
      if (id) {
        setFreshIds((prev) => {
          const next = new Set(prev);
          next.add(id);
          return next;
        });
        setTimeout(() => {
          setFreshIds((prev) => {
            const next = new Set(prev);
            next.delete(id);
            return next;
          });
        }, FRESH_WINDOW_MS);
      }
      qc.invalidateQueries({ queryKey: ["feeds"] });
    }
    if (ev.type === "demo.seeded" || ev.type === "demo.reset") {
      setFreshIds(new Set());
      qc.invalidateQueries({ queryKey: ["feeds"] });
    }
  });

  useEffect(() => {
    return () => setFreshIds(new Set());
  }, []);

  return { ...query, freshIds };
}
