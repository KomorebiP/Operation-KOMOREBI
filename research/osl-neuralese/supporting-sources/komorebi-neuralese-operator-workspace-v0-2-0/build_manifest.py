#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from komorebi_neuralese.reporting import code_files, tree_digest
from komorebi_neuralese.version import VERSION


GENERATED = {"MANIFEST.json", "SHA256SUMS.txt"}
IGNORED_PARTS = {"__pycache__", ".pytest_cache", ".git"}


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def included_files(include_manifest: bool = False) -> list[Path]:
    selected: list[Path] = []
    for path in ROOT.rglob("*"):
        if not path.is_file() or any(part in IGNORED_PARTS for part in path.parts):
            continue
        relative = path.relative_to(ROOT)
        if relative.as_posix() == "SHA256SUMS.txt":
            continue
        if relative.as_posix() == "MANIFEST.json" and not include_manifest:
            continue
        selected.append(relative)
    return sorted(selected, key=lambda value: value.as_posix())


def main() -> int:
    primary = ROOT / "results" / "v0.2.0" / "preregistered_primary"
    receipt = json.loads((primary / "RECEIPT.json").read_text(encoding="utf-8"))
    gates = json.loads((primary / "GATES.json").read_text(encoding="utf-8"))
    code_digest = tree_digest(ROOT, code_files(ROOT))
    if receipt["code_digest"] != code_digest:
        raise SystemExit("primary receipt does not match the current scientific code digest")
    protocol_path = ROOT / "protocols" / "V0_2_PRIMARY.json"
    protocol_sha = sha256(protocol_path)
    if receipt["protocol_digest"] != protocol_sha:
        raise SystemExit("primary receipt does not match the frozen protocol digest")

    payload = []
    for relative in included_files(include_manifest=False):
        path = ROOT / relative
        payload.append({"path": relative.as_posix(), "size": path.stat().st_size, "sha256": sha256(path)})
    manifest = {
        "schema": "komorebi.neuralese.package_manifest.v2",
        "version": VERSION,
        "file_count": len(payload),
        "files": payload,
        "scientific_code_digest": code_digest,
        "primary_protocol_digest": protocol_sha,
        "coordinate_split_digest": receipt["coordinate_split_digest"],
        "primary_outcome": {
            "status": receipt["status"],
            "scientific_gate_status": receipt["scientific_gate_status"],
            "all_gates_passed": gates["all_gates_passed"],
            "passed_gates": sum(bool(value["passed"]) for value in gates["gates"].values()),
            "failed_gates": sum(not bool(value["passed"]) for value in gates["gates"].values()),
            "arm_seed_cells": 80,
            "transport_pairs": receipt["transport_records"],
        },
        "evidence_ledger_sha256": sha256(ROOT / "EVIDENCE_LEDGER.json"),
        "prior_release_sha256": sha256(ROOT / "archive" / "Komorebi_Neuralese_Operator_Workspace_v0.1.1.zip"),
    }
    (ROOT / "MANIFEST.json").write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    checksum_files = included_files(include_manifest=True)
    (ROOT / "SHA256SUMS.txt").write_text(
        "".join(f"{sha256(ROOT / relative)}  {relative.as_posix()}\n" for relative in checksum_files),
        encoding="utf-8",
    )
    print(json.dumps({"file_count": len(payload), "checksum_count": len(checksum_files), "version": VERSION}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
