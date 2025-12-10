/**
 * Core type definitions for the Anatomy Explorer
 * 
 * These types define the data model for anatomical structures,
 * supporting both fitness enthusiasts and clinical/educational use.
 */

// ============================================================
// STRUCTURE IDENTITY
// ============================================================

export type StructureType = 
  | 'bone' 
  | 'muscle' 
  | 'tendon' 
  | 'ligament' 
  | 'cartilage' 
  | 'fascia'
  | 'organ';

export type AnatomicalSystem = 
  | 'skeletal' 
  | 'muscular' 
  | 'cardiovascular' 
  | 'nervous' 
  | 'digestive'
  | 'respiratory';

/**
 * Represents a single anatomical structure (bone, muscle, etc.)
 */
export interface AnatomicalStructure {
  /** Unique identifier, e.g., "rectus_abdominis" */
  id: string;
  
  /** Reference to the mesh name in the glTF file */
  meshId: string;
  
  /** User-friendly name for fitness audience, e.g., "Six-pack muscle" */
  commonName: string;
  
  /** Proper anatomical name, e.g., "Rectus abdominis" */
  anatomicalName: string;
  
  /** Latin terminology (optional), e.g., "Musculus rectus abdominis" */
  latinName?: string;
  
  /** Type of structure */
  type: StructureType;
  
  /** 
   * Depth layer for visibility logic:
   * 0 = deepest (bone/organs)
   * 1 = deep muscles, ligaments
   * 2 = intermediate muscles
   * 3 = superficial muscles
   * 4 = skin/fascia
   */
  layer: number;
  
  /** Anatomical systems this structure belongs to */
  systems: AnatomicalSystem[];
  
  /** Body regions this structure belongs to (can be multiple) */
  regions: RegionId[];
}

// ============================================================
// REGIONAL ORGANIZATION
// ============================================================

/** 
 * Region identifiers for the torso MVP
 * Will expand as more body regions are added
 */
export type RegionId = 
  | 'torso'
  | 'thorax' 
  | 'abdomen' 
  | 'pelvis'
  | 'lumbar_spine'
  | 'thoracic_spine';

/**
 * Defines a body region with camera defaults for navigation
 */
export interface Region {
  id: RegionId;
  name: string;
  parentRegion?: RegionId;
  
  /** Default camera position when focusing on this region */
  defaultCameraPosition: [number, number, number];
  
  /** Default camera look-at target */
  defaultCameraTarget: [number, number, number];
  
  /** Child region IDs */
  children?: RegionId[];
}

// ============================================================
// EDUCATIONAL CONTENT
// ============================================================

/**
 * Muscle-specific details
 */
export interface MuscleDetails {
  /** Where the muscle attaches (proximal) */
  origin: string[];
  
  /** Where the muscle attaches (distal) */
  insertion: string[];
  
  /** What movements the muscle performs */
  actions: string[];
  
  /** Nerve supply (clinical) */
  innervation?: string;
  
  /** Tips for fitness audience */
  fitnessNotes?: string;
  
  /** Common exercises that target this muscle */
  exercises?: string[];
}

/**
 * Bone-specific details
 */
export interface BoneDetails {
  /** Named features on the bone */
  landmarks: string[];
  
  /** Joints formed with other bones */
  articulations: string[];
  
  /** Clinical relevance */
  clinicalNotes?: string;
}

/**
 * Rich educational content for a structure
 * Stored separately to allow for independent updates
 */
export interface StructureContent {
  structureId: string;
  
  /** Brief description for fitness audience */
  simpleDescription: string;
  
  /** Detailed description for clinical/educational use */
  clinicalDescription: string;
  
  /** Muscle-specific information */
  muscleDetails?: MuscleDetails;
  
  /** Bone-specific information */
  boneDetails?: BoneDetails;
  
  /** IDs of anatomically related structures */
  relatedStructures: string[];
  
  /** Clinical significance, injury patterns, etc. */
  clinicalRelevance?: string;
  
  /** External resources */
  externalLinks?: Array<{ label: string; url: string }>;
}

// ============================================================
// RENDERING CONFIGURATION
// ============================================================

/**
 * Visual configuration for rendering a structure
 */
export interface RenderConfig {
  structureId: string;
  
  /** Base color (hex) */
  defaultColor: string;
  
  /** Color when hovered/selected (hex) */
  highlightColor: string;
  
  /** Opacity (0-1) for layering effects */
  opacity: number;
  
  /** Minimum zoom level at which this structure becomes visible */
  visibleAtZoomLevel: number;
  
  /** Offset for label placement relative to structure center */
  labelAnchorOffset: [number, number, number];
}

// ============================================================
// APPLICATION STATE
// ============================================================

/**
 * View mode affects which description/terminology is shown
 */
export type ViewMode = 'fitness' | 'clinical';

/**
 * Current visibility state for structure layers
 */
export interface LayerVisibility {
  bones: boolean;
  muscles: boolean;
  tendons: boolean;
  ligaments: boolean;
  organs: boolean;
}

/**
 * Camera state
 */
export interface CameraState {
  position: [number, number, number];
  target: [number, number, number];
  zoom: number;
}
