from __future__ import annotations

import argparse
import compileall
from pathlib import Path
import sys
import unittest

from g1d.integrity import verify_package_manifest


ROOT = Path(__file__).resolve().parent
VENDOR_ROOT = ROOT / "vendor" / "g1_v0_1_1"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Verify Neuralese G1-D1 package")
    parser.add_argument("--quick", action="store_true")
    return parser.parse_args()


def main() -> int:
    parse_args()
    package = verify_package_manifest(ROOT)
    sys.path.insert(0, str(VENDOR_ROOT))
    from neuralese_g1.integrity import verify_package_manifest as verify_upstream

    upstream = verify_upstream(VENDOR_ROOT)
    if not compileall.compile_dir(ROOT, quiet=1, force=True):
        raise RuntimeError("Python compilation failed")
    suite = unittest.defaultTestLoader.discover(str(ROOT / "tests"), pattern="test_*.py")
    result = unittest.TextTestRunner(verbosity=2, stream=sys.stdout).run(suite)
    if not result.wasSuccessful():
        raise RuntimeError("G1-D1 test suite failed")
    print(
        f"G1D_PACKAGE_VALID files={package['entry_count']} tests={result.testsRun} "
        f"skipped={len(result.skipped)} upstream_files={upstream['entry_count']}"
    )
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as error:
        print(f"G1D_PACKAGE_INVALID: {error}", file=sys.stderr)
        raise SystemExit(1)
