from __future__ import annotations

import argparse
from pathlib import Path
import sys

from neuralese_g1.integrity import atomic_json
from neuralese_g1.results import verify_run_directory


def main() -> int:
    parser = argparse.ArgumentParser(description="Verify a Komorebi Neuralese G1 run")
    parser.add_argument("--run", required=True, help="Run output directory")
    args = parser.parse_args()
    root = Path(args.run).resolve()
    report = verify_run_directory(root)
    atomic_json(root / "verification.json", report)
    print(f"G1_RUN_VALID claim={report['claim']} output={root}")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as error:
        print(f"G1_RUN_INVALID: {error}", file=sys.stderr)
        raise SystemExit(1)
