/**
 * What-if panel with sliders
 */
import React, { useState } from 'react';
import { useCounterfactual } from '../hooks/useCounterfactual';
import type { FeatureDelta } from '../api/types';

interface WhatIfPanelProps {
  lat: number;
  lon: number;
  date: string;
}

export const WhatIfPanel: React.FC<WhatIfPanelProps> = ({ lat, lon, date }) => {
  const [deltas, setDeltas] = useState<FeatureDelta>({});
  const { data, loading, runCounterfactual } = useCounterfactual();
  
  const handleApply = () => {
    runCounterfactual({ lat, lon, date, deltas, use_surrogate: true });
  };
  
  const handleReset = () => {
    setDeltas({});
  };
  
  return (
    <div className="panel">
      <h2>What-If Analysis</h2>
      
      <div className="slider-group">
        <label>Wind Speed (m/s): {deltas.wind_speed_10m?.toFixed(1) || 'default'}</label>
        <input
          type="range"
          min="0"
          max="30"
          step="0.5"
          value={deltas.wind_speed_10m || 10}
          onChange={(e) => setDeltas({ ...deltas, wind_speed_10m: parseFloat(e.target.value) })}
        />
      </div>
      
      <div className="slider-group">
        <label>Relative Humidity (%): {deltas.rh?.toFixed(1) || 'default'}</label>
        <input
          type="range"
          min="0"
          max="100"
          step="1"
          value={deltas.rh || 50}
          onChange={(e) => setDeltas({ ...deltas, rh: parseFloat(e.target.value) })}
        />
      </div>
      
      <div className="slider-group">
        <label>24h Rain (mm): {deltas.rain_24h?.toFixed(1) || 'default'}</label>
        <input
          type="range"
          min="0"
          max="50"
          step="0.5"
          value={deltas.rain_24h || 0}
          onChange={(e) => setDeltas({ ...deltas, rain_24h: parseFloat(e.target.value) })}
        />
      </div>
      
      <div style={{ marginTop: '1rem' }}>
        <button onClick={handleApply} disabled={loading}>
          {loading ? 'Computing...' : 'Apply'}
        </button>
        <button className="secondary" onClick={handleReset}>
          Reset
        </button>
      </div>
      
      {data && (
        <div style={{ marginTop: '1rem', padding: '0.5rem', backgroundColor: '#444', borderRadius: '4px' }}>
          <p><strong>Probability:</strong> {(data.probability * 100).toFixed(1)}%</p>
          <p><strong>Delta:</strong> {(data.delta * 100).toFixed(1)}%</p>
          <p><strong>Method:</strong> {data.used}</p>
        </div>
      )}
    </div>
  );
};
