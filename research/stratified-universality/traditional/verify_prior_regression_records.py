from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
GEN = ROOT / "generated"
EXPECTED = {
    "block03_periodic_atlas_validation.json": 39_805,
    "block04_rational_mask_atlas_validation.json": 11_391,
    "block05_regular_atlas_validation.json": 89_055,
    "block06_integral_tower_validation.json": 697_958,
    "block07_product_multiplicative_validation.json": 595_964,
    "block08_local_polyphase_validation.json": 229_743,
    "block09_holonomic_validation.json": 174_940,
    "block10_algebraic_validation.json": 73_088,
}

def failure_count(value: object) -> int:
    if isinstance(value, list):
        return len(value)
    if isinstance(value, int):
        return value
    return 0 if not value else 1

checks = 0
for name, expected in EXPECTED.items():
    path = GEN / name
    if not path.is_file():
        raise SystemExit(f"missing prior validation record: {path}")
    record = json.loads(path.read_text(encoding="utf-8"))
    observed = int(record.get("checks", record.get("block_checks", -1)))
    failures = failure_count(record.get("failures", []))
    if observed != expected:
        raise SystemExit(f"count mismatch for {name}: expected {expected}, observed {observed}")
    if failures != 0:
        raise SystemExit(f"nonzero failures in {name}: {failures}")
    checks += observed

print("PRIOR_REGRESSION_RECORDS=PASS")
print(f"BLOCK03_TO_BLOCK10_RECORDED_CHECKS={checks}")
print("NOTE=This validates frozen machine-readable records; use Build.ps1 -FullRegression to recompute them.")
