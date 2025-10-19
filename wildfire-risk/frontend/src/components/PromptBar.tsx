import React, { useState } from "react";
import { TriViewState, useTriViewState } from "../state/store";

const PromptBar: React.FC = () => {
  const [text, setText] = useState("");
  const runWhatIf = useTriViewState((s: TriViewState) => s.runWhatIf);

  const submit = async () => {
    if (!text.trim()) return;
    // Simple heuristic: extract "wind=10" pairs as mock overrides
    const overrides: Record<string, number> = {};
    text.split(/\s+/).forEach((tok) => {
      const m = tok.match(/([^=]+)=(\d+(?:\.\d+)?)/);
      if (m) overrides[m[1]] = Number(m[2]);
    });
    await runWhatIf(Object.keys(overrides).length ? overrides : { wind_speed_10m: 12 });
    setText("");
  };

  return (
    <div className="prompt-bar">
      <input
        className="prompt-input"
        placeholder="Ask: What if wind_speed_10m=15 and rh=20?"
        value={text}
        onChange={(e) => setText(e.target.value)}
        onKeyDown={(e) => e.key === "Enter" && submit()}
      />
      <button type="button" className="btn btn-accent" onClick={submit}>
        Send
      </button>
    </div>
  );
};

export default PromptBar;
