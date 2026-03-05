/** Accessible login form route with API error handling. */
import { useState } from "preact/hooks";
import { useLocation } from "wouter-preact";

import { ApiError, login, register, storeSessionTokens } from "../lib/api/client";

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
      storeSessionTokens(tokens);
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
    <section className="mx-auto mt-8 max-w-md rounded-2xl border border-slate-200/80 bg-white p-8 shadow-soft dark:border-slate-800 dark:bg-slate-900">
      <div className="mb-8 text-center">
        <div className="mx-auto mb-4 flex h-12 w-12 items-center justify-center rounded-xl bg-brand-100 text-brand-600 dark:bg-brand-500/20 dark:text-brand-400">
          <svg className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z" />
          </svg>
        </div>
        <h1 className="text-2xl font-bold tracking-tight text-slate-900 dark:text-white">Welcome back</h1>
        <p className="mt-2 text-sm text-slate-600 dark:text-slate-400">Sign in to manage your recovered items.</p>
      </div>

      <form className="space-y-5" onSubmit={handleSubmit} aria-label="Login form">
        <div>
          <label className="mb-1.5 block text-sm font-medium text-slate-700 dark:text-slate-300" for="email">
            Email address
          </label>
          <input
            id="email"
            type="email"
            required
            value={email}
            onInput={(event) => setEmail((event.target as HTMLInputElement).value)}
            className="block w-full rounded-lg border border-slate-300 bg-white px-4 py-2.5 text-slate-900 outline-none transition-all placeholder:text-slate-400 focus:border-brand-500 focus:ring-4 focus:ring-brand-500/10 dark:border-slate-700 dark:bg-slate-950 dark:text-white dark:focus:border-brand-400 dark:focus:ring-brand-400/10"
            placeholder="you@example.com"
          />
        </div>

        <div>
          <label className="mb-1.5 block text-sm font-medium text-slate-700 dark:text-slate-300" for="password">
            Password
          </label>
          <input
            id="password"
            type="password"
            required
            minLength={8}
            value={password}
            onInput={(event) => setPassword((event.target as HTMLInputElement).value)}
            className="block w-full rounded-lg border border-slate-300 bg-white px-4 py-2.5 text-slate-900 outline-none transition-all placeholder:text-slate-400 focus:border-brand-500 focus:ring-4 focus:ring-brand-500/10 dark:border-slate-700 dark:bg-slate-950 dark:text-white dark:focus:border-brand-400 dark:focus:ring-brand-400/10"
            placeholder="••••••••"
          />
        </div>

        {error && (
          <div className="flex items-center gap-3 rounded-lg border border-red-200 bg-red-50 p-3 text-sm text-red-800 dark:border-red-900/50 dark:bg-red-950/30 dark:text-red-300" role="alert">
            <svg className="h-5 w-5 flex-shrink-0" fill="currentColor" viewBox="0 0 20 20">
              <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" />
            </svg>
            <p>{error}</p>
          </div>
        )}
        
        {notice && (
          <div className="flex items-center gap-3 rounded-lg border border-emerald-200 bg-emerald-50 p-3 text-sm text-emerald-800 dark:border-emerald-900/50 dark:bg-emerald-950/30 dark:text-emerald-300">
            <svg className="h-5 w-5 flex-shrink-0" fill="currentColor" viewBox="0 0 20 20">
              <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
            </svg>
            <p>{notice}</p>
          </div>
        )}

        <div className="mt-6 flex flex-col gap-3 sm:flex-row">
          <button
            type="submit"
            disabled={isSubmitting}
            className="flex w-full items-center justify-center rounded-lg bg-brand-500 px-4 py-2.5 text-sm font-semibold text-white transition-all hover:bg-brand-600 hover:shadow-md focus:ring-4 focus:ring-brand-500/20 active:scale-[0.98] disabled:cursor-not-allowed disabled:opacity-70"
          >
            {isSubmitting ? "Working..." : "Sign in"}
          </button>
          <button
            type="button"
            onClick={handleRegister}
            disabled={isSubmitting}
            className="flex w-full items-center justify-center rounded-lg border-2 border-slate-200 bg-white px-4 py-2.5 text-sm font-semibold text-slate-700 transition-all hover:border-brand-500 hover:bg-slate-50 hover:text-brand-700 focus:ring-4 focus:ring-slate-200 active:scale-[0.98] disabled:cursor-not-allowed disabled:opacity-70 dark:border-slate-700 dark:bg-slate-900 dark:text-slate-300 dark:hover:border-brand-400 dark:hover:bg-slate-800 dark:hover:text-brand-400 dark:focus:ring-slate-800"
          >
            {isSubmitting ? "Working..." : "Create account"}
          </button>
        </div>
      </form>
    </section>
  );
}