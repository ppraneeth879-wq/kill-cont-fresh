import { FormEvent, useState } from "react";
import { motion } from "framer-motion";
import { useNavigate } from "react-router-dom";
import { authMode } from "../../lib/api";
import { useAuth } from "./useAuth";

export function SignInPage() {
  const navigate = useNavigate();
  const { signIn, loading } = useAuth();
  const mode = authMode();
  const [email, setEmail] = useState("ops@killcont.demo");
  const [displayName, setDisplayName] = useState("KillCont Demo Operator");
  const [error, setError] = useState<string | null>(null);

  async function onSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setError(null);
    try {
      await signIn(email, displayName);
      navigate("/app/overview");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Sign-in failed");
    }
  }

  return (
    <div className="page-frame page-frame--narrow">
      <motion.section
        animate={{ opacity: 1, y: 0 }}
        className="auth-panel"
        initial={{ opacity: 0, y: 16 }}
        transition={{ duration: 0.45, ease: "easeOut" }}
      >
        <span className="eyebrow">Simple Google sign-in</span>
        <h1 className="section-title">Step into the KillCont command center.</h1>
        <p className="body-copy">
          {mode === "firebase"
            ? "Firebase-backed authentication mode is active for this environment."
            : "This demo short-circuits Google OAuth with a local bearer token. The production flow will use Firebase Authentication — the route and treatment stay identical."}
        </p>

        <form className="auth-panel__form" onSubmit={onSubmit}>
          <label className="auth-panel__field">
            <span>Work email</span>
            <input
              autoComplete="email"
              onChange={(event) => setEmail(event.target.value)}
              placeholder="ops@killcont.demo"
              type="email"
              value={email}
            />
          </label>
          <label className="auth-panel__field">
            <span>Display name</span>
            <input
              autoComplete="name"
              onChange={(event) => setDisplayName(event.target.value)}
              placeholder="KillCont Demo Operator"
              type="text"
              value={displayName}
            />
          </label>

          <div className="auth-panel__actions">
            <button className="pill-link pill-link--solid" disabled={loading} type="submit">
              {loading ? "Signing in..." : "Continue with Google"}
            </button>
          </div>
          {error && (
            <p className="auth-panel__error" role="alert">
              {error}
            </p>
          )}
        </form>
      </motion.section>
    </div>
  );
}
