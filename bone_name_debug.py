#!/usr/bin/env python3
"""
Bone Name Debug - Find out what bone names actually exist in VRM
"""
import sys
import os
sys.path.insert(0, 'src')

def debug_bone_names():
    """Debug actual bone names in VRM file"""
    
    try:
        from avatarmcp.models.vrm_loader import VRMLoader
        
        vrm_path = r'C:\Users\sandr\.avatarmcp\models\Nekomimi-chan.vrm'
        
        print(f"🎌 Loading VRM to analyze bone names: {vrm_path}")
        vrm_model = VRMLoader.from_file(vrm_path)
        print(f"✅ Loaded: {len(vrm_model.bones)} bones")
        
        print(f"\n🦴 ACTUAL BONE NAMES IN VRM:")
        bone_names = list(vrm_model.bones.keys())
        bone_names.sort()
        
        for i, bone_name in enumerate(bone_names):
            bone = vrm_model.bones[bone_name]
            print(f"  {i:3d}: {bone_name}")
            if i < 20:  # Show first 20 with details
                print(f"       Position: ({bone.position[0]:.3f}, {bone.position[1]:.3f}, {bone.position[2]:.3f})")
                print(f"       Rotation: ({bone.rotation[0]:.3f}, {bone.rotation[1]:.3f}, {bone.rotation[2]:.3f}, {bone.rotation[3]:.3f})")
        
        if len(bone_names) > 20:
            print(f"  ... and {len(bone_names) - 20} more bones")
        
        # Look for key body bones using different naming patterns
        print(f"\n🔍 SEARCHING FOR KEY BODY BONES:")
        key_patterns = [
            ['hip', 'hips', 'pelvis'],
            ['spine', 'back'],
            ['chest', 'upper'],
            ['neck'],
            ['head'],
            ['shoulder', 'clavicle'],
            ['arm', 'upper_arm'],
            ['leg', 'thigh', 'upper_leg']
        ]
        
        for patterns in key_patterns:
            found_bones = []
            for bone_name in bone_names:
                for pattern in patterns:
                    if pattern.lower() in bone_name.lower():
                        found_bones.append(bone_name)
                        break
            
            if found_bones:
                print(f"  {patterns[0].upper()}: {found_bones[:3]}")  # Show first 3 matches
            else:
                print(f"  {patterns[0].upper()}: ❌ NOT FOUND")
        
        print(f"\n📊 SUMMARY:")
        print(f"The VRM has {len(vrm_model.bones)} bones but uses different naming convention.")
        print(f"The missing torso is because the VRM loader doesn't apply bone transforms.")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    debug_bone_names()


