"""
Z-Anatomy Torso Export Script for Anatomy Explorer
Version 2.0 - Fixed center computation for parented objects

This script exports torso structures from Z-Anatomy's Blender file
into a glTF format suitable for use with react-three-fiber.

KEY FIX: This version unparents all objects BEFORE applying transforms,
ensuring that:
1. Each object's world transform is baked into its vertex data
2. The object's location accurately represents the geometry center
3. No parent-child hierarchy issues in the exported glTF

Usage:
1. Open Z-Anatomy in Blender
2. Open this script in Blender's Text Editor (or run from command line)
3. Run the script
4. Find the exported files in the specified output directory

Requirements:
- Blender 3.0+ (tested with 3.6+)
- Z-Anatomy Blender template installed
"""

import bpy
import json
import os
from typing import Dict, List, Any

# ============================================================
# CONFIGURATION
# ============================================================

# Output directory - change this to your project's public/models folder
OUTPUT_DIR = os.path.expanduser("~/Code/anatomy-explorer/public/models")
METADATA_OUTPUT_DIR = os.path.expanduser("~/Code/anatomy-explorer/src/data")

# Output filenames
GLTF_FILENAME = "torso.glb"
METADATA_FILENAME = "torso_metadata.json"

# Enable verbose debugging
DEBUG_VERBOSE = True
# Specific structures to debug (empty = all)
DEBUG_STRUCTURES = ["inguinal_ligament"]

# Structure type mappings based on Z-Anatomy collection names
COLLECTION_TYPE_MAP = {
    "Bones": "bone",
    "Skeleton": "bone",
    "Skeletal": "bone",
    "Muscles": "muscle",
    "Muscular": "muscle",
    "Tendons": "tendon",
    "Ligaments": "ligament",
    "Cartilage": "cartilage",
    "Cartilages": "cartilage",
    "Organs": "organ",
    "Viscera": "organ",
    "Fascia": "fascia",
    "Fasciae": "fascia",
}

# Torso-related collection/object name patterns to include
TORSO_PATTERNS = [
    # Thorax
    "thorax", "thoracic", "chest",
    "rib", "costa", "costal",
    "sternum", "sternal",
    "intercostal",
    "pector", "pectoral",
    "serratus",
    "diaphragm",
    
    # Abdomen
    "abdomen", "abdominal", "abdominis",
    "rectus", "oblique", "transvers",
    "lumbar", "lumbo",
    "psoas", "iliacus",
    "quadratus",
    
    # Spine (thoracic and lumbar regions)
    "vertebra", "vertebrae", "vertebral",
    "spine", "spinal",
    "erector", "spinalis", "longissimus", "iliocostalis",
    "multifid",
    
    # Pelvis
    "pelvis", "pelvic",
    "ilium", "iliac",
    "ischium", "ischial",
    "pubis", "pubic",
    "sacrum", "sacral",
    "coccyx", "coccygeal",
    "gluteus", "gluteal",
    
    # Back muscles
    "latissimus", "dorsi",
    "trapezius",
    "rhomboid",
    
    # Groin/inguinal region
    "inguinal",
]

# Patterns to exclude (limbs, head, etc.)
EXCLUDE_PATTERNS = [
    "arm", "brachial", "brachii",
    "forearm", "antebrachial",
    "hand", "carpal", "metacarpal", "phalanx", "phalang",
    "leg", "femoral", "femur",
    "thigh",
    "knee", "patella",
    "calf", "crural",
    "foot", "tarsal", "metatarsal",
    "plantae",
    "head", "cranial", "cranium",
    "face", "facial",
    "neck", "cervical",
    "skull",
    "mandible", "maxilla",
    "eye", "ocular",
    "ear", "auricul",
    "nose", "nasal",
    "tongue", "lingual",
    "teeth", "dental",
    "brain", "cerebr",
    "shoulder", "scapula", "clavicle",
    "humerus",
]

# Suffix patterns to exclude
EXCLUDE_SUFFIX_PATTERNS = [
    "_ol", "_or",
    "_el", "_er",
]

# ============================================================
# DEBUG HELPERS
# ============================================================

def debug_log(obj_name: str, message: str, data: Any = None):
    """Log debug information for specific structures."""
    if not DEBUG_VERBOSE:
        return
    if DEBUG_STRUCTURES and not any(s.lower() in obj_name.lower() for s in DEBUG_STRUCTURES):
        return
    
    if data is not None:
        print(f"  [DEBUG {obj_name}] {message}: {data}")
    else:
        print(f"  [DEBUG {obj_name}] {message}")
    
    # Enhanced debug for key structures - print additional info
    if DEBUG_VERBOSE and any(s.lower() in obj_name.lower() for s in ["inguinal", "ligament"]):
        try:
            obj = bpy.data.objects.get(obj_name)
            if obj and hasattr(obj, 'parent'):
                print(f"    Object type: {obj.type}")
                if obj.parent:
                    print(f"    Parent object: {obj.parent.name}")
                print(f"    Location: {list(obj.location)}")
                print(f"    World matrix translation: {list(obj.matrix_world.translation)}")
        except Exception as e:
            print(f"    Could not fetch additional object info: {e}")
        
    # Add parent info for debugging
    if DEBUG_VERBOSE and DEBUG_STRUCTURES and any(s.lower() in obj_name.lower() for s in DEBUG_STRUCTURES):
        # Try to find and print parent info
        try:
            obj = bpy.data.objects.get(obj_name)
            if obj:
                parent_info = "None"
                if obj.parent:
                    parent_info = f"Parent: {obj.parent.name}"
                print(f"    {parent_info}")
        except:
            pass

def detailed_debug_log(obj, message: str, data: Any = None):
    """Provide more detailed debug information including parent hierarchy."""
    if not DEBUG_VERBOSE:
        return
    if DEBUG_STRUCTURES and not any(s.lower() in obj.name.lower() for s in DEBUG_STRUCTURES):
        return
    
    # Enhanced debugging with parent information
    parent_info = "None"
    if hasattr(obj, 'parent') and obj.parent:
        parent_info = f"{obj.parent.name} (type: {obj.parent.type})"
    
    if data is not None:
        print(f"  [DEBUG {obj.name}] {message}: {data}")
        print(f"    Parent: {parent_info}")
        print(f"    Location: {list(obj.location) if hasattr(obj, 'location') else 'N/A'}")
        print(f"    World Matrix Translation: {list(obj.matrix_world.translation) if hasattr(obj, 'matrix_world') else 'N/A'}")
    else:
        print(f"  [DEBUG {obj.name}] {message}")
        print(f"    Parent: {parent_info}")
        print(f"    Location: {list(obj.location) if hasattr(obj, 'location') else 'N/A'}")
        print(f"    World Matrix Translation: {list(obj.matrix_world.translation) if hasattr(obj, 'matrix_world') else 'N/A'}")

def detailed_debug_log(obj: bpy.types.Object, message: str, data: Any = None):
    """Provide more detailed debug information including parent hierarchy."""
    if not DEBUG_VERBOSE:
        return
    if DEBUG_STRUCTURES and not any(s.lower() in obj.name.lower() for s in DEBUG_STRUCTURES):
        return
    
    # Enhanced debugging with parent information
    parent_info = "None"
    if obj.parent:
        parent_info = f"{obj.parent.name} (type: {obj.parent.type})"
    
    if data is not None:
        print(f"  [DEBUG {obj.name}] {message}: {data}")
        print(f"    Parent: {parent_info}")
        print(f"    Location: {list(obj.location)}")
        print(f"    World Matrix Translation: {list(obj.matrix_world.translation)}")
    else:
        print(f"  [DEBUG {obj.name}] {message}")
        print(f"    Parent: {parent_info}")
        print(f"    Location: {list(obj.location)}")
        print(f"    World Matrix Translation: {list(obj.matrix_world.translation)}")

# ============================================================
# HELPER FUNCTIONS
# ============================================================

def normalize_name(name: str) -> str:
    """Convert Z-Anatomy object name to a clean mesh ID."""
    clean = name.lower()
    
    for suffix in [".l", ".r", "_l", "_r", " left", " right", " (left)", " (right)"]:
        if clean.endswith(suffix):
            clean = clean[:-len(suffix)]
    
    clean = clean.replace(" ", "_").replace("-", "_").replace(".", "_")
    
    while "__" in clean:
        clean = clean.replace("__", "_")
    
    clean = clean.strip("_")
    
    return clean


def matches_pattern(name: str, patterns: List[str]) -> bool:
    """Check if a name matches any of the given patterns."""
    name_lower = name.lower()
    return any(pattern in name_lower for pattern in patterns)


def has_excluded_suffix(name: str) -> bool:
    """Check if a name ends with an excluded suffix pattern."""
    name_lower = name.lower()
    for suffix in EXCLUDE_SUFFIX_PATTERNS:
        if name_lower.endswith(suffix):
            return True
    return False


def validate_structure_center(name: str, center: List[float], struct_type: str) -> bool:
    """Validate that a structure's center is plausible."""
    dist_from_origin = (center[0]**2 + center[1]**2 + center[2]**2) ** 0.5
    
    if dist_from_origin < 0.05:
        if abs(center[1]) < 0.1:
            print(f"  WARNING: {name} has suspicious center near origin: {center}")
            return False
    
    return True


def get_structure_type(obj: bpy.types.Object) -> str:
    """Determine the structure type based on object's collection hierarchy."""
    for collection in obj.users_collection:
        col_name = collection.name
        for key, struct_type in COLLECTION_TYPE_MAP.items():
            if key.lower() in col_name.lower():
                return struct_type
        
        def check_parents(col):
            for parent_col in bpy.data.collections:
                if col.name in [c.name for c in parent_col.children]:
                    for key, struct_type in COLLECTION_TYPE_MAP.items():
                        if key.lower() in parent_col.name.lower():
                            return struct_type
                    return check_parents(parent_col)
            return None
        
        parent_type = check_parents(collection)
        if parent_type:
            return parent_type
    
    name_lower = obj.name.lower()
    
    # Check for ligament keywords FIRST (before muscle patterns)
    if any(lig_word in name_lower for lig_word in ["ligament", "ligamentum"]):
        return "ligament"
    
    if any(bone_word in name_lower for bone_word in ["bone", "vertebra", "rib", "sternum", "pelvis", "sacrum"]):
        return "bone"
    if any(muscle_word in name_lower for muscle_word in ["muscle", "musculus", "abdominis", "dorsi", "pector"]):
        return "muscle"
    
    return "muscle"


def estimate_layer(obj: bpy.types.Object, struct_type: str) -> int:
    """Estimate the anatomical layer based on type and position."""
    if struct_type == "bone":
        return 0
    elif struct_type == "organ":
        return 0
    elif struct_type == "cartilage":
        return 0
    elif struct_type == "ligament":
        return 1
    elif struct_type == "tendon":
        return 1
    elif struct_type == "fascia":
        return 4
    else:  # muscle
        name_lower = obj.name.lower()
        
        if any(deep in name_lower for deep in ["transvers", "multifid", "rotat", "intercost", "diaphragm"]):
            return 1
        if any(mid in name_lower for mid in ["oblique", "erector", "serratus", "internal"]):
            return 2
        return 3


def get_regions(obj: bpy.types.Object) -> List[str]:
    """Determine which body regions this structure belongs to."""
    regions = set()
    name_lower = obj.name.lower()
    
    if any(t in name_lower for t in ["thorax", "thoracic", "rib", "sternum", "pector", "intercost"]):
        regions.add("thorax")
    if any(a in name_lower for a in ["abdomen", "abdomin", "rectus", "oblique", "transvers"]):
        regions.add("abdomen")
    if any(p in name_lower for p in ["pelvis", "pelvic", "ilium", "iliac", "ischium", "pubis", "sacrum", "coccyx", "gluteus", "inguinal"]):
        regions.add("pelvis")
    if any(s in name_lower for s in ["lumbar", "lumbo"]) or ("vertebra" in name_lower and "lumbar" in name_lower):
        regions.add("lumbar_spine")
    if "thoracic" in name_lower and "vertebra" in name_lower:
        regions.add("thoracic_spine")
    
    if any(span in name_lower for span in ["erector", "latissimus", "psoas"]):
        if "erector" in name_lower or "latissimus" in name_lower:
            regions.update(["thorax", "abdomen"])
        if "psoas" in name_lower:
            regions.update(["abdomen", "pelvis"])
    
    if not regions:
        regions.add("torso")
    
    return list(regions)


def get_object_center(obj: bpy.types.Object) -> List[float]:
    """
    Get the world-space center of an object.
    
    After unparenting and applying transforms, the object's location
    IS the geometry center, so we can just return that.
    
    Returns coordinates converted to Y-up system (for Three.js compatibility).
    """
    loc = obj.matrix_world.translation

    # Enhanced debug - show more context about object position
    if DEBUG_VERBOSE and any(s in obj.name.lower() for s in ["inguinal", "ligament"]):
        print(f"DEBUG {obj.name}:")
        print(f"  Blender loc=[{loc.x:.4f}, {loc.y:.4f}, {loc.z:.4f}]")
        print(f"  Object type: {obj.type}")
        print(f"  Parent: {obj.parent.name if obj.parent else 'None'}")
        print(f"  Data mesh name: {obj.data.name if hasattr(obj, 'data') else 'N/A'}")
        print(f"  Mesh users: {obj.data.users}")
        # print(f"  Mesh is multi-user: {len(obj.data.users) > 1 if hasattr(obj, 'data') and hasattr(obj.data, 'users') else 'Unknown'}")
    
    # Convert from Blender Z-up to Three.js Y-up
    x_threejs = loc.x
    y_threejs = loc.z      # Blender Z becomes Three.js Y
    z_threejs = -loc.y     # Blender Y becomes Three.js -Z
    
    return [round(x_threejs, 4), round(y_threejs, 4), round(z_threejs, 4)]


# ============================================================
# MAIN EXPORT FUNCTIONS
# ============================================================

def find_torso_objects() -> List[bpy.types.Object]:
    """Find all mesh objects that belong to the torso region."""
    torso_objects = []
    
    view_layer_objects = {obj.name for obj in bpy.context.view_layer.objects}
    
    total_meshes = 0
    skipped_not_in_view = 0
    skipped_exclude_pattern = 0
    skipped_exclude_suffix = 0
    skipped_no_torso_match = 0
    
    for obj in bpy.data.objects:
        if obj.type != 'MESH':
            continue
        
        total_meshes += 1
        
        if obj.name not in view_layer_objects:
            skipped_not_in_view += 1
            continue
        
        if matches_pattern(obj.name, EXCLUDE_PATTERNS):
            skipped_exclude_pattern += 1
            continue
        
        if has_excluded_suffix(obj.name):
            skipped_exclude_suffix += 1
            continue
        
        if matches_pattern(obj.name, TORSO_PATTERNS):
            torso_objects.append(obj)
            continue
        
        matched_collection = False
        for collection in obj.users_collection:
            if matches_pattern(collection.name, TORSO_PATTERNS):
                if not matches_pattern(obj.name, EXCLUDE_PATTERNS):
                    torso_objects.append(obj)
                    matched_collection = True
                break
        
        if not matched_collection:
            skipped_no_torso_match += 1
    
    print(f"\nFiltering summary:")
    print(f"  Total meshes in scene: {total_meshes}")
    print(f"  Skipped (not in view layer): {skipped_not_in_view}")
    print(f"  Skipped (exclude pattern): {skipped_exclude_pattern}")
    print(f"  Skipped (exclude suffix): {skipped_exclude_suffix}")
    print(f"  Skipped (no torso match): {skipped_no_torso_match}")
    print(f"  Included: {len(torso_objects)}")
    
    return torso_objects


def fix_object_transforms(objects: List[bpy.types.Object]) -> List[bpy.types.Object]:
    """
    Fix object transforms so that mesh.position in Three.js matches geometry center.
    
    KEY FIX IN V2: We now UNPARENT all objects first, which:
    1. Converts relative transforms to world transforms
    2. Breaks the parent-child hierarchy
    3. Ensures each object stands alone with its world position
    
    The order matters:
    1. Unparent (keep transforms) - converts to world space
    2. Apply all transforms - bakes into vertex data
    3. Set origin to geometry center - moves origin to where vertices are
    
    After this:
    - Object's location = geometry center (what Three.js sees as mesh.position)
    - Vertex data = relative to that center
    - No parent-child relationships = clean glTF hierarchy
    """
    print("\nFixing object transforms (V2 - with unparenting)...")
    
    bpy.ops.object.select_all(action='DESELECT')
    
    valid_objects = []
    fixed_count = 0
    unparented_count = 0
    failed_count = 0
    view_layer_objects = {obj.name for obj in bpy.context.view_layer.objects}
    
    for obj in objects:
        if obj.name not in view_layer_objects:
            print(f"  WARNING: {obj.name} not in view layer, including without transform fix")
            valid_objects.append(obj)
            failed_count += 1
            continue
        
        try:
            # Select only this object
            bpy.ops.object.select_all(action='DESELECT')
            obj.select_set(True)
            bpy.context.view_layer.objects.active = obj
            
            # Debug: Log before state
            debug_log(obj.name, "BEFORE transforms")
            debug_log(obj.name, "Parent", obj.parent.name if obj.parent else "None")
            debug_log(obj.name, "Location", list(obj.location))
            debug_log(obj.name, "World location", list(obj.matrix_world.translation))
            
            # Add detailed info for problematic structures
            if any(s in obj.name.lower() for s in ["inguinal", "ligament"]):
                print(f"    Object type: {obj.type}")
                print(f"    Data mesh name: {obj.data.name if hasattr(obj, 'data') else 'N/A'}")
                print(f"    Users of mesh: {len(obj.data.users) if hasattr(obj, 'data') and hasattr(obj.data, 'users') else 'N/A'}")
            
            # Step 0 (NEW): Unparent while keeping transforms
            # This converts the relative transform to absolute world transform
            if obj.parent is not None:
                debug_log(obj.name, f"Unparenting from {obj.parent.name}")
                # Store world matrix before unparenting
                world_matrix = obj.matrix_world.copy()
                # Clear parent
                obj.parent = None
                # Restore world matrix (this is what "keep transform" does)
                obj.matrix_world = world_matrix
                unparented_count += 1
            
            debug_log(obj.name, "After unparent - Location", list(obj.location))
            
            # Step 1: Apply all transforms
            # This bakes location/rotation/scale into the vertex data
            bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
            
            debug_log(obj.name, "After apply - Location", list(obj.location))
            
            # Step 2: Set origin to geometry center
            # This moves the origin point to where the vertices actually are
            bpy.ops.object.origin_set(type='ORIGIN_CENTER_OF_VOLUME', center='MEDIAN')
            
            debug_log(obj.name, "After origin_set - Location", list(obj.location))
            debug_log(obj.name, "AFTER transforms complete ✓")
            
            valid_objects.append(obj)
            fixed_count += 1
            
        except Exception as e:
            print(f"  WARNING: Could not fix transforms for {obj.name}: {e}")
            valid_objects.append(obj)
            failed_count += 1
    
    print(f"  Transform results: {fixed_count} fixed, {unparented_count} unparented, {failed_count} failed")
    return valid_objects


def prepare_export_objects(objects: List[bpy.types.Object]) -> Dict[str, Any]:
    """
    Prepare objects for export and generate metadata.
    Returns a dictionary with metadata for each structure.
    """
    metadata = {
        "version": "2.0",
        "source": "Z-Anatomy",
        "region": "torso",
        "export_notes": "V2: Objects unparented before transform application for accurate centers",
        "structures": {}
    }
    
    used_ids = set()
    skipped_validation = 0
    
    for obj in objects:
        base_id = normalize_name(obj.name)
        mesh_id = base_id
        counter = 1
        while mesh_id in used_ids:
            mesh_id = f"{base_id}_{counter}"
            counter += 1
        used_ids.add(mesh_id)
        
        original_name = obj.name
        obj.name = mesh_id
        
        struct_type = get_structure_type(obj)
        center = get_object_center(obj)
        
        debug_log(mesh_id, "Final center for metadata", center)
        
        if not validate_structure_center(mesh_id, center, struct_type):
            skipped_validation += 1
        
        metadata["structures"][mesh_id] = {
            "meshId": mesh_id,
            "originalName": original_name,
            "type": struct_type,
            "layer": estimate_layer(obj, struct_type),
            "regions": get_regions(obj),
            "center": center,
        }
    
    if skipped_validation > 0:
        print(f"\n  NOTE: {skipped_validation} structures have suspicious centers (see warnings above)")
    
    return metadata


def export_gltf(objects: List[bpy.types.Object], output_path: str):
    """Export selected objects as a glTF file."""
    bpy.ops.object.select_all(action='DESELECT')
    
    view_layer_objects = {obj.name for obj in bpy.context.view_layer.objects}
    valid_objects = []
    
    for obj in objects:
        if obj.name in view_layer_objects:
            try:
                obj.select_set(True)
                valid_objects.append(obj)
            except RuntimeError as e:
                print(f"Warning: Could not select {obj.name}: {e}")
        else:
            print(f"Warning: {obj.name} not in view layer, skipping")
    
    if not valid_objects:
        print("ERROR: No valid objects to export!")
        return
    
    bpy.context.view_layer.objects.active = valid_objects[0]
    
    print(f"Exporting {len(valid_objects)} objects...")
    
    bpy.ops.export_scene.gltf(
        filepath=output_path,
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
    
    print(f"Exported glTF to: {output_path}")


def export_metadata(metadata: Dict, output_path: str):
    """Export metadata as JSON."""
    with open(output_path, 'w') as f:
        json.dump(metadata, f, indent=2)
    
    print(f"Exported metadata to: {output_path}")


# ============================================================
# MAIN EXECUTION
# ============================================================

def main():
    """Main export function."""
    print("\n" + "=" * 60)
    print("Z-Anatomy Torso Export Script V2.0")
    print("(With parent-child hierarchy fix)")
    print("=" * 60 + "\n")
    
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    print("Scanning for torso structures...")
    torso_objects = find_torso_objects()
    print(f"Found {len(torso_objects)} torso structures\n")
    
    if not torso_objects:
        print("ERROR: No torso structures found!")
        print("Make sure you have Z-Anatomy loaded in Blender.")
        return
    
    print("Structures to export:")
    for obj in sorted(torso_objects, key=lambda o: o.name):
        parent_info = f" (child of {obj.parent.name})" if obj.parent else ""
        print(f"  - {obj.name}{parent_info}")
    print()
    
    # Fix transforms (with unparenting in V2)
    torso_objects = fix_object_transforms(torso_objects)
    
    if not torso_objects:
        print("ERROR: No valid objects after transform fixing!")
        return
    
    print("\nPreparing export...")
    metadata = prepare_export_objects(torso_objects)
    
    gltf_path = os.path.join(OUTPUT_DIR, GLTF_FILENAME)
    print(f"\nExporting glTF to {gltf_path}...")
    export_gltf(torso_objects, gltf_path)
    
    metadata_path = os.path.join(METADATA_OUTPUT_DIR, METADATA_FILENAME)
    print(f"Exporting metadata to {metadata_path}...")
    export_metadata(metadata, metadata_path)
    
    print("\n" + "=" * 60)
    print("Export complete!")
    print(f"  - Model: {gltf_path}")
    print(f"  - Metadata: {metadata_path}")
    print(f"  - Structures exported: {len(metadata['structures'])}")
    print("=" * 60 + "\n")


if __name__ == "__main__":
    main()
