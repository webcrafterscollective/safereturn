/** Home route showing responsive layout and API health status query. */
import { useQuery } from "@tanstack/react-query";
import { useState } from "preact/hooks";
import { Link } from "wouter-preact";

import {
  ApiError,
  getHealthLive,
  getHealthReady,
  getMetricsText,
  logoutStoredSession,
  refreshStoredSession,
} from "../lib/api/client";

function HealthSkeleton() {
  return (
    <div className="flex animate-pulse flex-col gap-3 rounded-xl border border-slate-100 bg-white p-5 shadow-sm dark:border-slate-800/60 dark:bg-slate-900/50" aria-label="Loading health status">
      <div className="h-4 w-2/3 rounded-md bg-slate-200 dark:bg-slate-700" />
      <div className="h-4 w-1/3 rounded-md bg-slate-100 dark:bg-slate-800" />
    </div>
  );
}

export function HomeRoute() {
  const [metricsPreview, setMetricsPreview] = useState("");
  const [authStatus, setAuthStatus] = useState("");
  const [authError, setAuthError] = useState("");

  const healthQuery = useQuery({
    queryKey: ["health", "live"],
    queryFn: getHealthLive,
  });
  const readyQuery = useQuery({
    queryKey: ["health", "ready"],
    queryFn: getHealthReady,
  });

  async function handleRefreshSession() {
    setAuthStatus("");
    setAuthError("");
    try {
      await refreshStoredSession();
      setAuthStatus("Session refreshed successfully.");
    } catch (error) {
      if (error instanceof ApiError) {
        setAuthError(`Refresh failed (${error.status}). Login again.`);
      } else {
        setAuthError("Refresh failed due to unexpected error.");
      }
    }
  }

  async function handleLogoutSession() {
    setAuthStatus("");
    setAuthError("");
    try {
      await logoutStoredSession();
      setAuthStatus("Session closed successfully.");
    } catch {
      setAuthError("Logout failed. Clear tokens and login again.");
    }
  }

  async function handleLoadMetrics() {
    setMetricsPreview("");
    try {
      const payload = await getMetricsText();
      setMetricsPreview(payload.split("\n").slice(0, 12).join("\n"));
    } catch {
      setMetricsPreview("Unable to load /metrics right now.");
    }
  }

  return (
    <section className="grid items-start gap-6 lg:grid-cols-[2fr_1fr]">
      <article className="rounded-2xl border border-slate-200/80 bg-white p-8 shadow-soft dark:border-slate-800 dark:bg-slate-900">
        <div className="mb-6 inline-flex items-center rounded-full bg-brand-50 px-3 py-1 text-xs font-semibold text-brand-700 dark:bg-brand-500/10 dark:text-brand-400">
          Platform Overview
        </div>
        <h1 className="text-3xl font-extrabold tracking-tight text-slate-900 dark:text-white sm:text-4xl">
          SafeReturn
        </h1>
        <p className="mt-4 max-w-2xl text-base leading-relaxed text-slate-600 dark:text-slate-300">
          Privacy-first QR lost-item recovery for individuals and organizations. Finders can
          contact owners securely without ever exposing personal contact details.
        </p>
        <div className="mt-8 flex flex-wrap gap-4">
          <Link href="/scan" className="inline-flex items-center justify-center rounded-lg bg-brand-500 px-6 py-2.5 text-sm font-semibold text-white transition-all hover:bg-brand-600 hover:shadow-md focus:ring-4 focus:ring-brand-500/20 active:scale-95">
            I found an item
          </Link>
          <Link href="/owner" className="inline-flex items-center justify-center rounded-lg border-2 border-slate-200 bg-transparent px-6 py-2.5 text-sm font-semibold text-slate-700 transition-all hover:border-brand-500 hover:bg-slate-50 hover:text-brand-700 focus:ring-4 focus:ring-slate-200 dark:border-slate-700 dark:text-slate-200 dark:hover:border-brand-400 dark:hover:bg-slate-800 dark:hover:text-brand-400 dark:focus:ring-slate-800">
            Owner Dashboard
          </Link>
          <a
            href="/doc"
            className="inline-flex items-center justify-center rounded-lg border-2 border-transparent px-6 py-2.5 text-sm font-semibold text-slate-500 transition-all hover:bg-slate-100 hover:text-slate-900 dark:text-slate-400 dark:hover:bg-slate-800 dark:hover:text-white"
          >
            API Swagger
          </a>
        </div>
      </article>

      <aside className="rounded-2xl border border-slate-200/80 bg-white p-6 shadow-soft dark:border-slate-800 dark:bg-slate-900">
        <h2 className="flex items-center gap-2 text-lg font-bold text-slate-900 dark:text-white">
          <div className="h-2 w-2 rounded-full bg-emerald-500"></div>
          System Status
        </h2>
        <div className="mt-6 space-y-4">
          {healthQuery.isPending && <HealthSkeleton />}
          
          {healthQuery.isError && (
            <div className="rounded-xl border border-red-200 bg-red-50 p-4 dark:border-red-900/50 dark:bg-red-950/30">
              <p className="text-sm font-medium text-red-800 dark:text-red-300">
                Failed to load health status.
              </p>
            </div>
          )}
          
          {healthQuery.data && (
            <div className="flex items-center justify-between rounded-xl border border-slate-100 bg-slate-50 p-4 dark:border-slate-800/60 dark:bg-slate-900/50">
              <span className="text-sm font-medium text-slate-600 dark:text-slate-400">API Service</span>
              <span className="inline-flex items-center rounded-full bg-emerald-100 px-2.5 py-0.5 text-xs font-semibold text-emerald-800 dark:bg-emerald-500/20 dark:text-emerald-400">
                {healthQuery.data.status}
              </span>
            </div>
          )}
          
          {readyQuery.data && (
            <div className="flex items-center justify-between rounded-xl border border-slate-100 bg-slate-50 p-4 dark:border-slate-800/60 dark:bg-slate-900/50">
              <span className="text-sm font-medium text-slate-600 dark:text-slate-400">Database</span>
              <span className="inline-flex items-center rounded-full bg-emerald-100 px-2.5 py-0.5 text-xs font-semibold text-emerald-800 dark:bg-emerald-500/20 dark:text-emerald-400">
                {readyQuery.data.status}
              </span>
            </div>
          )}

          <div className="pt-4 border-t border-slate-100 dark:border-slate-800">
            <h3 className="mb-3 text-xs font-semibold uppercase tracking-wider text-slate-500">Admin Controls</h3>
            <div className="flex flex-col gap-2">
              <button
                type="button"
                onClick={handleRefreshSession}
                className="w-full rounded-lg border border-slate-200 bg-white px-4 py-2 text-sm font-medium text-slate-700 transition-colors hover:bg-slate-50 hover:text-brand-600 active:bg-slate-100 dark:border-slate-700 dark:bg-slate-900 dark:text-slate-300 dark:hover:bg-slate-800 dark:hover:text-brand-400"
              >
                Refresh Session
              </button>
              <div className="grid grid-cols-2 gap-2">
                <button
                  type="button"
                  onClick={handleLogoutSession}
                  className="rounded-lg border border-slate-200 bg-white px-3 py-2 text-sm font-medium text-slate-700 transition-colors hover:bg-slate-50 hover:text-red-600 active:bg-slate-100 dark:border-slate-700 dark:bg-slate-900 dark:text-slate-300 dark:hover:bg-slate-800 dark:hover:text-red-400"
                >
                  Logout
                </button>
                <button
                  type="button"
                  onClick={handleLoadMetrics}
                  className="rounded-lg border border-slate-200 bg-white px-3 py-2 text-sm font-medium text-slate-700 transition-colors hover:bg-slate-50 active:bg-slate-100 dark:border-slate-700 dark:bg-slate-900 dark:text-slate-300 dark:hover:bg-slate-800"
                >
                  Metrics
                </button>
              </div>
            </div>
          </div>

          {authStatus && (
            <p className="rounded-lg border border-emerald-200 bg-emerald-50 p-3 text-sm font-medium text-emerald-800 dark:border-emerald-900/50 dark:bg-emerald-950/30 dark:text-emerald-300">
              {authStatus}
            </p>
          )}
          {authError && (
            <p className="rounded-lg border border-red-200 bg-red-50 p-3 text-sm font-medium text-red-800 dark:border-red-900/50 dark:bg-red-950/30 dark:text-red-300">
              {authError}
            </p>
          )}
          {metricsPreview && (
            <div className="overflow-hidden rounded-lg border border-slate-200 bg-slate-900 dark:border-slate-700 dark:bg-black">
              <div className="flex items-center border-b border-slate-700 bg-slate-800 px-3 py-1.5">
                <span className="text-xs font-medium text-slate-300">/metrics output</span>
              </div>
              <pre className="overflow-auto p-3 text-[11px] leading-5 text-emerald-400">
                {metricsPreview}
              </pre>
            </div>
          )}
        </div>
      </aside>
    </section>
  );
}