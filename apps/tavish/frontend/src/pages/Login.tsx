import { FormEvent, useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { api, setToken } from "../api/client";

export function Login({ mode }: { mode: "login" | "signup" }) {
  const navigate = useNavigate();
  const [error, setError] = useState("");
  async function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const form = new FormData(event.currentTarget);
    try {
      const data = await api(`/auth/${mode}`, { method: "POST", body: JSON.stringify({ email: form.get("email"), password: form.get("password") }) });
      setToken(data.access_token);
      navigate(mode === "signup" ? "/onboarding" : "/dashboard");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Unable to continue");
    }
  }
  return (
    <main className="auth-page">
      <form className="panel narrow" onSubmit={submit}>
        <h1>{mode === "signup" ? "Create your account" : "Welcome back"}</h1>
        <label>Email<input name="email" type="email" required /></label>
        <label>Password<input name="password" type="password" minLength={8} required /></label>
        {error && <p className="error">{error}</p>}
        <button className="button primary">{mode === "signup" ? "Sign up" : "Sign in"}</button>
        <p>{mode === "signup" ? "Already have an account?" : "New here?"} <Link to={mode === "signup" ? "/login" : "/signup"}>{mode === "signup" ? "Sign in" : "Create account"}</Link></p>
      </form>
    </main>
  );
}
