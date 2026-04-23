import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { api, apiBase, getToken } from "../../lib/api";
import type { AssetDetail, AssetSummary } from "../../lib/types";

type ListResponse = { items: AssetSummary[] };

export function useAssets() {
  return useQuery<ListResponse>({
    queryKey: ["assets"],
    queryFn: () => api<ListResponse>("/assets"),
    refetchOnWindowFocus: false,
  });
}

export function useAssetUpload() {
  const qc = useQueryClient();
  return useMutation<
    AssetDetail,
    Error,
    {
      title: string;
      asset_type: string;
      event_name?: string;
      description?: string;
      provenance_status: string;
      file: File;
    }
  >({
    mutationFn: async (body) => {
      // Create the asset row first.
      const created = await api<{ id: string; upload_url: string }>("/assets", {
        method: "POST",
        body: {
          title: body.title,
          asset_type: body.asset_type,
          event_name: body.event_name,
          description: body.description,
          provenance_status: body.provenance_status,
        },
      });

      // Upload binary via multipart. ``api()`` can't set form data natively.
      const form = new FormData();
      form.append("file", body.file);
      const res = await fetch(`${apiBase()}/assets/${created.id}/upload`, {
        method: "POST",
        headers: { Authorization: `Bearer ${getToken()}` },
        body: form,
      });
      if (!res.ok) {
        throw new Error(`${res.status} ${res.statusText}`);
      }
      return (await res.json()) as AssetDetail;
    },
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["assets"] });
      qc.invalidateQueries({ queryKey: ["dashboard", "overview"] });
    },
  });
}
