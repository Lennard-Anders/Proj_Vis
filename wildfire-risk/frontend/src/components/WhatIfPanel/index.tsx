import React, { useState } from "react";
import { runCounterfactual, fetchWildfireRiskLLM } from "../../api/client";
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
  const [llmText, setLlmText] = useState<string>("");
  const [llmProbability, setLlmProbability] = useState<number | null>(null);
  const [llmInputs, setLlmInputs] = useState<Record<string, number> | null>(null);
  
  const runWhatIf = useTriViewState((state: TriViewState) => state.runWhatIf);
  const runAIRiskPrediction = useTriViewState((state: TriViewState) => state.runAIRiskPrediction);
  const runAIRiskGrid = useTriViewState((state: TriViewState) => state.runAIRiskGrid);
  const mapViewState = useTriViewState((state: TriViewState) => state.mapViewState);
  const setWildfireLlmExplanation = useTriViewState((state: TriViewState) => state.setWildfireLlmExplanation);

  const handleChange = (feature: string, value: number) => {
    setOverrides((prev: Record<string, number>) => ({ ...prev, [feature]: value }));
  };

  const handleApply = async () => {
    // Use clicked location or center of map
    const lat = clickedLocation?.lat || mapViewState.latitude;
    const lon = clickedLocation?.lon || mapViewState.longitude;
    
    setResult("Running predictions...");
    setLlmText("");
    setLlmProbability(null);
    setLlmInputs(null);
    
    try {
      const snapshot = { ...overrides };
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

      // Call LLM-based wildfire risk estimation (UI-only for now)
      try {
        const windSpeedKmh = overrides.wind_speed_10m * 3.6; // convert m/s to km/h
        const llmData = await fetchWildfireRiskLLM({
          temperature_c: snapshot.temperature,
          wind_speed_kmh: windSpeedKmh,
          relative_humidity_percent: snapshot.rh,
          rain_last_24h_mm: snapshot.rain_24h,
        });
        console.log("Wildfire LLM result:", llmData);
        setWildfireLlmExplanation?.(llmData);
        setLlmProbability(llmData.wildfire_probability_percent);
        setLlmText(llmData.explanation);
        setLlmInputs({ ...snapshot, wind_speed_kmh: windSpeedKmh });
      } catch (err) {
        const message = err instanceof Error ? err.message : "Unknown LLM error";
        console.error("Wildfire LLM request failed:", err);
        setWildfireLlmExplanation?.({
          wildfire_probability_percent: 0,
          explanation: "The AI explanation service returned an invalid response.",
        });
        setLlmProbability(0);
        setLlmText("The AI explanation service returned an invalid response.");
        setLlmInputs({ ...overrides, wind_speed_kmh: overrides.wind_speed_10m * 3.6 });
        setResult("AI prediction complete, but LLM explanation failed.");
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

      {(llmText || llmProbability !== null) && (
        <div style={{
          marginTop: 'var(--spacing-md)',
          padding: 'var(--spacing-md)',
          background: 'linear-gradient(135deg, #eef2ff 0%, #e0e7ff 100%)',
          borderRadius: '8px',
          border: '1px solid #6366f1',
          color: 'var(--text-primary)'
        }}>
          <strong>🧠 LLM Assessment</strong>
          {llmProbability !== null && (
            <div style={{ marginTop: '6px', fontSize: '1rem', fontWeight: 700, color: '#4338ca' }}>
              Probability: {llmProbability}%
            </div>
          )}
          {llmText && (
            <div style={{ marginTop: '8px', fontSize: '0.95rem', lineHeight: 1.5 }}>
              {llmText}
            </div>
          )}
          {llmInputs && (
            <div style={{ marginTop: '10px', fontSize: '0.8rem', color: 'var(--text-secondary)' }}>
              Inputs → Temp: {llmInputs.temperature?.toFixed(1)} °C, Wind: {llmInputs.wind_speed_kmh?.toFixed(1)} km/h, RH: {llmInputs.rh?.toFixed(1)}%, Rain: {llmInputs.rain_24h?.toFixed(1)} mm
            </div>
          )}
        </div>
      )}
      
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
