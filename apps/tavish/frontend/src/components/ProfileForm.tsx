import { FormEvent, useEffect, useState } from "react";
import { api, Profile } from "../api/client";

const empty: Profile = {
  podcast_name: "",
  description: "",
  niche: "",
  target_audience: "",
  audience_level: "",
  brand_voice: "",
  tone: "",
  communication_style: "",
  content_goals: "",
  preferred_platforms: ["x", "linkedin", "instagram"],
  clip_style: "Educational insights",
  preferred_topics: [],
  excluded_topics: [],
  cta_style: "",
  language: "English",
  social_handles: {},
  brand_guidelines: ""
};

export function ProfileForm({ onSaved }: { onSaved?: () => void }) {
  const [profile, setProfile] = useState(empty);
  const [status, setStatus] = useState("");
  useEffect(() => { api("/profile").then((p) => p && setProfile({ ...empty, ...p })).catch(() => {}); }, []);
  async function submit(event: FormEvent) {
    event.preventDefault();
    await api("/profile", { method: "PUT", body: JSON.stringify(profile) });
    setStatus("Saved");
    onSaved?.();
  }
  function field(key: keyof Profile, label: string, area = false) {
    return <label>{label}{area ? <textarea value={String(profile[key] ?? "")} onChange={(e) => setProfile({ ...profile, [key]: e.target.value })} /> : <input value={String(profile[key] ?? "")} onChange={(e) => setProfile({ ...profile, [key]: e.target.value })} />}</label>;
  }
  return (
    <form className="grid-form" onSubmit={submit}>
      {field("podcast_name", "Podcast name")}
      {field("niche", "Niche")}
      {field("target_audience", "Target audience", true)}
      {field("audience_level", "Audience level")}
      {field("brand_voice", "Brand voice", true)}
      {field("tone", "Preferred tone")}
      {field("content_goals", "Content goals", true)}
      {field("clip_style", "Preferred clip style")}
      {field("cta_style", "Call to action preference", true)}
      {field("brand_guidelines", "Brand guidelines", true)}
      {field("description", "Podcast description", true)}
      <button className="button primary">Save profile</button>
      {status && <span className="success">{status}</span>}
    </form>
  );
}
