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

  const linkClass = (path: string) => {
    const isActive = location === path;
    return `relative rounded-full px-4 py-2 text-sm font-medium transition-all duration-200 ${
      isActive
        ? "bg-brand-50 text-brand-700 dark:bg-brand-500/10 dark:text-brand-400"
        : "text-slate-600 hover:bg-slate-100 hover:text-slate-900 dark:text-slate-400 dark:hover:bg-slate-800 dark:hover:text-slate-50"
    }`;
  };

  return (
    <div className="min-h-screen bg-slate-50 text-slate-900 selection:bg-brand-100 dark:bg-slate-950 dark:text-slate-50 dark:selection:bg-brand-900/50">
      <header className="sticky top-0 z-50 border-b border-slate-200/80 bg-white/80 backdrop-blur-md dark:border-slate-800/80 dark:bg-slate-950/80">
        <nav
          className="mx-auto flex max-w-6xl flex-wrap items-center justify-between gap-4 px-4 py-3 sm:px-6 lg:px-8"
          aria-label="Main navigation"
        >
          <div className="flex items-center gap-2">
            <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-brand-500 font-bold text-white shadow-sm">
              S
            </div>
            <div className="text-lg font-bold tracking-tight text-slate-900 dark:text-white">
              SafeReturn
            </div>
          </div>
          <div className="flex flex-wrap items-center gap-1 sm:gap-2">
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
                className="ml-2 rounded-full border border-slate-200 px-4 py-2 text-sm font-medium text-slate-600 transition-colors hover:bg-slate-100 hover:text-slate-900 dark:border-slate-700 dark:text-slate-300 dark:hover:bg-slate-800 dark:hover:text-white"
                onClick={() => void handleLogout()}
              >
                Logout
              </button>
            )}

            <button
              type="button"
              className="ml-2 flex h-9 w-9 items-center justify-center rounded-full border border-slate-200 text-slate-500 transition-colors hover:bg-slate-100 hover:text-slate-900 dark:border-slate-700 dark:text-slate-400 dark:hover:bg-slate-800 dark:hover:text-white"
              onClick={() => setDark((value) => !value)}
              aria-label="Toggle dark mode"
              title="Toggle theme"
            >
              {dark ? (
                <svg className="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 3v1m0 16v1m9-9h-1M4 12H3m15.364 6.364l-.707-.707M6.343 6.343l-.707-.707m12.728 0l-.707.707M6.343 17.657l-.707.707M16 12a4 4 0 11-8 0 4 4 0 018 0z" />
                </svg>
              ) : (
                <svg className="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M20.354 15.354A9 9 0 018.646 3.646 9.003 9.003 0 0012 21a9.003 9.003 0 008.354-5.646z" />
                </svg>
              )}
            </button>
          </div>
        </nav>
      </header>

      <main className="mx-auto max-w-6xl px-4 py-8 sm:px-6 lg:px-8">{children}</main>
    </div>
  );
}