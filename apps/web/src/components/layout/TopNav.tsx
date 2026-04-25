import { useEffect, useRef, useState } from "react";
import { NavLink, useNavigate } from "react-router-dom";
import { useAuth } from "../../features/auth/useAuth";

type TopNavProps = {
  mode: "marketing" | "product";
};

const productLinks = [
  { to: "/app/overview", label: "Overview" },
  { to: "/app/assets", label: "Assets" },
  { to: "/app/monitor", label: "Monitor" },
  { to: "/app/incidents", label: "Incidents" },
  { to: "/app/live-watch", label: "Live Watch" },
  { to: "/app/evidence", label: "Evidence" },
  { to: "/app/settings", label: "Settings" },
];

function initialsFrom(name: string | undefined, email: string | undefined): string {
  const source = (name ?? email ?? "").trim();
  if (!source) return "KC";
  const parts = source.split(/\s+/).filter(Boolean);
  if (parts.length === 0) return source.slice(0, 2).toUpperCase();
  if (parts.length === 1) return parts[0].slice(0, 2).toUpperCase();
  return (parts[0][0] + parts[parts.length - 1][0]).toUpperCase();
}

export function TopNav({ mode }: TopNavProps) {
  const navigate = useNavigate();
  const { user, signOut, isAuthenticated } = useAuth();
  const [menuOpen, setMenuOpen] = useState(false);
  const menuRef = useRef<HTMLDivElement | null>(null);

  useEffect(() => {
    if (!menuOpen) return;
    function onDocClick(event: MouseEvent) {
      if (menuRef.current && !menuRef.current.contains(event.target as Node)) {
        setMenuOpen(false);
      }
    }
    document.addEventListener("mousedown", onDocClick);
    return () => document.removeEventListener("mousedown", onDocClick);
  }, [menuOpen]);

  function handleSignOut() {
    signOut();
    setMenuOpen(false);
    navigate("/sign-in", { replace: true });
  }

  return (
    <header className="top-nav">
      <div className="top-nav__inner page-frame">
        <NavLink className="brand-mark" to={isAuthenticated ? "/app/overview" : "/"}>
          <span className="brand-mark__glow" />
          <span className="brand-mark__word">KillCont</span>
        </NavLink>

        {mode === "marketing" ? (
          <nav className="nav-links">
            <a className="nav-links__item" href="#workflow">
              Workflow
            </a>
            <a className="nav-links__item" href="#command-center">
              Command Center
            </a>
            <a className="nav-links__item" href="#standout">
              Why It Wins
            </a>
          </nav>
        ) : (
          <nav className="nav-links nav-links--product">
            {productLinks.map((link) => (
              <NavLink
                key={link.to}
                className={({ isActive }) =>
                  isActive ? "nav-links__item nav-links__item--active" : "nav-links__item"
                }
                to={link.to}
              >
                {link.label}
              </NavLink>
            ))}
          </nav>
        )}

        <div className="top-nav__actions">
          {mode === "marketing" ? (
            <>
              {isAuthenticated ? (
                <NavLink className="pill-link pill-link--solid" to="/app/overview">
                  Open Console
                </NavLink>
              ) : (
                <>
                  <NavLink className="pill-link pill-link--ghost" to="/sign-in">
                    Sign In
                  </NavLink>
                  <NavLink className="pill-link pill-link--solid" to="/sign-in">
                    Open Demo
                  </NavLink>
                </>
              )}
            </>
          ) : (
            <div
              ref={menuRef}
              style={{ position: "relative", display: "flex", alignItems: "center", gap: 8 }}
            >
              <button
                className="pill-link pill-link--frosted"
                onClick={() => setMenuOpen((value) => !value)}
                type="button"
                aria-haspopup="menu"
                aria-expanded={menuOpen}
                style={{ display: "flex", alignItems: "center", gap: 8 }}
              >
                <span
                  aria-hidden
                  style={{
                    display: "inline-flex",
                    alignItems: "center",
                    justifyContent: "center",
                    width: 26,
                    height: 26,
                    borderRadius: "50%",
                    background: "linear-gradient(135deg,#4c8bf5,#8b5cf6)",
                    color: "#fff",
                    fontSize: 11,
                    fontWeight: 600,
                    letterSpacing: 0.2,
                  }}
                >
                  {initialsFrom(user?.display_name, user?.email)}
                </span>
                <span style={{ maxWidth: 160, overflow: "hidden", textOverflow: "ellipsis", whiteSpace: "nowrap" }}>
                  {user?.display_name ?? user?.email ?? "Operator"}
                </span>
                <span aria-hidden style={{ opacity: 0.6 }}>▾</span>
              </button>

              {menuOpen && (
                <div
                  role="menu"
                  style={{
                    position: "absolute",
                    top: "calc(100% + 8px)",
                    right: 0,
                    minWidth: 240,
                    padding: 12,
                    background: "rgba(16,18,28,0.96)",
                    border: "1px solid rgba(255,255,255,0.08)",
                    borderRadius: 12,
                    boxShadow: "0 18px 48px rgba(0,0,0,0.45)",
                    backdropFilter: "blur(12px)",
                    zIndex: 1000,
                  }}
                >
                  <div style={{ padding: "4px 8px 10px", borderBottom: "1px solid rgba(255,255,255,0.06)" }}>
                    <div style={{ fontSize: 13, fontWeight: 600, color: "rgba(255,255,255,0.92)" }}>
                      {user?.display_name ?? "Signed in"}
                    </div>
                    <div style={{ fontSize: 12, color: "rgba(255,255,255,0.6)", marginTop: 2 }}>
                      {user?.email ?? "—"}
                    </div>
                    <div style={{ fontSize: 11, color: "rgba(255,255,255,0.45)", marginTop: 4 }}>
                      Org: {user?.organization_id ?? "demo"} · {user?.role ?? "operator"}
                    </div>
                  </div>
                  <button
                    type="button"
                    onClick={handleSignOut}
                    style={{
                      marginTop: 8,
                      width: "100%",
                      textAlign: "left",
                      padding: "8px 10px",
                      background: "transparent",
                      color: "rgba(255,255,255,0.92)",
                      border: "1px solid rgba(255,255,255,0.1)",
                      borderRadius: 8,
                      cursor: "pointer",
                      fontSize: 13,
                    }}
                  >
                    Sign out
                  </button>
                </div>
              )}
            </div>
          )}
        </div>
      </div>
    </header>
  );
}
