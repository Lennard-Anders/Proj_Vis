import { jsx as _jsx, jsxs as _jsxs } from "react/jsx-runtime";
const MapHeatmap = ({ data }) => {
    if (!data) {
        return _jsx("p", { children: "No risk data available yet." });
    }
    return (_jsxs("div", { className: "map-heatmap", children: [_jsx("strong", { children: "Heatmap Preview" }), _jsx("ul", { children: data.grid.slice(0, 5).map((cell) => (_jsxs("li", { children: [cell.lat.toFixed(2), ",", cell.lon.toFixed(2), " \u2192 ", (cell.prob * 100).toFixed(1), "%"] }, `${cell.lat}-${cell.lon}`))) })] }));
};
export default MapHeatmap;
