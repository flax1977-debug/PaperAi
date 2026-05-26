# DraftMyVan — Foundation

> **This folder is not part of the PaperAI Flutter app.** It shares the repository for
> persistence convenience only. The Flutter project lives under `lib/`; DraftMyVan
> lives entirely under `draftmyvan/` and has no build coupling to it.

DraftMyVan is a manufacturing-oriented 3D campervan configurator. This directory
holds the **data contract** — the single source of truth that UE5 (visualisation),
Blender (asset factory), and Fusion 360 (manufacturing brain) will all read from.

Nothing else. No UE5, no Blender, no Fusion, no UI, no CNC post processors yet.

## Layout

```
draftmyvan/
  manifest.schema.json     # JSON Schema (Draft 2020-12) for a module
  examples/
    galley_1000.json       # First module: 1000 mm galley cabinet
  tools/
    validate_manifest.py   # CLI validator
  tests/
    test_validator.py      # Schema + sample + negative tests
```

## Ground rules

- **Millimetres are canonical.** Every dimension and clearance is `*_mm` and
  stored as an integer. No cm, no inches, no floats for distances.
- **Schema-first.** A module cannot exist downstream until its manifest entry
  validates. No "we'll add the metadata later."
- **Versioned.** Every entry carries the schema version it was authored against
  (`"version": "0.1.0"` today). Bump on any breaking change.

## Required fields

`version`, `id`, `type`, `dimensions_mm`, `anchor`, `placement`, `clearances`,
`visual`, `manufacturing`, `rules`. See `manifest.schema.json` for the full
shape, allowed enum values, and constraints.

## Validate the sample

```bash
cd draftmyvan
pip install jsonschema           # one-time, if not already installed
python tools/validate_manifest.py examples/galley_1000.json
# or, validate every example at once:
python tools/validate_manifest.py --all
```

Expected output:

```
OK    examples/galley_1000.json

1/1 valid
```

## Run the tests

```bash
cd draftmyvan
python -m tests.test_validator                    # schema + manifest
python -m tests.test_blender_manifest_contract    # Blender gate, anchor enforcement
python -m tests.test_galley_fixture               # committed fixture + generator determinism
python -m tests.test_check_asset_ready            # one-shot readiness wrapper
```

Each suite prints `N/N passed` on success. None of them require Blender —
the fixture suite uses a pure-Python GLB generator
(`tools/assets/generate_galley_fixture_glb.py`) and pins the committed
`examples/assets/galley_1000.glb` to that generator's output byte-for-byte.

## Blender asset validation gate

This is the defence against the architecture doc's #1 fatal risk: visual
asset scale drift, **and** the closely related risk of origin drift (right
size, wrong position). See `tools/blender/README.md` for the full
description; the short version is below.

**Why it exists.** A GLB that looks correct in UE5 but whose bounding box
disagrees with `dimensions_mm` — or whose declared anchor corner is not
where the contract requires it — silently invalidates every cut list,
clearance check, and placement rule downstream. We refuse to commit any
GLB until it has passed this gate.

**Authoring coordinate contract.** Blender is the source of truth.
`+X` = width across the van, `+Y` = module depth (back is `+Y`),
`+Z` = floor → roof, units = metres. For `anchor = "floor_back_left"` the
mesh's bbox-min sits at `(0, 0, 0)` and bbox-max equals
`(width, depth, height)` converted from millimetres. UE5 / Fusion axis
conversion is downstream's job and must not mutate the source GLB.

**Two execution modes.**

* `tools/blender/validate_glb_against_manifest.py` — pure Python, no
  Blender. Reads the GLB's POSITION accessor `min`/`max` arrays. Runs in
  CI and locally.

  ```bash
  python tools/blender/validate_glb_against_manifest.py \
      --manifest examples/galley_1000.json \
      --glb path/to/galley_1000.glb
  ```

* `tools/blender/validate_in_blender.py` — runs inside Blender for the
  authoritative bbox (handles non-identity transforms).

  ```bash
  blender --background --python \
      draftmyvan/tools/blender/validate_in_blender.py -- \
      --manifest draftmyvan/examples/galley_1000.json \
      --glb path/to/galley_1000.glb
  ```

**Pass / fail.** Exit 0 = every axis within tolerance (`--tolerance-mm`,
default 1 mm). Exit 1 = drift. Exit 2 = malformed manifest or unreadable
GLB. The asset is not committable until the exit code is 0.

## Replacing the generated fixture with real art

The committed `examples/assets/galley_1000.glb` is a **deterministically
generated box**, not visual production art. Real cabinet GLBs cannot
silently overwrite it. Before any human-authored GLB lands:

1. Follow the documented procedure in
   `tools/blender/EXPORT_REAL_ASSET.md` (the why and how).
2. Sign off on `tools/blender/asset_export_checklist.md` (the one-pager).
3. Run the one-shot readiness wrapper:
   ```bash
   python tools/blender/check_asset_ready.py \
       --manifest examples/galley_1000.json \
       --glb /tmp/candidate.glb
   ```
   `RESULT: READY` means every gate (schema, dimensions, origin/anchor)
   passes. Anything else means the candidate is not committable.

Until the deferred follow-up in PR #7's "What this does not yet do"
section lands, the generated fixture remains the **golden boring
reference** — it is what every later candidate is measured against,
and it is what CI relies on to prove the pipeline still works.

## CI

`.github/workflows/draftmyvan.yml` runs the manifest validator (`--all`)
and four test suites — `tests.test_validator`,
`tests.test_blender_manifest_contract`, `tests.test_galley_fixture`,
and `tests.test_check_asset_ready` — on every push and pull request
that touches `draftmyvan/**` or the workflow file itself. It does
**not** run for changes that only touch the PaperAI Flutter app.
Blender itself is intentionally not installed in CI; the Blender mode
is a local-only gate (see `tools/blender/EXPORT_REAL_ASSET.md`).

## What's next (not in this slice)

1. UE5 Data Asset / importer that consumes the manifest at editor time.
2. Fusion 360 add-in that regenerates a parametric template from the same entry.
3. Collision-proxy and material-slot enforcement in the GLB validator.
4. Anchor enforcement for the remaining schema-valid anchor values
   (currently only `floor_back_left` is enforced; the rest fail loudly).
