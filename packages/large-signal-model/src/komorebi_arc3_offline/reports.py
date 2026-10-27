from __future__ import annotations

import csv
import json
from dataclasses import asdict
from pathlib import Path
from typing import Iterable

from .types import RunResult


def write_run_index(results: Iterable[RunResult], output_dir: str | Path) -> dict[str, Path]:
    rows = list(results)
    output = Path(output_dir).expanduser().resolve()
    output.mkdir(parents=True, exist_ok=True)
    summary = {
        "offline_only": True,
        "games": len(rows),
        "solved": sum(result.solved for result in rows),
        "solve_rate": sum(result.solved for result in rows) / max(1, len(rows)),
        "committed_actions": sum(result.committed_actions for result in rows),
        "probe_actions": sum(result.probe_actions for result in rows),
        "resets": sum(result.resets for result in rows),
        "elapsed_seconds": sum(result.elapsed_seconds for result in rows),
    }
    json_path = output / "run_index.json"
    json_path.write_text(
        json.dumps({"summary": summary, "results": [asdict(row) for row in rows]}, indent=2),
        encoding="utf-8",
    )
    csv_path = output / "run_index.csv"
    with csv_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=[
                "game_id",
                "solved",
                "final_state",
                "levels_completed",
                "win_levels",
                "committed_actions",
                "probe_actions",
                "resets",
                "elapsed_seconds",
                "model_updates",
                "output_dir",
            ],
        )
        writer.writeheader()
        for row in rows:
            payload = asdict(row)
            payload.pop("notes", None)
            writer.writerow(payload)
    return {"json": json_path, "csv": csv_path}
