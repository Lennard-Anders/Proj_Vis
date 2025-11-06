import { render } from "@testing-library/react";
import { describe, it, expect, vi } from "vitest";
import TriView from ".";

vi.mock("../state/selectors", () => ({
  useRisk: () => ({
    grid: [
      { lat: 35, lon: -120, prob: 0.3, ci: [0.2, 0.4] as [number, number] },
    ],
    quality: { dqf_mask: [0], data_availability: [0.95] },
    meta: { grid_deg: 0.25 },
  }),
  useScenario: () => "observed",
  useLoading: () => false,
}));

vi.mock("./MapHeatmap", () => ({
  default: () => <div data-testid="heatmap" />,
}));

vi.mock("./MapLegend", () => ({
  default: () => <div data-testid="legend" />,
}));

vi.mock("./TimeScrubber", () => ({
  default: () => <div data-testid="scrubber" />,
}));

describe("TriView", () => {
  it("renders scenario information", () => {
    const { getByText } = render(<TriView />);
    expect(getByText(/Scenario Maps/)).toBeInTheDocument();
    expect(getByText(/observed/)).toBeInTheDocument();
  });
});
