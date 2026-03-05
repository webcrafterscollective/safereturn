/** Accessible login form route with API error handling. */
import { useState } from "preact/hooks";
import { useLocation } from "wouter-preact";

import { ApiError, login, register } from "../lib/api/client";

export function LoginRoute() {
  const [, setLocation] = useLocation();
  const [email, setEmail] = useState("test.user@example.com");
  const [password, setPassword] = useState("password123");
  const [error, setError] = useState<string>("");
  const [notice, setNotice] = useState<string>("");
  const [isSubmitting, setIsSubmitting] = useState(false);

  async function handleSubmit(event: Event) {
    event.preventDefault();
    setError("");
    setNotice("");
    setIsSubmitting(true);

    try {
      const tokens = await login({ email, password });
      localStorage.setItem("access_token", tokens.access_token);
      localStorage.setItem("refresh_token", tokens.refresh_token);
      setLocation("/");
    } catch (err: unknown) {
      if (err instanceof ApiError && err.status === 401) {
        setError("Invalid credentials. Please try again.");
      } else {
        setError("Login failed due to an unexpected error.");
      }
    } finally {
      setIsSubmitting(false);
    }
  }

  async function handleRegister(event: Event) {
    event.preventDefault();
    setError("");
    setNotice("");
    setIsSubmitting(true);
    try {
      await register({ email, password });
      setNotice("Account created. You can now sign in with the same credentials.");
    } catch (err: unknown) {
      if (err instanceof ApiError && err.status === 409) {
        setError("Account already exists for this email.");
      } else {
        setError("Registration failed due to an unexpected error.");
      }
    } finally {
      setIsSubmitting(false);
    }
  }

  return (
    <section className="mx-auto max-w-md rounded-xl border border-slate-200 bg-white p-6 shadow-sm dark:border-slate-700 dark:bg-slate-900">
      <h1 className="text-xl font-semibold">Sign in</h1>
      <p className="mt-2 text-sm text-slate-600 dark:text-slate-300">Use your account credentials to receive JWT tokens.</p>

      <form className="mt-6 space-y-4" onSubmit={handleSubmit} aria-label="Login form">
        <div>
          <label className="mb-1 block text-sm font-medium" for="email">Email</label>
          <input
            id="email"
            type="email"
            required
            value={email}
            onInput={(event) => setEmail((event.target as HTMLInputElement).value)}
            className="w-full rounded border border-slate-300 px-3 py-2 dark:border-slate-700 dark:bg-slate-950"
          />
        </div>

        <div>
          <label className="mb-1 block text-sm font-medium" for="password">Password</label>
          <input
            id="password"
            type="password"
            required
            minLength={8}
            value={password}
            onInput={(event) => setPassword((event.target as HTMLInputElement).value)}
            className="w-full rounded border border-slate-300 px-3 py-2 dark:border-slate-700 dark:bg-slate-950"
          />
        </div>

        {error && (
          <p className="rounded border border-red-300 bg-red-50 p-2 text-sm text-red-700 dark:border-red-700 dark:bg-red-950/40 dark:text-red-300" role="alert">
            {error}
          </p>
        )}
        {notice && (
          <p className="rounded border border-emerald-300 bg-emerald-50 p-2 text-sm text-emerald-700 dark:border-emerald-700 dark:bg-emerald-950/30 dark:text-emerald-300">
            {notice}
          </p>
        )}

        <div className="grid gap-2 sm:grid-cols-2">
          <button
            type="submit"
            disabled={isSubmitting}
            className="w-full rounded bg-brand-500 px-4 py-2 font-medium text-white hover:bg-brand-700 disabled:cursor-not-allowed disabled:opacity-70"
          >
            {isSubmitting ? "Working..." : "Sign in"}
          </button>
          <button
            type="button"
            onClick={handleRegister}
            disabled={isSubmitting}
            className="w-full rounded border border-brand-500 px-4 py-2 font-medium text-brand-700 hover:bg-brand-50 disabled:cursor-not-allowed disabled:opacity-70 dark:text-brand-400 dark:hover:bg-slate-800"
          >
            {isSubmitting ? "Working..." : "Create account"}
          </button>
        </div>
      </form>
    </section>
  );
}


