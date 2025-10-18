"""
Test script for the enhanced Animation System

This script demonstrates the usage of the new animation system with:
- Animation layering
- Blending between animations
- Event handling
- State management
"""
import sys
import time
import math
from pathlib import Path

# Add the parent directory to the path so we can import avatarmcp
sys.path.append(str(Path(__file__).parent.parent))

from avatarmcp.animation_v2 import (
    AnimationController, 
    AnimationEventType,
    AnimationClip,
    AnimationKeyframe,
    AnimationEvent
)

def create_test_animation(name: str, duration: float = 1.0) -> AnimationClip:
    """Create a simple test animation clip."""
    clip = AnimationClip(
        name=name,
        duration=duration,
        loop=True
    )
    
    # Add some keyframes
    for i in range(5):
        t = i * (duration / 4)
        clip.keyframes.append(AnimationKeyframe(
            time=t,
            bone_name="Hips",
            rotation=(0, 0, 0, 1),
            position=(0, 0, 0.1 * i)
        ))
    
    # Add a footstep event
    clip.events.append(AnimationEvent(
        event_type=AnimationEventType.FOOTSTEP,
        time=duration / 2,
        name="footstep",
        data={"foot": "left" if name == "walk_left" else "right"}
    ))
    
    return clip

def test_basic_animation():
    """Test basic animation functionality."""
    print("\n=== Testing Basic Animation ===")
    
    # Create a controller
    controller = AnimationController()
    
    # Create some test animations
    walk_anim = create_test_animation("walk", 1.0)
    controller._animation_clips["walk"] = walk_anim
    
    # Play the animation
    print("Playing 'walk' animation...")
    controller.play_animation("base", "walk")
    
    # Run the animation for a few seconds
    run_animation_loop(controller, 3.0)

def test_animation_events():
    """Test animation event handling."""
    print("\n=== Testing Animation Events ===")
    
    # Create a controller
    controller = AnimationController()
    
    # Create a test animation with events
    anim = AnimationClip(
        name="event_test",
        duration=2.0,
        loop=True
    )
    
    # Add some events
    anim.events.extend([
        AnimationEvent(
            event_type=AnimationEventType.CUSTOM,
            time=0.5,
            name="custom_event_1",
            data={"value": 42}
        ),
        AnimationEvent(
            event_type=AnimationEventType.SOUND,
            time=1.0,
            name="play_sound",
            data={"sound": "jump"}
        ),
        AnimationEvent(
            event_type=AnimationEventType.EFFECT,
            time=1.5,
            name="sparkle",
            data={"type": "sparkle", "intensity": 0.8}
        )
    ])
    
    controller._animation_clips["event_test"] = anim
    
    # Set up event handlers
    def on_custom_event(layer, state, event):
        print(f"Custom event: {event.name} at {event.time:.2f}s - {event.data}")
    
    def on_sound_event(layer, state, event):
        print(f"Sound event: {event.name} - {event.data['sound']} at {event.time:.2f}s")
    
    def on_effect_event(layer, state, event):
        print(f"Effect event: {event.name} - {event.data['type']} (intensity: {event.data['intensity']})")
    
    controller.add_event_handler(AnimationEventType.CUSTOM, on_custom_event)
    controller.add_event_handler(AnimationEventType.SOUND, on_sound_event)
    controller.add_event_handler(AnimationEventType.EFFECT, on_effect_event)
    
    # Play the animation
    print("Playing 'event_test' animation...")
    controller.play_animation("base", "event_test")
    
    # Run the animation for a few seconds
    run_animation_loop(controller, 4.0)

def test_animation_layering():
    """Test animation layering and blending."""
    print("\n=== Testing Animation Layering ===")
    
    # Create a controller
    controller = AnimationController()
    
    # Create a base layer for body movement
    base_anim = AnimationClip(
        name="base_idle",
        duration=2.0,
        loop=True
    )
    
    # Add some breathing motion
    for i in range(5):
        t = i * 0.5
        y_pos = 1.0 + 0.02 * math.sin(t * math.pi)
        base_anim.keyframes.append(AnimationKeyframe(
            time=t,
            bone_name="Hips",
            position=(0, y_pos, 0)
        ))
    
    # Create an upper body animation
    upper_anim = AnimationClip(
        name="upper_wave",
        duration=2.0,
        loop=True
    )
    
    # Add waving motion to right arm
    for i in range(9):
        t = i * 0.25
        angle = math.sin(t * math.pi) * 0.5
        upper_anim.keyframes.append(AnimationKeyframe(
            time=t,
            bone_name="RightArm",
            rotation=(0, 0, math.sin(angle), 1)
        ))
    
    controller._animation_clips["base_idle"] = base_anim
    controller._animation_clips["upper_wave"] = upper_anim
    
    # Create a new layer for the upper body
    controller.add_layer("upper_body", 1.0)
    
    # Play animations on both layers
    print("Playing 'base_idle' on base layer...")
    print("Playing 'upper_wave' on upper_body layer...")
    controller.play_animation("base", "base_idle")
    controller.play_animation("upper_body", "upper_wave")
    
    # Run the animation for a few seconds
    run_animation_loop(controller, 5.0)
    
    # Test layer weight adjustment
    print("\nFading out upper body layer...")
    start_time = time.time()
    fade_duration = 2.0
    
    while time.time() - start_time < fade_duration:
        # Gradually reduce the weight of the upper body layer
        t = (time.time() - start_time) / fade_duration
        weight = max(0, 1.0 - t)
        controller.layers["upper_body"].weight = weight
        
        # Update the controller
        controller.update()
        
        # Get and print the current pose (simplified)
        bone_poses, _ = controller.get_pose()
        if "Hips" in bone_poses:
            print(f"Hips position: {bone_poses['Hips'][1]}")
        
        time.sleep(1/30)  # ~30 FPS
    
    print("Test complete!")

def run_animation_loop(controller: AnimationController, duration: float, fps: int = 30):
    """Run the animation loop for a specified duration."""
    print(f"Running animation for {duration:.1f} seconds...")
    
    start_time = time.time()
    frame_count = 0
    
    try:
        while time.time() - start_time < duration:
            # Update the controller
            controller.update()
            
            # Get the current pose (we'll just print a summary)
            bone_poses, blend_shapes = controller.get_pose()
            
            # Print a simple status every second
            if frame_count % fps == 0:
                elapsed = time.time() - start_time
                print(f"Time: {elapsed:.1f}s | Active bones: {len(bone_poses)} | Blend shapes: {len(blend_shapes)}")
            
            frame_count += 1
            time.sleep(1/fps)
            
    except KeyboardInterrupt:
        print("\nAnimation stopped by user")
    except Exception as e:
        print(f"\nError in animation loop: {e}")
    finally:
        print(f"Animation finished after {time.time() - start_time:.1f} seconds")

def main():
    """Run all animation tests."""
    print("VRM Animation System Test")
    print("=========================")
    
    tests = [
        ("Basic Animation", test_basic_animation),
        ("Animation Events", test_animation_events),
        ("Animation Layering", test_animation_layering)
    ]
    
    for name, test_func in tests:
        print(f"\n{'='*40}")
        print(f"TEST: {name}")
        print(f"{'='*40}")
        
        try:
            test_func()
            print(f"✅ {name} test passed")
        except Exception as e:
            print(f"❌ {name} test failed: {e}")
            import traceback
            traceback.print_exc()
    
    print("\nAll tests completed!")

if __name__ == "__main__":
    main()
