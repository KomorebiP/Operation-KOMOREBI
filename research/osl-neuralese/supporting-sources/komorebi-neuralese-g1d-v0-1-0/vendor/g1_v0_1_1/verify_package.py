from __future__ import annotations

import argparse
import compileall
from pathlib import Path
import sys
import unittest

from neuralese_g1.integrity import verify_package_manifest


ROOT = Path(__file__).resolve().parent


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Verify Komorebi Neuralese G1 package")
    parser.add_argument(
        "--quick",
        action="store_true",
        help="Retained for the Windows runner; all bounded release checks still run",
    )
    return parser.parse_args()


def main() -> int:
    parse_args()
    count = int(verify_package_manifest(ROOT)["entry_count"])
    if not compileall.compile_dir(ROOT, quiet=1, force=True):
        raise RuntimeError("Python compilation failed")
    suite = unittest.defaultTestLoader.discover(str(ROOT / "tests"), pattern="test_*.py")
    result = unittest.TextTestRunner(verbosity=2, stream=sys.stdout).run(suite)
    if not result.wasSuccessful():
        raise RuntimeError("package test suite failed")
    print(
        f"G1_PACKAGE_VALID files={count} tests={result.testsRun} skipped={len(result.skipped)}"
    )
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as error:
        print(f"G1_PACKAGE_INVALID: {error}", file=sys.stderr)
        raise SystemExit(1)
