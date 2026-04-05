# Product Requirements Document (PRD)

## 1. Overview

### 1.1 Purpose
This document outlines the requirements for the AvatarMCP 3D Visualization System, which provides real-time 3D visualization of VRM avatars with interactive controls.

### 1.2 Product Scope
The 3D visualization system enables users to:
- View and manipulate VRM avatars in real-time
- Adjust lighting and environment settings
- Toggle between different visualization modes
- Interact with the 3D viewport using mouse and keyboard controls

## 2. User Stories

### 2.1 Core Visualization
- As a user, I want to see my VRM avatar in a 3D viewport so I can visualize changes in real-time.
- As a user, I want to rotate, pan, and zoom the camera to examine my avatar from all angles.
- As a user, I want to switch between different view modes (solid, wireframe, etc.) to better understand the model structure.

### 2.2 Performance
- As a user with a low-end system, I want to adjust quality settings to maintain good performance.
- As a power user, I want to access advanced visualization features for detailed inspection.

### 2.3 Usability
- As a new user, I want intuitive controls that don't require reading documentation.
- As an experienced user, I want keyboard shortcuts for faster workflow.

## 3. Functional Requirements

### 3.1 Viewport Controls
| ID | Requirement | Priority | Status |
|----|------------|----------|--------|
| FR1 | Support mouse-based camera controls (rotate, pan, zoom) | Must | Implemented |
| FR2 | Provide keyboard shortcuts for common actions | Should | Implemented |
| FR3 | Support view reset to default position | Could | Implemented |
| FR4 | Multiple viewport layouts (single, quad, etc.) | Could | Planned |
| FR4.1 | **16 Consolidated Portmanteau Tools**: Essential tool count for FastMCP compliance; raw core tools are not registered; bootstrap via `system_monitor(operation="initialize")` | Must | Implemented |

### 3.2 Visualization Modes
| ID | Requirement | Priority | Status |
|----|------------|----------|--------|
| FR5 | Solid rendering with textures | Must | Implemented |
| FR6 | Wireframe mode | Should | Implemented |
| FR7 | Shaded mode without textures | Could | Implemented |
| FR8 | X-ray mode for seeing through meshes | Could | Implemented |

### 3.3 Lighting & Environment
| ID | Requirement | Priority | Status |
|----|------------|----------|--------|
| FR9 | Adjustable light intensity and direction | Should | Implemented |
| FR10 | Toggleable shadows | Could | Implemented |
| FR11 | Custom environment maps | Could | Planned |

## 4. Non-Functional Requirements

### 4.1 Performance
- The viewport should maintain at least 30 FPS on mid-range hardware
- Memory usage should not exceed 500MB for a single avatar
- Startup time should be under 5 seconds

### 4.2 Compatibility
- Support for Windows 10/11
- Support for VRM 2.0 specification
- OpenGL 3.3+ compatibility

### 4.3 Accessibility
- High contrast mode for better visibility
- Configurable UI scaling
- Support for screen readers

## 5. Technical Architecture

### 5.1 Components
- **Viewport**: Main 3D rendering component
- **Camera**: Handles view transformations
- **Lighting**: Manages light sources and shadows
- **Material System**: Handles shaders and textures
- **Input Handler**: Processes user input
- **Portmanteau Engine**: Dispatches operations to specialized managers (Animation, Emotion, etc.)

### 5.2 Data Flow
1. User loads VRM model
2. Model data is parsed and sent to GPU
3. Viewport renders the model using current settings
4. User interactions update camera/lighting parameters
5. Viewport re-renders as needed

## 6. User Interface

### 6.1 Viewport
- Main 3D canvas
- Camera controls overlay
- Performance metrics display
- Quick access to view modes

### 6.2 Control Panels
- Lighting controls
- Environment settings
- Display options
- Performance settings

## 7. Future Enhancements
- VR support
- Animation timeline
- Material editor
- Multi-avatar support
- Post-processing effects

## 8. Success Metrics
- 95% of users can perform basic navigation without documentation
- Average FPS > 30 on target hardware
- < 1% crash rate
- 90% user satisfaction in post-release survey

## 9. Open Issues
- Performance optimization for complex models
- Better error handling for unsupported GPUs
- Documentation for advanced features

## 10. Recent Updates (Tool Surface & Webapp)
- **Portmanteau-only tool list**: Raw tools (CoreAvatarTools, CoreSystemTools, CoreUnityIntegrationTools) are no longer registered; clients see only the 16 portmanteau tools. Call `system_monitor` with `operation="initialize"` first, then use other portmanteau tools.
- **Webapp Settings**: Ollama model discovery and selection (GET/PUT `/api/v1/settings/llm`, Ollama status/models endpoints). Loops page uses SOTA backend `/api/v1/intelligence/loops` and relative URLs.
- **Cursor/IDE stdio**: Banner suppression and stdout patching so stdio MCP does not corrupt the JSON-RPC stream.
