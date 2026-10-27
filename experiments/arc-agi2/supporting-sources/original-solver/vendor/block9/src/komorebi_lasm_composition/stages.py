"""Deterministic primitive stages and versioned endpoint leaves.

This module is deliberately task-ID blind.  Atomic proposals are derived only
from the current demonstration states, their targets, and a finite proposal
budget.  Endpoint proposals additionally require explicit, hash-verified Block
7 and Block 8 runtime-bank records; no packaged default bank is loaded here.

The inherited Block 6 and Block 8 compilers are endpoint recognizers.  They are
therefore exposed only by :func:`propose_endpoint_closers`.  The atomic registry
is the partial-stage interface used by recursive composition search.
"""
from __future__ import annotations

from collections import Counter, deque
from dataclasses import dataclass
from types import MappingProxyType
from typing import Any, Callable, Iterable, Mapping, Sequence
import json

import numpy as np

from komorebi_lasm_compiler.common import freeze as inherited_freeze
from komorebi_lasm_compiler.execution import execute_compiled
from komorebi_lasm_compiler.model import canonical_json, canonical_value, sha256_record
from komorebi_lasm_synthesis.families import (
    DEFINITIONS as BLOCK8_DEFINITIONS,
    DEFINITION_BY_NAME as BLOCK8_DEFINITION_BY_NAME,
    execute_family as execute_block8_family,
)

from .model import LeafInvocation, validate_grid


Grid = tuple[tuple[int, ...], ...]
ParameterValidator = Callable[[Mapping[str, Any]], None]
AtomicExecutor = Callable[[Grid, Mapping[str, Any]], Grid]

ARC_MIN_COLOR = 0
ARC_MAX_COLOR = 9
ARC_MAX_SIDE = 30
HARD_PROPOSAL_CAP = 512


# ---------------------------------------------------------------------------
# Small validation helpers
# ---------------------------------------------------------------------------


def _grid(value: Any) -> Grid:
    """Validate and freeze one ARC grid, tolerating either validator API style."""
    checked = validate_grid(value)
    # ``validate_grid`` is allowed to be an assertion-style validator or a
    # normalizer.  Supporting both keeps this leaf layer independent of that
    # implementation detail while retaining its checks.
    candidate = value if checked is None or checked is True else checked
    frozen = inherited_freeze(candidate)
    if not frozen or not frozen[0]:
        raise ValueError("grid must be nonempty")
    width = len(frozen[0])
    if len(frozen) > ARC_MAX_SIDE or width > ARC_MAX_SIDE:
        raise ValueError("ARC grids may not exceed 30 by 30")
    if any(len(row) != width for row in frozen):
        raise ValueError("grid rows must have equal length")
    if any(not ARC_MIN_COLOR <= value <= ARC_MAX_COLOR for row in frozen for value in row):
        raise ValueError("ARC colors must be integers from 0 through 9")
    return frozen


def _array(value: Any) -> np.ndarray:
    return np.asarray(_grid(value), dtype=np.int16)


def _output(value: Any) -> Grid:
    return _grid(value)


def _exact_keys(parameters: Mapping[str, Any], required: Iterable[str]) -> None:
    if not isinstance(parameters, Mapping):
        raise TypeError("stage parameters must be a mapping")
    expected = set(required)
    actual = {str(key) for key in parameters}
    if actual != expected:
        missing = sorted(expected - actual)
        extra = sorted(actual - expected)
        raise ValueError(f"parameter keys differ from schema; missing={missing}, extra={extra}")


def _is_int(value: Any) -> bool:
    return isinstance(value, (int, np.integer)) and not isinstance(value, (bool, np.bool_))


def _integer(value: Any, name: str, minimum: int, maximum: int) -> int:
    if not _is_int(value):
        raise TypeError(f"{name} must be an integer")
    result = int(value)
    if not minimum <= result <= maximum:
        raise ValueError(f"{name} must be between {minimum} and {maximum}")
    return result


def _color(value: Any, name: str = "color") -> int:
    return _integer(value, name, ARC_MIN_COLOR, ARC_MAX_COLOR)


def _choice(value: Any, name: str, choices: Iterable[str]) -> str:
    allowed = tuple(choices)
    if not isinstance(value, str) or value not in allowed:
        raise ValueError(f"{name} must be one of {allowed!r}")
    return value


def _bool(value: Any, name: str) -> bool:
    if not isinstance(value, (bool, np.bool_)):
        raise TypeError(f"{name} must be Boolean")
    return bool(value)


def _factor(value: Any) -> tuple[int, int]:
    if not isinstance(value, (list, tuple)) or len(value) != 2:
        raise TypeError("factor must be a two-element sequence")
    fy = _integer(value[0], "factor[0]", 1, 15)
    fx = _integer(value[1], "factor[1]", 1, 15)
    if fy * fx <= 1:
        raise ValueError("at least one scale factor must exceed one")
    return fy, fx


def _recolor_pairs(value: Any) -> tuple[tuple[int, int], ...]:
    if not isinstance(value, (list, tuple)):
        raise TypeError("recolor must be a sequence")
    pairs: list[tuple[int, int]] = []
    seen: set[int] = set()
    for index, pair in enumerate(value):
        if not isinstance(pair, (list, tuple)) or len(pair) != 2:
            raise TypeError(f"recolor[{index}] must be a two-element sequence")
        source = _color(pair[0], f"recolor[{index}][0]")
        target = _color(pair[1], f"recolor[{index}][1]")
        if source in seen:
            raise ValueError("recolor sources must be unique")
        seen.add(source)
        pairs.append((source, target))
    return tuple(pairs)


_D4_NAMES = (
    "id", "r90", "r180", "r270", "fliplr", "flipud", "transpose", "anti_transpose",
)
_ROLE_NAMES = (
    "most", "corner", "zero", "background", "most_foreground",
    "rarest_foreground", "unique_foreground",
)


def _validate_role(role: Any, name: str) -> str:
    if not isinstance(role, str):
        raise TypeError(f"{name} must be a role string")
    if role in _ROLE_NAMES:
        return role
    for prefix in ("literal:", "color:"):
        if role.startswith(prefix):
            suffix = role[len(prefix):]
            if suffix.isdigit() and ARC_MIN_COLOR <= int(suffix) <= ARC_MAX_COLOR:
                return role
    raise ValueError(f"unsupported {name} {role!r}")


def _resolve_role(grid: np.ndarray, role: str) -> int:
    role = _validate_role(role, "role")
    if role.startswith("literal:") or role.startswith("color:"):
        return int(role.split(":", 1)[1])
    counts = Counter(int(value) for value in grid.ravel())
    if role == "zero":
        return 0
    if role in {"most", "background"}:
        maximum = max(counts.values())
        winners = sorted(color for color, count in counts.items() if count == maximum)
        if len(winners) != 1:
            raise ValueError("most-common role is ambiguous")
        return winners[0]
    if role == "corner":
        corners = Counter((int(grid[0, 0]), int(grid[0, -1]), int(grid[-1, 0]), int(grid[-1, -1])))
        maximum = max(corners.values())
        winners = sorted(color for color, count in corners.items() if count == maximum)
        if len(winners) != 1:
            raise ValueError("corner role is ambiguous")
        return winners[0]
    background = _resolve_role(grid, "most")
    foreground = {color: count for color, count in counts.items() if color != background}
    if not foreground:
        raise ValueError("foreground role is unavailable on a uniform grid")
    if role == "unique_foreground":
        if len(foreground) != 1:
            raise ValueError("unique-foreground role is ambiguous")
        return next(iter(foreground))
    desired = max(foreground.values()) if role == "most_foreground" else min(foreground.values())
    winners = sorted(color for color, count in foreground.items() if count == desired)
    if len(winners) != 1:
        raise ValueError(f"{role} role is ambiguous")
    return winners[0]


# ---------------------------------------------------------------------------
# Atomic parameter schemas
# ---------------------------------------------------------------------------


def _validate_d4(parameters: Mapping[str, Any]) -> None:
    _exact_keys(parameters, ("transform",))
    _choice(parameters["transform"], "transform", _D4_NAMES)


def _validate_crop(parameters: Mapping[str, Any]) -> None:
    _exact_keys(parameters, ("background",))
    _color(parameters["background"], "background")


def _validate_empty(parameters: Mapping[str, Any]) -> None:
    _exact_keys(parameters, ())


def _validate_fill_holes(parameters: Mapping[str, Any]) -> None:
    _exact_keys(parameters, ("background", "fill", "connectivity"))
    background = _color(parameters["background"], "background")
    fill = _color(parameters["fill"], "fill")
    if background == fill:
        raise ValueError("hole fill must differ from background")
    if _integer(parameters["connectivity"], "connectivity", 4, 8) not in {4, 8}:
        raise ValueError("connectivity must be 4 or 8")


def _validate_extend(parameters: Mapping[str, Any]) -> None:
    _exact_keys(parameters, ("axis", "background"))
    _choice(parameters["axis"], "axis", ("h", "v", "both"))
    _color(parameters["background"], "background")


def _validate_upscale(parameters: Mapping[str, Any]) -> None:
    _exact_keys(parameters, ("factor",))
    _factor(parameters["factor"])


def _validate_downscale(parameters: Mapping[str, Any]) -> None:
    _exact_keys(parameters, ("factor", "mode"))
    _factor(parameters["factor"])
    _choice(parameters["mode"], "mode", ("uniform", "top_left", "majority"))


def _validate_role_erase(parameters: Mapping[str, Any]) -> None:
    _exact_keys(parameters, ("source_role", "background_role"))
    _validate_role(parameters["source_role"], "source_role")
    _validate_role(parameters["background_role"], "background_role")


def _validate_role_recolor(parameters: Mapping[str, Any]) -> None:
    _exact_keys(parameters, ("source_role", "target_color"))
    _validate_role(parameters["source_role"], "source_role")
    _color(parameters["target_color"], "target_color")


def _validate_spiral(parameters: Mapping[str, Any]) -> None:
    _exact_keys(parameters, ("background", "color"))
    background = _color(parameters["background"], "background")
    color = _color(parameters["color"], "color")
    if background == color:
        raise ValueError("spiral and background colors must differ")


def _validate_dynamic_layout(parameters: Mapping[str, Any]) -> None:
    # The dedicated dynamic-layout module owns this higher-order schema.  Its
    # constructor rejects missing, extra, ill-typed, and inconsistent fields.
    from .dynamic_layout import DynamicLayoutParameters

    DynamicLayoutParameters.from_record(parameters)


# ---------------------------------------------------------------------------
# Atomic execution
# ---------------------------------------------------------------------------


def _execute_d4(grid: Grid, parameters: Mapping[str, Any]) -> Grid:
    value = _array(grid)
    name = str(parameters["transform"])
    variants = {
        "id": value,
        "r90": np.rot90(value, 1),
        "r180": np.rot90(value, 2),
        "r270": np.rot90(value, 3),
        "fliplr": np.fliplr(value),
        "flipud": np.flipud(value),
        "transpose": value.T,
        "anti_transpose": np.rot90(value, 2).T,
    }
    return _output(variants[name])


def _execute_crop_bbox(grid: Grid, parameters: Mapping[str, Any]) -> Grid:
    value = _array(grid)
    background = int(parameters["background"])
    ys, xs = np.nonzero(value != background)
    if not len(ys):
        raise ValueError("cannot crop an empty foreground")
    result = value[int(ys.min()):int(ys.max()) + 1, int(xs.min()):int(xs.max()) + 1]
    return _output(result)


def _border_color(value: np.ndarray) -> int | None:
    border = np.concatenate((value[0], value[-1], value[1:-1, 0], value[1:-1, -1]))
    colors = set(int(item) for item in border)
    return next(iter(colors)) if len(colors) == 1 else None


def _execute_remove_uniform_border(grid: Grid, parameters: Mapping[str, Any]) -> Grid:
    value = _array(grid)
    if len(set(int(item) for item in value.ravel())) == 1:
        raise ValueError("a uniform grid has no distinguished bordered core")
    result = value.copy()
    removed = 0
    while result.shape[0] >= 3 and result.shape[1] >= 3 and _border_color(result) is not None:
        result = result[1:-1, 1:-1].copy()
        removed += 1
        if len(set(int(item) for item in result.ravel())) == 1:
            break
    if not removed:
        raise ValueError("grid has no uniform outer border")
    return _output(result)


def _background_components(mask: np.ndarray, connectivity: int) -> list[list[tuple[int, int]]]:
    directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]
    if connectivity == 8:
        directions += [(-1, -1), (-1, 1), (1, -1), (1, 1)]
    height, width = mask.shape
    seen = np.zeros(mask.shape, dtype=bool)
    result: list[list[tuple[int, int]]] = []
    for row in range(height):
        for column in range(width):
            if seen[row, column] or not mask[row, column]:
                continue
            queue: deque[tuple[int, int]] = deque(((row, column),))
            seen[row, column] = True
            component: list[tuple[int, int]] = []
            while queue:
                y, x = queue.popleft()
                component.append((y, x))
                for dy, dx in directions:
                    ny, nx = y + dy, x + dx
                    if 0 <= ny < height and 0 <= nx < width and mask[ny, nx] and not seen[ny, nx]:
                        seen[ny, nx] = True
                        queue.append((ny, nx))
            result.append(component)
    return result


def _execute_fill_holes(grid: Grid, parameters: Mapping[str, Any]) -> Grid:
    value = _array(grid)
    background = int(parameters["background"])
    fill = int(parameters["fill"])
    connectivity = int(parameters["connectivity"])
    result = value.copy()
    changed = 0
    height, width = value.shape
    for component in _background_components(value == background, connectivity):
        touches_boundary = any(y in {0, height - 1} or x in {0, width - 1} for y, x in component)
        if touches_boundary:
            continue
        for y, x in component:
            result[y, x] = fill
        changed += len(component)
    if not changed:
        raise ValueError("grid has no enclosed background component")
    return _output(result)


def _line_proposals(value: np.ndarray, background: int, axis: str) -> dict[tuple[int, int], int]:
    proposals: dict[tuple[int, int], int] = {}
    height, width = value.shape
    if axis in {"h", "both"}:
        for row in range(height):
            colors = sorted(set(int(item) for item in value[row]) - {background})
            if len(colors) != 1:
                continue
            color = colors[0]
            for column in range(width):
                if int(value[row, column]) == background:
                    proposals[(row, column)] = color
    if axis in {"v", "both"}:
        for column in range(width):
            colors = sorted(set(int(item) for item in value[:, column]) - {background})
            if len(colors) != 1:
                continue
            color = colors[0]
            for row in range(height):
                if int(value[row, column]) != background:
                    continue
                cell = (row, column)
                previous = proposals.get(cell)
                if previous is not None and previous != color:
                    raise ValueError("horizontal and vertical line extensions conflict")
                proposals[cell] = color
    return proposals


def _execute_extend_lines(grid: Grid, parameters: Mapping[str, Any]) -> Grid:
    value = _array(grid)
    proposals = _line_proposals(value, int(parameters["background"]), str(parameters["axis"]))
    if not proposals:
        raise ValueError("no unambiguous line can be extended")
    result = value.copy()
    for (row, column), color in sorted(proposals.items()):
        result[row, column] = color
    return _output(result)


def _execute_upscale(grid: Grid, parameters: Mapping[str, Any]) -> Grid:
    value = _array(grid)
    fy, fx = _factor(parameters["factor"])
    if value.shape[0] * fy > ARC_MAX_SIDE or value.shape[1] * fx > ARC_MAX_SIDE:
        raise ValueError("upscaled grid exceeds ARC dimensions")
    return _output(np.repeat(np.repeat(value, fy, axis=0), fx, axis=1))


def _execute_downscale(grid: Grid, parameters: Mapping[str, Any]) -> Grid:
    value = _array(grid)
    fy, fx = _factor(parameters["factor"])
    height, width = value.shape
    if height % fy or width % fx:
        raise ValueError("grid dimensions are not divisible by factor")
    mode = str(parameters["mode"])
    result = np.empty((height // fy, width // fx), dtype=np.int16)
    for row in range(result.shape[0]):
        for column in range(result.shape[1]):
            block = value[row * fy:(row + 1) * fy, column * fx:(column + 1) * fx]
            if mode == "top_left":
                selected = int(block[0, 0])
            else:
                counts = Counter(int(item) for item in block.ravel())
                if mode == "uniform":
                    if len(counts) != 1:
                        raise ValueError("downscale uniform mode encountered a nonuniform block")
                    selected = next(iter(counts))
                elif mode == "majority":
                    maximum = max(counts.values())
                    winners = sorted(color for color, count in counts.items() if count == maximum)
                    if len(winners) != 1:
                        raise ValueError("downscale majority is tied")
                    selected = winners[0]
                else:  # guarded by the exact schema
                    raise AssertionError(mode)
            result[row, column] = selected
    return _output(result)


def _execute_role_erase(grid: Grid, parameters: Mapping[str, Any]) -> Grid:
    value = _array(grid)
    source = _resolve_role(value, str(parameters["source_role"]))
    background = _resolve_role(value, str(parameters["background_role"]))
    if source == background or not np.any(value == source):
        raise ValueError("role erase would be a no-op")
    result = value.copy()
    result[value == source] = background
    return _output(result)


def _execute_role_recolor(grid: Grid, parameters: Mapping[str, Any]) -> Grid:
    value = _array(grid)
    source = _resolve_role(value, str(parameters["source_role"]))
    target = int(parameters["target_color"])
    if source == target or not np.any(value == source):
        raise ValueError("role recolor would be a no-op")
    result = value.copy()
    result[value == source] = target
    return _output(result)


def _open_u_mask(size: int) -> np.ndarray:
    mask = np.zeros((size, size), dtype=bool)
    mask[0, :] = True
    mask[:, -1] = True
    mask[-1, :] = True
    return mask


def _execute_outer_clockwise_u(grid: Grid, parameters: Mapping[str, Any]) -> Grid:
    value = _array(grid)
    background = int(parameters["background"])
    color = int(parameters["color"])
    if value.shape[0] != value.shape[1] or value.shape[0] < 4:
        raise ValueError("outer clockwise U requires a square of side at least four")
    if not np.all(value == background):
        raise ValueError("outer clockwise U requires an exactly uniform background grid")
    result = value.copy()
    result[_open_u_mask(value.shape[0])] = color
    return _output(result)


def _square_spiral(size: int, background: int, color: int) -> np.ndarray:
    result = np.full((size, size), background, dtype=np.int16)
    layer = 0
    while True:
        top = left = 2 * layer
        bottom = right = size - 1 - 2 * layer
        if top > bottom or left > right:
            break
        start = left if layer == 0 else left - 2
        result[top, start:right + 1] = color
        result[top:bottom + 1, right] = color
        result[bottom, left:right + 1] = color
        if top + 2 <= bottom:
            result[top + 2:bottom + 1, left] = color
        layer += 1
    # A 4k-sized canvas finishes one cell before the generic two-spaced ring
    # loop reaches the center.  Declaring the endpoint makes the construction
    # uniform for every even size and matches the clockwise path semantics.
    if size % 2 == 0:
        result[size // 2, size // 2 - 1] = color
    return result


def _execute_continue_square_spiral(grid: Grid, parameters: Mapping[str, Any]) -> Grid:
    value = _array(grid)
    background = int(parameters["background"])
    color = int(parameters["color"])
    if value.shape[0] != value.shape[1] or value.shape[0] < 4:
        raise ValueError("square-spiral continuation requires a square of side at least four")
    expected = np.full(value.shape, background, dtype=np.int16)
    expected[_open_u_mask(value.shape[0])] = color
    if not np.array_equal(value, expected):
        raise ValueError("square-spiral continuation requires the exact open-U prefix")
    result = _square_spiral(value.shape[0], background, color)
    if np.array_equal(result, value):
        raise ValueError("square-spiral continuation must be nontrivial")
    return _output(result)


def _execute_dynamic_layout(grid: Grid, parameters: Mapping[str, Any]) -> Grid:
    from .dynamic_layout import execute_dynamic_layout

    return _output(execute_dynamic_layout(grid, parameters))


@dataclass(frozen=True)
class AtomicStageDefinition:
    family: str
    macro_schema: str
    cost: int
    validator: ParameterValidator
    executor: AtomicExecutor
    description: str
    schema_version: int = 1

    @property
    def identity_record(self) -> dict[str, Any]:
        return {
            "schema": "komorebi.lasm.atomic_stage",
            "schema_version": self.schema_version,
            "family": self.family,
            "macro_schema": self.macro_schema,
            "cost": self.cost,
        }

    @property
    def stage_id(self) -> str:
        return sha256_record(self.identity_record)


# Order is a contract.  Proposal results are subsequently sorted by semantic
# fields, so this order is observable only through the registry manifest.
ATOMIC_STAGE_DEFINITIONS: tuple[AtomicStageDefinition, ...] = (
    AtomicStageDefinition("d4_transform", "d4_action", 1, _validate_d4, _execute_d4, "Apply one D4 action."),
    AtomicStageDefinition("crop_bbox", "shape_normalization", 2, _validate_crop, _execute_crop_bbox, "Crop to nonbackground support."),
    AtomicStageDefinition("remove_uniform_border", "shape_normalization", 2, _validate_empty, _execute_remove_uniform_border, "Remove maximal uniform border layers."),
    AtomicStageDefinition("fill_holes", "ambient_face_edit", 3, _validate_fill_holes, _execute_fill_holes, "Fill enclosed background faces."),
    AtomicStageDefinition("extend_lines", "line_closure", 3, _validate_extend, _execute_extend_lines, "Extend unambiguous rows or columns."),
    AtomicStageDefinition("upscale", "scale_transform", 3, _validate_upscale, _execute_upscale, "Repeat cells by an integral factor."),
    AtomicStageDefinition("downscale", "scale_transform", 3, _validate_downscale, _execute_downscale, "Reduce integral blocks."),
    AtomicStageDefinition("role_erase", "role_edit", 2, _validate_role_erase, _execute_role_erase, "Erase a semantic color role."),
    AtomicStageDefinition("role_recolor", "role_edit", 2, _validate_role_recolor, _execute_role_recolor, "Recolor a semantic color role."),
    AtomicStageDefinition("outer_clockwise_u", "square_spiral", 2, _validate_spiral, _execute_outer_clockwise_u, "Draw the open outer U prefix of a clockwise spiral."),
    AtomicStageDefinition("continue_square_spiral", "square_spiral", 3, _validate_spiral, _execute_continue_square_spiral, "Continue an exact open-U prefix into a clockwise square spiral."),
    AtomicStageDefinition("dynamic_layout_from_scene", "layout_from_scene", 8, _validate_dynamic_layout, _execute_dynamic_layout, "Derive a layout and payload packet from the current scene."),
)

ATOMIC_STAGE_REGISTRY = MappingProxyType({item.family: item for item in ATOMIC_STAGE_DEFINITIONS})
ATOMIC_REGISTRY_HASH = sha256_record([item.identity_record for item in ATOMIC_STAGE_DEFINITIONS])


def _make_leaf(
    namespace: str,
    family: str,
    macro_schema: str,
    parameters: Mapping[str, Any],
    source_macro_id: str,
    cost: int,
    *,
    status: str,
) -> LeafInvocation:
    return LeafInvocation(
        namespace=namespace,
        family=family,
        macro_schema=macro_schema,
        parameters_json=canonical_json(parameters),
        source_macro_id=source_macro_id,
        cost=int(cost),
        status=status,
        schema_version=1,
    )


def atomic_leaf(family: str, parameters: Mapping[str, Any]) -> LeafInvocation:
    """Construct one validated atomic leaf from an exact typed binding."""
    try:
        definition = ATOMIC_STAGE_REGISTRY[family]
    except KeyError as error:
        raise ValueError(f"unknown atomic stage {family!r}") from error
    definition.validator(parameters)
    return _make_leaf(
        "atomic", definition.family, definition.macro_schema, parameters,
        f"atomic:{definition.stage_id}", definition.cost, status="primitive",
    )


def _leaf_parameters(leaf: LeafInvocation) -> dict[str, Any]:
    raw = leaf.parameters_json
    try:
        value = json.loads(raw)
    except (TypeError, json.JSONDecodeError) as error:
        raise ValueError("leaf parameters_json is not valid JSON") from error
    if not isinstance(value, dict):
        raise TypeError("leaf parameters must decode to an object")
    if canonical_json(value) != raw:
        raise ValueError("leaf parameters_json must use canonical serialization")
    return value


def execute_leaf(leaf: LeafInvocation, grid: Any) -> Grid:
    """Execute one validated atomic or inherited versioned leaf."""
    if not isinstance(leaf, LeafInvocation):
        raise TypeError("leaf must be a LeafInvocation")
    source = _grid(grid)
    parameters = _leaf_parameters(leaf)
    if leaf.namespace == "atomic":
        try:
            definition = ATOMIC_STAGE_REGISTRY[leaf.family]
        except KeyError as error:
            raise ValueError(f"unknown atomic stage {leaf.family!r}") from error
        if leaf.macro_schema != definition.macro_schema:
            raise ValueError("atomic macro schema does not match registry")
        definition.validator(parameters)
        result = definition.executor(source, parameters)
    elif leaf.namespace == "block6":
        # Exact macro-ID membership is established when the explicit verified
        # bank record creates the leaf (and again by the enclosing composite
        # bank loader).  This context-free executor still rejects every
        # non-stable or structurally invalid inherited reference.
        if leaf.status != "stable":
            raise ValueError("Block 6 endpoint leaves must have stable status")
        if len(leaf.source_macro_id) != 64 or any(character not in "0123456789abcdef" for character in leaf.source_macro_id):
            raise ValueError("Block 6 source_macro_id must be a lowercase SHA-256 digest")
        if leaf.macro_schema != leaf.family:
            raise ValueError("Block 6 macro schema does not match family")
        validate_block6_binding(leaf.family, parameters)
        result = inherited_freeze(execute_compiled(leaf.family, source, parameters))
    elif leaf.namespace == "block8":
        # See the Block 6 branch above for the bank/source binding boundary.
        if leaf.status != "stable":
            raise ValueError("Block 8 endpoint leaves must have stable status")
        if len(leaf.source_macro_id) != 64 or any(character not in "0123456789abcdef" for character in leaf.source_macro_id):
            raise ValueError("Block 8 source_macro_id must be a lowercase SHA-256 digest")
        validate_block8_binding(leaf.family, parameters)
        try:
            definition = BLOCK8_DEFINITION_BY_NAME[leaf.family]
        except KeyError as error:
            raise ValueError(f"unknown Block 8 family {leaf.family!r}") from error
        if leaf.macro_schema != definition.macro_schema:
            raise ValueError("Block 8 macro schema does not match family")
        result = execute_block8_family(leaf.family, source, parameters)
    else:
        raise ValueError(f"unknown leaf namespace {leaf.namespace!r}")
    return _output(result)


# ---------------------------------------------------------------------------
# Finite atomic proposal enumeration
# ---------------------------------------------------------------------------


def _budget_cap(budget: Any, default: int = 128) -> int:
    if budget is None:
        value = default
    elif _is_int(budget):
        value = int(budget)
    elif isinstance(budget, Mapping):
        names = (
            "max_proposals_per_state", "proposal_limit_per_state",
            "atomic_proposals", "endpoint_proposals", "max_proposals",
            "proposals_per_state", "proposal_limit",
        )
        present = tuple(name for name in names if name in budget)
        if not present:
            raise TypeError("proposal-budget mapping lacks an integer proposal limit")
        normalized: list[int] = []
        for name in present:
            raw = budget[name]
            if not _is_int(raw):
                raise TypeError(f"{name} must be an integer")
            normalized.append(int(raw))
        if len(set(normalized)) != 1:
            raise ValueError("proposal-budget aliases disagree")
        value = normalized[0]
    else:
        # CompositionLimits exposes both of these exact integer accessors.  Do
        # not silently coerce strings, floats, booleans, or unrelated objects.
        raw = getattr(budget, "max_proposals_per_state", None)
        name = "max_proposals_per_state"
        if raw is None:
            raw = getattr(budget, "proposal_limit_per_state", None)
            name = "proposal_limit_per_state"
        if raw is None:
            raise TypeError("budget must be an integer or expose an integer proposal limit")
        if not _is_int(raw):
            raise TypeError(f"{name} must be an integer")
        value = int(raw)
    if value < 0:
        raise ValueError("proposal budget cannot be negative")
    return min(value, HARD_PROPOSAL_CAP)


def _validated_batches(currents: Sequence[Any], targets: Sequence[Any]) -> tuple[tuple[Grid, ...], tuple[Grid, ...]]:
    current_grids = tuple(_grid(value) for value in currents)
    target_grids = tuple(_grid(value) for value in targets)
    if not current_grids or len(current_grids) != len(target_grids):
        raise ValueError("currents and targets must contain the same positive number of grids")
    return current_grids, target_grids


def _common_colors(grids: Sequence[Grid]) -> tuple[int, ...]:
    intersection = set(int(value) for row in grids[0] for value in row)
    for grid in grids[1:]:
        intersection &= {int(value) for row in grid for value in row}
    return tuple(sorted(intersection))


def _novel_target_colors(currents: Sequence[Grid], targets: Sequence[Grid]) -> tuple[int, ...]:
    common: set[int] | None = None
    for current, target in zip(currents, targets):
        source_palette = {value for row in current for value in row}
        target_palette = {value for row in target for value in row}
        novel = target_palette - source_palette
        common = novel if common is None else common & novel
    return tuple(sorted(common or ()))


def _role_is_available(role: str, grids: Sequence[Grid]) -> bool:
    try:
        for grid in grids:
            _resolve_role(np.asarray(grid, dtype=np.int16), role)
    except (TypeError, ValueError):
        return False
    return True


def _candidate_factors(currents: Sequence[Grid], targets: Sequence[Grid], *, upscale: bool) -> tuple[tuple[int, int], ...]:
    candidates: set[tuple[int, int]] = set()
    ratios: list[tuple[int, int]] = []
    valid_ratio = True
    for current, target in zip(currents, targets):
        ch, cw = len(current), len(current[0])
        th, tw = len(target), len(target[0])
        if upscale:
            if th % ch or tw % cw:
                valid_ratio = False
                break
            ratios.append((th // ch, tw // cw))
        else:
            if ch % th or cw % tw:
                valid_ratio = False
                break
            ratios.append((ch // th, cw // tw))
    if valid_ratio and ratios and len(set(ratios)) == 1 and ratios[0][0] * ratios[0][1] > 1:
        candidates.add(ratios[0])
    # Small factors enable genuine intermediate normalization without turning
    # the proposer into an unbounded shape search.
    for fy in range(1, 5):
        for fx in range(1, 5):
            if fy * fx <= 1:
                continue
            if upscale:
                if all(len(grid) * fy <= ARC_MAX_SIDE and len(grid[0]) * fx <= ARC_MAX_SIDE for grid in currents):
                    candidates.add((fy, fx))
            elif all(len(grid) % fy == 0 and len(grid[0]) % fx == 0 for grid in currents):
                candidates.add((fy, fx))
    return tuple(sorted(candidates, key=lambda item: (item[0] * item[1], item)))


def _observed_recolors(currents: Sequence[Grid], targets: Sequence[Grid]) -> tuple[int, ...]:
    colors: set[int] = set()
    for current, target in zip(currents, targets):
        a = np.asarray(current, dtype=np.int16)
        b = np.asarray(target, dtype=np.int16)
        if a.shape != b.shape:
            continue
        colors.update(int(value) for value in b[a != b])
    return tuple(sorted(colors))


def _atomic_parameter_candidates(currents: tuple[Grid, ...], targets: tuple[Grid, ...], residual: Any) -> Iterable[tuple[str, dict[str, Any]]]:
    del residual  # routing is recomputed by search; proposals remain state-local

    for transform in _D4_NAMES[1:]:
        yield "d4_transform", {"transform": transform}

    common_source_colors = _common_colors(currents)
    for background in common_source_colors:
        yield "crop_bbox", {"background": background}
    yield "remove_uniform_border", {}

    target_colors = _observed_recolors(currents, targets)
    all_target_colors = tuple(sorted({value for grid in targets for row in grid for value in row}))
    fill_colors = target_colors or all_target_colors
    for background in common_source_colors:
        for fill in fill_colors:
            if fill == background:
                continue
            for connectivity in (4, 8):
                yield "fill_holes", {"background": background, "fill": fill, "connectivity": connectivity}
        for axis in ("h", "v", "both"):
            yield "extend_lines", {"axis": axis, "background": background}

    for factor in _candidate_factors(currents, targets, upscale=True):
        yield "upscale", {"factor": list(factor)}
    for factor in _candidate_factors(currents, targets, upscale=False):
        for mode in ("uniform", "top_left", "majority"):
            yield "downscale", {"factor": list(factor), "mode": mode}

    available_roles = tuple(role for role in _ROLE_NAMES if _role_is_available(role, currents))
    background_roles = tuple(role for role in ("most", "corner", "zero", "background") if role in available_roles)
    for source_role in available_roles:
        for background_role in background_roles:
            if source_role != background_role:
                yield "role_erase", {"source_role": source_role, "background_role": background_role}
        for target_color in target_colors:
            yield "role_recolor", {"source_role": source_role, "target_color": target_color}

    # The first square-spiral leaf is learned from a novel output color.  It is
    # intentionally partial and must be followed by the strict-U continuation.
    if all(len(grid) == len(grid[0]) >= 4 and len({value for row in grid for value in row}) == 1 for grid in currents):
        backgrounds = {grid[0][0] for grid in currents}
        if len(backgrounds) == 1:
            background = next(iter(backgrounds))
            for color in _novel_target_colors(currents, targets):
                if color != background:
                    yield "outer_clockwise_u", {"background": background, "color": color}

    # Exact-U recognition binds both colors from the current states.  A blank
    # grid can never pass this branch or the executor's exact precondition.
    spiral_bindings: set[tuple[int, int]] = set()
    for current in currents:
        value = np.asarray(current, dtype=np.int16)
        if value.shape[0] != value.shape[1] or value.shape[0] < 4:
            spiral_bindings.clear()
            break
        colors = sorted(set(int(item) for item in value.ravel()))
        matches: set[tuple[int, int]] = set()
        if len(colors) == 2:
            for background, color in ((colors[0], colors[1]), (colors[1], colors[0])):
                expected = np.full(value.shape, background, dtype=np.int16)
                expected[_open_u_mask(value.shape[0])] = color
                if np.array_equal(value, expected):
                    matches.add((background, color))
        spiral_bindings = matches if not spiral_bindings else spiral_bindings & matches
        if not spiral_bindings:
            break
    for background, color in sorted(spiral_bindings):
        yield "continue_square_spiral", {"background": background, "color": color}


def propose_atomic_stages(
    currents: Sequence[Any],
    targets: Sequence[Any],
    residual: Any = None,
    budget: Any = None,
) -> tuple[LeafInvocation, ...]:
    """Return a finite, deterministic set of nontrivial partial-stage leaves.

    The cap bounds stage executions, not merely the returned suffix of an
    exhaustively executed list.  Cheap typed invocations are canonicalized
    first; only the first ``cap`` invocations are run on demonstrations.
    """
    cap = _budget_cap(budget)
    if cap == 0:
        return ()
    current_grids, target_grids = _validated_batches(currents, targets)
    candidates: dict[tuple[str, str], LeafInvocation] = {}
    for family, parameters in _atomic_parameter_candidates(current_grids, target_grids, residual):
        try:
            leaf = atomic_leaf(family, parameters)
        except (KeyError, TypeError, ValueError, OverflowError):
            continue
        candidates[(family, leaf.parameters_json)] = leaf
    ordered = sorted(
        candidates.values(),
        key=lambda leaf: (leaf.cost, leaf.macro_schema, leaf.family, leaf.parameters_json, leaf.source_macro_id),
    )[:cap]
    result: list[LeafInvocation] = []
    for leaf in ordered:
        try:
            outputs = tuple(execute_leaf(leaf, grid) for grid in current_grids)
        except (KeyError, TypeError, ValueError, OverflowError):
            continue
        if all(output == current for output, current in zip(outputs, current_grids)):
            continue
        result.append(leaf)
    return tuple(result)


# ---------------------------------------------------------------------------
# Explicit schemas for inherited endpoint leaves
# ---------------------------------------------------------------------------


def _validate_axis_rank(parameters: Mapping[str, Any]) -> None:
    _exact_keys(parameters, ("axis_rule", "sequence", "period", "step", "phase"))
    _choice(parameters["axis_rule"], "axis_rule", ("more_unique", "row", "col"))
    period = _integer(parameters["period"], "period", 2, 6)
    step = _integer(parameters["step"], "step", 1, period - 1)
    del step
    _integer(parameters["phase"], "phase", 0, period - 1)
    sequence = parameters["sequence"]
    if not isinstance(sequence, (list, tuple)) or len(sequence) != period:
        raise ValueError("sequence length must equal period")
    for index, color in enumerate(sequence):
        _color(color, f"sequence[{index}]")


def _validate_d4_mosaic(parameters: Mapping[str, Any]) -> None:
    _exact_keys(parameters, ("base", "pattern", "recolor"))
    if not isinstance(parameters["base"], str) or not parameters["base"]:
        raise TypeError("base must be a nonempty layout specification")
    pattern = parameters["pattern"]
    if not isinstance(pattern, (list, tuple)) or not 1 <= len(pattern) <= 6:
        raise ValueError("pattern must have one through six rows")
    widths = set()
    for row in pattern:
        if not isinstance(row, (list, tuple)) or not 1 <= len(row) <= 6:
            raise ValueError("mosaic rows must have one through six entries")
        widths.add(len(row))
        for transform in row:
            _choice(transform, "pattern transform", ("id", "r90", "r180", "r270", "fh", "fv", "t", "at"))
    if len(widths) != 1:
        raise ValueError("mosaic pattern must be rectangular")
    _recolor_pairs(parameters["recolor"])


def _validate_block_reduce(parameters: Mapping[str, Any]) -> None:
    _exact_keys(parameters, ("factor", "mode", "recolor"))
    _factor(parameters["factor"])
    # The stable Block 7 macro is control-scoped to this exact reduction mode.
    _choice(parameters["mode"], "mode", ("any_nonbackground",))
    _recolor_pairs(parameters["recolor"])


def _validate_retain_rectangles(parameters: Mapping[str, Any]) -> None:
    _exact_keys(parameters, ("min_h", "min_w", "selection"))
    # ``min_h`` is the literal constant retained by the stable parameter
    # template; only min_w and selection are typed holes.
    if _integer(parameters["min_h"], "min_h", 1, ARC_MAX_SIDE) != 2:
        raise ValueError("the stable retain-rectangles macro requires min_h=2")
    _integer(parameters["min_w"], "min_w", 1, ARC_MAX_SIDE)
    _choice(parameters["selection"], "selection", ("all_maximal", "max_area"))


def _validate_finite_closure(parameters: Mapping[str, Any]) -> None:
    _exact_keys(parameters, ("key", "recolor"))
    _choice(parameters["key"], "key", ("extend_all", "full_d4_union"))
    _recolor_pairs(parameters["recolor"])


def _validate_panel(parameters: Mapping[str, Any]) -> None:
    _exact_keys(parameters, ("operation", "recolor", "spec"))
    if not isinstance(parameters["operation"], str) or not parameters["operation"]:
        raise TypeError("operation must be a nonempty string")
    if not isinstance(parameters["spec"], str) or not parameters["spec"]:
        raise TypeError("spec must be a nonempty string")
    _recolor_pairs(parameters["recolor"])


def _validate_role_panel(parameters: Mapping[str, Any]) -> None:
    _exact_keys(parameters, ("operation", "panelization", "recolor"))
    if not isinstance(parameters["operation"], (list, tuple)) or not parameters["operation"]:
        raise TypeError("operation must be a nonempty sequence")
    if not isinstance(parameters["panelization"], (list, tuple)) or not parameters["panelization"]:
        raise TypeError("panelization must be a nonempty sequence")
    _recolor_pairs(parameters["recolor"])


_BLOCK6_VALIDATORS: Mapping[str, ParameterValidator] = MappingProxyType({
    "axis_rank_recolor": _validate_axis_rank,
    "d4_mosaic": _validate_d4_mosaic,
    "block_reduce": _validate_block_reduce,
    "retain_maximal_rectangles": _validate_retain_rectangles,
    "finite_closure": _validate_finite_closure,
    "panel_program": _validate_panel,
    "role_panel_program": _validate_role_panel,
    "kaleido_constructor": _validate_empty,
})


def validate_block6_binding(family: str, parameters: Mapping[str, Any]) -> None:
    try:
        validator = _BLOCK6_VALIDATORS[family]
    except KeyError as error:
        raise ValueError(f"Block 6 family {family!r} is not a supported stable endpoint leaf") from error
    validator(parameters)


def _validate_axis_voronoi(parameters: Mapping[str, Any]) -> None:
    _exact_keys(parameters, ("axis", "tie", "full_boundary"))
    _choice(parameters["axis"], "axis", ("row", "col"))
    _choice(parameters["tie"], "tie", ("low", "high"))
    _bool(parameters["full_boundary"], "full_boundary")


def _validate_plus_stamp(parameters: Mapping[str, Any]) -> None:
    _exact_keys(parameters, ("radius", "cross", "diag"))
    _integer(parameters["radius"], "radius", 2, 5)
    cross = _bool(parameters["cross"], "cross")
    diag = _bool(parameters["diag"], "diag")
    if not cross and not diag:
        raise ValueError("plus stamp must enable at least one kernel")


def _validate_one_color(parameters: Mapping[str, Any]) -> None:
    _exact_keys(parameters, ("color",))
    _color(parameters["color"])


def _validate_manhattan(parameters: Mapping[str, Any]) -> None:
    _exact_keys(parameters, ("pivot_color", "fill_color", "routes"))
    _color(parameters["pivot_color"], "pivot_color")
    _color(parameters["fill_color"], "fill_color")
    routes = parameters["routes"]
    if not isinstance(routes, (list, tuple)) or not routes:
        raise TypeError("routes must be a nonempty sequence")
    seen: set[int] = set()
    for index, route in enumerate(routes):
        if not isinstance(route, (list, tuple)) or len(route) != 2:
            raise TypeError(f"routes[{index}] must be [color, order]")
        color = _color(route[0], f"routes[{index}][0]")
        if color in seen:
            raise ValueError("route colors must be unique")
        seen.add(color)
        _choice(route[1], f"routes[{index}][1]", ("hv", "vh"))


_BLOCK8_VALIDATORS: Mapping[str, ParameterValidator] = MappingProxyType({
    "axis_voronoi_frame": _validate_axis_voronoi,
    "plus_stamp_closure": _validate_plus_stamp,
    "cross_intersection_halo": _validate_one_color,
    "role_manhattan_connector": _validate_manhattan,
    "periodic_consensus_restore": _validate_empty,
    "blank_to_constant_frame": _validate_one_color,
    "singleton_to_frame": _validate_empty,
})


def validate_block8_binding(family: str, parameters: Mapping[str, Any]) -> None:
    try:
        validator = _BLOCK8_VALIDATORS[family]
    except KeyError as error:
        raise ValueError(f"Block 8 family {family!r} is not a supported stable endpoint leaf") from error
    validator(parameters)


# ---------------------------------------------------------------------------
# Verified stable-bank endpoint enumeration
# ---------------------------------------------------------------------------


_FORBIDDEN_RUNTIME_KEYS = {
    "task_id", "task_ids", "exact_task_ids", "wrong_task_ids", "expected_output",
    "expected_outputs", "input", "inputs", "output", "outputs", "grid", "grids",
    "input_grid", "input_grids", "output_grid", "output_grids", "training_hashes",
}


def _reject_runtime_provenance(value: Any) -> None:
    if isinstance(value, Mapping):
        for key, item in value.items():
            if str(key).lower() in _FORBIDDEN_RUNTIME_KEYS:
                raise ValueError(f"runtime bank contains forbidden provenance key {key!r}")
            _reject_runtime_provenance(item)
    elif isinstance(value, (list, tuple)):
        for item in value:
            _reject_runtime_provenance(item)


def _verified_block6_bank(record: Mapping[str, Any]) -> Any:
    if not isinstance(record, Mapping):
        raise TypeError("Block 6 runtime bank must be an explicit mapping record")
    _reject_runtime_provenance(record)
    if not isinstance(record.get("bank_id"), str) or not isinstance(record.get("content_hash"), str):
        raise ValueError("Block 6 runtime bank requires explicit bank_id and content_hash")
    expected_content = sha256_record({
        key: canonical_value(value) for key, value in record.items() if key != "content_hash"
    })
    if record["content_hash"] != expected_content:
        raise ValueError("Block 6 runtime-bank content hash mismatch")
    for macro in record.get("macros", ()):
        if not isinstance(macro, Mapping):
            raise TypeError("Block 6 macro record must be a mapping")
        if not isinstance(macro.get("macro_id"), str) or not isinstance(macro.get("content_hash"), str):
            raise ValueError("Block 6 macro requires explicit macro_id and content_hash")
        expected_macro_content = sha256_record({
            key: canonical_value(value) for key, value in macro.items() if key != "content_hash"
        })
        if macro["content_hash"] != expected_macro_content:
            raise ValueError("Block 6 macro content hash mismatch")
    from komorebi_lasm_grammar.model import MacroBank

    return MacroBank.from_runtime_record(record)


def _verified_block8_macros(record: Mapping[str, Any]) -> dict[str, tuple[str, tuple[str, ...]]]:
    if not isinstance(record, Mapping):
        raise TypeError("Block 8 runtime bank must be an explicit mapping record")
    _reject_runtime_provenance(record)
    if record.get("schema") != "komorebi.lasm_obstruction_macro_bank" or int(record.get("schema_version", 0)) != 1:
        raise ValueError("unsupported Block 8 runtime-bank schema")
    without_content = {key: canonical_value(value) for key, value in record.items() if key != "content_hash"}
    if record.get("content_hash") != sha256_record(without_content):
        raise ValueError("Block 8 runtime-bank content hash mismatch")
    without_ids = {
        key: canonical_value(value)
        for key, value in record.items()
        if key not in {"bank_id", "content_hash"}
    }
    if record.get("bank_id") != sha256_record(without_ids):
        raise ValueError("Block 8 runtime-bank ID mismatch")

    minimum_support = _integer(record.get("minimum_support"), "minimum_support", 1, 1_000_000)
    stable: dict[str, tuple[str, tuple[str, ...]]] = {}
    for macro in record.get("macros", ()):  # provisional records verify but do not authorize
        if not isinstance(macro, Mapping):
            raise TypeError("Block 8 macro record must be a mapping")
        macro_without_content = {key: canonical_value(value) for key, value in macro.items() if key != "content_hash"}
        if macro.get("content_hash") != sha256_record(macro_without_content):
            raise ValueError("Block 8 macro content hash mismatch")
        macro_core = {
            key: canonical_value(value)
            for key, value in macro.items()
            if key not in {
                "macro_id", "content_hash", "exact_source_tasks", "activation_count",
                "wrong_count", "evidence_digest",
            }
        }
        if macro.get("macro_id") != sha256_record(macro_core):
            raise ValueError("Block 8 macro ID mismatch")
        if str(macro.get("status")) != "stable":
            continue
        if int(macro.get("wrong_count", -1)) != 0:
            raise ValueError("stable Block 8 macro has wrong activations")
        if int(macro.get("exact_source_tasks", 0)) < max(minimum_support, int(macro.get("minimum_support", minimum_support))):
            raise ValueError("stable Block 8 macro lacks source support")
        schema = str(macro.get("macro_schema", ""))
        families = tuple(sorted(str(family) for family in macro.get("families", ())))
        if not schema or not families:
            raise ValueError("stable Block 8 macro lacks schema families")
        if schema in stable:
            raise ValueError("duplicate stable Block 8 macro schema")
        stable[schema] = (str(macro["macro_id"]), families)
    return stable


def verified_inherited_macro_ids(
    *,
    block6_bank_record: Mapping[str, Any] | None = None,
    block8_bank_record: Mapping[str, Any] | None = None,
) -> tuple[frozenset[str], frozenset[str]]:
    """Verify inherited banks and return their stable authorization IDs."""
    block6_ids: frozenset[str] = frozenset()
    block8_ids: frozenset[str] = frozenset()
    if block6_bank_record is not None:
        bank = _verified_block6_bank(block6_bank_record)
        block6_ids = frozenset(str(macro.macro_id) for macro in bank.macros)
    if block8_bank_record is not None:
        stable = _verified_block8_macros(block8_bank_record)
        block8_ids = frozenset(macro_id for macro_id, _ in stable.values())
    return block6_ids, block8_ids


def _training_task(currents: tuple[Grid, ...], targets: tuple[Grid, ...]) -> dict[str, Any]:
    # Deliberately no ``test`` key: inherited compilers see only sanitized
    # training pairs and cannot inspect or copy any attached held-out record.
    pairs = sorted(
        zip(currents, targets),
        key=lambda pair: sha256_record({"input": pair[0], "output": pair[1]}),
    )
    return {
        "train": [
            {"input": [list(row) for row in current], "output": [list(row) for row in target]}
            for current, target in pairs
        ]
    }


def _training_exact(namespace: str, family: str, parameters: Mapping[str, Any], currents: Sequence[Grid], targets: Sequence[Grid]) -> bool:
    try:
        if namespace == "block6":
            generated = tuple(inherited_freeze(execute_compiled(family, grid, parameters)) for grid in currents)
        elif namespace == "block8":
            generated = tuple(execute_block8_family(family, grid, parameters) for grid in currents)
        else:
            raise AssertionError(namespace)
        outputs = tuple(_output(output) for output in generated)
        return (
            all(output == target for output, target in zip(outputs, targets))
            and any(output != current for output, current in zip(outputs, currents))
        )
    except (KeyError, TypeError, ValueError, OverflowError):
        return False


def _block6_endpoint_leaves(
    task: Mapping[str, Any],
    currents: tuple[Grid, ...],
    targets: tuple[Grid, ...],
    bank: Any,
) -> Iterable[LeafInvocation]:
    from komorebi_lasm_compiler.compiler import compile_programs
    from komorebi_lasm_grammar.discovery import broad_candidates

    programs: list[tuple[str, Mapping[str, Any], int]] = []
    compiled, _ = compile_programs(task)
    programs.extend((program.family, program.parameters, int(program.cost)) for program in compiled)
    # Block 7's two deliberately broadened stable families must also be visible
    # as endpoint leaves when the current residual no longer matches Block 6's
    # original root route.
    for candidate in broad_candidates(task, bank=bank):
        program = candidate.get("program", {})
        programs.append((str(program.get("family", "")), dict(program.get("parameters", {})), int(program.get("cost", 4))))

    seen: set[tuple[str, str]] = set()
    for family, parameters, cost in programs:
        signature = (family, canonical_json(parameters))
        if signature in seen:
            continue
        seen.add(signature)
        try:
            validate_block6_binding(family, parameters)
            matching = tuple(sorted(bank.matching(family, parameters), key=lambda macro: macro.macro_id))
        except (KeyError, TypeError, ValueError):
            continue
        if not matching or not _training_exact("block6", family, parameters, currents, targets):
            continue
        macro = matching[0]
        yield _make_leaf(
            "block6", family, family, parameters, macro.macro_id, cost, status="stable",
        )


def _block8_endpoint_leaves(
    task: Mapping[str, Any],
    currents: tuple[Grid, ...],
    targets: tuple[Grid, ...],
    stable: Mapping[str, tuple[str, tuple[str, ...]]],
) -> Iterable[LeafInvocation]:
    seen: set[tuple[str, str]] = set()
    for definition in BLOCK8_DEFINITIONS:
        permitted = stable.get(definition.macro_schema)
        if permitted is None or definition.name not in permitted[1]:
            continue
        try:
            assignments = definition.compiler(task)
        except Exception:
            assignments = []
        for parameters in assignments:
            signature = (definition.name, canonical_json(parameters))
            if signature in seen:
                continue
            seen.add(signature)
            try:
                validate_block8_binding(definition.name, parameters)
            except (KeyError, TypeError, ValueError):
                continue
            if not _training_exact("block8", definition.name, parameters, currents, targets):
                continue
            yield _make_leaf(
                "block8", definition.name, definition.macro_schema, parameters,
                permitted[0], int(definition.sketch.cost), status="stable",
            )


def propose_endpoint_closers(
    currents: Sequence[Any],
    targets: Sequence[Any],
    *,
    block6_bank_record: Mapping[str, Any] | None = None,
    block8_bank_record: Mapping[str, Any] | None = None,
    budget: Any = None,
) -> tuple[LeafInvocation, ...]:
    """Enumerate stable, endpoint-exact inherited leaves under a return cap.

    Banks are never loaded implicitly.  Passing a malformed, stale, or
    provenance-bearing bank fails closed.  The constructed inherited task has
    training pairs only and contains no test record.  The cap limits leaves
    returned to the outer composer; finite work internal to inherited Block 6
    and Block 8 compilers is governed by those implementations and is not part
    of the Block 9 outer proposal counter.
    """
    cap = _budget_cap(budget)
    if cap == 0:
        return ()
    currents_batch, targets_batch = _validated_batches(currents, targets)
    task = _training_task(currents_batch, targets_batch)
    leaves: list[LeafInvocation] = []
    if block6_bank_record is not None:
        block6_bank = _verified_block6_bank(block6_bank_record)
        leaves.extend(_block6_endpoint_leaves(task, currents_batch, targets_batch, block6_bank))
    if block8_bank_record is not None:
        block8_stable = _verified_block8_macros(block8_bank_record)
        leaves.extend(_block8_endpoint_leaves(task, currents_batch, targets_batch, block8_stable))
    unique = {
        (leaf.namespace, leaf.family, leaf.parameters_json): leaf
        for leaf in leaves
    }
    ordered = sorted(
        unique.values(),
        key=lambda leaf: (leaf.cost, leaf.namespace, leaf.macro_schema, leaf.family, leaf.parameters_json, leaf.source_macro_id),
    )
    return tuple(ordered[:cap])


def enumerate_endpoint_closers(
    currents: Sequence[Any],
    targets: Sequence[Any],
    *,
    block6_bank_record: Mapping[str, Any] | None = None,
    block8_bank_record: Mapping[str, Any] | None = None,
    budget: Any = None,
) -> tuple[LeafInvocation, ...]:
    """Compatibility spelling for :func:`propose_endpoint_closers`."""
    return propose_endpoint_closers(
        currents,
        targets,
        block6_bank_record=block6_bank_record,
        block8_bank_record=block8_bank_record,
        budget=budget,
    )


__all__ = [
    "ARC_MAX_SIDE",
    "ATOMIC_REGISTRY_HASH",
    "ATOMIC_STAGE_DEFINITIONS",
    "ATOMIC_STAGE_REGISTRY",
    "AtomicStageDefinition",
    "atomic_leaf",
    "enumerate_endpoint_closers",
    "execute_leaf",
    "propose_atomic_stages",
    "propose_endpoint_closers",
    "validate_block6_binding",
    "validate_block8_binding",
    "verified_inherited_macro_ids",
]
