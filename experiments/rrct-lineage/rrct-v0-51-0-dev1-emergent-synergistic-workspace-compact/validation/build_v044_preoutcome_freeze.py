#!/usr/bin/env python3
"""Build the RRCT v0.44 source seal before any holdout outcome is opened."""
from __future__ import annotations

import hashlib
import json
import platform
import sys
from datetime import datetime, timezone
from pathlib import Path

import numpy as np


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def main() -> int:
    root = Path(__file__).resolve().parents[1]
    sys.path.insert(0, str(root / "src"))
    from rrct.transformational_self_continuity_experiment import (  # noqa: PLC0415
        V044_EXPOSED_TUNING_SEEDS,
        V044_HOLDOUT_SEEDS,
        V044_LINEAGE_SEQUENCE,
        V044_MODES,
        V044_SCENARIOS,
        V044_TRIALS_PER_SCENARIO,
    )

    if len(V044_HOLDOUT_SEEDS) != 4:
        raise RuntimeError("v0.44 holdout seeds must be fixed before sealing")
    output = root / "validation/V0_44_PREOUTCOME_FREEZE.json"
    companion = output.with_suffix(output.suffix + ".sha256")
    result_path = (
        root
        / "validation/v0.44.0_transformational_self_continuity/results/transformational_self_continuity_analysis.json"
    )
    if result_path.exists():
        raise RuntimeError(
            "refusing to create or replace the pre-outcome freeze after a "
            "v0.44 holdout analysis exists"
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
            root / "tests/test_v044_transformational_self_continuity.py",
            root / "validation/V0_44_TRANSFORMATIONAL_SELF_CONTINUITY_PROTOCOL.md",
            root / "validation/V0_44_HOLDOUT_SEED_SELECTION.json",
            root / "validation/V0_44_HOLDOUT_SEED_SELECTION.json.sha256",
            root / "validation/run_v044_frozen_holdout.py",
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
        "schema": "rrct.v044.preoutcome_freeze.v1",
        "status": "sealed_before_holdout_outcomes",
        "created_at_utc": datetime.now(timezone.utc)
        .isoformat()
        .replace("+00:00", "Z"),
        "version": "0.44.0.dev1",
        "holdout_seeds": list(V044_HOLDOUT_SEEDS),
        "exposed_tuning_seeds": list(V044_EXPOSED_TUNING_SEEDS),
        "additional_exposed_stress_seeds": [
            6201,
            6203,
            6207,
            6211,
            6217,
            6221,
            6229,
            6233,
        ],
        "transport_stress_seed_range": [6301, 6324],
        "candidate_outcomes_examined_before_seal": False,
        "seed_replacement_after_outcomes_permitted": False,
        "world_family": "inherited_v043_causal_planning_with_synthetic_transformations",
        "scenarios": list(V044_SCENARIOS),
        "trials_per_scenario": int(V044_TRIALS_PER_SCENARIO),
        "modes": list(V044_MODES),
        "multigeneration_sequence": list(V044_LINEAGE_SEQUENCE),
        "information_policy": {
            "default_coarse_rows": {"source": 8, "sensory": 14, "memory": 8},
            "default_refined_rows": {"source": 24, "sensory": 32, "memory": 24},
            "accept_threshold": 0.45,
            "reject_threshold": 0.06,
            "refinement_interval": [0.06, 0.90],
            "transported_model_cost": 2,
            "fresh_discovery_cost": 24,
            "snapshot_model_cost": 2,
        },
        "endpoint_count": 23,
        "environment": {
            "python": sys.version,
            "platform": platform.platform(),
            "numpy": np.__version__,
        },
        "file_count": len(files),
        "files": files,
        "claim_boundary": (
            "A passing result supports bounded functional transformational "
            "self-continuity in the sealed synthetic family. It cannot establish "
            "phenomenal consciousness, sentience, valence, moral status, "
            "autonomous desire, or open-world generality."
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
                "holdout_seeds": list(V044_HOLDOUT_SEEDS),
            },
            indent=2,
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
