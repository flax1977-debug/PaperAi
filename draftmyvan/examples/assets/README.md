# Asset placeholders

This directory is **intentionally empty** of real GLBs. The DraftMyVan
catalog has no committed binary art yet — and committing untested
high-poly meshes before the Blender validation gate is proven would
defeat the gate's purpose.

Real GLBs for each manifest entry should land here (or in a configured
LFS / asset-bucket path) once:

1. The pure-Python validator
   (`draftmyvan/tools/blender/validate_glb_against_manifest.py`) is
   accepted into CI.
2. A reproducible Blender export procedure exists and is documented.
3. Each candidate GLB has been validated locally with both the pure
   Python and Blender modes.

Until then, manifest entries reference paths (e.g.
`assets/galley_1000.glb`) that will resolve under this directory once the
first GLB is exported.
