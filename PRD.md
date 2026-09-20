# Product Requirements Document (PRD): avatar-mcp

**Product Name:** AvatarMCP  
**Repository:** `sandraschi/avatar-mcp`  
**Target Version:** 0.5.0  
**MCP Port:** 10793 | **Web Studio Port:** 10792 | **Metrics Port:** 10790  

---

## 1. Executive Summary & Vision

`AvatarMCP` is the fleet's primary avatar orchestrator, managing VRM 3D avatars, VRoid Studio pipeline, VRChat OSC communication, and audio-driven photorealistic digital human video synthesis via **Meituan LongCat-Video-Avatar 1.5**.

---

## 2. Core Capabilities

### 2.1 Audio-Driven Digital Humans (`digital_human_avatar`)
* **Engine:** Meituan LongCat-Video-Avatar 1.5 (Dense DiT).
* **Capabilities:** Audio-driven lip-sync, expression synthesis, and single reference image/video talking human generation (720p @ 30 FPS).
* **Studio UI:** `DigitalHumanStudio` page (`/digital-human`) in `web_sota`.

### 2.2 VRM 3D & Creative Pipeline
* **VRM 2.0 Management:** Active avatar model switching, blend shapes, morph targets, bone transforms, and thumbnail extraction.
* **Creative Pipeline (`avatar_pipeline`):** VRoid Studio export automation, Blender headless validation, and VTube Studio folder staging.

### 2.3 System Integration
* **VRChat OSC:** Real-time bi-directional OSC parameter syncing.
* **FastMCP 3.1+ Portmanteau Tools:** Consolidated tool surface reducing tool explosion to unified operations.

---

## 3. Success Metrics

* **Compatibility:** 100% test coverage pass rate on pytest suite and zero TypeScript errors on `web_sota` `npx tsc --noEmit`.

---

*Maintained by: Antigravity AI Avatar Engineering · 2026*
