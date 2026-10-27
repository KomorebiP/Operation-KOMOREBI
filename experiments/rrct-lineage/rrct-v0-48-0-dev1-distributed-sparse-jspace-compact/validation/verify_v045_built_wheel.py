#!/usr/bin/env python3
"""Verify the built RRCT v0.45 wheel and its exact embedded Komorebi wheel."""
from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import zipfile

EXPECTED_KOMOREBI_SHA256 = "7d51e3040aea84f6d540936c2427376205ef8660d44b6841c2848c542e628adb"
EXPECTED_KOMOREBI_VERSION = "1.0.0b4"
EXPECTED_RRCT_VERSION = "0.45.0.dev1"
EMBEDDED_PATH = "rrct/_vendor/komorebi_math-1.0.0b4-py3-none-any.whl"


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def main() -> int:
    root = Path(__file__).resolve().parents[1]
    wheels = sorted((root / "dist").glob("rrct_prototype-0.45.0.dev1-*.whl"))
    if len(wheels) != 1:
        raise RuntimeError(f"expected exactly one v0.45 wheel, found {len(wheels)}")
    wheel = wheels[0]
    checks: dict[str, bool] = {}
    with zipfile.ZipFile(wheel) as archive:
        names = set(archive.namelist())
        checks["embedded_komorebi_wheel_present"] = EMBEDDED_PATH in names
        embedded_sha = (
            sha256_bytes(archive.read(EMBEDDED_PATH))
            if EMBEDDED_PATH in names
            else None
        )
        checks["embedded_komorebi_sha256_exact"] = (
            embedded_sha == EXPECTED_KOMOREBI_SHA256
        )
        checks["vendor_manifest_present"] = (
            "rrct/_vendor/KOMOREBI_VENDOR_MANIFEST.json" in names
        )
        checks["vendor_license_present"] = (
            "rrct/_vendor/KOMOREBI_MATH_LICENSE.md" in names
        )

    with tempfile.TemporaryDirectory(prefix="rrct-v045-wheel-") as temp:
        target = Path(temp) / "site"
        target.mkdir()
        install = subprocess.run(
            [
                sys.executable,
                "-m",
                "pip",
                "install",
                "--disable-pip-version-check",
                "--no-deps",
                "--target",
                str(target),
                str(wheel),
            ],
            cwd=temp,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            check=False,
        )
        checks["offline_target_install"] = install.returncode == 0
        probe_code = r'''
import json
import pathlib
import tempfile
import rrct
import rrct.komorebi_operator_self_model as bridge
from rrct.komorebi_operator_self_model_experiment import run_operator_benchmark
km = bridge._ensure_komorebi()
result = run_operator_benchmark((45991,), trials_per_scenario=1, cohort="installed_wheel_verification")
print(json.dumps({
    "rrct_version": rrct.__version__,
    "komorebi_version": km.__version__,
    "komorebi_sha256": bridge.KOMOREBI_WHEEL_SHA256,
    "bridge_class": type(bridge.KomorebiOperatorBridge()).__name__,
    "all_endpoints_met": result["all_endpoints_met"],
    "decision_count": len(result["rows"]),
    "komorebi_accuracy": result["mode_summaries"]["komorebi_packets"]["change_class_accuracy"],
}, sort_keys=True))
'''
        environment = os.environ.copy()
        environment["PYTHONPATH"] = str(target)
        environment["PYTHONDONTWRITEBYTECODE"] = "1"
        probe = subprocess.run(
            [sys.executable, "-c", probe_code],
            cwd=temp,
            env=environment,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            check=False,
        )
        checks["installed_probe_exit_zero"] = probe.returncode == 0
        probe_payload = None
        if probe.returncode == 0:
            try:
                probe_payload = json.loads(probe.stdout.strip().splitlines()[-1])
            except (json.JSONDecodeError, IndexError):
                probe_payload = None
        checks["installed_rrct_version_exact"] = bool(
            probe_payload and probe_payload.get("rrct_version") == EXPECTED_RRCT_VERSION
        )
        checks["installed_komorebi_version_exact"] = bool(
            probe_payload
            and probe_payload.get("komorebi_version") == EXPECTED_KOMOREBI_VERSION
        )
        checks["installed_komorebi_sha256_exact"] = bool(
            probe_payload
            and probe_payload.get("komorebi_sha256") == EXPECTED_KOMOREBI_SHA256
        )
        checks["installed_operator_smoke_passed"] = bool(
            probe_payload
            and probe_payload.get("all_endpoints_met")
            and probe_payload.get("decision_count") == 16
            and probe_payload.get("komorebi_accuracy") == 1.0
        )

    payload = {
        "schema": "rrct.v045.built_wheel_verification.v1",
        "wheel": wheel.name,
        "wheel_sha256": sha256(wheel),
        "embedded_komorebi_sha256": embedded_sha,
        "checks": checks,
        "probe": probe_payload,
        "all_checks_pass": all(checks.values()),
        "failed_checks": sorted(name for name, passed in checks.items() if not passed),
    }
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0 if payload["all_checks_pass"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
