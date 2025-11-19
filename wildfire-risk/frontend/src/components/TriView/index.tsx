import React, { useMemo, useState } from "react";
import DeckGL from "@deck.gl/react";
import type { PickingInfo } from "@deck.gl/core";
import { ScatterplotLayer } from "@deck.gl/layers";
import { TileLayer } from "@deck.gl/geo-layers";
import { BitmapLayer } from "@deck.gl/layers";
import type { RiskGridCell } from "../../api/types";
import { useRisk, useScenario, useLoading } from "../../state/selectors";
import MapHeatmap from "../MapHeatmap";
import MapLegend from "../MapLegend";
import TimeScrubber from "../TimeScrubber";
import WorldMap from "../WorldMap";

const TriView: React.FC = () => {
  // Updated: Nov 2 2025 - Added WorldMap with deck.gl TileLayer
  const risk = useRisk();
  const scenario = useScenario();
  const loading = useLoading();
  const [date, setDate] = useState<string>(new Date().toISOString().slice(0, 10));

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
    
    return [
      ...baseLayers,
      new ScatterplotLayer<RiskGridCell>({
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
      }),
    ];
  }, [risk]);

  const INITIAL_VIEW_STATE = useMemo(
    () => ({ longitude: -120.25, latitude: 35.25, zoom: 5, pitch: 0, bearing: 0 }),
    []
  );

  return (
    <div className="panel" aria-busy={loading}>
      <h2>Scenario Maps - Build: {new Date().toISOString()}</h2>
      <p>
        Active scenario: <strong>{scenario}</strong>
      </p>
      <p>Selected date: {date}</p>
      {loading && <p>Loading synthetic tiles…</p>}
      {!loading && risk && (
        <>
          <div className="maps-container">
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
                  getTooltip={(info: PickingInfo<RiskGridCell>) => {
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
            <WorldMap />
          </div>
        </>
      )}
      <TimeScrubber date={date} onChange={setDate} />
    </div>
  );
};

export default TriView;
