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
      <h2>What-If Analysis</h2>
      <p style={{ fontSize: '0.9rem', color: 'var(--text-secondary)', marginBottom: 'var(--spacing-md)' }}>
        Adjust environmental parameters to see potential risk changes
      </p>
      <div className="what-if__controls">
  {(Object.entries(overrides) as Array<[string, number]>).map(([feature, value]) => (
          <label key={feature}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <span style={{ textTransform: 'capitalize' }}>{feature.replace(/_/g, ' ')}</span>
              <span>{value.toFixed(0)}</span>
            </div>
            <input
              type="range"
              min={0}
              max={50}
              value={value}
              onChange={(event: React.ChangeEvent<HTMLInputElement>) =>
                handleChange(feature, Number(event.target.value))
              }
            />
          </label>
        ))}
      </div>
      <button type="button" onClick={handleApply}>
        🔥 Run Scenario
      </button>
      {result && (
        <div style={{
          marginTop: 'var(--spacing-md)',
          padding: 'var(--spacing-md)',
          background: 'linear-gradient(135deg, #f0fdf4 0%, #dcfce7 100%)',
          borderRadius: '8px',
          border: '1px solid var(--success-green)',
          color: 'var(--text-primary)'
        }}>
          <strong>✅ Result:</strong> {result}
        </div>
      )}
    </div>
  );
};

export default WhatIfPanel;
