"""Inherited exact-fit core-search entrant for the Block 13 tournament.

This adapter exposes the existing :mod:`komorebi_arc2.entry` proposal
portfolio through the deliberately small Block 13 entrant contract.  It sees
only demonstrations and test inputs, retains candidates whose *recorded*
training executions exactly replay every demonstration, and ranks complete
multi-test behaviors with the inherited legacy MDL/vote rule.

The adapter never calls submission, solution, scoring, task-identity, or
production runner APIs.  Its ``program`` field is a JSON-safe receipt for an
already-executed inherited candidate; it is not an alternate execution path.

Author: Komorebi P.
"""

from __future__ import annotations

from collections import defaultdict
from collections.abc import Mapping, Sequence
import json
import math
from typing import Any

import numpy as np

from komorebi_arc2 import entry as _core


Grid = list[list[int]]

_DEFAULT_TIME_LIMIT = 2.0
_DEFAULT_MAX_PROGRAMS = 36
_MAX_TIME_LIMIT = 30.0
_MAX_PROGRAMS = 256


def _grid(value: Any) -> np.ndarray | None:
    """Validate and detach one ARC grid without using the core sanitizer.

    The inherited sanitizer intentionally repairs malformed values for its
    public solver fallback.  A tournament entrant should instead fail closed,
    so validation happens before conversion to the inherited array type.
    """

    if not isinstance(value, list) or not value or len(value) > 30:
        return None
    if not all(isinstance(row, list) and row for row in value):
        return None
    width = len(value[0])
    if width > 30 or any(len(row) != width for row in value):
        return None
    result: list[list[int]] = []
    for row in value:
        converted: list[int] = []
        for cell in row:
            if isinstance(cell, bool) or not isinstance(cell, int) or not 0 <= cell <= 9:
                return None
            converted.append(int(cell))
        result.append(converted)
    return np.asarray(result, dtype=np.int16)


def _read_task(task: Any) -> tuple[list[tuple[np.ndarray, np.ndarray]], list[np.ndarray]] | None:
    """Read exactly the fields permitted by the sanitized entrant boundary."""

    if not isinstance(task, Mapping):
        return None
    try:
        raw_train = task["train"]
        raw_test = task["test"]
    except (KeyError, TypeError):
        return None
    if (
        not isinstance(raw_train, Sequence)
        or isinstance(raw_train, (str, bytes))
        or not raw_train
        or not isinstance(raw_test, Sequence)
        or isinstance(raw_test, (str, bytes))
        or not raw_test
    ):
        return None

    train: list[tuple[np.ndarray, np.ndarray]] = []
    for example in raw_train:
        if not isinstance(example, Mapping):
            return None
        try:
            source = _grid(example["input"])
            target = _grid(example["output"])
        except (KeyError, TypeError):
            return None
        if source is None or target is None:
            return None
        train.append((source, target))

    tests: list[np.ndarray] = []
    for example in raw_test:
        if not isinstance(example, Mapping):
            return None
        try:
            # Do not use ``get`` or enumerate keys: only this field is allowed.
            source = _grid(example["input"])
        except (KeyError, TypeError):
            return None
        if source is None:
            return None
        tests.append(source)
    return train, tests


def _limit(limits: Any, names: tuple[str, ...], default: Any) -> Any:
    if isinstance(limits, Mapping):
        for name in names:
            if name in limits:
                return limits[name]
    elif limits is not None:
        for name in names:
            if hasattr(limits, name):
                return getattr(limits, name)
    return default


def _time_limit(limits: Any) -> float:
    value = _limit(limits, ("time_limit", "time_limit_seconds"), _DEFAULT_TIME_LIMIT)
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        return _DEFAULT_TIME_LIMIT
    seconds = float(value)
    if not math.isfinite(seconds):
        return _DEFAULT_TIME_LIMIT
    return max(0.0, min(_MAX_TIME_LIMIT, seconds))


def _program_cap(limits: Any) -> int:
    """Resolve both tournament and entrant-local spellings conservatively."""

    explicit = _limit(limits, ("max_programs",), None)
    tournament = _limit(limits, ("max_candidates", "candidate_cap"), None)
    values: list[int] = []
    # ``max_programs`` is the entrant's requested behavior budget.  Without it
    # retain the conservative local default, then intersect either choice with
    # the harness-wide candidate cap when one is explicitly supplied.
    primary = explicit
    if isinstance(primary, bool) or not isinstance(primary, int):
        primary = _DEFAULT_MAX_PROGRAMS
    for value in (primary, tournament):
        if value is None:
            continue
        if isinstance(value, bool) or not isinstance(value, int):
            continue
        values.append(value)
    if not values:
        return _DEFAULT_MAX_PROGRAMS
    return max(0, min(_MAX_PROGRAMS, min(values)))


def _plain_grid(value: Any) -> Grid | None:
    """Return a strict JSON grid for an inherited execution result."""

    array = np.asarray(value)
    if array.ndim != 2 or array.size == 0 or max(array.shape) > 30:
        return None
    if array.dtype.kind not in {"i", "u"}:
        return None
    if np.any(array < 0) or np.any(array > 9):
        return None
    return [[int(cell) for cell in row] for row in array.tolist()]


def _canonical(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def _exact_candidate(
    candidate: Any,
    train: Sequence[tuple[np.ndarray, np.ndarray]],
    test_count: int,
) -> tuple[list[Grid], list[Grid]] | None:
    """Validate exact replay from candidate executions, not error metadata alone."""

    if not isinstance(candidate, _core.RuleCandidate):
        return None
    if int(candidate.train_error) != 0:
        return None
    if len(candidate.train_grids) != len(train) or len(candidate.grids) != test_count:
        return None

    train_outputs: list[Grid] = []
    for prediction, (_, target) in zip(candidate.train_grids, train):
        plain = _plain_grid(prediction)
        if plain is None:
            return None
        predicted_array = np.asarray(plain, dtype=np.int16)
        if predicted_array.shape != target.shape or not np.array_equal(predicted_array, target):
            return None
        train_outputs.append(plain)

    test_outputs: list[Grid] = []
    for prediction in candidate.grids:
        plain = _plain_grid(prediction)
        if plain is None:
            return None
        test_outputs.append(plain)
    return train_outputs, test_outputs


def _representative_key(candidate: _core.RuleCandidate) -> tuple[Any, ...]:
    # Equal-MDL ties are resolved without relying on generator insertion order.
    return (
        max(0, int(candidate.complexity)),
        str(candidate.family),
        str(candidate.name),
    )


def compile_task(task: Any, limits: Any = None) -> list[dict[str, Any]]:
    """Compile deterministic exact-fit inherited candidates.

    Candidates are grouped by their complete tuple of test predictions.  For
    each behavior the lowest-complexity program is its representative, while
    all exact aliases contribute votes and distinct-family support.  The rank
    is exactly the integer-scaled form of ``legacy_rank_predictions`` for
    zero-training-error candidates::

        100 * score = complexity - 2 * votes - 3 * distinct_families

    Thus ``max_programs=1`` chooses a principled inherited MDL/vote winner and
    never consults a hidden target.
    """

    parsed = _read_task(task)
    cap = _program_cap(limits)
    if parsed is None or cap == 0:
        return []
    train, tests = parsed
    seconds = _time_limit(limits)

    try:
        raw_candidates = _core.collect_candidates(train, tests, time_limit=seconds)
        candidates = _core.admissible_candidates(
            _core.deduplicate_candidates(raw_candidates)
        )
    except Exception:
        # Entrants are optional challengers.  Any inherited compiler failure is
        # a local abstention, never permission to emit repaired or partial data.
        return []

    groups: dict[str, list[tuple[_core.RuleCandidate, list[Grid], list[Grid]]]] = defaultdict(list)
    for candidate in candidates:
        validated = _exact_candidate(candidate, train, len(tests))
        if validated is None:
            continue
        train_outputs, test_outputs = validated
        groups[_canonical(test_outputs)].append((candidate, train_outputs, test_outputs))

    exact_program_count = sum(len(group) for group in groups.values())
    records: list[tuple[tuple[Any, ...], dict[str, Any]]] = []
    for behavior_key, aliases in groups.items():
        aliases.sort(key=lambda item: _representative_key(item[0]))
        representative, train_outputs, test_outputs = aliases[0]
        votes = len(aliases)
        family_count = len({str(item[0].family) for item in aliases})
        complexity = max(0, int(representative.complexity))
        rank_numerator = complexity - 2 * votes - 3 * family_count
        family = str(representative.family).strip() or "unclassified"
        name = str(representative.name)
        body = {
            "family": f"core_search.{family}",
            "program": {
                "op": "inherited_core_exact_fit",
                "name": name,
                "source_family": family,
                "selector": "legacy_mdl_vote_complete_behavior",
                "nominal_time_limit_seconds": seconds,
            },
            "train_outputs": train_outputs,
            "test_outputs": test_outputs,
            "complexity": complexity,
            "evidence": {
                "all_demos_exact": True,
                "exact_replay": True,
                "replay_source": "recorded_inherited_candidate_executions",
                "admissibility_checked": True,
                "behavior_alias_votes": votes,
                "distinct_family_votes": family_count,
                "legacy_rank_numerator_centipoints": rank_numerator,
                "exact_program_count": exact_program_count,
                "exact_behavior_count": len(groups),
                "selection_is_label_free": True,
            },
        }
        # Match the inherited legacy ordering after scaling away floating point:
        # (rank score, train error=0, best complexity, -votes, canonical grid).
        rank = (rank_numerator, 0, complexity, -votes, behavior_key)
        records.append((rank, body))

    records.sort(key=lambda item: item[0])
    return [body for _, body in records[:cap]]


__all__ = ["compile_task"]
