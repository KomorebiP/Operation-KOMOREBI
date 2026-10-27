"""Palette-role transduction entrant for PR-LASM Block 13.

The compiler induces whole-grid color substitutions from demonstrations using
structural roles (frequency, first occurrence, sorted order, shared literals)
and, as a deliberately lower-confidence arm, exact input-palette contexts.
Only exact demonstration replays are emitted.
"""

from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
import hashlib
import itertools
import json
from typing import Any, Callable, Mapping, Sequence

import numpy as np


Grid = list[list[int]]


@dataclass(frozen=True)
class Limits:
    max_side: int = 30
    max_programs: int = 64
    max_expression_products: int = 512

    @classmethod
    def from_value(cls, value: Mapping[str, Any] | None) -> "Limits":
        if value is None:
            return cls()
        return cls(
            max_side=int(value.get("max_side", cls.max_side)),
            max_programs=int(value.get("max_programs", cls.max_programs)),
            max_expression_products=int(
                value.get("max_expression_products", cls.max_expression_products)
            ),
        )


def _grid(value: Any, limits: Limits) -> np.ndarray:
    array = np.asarray(value)
    if array.ndim != 2 or array.size == 0:
        raise ValueError("invalid grid")
    if max(array.shape) > limits.max_side or array.dtype.kind not in {"i", "u"}:
        raise ValueError("grid outside declared domain")
    array = array.astype(np.int16, copy=True)
    if np.any(array < 0) or np.any(array > 9):
        raise ValueError("invalid ARC color")
    return array


def _plain(array: np.ndarray) -> Grid:
    return [[int(value) for value in row] for row in array.tolist()]


def _palette(array: np.ndarray) -> tuple[int, ...]:
    return tuple(sorted(int(value) for value in np.unique(array)))


def _counts(array: np.ndarray) -> Counter[int]:
    return Counter(int(value) for value in array.flat)


def _first_order(array: np.ndarray) -> tuple[int, ...]:
    seen: list[int] = []
    for value in array.flat:
        color = int(value)
        if color not in seen:
            seen.append(color)
    return tuple(seen)


def _frequency_order(array: np.ndarray, *, descending: bool) -> tuple[int, ...]:
    counts = _counts(array)
    return tuple(
        sorted(counts, key=lambda color: ((-counts[color] if descending else counts[color]), color))
    )


def _mode(array: np.ndarray) -> int:
    return _frequency_order(array, descending=True)[0]


def _uniform_mapping(source: np.ndarray, target: np.ndarray) -> dict[int, int] | None:
    if source.shape != target.shape:
        return None
    mapping: dict[int, int] = {}
    for before, after in zip(source.flat, target.flat):
        before, after = int(before), int(after)
        if before in mapping and mapping[before] != after:
            return None
        mapping[before] = after
    return mapping


def _key_schemes(shared_literals: Sequence[int]) -> list[tuple[str, Callable[[np.ndarray, int], Any]]]:
    schemes: list[tuple[str, Callable[[np.ndarray, int], Any]]] = [
        ("literal", lambda grid, color: color),
        ("frequency_ascending", lambda grid, color: _frequency_order(grid, descending=False).index(color)),
        ("frequency_descending", lambda grid, color: _frequency_order(grid, descending=True).index(color)),
        ("first_occurrence", lambda grid, color: _first_order(grid).index(color)),
        ("sorted_palette", lambda grid, color: _palette(grid).index(color)),
        ("mode_binary", lambda grid, color: int(color == _mode(grid))),
        ("literal_palette", lambda grid, color: (_palette(grid), color)),
        (
            "palette_frequency",
            lambda grid, color: (_palette(grid), _frequency_order(grid, descending=True).index(color)),
        ),
    ]
    for literal in shared_literals:
        schemes.extend(
            [
                (
                    f"literal_{literal}_else_frequency_descending",
                    lambda grid, color, literal=literal: (
                        "literal" if color == literal else "other",
                        0 if color == literal else _frequency_order(grid, descending=True).index(color),
                    ),
                ),
                (
                    f"literal_{literal}_else_frequency_ascending",
                    lambda grid, color, literal=literal: (
                        "literal" if color == literal else "other",
                        0 if color == literal else _frequency_order(grid, descending=False).index(color),
                    ),
                ),
            ]
        )
    return schemes


def _selectors(
    maximum_palette: int,
    shared_literals: Sequence[int],
) -> list[tuple[dict[str, Any], Callable[[np.ndarray], int]]]:
    selectors: list[tuple[dict[str, Any], Callable[[np.ndarray], int]]] = []
    for color in range(10):
        selectors.append(({"kind": "literal", "color": color}, lambda grid, color=color: color))
    selectors.extend(
        [
            ({"kind": "mode"}, _mode),
            ({"kind": "minimum_color"}, lambda grid: min(_palette(grid))),
            ({"kind": "maximum_color"}, lambda grid: max(_palette(grid))),
        ]
    )
    for index in range(maximum_palette):
        selectors.extend(
            [
                (
                    {"kind": "frequency_descending", "index": index},
                    lambda grid, index=index: _frequency_order(grid, descending=True)[index],
                ),
                (
                    {"kind": "frequency_ascending", "index": index},
                    lambda grid, index=index: _frequency_order(grid, descending=False)[index],
                ),
                (
                    {"kind": "first_occurrence", "index": index},
                    lambda grid, index=index: _first_order(grid)[index],
                ),
                (
                    {"kind": "sorted_palette", "index": index},
                    lambda grid, index=index: _palette(grid)[index],
                ),
            ]
        )
    for literal in shared_literals:
        selectors.append(
            (
                {"kind": "unique_other_than_literal", "literal": int(literal)},
                lambda grid, literal=literal: next(
                    color for color in _palette(grid) if color != literal
                )
                if len([color for color in _palette(grid) if color != literal]) == 1
                else (_ for _ in ()).throw(IndexError("not a unique other color")),
            )
        )
    return selectors


def _resolve_selector(record: Mapping[str, Any], grid: np.ndarray) -> int:
    kind = str(record["kind"])
    if kind == "literal":
        return int(record["color"])
    if kind == "mode":
        return _mode(grid)
    if kind == "minimum_color":
        return min(_palette(grid))
    if kind == "maximum_color":
        return max(_palette(grid))
    if kind == "unique_other_than_literal":
        literal = int(record["literal"])
        others = [color for color in _palette(grid) if color != literal]
        if len(others) != 1:
            raise ValueError("not a unique other color")
        return others[0]
    index = int(record["index"])
    if kind == "frequency_descending":
        return _frequency_order(grid, descending=True)[index]
    if kind == "frequency_ascending":
        return _frequency_order(grid, descending=False)[index]
    if kind == "first_occurrence":
        return _first_order(grid)[index]
    if kind == "sorted_palette":
        return _palette(grid)[index]
    raise ValueError("unknown selector")


def _execute(
    grid: np.ndarray,
    key_function: Callable[[np.ndarray, int], Any],
    expressions: Mapping[str, Mapping[str, Any]],
) -> np.ndarray:
    output = grid.copy()
    for color in _palette(grid):
        key = repr(key_function(grid, color))
        expression = expressions.get(key)
        if expression is None:
            output[grid == color] = color
            continue
        try:
            target = _resolve_selector(expression, grid)
        except (IndexError, KeyError, TypeError, ValueError):
            raise ValueError("selector outside test palette")
        output[grid == color] = target
    return output


def _behavior_hash(outputs: Sequence[np.ndarray]) -> str:
    payload = json.dumps([_plain(array) for array in outputs], separators=(",", ":"))
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def _selector_preference(record: Mapping[str, Any]) -> int:
    """MDL-style stability cost used only to order demo-equivalent programs.

    Palette-relative selectors are preferred when they state an invariant
    (minimum/maximum/sorted role or the sole non-literal color).  Frequency and
    raster-order ties are weaker because a differently sized test instance can
    reverse them despite an exact demonstration replay.
    """

    kind = str(record.get("kind", ""))
    return {
        "unique_other_than_literal": 0,
        "minimum_color": 1,
        "maximum_color": 1,
        "sorted_palette": 1,
        "literal": 2,
        "frequency_ascending": 3,
        "frequency_descending": 3,
        "mode": 3,
        "first_occurrence": 4,
    }.get(kind, 9)


def compile_task(task: Mapping[str, Any], limits: Mapping[str, Any] | None = None) -> list[dict[str, Any]]:
    bounds = Limits.from_value(limits)
    if not isinstance(task, Mapping):
        return []
    try:
        train = [(_grid(example["input"], bounds), _grid(example["output"], bounds)) for example in task["train"]]
        tests = [_grid(example["input"], bounds) for example in task["test"]]
    except (KeyError, TypeError, ValueError):
        return []
    if not train or not tests:
        return []
    mappings = [_uniform_mapping(source, target) for source, target in train]
    if any(mapping is None for mapping in mappings):
        return []
    typed_mappings = [mapping for mapping in mappings if mapping is not None]
    shared_literals = sorted(
        set.intersection(*(set(_palette(source)) for source, _ in train))
    )
    maximum_palette = max(len(_palette(source)) for source, _ in train + [(test, test) for test in tests])
    selectors = _selectors(maximum_palette, shared_literals)
    proposals: list[dict[str, Any]] = []

    for scheme_name, key_function in _key_schemes(shared_literals):
        observations: dict[str, list[tuple[np.ndarray, int]]] = {}
        valid = True
        for (source, _), mapping in zip(train, typed_mappings):
            for color, target in mapping.items():
                try:
                    key = repr(key_function(source, color))
                except (IndexError, ValueError):
                    valid = False
                    break
                observations.setdefault(key, []).append((source, target))
            if not valid:
                break
        if not valid:
            continue
        choices: list[tuple[str, list[dict[str, Any]]]] = []
        for key in sorted(observations):
            compatible: list[dict[str, Any]] = []
            for selector_record, selector in selectors:
                try:
                    if all(int(selector(source)) == int(target) for source, target in observations[key]):
                        compatible.append(selector_record)
                except IndexError:
                    continue
            compatible = sorted(compatible, key=lambda record: (0 if record["kind"] != "literal" else 1, json.dumps(record, sort_keys=True)))
            if not compatible:
                valid = False
                break
            choices.append((key, compatible[:3]))
        if not valid:
            continue
        products = itertools.product(*(options for _, options in choices))
        for product_index, product in enumerate(products):
            if product_index >= bounds.max_expression_products:
                break
            expressions = {key: expression for (key, _), expression in zip(choices, product)}
            try:
                train_outputs = [_execute(source, key_function, expressions) for source, _ in train]
                if not all(np.array_equal(prediction, target) for prediction, (_, target) in zip(train_outputs, train)):
                    continue
                test_outputs = [_execute(test, key_function, expressions) for test in tests]
            except ValueError:
                continue
            dynamic_count = sum(expression["kind"] != "literal" for expression in expressions.values())
            selector_stability_cost = sum(
                _selector_preference(expression) for expression in expressions.values()
            )
            if "_else_" in scheme_name:
                # A shared literal plus a role for every other color is more
                # compact and more transferable than enumerating each observed
                # literal independently.
                key_stability_cost = 0
            else:
                key_stability_cost = {
                    "literal": 0,
                    "frequency_ascending": 1,
                    "frequency_descending": 1,
                    "first_occurrence": 2,
                    "sorted_palette": 1,
                    "mode_binary": 2,
                    "literal_palette": 3,
                    "palette_frequency": 4,
                }.get(scheme_name, 2)
            program = {
                "operator": "palette_role_substitution",
                "key_scheme": scheme_name,
                "expressions": expressions,
                "unseen_key": "identity",
            }
            proposals.append(
                {
                    "family": "palette_roles",
                    "program": program,
                    "train_outputs": [_plain(array) for array in train_outputs],
                    "test_outputs": [_plain(array) for array in test_outputs],
                    "complexity": 3 + len(expressions) + sum(1 for expression in expressions.values() if expression["kind"] == "literal"),
                    "evidence": {
                        "all_demonstrations_exact": True,
                        "uniform_per_source_color": True,
                        "demonstration_permutation_invariant": True,
                        "dynamic_expression_count": dynamic_count,
                        "palette_contextual": "palette" in scheme_name,
                        "selector_stability_cost": selector_stability_cost,
                        "key_stability_cost": key_stability_cost,
                    },
                }
            )

    proposals.sort(
        key=lambda candidate: (
            candidate["evidence"]["palette_contextual"],
            candidate["evidence"]["selector_stability_cost"]
            + candidate["evidence"]["key_stability_cost"],
            candidate["evidence"]["key_stability_cost"],
            -candidate["evidence"]["dynamic_expression_count"],
            candidate["complexity"],
            json.dumps(candidate["program"], sort_keys=True),
        )
    )
    seen: set[str] = set()
    output: list[dict[str, Any]] = []
    for candidate in proposals:
        behavior = _behavior_hash([np.asarray(grid, dtype=np.int16) for grid in candidate["test_outputs"]])
        if behavior in seen:
            continue
        seen.add(behavior)
        candidate["evidence"]["behavior_hash"] = behavior
        output.append(candidate)
        if len(output) >= bounds.max_programs:
            break
    return output


__all__ = ["Limits", "compile_task"]
