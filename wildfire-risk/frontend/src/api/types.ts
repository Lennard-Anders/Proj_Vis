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
