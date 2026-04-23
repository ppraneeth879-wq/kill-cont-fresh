import { Outlet } from "react-router-dom";
import { TopNav } from "../components/layout/TopNav";

type AppShellProps = {
  mode: "marketing" | "product";
};

export function AppShell({ mode }: AppShellProps) {
  return (
    <div className={`shell shell--${mode}`}>
      <TopNav mode={mode} />
      <main className="shell__content">
        <Outlet />
      </main>
    </div>
  );
}
