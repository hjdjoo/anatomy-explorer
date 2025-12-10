# Blender Export Scripts

This directory contains Python scripts for exporting anatomical models from Z-Anatomy into formats suitable for Anatomy Explorer.

## Prerequisites

1. **Blender 3.0+** (tested with 3.6+)
   - Download from: https://www.blender.org/download/

2. **Z-Anatomy Blender Template**
   - Download from: https://github.com/Z-Anatomy/Models-of-human-anatomy
   - Follow their installation instructions to set up the template

## Quick Start

### Step 1: Set Up Z-Anatomy

```bash
# Clone the Z-Anatomy repository
git clone https://github.com/Z-Anatomy/Models-of-human-anatomy.git

# Or download the ZIP from GitHub and extract it
```

### Step 2: Open in Blender

1. Open Blender
2. Go to **File > Open**
3. Navigate to the Z-Anatomy folder and open the `.blend` file
4. Wait for all assets to load (may take a minute)

### Step 3: Configure the Export Script

1. Open `export_torso.py` in a text editor
2. Update the `OUTPUT_DIR` variable to point to your project:

```python
# Change this line to your actual path:
OUTPUT_DIR = "/path/to/your/anatomy-explorer/public/models"
```

### Step 4: Run the Export Script

**Option A: From Blender's Text Editor**

1. In Blender, switch to the **Scripting** workspace (top tabs)
2. Click **Open** and select `export_torso.py`
3. Click **Run Script** (or press Alt+P)

**Option B: From Command Line**

```bash
# Run Blender with the script
blender path/to/z-anatomy.blend --background --python export_torso.py
```

### Step 5: Verify the Export

After running, you should have two files in your `public/models/` directory:

- `torso.glb` - The 3D model file
- `torso_metadata.json` - Structure metadata

## What the Script Does

1. **Scans** all objects in the Z-Anatomy file
2. **Filters** to include only torso-related structures (ribs, spine, abdominal muscles, etc.)
3. **Excludes** limbs, head, and neck structures
4. **Renames** objects to clean mesh IDs (e.g., "Rectus abdominis.L" → "rectus_abdominis")
5. **Exports** as a single `.glb` file with all structures as named meshes
6. **Generates** a metadata JSON with structure types, layers, and regions

## Customizing the Export

### Adding/Removing Structures

Edit the pattern lists in `export_torso.py`:

```python
# Add patterns to include more structures
TORSO_PATTERNS = [
    "thorax", "thoracic",
    # Add your patterns here...
]

# Add patterns to exclude structures
EXCLUDE_PATTERNS = [
    "arm", "leg",
    # Add exclusions here...
]
```

### Changing Structure Types

The script infers structure type from Z-Anatomy's collection hierarchy. You can customize the mapping:

```python
COLLECTION_TYPE_MAP = {
    "Bones": "bone",
    "Muscles": "muscle",
    # Add custom mappings...
}
```

## Troubleshooting

### "No torso structures found"

- Make sure Z-Anatomy is properly loaded in Blender
- Check that objects are visible (not hidden)
- Verify the collection hierarchy hasn't changed

### Objects missing in export

- Check if the object name matches an exclude pattern
- Add the object's name pattern to `TORSO_PATTERNS`

### Export fails

- Ensure the output directory exists and is writable
- Check Blender's console for error messages (Window > Toggle System Console)

### Objects have wrong type

- Check which collection the object is in
- Add the collection name to `COLLECTION_TYPE_MAP`

## Output Format

### glTF Structure

The exported `.glb` file contains:

- All mesh geometries as named objects
- Materials (basic, may need adjustment)
- Proper Y-up orientation for Three.js

### Metadata JSON

```json
{
  "version": "1.0",
  "source": "Z-Anatomy",
  "region": "torso",
  "structures": {
    "rectus_abdominis": {
      "meshId": "rectus_abdominis",
      "originalName": "Rectus abdominis.L",
      "type": "muscle",
      "layer": 3,
      "regions": ["abdomen"],
      "center": [0.05, -0.1, 0.15]
    }
    // ... more structures
  }
}
```

## Integrating with Anatomy Explorer

After exporting, you'll need to:

1. **Update `torsoData.ts`** with the actual mesh IDs from your export
2. **Modify `AnatomyModel.tsx`** to load the glTF instead of placeholder geometry

See the main project README for the next steps.

## Scripts in This Directory

| Script | Purpose |
|--------|---------|
| `export_torso.py` | Export torso structures from Z-Anatomy |
| *(planned)* `export_limbs.py` | Export arm/leg structures |
| *(planned)* `export_head.py` | Export head/neck structures |
