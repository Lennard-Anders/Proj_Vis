import React, { useMemo, useState, useEffect } from "react";
import DeckGL from "@deck.gl/react";
import type { PickingInfo } from "@deck.gl/core";
import { ScatterplotLayer } from "@deck.gl/layers";
import { HeatmapLayer, ScreenGridLayer } from "@deck.gl/aggregation-layers";
import { TileLayer } from "@deck.gl/geo-layers";
import { BitmapLayer } from "@deck.gl/layers";
import type { RiskGridCell } from "../../api/types";
import { useRisk, useScenario, useLoading, useSelectedFireEvent, useFireAnalysis } from "../../state/selectors";
import { useTriViewState, TriViewState } from "../../state/store";
import MapHeatmap from "../MapHeatmap";
import MapLegend from "../MapLegend";
import TimeScrubber from "../TimeScrubber";

interface TemperaturePoint {
  latitude: number;
  longitude: number;
  temperature: number;
}

// Color scale for temperature (like weather maps) - blue to red gradient
const TEMP_COLOR_RANGE = [
  [0, 0, 255],      // -10°C: Deep blue
  [0, 128, 255],    // 0°C: Light blue
  [0, 255, 255],    // 10°C: Cyan
  [0, 255, 128],    // 20°C: Cyan-green
  [128, 255, 0],    // 25°C: Green-yellow
  [255, 255, 0],    // 30°C: Yellow
  [255, 200, 0],    // 35°C: Yellow-orange
  [255, 128, 0],    // 40°C: Orange
  [255, 64, 0],     // 45°C: Orange-red
  [255, 0, 0],      // 50°C: Red
];

const TriView: React.FC = () => {
  const risk = useRisk();
  const scenario = useScenario();
  const loading = useLoading();
  const selectedFireEvent = useSelectedFireEvent();
  const fireAnalysis = useFireAnalysis();
  const aiRiskGrid = useTriViewState((state: TriViewState) => state.aiRiskGrid);
  const [date, setDate] = useState<string>("2013-01-01"); // Use date that exists in historical dataset
  const [temperatureData, setTemperatureData] = useState<TemperaturePoint[]>([]);
  const [showTempLayer, setShowTempLayer] = useState(false);

  // Load temperature data - ALWAYS load, just control visibility
  useEffect(() => {
    const loadTemperatureData = async () => {
      try {
        console.log('Loading temperature data for date:', date);
        const response = await fetch('http://localhost:8000/api/temperature/heatmap', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            date,
            region: 'global',
            bbox: null
          })
        });
        if (response.ok) {
          const result = await response.json();
          console.log('Loaded temperature points:', result.count);
          setTemperatureData(result.data || []);
        } else {
          console.error('Temperature API error:', response.status);
        }
      } catch (err) {
        console.error('Failed to load temperature data:', err);
      }
    };
    loadTemperatureData(); // Always load, visibility controlled by showTempLayer
  }, [date]);

  const layers = useMemo(() => {
    const baseLayers: any[] = [
      new TileLayer({
        id: "base-map",
        data: "https://tile.openstreetmap.org/{z}/{x}/{y}.png",
        minZoom: 0,
        maxZoom: 19,
        tileSize: 256,
        renderSubLayers: (props: any) => {
          if (!props.data) return null;
          
          const {
            bbox: {west, south, east, north}
          } = props.tile;
          
          return new BitmapLayer(props, {
            data: null,
            image: props.data,
            bounds: [west, south, east, north]
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
    
    // Temperature heatmap layer - continuous weather-style gradient
    const tempLayer = showTempLayer && temperatureData.length > 0 ? new HeatmapLayer({
      id: 'temperature-weather-map',
      data: temperatureData,
      getPosition: (d: TemperaturePoint) => [d.longitude, d.latitude],
      getWeight: (d: TemperaturePoint) => Math.max(0, d.temperature + 10), // Shift to positive
      radiusPixels: 60,
      intensity: 1.5,
      threshold: 0.03,
      colorRange: TEMP_COLOR_RANGE as any,
      aggregation: 'MEAN',
    }) : null;

    // AI Risk Grid layer
    const aiRiskLayer = aiRiskGrid && aiRiskGrid.grid_cells.length > 0 ? new ScatterplotLayer({
      id: 'ai-risk-grid',
      data: aiRiskGrid.grid_cells,
      getPosition: (d: any) => [d.longitude, d.latitude],
      getRadius: 12000,
      radiusUnits: 'meters',
      getFillColor: (d: any) => {
        const hex = d.risk_color.replace('#', '');
        const r = parseInt(hex.substring(0, 2), 16);
        const g = parseInt(hex.substring(2, 4), 16);
        const b = parseInt(hex.substring(4, 6), 16);
        return [r, g, b, 150];
      },
      pickable: true,
      opacity: 0.7,
    }) : null;
    
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
      onHover: (_info: any) => {
        // Fire hover handling moved to WorldMap component
      },
    }) : null;
    
    return [
      ...baseLayers,
      tempLayer,
      riskLayer,
      aiRiskLayer,
      fireMarkerLayer,
    ].filter(Boolean);
  }, [risk, selectedFireEvent, showTempLayer, temperatureData, aiRiskGrid]);

  const INITIAL_VIEW_STATE = useMemo(
    () => ({ longitude: -120.25, latitude: 35.25, zoom: 5, pitch: 0, bearing: 0 }),
    []
  );

  return (
    <div className="panel" aria-busy={loading}>
      <div style={{ marginBottom: 'var(--spacing-md)' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <h2>🗺️ Wildfire Risk Visualization</h2>
          <button 
            onClick={() => setShowTempLayer(!showTempLayer)}
            style={{
              padding: '6px 12px',
              fontSize: '0.85rem',
              background: showTempLayer ? 'linear-gradient(135deg, #3b82f6 0%, #2563eb 100%)' : 'var(--bg-secondary)',
              color: 'white',
              border: 'none',
              borderRadius: '4px',
              cursor: 'pointer'
            }}
          >
            {showTempLayer ? '🌡️ Hide Temp' : '🌡️ Show Temp'}
          </button>
        </div>
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
                initialViewState={INITIAL_VIEW_STATE as any}
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
                  const cell = info?.object as RiskGridCell | null;
                  if (!cell || !cell.lat || !cell.lon || cell.prob === undefined) {
                    return null;
                  }
                  return `Risk ${(cell.prob * 100).toFixed(1)}% at ${cell.lat.toFixed(2)}, ${cell.lon.toFixed(2)}`;
                }}
              />
            </div>
            <MapHeatmap data={risk} />
            <MapLegend />
          </div>

          {/* Temperature Heatmap Visualization */}
          <div className="tri-view" style={{ marginTop: 'var(--spacing-lg)' }}>
            <h3>🌡️ Global Temperature Heatmap</h3>
            <div className="tri-view__deck" style={{ height: '500px' }}>
              <DeckGL
                style={{ width: "100%", height: "100%" }}
                layers={[
                  new TileLayer({
                    id: "temp-base-map",
                    data: "https://tile.openstreetmap.org/{z}/{x}/{y}.png",
                    minZoom: 0,
                    maxZoom: 19,
                    tileSize: 256,
                    renderSubLayers: (props: any) => {
                      if (!props.data) return null;
                      const {
                        bbox: {west, south, east, north}
                      } = props.tile;
                      return new BitmapLayer(props, {
                        data: null,
                        image: props.data,
                        bounds: [west, south, east, north]
                      });
                    },
                  }),
                  showTempLayer && temperatureData.length > 0 ? new HeatmapLayer({
                    id: 'global-temperature-heatmap',
                    data: temperatureData,
                    getPosition: (d: TemperaturePoint) => [d.longitude, d.latitude],
                    getWeight: (d: TemperaturePoint) => Math.max(0, d.temperature + 10),
                    radiusPixels: 50,
                    intensity: 2,
                    threshold: 0.05,
                    colorRange: TEMP_COLOR_RANGE as any,
                    aggregation: 'MEAN',
                  }) : null,
                ].filter(Boolean)}
                initialViewState={{
                  longitude: 0,
                  latitude: 20,
                  zoom: 2,
                  pitch: 0,
                  bearing: 0
                }}
                controller
                getTooltip={(info: PickingInfo<any>) => {
                  const temp = info?.object as TemperaturePoint | null;
                  if (!temp || temp.temperature === undefined) return null;
                  return `Temperature: ${temp.temperature.toFixed(1)}°C`;
                }}
              />
            </div>
            <div style={{ 
              marginTop: 'var(--spacing-md)', 
              padding: 'var(--spacing-md)',
              background: 'var(--bg-secondary)',
              borderRadius: '8px'
            }}>
              <h4 style={{ marginBottom: 'var(--spacing-sm)', fontSize: '0.9rem' }}>
                Temperature Scale (°C)
              </h4>
              <div style={{ 
                display: 'flex', 
                height: '30px', 
                borderRadius: '4px',
                overflow: 'hidden',
                marginBottom: 'var(--spacing-sm)'
              }}>
                {TEMP_COLOR_RANGE.map((color, i) => (
                  <div
                    key={i}
                    style={{
                      flex: 1,
                      background: `rgb(${color[0]}, ${color[1]}, ${color[2]})`
                    }}
                  />
                ))}
              </div>
              <div style={{ 
                display: 'flex', 
                justifyContent: 'space-between',
                fontSize: '0.75rem',
                color: 'var(--text-secondary)'
              }}>
                <span>-10°C (Blue)</span>
                <span>20°C (Green)</span>
                <span>50°C (Red)</span>
              </div>
            </div>
          </div>
        </>
      )}
      <TimeScrubber date={date} onChange={setDate} />
    </div>
  );
};

export default TriView;
