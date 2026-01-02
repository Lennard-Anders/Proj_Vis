import React, { useEffect, useState } from "react";
import { runCounterfactual, fetchWildfireRiskLLM, fetchWildfireModels } from "../../api/client";
import { useTriViewState, TriViewState } from "../../state/store";
import { PARAM_LABELS, PARAM_HELP } from "../../ui/labels";

const defaultOverrides = {
  temperature: 24,
  wind_speed_10m: 10,
  rh: 65,
  rain_24h: 1,
};

type LlmInputs = {
  temperature: number;
  wind_speed_kmh: number;
  rh: number;
  rain_24h: number;
  lat?: number;
  lon?: number;
};

const getConfidenceLabel = (probability: number | null) => {
  if (probability === null) return "Unknown";
  if (probability >= 70) return "High";
  if (probability >= 40) return "Medium";
  return "Low";
};

const formatFeatureName = (name: string) => {
  const map: Record<string, string> = {
    rh: "Humidity",
    wind_speed_10m: "Wind speed (10 m)",
    rain_24h: "Rain (last 24h)",
    vpd: "Vapor pressure deficit",
  };

  return map[name] ?? name.replace(/_/g, " ");
};


const WhatIfPanel: React.FC = () => {
  const [overrides, setOverrides] = useState<Record<string, number>>(defaultOverrides);
  const [result, setResult] = useState<string>("");
  const [clickedLocation, setClickedLocation] = useState<{ lat: number; lon: number } | null>(null);
  const [llmText, setLlmText] = useState<string>("");
  const [llmProbability, setLlmProbability] = useState<number | null>(null);
  const [llmInputs, setLlmInputs] = useState<LlmInputs | null>(null);
  const [llmLoading, setLlmLoading] = useState<boolean>(false);
  const [featureContribs, setFeatureContribs] = useState<Array<{ feature: string; weight: number }>>([]);
  const [featureInteractions, setFeatureInteractions] = useState<Array<{ pair: string; weight: number }>>([]);
  const [manualLat, setManualLat] = useState<string>("");
  const [manualLon, setManualLon] = useState<string>("");
  const [availableModels, setAvailableModels] = useState<string[]>([]);
  const [selectedModel, setSelectedModel] = useState<string>("");
  
  const runWhatIf = useTriViewState((state: TriViewState) => state.runWhatIf);
  const runAIRiskPrediction = useTriViewState((state: TriViewState) => state.runAIRiskPrediction);
  const runAIRiskGrid = useTriViewState((state: TriViewState) => state.runAIRiskGrid);
  const mapViewState = useTriViewState((state: TriViewState) => state.mapViewState);
  const setWildfireLlmExplanation = useTriViewState((state: TriViewState) => state.setWildfireLlmExplanation);

  useEffect(() => {
    const loadModels = async () => {
      try {
        const models = await fetchWildfireModels();
        setAvailableModels(models);
        if (models.length > 0) {
          setSelectedModel((current) => current || models[0]);
        }
      } catch (err) {
        console.warn("Unable to load LLM models", err);
      }
    };
    loadModels();
  }, []);

  const handleChange = (feature: string, value: number) => {
    setOverrides((prev: Record<string, number>) => ({ ...prev, [feature]: value }));
  };

  const handleApply = async () => {
    // Use manual coords if provided, else clicked, else map center
    const parsedLat = parseFloat(manualLat);
    const parsedLon = parseFloat(manualLon);
    const hasManualLat = Number.isFinite(parsedLat);
    const hasManualLon = Number.isFinite(parsedLon);
    const lat = hasManualLat ? parsedLat : (clickedLocation?.lat || mapViewState.latitude);
    const lon = hasManualLon ? parsedLon : (clickedLocation?.lon || mapViewState.longitude);
    
    setResult("Running predictions...");
    setLlmText("");
    setLlmProbability(null);
    setLlmInputs(null);
    setFeatureContribs([]);
    setFeatureInteractions([]);
    setLlmLoading(true);
    
    try {
      const snapshot: LlmInputs = {
        temperature: overrides.temperature,
        wind_speed_kmh: overrides.wind_speed_10m * 3.6,
        rh: overrides.rh,
        rain_24h: overrides.rain_24h,
        lat,
        lon,
      };
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
          model: selectedModel,
          lat,
          lon,
        });
        console.log("Wildfire LLM result:", llmData);
        setWildfireLlmExplanation?.(llmData);
        setLlmProbability(llmData.wildfire_probability_percent);
        setLlmText(llmData.explanation);
        setLlmInputs({ ...snapshot, wind_speed_kmh: windSpeedKmh });
        setFeatureContribs(llmData.feature_contributions || []);
        setFeatureInteractions(llmData.feature_interactions || []);
      } catch (err) {
        const message = err instanceof Error ? err.message : "Unknown LLM error";
        console.error("Wildfire LLM request failed:", err);
        setWildfireLlmExplanation?.({
          wildfire_probability_percent: 0,
          explanation: "The AI explanation service returned an invalid response.",
        });
        setLlmProbability(0);
        setLlmText("The AI explanation service returned an invalid response.");
        setLlmInputs({
          temperature: overrides.temperature,
          wind_speed_kmh: overrides.wind_speed_10m * 3.6,
          rh: overrides.rh,
          rain_24h: overrides.rain_24h,
          lat,
          lon,
        });
        setFeatureContribs([]);
        setFeatureInteractions([]);
        setResult("AI prediction complete, but LLM explanation failed.");
      }
      setLlmLoading(false);
      
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
          <span>
            Selected location: {clickedLocation.lat.toFixed(4)}, {clickedLocation.lon.toFixed(4)}
          </span>
          <button 
            onClick={() => setClickedLocation(null)}
            style={{ marginLeft: '8px', fontSize: '0.75rem', padding: '2px 6px' }}
          >
            Clear
          </button>
        </div>
      )}
      
      <div className="what-if__controls">
        <div style={{ marginBottom: 'var(--spacing-md)' }}>
          <label style={{ fontSize: '0.9rem', display: 'block', marginBottom: '4px' }}>
            Prediction Model
          </label>
          <select
            value={selectedModel}
            onChange={(e) => setSelectedModel(e.target.value)}
            style={{ width: '100%', padding: '6px', borderRadius: '4px' }}
          >
            {availableModels.length === 0 && <option value="">Loading models...</option>}
            {availableModels.map((model) => (
              <option key={model} value={model}>
                {model}
              </option>
            ))}
          </select>
        </div>

        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '8px', marginBottom: 'var(--spacing-md)' }}>
          <div>
            <label style={{ fontSize: '0.9rem' }}>
              Latitude
              <input
                type="number"
                step="0.0001"
                placeholder={mapViewState.latitude.toFixed(4)}
                value={manualLat}
                onChange={(e) => setManualLat(e.target.value)}
                style={{ width: '100%', marginTop: '4px' }}
              />
            </label>
          </div>
          <div>
            <label style={{ fontSize: '0.9rem' }}>
              Longitude
              <input
                type="number"
                step="0.0001"
                placeholder={mapViewState.longitude.toFixed(4)}
                value={manualLon}
                onChange={(e) => setManualLon(e.target.value)}
                style={{ width: '100%', marginTop: '4px' }}
              />
            </label>
          </div>
        </div>

        {(Object.entries(overrides) as Array<[string, number]>).map(([feature, value]) => {
          const range = parameterRanges[feature] || { min: 0, max: 100, unit: '' };
          return (
            <label key={feature}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <span style={{ textTransform: "none" }} title={PARAM_HELP[feature] ?? ""}>
  {PARAM_LABELS[feature] ?? feature.replace(/_/g, " ")}
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
          background: 'linear-gradient(135deg, #0ea5e9 0%, #0369a1 100%)',
          fontSize: '1rem',
          fontWeight: 'bold'
        }}
      >
        🔥 Calculate AI Risk Prediction
      </button>

      {(llmLoading || llmText || llmProbability !== null) && (
        <div style={{
          marginTop: 'var(--spacing-md)',
          padding: 'var(--spacing-md)',
          background: 'linear-gradient(135deg, #eef2ff 0%, #e0e7ff 100%)',
          borderRadius: '8px',
          border: '1px solid #6366f1',
          color: 'var(--text-primary)'
        }}>
          <strong>🧠 LLM Assessment</strong>
          {llmLoading && (
            <div style={{ marginTop: '8px', display: 'flex', alignItems: 'center', gap: '8px', color: '#4338ca' }}>
              <div className="spinner" style={{ width: '16px', height: '16px', border: '2px solid #c7d2fe', borderTopColor: '#4338ca', borderRadius: '50%', animation: 'spin 1s linear infinite' }} />
              <span style={{ fontSize: '0.95rem' }}>Generating explanation…</span>
            </div>
          )}

          {!llmLoading && llmProbability !== null && (
            <div style={{ marginTop: '6px', fontSize: '1rem', fontWeight: 700, color: '#4338ca' }}>
              Probability: {llmProbability}%
              <div style={{ fontSize: '0.8rem', fontWeight: 400, marginTop: '2px', opacity: 0.85 }}>
               Confidence: {getConfidenceLabel(llmProbability)}
              </div>
            </div>
          )}
          {!llmLoading && llmText && (
            <div style={{ marginTop: '8px', fontSize: '0.95rem', lineHeight: 1.5 }}>
              {llmText}
            </div>
          )}
          {!llmLoading && llmInputs && (
            <div style={{ marginTop: '10px', fontSize: '0.8rem', color: 'var(--text-secondary)' }}>
              Inputs → Temp: {llmInputs.temperature?.toFixed(1)} °C, Wind: {llmInputs.wind_speed_kmh?.toFixed(1)} km/h, RH: {llmInputs.rh?.toFixed(1)}%, Rain: {llmInputs.rain_24h?.toFixed(1)} mm, Lat: {llmInputs.lat?.toFixed(4)}, Lon: {llmInputs.lon?.toFixed(4)}
            </div>
          )}

          {(featureContribs.length > 0 || featureInteractions.length > 0) && (
            <div style={{ marginTop: '12px', display: 'grid', gap: '8px', fontSize: '0.9rem' }}>
              {featureContribs.length > 0 && (
                <div>
                  <div style={{ fontWeight: 700, color: '#4338ca', marginBottom: '4px' }}>📊 Feature Contributions</div>
                  <div style={{ display: 'grid', gridTemplateColumns: '1fr auto', gap: '4px', background: 'rgba(99,102,241,0.05)', padding: '8px', borderRadius: '6px' }}>
                    {featureContribs.map((item) => (
                      <React.Fragment key={item.feature}>
                        <span style={{ textTransform: 'none' }}>{formatFeatureName(item.feature)}</span>
                        <span style={{ fontVariantNumeric: 'tabular-nums', color: item.weight >= 0 ? '#16a34a' : '#dc2626' }}>
                          {item.weight.toFixed(2)}
                        </span>
                      </React.Fragment>
                    ))}
                  </div>
                </div>
              )}

              {featureInteractions.length > 0 && (
                <div>
                  <div style={{ fontWeight: 700, color: '#4338ca', marginBottom: '4px' }}>🔗 Feature Interactions</div>
                  <div style={{ display: 'grid', gridTemplateColumns: '1fr auto', gap: '4px', background: 'rgba(99,102,241,0.05)', padding: '8px', borderRadius: '6px' }}>
                    {featureInteractions.map((item) => (
                      <React.Fragment key={item.pair}>
                        <span style={{ textTransform: 'none' }}>{item.pair
                     .split(" x ")
                     .map(formatFeatureName)
                     .join(" × ")}
                </span>
                        <span style={{ fontVariantNumeric: 'tabular-nums', color: item.weight >= 0 ? '#16a34a' : '#dc2626' }}>
                          {item.weight.toFixed(2)}
                        </span>
                      </React.Fragment>
                    ))}
                  </div>
                </div>
              )}
            </div>
          )}
        </div>
      )}
      
    </div>
  );
};

export default WhatIfPanel;
