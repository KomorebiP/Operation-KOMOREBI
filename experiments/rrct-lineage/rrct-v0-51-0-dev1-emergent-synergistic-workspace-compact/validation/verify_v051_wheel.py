#!/usr/bin/env python3
"""Verify RRCT v0.51 wheel identity, metadata, and required package files."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
import zipfile


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def main() -> int:
    root = Path(__file__).resolve().parents[1]
    receipt_path = root / "validation/V0_51_WHEEL_VERIFICATION.json"
    receipt = json.loads(receipt_path.read_text(encoding="utf-8"))
    wheel = root / "dist" / receipt["wheel_name"]
    checks: dict[str, bool] = {
        "wheel_present": wheel.is_file(),
        "wheel_sha256": bool(
            wheel.is_file() and sha256(wheel) == receipt["wheel_sha256"]
        ),
        "wheel_size": bool(
            wheel.is_file() and wheel.stat().st_size == receipt["wheel_size_bytes"]
        ),
    }
    if wheel.is_file():
        with zipfile.ZipFile(wheel) as archive:
            names = set(archive.namelist())
            metadata_names = [
                name for name in names if name.endswith(".dist-info/METADATA")
            ]
            checks["one_metadata_file"] = len(metadata_names) == 1
            metadata = (
                archive.read(metadata_names[0]).decode("utf-8")
                if len(metadata_names) == 1
                else ""
            )
            checks["metadata_name"] = "Name: rrct-prototype" in metadata
            checks["metadata_version"] = "Version: 0.51.0.dev1" in metadata
            for relative in receipt["required_members"]:
                checks[f"member::{relative}"] = relative in names
    payload = {
        "schema": "rrct.v051.wheel_runtime_verification.v1",
        "wheel_name": receipt["wheel_name"],
        "wheel_sha256": sha256(wheel) if wheel.is_file() else None,
        "all_checks_pass": all(checks.values()),
        "failed_checks": sorted(
            name for name, passed in checks.items() if not passed
        ),
    }
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0 if payload["all_checks_pass"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
