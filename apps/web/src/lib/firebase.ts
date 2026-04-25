/**
 * Firebase web SDK init — only when ``VITE_AUTH_MODE === "firebase"``.
 *
 * Demo profile leaves these helpers unused (and never instantiates the
 * SDK), so the local dev experience does not require Firebase env vars.
 *
 * The web Firebase config keys (``apiKey``, ``authDomain``, etc.) are
 * designed to be public — committing them to a private repo or exposing
 * them in a JS bundle is safe per Firebase's documentation.
 */
import {
  type Auth,
  GoogleAuthProvider,
  getAuth,
  onIdTokenChanged,
  signInWithPopup,
  signOut as fbSignOut,
} from "firebase/auth";
import { type FirebaseApp, getApps, initializeApp } from "firebase/app";

import { FIREBASE_ID_TOKEN_KEY, authMode } from "./api";

let _app: FirebaseApp | null = null;
let _auth: Auth | null = null;

function _config() {
  return {
    apiKey: import.meta.env.VITE_FIREBASE_API_KEY as string | undefined,
    authDomain: import.meta.env.VITE_FIREBASE_AUTH_DOMAIN as string | undefined,
    projectId: import.meta.env.VITE_FIREBASE_PROJECT_ID as string | undefined,
    storageBucket: import.meta.env.VITE_FIREBASE_STORAGE_BUCKET as string | undefined,
    messagingSenderId: import.meta.env.VITE_FIREBASE_MESSAGING_SENDER_ID as string | undefined,
    appId: import.meta.env.VITE_FIREBASE_APP_ID as string | undefined,
  };
}

export function isFirebaseConfigured(): boolean {
  if (authMode() !== "firebase") return false;
  const cfg = _config();
  return Boolean(cfg.apiKey && cfg.projectId && cfg.appId);
}

function _ensureApp(): FirebaseApp {
  if (_app) return _app;
  const cfg = _config();
  if (!cfg.apiKey || !cfg.projectId || !cfg.appId) {
    throw new Error(
      "Firebase auth mode requires VITE_FIREBASE_API_KEY, VITE_FIREBASE_PROJECT_ID, and VITE_FIREBASE_APP_ID.",
    );
  }
  _app = getApps()[0] ?? initializeApp(cfg as Parameters<typeof initializeApp>[0]);
  return _app;
}

function _ensureAuth(): Auth {
  if (_auth) return _auth;
  _auth = getAuth(_ensureApp());
  // Re-stash the ID token whenever Firebase rotates it (default ~1 h).
  onIdTokenChanged(_auth, async (user) => {
    if (!user) {
      try {
        localStorage.removeItem(FIREBASE_ID_TOKEN_KEY);
      } catch {
        /* ignore */
      }
      return;
    }
    try {
      const token = await user.getIdToken();
      localStorage.setItem(FIREBASE_ID_TOKEN_KEY, token);
    } catch {
      /* ignore — next request will re-prompt */
    }
  });
  return _auth;
}

export interface FirebaseSignInResult {
  idToken: string;
  email: string;
  displayName: string;
}

export async function signInWithGoogle(): Promise<FirebaseSignInResult> {
  const auth = _ensureAuth();
  const provider = new GoogleAuthProvider();
  provider.setCustomParameters({ prompt: "select_account" });
  const cred = await signInWithPopup(auth, provider);
  const idToken = await cred.user.getIdToken();
  try {
    localStorage.setItem(FIREBASE_ID_TOKEN_KEY, idToken);
  } catch {
    /* ignore */
  }
  return {
    idToken,
    email: cred.user.email ?? "",
    displayName: cred.user.displayName ?? cred.user.email ?? "Operator",
  };
}

export async function signOutGoogle(): Promise<void> {
  if (authMode() !== "firebase") return;
  if (!_auth) return;
  try {
    await fbSignOut(_auth);
  } catch {
    /* ignore */
  } finally {
    try {
      localStorage.removeItem(FIREBASE_ID_TOKEN_KEY);
    } catch {
      /* ignore */
    }
  }
}
