/**
 * State selectors
 */
import { useStore } from './store';

export const usePanelA = () => useStore((state) => state.panelA);
export const usePanelB = () => useStore((state) => state.panelB);
export const usePanelC = () => useStore((state) => state.panelC);
export const useLinked = () => useStore((state) => state.linked);
export const useUpdatePanel = () => useStore((state) => state.updatePanel);
export const useToggleLinked = () => useStore((state) => state.toggleLinked);
