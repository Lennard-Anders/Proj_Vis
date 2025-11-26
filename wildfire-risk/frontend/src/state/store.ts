import create from "zustand";
import { persist, createJSONStorage } from "zustand/middleware";
import { fetchRiskGrid, fetchExplain, fetchFrames, fetchFireHistory, fetchFireAnalysis } from "../api/client";
import type { RiskResponse, ExplainResponse, FramesResponse, FireHistoryResponse, FireEvent, FireAnalysis } from "../api/types";

export interface TriViewState {
  risk?: RiskResponse;
  explanation?: ExplainResponse;
  frames?: FramesResponse;
  fireHistory?: FireHistoryResponse;
  selectedFireEvent?: FireEvent;
  fireAnalysis?: FireAnalysis;
  selectedScenario: "observed" | "counterfactual" | "variant";
  loading: boolean;
  mapViewState: { longitude: number; latitude: number; zoom: number; pitch: number; bearing: number; transitionDuration?: number };
  initialize: () => Promise<void>;
  setScenario: (scenario: TriViewState["selectedScenario"]) => void;
  runWhatIf: (overrides: Record<string, number>) => Promise<void>;
  loadFireHistory: (lat?: number, lon?: number, radiusKm?: number, daysBack?: number, startDate?: string, endDate?: string) => Promise<void>;
  selectFireEvent: (event: FireEvent | undefined) => Promise<void>;
  setMapViewState: (viewState: Partial<TriViewState["mapViewState"]>) => void;
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
  loading: false,
  mapViewState: {
    longitude: -100,
    latitude: 40,
    zoom: 3,
    pitch: 0,
    bearing: 0,
  },
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
  setMapViewState: (viewState) => {
    set((state) => ({ 
      mapViewState: { ...state.mapViewState, ...viewState } 
    }));
  },
});

export const useTriViewState = create<TriViewState>()(
  persist<TriViewState>(creator, {
    name: "tri-view-state",
    storage: createJSONStorage(storageFactory),
  })
);
