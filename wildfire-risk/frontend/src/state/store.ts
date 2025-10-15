import create from "zustand";
import { persist, createJSONStorage } from "zustand/middleware";
import { fetchRiskGrid, fetchExplain, fetchFrames } from "../api/client";
import type { RiskResponse, ExplainResponse, FramesResponse } from "../api/types";

export interface TriViewState {
  risk?: RiskResponse;
  explanation?: ExplainResponse;
  frames?: FramesResponse;
  selectedScenario: "observed" | "counterfactual" | "variant";
  loading: boolean;
  initialize: () => Promise<void>;
  setScenario: (scenario: TriViewState["selectedScenario"]) => void;
  runWhatIf: (overrides: Record<string, number>) => Promise<void>;
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
});

export const useTriViewState = create<TriViewState>()(
  persist<TriViewState>(creator, {
    name: "tri-view-state",
    storage: createJSONStorage(storageFactory),
  })
);
