"""
Z-Anatomy Detailed Transform Diagnostic
Version 2.0 - Deep inspection of parent chain transforms

This script investigates WHY world transforms might not be computing correctly.
It manually walks the parent chain and computes expected world positions.

Run on a FRESH Z-Anatomy file (File > Revert first!)
"""

import bpy
import mathutils
from typing import List, Tuple

# Structures to investigate in detail
INVESTIGATE = [
    "superior_pubic_ligament",
    "inferior_pubic_ligament", 
    "interpubic_disc",
    "pubic_symphysis",
    "inguinal_ligament",
    "inguinal_ligament_1",
]

def get_full_parent_chain(obj: bpy.types.Object) -> List[bpy.types.Object]:
    """Get all parents from object to root."""
    chain = []
    current = obj.parent
    while current:
        chain.append(current)
        current = current.parent
    return chain


def compute_world_matrix_manually(obj: bpy.types.Object) -> mathutils.Matrix:
    """
    Manually compute world matrix by walking parent chain.
    This helps debug if Blender's matrix_world isn't updating correctly.
    """
    # Start with object's local matrix
    world = obj.matrix_local.copy()
    
    # Multiply by each parent's local matrix
    current = obj.parent
    while current:
        world = current.matrix_local @ world
        current = current.parent
    
    return world


def print_transform_details(obj: bpy.types.Object, indent: int = 0):
    """Print detailed transform information for an object."""
    prefix = "  " * indent
    
    print(f"{prefix}Object: {obj.name}")
    print(f"{prefix}  Type: {obj.type}")
    
    # Local transform components
    loc = obj.location
    rot = obj.rotation_euler
    scale = obj.scale
    print(f"{prefix}  Local Location: [{loc.x:.6f}, {loc.y:.6f}, {loc.z:.6f}]")
    print(f"{prefix}  Local Rotation: [{rot.x:.6f}, {rot.y:.6f}, {rot.z:.6f}]")
    print(f"{prefix}  Local Scale: [{scale.x:.6f}, {scale.y:.6f}, {scale.z:.6f}]")
    
    # Matrix local
    ml = obj.matrix_local
    print(f"{prefix}  Matrix Local Translation: [{ml.translation.x:.6f}, {ml.translation.y:.6f}, {ml.translation.z:.6f}]")
    
    # Matrix world (Blender's computed)
    mw = obj.matrix_world
    print(f"{prefix}  Matrix World Translation: [{mw.translation.x:.6f}, {mw.translation.y:.6f}, {mw.translation.z:.6f}]")
    
    # Check if object is hidden or disabled (can affect matrix computation)
    print(f"{prefix}  Hide Viewport: {obj.hide_viewport}")
    print(f"{prefix}  Hide Render: {obj.hide_render}")
    if hasattr(obj, 'visible_get'):
        print(f"{prefix}  Visible: {obj.visible_get()}")


def analyze_object(name: str):
    """Deep analysis of a single object's transforms."""
    obj = bpy.data.objects.get(name)
    if not obj:
        print(f"\n⚠️ Object not found: {name}")
        return
    
    print(f"\n{'='*70}")
    print(f"ANALYZING: {name}")
    print(f"{'='*70}")
    
    # Force matrix update for entire scene
    bpy.context.view_layer.update()
    
    # Also try updating from object directly
    obj.update_tag()
    bpy.context.evaluated_depsgraph_get()
    
    # Get parent chain
    parents = get_full_parent_chain(obj)
    
    print(f"\n--- Object Details ---")
    print_transform_details(obj)
    
    print(f"\n--- Parent Chain ({len(parents)} parents) ---")
    for i, parent in enumerate(parents):
        print(f"\nParent {i+1}:")
        print_transform_details(parent, indent=1)
    
    # Manually compute world position by accumulating transforms
    print(f"\n--- Manual World Position Calculation ---")
    
    # Method 1: Sum of locations (only valid if no rotations)
    total_loc = mathutils.Vector((0, 0, 0))
    total_loc += obj.location
    print(f"  Object location: [{obj.location.x:.6f}, {obj.location.y:.6f}, {obj.location.z:.6f}]")
    
    for i, parent in enumerate(parents):
        total_loc += parent.location
        print(f"  + Parent {i+1} ({parent.name}): [{parent.location.x:.6f}, {parent.location.y:.6f}, {parent.location.z:.6f}]")
    
    print(f"  = Sum of locations: [{total_loc.x:.6f}, {total_loc.y:.6f}, {total_loc.z:.6f}]")
    
    # Method 2: Proper matrix multiplication
    manual_world = compute_world_matrix_manually(obj)
    manual_pos = manual_world.translation
    print(f"  Manual matrix world: [{manual_pos.x:.6f}, {manual_pos.y:.6f}, {manual_pos.z:.6f}]")
    
    # Method 3: Blender's matrix_world
    blender_pos = obj.matrix_world.translation
    print(f"  Blender matrix_world: [{blender_pos.x:.6f}, {blender_pos.y:.6f}, {blender_pos.z:.6f}]")
    
    # Compare
    print(f"\n--- Comparison ---")
    sum_vs_blender = (total_loc - blender_pos).length
    manual_vs_blender = (manual_pos - blender_pos).length
    print(f"  Sum vs Blender: {sum_vs_blender:.6f}m difference")
    print(f"  Manual vs Blender: {manual_vs_blender:.6f}m difference")
    
    if sum_vs_blender > 0.001 or manual_vs_blender > 0.001:
        print(f"  ⚠️ DISCREPANCY DETECTED!")
    else:
        print(f"  ✓ All methods agree")
    
    # If mesh, also compute geometry center
    if obj.type == 'MESH' and obj.data and len(obj.data.vertices) > 0:
        print(f"\n--- Geometry Analysis ---")
        mesh = obj.data
        print(f"  Vertex count: {len(mesh.vertices)}")
        
        # Local geometry center
        local_center = mathutils.Vector((0, 0, 0))
        for v in mesh.vertices:
            local_center += v.co
        local_center /= len(mesh.vertices)
        print(f"  Local geometry center: [{local_center.x:.6f}, {local_center.y:.6f}, {local_center.z:.6f}]")
        
        # World geometry center using matrix_world
        world_center = mathutils.Vector((0, 0, 0))
        for v in mesh.vertices:
            world_co = obj.matrix_world @ v.co
            world_center += world_co
        world_center /= len(mesh.vertices)
        print(f"  World geometry center: [{world_center.x:.6f}, {world_center.y:.6f}, {world_center.z:.6f}]")
        
        # World geometry center using manual matrix
        manual_center = mathutils.Vector((0, 0, 0))
        for v in mesh.vertices:
            world_co = manual_world @ v.co
            manual_center += world_co
        manual_center /= len(mesh.vertices)
        print(f"  Manual world geometry center: [{manual_center.x:.6f}, {manual_center.y:.6f}, {manual_center.z:.6f}]")
        
        # Expected world center (local center + accumulated transforms)
        expected_center = manual_world @ local_center
        print(f"  Expected (matrix @ local_center): [{expected_center.x:.6f}, {expected_center.y:.6f}, {expected_center.z:.6f}]")


def check_scene_state():
    """Check overall scene state that might affect matrix computation."""
    print("\n" + "="*70)
    print("SCENE STATE CHECK")
    print("="*70)
    
    print(f"\nActive view layer: {bpy.context.view_layer.name}")
    print(f"Scene frame: {bpy.context.scene.frame_current}")
    
    # Check if auto-update is enabled
    print(f"\nDependency Graph State:")
    depsgraph = bpy.context.evaluated_depsgraph_get()
    print(f"  Depsgraph mode: {depsgraph.mode}")
    
    # Count object types
    type_counts = {}
    for obj in bpy.data.objects:
        type_counts[obj.type] = type_counts.get(obj.type, 0) + 1
    print(f"\nObject types in scene:")
    for t, c in sorted(type_counts.items()):
        print(f"  {t}: {c}")


def main():
    print("\n" + "="*70)
    print("Z-ANATOMY DETAILED TRANSFORM DIAGNOSTIC V2")
    print("="*70)
    print("\nIMPORTANT: Run this on a FRESH Z-Anatomy file!")
    print("If previous scripts modified the file, do File > Revert first.")
    
    # Force full scene update
    print("\nForcing scene update...")
    bpy.context.view_layer.update()
    
    # Check scene state
    check_scene_state()
    
    # Find and analyze target objects
    found = []
    not_found = []
    
    for pattern in INVESTIGATE:
        # Try exact match first
        if pattern in bpy.data.objects:
            found.append(pattern)
        else:
            # Try partial match
            matches = [o.name for o in bpy.data.objects if pattern.lower() in o.name.lower()]
            if matches:
                found.extend(matches[:2])  # Take first 2 matches
            else:
                not_found.append(pattern)
    
    if not_found:
        print(f"\n⚠️ Objects not found: {not_found}")
    
    print(f"\nAnalyzing {len(set(found))} objects...")
    
    for name in sorted(set(found)):
        analyze_object(name)
    
    print("\n" + "="*70)
    print("DIAGNOSTIC COMPLETE")
    print("="*70)
    print("\nKey things to look for:")
    print("1. Does 'Sum of locations' match 'Blender matrix_world'?")
    print("2. Is the World geometry center in a reasonable position (Z ≈ 0.8-1.0 for pelvis)?")
    print("3. Are any parents showing [0,0,0] location when they shouldn't?")
    print("="*70 + "\n")


if __name__ == "__main__":
    main()