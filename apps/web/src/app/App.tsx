import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { BrowserRouter } from "react-router-dom";
import { AppRouter } from "./router";
import { AppBackground } from "../components/layout/AppBackground";

const queryClient = new QueryClient();

export function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <BrowserRouter>
        <div className="app-root">
          <AppBackground />
          <AppRouter />
        </div>
      </BrowserRouter>
    </QueryClientProvider>
  );
}
