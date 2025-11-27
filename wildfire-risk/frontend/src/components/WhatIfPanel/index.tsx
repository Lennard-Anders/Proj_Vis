import React, { useState } from "react";
import { runCounterfactual } from "../../api/client";
import { useTriViewState, TriViewState } from "../../state/store";

const defaultOverrides = {
  temperature: 30,
  wind_speed_10m: 10,
  rh: 25,
  rain_24h: 1,
};

const WhatIfPanel: React.FC = () => {
  const [overrides, setOverrides] = useState<Record<string, number>>(defaultOverrides);
  const [result, setResult] = useState<string>("");
  const [clickedLocation, setClickedLocation] = useState<{ lat: number; lon: number } | null>(null);
  
  const runWhatIf = useTriViewState((state: TriViewState) => state.runWhatIf);
  const runAIRiskPrediction = useTriViewState((state: TriViewState) => state.runAIRiskPrediction);
  const runAIRiskGrid = useTriViewState((state: TriViewState) => state.runAIRiskGrid);
  const mapViewState = useTriViewState((state: TriViewState) => state.mapViewState);

  const handleChange = (feature: string, value: number) => {
    setOverrides((prev: Record<string, number>) => ({ ...prev, [feature]: value }));
  };

  const handleApply = async () => {
    // Use clicked location or center of map
    const lat = clickedLocation?.lat || mapViewState.latitude;
    const lon = clickedLocation?.lon || mapViewState.longitude;
    
    setResult("Running predictions...");
    
    try {
      // Run both old and new prediction systems
      await runWhatIf(overrides);
      
      // Run AI risk prediction for single point
      if (runAIRiskPrediction) {
        await runAIRiskPrediction({
          lat,
          lon,
          temperature: overrides.temperature,
          wind_speed_10m: overrides.wind_speed_10m,
          rh: overrides.rh,
          rain_24h: overrides.rain_24h
        });
      }
      
      // Run AI risk grid prediction
      if (runAIRiskGrid) {
        await runAIRiskGrid({
          lat,
          lon,
          temperature: overrides.temperature,
          wind_speed_10m: overrides.wind_speed_10m,
          rh: overrides.rh,
          rain_24h: overrides.rain_24h,
          grid_size_deg: 2.0
        });
      }
      
      try {
        await runCounterfactual(overrides);
      } catch (err) {
        console.warn('Counterfactual failed:', err);
      }
      
      setResult(
        `AI prediction complete! Risk probability calculated for location (${lat.toFixed(2)}, ${lon.toFixed(2)})`
      );
    } catch (error) {
      console.error('Prediction failed:', error);
      setResult(`Error: ${error instanceof Error ? error.message : 'Prediction failed'}`);
    }
  };

  const parameterRanges: Record<string, { min: number; max: number; unit: string }> = {
    temperature: { min: -10, max: 50, unit: '°C' },
    wind_speed_10m: { min: 0, max: 30, unit: 'm/s' },
    rh: { min: 0, max: 100, unit: '%' },
    rain_24h: { min: 0, max: 50, unit: 'mm' },
  };

  return (
    <div className="panel">
      <h2>🌡️ What-If Risk Analysis</h2>
      <p style={{ fontSize: '0.9rem', color: 'var(--text-secondary)', marginBottom: 'var(--spacing-md)' }}>
        Adjust weather parameters to predict wildfire risk using AI
      </p>
      
      {clickedLocation && (
        <div style={{
          marginBottom: 'var(--spacing-md)',
          padding: '8px',
          background: 'rgba(59, 130, 246, 0.1)',
          borderRadius: '4px',
          fontSize: '0.85rem'
        }}>
          📍 Location: {clickedLocation.lat.toFixed(3)}°, {clickedLocation.lon.toFixed(3)}°
          <button 
            onClick={() => setClickedLocation(null)}
            style={{ marginLeft: '8px', fontSize: '0.75rem', padding: '2px 6px' }}
          >
            Clear
          </button>
        </div>
      )}
      
      <div className="what-if__controls">
        {(Object.entries(overrides) as Array<[string, number]>).map(([feature, value]) => {
          const range = parameterRanges[feature] || { min: 0, max: 100, unit: '' };
          return (
            <label key={feature}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <span style={{ textTransform: 'capitalize' }}>
                  {feature.replace(/_/g, ' ')}
                </span>
                <span style={{ fontWeight: 'bold', color: 'var(--primary)' }}>
                  {value.toFixed(1)} {range.unit}
                </span>
              </div>
              <input
                type="range"
                min={range.min}
                max={range.max}
                step={feature === 'rain_24h' ? 0.5 : 0.1}
                value={value}
                onChange={(event: React.ChangeEvent<HTMLInputElement>) =>
                  handleChange(feature, Number(event.target.value))
                }
              />
            </label>
          );
        })}
      </div>
      
      <button 
        type="button" 
        onClick={handleApply}
        style={{
          width: '100%',
          background: 'linear-gradient(135deg, #f97316 0%, #ea580c 100%)',
          fontSize: '1rem',
          fontWeight: 'bold'
        }}
      >
        🔥 Calculate AI Risk Prediction
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
          <div style={{ marginTop: '8px', fontSize: '0.85rem', color: '#059669' }}>
            View detailed analysis in the <strong>AI Explanation</strong> panel →
          </div>
        </div>
      )}
    </div>
  );
};

export default WhatIfPanel;
