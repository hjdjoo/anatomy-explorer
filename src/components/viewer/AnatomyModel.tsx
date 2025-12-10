import { useRef, useState, useMemo } from 'react';
import { useFrame } from '@react-three/fiber';
import * as THREE from 'three';
import { useAnatomyStore } from '@/store';
import { torsoStructures, getRenderConfig } from '@/data';
import type { AnatomicalStructure } from '@/types';

/**
 * Individual structure mesh component with hover/selection handling.
 * This is a placeholder implementation using basic geometry.
 * Will be replaced with actual loaded meshes from glTF.
 */
function StructureMesh({ 
  structure,
  position,
  geometry,
}: { 
  structure: AnatomicalStructure;
  position: [number, number, number];
  geometry: THREE.BufferGeometry;
}) {
  const meshRef = useRef<THREE.Mesh>(null);
  const [hovered, setHovered] = useState(false);
  
  const {
    hoveredStructureId,
    selectedStructureId,
    setHoveredStructure,
    setSelectedStructure,
    layerVisibility,
    zoomLevel,
  } = useAnatomyStore();

  const renderConfig = getRenderConfig(structure.id);
  const isSelected = selectedStructureId === structure.id;
  const isHighlighted = hovered || isSelected || hoveredStructureId === structure.id;

  // Check if this structure type is visible
  const typeVisibilityKey = structure.type === 'bone' ? 'bones' :
                            structure.type === 'muscle' ? 'muscles' :
                            structure.type === 'tendon' ? 'tendons' :
                            structure.type === 'ligament' ? 'ligaments' :
                            structure.type === 'organ' ? 'organs' : 'muscles';
  
  const isTypeVisible = layerVisibility[typeVisibilityKey as keyof typeof layerVisibility];
  
  // Check zoom-based visibility
  const isZoomVisible = !renderConfig || zoomLevel >= renderConfig.visibleAtZoomLevel;
  
  const isVisible = isTypeVisible && isZoomVisible;

  // Material colors
  const baseColor = renderConfig?.defaultColor ?? '#888888';
  const highlightColor = renderConfig?.highlightColor ?? '#ffffff';
  const opacity = renderConfig?.opacity ?? 1;

  // Animate highlight effect
  useFrame(() => {
    if (meshRef.current && meshRef.current.material instanceof THREE.MeshStandardMaterial) {
      const targetColor = isHighlighted ? highlightColor : baseColor;
      meshRef.current.material.color.lerp(new THREE.Color(targetColor), 0.1);
      
      // Slight scale pulse when selected
      const targetScale = isSelected ? 1.02 : 1;
      meshRef.current.scale.lerp(new THREE.Vector3(targetScale, targetScale, targetScale), 0.1);
    }
  });

  if (!isVisible) return null;

  return (
    <mesh
      ref={meshRef}
      position={position}
      geometry={geometry}
      onPointerOver={(e) => {
        e.stopPropagation();
        setHovered(true);
        setHoveredStructure(structure.id);
        document.body.style.cursor = 'pointer';
      }}
      onPointerOut={(e) => {
        e.stopPropagation();
        setHovered(false);
        setHoveredStructure(null);
        document.body.style.cursor = 'auto';
      }}
      onClick={(e) => {
        e.stopPropagation();
        setSelectedStructure(isSelected ? null : structure.id);
      }}
      castShadow
      receiveShadow
    >
      <meshStandardMaterial
        color={baseColor}
        transparent={opacity < 1}
        opacity={opacity}
        roughness={0.6}
        metalness={0.1}
        side={THREE.DoubleSide}
      />
    </mesh>
  );
}

/**
 * Main anatomy model component.
 * 
 * CURRENT: Renders placeholder geometry for development.
 * FUTURE: Will load glTF from Z-Anatomy export and render actual meshes.
 */
export function AnatomyModel() {
  const clearSelection = useAnatomyStore((state) => state.clearSelection);

  // Create placeholder geometries
  // These approximate the shapes and positions of torso structures
  const geometries = useMemo(() => ({
    // Bones
    ribcage: new THREE.TorusGeometry(0.4, 0.08, 8, 24),
    sternum: new THREE.BoxGeometry(0.08, 0.4, 0.05),
    thoracic_vertebrae: new THREE.CylinderGeometry(0.06, 0.06, 0.5, 8),
    lumbar_vertebrae: new THREE.CylinderGeometry(0.08, 0.08, 0.3, 8),
    pelvis_bone: new THREE.TorusGeometry(0.25, 0.06, 6, 16, Math.PI),

    // Muscles
    rectus_abdominis: new THREE.BoxGeometry(0.2, 0.5, 0.08),
    external_oblique: new THREE.BoxGeometry(0.15, 0.4, 0.06),
    internal_oblique: new THREE.BoxGeometry(0.12, 0.35, 0.05),
    transversus_abdominis: new THREE.BoxGeometry(0.25, 0.4, 0.03),
    pectoralis_major: new THREE.SphereGeometry(0.15, 16, 12, 0, Math.PI * 2, 0, Math.PI * 0.6),
    serratus_anterior: new THREE.BoxGeometry(0.08, 0.2, 0.04),
    intercostals: new THREE.BoxGeometry(0.3, 0.02, 0.05),
    erector_spinae: new THREE.CylinderGeometry(0.06, 0.04, 0.8, 8),
    latissimus_dorsi: new THREE.PlaneGeometry(0.4, 0.5),
    diaphragm: new THREE.CircleGeometry(0.35, 24),
  }), []);

  // Placeholder positions for structures
  const positions: Record<string, [number, number, number]> = {
    // Bones
    ribcage: [0, 0.2, 0],
    sternum: [0, 0.2, 0.15],
    thoracic_vertebrae: [0, 0.25, -0.2],
    lumbar_vertebrae: [0, -0.2, -0.18],
    pelvis_bone: [0, -0.5, 0],

    // Muscles
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

  return (
    <group
      // Clear selection when clicking empty space
      onClick={(e) => {
        if (e.eventObject === e.object) {
          clearSelection();
        }
      }}
    >
      {/* Render all structures */}
      {torsoStructures.map((structure) => {
        const geometry = geometries[structure.id as keyof typeof geometries];
        const position = positions[structure.id] ?? [0, 0, 0];
        
        if (!geometry) {
          console.warn(`No geometry found for structure: ${structure.id}`);
          return null;
        }

        return (
          <StructureMesh
            key={structure.id}
            structure={structure}
            position={position}
            geometry={geometry}
          />
        );
      })}

      {/* Center reference (hidden in production) */}
      {process.env.NODE_ENV === 'development' && (
        <axesHelper args={[0.5]} />
      )}
    </group>
  );
}
