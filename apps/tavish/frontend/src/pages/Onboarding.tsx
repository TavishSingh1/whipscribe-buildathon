import { useNavigate } from "react-router-dom";
import { ProfileForm } from "../components/ProfileForm";

export function Onboarding() {
  const navigate = useNavigate();
  return (
    <main className="auth-page">
      <section className="panel wide">
        <p className="eyebrow">Creator profile</p>
        <h1>Teach the factory who you are creating for</h1>
        <ProfileForm onSaved={() => navigate("/dashboard")} />
      </section>
    </main>
  );
}
