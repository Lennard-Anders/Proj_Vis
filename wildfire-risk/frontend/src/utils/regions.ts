export interface RegionBounds {
  latMin: number;
  latMax: number;
  lonMin: number;
  lonMax: number;
}

export interface RegionDefinition {
  name: string;
  lat?: number;
  lon?: number;
  radius?: number;
  bounds?: RegionBounds;
}

export const REGION_PRESETS: Record<string, RegionDefinition> = {
  americas: { name: "🌎 Americas" },
  northamerica: { name: "🇺🇸 North America", lat: 45, lon: -100, radius: 2500, bounds: { latMin: 5, latMax: 83, lonMin: -170, lonMax: -50 } },
  southamerica: { name: "🇧🇷 South America", lat: -15, lon: -60, radius: 2500, bounds: { latMin: -60, latMax: 15, lonMin: -90, lonMax: -30 } },
  amazon: { name: "🌳 Amazon Basin", lat: -5, lon: -62, radius: 1500, bounds: { latMin: -20, latMax: 10, lonMin: -75, lonMax: -45 } },
  california: { name: "🔥 California", lat: 37, lon: -120, radius: 700, bounds: { latMin: 32, latMax: 42.5, lonMin: -125, lonMax: -114 } },
  australia: { name: "🇦🇺 Australia", lat: -25, lon: 135, radius: 2000, bounds: { latMin: -44, latMax: -10, lonMin: 112, lonMax: 155 } },
  canada: { name: "🇨🇦 Canada", lat: 60, lon: -110, radius: 2200, bounds: { latMin: 41, latMax: 83, lonMin: -141, lonMax: -52 } },
};

export type RegionKey = keyof typeof REGION_PRESETS;
