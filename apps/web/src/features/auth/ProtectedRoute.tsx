import { Navigate, Outlet } from "react-router-dom";
import { TOKEN_KEY } from "../../lib/api";

/**
 * Redirects to /sign-in if no bearer token is present. Intentionally
 * synchronous — /session/me is revalidated by the hooks that actually need
 * the user object.
 */
export function ProtectedRoute() {
  const hasToken = (() => {
    try {
      return Boolean(localStorage.getItem(TOKEN_KEY));
    } catch {
      return false;
    }
  })();

  if (!hasToken) {
    return <Navigate replace to="/sign-in" />;
  }
  return <Outlet />;
}
