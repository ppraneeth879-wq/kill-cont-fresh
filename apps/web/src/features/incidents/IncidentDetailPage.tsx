import { motion } from "framer-motion";
import { NavLink, useParams } from "react-router-dom";
import { mediaUrl } from "../../lib/api";
import { useIncidentAction, useIncidentDetail } from "./useIncidentDetail";

function toLabel(value: string | undefined): string {
  if (!value) return "Unknown";
  return value.charAt(0).toUpperCase() + value.slice(1);
}

function severityClass(severity: string | undefined): string {
  const normalized = (severity ?? "monitor").toLowerCase();
  if (normalized === "strike") return "status-pill--strike";
  if (normalized === "verified") return "status-pill--verified";
  return "status-pill--monitor";
}

export function IncidentDetailPage() {
  const { incidentId } = useParams();
  const { data, isLoading, isError } = useIncidentDetail(incidentId);
  const actionMutation = useIncidentAction(incidentId);

  if (isLoading) {
    return (
      <div className="page-frame page-frame--narrow">
        <section className="panel">
          <div className="panel__header">
            <div>
              <span className="eyebrow eyebrow--muted">Incident detail</span>
              <h2 className="panel__title">Loading incident...</h2>
            </div>
          </div>
        </section>
      </div>
    );
  }

  if (isError || !data) {
    return (
      <div className="page-frame page-frame--narrow">
        <section className="panel">
          <div className="panel__header">
            <div>
              <span className="eyebrow eyebrow--muted">Incident detail</span>
              <h2 className="panel__title">Incident not found</h2>
            </div>
            <NavLink className="pill-link pill-link--frosted" to="/app/incidents">
              Back to incidents
            </NavLink>
          </div>
        </section>
      </div>
    );
  }

  const officialPreview = mediaUrl(data.asset.preview_path ?? data.asset.primary_path);
  const detectedPreview = mediaUrl(data.feed_item.preview_path ?? data.feed_item.media_path);
  const topCandidate = data.candidates[0];

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
            <span className="eyebrow">Incident detail</span>
            <h1 className="section-title">{data.title}</h1>
          </div>
          <span className={`status-pill ${severityClass(data.severity)}`}>{toLabel(data.severity)}</span>
        </div>
      </motion.section>

      <section className="incident-workbench">
        <article className="panel">
          <div className="panel__header">
            <div>
              <span className="eyebrow eyebrow--muted">Context</span>
              <h2 className="panel__title">Case summary</h2>
            </div>
            <NavLink className="pill-link pill-link--frosted" to="/app/incidents">
              Back to incidents
            </NavLink>
          </div>
          <ul className="signal-list">
            <li>Asset: {data.asset.title}</li>
            <li>Platform: {data.feed_item.source_platform ?? "unknown"}</li>
            <li>Region: {data.map_region ?? data.feed_item.source_region ?? "unknown"}</li>
            <li>Trust score: {(data.trust_score * 100).toFixed(1)}%</li>
            <li>Operator status: {toLabel(data.operator_status)}</li>
            {topCandidate && (
              <li>
                Similarity: {(topCandidate.similarity_score * 100).toFixed(1)}% ({topCandidate.confidence_band})
              </li>
            )}
          </ul>
        </article>

        <article className="panel panel--detail">
          <div className="panel__header">
            <div>
              <span className="eyebrow eyebrow--muted">Evidence comparison</span>
              <h2 className="panel__title">Official vs detected upload</h2>
            </div>
          </div>

          <div className="comparison-grid">
            <div className="media-frame media-frame--official" style={officialPreview ? { padding: 0, overflow: "hidden" } : undefined}>
              {officialPreview ? (
                <img
                  alt="Official protected asset"
                  src={officialPreview}
                  style={{ width: "100%", height: "100%", objectFit: "cover" }}
                />
              ) : (
                <span>Official protected asset</span>
              )}
            </div>
            <div className="media-frame media-frame--detected" style={detectedPreview ? { padding: 0, overflow: "hidden" } : undefined}>
              {detectedPreview ? (
                <img
                  alt="Detected suspicious upload"
                  src={detectedPreview}
                  style={{ width: "100%", height: "100%", objectFit: "cover" }}
                />
              ) : (
                <span>Detected suspicious upload</span>
              )}
            </div>
          </div>

          <div className="detail-grid">
            <article className="detail-card">
              <span className="detail-card__label">Why it matched</span>
              <p>{data.reason_detailed ?? data.reason_short ?? "Similarity and spread analysis indicate this should be reviewed."}</p>
            </article>
            <article className="detail-card">
              <span className="detail-card__label">Trust gap</span>
              <p>
                Asset provenance: {toLabel(data.asset.provenance_status)}. Candidate provenance gap: {topCandidate?.provenance_gap ? "present" : "not detected"}.
              </p>
            </article>
            <article className="detail-card">
              <span className="detail-card__label">Operator copy</span>
              <p>{data.operator_copy ?? "Review and classify this case based on impact and spread."}</p>
            </article>
            <article className="detail-card">
              <span className="detail-card__label">Action</span>
              <p>Choose the next state to keep this incident queue accurate and auditable.</p>
            </article>
          </div>

          <div className="auth-panel__actions">
            <button
              className="pill-link pill-link--solid"
              disabled={actionMutation.isPending}
              onClick={() => actionMutation.mutate({ type: "escalate" })}
              type="button"
            >
              Escalate
            </button>
            <button
              className="pill-link pill-link--frosted"
              disabled={actionMutation.isPending}
              onClick={() => actionMutation.mutate({ type: "monitor" })}
              type="button"
            >
              Monitor
            </button>
            <button
              className="pill-link pill-link--ghost"
              disabled={actionMutation.isPending}
              onClick={() => actionMutation.mutate({ type: "ignore" })}
              type="button"
            >
              Ignore
            </button>
          </div>
        </article>
      </section>
    </div>
  );
}