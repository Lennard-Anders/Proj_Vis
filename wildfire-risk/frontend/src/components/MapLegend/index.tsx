import React from "react";

const MapLegend: React.FC = () => {
  return (
    <div className="map-legend" aria-label="Map legend and explanations">
      <h3 style={{ marginBottom: 6 }}>Legend</h3>
      <p style={{ marginTop: 0, fontSize: "0.85rem", opacity: 0.85, lineHeight: 1.35 }}>
        The map uses color to encode estimated wildfire risk. Use the legend below to interpret the scenario view.
      </p>

      <div style={{ marginTop: 10 }}>
        <div style={{ fontWeight: 700, marginBottom: 6 }}>Risk levels (color)</div>
        <ul style={{ margin: 0, paddingLeft: 18 }}>
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

      <div style={{ marginTop: 14 }}>
        <div style={{ fontWeight: 700, marginBottom: 6 }}>Scenario Risk Map (“four boxes”)</div>
        <p style={{ marginTop: 0, fontSize: "0.85rem", opacity: 0.85, lineHeight: 1.35 }}>
          The scenario view groups outcomes into four categories based on how conditions change compared to the baseline.
        </p>

        <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 8 }}>
          <div style={{ padding: 8, borderRadius: 6, border: "1px solid rgba(0,0,0,0.12)" }}>
            <div style={{ fontWeight: 700, marginBottom: 4 }}>Lower risk</div>
            <div style={{ fontSize: "0.85rem", opacity: 0.85 }}>
              Conditions reduce estimated risk compared to the baseline.
            </div>
          </div>

          <div style={{ padding: 8, borderRadius: 6, border: "1px solid rgba(0,0,0,0.12)" }}>
            <div style={{ fontWeight: 700, marginBottom: 4 }}>Higher risk</div>
            <div style={{ fontSize: "0.85rem", opacity: 0.85 }}>
              Conditions increase estimated risk compared to the baseline.
            </div>
          </div>

          <div style={{ padding: 8, borderRadius: 6, border: "1px solid rgba(0,0,0,0.12)" }}>
            <div style={{ fontWeight: 700, marginBottom: 4 }}>Unchanged / neutral</div>
            <div style={{ fontSize: "0.85rem", opacity: 0.85 }}>
              Small or no meaningful change compared to the baseline.
            </div>
          </div>

          <div style={{ padding: 8, borderRadius: 6, border: "1px solid rgba(0,0,0,0.12)" }}>
            <div style={{ fontWeight: 700, marginBottom: 4 }}>Uncertain / missing data</div>
            <div style={{ fontSize: "0.85rem", opacity: 0.85 }}>
              The system cannot confidently classify the outcome (e.g., missing inputs or model limitations).
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default MapLegend;
