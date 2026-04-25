import { useEffect, useMemo, useState } from "react";
import { motion } from "framer-motion";
import { useNavigate } from "react-router-dom";
import { mediaUrl } from "../../lib/api";
import { MediaFrame } from "../../components/ui/MediaFrame";
import { useIncidents } from "./useIncidents";
import { useIncidentDetail } from "./useIncidentDetail";

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

export function IncidentsPage() {
  const navigate = useNavigate();
  const incidentsQuery = useIncidents({ live: true });
  const incidents = useMemo(
    () => incidentsQuery.data?.items ?? [],
    [incidentsQuery.data?.items],
  );
  const freshIds = incidentsQuery.freshIds;

  const [selectedId, setSelectedId] = useState<string | undefined>(undefined);

  useEffect(() => {
    if (!selectedId && incidents.length > 0) {
      setSelectedId(incidents[0].incident_id);
    }
    if (selectedId && !incidents.some((i) => i.incident_id === selectedId) && incidents.length > 0) {
      setSelectedId(incidents[0].incident_id);
    }
  }, [incidents, selectedId]);

  const detailQuery = useIncidentDetail(selectedId);
  const detail = detailQuery.data;
  const selectedSummary = incidents.find((i) => i.incident_id === selectedId);
  const topCandidate = detail?.candidates[0];

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
            <span className="eyebrow">Incidents</span>
            <h1 className="section-title">A workbench for evidence-backed decisions.</h1>
          </div>
          <span className="meta-chip meta-chip--compact">
            <span className="meta-chip__label">Queue</span>
            <span>{incidents.length} incidents</span>
          </span>
        </div>
      </motion.section>

      <section className="incident-workbench">
        <article className="panel">
          <div className="panel__header">
            <div>
              <span className="eyebrow eyebrow--muted">Incident list</span>
              <h2 className="panel__title">Priority queue</h2>
            </div>
          </div>
          <div className="stack-list">
            {incidents.map((incident) => {
              const isSelected = incident.incident_id === selectedId;
              const isFresh = freshIds.has(incident.incident_id);
              return (
                <article
                  className="stack-list__item"
                  key={incident.incident_id}
                  onClick={() => setSelectedId(incident.incident_id)}
                  role="button"
                  tabIndex={0}
                  onKeyDown={(event) => {
                    if (event.key === "Enter" || event.key === " ") {
                      event.preventDefault();
                      setSelectedId(incident.incident_id);
                    }
                  }}
                  style={{
                    cursor: "pointer",
                    outline: isSelected ? "1px solid rgba(120,150,255,0.55)" : "none",
                    outlineOffset: 2,
                    boxShadow: isFresh ? "0 0 0 2px rgba(120,150,255,0.45)" : undefined,
                    transition: "box-shadow 0.4s ease, outline 0.2s ease",
                  }}
                >
                  <div className="stack-list__meta">
                    <span className={`status-pill ${severityClass(incident.severity)}`}>
                      {toLabel(incident.severity)}
                    </span>
                    <span>{incident.platform}</span>
                    {isFresh && (
                      <span
                        style={{
                          marginLeft: "auto",
                          fontSize: 10,
                          letterSpacing: 0.5,
                          color: "rgba(120,180,255,0.95)",
                          textTransform: "uppercase",
                        }}
                      >
                        ● New
                      </span>
                    )}
                  </div>
                  <strong>{incident.title}</strong>
                  <p>{incident.matched_asset}</p>
                  <div className="auth-panel__actions" onClick={(event) => event.stopPropagation()}>
                    <button
                      className="pill-link pill-link--ghost"
                      onClick={() => navigate(`/app/incidents/${incident.incident_id}`)}
                      type="button"
                    >
                      Open detail
                    </button>
                  </div>
                </article>
              );
            })}
            {incidents.length === 0 && (
              <article className="stack-list__item">
                <strong>No incidents yet</strong>
                <p>Seed the demo scenario from Settings to start the queue.</p>
              </article>
            )}
          </div>
        </article>

        <article className="panel panel--detail">
          <div className="panel__header">
            <div>
              <span className="eyebrow eyebrow--muted">Selected incident</span>
              <h2 className="panel__title">
                {detail?.title ?? selectedSummary?.title ?? "No incident selected"}
              </h2>
            </div>
            <span className={`status-pill ${severityClass(detail?.severity ?? selectedSummary?.severity)}`}>
              {toLabel(detail?.severity ?? selectedSummary?.severity)}
            </span>
          </div>

          <div className="comparison-grid">
            <MediaFrame
              src={officialPreview}
              alt="Official protected asset"
              variant="official"
              caption="Official asset"
            />
            <MediaFrame
              src={detectedPreview}
              alt="Detected suspicious upload"
              variant="detected"
              caption="Detected upload"
            />
          </div>

          <div className="detail-grid">
            <article className="detail-card">
              <span className="detail-card__label">Why it matched</span>
              <p>
                {detail?.reason_detailed ??
                  detail?.reason_short ??
                  selectedSummary?.summary ??
                  "Select an incident to see the AI-generated reason."}
              </p>
            </article>
            <article className="detail-card">
              <span className="detail-card__label">Similarity + trust</span>
              <p>
                {topCandidate
                  ? `${(topCandidate.similarity_score * 100).toFixed(1)}% pHash match (${topCandidate.confidence_band} confidence). `
                  : ""}
                {detail ? `Trust score ${(detail.trust_score * 100).toFixed(0)}%. ` : ""}
                Asset provenance: {toLabel(detail?.asset.provenance_status)}.
              </p>
            </article>
            <article className="detail-card">
              <span className="detail-card__label">Spread context</span>
              <p>
                {detail?.map_region ??
                  detail?.feed_item.source_region ??
                  selectedSummary?.region ??
                  "No spread data yet."}
                {detail?.feed_item.source_platform ? ` Platform: ${detail.feed_item.source_platform}.` : ""}
              </p>
            </article>
            <article className="detail-card">
              <span className="detail-card__label">Recommendation</span>
              <p>
                {detail?.operator_copy ??
                  "Open the detail page to review full evidence and choose an action."}
              </p>
            </article>
          </div>

          <div className="auth-panel__actions" style={{ marginTop: 12 }}>
            <button
              className="pill-link pill-link--solid"
              disabled={!selectedId}
              onClick={() => selectedId && navigate(`/app/incidents/${selectedId}`)}
              type="button"
            >
              Open full evidence
            </button>
            <button
              className="pill-link pill-link--frosted"
              disabled={!selectedId}
              onClick={() => selectedId && navigate(`/app/evidence?incidentId=${selectedId}`)}
              type="button"
            >
              View evidence pack
            </button>
          </div>
        </article>
      </section>
    </div>
  );
}
