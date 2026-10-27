"""Conservative same-shape local transduction entrant for the Block 13 tourney.

The entrant intentionally has a narrow interface.  It consumes only training
input/output pairs and test inputs, learns deterministic identity-default edit
programs, and returns only programs which replay every training output exactly.
No task identifier, test output, solution, or external corpus is consulted.

The program dictionaries returned here are deliberately executable and JSON
serializable.  ``execute_program`` is public so the tournament harness can
independently replay a candidate instead of trusting cached predictions.
"""

from __future__ import annotations

from collections import Counter
from collections.abc import Mapping, Sequence
import json
from typing import Any, Callable, Optional


Grid = list[list[int]]
Pair = tuple[Grid, Grid]
ProgramLearner = Callable[[list[Pair]], Optional[dict[str, Any]]]

_OUTSIDE = -1
_DEFAULT_MAX_CANDIDATES = 32
_DEFAULT_MAX_RADIUS = 2
_DEFAULT_MAX_RULES = 512


def _copy_grid(grid: Grid) -> Grid:
    return [row[:] for row in grid]


def _shape(grid: Grid) -> tuple[int, int]:
    return len(grid), len(grid[0])


def _as_grid(value: Any) -> Optional[Grid]:
    """Return a detached ARC grid, rejecting malformed/non-ARC values."""

    if not isinstance(value, list) or not value:
        return None
    width: Optional[int] = None
    result: Grid = []
    for raw_row in value:
        if not isinstance(raw_row, list) or not raw_row:
            return None
        if width is None:
            width = len(raw_row)
        elif len(raw_row) != width:
            return None
        row: list[int] = []
        for cell in raw_row:
            # bool is an int subclass, but is not an ARC color.
            if isinstance(cell, bool) or not isinstance(cell, int):
                return None
            if cell < 0 or cell > 9:
                return None
            row.append(int(cell))
        result.append(row)
    return result


def _read_task(task: Any) -> Optional[tuple[list[Pair], list[Grid]]]:
    """Read only the contractually permitted portions of a sanitized task."""

    if not isinstance(task, Mapping):
        return None
    try:
        raw_train = task["train"]
        raw_test = task["test"]
    except (KeyError, TypeError):
        return None
    if not isinstance(raw_train, Sequence) or isinstance(raw_train, (str, bytes)):
        return None
    if not isinstance(raw_test, Sequence) or isinstance(raw_test, (str, bytes)):
        return None
    if not raw_train:
        return None

    train: list[Pair] = []
    for example in raw_train:
        if not isinstance(example, Mapping):
            return None
        try:
            input_grid = _as_grid(example["input"])
            output_grid = _as_grid(example["output"])
        except (KeyError, TypeError):
            return None
        if input_grid is None or output_grid is None:
            return None
        if _shape(input_grid) != _shape(output_grid):
            return None
        train.append((input_grid, output_grid))

    tests: list[Grid] = []
    for example in raw_test:
        if not isinstance(example, Mapping):
            return None
        try:
            # Deliberately do not probe for any other field on a test example.
            input_grid = _as_grid(example["input"])
        except (KeyError, TypeError):
            return None
        if input_grid is None:
            return None
        tests.append(input_grid)
    return train, tests


def _limit(limits: Any, names: tuple[str, ...], default: int) -> int:
    value: Any = default
    if isinstance(limits, Mapping):
        for name in names:
            if name in limits:
                value = limits[name]
                break
    elif limits is not None:
        for name in names:
            if hasattr(limits, name):
                value = getattr(limits, name)
                break
    if isinstance(value, bool) or not isinstance(value, int):
        return default
    return value


def _modal_color(grid: Grid) -> int:
    counts = Counter(cell for row in grid for cell in row)
    # Favor the smaller color on a tie.  This is deterministic and is usually
    # the intended ARC background convention.
    return min(counts, key=lambda color: (-counts[color], color))


def _sparse_hist(values: Sequence[int]) -> list[list[int]]:
    counts = Counter(values)
    return [[color, counts[color]] for color in sorted(counts)]


def _patch(grid: Grid, row: int, col: int, radius: int) -> list[list[int]]:
    height, width = _shape(grid)
    patch: list[list[int]] = []
    for dr in range(-radius, radius + 1):
        patch_row: list[int] = []
        for dc in range(-radius, radius + 1):
            rr, cc = row + dr, col + dc
            patch_row.append(grid[rr][cc] if 0 <= rr < height and 0 <= cc < width else _OUTSIDE)
        patch.append(patch_row)
    return patch


def _rotate_square(square: list[list[int]]) -> list[list[int]]:
    size = len(square)
    return [[square[size - 1 - col][row] for col in range(size)] for row in range(size)]


def _mirror_square(square: list[list[int]]) -> list[list[int]]:
    return [list(reversed(row)) for row in square]


def _d4_canonical(square: list[list[int]]) -> list[int]:
    variants: list[tuple[int, ...]] = []
    current = [row[:] for row in square]
    for _ in range(4):
        variants.append(tuple(cell for row in current for cell in row))
        mirrored = _mirror_square(current)
        variants.append(tuple(cell for row in mirrored for cell in row))
        current = _rotate_square(current)
    return list(min(variants))


def _offsets(radius: int, mask: str) -> list[tuple[int, int]]:
    result: list[tuple[int, int]] = []
    for dr in range(-radius, radius + 1):
        for dc in range(-radius, radius + 1):
            if dr == 0 and dc == 0:
                continue
            include = False
            if mask == "moore":
                include = True
            elif mask == "cross":
                include = (dr == 0) != (dc == 0)
            elif mask == "diagonal":
                include = abs(dr) == abs(dc)
            elif mask == "ring":
                include = max(abs(dr), abs(dc)) == radius
            if include:
                result.append((dr, dc))
    return result


def _neighbor_values(
    grid: Grid,
    row: int,
    col: int,
    radius: int,
    mask: str,
) -> tuple[list[int], int]:
    height, width = _shape(grid)
    values: list[int] = []
    outside = 0
    for dr, dc in _offsets(radius, mask):
        rr, cc = row + dr, col + dc
        if 0 <= rr < height and 0 <= cc < width:
            values.append(grid[rr][cc])
        else:
            outside += 1
    return values, outside


def _nearest(
    grid: Grid,
    row: int,
    col: int,
    dr: int,
    dc: int,
    mode: str,
    background: int,
) -> list[int]:
    height, width = _shape(grid)
    center = grid[row][col]
    rr, cc, distance = row + dr, col + dc, 1
    while 0 <= rr < height and 0 <= cc < width:
        value = grid[rr][cc]
        if mode == "nonbackground":
            visible = value != background
        elif mode == "different":
            visible = value != center
        else:
            visible = True
        if visible:
            return [value, distance]
        rr += dr
        cc += dc
        distance += 1
    return [_OUTSIDE, 0]


def _feature_key(grid: Grid, row: int, col: int, spec: Mapping[str, Any]) -> list[Any]:
    kind = spec["kind"]
    center = grid[row][col]
    height, width = _shape(grid)

    if kind == "patch":
        radius = int(spec["radius"])
        patch = _patch(grid, row, col, radius)
        if bool(spec.get("d4", False)):
            return _d4_canonical(patch)
        return [cell for patch_row in patch for cell in patch_row]

    if kind == "color_counts":
        radius = int(spec["radius"])
        mask = str(spec["mask"])
        values, outside = _neighbor_values(grid, row, col, radius, mask)
        if spec.get("mode") == "background_relational":
            background = _modal_color(grid)
            nonbackground = [value for value in values if value != background]
            return [
                center,
                int(center == background),
                len(values),
                outside,
                sum(value == center for value in values),
                len(nonbackground),
                len(set(nonbackground)),
                _sparse_hist(nonbackground),
            ]
        return [center, len(values), outside, _sparse_hist(values)]

    if kind == "row_column":
        row_values = list(grid[row])
        column_values = [grid[rr][col] for rr in range(height)]
        edge_flags = [int(row == 0), int(row == height - 1), int(col == 0), int(col == width - 1)]
        if spec.get("mode") == "background_relational":
            background = _modal_color(grid)
            row_nonbackground = [value for value in row_values if value != background]
            col_nonbackground = [value for value in column_values if value != background]
            return [
                center,
                int(center == background),
                height,
                width,
                edge_flags,
                len(row_nonbackground),
                len(col_nonbackground),
                len(set(row_nonbackground)),
                len(set(col_nonbackground)),
                _sparse_hist(row_nonbackground),
                _sparse_hist(col_nonbackground),
            ]
        return [
            center,
            height,
            width,
            edge_flags,
            _sparse_hist(row_values),
            _sparse_hist(column_values),
        ]

    if kind == "rays":
        background = _modal_color(grid)
        mode = str(spec.get("mode", "nonbackground"))
        directions = ((0, -1), (0, 1), (-1, 0), (1, 0))
        rays = [_nearest(grid, row, col, dr, dc, mode, background) for dr, dc in directions]
        return [center, int(center == background), height, width, rays]

    raise ValueError(f"unknown feature kind: {kind}")


def _fingerprint(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True)


def _learn_feature_program(
    train: list[Pair],
    feature: Mapping[str, Any],
    max_rules: int = _DEFAULT_MAX_RULES,
) -> Optional[dict[str, Any]]:
    """Learn a consistent feature-to-color table with identity as its default."""

    observations: dict[str, tuple[list[Any], int, int]] = {}
    for input_grid, output_grid in train:
        height, width = _shape(input_grid)
        for row in range(height):
            for col in range(width):
                key = _feature_key(input_grid, row, col, feature)
                fingerprint = _fingerprint(key)
                desired = output_grid[row][col]
                center = input_grid[row][col]
                previous = observations.get(fingerprint)
                if previous is not None and previous[1] != desired:
                    return None
                observations[fingerprint] = (key, desired, center)

    rules: list[dict[str, Any]] = []
    for fingerprint in sorted(observations):
        key, desired, center = observations[fingerprint]
        if desired != center:
            rules.append({"when": key, "write": desired})
    if len(rules) > max_rules:
        return None
    program: dict[str, Any] = {
        "op": "feature_edit",
        "feature": dict(feature),
        "rules": rules,
        "default": "identity",
        "synchronous": True,
    }
    if not _program_fits(program, train):
        return None
    return program


def _ray_pair_color(grid: Grid, row: int, col: int, axis: str, background: int) -> Optional[int]:
    if axis == "horizontal":
        directions = ((0, -1), (0, 1))
    else:
        directions = ((-1, 0), (1, 0))
    hits = [_nearest(grid, row, col, dr, dc, "nonbackground", background) for dr, dc in directions]
    if all(hit[0] != _OUTSIDE for hit in hits) and hits[0][0] == hits[1][0]:
        return hits[0][0]
    return None


def _direct_value(program: Mapping[str, Any], grid: Grid, row: int, col: int) -> Optional[int]:
    op = program["op"]
    background = _modal_color(grid)
    center = grid[row][col]

    if op == "ray_fill":
        if center != background:
            return None
        horizontal = _ray_pair_color(grid, row, col, "horizontal", background)
        vertical = _ray_pair_color(grid, row, col, "vertical", background)
        axis = program["axis"]
        if axis == "horizontal":
            return horizontal
        if axis == "vertical":
            return vertical
        if axis == "either":
            choices = [value for value in (horizontal, vertical) if value is not None]
            if choices and len(set(choices)) == 1:
                return choices[0]
            return None
        if axis == "both_agree" and horizontal is not None and horizontal == vertical:
            return horizontal
        return None

    if op == "neighbor_rule":
        source = program["source"]
        if source == "background" and center != background:
            return None
        if source == "nonbackground" and center == background:
            return None
        values, _ = _neighbor_values(
            grid,
            row,
            col,
            int(program["radius"]),
            str(program["mask"]),
        )
        nonbackground = [value for value in values if value != background]
        if len(nonbackground) != int(program["count"]):
            return None
        action = program["action"]
        if action == "background":
            return background
        if not nonbackground:
            return None
        counts = Counter(nonbackground)
        if action == "unique_color":
            return next(iter(counts)) if len(counts) == 1 else None
        if action == "strict_majority_color":
            ordered = sorted(counts.items(), key=lambda item: (-item[1], item[0]))
            if len(ordered) == 1 or ordered[0][1] > ordered[1][1]:
                return ordered[0][0]
            return None
        return None

    if op == "row_column_fill":
        if center != background:
            return None
        height, width = _shape(grid)
        row_values = [grid[row][cc] for cc in range(width) if grid[row][cc] != background]
        col_values = [grid[rr][col] for rr in range(height) if grid[rr][col] != background]

        def unique_with_support(values: list[int]) -> Optional[int]:
            if len(values) < int(program["min_support"]):
                return None
            return values[0] if len(set(values)) == 1 else None

        row_color = unique_with_support(row_values)
        col_color = unique_with_support(col_values)
        axis = program["axis"]
        if axis == "row":
            return row_color
        if axis == "column":
            return col_color
        if axis == "either":
            choices = [value for value in (row_color, col_color) if value is not None]
            return choices[0] if choices and len(set(choices)) == 1 else None
        if axis == "intersection" and row_color is not None and row_color == col_color:
            return row_color
        return None

    raise ValueError(f"unknown direct program op: {op}")


def execute_program(program: Mapping[str, Any], grid: Grid) -> Grid:
    """Execute one returned program synchronously on a same-shape grid."""

    source = _as_grid(grid)
    if source is None:
        raise ValueError("grid must be a non-empty rectangular ARC color grid")
    op = program.get("op")
    if op == "identity":
        return _copy_grid(source)

    height, width = _shape(source)
    result = _copy_grid(source)
    if op == "feature_edit":
        raw_rules = program.get("rules", [])
        rule_table = {_fingerprint(rule["when"]): int(rule["write"]) for rule in raw_rules}
        feature = program["feature"]
        for row in range(height):
            for col in range(width):
                key = _fingerprint(_feature_key(source, row, col, feature))
                if key in rule_table:
                    result[row][col] = rule_table[key]
        return result

    if op in {"ray_fill", "neighbor_rule", "row_column_fill"}:
        for row in range(height):
            for col in range(width):
                value = _direct_value(program, source, row, col)
                if value is not None:
                    result[row][col] = value
        return result

    raise ValueError(f"unsupported local transducer op: {op}")


def _program_fits(program: Mapping[str, Any], train: list[Pair]) -> bool:
    return all(execute_program(program, input_grid) == output_grid for input_grid, output_grid in train)


def _change_count(train: list[Pair]) -> int:
    return sum(
        input_grid[row][col] != output_grid[row][col]
        for input_grid, output_grid in train
        for row in range(len(input_grid))
        for col in range(len(input_grid[0]))
    )


def _loo_evidence(train: list[Pair], learner: ProgramLearner) -> dict[str, Any]:
    if len(train) < 2:
        return {
            "available": False,
            "folds": 0,
            "eligible_folds": 0,
            "grid_exact": None,
            "cell_correct": None,
            "cell_total": None,
            "cell_accuracy": None,
            "all_exact": None,
        }

    grid_exact = 0
    eligible = 0
    cell_correct = 0
    cell_total = 0
    fold_exact: list[bool] = []
    for held_out in range(len(train)):
        kept = train[:held_out] + train[held_out + 1 :]
        fold_program = learner(kept)
        target_input, target_output = train[held_out]
        total = len(target_output) * len(target_output[0])
        cell_total += total
        if fold_program is None or not _program_fits(fold_program, kept):
            fold_exact.append(False)
            continue
        eligible += 1
        prediction = execute_program(fold_program, target_input)
        exact = prediction == target_output
        fold_exact.append(exact)
        grid_exact += int(exact)
        cell_correct += sum(
            prediction[row][col] == target_output[row][col]
            for row in range(len(target_output))
            for col in range(len(target_output[0]))
        )
    return {
        "available": True,
        "folds": len(train),
        "eligible_folds": eligible,
        "grid_exact": grid_exact,
        "cell_correct": cell_correct,
        "cell_total": cell_total,
        "cell_accuracy": (cell_correct / cell_total) if cell_total else 0.0,
        "all_exact": grid_exact == len(train),
        "fold_exact": fold_exact,
    }


def _candidate(
    family: str,
    program: dict[str, Any],
    train: list[Pair],
    tests: list[Grid],
    complexity: int,
    learner: ProgramLearner,
    extra_evidence: Optional[Mapping[str, Any]] = None,
) -> Optional[dict[str, Any]]:
    train_predictions = [execute_program(program, input_grid) for input_grid, _ in train]
    if any(prediction != output_grid for prediction, (_, output_grid) in zip(train_predictions, train)):
        return None
    test_predictions = [execute_program(program, grid) for grid in tests]
    evidence: dict[str, Any] = {
        "scope": "same_shape_local",
        "train_exact": True,
        "training_examples": len(train),
        "changed_cells": _change_count(train),
        "identity_default": True,
        "leave_one_demo_out": _loo_evidence(train, learner),
    }
    if extra_evidence:
        evidence.update(dict(extra_evidence))
    return {
        "family": family,
        "program": program,
        "train_outputs": train_predictions,
        "test_outputs": test_predictions,
        "complexity": int(complexity),
        "evidence": evidence,
    }


def _fixed_learner(program: dict[str, Any]) -> ProgramLearner:
    def learn(train: list[Pair]) -> Optional[dict[str, Any]]:
        return program if _program_fits(program, train) else None

    return learn


def _feature_learner(feature: dict[str, Any], max_rules: int) -> ProgramLearner:
    def learn(train: list[Pair]) -> Optional[dict[str, Any]]:
        return _learn_feature_program(train, feature, max_rules=max_rules)

    return learn


def _direct_programs() -> list[tuple[str, dict[str, Any], int]]:
    result: list[tuple[str, dict[str, Any], int]] = []

    for axis in ("horizontal", "vertical", "either", "both_agree"):
        program = {
            "op": "ray_fill",
            "axis": axis,
            "background": "modal_per_grid",
            "default": "identity",
            "synchronous": True,
        }
        result.append((f"local.ray_predicate.{axis}", program, 5 if axis in {"horizontal", "vertical"} else 7))

    for axis in ("row", "column", "either", "intersection"):
        for min_support in (1, 2):
            program = {
                "op": "row_column_fill",
                "axis": axis,
                "min_support": min_support,
                "background": "modal_per_grid",
                "default": "identity",
                "synchronous": True,
            }
            result.append((f"local.row_column_predicate.{axis}.s{min_support}", program, 6 + min_support))

    for mask in ("cross", "diagonal", "moore"):
        maximum = len(_offsets(1, mask))
        for count in range(maximum + 1):
            for action in ("unique_color", "strict_majority_color"):
                program = {
                    "op": "neighbor_rule",
                    "source": "background",
                    "radius": 1,
                    "mask": mask,
                    "count": count,
                    "action": action,
                    "background": "modal_per_grid",
                    "default": "identity",
                    "synchronous": True,
                }
                result.append((f"local.color_count_predicate.{mask}.n{count}.{action}", program, 7 + count))
        for count in range(maximum + 1):
            program = {
                "op": "neighbor_rule",
                "source": "nonbackground",
                "radius": 1,
                "mask": mask,
                "count": count,
                "action": "background",
                "background": "modal_per_grid",
                "default": "identity",
                "synchronous": True,
            }
            result.append((f"local.color_count_predicate.{mask}.erase_n{count}", program, 7 + count))
    return result


def _rank(candidate: Mapping[str, Any]) -> tuple[Any, ...]:
    loo = candidate["evidence"]["leave_one_demo_out"]
    all_exact = loo.get("all_exact") is True
    grid_exact = loo.get("grid_exact") or 0
    folds = loo.get("folds") or 0
    cell_correct = loo.get("cell_correct") or 0
    cell_total = loo.get("cell_total") or 0
    grid_rate = grid_exact / folds if folds else -1.0
    cell_rate = cell_correct / cell_total if cell_total else -1.0
    return (
        -int(all_exact),
        -grid_rate,
        -cell_rate,
        int(candidate["complexity"]),
        str(candidate["family"]),
        _fingerprint(candidate["program"]),
    )


def compile_task(task: Any, limits: Any = None) -> list[dict[str, Any]]:
    """Compile exact, conservative local candidates for one sanitized ARC task.

    ``limits`` may be a mapping or simple attribute object.  Recognized values
    are ``max_candidates``/``candidate_cap``, ``max_radius``, and ``max_rules``.
    Candidate generation, ranking, behavior deduplication, and truncation are
    deterministic.
    """

    parsed = _read_task(task)
    if parsed is None:
        return []
    train, tests = parsed
    max_candidates = max(0, min(128, _limit(limits, ("max_candidates", "candidate_cap"), _DEFAULT_MAX_CANDIDATES)))
    max_radius = max(0, min(4, _limit(limits, ("max_radius",), _DEFAULT_MAX_RADIUS)))
    max_rules = max(0, min(4096, _limit(limits, ("max_rules",), _DEFAULT_MAX_RULES)))
    if max_candidates == 0:
        return []

    candidates: list[dict[str, Any]] = []

    identity = {
        "op": "identity",
        "default": "identity",
        "synchronous": True,
    }
    if _program_fits(identity, train):
        candidate = _candidate(
            "local.identity",
            identity,
            train,
            tests,
            0,
            _fixed_learner(identity),
            {"rule_count": 0},
        )
        if candidate is not None:
            candidates.append(candidate)

    # Fixed relational predicates are intentionally considered before learned
    # tables.  When they fit, their LOO evidence is genuinely hypothesis-level.
    for family, program, complexity in _direct_programs():
        if not _program_fits(program, train):
            continue
        candidate = _candidate(
            family,
            program,
            train,
            tests,
            complexity,
            _fixed_learner(program),
            {"rule_count": 1, "hypothesis_fixed_before_data": True},
        )
        if candidate is not None:
            candidates.append(candidate)

    feature_specs: list[tuple[str, dict[str, Any], int]] = []
    for radius in range(max_radius + 1):
        exact = {"kind": "patch", "radius": radius, "d4": False, "padding": "outside_sentinel"}
        feature_specs.append((f"local.exact_patch.r{radius}", exact, 10 + (2 * radius + 1) ** 2))
        if radius > 0:
            canonical = {"kind": "patch", "radius": radius, "d4": True, "padding": "outside_sentinel"}
            feature_specs.append((f"local.d4_canonical_patch.r{radius}", canonical, 13 + (2 * radius + 1) ** 2))

    for radius in range(1, max_radius + 1):
        for mask in ("cross", "diagonal", "moore", "ring"):
            for mode in ("absolute", "background_relational"):
                feature = {"kind": "color_counts", "radius": radius, "mask": mask, "mode": mode}
                feature_specs.append((f"local.color_count.{mask}.r{radius}.{mode}", feature, 12 + radius * 3))

    for mode in ("absolute", "background_relational"):
        feature = {"kind": "row_column", "mode": mode}
        feature_specs.append((f"local.row_column_lookup.{mode}", feature, 16))
    for mode in ("nonbackground", "different"):
        feature = {"kind": "rays", "mode": mode}
        feature_specs.append((f"local.ray_lookup.{mode}", feature, 17))

    for family, feature, base_complexity in feature_specs:
        program = _learn_feature_program(train, feature, max_rules=max_rules)
        if program is None:
            continue
        rule_count = len(program["rules"])
        # Empty learned tables are just verbose identity programs.
        if rule_count == 0:
            continue
        learner = _feature_learner(feature, max_rules)
        candidate = _candidate(
            family,
            program,
            train,
            tests,
            base_complexity + 2 * rule_count,
            learner,
            {
                "rule_count": rule_count,
                "feature": dict(feature),
                "identity_default_on_unseen_features": True,
            },
        )
        if candidate is not None:
            candidates.append(candidate)

    # First select the best-supported/simple representative of an identical
    # test behavior, then impose the deterministic cap.
    candidates.sort(key=_rank)
    deduplicated: list[dict[str, Any]] = []
    seen_behaviors: set[str] = set()
    for candidate in candidates:
        behavior = _fingerprint(candidate["test_outputs"])
        if behavior in seen_behaviors:
            continue
        seen_behaviors.add(behavior)
        deduplicated.append(candidate)
        if len(deduplicated) >= max_candidates:
            break
    return deduplicated


__all__ = ["compile_task", "execute_program"]
