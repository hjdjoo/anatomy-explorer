"""
Z-Anatomy Torso Export Script for Anatomy Explorer
Version 7.0 - Handles BOTH transform patterns in Z-Anatomy

KEY DISCOVERY:
Z-Anatomy uses two different transform storage patterns:
1. MUSCLE PATH: Locations are [0,0,0], transforms in matrix_local → matrix_world is CORRECT
2. JOINT PATH: Locations have values, but matrix_parent_inverse is broken → 
   matrix_world is WRONG, but SUM OF LOCATIONS is CORRECT

This script detects which pattern each object uses and applies the appropriate calculation.

IMPORTANT: Run on a FRESH Z-Anatomy file (File > Revert if needed)
"""

import bpy
import mathutils
import json
import os
from typing import Dict, List, Any, Tuple, Optional

# ============================================================
# CONFIGURATION
# ============================================================

OUTPUT_DIR = os.path.expanduser("~/Code/anatomy-explorer/public/models")
METADATA_OUTPUT_DIR = os.path.expanduser("~/Code/anatomy-explorer/src/data")

GLTF_FILENAME = "torso.glb"
METADATA_FILENAME = "torso_metadata.json"

# Position validation thresholds
MIN_VALID_HEIGHT = 0.3      # 30cm - below this is suspicious
MAX_VALID_HEIGHT = 2.5      # 2.5m - above this is suspicious
MAX_LATERAL_DIST = 0.5      # 50cm from midline

DEBUG_VERBOSE = True
DEBUG_STRUCTURES = ["pubic_ligament", "inguinal_ligament", "interpubic", "symphysis"]

EXPORT_COLLECTION_NAME = "_EXPORT_TEMP_"

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
    "arm", "brachial", "brachii", "forearm", "antebrachial",
    "hand", "carpal", "metacarpal", "phalanx", "phalang",
    "leg", "femoral", "femur", "thigh", "knee", "patella",
    "calf", "crural", "foot", "tarsal", "metatarsal", "plantae",
    "head", "cranial", "cranium", "face", "facial", "neck", "cervical",
    "skull", "mandible", "maxilla", "eye", "ocular", "ear", "auricul",
    "nose", "nasal", "tongue", "lingual", "teeth", "dental",
    "brain", "cerebr", "shoulder", "scapula", "clavicle", "humerus",
]

EXCLUDE_SUFFIX_PATTERNS = ["_ol", "_or", "_el", "_er"]

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
    clean = name.lower()
    if clean.endswith("_copy"):
        clean = clean[:-5]
    for suffix in [".l", ".r", "_l", "_r", " left", " right", " (left)", " (right)"]:
        if clean.endswith(suffix):
            clean = clean[:-len(suffix)]
    clean = clean.replace(" ", "_").replace("-", "_").replace(".", "_")
    while "__" in clean:
        clean = clean.replace("__", "_")
    return clean.strip("_")


def matches_pattern(name: str, patterns: List[str]) -> bool:
    return any(p in name.lower() for p in patterns)


def has_excluded_suffix(name: str) -> bool:
    return any(name.lower().endswith(s) for s in EXCLUDE_SUFFIX_PATTERNS)


def get_structure_type(obj: bpy.types.Object, original_name: str) -> str:
    for col in obj.users_collection:
        for key, stype in COLLECTION_TYPE_MAP.items():
            if key.lower() in col.name.lower():
                return stype
    
    name_lower = original_name.lower()
    if any(w in name_lower for w in ["ligament", "ligamentum"]):
        return "ligament"
    if any(w in name_lower for w in ["disc", "symphysis"]):
        return "cartilage"
    if any(w in name_lower for w in ["bone", "vertebra", "rib", "sternum", "pelvis", "sacrum"]):
        return "bone"
    if any(w in name_lower for w in ["muscle", "musculus", "abdominis", "dorsi", "pector"]):
        return "muscle"
    return "muscle"


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


def is_position_valid(pos: mathutils.Vector) -> Tuple[bool, str]:
    """Check if a Blender position is valid for torso anatomy."""
    height = pos.z  # Z is up in Blender
    
    if height < MIN_VALID_HEIGHT:
        return False, f"height {height:.3f}m < {MIN_VALID_HEIGHT}m"
    if height > MAX_VALID_HEIGHT:
        return False, f"height {height:.3f}m > {MAX_VALID_HEIGHT}m"
    
    lateral = (pos.x**2 + pos.y**2) ** 0.5
    if lateral > MAX_LATERAL_DIST:
        return False, f"lateral {lateral:.3f}m > {MAX_LATERAL_DIST}m"
    
    return True, "valid"


# ============================================================
# TRANSFORM COMPUTATION - THE KEY INNOVATION
# ============================================================

def sum_parent_locations(obj: bpy.types.Object) -> mathutils.Vector:
    """
    Sum of all location values up the parent chain.
    This works for JOINT PATH objects where matrix_world is broken
    but location values are correct.
    """
    total = obj.location.copy()
    current = obj.parent
    while current:
        total += current.location
        current = current.parent
    return total


def get_geometry_center_local(obj: bpy.types.Object) -> mathutils.Vector:
    """Get the local-space center of mesh geometry."""
    if obj.type != 'MESH' or not obj.data or len(obj.data.vertices) == 0:
        return mathutils.Vector((0, 0, 0))
    
    center = mathutils.Vector((0, 0, 0))
    for v in obj.data.vertices:
        center += v.co
    center /= len(obj.data.vertices)
    return center


def get_geometry_center_via_matrix_world(obj: bpy.types.Object) -> mathutils.Vector:
    """
    Compute world geometry center using matrix_world.
    This works for MUSCLE PATH objects.
    """
    if obj.type != 'MESH' or not obj.data or len(obj.data.vertices) == 0:
        return mathutils.Vector((0, 0, 0))
    
    center = mathutils.Vector((0, 0, 0))
    for v in obj.data.vertices:
        center += obj.matrix_world @ v.co
    center /= len(obj.data.vertices)
    return center


def get_geometry_center_via_location_sum(obj: bpy.types.Object) -> mathutils.Vector:
    """
    Compute world geometry center using sum of parent locations.
    This works for JOINT PATH objects where matrix_world is broken.
    
    Note: This assumes no rotation in the parent chain (or that rotations cancel out).
    For objects with parent rotation, we need to also handle scale/rotation.
    """
    if obj.type != 'MESH' or not obj.data or len(obj.data.vertices) == 0:
        return mathutils.Vector((0, 0, 0))
    
    # Get local geometry center
    local_center = get_geometry_center_local(obj)
    
    # Get world offset from location sum
    world_offset = sum_parent_locations(obj)
    
    # Handle object's own scale and rotation on the local center
    # Apply object's local transform to the local center first
    transformed_local = obj.matrix_local @ mathutils.Vector((0, 0, 0))
    
    # Actually, for the pubic structures, they have scale [-0.1, -0.1, -0.1]
    # and rotation [π, 0, 0]. We need to account for this.
    
    # The local center in object space needs to be transformed by scale and rotation
    scale = obj.scale
    rot = obj.rotation_euler.to_matrix()
    
    # Transform local center
    scaled_center = mathutils.Vector((
        local_center.x * scale.x,
        local_center.y * scale.y,
        local_center.z * scale.z
    ))
    rotated_center = rot @ scaled_center
    
    # World center = sum of locations + rotated/scaled local center
    world_center = world_offset + rotated_center
    
    return world_center


def compute_best_world_center(obj: bpy.types.Object) -> Tuple[mathutils.Vector, str]:
    """
    Compute the best world geometry center by trying both methods
    and choosing the one that gives a valid result.
    
    Returns (center, method_used)
    """
    name = obj.name
    
    # Method 1: Standard matrix_world approach
    center_matrix = get_geometry_center_via_matrix_world(obj)
    valid_matrix, reason_matrix = is_position_valid(center_matrix)
    
    debug_log(name, "matrix_world center", 
              [round(center_matrix.x, 4), round(center_matrix.y, 4), round(center_matrix.z, 4)])
    debug_log(name, f"matrix_world valid: {valid_matrix} ({reason_matrix})")
    
    # Method 2: Location sum approach
    center_sum = get_geometry_center_via_location_sum(obj)
    valid_sum, reason_sum = is_position_valid(center_sum)
    
    debug_log(name, "location_sum center", 
              [round(center_sum.x, 4), round(center_sum.y, 4), round(center_sum.z, 4)])
    debug_log(name, f"location_sum valid: {valid_sum} ({reason_sum})")
    
    # Decision logic
    if valid_matrix and valid_sum:
        # Both valid - prefer matrix_world as it's more standard
        # But check if they're close - if very different, something's weird
        dist = (center_matrix - center_sum).length
        if dist > 0.1:  # More than 10cm difference
            debug_log(name, f"⚠️ Methods differ by {dist:.3f}m, using matrix_world")
        return center_matrix, "matrix_world"
    
    elif valid_matrix:
        return center_matrix, "matrix_world"
    
    elif valid_sum:
        debug_log(name, "Using location_sum (matrix_world was invalid)")
        return center_sum, "location_sum"
    
    else:
        # Neither valid - return matrix_world result and let caller decide
        debug_log(name, f"⚠️ BOTH METHODS INVALID")
        return center_matrix, "invalid"


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


def create_export_copy(
    original: bpy.types.Object,
    world_center: mathutils.Vector,
    export_collection: bpy.types.Collection
) -> Optional[bpy.types.Object]:
    """
    Create an export copy with geometry positioned at computed world center.
    """
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
    
    # Clear parent
    if copy.parent:
        copy.parent = None
    
    # Reset transform and position at world center
    copy.location = world_center
    copy.rotation_euler = (0, 0, 0)
    copy.scale = (1, 1, 1)
    
    # Now we need to transform the geometry to be centered at origin
    # relative to this new position
    bpy.ops.object.select_all(action='DESELECT')
    copy.select_set(True)
    bpy.context.view_layer.objects.active = copy
    
    # The geometry is still in its original local space
    # We need to:
    # 1. Transform vertices to world space (using original's matrix_world)
    # 2. Then transform to new local space (centered at world_center)
    
    if copy.type == 'MESH' and copy.data:
        mesh = copy.data
        # Get original world matrix
        orig_matrix = original.matrix_world.copy()
        
        # Check if we need to use location sum instead
        center_via_matrix = get_geometry_center_via_matrix_world(original)
        is_matrix_valid, _ = is_position_valid(center_via_matrix)
        
        if is_matrix_valid:
            # Standard case - use original matrix_world
            for v in mesh.vertices:
                # Transform to world
                world_co = orig_matrix @ v.co
                # Transform to new local (just offset by center)
                v.co = world_co - world_center
        else:
            # Broken matrix case - need to manually compute world positions
            # using scale, rotation, and location sum
            scale = original.scale
            rot = original.rotation_euler.to_matrix()
            offset = sum_parent_locations(original)
            
            for v in mesh.vertices:
                # Apply scale
                scaled = mathutils.Vector((
                    v.co.x * scale.x,
                    v.co.y * scale.y,
                    v.co.z * scale.z
                ))
                # Apply rotation
                rotated = rot @ scaled
                # Apply location offset
                world_co = rotated + offset
                # Transform to new local
                v.co = world_co - world_center
        
        mesh.update()
    
    # Apply transforms
    try:
        bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
        bpy.ops.object.origin_set(type='ORIGIN_CENTER_OF_VOLUME', center='MEDIAN')
    except Exception as e:
        debug_log(original.name, f"Transform warning: {e}")
    
    return copy


def export_torso():
    """Main export function."""
    print("\n" + "="*60)
    print("Z-Anatomy Torso Export V7.0")
    print("(Dual transform pattern support)")
    print("="*60)
    
    print(f"\nOutput: {OUTPUT_DIR}/{GLTF_FILENAME}")
    print(f"Metadata: {METADATA_OUTPUT_DIR}/{METADATA_FILENAME}")
    
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    os.makedirs(METADATA_OUTPUT_DIR, exist_ok=True)
    
    # Force scene update
    print("\nUpdating scene...")
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
        "version": "7.0",
        "source": "Z-Anatomy",
        "region": "torso",
        "export_notes": "V7: Dual transform pattern support (matrix_world + location_sum)",
        "structures": {}
    }
    
    used_ids = set()
    stats = {"matrix_world": 0, "location_sum": 0, "invalid": 0}
    invalid_report = []
    
    for original in torso_objects:
        # Compute best world center
        world_center, method = compute_best_world_center(original)
        
        if method == "invalid":
            stats["invalid"] += 1
            invalid_report.append(f"{original.name}: both methods gave invalid positions")
            continue
        
        stats[method] = stats.get(method, 0) + 1
        
        # Create export copy
        copy = create_export_copy(original, world_center, export_collection)
        if not copy:
            continue
        
        # Generate mesh ID
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
            print(f"  ✓ {mesh_id}: center={center_threejs}, method={method}")
    
    print(f"\n  Methods used:")
    print(f"    matrix_world: {stats.get('matrix_world', 0)}")
    print(f"    location_sum: {stats.get('location_sum', 0)}")
    print(f"    invalid: {stats.get('invalid', 0)}")
    
    if invalid_report:
        print(f"\n  Invalid structures:")
        for item in invalid_report[:20]:
            print(f"    - {item}")
        if len(invalid_report) > 20:
            print(f"    ... and {len(invalid_report) - 20} more")
    
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
    print(f"  (matrix_world: {stats.get('matrix_world', 0)}, location_sum: {stats.get('location_sum', 0)})")
    print("="*60 + "\n")


if __name__ == "__main__":
    export_torso()