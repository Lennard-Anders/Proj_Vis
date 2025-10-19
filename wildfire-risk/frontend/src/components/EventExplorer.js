import { jsx as _jsx, jsxs as _jsxs } from "react/jsx-runtime";
import { useFrames } from "../state/selectors";
const EventExplorer = () => {
    const frames = useFrames();
    return (_jsxs("div", { className: "panel", children: [_jsx("h2", { children: "Event Explorer" }), !frames && _jsx("p", { children: "No frames available." }), frames && (_jsx("div", { className: "event-explorer__strip", children: frames.frames.map((frame) => (_jsxs("div", { className: "event-explorer__item", children: [_jsx("img", { src: frame.url, alt: frame.frame_id }), _jsx("span", { children: frame.timestamp })] }, frame.frame_id))) }))] }));
};
export default EventExplorer;
