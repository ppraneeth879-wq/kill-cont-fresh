import { useMemo, useState } from "react";
import { motion } from "framer-motion";
import { useNavigate } from "react-router-dom";
import { api } from "../../lib/api";
import { useSSE } from "../../lib/sse";
import type { LiveSegmentEvent } from "../../lib/types";
import { useIncidents } from "../incidents/useIncidents";
import { useAssets } from "../assets/useAssets";
import { ThreatMap } from "../shared/ThreatMap";
import { ContextHeader } from "../../components/layout/ContextHeader";

type SegmentRow = {
  minute: string;
  source: string;
  status: string;
  latency: string;
  at: string;
};

function severityClass(severity: string | undefined): string {
  const normalized = (severity ?? "monitor").toLowerCase();
  if (normalized === "strike") return "status-pill--strike";
  if (normalized === "verified") return "status-pill--verified";
  return "status-pill--monitor";
}

export function LiveWatchPage() {
  const navigate = useNavigate();
  const [segments, setSegments] = useState<SegmentRow[]>([]);
  const [starting, setStarting] = useState(false);
  const [connected, setConnected] = useState(false);
  const [selectedAssetId, setSelectedAssetId] = useState<string>("__auto__");
  const incidentsQuery = useIncidents({ live: true });
  const allIncidents = incidentsQuery.data?.items ?? [];
  const latestIncidents = allIncidents.slice(0, 4);
  const freshIds = incidentsQuery.freshIds;
  const assetsQuery = useAssets();
  const assets = useMemo(
    () => assetsQuery.data?.items ?? [],
    [assetsQuery.data?.items],
  );

  useSSE((event) => {
    setConnected(true);
    if (event.type !== "live.segment") return;
    const data = event.data as unknown as LiveSegmentEvent;
    const segment: SegmentRow = {
      minute: data.minute,
      source: data.source,
      status: data.status,
      latency: `${data.latency_seconds}s`,
      at: new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit", second: "2-digit" }),
    };
    setSegments((previous) => [segment, ...previous].slice(0, 12));
  });

  async function startLive() {
    setStarting(true);
    try {
      const payload: Record<string, unknown> = {
        segments: 8,
        interval_seconds: 2,
      };
      if (selectedAssetId && selectedAssetId !== "__auto__") {
        payload.asset_id = selectedAssetId;
      }
      await api("/demo/live/start", {
        method: "POST",
        body: payload,
      });
    } finally {
      setStarting(false);
    }
  }

  return (
    <div className="page-frame">
      <motion.section
        animate={{ opacity: 1, y: 0 }}
        className="page-section page-section--compact"
        initial={{ opacity: 0, y: 16 }}
        transition={{ duration: 0.45, ease: "easeOut" }}
      >
        <ContextHeader
          eyebrow="Live watch · simulated stream"
          title="Near-real-time segment monitoring"
          subtitle="Demo stream: a deterministic 8-segment loop is emitted over SSE; ~2–3 segments per run flip to 'Signal match' or 'Restream suspected' and promote a real incident with rotating platform/region so the matcher rail visibly cycles. Pick an asset to scope the next run, or leave it on auto-pick."
          actions={
            <>
              <label className="live-watch__selector">
                <span className="live-watch__selector-label">Asset</span>
                <select
                  value={selectedAssetId}
                  onChange={(e) => setSelectedAssetId(e.target.value)}
                  className="live-watch__select"
                >
                  <option value="__auto__">Auto-pick (random)</option>
                  {assets.map((a) => (
                    <option value={a.asset_id} key={a.asset_id}>
                      {a.asset_id} — {a.title}
                    </option>
                  ))}
                </select>
              </label>
              <span
                className="status-pill status-pill--monitor"
                style={{ display: "inline-flex", alignItems: "center", gap: 6 }}
              >
                <span className={connected ? "status-dot status-dot--ok" : "status-dot status-dot--muted"} aria-hidden />
                {connected ? "SSE connected" : "Awaiting stream"}
              </span>
              <button
                className="pill-link pill-link--solid"
                disabled={starting}
                onClick={startLive}
                type="button"
              >
                {starting ? "Starting..." : "Start live event"}
              </button>
            </>
          }
        />
      </motion.section>

      <section className="page-section" style={{ marginBottom: 16 }}>
        <article className="panel panel--map">
          <div className="panel__header">
            <div>
              <span className="eyebrow eyebrow--muted">Global spread</span>
              <h2 className="panel__title">Where incidents are surfacing</h2>
            </div>
            <span className="status-pill status-pill--monitor">
              {allIncidents.length} incidents on map
            </span>
          </div>
          <ThreatMap
            incidents={allIncidents}
            freshIds={freshIds}
            height={300}
            onSelect={(id) => navigate(`/app/incidents/${id}`)}
          />
        </article>
      </section>

      <section className="live-grid">
        <article className="panel">
          <div className="panel__header">
            <div>
              <span className="eyebrow eyebrow--muted">Segment stream</span>
              <h2 className="panel__title">Latest segments ({segments.length})</h2>
            </div>
          </div>
          <div className="stack-list">
            {segments.map((segment, index) => (
              <article
                className="stack-list__item"
                key={`${segment.minute}-${segment.source}-${index}`}
                style={
                  index === 0
                    ? { boxShadow: "0 0 0 2px rgba(120,180,255,0.35)", transition: "box-shadow 0.4s ease" }
                    : undefined
                }
              >
                <div className="stack-list__meta">
                  <span>{segment.minute}</span>
                  <span>{segment.source}</span>
                  <span style={{ marginLeft: "auto", opacity: 0.6 }}>{segment.at}</span>
                </div>
                <strong>{segment.status}</strong>
                <p>Detection latency: {segment.latency}</p>
              </article>
            ))}
            {segments.length === 0 && (
              <article
                className="stack-list__item"
                style={{
                  textAlign: "center",
                  padding: "28px 20px",
                }}
              >
                <strong>No live segments yet</strong>
                <p style={{ marginTop: 6 }}>
                  Click <em>Start live event</em> above. The backend will push ~8 segments over SSE;
                  each one is fingerprinted and matched against your registered assets in real time.
                </p>
              </article>
            )}
          </div>
        </article>

        <article className="panel">
          <div className="panel__header">
            <div>
              <span className="eyebrow eyebrow--muted">Auto-triaged incidents</span>
              <h2 className="panel__title">Fresh from the matcher</h2>
            </div>
          </div>
          <div className="stack-list">
            {latestIncidents.map((incident) => {
              const isFresh = freshIds.has(incident.incident_id);
              return (
                <article
                  className={`stack-list__item${isFresh ? " stack-list__item--flash" : ""}`}
                  key={incident.incident_id}
                  onClick={() => navigate(`/app/incidents/${incident.incident_id}`)}
                  style={{ cursor: "pointer" }}
                >
                  <div className="stack-list__meta">
                    <span className={`status-pill ${severityClass(incident.severity)}`}>
                      {incident.severity}
                    </span>
                    <span>{incident.platform}</span>
                    {isFresh && (
                      <span
                        className="status-pill status-pill--monitor"
                        style={{ marginLeft: "auto", fontSize: 10 }}
                      >
                        NEW
                      </span>
                    )}
                  </div>
                  <strong>{incident.title}</strong>
                  {incident.summary && (
                    <p
                      style={{
                        marginTop: 4,
                        fontSize: 12,
                        color: "var(--ghost)",
                        overflow: "hidden",
                        textOverflow: "ellipsis",
                        display: "-webkit-box",
                        WebkitLineClamp: 2,
                        WebkitBoxOrient: "vertical",
                      }}
                    >
                      {incident.summary}
                    </p>
                  )}
                  <p style={{ marginTop: 4, fontSize: 11, opacity: 0.7 }}>
                    {incident.region}
                  </p>
                </article>
              );
            })}
            {latestIncidents.length === 0 && (
              <article className="stack-list__item">
                <strong>No incidents yet</strong>
                <p>Run the live stream to see the matcher form incidents in real time.</p>
              </article>
            )}
          </div>
        </article>
      </section>
    </div>
  );
}
