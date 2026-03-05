/** Responsive application shell with navigation and dark mode toggle. */
import type { ComponentChildren } from "preact";
import { useEffect, useState } from "preact/hooks";
import { Link, useLocation } from "wouter-preact";

interface AppShellProps {
  children: ComponentChildren;
}

const THEME_STORAGE_KEY = "app-theme";

export function AppShell({ children }: AppShellProps) {
  const [location] = useLocation();
  const [dark, setDark] = useState<boolean>(() => localStorage.getItem(THEME_STORAGE_KEY) === "dark");

  useEffect(() => {
    const root = document.documentElement;
    if (dark) {
      root.classList.add("dark");
      localStorage.setItem(THEME_STORAGE_KEY, "dark");
    } else {
      root.classList.remove("dark");
      localStorage.setItem(THEME_STORAGE_KEY, "light");
    }
  }, [dark]);

  return (
    <div className="min-h-screen bg-gradient-to-b from-white via-sky-50 to-slate-100 dark:from-slate-950 dark:via-slate-900 dark:to-slate-950">
      <header className="border-b border-slate-200/70 bg-white/70 backdrop-blur dark:border-slate-700 dark:bg-slate-900/70">
        <nav className="mx-auto flex max-w-6xl items-center justify-between px-4 py-3 sm:px-6" aria-label="Main navigation">
          <div className="text-sm font-semibold tracking-wide text-brand-700 dark:text-brand-500">fastapi-fullstack-prod</div>
          <div className="flex items-center gap-3">
            <Link href="/" className={`rounded px-3 py-1.5 text-sm ${location === "/" ? "bg-brand-500 text-white" : "hover:bg-slate-200 dark:hover:bg-slate-800"}`}>
              Home
            </Link>
            <Link href="/login" className={`rounded px-3 py-1.5 text-sm ${location === "/login" ? "bg-brand-500 text-white" : "hover:bg-slate-200 dark:hover:bg-slate-800"}`}>
              Login
            </Link>
            <Link href="/scan" className={`rounded px-3 py-1.5 text-sm ${location === "/scan" ? "bg-brand-500 text-white" : "hover:bg-slate-200 dark:hover:bg-slate-800"}`}>
              Finder
            </Link>
            <Link href="/inbox" className={`rounded px-3 py-1.5 text-sm ${location === "/inbox" ? "bg-brand-500 text-white" : "hover:bg-slate-200 dark:hover:bg-slate-800"}`}>
              Owner
            </Link>
            <button
              type="button"
              className="rounded border border-slate-300 px-3 py-1.5 text-sm hover:bg-slate-100 dark:border-slate-700 dark:hover:bg-slate-800"
              onClick={() => setDark((value) => !value)}
              aria-label="Toggle dark mode"
            >
              {dark ? "Light" : "Dark"}
            </button>
          </div>
        </nav>
      </header>

      <main className="mx-auto max-w-6xl px-4 py-8 sm:px-6">{children}</main>
    </div>
  );
}


