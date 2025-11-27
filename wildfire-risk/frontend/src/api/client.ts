import axios from "axios";
import {
  RiskResponse,
  ExplainResponse,
  FramesResponse,
  CounterfactualResponse,
  FireHistoryResponse,
  FireAnalysis,
  AIRiskPrediction,
  AIRiskGridResponse,
} from "./types";

const apiBase = import.meta.env.VITE_API_BASE_URL || "/api";
const api = axios.create({ baseURL: apiBase });

const DEFAULT_DATE = new Date().toISOString().slice(0, 10);
const DEFAULT_BBOX = "-120.5,35.0,-120.0,35.5";
const DEFAULT_POINT = { lat: 35.25, lon: -120.25 };

export async function fetchRiskGrid(_: Record<string, number> | undefined = undefined): Promise<RiskResponse> {
  const params = { date: DEFAULT_DATE, bbox: DEFAULT_BBOX };
  const { data } = await api.get<RiskResponse>("/risk", { params });
  return data;
}

export async function fetchExplain(_: Record<string, number> | undefined = undefined): Promise<ExplainResponse> {
  const params = {
    date: DEFAULT_DATE,
    lat: DEFAULT_POINT.lat,
    lon: DEFAULT_POINT.lon,
  };
  const { data } = await api.get<ExplainResponse>("/explain", { params });
  return data;
}

export async function fetchFrames(): Promise<FramesResponse> {
  const params = { date: DEFAULT_DATE, lat: DEFAULT_POINT.lat, lon: DEFAULT_POINT.lon };
  const { data } = await api.get<FramesResponse>("/frames", { params });
  return data;
}

export async function runCounterfactual(
  overrides: Record<string, number>
): Promise<CounterfactualResponse> {
  const payload = {
    lat: DEFAULT_POINT.lat,
    lon: DEFAULT_POINT.lon,
    date: DEFAULT_DATE,
    overrides,
  };
  const { data } = await api.post<CounterfactualResponse>("/risk/counterfactual", payload);
  return data;
}

export async function fetchFireHistory(
  lat?: number,
  lon?: number,
  radiusKm?: number,
  daysBack?: number,
  startDate?: string,
  endDate?: string
): Promise<FireHistoryResponse> {
  const params: any = {};
  
  // Use date range if provided, otherwise use days_back
  if (startDate && endDate) {
    params.start_date = startDate;
    params.end_date = endDate;
  } else {
    params.days_back = daysBack || 1825;
  }
  
  // Only add location params if provided (otherwise searches all Americas)
  if (lat !== undefined && lon !== undefined) {
    params.lat = lat;
    params.lon = lon;
    params.radius_km = radiusKm || 100;
  }
  const { data } = await api.get<FireHistoryResponse>("/gee/fire-history", { params });
  return data;
}

export async function fetchFireAnalysis(
  eventId: string,
  lat: number,
  lon: number,
  date: string
): Promise<FireAnalysis> {
  const params = { lat, lon, date };
  const { data } = await api.get<FireAnalysis>(`/gee/fire-analysis/${eventId}`, { params });
  return data;
}

export async function predictAIRisk(
  latitude: number,
  longitude: number,
  temperature: number,
  wind_speed_10m: number,
  rh: number,
  rain_24h: number = 0,
  date?: string
): Promise<AIRiskPrediction> {
  const payload = {
    latitude,
    longitude,
    temperature,
    wind_speed_10m,
    rh,
    rain_24h,
    date,
    use_historical_context: true
  };
  const { data } = await api.post<AIRiskPrediction>("/ai-risk/predict", payload);
  return data;
}

export async function predictAIRiskGrid(
  center_lat: number,
  center_lon: number,
  temperature: number,
  wind_speed_10m: number,
  rh: number,
  rain_24h: number = 0,
  grid_size_deg: number = 1.0,
  grid_resolution: number = 20
): Promise<AIRiskGridResponse> {
  const payload = {
    center_lat,
    center_lon,
    grid_size_deg,
    grid_resolution,
    temperature,
    wind_speed_10m,
    rh,
    rain_24h
  };
  const { data } = await api.post<AIRiskGridResponse>("/ai-risk/predict-grid", payload);
  return data;
}
