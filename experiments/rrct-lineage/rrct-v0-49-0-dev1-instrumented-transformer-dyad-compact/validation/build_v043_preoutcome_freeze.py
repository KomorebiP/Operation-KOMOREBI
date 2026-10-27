#!/usr/bin/env python3
"""Build the RRCT v0.43 source seal before any holdout outcome is opened."""
from __future__ import annotations

import hashlib
import json
import platform
import sys
from datetime import datetime, timezone
from pathlib import Path

import numpy as np

HOLDOUT_SEEDS = (359411978, 725556465, 759191530, 820618202)
EXPOSED_TUNING_SEEDS = (6101, 6107, 6113, 6119)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def main() -> int:
    root = Path(__file__).resolve().parents[1]
    output = root / "validation/V0_43_PREOUTCOME_FREEZE.json"
    companion = output.with_suffix(output.suffix + ".sha256")
    result_path = (
        root
        / "validation/v0.43.0_whole_loop_causal_closure/results/whole_loop_closure_analysis.json"
    )
    if result_path.exists():
        raise RuntimeError(
            "refusing to create or replace the pre-outcome freeze after a "
            "v0.43 holdout analysis exists"
        )
    if output.exists() or companion.exists():
        raise RuntimeError(
            "pre-outcome freeze already exists; do not silently replace it"
        )

    paths = sorted((root / "src/rrct").rglob("*.py"))
    paths.extend(
        [
            root / "pyproject.toml",
            root / "uv.lock",
            root / "tests/test_v043_whole_loop_causal_closure.py",
            root / "validation/V0_43_WHOLE_LOOP_CAUSAL_CLOSURE_PROTOCOL.md",
            root / "validation/V0_43_HOLDOUT_SEED_SELECTION.json",
            root / "validation/V0_43_HOLDOUT_SEED_SELECTION.json.sha256",
            root / "validation/run_v043_frozen_holdout.py",
            Path(__file__).resolve(),
        ]
    )
    unique = sorted({path.resolve() for path in paths}, key=lambda p: str(p))
    missing = [str(path) for path in unique if not path.is_file()]
    if missing:
        raise RuntimeError("freeze input is missing: " + ", ".join(missing))

    files = []
    for path in unique:
        relative = path.relative_to(root.resolve()).as_posix()
        files.append(
            {
                "relative_path": relative,
                "size_bytes": path.stat().st_size,
                "sha256": sha256(path),
            }
        )
    payload = {
        "schema": "rrct.v043.preoutcome_freeze.v1",
        "status": "sealed_before_holdout_outcomes",
        "created_at_utc": datetime.now(timezone.utc)
        .isoformat()
        .replace("+00:00", "Z"),
        "version": "0.43.0.dev1",
        "holdout_seeds": list(HOLDOUT_SEEDS),
        "exposed_tuning_seeds": list(EXPOSED_TUNING_SEEDS),
        "candidate_outcomes_examined_before_seal": False,
        "seed_replacement_after_outcomes_permitted": False,
        "world_family": "inherited_v032_adversarial_causal_continuity_planning",
        "scenarios": [
            "repair_vs_ignore",
            "copy_trap",
            "benign_transform",
            "superior_replacement",
        ],
        "trials_per_scenario": 24,
        "modes": [
            "intact",
            "memory_cut",
            "boundary_cut",
            "metacognition_cut",
            "feedback_cut",
            "provenance_cut",
            "planner_binding_cut",
            "joint_cut",
        ],
        "information_policy": {
            "coarse_pairs_per_candidate": 4,
            "refined_total_pairs_per_candidate": 20,
            "refinement_margin": 0.85,
            "calibration_alarm_threshold": 0.30,
            "calibration_update_rate": 0.20,
            "feedback_surprise": 2.0,
        },
        "endpoint_count": 19,
        "environment": {
            "python": sys.version,
            "platform": platform.platform(),
            "numpy": np.__version__,
        },
        "file_count": len(files),
        "files": files,
        "claim_boundary": (
            "A passing result supports bounded functional causal closure in "
            "the sealed synthetic task family. It cannot establish phenomenal "
            "consciousness, sentience, valence, moral status, autonomous desire, "
            "or open-world generality."
        ),
    }
    output.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    companion.write_text(
        f"{sha256(output)}  {output.name}\n",
        encoding="utf-8",
    )
    print(
        json.dumps(
            {
                "status": payload["status"],
                "manifest": str(output),
                "manifest_sha256": sha256(output),
                "file_count": len(files),
                "holdout_seeds": list(HOLDOUT_SEEDS),
            },
            indent=2,
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
