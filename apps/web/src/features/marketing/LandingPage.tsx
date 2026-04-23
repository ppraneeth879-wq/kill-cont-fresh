import { motion } from "framer-motion";
import { NavLink } from "react-router-dom";
import { incidents, overviewMetrics } from "../../lib/mock-data";

export function LandingPage() {
  return (
    <div className="page-frame page-frame--landing">
      <motion.section
        animate={{ opacity: 1, y: 0 }}
        className="hero"
        initial={{ opacity: 0, y: 18 }}
        transition={{ duration: 0.6, ease: "easeOut" }}
      >
        <div className="hero__copy">
          <span className="eyebrow">Digital asset protection for sports media</span>
          <h1 className="display-heading">
            Stop official media from disappearing into the web.
          </h1>
          <p className="body-large hero__body">
            KillCont helps rights holders authenticate official assets, detect altered
            re-uploads, and respond from one live command center.
          </p>

          <div className="hero__actions">
            <NavLink className="pill-link pill-link--solid" to="/app/overview">
              Open command center
            </NavLink>
            <a className="pill-link pill-link--frosted" href="#workflow">
              See the workflow
            </a>
          </div>

          <div className="hero__meta">
            <div className="meta-chip">
              <span className="meta-chip__label">Trust</span>
              <span>Provenance-aware registration</span>
            </div>
            <div className="meta-chip">
              <span className="meta-chip__label">Detection</span>
              <span>Edited image and video matching</span>
            </div>
            <div className="meta-chip">
              <span className="meta-chip__label">Action</span>
              <span>Live incidents, evidence, and triage</span>
            </div>
          </div>
        </div>

        <div className="hero__visual">
          <div className="product-shot">
            <div className="product-shot__toolbar">
              <span className="product-shot__tag">Overview</span>
              <span className="product-shot__hint">Realtime command center</span>
            </div>

            <div className="metric-grid">
              {overviewMetrics.map((metric) => (
                <div className="metric-card" key={metric.label}>
                  <span className="metric-card__label">{metric.label}</span>
                  <strong className="metric-card__value">{metric.value}</strong>
                  <span className="metric-card__delta">{metric.delta}</span>
                </div>
              ))}
            </div>

            <div className="product-shot__lower">
              <div className="mini-map">
                <span className="mini-map__label">Propagation map</span>
                <div className="mini-map__nodes">
                  <span className="mini-map__node mini-map__node--a" />
                  <span className="mini-map__node mini-map__node--b" />
                  <span className="mini-map__node mini-map__node--c" />
                  <span className="mini-map__arc mini-map__arc--one" />
                  <span className="mini-map__arc mini-map__arc--two" />
                </div>
              </div>

              <div className="incident-stack">
                {incidents.slice(0, 2).map((incident) => (
                  <article className="incident-brief" key={incident.id}>
                    <div className="incident-brief__header">
                      <span
                        className={`status-pill status-pill--${incident.severity.toLowerCase()}`}
                      >
                        {incident.severity}
                      </span>
                      <span className="incident-brief__id">{incident.id}</span>
                    </div>
                    <strong>{incident.title}</strong>
                    <p>{incident.summary}</p>
                  </article>
                ))}
              </div>
            </div>
          </div>
        </div>
      </motion.section>

      <section className="signal-strip">
        <div className="signal-strip__track">
          <span>Credential intact on 126 protected assets</span>
          <span>Edited clip match surfaced in 43 seconds</span>
          <span>One live relay chain flagged across three regions</span>
          <span>Evidence pack ready for operator review</span>
        </div>
      </section>

      <section className="page-section" id="workflow">
        <div className="section-heading">
          <span className="eyebrow">How it works</span>
          <h2 className="section-title">One visibility loop from source to response.</h2>
        </div>

        <div className="card-grid card-grid--three">
          <article className="glass-card">
            <span className="glass-card__index">01</span>
            <h3>Register trusted media</h3>
            <p>
              Upload official image and video assets, attach event context, and prepare them
              for monitoring with provenance and embedding-ready metadata.
            </p>
          </article>
          <article className="glass-card">
            <span className="glass-card__index">02</span>
            <h3>Detect edited reuse</h3>
            <p>
              Compare monitored media against protected assets using multimodal similarity,
              even after cropping, overlays, or re-encoding.
            </p>
          </article>
          <article className="glass-card">
            <span className="glass-card__index">03</span>
            <h3>Review and act</h3>
            <p>
              Surface incidents in a live dashboard with evidence, propagation context, and
              operator-ready recommendations.
            </p>
          </article>
        </div>
      </section>

      <section className="page-section" id="command-center">
        <div className="two-column">
          <div className="two-column__copy">
            <span className="eyebrow">Command center</span>
            <h2 className="section-title">A product that shows its own proof.</h2>
            <p className="body-copy">
              KillCont treats the dashboard, the map, and the evidence panel as the product
              itself. The UI is not decoration around the model. It is where trust is made
              legible.
            </p>
          </div>

          <div className="command-panel">
            <div className="command-panel__header">
              <span className="command-panel__title">Incident command</span>
              <span className="status-pill status-pill--monitor">Live signal</span>
            </div>
            <div className="command-panel__body">
              <div className="command-panel__comparison">
                <div className="media-frame media-frame--official">
                  <span>Official asset</span>
                </div>
                <div className="media-frame media-frame--detected">
                  <span>Detected upload</span>
                </div>
              </div>
              <ul className="signal-list">
                <li>Credential gap surfaced after repost normalization</li>
                <li>Semantic match remained strong after crop and overlay</li>
                <li>Spread velocity increased after the second mirror source</li>
              </ul>
            </div>
          </div>
        </div>
      </section>

      <section className="page-section" id="standout">
        <div className="section-heading">
          <span className="eyebrow">Why this stands out</span>
          <h2 className="section-title">Trust plus detection plus action.</h2>
        </div>

        <div className="standout-grid">
          <article className="feature-panel">
            <h3>Authenticity when it exists</h3>
            <p>
              Official assets can carry provenance signals that make the trust gap visible when
              suspicious copies circulate without them.
            </p>
          </article>
          <article className="feature-panel">
            <h3>Similarity when provenance is gone</h3>
            <p>
              Embedding-driven matching keeps detection alive after compression, mirroring, or
              platform transformation.
            </p>
          </article>
          <article className="feature-panel">
            <h3>Operational evidence, not raw scores</h3>
            <p>
              The product turns signals into an incident case with proof, spread context, and
              next actions.
            </p>
          </article>
        </div>
      </section>
    </div>
  );
}
