from __future__ import annotations

import argparse
import json
import pathlib


def load(path: pathlib.Path) -> dict:
    if path.is_dir():
        path = path / "summary.json"
    return json.loads(path.read_text(encoding="utf-8"))


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("left", type=pathlib.Path)
    parser.add_argument("right", type=pathlib.Path)
    args = parser.parse_args()
    left = load(args.left)
    right = load(args.right)
    keys = sorted(set(left.get("metrics", {})) | set(right.get("metrics", {})))
    rows = []
    for key in keys:
        a = left.get("metrics", {}).get(key)
        b = right.get("metrics", {}).get(key)
        difference = b - a if isinstance(a, (int, float)) and isinstance(b, (int, float)) else None
        rows.append({"metric": key, "left": a, "right": b, "right_minus_left": difference})
    print(json.dumps(rows, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
