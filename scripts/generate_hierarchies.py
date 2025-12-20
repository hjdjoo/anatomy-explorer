import bpy
from pprint import pprint
import json
import os

ALLOW_COLLECTIONS = ['Skeletal system', 'Joints', 'Muscular system']

OUTPUT_DIR = os.path.expanduser("~/Code/anatomy-explorer/src/data")
FILENAME = 'hierarchies.json'

def blender_test():
    print("Running blender test")

    bpy.context.view_layer.update()
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    all_objs = bpy.context.view_layer.objects
    
    print(len(all_objs), "objects found")

    groups = {
        'Skeletal system.g': {},
        'Joints.g': {},
        'Fasciae.g': {},
        'Muscular system.g': {}
    }
    
    for obj in all_objs:
        groups = update_groups(groups, scan_hierarchy(obj))
        
    filename = "hierarchies.json"
    json_path = os.path.join(OUTPUT_DIR, filename)

    with open(json_path, 'w') as f:
        f.write(json.dumps(groups, indent=2))

def scan_hierarchy(obj, hierarchy = {}):
    
    if obj.parent:
        hierarchy = scan_hierarchy(obj.parent, {obj.name: hierarchy})
    else:
        hierarchy = {obj.name: hierarchy}
        
    return hierarchy


def update_groups(groups, obj_hierarchy):
    
    for key in obj_hierarchy.keys():
        if key in groups:
            print(f"found {key} in group, traversing further before assigning")
            update_groups(groups[key], obj_hierarchy[key])
        else:
            print(f"no key found, assigning key to group")
            groups[key] = obj_hierarchy

    return groups

if __name__ == "__main__":
    blender_test()