import { Navigate, Route, Routes } from "react-router-dom";
import { AppShell } from "./AppShell";
import { LandingPage } from "../features/marketing/LandingPage";
import { SignInPage } from "../features/auth/SignInPage";
import { ProtectedRoute } from "../features/auth/ProtectedRoute";
import { OverviewPage } from "../features/overview/OverviewPage";
import { AssetsPage } from "../features/assets/AssetsPage";
import { MonitorPage } from "../features/monitor/MonitorPage";
import { IncidentsPage } from "../features/incidents/IncidentsPage";
import { IncidentDetailPage } from "../features/incidents/IncidentDetailPage";
import { LiveWatchPage } from "../features/live-watch/LiveWatchPage";
import { EvidencePage } from "../features/evidence/EvidencePage";
import { SettingsPage } from "../features/settings/SettingsPage";

export function AppRouter() {
  return (
    <Routes>
      <Route element={<AppShell mode="marketing" />}>
        <Route index element={<LandingPage />} />
        <Route path="/sign-in" element={<SignInPage />} />
      </Route>

      <Route element={<ProtectedRoute />}>
        <Route path="/app" element={<AppShell mode="product" />}>
          <Route index element={<Navigate replace to="/app/overview" />} />
          <Route path="overview" element={<OverviewPage />} />
          <Route path="assets" element={<AssetsPage />} />
          <Route path="monitor" element={<MonitorPage />} />
          <Route path="incidents" element={<IncidentsPage />} />
          <Route path="incidents/:incidentId" element={<IncidentDetailPage />} />
          <Route path="live-watch" element={<LiveWatchPage />} />
          <Route path="evidence" element={<EvidencePage />} />
          <Route path="settings" element={<SettingsPage />} />
        </Route>
      </Route>
    </Routes>
  );
}
