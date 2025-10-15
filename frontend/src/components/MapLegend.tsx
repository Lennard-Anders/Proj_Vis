/** Map legend component stub */
import React from 'react';

export const MapLegend: React.FC = () => (
  <div style={{
    position: 'absolute',
    bottom: '20px',
    right: '20px',
    padding: '1rem',
    backgroundColor: 'rgba(42, 42, 42, 0.9)',
    borderRadius: '8px',
    fontSize: '0.85rem'
  }}>
    <div><strong>Risk Level</strong></div>
    <div style={{ marginTop: '0.5rem' }}>
      <div>🟢 Low (&lt;10%)</div>
      <div>🟡 Medium (10-30%)</div>
      <div>🟠 High (30-60%)</div>
      <div>🔴 Very High (&gt;60%)</div>
    </div>
  </div>
);
