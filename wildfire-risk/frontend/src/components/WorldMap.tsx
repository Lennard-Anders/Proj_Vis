import React from "react";

// Simple world map showing major cities as reference points
const MAJOR_CITIES = [
  { name: "New York", lon: -74.006, lat: 40.7128 },
  { name: "London", lon: -0.1276, lat: 51.5074 },
  { name: "Tokyo", lon: 139.6917, lat: 35.6895 },
  { name: "Sydney", lon: 151.2093, lat: -33.8688 },
  { name: "São Paulo", lon: -46.6333, lat: -23.5505 },
  { name: "Cairo", lon: 31.2357, lat: 30.0444 },
  { name: "Mumbai", lon: 72.8777, lat: 19.076 },
  { name: "Beijing", lon: 116.4074, lat: 39.9042 },
  { name: "Los Angeles", lon: -118.2437, lat: 34.0522 },
  { name: "Moscow", lon: 37.6173, lat: 55.7558 },
];

const WorldMap: React.FC = () => {
  // Convert lat/lon to x/y percentage for positioning
  const latLonToPercent = (lat: number, lon: number) => {
    const x = ((lon + 180) / 360) * 100;
    const y = ((90 - lat) / 180) * 100;
    return { x, y };
  };

  return (
    <div className="world-map">
      <h3>World Reference Map</h3>
      <div className="world-map__container" style={{ position: 'relative', height: '400px', background: '#0a1929', borderRadius: '8px', overflow: 'hidden' }}>
        {/* Grid lines */}
        <svg style={{ position: 'absolute', width: '100%', height: '100%', top: 0, left: 0 }}>
          {/* Latitude lines */}
          {[-60, -30, 0, 30, 60].map(lat => {
            const y = ((90 - lat) / 180) * 100;
            return (
              <line
                key={`lat-${lat}`}
                x1="0%"
                y1={`${y}%`}
                x2="100%"
                y2={`${y}%`}
                stroke="#334155"
                strokeWidth="1"
              />
            );
          })}
          {/* Longitude lines */}
          {[-120, -60, 0, 60, 120].map(lon => {
            const x = ((lon + 180) / 360) * 100;
            return (
              <line
                key={`lon-${lon}`}
                x1={`${x}%`}
                y1="0%"
                x2={`${x}%`}
                y2="100%"
                stroke="#334155"
                strokeWidth="1"
              />
            );
          })}
        </svg>
        
        {/* Cities */}
        {MAJOR_CITIES.map(city => {
          const pos = latLonToPercent(city.lat, city.lon);
          return (
            <div
              key={city.name}
              style={{
                position: 'absolute',
                left: `${pos.x}%`,
                top: `${pos.y}%`,
                transform: 'translate(-50%, -50%)',
              }}
              title={city.name}
            >
              <div style={{
                width: '8px',
                height: '8px',
                borderRadius: '50%',
                background: '#ff8c00',
                border: '2px solid #ffc870',
                boxShadow: '0 0 8px rgba(255, 140, 0, 0.6)',
              }} />
              <div style={{
                position: 'absolute',
                top: '12px',
                left: '50%',
                transform: 'translateX(-50%)',
                whiteSpace: 'nowrap',
                fontSize: '10px',
                color: '#94a3b8',
                textShadow: '0 1px 2px rgba(0,0,0,0.8)',
              }}>
                {city.name}
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
};

export default WorldMap;
