"""Smoke tests for the manifest validator.

Run from the draftmyvan/ directory:
    python -m tests.test_validator

Confirms:
  1. The schema itself is a valid Draft 2020-12 schema.
  2. The shipped galley_1000.json example validates.
  3. A deliberately broken copy is rejected (negative test).
"""

from __future__ import annotations

import copy
import json
import sys
from pathlib import Path

from jsonschema import Draft202012Validator

REPO_ROOT = Path(__file__).resolve().parent.parent
SCHEMA_PATH = REPO_ROOT / "manifest.schema.json"
SAMPLE_PATH = REPO_ROOT / "examples" / "galley_1000.json"


def _load(path: Path) -> dict:
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def test_schema_is_valid() -> None:
    schema = _load(SCHEMA_PATH)
    Draft202012Validator.check_schema(schema)


def test_galley_1000_validates() -> None:
    schema = _load(SCHEMA_PATH)
    sample = _load(SAMPLE_PATH)
    errors = list(Draft202012Validator(schema).iter_errors(sample))
    assert not errors, f"galley_1000.json should validate, got: {errors}"


def test_negative_missing_required_field() -> None:
    schema = _load(SCHEMA_PATH)
    sample = _load(SAMPLE_PATH)
    broken = copy.deepcopy(sample)
    del broken["dimensions_mm"]
    errors = list(Draft202012Validator(schema).iter_errors(broken))
    assert errors, "removing dimensions_mm should produce a validation error"


def test_negative_fractional_mm_rejected() -> None:
    schema = _load(SCHEMA_PATH)
    sample = _load(SAMPLE_PATH)
    broken = copy.deepcopy(sample)
    broken["dimensions_mm"]["width"] = 1000.5
    errors = list(Draft202012Validator(schema).iter_errors(broken))
    assert errors, "fractional mm widths must be rejected"


def main() -> int:
    tests = [
        test_schema_is_valid,
        test_galley_1000_validates,
        test_negative_missing_required_field,
        test_negative_fractional_mm_rejected,
    ]
    failed = 0
    for t in tests:
        try:
            t()
            print(f"PASS  {t.__name__}")
        except AssertionError as e:
            failed += 1
            print(f"FAIL  {t.__name__}: {e}")
        except Exception as e:
            failed += 1
            print(f"ERROR {t.__name__}: {e}")
    print()
    print(f"{len(tests) - failed}/{len(tests)} passed")
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
