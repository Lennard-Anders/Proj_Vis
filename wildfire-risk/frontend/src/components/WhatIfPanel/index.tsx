import React, { useState } from "react";
import { runCounterfactual } from "../../api/client";
import { useTriViewState, TriViewState } from "../../state/store";

const defaultOverrides = {
  wind_speed_10m: 10,
  rh: 25,
  rain_24h: 1,
};

const WhatIfPanel: React.FC = () => {
  const [overrides, setOverrides] = useState<Record<string, number>>(defaultOverrides);
  const [result, setResult] = useState<string>("");
  const runWhatIf = useTriViewState((state: TriViewState) => state.runWhatIf);

  const handleChange = (feature: string, value: number) => {
  setOverrides((prev: Record<string, number>) => ({ ...prev, [feature]: value }));
  };

  const handleApply = async () => {
    await runWhatIf(overrides);
    const response = await runCounterfactual(overrides);
    setResult(
      `New probability ${(response.probability * 100).toFixed(1)}% via ${response.used} path`
    );
  };

  return (
    <div className="panel">
      <h2>What-If Panel</h2>
      <div className="what-if__controls">
  {(Object.entries(overrides) as Array<[string, number]>).map(([feature, value]) => (
          <label key={feature}>
            {feature}
            <input
              type="range"
              min={0}
              max={50}
              value={value}
              onChange={(event: React.ChangeEvent<HTMLInputElement>) =>
                handleChange(feature, Number(event.target.value))
              }
            />
            <span>{value.toFixed(0)}</span>
          </label>
        ))}
      </div>
      <button type="button" onClick={handleApply}>
        Apply
      </button>
      {result && <p>{result}</p>}
    </div>
  );
};

export default WhatIfPanel;
