import { useState } from "react";
import { motion } from "framer-motion";
import { api } from "../../lib/api";
import { useSSE } from "../../lib/sse";
import type { LiveSegmentEvent } from "../../lib/types";

type SegmentRow = {
  minute: string;
  source: string;
  status: string;
  latency: string;
};

const fallbackSegments: SegmentRow[] = [
  { minute: "74:18", source: "Primary feed A", status: "Segment clean", latency: "31s" },
  { minute: "74:24", source: "Short relay node", status: "Signal match", latency: "44s" },
  { minute: "74:31", source: "Mirror ingest", status: "Restream suspected", latency: "52s" },
];

export function LiveWatchPage() {
  const [segments, setSegments] = useState<SegmentRow[]>([]);
  const [starting, setStarting] = useState(false);

  useSSE((event) => {
    if (event.type !== "live.segment") return;
    const data = event.data as unknown as LiveSegmentEvent;
    const segment: SegmentRow = {
      minute: data.minute,
      source: data.source,
      status: data.status,
      latency: `${data.latency_seconds}s`,
    };
    setSegments((previous) => [segment, ...previous].slice(0, 10));
  });

  async function startLive() {
    setStarting(true);
    try {
      await api("/demo/live/start", {
        method: "POST",
        body: { segments: 5, interval_seconds: 2 },
      });
    } finally {
      setStarting(false);
    }
  }

  const liveSegments = segments.length > 0 ? segments : fallbackSegments;

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
            <span className="eyebrow">Live watch</span>
            <h1 className="section-title">Near-real-time segment monitoring for active events.</h1>
          </div>
          <div className="auth-panel__actions">
            <span className="status-pill status-pill--monitor">Semifinal stream active</span>
            <button className="pill-link pill-link--frosted" disabled={starting} onClick={startLive} type="button">
              {starting ? "Starting..." : "Start live event"}
            </button>
          </div>
        </div>
      </motion.section>

      <section className="live-grid">
        <article className="panel">
          <div className="panel__header">
            <div>
              <span className="eyebrow eyebrow--muted">Segment stream</span>
              <h2 className="panel__title">Latest segment states</h2>
            </div>
          </div>
          <div className="stack-list">
            {liveSegments.map((segment) => (
              <article className="stack-list__item" key={`${segment.minute}-${segment.source}`}>
                <div className="stack-list__meta">
                  <span>{segment.minute}</span>
                  <span>{segment.source}</span>
                </div>
                <strong>{segment.status}</strong>
                <p>Detection latency: {segment.latency}</p>
              </article>
            ))}
          </div>
        </article>

        <article className="panel">
          <div className="panel__header">
            <div>
              <span className="eyebrow eyebrow--muted">Live timeline</span>
              <h2 className="panel__title">Signal pressure over the last minute</h2>
            </div>
          </div>
          <div className="timeline-stage">
            <span className="timeline-stage__bar timeline-stage__bar--low" />
            <span className="timeline-stage__bar timeline-stage__bar--mid" />
            <span className="timeline-stage__bar timeline-stage__bar--high" />
            <span className="timeline-stage__bar timeline-stage__bar--peak" />
            <span className="timeline-stage__line" />
          </div>
        </article>
      </section>
    </div>
  );
}
