/** Basic frontend smoke test to verify Home route rendering. */
import { render, screen } from "@testing-library/preact";

import { HomeRoute } from "../routes/Home";

vi.mock("@tanstack/react-query", () => ({
  useQuery: () => ({
    isPending: false,
    isError: false,
    data: { status: "live" },
  }),
}));

vi.mock("../lib/api/client", () => ({
  getHealthLive: async () => ({ status: "live" }),
  getHealthReady: async () => ({ status: "ready" }),
  getMetricsText: async () => "http_requests_total 1",
  refreshStoredSession: async () => ({
    access_token: "a",
    refresh_token: "b",
    token_type: "bearer",
    expires_in: 900,
  }),
  logoutStoredSession: async () => undefined,
}));

describe("HomeRoute", () => {
  it("renders template title", async () => {
    render(<HomeRoute />);
    expect(await screen.findByText("SafeReturn Platform")).toBeInTheDocument();
  });
});


