from __future__ import annotations

import argparse
import json
import os
from pathlib import Path


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--environments-dir", type=Path, required=True)
    parser.add_argument("--recordings-dir", type=Path, required=True)
    parser.add_argument("--report", type=Path, required=True)
    args = parser.parse_args()

    # Force the official toolkit into local-only mode before importing it.
    os.environ["OPERATION_MODE"] = "OFFLINE"
    os.environ["ARC_API_KEY"] = ""
    os.environ["ENVIRONMENTS_DIR"] = str(args.environments_dir)
    os.environ["RECORDINGS_DIR"] = str(args.recordings_dir)

    from arc_agi import Arcade, OperationMode

    arcade = Arcade(
        arc_api_key="",
        operation_mode=OperationMode.OFFLINE,
        environments_dir=str(args.environments_dir),
        recordings_dir=str(args.recordings_dir),
    )
    environments = arcade.get_environments()
    rows = [
        {
            "game_id": env.game_id,
            "title": env.title,
            "class_name": env.class_name,
            "local_dir": env.local_dir,
        }
        for env in environments
    ]

    print("Offline local games:")
    for row in rows:
        print(f"  {row['game_id']}  [{row['local_dir']}]")

    args.report.parent.mkdir(parents=True, exist_ok=True)
    args.report.write_text(
        json.dumps(
            {
                "operation_mode": "OFFLINE",
                "network_required": False,
                "game_count": len(rows),
                "games": rows,
            },
            indent=2,
        ),
        encoding="utf-8",
    )
    return 0 if rows else 5


if __name__ == "__main__":
    raise SystemExit(main())
