#!/usr/bin/env python3
"""Verify the installable RRCT v0.46 wheel without network access."""
from __future__ import annotations

import hashlib
import json
import os
import subprocess
import sys
import tempfile
import zipfile
from pathlib import Path

EXPECTED_VERSION = "0.46.0.dev1"
EXPECTED_KOMOREBI_SHA256 = (
    "7d51e3040aea84f6d540936c2427376205ef8660d44b6841c2848c542e628adb"
)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def main() -> int:
    root = Path(__file__).resolve().parents[1]
    wheels = sorted((root / "dist").glob("rrct_prototype-0.46.0.dev1-*.whl"))
    if len(wheels) != 1:
        raise RuntimeError(f"expected one v0.46 wheel, found {len(wheels)}")
    wheel = wheels[0]
    with zipfile.ZipFile(wheel) as archive:
        names = set(archive.namelist())
        required_suffixes = {
            "rrct/jspace_self_indexed_workspace.py",
            "rrct/jspace_self_indexed_workspace_experiment.py",
            "rrct/_vendor/komorebi_math-1.0.0b4-py3-none-any.whl",
        }
        required_present = {
            suffix: suffix in names for suffix in sorted(required_suffixes)
        }
        vendor_bytes = archive.read(
            "rrct/_vendor/komorebi_math-1.0.0b4-py3-none-any.whl"
        )
        vendor_sha = hashlib.sha256(vendor_bytes).hexdigest()

    with tempfile.TemporaryDirectory(prefix="rrct-v046-wheel-") as directory:
        target = Path(directory) / "site"
        target.mkdir()
        install = subprocess.run(
            [
                sys.executable,
                "-m",
                "pip",
                "install",
                "--disable-pip-version-check",
                "--no-index",
                "--no-deps",
                "--target",
                str(target),
                str(wheel),
            ],
            cwd=root,
            text=True,
            capture_output=True,
            check=False,
        )
        smoke_code = r'''
import json
import rrct
from rrct.jspace_self_indexed_workspace_experiment import run_neutral_workspace_benchmark
result = run_neutral_workspace_benchmark(
    (46125,), trials_per_scenario=1, cohort="installed_wheel_smoke"
)
print(json.dumps({
    "version": rrct.__version__,
    "unique_world_case_count": result["unique_world_case_count"],
    "decision_count": result["decision_count"],
    "projector_overlap": result["discovery_summary"]["mean_projector_overlap"],
    "all_receipt_chains_valid": all(
        values["receipt_chain_valid_rate"] == 1.0
        for values in result["mode_summaries"].values()
    ),
}, sort_keys=True))
'''
        environment = os.environ.copy()
        environment["PYTHONPATH"] = str(target)
        environment["PYTHONDONTWRITEBYTECODE"] = "1"
        smoke = subprocess.run(
            [sys.executable, "-c", smoke_code],
            cwd=directory,
            env=environment,
            text=True,
            capture_output=True,
            check=False,
        )
    smoke_payload = None
    if smoke.returncode == 0:
        smoke_payload = json.loads(smoke.stdout.strip().splitlines()[-1])
    checks = {
        "wheel_filename_version_matches": EXPECTED_VERSION in wheel.name,
        "required_package_files_present": all(required_present.values()),
        "vendored_komorebi_sha256_matches": vendor_sha == EXPECTED_KOMOREBI_SHA256,
        "offline_install_passed": install.returncode == 0,
        "installed_import_passed": smoke.returncode == 0,
        "installed_version_matches": bool(
            smoke_payload and smoke_payload["version"] == EXPECTED_VERSION
        ),
        "installed_receipt_chains_valid": bool(
            smoke_payload and smoke_payload["all_receipt_chains_valid"]
        ),
        "installed_projector_recovered": bool(
            smoke_payload
            and abs(float(smoke_payload["projector_overlap"]) - 1.0) <= 1e-10
        ),
    }
    payload = {
        "schema": "rrct.v046.wheel_verification.v1",
        "version": EXPECTED_VERSION,
        "status": (
            "V046_WHEEL_VERIFIED"
            if all(checks.values())
            else "V046_WHEEL_FAILED"
        ),
        "wheel_name": wheel.name,
        "wheel_sha256": sha256(wheel),
        "wheel_size_bytes": wheel.stat().st_size,
        "vendored_komorebi_sha256": vendor_sha,
        "required_files": required_present,
        "smoke_result": smoke_payload,
        "checks": checks,
        "all_checks_pass": all(checks.values()),
        "install_stderr": install.stderr.strip() if install.returncode else "",
        "smoke_stderr": smoke.stderr.strip() if smoke.returncode else "",
        "direct_zipimport_boundary": (
            "The wheel is verified through standard installation. Directly "
            "placing the unopened RRCT wheel on PYTHONPATH is not supported "
            "because the nested Komorebi wheel must exist as a filesystem file."
        ),
    }
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0 if payload["all_checks_pass"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
