import { useState } from "react";
import { motion } from "framer-motion";
import { useNavigate } from "react-router-dom";
import { api, TOKEN_KEY, USER_KEY } from "../../lib/api";
import type { GeminiSnapshot, TestGeminiResponse } from "../../lib/types";
import { ContextHeader } from "../../components/layout/ContextHeader";
import { useAuth } from "../auth/useAuth";
import { useHealthProfile } from "./useHealthProfile";
import { DemoControlPanel } from "../demo/DemoControlPanel";

function geminiTone(status: GeminiSnapshot["status"]): string {
  if (status === "ok") return "status-dot status-dot--ok";
  if (status === "unconfigured") return "status-dot status-dot--muted";
  return "status-dot status-dot--warn";
}

function geminiLabel(g: GeminiSnapshot): string {
  if (!g.configured) return "Unconfigured — fallback reasons only";
  if (g.status === "ok") return `Live (${g.model})`;
  if (g.status === "rate_limited") return "Rate limited — using fallback";
  if (g.status === "network_error") return "Network error — using fallback";
  if (g.status === "parse_error") return "Parse error — using fallback";
  if (g.status === "fallback") return "Idle — fallback on last call";
  return g.status;
}

function StatusRow({
  label,
  value,
  tone,
}: {
  label: string;
  value: React.ReactNode;
  tone?: string;
}) {
  return (
    <div className="status-row">
      <span className="status-row__label">{label}</span>
      <span className="status-row__value">
        {tone ? <span className={tone} aria-hidden /> : null}
        {value}
      </span>
    </div>
  );
}

export function SettingsPage() {
  const navigate = useNavigate();
  const { user, signOut } = useAuth();
  const profileQuery = useHealthProfile();
  const profile = profileQuery.data;

  const [testing, setTesting] = useState(false);
  const [testResult, setTestResult] = useState<TestGeminiResponse | null>(null);
  const [testError, setTestError] = useState<string | null>(null);

  async function runGeminiTest() {
    setTesting(true);
    setTestError(null);
    setTestResult(null);
    try {
      const res = await api<TestGeminiResponse>("/debug/test-gemini", {
        method: "POST",
        body: { severity: "monitor" },
      });
      setTestResult(res);
      await profileQuery.refetch();
    } catch (err) {
      setTestError(err instanceof Error ? err.message : "Test failed");
    } finally {
      setTesting(false);
    }
  }

  function handleSignOut() {
    signOut();
    try {
      localStorage.removeItem(TOKEN_KEY);
      localStorage.removeItem(USER_KEY);
    } catch {
      /* ignore */
    }
    navigate("/sign-in", { replace: true });
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
          eyebrow="Settings"
          title="System status and account"
          subtitle="Live view of the runtime profile, backends, and your operator account."
        />

        <div className="settings-grid">
          <article className="glass-card settings-card">
            <header className="settings-card__header">
              <h3>System status</h3>
              <span className="eyebrow eyebrow--muted">
                {profile ? `v${profile.app_version}` : "loading…"}
              </span>
            </header>
            {profileQuery.isLoading ? (
              <p className="settings-card__muted">Loading profile…</p>
            ) : profileQuery.isError || !profile ? (
              <p className="settings-card__muted">Could not load /health/profile.</p>
            ) : (
              <div className="status-list">
                <StatusRow
                  label="Runtime profile"
                  value={profile.runtime_profile}
                  tone="status-dot status-dot--ok"
                />
                <StatusRow label="Metadata backend" value={profile.metadata_backend} />
                <StatusRow label="Media backend" value={profile.media_backend} />
                <StatusRow label="Auth backend" value={profile.auth_backend} />
                <StatusRow
                  label="SSE state"
                  value={profile.sse_state}
                  tone="status-dot status-dot--ok"
                />
                <StatusRow
                  label="pHash threshold"
                  value={profile.phash_threshold.toFixed(2)}
                />
                <StatusRow
                  label="Gemini"
                  value={geminiLabel(profile.gemini)}
                  tone={geminiTone(profile.gemini.status)}
                />
                {/* Bundle D4: cumulative call counters. Only show once we have any data. */}
                {typeof profile.gemini.total_count === "number" && profile.gemini.total_count > 0 && (
                  <StatusRow
                    label="Gemini activity"
                    value={`${profile.gemini.ok_count ?? 0} live · ${profile.gemini.fallback_count ?? 0} fallback · ${profile.gemini.total_count} total`}
                    tone={
                      (profile.gemini.ok_count ?? 0) > 0
                        ? "status-dot status-dot--ok"
                        : "status-dot status-dot--warn"
                    }
                  />
                )}
              </div>
            )}
            <div className="settings-card__actions">
              <button
                className="pill-link pill-link--frosted"
                disabled={testing}
                onClick={runGeminiTest}
                type="button"
              >
                {testing ? "Testing…" : "Test Gemini"}
              </button>
              {testResult ? (
                <span className="settings-card__muted settings-card__result">
                  <b>{testResult.source}</b> · {testResult.latency_ms} ms — {testResult.reason_short}
                </span>
              ) : null}
              {testError ? (
                <span className="settings-card__muted settings-card__error">
                  {testError}
                </span>
              ) : null}
            </div>
          </article>

          <article className="glass-card settings-card">
            <header className="settings-card__header">
              <h3>Operator profile</h3>
              <span className="eyebrow eyebrow--muted">Signed in</span>
            </header>
            {user ? (
              <div className="status-list">
                <StatusRow label="Name" value={user.display_name || "—"} />
                <StatusRow label="Email" value={user.email || "—"} />
                <StatusRow label="Role" value={user.role || "operator"} />
                <StatusRow label="Org" value={user.organization_id || "—"} />
                <StatusRow label="User ID" value={user.user_id || "—"} />
              </div>
            ) : (
              <p className="settings-card__muted">No session detected.</p>
            )}
            <div className="settings-card__actions">
              <button
                className="pill-link pill-link--ghost"
                onClick={handleSignOut}
                type="button"
              >
                Sign out
              </button>
            </div>
          </article>

          <DemoControlPanel />
        </div>
      </motion.section>
    </div>
  );
}
