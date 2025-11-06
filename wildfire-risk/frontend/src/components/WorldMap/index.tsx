import React, { useMemo } from "react";
import DeckGL from "@deck.gl/react";
import { TileLayer } from "@deck.gl/geo-layers";
import { BitmapLayer } from "@deck.gl/layers";

const WorldMap: React.FC = () => {
  // World view centered on prime meridian
  const WORLD_VIEW_STATE = {
    longitude: 0,
    latitude: 20,
    zoom: 1,
    pitch: 0,
    bearing: 0,
  };

  const layers = useMemo(() => {
    return [
      new TileLayer({
        id: "world-base-map",
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
  }, []);

  return (
    <div className="world-map" style={{ marginLeft: '20px', flex: 1 }}>
      <h3 style={{ color: '#ff8c00', marginBottom: '10px' }}>Global Context Map</h3>
      <div style={{ position: 'relative', height: '400px', background: '#0a1929', borderRadius: '8px', overflow: 'hidden', border: '2px solid #ff8c00' }}>
        <DeckGL
          style={{ width: '100%', height: '100%' }}
          layers={layers}
          initialViewState={WORLD_VIEW_STATE}
          controller={true}
        />
      </div>
    </div>
  );
};

export default WorldMap;
