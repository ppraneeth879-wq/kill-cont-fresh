import { motion } from "framer-motion";
import { useIncidents } from "../incidents/useIncidents";
import { useDashboardOverview } from "./useDashboardOverview";

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

export function OverviewPage() {
  const overviewQuery = useDashboardOverview();
  const incidentsQuery = useIncidents({ live: true });

  const metrics = overviewQuery.data?.metrics ?? [];
  const liveIncidents = incidentsQuery.data?.items ?? overviewQuery.data?.recent_incidents ?? [];
  const actionQueue =
    liveIncidents.slice(0, 3).map((incident) => `Review ${incident.title.toLowerCase()}`) ?? [];

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
            <span className="eyebrow">Overview</span>
            <h1 className="section-title">Realtime rights protection at a glance.</h1>
          </div>
          <div className="section-heading__meta">
            <span className="meta-chip meta-chip--compact">
              <span className="meta-chip__label">Org</span>
              <span>KillCont Sports Demo</span>
            </span>
          </div>
        </div>

        <div className="metric-grid">
          {metrics.map((metric) => (
            <article className="metric-card metric-card--product" key={metric.label}>
              <span className="metric-card__label">{metric.label}</span>
              <strong className="metric-card__value">{metric.value}</strong>
              <span className="metric-card__delta">{metric.delta}</span>
            </article>
          ))}
        </div>
      </motion.section>

      <section className="dashboard-grid">
        <article className="panel panel--map">
          <div className="panel__header">
            <div>
              <span className="eyebrow eyebrow--muted">Threat map</span>
              <h2 className="panel__title">Propagation hotspots</h2>
            </div>
            <span className="status-pill status-pill--monitor">
              {Math.max(1, Math.min(3, liveIncidents.length || 1))} active chains
            </span>
          </div>
          <div className="map-stage">
            <span className="map-stage__cluster map-stage__cluster--one" />
            <span className="map-stage__cluster map-stage__cluster--two" />
            <span className="map-stage__cluster map-stage__cluster--three" />
            <span className="map-stage__arc map-stage__arc--one" />
            <span className="map-stage__arc map-stage__arc--two" />
            <span className="map-stage__arc map-stage__arc--three" />
          </div>
        </article>

        <article className="panel">
          <div className="panel__header">
            <div>
              <span className="eyebrow eyebrow--muted">Live queue</span>
              <h2 className="panel__title">Newest incidents</h2>
            </div>
          </div>
          <div className="stack-list">
            {liveIncidents.map((incident) => (
              <article className="stack-list__item" key={incident.incident_id}>
                <div className="stack-list__meta">
                  <span className={`status-pill ${severityClass(incident.severity)}`}>
                    {toLabel(incident.severity)}
                  </span>
                  <span>{incident.incident_id}</span>
                </div>
                <strong>{incident.title}</strong>
                <p>{incident.summary}</p>
              </article>
            ))}
          </div>
        </article>

        <article className="panel">
          <div className="panel__header">
            <div>
              <span className="eyebrow eyebrow--muted">Action queue</span>
              <h2 className="panel__title">What needs a decision</h2>
            </div>
          </div>
          <ul className="signal-list">
            {actionQueue.length > 0 ? (
              actionQueue.map((item) => <li key={item}>{item}</li>)
            ) : (
              <li>No active incidents yet. Seed the scenario from Settings.</li>
            )}
          </ul>
        </article>
      </section>
    </div>
  );
}
