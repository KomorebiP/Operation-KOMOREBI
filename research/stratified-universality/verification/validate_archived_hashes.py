"""Check the archived copies against the original run's pinned hashes.

This checks relocatable archive integrity, not the mathematical claims and not
the full computation-manifest schema. The official v2 schema validator was run
with --root against the original workspace after each experiment.
"""
from pathlib import Path
import hashlib
import json

root = Path(__file__).resolve().parent
output_prefix = "output/Komorebi_Stratified_Universality_Final_Edition_2026-10-06/verification/"
input_prefix = "work/stratified/replay/manuscript/"
checked = 0
for manifest in sorted((root / "evidence").glob("block*/manifest.json")):
    record = json.loads(manifest.read_text(encoding="utf-8"))
    for entry in record["input_artifacts"]:
        path = entry["path"]
        if path == "work/stratified/run_validator_with_results.py":
            actual = root / "execution_inputs/run_validator_with_results.py"
        elif path.startswith(input_prefix):
            actual = root / "execution_inputs/manuscript" / path.removeprefix(input_prefix)
        else:
            raise ValueError(f"Unrecognized archive input mapping: {path}")
        assert hashlib.sha256(actual.read_bytes()).hexdigest() == entry["sha256"] == entry["sha256_after"], path
        checked += 1
    for entry in record["outputs"]:
        path = entry["path"]
        if not path.startswith(output_prefix):
            raise ValueError(f"Unrecognized archive output mapping: {path}")
        actual = root / path.removeprefix(output_prefix)
        assert hashlib.sha256(actual.read_bytes()).hexdigest() == entry["sha256"], path
        checked += 1
print(json.dumps({"archive_hash_status": "PASS", "hash_records_checked": checked,
                  "boundary": "Archive integrity only; no theorem proof or full manifest-schema validation."}, indent=2))
