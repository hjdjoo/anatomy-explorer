import { Html } from '@react-three/drei';
import { useAnatomyStore, useActiveStructureId } from '@/store';
import torsoMetadata from '@/data/torso_metadata.json';

// Type for metadata structure
interface StructureMetadata {
  meshId: string;
  originalName: string;
  type: string;
  layer: number;
  regions: string[];
  center: [number, number, number];
}

// Quick name formatter for mesh IDs
function formatName(meshId: string): { common: string; anatomical: string } {
  // Remove suffixes like _j, _i, _1
  let clean = meshId
    .replace(/_[jio]$/, '')
    .replace(/_\d+$/, '')
    .replace(/_ol$/, '')
    .replace(/_or$/, '')
    .replace(/[()]/g, '');

  // Title case
  const words = clean.split('_').filter(Boolean);
  const titleCased = words
    .map(word => word.charAt(0).toUpperCase() + word.slice(1).toLowerCase())
    .join(' ');

  return { common: titleCased, anatomical: titleCased };
}

/**
 * Floating label that appears when hovering over or selecting a structure.
 * Positioned in 3D space near the structure.
 */
export function StructureLabel() {
  const activeId = useActiveStructureId();
  const viewMode = useAnatomyStore((state) => state.viewMode);
  const selectedStructureId = useAnatomyStore((state) => state.selectedStructureId);

  if (!activeId) return null;

  // Get structure data from metadata
  const metadata = JSON.parse(JSON.stringify(torsoMetadata)) as { structures: Record<string, StructureMetadata> };
  const structureData = metadata.structures[activeId];

  if (!structureData) return null;

  const names = formatName(activeId);

  // Use common name for fitness mode, anatomical name for clinical
  const displayName = viewMode === 'fitness' ? names.common : names.anatomical;

  // Use the center from metadata for label position
  const position: [number, number, number] = [
    structureData.center[0],
    structureData.center[1] + 0.05,
    structureData.center[2],
  ];

  const isSelected = selectedStructureId === activeId;

  return (
    <Html
      position={position}
      center
      distanceFactor={1.5}
      style={{
        pointerEvents: 'none',
        userSelect: 'none',
      }}
    >
      <div
        className={`
          px-3 py-1.5 rounded-lg 
          backdrop-blur-md
          border border-surface-700/50
          shadow-lg shadow-black/20
          transition-all duration-200
          ${isSelected
            ? 'bg-surface-800/95 scale-105'
            : 'bg-surface-900/90'
          }
        `}
      >
        <span className="text-sm font-medium text-surface-100 whitespace-nowrap">
          {displayName}
        </span>

        {/* Show regions on selection */}
        {isSelected && structureData.regions.length > 0 && (
          <span className="block text-xs text-surface-400 mt-0.5">
            {structureData.regions.join(', ')}
          </span>
        )}

        {/* Structure type badge */}
        <span className={`
          inline-block mt-1 px-1.5 py-0.5 rounded text-[10px] uppercase tracking-wide
          ${structureData.type === 'bone' ? 'bg-anatomy-bone/20 text-anatomy-bone' : ''}
          ${structureData.type === 'muscle' ? 'bg-anatomy-muscle/20 text-red-300' : ''}
          ${structureData.type === 'tendon' ? 'bg-anatomy-tendon/20 text-anatomy-tendon' : ''}
          ${structureData.type === 'organ' ? 'bg-anatomy-organ/20 text-pink-300' : ''}
        `}>
          {structureData.type}
        </span>
      </div>
    </Html>
  );
}
