/** App entrypoint wiring query client, router, and error boundary. */
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { Component, type ComponentChildren, type ComponentType, render } from "preact";
import { Route, Router } from "wouter-preact";

import { AppShell } from "./components/layout/AppShell";
import { AdminRoute } from "./routes/Admin";
import { HomeRoute } from "./routes/Home";
import { InboxRoute } from "./routes/Inbox";
import { LoginRoute } from "./routes/Login";
import { ScanRoute } from "./routes/Scan";
import "./styles/tailwind.css";

const queryClient = new QueryClient();
const PreactQueryClientProvider =
  QueryClientProvider as unknown as ComponentType<{
    client: QueryClient;
    children: ComponentChildren;
  }>;

class GlobalErrorBoundary extends Component<
  { children?: ComponentChildren },
  { hasError: boolean }
> {
  constructor() {
    super();
    this.state = { hasError: false };
  }

  override componentDidCatch(error: Error): void {
    console.error("Unhandled UI error", error);
    this.setState({ hasError: true });
  }

  override render({ children }: { children?: ComponentChildren }): ComponentChildren {
    if (this.state.hasError) {
      return (
        <div className="rounded border border-red-300 bg-red-50 p-4 text-red-700">
          An unexpected UI error occurred. Please reload the page.
        </div>
      );
    }

    return children;
  }
}

function AppRouter() {
  return (
    <Router>
      <Route path="/" component={HomeRoute} />
      <Route path="/login" component={LoginRoute} />
      <Route path="/scan" component={ScanRoute} />
      <Route path="/owner" component={InboxRoute} />
      <Route path="/inbox" component={InboxRoute} />
      <Route path="/admin" component={AdminRoute} />
      <Route path="/:rest*" component={HomeRoute} />
    </Router>
  );
}

function App() {
  return (
    <PreactQueryClientProvider client={queryClient}>
      <GlobalErrorBoundary>
        <AppShell>
          <AppRouter />
        </AppShell>
      </GlobalErrorBoundary>
    </PreactQueryClientProvider>
  );
}

const container = document.getElementById("app");
if (!container) {
  throw new Error("Missing #app root element");
}

render(<App />, container);


