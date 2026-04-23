import { useState } from "react";
import { useQueryClient } from "@tanstack/react-query";
import { api } from "../../lib/api";

type BusyAction = "seed" | "simulate" | "live" | "reset" | null;

export function DemoControlPanel() {
  const queryClient = useQueryClient();
  const [busy, setBusy] = useState<BusyAction>(null);
  const [notice, setNotice] = useState<string>("");

  async function run(action: Exclude<BusyAction, null>) {
    setBusy(action);
    setNotice("");
    try {
      if (action === "seed") {
        await api("/demo/seed", {
          method: "POST",
          body: { scenario: "championship-final" },
        });
        setNotice("Scenario seeded.");
      }
      if (action === "simulate") {
        await api("/demo/simulate-incident", {
          method: "POST",
          body: {},
        });
        setNotice("Simulated incident created.");
      }
      if (action === "live") {
        await api("/demo/live/start", {
          method: "POST",
          body: { segments: 5, interval_seconds: 2 },
        });
        setNotice("Live segment emitter started.");
      }
      if (action === "reset") {
        await api("/demo/reset", {
          method: "POST",
          body: {},
        });
        setNotice("Demo state reset.");
      }

      await Promise.all([
        queryClient.invalidateQueries({ queryKey: ["dashboard", "overview"] }),
        queryClient.invalidateQueries({ queryKey: ["incidents"] }),
        queryClient.invalidateQueries({ queryKey: ["feeds"] }),
        queryClient.invalidateQueries({ queryKey: ["assets"] }),
      ]);
    } catch (error) {
      const message = error instanceof Error ? error.message : "Action failed";
      setNotice(message);
    } finally {
      setBusy(null);
    }
  }

  return (
    <article className="glass-card">
      <h3>Demo control panel</h3>
      <p>Seed, simulate, and reset flows for repeatable live demos without restarting the server.</p>
      <div className="auth-panel__actions">
        <button
          className="pill-link pill-link--solid"
          disabled={busy !== null}
          onClick={() => run("seed")}
          type="button"
        >
          {busy === "seed" ? "Seeding..." : "Seed scenario"}
        </button>
        <button
          className="pill-link pill-link--frosted"
          disabled={busy !== null}
          onClick={() => run("simulate")}
          type="button"
        >
          {busy === "simulate" ? "Simulating..." : "Simulate incident"}
        </button>
        <button
          className="pill-link pill-link--frosted"
          disabled={busy !== null}
          onClick={() => run("live")}
          type="button"
        >
          {busy === "live" ? "Starting..." : "Start live"}
        </button>
        <button
          className="pill-link pill-link--ghost"
          disabled={busy !== null}
          onClick={() => run("reset")}
          type="button"
        >
          {busy === "reset" ? "Resetting..." : "Reset"}
        </button>
      </div>
      {notice && <p className="body-copy">{notice}</p>}
    </article>
  );
}