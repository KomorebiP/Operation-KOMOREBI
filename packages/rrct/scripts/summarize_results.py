from __future__ import annotations

import argparse
import json
import pathlib


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("root", type=pathlib.Path)
    args = parser.parse_args()
    rows = []
    for path in sorted(args.root.rglob("summary.json")):
        payload = json.loads(path.read_text(encoding="utf-8"))
        rows.append(
            {
                "path": str(path),
                "family": payload.get("family"),
                "status": payload.get("status"),
                "task_accuracy": payload.get("metrics", {}).get("task_accuracy"),
                "closure": payload.get("functional_profile", {}).get("functional_closure_composite"),
                "elapsed_seconds": payload.get("elapsed_seconds"),
            }
        )
    print(json.dumps(rows, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
