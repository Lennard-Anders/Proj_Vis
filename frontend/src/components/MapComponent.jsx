import React, { useState, useCallback } from 'react';
import DeckGL from '@deck.gl/react';
import { Map } from 'react-map-gl';
import { HeatmapLayer, ScatterplotLayer } from '@deck.gl/layers';
import { TileLayer } from '@deck.gl/geo-layers';
import { BitmapLayer } from '@deck.gl/layers';

const INITIAL_VIEW_STATE = {
  longitude: -120,
  latitude: 37,
  zoom: 6,
  pitch: 0,
  bearing: 0
};

const MAP_STYLE = 'https://basemaps.cartocdn.com/gl/positron-gl-style/style.json';

function MapComponent({ riskData, selectedLocation, onLocationSelect }) {
  const [viewState, setViewState] = useState(INITIAL_VIEW_STATE);

  // Create layers
  const layers = [];

  // Heatmap layer for risk visualization
  if (riskData && riskData.length > 0) {
    layers.push(
      new HeatmapLayer({
        id: 'risk-heatmap',
        data: riskData,
        getPosition: d => [d.longitude, d.latitude],
        getWeight: d => d.risk_score || 0.5,
        radiusPixels: 60,
        intensity: 1,
        threshold: 0.05,
        colorRange: [
          [0, 255, 0, 25],      // Low risk - green
          [255, 255, 0, 85],    // Moderate risk - yellow
          [255, 165, 0, 127],   // High risk - orange
          [255, 0, 0, 255]      // Critical risk - red
        ]
      })
    );
  }

  // Scatterplot for specific locations
  if (selectedLocation) {
    layers.push(
      new ScatterplotLayer({
        id: 'selected-location',
        data: [selectedLocation],
        getPosition: d => [d.longitude, d.latitude],
        getFillColor: [0, 0, 255],
        getRadius: 5000,
        radiusMinPixels: 5,
        radiusMaxPixels: 50,
        pickable: true
      })
    );
  }

  const handleClick = useCallback((info, event) => {
    if (info.coordinate) {
      const [longitude, latitude] = info.coordinate;
      onLocationSelect({ latitude, longitude });
    }
  }, [onLocationSelect]);

  return (
    <DeckGL
      initialViewState={INITIAL_VIEW_STATE}
      viewState={viewState}
      onViewStateChange={({ viewState }) => setViewState(viewState)}
      controller={true}
      layers={layers}
      onClick={handleClick}
      style={{ position: 'relative', width: '100%', height: '100%' }}
    >
      <Map
        mapStyle={MAP_STYLE}
        mapboxAccessToken="pk.eyJ1IjoibWFwYm94IiwiYSI6ImNpejY4NXVycTA2emYycXBndHRqcmZ3N3gifQ.rJcFIG214AriISLbB6B5aw"
      />
    </DeckGL>
  );
}

export default MapComponent;
