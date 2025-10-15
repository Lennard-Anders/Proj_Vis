import React, { useState } from 'react';
import './WhatIfPanel.css';

function WhatIfPanel({ currentConditions, onRunScenario }) {
  const [scenarios, setScenarios] = useState({
    temperature: currentConditions?.temperature || 25,
    humidity: currentConditions?.humidity || 50,
    wind_speed: currentConditions?.wind_speed || 10,
    precipitation: currentConditions?.precipitation || 0
  });

  const [results, setResults] = useState(null);
  const [loading, setLoading] = useState(false);

  const handleInputChange = (field, value) => {
    setScenarios({
      ...scenarios,
      [field]: parseFloat(value)
    });
  };

  const runScenario = async () => {
    setLoading(true);
    try {
      const result = await onRunScenario(scenarios);
      setResults(result);
    } catch (error) {
      console.error('Error running scenario:', error);
    } finally {
      setLoading(false);
    }
  };

  const resetToBaseline = () => {
    setScenarios({
      temperature: currentConditions?.temperature || 25,
      humidity: currentConditions?.humidity || 50,
      wind_speed: currentConditions?.wind_speed || 10,
      precipitation: currentConditions?.precipitation || 0
    });
    setResults(null);
  };

  const getRiskColor = (score) => {
    if (score < 0.3) return '#4caf50'; // green
    if (score < 0.6) return '#ffc107'; // yellow
    if (score < 0.8) return '#ff9800'; // orange
    return '#f44336'; // red
  };

  return (
    <div className="what-if-panel">
      <h3>What-If Analysis</h3>
      
      <div className="scenario-inputs">
        <div className="input-group">
          <label htmlFor="temperature">Temperature (°C)</label>
          <input
            id="temperature"
            type="range"
            min="0"
            max="50"
            step="0.5"
            value={scenarios.temperature}
            onChange={(e) => handleInputChange('temperature', e.target.value)}
          />
          <span className="value">{scenarios.temperature.toFixed(1)}°C</span>
        </div>

        <div className="input-group">
          <label htmlFor="humidity">Humidity (%)</label>
          <input
            id="humidity"
            type="range"
            min="0"
            max="100"
            step="1"
            value={scenarios.humidity}
            onChange={(e) => handleInputChange('humidity', e.target.value)}
          />
          <span className="value">{scenarios.humidity.toFixed(0)}%</span>
        </div>

        <div className="input-group">
          <label htmlFor="wind_speed">Wind Speed (m/s)</label>
          <input
            id="wind_speed"
            type="range"
            min="0"
            max="40"
            step="0.5"
            value={scenarios.wind_speed}
            onChange={(e) => handleInputChange('wind_speed', e.target.value)}
          />
          <span className="value">{scenarios.wind_speed.toFixed(1)} m/s</span>
        </div>

        <div className="input-group">
          <label htmlFor="precipitation">Precipitation (mm)</label>
          <input
            id="precipitation"
            type="range"
            min="0"
            max="50"
            step="0.5"
            value={scenarios.precipitation}
            onChange={(e) => handleInputChange('precipitation', e.target.value)}
          />
          <span className="value">{scenarios.precipitation.toFixed(1)} mm</span>
        </div>
      </div>

      <div className="action-buttons">
        <button onClick={runScenario} disabled={loading} className="run-button">
          {loading ? 'Running...' : 'Run Scenario'}
        </button>
        <button onClick={resetToBaseline} className="reset-button">
          Reset to Baseline
        </button>
      </div>

      {results && (
        <div className="results-panel">
          <h4>Scenario Results</h4>
          <div className="result-item">
            <span className="label">Predicted Risk:</span>
            <span className="value" style={{ color: getRiskColor(results.risk_score) }}>
              {(results.risk_score * 100).toFixed(1)}%
            </span>
          </div>
          <div className="result-item">
            <span className="label">Risk Level:</span>
            <span className="value risk-level">{results.risk_level}</span>
          </div>
          <div className="result-item">
            <span className="label">Confidence:</span>
            <span className="value">{(results.confidence * 100).toFixed(0)}%</span>
          </div>
          {currentConditions && (
            <div className="comparison">
              <span className="label">Change from baseline:</span>
              <span className={`value ${results.risk_score > 0.5 ? 'increase' : 'decrease'}`}>
                {results.risk_score > 0.5 ? '↑' : '↓'} 
                {Math.abs((results.risk_score - 0.5) * 100).toFixed(1)}%
              </span>
            </div>
          )}
        </div>
      )}
    </div>
  );
}

export default WhatIfPanel;
