import { FormEvent, useState } from "react";
import { motion } from "framer-motion";
import { useNavigate } from "react-router-dom";
import { authMode } from "../../lib/api";
import { isFirebaseConfigured, signInWithGoogle } from "../../lib/firebase";
import { useAuth } from "./useAuth";

export function SignInPage() {
  const navigate = useNavigate();
  const { signIn, loading } = useAuth();
  const mode = authMode();
  const firebaseReady = isFirebaseConfigured();
  const [email, setEmail] = useState("ops@killcont.demo");
  const [displayName, setDisplayName] = useState("KillCont Demo Operator");
  const [error, setError] = useState<string | null>(null);
  const [popupBusy, setPopupBusy] = useState(false);

  async function onDemoSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setError(null);
    try {
      await signIn(email, displayName);
      navigate("/app/overview");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Sign-in failed");
    }
  }

  async function onGoogleClick() {
    setError(null);
    setPopupBusy(true);
    try {
      const cred = await signInWithGoogle();
      // ID token is in localStorage; signIn() picks it up and forwards
      // it to /session/login. Backend reads name/email from verified token.
      await signIn(cred.email, cred.displayName);
      navigate("/app/overview");
    } catch (err) {
      // Bundle F: surface a clean, recoverable message for the common
      // popup-cancel paths instead of dumping a Firebase exception trace.
      const code = (err as { code?: string })?.code ?? "";
      if (code === "auth/popup-closed-by-user" || code === "auth/cancelled-popup-request") {
        setError("Sign-in cancelled. Try again, or pick a different account.");
      } else if (code === "auth/popup-blocked") {
        setError("Browser blocked the popup. Please allow popups for this site and retry.");
      } else if (code === "auth/unauthorized-domain") {
        setError("This domain isn't on the Firebase Authorized Domains list. Add it in Firebase Console -> Authentication -> Settings.");
      } else {
        setError(err instanceof Error ? err.message : "Google sign-in failed");
      }
    } finally {
      setPopupBusy(false);
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
            ? "Authenticate with your Google account — Firebase issues a short-lived ID token that the API verifies on every request."
            : "This demo short-circuits Google OAuth with a local bearer token. The production flow uses Firebase Authentication — the route and treatment stay identical."}
        </p>

        {mode === "firebase" ? (
          <div className="auth-panel__form">
            <button
              className="pill-link pill-link--solid"
              disabled={popupBusy || loading || !firebaseReady}
              onClick={onGoogleClick}
              type="button"
            >
              {popupBusy ? "Opening Google..." : "Continue with Google"}
            </button>
            {!firebaseReady && (
              <p className="auth-panel__error" role="alert">
                Firebase web config is missing. Set VITE_FIREBASE_API_KEY, VITE_FIREBASE_PROJECT_ID,
                and VITE_FIREBASE_APP_ID in the build environment.
              </p>
            )}
            {error && (
              <p className="auth-panel__error" role="alert">
                {error}
              </p>
            )}
          </div>
        ) : (
          <form className="auth-panel__form" onSubmit={onDemoSubmit}>
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
        )}
      </motion.section>
    </div>
  );
}
