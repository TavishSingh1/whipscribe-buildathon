import { FormEvent, useState } from "react";
import { useNavigate } from "react-router-dom";
import { api } from "../api/client";

export function EpisodeNew() {
  const navigate = useNavigate();
  const [error, setError] = useState("");
  async function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const form = new FormData(event.currentTarget);
    try {
      const job = await api("/episodes", { method: "POST", body: form });
      navigate(`/episodes/${job.episode_id}`);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Upload failed");
    }
  }
  return (
    <div className="page">
      <header className="page-header"><div><p className="eyebrow">Create</p><h1>Upload your episode</h1></div></header>
      <form className="panel upload-form" onSubmit={submit}>
        <label>Podcast file<input name="file" type="file" accept="audio/*,video/mp4" required /></label>
        <label>Episode title<input name="title" /></label>
        <label>Guest<input name="guest" /></label>
        <label>Topic<input name="topic" /></label>
        <label>Description<textarea name="description" /></label>
        <label>Episode instructions<textarea name="additional_instructions" placeholder="Prioritize clips about AI agents, aim LinkedIn at CTOs..." /></label>
        <div className="two">
          <label>Clip goal<select name="clip_goal"><option>Balanced</option><option>Educational</option><option>Entertainment</option><option>Thought leadership</option><option>Promotional</option></select></label>
          <label>Social goal<select name="social_goal"><option>Engagement</option><option>Followers</option><option>Website traffic</option><option>Newsletter</option></select></label>
        </div>
        {error && <p className="error">{error}</p>}
        <button className="button primary">Generate content package</button>
      </form>
    </div>
  );
}
