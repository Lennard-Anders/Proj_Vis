import React from "react";
import { useRisk } from "../../state/selectors";

const QualityBoard: React.FC = () => {
  const risk = useRisk();

  return (
    <div className="panel">
      <h2>Quality Board</h2>
      {!risk && <p>No quality metrics yet.</p>}
      {risk && (
        <ul>
          <li>Grid size: {risk.grid.length}</li>
          <li>Avg availability: {average(risk.quality.data_availability).toFixed(2)}</li>
        </ul>
      )}
    </div>
  );
};

function average(values: number[]): number {
  if (!values.length) return 0;
  return values.reduce((sum, value) => sum + value, 0) / values.length;
}

export default QualityBoard;
