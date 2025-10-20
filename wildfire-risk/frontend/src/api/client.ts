import axios from "axios";
import {
  RiskResponse,
  ExplainResponse,
  FramesResponse,
  CounterfactualResponse,
} from "./types";

const apiBase = import.meta.env.VITE_API_BASE_URL || "/api";
const api = axios.create({ baseURL: apiBase });

const DEFAULT_DATE = new Date().toISOString().slice(0, 10);
const DEFAULT_BBOX = "-120.5,35.0,-120.0,35.5";
const DEFAULT_POINT = { lat: 35.25, lon: -120.25 };

// eslint-disable-next-line @typescript-eslint/no-unused-vars
export async function fetchRiskGrid(_overrides: Record<string, number> | undefined = undefined): Promise<RiskResponse> {
  const params = { date: DEFAULT_DATE, bbox: DEFAULT_BBOX };
  const { data } = await api.get<RiskResponse>("/risk", { params });
  return data;
}

// eslint-disable-next-line @typescript-eslint/no-unused-vars
export async function fetchExplain(_overrides: Record<string, number> | undefined = undefined): Promise<ExplainResponse> {
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
