import { jsx as _jsx, jsxs as _jsxs } from "react/jsx-runtime";
import { useState } from "react";
import { useTriViewState } from "../state/store";
const PromptBar = () => {
    const [text, setText] = useState("");
    const runWhatIf = useTriViewState((s) => s.runWhatIf);
    const submit = async () => {
        if (!text.trim())
            return;
        // Simple heuristic: extract "wind=10" pairs as mock overrides
        const overrides = {};
        text.split(/\s+/).forEach((tok) => {
            const m = tok.match(/([^=]+)=(\d+(?:\.\d+)?)/);
            if (m)
                overrides[m[1]] = Number(m[2]);
        });
        await runWhatIf(Object.keys(overrides).length ? overrides : { wind_speed_10m: 12 });
        setText("");
    };
    return (_jsxs("div", { className: "prompt-bar", children: [_jsx("input", { className: "prompt-input", placeholder: "Ask: What if wind_speed_10m=15 and rh=20?", value: text, onChange: (e) => setText(e.target.value), onKeyDown: (e) => e.key === "Enter" && submit() }), _jsx("button", { type: "button", className: "btn btn-accent", onClick: submit, children: "Send" })] }));
};
export default PromptBar;
