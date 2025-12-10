# Models Directory

Place your glTF/glb anatomy models here.

## Expected Files

After running the Blender export script on Z-Anatomy:

- `torso.glb` - Complete torso model with all structures as named meshes

## Model Requirements

- Format: glTF 2.0 (.glb or .gltf)
- Each anatomical structure should be a separate named mesh
- Mesh names should match the `meshId` in `src/data/torsoData.ts`
- Centered at origin
- Scaled appropriately (roughly 1 unit = 1 meter)

## Getting Models

1. Download Z-Anatomy from: https://github.com/Z-Anatomy/Models-of-human-anatomy
2. Open in Blender
3. Run the export script (to be created)
4. Place exported .glb file here
