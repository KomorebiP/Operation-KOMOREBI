#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Runtime wrapper for the Block 2 Discrete Perturbation Operator Atlas.

The wrapper preserves Attempt 1 from the verified 1.6.0.dev2 solver.  It may
replace Attempt 2 only when exactly one approved semantic family (or several
approved families with the same output) compiles from the task's training
examples and executes unambiguously on the held-out input.

The approval file contains family names and an implementation fingerprint,
not task identifiers, coordinates, expected test grids, or answer hashes.
"""

from __future__ import annotations

import argparse
import json
from copy import deepcopy
from pathlib import Path
from typing import Dict, Iterable, List, Mapping, Optional, Sequence, Set, Tuple

import numpy as np

from discrete_perturbation_operator_atlas import (
    AtlasCompilation,
    compile_discrete_perturbation_operator_atlas,
    exact,
    family_outputs_by_test,
    grid_hash,
    grid_to_list,
    implementation_fingerprint,
    sanitize_grid,
)

Grid = List[List[int]]
Prediction = Dict[str, Grid]
DEFAULT_APPROVAL_FILE = Path(__file__).with_name("approved_families.json")


class Block2RuntimeError(ValueError):
    """Invalid approval evidence, task, or baseline prediction."""


def load_approved_families(path: Path = DEFAULT_APPROVAL_FILE) -> Set[str]:
    record = json.loads(path.read_text(encoding="utf-8"))
    if record.get("schema") != "komorebi.arc.discrete-perturbation-approved-families.v1":
        raise Block2RuntimeError("unsupported approved-family evidence schema")
    expected = str(record.get("implementation_sha256", ""))
    observed = implementation_fingerprint()
    if expected != observed:
        raise Block2RuntimeError(
            f"operator-atlas fingerprint mismatch: evidence={expected} runtime={observed}"
        )
    families = record.get("families")
    if not isinstance(families, list) or not families or not all(isinstance(value, str) and value for value in families):
        raise Block2RuntimeError("approved-family evidence contains no valid families")
    return set(families)


def _normalize_task(task: Mapping[str, object]) -> Tuple[List[Tuple[np.ndarray, np.ndarray]], List[np.ndarray]]:
    train: List[Tuple[np.ndarray, np.ndarray]] = []
    for index, pair in enumerate(task.get("train", [])):  # type: ignore[arg-type]
        if not isinstance(pair, Mapping) or "input" not in pair or "output" not in pair:
            raise Block2RuntimeError(f"training pair {index} lacks input/output")
        train.append((sanitize_grid(pair["input"]), sanitize_grid(pair["output"])))
    tests: List[np.ndarray] = []
    for index, pair in enumerate(task.get("test", [])):  # type: ignore[arg-type]
        if not isinstance(pair, Mapping) or "input" not in pair:
            raise Block2RuntimeError(f"test pair {index} lacks input")
        # Deliberately ignore any attached test output.
        tests.append(sanitize_grid(pair["input"]))
    if not train:
        raise Block2RuntimeError("Block 2 requires at least one training demonstration")
    if not tests:
        raise Block2RuntimeError("Block 2 requires at least one test input")
    return train, tests


def _normalize_baseline(results: Sequence[Mapping[str, object]], test_count: int) -> List[Prediction]:
    if len(results) != test_count:
        raise Block2RuntimeError("baseline result count does not match test count")
    output: List[Prediction] = []
    for index, record in enumerate(results):
        if "attempt_1" not in record or "attempt_2" not in record:
            raise Block2RuntimeError(f"baseline result {index} lacks two attempts")
        output.append(
            {
                "attempt_1": grid_to_list(record["attempt_1"]),
                "attempt_2": grid_to_list(record["attempt_2"]),
            }
        )
    return output


def apply_block2_atlas(
    task: Mapping[str, object],
    baseline_results: Sequence[Mapping[str, object]],
    *,
    approved_families: Optional[Iterable[str]] = None,
) -> Tuple[List[Prediction], Dict[str, object]]:
    """Apply the source-blind Block 2 lane to already computed base attempts."""

    train, tests = _normalize_task(task)
    approved = set(approved_families) if approved_families is not None else load_approved_families()
    final = _normalize_baseline(baseline_results, len(tests))

    try:
        compilation = compile_discrete_perturbation_operator_atlas(train, tests)
        by_family = family_outputs_by_test(compilation, len(tests))
    except Exception as error:
        return final, {
            "lane": "discrete_perturbation_operator_atlas",
            "status": "rolled_back_to_baseline",
            "error": f"{type(error).__name__}: {error}",
            "approved_families": sorted(approved),
            "promotions": [],
        }

    promotions: List[Dict[str, object]] = []
    for test_index, test_grid in enumerate(tests):
        candidates: Dict[str, Dict[str, object]] = {}
        for family in sorted(approved):
            outputs = by_family.get(family)
            if outputs is None or test_index >= len(outputs):
                continue
            candidate = outputs[test_index]
            if candidate is None:
                continue
            candidate_hash = grid_hash(candidate)
            item = candidates.setdefault(
                candidate_hash,
                {
                    "grid": candidate.copy(),
                    "families": [],
                    "program_hashes": [],
                },
            )
            item["families"].append(family)
            item["program_hashes"].extend(
                packet.program_hash
                for packet in compilation.packets
                if packet.family == family
            )

        if not candidates:
            promotions.append(
                {
                    "test_index": test_index,
                    "promoted": False,
                    "reason": "no_approved_unanimous_family",
                }
            )
            continue
        if len(candidates) != 1:
            promotions.append(
                {
                    "test_index": test_index,
                    "promoted": False,
                    "reason": "approved_family_conflict",
                    "candidate_hashes": sorted(candidates),
                    "families": sorted(
                        {family for item in candidates.values() for family in item["families"]}
                    ),
                }
            )
            continue

        candidate_hash, item = next(iter(candidates.items()))
        candidate = sanitize_grid(item["grid"])
        first = sanitize_grid(final[test_index]["attempt_1"])
        second = sanitize_grid(final[test_index]["attempt_2"])
        common = {
            "test_index": test_index,
            "families": sorted(set(item["families"])),
            "program_hashes": sorted(set(item["program_hashes"])),
            "candidate_hash": candidate_hash,
            "training_exact_gate": True,
            "source_blind_test_execution": True,
        }
        if exact(candidate, first) or exact(candidate, second):
            promotions.append(
                {
                    **common,
                    "promoted": False,
                    "reason": "candidate_already_present",
                }
            )
            continue
        displaced_hash = grid_hash(second)
        final[test_index]["attempt_2"] = grid_to_list(candidate)
        promotions.append(
            {
                **common,
                "promoted": True,
                "reason": "unique_approved_family_override_attempt_2",
                "displaced_attempt_2_hash": displaced_hash,
            }
        )

    return final, {
        "lane": "discrete_perturbation_operator_atlas",
        "status": "completed",
        "tool_version": "0.1.0",
        "implementation_sha256": implementation_fingerprint(),
        "approved_families": sorted(approved),
        "packet_count": len(compilation.packets),
        "compiled_families": sorted({packet.family for packet in compilation.packets}),
        "abstentions": [dict(record) for record in compilation.abstentions],
        "promotions": promotions,
        "attempt_1_protected": True,
        "test_outputs_ignored": True,
    }


def solve_task(
    task: Mapping[str, object],
    *,
    time_limit: float = 8.0,
    approved_families: Optional[Iterable[str]] = None,
) -> Tuple[List[Prediction], Dict[str, object]]:
    """Run the verified base solver, then the isolated Block 2 challenger lane."""

    from komorebi_arc2.entry import solve_task as solve_base_task

    base_diagnostics: Dict[str, object] = {}
    baseline = solve_base_task(dict(task), time_limit=time_limit, diagnostics=base_diagnostics)
    final, block2_diagnostics = apply_block2_atlas(
        task,
        baseline,
        approved_families=approved_families,
    )
    return final, {
        "solver": "Komorebi ARC-AGI2 1.6.0.dev2 + Block 2",
        "base_solver_version": "1.6.0.dev2",
        "base": base_diagnostics,
        "block2": block2_diagnostics,
    }


def solve_challenge_file(
    input_path: Path,
    output_path: Path,
    *,
    time_limit: float = 8.0,
    diagnostics_path: Optional[Path] = None,
) -> Dict[str, object]:
    tasks = json.loads(input_path.read_text(encoding="utf-8"))
    if not isinstance(tasks, dict):
        raise Block2RuntimeError("challenge file must contain a task dictionary")
    submission: Dict[str, object] = {}
    diagnostics: Dict[str, object] = {}
    for ordinal, task_id in enumerate(sorted(tasks), 1):
        task = tasks[task_id]
        if not isinstance(task, Mapping):
            raise Block2RuntimeError(f"task {task_id!r} is not a mapping")
        results, record = solve_task(task, time_limit=time_limit)
        submission[str(task_id)] = results
        diagnostics[str(task_id)] = record
        print(f"[{ordinal:4d}/{len(tasks)}] {task_id}", flush=True)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(submission, separators=(",", ":")) + "\n", encoding="utf-8")
    if diagnostics_path is not None:
        diagnostics_path.parent.mkdir(parents=True, exist_ok=True)
        diagnostics_path.write_text(json.dumps(diagnostics, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return submission


def main() -> None:
    parser = argparse.ArgumentParser(description="Komorebi ARC-AGI2 Block 2 runtime")
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--diagnostics", type=Path)
    parser.add_argument("--time-limit", type=float, default=8.0)
    args = parser.parse_args()
    solve_challenge_file(
        args.input,
        args.output,
        time_limit=args.time_limit,
        diagnostics_path=args.diagnostics,
    )


if __name__ == "__main__":
    main()
