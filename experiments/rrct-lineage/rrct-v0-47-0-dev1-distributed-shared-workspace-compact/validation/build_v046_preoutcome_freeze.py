#!/usr/bin/env python3
"""Create the one-time RRCT v0.46 pre-outcome source seal."""
from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def main() -> int:
    root = Path(__file__).resolve().parents[1]
    output = root / "validation/V0_46_PREOUTCOME_FREEZE.json"
    if output.exists():
        raise RuntimeError("v0.46 pre-outcome freeze already exists")
    paths = [
        root / "pyproject.toml",
        root / "uv.lock",
        root / "MANIFEST.in",
        root / "README.md",
        root / "THEORY.md",
        root / "ETHICS.md",
        root / "RELEASE_NOTES.md",
        root / "RUN_V046_NEUTRAL_WORKSPACE.ps1",
        root / "RUN_V046_NEUTRAL_WORKSPACE.sh",
        root / "tests/test_v046_jspace_self_indexed_workspace.py",
        root / "validation/V0_46_HOLDOUT_SEED_SELECTION.json",
        root / "validation/V0_46_HOLDOUT_SEED_SELECTION.json.sha256",
        root / "validation/V0_46_NEUTRAL_SELF_INDEXED_WORKSPACE_PROTOCOL.md",
        root / "validation/V0_46_DEVELOPMENT_REPORT.md",
        root / "validation/select_v046_holdout_seeds.py",
        root / "validation/build_v046_preoutcome_freeze.py",
        root / "validation/run_v046_frozen_holdout.py",
        root / "validation/verify_v046_release.py",
    ]
    paths.extend(sorted((root / "src/rrct").glob("*.py")))
    paths.extend(sorted((root / "src/rrct/_vendor").glob("*")))
    unique: list[Path] = []
    seen: set[str] = set()
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
        for path in sorted(unique, key=lambda item: item.relative_to(root).as_posix())
    ]
    payload = {
        "schema": "rrct.v046.preoutcome_freeze.v1",
        "version": "0.46.0.dev1",
        "status": "frozen_before_holdout_execution",
        "created_at_utc": datetime.now(timezone.utc).isoformat().replace(
            "+00:00", "Z"
        ),
        "scientific_question": (
            "Does a Jacobian-discovered sparse workspace require separate RRCT "
            "self-indexing, planner binding, and consequence recurrence to form "
            "a bounded functional closure loop?"
        ),
        "holdout_seed_selection_sha256": sha256(
            root / "validation/V0_46_HOLDOUT_SEED_SELECTION.json"
        ),
        "komorebi_wheel_sha256": (
            "7d51e3040aea84f6d540936c2427376205ef8660d44b6841c2848c542e628adb"
        ),
        "file_count": len(entries),
        "files": entries,
        "holdout_outcomes_examined": False,
        "postoutcome_source_changes_prohibited": True,
        "explicit_survival_reward": 0.0,
        "explicit_identity_reward": 0.0,
        "explicit_continuity_reward": 0.0,
        "valence_model_present": False,
    }
    output.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    companion = output.with_suffix(output.suffix + ".sha256")
    companion.write_text(f"{sha256(output)}  {output.name}\n", encoding="utf-8")
    print(
        json.dumps(
            {
                "status": payload["status"],
                "file_count": len(entries),
                "freeze_sha256": sha256(output),
            },
            indent=2,
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
