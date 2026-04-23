import { useState } from "react";
import { motion } from "framer-motion";
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
            <span className="meta-chip__label">Filter</span>
            <span>Video + Image + Live Watch</span>
          </span>
          <span className="meta-chip meta-chip--compact">
            <span className="meta-chip__label">Event</span>
            <span>Championship Night</span>
          </span>
        </div>

        <div className="table-grid">
          <div className="table-grid__head">
            <span>Asset</span>
            <span>Type</span>
            <span>Provenance</span>
            <span>Status</span>
            <span>Incidents</span>
          </div>
          {assets.map((asset) => (
            <article className="table-grid__row" key={asset.asset_id}>
              <div>
                <strong>{asset.title}</strong>
                <p>{asset.event_name}</p>
              </div>
              <span>{toLabel(asset.asset_type)}</span>
              <span className={`status-pill ${provenanceClass(asset.provenance_status)}`}>
                {toLabel(asset.provenance_status)}
              </span>
              <span>{toLabel(asset.status)}</span>
              <span>{asset.incident_count}</span>
            </article>
          ))}
          {assets.length === 0 && (
            <article className="table-grid__row">
              <div>
                <strong>No protected assets yet</strong>
                <p>Upload your first official image or clip.</p>
              </div>
              <span>-</span>
              <span>-</span>
              <span>-</span>
              <span>0</span>
            </article>
          )}
        </div>

        <AssetUploadModal onClose={() => setShowUploader(false)} open={showUploader} />
      </section>
    </div>
  );
}
