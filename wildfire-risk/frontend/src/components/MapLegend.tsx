import React from "react";

const MapLegend: React.FC = () => (
  <div className="map-legend">
    <h3>Legend</h3>
    <ul>
      <li>
        <span className="legend-swatch legend-low" /> Low risk
      </li>
      <li>
        <span className="legend-swatch legend-medium" /> Moderate risk
      </li>
      <li>
        <span className="legend-swatch legend-high" /> Elevated risk
      </li>
    </ul>
  </div>
);

export default MapLegend;
