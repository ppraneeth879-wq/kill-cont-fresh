import { motion } from "framer-motion";
import { DemoControlPanel } from "../demo/DemoControlPanel";

export function SettingsPage() {
  return (
    <div className="page-frame page-frame--narrow">
      <motion.section
        animate={{ opacity: 1, y: 0 }}
        className="page-section page-section--compact"
        initial={{ opacity: 0, y: 16 }}
        transition={{ duration: 0.45, ease: "easeOut" }}
      >
        <div className="section-heading">
          <span className="eyebrow">Settings</span>
          <h1 className="section-title">Project switches for the hackathon build.</h1>
        </div>

        <div className="card-grid card-grid--two">
          <article className="glass-card">
            <h3>Monitoring mode</h3>
            <p>Mixed real plus simulated connectors for a stable demo and believable operations story.</p>
          </article>
          <article className="glass-card">
            <h3>AI mode</h3>
            <p>Vertex AI embeddings for similarity and Gemini for bounded incident explanation only.</p>
          </article>
          <DemoControlPanel />
        </div>
      </motion.section>
    </div>
  );
}
