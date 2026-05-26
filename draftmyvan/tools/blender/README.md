# Blender validation tools

This directory holds the scale-drift defence for DraftMyVan visual assets.

## Why this exists

A GLB that looks correct in UE5 but disagrees with `dimensions_mm` in the
manifest silently invalidates every downstream output: cut lists, clearance
checks, placement snapping, and Fusion cabinet regeneration. Scale drift is
the #1 fatal risk called out in the architecture doc.

Both scripts here answer the same question — *does this GLB's bounding box
match the manifest within tolerance?* — at different levels of authority.

## Two execution modes

### 1. `validate_glb_against_manifest.py` — pure Python (CI-safe)

Reads the GLB header + JSON chunk and pulls the bounding box straight from
each POSITION accessor's `min`/`max` arrays (mandatory under glTF 2.0
§3.6.2.4). No Blender needed; runs in GitHub Actions.

```bash
python draftmyvan/tools/blender/validate_glb_against_manifest.py \
    --manifest draftmyvan/examples/galley_1000.json \
    --glb path/to/galley_1000.glb
```

Optional flags:

| Flag | Default | Purpose |
|---|---|---|
| `--tolerance-mm` | `1.0` | Per-axis allowed delta. |
| `--glb-units` | `meters` | Set to `millimeters` if your exporter writes mm directly. |
| `--ignore-path-mismatch` | off | Accept a GLB whose basename differs from `visual.glb_path`. |

**Assumption.** This mode assumes the module is authored at the origin
with identity node transforms — i.e. accessor min/max equals the
world-space bounding box. For complex hierarchies use the Blender mode
below.

### 2. `validate_in_blender.py` — authoritative (manual)

Runs inside Blender. Imports the GLB, walks every mesh object's
`bound_box` through its `matrix_world`, and gives the true assembled
extents. Use it when the pure-Python check disagrees with your eye, or
before promoting a new GLB.

```bash
blender --background --python \
    draftmyvan/tools/blender/validate_in_blender.py -- \
    --manifest draftmyvan/examples/galley_1000.json \
    --glb path/to/galley_1000.glb
```

The bare `--` is required: Blender forwards everything after it to the
script.

## Pass / fail semantics

* **PASS** — every axis is within `tolerance-mm`. Safe to commit the GLB.
* **FAIL** — at least one axis exceeds tolerance. Do not commit; fix the
  exporter or the manifest, not both at once.
* **ERROR** (exit 2) — manifest malformed or GLB unreadable. The asset
  pipeline itself is broken.

## What is *not* validated here yet

* **Origin / anchor alignment.** The manifest declares an `anchor` (e.g.
  `floor_back_left`); making sure that corner actually sits at world (0,0,0)
  requires agreeing with the UE5 import side on axis conventions. Reported
  as informational only for now.
* **Collision proxy presence.** `visual.collision_proxy` is expected to be a
  `UCX_…` mesh inside the GLB; verifying that is the next slice after this
  one.
* **Material slot names.** Likewise deferred until UE5 import is wired up.
