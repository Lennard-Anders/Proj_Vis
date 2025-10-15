/**
 * Explanation panel with waterfall and interaction heatmap
 */
import React from 'react';
import type { ExplainResponse } from '../api/types';

interface ExplanationPanelProps {
  data: ExplainResponse | null;
  loading: boolean;
}

export const ExplanationPanel: React.FC<ExplanationPanelProps> = ({ data, loading }) => {
  if (loading) {
    return <div className="panel"><div className="loading">Loading explanation...</div></div>;
  }
  
  if (!data) {
    return <div className="panel"><p>Click on map to get explanation</p></div>;
  }
  
  return (
    <div className="panel">
      <h2>Explanation</h2>
      
      <div style={{ marginBottom: '1rem' }}>
        <p><strong>Probability:</strong> {(data.probability * 100).toFixed(1)}%</p>
        <p><strong>CI:</strong> [{(data.ci[0] * 100).toFixed(1)}%, {(data.ci[1] * 100).toFixed(1)}%]</p>
        <p><strong>Reliability:</strong> {(data.reliability_bin.observed * 100).toFixed(1)}%</p>
        {data.ood && <span style={{ color: '#e74c3c' }}>⚠️ Out-of-distribution</span>}
      </div>
      
      <h3 style={{ fontSize: '1rem', marginBottom: '0.5rem' }}>Feature Contributions</h3>
      {data.local_shap.map((contrib, i) => (
        <div key={i} style={{ marginBottom: '0.5rem', fontSize: '0.85rem' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between' }}>
            <span>{contrib.feature}</span>
            <span style={{ color: contrib.contribution > 0 ? '#e74c3c' : '#3498db' }}>
              {contrib.contribution > 0 ? '+' : ''}{(contrib.contribution * 100).toFixed(1)}%
            </span>
          </div>
          <div style={{ fontSize: '0.75rem', color: '#999' }}>
            {contrib.value.toFixed(2)} {contrib.unit}
          </div>
        </div>
      ))}
      
      {data.interactions.length > 0 && (
        <>
          <h3 style={{ fontSize: '1rem', marginTop: '1rem', marginBottom: '0.5rem' }}>Interactions</h3>
          {data.interactions.map((inter, i) => (
            <div key={i} style={{ fontSize: '0.85rem', marginBottom: '0.25rem' }}>
              {inter.pair[0]} × {inter.pair[1]}: {(inter.value * 100).toFixed(1)}%
            </div>
          ))}
        </>
      )}
    </div>
  );
};
