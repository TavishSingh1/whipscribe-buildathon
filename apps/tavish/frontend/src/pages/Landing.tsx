import { Link } from "react-router-dom";

export function Landing() {
  return (
    <main className="landing">
      <section className="hero">
        <div>
          <p className="eyebrow">Personalized podcast repurposing</p>
          <h1>Podcast Clip Factory</h1>
          <p>Upload one episode and turn it into creator-specific clips, show notes, and social posts for X, LinkedIn, and Instagram.</p>
          <div className="actions">
            <Link className="button primary" to="/signup">Start free</Link>
            <Link className="button" to="/login">Sign in</Link>
          </div>
        </div>
      </section>
    </main>
  );
}
