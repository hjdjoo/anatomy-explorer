"""
Diagnostic Script: Analyze Pectoralis Major Structure
Run this in Blender to understand why pectoralis major is excluded from export.
"""

import bpy

def diagnose_pectoralis():
    print("\n" + "="*70)
    print("PECTORALIS MAJOR DIAGNOSTIC REPORT")
    print("="*70)
    
    # Get view layer object names for visibility check
    view_layer_names = {o.name for o in bpy.context.view_layer.objects}
    
    # Find all pectoralis-related objects
    pec_objects = []
    for obj in bpy.data.objects:
        if "pector" in obj.name.lower():
            pec_objects.append(obj)
    
    print(f"\nFound {len(pec_objects)} objects with 'pector' in name:\n")
    
    # Categorize by type
    by_type = {}
    for obj in pec_objects:
        obj_type = obj.type
        if obj_type not in by_type:
            by_type[obj_type] = []
        by_type[obj_type].append(obj)
    
    print("Objects by type:")
    for t, objs in sorted(by_type.items()):
        print(f"  {t}: {len(objs)}")
    
    # Detailed report
    print("\n" + "-"*70)
    print("DETAILED OBJECT ANALYSIS:")
    print("-"*70)
    
    for obj in sorted(pec_objects, key=lambda x: x.name):
        in_view_layer = obj.name in view_layer_names
        is_visible = not obj.hide_viewport and not obj.hide_get()
        
        # Get parent chain
        parent_chain = []
        current = obj.parent
        while current:
            parent_chain.append(current.name)
            current = current.parent
        
        # Get collections
        collections = [c.name for c in obj.users_collection]
        
        # Get mesh info if applicable
        mesh_info = ""
        if obj.type == 'MESH' and obj.data:
            vert_count = len(obj.data.vertices)
            mesh_info = f"  (verts: {vert_count})"
        
        # Status indicators
        status = []
        if not in_view_layer:
            status.append("❌ NOT IN VIEW LAYER")
        if not is_visible:
            status.append("❌ HIDDEN")
        if obj.type != 'MESH':
            status.append(f"⚠️ TYPE={obj.type}")
        if not status:
            status.append("✓ SHOULD BE EXPORTED")
        
        print(f"\n{obj.name}")
        print(f"  Type: {obj.type}{mesh_info}")
        print(f"  Status: {' | '.join(status)}")
        print(f"  In View Layer: {in_view_layer}")
        print(f"  Visible: {is_visible}")
        if parent_chain:
            print(f"  Parent Chain: {' → '.join(parent_chain[:5])}")
        print(f"  Collections: {collections}")
    
    # Check specifically for composite muscle patterns
    print("\n" + "-"*70)
    print("COMPOSITE MUSCLE GROUP ANALYSIS:")
    print("-"*70)
    
    groups = [o for o in pec_objects if o.name.endswith('.g')]
    print(f"\nFound {len(groups)} .g group containers:")
    
    for group in groups:
        print(f"\n  {group.name}:")
        children = [o for o in bpy.data.objects if o.parent == group]
        
        if not children:
            print("    ❌ NO CHILDREN FOUND")
        else:
            print(f"    Children ({len(children)}):")
            for child in children:
                in_vl = child.name in view_layer_names
                print(f"      - {child.name} ({child.type}) {'✓' if in_vl else '❌ not in view layer'}")
    
    # Summary
    print("\n" + "="*70)
    print("SUMMARY:")
    print("="*70)
    
    mesh_pecs = [o for o in pec_objects if o.type == 'MESH']
    exportable = [o for o in mesh_pecs if o.name in view_layer_names]
    
    print(f"\nTotal pectoralis objects: {len(pec_objects)}")
    print(f"  - MESH type: {len(mesh_pecs)}")
    print(f"  - In view layer: {len(exportable)}")
    print(f"  - NOT in view layer: {len(mesh_pecs) - len(exportable)}")
    
    if len(mesh_pecs) > len(exportable):
        print("\n⚠️  ISSUE: Some pectoralis meshes are NOT in view layer!")
        print("   This is why they're being excluded from export.")
        print("   These meshes need to be made visible/linked to the scene.")
        
        missing = [o for o in mesh_pecs if o.name not in view_layer_names]
        print(f"\n   Missing meshes:")
        for m in missing:
            print(f"     - {m.name}")
    
    if not mesh_pecs:
        print("\n⚠️  ISSUE: No MESH objects found with 'pector' in name!")
        print("   The pectoralis objects may be EMPTY groups only.")
    
    print("\n" + "="*70 + "\n")


if __name__ == "__main__":
    diagnose_pectoralis()