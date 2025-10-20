import { jsx as _jsx, jsxs as _jsxs } from "react/jsx-runtime";
import { useEffect } from "react";
import TriView from "./components/TriView";
import WhatIfPanel from "./components/WhatIfPanel";
import ExplanationPanel from "./components/ExplanationPanel";
import QualityBoard from "./components/QualityBoard";
import EventExplorer from "./components/EventExplorer";
import { useTriViewState } from "./state/store";
import TimeScrubber from "./components/TimeScrubber";
import PromptBar from "./components/PromptBar";
import { FaCloudSun, FaBolt, FaWind, FaCloudRain } from "react-icons/fa";
const App = () => {
    const initialize = useTriViewState((state) => state.initialize);
    useEffect(() => {
        initialize();
    }, [initialize]);
    return (_jsxs("div", { className: "app-layout", children: [_jsx("div", { className: "timeline-bar", children: _jsx("div", { className: "timeline-bar__inner", children: _jsx(TimeScrubber, { date: new Date().toISOString().slice(0, 10), onChange: () => { } }) }) }), _jsxs("div", { className: "shell-grid", children: [_jsxs("aside", { className: "shell-dock", children: [_jsx("button", { className: "icon-btn", title: "Weather", children: _jsx(FaCloudSun, {}) }), _jsx("button", { className: "icon-btn", title: "Thunder", children: _jsx(FaBolt, {}) }), _jsx("button", { className: "icon-btn", title: "Wind", children: _jsx(FaWind, {}) }), _jsx("button", { className: "icon-btn", title: "Rain", children: _jsx(FaCloudRain, {}) })] }), _jsx("main", { className: "shell-main", children: _jsx(TriView, {}) }), _jsxs("aside", { className: "shell-aside", children: [_jsx(WhatIfPanel, {}), _jsx(ExplanationPanel, {}), _jsx(QualityBoard, {}), _jsx(EventExplorer, {})] })] }), _jsx("footer", { className: "prompt-footer", children: _jsx(PromptBar, {}) })] }));
};
export default App;
