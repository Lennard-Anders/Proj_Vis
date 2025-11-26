import React from "react";
import { useRisk } from "../../state/selectors";

const QualityBoard: React.FC = () => {
  const risk = useRisk();

  return (
    <div className="panel">
      <h2>📈 Data Quality</h2>
      {!risk && <p>No quality metrics yet.</p>}
      {risk && (
        <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--spacing-sm)' }}>
          <div style={{
            padding: 'var(--spacing-md)',
            background: 'linear-gradient(135deg, #dbeafe 0%, #bfdbfe 100%)',
            borderRadius: '8px',
            border: '1px solid var(--info-blue)'
          }}>
            <div style={{ fontSize: '0.8rem', color: 'var(--text-secondary)' }}>Grid Points</div>
            <div style={{ fontSize: '1.5rem', fontWeight: '700', color: 'var(--info-blue)' }}>
              {risk.grid.length.toLocaleString()}
            </div>
          </div>
          <div style={{
            padding: 'var(--spacing-md)',
            background: 'linear-gradient(135deg, #f0fdf4 0%, #dcfce7 100%)',
            borderRadius: '8px',
            border: '1px solid var(--success-green)'
          }}>
            <div style={{ fontSize: '0.8rem', color: 'var(--text-secondary)' }}>Average Data Availability</div>
            <div style={{ fontSize: '1.5rem', fontWeight: '700', color: 'var(--success-green)' }}>
              {(average(risk.quality.data_availability) * 100).toFixed(1)}%
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

function average(values: number[]): number {
  if (!values.length) return 0;
  return values.reduce((sum, value) => sum + value, 0) / values.length;
}

export default QualityBoard;
