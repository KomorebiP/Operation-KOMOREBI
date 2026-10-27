from __future__ import annotations

import concurrent.futures
import copy
import itertools
import json
import multiprocessing as mp
import pathlib
import traceback
from collections.abc import Mapping
from typing import Any

from .config import validate_config
from .exceptions import ConfigError
from .runner import project_root, run_config
from .utils import atomic_write_json, digest_object, set_dotted, write_csv


def expand_grid(grid: Mapping[str, Any]) -> list[dict[str, Any]]:
    keys = list(grid)
    values = []
    for key in keys:
        value = grid[key]
        values.append(value if isinstance(value, list) else [value])
    return [
        dict(zip(keys, combination, strict=True))
        for combination in itertools.product(*values)
    ]


def _base_config_digest(config: dict[str, Any]) -> str:
    return digest_object(config)


def _cell_name(
    index: int,
    overrides: dict[str, Any],
    base_config_digest: str,
) -> str:
    identity = {
        "base_config_digest": base_config_digest,
        "overrides": overrides,
    }
    return f"cell{index:04d}_{digest_object(identity)[:10]}"


def _execute_cell(payload: dict[str, Any]) -> dict[str, Any]:
    index = int(payload["index"])
    overrides = dict(payload["overrides"])
    local = dict(payload["config"])
    try:
        summary = run_config(local)[0]
        row = {
            "cell": index,
            "cell_id": payload["cell_id"],
            **overrides,
            "status": summary["status"],
            "run_directory": summary["run_directory"],
            "resumed_without_reexecution": bool(
                summary.get("resumed_without_reexecution", False)
            ),
        }
        row.update(
            {
                f"metric.{key}": value
                for key, value in summary.get("metrics", {}).items()
                if isinstance(value, (int, float, str, bool))
            }
        )
        return {"ok": True, "row": row}
    except BaseException as exc:
        return {
            "ok": False,
            "row": {
                "cell": index,
                "cell_id": payload["cell_id"],
                **overrides,
                "status": "failed",
                "error_type": type(exc).__name__,
                "error": str(exc),
                "traceback": traceback.format_exc(),
            },
        }


def _prepare_cells(
    config: dict[str, Any],
    sweep_dir: pathlib.Path,
    base_config_digest: str,
) -> list[dict[str, Any]]:
    grid = config.get("sweep", {}).get("grid", {})
    combinations = expand_grid(grid)
    max_runs = int(config.get("sweep", {}).get("max_runs", 0))
    if max_runs > 0:
        combinations = combinations[:max_runs]
    cells: list[dict[str, Any]] = []
    for index, overrides in enumerate(combinations):
        local = copy.deepcopy(config)
        cell_id = _cell_name(index, overrides, base_config_digest)
        local["run"]["name"] = cell_id
        local["run"]["repetitions"] = 1
        local["run"]["output_root"] = str(sweep_dir / "cells")
        local["run"]["overwrite"] = True
        local["run"]["resume"] = bool(config.get("sweep", {}).get("resume", True))
        local["sweep"]["enabled"] = False
        for key, value in overrides.items():
            set_dotted(local, key, value)
        validate_config(local)
        cells.append(
            {
                "index": index,
                "cell_id": cell_id,
                "overrides": overrides,
                "config": local,
            }
        )
    return cells


def run_sweep(config: dict[str, Any]) -> dict[str, Any]:
    validate_config(config)
    root = project_root()
    output_root = pathlib.Path(config["run"]["output_root"])
    if not output_root.is_absolute():
        output_root = root / output_root
    sweep_dir = output_root / f"{config['run']['name']}_sweep"
    sweep_dir.mkdir(parents=True, exist_ok=True)
    base_config_digest = _base_config_digest(config)
    cells = _prepare_cells(config, sweep_dir, base_config_digest)
    state_path = sweep_dir / str(config.get("sweep", {}).get("state_file", "sweep_state.json"))
    existing_rows: dict[str, dict[str, Any]] = {}
    if bool(config.get("sweep", {}).get("resume", True)) and state_path.is_file():
        try:
            prior_state = json.loads(state_path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError) as exc:
            raise ConfigError(f"cannot resume invalid sweep state: {state_path}") from exc
        if not isinstance(prior_state, dict):
            raise ConfigError(f"cannot resume invalid sweep state: {state_path}")
        if prior_state.get("base_config_digest") != base_config_digest:
            raise ConfigError(
                "sweep state base configuration digest does not match the requested sweep"
            )
        for row in prior_state.get("rows", []):
            if isinstance(row, dict) and row.get("status") == "completed":
                existing_rows[str(row["cell_id"])] = row

    pending = [cell for cell in cells if cell["cell_id"] not in existing_rows]
    workers = max(1, int(config.get("sweep", {}).get("parallel_workers", 1)))
    device = str(config.get("runtime", {}).get("device", "auto")).lower()
    if device.startswith("cuda"):
        workers = min(workers, max(1, int(config.get("sweep", {}).get("gpu_workers", 1))))
    execute = bool(config.get("sweep", {}).get("execute", True))
    rows: dict[str, dict[str, Any]] = dict(existing_rows)
    retries = max(0, int(config.get("sweep", {}).get("retry_failures", 0)))
    fail_fast = bool(config.get("sweep", {}).get("fail_fast", False))

    manifest = {
        "schema": "rrct.lab.sweep_state.v3",
        "sweep_name": config["run"]["name"],
        "base_config_digest": base_config_digest,
        "grid": config.get("sweep", {}).get("grid", {}),
        "cell_count": len(cells),
        "parallel_workers": workers,
        "resume": bool(config.get("sweep", {}).get("resume", True)),
        "rows": sorted(rows.values(), key=lambda item: int(item["cell"])),
    }
    atomic_write_json(state_path, manifest)

    if execute and pending:
        attempts: dict[str, int] = {cell["cell_id"]: 0 for cell in pending}
        queue = list(pending)
        context = mp.get_context("spawn")
        with concurrent.futures.ProcessPoolExecutor(
            max_workers=workers,
            mp_context=context,
        ) as pool:
            futures: dict[concurrent.futures.Future[dict[str, Any]], dict[str, Any]] = {}

            def submit(cell: dict[str, Any]) -> None:
                attempts[cell["cell_id"]] += 1
                futures[pool.submit(_execute_cell, cell)] = cell

            while queue and len(futures) < workers:
                submit(queue.pop(0))
            while futures:
                done, _ = concurrent.futures.wait(
                    futures,
                    return_when=concurrent.futures.FIRST_COMPLETED,
                )
                for future in done:
                    cell = futures.pop(future)
                    result = future.result()
                    row = result["row"]
                    rows[cell["cell_id"]] = row
                    if (
                        not result["ok"]
                        and attempts[cell["cell_id"]] <= retries
                    ):
                        queue.append(cell)
                    elif not result["ok"] and fail_fast:
                        for other in futures:
                            other.cancel()
                        futures.clear()
                        queue.clear()
                    manifest["rows"] = sorted(
                        rows.values(), key=lambda item: int(item["cell"])
                    )
                    manifest["completed_cells"] = sum(
                        row.get("status") == "completed" for row in rows.values()
                    )
                    manifest["failed_cells"] = sum(
                        row.get("status") == "failed" for row in rows.values()
                    )
                    atomic_write_json(state_path, manifest)
                while queue and len(futures) < workers:
                    submit(queue.pop(0))

    ordered = sorted(rows.values(), key=lambda item: int(item["cell"]))
    write_csv(sweep_dir / "sweep.csv", ordered)
    payload = {
        "schema": "rrct.lab.sweep.v3",
        "base_config_digest": base_config_digest,
        "cell_count": len(cells),
        "completed_cells": sum(row.get("status") == "completed" for row in ordered),
        "failed_cells": sum(row.get("status") == "failed" for row in ordered),
        "skipped_completed_cells": len(existing_rows),
        "grid": config.get("sweep", {}).get("grid", {}),
        "parallel_workers": workers,
        "sweep_directory": str(sweep_dir),
        "rows": ordered,
    }
    atomic_write_json(sweep_dir / "sweep.json", payload)
    atomic_write_json(state_path, {**manifest, **payload})
    return payload
