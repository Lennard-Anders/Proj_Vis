import { jsx as _jsx, jsxs as _jsxs } from "react/jsx-runtime";
import { useMemo, useState } from "react";
import DeckGL from "@deck.gl/react";
import { ScatterplotLayer } from "@deck.gl/layers";
import { useRisk, useScenario, useLoading } from "../state/selectors";
import MapHeatmap from "./MapHeatmap";
import MapLegend from "./MapLegend";
import TimeScrubber from "./TimeScrubber";
const TriView = () => {
    const risk = useRisk();
    const scenario = useScenario();
    const loading = useLoading();
    const [date, setDate] = useState(new Date().toISOString().slice(0, 10));
    const layers = useMemo(() => {
        if (!risk) {
            return [];
        }
        return [
            new ScatterplotLayer({
                id: "risk-layer",
                data: risk.grid,
                getPosition: (cell) => [cell.lon, cell.lat],
                getRadius: 6000,
                radiusUnits: "meters",
                getFillColor: (cell) => {
                    const intensity = Math.min(255, Math.round(cell.prob * 255));
                    const cooled = Math.max(0, 170 - Math.round(intensity / 2));
                    return [255, cooled, 0, 200];
                },
                pickable: true,
            }),
        ];
    }, [risk]);
    const INITIAL_VIEW_STATE = useMemo(() => ({ longitude: -120.25, latitude: 35.25, zoom: 5, pitch: 0, bearing: 0 }), []);
    return (_jsxs("div", { className: "panel", "aria-busy": loading, children: [_jsx("h2", { children: "Scenario Maps" }), _jsxs("p", { children: ["Active scenario: ", _jsx("strong", { children: scenario })] }), _jsxs("p", { children: ["Selected date: ", date] }), loading && _jsx("p", { children: "Loading synthetic tiles\u2026" }), !loading && risk && (_jsxs("div", { className: "tri-view", children: [_jsx("div", { className: "tri-view__grid", children: risk.grid.slice(0, 6).map((cell) => (_jsxs("div", { className: "tri-view__cell", children: [_jsxs("span", { children: [cell.lat.toFixed(2), ", ", cell.lon.toFixed(2)] }), _jsxs("span", { children: [(cell.prob * 100).toFixed(1), "%"] })] }, `${cell.lat}-${cell.lon}`))) }), _jsx("div", { className: "tri-view__deck", children: _jsx(DeckGL, { style: { width: "100%", height: "100%" }, layers: layers, initialViewState: INITIAL_VIEW_STATE, controller: true, getTooltip: (info) => {
                                const cell = (info && info.object) || undefined;
                                if (!cell) {
                                    return null;
                                }
                                return `Risk ${(cell.prob * 100).toFixed(1)}% at ${cell.lat.toFixed(2)}, ${cell.lon.toFixed(2)}`;
                            } }) }), _jsx(MapHeatmap, { data: risk }), _jsx(MapLegend, {})] })), _jsx(TimeScrubber, { date: date, onChange: setDate })] }));
};
export default TriView;
