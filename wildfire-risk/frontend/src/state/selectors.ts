import { TriViewState, useTriViewState } from "./store";

export const useRisk = () => useTriViewState((state: TriViewState) => state.risk);
export const useExplanation = () =>
	useTriViewState((state: TriViewState) => state.explanation);
export const useFrames = () => useTriViewState((state: TriViewState) => state.frames);
export const useScenario = () =>
	useTriViewState((state: TriViewState) => state.selectedScenario);
export const useSelectedRegion = () =>
	useTriViewState((state: TriViewState) => state.selectedRegion);
export const useSetSelectedRegion = () =>
	useTriViewState((state: TriViewState) => state.setSelectedRegion);
export const useSelectedYear = () =>
	useTriViewState((state: TriViewState) => state.selectedYear);
export const useSetSelectedYear = () =>
	useTriViewState((state: TriViewState) => state.setSelectedYear);
export const useLoading = () => useTriViewState((state: TriViewState) => state.loading);
export const useFireHistory = () => useTriViewState((state: TriViewState) => state.fireHistory);
export const useSelectedFireEvent = () => useTriViewState((state: TriViewState) => state.selectedFireEvent);
export const useFireAnalysis = () => useTriViewState((state: TriViewState) => state.fireAnalysis);
export const useLoadFireHistory = () => useTriViewState((state: TriViewState) => state.loadFireHistory);
export const useSelectFireEvent = () => useTriViewState((state: TriViewState) => state.selectFireEvent);
export const useMapViewState = () => useTriViewState((state: TriViewState) => state.mapViewState);
export const useSetMapViewState = () => useTriViewState((state: TriViewState) => state.setMapViewState);
export const useClickedLocation = () => useTriViewState((state: TriViewState) => state.clickedLocation);
export const useSetClickedLocation = () => useTriViewState((state: TriViewState) => state.setClickedLocation);
export const useAIRiskPrediction = () => useTriViewState((state: TriViewState) => state.aiRiskPrediction);
export const useAIRiskConfidencePercent = () => useTriViewState((state: TriViewState) => state.aiRiskConfidencePercent);
export const useAIRiskGrid = () => useTriViewState((state: TriViewState) => state.aiRiskGrid);
