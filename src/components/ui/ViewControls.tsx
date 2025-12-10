import { useAnatomyStore } from '@/store';
import type { LayerVisibility } from '@/types';

/**
 * Control panel for view mode toggle and layer visibility.
 */
export function ViewControls() {
  const {
    viewMode,
    toggleViewMode,
    layerVisibility,
    toggleLayer,
    showAllLayers,
    hideAllLayers,
  } = useAnatomyStore();

  const layers: Array<{ key: keyof LayerVisibility; label: string; color: string }> = [
    { key: 'bones', label: 'Bones', color: 'bg-anatomy-bone' },
    { key: 'muscles', label: 'Muscles', color: 'bg-anatomy-muscle' },
    { key: 'tendons', label: 'Tendons', color: 'bg-anatomy-tendon' },
    { key: 'ligaments', label: 'Ligaments', color: 'bg-anatomy-ligament' },
    { key: 'organs', label: 'Organs', color: 'bg-anatomy-organ' },
  ];

  return (
    <div className="absolute left-4 top-24 space-y-3">
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
            Layers
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

      {/* Zoom hint */}
      <div className="bg-surface-900/80 backdrop-blur-xl rounded-lg border border-surface-700/50 px-3 py-2 text-xs text-surface-500">
        <div className="flex items-center gap-2">
          <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0zM10 7v6m3-3H7" />
          </svg>
          <span>Zoom to reveal deeper layers</span>
        </div>
      </div>
    </div>
  );
}
