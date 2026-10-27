#!/usr/bin/env python3
"""Create the one-time RRCT v0.45 pre-outcome source seal."""
from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()


def main() -> int:
    root = Path(__file__).resolve().parents[1]
    output = root / "validation/V0_45_PREOUTCOME_FREEZE.json"
    if output.exists():
        raise RuntimeError("v0.45 pre-outcome freeze already exists")
    paths = [
        root / "pyproject.toml",
        root / "RUN_V045_KOMOREBI_OPERATOR.ps1",
        root / "RUN_V045_KOMOREBI_OPERATOR.sh",
        root / "tests/test_v045_komorebi_operator_self_model.py",
        root / "validation/V0_45_HOLDOUT_SEED_SELECTION.json",
        root / "validation/V0_45_KOMOREBI_OPERATOR_SELF_MODEL_PROTOCOL.md",
        root / "validation/build_v045_preoutcome_freeze.py",
        root / "validation/run_v045_frozen_holdout.py",
        root / "validation/verify_v045_release.py",
    ]
    paths.extend(sorted((root / "src/rrct").glob("*.py")))
    paths.extend(sorted((root / "src/rrct/_vendor").glob("*")))
    unique = []
    seen = set()
    for path in paths:
        if not path.is_file():
            raise RuntimeError(f"required freeze file is missing: {path}")
        relative = path.relative_to(root).as_posix()
        if relative not in seen:
            seen.add(relative)
            unique.append(path)
    entries = [
        {
            "relative_path": path.relative_to(root).as_posix(),
            "size_bytes": path.stat().st_size,
            "sha256": sha256(path),
        }
        for path in sorted(unique, key=lambda value: value.relative_to(root).as_posix())
    ]
    payload = {
        "schema": "rrct.v045.preoutcome_freeze.v1",
        "version": "0.45.0.dev1",
        "status": "frozen_before_holdout_execution",
        "created_at_utc": datetime.now(timezone.utc).isoformat().replace(
            "+00:00", "Z"
        ),
        "scientific_question": (
            "Do Komorebi packet projectors, transfer blocks, Bayesian updates, "
            "and certified packet recompression provide measurable leverage for "
            "bounded RRCT self/world change attribution and self-memory retention?"
        ),
        "holdout_seed_selection_sha256": sha256(
            root / "validation/V0_45_HOLDOUT_SEED_SELECTION.json"
        ),
        "komorebi_wheel_sha256": (
            "7d51e3040aea84f6d540936c2427376205ef8660d44b6841c2848c542e628adb"
        ),
        "file_count": len(entries),
        "files": entries,
        "holdout_outcomes_examined": False,
        "postoutcome_source_changes_prohibited": True,
    }
    output.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")
    companion = output.with_suffix(output.suffix + ".sha256")
    companion.write_text(f"{sha256(output)}  {output.name}\n")
    print(json.dumps({
        "status": payload["status"],
        "file_count": len(entries),
        "freeze_sha256": sha256(output),
    }, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
