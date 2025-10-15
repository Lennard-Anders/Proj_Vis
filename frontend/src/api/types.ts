/**
 * TypeScript types mirroring Pydantic schemas
 */

export interface BBox {
  min_lon: number;
  min_lat: number;
  max_lon: number;
  max_lat: number;
}

export interface RiskTile {
  lat: number;
  lon: number;
  prob: number;
  ci: [number, number];
}

export interface QualityData {
  dqf_mask: number[];
  data_availability: number[];
}

export interface RiskResponse {
  grid: RiskTile[];
  quality: QualityData;
  date: string;
  bbox: BBox;
}

export interface FeatureContribution {
  feature: string;
  value: number;
  unit: string;
  contribution: number;
}

export interface FeatureInteraction {
  pair: [string, string];
  value: number;
}

export interface ReliabilityBin {
  range: [number, number];
  observed: number;
}

export interface ExplainResponse {
  probability: number;
  ci: [number, number];
  local_shap: FeatureContribution[];
  interactions: FeatureInteraction[];
  reliability_bin: ReliabilityBin;
  ood: boolean;
}

export interface FeatureDelta {
  wind_speed_10m?: number;
  rh?: number;
  rain_24h?: number;
  gust_10m?: number;
}

export interface CounterfactualRequest {
  lat: number;
  lon: number;
  date: string;
  deltas: FeatureDelta;
  use_surrogate: boolean;
}

export interface ReasonCodeDelta {
  feature: string;
  delta_contribution: number;
}

export interface CounterfactualResponse {
  probability: number;
  delta: number;
  reason_codes_delta: ReasonCodeDelta[];
  used: string;
}

export interface FramesResponse {
  times: string[];
  tiles: string[];
}

export interface SpreadRequest {
  lat: number;
  lon: number;
  date: string;
  wind_speed_10m: number;
  wind_dir: number;
  duration_hours: number;
  steps: number;
}

export interface SpreadMetrics {
  hit_rate: number;
  over_under_spread: number;
  steps: number;
}

export interface SpreadResponse {
  footprint_geojson: any;
  metrics: SpreadMetrics;
}
