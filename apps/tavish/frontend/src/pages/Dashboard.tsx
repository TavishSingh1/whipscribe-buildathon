import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { api } from "../api/client";

export function Dashboard() {
  const [profile, setProfile] = useState<any>(null);
  const [episodes, setEpisodes] = useState<any[]>([]);
  const [connections, setConnections] = useState<any[]>([]);
  useEffect(() => {
    api("/profile").then(setProfile).catch(() => {});
    api("/episodes").then(setEpisodes).catch(() => {});
    api("/connections").then(setConnections).catch(() => {});
  }, []);
  return (
    <div className="page">
      <header className="page-header">
        <div>
          <p className="eyebrow">Dashboard</p>
          <h1>Welcome back{profile?.podcast_name ? `, ${profile.podcast_name}` : ""}</h1>
        </div>
        <Link className="button primary" to="/episodes/new">Create new episode</Link>
      </header>
      <section className="metrics">
        <div><strong>{episodes.length}</strong><span>Episodes</span></div>
        <div><strong>{connections.length}</strong><span>Connected tools</span></div>
        <div><strong>5</strong><span>Free episode quota</span></div>
      </section>
      <section>
        <h2>Recent episodes</h2>
        <div className="list">
          {episodes.length === 0 && <p className="muted">No episodes yet. Upload your first podcast to generate a content package.</p>}
          {episodes.map((episode) => (
            <Link className="row" to={`/episodes/${episode.id}`} key={episode.id}>
              <span>{episode.title || episode.file_name}</span><small>{episode.status}</small>
            </Link>
          ))}
        </div>
      </section>
    </div>
  );
}
