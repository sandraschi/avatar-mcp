# inspect_vrm.py
from pathlib import Path
import json
from pygltflib import GLTF2

# --------------------------------------------------------------------
# 1️⃣ Locate the VRM
vrm_path = Path(__file__).parent / "Nekomimi-chan.vrm"

# --------------------------------------------------------------------
# 2️⃣ Temporarily change the extension to .glb (the file *content* stays the same)
temp_glb = vrm_path.with_suffix(".glb")   # new temporary path
vrm_path.rename(temp_glb)                # <-- rename on disk

# --------------------------------------------------------------------
# 3️⃣ Load it – here we use the *instance* method
glf_loader = GLTF2()                   # create an instance
glf_loader.load(temp_glb.as_posix())   # <-- this returns the same instance
gltf = glf_loader                      # now `gltf` is a GLTF2 object

# --------------------------------------------------------------------
# 4️⃣ Restore the original file name (optional but tidy)
temp_glb.rename(vrm_path)               # <-- rename back

# --------------------------------------------------------------------
# 5️⃣ Grab the VRM 1.0 extension
vrm_ext = gltf.extensions.get("VRM")

# --------------------------------------------------------------------
# 6️⃣ Pretty‑print the information you care about
print("=== VRM 1.0 Metadata ===")
print(json.dumps(vrm_ext.metadata.__dict__, indent=2))

print("\n=== First 5 blend‑shape expressions ===")
for expr in vrm_ext.expressions[:5]:
    print(f"  {expr.name:<25} → index {expr.blendShapeIndex}")

print("\n=== Humanoid bone mapping (first 10) ===")
for bone in vrm_ext.humanoid.humanBones[:10]:
    print(f"  {bone.boneName:<25} → node index {bone.node}")
