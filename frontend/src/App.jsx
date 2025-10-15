import { useState, useCallback } from 'react'
import MapComponent from './components/MapComponent'
import TriViewTimeline from './components/TriViewTimeline'
import WhatIfPanel from './components/WhatIfPanel'
import XAIPanel from './components/XAIPanel'
import './App.css'

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

function App() {
  const [selectedLocation, setSelectedLocation] = useState(null);
  const [riskData, setRiskData] = useState([]);
  const [frames, setFrames] = useState(null);
  const [currentFrame, setCurrentFrame] = useState(0);

  const handleLocationSelect = useCallback((location) => {
    setSelectedLocation(location);
    console.log('Selected location:', location);
  }, []);

  const handleRunScenario = useCallback(async (scenarios) => {
    if (!selectedLocation) {
      return { risk_score: 0.5, risk_level: 'moderate', confidence: 0.8 };
    }

    try {
      const response = await fetch(`${API_BASE_URL}/risk/`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          latitude: selectedLocation.latitude,
          longitude: selectedLocation.longitude,
          temperature: scenarios.temperature,
          humidity: scenarios.humidity,
          wind_speed: scenarios.wind_speed,
          precipitation: scenarios.precipitation,
          vegetation_index: 0.6,
          fuel_moisture: 10.0
        })
      });
      const data = await response.json();
      return data;
    } catch (error) {
      console.error('API error:', error);
      return { risk_score: 0.5, risk_level: 'moderate', confidence: 0.8 };
    }
  }, [selectedLocation]);

  const handleExplain = useCallback(async (location, mode) => {
    if (mode === 'shap') {
      try {
        const response = await fetch(`${API_BASE_URL}/explain/`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            latitude: location.latitude,
            longitude: location.longitude,
            temperature: 30,
            humidity: 30,
            wind_speed: 15,
            precipitation: 0,
            vegetation_index: 0.6,
            fuel_moisture: 8.0
          })
        });
        return await response.json();
      } catch (error) {
        console.error('API error:', error);
        return null;
      }
    } else {
      try {
        const response = await fetch(`${API_BASE_URL}/risk/counterfactual`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            latitude: location.latitude,
            longitude: location.longitude,
            temperature: 30,
            humidity: 30,
            wind_speed: 15,
            precipitation: 0,
            vegetation_index: 0.6,
            fuel_moisture: 8.0,
            target_risk: 0.3
          })
        });
        return await response.json();
      } catch (error) {
        console.error('API error:', error);
        return null;
      }
    }
  }, []);

  return (
    <div className="app">
      <header className="app-header">
        <h1>🔥 Wildfire Risk Visualization</h1>
        <p>Interactive wildfire risk prediction and explainability platform</p>
      </header>

      <div className="app-layout">
        <div className="main-content">
          <div className="map-container">
            <MapComponent
              riskData={riskData}
              selectedLocation={selectedLocation}
              onLocationSelect={handleLocationSelect}
            />
          </div>
          <TriViewTimeline
            frames={frames}
            currentFrame={currentFrame}
            onFrameSelect={setCurrentFrame}
          />
        </div>

        <div className="sidebar">
          <WhatIfPanel
            currentConditions={selectedLocation}
            onRunScenario={handleRunScenario}
          />
          <XAIPanel
            location={selectedLocation}
            onExplain={handleExplain}
          />
        </div>
      </div>
    </div>
  )
}

export default App
