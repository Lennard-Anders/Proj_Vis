import { jsx as _jsx, jsxs as _jsxs } from "react/jsx-runtime";
import { useExplanation } from "../state/selectors";
const ExplanationPanel = () => {
    const explanation = useExplanation();
    if (!explanation) {
        return (_jsxs("div", { className: "panel", children: [_jsx("h2", { children: "Explanation" }), _jsx("p", { children: "No explanation available." })] }));
    }
    return (_jsxs("div", { className: "panel", children: [_jsx("h2", { children: "Explanation" }), _jsxs("p", { children: ["Probability: ", _jsxs("strong", { children: [(explanation.probability * 100).toFixed(1), "%"] })] }), _jsx("h3", { children: "Local Contributions" }), _jsx("ul", { children: explanation.local_shap.map((item) => (_jsxs("li", { children: [item.feature, ": ", item.contribution.toFixed(2)] }, item.feature))) }), _jsx("h3", { children: "Interactions" }), _jsx("ul", { children: explanation.interactions.map((interaction) => (_jsxs("li", { children: [interaction.pair.join(" × "), ": ", interaction.value.toFixed(2)] }, interaction.pair.join("-")))) }), _jsxs("p", { children: ["OOD: ", explanation.ood ? "Yes" : "No"] })] }));
};
export default ExplanationPanel;
