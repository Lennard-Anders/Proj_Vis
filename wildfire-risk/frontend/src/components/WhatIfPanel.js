import { jsx as _jsx, jsxs as _jsxs } from "react/jsx-runtime";
import { useState } from "react";
import { runCounterfactual } from "../api/client";
import { useTriViewState } from "../state/store";
const defaultOverrides = {
    wind_speed_10m: 10,
    rh: 25,
    rain_24h: 1,
};
const WhatIfPanel = () => {
    const [overrides, setOverrides] = useState(defaultOverrides);
    const [result, setResult] = useState("");
    const runWhatIf = useTriViewState((state) => state.runWhatIf);
    const handleChange = (feature, value) => {
        setOverrides((prev) => ({ ...prev, [feature]: value }));
    };
    const handleApply = async () => {
        await runWhatIf(overrides);
        const response = await runCounterfactual(overrides);
        setResult(`New probability ${(response.probability * 100).toFixed(1)}% via ${response.used} path`);
    };
    return (_jsxs("div", { className: "panel", children: [_jsx("h2", { children: "What-If Panel" }), _jsx("div", { className: "what-if__controls", children: Object.entries(overrides).map(([feature, value]) => (_jsxs("label", { children: [feature, _jsx("input", { type: "range", min: 0, max: 50, value: value, onChange: (event) => handleChange(feature, Number(event.target.value)) }), _jsx("span", { children: value.toFixed(0) })] }, feature))) }), _jsx("button", { type: "button", onClick: handleApply, children: "Apply" }), result && _jsx("p", { children: result })] }));
};
export default WhatIfPanel;
