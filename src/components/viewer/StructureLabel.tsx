import { Html } from '@react-three/drei';
import { useAnatomyStore, useActiveStructureId } from '@/store';
import { getStructureById, getRenderConfig } from '@/data';

/**
 * Floating label that appears when hovering over or selecting a structure.
 * Positioned in 3D space near the structure.
 */
export function StructureLabel() {
  const activeId = useActiveStructureId();
  const viewMode = useAnatomyStore((state) => state.viewMode);
  const selectedStructureId = useAnatomyStore((state) => state.selectedStructureId);

  if (!activeId) return null;

  const structure = getStructureById(activeId);
  const renderConfig = getRenderConfig(activeId);

  if (!structure) return null;

  // Use common name for fitness mode, anatomical name for clinical
  const displayName = viewMode === 'fitness' 
    ? structure.commonName 
    : structure.anatomicalName;

  // Get label position from render config, or use default
  const labelOffset = renderConfig?.labelAnchorOffset ?? [0, 0.3, 0];
  
  // Approximate structure position (will be more accurate with real models)
  const structurePositions: Record<string, [number, number, number]> = {
    ribcage: [0, 0.2, 0],
    sternum: [0, 0.2, 0.15],
    thoracic_vertebrae: [0, 0.25, -0.2],
    lumbar_vertebrae: [0, -0.2, -0.18],
    pelvis_bone: [0, -0.5, 0],
    rectus_abdominis: [0, -0.1, 0.2],
    external_oblique: [0.25, -0.05, 0.15],
    internal_oblique: [0.22, -0.05, 0.12],
    transversus_abdominis: [0, -0.1, 0.08],
    pectoralis_major: [0.18, 0.35, 0.18],
    serratus_anterior: [0.35, 0.15, 0.1],
    intercostals: [0.2, 0.2, 0.1],
    erector_spinae: [0, 0, -0.25],
    latissimus_dorsi: [0.3, 0.1, -0.15],
    diaphragm: [0, 0.05, 0],
  };

  const basePosition = structurePositions[activeId] ?? [0, 0, 0];
  const position: [number, number, number] = [
    basePosition[0] + labelOffset[0],
    basePosition[1] + labelOffset[1] + 0.15,
    basePosition[2] + labelOffset[2],
  ];

  const isSelected = selectedStructureId === activeId;

  return (
    <Html
      position={position}
      center
      distanceFactor={2}
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
        
        {/* Show secondary name on selection */}
        {isSelected && viewMode === 'fitness' && structure.anatomicalName !== structure.commonName && (
          <span className="block text-xs text-surface-400 mt-0.5">
            {structure.anatomicalName}
          </span>
        )}
        {isSelected && viewMode === 'clinical' && structure.latinName && (
          <span className="block text-xs text-surface-400 italic mt-0.5">
            {structure.latinName}
          </span>
        )}
        
        {/* Structure type badge */}
        <span className={`
          inline-block mt-1 px-1.5 py-0.5 rounded text-[10px] uppercase tracking-wide
          ${structure.type === 'bone' ? 'bg-anatomy-bone/20 text-anatomy-bone' : ''}
          ${structure.type === 'muscle' ? 'bg-anatomy-muscle/20 text-red-300' : ''}
          ${structure.type === 'tendon' ? 'bg-anatomy-tendon/20 text-anatomy-tendon' : ''}
          ${structure.type === 'organ' ? 'bg-anatomy-organ/20 text-pink-300' : ''}
        `}>
          {structure.type}
        </span>
      </div>
    </Html>
  );
}
