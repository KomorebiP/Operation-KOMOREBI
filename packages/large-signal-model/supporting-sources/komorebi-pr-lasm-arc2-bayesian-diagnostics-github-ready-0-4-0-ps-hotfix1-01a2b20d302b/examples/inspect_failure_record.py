#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path


def main() -> int:
    parser = argparse.ArgumentParser(description="Inspect one PR-LASM ARC2 diagnostic JSON record")
    parser.add_argument("record")
    args = parser.parse_args()
    record = json.loads(Path(args.record).read_text(encoding="utf-8"))
    print(f"task={record['task_id']}[{record['test_index']}] solved={record['solved']}")
    print(json.dumps(record.get("diagnosis", {}), indent=2))
    for name in ("attempt_1", "attempt_2"):
        comparison = record[f"{name}_comparison"]
        print(
            f"{name}: exact={comparison['exact']} shape_match={comparison['shape_match']} "
            f"agreement={float(comparison['cell_accuracy']):.3%} wrong={comparison['wrong_cells']}"
        )
        print("  residual:", record.get(f"{name}_residual_counts"))
        print("  confusions:", comparison.get("color_confusion", [])[:5])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
