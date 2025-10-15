import React, { useState, useEffect } from 'react';
import './XAIPanel.css';

function XAIPanel({ location, onExplain }) {
  const [explanation, setExplanation] = useState(null);
  const [loading, setLoading] = useState(false);
  const [mode, setMode] = useState('shap'); // 'shap' or 'counterfactual'

  useEffect(() => {
    if (location) {
      loadExplanation();
    }
  }, [location, mode]);

  const loadExplanation = async () => {
    if (!location) return;
    
    setLoading(true);
    try {
      const result = await onExplain(location, mode);
      setExplanation(result);
    } catch (error) {
      console.error('Error loading explanation:', error);
    } finally {
      setLoading(false);
    }
  };

  const getBarColor = (direction) => {
    return direction === 'positive' ? '#f44336' : '#4caf50';
  };

  const renderSHAPExplanation = () => {
    if (!explanation || !explanation.feature_importances) return null;

    return (
      <div className="shap-explanation">
        <div className="base-value">
          <span className="label">Base Risk:</span>
          <span className="value">{(explanation.base_value * 100).toFixed(1)}%</span>
        </div>
        <div className="predicted-value">
          <span className="label">Predicted Risk:</span>
          <span className="value">{(explanation.predicted_value * 100).toFixed(1)}%</span>
        </div>
        
        <h4>Feature Contributions</h4>
        <div className="feature-importances">
          {explanation.feature_importances.map((feat, idx) => (
            <div key={idx} className="feature-item">
              <div className="feature-name">{feat.feature}</div>
              <div className="feature-bar-container">
                <div
                  className="feature-bar"
                  style={{
                    width: `${Math.abs(feat.importance) * 100}%`,
                    backgroundColor: getBarColor(feat.direction),
                    marginLeft: feat.direction === 'negative' ? 'auto' : '0'
                  }}
                />
              </div>
              <div className="feature-value">
                {feat.direction === 'positive' ? '+' : '-'}
                {(feat.importance * 100).toFixed(1)}%
              </div>
            </div>
          ))}
        </div>
      </div>
    );
  };

  const renderCounterfactualExplanation = () => {
    if (!explanation || !explanation.suggested_changes) return null;

    return (
      <div className="counterfactual-explanation">
        <div className="current-risk">
          <span className="label">Current Risk:</span>
          <span className="value">{(explanation.original_risk * 100).toFixed(1)}%</span>
        </div>
        <div className="target-risk">
          <span className="label">Target Risk:</span>
          <span className="value">{(explanation.target_risk * 100).toFixed(1)}%</span>
        </div>
        
        <h4>Suggested Changes</h4>
        <div className="suggested-changes">
          {Object.entries(explanation.suggested_changes).map(([feature, change]) => (
            <div key={feature} className="change-item">
              <span className="feature-name">{feature}</span>
              <span className="change-value">{change}</span>
            </div>
          ))}
        </div>
        
        <div className="feasibility">
          <span className="label">Feasibility:</span>
          <div className="feasibility-bar">
            <div
              className="feasibility-fill"
              style={{ width: `${explanation.feasibility * 100}%` }}
            />
          </div>
          <span className="value">{(explanation.feasibility * 100).toFixed(0)}%</span>
        </div>
      </div>
    );
  };

  return (
    <div className="xai-panel">
      <div className="xai-header">
        <h3>Explainable AI</h3>
        <div className="mode-selector">
          <button
            className={mode === 'shap' ? 'active' : ''}
            onClick={() => setMode('shap')}
          >
            SHAP
          </button>
          <button
            className={mode === 'counterfactual' ? 'active' : ''}
            onClick={() => setMode('counterfactual')}
          >
            What-If
          </button>
        </div>
      </div>

      {loading ? (
        <div className="loading">Loading explanation...</div>
      ) : !location ? (
        <div className="no-location">Select a location on the map</div>
      ) : (
        <div className="explanation-content">
          {mode === 'shap' ? renderSHAPExplanation() : renderCounterfactualExplanation()}
        </div>
      )}
    </div>
  );
}

export default XAIPanel;
