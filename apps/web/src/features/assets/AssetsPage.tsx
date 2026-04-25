import { useState } from "react";
import { motion } from "framer-motion";
import { mediaUrl } from "../../lib/api";
import { AssetUploadModal } from "./AssetUploadModal";
import { useAssets } from "./useAssets";

function toLabel(value: string | undefined): string {
  if (!value) return "Unknown";
  return value
    .replace(/_/g, " ")
    .split(" ")
    .map((word) => word.charAt(0).toUpperCase() + word.slice(1))
    .join(" ");
}

function provenanceClass(status: string | undefined): string {
  const normalized = (status ?? "pending").toLowerCase();
  if (normalized === "verified") return "status-pill--verified";
  if (normalized === "present" || normalized === "pending") return "status-pill--monitor";
  return "status-pill--strike";
}

function Thumb({ src, label }: { src: string | undefined; label: string }) {
  if (!src) {
    return (
      <div
        aria-hidden
        style={{
          width: 56,
          height: 56,
          borderRadius: 8,
          background:
            "linear-gradient(135deg, rgba(80,100,140,0.4), rgba(30,30,55,0.6))",
          display: "flex",
          alignItems: "center",
          justifyContent: "center",
          color: "rgba(255,255,255,0.55)",
          fontSize: 10,
          letterSpacing: 0.5,
          textTransform: "uppercase",
          flexShrink: 0,
        }}
      >
        {label.slice(0, 3)}
      </div>
    );
  }
  return (
    <img
      alt={label}
      src={src}
      style={{
        width: 56,
        height: 56,
        borderRadius: 8,
        objectFit: "cover",
        flexShrink: 0,
        boxShadow: "0 2px 10px rgba(0,0,0,0.3)",
      }}
    />
  );
}

export function AssetsPage() {
  const [showUploader, setShowUploader] = useState(false);
  const assetsQuery = useAssets();
  const assets = assetsQuery.data?.items ?? [];

  return (
    <div className="page-frame">
      <motion.section
        animate={{ opacity: 1, y: 0 }}
        className="page-section page-section--compact"
        initial={{ opacity: 0, y: 16 }}
        transition={{ duration: 0.45, ease: "easeOut" }}
      >
        <div className="section-heading section-heading--inline">
          <div>
            <span className="eyebrow">Protected assets</span>
            <h1 className="section-title">Official media under watch.</h1>
          </div>
          <button
            className="pill-link pill-link--solid"
            onClick={() => setShowUploader((value) => !value)}
            type="button"
          >
            {showUploader ? "Close uploader" : "Register asset"}
          </button>
        </div>
      </motion.section>

      <section className="table-panel">
        <div className="table-panel__toolbar">
          <span className="meta-chip meta-chip--compact">
            <span className="meta-chip__label">Count</span>
            <span>{assets.length} registered</span>
          </span>
          <span className="meta-chip meta-chip--compact">
            <span className="meta-chip__label">Event</span>
            <span>Championship Night</span>
          </span>
        </div>

        <div
          className="stack-list"
          style={{ display: "flex", flexDirection: "column", gap: 10 }}
        >
          {assets.map((asset) => {
            const thumb = mediaUrl(asset.preview_path);
            return (
              <article
                className="stack-list__item"
                key={asset.asset_id}
                style={{
                  display: "grid",
                  gridTemplateColumns: "64px 1fr auto auto auto",
                  alignItems: "center",
                  gap: 16,
                }}
              >
                <Thumb src={thumb} label={asset.asset_type} />
                <div>
                  <strong>{asset.title}</strong>
                  <p style={{ margin: "4px 0 0", opacity: 0.75, fontSize: 12 }}>
                    {asset.event_name || "—"} · {toLabel(asset.asset_type)} ·{" "}
                    <span style={{ opacity: 0.7 }}>{asset.asset_id}</span>
                  </p>
                </div>
                <span className={`status-pill ${provenanceClass(asset.provenance_status)}`}>
                  {toLabel(asset.provenance_status)}
                </span>
                <span className="meta-chip meta-chip--compact">
                  <span className="meta-chip__label">Status</span>
                  <span>{toLabel(asset.status)}</span>
                </span>
                <span className="meta-chip meta-chip--compact">
                  <span className="meta-chip__label">Incidents</span>
                  <span>{asset.incident_count}</span>
                </span>
              </article>
            );
          })}
          {assets.length === 0 && (
            <article className="stack-list__item">
              <strong>No protected assets yet</strong>
              <p>Upload your first official image or clip to start monitoring.</p>
            </article>
          )}
        </div>

        <AssetUploadModal onClose={() => setShowUploader(false)} open={showUploader} />
      </section>
    </div>
  );
}
