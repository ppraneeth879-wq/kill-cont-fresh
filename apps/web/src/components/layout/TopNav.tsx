import { NavLink } from "react-router-dom";

type TopNavProps = {
  mode: "marketing" | "product";
};

const productLinks = [
  { to: "/app/overview", label: "Overview" },
  { to: "/app/assets", label: "Assets" },
  { to: "/app/monitor", label: "Monitor" },
  { to: "/app/incidents", label: "Incidents" },
  { to: "/app/live-watch", label: "Live Watch" },
  { to: "/app/evidence", label: "Evidence" }
];

export function TopNav({ mode }: TopNavProps) {
  return (
    <header className="top-nav">
      <div className="top-nav__inner page-frame">
        <NavLink className="brand-mark" to="/">
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
              <NavLink className="pill-link pill-link--ghost" to="/sign-in">
                Sign In
              </NavLink>
              <NavLink className="pill-link pill-link--solid" to="/app/overview">
                Open Demo
              </NavLink>
            </>
          ) : (
            <>
              <button className="pill-link pill-link--frosted" type="button">
                Live Sync
              </button>
              <button className="pill-link pill-link--solid" type="button">
                Google Login
              </button>
            </>
          )}
        </div>
      </div>
    </header>
  );
}
