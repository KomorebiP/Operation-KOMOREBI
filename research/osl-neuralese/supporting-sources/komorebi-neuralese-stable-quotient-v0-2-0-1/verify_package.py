#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from komorebi_neuralese.reporting import source_files, tree_digest


def file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def load_json(relative: str) -> dict:
    path = ROOT / relative
    if not path.exists():
        raise SystemExit(f"Missing required artifact: {relative}")
    return json.loads(path.read_text(encoding="utf-8"))


def verify_completion(directory: str, expected_schema: str) -> dict:
    completion = load_json(f"{directory}/RUN_COMPLETE.json")
    if completion.get("schema") != expected_schema:
        raise SystemExit(f"Completion schema mismatch: {directory}")
    if completion.get("profile") != "pilot":
        raise SystemExit(f"Completion profile mismatch: {directory}")
    if not completion.get("all_gates_passed", False):
        raise SystemExit(f"Developmental gates did not pass: {directory}")
    for key, filename in (("results_sha256", "RESULTS.json"), ("report_sha256", "REPORT.md")):
        observed = file_sha256(ROOT / directory / filename)
        if completion.get(key) != observed:
            raise SystemExit(f"Completion hash mismatch: {directory}/{filename}")
    return completion


def verify_manifest() -> None:
    manifest = load_json("MANIFEST.json")
    if manifest.get("schema") != "komorebi.neuralese.package_manifest.v2":
        raise SystemExit("Manifest schema mismatch")
    if manifest.get("version") != "0.2.0":
        raise SystemExit("Manifest version mismatch")
    records = manifest.get("files", [])
    if manifest.get("file_count") != len(records):
        raise SystemExit("Manifest file count mismatch")
    sum_lines = [line for line in (ROOT / "SHA256SUMS.txt").read_text(encoding="utf-8").splitlines() if line]
    expected_sums = {record["path"]: record["sha256"] for record in records}
    parsed_sums: dict[str, str] = {}
    for line in sum_lines:
        expected, relative = line.split("  ", 1)
        parsed_sums[relative] = expected
    if parsed_sums != expected_sums:
        raise SystemExit("SHA256SUMS and MANIFEST disagree")
    for record in records:
        path = ROOT / record["path"]
        if not path.exists():
            raise SystemExit(f"Manifest file missing: {record['path']}")
        if path.stat().st_size != record["size"]:
            raise SystemExit(f"Manifest size mismatch: {record['path']}")
        if file_sha256(path) != record["sha256"]:
            raise SystemExit(f"Checksum mismatch: {record['path']}")


def main() -> int:
    verify_manifest()
    subprocess.run([sys.executable, "-m", "pytest", "-q", str(ROOT / "tests")], cwd=ROOT, check=True)

    legacy = load_json("results/pilot/RUN_COMPLETE.json")
    if legacy.get("schema") != "komorebi.neuralese.run_complete.v1" or not legacy.get(
        "all_development_gates_passed", False
    ):
        raise SystemExit("Legacy parent pilot is incomplete")

    stability = verify_completion(
        "results/stability_pilot", "komorebi.neuralese.stable_quotient.completion.v1"
    )
    projective = verify_completion(
        "results/projective_pilot", "komorebi.neuralese.projective_training.completion.v1"
    )
    current_source_digest = tree_digest(ROOT, source_files(ROOT))
    for name, completion in (("stability", stability), ("projective", projective)):
        if completion.get("evaluation_source_digest") != current_source_digest:
            raise SystemExit(f"{name} result was not evaluated from the packaged source")

    print(
        json.dumps(
            {
                "status": "PACKAGE_VERIFY_PASS",
                "version": "0.2.0",
                "manifest_files": load_json("MANIFEST.json")["file_count"],
                "tests": "passed",
                "stability_gates": "passed",
                "projective_gates": "passed",
                "source_digest": current_source_digest,
            },
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
