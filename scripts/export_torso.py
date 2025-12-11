"""
Z-Anatomy Torso Export Script for Anatomy Explorer

This script exports torso structures from Z-Anatomy's Blender file
into a glTF format suitable for use with react-three-fiber.

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
from mathutils import Vector
from typing import Dict, List, Any

# ============================================================
# CONFIGURATION
# ============================================================

# Output directory - change this to your project's public/models folder
OUTPUT_DIR = os.path.expanduser("~/Code/anatomy-explorer/public/models")

# Output filenames
GLTF_FILENAME = "torso.glb"
METADATA_FILENAME = "torso_metadata.json"

# Structure type mappings based on Z-Anatomy collection names
# Z-Anatomy organizes by system, we need to map to our types
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
# These patterns help identify torso structures in Z-Anatomy's hierarchy
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
    "trapezius",  # Upper portion overlaps torso
    "rhomboid",
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
    "head", "cranial", "cranium",
    "face", "facial",
    "neck", "cervical",  # Neck is debatable, excluding for MVP
    "skull",
    "mandible", "maxilla",
    "eye", "ocular",
    "ear", "auricul",
    "nose", "nasal",
    "tongue", "lingual",
    "teeth", "dental",
    "brain", "cerebr",
    "shoulder", "scapula", "clavicle",  # Excluding for cleaner torso
    "humerus",
]

# ============================================================
# HELPER FUNCTIONS
# ============================================================

def normalize_name(name: str) -> str:
    """Convert Z-Anatomy object name to a clean mesh ID."""
    # Remove common prefixes/suffixes
    clean = name.lower()
    
    # Remove side indicators for now (we'll handle bilateral structures later)
    for suffix in [".l", ".r", "_l", "_r", " left", " right", " (left)", " (right)"]:
        if clean.endswith(suffix):
            clean = clean[:-len(suffix)]
    
    # Replace spaces and special chars with underscores
    clean = clean.replace(" ", "_").replace("-", "_").replace(".", "_")
    
    # Remove double underscores
    while "__" in clean:
        clean = clean.replace("__", "_")
    
    # Strip leading/trailing underscores
    clean = clean.strip("_")
    
    return clean


def matches_pattern(name: str, patterns: List[str]) -> bool:
    """Check if a name matches any of the given patterns."""
    name_lower = name.lower()
    return any(pattern in name_lower for pattern in patterns)


def get_structure_type(obj: bpy.types.Object) -> str:
    """Determine the structure type based on object's collection hierarchy."""
    # Walk up the collection hierarchy to find type indicators
    for collection in obj.users_collection:
        col_name = collection.name
        for key, struct_type in COLLECTION_TYPE_MAP.items():
            if key.lower() in col_name.lower():
                return struct_type
        
        # Check parent collections
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
    
    # Default based on object name heuristics
    name_lower = obj.name.lower()
    if any(bone_word in name_lower for bone_word in ["bone", "vertebra", "rib", "sternum", "pelvis", "sacrum"]):
        return "bone"
    if any(muscle_word in name_lower for muscle_word in ["muscle", "musculus", "abdominis", "dorsi", "pector"]):
        return "muscle"
    
    return "muscle"  # Default fallback


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
        # Estimate based on Z position (front vs back) and name
        name_lower = obj.name.lower()
        
        # Deep muscles
        if any(deep in name_lower for deep in ["transvers", "multifid", "rotat", "intercost", "diaphragm"]):
            return 1
        # Intermediate
        if any(mid in name_lower for mid in ["oblique", "erector", "serratus", "internal"]):
            return 2
        # Superficial
        return 3


def get_regions(obj: bpy.types.Object) -> List[str]:
    """Determine which body regions this structure belongs to."""
    regions = set()
    name_lower = obj.name.lower()
    
    # Check for region indicators in name
    if any(t in name_lower for t in ["thorax", "thoracic", "rib", "sternum", "pector", "intercost"]):
        regions.add("thorax")
    if any(a in name_lower for a in ["abdomen", "abdomin", "rectus", "oblique", "transvers"]):
        regions.add("abdomen")
    if any(p in name_lower for p in ["pelvis", "pelvic", "ilium", "iliac", "ischium", "pubis", "sacrum", "coccyx", "gluteus"]):
        regions.add("pelvis")
    if any(s in name_lower for s in ["lumbar", "lumbo"]) or ("vertebra" in name_lower and "lumbar" in name_lower):
        regions.add("lumbar_spine")
    if "thoracic" in name_lower and "vertebra" in name_lower:
        regions.add("thoracic_spine")
    
    # Structures that span regions
    if any(span in name_lower for span in ["erector", "latissimus", "psoas"]):
        if "erector" in name_lower or "latissimus" in name_lower:
            regions.update(["thorax", "abdomen"])
        if "psoas" in name_lower:
            regions.update(["abdomen", "pelvis"])
    
    # Default to torso if nothing specific found
    if not regions:
        regions.add("torso")
    
    return list(regions)


def get_object_center(obj: bpy.types.Object) -> List[float]:
    """Get the world-space center of an object's mesh vertices.
    
    Returns coordinates in Blender's native system (Z-up):
    [X, Y, Z] where X=right/left, Y=front/back, Z=up/down
    
    The TypeScript side will handle any coordinate system matching.
    """
    try:
        # Get the evaluated mesh (applies modifiers)
        depsgraph = bpy.context.evaluated_depsgraph_get()
        eval_obj = obj.evaluated_get(depsgraph)
        mesh = eval_obj.to_mesh()
        
        if not mesh or len(mesh.vertices) == 0:
            # Fallback to object location if no vertices
            loc = obj.matrix_world.translation
            return [round(loc.x, 4), round(loc.y, 4), round(loc.z, 4)]
        
        # Transform all vertices to world space and find center
        world_matrix = obj.matrix_world
        world_verts = [world_matrix @ v.co for v in mesh.vertices]
        
        # Calculate centroid (average of all vertex positions)
        centroid = sum(world_verts, Vector()) / len(world_verts)
        
        # Clean up the temporary mesh
        eval_obj.to_mesh_clear()
        
        # Return raw Blender coordinates [X, Y, Z] (Z-up)
        return [round(centroid.x, 4), round(centroid.y, 4), round(centroid.z, 4)]
    
    except Exception as e:
        # Fallback to object location on any error
        print(f"Warning: Could not calculate center for {obj.name}: {e}")
        loc = obj.matrix_world.translation
        return [round(loc.x, 4), round(loc.y, 4), round(loc.z, 4)]


# ============================================================
# MAIN EXPORT FUNCTIONS
# ============================================================

def find_torso_objects() -> List[bpy.types.Object]:
    """Find all mesh objects that belong to the torso region."""
    torso_objects = []
    
    # Get objects in the current view layer (only these can be selected/exported)
    view_layer_objects = {obj.name for obj in bpy.context.view_layer.objects}
    
    for obj in bpy.data.objects:
        # Only process mesh objects
        if obj.type != 'MESH':
            continue
        
        # Skip objects not in current view layer (can't be selected for export)
        if obj.name not in view_layer_objects:
            continue
        
        # Skip if it matches exclude patterns
        if matches_pattern(obj.name, EXCLUDE_PATTERNS):
            continue
        
        # Include if it matches torso patterns
        if matches_pattern(obj.name, TORSO_PATTERNS):
            torso_objects.append(obj)
            continue
        
        # Also check collection names
        for collection in obj.users_collection:
            if matches_pattern(collection.name, TORSO_PATTERNS):
                if not matches_pattern(obj.name, EXCLUDE_PATTERNS):
                    torso_objects.append(obj)
                break
    
    return torso_objects


def prepare_export_objects(objects: List[bpy.types.Object]) -> Dict[str, Any]:
    """
    Prepare objects for export and generate metadata.
    Returns a dictionary with metadata for each structure.
    """
    metadata = {
        "version": "1.0",
        "source": "Z-Anatomy",
        "region": "torso",
        "structures": {}
    }
    
    # Track mesh IDs to handle duplicates
    used_ids = set()
    
    for obj in objects:
        # Generate clean mesh ID
        base_id = normalize_name(obj.name)
        mesh_id = base_id
        counter = 1
        while mesh_id in used_ids:
            mesh_id = f"{base_id}_{counter}"
            counter += 1
        used_ids.add(mesh_id)
        
        # Rename object for export (so glTF uses our IDs)
        original_name = obj.name
        obj.name = mesh_id
        
        # Gather metadata
        struct_type = get_structure_type(obj)
        metadata["structures"][mesh_id] = {
            "meshId": mesh_id,
            "originalName": original_name,
            "type": struct_type,
            "layer": estimate_layer(obj, struct_type),
            "regions": get_regions(obj),
            "center": get_object_center(obj),
        }
    
    return metadata


def export_gltf(objects: List[bpy.types.Object], output_path: str):
    """Export selected objects as a glTF file."""
    # Deselect all
    bpy.ops.object.select_all(action='DESELECT')
    
    # Get valid objects (in view layer and selectable)
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
    
    # Set active object
    bpy.context.view_layer.objects.active = valid_objects[0]
    
    print(f"Exporting {len(valid_objects)} objects...")
    
    # Export as glTF
    bpy.ops.export_scene.gltf(
        filepath=output_path,
        use_selection=True,
        export_draco_mesh_compression_enable=True,
        export_format='GLB',  # Binary format, more compact
        export_apply=True,  # Apply modifiers
        export_texcoords=True,
        export_normals=True,
        export_materials='EXPORT',
        export_all_vertex_colors=True,  # Include vertex colors if present
        export_yup=True,  # Y-up for Three.js
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
    print("Z-Anatomy Torso Export Script")
    print("=" * 60 + "\n")
    
    # Ensure output directory exists
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    # Find torso objects
    print("Scanning for torso structures...")
    torso_objects = find_torso_objects()
    print(f"Found {len(torso_objects)} torso structures\n")
    
    if not torso_objects:
        print("ERROR: No torso structures found!")
        print("Make sure you have Z-Anatomy loaded in Blender.")
        return
    
    # List what we found
    print("Structures to export:")
    for obj in sorted(torso_objects, key=lambda o: o.name):
        print(f"  - {obj.name}")
    print()
    
    # Prepare objects and generate metadata
    print("Preparing export...")
    metadata = prepare_export_objects(torso_objects)
    
    # Export glTF
    gltf_path = os.path.join(OUTPUT_DIR, GLTF_FILENAME)
    print(f"Exporting glTF to {gltf_path}...")
    export_gltf(torso_objects, gltf_path)
    
    # Export metadata
    metadata_path = os.path.join(OUTPUT_DIR, METADATA_FILENAME)
    print(f"Exporting metadata to {metadata_path}...")
    export_metadata(metadata, metadata_path)
    
    print("\n" + "=" * 60)
    print("Export complete!")
    print(f"  - Model: {gltf_path}")
    print(f"  - Metadata: {metadata_path}")
    print(f"  - Structures exported: {len(metadata['structures'])}")
    print("=" * 60 + "\n")


# Run if executed directly
if __name__ == "__main__":
    main()