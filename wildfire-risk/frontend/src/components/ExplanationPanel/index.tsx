import React from "react";
import type { ExplainResponse } from "../../api/types";
import { useExplanation } from "../../state/selectors";

const ExplanationPanel: React.FC = () => {
  const explanation = useExplanation();

  if (!explanation) {
    return (
      <div className="panel">
        <h2>Explanation</h2>
        <p>No explanation available.</p>
      </div>
    );
  }

  return (
    <div className="panel">
      <h2>AI Explanation</h2>
      <div style={{
        padding: 'var(--spacing-md)',
        background: 'linear-gradient(135deg, #fef3c7 0%, #fde68a 100%)',
        borderRadius: '8px',
        marginBottom: 'var(--spacing-md)',
        border: '2px solid var(--accent-yellow)'
      }}>
        <div style={{ fontSize: '0.85rem', color: 'var(--text-secondary)' }}>Predicted Risk Probability</div>
        <div style={{ fontSize: '2rem', fontWeight: '700', color: 'var(--accent-orange)' }}>
          {(explanation.probability * 100).toFixed(1)}%
        </div>
      </div>
      <h3>📊 Feature Contributions</h3>
      <ul>
  {explanation.local_shap.map((item: ExplainResponse["local_shap"][number]) => (
          <li key={item.feature}>
            {item.feature}: {item.contribution.toFixed(2)}
          </li>
        ))}
      </ul>
      <h3>🔗 Feature Interactions</h3>
      <ul>
  {explanation.interactions.map((interaction: ExplainResponse["interactions"][number]) => (
          <li key={interaction.pair.join("-")}>
            {interaction.pair.join(" × ")}: {interaction.value.toFixed(2)}
          </li>
        ))}
      </ul>
      <div style={{
        marginTop: 'var(--spacing-md)',
        padding: 'var(--spacing-sm) var(--spacing-md)',
        background: explanation.ood ? 'linear-gradient(135deg, #fee2e2 0%, #fecaca 100%)' : 'linear-gradient(135deg, #f0fdf4 0%, #dcfce7 100%)',
        borderRadius: '6px',
        border: `1px solid ${explanation.ood ? 'var(--accent-red)' : 'var(--success-green)'}`,
        display: 'inline-block'
      }}>
        <strong>Data Quality:</strong> {explanation.ood ? "⚠️ Out of Distribution" : "✅ Within Distribution"}
      </div>
    </div>
  );
};

export default ExplanationPanel;
