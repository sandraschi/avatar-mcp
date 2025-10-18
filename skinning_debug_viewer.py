#!/usr/bin/env python3
"""
Skinning Debug Viewer - Analyze why torso is missing from VRM models
"""
import sys
import os
import numpy as np
sys.path.insert(0, 'src')

def analyze_vrm_skinning():
    """Analyze VRM skinning data to understand missing torso issue"""
    
    try:
        from avatarmcp.models.vrm_loader import VRMLoader
        
        # Test with Nekomimi-chan first
        vrm_path = r'C:\Users\sandr\.avatarmcp\models\Nekomimi-chan.vrm'
        
        if not os.path.exists(vrm_path):
            print(f"❌ VRM file not found: {vrm_path}")
            return
            
        print(f"🎌 Loading VRM for skinning analysis: {vrm_path}")
        vrm_model = VRMLoader.from_file(vrm_path)
        print(f"✅ Loaded: {len(vrm_model.meshes)} meshes, {len(vrm_model.bones)} bones")
        
        print("\n🦴 BONE ANALYSIS:")
        print(f"  Total bones: {len(vrm_model.bones)}")
        
        # List key bones
        key_bones = ['Hips', 'Spine', 'Chest', 'Neck', 'Head', 'LeftShoulder', 'RightShoulder']
        for bone_name in key_bones:
            if bone_name in vrm_model.bones:
                bone = vrm_model.bones[bone_name]
                print(f"  ✅ {bone_name}: position {bone.position}")
            else:
                print(f"  ❌ {bone_name}: NOT FOUND")
        
        print("\n🔍 MESH SKINNING ANALYSIS:")
        for i, mesh in enumerate(vrm_model.meshes):
            print(f"\n--- MESH {i} ({mesh.name}) ---")
            print(f"  Vertices: {len(mesh.vertices)}")
            print(f"  Faces: {len(mesh.faces)}")
            
            # Check for skinning attributes
            has_joint_indices = hasattr(mesh, 'attributes') and 'joint_indices' in mesh.attributes
            has_joint_weights = hasattr(mesh, 'attributes') and 'joint_weights' in mesh.attributes
            
            print(f"  Has joint indices: {has_joint_indices}")
            print(f"  Has joint weights: {has_joint_weights}")
            
            if has_joint_indices:
                joint_indices = mesh.attributes['joint_indices']
                print(f"  Joint indices shape: {joint_indices.shape}")
                print(f"  Joint indices range: {joint_indices.min()} - {joint_indices.max()}")
                
            if has_joint_weights:
                joint_weights = mesh.attributes['joint_weights']
                print(f"  Joint weights shape: {joint_weights.shape}")
                print(f"  Joint weights range: {joint_weights.min():.3f} - {joint_weights.max():.3f}")
                
                # Check if weights are normalized
                if len(joint_weights.shape) == 2 and joint_weights.shape[1] >= 4:
                    weight_sums = joint_weights.sum(axis=1)
                    print(f"  Weight sums range: {weight_sums.min():.3f} - {weight_sums.max():.3f}")
                    normalized_count = np.sum(np.abs(weight_sums - 1.0) < 0.01)
                    print(f"  Normalized vertices: {normalized_count}/{len(weight_sums)} ({100*normalized_count/len(weight_sums):.1f}%)")
            
            # Analyze vertex positions
            vertices = np.array(mesh.vertices)
            if len(vertices) > 0:
                center = vertices.mean(axis=0)
                min_bounds = vertices.min(axis=0)
                max_bounds = vertices.max(axis=0)
                size = max_bounds - min_bounds
                
                print(f"  Vertex center: ({center[0]:.3f}, {center[1]:.3f}, {center[2]:.3f})")
                print(f"  Vertex bounds: min({min_bounds[0]:.3f}, {min_bounds[1]:.3f}, {min_bounds[2]:.3f})")
                print(f"                 max({max_bounds[0]:.3f}, {max_bounds[1]:.3f}, {max_bounds[2]:.3f})")
                print(f"  Mesh size: ({size[0]:.3f}, {size[1]:.3f}, {size[2]:.3f})")
                
                # Classify mesh by Y position and size
                if center[1] > 1.2:
                    mesh_type = "HEAD/FACE"
                elif center[1] > 0.5 and size[1] > 0.8:
                    mesh_type = "BODY/TORSO"
                elif center[1] > 1.0 and size[0] > 0.25:
                    mesh_type = "HAIR"
                else:
                    mesh_type = "OTHER"
                    
                print(f"  Predicted type: {mesh_type}")
                
                # Check if this might be the missing torso
                if "BODY" in mesh_type or "TORSO" in mesh_type:
                    print("  🚨 THIS MIGHT BE THE MISSING TORSO!")
                    
                    # Check if skinning data exists for body mesh
                    if not (has_joint_indices and has_joint_weights):
                        print("  🔥 PROBLEM: Body mesh has no skinning data!")
                    elif has_joint_weights:
                        # Check if weights are valid
                        weights = mesh.attributes['joint_weights']
                        zero_weight_verts = np.sum(weights.sum(axis=1) < 0.001)
                        print(f"  Zero-weight vertices: {zero_weight_verts}/{len(weights)} ({100*zero_weight_verts/len(weights):.1f}%)")
                        
                        if zero_weight_verts > len(weights) * 0.5:
                            print("  🔥 PROBLEM: Too many vertices have zero weights!")
        
        print("\n📊 SUMMARY:")
        print("The missing torso issue is likely caused by:")
        print("1. Missing or invalid bone weights for body mesh vertices")
        print("2. VRM loader not applying skinning transformations")
        print("3. Body mesh vertices positioned incorrectly without bone influence")
        
    except Exception as e:
        print(f"❌ Error in skinning analysis: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    analyze_vrm_skinning()

