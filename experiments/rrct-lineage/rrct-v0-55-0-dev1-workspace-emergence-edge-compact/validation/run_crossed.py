from __future__ import annotations

import concurrent.futures
import hashlib
import json
import multiprocessing as mp
import os
import pathlib
import sys
from dataclasses import asdict

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from workspace_edge import DEFAULT_CHECKPOINTS, train_trajectory


def base_seed(init_seed: int, data_seed: int) -> int:
    digest = hashlib.sha256(f"v055-cross:{init_seed}:{data_seed}".encode()).digest()
    return int.from_bytes(digest[:8], "big") % 900_000_000 + 100_000_000


def worker(task: tuple[int, int]) -> dict[str, object]:
    init_seed, data_seed = task
    result = train_trajectory(
        dim=2,
        hidden=32,
        base_seed=base_seed(init_seed, data_seed),
        initialization_seed=init_seed,
        data_seed=data_seed,
        checkpoints=DEFAULT_CHECKPOINTS,
    )
    return asdict(result)


def main() -> int:
    payload = json.loads((ROOT / "validation/SEEDS.json").read_text())
    init_seeds = payload["cross_initialization_seeds"]
    data_seeds = payload["cross_data_seeds"]
    output_root = ROOT / "results/crossed"
    output_root.mkdir(parents=True, exist_ok=True)
    tasks: list[tuple[int, int]] = []
    for init_seed in init_seeds:
        for data_seed in data_seeds:
            output = output_root / f"init{init_seed}_data{data_seed}.json"
            if not output.exists():
                tasks.append((init_seed, data_seed))
    print(json.dumps({"pending_crossed_tasks": len(tasks)}, sort_keys=True), flush=True)
    context = mp.get_context("spawn")
    with concurrent.futures.ProcessPoolExecutor(
        max_workers=min(4, os.cpu_count() or 1), mp_context=context
    ) as executor:
        future_map = {executor.submit(worker, task): task for task in tasks}
        completed = 0
        for future in concurrent.futures.as_completed(future_map):
            init_seed, data_seed = future_map[future]
            result = future.result()
            output = output_root / f"init{init_seed}_data{data_seed}.json"
            output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
            completed += 1
            print(json.dumps({
                "completed": completed,
                "total": len(tasks),
                "init_seed": init_seed,
                "data_seed": data_seed,
                "stable_onset_step": result["stable_onset_step"],
                "final_emergence": result["final_emergence"],
            }, sort_keys=True), flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
