/** Home route showing responsive layout and API health status query. */
import { useQuery } from "@tanstack/react-query";
import { Link } from "wouter-preact";

import { getHealthLive } from "../lib/api/client";

function HealthSkeleton() {
  return (
    <div className="animate-pulse rounded-lg border border-slate-200 bg-white p-4 dark:border-slate-700 dark:bg-slate-900" aria-label="Loading health status">
      <div className="mb-3 h-4 w-40 rounded bg-slate-200 dark:bg-slate-700" />
      <div className="h-4 w-24 rounded bg-slate-200 dark:bg-slate-700" />
    </div>
  );
}

export function HomeRoute() {
  const healthQuery = useQuery({
    queryKey: ["health", "live"],
    queryFn: getHealthLive,
  });

  return (
    <section className="grid gap-6 md:grid-cols-[2fr_1fr]">
      <article className="rounded-xl border border-slate-200 bg-white p-6 shadow-sm dark:border-slate-700 dark:bg-slate-900">
        <h1 className="text-2xl font-bold text-slate-900 dark:text-slate-100">SafeReturn Platform</h1>
        <p className="mt-3 text-sm leading-6 text-slate-600 dark:text-slate-300">
          Privacy-first QR lost-item recovery for individuals and organizations. Finders can
          contact owners without exposing personal contact details.
        </p>
        <div className="mt-4 flex gap-3">
          <Link href="/scan" className="rounded bg-brand-500 px-4 py-2 text-sm font-medium text-white hover:bg-brand-700">
            I found an item
          </Link>
          <Link href="/inbox" className="rounded border border-brand-500 px-4 py-2 text-sm font-medium text-brand-700 hover:bg-brand-50 dark:text-brand-400 dark:hover:bg-slate-800">
            Owner dashboard
          </Link>
        </div>
      </article>

      <aside className="rounded-xl border border-slate-200 bg-white p-6 shadow-sm dark:border-slate-700 dark:bg-slate-900">
        <h2 className="text-lg font-semibold">API Health</h2>
        <div className="mt-4">
          {healthQuery.isPending && <HealthSkeleton />}
          {healthQuery.isError && (
            <p className="rounded border border-red-300 bg-red-50 p-3 text-sm text-red-700 dark:border-red-700 dark:bg-red-950/30 dark:text-red-300">
              Failed to load health status.
            </p>
          )}
          {healthQuery.data && (
            <p className="rounded border border-emerald-300 bg-emerald-50 p-3 text-sm text-emerald-700 dark:border-emerald-700 dark:bg-emerald-950/30 dark:text-emerald-300">
              Service status: <strong>{healthQuery.data.status}</strong>
            </p>
          )}
        </div>
      </aside>
    </section>
  );
}


