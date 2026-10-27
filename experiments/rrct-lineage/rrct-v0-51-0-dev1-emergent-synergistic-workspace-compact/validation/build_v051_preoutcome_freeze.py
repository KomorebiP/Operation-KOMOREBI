#!/usr/bin/env python3
"""Create the one-time RRCT v0.51 pre-outcome source seal."""
from __future__ import annotations

from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def scientific_files(root: Path) -> list[Path]:
    files: list[Path] = []
    for relative in ("pyproject.toml", "MANIFEST.in"):
        path = root / relative
        if path.is_file():
            files.append(path)
    for path in sorted((root / "src/rrct").rglob("*")):
        if not path.is_file():
            continue
        if any(part in {"__pycache__", ".pytest_cache"} for part in path.parts):
            continue
        if path.suffix in {".pyc", ".pyo"}:
            continue
        files.append(path)
    explicit = [
        "tests/test_v051_emergent_synergistic_workspace.py",
        "validation/select_v051_holdout_seeds.py",
        "validation/V0_51_HOLDOUT_SEED_SELECTION.json",
        "validation/V0_51_HOLDOUT_SEED_SELECTION.json.sha256",
        "validation/V0_51_EMERGENT_SYNERGISTIC_WORKSPACE_PROTOCOL.md",
        "validation/V0_51_DEVELOPMENT_REPORT.md",
        "validation/train_v051_model.py",
        "validation/run_v051_frozen_holdout.py",
        "validation/verify_v051_results.py",
        "validation/build_v051_preoutcome_freeze.py",
        "RUN_V051_EMERGENT_WORKSPACE.sh",
        "RUN_V051_EMERGENT_WORKSPACE.ps1",
    ]
    files.extend(root / relative for relative in explicit)
    missing = [str(path.relative_to(root)) for path in files if not path.is_file()]
    if missing:
        raise RuntimeError(f"cannot freeze missing files: {missing}")
    unique = {path.resolve(): path for path in files}
    return sorted(unique.values(), key=lambda path: path.relative_to(root).as_posix())


def main() -> int:
    root = Path(__file__).resolve().parents[1]
    output = root / "validation/V0_51_PREOUTCOME_FREEZE.json"
    companion = output.with_suffix(output.suffix + ".sha256")
    if output.exists() or companion.exists():
        raise RuntimeError("v0.51 pre-outcome freeze already exists")
    files = scientific_files(root)
    seed_receipt = json.loads(
        (root / "validation/V0_51_HOLDOUT_SEED_SELECTION.json").read_text(
            encoding="utf-8"
        )
    )
    payload = {
        "schema": "rrct.v051.preoutcome_freeze.v1",
        "version": "0.51.0.dev1",
        "created_at_utc": datetime.now(timezone.utc)
        .isoformat()
        .replace("+00:00", "Z"),
        "scientific_status": "source_protocol_thresholds_and_seeds_sealed_before_holdout",
        "holdout_seeds": seed_receipt["selected_seeds"],
        "files": [
            {
                "relative_path": path.relative_to(root).as_posix(),
                "size_bytes": path.stat().st_size,
                "sha256": sha256(path),
            }
            for path in files
        ],
        "outcomes_examined_before_seal": False,
        "post_seal_scientific_source_changes_permitted": False,
    }
    unsigned = json.dumps(payload, sort_keys=True, separators=(",", ":"))
    payload["digest"] = hashlib.sha256(unsigned.encode()).hexdigest()
    output.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")
    companion.write_text(f"{sha256(output)}  {output.name}\n")
    print(
        json.dumps(
            {
                "path": str(output),
                "file_count": len(files),
                "manifest_sha256": sha256(output),
                "holdout_seeds": payload["holdout_seeds"],
            },
            indent=2,
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
