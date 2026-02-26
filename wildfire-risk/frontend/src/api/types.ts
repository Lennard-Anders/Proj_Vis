export interface RiskGridCell {
  lat: number;
  lon: number;
  prob: number;
  ci: [number, number];
}

export interface RiskResponse {
  grid: RiskGridCell[];
  quality: {
    dqf_mask: number[];
    data_availability: number[];
  };
  meta: {
    grid_deg: number;
    generated_at?: string;
  };
}

export interface ExplainResponse {
  probability: number;
  ci: [number, number];
  local_shap: Array<{ feature: string; value: number; unit: string; contribution: number }>;
  interactions: Array<{ pair: [string, string]; value: number }>;
  reliability_bin: {
    range: [number, number];
    observed: number;
  };
  ood: boolean;
}

export interface FramesResponse {
  frames: Array<{ frame_id: string; timestamp: string; url: string; cloud_coverage: number }>;
}

export interface CounterfactualResponse {
  probability: number;
  delta: number;
  reason_codes_delta: Array<{ feature: string; from: number; to: number; d_contribution: number }>;
  used: "surrogate" | "full";
}

export interface FireEvent {
  event_id: string;
  latitude: number;
  longitude: number;
  date: string;
  fire_radiative_power: number;
  confidence: number;
  brightness_temp: number;
  area_km2: number | null;
}

export interface FireHistoryResponse {
  events: FireEvent[];
  total_events: number;
  period_start: string;
  period_end: string;
  region_center: { latitude: number; longitude: number };
}

export interface FireAnalysis {
  event_id: string;
  location: {
    latitude: number;
    longitude: number;
    elevation_m: number;
    slope_degrees: number;
    aspect_degrees: number;
  };
  fire_data: {
    date: string;
    max_frp: number;
    total_frp: number;
  };
  environmental_conditions: {
    temperature_c: number;
    humidity_percent: number;
    wind_speed_ms: number;
    precipitation_mm: number;
    ndvi: number;
    evi: number;
  };
  risk_factors: string[];
  description: string;
  analysis: {
    severity: string;
    terrain_risk: string;
    weather_risk: string;
  };
}

export interface AIRiskPrediction {
  probability: number;
  risk_level: string;
  risk_color: string;
  contributing_factors: Array<{
    factor: string;
    contribution: number;
    impact: string;
  }>;
  recommendations: string[];
  confidence: number;
  features: {
    temperature: number;
    wind_speed: number;
    humidity: number;
    rainfall: number;
    vegetation_dryness: number;
    drought_index: number;
  };
}

export interface RiskGridCell_AI {
  latitude: number;
  longitude: number;
  probability: number;
  risk_level: string;
  risk_color: string;
}

export interface AIRiskGridResponse {
  grid_cells: RiskGridCell_AI[];
  center_lat: number;
  center_lon: number;
  grid_size_deg: number;
  resolution: number;
}

export interface AIRiskConfidenceResponse {
  confidence_percent: number;
}

export interface WildfireLlmResponse {
  wildfire_probability_percent: number;
  explanation: string;
  feature_contributions?: Array<{ feature: string; weight: number }>;
  feature_interactions?: Array<{ pair: string; weight: number }>;
}
