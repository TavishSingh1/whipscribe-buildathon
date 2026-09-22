import { NavLink, Outlet } from "react-router-dom";
import { LayoutDashboard, Mic2, PlusCircle, Settings } from "lucide-react";

export function AppShell() {
  return (
    <div className="app-shell">
      <aside className="sidebar">
        <div className="brand"><Mic2 size={22} /> Podcast Clip Factory</div>
        <nav>
          <NavLink to="/dashboard"><LayoutDashboard size={18} /> Dashboard</NavLink>
          <NavLink to="/episodes/new"><PlusCircle size={18} /> Create</NavLink>
          <NavLink to="/settings/profile"><Settings size={18} /> Settings</NavLink>
        </nav>
      </aside>
      <main className="main"><Outlet /></main>
    </div>
  );
}
