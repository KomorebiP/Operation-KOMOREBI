from __future__ import annotations

from deterministic_bootstrap import ensure as _ensure_deterministic
_ensure_deterministic()

import argparse
from pathlib import Path

from block23.external.preflight import write_preflight

ROOT = Path(__file__).resolve().parent


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo-dir")
    ap.add_argument("--checkpoint")
    ap.add_argument("--output", default=str(ROOT / "external_status" / "preflight.json"))
    args = ap.parse_args()
    result = write_preflight(
        args.output,
        repo_dir=args.repo_dir,
        checkpoint=args.checkpoint,
        source_lock=ROOT / "frozen" / "SOURCE_LOCK.json",
    )
    print(f"BLOCK23_EXTERNAL_STATUS={result['status']}")
    print(f"blockers={','.join(result['blockers'])}")


if __name__ == "__main__":
    main()
