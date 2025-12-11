import { AnatomyCanvas } from '@/components/viewer';
import { InfoPanel, ViewControls } from '@/components/ui';
import { Header } from '@/components/layout';

/**
 * Main application component.
 * Combines the 3D viewer with UI overlays.
 */
function App() {
  return (
    <div className="w-screen h-screen bg-surface-950 overflow-hidden relative">
      {/* Background gradient */}
      <div className="absolute inset-0 bg-gradient-to-b from-surface-900 via-surface-950 to-surface-950" />

      {/* Subtle grid pattern */}
      <div
        className="absolute inset-0 opacity-[0.02]"
        style={{
          backgroundImage: `
            linear-gradient(to right, rgb(255 255 255 / 0.1) 1px, transparent 1px),
            linear-gradient(to bottom, rgb(255 255 255 / 0.1) 1px, transparent 1px)
          `,
          backgroundSize: '40px 40px',
        }}
      />

      {/* 3D Canvas */}
      <div className="absolute inset-0">
        <AnatomyCanvas />
      </div>

      {/* UI Overlays */}
      <Header />
      <ViewControls />
      <InfoPanel />

      {/* Instructions overlay for first-time users */}
      <div className="absolute bottom-4 left-1/2 -translate-x-1/2 pointer-events-none">
        <div className="bg-surface-900/80 backdrop-blur-xl rounded-full px-4 py-2 border border-surface-700/50">
          <p className="text-xs text-surface-400 flex items-center gap-3">
            <span className="flex items-center gap-1.5">
              <kbd className="px-1.5 py-0.5 bg-surface-800 rounded text-surface-300 font-mono">Drag</kbd>
              <span>Rotate</span>
            </span>
            <span className="text-surface-700">•</span>
            <span className="flex items-center gap-1.5">
              <kbd className="px-1.5 py-0.5 bg-surface-800 rounded text-surface-300 font-mono">Scroll</kbd>
              <span>Zoom</span>
            </span>
            <span className="text-surface-700">•</span>
            <span className="flex items-center gap-1.5">
              <kbd className="px-1.5 py-0.5 bg-surface-800 rounded text-surface-300 font-mono">Click</kbd>
              <span>Select</span>
            </span>
          </p>
        </div>
      </div>
    </div>
  );
}

export default App;
