import { create } from 'zustand';
import { subscribeWithSelector } from 'zustand/middleware';
import type {
  ViewMode,
  LayerVisibility,
  // CameraState,
  RegionId,
  // AnatomicalStructure 
} from '@/types';

// ============================================================
// STORE STATE INTERFACE
// ============================================================

interface AnatomyState {
  // === Selection State ===
  /** Currently hovered structure ID */
  hoveredStructureId: string | null;

  /** Currently selected (clicked) structure ID */
  selectedStructureId: string | null;

  /** Currently focused body region */
  activeRegion: RegionId;

  // === View Settings ===
  /** Fitness vs clinical terminology/descriptions */
  viewMode: ViewMode;

  /** Which structure types are visible */
  layerVisibility: LayerVisibility;

  /** Current zoom level (affects layer auto-visibility) */
  zoomLevel: number;

  /** 
   * Depth peel level (0-3)
   * 0 = show all layers (superficial to deep)
   * 1 = hide superficial (layer 3), show layers 0-2
   * 2 = hide superficial + intermediate, show layers 0-1
   * 3 = show only deepest (bones, layer 0)
   */
  peelDepth: number;

  // === UI State ===
  /** Whether the info panel is expanded */
  infoPanelOpen: boolean;

  /** Whether settings panel is open */
  settingsPanelOpen: boolean;

  /** Search query for structure search */
  searchQuery: string;

  // === Loading State ===
  /** Whether models are currently loading */
  isLoading: boolean;

  /** Loading progress (0-100) */
  loadingProgress: number;
}

interface AnatomyActions {
  // === Selection Actions ===
  setHoveredStructure: (id: string | null) => void;
  setSelectedStructure: (id: string | null) => void;
  clearSelection: () => void;
  setActiveRegion: (region: RegionId) => void;

  // === View Actions ===
  setViewMode: (mode: ViewMode) => void;
  toggleViewMode: () => void;
  setLayerVisibility: (layer: keyof LayerVisibility, visible: boolean) => void;
  toggleLayer: (layer: keyof LayerVisibility) => void;
  showAllLayers: () => void;
  hideAllLayers: () => void;
  setZoomLevel: (zoom: number) => void;

  // === Depth Peeling Actions ===
  /** Peel one layer deeper (increase peelDepth) */
  peelDeeper: () => void;
  /** Restore one layer (decrease peelDepth) */
  restoreLayer: () => void;
  /** Set specific peel depth */
  setPeelDepth: (depth: number) => void;
  /** Reset to show all layers */
  resetPeel: () => void;

  // === UI Actions ===
  toggleInfoPanel: () => void;
  setInfoPanelOpen: (open: boolean) => void;
  toggleSettingsPanel: () => void;
  setSearchQuery: (query: string) => void;

  // === Loading Actions ===
  setLoading: (loading: boolean) => void;
  setLoadingProgress: (progress: number) => void;
}

type AnatomyStore = AnatomyState & AnatomyActions;

// ============================================================
// DEFAULT STATE
// ============================================================

const defaultLayerVisibility: LayerVisibility = {
  bones: true,
  muscles: true,
  tendons: true,
  ligaments: true,
  organs: true,
};

// ============================================================
// STORE IMPLEMENTATION
// ============================================================

export const useAnatomyStore = create<AnatomyStore>()(
  subscribeWithSelector((set, _get) => ({
    // === Initial State ===
    hoveredStructureId: null,
    selectedStructureId: null,
    activeRegion: 'torso',
    viewMode: 'fitness',
    layerVisibility: defaultLayerVisibility,
    zoomLevel: 1,
    peelDepth: 0, // 0 = show all layers
    infoPanelOpen: false,
    settingsPanelOpen: false,
    searchQuery: '',
    isLoading: true,
    loadingProgress: 0,

    // === Selection Actions ===
    setHoveredStructure: (id) => set({ hoveredStructureId: id }),

    setSelectedStructure: (id) => set({
      selectedStructureId: id,
      // Auto-open info panel when selecting a structure
      infoPanelOpen: id !== null,
    }),

    clearSelection: () => set({
      selectedStructureId: null,
      hoveredStructureId: null,
    }),

    setActiveRegion: (region) => set({ activeRegion: region }),

    // === View Actions ===
    setViewMode: (mode) => set({ viewMode: mode }),

    toggleViewMode: () => set((state) => ({
      viewMode: state.viewMode === 'fitness' ? 'clinical' : 'fitness'
    })),

    setLayerVisibility: (layer, visible) => set((state) => ({
      layerVisibility: {
        ...state.layerVisibility,
        [layer]: visible,
      },
    })),

    toggleLayer: (layer) => set((state) => ({
      layerVisibility: {
        ...state.layerVisibility,
        [layer]: !state.layerVisibility[layer],
      },
    })),

    showAllLayers: () => set({
      layerVisibility: {
        bones: true,
        muscles: true,
        tendons: true,
        ligaments: true,
        organs: true,
      },
    }),

    hideAllLayers: () => set({
      layerVisibility: {
        bones: false,
        muscles: false,
        tendons: false,
        ligaments: false,
        organs: false,
      },
    }),

    setZoomLevel: (zoom) => set({ zoomLevel: zoom }),

    // === Depth Peeling Actions ===
    peelDeeper: () => set((state) => ({
      peelDepth: Math.min(state.peelDepth + 1, 3),
    })),

    restoreLayer: () => set((state) => ({
      peelDepth: Math.max(state.peelDepth - 1, 0),
    })),

    setPeelDepth: (depth) => set({
      peelDepth: Math.max(0, Math.min(3, depth)),
    }),

    resetPeel: () => set({ peelDepth: 0 }),

    // === UI Actions ===
    toggleInfoPanel: () => set((state) => ({
      infoPanelOpen: !state.infoPanelOpen
    })),

    setInfoPanelOpen: (open) => set({ infoPanelOpen: open }),

    toggleSettingsPanel: () => set((state) => ({
      settingsPanelOpen: !state.settingsPanelOpen
    })),

    setSearchQuery: (query) => set({ searchQuery: query }),

    // === Loading Actions ===
    setLoading: (loading) => set({ isLoading: loading }),

    setLoadingProgress: (progress) => set({ loadingProgress: progress }),
  }))
);

// ============================================================
// SELECTOR HOOKS
// ============================================================

/**
 * Get the currently hovered or selected structure for display
 */
export const useActiveStructureId = () =>
  useAnatomyStore((state) => state.selectedStructureId ?? state.hoveredStructureId);

/**
 * Check if a specific structure should be highlighted
 */
export const useIsStructureHighlighted = (structureId: string) =>
  useAnatomyStore((state) =>
    state.hoveredStructureId === structureId ||
    state.selectedStructureId === structureId
  );

/**
 * Check if a structure type is currently visible
 */
export const useIsStructureTypeVisible = (type: keyof LayerVisibility) =>
  useAnatomyStore((state) => state.layerVisibility[type]);
