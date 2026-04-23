import { motion } from "framer-motion";
import { useSearchParams } from "react-router-dom";
import { mediaUrl } from "../../lib/api";
import { useIncidentDetail } from "../incidents/useIncidentDetail";
import { useIncidents } from "../incidents/useIncidents";

function severityClass(severity: string | undefined): string {
  const normalized = (severity ?? "monitor").toLowerCase();
  if (normalized === "strike") return "status-pill--strike";
  if (normalized === "verified") return "status-pill--verified";
  return "status-pill--monitor";
}

function toLabel(value: string | undefined): string {
  if (!value) return "Unknown";
  return value.charAt(0).toUpperCase() + value.slice(1);
}

export function EvidencePage() {
  const [searchParams] = useSearchParams();
  const incidentsQuery = useIncidents();
  const incidents = incidentsQuery.data?.items ?? [];
  const selectedId = searchParams.get("incidentId") ?? incidents[0]?.incident_id;
  const detailQuery = useIncidentDetail(selectedId);
  const detail = detailQuery.data;

  const points = [
    detail?.reason_short,
    detail?.reason_detailed,
    detail?.operator_copy,
    detail?.candidates[0]
      ? `Similarity ${(detail.candidates[0].similarity_score * 100).toFixed(1)}% with ${detail.candidates[0].confidence_band} confidence.`
      : "Candidate matching details are not available.",
  ].filter((value): value is string => Boolean(value));

  const officialPreview = mediaUrl(detail?.asset.preview_path ?? detail?.asset.primary_path);
  const detectedPreview = mediaUrl(detail?.feed_item.preview_path ?? detail?.feed_item.media_path);

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
            <span className="eyebrow">Evidence pack</span>
            <h1 className="section-title">A case view operators can trust and explain.</h1>
          </div>
          <button className="pill-link pill-link--frosted" type="button">
            Prepare notice
          </button>
        </div>
      </motion.section>

      <section className="evidence-grid">
        <article className="panel panel--detail">
          <div className="panel__header">
            <div>
              <span className="eyebrow eyebrow--muted">Case summary</span>
              <h2 className="panel__title">{selectedId ?? "No incident selected"}</h2>
            </div>
            <span className={`status-pill ${severityClass(detail?.severity)}`}>
              {toLabel(detail?.severity)}
            </span>
          </div>
          <div className="comparison-grid">
            <div className="media-frame media-frame--official" style={officialPreview ? { padding: 0, overflow: "hidden" } : undefined}>
              {officialPreview ? (
                <img
                  alt="Official asset snapshot"
                  src={officialPreview}
                  style={{ width: "100%", height: "100%", objectFit: "cover" }}
                />
              ) : (
                <span>Official asset snapshot</span>
              )}
            </div>
            <div className="media-frame media-frame--detected" style={detectedPreview ? { padding: 0, overflow: "hidden" } : undefined}>
              {detectedPreview ? (
                <img
                  alt="Captured suspicious upload"
                  src={detectedPreview}
                  style={{ width: "100%", height: "100%", objectFit: "cover" }}
                />
              ) : (
                <span>Captured suspicious upload</span>
              )}
            </div>
          </div>
        </article>

        <article className="panel">
          <div className="panel__header">
            <div>
              <span className="eyebrow eyebrow--muted">Why we believe this case matters</span>
              <h2 className="panel__title">Structured evidence points</h2>
            </div>
          </div>
          <ul className="signal-list">
            {points.map((point) => (
              <li key={point}>{point}</li>
            ))}
            {points.length === 0 && <li>No evidence points yet. Seed and simulate from Settings.</li>}
          </ul>
        </article>
      </section>
    </div>
  );
}
