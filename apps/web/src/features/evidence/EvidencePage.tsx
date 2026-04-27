import { useEffect, useMemo, useRef, useState } from "react";
import { motion } from "framer-motion";
import { useNavigate, useSearchParams } from "react-router-dom";
import { apiBase, getToken, mediaUrl } from "../../lib/api";
import { MediaFrame } from "../../components/ui/MediaFrame";
import { TriageSourceChip } from "../../components/ui/TriageSourceChip";
import { ContextHeader } from "../../components/layout/ContextHeader";
import { useIncidentDetail } from "../incidents/useIncidentDetail";
import { useIncidents } from "../incidents/useIncidents";
import { useSSE } from "../../lib/sse";

function severityClass(severity: string | undefined): string {
  const normalized = (severity ?? "monitor").toLowerCase();
  if (normalized === "strike") return "status-pill--strike";
  if (normalized === "verified") return "status-pill--verified";
  return "status-pill--monitor";
}

function toLabel(value: string | undefined): string {
  if (!value) return "Unknown";
  return value
    .replace(/_/g, " ")
    .split(" ")
    .map((word) => word.charAt(0).toUpperCase() + word.slice(1))
    .join(" ");
}

type ProvenanceVisual = {
  label: string;
  className: string;
  icon: string;
  tooltip: string;
};

function provenanceVisual(status: string | undefined): ProvenanceVisual {
  const normalized = (status ?? "pending").toLowerCase();
  if (normalized === "verified") {
    return {
      label: "Provenance verified",
      className: "status-pill--verified",
      icon: "✓",
      tooltip: "C2PA credential intact on the official asset.",
    };
  }
  if (normalized === "credential_removed_suspected") {
    return {
      label: "Credential stripped",
      className: "status-pill--strike",
      icon: "✕",
      tooltip: "C2PA manifest appears to have been removed — strong reuse signal.",
    };
  }
  if (normalized === "present") {
    return {
      label: "Credential present",
      className: "status-pill--monitor",
      icon: "•",
      tooltip: "A provenance credential is attached but has not yet been verified.",
    };
  }
  return {
    label: "Provenance pending",
    className: "status-pill--monitor",
    icon: "…",
    tooltip: "No provenance signal captured yet for this asset.",
  };
}

export function EvidencePage() {
  const navigate = useNavigate();
  const [searchParams, setSearchParams] = useSearchParams();
  const incidentsQuery = useIncidents();
  const incidents = useMemo(
    () => incidentsQuery.data?.items ?? [],
    [incidentsQuery.data?.items],
  );
  const paramId = searchParams.get("incident") ?? searchParams.get("incidentId");
  const selectedId = paramId ?? incidents[0]?.incident_id;
  const detailQuery = useIncidentDetail(selectedId);
  const detail = detailQuery.data;

  const currentIndex = useMemo(
    () => incidents.findIndex((item) => item.incident_id === selectedId),
    [incidents, selectedId],
  );
  const prevIncident = currentIndex > 0 ? incidents[currentIndex - 1] : undefined;
  const nextIncident =
    currentIndex >= 0 && currentIndex < incidents.length - 1
      ? incidents[currentIndex + 1]
      : undefined;

  function goTo(incidentId: string | undefined) {
    if (!incidentId) return;
    const next = new URLSearchParams(searchParams);
    next.set("incident", incidentId);
    next.delete("incidentId");
    setSearchParams(next, { replace: false });
  }

  const [noticeState, setNoticeState] = useState<"idle" | "preparing" | "error">("idle");
  const [copyState, setCopyState] = useState<"idle" | "copied">("idle");

  // Bundle E: "N new cases" jump banner. Increments on incident.created
  // events that don't match the currently-viewed incident; auto-clears
  // after 30s of no new events, or immediately on click.
  const [incomingCount, setIncomingCount] = useState(0);
  const [latestNewId, setLatestNewId] = useState<string | null>(null);
  const lastEventAt = useRef<number>(0);

  useSSE((ev) => {
    if (ev.type !== "incident.created") return;
    const id = (ev.data?.incident_id as string | undefined) ?? "";
    if (!id || id === selectedId) return;
    setIncomingCount((c) => c + 1);
    setLatestNewId(id);
    lastEventAt.current = Date.now();
  });

  useEffect(() => {
    if (incomingCount === 0) return;
    const t = setInterval(() => {
      if (Date.now() - lastEventAt.current > 30_000) {
        setIncomingCount(0);
        setLatestNewId(null);
      }
    }, 1000);
    return () => clearInterval(t);
  }, [incomingCount]);

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
  const provenance = provenanceVisual(detail?.asset.provenance_status);

  async function prepareNotice() {
    if (!selectedId) return;
    setNoticeState("preparing");
    try {
      const res = await fetch(`${apiBase()}/incidents/${selectedId}/notice`, {
        headers: { Authorization: `Bearer ${getToken()}` },
      });
      if (!res.ok) throw new Error(`notice fetch failed: ${res.status}`);
      const blob = await res.blob();
      const url = URL.createObjectURL(blob);
      const link = document.createElement("a");
      link.href = url;
      link.download = `killcont-notice-${selectedId}.md`;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      URL.revokeObjectURL(url);
      setNoticeState("idle");
    } catch (err) {
      console.error(err);
      setNoticeState("error");
      setTimeout(() => setNoticeState("idle"), 2500);
    }
  }

  async function copyOperatorSummary() {
    if (!detail?.operator_copy) return;
    try {
      await navigator.clipboard.writeText(detail.operator_copy);
      setCopyState("copied");
      setTimeout(() => setCopyState("idle"), 1800);
    } catch (err) {
      console.error(err);
    }
  }

  const incidentRef = detail?.id ?? selectedId;
  const assetRef = detail?.asset.id;
  const feedRef = detail?.feed_item.id;

  const eyebrow = (
    <>
      <button type="button" onClick={() => navigate("/app/incidents")}>
        ← Incidents
      </button>
      <span aria-hidden>·</span>
      <span>Evidence pack</span>
      {incidentRef ? (
        <>
          <span aria-hidden>·</span>
          <span>{incidentRef}</span>
        </>
      ) : null}
    </>
  );

  const title = detail
    ? `Evidence · ${detail.id} — ${detail.asset.title}`
    : selectedId
      ? `Evidence · ${selectedId}`
      : "Evidence pack";

  const subtitle = detail ? (
    <>
      {assetRef ? <><b>Asset:</b> {assetRef}</> : null}
      {assetRef ? " · " : null}
      {feedRef ? <><b>Feed:</b> {feedRef}</> : null}
      {feedRef ? " · " : null}
      <b>Severity:</b> {toLabel(detail.severity)}
      {detail.candidates[0]
        ? ` · Similarity ${(detail.candidates[0].similarity_score * 100).toFixed(1)}%`
        : null}
    </>
  ) : (
    "A case view operators can trust and explain."
  );

  const actions = (
    <>
      {incomingCount > 0 && latestNewId && (
        <button
          className="pill-link pill-link--solid evidence-jump-banner"
          onClick={() => {
            goTo(latestNewId);
            setIncomingCount(0);
            setLatestNewId(null);
          }}
          type="button"
        >
          ⚡ {incomingCount} new case{incomingCount === 1 ? "" : "s"} — View latest
        </button>
      )}
      <button
        className="pill-link pill-link--ghost"
        disabled={!prevIncident}
        onClick={() => goTo(prevIncident?.incident_id)}
        type="button"
      >
        ← Prev
      </button>
      <button
        className="pill-link pill-link--ghost"
        disabled={!nextIncident}
        onClick={() => goTo(nextIncident?.incident_id)}
        type="button"
      >
        Next →
      </button>
      <button
        className="pill-link pill-link--ghost"
        disabled={!detail?.operator_copy}
        onClick={copyOperatorSummary}
        type="button"
      >
        {copyState === "copied" ? "Copied ✓" : "Copy summary"}
      </button>
      <button
        className="pill-link pill-link--frosted"
        disabled={!selectedId || noticeState === "preparing"}
        onClick={prepareNotice}
        type="button"
      >
        {noticeState === "preparing"
          ? "Preparing..."
          : noticeState === "error"
            ? "Retry notice"
            : "Export notice"}
      </button>
    </>
  );

  return (
    <div className="page-frame">
      <motion.section
        animate={{ opacity: 1, y: 0 }}
        className="page-section page-section--compact"
        initial={{ opacity: 0, y: 16 }}
        transition={{ duration: 0.45, ease: "easeOut" }}
      >
        <ContextHeader
          eyebrow={eyebrow}
          title={title}
          subtitle={subtitle}
          actions={actions}
        />
      </motion.section>

      <section className="evidence-grid">
        <article className="panel panel--detail">
          <div className="panel__header">
            <div>
              <span className="eyebrow eyebrow--muted">Case summary</span>
              <h2 className="panel__title">
                {detail?.title ?? selectedId ?? "No incident selected"}
              </h2>
            </div>
            <div style={{ display: "flex", gap: 8, alignItems: "center", flexWrap: "wrap" }}>
              {detail?.triage_source && (
                <TriageSourceChip
                  source={detail.triage_source}
                  model={detail.triage_model}
                  latencyMs={detail.triage_latency_ms}
                  size="md"
                />
              )}
              <span
                className={`status-pill ${provenance.className}`}
                title={provenance.tooltip}
                style={{ display: "inline-flex", alignItems: "center", gap: 6 }}
              >
                <span aria-hidden>{provenance.icon}</span>
                {provenance.label}
              </span>
              <span className={`status-pill ${severityClass(detail?.severity)}`}>
                {toLabel(detail?.severity)}
              </span>
            </div>
          </div>
          <div className="comparison-grid">
            <MediaFrame
              src={officialPreview}
              alt="Official asset snapshot"
              variant="official"
              caption="Official asset"
            />
            <MediaFrame
              src={detectedPreview}
              alt="Captured suspicious upload"
              variant="detected"
              caption="Captured upload"
            />
          </div>
          <ul className="signal-list" style={{ marginTop: 14 }}>
            <li>
              <strong>Asset:</strong> {detail?.asset.title ?? "—"}
              {detail?.asset.event_name ? ` · ${detail.asset.event_name}` : ""}
            </li>
            <li>
              <strong>Platform / region:</strong>{" "}
              {detail?.feed_item.source_platform ?? "—"} ·{" "}
              {detail?.map_region ?? detail?.feed_item.source_region ?? "—"}
            </li>
            <li>
              <strong>Author:</strong> {detail?.feed_item.source_author ?? "—"}
            </li>
            <li>
              <strong>Match:</strong>{" "}
              {detail?.candidates[0]
                ? `${(detail.candidates[0].similarity_score * 100).toFixed(1)}% pHash (${detail.candidates[0].confidence_band}) — Hamming ${detail.candidates[0].hamming_distance}`
                : "—"}
            </li>
            <li>
              <strong>Trust / spread:</strong>{" "}
              {detail
                ? `${(detail.trust_score * 100).toFixed(0)}% · ${(detail.spread_score * 100).toFixed(0)}%`
                : "—"}
            </li>
          </ul>
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
          {noticeState === "error" && (
            <p style={{ marginTop: 12, color: "#ff9aa8", fontSize: 12 }}>
              Notice generation failed. Check the backend log and try again.
            </p>
          )}
        </article>
      </section>
    </div>
  );
}
