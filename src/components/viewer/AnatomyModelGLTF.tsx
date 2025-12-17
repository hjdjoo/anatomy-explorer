import { useEffect, useMemo, useRef, useState } from 'react';
import { useGLTF } from '@react-three/drei';
import { useFrame } from '@react-three/fiber';
import * as THREE from 'three';
import { useAnatomyStore } from '@/store';
import type { LayerVisibility } from '@/types';

// Import the metadata
import torsoMetadata from '@/data/torso_metadata.json';

// ============================================================
// DEBUG CONFIGURATION
// ============================================================

const DEBUG_ENABLED = false;
const DEBUG_STRUCTURES = ['inguinal_ligament', 'pubic_ligament'];

function debugLog(meshName: string, message: string, data?: unknown) {
  if (!DEBUG_ENABLED) return;
  if (!DEBUG_STRUCTURES.some(s => meshName.toLowerCase().includes(s.toLowerCase()))) return;
  console.log(`[DEBUG ${meshName}] ${message}`, data ?? '');
}

// ============================================================
// TYPES
// ============================================================

interface StructureMetadata {
  meshId: string;
  originalName: string;
  type: 'bone' | 'muscle' | 'organ' | 'tendon' | 'ligament' | 'cartilage' | 'fascia';
  layer: number;
  regions: string[];
  center: [number, number, number];
}

interface MetadataFile {
  version: string;
  source: string;
  region: string;
  structures: Record<string, StructureMetadata>;
}

interface ProcessedStructure {
  uniqueKey: string;           // Unique key for React (glTF mesh name)
  mesh: THREE.Mesh;
  metadata: StructureMetadata;
  center: THREE.Vector3;       // From metadata (trusted from V7 export)
}

// ============================================================
// CONSTANTS
// ============================================================

const TYPE_COLORS: Record<string, { default: string; highlight: string }> = {
  bone: { default: '#E8DCC4', highlight: '#FFF8E7' },
  muscle: { default: '#C41E3A', highlight: '#FF4D6A' },
  organ: { default: '#8B4557', highlight: '#A85A6F' },
  tendon: { default: '#D4A574', highlight: '#E8C9A0' },
  ligament: { default: '#8B7355', highlight: '#A89070' },
  cartilage: { default: '#A8D5BA', highlight: '#C5E8D2' },
  fascia: { default: '#D4A5A5', highlight: '#E8C5C5' },
};

const TYPE_TO_VISIBILITY_KEY: Record<string, keyof LayerVisibility> = {
  bone: 'bones',
  muscle: 'muscles',
  organ: 'organs',
  tendon: 'tendons',
  ligament: 'ligaments',
  cartilage: 'bones',
  fascia: 'muscles',
};

// ============================================================
// GLTF NAME NORMALIZATION
// ============================================================

/**
 * Normalize a glTF mesh name to match metadata keys.
 * 
 * glTF exporter adds suffixes like '001', '002' to mesh names.
 * Examples:
 *   - 'inguinal_ligament001' → 'inguinal_ligament'
 *   - 'inguinal_ligament_1001' → 'inguinal_ligament_1'
 *   - 'Hip_bone001' → 'hip_bone'
 */
function normalizeGltfName(gltfName: string): string {
  return gltfName
    .replace(/00\d+/g, '')      // Remove Blender's numeric suffixes (001, 002, etc.)
    .toLowerCase()
    .replace(/__+/g, '_')       // Clean up double underscores
    .replace(/_+$/, '');        // Remove trailing underscores
}

/**
 * Find metadata for a glTF mesh.
 * Returns the metadata key and data, or null if not found.
 */
function findMetadataForMesh(
  gltfName: string,
  structures: Record<string, StructureMetadata>
): { key: string; data: StructureMetadata } | null {
  // Try exact match first
  if (structures[gltfName]) {
    return { key: gltfName, data: structures[gltfName] };
  }

  // Try normalized name
  const normalized = normalizeGltfName(gltfName);
  if (structures[normalized]) {
    return { key: normalized, data: structures[normalized] };
  }

  // Try lowercase only
  const lowercased = gltfName.toLowerCase();
  if (structures[lowercased]) {
    return { key: lowercased, data: structures[lowercased] };
  }

  return null;
}

// ============================================================
// STRUCTURE FILTERING
// ============================================================

const EXCLUDE_NAME_PATTERNS = [
  'plane', 'planes', 'flexion', 'extension', 'rotation', 'abduction',
  'adduction', 'pronation', 'supination', 'circumduction',
  'lateral_rectus_muscle', 'medial_rectus_muscle', 'superior_rectus_muscle',
  'inferior_rectus_muscle', 'superior_oblique_muscle', 'inferior_oblique_muscle',
  'pronator_quadratus', 'pronator_teres', 'supinator', 'oblique_cord',
  'plantae', 'popliteal', 'femoris', 'tibial', 'fibular', 'peroneal',
  'gastrocnemius', 'soleus', 'plantaris', 'lymph_node',
];

const EXCLUDE_SUFFIX_PATTERNS = [
  /_i$/i,
  /_o\d*[lr]$/i,
  /_e\d+[lr]$/i,
  /_el$/i,
  /_er$/i,
];

const EXCLUDE_TYPES = ['organ'];

function shouldRenderByTypeAndName(metadata: StructureMetadata): boolean {
  if (EXCLUDE_TYPES.includes(metadata.type)) {
    return false;
  }

  const nameLower = metadata.meshId.toLowerCase();

  if (EXCLUDE_NAME_PATTERNS.some(pattern => nameLower.includes(pattern))) {
    return false;
  }

  if (EXCLUDE_SUFFIX_PATTERNS.some(pattern => pattern.test(metadata.meshId))) {
    return false;
  }

  return true;
}

// ============================================================
// MESH PROCESSING (SIMPLIFIED - TRUST METADATA)
// ============================================================

/**
 * Process a mesh from the glTF scene.
 * Simply clones geometry with world transforms baked in.
 * Center comes from metadata (trusted from V7 export).
 */
function processGLTFMesh(
  child: THREE.Mesh,
  metadata: StructureMetadata,
  uniqueKey: string
): ProcessedStructure {
  debugLog(child.name, 'Processing mesh');

  // Clone geometry and bake world transform into vertices
  const clonedGeometry = child.geometry.clone();
  clonedGeometry.applyMatrix4(child.matrixWorld);

  // Create new mesh at origin (transform is baked into vertices)
  const newMesh = new THREE.Mesh(clonedGeometry);
  newMesh.name = child.name;

  // Use center from metadata (V7 export computed this correctly)
  const center = new THREE.Vector3(...metadata.center);

  debugLog(child.name, 'Center from metadata:', metadata.center);

  return {
    uniqueKey,
    mesh: newMesh,
    metadata,
    center,
  };
}

// ============================================================
// STRUCTURE MESH COMPONENT
// ============================================================

interface StructureMeshProps {
  structure: ProcessedStructure;
}

function StructureMesh({ structure }: StructureMeshProps) {
  const { mesh, metadata, center } = structure;
  const materialRef = useRef<THREE.MeshStandardMaterial>(null);
  const meshRef = useRef<THREE.Mesh>(null);
  const [hovered, setHovered] = useState(false);
  const animatedOpacity = useRef(1);

  const {
    hoveredStructureId,
    selectedStructureId,
    setHoveredStructure,
    setSelectedStructure,
    layerVisibility,
    peelDepth,
    searchQuery,
  } = useAnatomyStore();

  const colors = TYPE_COLORS[metadata.type] || TYPE_COLORS.muscle;
  const isSelected = selectedStructureId === metadata.meshId;

  const matchesSearch = searchQuery.length > 1 && (
    metadata.meshId.toLowerCase().includes(searchQuery.toLowerCase()) ||
    metadata.originalName.toLowerCase().includes(searchQuery.toLowerCase())
  );

  const isHighlighted = hovered || isSelected || hoveredStructureId === metadata.meshId || matchesSearch;

  const visibilityKey = TYPE_TO_VISIBILITY_KEY[metadata.type] || 'muscles';
  const isTypeVisible = layerVisibility[visibilityKey];

  const maxVisibleLayer = 3 - peelDepth;
  const isPeeled = metadata.layer > maxVisibleLayer;
  const shouldPeel = isPeeled && !matchesSearch;
  const targetOpacity = shouldPeel ? 0 : (metadata.type === 'bone' ? 1 : 0.9);

  const material = useMemo(() => {
    return new THREE.MeshStandardMaterial({
      color: colors.default,
      roughness: 0.6,
      metalness: 0.1,
      transparent: true,
      opacity: metadata.type === 'bone' ? 1 : 0.9,
      side: THREE.DoubleSide,
      depthWrite: true,
    });
  }, [colors.default, metadata.type]);

  useFrame(() => {
    if (!materialRef.current) return;

    let targetColor = colors.default;
    if (matchesSearch) {
      targetColor = '#FFD700';
    } else if (isHighlighted && !shouldPeel) {
      targetColor = colors.highlight;
    }
    materialRef.current.color.lerp(new THREE.Color(targetColor), 0.1);

    animatedOpacity.current += (targetOpacity - animatedOpacity.current) * 0.08;
    materialRef.current.opacity = animatedOpacity.current;
    materialRef.current.depthWrite = animatedOpacity.current > 0.5;
  });

  if (!isTypeVisible) return null;

  const isInteractive = animatedOpacity.current > 0.1;

  useEffect(() => {
    if (isSelected) {
      debugLog(metadata.meshId, 'SELECTED - Center:', center.toArray());
    }
  }, [isSelected, metadata.meshId, center]);

  return (
    <mesh
      ref={meshRef}
      geometry={mesh.geometry}
      raycast={isInteractive ? undefined : () => { }}
      onPointerOver={(e) => {
        if (!isInteractive) return;
        e.stopPropagation();
        setHovered(true);
        setHoveredStructure(metadata.meshId);
        document.body.style.cursor = 'pointer';
      }}
      onPointerOut={(e) => {
        if (!isInteractive) return;
        e.stopPropagation();
        setHovered(false);
        setHoveredStructure(null);
        document.body.style.cursor = 'auto';
      }}
      onClick={(e) => {
        if (!isInteractive) return;
        e.stopPropagation();
        setSelectedStructure(isSelected ? null : metadata.meshId);
      }}
    >
      <primitive object={material} ref={materialRef} attach="material" />
    </mesh>
  );
}

// ============================================================
// MAIN ANATOMY MODEL COMPONENT
// ============================================================

export function AnatomyModelGLTF() {
  const { scene } = useGLTF('/models/torso.glb');
  const clearSelection = useAnatomyStore((state) => state.clearSelection);
  const setLoading = useAnatomyStore((state) => state.setLoading);

  const metadata = JSON.parse(JSON.stringify(torsoMetadata)) as MetadataFile;

  const processedStructures = useMemo(() => {
    const structures: ProcessedStructure[] = [];
    const usedMetadataKeys = new Set<string>();  // Track which metadata entries have been used
    let skippedByTypeOrName = 0;
    let skippedDuplicate = 0;
    let unmatchedCount = 0;

    // Update world matrices for the entire scene hierarchy
    scene.updateMatrixWorld(true);

    if (DEBUG_ENABLED) {
      console.log('='.repeat(60));
      console.log('[DEBUG] Processing anatomy model...');
      console.log('='.repeat(60));
    }

    scene.traverse((child) => {
      if (child instanceof THREE.Mesh) {
        const gltfMeshName = child.name;

        // Find matching metadata
        const match = findMetadataForMesh(gltfMeshName, metadata.structures);

        if (!match) {
          unmatchedCount++;
          return;
        }

        // Skip if we've already used this metadata entry (prevents duplicates)
        if (usedMetadataKeys.has(match.key)) {
          skippedDuplicate++;
          debugLog(gltfMeshName, `Skipping duplicate for metadata key: ${match.key}`);
          return;
        }

        const structureData = match.data;

        // Filter by type and name patterns
        if (!shouldRenderByTypeAndName(structureData)) {
          skippedByTypeOrName++;
          return;
        }

        // Mark this metadata key as used
        usedMetadataKeys.add(match.key);

        // Process the mesh - use gltfMeshName as unique key to avoid React key conflicts
        const processed = processGLTFMesh(child, structureData, gltfMeshName);
        structures.push(processed);
      }
    });

    console.log(`Loaded ${structures.length} structures`);
    console.log(`  Skipped: ${skippedByTypeOrName} (filtered), ${skippedDuplicate} (duplicate), ${unmatchedCount} (no metadata)`);

    return structures;
  }, [scene, metadata]);

  useEffect(() => {
    setLoading(false);
  }, [setLoading]);

  // Calculate model bounds from all structures
  const modelCenter = useMemo(() => {
    if (processedStructures.length === 0) {
      return new THREE.Vector3();
    }

    const box = new THREE.Box3();
    processedStructures.forEach(({ mesh }) => {
      const meshBox = new THREE.Box3().setFromObject(mesh);
      box.union(meshBox);
    });

    return box.getCenter(new THREE.Vector3());
  }, [processedStructures]);

  return (
    <group
      position={[-modelCenter.x, -modelCenter.y, -modelCenter.z]}
      onClick={(e) => {
        if (e.eventObject === e.object) {
          clearSelection();
        }
      }}
    >
      {processedStructures.map((structure) => (
        <StructureMesh
          key={structure.uniqueKey}  // Use unique glTF mesh name, not metadata meshId
          structure={structure}
        />
      ))}
    </group>
  );
}

useGLTF.preload('/models/torso.glb');