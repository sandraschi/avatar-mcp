# 🐱 Nekomimi-chan VRM to VRChat Full Pipeline Implementation Guide

**Project**: AvatarMCP VRChat Integration  
**Date**: August 19, 2025  
**Status**: Implementation Roadmap  
**Target**: Complete VRM → VRChat dancing avatar with AI control

## 🎯 Project Goal

Create a complete pipeline for **Nekomimi-chan** (cat-eared avatar) to:
- ✅ Load VRM models in Unity
- 🎵 Dance and perform in VRChat  
- 👁️ See (camera input processing)
- 👂 Hear (audio input processing)  
- 🗣️ Speak (TTS output)
- 🎤 Sing (musical performance)
- 🎮 Full OSC control from external AI system

## 🏗️ Architecture Overview

```
VRM Model → Unity Pipeline → VRChat → OSC Control ← AI Brain
    ↓           ↓              ↓         ↑           ↑
VRM Import → Avatar Setup → World Sync → Parameters ← Claude/AI
    ↓           ↓              ↓         ↑           ↑
Rigging   → Animations  → Performance → Triggers  ← Sensors
```

## 📋 Implementation Phases

### Phase 1: VRM Loading & Unity Setup ⚡ (Current Priority)
**Location**: `D:\Dev\repos\Unity_TransparentWindowManager` + `D:\Dev\repos\avatarmcp`

#### 1.1 Unity Project Foundation
- [x] Unity 2022.3 LTS installed
- [x] Unity_TransparentWindowManager cloned
- [ ] VRM SDK integration
- [ ] UniVRM package import
- [ ] Basic VRM loading scene

#### 1.2 VRM Import Pipeline
```csharp
// Target implementation
public class VRMLoader : MonoBehaviour {
    public void LoadVRMFromFile(string vrmPath);
    public void LoadVRMFromWeb(string url);
    public void SetupVRChatCompatibility();
    public void ExportToVRChat();
}
```

#### 1.3 Essential Unity Packages
```
com.unity.xr.management
com.vrmc.gltf
com.vrmc.univrm
com.vrchat.avatars  
com.vrchat.base
```

### Phase 2: VRChat Avatar Setup 🎮
**Timeline**: 2-3 days after Phase 1

#### 2.1 VRChat SDK Integration
- [ ] VRChat Creator Companion setup
- [ ] Avatar descriptor configuration
- [ ] Expression parameters setup
- [ ] Gesture layer configuration

#### 2.2 Avatar Requirements
```
VRChat Avatar Specs:
- Polygon count: <32k triangles
- Materials: <16 materials  
- Bones: <256 bones
- PhysBones: <64 components
- Expressions: 16 bool, 16 float, 8 int parameters
```

#### 2.3 Nekomimi Features
- Cat ears with physics
- Tail animation
- Facial expressions (happy, surprised, sleepy)
- Eye tracking/blinking
- Mouth shapes for speech

### Phase 3: OSC Control System 🎛️
**Location**: `D:\Dev\repos\oscmcp` + new OSC bridge

#### 3.1 OSC Parameter Mapping
```python
# Avatar parameters for Nekomimi-chan
OSC_PARAMETERS = {
    # Movement
    'VelocityX': '/avatar/parameters/VelocityX',
    'VelocityY': '/avatar/parameters/VelocityY', 
    'VelocityZ': '/avatar/parameters/VelocityZ',
    
    # Expressions
    'Happy': '/avatar/parameters/Happy',
    'Surprised': '/avatar/parameters/Surprised',
    'Sleepy': '/avatar/parameters/Sleepy',
    
    # Cat features
    'EarTwitch': '/avatar/parameters/EarTwitch',
    'TailWag': '/avatar/parameters/TailWag',
    
    # Audio/Speech
    'Viseme_aa': '/avatar/parameters/Viseme_aa',
    'Viseme_E': '/avatar/parameters/Viseme_E',
    'Viseme_ih': '/avatar/parameters/Viseme_ih',
    # ... all 15 visemes
    
    # Dance/Performance
    'Dance_Beat': '/avatar/parameters/Dance_Beat',
    'Dance_Style': '/avatar/parameters/Dance_Style',
    'Performance_Mode': '/avatar/parameters/Performance_Mode'
}
```

#### 3.2 OSC Bridge Implementation
```python
# File: avatarmcp/src/osc_bridge.py
class VRChatOSCBridge:
    def __init__(self, ip='127.0.0.1', port=9000):
        self.client = SimpleUDPClient(ip, port)
    
    def send_expression(self, emotion: str, intensity: float):
        """Send facial expression to VRChat"""
        
    def send_dance_command(self, style: str, tempo: float):
        """Trigger dance animations"""
        
    def send_speech_visemes(self, text: str):
        """Convert text to viseme sequence"""
        
    def send_audio_reaction(self, audio_data: np.array):
        """React to audio input"""
```

### Phase 4: AI Sensory Integration 👁️👂
**Components**: Computer vision, audio processing, TTS

#### 4.1 Vision System
```python
# Eye tracking and scene analysis
class VisionProcessor:
    def __init__(self):
        self.camera = cv2.VideoCapture(0)
        self.face_detector = dlib.get_frontal_face_detector()
    
    def detect_faces(self) -> List[Face]:
        """Detect faces for interaction"""
        
    def analyze_scene(self) -> SceneData:
        """Understand environment"""
        
    def track_movement(self) -> MotionData:
        """Track user movement for reactions"""
```

#### 4.2 Audio System
```python
# Hearing and speech processing
class AudioProcessor:
    def __init__(self):
        self.mic = pyaudio.PyAudio()
        self.tts_engine = pyttsx3.init()
    
    def listen_continuously(self):
        """Process audio input"""
        
    def generate_speech(self, text: str):
        """Text-to-speech output"""
        
    def analyze_music(self, audio_data) -> BeatData:
        """Extract beat for dancing"""
```

### Phase 5: Performance & Dancing 💃
**Integration**: Beat detection, choreography, musical sync

#### 5.1 Dance System
```python
class DanceChoreographer:
    def __init__(self):
        self.beat_detector = BeatDetector()
        self.move_library = self.load_dance_moves()
    
    def sync_to_music(self, audio_stream):
        """Synchronize avatar to music"""
        
    def generate_choreography(self, mood: str, tempo: float):
        """Create dance sequence"""
        
    def trigger_performance(self, performance_type: str):
        """Execute full performance"""
```

#### 5.2 Animation Sequences
- **Nekomimi Dance Moves**:
  - Cat stretch and yawn
  - Playful pounce motions
  - Tail swish choreography
  - Ear twitch to beat
  - Cute pose variations

### Phase 6: AI Brain Integration 🧠
**Connection**: Claude MCP → OSC → VRChat

#### 6.1 AI Decision Engine
```python
class NekomimiBrain:
    def __init__(self, claude_client):
        self.claude = claude_client
        self.personality = self.load_nekomimi_personality()
        
    def process_environment(self, vision_data, audio_data):
        """Understand surroundings"""
        
    def decide_action(self, context) -> ActionPlan:
        """Choose appropriate response"""
        
    def execute_performance(self, action_plan):
        """Coordinate all systems"""
```

## 🛠️ Tools & Dependencies

### Unity Tools
- **Unity 2022.3 LTS**
- **UniVRM 0.112+** (VRM import/export)
- **VRChat Creator Companion**
- **Blender 4.0+** (avatar editing)
- **VSeeFace** (testing facial tracking)

### Python Libraries
```requirements
fastmcp>=2.12.0
python-osc>=1.8.0
opencv-python>=4.8.0
librosa>=0.10.0
pyttsx3>=2.90
speechrecognition>=3.10.0
numpy>=1.24.0
```

### Development Environment
- **Windsurf IDE** (primary development)
- **Unity Editor** (avatar setup)
- **VRChat** (testing environment)
- **OBS Studio** (streaming/recording)

## 📝 Implementation Order (Next Steps for Windsurf)

### Immediate (Today/Tomorrow):
1. **Setup VRM import in Unity**
   - Import UniVRM package
   - Create VRM loading scene
   - Test basic VRM model import

2. **Basic OSC connection**
   - Setup python-osc in avatarmcp
   - Test simple parameter sending
   - Verify VRChat receives commands

### This Week:
3. **Avatar preparation**
   - Download/create Nekomimi VRM model
   - Setup VRChat avatar descriptor
   - Configure basic expressions

4. **OSC parameter mapping**
   - Map all essential avatar parameters
   - Test facial expressions via OSC
   - Implement basic movement control

### Next Week:
5. **Sensory integration**
   - Camera input processing
   - Audio input handling
   - Basic AI response system

6. **Performance system**
   - Beat detection implementation
   - Dance move library creation
   - Music synchronization

## 🎵 Nekomimi-chan Personality Profile

**Character**: Playful cat-girl AI assistant
**Traits**: 
- Curious and energetic
- Responds to music with dancing
- Shows cat-like behaviors (stretching, ear twitches)
- Friendly and helpful
- Expressive with emotes and gestures

**Interaction Patterns**:
- Tilts head when confused
- Ears perk up when interested  
- Tail swishes when excited
- Stretches when bored
- Dances to any music detected

## 🔧 Technical Specifications

### VRM Model Requirements:
- **Format**: VRM 1.0 compatible
- **Polygons**: <20k triangles (VRChat optimized)
- **Textures**: 2048x2048 max, PBR materials
- **Bones**: Standard humanoid + cat ears + tail
- **BlendShapes**: Full face rig with cat expressions

### OSC Communication:
- **Protocol**: OSC 1.0 over UDP
- **Port**: 9000 (VRChat default)
- **Rate**: 60 FPS parameter updates
- **Format**: Float32 for continuous, Bool for triggers

### Performance Targets:
- **Latency**: <50ms OSC response time
- **FPS**: 60+ in Unity, 90+ in VRChat
- **CPU**: <30% usage for AI processing
- **Memory**: <2GB total system usage

## 🚀 Getting Started Command

```bash
# Windsurf should start here:
cd D:\Dev\repos\avatarmcp
# 1. Setup Unity VRM import
# 2. Create OSC bridge
# 3. Test basic parameter control
# 4. Implement vision/audio
# 5. Add dance choreography
```

**Priority**: High  
**Complexity**: Advanced (multi-system integration)  
**Timeline**: 2-3 weeks for full implementation  
**Success Metric**: Nekomimi-chan dancing in VRChat, controlled by AI

---

*Ready to bring Nekomimi-chan to life! 🐱✨*
