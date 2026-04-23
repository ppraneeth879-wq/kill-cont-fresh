import { motion } from "framer-motion";
import { useNavigate } from "react-router-dom";
import { useIncidents } from "./useIncidents";

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
  const incidents = incidentsQuery.data?.items ?? [];
  const selected = incidents[0];

  return (
    <div className="page-frame">
      <motion.section
        animate={{ opacity: 1, y: 0 }}
        className="page-section page-section--compact"
        initial={{ opacity: 0, y: 16 }}
        transition={{ duration: 0.45, ease: "easeOut" }}
      >
        <div className="section-heading">
          <span className="eyebrow">Incidents</span>
          <h1 className="section-title">A workbench for evidence-backed decisions.</h1>
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
            {incidents.map((incident) => (
              <article className="stack-list__item" key={incident.incident_id}>
                <div className="stack-list__meta">
                  <span className={`status-pill ${severityClass(incident.severity)}`}>
                    {toLabel(incident.severity)}
                  </span>
                  <span>{incident.platform}</span>
                </div>
                <strong>{incident.title}</strong>
                <p>{incident.matched_asset}</p>
                <div className="auth-panel__actions">
                  <button
                    className="pill-link pill-link--ghost"
                    onClick={() => navigate(`/app/incidents/${incident.incident_id}`)}
                    type="button"
                  >
                    Open detail
                  </button>
                </div>
              </article>
            ))}
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
              <h2 className="panel__title">{selected?.title ?? "No incident selected"}</h2>
            </div>
            <span className={`status-pill ${severityClass(selected?.severity)}`}>
              {toLabel(selected?.severity)}
            </span>
          </div>

          <div className="comparison-grid">
            <div className="media-frame media-frame--official">
              <span>Official broadcast asset</span>
            </div>
            <div className="media-frame media-frame--detected">
              <span>Detected reposted upload</span>
            </div>
          </div>

          <div className="detail-grid">
            <article className="detail-card">
              <span className="detail-card__label">Why it matched</span>
              <p>
                High alignment across protected keyframes, preserved scoreboard geometry, and
                matching end-sequence choreography.
              </p>
            </article>
            <article className="detail-card">
              <span className="detail-card__label">Trust gap</span>
              <p>
                The official asset remains verified while the reposted upload appears detached
                from the trust record.
              </p>
            </article>
            <article className="detail-card">
              <span className="detail-card__label">Spread context</span>
              <p>{selected?.region ?? "No spread data yet"}</p>
            </article>
            <article className="detail-card">
              <span className="detail-card__label">Recommendation</span>
              <p>Escalate due to confidence, missing credential, and growing repost velocity.</p>
            </article>
          </div>
        </article>
      </section>
    </div>
  );
}
