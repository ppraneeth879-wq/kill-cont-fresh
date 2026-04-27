import { useMemo, useState } from "react";
import { motion } from "framer-motion";
import { useNavigate } from "react-router-dom";
import { mediaUrl } from "../../lib/api";
import { MediaFrame } from "../../components/ui/MediaFrame";
import { useFeeds } from "./useFeeds";
import { useIncidents } from "../incidents/useIncidents";

function formatTime(value: string | undefined): string {
  if (!value) return "--:--";
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return "--:--";
  return date.toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" });
}

function Thumb({ src, label }: { src: string | undefined; label: string }) {
  if (!src) {
    return (
      <div
        aria-hidden
        style={{
          width: 64,
          height: 64,
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
        width: 64,
        height: 64,
        borderRadius: 8,
        objectFit: "cover",
        flexShrink: 0,
        boxShadow: "0 2px 10px rgba(0,0,0,0.3)",
      }}
    />
  );
}

export function MonitorPage() {
  const navigate = useNavigate();
  const { freshIds, ...feedsQuery } = useFeeds();
  const incidentsQuery = useIncidents();
  const feedRows = feedsQuery.data?.items ?? [];

  // Build feed_item_id -> incident mapping so each feed row can deep-link
  // to its incident if the matcher created one.
  const feedToIncident = useMemo(() => {
    const map = new Map<string, { incident_id: string; severity: string }>();
    for (const incident of incidentsQuery.data?.items ?? []) {
      if (incident.feed_item_id) {
        map.set(incident.feed_item_id, {
          incident_id: incident.incident_id,
          severity: incident.severity,
        });
      }
    }
    return map;
  }, [incidentsQuery.data?.items]);

  const [selectedId, setSelectedId] = useState<string | undefined>(undefined);
  const selected =
    feedRows.find((row) => row.id === selectedId) ?? feedRows[0];
  const selectedIncident = selected ? feedToIncident.get(selected.id) : undefined;
  const selectedPreview = mediaUrl(selected?.preview_path ?? selected?.media_path);

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
            <span className="eyebrow">Monitor</span>
            <h1 className="section-title">Incoming media before it becomes a case file.</h1>
          </div>
          <span className="meta-chip meta-chip--compact">
            <span className="meta-chip__label">Inbox</span>
            <span>{feedRows.length} items</span>
          </span>
        </div>
      </motion.section>

      <section className="monitor-grid">
        <article className="panel">
          <div className="panel__header">
            <div>
              <span className="eyebrow eyebrow--muted">Live feed</span>
              <h2 className="panel__title">Normalized feed items</h2>
            </div>
          </div>
          <div className="stack-list">
            {feedRows.map((row) => {
              const thumb = mediaUrl(row.preview_path ?? row.media_path);
              const linked = feedToIncident.get(row.id);
              const isSelected = (selected?.id ?? feedRows[0]?.id) === row.id;
              const isFresh = freshIds.has(row.id);
              return (
                <article
                  className={`stack-list__item${isFresh ? " stack-list__item--flash" : ""}`}
                  key={row.id}
                  onClick={() => setSelectedId(row.id)}
                  role="button"
                  tabIndex={0}
                  style={{
                    cursor: "pointer",
                    display: "grid",
                    gridTemplateColumns: "72px 1fr auto",
                    alignItems: "center",
                    gap: 14,
                    outline: isSelected ? "1px solid rgba(120,150,255,0.45)" : "none",
                    outlineOffset: 2,
                  }}
                >
                  <Thumb src={thumb} label={row.content_type || "feed"} />
                  <div>
                    <div
                      className="stack-list__meta"
                      style={{ display: "flex", gap: 8, fontSize: 11, alignItems: "center" }}
                    >
                      <span>{row.source_platform ?? "unknown"}</span>
                      <span>·</span>
                      <span>{row.source_region ?? "—"}</span>
                      <span>·</span>
                      <span>{formatTime(row.ingest_time)}</span>
                      {isFresh && (
                        <span
                          className="status-pill status-pill--monitor"
                          style={{ marginLeft: 4, fontSize: 10, padding: "1px 6px" }}
                        >
                          NEW
                        </span>
                      )}
                    </div>
                    <strong style={{ display: "block", marginTop: 4 }}>
                      {row.caption ?? row.source_author ?? "No caption"}
                    </strong>
                    <p style={{ margin: "2px 0 0", fontSize: 11, opacity: 0.6 }}>
                      {row.id}
                    </p>
                  </div>
                  <div style={{ display: "flex", flexDirection: "column", gap: 6, alignItems: "flex-end" }}>
                    {linked ? (
                      <button
                        type="button"
                        onClick={(event) => {
                          event.stopPropagation();
                          navigate(`/app/incidents/${linked.incident_id}`);
                        }}
                        className={`status-pill ${
                          linked.severity === "strike"
                            ? "status-pill--strike"
                            : linked.severity === "verified"
                            ? "status-pill--verified"
                            : "status-pill--monitor"
                        }`}
                        style={{ cursor: "pointer", border: "none" }}
                        title="Open linked incident"
                      >
                        {linked.incident_id}
                      </button>
                    ) : (
                      <span
                        style={{
                          fontSize: 10,
                          opacity: 0.5,
                          textTransform: "uppercase",
                          letterSpacing: 0.5,
                        }}
                      >
                        No incident
                      </span>
                    )}
                  </div>
                </article>
              );
            })}
            {feedRows.length === 0 && (
              <article className="stack-list__item">
                <strong>No feed items yet</strong>
                <p>Seed the scenario or start live watch from Settings.</p>
              </article>
            )}
          </div>
        </article>

        <article className="panel">
          <div className="panel__header">
            <div>
              <span className="eyebrow eyebrow--muted">Selected capture</span>
              <h2 className="panel__title">Pre-incident review</h2>
            </div>
            <span className="status-pill status-pill--monitor">
              {selected?.source_platform ?? "Awaiting feed"}
            </span>
          </div>
          <div className="comparison-stack">
            <MediaFrame
              src={selectedPreview}
              alt={selected?.caption ?? "Detected upload"}
              variant="detected"
              caption={selected?.source_platform ?? undefined}
            />
            <ul
              className="signal-list"
              style={{ marginTop: 12 }}
            >
              <li>
                <strong>Author:</strong> {selected?.source_author ?? "—"}
              </li>
              <li>
                <strong>Region:</strong> {selected?.source_region ?? "—"}
              </li>
              <li>
                <strong>Caption:</strong> {selected?.caption ?? "—"}
              </li>
              <li>
                <strong>Ingested:</strong>{" "}
                {selected?.ingest_time
                  ? new Date(selected.ingest_time).toLocaleString()
                  : "—"}
              </li>
              {selectedIncident && (
                <li>
                  <strong>Incident:</strong>{" "}
                  <a
                    href={`/app/incidents/${selectedIncident.incident_id}`}
                    onClick={(event) => {
                      event.preventDefault();
                      navigate(`/app/incidents/${selectedIncident.incident_id}`);
                    }}
                  >
                    {selectedIncident.incident_id} ({selectedIncident.severity})
                  </a>
                </li>
              )}
            </ul>
          </div>
        </article>
      </section>
    </div>
  );
}
