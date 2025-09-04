# VRM File Format and Structure

## Table of Contents
1. [Introduction](#introduction)
2. [File Structure](#file-structure)
3. [Armature and Bones](#armature-and-bones)
4. [Meshes and Geometry](#meshes-and-geometry)
5. [Materials and Textures](#materials-and-textures)
6. [Clothing and Accessories](#clothing-and-accessories)
7. [Blend Shapes](#blend-shapes)
8. [Animations](#animations)
9. [VRM Extensions](#vrm-extensions)
10. [Working with VRM in Code](#working-with-vrm-in-code)

## Introduction

VRM (Virtual Reality Model) is a file format for 3D humanoid avatars, primarily used in virtual reality and metaverse applications. It's based on glTF 2.0 with additional specifications for humanoid avatars.

### Blender Support

Yes, Blender has excellent VRM support through the following add-ons:

1. **VRM Add-on for Blender**
   - Official add-on for VRM import/export
   - Supports VRM 0.x and 1.0
   - Features:
     - Import/Export VRM models
     - Edit materials and textures
     - Adjust armature and weights
     - Export with custom expressions

2. **Installation**
   ```python
   # In Blender:
   # 1. Edit > Preferences > Add-ons
   # 2. Click 'Install...'
   # 3. Select the downloaded VRM add-on (.zip)
   # 4. Enable the add-on
   ```

3. **Common Workflows**
   - **Importing VRM**: File > Import > VRM
   - **Exporting VRM**: File > Export > VRM
   - **Editing**: Full access to mesh, armature, and materials
   - **Testing**: Use the built-in VRM validator

## File Structure

A VRM file is essentially a glTF 2.0 file with additional extensions:

```
.vrm/
├── .vrm/
│   ├── meta.json         # Metadata about the avatar
│   ├── textures/         # Texture files
│   ├── materials/        # Material definitions
│   └── nodes/            # Node hierarchy
├── meshes/              # 3D mesh data
├── skins/               # Skin and bone data
└── animations/          # Animation data
```

## Armature and Bones

### Bone Hierarchy
VRM uses a standard humanoid bone structure based on the VRM specification. Here's a detailed breakdown:

```
Hips (hips)
├── Spine
│   └── Chest
│       ├── UpperChest
│       │   ├── Neck
│       │   │   └── Head
│       │   │       ├── LeftEye
│       │   │       └── RightEye
│       │   ├── LeftShoulder
│       │   │   └── LeftArm
│       │   │       └── LeftForeArm
│       │   │           └── LeftHand
│       │   │               ├── LeftThumbProximal
│       │   │               ├── LeftIndexProximal
│       │   │               └── ... (other fingers)
│       │   └── RightShoulder
│       │       └── RightArm
│       │           └── RightForeArm
│       │               └── RightHand
│       │                   ├── RightThumbProximal
│       │                   └── ... (other fingers)
│       ├── LeftUpLeg
│       │   └── LeftLeg
│       │       └── LeftFoot
│       │           └── LeftToes
│       └── RightUpLeg
│           └── RightLeg
│               └── RightFoot
│                   └── RightToes
└── ... (other bones)
```

### Bone Naming Conventions
- Left/Right prefixes for paired bones
- Standardized names for compatibility
- Optional bones for facial expressions

- **Hips (hips)** - Root of the hierarchy
  - **Spine**
    - **Chest**
      - **UpperChest**
        - **Neck**
          - **Head**
            - **Left/Right Eye**
        - **Left/Right Shoulder**
          - **Upper Arm**
            - **Lower Arm**
              - **Hand**
                - **Fingers**
  - **Left/Right Leg**
    - **Lower Leg**
      - **Foot**
        - **Toes**

### Bone Properties
Each bone typically has:
- Position (x, y, z)
- Rotation (quaternion)
- Scale
- Parent bone reference
- Inverse bind matrices for skinning

## Meshes and Geometry

### Main Body Mesh
- Typically the first mesh in the file
- Contains the base humanoid shape
- Rigged to the armature

### Additional Meshes
- Clothes
- Hair
- Accessories
- Each can have its own materials and textures

## Materials and Textures

### Material Properties
- Base color (albedo)
- Metallic-Roughness values
- Normal maps
- Emissive properties
- Transparency/Alpha settings

### Common Textures
- **Albedo/Diffuse**: Base color texture
- **Normal Map**: Surface detail
- **Metallic-Roughness**: PBR material properties
- **Emissive**: Glow/emission effects
- **Occlusion**: Ambient occlusion data

## Clothing and Accessories

### Attachment System
- Clothes are separate meshes
- Typically skinned to the same armature as the body
- Can have custom blend shapes for better fit

### Common Clothing Items
- Tops (shirts, jackets)
- Bottoms (pants, skirts)
- Shoes
- Hats/headwear
- Accessories (glasses, jewelry)

## Blend Shapes

### Preset Expressions
VRM defines several standard blend shapes:
- **Neutral**
- **Happy**
- **Angry**
- **Sad**
- **Surprised**
- **Aa** (Mouth shape for 'ah' sound)
- **Ih** (Mouth shape for 'ee' sound)
- **Ou** (Mouth shape for 'oh' sound)
- **Ee** (Mouth shape for 'ee' sound)
- **Oh** (Mouth shape for 'o' sound)

### Custom Blend Shapes
- Can be defined for custom expressions
- Used for visemes and facial expressions

## Animations

### Types of Animations
1. **Bone Animations**
   - Transform bone hierarchies over time
   - Used for full-body movements

2. **Morph Target Animations**
   - Animate blend shapes
   - Used for facial expressions and visemes

3. **Procedural Animations**
   - Eye tracking
   - Physics-based simulations (hair, clothing)

## VRM Extensions

### Humanoid
- Defines bone mappings
- Sets up humanoid proportions
- Configures first-person view settings

### FirstPerson
- Defines mesh visibility in first-person view
- Configures look-at behavior

### SpringBone
- Physics-based animation for hair and clothing
- Simulates soft-body dynamics

### LookAt
- Controls eye movement and gaze
- Can target objects or follow the camera

## Practical Examples

### 1. Basic VRM Viewer
```python
import pyvista as pv
from pyvista import examples

def view_vrm(filepath):
    # Load and display VRM
    plotter = pv.Plotter()
    model = pv.read(filepath)
    plotter.add_mesh(model)
    
    # Add coordinate axes
    plotter.show_axes()
    
    # Start interactive viewer
    plotter.show()
```

### 2. Bone Visualization
```python
def visualize_armature(plotter, model):
    """Draw lines between connected bones"""
    if not hasattr(model, 'bones'):
        return
        
    for bone_name, bone in model.bones.items():
        if not hasattr(bone, 'position') or not bone.parent:
            continue
            
        parent = model.bones.get(bone.parent)
        if parent and hasattr(parent, 'position'):
            line = pv.Line(bone.position, parent.position)
            plotter.add_mesh(line, color='red', line_width=2)
```

### 3. Simple Animation
```python
import numpy as np

def wave_hand(model, frame):
    """Simple waving animation"""
    if not hasattr(model, 'bones'):
        return
        
    # Get hand bone (adjust name as needed)
    hand_bone = model.bones.get('RightHand')
    if hand_bone:
        # Simple sine wave motion
        angle = np.sin(frame * 0.1) * 30  # 30 degree range
        hand_bone.rotation.z = np.radians(angle)
```

### 4. Exporting Poses
```python
def save_pose(model, filename):
    """Save bone rotations to a pose file"""
    pose_data = {}
    for name, bone in model.bones.items():
        pose_data[name] = {
            'rotation': bone.rotation.tolist(),
            'position': bone.position.tolist()
        }
    
    import json
    with open(filename, 'w') as f:
        json.dump(pose_data, f, indent=2)
```

### 5. Loading VRM with Materials
```python
def load_vrm_with_materials(filepath):
    """Load VRM with proper material handling"""
    reader = pv.get_reader(filepath)
    model = reader.read()
    
    # Apply basic materials
    for i, mesh in enumerate(model.meshes):
        if hasattr(mesh, 'material'):
            # Apply material properties
            mesh.texture = load_texture(mesh.material.base_color_texture)
            mesh.metallic = mesh.material.metallic_factor
            mesh.roughness = mesh.material.roughness_factor
    
    return model
```

## Working with VRM in Code

### Loading a VRM Model
```python
import pyvista as pv
from pyvista import examples

# Load VRM model
model = pv.read('path/to/model.vrm')

# Visualize
plotter = pv.Plotter()
plotter.add_mesh(model)
plotter.show()
```

### Accessing Bones
```python
def list_bones(model):
    if hasattr(model, 'bones'):
        for bone_name, bone in model.bones.items():
            print(f"Bone: {bone_name}")
            print(f"  Position: {bone.position}")
            print(f"  Parent: {bone.parent}")
```

### Applying a Pose
```python
def apply_pose(model, bone_name, rotation):
    if hasattr(model, 'bones') and bone_name in model.bones:
        model.bones[bone_name].rotation = rotation
        update_skin_weights(model)
```

### Resources
- [VRM Specification](https://vrm.dev/en/)
- [glTF 2.0 Specification](https://www.khronos.org/gltf/)
- [VRM Add-on for Blender](https://github.com/saturday06/VRM_Addon_for_Blender)

## Advanced Topics

### Performance Optimization
- Level of Detail (LOD) systems
- Mesh simplification
- Texture atlasing

### Custom Shaders
- Toon shading
- Subsurface scattering
- Custom lighting models

### Physics
- Collision detection
- Cloth simulation
- Hair dynamics

## Troubleshooting

### Common Issues
1. **Missing Textures**
   - Check texture paths
   - Verify texture formats

2. **Broken Rigging**
   - Verify bone weights
   - Check for missing bones

3. **Animation Problems**
   - Check keyframe interpolation
   - Verify bone constraints

## Conclusion

Understanding the VRM format is essential for working with 3D avatars in virtual environments. By mastering the structure and components of VRM files, you can create more sophisticated and performant avatar systems.
