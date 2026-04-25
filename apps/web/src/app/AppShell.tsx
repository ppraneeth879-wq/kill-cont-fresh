import { Outlet } from "react-router-dom";
import { TopNav } from "../components/layout/TopNav";
import { Sidebar } from "../components/layout/Sidebar";

type AppShellProps = {
  mode: "marketing" | "product";
};

export function AppShell({ mode }: AppShellProps) {
  if (mode === "product") {
    return (
      <div className="product-shell">
        <Sidebar />
        <div className="product-shell__body">
          <main className="product-shell__content">
            <Outlet />
          </main>
        </div>
      </div>
    );
  }

  return (
    <div className="shell shell--marketing">
      <TopNav mode={mode} />
      <main className="shell__content">
        <Outlet />
      </main>
    </div>
  );
}
