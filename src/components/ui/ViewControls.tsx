import { useAnatomyStore } from '@/store';
import type { LayerVisibility } from '@/types';

// Layer labels for depth peeling
const DEPTH_LABELS = [
  'All Layers',
  'Remove Superficial',
  'Deep Muscles Only',
  'Bones Only',
];

/**
 * Control panel for view mode toggle, layer visibility, and depth peeling.
 */
export function ViewControls() {
  const {
    viewMode,
    toggleViewMode,
    layerVisibility,
    toggleLayer,
    showAllLayers,
    hideAllLayers,
    peelDepth,
    peelDeeper,
    restoreLayer,
    resetPeel,
    searchQuery,
    setSearchQuery,
  } = useAnatomyStore();

  const layers: Array<{ key: keyof LayerVisibility; label: string; color: string }> = [
    { key: 'bones', label: 'Bones', color: 'bg-anatomy-bone' },
    { key: 'muscles', label: 'Muscles', color: 'bg-anatomy-muscle' },
    { key: 'tendons', label: 'Tendons', color: 'bg-anatomy-tendon' },
    { key: 'ligaments', label: 'Ligaments', color: 'bg-anatomy-ligament' },
    { key: 'organs', label: 'Organs', color: 'bg-anatomy-organ' },
  ];

  return (
    <div className="absolute left-4 top-4 space-y-3 max-h-[calc(100vh-2rem)] overflow-y-auto">
      {/* Search */}
      <div className="bg-surface-900/95 backdrop-blur-xl rounded-xl border border-surface-700/50 p-3 shadow-lg">
        <div className="text-xs font-semibold text-surface-400 uppercase tracking-wide mb-2">
          Search
        </div>
        <div className="relative">
          <input
            type="text"
            placeholder="Find structure..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="w-full bg-surface-800 border border-surface-700 rounded-lg px-3 py-2 pl-9 text-sm text-surface-200 placeholder-surface-500 focus:outline-none focus:ring-2 focus:ring-accent-500/50 focus:border-accent-500"
          />
          <svg
            className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-surface-500"
            fill="none"
            viewBox="0 0 24 24"
            stroke="currentColor"
          >
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
          </svg>
          {searchQuery && (
            <button
              onClick={() => setSearchQuery('')}
              className="absolute right-2 top-1/2 -translate-y-1/2 p-1 text-surface-500 hover:text-surface-300"
            >
              <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          )}
        </div>
      </div>

      {/* Depth Peeling */}
      <div className="bg-surface-900/95 backdrop-blur-xl rounded-xl border border-surface-700/50 p-3 shadow-lg">
        <div className="text-xs font-semibold text-surface-400 uppercase tracking-wide mb-2">
          Depth Peel
        </div>
        <div className="flex items-center gap-2 mb-2">
          <button
            onClick={restoreLayer}
            disabled={peelDepth === 0}
            className={`
              flex-1 px-3 py-2 rounded-lg text-sm font-medium transition-all
              flex items-center justify-center gap-1
              ${peelDepth === 0
                ? 'bg-surface-800 text-surface-600 cursor-not-allowed'
                : 'bg-surface-800 text-surface-200 hover:bg-surface-700 active:scale-95'
              }
            `}
          >
            <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 6v6m0 0v6m0-6h6m-6 0H6" />
            </svg>
            Add
          </button>
          <button
            onClick={peelDeeper}
            disabled={peelDepth === 3}
            className={`
              flex-1 px-3 py-2 rounded-lg text-sm font-medium transition-all
              flex items-center justify-center gap-1
              ${peelDepth === 3
                ? 'bg-surface-800 text-surface-600 cursor-not-allowed'
                : 'bg-accent-600 text-white hover:bg-accent-500 active:scale-95'
              }
            `}
          >
            <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M20 12H4" />
            </svg>
            Peel
          </button>
        </div>

        {/* Depth indicator */}
        <div className="flex gap-1 mb-2">
          {[0, 1, 2, 3].map((level) => (
            <div
              key={level}
              className={`
                flex-1 h-1.5 rounded-full transition-all
                ${level <= peelDepth ? 'bg-accent-500' : 'bg-surface-700'}
              `}
            />
          ))}
        </div>
        <div className="text-xs text-surface-400 text-center">
          {DEPTH_LABELS[peelDepth]}
        </div>
        {peelDepth > 0 && (
          <button
            onClick={resetPeel}
            className="w-full mt-2 px-2 py-1 text-xs text-surface-500 hover:text-surface-300 transition-colors"
          >
            Reset to show all
          </button>
        )}
      </div>

      {/* View Mode Toggle */}
      <div className="bg-surface-900/95 backdrop-blur-xl rounded-xl border border-surface-700/50 p-3 shadow-lg">
        <div className="text-xs font-semibold text-surface-400 uppercase tracking-wide mb-2">
          View Mode
        </div>
        <div className="flex rounded-lg bg-surface-800 p-1">
          <button
            onClick={() => viewMode !== 'fitness' && toggleViewMode()}
            className={`
              flex-1 px-3 py-1.5 text-sm font-medium rounded-md transition-all
              ${viewMode === 'fitness'
                ? 'bg-surface-700 text-surface-100 shadow'
                : 'text-surface-400 hover:text-surface-300'
              }
            `}
          >
            Fitness
          </button>
          <button
            onClick={() => viewMode !== 'clinical' && toggleViewMode()}
            className={`
              flex-1 px-3 py-1.5 text-sm font-medium rounded-md transition-all
              ${viewMode === 'clinical'
                ? 'bg-surface-700 text-surface-100 shadow'
                : 'text-surface-400 hover:text-surface-300'
              }
            `}
          >
            Clinical
          </button>
        </div>
      </div>

      {/* Layer Visibility */}
      <div className="bg-surface-900/95 backdrop-blur-xl rounded-xl border border-surface-700/50 p-3 shadow-lg">
        <div className="flex items-center justify-between mb-2">
          <span className="text-xs font-semibold text-surface-400 uppercase tracking-wide">
            Structure Types
          </span>
          <div className="flex gap-1">
            <button
              onClick={showAllLayers}
              className="px-1.5 py-0.5 text-[10px] text-surface-500 hover:text-surface-300 transition-colors"
            >
              All
            </button>
            <span className="text-surface-700">|</span>
            <button
              onClick={hideAllLayers}
              className="px-1.5 py-0.5 text-[10px] text-surface-500 hover:text-surface-300 transition-colors"
            >
              None
            </button>
          </div>
        </div>
        <div className="space-y-1">
          {layers.map(({ key, label, color }) => (
            <button
              key={key}
              onClick={() => toggleLayer(key)}
              className={`
                w-full flex items-center gap-2 px-2 py-1.5 rounded-lg text-sm
                transition-all
                ${layerVisibility[key]
                  ? 'bg-surface-800 text-surface-200'
                  : 'text-surface-500 hover:bg-surface-800/50'
                }
              `}
            >
              <span className={`
                w-3 h-3 rounded-full transition-opacity
                ${color}
                ${layerVisibility[key] ? 'opacity-100' : 'opacity-30'}
              `} />
              {label}
              {layerVisibility[key] && (
                <svg className="w-4 h-4 ml-auto text-surface-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                </svg>
              )}
            </button>
          ))}
        </div>
      </div>

      {/* Keyboard shortcuts hint */}
      <div className="bg-surface-900/80 backdrop-blur-xl rounded-lg border border-surface-700/50 px-3 py-2 text-xs text-surface-500">
        <div className="flex items-center gap-2">
          <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
          <span>Click structure for details</span>
        </div>
      </div>
    </div>
  );
}
