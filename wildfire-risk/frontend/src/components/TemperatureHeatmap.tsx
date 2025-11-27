import React, { useEffect, useState } from 'react';
import DeckGL from '@deck.gl/react';
import { HeatmapLayer } from '@deck.gl/aggregation-layers';
import { useTriViewState, TriViewState } from '../state/store';

interface TemperaturePoint {
  latitude: number;
  longitude: number;
  temperature: number;
  uncertainty: number;
  city: string;
  country: string;
}

const TemperatureHeatmap: React.FC = () => {
  const [temperatureData, setTemperatureData] = useState<TemperaturePoint[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  
  const selectedDate = useTriViewState((state: TriViewState) => state.selectedDate);
  const bbox = useTriViewState((state: TriViewState) => state.bbox);

  useEffect(() => {
    loadTemperatureData();
  }, [selectedDate, bbox]);

  const loadTemperatureData = async () => {
    setLoading(true);
    setError(null);
    
    try {
      const response = await fetch('http://localhost:8000/api/temperature/heatmap', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          date: selectedDate,
          region: 'california', // Can be made dynamic
          bbox: bbox ? {
            min_lat: bbox.min_lat,
            max_lat: bbox.max_lat,
            min_lon: bbox.min_lon,
            max_lon: bbox.max_lon
          } : null
        })
      });
      
      if (!response.ok) {
        throw new Error(`Failed to fetch temperature data: ${response.statusText}`);
      }
      
      const result = await response.json();
      setTemperatureData(result.data || []);
      console.log(`Loaded ${result.count} temperature points`);
    } catch (err) {
      console.error('Error loading temperature data:', err);
      setError(err instanceof Error ? err.message : 'Failed to load temperature data');
    } finally {
      setLoading(false);
    }
  };

  const layers = [
    new HeatmapLayer({
      id: 'temperature-heatmap',
      data: temperatureData,
      getPosition: (d: TemperaturePoint) => [d.longitude, d.latitude],
      getWeight: (d: TemperaturePoint) => Math.max(0, d.temperature + 50), // Normalize temp to positive values
      radiusPixels: 60,
      intensity: 1,
      threshold: 0.05,
      colorRange: [
        [0, 0, 255, 100],      // Cold: Blue
        [0, 255, 255, 150],    // Cool: Cyan
        [0, 255, 0, 180],      // Mild: Green
        [255, 255, 0, 200],    // Warm: Yellow
        [255, 165, 0, 230],    // Hot: Orange
        [255, 0, 0, 255]       // Very Hot: Red
      ]
    })
  ];

  const initialViewState = {
    longitude: bbox?.min_lon || -120,
    latitude: bbox?.min_lat || 36,
    zoom: 6,
    pitch: 0,
    bearing: 0
  };

  return (
    <div style={{ position: 'relative', height: '400px', width: '100%', marginTop: '10px', background: '#1a1a2e' }}>
      <div style={{
        position: 'absolute',
        top: 10,
        left: 10,
        background: 'rgba(0, 0, 0, 0.8)',
        color: 'white',
        padding: '8px 12px',
        borderRadius: '4px',
        zIndex: 1,
        fontSize: '12px'
      }}>
        <strong>Temperature Heatmap</strong>
        <div style={{ marginTop: '4px', fontSize: '11px' }}>
          {loading && '🔄 Loading...'}
          {error && `❌ ${error}`}
          {!loading && !error && `${temperatureData.length} data points`}
        </div>
        <div style={{ marginTop: '4px', fontSize: '10px', color: '#aaa' }}>
          Date: {selectedDate}
        </div>
      </div>
      
      <DeckGL
        initialViewState={initialViewState as any}
        controller={true}
        layers={layers}
      />
      
      {/* Legend */}
      <div style={{
        position: 'absolute',
        bottom: 10,
        right: 10,
        background: 'rgba(0, 0, 0, 0.8)',
        color: 'white',
        padding: '8px 12px',
        borderRadius: '4px',
        zIndex: 1,
        fontSize: '11px'
      }}>
        <div><span style={{color: '#0000FF'}}>■</span> Cold (&lt;0°C)</div>
        <div><span style={{color: '#00FFFF'}}>■</span> Cool (0-10°C)</div>
        <div><span style={{color: '#00FF00'}}>■</span> Mild (10-20°C)</div>
        <div><span style={{color: '#FFFF00'}}>■</span> Warm (20-30°C)</div>
        <div><span style={{color: '#FFA500'}}>■</span> Hot (30-40°C)</div>
        <div><span style={{color: '#FF0000'}}>■</span> Very Hot (&gt;40°C)</div>
      </div>
    </div>
  );
};

export default TemperatureHeatmap;
