import { motion } from "framer-motion";
import { useFeeds } from "./useFeeds";

function formatTime(value: string | undefined): string {
  if (!value) return "--:--";
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return "--:--";
  return date.toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" });
}

export function MonitorPage() {
  const feedsQuery = useFeeds();
  const feedRows = feedsQuery.data?.items ?? [];
  const selected = feedRows[0];

  return (
    <div className="page-frame">
      <motion.section
        animate={{ opacity: 1, y: 0 }}
        className="page-section page-section--compact"
        initial={{ opacity: 0, y: 16 }}
        transition={{ duration: 0.45, ease: "easeOut" }}
      >
        <div className="section-heading">
          <span className="eyebrow">Monitor</span>
          <h1 className="section-title">Incoming media before it becomes a case file.</h1>
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
            {feedRows.map((row) => (
              <article className="stack-list__item" key={row.id}>
                <div className="stack-list__meta">
                  <span>{row.source_platform ?? "unknown source"}</span>
                  <span>{formatTime(row.ingest_time)}</span>
                </div>
                <strong>{row.caption ?? "No caption provided"}</strong>
                <p>{row.source_region ?? "Region unavailable"}</p>
              </article>
            ))}
            {feedRows.length === 0 && (
              <article className="stack-list__item">
                <strong>No feed items yet</strong>
                <p>Start with seed or simulate actions in Settings.</p>
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
            <div className="media-frame media-frame--official">
              <span>{selected?.source_author ?? "Official protected clip"}</span>
            </div>
            <div className="media-frame media-frame--detected">
              <span>{selected?.caption ?? "Detected normalized upload"}</span>
            </div>
          </div>
        </article>
      </section>
    </div>
  );
}
