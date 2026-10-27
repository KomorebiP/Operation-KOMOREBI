#!/usr/bin/env python3
from __future__ import annotations

"""Live Block 4 wrapper: Block 2 portfolio + half-turn lane + open-world posterior."""

import argparse
import copy
import hashlib
import json
from pathlib import Path
import sys
from typing import Any, Mapping, Sequence

from halfturn_completion import compile_task, exact, freeze
from open_world_posterior import calibrate_runtime_submission

ROOT = Path(__file__).resolve().parents[1]
BLOCK2 = ROOT / "block2"
if str(BLOCK2) not in sys.path:
    sys.path.insert(0, str(BLOCK2))

from block2_solver import solve_task as solve_block2_task  # noqa: E402

DEFAULT_MODEL = Path(__file__).with_name("models") / "open_world_posterior_models.json"
DEFAULT_APPROVAL = Path(__file__).with_name("approved_halfturn_family.json")


class Block4RuntimeError(ValueError):
    pass


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def load_halfturn_approval(path: Path = DEFAULT_APPROVAL) -> dict[str, Any]:
    record = json.loads(path.read_text(encoding="utf-8"))
    if record.get("schema") != "komorebi.arc.approved-halfturn-family.v1":
        raise Block4RuntimeError("unsupported half-turn approval schema")
    runtime = Path(__file__).with_name("halfturn_completion.py")
    observed = _sha256(runtime)
    if observed != record.get("implementation_sha256"):
        raise Block4RuntimeError("half-turn approval fingerprint does not match runtime source")
    if record.get("family") != "masked_half_turn_completion":
        raise Block4RuntimeError("unexpected approved family")
    return record


def apply_halfturn_lane(
    task: Mapping[str, Any],
    baseline_results: Sequence[Mapping[str, Any]],
    *,
    approval_path: Path = DEFAULT_APPROVAL,
) -> tuple[list[dict[str, Any]], dict[str, Any], list[dict[str, Any]]]:
    approval = load_halfturn_approval(approval_path)
    final = copy.deepcopy(list(baseline_results))
    compilation = compile_task(task)
    outputs: list[dict[str, Any]] = []
    if compilation is None:
        return final, {
            "lane": "masked_half_turn_completion",
            "status": "abstained",
            "reason": "demonstrations_not_exact_or_test_execution_undefined",
        }, []
    if len(compilation.test_outputs) != len(final):
        raise Block4RuntimeError("half-turn output count does not match baseline")
    for index, candidate in enumerate(compilation.test_outputs):
        before_1 = freeze(final[index]["attempt_1"])
        before_2 = freeze(final[index]["attempt_2"])
        if candidate in {before_1, before_2}:
            outputs.append({"test_index": index, "promoted": False, "reason": "already_present"})
            continue
        final[index]["attempt_2"] = [list(row) for row in candidate]
        outputs.append(
            {
                "test_index": index,
                "promoted": True,
                "reason": "unique_demonstration_exact_approved_family",
                "family": compilation.family,
            }
        )
    ledger = [
        {
            "task_id": "runtime",
            "family": compilation.family,
            "program": compilation.program,
            "train_pair_count": compilation.train_pair_count,
            "outputs": outputs,
        }
    ]
    return final, {
        "lane": "masked_half_turn_completion",
        "status": "completed",
        "approval_sha256": _sha256(approval_path),
        "implementation_sha256": approval["implementation_sha256"],
        "outputs": outputs,
        "test_outputs_ignored": True,
    }, ledger


def _normalize_block2_promotions(record: Mapping[str, Any]) -> list[dict[str, Any]]:
    output: list[dict[str, Any]] = []
    block2 = record.get("block2", {}) if isinstance(record, Mapping) else {}
    for row in block2.get("promotions", []) if isinstance(block2, Mapping) else []:
        if not row.get("promoted"):
            continue
        families = list(row.get("families", []))
        output.append(
            {
                "task_id": "runtime",
                "test_index": int(row["test_index"]),
                "family": str(families[0] if families else "discrete_unknown"),
                "promoted": True,
            }
        )
    return output


def solve_task(
    task: Mapping[str, Any],
    *,
    time_limit: float = 8.0,
    model_path: Path = DEFAULT_MODEL,
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    block2_results, block2_diagnostics = solve_block2_task(task, time_limit=time_limit)
    halfturn_results, halfturn_diagnostics, halfturn_ledger = apply_halfturn_lane(task, block2_results)
    model_bundle = json.loads(model_path.read_text(encoding="utf-8"))
    challenges = {"runtime": task}
    submission = {"runtime": halfturn_results}
    base_diagnostics = block2_diagnostics.get("base", {})
    diagnostics = {"tasks": {"runtime": base_diagnostics}}
    calibrated, posterior_ledger = calibrate_runtime_submission(
        challenges,
        diagnostics,
        submission,
        model_bundle,
        block2_promotions=_normalize_block2_promotions(block2_diagnostics),
        halfturn_ledger=halfturn_ledger,
    )
    return calibrated["runtime"], {
        "solver": "Komorebi ARC-AGI2 1.6.0.dev2 + Blocks 2/4",
        "block2": block2_diagnostics,
        "halfturn": halfturn_diagnostics,
        "open_world_posterior": posterior_ledger,
        "attempt_set_preserved": True,
    }


def solve_challenge_file(
    input_path: Path,
    output_path: Path,
    *,
    diagnostics_path: Path | None = None,
    time_limit: float = 8.0,
) -> dict[str, Any]:
    tasks = json.loads(input_path.read_text(encoding="utf-8"))
    if not isinstance(tasks, dict):
        raise Block4RuntimeError("challenge file must contain a task dictionary")
    submission: dict[str, Any] = {}
    diagnostics: dict[str, Any] = {}
    for ordinal, task_id in enumerate(sorted(tasks), 1):
        task = tasks[task_id]
        if not isinstance(task, Mapping):
            raise Block4RuntimeError(f"task {task_id!r} is not a mapping")
        answers, record = solve_task(task, time_limit=time_limit)
        submission[str(task_id)] = answers
        diagnostics[str(task_id)] = record
        print(f"[{ordinal:4d}/{len(tasks)}] {task_id}", flush=True)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(submission, separators=(",", ":")) + "\n", encoding="utf-8")
    if diagnostics_path is not None:
        diagnostics_path.parent.mkdir(parents=True, exist_ok=True)
        diagnostics_path.write_text(json.dumps(diagnostics, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return submission


def main() -> None:
    parser = argparse.ArgumentParser(description="Komorebi ARC-AGI2 Block 4 runtime")
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--diagnostics", type=Path)
    parser.add_argument("--time-limit", type=float, default=8.0)
    args = parser.parse_args()
    solve_challenge_file(
        args.input,
        args.output,
        diagnostics_path=args.diagnostics,
        time_limit=args.time_limit,
    )


if __name__ == "__main__":
    main()
