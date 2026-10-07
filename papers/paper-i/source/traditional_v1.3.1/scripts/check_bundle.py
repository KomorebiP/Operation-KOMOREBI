#!/usr/bin/env python3
"""Read-only bundle checks; optional Python regression. Does not install dependencies."""
from __future__ import annotations
import argparse
import os
from pathlib import Path
import subprocess
import sys
import tempfile


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--tests", action="store_true", help="Also run the local Python tests")
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[1]
    result = subprocess.run([sys.executable, str(root / "scripts/verify_manifest.py")], cwd=root, check=False)
    if result.returncode or not args.tests:
        return result.returncode
    with tempfile.TemporaryDirectory(prefix="komorebi-check-") as cache:
        env = os.environ.copy()
        env["PYTHONPATH"] = str(root / "code/python") + os.pathsep + env.get("PYTHONPATH", "")
        env["PYTHONDONTWRITEBYTECODE"] = "1"
        env["MPLBACKEND"] = "Agg"
        env["MPLCONFIGDIR"] = cache
        command = [sys.executable, "-m", "pytest", "-q", "-W", "error", "-p", "no:cacheprovider",
                   "--import-mode=importlib", str(root / "code/python/tests")]
        try:
            result = subprocess.run(command, cwd=root, env=env, check=False, timeout=300)
        except subprocess.TimeoutExpired:
            print("FAIL: Python tests exceeded 300 seconds.", file=sys.stderr)
            return 124
        if result.returncode:
            print("Python tests failed. Check the error output and dependency requirements.", file=sys.stderr)
        return result.returncode


if __name__ == "__main__":
    raise SystemExit(main())
