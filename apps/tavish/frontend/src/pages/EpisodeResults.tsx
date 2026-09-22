import { Copy, Download } from "lucide-react";
import { useEffect, useState } from "react";
import { useParams } from "react-router-dom";
import { api } from "../api/client";

export function EpisodeResults() {
  const { id } = useParams();
  const [data, setData] = useState<any>(null);
  const [active, setActive] = useState("x");
  useEffect(() => {
    const load = () => api(`/episodes/${id}`).then(setData).catch(() => {});
    load();
    const timer = setInterval(load, 4000);
    return () => clearInterval(timer);
  }, [id]);
  if (!data) return <div className="page"><div className="skeleton">Loading episode...</div></div>;
  const posts = data.social_posts ?? [];
  const activePost = posts.find((p: any) => p.platform === active);
  return (
    <div className="page">
      <header className="page-header">
        <div><p className="eyebrow">{data.episode.status}</p><h1>{data.episode.title || data.episode.file_name}</h1></div>
      </header>
      <section className="personalized"><strong>Personalized using</strong>{data.personalized_using.map((x: string) => <span key={x}>✓ {x}</span>)}</section>
      <section><h2>Clips</h2><div className="cards">{(data.clips ?? []).map((clip: any) => <article className="card" key={clip.id}><h3>{clip.title}</h3><p>{clip.score_reason}</p><small>{clip.start_time}s - {clip.end_time}s</small>{clip.video_url && <a className="button" href={clip.video_url}><Download size={16} /> Download</a>}</article>)}</div></section>
      <section><h2>Show notes</h2><div className="panel"><p>{data.show_notes?.summary ?? "Show notes will appear when processing completes."}</p>{data.show_notes?.chapters?.map((c: any) => <div className="chapter" key={c.timestamp_s}><strong>{c.title}</strong><span>{c.summary}</span></div>)}</div></section>
      <section><h2>Social content</h2><div className="tabs">{["x", "linkedin", "instagram"].map((p) => <button className={active === p ? "active" : ""} onClick={() => setActive(p)} key={p}>{p}</button>)}</div><textarea className="post-editor" value={activePost?.content ?? ""} onChange={(e) => activePost && setData({ ...data, social_posts: posts.map((p: any) => p.id === activePost.id ? { ...p, content: e.target.value } : p) })} /><button className="button" onClick={() => navigator.clipboard.writeText(activePost?.content ?? "")}><Copy size={16} /> Copy</button></section>
    </div>
  );
}
