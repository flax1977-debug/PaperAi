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
python -m tests.test_validator
```

Expected:

```
PASS  test_schema_is_valid
PASS  test_galley_1000_validates
PASS  test_negative_missing_required_field
PASS  test_negative_fractional_mm_rejected
PASS  test_negative_id_with_spaces_or_capitals_rejected
PASS  test_negative_missing_glb_path_rejected
PASS  test_negative_fbx_visual_path_rejected
PASS  test_negative_negative_clearance_rejected
PASS  test_negative_unknown_extra_field_at_root_rejected
PASS  test_negative_unknown_extra_field_nested_rejected

10/10 passed
```

## CI

`.github/workflows/draftmyvan.yml` runs the validator (`--all`) and the test
suite on every push and pull request that touches `draftmyvan/**` or the
workflow file itself. It does **not** run for changes that only touch the
PaperAI Flutter app.

## What's next (not in this slice)

1. Blender export script that reads a manifest entry and **verifies** the GLB's
   bounding box matches `dimensions_mm` before saving.
2. UE5 Data Asset / importer that consumes the manifest at editor time.
3. Fusion 360 add-in that regenerates a parametric template from the same entry.
