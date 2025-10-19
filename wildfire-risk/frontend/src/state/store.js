import create from "zustand";
import { persist, createJSONStorage } from "zustand/middleware";
import { fetchRiskGrid, fetchExplain, fetchFrames } from "../api/client";
const storageFactory = () => {
    if (typeof window !== "undefined" && window.localStorage) {
        return window.localStorage;
    }
    const memory = new Map();
    return {
        getItem: (key) => memory.get(key) ?? null,
        setItem: (key, value) => {
            memory.set(key, value);
        },
        removeItem: (key) => {
            memory.delete(key);
        },
    };
};
const creator = (set) => ({
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
        }
        finally {
            set({ loading: false });
        }
    },
    setScenario: (selectedScenario) => set({ selectedScenario }),
    runWhatIf: async (overrides) => {
        set({ loading: true });
        try {
            const [risk, explanation] = await Promise.all([
                fetchRiskGrid(overrides),
                fetchExplain(overrides),
            ]);
            set({ risk, explanation });
        }
        finally {
            set({ loading: false });
        }
    },
});
export const useTriViewState = create()(persist(creator, {
    name: "tri-view-state",
    storage: createJSONStorage(storageFactory),
}));
