import React from "react";
import type { ExplainResponse } from "../api/types";
import { useExplanation } from "../state/selectors";

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
      <h2>Explanation</h2>
      <p>
        Probability: <strong>{(explanation.probability * 100).toFixed(1)}%</strong>
      </p>
      <h3>Local Contributions</h3>
      <ul>
  {explanation.local_shap.map((item: ExplainResponse["local_shap"][number]) => (
          <li key={item.feature}>
            {item.feature}: {item.contribution.toFixed(2)}
          </li>
        ))}
      </ul>
      <h3>Interactions</h3>
      <ul>
  {explanation.interactions.map((interaction: ExplainResponse["interactions"][number]) => (
          <li key={interaction.pair.join("-")}>
            {interaction.pair.join(" × ")}: {interaction.value.toFixed(2)}
          </li>
        ))}
      </ul>
      <p>OOD: {explanation.ood ? "Yes" : "No"}</p>
    </div>
  );
};

export default ExplanationPanel;
