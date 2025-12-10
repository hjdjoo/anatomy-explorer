import { useProgress, Html } from '@react-three/drei';

/**
 * Loading indicator shown while 3D models are loading.
 * Uses drei's Html component to render DOM elements in 3D space.
 */
export function LoadingIndicator() {
  const { progress, active } = useProgress();

  if (!active) return null;

  return (
    <Html center>
      <div className="flex flex-col items-center gap-3 text-surface-200">
        {/* Animated skeleton */}
        <div className="relative w-12 h-16">
          <svg viewBox="0 0 48 64" className="w-full h-full animate-pulse">
            {/* Simplified skeleton icon */}
            <ellipse cx="24" cy="8" rx="6" ry="8" fill="currentColor" opacity="0.6" />
            <rect x="22" y="16" width="4" height="20" fill="currentColor" opacity="0.5" />
            <rect x="12" y="20" width="24" height="3" rx="1" fill="currentColor" opacity="0.4" />
            <rect x="14" y="24" width="20" height="2" rx="1" fill="currentColor" opacity="0.3" />
            <rect x="16" y="27" width="16" height="2" rx="1" fill="currentColor" opacity="0.3" />
            <ellipse cx="18" cy="45" rx="6" ry="8" fill="currentColor" opacity="0.4" />
            <ellipse cx="30" cy="45" rx="6" ry="8" fill="currentColor" opacity="0.4" />
            <rect x="16" y="52" width="4" height="12" fill="currentColor" opacity="0.3" />
            <rect x="28" y="52" width="4" height="12" fill="currentColor" opacity="0.3" />
          </svg>
        </div>
        
        {/* Progress bar */}
        <div className="w-32 h-1 bg-surface-800 rounded-full overflow-hidden">
          <div 
            className="h-full bg-surface-400 transition-all duration-300 ease-out"
            style={{ width: `${progress}%` }}
          />
        </div>
        
        {/* Progress text */}
        <span className="text-xs font-mono text-surface-400">
          Loading anatomy... {Math.round(progress)}%
        </span>
      </div>
    </Html>
  );
}
