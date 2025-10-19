import { useTriViewState } from "./store";
export const useRisk = () => useTriViewState((state) => state.risk);
export const useExplanation = () => useTriViewState((state) => state.explanation);
export const useFrames = () => useTriViewState((state) => state.frames);
export const useScenario = () => useTriViewState((state) => state.selectedScenario);
export const useLoading = () => useTriViewState((state) => state.loading);
