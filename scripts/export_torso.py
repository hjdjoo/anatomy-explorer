"""
Z-Anatomy Torso Export Script for Anatomy Explorer
Version 9.0 - Preserved side information + improved type detection

CHANGES FROM V8:
- normalize_name now PRESERVES side suffixes (_l/_r) instead of stripping them
  This fixes asymmetric rendering where only one side of bilateral structures appears
- get_structure_type now prioritizes name-based detection over collection membership
  This fixes misclassification (e.g., iliopsoas_fascia incorrectly labeled as "muscle")
- EXCLUDE_SUFFIX_PATTERNS updated to include .ol/.or/.el/.er (dot variants)

APPROACH:
- Use standard transform method (unparent + apply + set origin) for 99% of structures
- Apply special location-sum fix ONLY to specific whitelisted structures that have
  broken parent chain transforms (pubic ligaments, interpubic disc, etc.)

IMPORTANT: Run on a FRESH Z-Anatomy file (File > Revert if needed)
"""

import bpy
import mathutils
import json
import os
from typing import Dict, List, Any, Tuple, Optional, Set

# ============================================================
# CONFIGURATION
# ============================================================

OUTPUT_DIR = os.path.expanduser("~/Code/anatomy-explorer/public/models")
METADATA_OUTPUT_DIR = os.path.expanduser("~/Code/anatomy-explorer/src/data")

GLTF_FILENAME = "torso.glb"
METADATA_FILENAME = "torso_metadata.json"

DEBUG_VERBOSE = True
DEBUG_STRUCTURES = ["pubic_ligament", "inguinal_ligament", "interpubic", "trapezius"]

EXPORT_COLLECTION_NAME = "_EXPORT_TEMP_"

# ============================================================
# STRUCTURES THAT NEED SPECIAL HANDLING
# ============================================================

# These structures have broken parent chain transforms in Z-Anatomy.
# Their matrix_world doesn't reflect the actual world position.
# We need to compute their position using sum of parent locations instead.
#
# Identified from diagnostic: structures parented under pubic_symphysis
# in the Joints hierarchy have this issue.

BROKEN_PARENT_CHAIN_PATTERNS = [
    "inferior_pubic_ligament",
    "superior_pubic_ligament",
    "interpubic_disc",
    # Add more patterns here if other structures have the same issue
]

def needs_location_sum_fix(obj_name: str) -> bool:
    """Check if an object needs the special location-sum transform fix."""
    name_lower = obj_name.lower()
    return any(pattern in name_lower for pattern in BROKEN_PARENT_CHAIN_PATTERNS)

# ============================================================
# TYPE MAPPINGS
# ============================================================

COLLECTION_TYPE_MAP = {
    "Bones": "bone", "Skeleton": "bone", "Skeletal": "bone",
    "Muscles": "muscle", "Muscular": "muscle",
    "Tendons": "tendon", "Ligaments": "ligament",
    "Cartilage": "cartilage", "Cartilages": "cartilage",
    "Organs": "organ", "Viscera": "organ",
    "Fascia": "fascia", "Fasciae": "fascia",
    "Joints": "cartilage",
}

TORSO_PATTERNS = [
    "thorax", "thoracic", "chest", "rib", "costa", "costal",
    "sternum", "sternal", "intercostal", "pector", "pectoral",
    "serratus", "diaphragm", "abdomen", "abdominal", "abdominis",
    "rectus", "oblique", "transvers", "lumbar", "lumbo",
    "psoas", "iliacus", "quadratus", "vertebra", "vertebrae", 
    "vertebral", "spine", "spinal", "erector", "spinalis", 
    "longissimus", "iliocostalis", "multifid", "pelvis", "pelvic",
    "ilium", "iliac", "ischium", "ischial", "pubis", "pubic",
    "sacrum", "sacral", "coccyx", "coccygeal", "gluteus", "gluteal",
    "latissimus", "dorsi", "trapezius", "rhomboid", "inguinal",
    "symphysis",
]

EXCLUDE_PATTERNS = [
    # Upper limb (excluding shoulder girdle connections to torso)
    "arm", "brachial", "brachii", "forearm", "antebrachial",
    "hand", "carpal", "metacarpal", "phalanx", "phalang",
    # Lower limb
    "leg", "femoral", "femur", "thigh", "knee", "patella",
    "calf", "crural", "foot", "tarsal", "metatarsal", "plantae",
    # Head/neck - NOTE: "head" removed because it conflicts with muscle terminology
    # (e.g., "clavicular head of pectoralis major", "long head of biceps")
    # Using more specific cranial terms instead:
    "cranial", "cranium", "skull", "calvaria", "calvarium",
    "face", "facial", "neck", "cervical",
    "mandible", "maxilla", "eye", "ocular", "ear", "auricul",
    "nose", "nasal", "tongue", "lingual", "teeth", "dental",
    "brain", "cerebr",
    # Shoulder structures (bones, not muscles attaching to torso)
    "shoulder", "scapula", "clavicle", "humerus",
]

# V9: Added .ol/.or/.el/.er patterns (dot variants that get normalized to underscores)
EXCLUDE_SUFFIX_PATTERNS = [
    "_ol", "_or", "_el", "_er",  # Underscore variants
    ".ol", ".or", ".el", ".er",  # Dot variants (before normalization)
]

# ============================================================
# HELPERS
# ============================================================

def should_debug(name: str) -> bool:
    if not DEBUG_VERBOSE:
        return False
    if not DEBUG_STRUCTURES:
        return True
    return any(s.lower() in name.lower() for s in DEBUG_STRUCTURES)


def debug_log(name: str, msg: str, data: Any = None):
    if not should_debug(name):
        return
    if data is not None:
        print(f"  [DEBUG {name}] {msg}: {data}")
    else:
        print(f"  [DEBUG {name}] {msg}")


def normalize_name(name: str) -> str:
    """
    Normalize mesh name, PRESERVING left/right side information.
    
    V9 CHANGE: Side suffixes are now converted to standardized format (_l/_r)
    instead of being stripped. This ensures bilateral structures get unique
    metadata keys and don't collide during React rendering.
    
    Examples:
        'Descending part of trapezius muscle.l' → 'descending_part_of_trapezius_muscle_l'
        'Descending part of trapezius muscle.r' → 'descending_part_of_trapezius_muscle_r'
        'Iliopsoas fascia.l' → 'iliopsoas_fascia_l'
        'Rectus abdominis muscle' → 'rectus_abdominis_muscle' (no side suffix)
    """
    clean = name.lower()
    
    # Remove export/copy suffixes
    if clean.endswith("_copy") or clean.endswith("_export"):
        clean = clean.rsplit("_", 1)[0]
    
    # CONVERT (not remove) side suffixes to standardized format
    side_suffix = None
    for suffix, normalized in [
        (".l", "_l"), (".r", "_r"), 
        ("_l", "_l"), ("_r", "_r"),
        (" left", "_l"), (" right", "_r"),
        (" (left)", "_l"), (" (right)", "_r"),
    ]:
        if clean.endswith(suffix):
            clean = clean[:-len(suffix)]
            side_suffix = normalized
            break
    
    # Normalize characters
    clean = clean.replace(" ", "_").replace("-", "_").replace(".", "_")
    while "__" in clean:
        clean = clean.replace("__", "_")
    clean = clean.strip("_")
    
    # Re-append side suffix if present
    if side_suffix:
        clean = clean + side_suffix
    
    return clean


def matches_pattern(name: str, patterns: List[str]) -> bool:
    return any(p in name.lower() for p in patterns)


def has_excluded_suffix(name: str) -> bool:
    """Check if name ends with an excluded suffix (before or after normalization)."""
    name_lower = name.lower()
    return any(name_lower.endswith(s) for s in EXCLUDE_SUFFIX_PATTERNS)


def get_structure_type(obj: bpy.types.Object, original_name: str) -> str:
    """
    Determine structure type, prioritizing explicit name indicators.
    
    V9 CHANGE: Name-based detection now takes precedence for specific types
    (fascia, ligament, tendon, etc.) because these are explicitly named in
    Z-Anatomy, while collection membership can be ambiguous.
    
    This fixes issues like iliopsoas_fascia being classified as "muscle"
    because it's in the Muscles collection.
    """
    name_lower = original_name.lower()
    
    # Priority 1: Explicit type keywords in name (most reliable)
    # These keywords are unambiguous indicators of structure type
    if any(w in name_lower for w in ["fascia", "fasciae", "aponeurosis"]):
        return "fascia"
    if any(w in name_lower for w in ["ligament", "ligamentum"]):
        return "ligament"
    if any(w in name_lower for w in ["tendon"]):
        return "tendon"
    if any(w in name_lower for w in ["disc", "meniscus"]):
        return "cartilage"
    
    # Priority 2: Collection-based detection
    for col in obj.users_collection:
        for key, stype in COLLECTION_TYPE_MAP.items():
            if key.lower() in col.name.lower():
                return stype
    
    # Priority 3: Additional name-based fallbacks
    if any(w in name_lower for w in ["symphysis", "cartilage"]):
        return "cartilage"
    if any(w in name_lower for w in ["bone", "vertebra", "rib", "sternum", "pelvis", 
                                      "sacrum", "ilium", "ischium", "coccyx", "sacral"]):
        return "bone"
    if any(w in name_lower for w in ["muscle", "musculus", "abdominis", "dorsi", "pector"]):
        return "muscle"
    
    # Default to "other" for unidentified structures (V9: changed from "muscle")
    return "other"


def estimate_layer(name: str, struct_type: str) -> int:
    if struct_type in ["bone", "organ", "cartilage"]:
        return 0
    elif struct_type in ["ligament", "tendon"]:
        return 1
    elif struct_type == "fascia":
        return 4
    else:
        name_lower = name.lower()
        if any(d in name_lower for d in ["transvers", "multifid", "rotat", "intercost", "diaphragm"]):
            return 1
        if any(m in name_lower for m in ["oblique", "erector", "serratus", "internal"]):
            return 2
        return 3


def get_regions(name: str) -> List[str]:
    regions = set()
    name_lower = name.lower()
    
    if any(t in name_lower for t in ["thorax", "thoracic", "rib", "sternum", "pector", "intercost"]):
        regions.add("thorax")
    if any(a in name_lower for a in ["abdomen", "abdomin", "rectus", "oblique", "transvers"]):
        regions.add("abdomen")
    if any(p in name_lower for p in ["pelvis", "pelvic", "ilium", "iliac", "ischium", "pubis", 
                                      "sacrum", "coccyx", "gluteus", "inguinal", "symphysis"]):
        regions.add("pelvis")
    if any(s in name_lower for s in ["lumbar", "lumbo"]):
        regions.add("lumbar_spine")
    if "thoracic" in name_lower and "vertebra" in name_lower:
        regions.add("thoracic_spine")
    
    return list(regions) if regions else ["torso"]


def blender_to_threejs(loc) -> List[float]:
    """Convert Blender Z-up to Three.js Y-up."""
    return [round(loc[0], 4), round(loc[2], 4), round(-loc[1], 4)]


# ============================================================
# TRANSFORM FUNCTIONS
# ============================================================

def sum_parent_locations(obj: bpy.types.Object) -> mathutils.Vector:
    """Sum of all location values up the parent chain."""
    total = obj.location.copy()
    current = obj.parent
    while current:
        total += current.location
        current = current.parent
    return total


def compute_world_center_via_location_sum(obj: bpy.types.Object) -> mathutils.Vector:
    """
    Compute world geometry center using sum of parent locations.
    Used for structures with broken matrix_world (pubic ligaments, etc.)
    """
    if obj.type != 'MESH' or not obj.data or len(obj.data.vertices) == 0:
        return sum_parent_locations(obj)
    
    # Get local geometry center
    local_center = mathutils.Vector((0, 0, 0))
    for v in obj.data.vertices:
        local_center += v.co
    local_center /= len(obj.data.vertices)
    
    # Apply object's local scale and rotation to local center
    scale = obj.scale
    rot = obj.rotation_euler.to_matrix()
    
    scaled_center = mathutils.Vector((
        local_center.x * scale.x,
        local_center.y * scale.y,
        local_center.z * scale.z
    ))
    rotated_center = rot @ scaled_center
    
    # World center = sum of locations + transformed local center
    world_offset = sum_parent_locations(obj)
    return world_offset + rotated_center


# ============================================================
# COLLECTION MANAGEMENT
# ============================================================

def create_export_collection() -> bpy.types.Collection:
    if EXPORT_COLLECTION_NAME in bpy.data.collections:
        old = bpy.data.collections[EXPORT_COLLECTION_NAME]
        for obj in list(old.objects):
            bpy.data.objects.remove(obj, do_unlink=True)
        bpy.data.collections.remove(old)
    
    col = bpy.data.collections.new(EXPORT_COLLECTION_NAME)
    bpy.context.scene.collection.children.link(col)
    return col


def cleanup_export_collection():
    if EXPORT_COLLECTION_NAME in bpy.data.collections:
        col = bpy.data.collections[EXPORT_COLLECTION_NAME]
        for obj in list(col.objects):
            bpy.data.objects.remove(obj, do_unlink=True)
        bpy.data.collections.remove(col)


# ============================================================
# MAIN FUNCTIONS
# ============================================================

def find_torso_objects() -> List[bpy.types.Object]:
    """Find torso meshes in view layer."""
    torso = []
    view_layer_names = {o.name for o in bpy.context.view_layer.objects}
    
    for obj in bpy.data.objects:
        if obj.type != 'MESH':
            continue
        if obj.name not in view_layer_names:
            continue
        if matches_pattern(obj.name, EXCLUDE_PATTERNS) or has_excluded_suffix(obj.name):
            continue
        
        if matches_pattern(obj.name, TORSO_PATTERNS):
            torso.append(obj)
            continue
        
        for col in obj.users_collection:
            if matches_pattern(col.name, TORSO_PATTERNS):
                torso.append(obj)
                break
    
    print(f"\nFound {len(torso)} torso structures")
    return torso


def process_standard_object(
    original: bpy.types.Object,
    export_collection: bpy.types.Collection
) -> Tuple[Optional[bpy.types.Object], mathutils.Vector]:
    """
    Standard processing: duplicate, unparent, apply transforms, set origin.
    This works for 99% of structures.
    Returns (processed_copy, world_center)
    """
    # Store original world matrix
    world_matrix = original.matrix_world.copy()
    
    # Duplicate
    bpy.ops.object.select_all(action='DESELECT')
    original.select_set(True)
    bpy.context.view_layer.objects.active = original
    bpy.ops.object.duplicate(linked=False)
    
    copy = bpy.context.active_object
    copy.name = f"{original.name}_export"
    
    # Move to export collection
    for col in copy.users_collection:
        col.objects.unlink(copy)
    export_collection.objects.link(copy)
    
    # Make single-user if needed
    if copy.data and copy.data.users > 1:
        copy.data = copy.data.copy()
    
    # Unparent while preserving world transform
    if copy.parent:
        copy.parent = None
        copy.matrix_world = world_matrix
    
    # Apply transforms
    bpy.ops.object.select_all(action='DESELECT')
    copy.select_set(True)
    bpy.context.view_layer.objects.active = copy
    
    try:
        bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
        bpy.ops.object.origin_set(type='ORIGIN_CENTER_OF_VOLUME', center='MEDIAN')
    except Exception as e:
        debug_log(original.name, f"Transform warning: {e}")
    
    # After origin_set, location IS the geometry center
    world_center = copy.location.copy()
    
    return copy, world_center


def process_broken_parent_object(
    original: bpy.types.Object,
    export_collection: bpy.types.Collection
) -> Tuple[Optional[bpy.types.Object], mathutils.Vector]:
    """
    Special processing for structures with broken parent chain transforms.
    Computes world position using sum of parent locations.
    Returns (processed_copy, world_center)
    """
    debug_log(original.name, "Using location-sum fix (broken parent chain)")
    
    # Compute correct world center using location sum
    world_center = compute_world_center_via_location_sum(original)
    
    debug_log(original.name, "Computed world center", 
              [round(world_center.x, 4), round(world_center.y, 4), round(world_center.z, 4)])
    
    # Duplicate
    bpy.ops.object.select_all(action='DESELECT')
    original.select_set(True)
    bpy.context.view_layer.objects.active = original
    bpy.ops.object.duplicate(linked=False)
    
    copy = bpy.context.active_object
    copy.name = f"{original.name}_export"
    
    # Move to export collection
    for col in copy.users_collection:
        col.objects.unlink(copy)
    export_collection.objects.link(copy)
    
    # Make single-user if needed
    if copy.data and copy.data.users > 1:
        copy.data = copy.data.copy()
    
    # Clear parent
    copy.parent = None
    
    # Position at computed world center
    copy.location = world_center
    copy.rotation_euler = (0, 0, 0)
    copy.scale = (1, 1, 1)
    
    # Transform the geometry to be centered at origin relative to world_center
    if copy.type == 'MESH' and copy.data:
        mesh = copy.data
        scale = original.scale
        rot = original.rotation_euler.to_matrix()
        offset = sum_parent_locations(original)
        
        for v in mesh.vertices:
            # Apply original scale
            scaled = mathutils.Vector((
                v.co.x * scale.x,
                v.co.y * scale.y,
                v.co.z * scale.z
            ))
            # Apply original rotation
            rotated = rot @ scaled
            # Move to world position, then offset by center
            v.co = rotated + offset - world_center
        
        mesh.update()
    
    # Apply transforms and set origin
    bpy.ops.object.select_all(action='DESELECT')
    copy.select_set(True)
    bpy.context.view_layer.objects.active = copy
    
    try:
        bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
        bpy.ops.object.origin_set(type='ORIGIN_CENTER_OF_VOLUME', center='MEDIAN')
    except Exception as e:
        debug_log(original.name, f"Transform warning: {e}")
    
    # Update world_center to final location after origin_set
    world_center = copy.location.copy()
    
    return copy, world_center


def export_torso():
    """Main export function."""
    print("\n" + "="*60)
    print("Z-Anatomy Torso Export V9.0")
    print("(Preserved side info + improved type detection)")
    print("="*60)
    
    print(f"\nOutput: {OUTPUT_DIR}/{GLTF_FILENAME}")
    print(f"Metadata: {METADATA_OUTPUT_DIR}/{METADATA_FILENAME}")
    print(f"\nStructures with special handling: {BROKEN_PARENT_CHAIN_PATTERNS}")
    
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    os.makedirs(METADATA_OUTPUT_DIR, exist_ok=True)
    
    # Force scene update
    bpy.context.view_layer.update()
    
    # Find objects
    print("\nFinding torso structures...")
    torso_objects = find_torso_objects()
    
    if not torso_objects:
        print("ERROR: No torso structures found!")
        return
    
    # Process
    print(f"\nProcessing {len(torso_objects)} structures...")
    export_collection = create_export_collection()
    
    export_objects = []
    metadata = {
        "version": "9.0",
        "source": "Z-Anatomy",
        "region": "torso",
        "export_notes": "V9: Preserved side suffixes (_l/_r), name-priority type detection, default 'other' type",
        "structures": {}
    }
    
    used_ids = set()
    stats = {"standard": 0, "special_fix": 0, "failed": 0}
    type_stats = {}  # Track type distribution
    
    for original in torso_objects:
        try:
            # Choose processing method based on whether structure needs special handling
            if needs_location_sum_fix(original.name):
                copy, world_center = process_broken_parent_object(original, export_collection)
                stats["special_fix"] += 1
            else:
                copy, world_center = process_standard_object(original, export_collection)
                stats["standard"] += 1
            
            if copy is None:
                stats["failed"] += 1
                continue
            
            # Generate mesh ID (V9: now preserves _l/_r suffixes)
            base_id = normalize_name(original.name)
            mesh_id = base_id
            counter = 1
            while mesh_id in used_ids:
                mesh_id = f"{base_id}_{counter}"
                counter += 1
            used_ids.add(mesh_id)
            
            copy.name = mesh_id
            center_threejs = blender_to_threejs(world_center)
            struct_type = get_structure_type(original, original.name)
            
            # Track type distribution
            type_stats[struct_type] = type_stats.get(struct_type, 0) + 1
            
            metadata["structures"][mesh_id] = {
                "meshId": mesh_id,
                "originalName": original.name,
                "type": struct_type,
                "layer": estimate_layer(original.name, struct_type),
                "regions": get_regions(original.name),
                "center": center_threejs,
            }
            
            export_objects.append(copy)
            
            if should_debug(mesh_id):
                method = "SPECIAL" if needs_location_sum_fix(original.name) else "standard"
                print(f"  ✓ {mesh_id}: type={struct_type}, center={center_threejs}, method={method}")
                
        except Exception as e:
            print(f"  ✗ Failed to process {original.name}: {e}")
            stats["failed"] += 1
    
    print(f"\n  Processing results:")
    print(f"    Standard method: {stats['standard']}")
    print(f"    Special fix: {stats['special_fix']}")
    print(f"    Failed: {stats['failed']}")
    
    print(f"\n  Type distribution:")
    for t, count in sorted(type_stats.items(), key=lambda x: -x[1]):
        print(f"    {t}: {count}")
    
    if not export_objects:
        print("ERROR: No valid objects to export!")
        cleanup_export_collection()
        return
    
    # Export glTF
    print(f"\nExporting {len(export_objects)} structures...")
    bpy.ops.object.select_all(action='DESELECT')
    for obj in export_objects:
        obj.select_set(True)
    bpy.context.view_layer.objects.active = export_objects[0]
    
    gltf_path = os.path.join(OUTPUT_DIR, GLTF_FILENAME)
    bpy.ops.export_scene.gltf(
        filepath=gltf_path,
        use_selection=True,
        export_draco_mesh_compression_enable=True,
        export_format='GLB',
        export_apply=True,
        export_texcoords=True,
        export_normals=True,
        export_materials='EXPORT',
        export_all_vertex_colors=True,
        export_yup=True,
    )
    print(f"  ✓ {gltf_path}")
    
    # Export metadata
    metadata_path = os.path.join(METADATA_OUTPUT_DIR, METADATA_FILENAME)
    with open(metadata_path, 'w') as f:
        json.dump(metadata, f, indent=2)
    print(f"  ✓ {metadata_path}")
    
    # Cleanup
    cleanup_export_collection()
    
    print("\n" + "="*60)
    print("Export complete!")
    print(f"  Total: {len(metadata['structures'])}")
    print("="*60 + "\n")


if __name__ == "__main__":
    export_torso()