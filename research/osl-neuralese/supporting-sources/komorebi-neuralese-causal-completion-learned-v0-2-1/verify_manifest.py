#!/usr/bin/env python3
"""Verify release hashes and registered-run receipts."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parent


def digest(path: Path) -> str:
    value = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            value.update(chunk)
    return value.hexdigest()


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def main() -> int:
    manifest = json.loads((ROOT / "MANIFEST.json").read_text(encoding="utf-8"))
    for row in manifest["files"]:
        path = ROOT / row["path"]
        require(path.is_file(), f"missing file: {row['path']}")
        require(path.stat().st_size == row["bytes"], f"size mismatch: {row['path']}")
        require(digest(path) == row["sha256"], f"digest mismatch: {row['path']}")

    results = json.loads((ROOT / "results" / "RESULTS.json").read_text(encoding="utf-8"))
    require(
        results["preregistration_sha256"] == digest(ROOT / "PREREGISTRATION.json"),
        "registered result does not match the frozen registration",
    )
    receipt = json.loads(
        (ROOT / "results" / "RUN_COMPLETE.json").read_text(encoding="utf-8")
    )
    require(
        receipt["results_sha256"] == digest(ROOT / "results" / receipt["results_file"]),
        "registered result receipt mismatch",
    )
    require(
        receipt["report_sha256"] == digest(ROOT / "results" / receipt["report_file"]),
        "registered report receipt mismatch",
    )
    require(receipt["execution_passed"] is True, "registered execution gates did not pass")
    print(
        json.dumps(
            {
                "manifest_files_verified": manifest["file_count"],
                "registered_execution_passed": True,
                "status": "verified",
            },
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
