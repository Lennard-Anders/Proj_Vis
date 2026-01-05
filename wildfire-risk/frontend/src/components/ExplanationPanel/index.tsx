import React from "react";
import type { ExplainResponse } from "../../api/types";
import { useExplanation } from "../../state/selectors";
import { useTriViewState, TriViewState } from "../../state/store";

const ExplanationPanel: React.FC = () => {
  const explanation = useExplanation();
  const aiRiskPrediction = useTriViewState((state: TriViewState) => state.aiRiskPrediction);
  const aiRiskConfidencePercent = useTriViewState((state: TriViewState) => state.aiRiskConfidencePercent);
  const wildfireLlmExplanation = useTriViewState((state: TriViewState) => state.wildfireLlmExplanation);

  // DEBUG: Log what we have
  console.log('ExplanationPanel render:', { 
    hasAiPrediction: !!aiRiskPrediction, 
    hasExplanation: !!explanation,
    hasWildfireLlmExplanation: !!wildfireLlmExplanation,
    aiRiskConfidencePercent,
    aiRiskPrediction,
    wildfireLlmExplanation,
  });

  // Show AI prediction if available, otherwise fall back to LLM or traditional explanation
  if (aiRiskPrediction) {
    const { probability, risk_level, risk_color, contributing_factors, recommendations, confidence, features } = aiRiskPrediction;
    
    return (
      <div className="panel">
        <h2>🤖 AI Risk Explanation</h2>
        
        {/* Risk Level Display */}
        <div style={{
          padding: 'var(--spacing-md)',
          background: `linear-gradient(135deg, ${risk_color}22 0%, ${risk_color}44 100%)`,
          borderRadius: '8px',
          marginBottom: 'var(--spacing-md)',
          border: `2px solid ${risk_color}`
        }}>
          <div style={{ fontSize: '0.85rem', color: 'var(--text-secondary)' }}>Wildfire Risk Level</div>
          <div style={{ 
            fontSize: '1.8rem', 
            fontWeight: '700', 
            color: risk_color,
            textTransform: 'uppercase',
            marginTop: '4px'
          }}>
            {risk_level}
          </div>
          <div style={{ fontSize: '1.2rem', color: 'var(--text-primary)', marginTop: '8px' }}>
            Probability: <strong>{(probability * 100).toFixed(1)}%</strong>
          </div>
          <div style={{ fontSize: '0.8rem', color: 'var(--text-secondary)', marginTop: '8px' }}>
            Confidence (model): {(confidence * 100).toFixed(0)}%
          </div>

          {typeof aiRiskConfidencePercent === "number" && (
            <div style={{ fontSize: '0.8rem', color: 'var(--text-secondary)', marginTop: '4px' }}>
              Confidence (AI): {aiRiskConfidencePercent.toFixed(0)}%
            </div>
          )}
        </div>

        {/* Environmental Conditions */}
        <div style={{
          background: 'rgba(59, 130, 246, 0.05)',
          padding: 'var(--spacing-md)',
          borderRadius: '6px',
          marginBottom: 'var(--spacing-md)'
        }}>
          <h3 style={{ marginTop: 0, fontSize: '0.95rem' }}>🌡️ Current Conditions</h3>
          <div style={{ 
            display: 'grid', 
            gridTemplateColumns: '1fr 1fr', 
            gap: '8px',
            fontSize: '0.85rem'
          }}>
            <div>Temperature: <strong>{features.temperature.toFixed(1)}°C</strong></div>
            <div>Humidity: <strong>{features.humidity.toFixed(0)}%</strong></div>
            <div>Wind Speed: <strong>{features.wind_speed.toFixed(1)} m/s</strong></div>
            <div>Rainfall: <strong>{features.rainfall.toFixed(1)} mm</strong></div>
          </div>
        </div>

        {/* Risk Indices */}
        <div style={{
          background: 'rgba(234, 88, 12, 0.05)',
          padding: 'var(--spacing-md)',
          borderRadius: '6px',
          marginBottom: 'var(--spacing-md)'
        }}>
          <h3 style={{ marginTop: 0, fontSize: '0.95rem' }}>🔥 Risk Indicators</h3>
          <div style={{ fontSize: '0.85rem' }}>
            <div style={{ marginBottom: '8px' }}>
              Vegetation Dryness: <strong>{features.vegetation_dryness.toFixed(0)}/100</strong>
              <div style={{
                width: '100%',
                height: '6px',
                background: '#e5e7eb',
                borderRadius: '3px',
                marginTop: '4px',
                overflow: 'hidden'
              }}>
                <div style={{
                  width: `${features.vegetation_dryness}%`,
                  height: '100%',
                  background: features.vegetation_dryness > 70 ? '#ef4444' : features.vegetation_dryness > 40 ? '#f59e0b' : '#10b981'
                }}></div>
              </div>
            </div>
            <div>
              Drought Index: <strong>{features.drought_index.toFixed(0)}/100</strong>
              <div style={{
                width: '100%',
                height: '6px',
                background: '#e5e7eb',
                borderRadius: '3px',
                marginTop: '4px',
                overflow: 'hidden'
              }}>
                <div style={{
                  width: `${features.drought_index}%`,
                  height: '100%',
                  background: features.drought_index > 70 ? '#ef4444' : features.drought_index > 40 ? '#f59e0b' : '#10b981'
                }}></div>
              </div>
            </div>
          </div>
        </div>

        {/* Contributing Factors */}
        <h3 style={{ fontSize: '0.95rem' }}>📊 Contributing Factors</h3>
        <ul style={{ paddingLeft: '20px', marginTop: '8px' }}>
          {contributing_factors.map((factor, idx) => (
            <li key={idx} style={{ 
              marginBottom: '6px',
              fontSize: '0.85rem',
              color: factor.impact === 'increases' ? '#dc2626' : '#059669'
            }}>
              <strong>{factor.factor}</strong>
              <div style={{ fontSize: '0.75rem', color: 'var(--text-secondary)' }}>
                {factor.impact === 'increases' ? '↑ Increases' : '↓ Decreases'} risk by {Math.abs(factor.contribution).toFixed(3)}
              </div>
            </li>
          ))}
        </ul>

        {/* Recommendations */}
        <div style={{
          marginTop: 'var(--spacing-md)',
          padding: 'var(--spacing-md)',
          background: risk_level === 'extreme' ? 'linear-gradient(135deg, #fee2e2 0%, #fecaca 100%)' : 
                     risk_level === 'high' ? 'linear-gradient(135deg, #ffedd5 0%, #fed7aa 100%)' :
                     'linear-gradient(135deg, #f0fdf4 0%, #dcfce7 100%)',
          borderRadius: '6px',
          border: `1px solid ${risk_color}`
        }}>
          <h3 style={{ marginTop: 0, fontSize: '0.95rem' }}>💡 Recommendations</h3>
          <ul style={{ paddingLeft: '20px', marginTop: '8px', marginBottom: 0 }}>
            {recommendations.map((rec, idx) => (
              <li key={idx} style={{ marginBottom: '6px', fontSize: '0.85rem' }}>
                {rec}
              </li>
            ))}
          </ul>
        </div>
      </div>
    );
  }

  if (wildfireLlmExplanation) {
    const { wildfire_probability_percent, explanation: llmText } = wildfireLlmExplanation;
    return (
      <div className="panel">
        <h2>🧠 LLM Wildfire Assessment</h2>
        <div style={{
          padding: 'var(--spacing-md)',
          background: 'linear-gradient(135deg, #eff6ff 0%, #dbeafe 100%)',
          borderRadius: '8px',
          marginBottom: 'var(--spacing-md)',
          border: '1px solid #3b82f6'
        }}>
          <div style={{ fontSize: '0.85rem', color: 'var(--text-secondary)' }}>Estimated Wildfire Probability</div>
          <div style={{ fontSize: '1.8rem', fontWeight: 700, color: '#1d4ed8', marginTop: '4px' }}>
            {wildfire_probability_percent}%
          </div>
        </div>
        <p style={{ fontSize: '0.9rem', lineHeight: 1.5 }}>{llmText}</p>
      </div>
    );
  }

  // If no LLM explanation and no classic explanation, render nothing
  return null;
};

export default ExplanationPanel;
