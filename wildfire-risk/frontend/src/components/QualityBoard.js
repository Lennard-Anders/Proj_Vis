import { jsx as _jsx, jsxs as _jsxs } from "react/jsx-runtime";
import { useRisk } from "../state/selectors";
const QualityBoard = () => {
    const risk = useRisk();
    return (_jsxs("div", { className: "panel", children: [_jsx("h2", { children: "Quality Board" }), !risk && _jsx("p", { children: "No quality metrics yet." }), risk && (_jsxs("ul", { children: [_jsxs("li", { children: ["Grid size: ", risk.grid.length] }), _jsxs("li", { children: ["Avg availability: ", average(risk.quality.data_availability).toFixed(2)] })] }))] }));
};
function average(values) {
    if (!values.length)
        return 0;
    return values.reduce((sum, value) => sum + value, 0) / values.length;
}
export default QualityBoard;
