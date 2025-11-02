import { jsxs as _jsxs, jsx as _jsx, Fragment as _Fragment } from "react/jsx-runtime";
import { useMemo, useState } from "react";
import DeckGL from "@deck.gl/react";
import { ScatterplotLayer } from "@deck.gl/layers";
import { TileLayer } from "@deck.gl/geo-layers";
import { BitmapLayer } from "@deck.gl/layers";
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
        const baseLayers = [
            new TileLayer({
                id: "base-map",
                data: "https://tile.openstreetmap.org/{z}/{x}/{y}.png",
                minZoom: 0,
                maxZoom: 19,
                tileSize: 256,
                renderSubLayers: (props) => {
                    const { boundingBox } = props.tile;
                    return new BitmapLayer(props, {
                        data: undefined,
                        image: props.data,
                        bounds: [boundingBox[0][0], boundingBox[0][1], boundingBox[1][0], boundingBox[1][1]],
                    });
                },
            }),
        ];
        if (!risk) {
            return baseLayers;
        }
        return [
            ...baseLayers,
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
    return (_jsxs("div", { className: "panel", "aria-busy": loading, children: [_jsxs("h2", { children: ["Scenario Maps - Build: ", new Date().toISOString()] }), _jsxs("p", { children: ["Active scenario: ", _jsx("strong", { children: scenario })] }), _jsxs("p", { children: ["Selected date: ", date] }), loading && _jsx("p", { children: "Loading synthetic tiles\u2026" }), !loading && risk && (_jsx(_Fragment, { children: _jsxs("div", { className: "maps-container", children: [_jsxs("div", { className: "tri-view", children: [_jsx("h3", { children: "Scenario Risk Map" }), _jsx("div", { className: "tri-view__grid", children: risk.grid.slice(0, 6).map((cell) => (_jsxs("div", { className: "tri-view__cell", children: [_jsxs("span", { children: [cell.lat.toFixed(2), ", ", cell.lon.toFixed(2)] }), _jsxs("span", { children: [(cell.prob * 100).toFixed(1), "%"] })] }, `${cell.lat}-${cell.lon}`))) }), _jsx("div", { className: "tri-view__deck", children: _jsx(DeckGL, { style: { width: "100%", height: "100%" }, layers: layers, initialViewState: INITIAL_VIEW_STATE, controller: true, getTooltip: (info) => {
                                            const cell = (info && info.object) || undefined;
                                            if (!cell) {
                                                return null;
                                            }
                                            return `Risk ${(cell.prob * 100).toFixed(1)}% at ${cell.lat.toFixed(2)}, ${cell.lon.toFixed(2)}`;
                                        } }) }), _jsx(MapHeatmap, { data: risk }), _jsx(MapLegend, {})] }), _jsxs("div", { className: "world-map", style: { marginLeft: '20px', flex: 1 }, children: [_jsx("h3", { style: { color: '#ff8c00', marginBottom: '10px' }, children: "World Reference Map" }), _jsxs("div", { style: { position: 'relative', height: '400px', background: '#0a1929', borderRadius: '8px', border: '2px solid #ff8c00', overflow: 'hidden' }, children: [_jsxs("svg", { style: { position: 'absolute', width: '100%', height: '100%' }, children: [[-60, -30, 0, 30, 60].map(lat => (_jsx("line", { x1: "0%", y1: `${((90 - lat) / 180) * 100}%`, x2: "100%", y2: `${((90 - lat) / 180) * 100}%`, stroke: "#334155", strokeWidth: "1" }, `lat-${lat}`))), [-120, -60, 0, 60, 120].map(lon => (_jsx("line", { x1: `${((lon + 180) / 360) * 100}%`, y1: "0%", x2: `${((lon + 180) / 360) * 100}%`, y2: "100%", stroke: "#334155", strokeWidth: "1" }, `lon-${lon}`)))] }), _jsx("div", { style: { position: 'absolute', color: '#94a3b8', fontSize: '12px', top: '10px', left: '10px' }, children: "Global Context Map" })] })] })] }) })), _jsx(TimeScrubber, { date: date, onChange: setDate })] }));
};
export default TriView;
