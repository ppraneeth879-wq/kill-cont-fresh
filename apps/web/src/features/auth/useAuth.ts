import { useCallback, useEffect, useState } from "react";
import { api, authMode, FIREBASE_ID_TOKEN_KEY, TOKEN_KEY, USER_KEY } from "../../lib/api";
import type { LoginResponse, SessionUser } from "../../lib/types";

export function useAuth() {
  const [user, setUser] = useState<SessionUser | null>(() => {
    try {
      const raw = localStorage.getItem(USER_KEY);
      return raw ? (JSON.parse(raw) as SessionUser) : null;
    } catch {
      return null;
    }
  });

  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (user) return;
    if (!localStorage.getItem(TOKEN_KEY)) return;
    (async () => {
      try {
        const me = await api<SessionUser>("/session/me");
        localStorage.setItem(USER_KEY, JSON.stringify(me));
        setUser(me);
      } catch {
        /* ignore — stay signed out */
      }
    })();
  }, [user]);

  const signIn = useCallback(
    async (email: string, displayName: string) => {
      setLoading(true);
      try {
        const mode = authMode();
        const firebaseIdToken =
          mode === "firebase" ? localStorage.getItem(FIREBASE_ID_TOKEN_KEY) ?? "" : "";
        if (mode === "firebase" && !firebaseIdToken) {
          throw new Error("Firebase auth mode is enabled, but no Firebase ID token is available.");
        }

        const res = await api<LoginResponse>("/session/login", {
          method: "POST",
          body: {
            email,
            display_name: displayName,
            ...(mode === "firebase" ? { id_token: firebaseIdToken } : {}),
          },
        });
        localStorage.setItem(TOKEN_KEY, res.token);
        localStorage.setItem(USER_KEY, JSON.stringify(res.user));
        setUser(res.user);
        return res;
      } finally {
        setLoading(false);
      }
    },
    [],
  );

  const signOut = useCallback(() => {
    localStorage.removeItem(TOKEN_KEY);
    localStorage.removeItem(USER_KEY);
    setUser(null);
  }, []);

  return { user, loading, signIn, signOut, isAuthenticated: !!user };
}
