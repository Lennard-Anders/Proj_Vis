import React, { useMemo, useState, useEffect } from "react";
import DeckGL from "@deck.gl/react";
import { TileLayer } from "@deck.gl/geo-layers";
import { BitmapLayer, ScatterplotLayer } from "@deck.gl/layers";
import { useMapViewState, useSetMapViewState, useFireHistory, useSelectedFireEvent } from "../../state/selectors";
import { useTriViewState, TriViewState } from "../../state/store";
import type { FireEvent } from "../../api/types";

const WorldMap: React.FC = () => {
  const mapViewState = useMapViewState();
  const setMapViewState = useSetMapViewState();
  const fireHistory = useFireHistory();
  const selectedFireEvent = useSelectedFireEvent();
  const aiRiskGrid = useTriViewState((state: TriViewState) => state.aiRiskGrid);
  const [hoveredFire, setHoveredFire] = useState<FireEvent | null>(null);
  const [locationName, setLocationName] = useState<string>("");
  const [isLoadingLocation, setIsLoadingLocation] = useState(false);

  // Fetch location name when hovering over a fire
  useEffect(() => {
    if (!hoveredFire) {
      setLocationName("");
      return;
    }

    const fetchLocationName = async () => {
      setIsLoadingLocation(true);
      try {
        // Use Nominatim reverse geocoding (OpenStreetMap)
        const response = await fetch(
          `https://nominatim.openstreetmap.org/reverse?format=json&lat=${hoveredFire.latitude}&lon=${hoveredFire.longitude}&zoom=5&addressdetails=1`,
          {
            headers: {
              'User-Agent': 'WildfireRiskExplorer/1.0'
            }
          }
        );
        const data = await response.json();
        
        // Extract country and state/region
        const address = data.address || {};
        const parts = [];
        
        if (address.state || address.region) {
          parts.push(address.state || address.region);
        }
        if (address.country) {
          parts.push(address.country);
        }
        
        setLocationName(parts.length > 0 ? parts.join(", ") : "Unknown location");
      } catch (error) {
        console.error("Failed to fetch location:", error);
        setLocationName("Unknown location");
      } finally {
        setIsLoadingLocation(false);
      }
    };

    // Debounce the request slightly
    const timer = setTimeout(fetchLocationName, 300);
    return () => clearTimeout(timer);
  }, [hoveredFire]);

  const layers = useMemo(() => {
    const baseLayers: any[] = [
      new TileLayer({
        id: "world-base-map",
        data: "https://tile.openstreetmap.org/{z}/{x}/{y}.png",
        minZoom: 0,
        maxZoom: 19,
        tileSize: 256,
        renderSubLayers: (props: any) => {
          const { boundingBox } = props.tile;
          return new BitmapLayer({
            ...props,
            data: undefined,
            image: props.data,
            bounds: [boundingBox[0][0], boundingBox[0][1], boundingBox[1][0], boundingBox[1][1]],
          });
        },
      }),
    ];

    // Add fire markers if we have fire history
    if (fireHistory && fireHistory.events.length > 0) {
      const fireLayer = new ScatterplotLayer({
        id: 'fire-events',
        data: fireHistory.events,
        getPosition: (d: FireEvent) => [d.longitude, d.latitude],
        getRadius: (d: FireEvent) => {
          const isSelected = selectedFireEvent?.event_id === d.event_id;
          return isSelected ? 8000 : 5000;
        },
        getFillColor: (d: FireEvent) => {
          const isSelected = selectedFireEvent?.event_id === d.event_id;
          if (isSelected) return [255, 51, 51, 255]; // Bright red for selected
          const frp = d.fire_radiative_power;
          if (frp > 100) return [255, 51, 51, 200];
          if (frp > 50) return [255, 153, 51, 200];
          return [255, 204, 51, 200];
        },
        pickable: true,
        onHover: (info: any) => setHoveredFire(info.object || null),
        updateTriggers: {
          getRadius: [selectedFireEvent],
          getFillColor: [selectedFireEvent],
        },
      });
      baseLayers.push(fireLayer);
    }

    // Add AI risk grid layer if available
    if (aiRiskGrid && aiRiskGrid.grid_cells.length > 0) {
      const riskGridLayer = new ScatterplotLayer({
        id: 'ai-risk-grid',
        data: aiRiskGrid.grid_cells,
        getPosition: (d: any) => [d.longitude, d.latitude],
        getRadius: 15000, // Size of each grid cell
        getFillColor: (d: any) => {
          // Parse the hex color from risk_color
          const hex = d.risk_color.replace('#', '');
          const r = parseInt(hex.substring(0, 2), 16);
          const g = parseInt(hex.substring(2, 4), 16);
          const b = parseInt(hex.substring(4, 6), 16);
          return [r, g, b, 180]; // Semi-transparent
        },
        pickable: true,
        opacity: 0.6,
      });
      baseLayers.push(riskGridLayer);
    }

    return baseLayers;
  }, [fireHistory, selectedFireEvent, aiRiskGrid]);

  return (
    <div className="panel">
      <h2>🌍 Global Context Map</h2>
      <div className="world-map__container" style={{ position: 'relative' }}>
        <DeckGL
          style={{ width: '100%', height: '100%' }}
          layers={layers}
          viewState={mapViewState}
          onViewStateChange={({ viewState }: any) => setMapViewState && setMapViewState(viewState)}
          controller={true}
        />
        {hoveredFire && (
          <div
            style={{
              position: 'absolute',
              zIndex: 1,
              pointerEvents: 'none',
              left: '50%',
              top: '10px',
              transform: 'translateX(-50%)',
              background: 'rgba(0, 0, 0, 0.8)',
              color: 'white',
              padding: '8px 12px',
              borderRadius: '4px',
              fontSize: '12px',
              whiteSpace: 'nowrap',
            }}
          >
            <div><strong>🔥 Fire Event</strong></div>
            <div>📍 {isLoadingLocation ? "Loading..." : locationName}</div>
            <div>📅 Date: {hoveredFire.date}</div>
            <div>🌐 Coords: {hoveredFire.latitude.toFixed(3)}°, {hoveredFire.longitude.toFixed(3)}°</div>
            <div>🔥 FRP: {hoveredFire.fire_radiative_power.toFixed(1)} MW</div>
            <div>✓ Confidence: {hoveredFire.confidence}%</div>
          </div>
        )}
      </div>
    </div>
  );
};

export default WorldMap;
