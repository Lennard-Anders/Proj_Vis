/**
 * Zustand store for managing application state
 */
import { create } from 'zustand';

interface PanelState {
  date: string;
  bbox: [number, number, number, number];
  layers: string[];
  scenario: any;
}

interface AppState {
  panelA: PanelState;
  panelB: PanelState;
  panelC: PanelState;
  linked: boolean;
  
  updatePanel: (panel: 'A' | 'B' | 'C', updates: Partial<PanelState>) => void;
  toggleLinked: () => void;
}

export const useStore = create<AppState>((set) => ({
  panelA: {
    date: '2024-01-15',
    bbox: [-122, 37, -121, 38],
    layers: ['risk'],
    scenario: null,
  },
  panelB: {
    date: '2024-01-15',
    bbox: [-122, 37, -121, 38],
    layers: ['risk'],
    scenario: null,
  },
  panelC: {
    date: '2024-01-15',
    bbox: [-122, 37, -121, 38],
    layers: ['risk'],
    scenario: null,
  },
  linked: true,
  
  updatePanel: (panel, updates) =>
    set((state) => ({
      [`panel${panel}`]: { ...state[`panel${panel}` as keyof AppState] as PanelState, ...updates },
    })),
  
  toggleLinked: () => set((state) => ({ linked: !state.linked })),
}));
