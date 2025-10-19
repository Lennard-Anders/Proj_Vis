import { jsx as _jsx, jsxs as _jsxs } from "react/jsx-runtime";
import { useEffect } from "react";
import TriView from "./components/TriView";
import WhatIfPanel from "./components/WhatIfPanel";
import ExplanationPanel from "./components/ExplanationPanel";
import QualityBoard from "./components/QualityBoard";
import EventExplorer from "./components/EventExplorer";
import { useTriViewState } from "./state/store";
const App = () => {
    const initialize = useTriViewState((state) => state.initialize);
    useEffect(() => {
        initialize();
    }, [initialize]);
    return (_jsxs("div", { className: "app-layout", children: [_jsxs("header", { className: "app-header", children: [_jsx("h1", { children: "Wildfire Risk Explorer" }), _jsx("p", { children: "Synthetic tri-view for wildfire risk scenarios." })] }), _jsxs("main", { className: "app-main", children: [_jsx("section", { className: "app-main__maps", children: _jsx(TriView, {}) }), _jsxs("aside", { className: "app-main__panels", children: [_jsx(WhatIfPanel, {}), _jsx(ExplanationPanel, {}), _jsx(QualityBoard, {}), _jsx(EventExplorer, {})] })] })] }));
};
export default App;
