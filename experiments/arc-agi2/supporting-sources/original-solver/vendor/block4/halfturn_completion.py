from __future__ import annotations

"""Generic masked half-turn completion used to reconcile the Block 3 floor.

The runtime is source-blind with respect to task identifiers.  It infers the most
frequent background color, rotates the foreground bounding box by 180 degrees,
and copies only rotated foreground values into previously background positions.
Original non-background values are preserved.
"""

from collections import Counter
from dataclasses import asdict, dataclass
from typing import Any, Mapping, Sequence

import numpy as np

Grid = tuple[tuple[int, ...], ...]


def array(grid: Any) -> np.ndarray:
    value = np.asarray(grid, dtype=np.int16)
    if value.ndim != 2 or value.size == 0:
        raise ValueError("grid must be a nonempty two-dimensional array")
    return value


def freeze(grid: Any) -> Grid:
    return tuple(tuple(int(v) for v in row) for row in array(grid).tolist())


def exact(left: Any, right: Any) -> bool:
    a, b = array(left), array(right)
    return a.shape == b.shape and bool(np.array_equal(a, b))


def unique_most_frequent_color(grid: Any) -> int | None:
    counts = Counter(int(v) for v in array(grid).ravel())
    if not counts:
        return None
    ranked = counts.most_common()
    if len(ranked) > 1 and ranked[0][1] == ranked[1][1]:
        return None
    return int(ranked[0][0])


def predict_masked_half_turn(grid: Any) -> Grid | None:
    value = array(grid)
    background = unique_most_frequent_color(value)
    if background is None:
        return None
    ys, xs = np.nonzero(value != background)
    if len(ys) == 0:
        return None
    y0, y1 = int(ys.min()), int(ys.max()) + 1
    x0, x1 = int(xs.min()), int(xs.max()) + 1
    source = value[y0:y1, x0:x1]
    rotated = np.rot90(source, 2)
    target = source.copy()
    fill = (target == background) & (rotated != background)
    if not np.any(fill):
        return None
    target[fill] = rotated[fill]
    output = value.copy()
    output[y0:y1, x0:x1] = target
    if np.array_equal(output, value):
        return None
    return freeze(output)


@dataclass(frozen=True)
class HalfTurnCompilation:
    family: str
    program: str
    test_outputs: tuple[Grid, ...]
    train_pair_count: int

    def to_json(self) -> dict[str, Any]:
        return asdict(self)


def compile_task(task: Mapping[str, Any]) -> HalfTurnCompilation | None:
    train = list(task.get("train", ()))
    test = list(task.get("test", ()))
    if not train or not test:
        return None
    for pair in train:
        prediction = predict_masked_half_turn(pair.get("input"))
        if prediction is None or not exact(prediction, pair.get("output")):
            return None
    outputs: list[Grid] = []
    for case in test:
        prediction = predict_masked_half_turn(case.get("input"))
        if prediction is None:
            return None
        outputs.append(prediction)
    return HalfTurnCompilation(
        family="masked_half_turn_completion",
        program="foreground_bbox_rot180_fill_background_preserve_original",
        test_outputs=tuple(outputs),
        train_pair_count=len(train),
    )


def d4_items(grid: Any) -> tuple[np.ndarray, ...]:
    value = array(grid)
    candidates = [
        value,
        np.rot90(value, 1),
        np.rot90(value, 2),
        np.rot90(value, 3),
        np.fliplr(value),
        np.rot90(np.fliplr(value), 1),
        np.rot90(np.fliplr(value), 2),
        np.rot90(np.fliplr(value), 3),
    ]
    return tuple(np.asarray(v, dtype=np.int16) for v in candidates)


def apply_palette(grid: Any, mapping: Mapping[int, int]) -> Grid:
    value = array(grid)
    output = value.copy()
    for source, target in mapping.items():
        output[value == int(source)] = int(target)
    return freeze(output)


def score_submission(submission: Mapping[str, Any], solutions: Mapping[str, Any]) -> dict[str, Any]:
    exact_outputs = 0
    attempt_1_exact = 0
    attempt_2_incremental_exact = 0
    whole_tasks = 0
    exact_keys: list[str] = []
    total = 0
    for task_id, truths in solutions.items():
        task_ok = True
        for index, truth in enumerate(truths):
            total += 1
            row = submission[task_id][index]
            e1 = exact(row["attempt_1"], truth)
            e2 = exact(row["attempt_2"], truth)
            solved = e1 or e2
            exact_outputs += int(solved)
            attempt_1_exact += int(e1)
            attempt_2_incremental_exact += int((not e1) and e2)
            task_ok = task_ok and solved
            if solved:
                exact_keys.append(f"{task_id}:{index}")
        whole_tasks += int(task_ok)
    return {
        "exact_outputs": exact_outputs,
        "total_outputs": total,
        "exact_output_rate": exact_outputs / total if total else 0.0,
        "whole_tasks_solved": whole_tasks,
        "total_tasks": len(solutions),
        "attempt_1_exact": attempt_1_exact,
        "attempt_2_incremental_exact": attempt_2_incremental_exact,
        "exact_keys": exact_keys,
    }


def audit_and_overlay(
    challenges: Mapping[str, Any],
    solutions: Mapping[str, Any],
    baseline_submission: Mapping[str, Any],
    *,
    palette_trials: int = 20,
    random_seed: int = 4421,
) -> tuple[dict[str, Any], dict[str, Any], list[dict[str, Any]]]:
    import copy

    output = copy.deepcopy(baseline_submission)
    ledger: list[dict[str, Any]] = []
    exact_activations = 0
    wrong_activations = 0
    gains = 0
    displaced_exact = 0
    d4_total = 0
    d4_exact = 0
    palette_total = 0
    palette_exact = 0
    rng = np.random.default_rng(random_seed)

    for task_id in sorted(challenges):
        task = challenges[task_id]
        compilation = compile_task(task)
        if compilation is None:
            continue
        truth_outputs = solutions[task_id]
        activation = {
            "task_id": task_id,
            "family": compilation.family,
            "program": compilation.program,
            "train_pair_count": compilation.train_pair_count,
            "outputs": [],
        }
        for index, prediction in enumerate(compilation.test_outputs):
            truth = truth_outputs[index]
            row = output[task_id][index]
            old_solved = exact(row["attempt_1"], truth) or exact(row["attempt_2"], truth)
            old_attempt_2_exact = exact(row["attempt_2"], truth)
            candidate_exact = exact(prediction, truth)
            exact_activations += int(candidate_exact)
            wrong_activations += int(not candidate_exact)
            gains += int(candidate_exact and not old_solved)
            displaced_exact += int(old_attempt_2_exact and not candidate_exact)
            row["attempt_2"] = [list(r) for r in prediction]
            activation["outputs"].append(
                {
                    "test_index": index,
                    "candidate_exact": candidate_exact,
                    "old_solved": old_solved,
                    "gain": bool(candidate_exact and not old_solved),
                    "displaced_attempt_2_exact": old_attempt_2_exact,
                }
            )

        # Equivariance is tested on demonstrations and public-training test outputs.
        source_pairs = list(task["train"]) + [
            {"input": case["input"], "output": truth_outputs[index]}
            for index, case in enumerate(task["test"])
        ]
        for pair in source_pairs:
            input_transforms = d4_items(pair["input"])
            output_transforms = d4_items(pair["output"])
            for transformed_input, transformed_output in zip(input_transforms, output_transforms):
                d4_total += 1
                result = predict_masked_half_turn(transformed_input)
                d4_exact += int(result is not None and exact(result, transformed_output))

            colors = sorted(set(int(v) for v in array(pair["input"]).ravel()) | set(int(v) for v in array(pair["output"]).ravel()))
            for _ in range(palette_trials):
                targets = rng.permutation(np.arange(10, dtype=np.int16))[: len(colors)]
                mapping = {source: int(target) for source, target in zip(colors, targets)}
                transformed_input = apply_palette(pair["input"], mapping)
                transformed_output = apply_palette(pair["output"], mapping)
                palette_total += 1
                result = predict_masked_half_turn(transformed_input)
                palette_exact += int(result is not None and exact(result, transformed_output))
        ledger.append(activation)

    baseline_score = score_submission(baseline_submission, solutions)
    reconciled_score = score_submission(output, solutions)
    baseline_keys = set(baseline_score.pop("exact_keys"))
    reconciled_keys = set(reconciled_score.pop("exact_keys"))
    audit = {
        "schema": "komorebi.arc.masked-half-turn-reconciliation.v1",
        "activation_tasks": len(ledger),
        "activation_outputs": exact_activations + wrong_activations,
        "exact_activations": exact_activations,
        "wrong_activations": wrong_activations,
        "new_exact_outputs": gains,
        "displaced_exact_attempt_2_outputs": displaced_exact,
        "baseline": baseline_score,
        "reconciled": reconciled_score,
        "lost_exact_outputs": sorted(baseline_keys - reconciled_keys),
        "gained_exact_outputs": sorted(reconciled_keys - baseline_keys),
        "d4": {"exact": d4_exact, "total": d4_total},
        "palette": {"exact": palette_exact, "total": palette_total},
        "pass": all(
            [
                len(ledger) == 1,
                wrong_activations == 0,
                gains == 1,
                displaced_exact == 0,
                not (baseline_keys - reconciled_keys),
                d4_exact == d4_total,
                palette_exact == palette_total,
            ]
        ),
        "claim_boundary": "Retrospective public-training validation of one generic demonstration-compiled operator family; no hidden-evaluation claim.",
    }
    return output, audit, ledger
