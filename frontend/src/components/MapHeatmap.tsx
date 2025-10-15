/**
 * Map heatmap component - WebGL grid rendering stub
 */
import React from 'react';

interface MapHeatmapProps {
  data: any[];
  bbox: [number, number, number, number];
}

export const MapHeatmap: React.FC<MapHeatmapProps> = ({ data, bbox }) => {
  return (
    <div style={{
      width: '100%',
      height: '100%',
      background: 'linear-gradient(to bottom right, #1a1a1a, #2a2a2a)',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
      color: '#666'
    }}>
      <div style={{ textAlign: 'center' }}>
        <p>Map Heatmap Component</p>
        <p style={{ fontSize: '0.8rem', marginTop: '0.5rem' }}>
          {data.length} tiles | BBox: {bbox.map(v => v.toFixed(2)).join(', ')}
        </p>
        <p style={{ fontSize: '0.7rem', marginTop: '0.5rem', color: '#555' }}>
          TODO: Implement deck.gl WebGL grid layer
        </p>
      </div>
    </div>
  );
};
