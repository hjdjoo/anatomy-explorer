import type { 
  AnatomicalStructure, 
  StructureContent, 
  RenderConfig,
  Region 
} from '@/types';

// ============================================================
// REGIONS
// ============================================================

export const torsoRegions: Region[] = [
  {
    id: 'torso',
    name: 'Torso',
    defaultCameraPosition: [0, 0, 3],
    defaultCameraTarget: [0, 0, 0],
    children: ['thorax', 'abdomen', 'pelvis'],
  },
  {
    id: 'thorax',
    name: 'Thorax (Chest)',
    parentRegion: 'torso',
    defaultCameraPosition: [0, 0.3, 2],
    defaultCameraTarget: [0, 0.3, 0],
  },
  {
    id: 'abdomen',
    name: 'Abdomen',
    parentRegion: 'torso',
    defaultCameraPosition: [0, -0.1, 2],
    defaultCameraTarget: [0, -0.1, 0],
  },
  {
    id: 'pelvis',
    name: 'Pelvis',
    parentRegion: 'torso',
    defaultCameraPosition: [0, -0.5, 2],
    defaultCameraTarget: [0, -0.5, 0],
  },
  {
    id: 'thoracic_spine',
    name: 'Thoracic Spine',
    parentRegion: 'torso',
    defaultCameraPosition: [2, 0.3, 0],
    defaultCameraTarget: [0, 0.3, 0],
  },
  {
    id: 'lumbar_spine',
    name: 'Lumbar Spine',
    parentRegion: 'torso',
    defaultCameraPosition: [2, -0.2, 0],
    defaultCameraTarget: [0, -0.2, 0],
  },
];

// ============================================================
// SAMPLE STRUCTURES
// These are examples for development. Real data will come from
// Z-Anatomy export + manual enrichment.
// ============================================================

export const torsoStructures: AnatomicalStructure[] = [
  // === BONES ===
  {
    id: 'ribcage',
    meshId: 'Ribcage',
    commonName: 'Rib Cage',
    anatomicalName: 'Thoracic cage',
    latinName: 'Cavea thoracis',
    type: 'bone',
    layer: 0,
    systems: ['skeletal'],
    regions: ['thorax'],
  },
  {
    id: 'sternum',
    meshId: 'Sternum',
    commonName: 'Breastbone',
    anatomicalName: 'Sternum',
    type: 'bone',
    layer: 0,
    systems: ['skeletal'],
    regions: ['thorax'],
  },
  {
    id: 'thoracic_vertebrae',
    meshId: 'ThoracicVertebrae',
    commonName: 'Upper Back Bones',
    anatomicalName: 'Thoracic vertebrae',
    latinName: 'Vertebrae thoracicae',
    type: 'bone',
    layer: 0,
    systems: ['skeletal'],
    regions: ['thorax', 'thoracic_spine'],
  },
  {
    id: 'lumbar_vertebrae',
    meshId: 'LumbarVertebrae',
    commonName: 'Lower Back Bones',
    anatomicalName: 'Lumbar vertebrae',
    latinName: 'Vertebrae lumbales',
    type: 'bone',
    layer: 0,
    systems: ['skeletal'],
    regions: ['abdomen', 'lumbar_spine'],
  },
  {
    id: 'pelvis_bone',
    meshId: 'Pelvis',
    commonName: 'Hip Bones',
    anatomicalName: 'Pelvic girdle',
    latinName: 'Cingulum pelvicum',
    type: 'bone',
    layer: 0,
    systems: ['skeletal'],
    regions: ['pelvis'],
  },

  // === MUSCLES ===
  {
    id: 'rectus_abdominis',
    meshId: 'RectusAbdominis',
    commonName: 'Six-Pack Muscle',
    anatomicalName: 'Rectus abdominis',
    latinName: 'Musculus rectus abdominis',
    type: 'muscle',
    layer: 3,
    systems: ['muscular'],
    regions: ['abdomen'],
  },
  {
    id: 'external_oblique',
    meshId: 'ExternalOblique',
    commonName: 'Side Abs (Outer)',
    anatomicalName: 'External oblique',
    latinName: 'Musculus obliquus externus abdominis',
    type: 'muscle',
    layer: 3,
    systems: ['muscular'],
    regions: ['abdomen'],
  },
  {
    id: 'internal_oblique',
    meshId: 'InternalOblique',
    commonName: 'Side Abs (Inner)',
    anatomicalName: 'Internal oblique',
    latinName: 'Musculus obliquus internus abdominis',
    type: 'muscle',
    layer: 2,
    systems: ['muscular'],
    regions: ['abdomen'],
  },
  {
    id: 'transversus_abdominis',
    meshId: 'TransversusAbdominis',
    commonName: 'Deep Core Muscle',
    anatomicalName: 'Transversus abdominis',
    latinName: 'Musculus transversus abdominis',
    type: 'muscle',
    layer: 1,
    systems: ['muscular'],
    regions: ['abdomen'],
  },
  {
    id: 'pectoralis_major',
    meshId: 'PectoralisMajor',
    commonName: 'Chest Muscle',
    anatomicalName: 'Pectoralis major',
    latinName: 'Musculus pectoralis major',
    type: 'muscle',
    layer: 3,
    systems: ['muscular'],
    regions: ['thorax'],
  },
  {
    id: 'serratus_anterior',
    meshId: 'SerratusAnterior',
    commonName: 'Boxer\'s Muscle',
    anatomicalName: 'Serratus anterior',
    latinName: 'Musculus serratus anterior',
    type: 'muscle',
    layer: 2,
    systems: ['muscular'],
    regions: ['thorax'],
  },
  {
    id: 'intercostals',
    meshId: 'Intercostals',
    commonName: 'Rib Muscles',
    anatomicalName: 'Intercostal muscles',
    latinName: 'Musculi intercostales',
    type: 'muscle',
    layer: 1,
    systems: ['muscular'],
    regions: ['thorax'],
  },
  {
    id: 'erector_spinae',
    meshId: 'ErectorSpinae',
    commonName: 'Back Extensors',
    anatomicalName: 'Erector spinae',
    latinName: 'Musculus erector spinae',
    type: 'muscle',
    layer: 2,
    systems: ['muscular'],
    regions: ['thorax', 'abdomen', 'thoracic_spine', 'lumbar_spine'],
  },
  {
    id: 'latissimus_dorsi',
    meshId: 'LatissimusDorsi',
    commonName: 'Lats',
    anatomicalName: 'Latissimus dorsi',
    latinName: 'Musculus latissimus dorsi',
    type: 'muscle',
    layer: 3,
    systems: ['muscular'],
    regions: ['thorax', 'abdomen'],
  },
  {
    id: 'diaphragm',
    meshId: 'Diaphragm',
    commonName: 'Breathing Muscle',
    anatomicalName: 'Thoracic diaphragm',
    latinName: 'Diaphragma',
    type: 'muscle',
    layer: 1,
    systems: ['muscular', 'respiratory'],
    regions: ['thorax', 'abdomen'],
  },
];

// ============================================================
// EDUCATIONAL CONTENT
// ============================================================

export const structureContent: Record<string, StructureContent> = {
  rectus_abdominis: {
    structureId: 'rectus_abdominis',
    simpleDescription: 
      'The "six-pack" muscle running down the front of your abdomen. ' +
      'It\'s responsible for flexing your spine (like in a crunch) and ' +
      'stabilizing your core during heavy lifts.',
    clinicalDescription:
      'A long, flat muscle extending vertically along the anterior abdominal wall. ' +
      'It is divided by tendinous intersections, creating the characteristic ' +
      '"six-pack" appearance when well-developed and body fat is low. ' +
      'Enclosed within the rectus sheath formed by the aponeuroses of the lateral ' +
      'abdominal muscles.',
    muscleDetails: {
      origin: ['Pubic crest', 'Pubic symphysis'],
      insertion: ['Xiphoid process', 'Costal cartilages of ribs 5-7'],
      actions: [
        'Flexion of the lumbar spine',
        'Compression of abdominal contents',
        'Stabilization of the pelvis during walking',
      ],
      innervation: 'Intercostal nerves (T7-T11)',
      fitnessNotes: 
        'Visible "abs" require both muscle development AND low body fat. ' +
        'The muscle itself responds well to both weighted exercises and ' +
        'high-rep endurance work.',
      exercises: ['Crunches', 'Leg raises', 'Planks', 'Cable crunches', 'Ab wheel rollouts'],
    },
    relatedStructures: ['external_oblique', 'internal_oblique', 'transversus_abdominis'],
    clinicalRelevance: 
      'Diastasis recti (separation of the rectus muscles) can occur during ' +
      'pregnancy or with repeated heavy lifting. The rectus sheath is a ' +
      'common site for incisions in abdominal surgery.',
  },
  
  pectoralis_major: {
    structureId: 'pectoralis_major',
    simpleDescription:
      'The main chest muscle that gives your chest its shape. ' +
      'It\'s used for pushing movements and bringing your arms across your body.',
    clinicalDescription:
      'A large, fan-shaped muscle covering the upper anterior thorax. ' +
      'It has two heads: the clavicular head (upper chest) and the sternocostal ' +
      'head (lower chest), which can be targeted independently through exercise selection.',
    muscleDetails: {
      origin: [
        'Clavicular head: Anterior surface of medial half of clavicle',
        'Sternocostal head: Anterior surface of sternum, costal cartilages of ribs 1-6',
      ],
      insertion: ['Lateral lip of intertubercular sulcus of humerus'],
      actions: [
        'Flexion of the arm',
        'Adduction of the arm',
        'Medial rotation of the arm',
      ],
      innervation: 'Medial and lateral pectoral nerves (C5-T1)',
      fitnessNotes:
        'Incline movements emphasize the clavicular head (upper chest), ' +
        'while decline movements target the sternocostal head (lower chest). ' +
        'Flat bench works both heads relatively evenly.',
      exercises: ['Bench press', 'Push-ups', 'Dumbbell flyes', 'Cable crossovers'],
    },
    relatedStructures: ['serratus_anterior', 'intercostals'],
    clinicalRelevance:
      'Poland syndrome involves congenital absence of the pectoralis major. ' +
      'Pectoralis major rupture can occur during heavy bench pressing.',
  },

  erector_spinae: {
    structureId: 'erector_spinae',
    simpleDescription:
      'A group of muscles running along your spine that keep you upright ' +
      'and help you extend (arch) your back. Essential for deadlifts and posture.',
    clinicalDescription:
      'A complex group of muscles and tendons running longitudinally along the ' +
      'vertebral column from the sacrum to the skull. Comprises three columns: ' +
      'iliocostalis (lateral), longissimus (intermediate), and spinalis (medial).',
    muscleDetails: {
      origin: [
        'Sacrum', 
        'Iliac crest', 
        'Lumbar and lower thoracic vertebrae',
      ],
      insertion: [
        'Ribs', 
        'Cervical and thoracic vertebrae', 
        'Mastoid process of temporal bone',
      ],
      actions: [
        'Extension of the vertebral column',
        'Lateral flexion of the vertebral column',
        'Maintenance of posture',
      ],
      innervation: 'Posterior rami of spinal nerves',
      fitnessNotes:
        'These muscles work isometrically during deadlifts to keep your spine ' +
        'neutral. Hyperextensions and good mornings can be used for direct training. ' +
        'Often a limiting factor in heavy compound lifts.',
      exercises: ['Deadlifts', 'Good mornings', 'Back extensions', 'Hyperextensions'],
    },
    relatedStructures: ['thoracic_vertebrae', 'lumbar_vertebrae', 'latissimus_dorsi'],
    clinicalRelevance:
      'Erector spinae strain is a common cause of lower back pain. ' +
      'Chronic tension in these muscles can contribute to postural dysfunction.',
  },
};

// ============================================================
// RENDER CONFIGURATION
// ============================================================

export const renderConfigs: Record<string, RenderConfig> = {
  // Bones - off-white/cream color
  ribcage: {
    structureId: 'ribcage',
    defaultColor: '#E8DCC4',
    highlightColor: '#FFF8E7',
    opacity: 1,
    visibleAtZoomLevel: 0,
    labelAnchorOffset: [0, 0.2, 0.3],
  },
  sternum: {
    structureId: 'sternum',
    defaultColor: '#E8DCC4',
    highlightColor: '#FFF8E7',
    opacity: 1,
    visibleAtZoomLevel: 0.5,
    labelAnchorOffset: [0, 0, 0.2],
  },
  thoracic_vertebrae: {
    structureId: 'thoracic_vertebrae',
    defaultColor: '#E8DCC4',
    highlightColor: '#FFF8E7',
    opacity: 1,
    visibleAtZoomLevel: 0,
    labelAnchorOffset: [0, 0.2, -0.2],
  },
  lumbar_vertebrae: {
    structureId: 'lumbar_vertebrae',
    defaultColor: '#E8DCC4',
    highlightColor: '#FFF8E7',
    opacity: 1,
    visibleAtZoomLevel: 0,
    labelAnchorOffset: [0, -0.1, -0.2],
  },
  pelvis_bone: {
    structureId: 'pelvis_bone',
    defaultColor: '#E8DCC4',
    highlightColor: '#FFF8E7',
    opacity: 1,
    visibleAtZoomLevel: 0,
    labelAnchorOffset: [0, -0.3, 0.2],
  },

  // Muscles - reddish tones
  rectus_abdominis: {
    structureId: 'rectus_abdominis',
    defaultColor: '#C41E3A',
    highlightColor: '#FF4D6A',
    opacity: 0.9,
    visibleAtZoomLevel: 0,
    labelAnchorOffset: [0, 0, 0.15],
  },
  external_oblique: {
    structureId: 'external_oblique',
    defaultColor: '#B31B34',
    highlightColor: '#E84A5F',
    opacity: 0.85,
    visibleAtZoomLevel: 0,
    labelAnchorOffset: [0.2, 0, 0.1],
  },
  internal_oblique: {
    structureId: 'internal_oblique',
    defaultColor: '#9A1829',
    highlightColor: '#D43F52',
    opacity: 0.8,
    visibleAtZoomLevel: 0.3,
    labelAnchorOffset: [0.15, 0, 0.05],
  },
  transversus_abdominis: {
    structureId: 'transversus_abdominis',
    defaultColor: '#82151F',
    highlightColor: '#BA3545',
    opacity: 0.75,
    visibleAtZoomLevel: 0.5,
    labelAnchorOffset: [0.1, 0, 0],
  },
  pectoralis_major: {
    structureId: 'pectoralis_major',
    defaultColor: '#C41E3A',
    highlightColor: '#FF4D6A',
    opacity: 0.9,
    visibleAtZoomLevel: 0,
    labelAnchorOffset: [0.15, 0.3, 0.15],
  },
  serratus_anterior: {
    structureId: 'serratus_anterior',
    defaultColor: '#A81C30',
    highlightColor: '#E04055',
    opacity: 0.85,
    visibleAtZoomLevel: 0.2,
    labelAnchorOffset: [0.25, 0.1, 0.1],
  },
  intercostals: {
    structureId: 'intercostals',
    defaultColor: '#8B1725',
    highlightColor: '#C43040',
    opacity: 0.7,
    visibleAtZoomLevel: 0.4,
    labelAnchorOffset: [0.1, 0.2, 0.05],
  },
  erector_spinae: {
    structureId: 'erector_spinae',
    defaultColor: '#A81C30',
    highlightColor: '#E04055',
    opacity: 0.85,
    visibleAtZoomLevel: 0,
    labelAnchorOffset: [0, 0.1, -0.15],
  },
  latissimus_dorsi: {
    structureId: 'latissimus_dorsi',
    defaultColor: '#C41E3A',
    highlightColor: '#FF4D6A',
    opacity: 0.9,
    visibleAtZoomLevel: 0,
    labelAnchorOffset: [0.25, 0, -0.1],
  },
  diaphragm: {
    structureId: 'diaphragm',
    defaultColor: '#9A1829',
    highlightColor: '#D43F52',
    opacity: 0.7,
    visibleAtZoomLevel: 0.5,
    labelAnchorOffset: [0, 0.1, 0],
  },
};

// ============================================================
// UTILITY FUNCTIONS
// ============================================================

export function getStructureById(id: string): AnatomicalStructure | undefined {
  return torsoStructures.find((s) => s.id === id);
}

export function getStructuresByRegion(regionId: string): AnatomicalStructure[] {
  return torsoStructures.filter((s) => s.regions.includes(regionId as any));
}

export function getStructuresByType(type: string): AnatomicalStructure[] {
  return torsoStructures.filter((s) => s.type === type);
}

export function getStructuresByLayer(layer: number): AnatomicalStructure[] {
  return torsoStructures.filter((s) => s.layer === layer);
}

export function getContentForStructure(id: string): StructureContent | undefined {
  return structureContent[id];
}

export function getRenderConfig(id: string): RenderConfig | undefined {
  return renderConfigs[id];
}
