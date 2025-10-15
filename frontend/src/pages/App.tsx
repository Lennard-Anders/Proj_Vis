/**
 * Main App component
 */
import React, { useState } from 'react';
import { MapHeatmap } from '../components/MapHeatmap';
import { MapLegend } from '../components/MapLegend';
import { TimeScrubber } from '../components/TimeScrubber';
import { WhatIfPanel } from '../components/WhatIfPanel';
import { ExplanationPanel } from '../components/ExplanationPanel';
import { QualityBoard } from '../components/QualityBoard';
import { useRisk } from '../hooks/useRisk';
import { useExplain } from '../hooks/useExplain';

const App: React.FC = () => {
  const [date, setDate] = useState('2024-01-15');
  const [bbox] = useState<[number, number, number, number]>([-122, 37, -121, 38]);
  const [selectedLocation, setSelectedLocation] = useState<[number, number] | null>(null);
  
  // Fetch risk data
  const { data: riskData, loading: riskLoading, error: riskError } = useRisk(date, bbox);
  
  // Explanation data
  const { data: explainData, loading: explainLoading, fetchExplanation } = useExplain();
  
  // Handle map click
  const handleMapClick = (lat: number, lon: number) => {
    setSelectedLocation([lat, lon]);
    fetchExplanation(lat, lon, date);
  };
  
  return (
    <div className="app-container">
      <header className="app-header">
        <h1>🔥 Wildfire Risk - Multimodal Modeling (Americas)</h1>
      </header>
      
      <main className="app-main">
        <div className="map-container">
          {riskLoading && (
            <div className="loading">Loading risk data...</div>
          )}
          
          {riskError && (
            <div className="error">Error: {riskError.message}</div>
          )}
          
          {riskData && !riskLoading && (
            <>
              <MapHeatmap
                data={riskData.grid}
                bbox={bbox}
              />
              <MapLegend />
            </>
          )}
          
          {/* TODO: Add click handler */}
          <div
            style={{
              position: 'absolute',
              top: '50%',
              left: '50%',
              transform: 'translate(-50%, -50%)',
              textAlign: 'center',
              pointerEvents: 'none',
              color: '#666',
              fontSize: '0.9rem'
            }}
          >
            Click map to get explanation (TODO)
          </div>
        </div>
        
        <aside className="sidebar">
          <div className="panel">
            <h2>Controls</h2>
            <TimeScrubber
              initialDate={date}
              onChange={setDate}
            />
          </div>
          
          {selectedLocation && (
            <WhatIfPanel
              lat={selectedLocation[0]}
              lon={selectedLocation[1]}
              date={date}
            />
          )}
          
          <ExplanationPanel
            data={explainData}
            loading={explainLoading}
          />
          
          {riskData && (
            <QualityBoard quality={riskData.quality} />
          )}
        </aside>
      </main>
    </div>
  );
};

export default App;
