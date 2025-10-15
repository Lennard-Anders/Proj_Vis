import { TriViewState, useTriViewState } from "./store";

export const useRisk = () => useTriViewState((state: TriViewState) => state.risk);
export const useExplanation = () =>
	useTriViewState((state: TriViewState) => state.explanation);
export const useFrames = () => useTriViewState((state: TriViewState) => state.frames);
export const useScenario = () =>
	useTriViewState((state: TriViewState) => state.selectedScenario);
export const useLoading = () => useTriViewState((state: TriViewState) => state.loading);
