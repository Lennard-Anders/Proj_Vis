/** Data quality dashboard stub */
import React from 'react';

export const QualityBoard: React.FC<{ quality: any }> = ({ quality }) => (
  <div className="panel">
    <h2>Data Quality</h2>
    <p style={{ fontSize: '0.85rem' }}>Availability: {((quality?.data_availability?.[0] || 0.95) * 100).toFixed(0)}%</p>
    <p style={{ fontSize: '0.85rem' }}>DQF: Good</p>
  </div>
);
