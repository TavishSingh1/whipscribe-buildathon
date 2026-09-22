import React from "react";
import { createRoot } from "react-dom/client";
import { BrowserRouter, Navigate, Route, Routes } from "react-router-dom";
import { AppShell } from "./components/AppShell";
import { token } from "./api/client";
import { Dashboard } from "./pages/Dashboard";
import { EpisodeNew } from "./pages/EpisodeNew";
import { EpisodeResults } from "./pages/EpisodeResults";
import { Landing } from "./pages/Landing";
import { Login } from "./pages/Login";
import { Onboarding } from "./pages/Onboarding";
import { Settings } from "./pages/Settings";
import "./styles/app.css";

function Protected({ children }: { children: React.ReactNode }) {
  return token() ? <>{children}</> : <Navigate to="/login" replace />;
}

createRoot(document.getElementById("root")!).render(
  <React.StrictMode>
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Landing />} />
        <Route path="/login" element={<Login mode="login" />} />
        <Route path="/signup" element={<Login mode="signup" />} />
        <Route path="/onboarding" element={<Protected><Onboarding /></Protected>} />
        <Route element={<Protected><AppShell /></Protected>}>
          <Route path="/dashboard" element={<Dashboard />} />
          <Route path="/episodes/new" element={<EpisodeNew />} />
          <Route path="/episodes/:id" element={<EpisodeResults />} />
          <Route path="/settings/:section" element={<Settings />} />
        </Route>
      </Routes>
    </BrowserRouter>
  </React.StrictMode>
);
