import React, { useMemo, useState } from "react";
import DeckGL from "@deck.gl/react";
import type { PickingInfo } from "@deck.gl/core";
import { ScatterplotLayer, IconLayer } from "@deck.gl/layers";
import { TileLayer } from "@deck.gl/geo-layers";
import { BitmapLayer } from "@deck.gl/layers";
import type { RiskGridCell } from "../../api/types";
import { useRisk, useScenario, useLoading, useSelectedFireEvent, useFireAnalysis } from "../../state/selectors";
import MapHeatmap from "../MapHeatmap";
import MapLegend from "../MapLegend";
import TimeScrubber from "../TimeScrubber";
import WorldMap from "../WorldMap";

const TriView: React.FC = () => {
  // Updated: Nov 2 2025 - Added WorldMap with deck.gl TileLayer
  const risk = useRisk();
  const scenario = useScenario();
  const loading = useLoading();
  const selectedFireEvent = useSelectedFireEvent();
  const fireAnalysis = useFireAnalysis();
  const [date, setDate] = useState<string>(new Date().toISOString().slice(0, 10));
  const [hoveredFire, setHoveredFire] = useState<any>(null);

  const layers = useMemo(() => {
    const baseLayers: any[] = [
      new TileLayer({
        id: "base-map",
        data: "https://tile.openstreetmap.org/{z}/{x}/{y}.png",
        minZoom: 0,
        maxZoom: 19,
        tileSize: 256,
        renderSubLayers: (props: any) => {
          const { boundingBox } = props.tile;
          return new BitmapLayer(props, {
            data: undefined,
            image: props.data,
            bounds: [boundingBox[0][0], boundingBox[0][1], boundingBox[1][0], boundingBox[1][1]],
          });
        },
      }),
    ];

    if (!risk) {
      return baseLayers;
    }
    
    const riskLayer = new ScatterplotLayer<RiskGridCell>({
      id: "risk-layer",
      data: risk.grid,
      getPosition: (cell: RiskGridCell) => [cell.lon, cell.lat],
      getRadius: 8000,
      radiusUnits: "meters",
      getFillColor: (cell: RiskGridCell) => {
        const intensity = Math.min(255, Math.round(cell.prob * 255));
        const cooled = Math.max(0, 170 - Math.round(intensity / 2));
        return [255, cooled, 0, 255];
      },
      opacity: 1.0,
      pickable: true,
    });
    
    // Add fire event marker if one is selected
    const fireMarkerLayer = selectedFireEvent ? new ScatterplotLayer({
      id: "fire-marker",
      data: [selectedFireEvent],
      getPosition: (d: any) => [d.longitude, d.latitude],
      getRadius: 15000,
      radiusUnits: "meters",
      getFillColor: [255, 50, 50, 200],
      getLineColor: [255, 255, 255, 255],
      getLineWidth: 300,
      lineWidthUnits: "meters",
      pickable: true,
      stroked: true,
      onHover: (info: any) => {
        if (info.object) {
          setHoveredFire(info.object);
        }
      },
    }) : null;
    
    return [
      ...baseLayers,
      riskLayer,
      fireMarkerLayer,
    ].filter(Boolean);
  }, [risk, selectedFireEvent]);

  const INITIAL_VIEW_STATE = useMemo(
    () => ({ longitude: -120.25, latitude: 35.25, zoom: 5, pitch: 0, bearing: 0 }),
    []
  );

  return (
    <div className="panel" aria-busy={loading}>
      <div style={{ marginBottom: 'var(--spacing-md)' }}>
        <h2>🗺️ Wildfire Risk Visualization</h2>
        <div style={{ 
          display: 'flex', 
          gap: 'var(--spacing-md)', 
          flexWrap: 'wrap',
          fontSize: '0.9rem',
          color: 'var(--text-secondary)'
        }}>
          <div>
            <strong style={{ color: 'var(--accent-orange)' }}>Scenario:</strong> {scenario}
          </div>
          <div>
            <strong style={{ color: 'var(--accent-orange)' }}>Date:</strong> {date}
          </div>
        </div>
      </div>
      {loading && (
        <div style={{ 
          textAlign: 'center', 
          padding: 'var(--spacing-xl)',
          color: 'var(--text-secondary)' 
        }}>
          ⏳ Loading risk data...
        </div>
      )}
      {!loading && risk && (
        <>
          <div className="tri-view">
            <h3>Scenario Risk Map</h3>
            <div className="tri-view__grid">
              {risk.grid.slice(0, 6).map((cell: RiskGridCell) => (
                <div key={`${cell.lat}-${cell.lon}`} className="tri-view__cell">
                  <span>
                    {cell.lat.toFixed(2)}, {cell.lon.toFixed(2)}
                  </span>
                  <span>{(cell.prob * 100).toFixed(1)}%</span>
                </div>
              ))}
            </div>
            <div className="tri-view__deck">
              <DeckGL
                style={{ width: "100%", height: "100%" }}
                layers={layers}
                initialViewState={INITIAL_VIEW_STATE}
                controller
                getTooltip={(info: PickingInfo<any>) => {
                  // Show fire analysis tooltip if hovering fire marker
                  if (info.layer?.id === 'fire-marker' && fireAnalysis) {
                    const analysis = fireAnalysis;
                    return {
                      html: `
                        <div style="padding: 12px; max-width: 320px; background: rgba(10, 14, 39, 0.98); border-radius: 8px; border: 2px solid #ff6b35;">
                          <div style="font-weight: bold; font-size: 16px; color: #ff6b35; margin-bottom: 8px;">
                            🔥 ${analysis.fire_data.date}
                          </div>
                          <div style="color: #e0e6f5; line-height: 1.6; margin-bottom: 8px;">
                            ${analysis.description}
                          </div>
                          <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 8px; margin-top: 12px; padding-top: 12px; border-top: 1px solid rgba(224, 230, 245, 0.2);">
                            <div>
                              <div style="font-size: 11px; color: #9ca3af;">Severity</div>
                              <div style="font-weight: bold; color: ${analysis.analysis.severity === 'High' ? '#ff3333' : analysis.analysis.severity === 'Medium' ? '#ff9933' : '#ffcc33'};">
                                ${analysis.analysis.severity}
                              </div>
                            </div>
                            <div>
                              <div style="font-size: 11px; color: #9ca3af;">FRP</div>
                              <div style="font-weight: bold; color: #ff6b35;">${analysis.fire_data.max_frp.toFixed(1)} MW</div>
                            </div>
                            <div>
                              <div style="font-size: 11px; color: #9ca3af;">Elevation</div>
                              <div style="color: #e0e6f5;">${analysis.location.elevation_m.toFixed(0)}m</div>
                            </div>
                            <div>
                              <div style="font-size: 11px; color: #9ca3af;">Slope</div>
                              <div style="color: #e0e6f5;">${analysis.location.slope_degrees.toFixed(1)}°</div>
                            </div>
                            <div>
                              <div style="font-size: 11px; color: #9ca3af;">Temperature</div>
                              <div style="color: #e0e6f5;">${analysis.environmental_conditions.temperature_c.toFixed(1)}°C</div>
                            </div>
                            <div>
                              <div style="font-size: 11px; color: #9ca3af;">Humidity</div>
                              <div style="color: #e0e6f5;">${analysis.environmental_conditions.humidity_percent.toFixed(0)}%</div>
                            </div>
                          </div>
                          ${analysis.risk_factors.length > 0 ? `
                            <div style="margin-top: 12px; padding-top: 12px; border-top: 1px solid rgba(224, 230, 245, 0.2);">
                              <div style="font-size: 11px; color: #9ca3af; margin-bottom: 4px;">Risk Factors:</div>
                              ${analysis.risk_factors.map((factor: string) => 
                                `<div style="color: #ff9933; font-size: 13px;">⚠️ ${factor}</div>`
                              ).join('')}
                            </div>
                          ` : ''}
                        </div>
                      `,
                      style: {
                        backgroundColor: 'transparent',
                        padding: '0',
                      }
                    };
                  }
                  
                  // Show risk cell tooltip
                  const cell = (info && (info.object as RiskGridCell | null)) || undefined;
                  if (!cell) {
                    return null;
                  }
                  return `Risk ${(cell.prob * 100).toFixed(1)}% at ${cell.lat.toFixed(2)}, ${cell.lon.toFixed(2)}`;
                }}
              />
            </div>
            <MapHeatmap data={risk} />
            <MapLegend />
          </div>
        </>
      )}
      <TimeScrubber date={date} onChange={setDate} />
    </div>
  );
};

export default TriView;
