#!/usr/bin/env python3
"""Recover historical replay inputs and packet cores from checked model archives.

Usage:
    python scripts/build_paper_fixtures.py --archive-root PATH_TO_PAPER_REPLAY

The root must contain CASE/CASE.amspd for each of the four published cases.
This preserves the archived source and core instead of regenerating masks
with potentially changed imaging dependencies. It does not copy final results
into the replay calculation or change the reference benchmark numbers.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path

import numpy as np

CASES = ("synthetic_geometry", "synthetic_text_curves", "camera", "astronaut")
FIXTURE_KEYS = ("source", "core_atoms", "core_coefficients", "packet_specs_json", "packet_history_json")


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def build_fixtures(archive_root: Path, repo_root: Path) -> dict[str, object]:
    sys.path.insert(0, str(repo_root / "src"))
    from am_spd.model import AMSpdModel

    ledger_path = repo_root / "validation" / "paper_backend_provenance.json"
    provenance = json.loads(ledger_path.read_text(encoding="utf-8"))
    for name, expected in provenance["files"].items():
        actual = sha256(repo_root / "src" / "am_spd" / "_paper_v03" / name)
        if actual != expected:
            raise ValueError(f"frozen backend hash mismatch: {name}")

    resources = repo_root / "src" / "am_spd" / "resources"
    resources.mkdir(parents=True, exist_ok=True)
    cases: dict[str, object] = {}
    for case in CASES:
        archive_path = archive_root / case / f"{case}.amspd"
        model = AMSpdModel.load(archive_path)
        verification = model.verify()
        if not verification["passed"]:
            raise ValueError(f"archived model did not validate: {case}: {verification['errors']}")
        if model.core_atoms is None or model.core_coefficients is None:
            raise ValueError(f"archived model lacks packet core arrays: {case}")
        decoded = model.decode("exact")
        source = np.clip(decoded, 0.0, 1.0)
        atoms = np.asarray(model.core_atoms, dtype=np.float64)
        coefficients = np.asarray(model.core_coefficients, dtype=np.float64)
        if atoms.shape != (44, *source.shape[:2]) or coefficients.shape != (44, source.shape[2]):
            raise ValueError(f"unexpected paper packet core dimensions: {case}")
        if len(model.packet_specs) != 44 or len(model.packet_history) != 43:
            raise ValueError(f"unexpected paper packet metadata counts: {case}")
        payload = {
            "source": source,
            "core_atoms": atoms,
            "core_coefficients": coefficients,
            "packet_specs_json": np.array(json.dumps(model.packet_specs, sort_keys=True, allow_nan=False)),
            "packet_history_json": np.array(json.dumps(model.packet_history, sort_keys=True, allow_nan=False)),
        }
        destination = resources / f"paper_fixture_{case}.npz"
        np.savez_compressed(destination, **payload)
        with np.load(destination, allow_pickle=False) as recovered:
            if set(recovered.files) != set(FIXTURE_KEYS):
                raise ValueError(f"unexpected fixture keys: {case}")
            for key in FIXTURE_KEYS:
                if not np.array_equal(recovered[key], payload[key]):
                    raise ValueError(f"fixture roundtrip mismatch: {case}/{key}")
        cases[case] = {
            "archive_relative_path": f"{case}/{case}.amspd",
            "archive_sha256": sha256(archive_path),
            "archive_schema_version": model.schema_version,
            "archive_verification_passed": True,
            "fixture": destination.name,
            "fixture_sha256": sha256(destination),
            "fixture_bytes": destination.stat().st_size,
            "arrays": {key: {"shape": list(value.shape), "dtype": str(value.dtype)} for key, value in payload.items()},
            "packet_count": len(model.packet_specs),
            "packet_history_count": len(model.packet_history),
            "source_clipping_max_delta": float(np.max(np.abs(decoded - source))),
        }
    provenance.update({
        "fixture_schema_version": 1,
        "fixture_keys": list(FIXTURE_KEYS),
        "fixture_recovery_method": "Validated archived v0.3 model: source = clip(decode('exact'), 0, 1); original packet atoms, coefficients, specification records and selection history copied without refitting.",
        "fixture_scope": "Historical input/core anchors only. Downstream SPD, tree and portfolio stages are freshly executed by the frozen v0.3 replay backend. Archived final approximations are not bundled in these fixtures.",
        "generation_command": "python scripts/build_paper_fixtures.py --archive-root PATH_TO_PAPER_REPLAY",
        "cases": cases,
    })
    encoded = json.dumps(provenance, indent=2, sort_keys=True, allow_nan=False) + "\n"
    (resources / "paper_backend_provenance.json").write_text(encoded, encoding="utf-8")
    ledger_path.write_text(encoded, encoding="utf-8")
    return provenance


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--archive-root", type=Path, required=True, help="Directory containing CASE/CASE.amspd")
    parser.add_argument("--repo-root", type=Path, default=Path(__file__).resolve().parents[1])
    args = parser.parse_args()
    provenance = build_fixtures(args.archive_root.resolve(), args.repo_root.resolve())
    print(json.dumps({"fixtures_generated": len(provenance["cases"]), "cases": provenance["cases"]}, indent=2))


if __name__ == "__main__":
    main()
