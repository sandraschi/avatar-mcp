#!/usr/bin/env python3
"""
Comparison VRM Viewer - Compare AnimeGirl2 vs Nekomimi-chan mesh issues
"""
import sys
import os
import time
import numpy as np
from pathlib import Path
sys.path.insert(0, 'src')

def compare_vrm_models():
    """Compare the two VRM models to understand mesh binding issues"""
    
    try:
        from avatarmcp.models.vrm_loader import VRMLoader
        import pyvista as pv
        
        # Load both models
        nekomimi_path = r'C:\Users\sandr\.avatarmcp\models\Nekomimi-chan.vrm'
        animegirl2_path = r'D:\Dev\repos\avatarmcp\models\AnimeGirl2.vrm'
        
        print("🎌 Loading VRM models for comparison...")
        
        # Load Nekomimi-chan
        if os.path.exists(nekomimi_path):
            print(f"📁 Loading Nekomimi-chan from: {nekomimi_path}")
            nekomimi_model = VRMLoader.from_file(nekomimi_path)
            print(f"✅ Nekomimi-chan: {len(nekomimi_model.meshes)} meshes, {len(nekomimi_model.bones)} bones")
        else:
            print(f"❌ Nekomimi-chan not found at: {nekomimi_path}")
            nekomimi_model = None
        
        # Load AnimeGirl2
        if os.path.exists(animegirl2_path):
            print(f"📁 Loading AnimeGirl2 from: {animegirl2_path}")
            animegirl2_model = VRMLoader.from_file(animegirl2_path)
            print(f"✅ AnimeGirl2: {len(animegirl2_model.meshes)} meshes, {len(animegirl2_model.bones)} bones")
        else:
            print(f"❌ AnimeGirl2 not found at: {animegirl2_path}")
            animegirl2_model = None
        
        if not nekomimi_model or not animegirl2_model:
            print("❌ Cannot compare - one or both models failed to load")
            return
        
        # Create side-by-side comparison
        pv.set_plot_theme('document')
        plotter = pv.Plotter(
            shape=(1, 2),
            window_size=[1800, 900],
            title="🎌 VRM Comparison: Nekomimi-chan vs AnimeGirl2"
        )
        
        # Render Nekomimi-chan (left side)
        plotter.subplot(0, 0)
        plotter.add_text("Nekomimi-chan", position='upper_left', font_size=14)
        
        colors_left = ['lightsalmon', 'lightblue', 'darkseagreen']
        for i, mesh in enumerate(nekomimi_model.meshes):
            if len(mesh.vertices) > 0 and len(mesh.faces) > 0:
                pv_mesh = pv.PolyData(mesh.vertices, mesh.faces)
                plotter.add_mesh(
                    pv_mesh, 
                    color=colors_left[i % len(colors_left)], 
                    smooth_shading=True,
                    name=f"nekomimi_mesh_{i}"
                )
        
        plotter.camera_position = [(2, 1.5, 2), (0, 1, 0), (0, 0, 1)]
        plotter.add_axes()
        
        # Render AnimeGirl2 (right side)
        plotter.subplot(0, 1)
        plotter.add_text("AnimeGirl2", position='upper_left', font_size=14)
        
        colors_right = ['lightcoral', 'lightsteelblue', 'lightgreen']
        for i, mesh in enumerate(animegirl2_model.meshes):
            if len(mesh.vertices) > 0 and len(mesh.faces) > 0:
                pv_mesh = pv.PolyData(mesh.vertices, mesh.faces)
                plotter.add_mesh(
                    pv_mesh, 
                    color=colors_right[i % len(colors_right)], 
                    smooth_shading=True,
                    name=f"animegirl2_mesh_{i}"
                )
        
        plotter.camera_position = [(2, 1.5, 2), (0, 1, 0), (0, 0, 1)]
        plotter.add_axes()
        
        # Detailed mesh analysis
        print("\n🔍 DETAILED MESH COMPARISON:")
        print("-" * 60)
        
        for i in range(min(len(nekomimi_model.meshes), len(animegirl2_model.meshes))):
            neko_mesh = nekomimi_model.meshes[i]
            anime_mesh = animegirl2_model.meshes[i]
            
            print(f"\n--- MESH {i} COMPARISON ---")
            print(f"  Nekomimi-chan  : {len(neko_mesh.vertices):5d} vertices, {len(neko_mesh.faces):5d} faces")
            print(f"  AnimeGirl2     : {len(anime_mesh.vertices):5d} vertices, {len(anime_mesh.faces):5d} faces")
            
            # Check for skinning data
            neko_has_joints = hasattr(neko_mesh, 'attributes') and 'joint_indices' in neko_mesh.attributes
            neko_has_weights = hasattr(neko_mesh, 'attributes') and 'joint_weights' in neko_mesh.attributes
            
            anime_has_joints = hasattr(anime_mesh, 'attributes') and 'joint_indices' in anime_mesh.attributes
            anime_has_weights = hasattr(anime_mesh, 'attributes') and 'joint_weights' in anime_mesh.attributes
            
            print(f"  Nekomimi Skinning: joints={neko_has_joints}, weights={neko_has_weights}")
            print(f"  AnimeGirl2 Skinning: joints={anime_has_joints}, weights={anime_has_weights}")
            
            # Calculate mesh bounds
            if len(neko_mesh.vertices) > 0:
                neko_bounds = np.array(neko_mesh.vertices)
                neko_center = neko_bounds.mean(axis=0)
                neko_size = neko_bounds.max(axis=0) - neko_bounds.min(axis=0)
                print(f"  Nekomimi Center : ({neko_center[0]:.3f}, {neko_center[1]:.3f}, {neko_center[2]:.3f})")
                print(f"  Nekomimi Size   : ({neko_size[0]:.3f}, {neko_size[1]:.3f}, {neko_size[2]:.3f})")
            
            if len(anime_mesh.vertices) > 0:
                anime_bounds = np.array(anime_mesh.vertices)
                anime_center = anime_bounds.mean(axis=0)
                anime_size = anime_bounds.max(axis=0) - anime_bounds.min(axis=0)
                print(f"  AnimeGirl2 Center: ({anime_center[0]:.3f}, {anime_center[1]:.3f}, {anime_center[2]:.3f})")
                print(f"  AnimeGirl2 Size  : ({anime_size[0]:.3f}, {anime_size[1]:.3f}, {anime_size[2]:.3f})")
        
        # Bone comparison
        print(f"\n🦴 BONE COMPARISON:")
        print(f"  Nekomimi-chan : {len(nekomimi_model.bones)} bones")
        print(f"  AnimeGirl2    : {len(animegirl2_model.bones)} bones")
        
        # Blend shape comparison
        print(f"\n😮 BLEND SHAPE COMPARISON:")
        print(f"  Nekomimi-chan : {len(nekomimi_model.blend_shapes)} blend shapes")
        print(f"  AnimeGirl2    : {len(animegirl2_model.blend_shapes)} blend shapes")
        
        print(f"\n✅ Comparison viewer setup complete!")
        print(f"🎮 Controls:")
        print(f"  - Mouse: Rotate, pan, zoom each view independently")
        print(f"  - Both models should show the same issues if VRM loader is the problem")
        print(f"  - Press Ctrl+C to exit")
        
        # Show comparison
        plotter.show()
        
    except Exception as e:
        print(f"❌ Error in comparison: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    compare_vrm_models()

