import create from "zustand";
import { persist, createJSONStorage } from "zustand/middleware";
import { fetchRiskGrid, fetchExplain, fetchFrames, fetchFireHistory, fetchFireAnalysis } from "../api/client";
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
    mapViewState: {
        longitude: 0,
        latitude: 20,
        zoom: 1,
        pitch: 0,
        bearing: 0,
    },
    clickedLocation: undefined,
    setMapViewState: (viewState) => set({ mapViewState: viewState }),
    setClickedLocation: (coords) => {
        set({ clickedLocation: coords });
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
    loadFireHistory: async (lat, lon, radiusKm, daysBack, startDate, endDate) => {
        try {
            const fireHistory = await fetchFireHistory(lat, lon, radiusKm, daysBack, startDate, endDate);
            set({ fireHistory });
        } catch (error) {
            console.error('Failed to load fire history:', error);
            throw error;
        }
    },
    selectFireEvent: async (event) => {
        set({ selectedFireEvent: event, fireAnalysis: undefined });
        if (event) {
            // Zoom map to fire location
            set({
                mapViewState: {
                    longitude: event.longitude,
                    latitude: event.latitude,
                    zoom: 8,
                    pitch: 0,
                    bearing: 0,
                }
            });
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
});
export const useTriViewState = create()(persist(creator, {
    name: "tri-view-state",
    storage: createJSONStorage(storageFactory),
}));
