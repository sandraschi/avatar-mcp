"""Convert a .vrm file to a standard .glb for engines that don't understand VRM directly
(Overte's Model entity, confirmed - see overte-mcp CHANGELOG 2026-09-02).

VRM's container format IS binary glTF (magic header "glTF", same as .glb) - it just adds
VRM-specific extensions (humanoid bone mapping, MToon toon-shader materials, blendshape
presets) on top. A non-VRM-aware glTF loader safely ignores extensions it doesn't recognize
and still renders the base mesh/skin/skeleton, so this is a byte-preserving load+resave, not
a real transcode: live-verified against AnimeGirl2.vrm (18,054,236 bytes in, 18,055,100 out -
the ~864 byte difference is JSON re-serialization, not content loss) and spawned successfully
in a live Overte session (real ~1.16m x 1.44m x 0.57m bounding box, not an empty/broken mesh).

What's lost: MToon shading (Overte falls back to its own default material), VRM-specific
metadata (license, humanoid bone name mapping) - the mesh, skin, and skeleton survive as
plain glTF, which is all a Model entity needs.

Usage: uv run --with pygltflib python scripts/vrm_to_glb.py <input.vrm> <output.glb>
"""

from __future__ import annotations

import sys
from pathlib import Path

from pygltflib import GLTF2


def main() -> None:
    if len(sys.argv) != 3:
        print(__doc__)
        sys.exit(1)

    src = Path(sys.argv[1])
    dst = Path(sys.argv[2])
    if not src.exists():
        print(f"Input not found: {src}")
        sys.exit(1)

    # GLTF2.load() picks JSON-vs-binary by file extension, and doesn't recognize .vrm - use
    # load_binary() explicitly since VRM is always the binary container form.
    gltf = GLTF2.load_binary(str(src))
    dst.parent.mkdir(parents=True, exist_ok=True)
    gltf.save(str(dst))
    print(f"Wrote {dst} ({dst.stat().st_size / 1024 / 1024:.1f} MB, from {src.name})")


if __name__ == "__main__":
    main()
