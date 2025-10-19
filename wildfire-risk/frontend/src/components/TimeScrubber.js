import { jsx as _jsx, jsxs as _jsxs } from "react/jsx-runtime";
const TimeScrubber = ({ date, onChange }) => (_jsx("div", { className: "time-scrubber", children: _jsxs("label", { htmlFor: "scrubber", children: ["Date", _jsx("input", { id: "scrubber", type: "date", value: date, onChange: (event) => onChange(event.target.value) })] }) }));
export default TimeScrubber;
