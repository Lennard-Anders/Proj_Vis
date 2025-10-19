import { jsx as _jsx } from "react/jsx-runtime";
import { render } from "@testing-library/react";
import { describe, it, expect, vi } from "vitest";
import TriView from "./TriView";
vi.mock("../state/selectors", () => ({
    useRisk: () => ({
        grid: [
            { lat: 35, lon: -120, prob: 0.3, ci: [0.2, 0.4] },
        ],
        quality: { dqf_mask: [0], data_availability: [0.95] },
        meta: { grid_deg: 0.25 },
    }),
    useScenario: () => "observed",
    useLoading: () => false,
}));
vi.mock("./MapHeatmap", () => ({
    default: () => _jsx("div", { "data-testid": "heatmap" }),
}));
vi.mock("./MapLegend", () => ({
    default: () => _jsx("div", { "data-testid": "legend" }),
}));
vi.mock("./TimeScrubber", () => ({
    default: () => _jsx("div", { "data-testid": "scrubber" }),
}));
describe("TriView", () => {
    it("renders scenario information", () => {
        const { getByText } = render(_jsx(TriView, {}));
        expect(getByText(/Scenario Maps/)).toBeInTheDocument();
        expect(getByText(/observed/)).toBeInTheDocument();
    });
});
