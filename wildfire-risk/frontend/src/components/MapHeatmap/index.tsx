import React from "react";
import type { RiskResponse, RiskGridCell } from "../../api/types";

interface Props {
  data?: RiskResponse;
}

const MapHeatmap: React.FC<Props> = ({ data }: Props) => {
  if (!data) {
    return <p>No risk data available yet.</p>;
  }
  return (
    <div className="map-heatmap">
      <strong>Heatmap Preview</strong>
      <ul>
  {data.grid.slice(0, 5).map((cell: RiskGridCell) => (
          <li key={`${cell.lat}-${cell.lon}`}>
            {cell.lat.toFixed(2)},{cell.lon.toFixed(2)} → {(cell.prob * 100).toFixed(1)}%
          </li>
        ))}
      </ul>
    </div>
  );
};

export default MapHeatmap;
