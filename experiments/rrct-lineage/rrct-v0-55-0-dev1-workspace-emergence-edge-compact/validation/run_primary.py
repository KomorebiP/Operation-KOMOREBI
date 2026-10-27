from __future__ import annotations

import concurrent.futures
import json
import multiprocessing as mp
import os
import pathlib
import sys
from dataclasses import asdict

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from workspace_edge import D1_CHECKPOINTS, DEFAULT_CHECKPOINTS, train_trajectory

SETTINGS = (
    (1, 44, 12, D1_CHECKPOINTS),
    (2, 32, 24, DEFAULT_CHECKPOINTS),
    (3, 25, 24, DEFAULT_CHECKPOINTS),
    (4, 20, 24, DEFAULT_CHECKPOINTS),
    (6, 14, 24, DEFAULT_CHECKPOINTS),
    (8, 10, 24, DEFAULT_CHECKPOINTS),
)


def worker(task: tuple[int, int, int, tuple[int, ...]]) -> dict[str, object]:
    dim, hidden, seed, checkpoints = task
    result = train_trajectory(
        dim=dim,
        hidden=hidden,
        base_seed=seed,
        checkpoints=checkpoints,
    )
    return asdict(result)


def main() -> int:
    seeds = json.loads((ROOT / "validation/SEEDS.json").read_text())["primary_base_seeds"]
    output_root = ROOT / "results/primary"
    output_root.mkdir(parents=True, exist_ok=True)
    tasks: list[tuple[int, int, int, tuple[int, ...]]] = []
    for dim, hidden, count, checkpoints in SETTINGS:
        for seed in seeds[:count]:
            output = output_root / f"d{dim}_h{hidden}_seed{seed}.json"
            if not output.exists():
                tasks.append((dim, hidden, seed, checkpoints))
    print(json.dumps({"pending_primary_tasks": len(tasks)}, sort_keys=True), flush=True)
    context = mp.get_context("spawn")
    with concurrent.futures.ProcessPoolExecutor(
        max_workers=min(4, os.cpu_count() or 1), mp_context=context
    ) as executor:
        future_map = {executor.submit(worker, task): task for task in tasks}
        completed = 0
        for future in concurrent.futures.as_completed(future_map):
            task = future_map[future]
            result = future.result()
            dim, hidden, seed, _ = task
            output = output_root / f"d{dim}_h{hidden}_seed{seed}.json"
            output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
            completed += 1
            print(json.dumps({
                "completed": completed,
                "total": len(tasks),
                "dim": dim,
                "hidden": hidden,
                "seed": seed,
                "stable_onset_step": result["stable_onset_step"],
                "final_emergence": result["final_emergence"],
                "train_seconds": result["train_seconds"],
            }, sort_keys=True), flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
