# Creative Pipeline (avatar-mcp)

Orchestrates VRM acquisition, validation, and staging across the fleet.

**Central docs:** `D:/Dev/repos/mcp-central-docs/docs/avatars/`

## Web UI

Start avatar-mcp, open **http://127.0.0.1:10792/pipeline**

## MCP tool: `avatar_pipeline`

All operations accept a single `params` dict with `operation` key.

### Hub operations

| Operation | Key params |
|-----------|------------|
| `hub_auth` | `auth_step`: `status` \| `start` \| `complete` \| `set_token`; `auth_code`, `oauth_state`, `access_token` |
| `hub_download` | `character_model_id`, `vrm_filename`, `model_type_override` |
| `hub_to_studio` | `character_model_id` and/or `project_path` (.vroid), `depot_id`, `open_in_studio`, `export_after`, `output_name` |

### Depot (local catalog)

| Operation | Key params |
|-----------|------------|
| `depot_list` | `depot_kind`: `vrm` \| `vroid`; `scan_depot`: true |
| `depot_register` | `source_path`, `copy_to_depot`, `character_model_id` |
| `depot_get` | `depot_id` |
| `depot_scan` | Rescan staging/hub/output |

**OAuth redirect URI** (register at hub.vroid.com):

```text
http://127.0.0.1:10793/api/v1/pipeline/hub/callback
```

**Environment:**

```powershell
$env:VROID_HUB_CLIENT_ID = "..."
$env:VROID_HUB_CLIENT_SECRET = "..."
# Dev only:
$env:VROID_HUB_ACCESS_TOKEN = "..."
```

### Local / VRoid / Blender

| Operation | Key params |
|-----------|------------|
| `hub_stage_file` | `source_path`, `vrm_filename` |
| `vroid_quick_avatar` | `vrm_filename`, `pick_sample` |
| `blender_validate` | `vrm_filename` |
| `blender_reexport` | `vrm_filename`, `output_name` |
| `stage_for_vts` | `vrm_filename`, `label` |
| `full_pipeline` | `vrm_filename`, `skip_vroid`, `pick_sample` |
| `list_staging` | — |
| `longcat_avatar_status` | — |
| `longcat_avatar_generate` | `source_path` (audio), `vrm_filename` (reference image .png/.jpg/.webp), `label` (prompt), `output_name` |
| `status` | — |

## Staging layout

Default root: `%USERPROFILE%\.avatarmcp\pipeline` or `AVATAR_PIPELINE_WORK_DIR`

```text
pipeline/
  hub/          # Hub downloads
  staging/      # Active VRMs
  output/       # Blender re-exports
  depot/
    catalog.json
    vrm/
    projects/
  staging/vts/  # VTube manifests
  hub/token.json
```

## model_type detection

Module: `src/avatarmcp/pipeline/vrm_type_detect.py`

On import, writes `{model_id}.meta.json` with:

- `model_type`: humanoid | quadruped | winged | serpent | taur | generic
- `is_humanoid`: bool
- `custom_properties.type_detection`: confidence + hints

## HTTP routes

| Route | Method |
|-------|--------|
| `/api/v1/pipeline/status` | GET |
| `/api/v1/pipeline/hub/callback` | GET (OAuth) |
| `/api/v1/control/tool` | POST (`tool: avatar_pipeline`) |
| `/api/v1/tools/execute` | POST (web UI) |

## Fleet dependencies

| Service | URL | Required for |
|---------|-----|--------------|
| vroidstudio-mcp | :10881 | `vroid_quick_avatar` |
| pywinauto-mcp | :10789 | vroidstudio-mcp |
| blender-mcp | :10849 | validate / reexport |

Hub download requires only avatar-mcp + Hub credentials.

## Related

- [MMD explainer (MCD)](../../mcp-central-docs/docs/avatars/MMD_EXPLAINER.md)
- [Godot + avatars (MCD)](../../mcp-central-docs/docs/avatars/GODOT_AND_AVATARS.md)
- [Non-human VRM (MCD)](../../mcp-central-docs/docs/avatars/NONHUMAN_VRM.md)
