#!/usr/bin/env python3
"""Validate that a GLB's bounding box matches a DraftMyVan manifest entry.

This is the defence against the #1 fatal risk in the architecture plan:
visual asset scale drift — a GLB that looks correct in UE5 but quietly
disagrees with the manifest's `dimensions_mm`, breaking every cut list,
clearance check, and placement rule downstream.

Two execution modes:

  1. Pure Python (this script, the default). Parses the GLB header and
     reads the POSITION accessors' `min`/`max` arrays (mandatory under
     glTF 2.0 §3.6.2.4). Fast, no Blender dependency, runs in CI.

  2. Blender (sibling `validate_in_blender.py`). Imports the GLB and
     reads the assembled object bounding box from bpy. Authoritative
     for assets with non-identity node transforms or accessors that
     somehow lack extents. Run locally when in doubt.

Usage:
    python validate_glb_against_manifest.py \\
        --manifest draftmyvan/examples/galley_1000.json \\
        --glb path/to/galley_1000.glb \\
        [--tolerance-mm 1.0] \\
        [--glb-units meters|millimeters] \\
        [--ignore-path-mismatch]

Exit codes:
    0  GLB matches manifest within tolerance
    1  Mismatch or validation error
    2  Bad arguments / file not found / malformed GLB

Assumptions (documented; will be revisited when real assets exist):
    * The module is authored at the origin with identity node transforms.
      Per-mesh accessor min/max therefore equals the world-space bbox.
      For hierarchies, use the Blender variant.
    * glTF positions are in metres (the spec's default convention).
      Override with --glb-units millimeters if your exporter writes mm.
"""

from __future__ import annotations

import argparse
import json
import os
import struct
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

# glTF 2.0 binary constants
GLB_MAGIC = b"glTF"
GLB_VERSION = 2
CHUNK_TYPE_JSON = 0x4E4F534A
CHUNK_TYPE_BIN = 0x004E4942


# ---------------------------------------------------------------------------
# Data classes
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class BBox:
    """Axis-aligned bounding box in some unit."""
    min_x: float
    min_y: float
    min_z: float
    max_x: float
    max_y: float
    max_z: float

    @property
    def size_xyz(self) -> tuple[float, float, float]:
        return (
            self.max_x - self.min_x,
            self.max_y - self.min_y,
            self.max_z - self.min_z,
        )

    def scaled(self, factor: float) -> "BBox":
        return BBox(
            self.min_x * factor, self.min_y * factor, self.min_z * factor,
            self.max_x * factor, self.max_y * factor, self.max_z * factor,
        )


@dataclass
class ValidationReport:
    ok: bool
    messages: list[str]

    def __str__(self) -> str:
        return "\n".join(self.messages)


# ---------------------------------------------------------------------------
# Errors
# ---------------------------------------------------------------------------

class ManifestError(Exception):
    """Manifest is missing required fields or malformed."""


class GlbParseError(Exception):
    """GLB file is missing, malformed, or lacks a POSITION accessor."""


# ---------------------------------------------------------------------------
# Manifest loading
# ---------------------------------------------------------------------------

REQUIRED_DIM_KEYS = ("width", "depth", "height")


def load_manifest(path: Path) -> dict:
    if not path.exists():
        raise ManifestError(f"manifest not found: {path}")
    try:
        with path.open("r", encoding="utf-8") as f:
            return json.load(f)
    except json.JSONDecodeError as e:
        raise ManifestError(f"manifest {path} is not valid JSON: {e}") from e


def extract_manifest_dimensions_mm(manifest: dict) -> tuple[int, int, int]:
    """Return (width, depth, height) in mm, raising ManifestError if absent."""
    if "id" not in manifest:
        raise ManifestError("manifest missing required field 'id'")
    dims = manifest.get("dimensions_mm")
    if not isinstance(dims, dict):
        raise ManifestError("manifest missing required field 'dimensions_mm'")
    missing = [k for k in REQUIRED_DIM_KEYS if k not in dims]
    if missing:
        raise ManifestError(
            f"manifest dimensions_mm missing key(s): {', '.join(missing)}"
        )
    return tuple(int(dims[k]) for k in REQUIRED_DIM_KEYS)  # type: ignore[return-value]


def extract_manifest_glb_path(manifest: dict) -> str:
    visual = manifest.get("visual")
    if not isinstance(visual, dict) or "glb_path" not in visual:
        raise ManifestError("manifest missing required field 'visual.glb_path'")
    glb_path = visual["glb_path"]
    if not isinstance(glb_path, str) or not glb_path.endswith(".glb"):
        raise ManifestError(
            f"visual.glb_path must end in .glb (got: {glb_path!r})"
        )
    return glb_path


# ---------------------------------------------------------------------------
# GLB parsing
# ---------------------------------------------------------------------------

def parse_glb_bbox(glb_bytes: bytes) -> BBox:
    """Compute the union bounding box of every POSITION accessor.

    Operates on the JSON chunk only — no need to read the binary buffer
    because glTF 2.0 mandates `min`/`max` on POSITION accessors.
    """
    if len(glb_bytes) < 12:
        raise GlbParseError("file too short to be a GLB")
    magic, version, total_length = struct.unpack_from("<4sII", glb_bytes, 0)
    if magic != GLB_MAGIC:
        raise GlbParseError(f"bad GLB magic: {magic!r}")
    if version != GLB_VERSION:
        raise GlbParseError(f"unsupported GLB version: {version}")
    if total_length != len(glb_bytes):
        raise GlbParseError(
            f"GLB header length {total_length} != actual size {len(glb_bytes)}"
        )

    offset = 12
    json_payload: bytes | None = None
    while offset < total_length:
        if offset + 8 > total_length:
            raise GlbParseError("truncated chunk header")
        chunk_length, chunk_type = struct.unpack_from("<II", glb_bytes, offset)
        offset += 8
        if offset + chunk_length > total_length:
            raise GlbParseError("chunk length exceeds file size")
        payload = glb_bytes[offset:offset + chunk_length]
        offset += chunk_length
        if chunk_type == CHUNK_TYPE_JSON and json_payload is None:
            json_payload = payload
        # BIN chunk is ignored; accessor min/max gives us what we need.

    if json_payload is None:
        raise GlbParseError("GLB has no JSON chunk")

    try:
        gltf = json.loads(json_payload.decode("utf-8").rstrip("\x00 "))
    except (UnicodeDecodeError, json.JSONDecodeError) as e:
        raise GlbParseError(f"GLB JSON chunk unreadable: {e}") from e

    accessors = gltf.get("accessors") or []
    meshes = gltf.get("meshes") or []
    position_accessor_ids: set[int] = set()
    for mesh in meshes:
        for primitive in mesh.get("primitives", []):
            pos = (primitive.get("attributes") or {}).get("POSITION")
            if isinstance(pos, int):
                position_accessor_ids.add(pos)

    if not position_accessor_ids:
        raise GlbParseError("GLB declares no POSITION accessor")

    bbox_min = [float("inf")] * 3
    bbox_max = [float("-inf")] * 3
    for idx in position_accessor_ids:
        if idx < 0 or idx >= len(accessors):
            raise GlbParseError(f"POSITION accessor index {idx} out of range")
        acc = accessors[idx]
        mn, mx = acc.get("min"), acc.get("max")
        if not (isinstance(mn, list) and isinstance(mx, list) and len(mn) == 3 and len(mx) == 3):
            raise GlbParseError(
                f"POSITION accessor {idx} missing min/max arrays "
                "(required by glTF 2.0 §3.6.2.4)"
            )
        for i in range(3):
            bbox_min[i] = min(bbox_min[i], float(mn[i]))
            bbox_max[i] = max(bbox_max[i], float(mx[i]))

    return BBox(*bbox_min, *bbox_max)


def load_glb_bbox(glb_path: Path) -> BBox:
    if not glb_path.exists():
        raise GlbParseError(f"GLB file not found: {glb_path}")
    return parse_glb_bbox(glb_path.read_bytes())


# ---------------------------------------------------------------------------
# Comparison
# ---------------------------------------------------------------------------

def to_mm(bbox: BBox, units: str) -> BBox:
    if units == "millimeters":
        return bbox
    if units == "meters":
        return bbox.scaled(1000.0)
    raise ValueError(f"unknown --glb-units value: {units!r}")


def compare(
    bbox_mm: BBox,
    manifest_dims_mm: tuple[int, int, int],
    tolerance_mm: float,
) -> tuple[bool, list[str]]:
    width_mm, depth_mm, height_mm = bbox_mm.size_xyz
    m_w, m_d, m_h = manifest_dims_mm
    diffs = {
        "width":  (width_mm,  m_w),
        "depth":  (depth_mm,  m_d),
        "height": (height_mm, m_h),
    }
    lines: list[str] = []
    ok = True
    for axis, (actual, expected) in diffs.items():
        delta = actual - expected
        within = abs(delta) <= tolerance_mm
        marker = "OK" if within else "FAIL"
        lines.append(
            f"  [{marker}] {axis}: glb={actual:.3f} mm  manifest={expected} mm  "
            f"delta={delta:+.3f} mm  (tolerance={tolerance_mm} mm)"
        )
        if not within:
            ok = False
    return ok, lines


# ---------------------------------------------------------------------------
# Orchestration
# ---------------------------------------------------------------------------

def validate(
    manifest_path: Path,
    glb_path: Path,
    tolerance_mm: float = 1.0,
    glb_units: str = "meters",
    ignore_path_mismatch: bool = False,
) -> ValidationReport:
    messages: list[str] = []

    manifest = load_manifest(manifest_path)
    dims_mm = extract_manifest_dimensions_mm(manifest)
    manifest_glb_rel = extract_manifest_glb_path(manifest)
    messages.append(f"Manifest:        {manifest_path}")
    messages.append(f"Manifest id:     {manifest['id']}")
    messages.append(f"Manifest dims:   width={dims_mm[0]} depth={dims_mm[1]} height={dims_mm[2]} (mm)")
    messages.append(f"Manifest glb:    {manifest_glb_rel}")
    messages.append(f"Supplied glb:    {glb_path}")

    # Path-match check (basename only — manifest paths are repo-relative,
    # supplied paths may be wherever the artist built the asset).
    expected_basename = os.path.basename(manifest_glb_rel)
    actual_basename = glb_path.name
    if expected_basename != actual_basename:
        if ignore_path_mismatch:
            messages.append(
                f"  [WARN] glb basename {actual_basename!r} != manifest "
                f"{expected_basename!r} (override accepted)"
            )
        else:
            messages.append(
                f"  [FAIL] glb basename {actual_basename!r} != manifest "
                f"{expected_basename!r} "
                f"(use --ignore-path-mismatch to override)"
            )
            return ValidationReport(False, messages)

    bbox_native = load_glb_bbox(glb_path)
    bbox_mm = to_mm(bbox_native, glb_units)
    w, d, h = bbox_mm.size_xyz
    messages.append(
        f"GLB bbox (mm):   width={w:.3f} depth={d:.3f} height={h:.3f}  "
        f"(units in file: {glb_units})"
    )

    # Anchor contract — reported, not enforced. The exporter is expected to
    # author the mesh so that the manifest's `anchor` corner sits at the
    # origin, but verifying that requires the UE5 / Blender import side
    # to declare which axis is "up" and which corner is "back-left".
    anchor = manifest.get("anchor", "(unset)")
    messages.append(
        f"Anchor contract: manifest declares anchor={anchor!r}. "
        "Origin/anchor alignment is not yet enforced by this validator — "
        "deferred until the Blender import variant is wired up."
    )

    ok, axis_lines = compare(bbox_mm, dims_mm, tolerance_mm)
    messages.append("Dimension check:")
    messages.extend(axis_lines)
    if ok:
        messages.append("RESULT: PASS")
    else:
        messages.append("RESULT: FAIL — bounding box exceeds tolerance")
    return ValidationReport(ok, messages)


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        description="Validate a GLB's bounding box against a DraftMyVan manifest entry.",
    )
    p.add_argument("--manifest", required=True, type=Path,
                   help="Path to the manifest JSON file.")
    p.add_argument("--glb", required=True, type=Path,
                   help="Path to the GLB file to validate.")
    p.add_argument("--tolerance-mm", type=float, default=1.0,
                   help="Per-axis tolerance in millimetres (default: 1.0).")
    p.add_argument("--glb-units", choices=("meters", "millimeters"),
                   default="meters",
                   help="Unit interpretation of GLB positions (default: meters).")
    p.add_argument("--ignore-path-mismatch", action="store_true",
                   help="Do not fail when the GLB basename differs from "
                        "manifest.visual.glb_path.")
    return p


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        report = validate(
            manifest_path=args.manifest,
            glb_path=args.glb,
            tolerance_mm=args.tolerance_mm,
            glb_units=args.glb_units,
            ignore_path_mismatch=args.ignore_path_mismatch,
        )
    except ManifestError as e:
        print(f"ERROR (manifest): {e}", file=sys.stderr)
        return 2
    except GlbParseError as e:
        print(f"ERROR (glb): {e}", file=sys.stderr)
        return 2
    print(report)
    return 0 if report.ok else 1


if __name__ == "__main__":
    sys.exit(main())
