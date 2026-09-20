# Handover Document for Claude (`avatar-mcp`)

**Repository:** `avatar-mcp`  
**Last Updated:** 2026-08-21  
**Status:** Operational (v0.5.0) · VRM 2.0 + LongCat Digital Human Engine · 100% Test Pass Rate  

---

## 1. System Architecture & Ports

| Component | Port / Scheme | Description |
|---|---|---|
| **Metrics Collector** | `:10790` | Prometheus health and diagnostics telemetry |
| **SOTA Web Dashboard** | `:10792` | Vite + React + Tailwind dashboard (`web_sota`) |
| **FastMCP Backend** | `:10793` | FastMCP 3.1+ portmanteau tool server |
| **VRChat OSC Sync** | `:9000` / `:9001` | Bi-directional OSC parameter client & server |
| **LongCat Sidecar** | `http://localhost:8189` | Meituan LongCat-Video-Avatar 1.5 sidecar |

---

## 2. Core Capabilities & Recent Accomplishments (v0.5.0)

1. **Meituan LongCat-Video-Avatar 1.5 Integration:**
   - **Engine Service:** Authored [`avatarmcp.digital_human.LongCatAvatarService`](../src/avatarmcp/digital_human/longcat_avatar_service.py) for audio-driven photorealistic digital human video synthesis (audio + reference portrait $\rightarrow$ 720p @ 30 FPS MP4 video).
   - **`digital_human_avatar` Portmanteau Tool:** Registered tool in [`digital_human_tool.py`](../src/avatarmcp/tools/portmanteau/digital_human_tool.py) supporting `longcat_status`, `longcat_generate`, `lipsync_drive`, and `vroid_animate`.
   - **VRoid Bridge:** Connected VRoid Studio character renders to LongCat audio-driven digital human video generation (`vroid_to_longcat_avatar` in [`service.py`](../src/avatarmcp/pipeline/service.py)).
   - **Digital Human Studio Web UI:** Built [`digital-human.tsx`](../web_sota/src/pages/digital-human.tsx) (`/digital-human`) in `web_sota`.

2. **VRM 2.0 & Creative Pipeline:**
   - Full VRM model loading, thumbnail extraction, blend shapes, morph targets, and bone manipulation.
   - Headless Blender validation (`blender_validate`) and VTube Studio staging (`stage_for_vts`).

3. **Product Requirements & Specifications:**
   - Authored PRD [`PRD.md`](../PRD.md) (v0.5.0), updated [`README.md`](../README.md), [`CHANGELOG.md`](../CHANGELOG.md), and published [`mcp-central-docs/integrations/longcat-avatar.md`](../../mcp-central-docs/integrations/longcat-avatar.md).

---

## 3. FastMCP Tool Surface (16 Portmanteau Tools)

FastMCP tools are consolidated into operation-based portmanteau tools:
- `digital_human_avatar`: LongCat status, video generation, lip-sync, and VRoid animation.
- `avatar_pipeline`: Creative pipeline status, hub auth, download, staging, and validation.
- `avatar_manager`: VRM model loading, active switching, and blend shape inspection.
- `animation_manager`: Animation playback, looping, and bone control.
- `system_monitor`: Initialization, shutdown, and telemetry.

---

## 4. Verification Commands

```powershell
# Run avatar-mcp Python test suite
uv run pytest tests/test_longcat_avatar.py -q

# Run web_sota TypeScript check
npx tsc --noEmit (in web_sota)
```

---

*Handover document prepared by Antigravity AI Orchestrator · 2026*
