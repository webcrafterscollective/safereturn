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
}));

describe("HomeRoute", () => {
  it("renders template title", async () => {
    render(<HomeRoute />);
    expect(await screen.findByText("FastAPI + Preact Production Template")).toBeInTheDocument();
  });
});


