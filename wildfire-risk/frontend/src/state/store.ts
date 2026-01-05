import create from "zustand";
import { persist, createJSONStorage } from "zustand/middleware";
import { fetchRiskGrid, fetchExplain, fetchFrames, fetchFireHistory, fetchFireAnalysis, predictAIRisk, predictAIRiskGrid, fetchAIRiskConfidence } from "../api/client";
import type { RiskResponse, ExplainResponse, FramesResponse, FireHistoryResponse, FireEvent, FireAnalysis, AIRiskPrediction, AIRiskGridResponse, WildfireLlmResponse } from "../api/types";

export interface TriViewState {
  risk?: RiskResponse;
  explanation?: ExplainResponse;
  frames?: FramesResponse;
  fireHistory?: FireHistoryResponse;
  selectedFireEvent?: FireEvent;
  fireAnalysis?: FireAnalysis;
  wildfireLlmExplanation?: WildfireLlmResponse;
  aiRiskPrediction?: AIRiskPrediction;
  aiRiskConfidencePercent?: number | null;
  aiRiskGrid?: AIRiskGridResponse;
  selectedScenario: "observed" | "counterfactual" | "variant";
  selectedDate: string;
  bbox?: { min_lat: number; max_lat: number; min_lon: number; max_lon: number };
  loading: boolean;
  mapViewState: { longitude: number; latitude: number; zoom: number; pitch: number; bearing: number };
  clickedLocation?: { lat: number; lon: number };
  initialize: () => Promise<void>;
  setScenario: (scenario: TriViewState["selectedScenario"]) => void;
  runWhatIf: (overrides: Record<string, number>) => Promise<void>;
  runAIRiskPrediction: (params: { lat: number; lon: number; temperature: number; wind_speed_10m: number; rh: number; rain_24h?: number }) => Promise<void>;
  runAIRiskGrid: (params: { lat: number; lon: number; temperature: number; wind_speed_10m: number; rh: number; rain_24h?: number; grid_size_deg?: number }) => Promise<void>;
  loadFireHistory: (lat?: number, lon?: number, radiusKm?: number, daysBack?: number, startDate?: string, endDate?: string) => Promise<void>;
  selectFireEvent: (event: FireEvent | undefined) => Promise<void>;
  setWildfireLlmExplanation: (data: WildfireLlmResponse | undefined) => void;
  setMapViewState: (viewState: Partial<TriViewState["mapViewState"]>) => void;
  setClickedLocation: (coords: { lat: number; lon: number }) => void;
  setDate: (date: string) => void;
  setBbox: (bbox: { min_lat: number; max_lat: number; min_lon: number; max_lon: number } | undefined) => void;
}

type SetState = (
  partial:
    | TriViewState
    | Partial<TriViewState>
    | ((state: TriViewState) => TriViewState | Partial<TriViewState>),
  replace?: boolean
) => void;

const storageFactory = () => {
  if (typeof window !== "undefined" && window.localStorage) {
    return window.localStorage;
  }
  const memory = new Map<string, string>();
  return {
    getItem: (key: string) => memory.get(key) ?? null,
    setItem: (key: string, value: string) => {
      memory.set(key, value);
    },
    removeItem: (key: string) => {
      memory.delete(key);
    },
  } as Storage;
};

const creator = (set: SetState): TriViewState => ({
  selectedScenario: "observed",
  selectedDate: new Date().toISOString().slice(0, 10),
  loading: false,
  mapViewState: {
    longitude: -100,
    latitude: 40,
    zoom: 3,
    pitch: 0,
    bearing: 0,
  },
  clickedLocation: undefined,
  wildfireLlmExplanation: undefined,
  aiRiskConfidencePercent: null,
  initialize: async () => {
    set({ loading: true });
    try {
      const [risk, explanation, frames] = await Promise.all([
        fetchRiskGrid(),
        fetchExplain(),
        fetchFrames(),
      ]);
      set({ risk, explanation, frames });
    } finally {
      set({ loading: false });
    }
  },
  setScenario: (selectedScenario: TriViewState["selectedScenario"]) =>
    set({ selectedScenario }),
  runWhatIf: async (overrides: Record<string, number>) => {
    set({ loading: true });
    try {
      const [risk, explanation] = await Promise.all([
        fetchRiskGrid(overrides),
        fetchExplain(overrides),
      ]);
      set({ risk, explanation });
    } finally {
      set({ loading: false });
    }
  },
  runAIRiskPrediction: async (params) => {
    set({ loading: true });
    try {
      console.log('runAIRiskPrediction called with:', params);
      set({ aiRiskConfidencePercent: null });
      const prediction = await predictAIRisk(
        params.lat,
        params.lon,
        params.temperature,
        params.wind_speed_10m,
        params.rh,
        params.rain_24h || 0
      );
      console.log('AI Risk Prediction received:', prediction);
      set({ aiRiskPrediction: prediction });
      console.log('AI Risk Prediction stored in state');

      // Separate LLM call to estimate confidence for the predicted probability
      try {
        const confidence = await fetchAIRiskConfidence({
          predicted_probability_percent: prediction.probability * 100,
          latitude: params.lat,
          longitude: params.lon,
          temperature: params.temperature,
          wind_speed_10m: params.wind_speed_10m,
          rh: params.rh,
          rain_24h: params.rain_24h || 0,
        });
        set({ aiRiskConfidencePercent: confidence.confidence_percent });
      } catch (confidenceErr) {
        console.warn('AI confidence request failed:', confidenceErr);
        set({ aiRiskConfidencePercent: null });
      }
    } catch (error) {
      console.error('AI risk prediction failed:', error);
    } finally {
      set({ loading: false });
    }
  },
  runAIRiskGrid: async (params) => {
    set({ loading: true });
    try {
      const gridResult = await predictAIRiskGrid(
        params.lat,
        params.lon,
        params.temperature,
        params.wind_speed_10m,
        params.rh,
        params.rain_24h || 0,
        params.grid_size_deg || 1.0,
        20
      );
      set({ aiRiskGrid: gridResult });
    } catch (error) {
      console.error('AI risk grid prediction failed:', error);
    } finally {
      set({ loading: false });
    }
  },
  loadFireHistory: async (lat?: number, lon?: number, radiusKm?: number, daysBack?: number, startDate?: string, endDate?: string) => {
    try {
      const fireHistory = await fetchFireHistory(lat, lon, radiusKm, daysBack, startDate, endDate);
      set({ fireHistory });
    } catch (error) {
      console.error('Failed to load fire history:', error);
    }
  },
  selectFireEvent: async (event: FireEvent | undefined) => {
    set({ selectedFireEvent: event, fireAnalysis: undefined });
    if (event) {
      try {
        const analysis = await fetchFireAnalysis(
          event.event_id,
          event.latitude,
          event.longitude,
          event.date
        );
        set({ fireAnalysis: analysis });
      } catch (error) {
        console.error('Failed to fetch fire analysis:', error);
      }
    }
  },
  setWildfireLlmExplanation: (data) => {
    set({ wildfireLlmExplanation: data });
  },
  setMapViewState: (viewState) => {
    set((state) => ({ 
      mapViewState: { ...state.mapViewState, ...viewState } 
    }));
  },
  setClickedLocation: (coords) => {
    set({ clickedLocation: coords });
  },
  setDate: (date: string) => {
    set({ selectedDate: date });
  },
  setBbox: (bbox) => {
    set({ bbox });
  },
});

export const useTriViewState = create<TriViewState>()(
  persist<TriViewState>(creator, {
    name: "tri-view-state",
    storage: createJSONStorage(storageFactory),
  })
);
