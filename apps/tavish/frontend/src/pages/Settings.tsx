import { FormEvent, useEffect, useState } from "react";
import { useParams } from "react-router-dom";
import { api } from "../api/client";
import { ProfileForm } from "../components/ProfileForm";

export function Settings() {
  const { section } = useParams();
  const [connections, setConnections] = useState<any[]>([]);
  const [examples, setExamples] = useState<any[]>([]);
  const reload = () => { api("/connections").then(setConnections).catch(() => {}); api("/content-examples").then(setExamples).catch(() => {}); };
  useEffect(reload, []);
  async function addExample(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const form = new FormData(event.currentTarget);
    await api("/content-examples", { method: "POST", body: JSON.stringify({ platform: form.get("platform"), title: form.get("title"), content: form.get("content") }) });
    event.currentTarget.reset();
    reload();
  }
  async function addConnection(provider: string) {
    await api("/connections", { method: "POST", body: JSON.stringify({ provider, account_name: `${provider} preview connection`, scopes: ["read", "publish"] }) });
    reload();
  }
  return (
    <div className="page">
      <header className="page-header"><div><p className="eyebrow">Settings</p><h1>{section}</h1></div></header>
      {section === "profile" && <section className="panel"><ProfileForm /></section>}
      {section === "connections" && <section className="panel"><h2>Connections</h2>{["whipscribe", "notion", "slack"].map((p) => <div className="row" key={p}><span>{p}</span><small>{connections.find((c) => c.provider === p)?.status ?? "Not connected"}</small><button className="button" onClick={() => addConnection(p)}>Connect</button></div>)}</section>}
      {section === "content" && <section className="panel"><h2>Learn my writing style</h2><form className="grid-form" onSubmit={addExample}><label>Platform<input name="platform" /></label><label>Title<input name="title" /></label><label>Example<textarea name="content" required /></label><button className="button primary">Add example</button></form><div className="list">{examples.map((e) => <div className="row" key={e.id}><span>{e.title}</span><small>{e.platform}</small></div>)}</div></section>}
      {section === "publishing" && <section className="panel"><h2>Publishing</h2><p className="muted">External publishing always requires preview and confirmation. Automatic posting is disabled by default.</p></section>}
    </div>
  );
}
