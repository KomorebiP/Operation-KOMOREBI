#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Hard-isolated Kaggle submission runner for the frozen PR-LASM ARC2 solver."""

from __future__ import annotations

import argparse
import importlib.util
import json
import os
import shutil
import subprocess
import sys
import tempfile
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from typing import Any

# Each task runs in its own process. Prevent NumPy/BLAS from multiplying the
# process count by an additional thread pool on Kaggle CPUs.
for _name in ("OPENBLAS_NUM_THREADS", "OMP_NUM_THREADS", "MKL_NUM_THREADS", "NUMEXPR_NUM_THREADS"):
    os.environ.setdefault(_name, "1")


def load_solver(path: str | Path):
    path = str(Path(path).resolve())
    spec = importlib.util.spec_from_file_location("pr_lasm_arc2_frozen", path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Could not load frozen solver: {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def safe_fallback(task: dict[str, Any], solver) -> list[dict[str, list[list[int]]]]:
    out = []
    for case in task.get("test", []):
        grid = solver.as_array(case.get("input", [[0]]))
        crop = solver.crop_bbox_non_bg(grid)
        out.append({
            "attempt_1": solver.grid_to_list(grid),
            "attempt_2": solver.grid_to_list(crop),
        })
    return out


def worker_mode(args: argparse.Namespace) -> int:
    solver = load_solver(args.solver)
    task = json.loads(Path(args.task).read_text(encoding="utf-8"))
    predictions = solver.solve_task(task, time_limit=args.soft_time_limit)
    Path(args.result).write_text(json.dumps(predictions, separators=(",", ":")), encoding="utf-8")
    return 0


def run_one(
    task_id: str,
    task: dict[str, Any],
    solver_path: Path,
    runner_path: Path,
    work_dir: Path,
    soft_limit: float,
    hard_limit: float,
) -> tuple[str, list[dict[str, list[list[int]]]] | None, dict[str, Any]]:
    task_path = work_dir / f"{task_id}.task.json"
    result_path = work_dir / f"{task_id}.result.json"
    task_path.write_text(json.dumps(task, separators=(",", ":")), encoding="utf-8")
    command = [
        sys.executable,
        str(runner_path),
        "--worker",
        "--solver",
        str(solver_path),
        "--task",
        str(task_path),
        "--result",
        str(result_path),
        "--soft-time-limit",
        str(soft_limit),
    ]
    started = time.perf_counter()
    try:
        child_env = os.environ.copy()
        child_env.update({
            "OPENBLAS_NUM_THREADS": "1",
            "OMP_NUM_THREADS": "1",
            "MKL_NUM_THREADS": "1",
            "NUMEXPR_NUM_THREADS": "1",
        })
        proc = subprocess.run(
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            timeout=hard_limit,
            check=False,
            env=child_env,
        )
        elapsed = time.perf_counter() - started
        if proc.returncode != 0 or not result_path.exists():
            return task_id, None, {
                "status": "worker_error",
                "elapsed_seconds": elapsed,
                "returncode": proc.returncode,
                "stderr": proc.stderr[-2000:],
            }
        predictions = json.loads(result_path.read_text(encoding="utf-8"))
        return task_id, predictions, {
            "status": "ok",
            "elapsed_seconds": elapsed,
            "returncode": 0,
        }
    except subprocess.TimeoutExpired as exc:
        return task_id, None, {
            "status": "hard_timeout",
            "elapsed_seconds": time.perf_counter() - started,
            "returncode": None,
            "stderr": str(exc),
        }
    except Exception as exc:
        return task_id, None, {
            "status": "runner_error",
            "elapsed_seconds": time.perf_counter() - started,
            "returncode": None,
            "stderr": f"{type(exc).__name__}: {exc}",
        }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Hard-isolated PR-LASM ARC2 Kaggle runner")
    parser.add_argument("--worker", action="store_true", help=argparse.SUPPRESS)
    parser.add_argument("--solver", required=True, help="path to the frozen arc2_entry.py")
    parser.add_argument("--task", help=argparse.SUPPRESS)
    parser.add_argument("--result", help=argparse.SUPPRESS)
    parser.add_argument("--data-dir", default="/kaggle/input")
    parser.add_argument("--input", default=None, help="explicit ARC challenge JSON")
    parser.add_argument("--output", default="/kaggle/working/submission.json")
    parser.add_argument("--report", default="/kaggle/working/pr_lasm_arc2_runtime_report.json")
    parser.add_argument("--soft-time-limit", type=float, default=8.0)
    parser.add_argument("--hard-time-limit", type=float, default=20.0)
    parser.add_argument("--workers", type=int, default=max(1, min(4, os.cpu_count() or 1)))
    parser.add_argument("--max-tasks", type=int, default=None)
    parser.add_argument("--keep-work-dir", action="store_true")
    args = parser.parse_args(argv)

    if args.worker:
        if not args.task or not args.result:
            parser.error("worker mode requires --task and --result")
        return worker_mode(args)

    solver_path = Path(args.solver).resolve()
    runner_path = Path(__file__).resolve()
    solver = load_solver(solver_path)
    challenge_path = args.input or solver.find_challenge_json(args.data_dir, "test") or solver.find_input_json(args.data_dir, "test")
    if not challenge_path:
        raise FileNotFoundError(f"No ARC-AGI-2 test challenge JSON found under {args.data_dir}")
    tasks = solver.load_tasks_from_path(challenge_path)
    if args.max_tasks is not None:
        tasks = dict(list(tasks.items())[: args.max_tasks])

    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    report_path = Path(args.report)
    report_path.parent.mkdir(parents=True, exist_ok=True)
    work_dir = Path(tempfile.mkdtemp(prefix="pr_lasm_arc2_", dir=str(output_path.parent)))

    started = time.perf_counter()
    submission: dict[str, Any] = {}
    records: dict[str, Any] = {}
    try:
        with ThreadPoolExecutor(max_workers=max(1, args.workers)) as executor:
            futures = {
                executor.submit(
                    run_one,
                    task_id,
                    task,
                    solver_path,
                    runner_path,
                    work_dir,
                    args.soft_time_limit,
                    args.hard_time_limit,
                ): task_id
                for task_id, task in tasks.items()
            }
            for number, future in enumerate(as_completed(futures), 1):
                task_id, predictions, record = future.result()
                if predictions is None:
                    predictions = safe_fallback(tasks[task_id], solver)
                    record["fallback"] = "identity_and_nonbackground_crop"
                else:
                    record["fallback"] = None
                submission[task_id] = predictions
                records[task_id] = record
                if number % 25 == 0 or number == len(tasks):
                    print(f"completed {number}/{len(tasks)} tasks", flush=True)

        submission = {task_id: submission[task_id] for task_id in tasks}
        errors = solver.validate_submission(submission, tasks)
        solver.write_submission(submission, output_path)
        report = {
            "solver_name": solver.SOLVER_NAME,
            "solver_version": solver.SOLVER_VERSION,
            "challenge_path": str(challenge_path),
            "output_path": str(output_path),
            "tasks": len(tasks),
            "soft_time_limit_seconds": args.soft_time_limit,
            "hard_time_limit_seconds": args.hard_time_limit,
            "workers": max(1, args.workers),
            "wall_seconds": time.perf_counter() - started,
            "worker_ok": sum(r["status"] == "ok" for r in records.values()),
            "hard_timeouts": sum(r["status"] == "hard_timeout" for r in records.values()),
            "worker_errors": sum(r["status"] not in {"ok", "hard_timeout"} for r in records.values()),
            "valid_submission": not errors,
            "validation_errors": errors[:25],
            "per_task": {k: records[k] for k in tasks},
        }
        report_path.write_text(json.dumps(report, indent=2), encoding="utf-8")
        print(json.dumps({k: v for k, v in report.items() if k != "per_task"}, indent=2))
        return 0 if not errors else 2
    finally:
        if not args.keep_work_dir:
            shutil.rmtree(work_dir, ignore_errors=True)


if __name__ == "__main__":
    raise SystemExit(main())
