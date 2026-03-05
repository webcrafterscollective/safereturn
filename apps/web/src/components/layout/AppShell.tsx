/** Application shell with responsive navigation and role-aware menu items. */

import type { ComponentChildren } from "preact";
import { useEffect, useState } from "preact/hooks";
import { Link, useLocation } from "wouter-preact";

import {
  AUTH_CHANGED_EVENT,
  getSessionSnapshot,
  logoutStoredSession,
} from "../../lib/api/client";

interface AppShellProps {
  children: ComponentChildren;
}

const THEME_STORAGE_KEY = "app-theme";

export function AppShell({ children }: AppShellProps) {
  const [location, setLocation] = useLocation();
  const [dark, setDark] = useState<boolean>(() => localStorage.getItem(THEME_STORAGE_KEY) === "dark");
  const [session, setSession] = useState(getSessionSnapshot());

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

  useEffect(() => {
    const handleAuthChanged = () => setSession(getSessionSnapshot());
    window.addEventListener(AUTH_CHANGED_EVENT, handleAuthChanged);
    window.addEventListener("storage", handleAuthChanged);
    return () => {
      window.removeEventListener(AUTH_CHANGED_EVENT, handleAuthChanged);
      window.removeEventListener("storage", handleAuthChanged);
    };
  }, []);

  async function handleLogout(): Promise<void> {
    await logoutStoredSession();
    setSession(getSessionSnapshot());
    setLocation("/login");
  }

  const linkClass = (path: string) =>
    `rounded px-3 py-1.5 text-sm ${
      location === path
        ? "bg-brand-500 text-white"
        : "hover:bg-slate-200 dark:hover:bg-slate-800"
    }`;

  return (
    <div className="min-h-screen bg-gradient-to-b from-white via-sky-50 to-slate-100 dark:from-slate-950 dark:via-slate-900 dark:to-slate-950">
      <header className="border-b border-slate-200/70 bg-white/70 backdrop-blur dark:border-slate-700 dark:bg-slate-900/70">
        <nav
          className="mx-auto flex max-w-6xl flex-wrap items-center justify-between gap-2 px-4 py-3 sm:px-6"
          aria-label="Main navigation"
        >
          <div className="text-base font-semibold tracking-wide text-brand-700 dark:text-brand-500">
            SafeReturn
          </div>
          <div className="flex flex-wrap items-center gap-2">
            <Link href="/" className={linkClass("/")}>
              Home
            </Link>
            <Link href="/scan" className={linkClass("/scan")}>
              Finder
            </Link>

            {!session.isAuthenticated && (
              <Link href="/login" className={linkClass("/login")}>
                Login
              </Link>
            )}

            {session.isAuthenticated && (
              <Link href="/owner" className={linkClass("/owner")}>
                Owner
              </Link>
            )}

            {session.isAuthenticated && session.isAdmin && (
              <Link href="/admin" className={linkClass("/admin")}>
                Admin
              </Link>
            )}

            {session.isAuthenticated && (
              <button
                type="button"
                className="rounded border border-slate-300 px-3 py-1.5 text-sm hover:bg-slate-100 dark:border-slate-700 dark:hover:bg-slate-800"
                onClick={() => void handleLogout()}
              >
                Logout
              </button>
            )}

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
