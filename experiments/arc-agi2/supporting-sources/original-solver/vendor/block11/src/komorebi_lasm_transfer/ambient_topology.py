"""Finite, fail-closed ambient/topology synthesis for PR-LASM Block 11.

Only families that had zero wrong unique activations and zero ambiguous task
activations in the complete frozen lane-D audit are executable here.  The
compiler consumes labelled training demonstrations, but sanitizes every test
record to its input grid before enumeration.  Programs are immutable,
task-ID-free values: no program field can contain a target, prediction, label,
answer, or expected-output hash.

All typed coordinates of every admitted family are enumerated.  A candidate
must replay every demonstration exactly; surviving test executions are then
collapsed by exact raster behavior.  More than one behavior class is an
abstention, not a ranking problem.

Author: Komorebi P.
"""
from __future__ import annotations

from collections import Counter, defaultdict, deque
from dataclasses import dataclass
from functools import lru_cache
import hashlib
import json
from typing import Any, Iterable, Mapping, Sequence

from komorebi_lasm_composition.task import sanitized_task_mapping


Grid = tuple[tuple[int, ...], ...]
ORTHOGONAL = ((-1, 0), (1, 0), (0, -1), (0, 1))
SCHEMA_VERSION = 1
PROGRAM_SCHEMA = "komorebi.lasm_transfer.ambient_topology_program"
COMPILATION_SCHEMA = "komorebi.lasm_transfer.ambient_topology_compilation"
MAXIMUM_PROGRAMS = 9_000
SAFE_FAMILIES = frozenset({
    "arrow_boundary_projection",
    "container_fill",
    "container_symmetry",
    "empty_boundary_channels",
    "frame_color_template",
    "frame_lattice_span",
    "keyed_payload_recolor",
    "nested_recolor",
    "recolor_topology",
    "tail_boundary_punch",
})
STABLE_FAMILIES = frozenset({"recolor_topology"})
PROVISIONAL_FAMILIES = SAFE_FAMILIES - STABLE_FAMILIES
EXCLUDED_FAMILIES = frozenset({
    "component_corridors",
    "object_bbox_fill",
    "crop_container",
    "span_closure",
})
_FORBIDDEN_PROGRAM_FIELDS = frozenset({
    "task_id", "target", "targets", "output", "outputs", "prediction",
    "predictions", "answer", "answers", "label", "labels", "expected_hash",
})


class Inapplicable(ValueError):
    """The executable contract is undefined on a particular scene."""


def canonical_json(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True)


def digest(value: Any) -> str:
    return hashlib.sha256(canonical_json(value).encode("utf-8")).hexdigest()


def validate_grid(value: Any) -> Grid:
    if not isinstance(value, (list, tuple)) or not value:
        raise TypeError("grid must be a nonempty row sequence")
    rows: list[tuple[int, ...]] = []
    width: int | None = None
    for row in value:
        if not isinstance(row, (list, tuple)) or not row:
            raise TypeError("grid rows must be nonempty sequences")
        normalized = tuple(int(item) for item in row)
        if any(isinstance(item, bool) or not isinstance(item, int) for item in row):
            raise TypeError("grid colors must be integers")
        if any(item < 0 or item > 9 for item in normalized):
            raise ValueError("grid colors must lie in [0, 9]")
        if width is None:
            width = len(normalized)
        elif len(normalized) != width:
            raise ValueError("grid must be rectangular")
        rows.append(normalized)
    if len(rows) > 30 or (width or 0) > 30:
        raise ValueError("grid exceeds ARC's 30x30 bound")
    return tuple(rows)


def thaw(grid: Grid) -> list[list[int]]:
    return [list(row) for row in grid]


def shape(grid: Grid) -> tuple[int, int]:
    return len(grid), len(grid[0])


@lru_cache(maxsize=16384)
def background(grid: Grid, role: str) -> int:
    counts = Counter(item for row in grid for item in row)
    if role.startswith("literal:"):
        value = int(role.split(":", 1)[1])
        if value not in counts:
            raise Inapplicable("literal background is absent")
        return value
    if role == "mode":
        maximum = max(counts.values())
        winners = [color for color, count in counts.items() if count == maximum]
        if len(winners) != 1:
            raise Inapplicable("modal background is ambiguous")
        return winners[0]
    if role == "corner":
        corners = Counter((grid[0][0], grid[0][-1], grid[-1][0], grid[-1][-1]))
        maximum = max(corners.values())
        winners = [color for color, count in corners.items() if count == maximum]
        if len(winners) != 1:
            raise Inapplicable("corner background is ambiguous")
        return winners[0]
    raise Inapplicable(f"unknown background role {role!r}")


@lru_cache(maxsize=32768)
def resolve_color(grid: Grid, role: str, bg: int) -> int:
    counts = Counter(item for row in grid for item in row)
    if role.startswith("literal:"):
        return int(role.split(":", 1)[1])
    if role == "background":
        return bg
    foreground = {color: count for color, count in counts.items() if color != bg}
    if not foreground:
        raise Inapplicable("foreground color role is unavailable")
    if role == "unique_foreground":
        if len(foreground) != 1:
            raise Inapplicable("unique foreground is ambiguous")
        return next(iter(foreground))
    if role in {"rarest_foreground", "most_foreground"}:
        wanted = min(foreground.values()) if role.startswith("rarest") else max(foreground.values())
        winners = [color for color, count in foreground.items() if count == wanted]
        if len(winners) != 1:
            raise Inapplicable(f"{role} is ambiguous")
        return winners[0]
    raise Inapplicable(f"unknown color role {role!r}")


def components(cells: Iterable[tuple[int, int]], height: int, width: int) -> tuple[frozenset[tuple[int, int]], ...]:
    remaining = set(cells)
    answer: list[frozenset[tuple[int, int]]] = []
    while remaining:
        seed = min(remaining)
        remaining.remove(seed)
        queue = deque((seed,))
        component = {seed}
        while queue:
            row, column = queue.popleft()
            for delta_row, delta_column in ORTHOGONAL:
                neighbor = row + delta_row, column + delta_column
                if (
                    0 <= neighbor[0] < height
                    and 0 <= neighbor[1] < width
                    and neighbor in remaining
                ):
                    remaining.remove(neighbor)
                    component.add(neighbor)
                    queue.append(neighbor)
        answer.append(frozenset(component))
    return tuple(sorted(answer, key=lambda item: (min(item), len(item))))


def bounding_box(cells: Iterable[tuple[int, int]]) -> tuple[int, int, int, int]:
    materialized = tuple(cells)
    rows = [row for row, _ in materialized]
    columns = [column for _, column in materialized]
    return min(rows), min(columns), max(rows), max(columns)


def enclosed_regions(support: frozenset[tuple[int, int]]) -> tuple[frozenset[tuple[int, int]], ...]:
    top, left, bottom, right = bounding_box(support)
    if bottom - top < 2 or right - left < 2:
        return ()
    height, width = bottom - top + 1, right - left + 1
    void = {
        (row, column)
        for row in range(top, bottom + 1)
        for column in range(left, right + 1)
        if (row, column) not in support
    }
    result = []
    for region in components(void, bottom + 1, right + 1):
        if any(row in {top, bottom} or column in {left, right} for row, column in region):
            continue
        result.append(region)
    return tuple(sorted(result, key=lambda item: (len(item), min(item))))


@dataclass(frozen=True, slots=True)
class ObjectPacket:
    color: int
    cells: frozenset[tuple[int, int]]
    top: int
    left: int
    bottom: int
    right: int
    holes: tuple[frozenset[tuple[int, int]], ...]

    @property
    def area(self) -> int:
        return len(self.cells)

    @property
    def height(self) -> int:
        return self.bottom - self.top + 1

    @property
    def width(self) -> int:
        return self.right - self.left + 1

    @property
    def center2(self) -> tuple[int, int]:
        return self.top + self.bottom, self.left + self.right

    @property
    def normalized(self) -> tuple[tuple[int, int], ...]:
        return tuple(sorted((row - self.top, column - self.left) for row, column in self.cells))

    @property
    def is_frame(self) -> bool:
        if self.height < 3 or self.width < 3:
            return False
        outline = {
            (row, column)
            for row in range(self.top, self.bottom + 1)
            for column in range(self.left, self.right + 1)
            if row in {self.top, self.bottom} or column in {self.left, self.right}
        }
        return set(self.cells) == outline

    @property
    def hole_area(self) -> int:
        return sum(len(region) for region in self.holes)

    @property
    def void(self) -> frozenset[tuple[int, int]]:
        return frozenset(cell for region in self.holes for cell in region)

    def contains(self, other: "ObjectPacket") -> bool:
        return other is not self and bool(other.cells) and set(other.cells) <= set(self.void)


@lru_cache(maxsize=4096)
def objects(grid: Grid, bg: int) -> tuple[ObjectPacket, ...]:
    height, width = shape(grid)
    answer: list[ObjectPacket] = []
    for color in sorted({item for row in grid for item in row} - {bg}):
        support = {
            (row, column)
            for row in range(height)
            for column in range(width)
            if grid[row][column] == color
        }
        for cells in components(support, height, width):
            top, left, bottom, right = bounding_box(cells)
            answer.append(
                ObjectPacket(
                    color=color,
                    cells=cells,
                    top=top,
                    left=left,
                    bottom=bottom,
                    right=right,
                    holes=enclosed_regions(cells),
                )
            )
    return tuple(
        sorted(
            answer,
            key=lambda item: (
                item.top, item.left, item.bottom, item.right, item.color, item.normalized
            ),
        )
    )


@lru_cache(maxsize=4096)
def rectangle_frames(grid: Grid, bg: int, *, maximum: int = 128) -> tuple[ObjectPacket, ...]:
    """Find monochrome rectangular boundaries even when decorations touch them.

    Connected-component-only extraction merges a frame with same-color payload
    cells.  This finite rectangle scan treats the boundary as the object and
    therefore preserves the container relation in exactly that case.
    """

    height, width = shape(grid)
    answer: list[ObjectPacket] = []
    colors = sorted({item for row in grid for item in row} - {bg})
    row_prefix: dict[int, list[list[int]]] = {}
    column_prefix: dict[int, list[list[int]]] = {}
    for color in colors:
        row_prefix[color] = [
            [0] + [
                sum(grid[row][offset] == color for offset in range(column + 1))
                for column in range(width)
            ]
            for row in range(height)
        ]
        column_prefix[color] = [
            [0] + [
                sum(grid[offset][column] == color for offset in range(row + 1))
                for row in range(height)
            ]
            for column in range(width)
        ]
    for color in colors:
        for top in range(height - 2):
            for bottom in range(top + 2, height):
                vertical_sides = [
                    column
                    for column in range(width)
                    if (
                        column_prefix[color][column][bottom + 1]
                        - column_prefix[color][column][top]
                        == bottom - top + 1
                    )
                ]
                for side_index, left in enumerate(vertical_sides):
                    for right in vertical_sides[side_index + 1:]:
                        if right - left < 2:
                            continue
                        horizontal_length = right - left + 1
                        if (
                            row_prefix[color][top][right + 1]
                            - row_prefix[color][top][left]
                            != horizontal_length
                            or row_prefix[color][bottom][right + 1]
                            - row_prefix[color][bottom][left]
                            != horizontal_length
                        ):
                            continue
                        outline = frozenset(
                            (row, column)
                            for row in range(top, bottom + 1)
                            for column in range(left, right + 1)
                            if row in {top, bottom} or column in {left, right}
                        )
                        interior = frozenset(
                            (row, column)
                            for row in range(top + 1, bottom)
                            for column in range(left + 1, right)
                        )
                        # Reject rectangles cut from uniform blocks.  A usable
                        # frame must expose at least one differently colored
                        # interior cell; that interior need not be global background.
                        if not any(grid[row][column] != color for row, column in interior):
                            continue
                        answer.append(
                            ObjectPacket(
                                color=color,
                                cells=outline,
                                top=top,
                                left=left,
                                bottom=bottom,
                                right=right,
                                holes=(interior,),
                            )
                        )
                        # A dense separator lattice can induce thousands of
                        # overlapping rectangle aliases.  Return a cacheable
                        # abstention instead of raising an exception that every
                        # syntactic frame program would rediscover.
                        if len(answer) > 512:
                            return ()
    # Keep maximal candidates when two same-color frames have the same center;
    # this removes thick-boundary aliases without deleting separate panels.
    grouped: dict[tuple[int, int, int], list[ObjectPacket]] = defaultdict(list)
    for item in answer:
        grouped[(item.color, *item.center2)].append(item)
    kept = [
        max(items, key=lambda item: (item.height * item.width, -item.top, -item.left))
        for items in grouped.values()
    ]
    if len(kept) > maximum:
        return ()
    kept = [
        item
        for item in kept
        if not any(
            other.color == item.color
            and other is not item
            and other.top <= item.top
            and other.left <= item.left
            and other.bottom >= item.bottom
            and other.right >= item.right
            and (other.height * other.width) > (item.height * item.width)
            for other in kept
        )
    ]
    return tuple(sorted(kept, key=lambda item: (item.top, item.left, item.bottom, item.right, item.color)))






_FAMILY_COSTS = {
    "arrow_boundary_projection": 8,
    "container_fill": 5,
    "container_symmetry": 7,
    "empty_boundary_channels": 5,
    "frame_color_template": 6,
    "frame_lattice_span": 8,
    "keyed_payload_recolor": 7,
    "nested_recolor": 6,
    "recolor_topology": 5,
    "tail_boundary_punch": 7,
}


def _is_literal_role(value: Any) -> bool:
    if not isinstance(value, str) or not value.startswith("literal:"):
        return False
    try:
        color = int(value.split(":", 1)[1])
    except ValueError:
        return False
    return value == f"literal:{color}" and 0 <= color <= 9


def _validate_role(value: Any, *, background_role: bool = False) -> None:
    fixed = {"mode", "corner"} if background_role else {
        "unique_foreground", "rarest_foreground", "most_foreground",
        "container_color", "marker_color",
    }
    if value not in fixed and not _is_literal_role(value):
        raise ValueError(f"invalid {'background' if background_role else 'color'} role")


def _require_domain(parameters: Mapping[str, Any], name: str, domain: set[Any]) -> None:
    if parameters[name] not in domain:
        raise ValueError(f"parameter {name!r} is outside the finite grammar")


def _validate_program_parameters(operator: str, parameters: Mapping[str, Any]) -> None:
    signatures = {
        "container_fill": {
            "background_role", "container_kind", "container_selector", "paint_role",
            "background_only", "protect_payload_bbox",
        },
        "nested_recolor": {
            "background_role", "container_kind", "container_scope", "paint_role",
        },
        "container_symmetry": {
            "background_role", "container_kind", "container_selector", "symmetry",
            "color_mode", "background_only",
        },
        "frame_color_template": {
            "background_role", "conflict_policy", "require_group",
        },
        "frame_lattice_span": {"background_role"},
        "keyed_payload_recolor": {
            "background_role", "marker_frequency", "payload_frequency",
            "require_all_markers",
        },
        "empty_boundary_channels": {
            "background_role", "axis_requirement", "paint_role",
        },
        "arrow_boundary_projection": {"background_role", "opposite_role"},
        "tail_boundary_punch": {"background_role"},
        "recolor_topology": {"background_role", "predicate", "paint_role"},
    }
    if set(parameters) != signatures[operator]:
        raise ValueError(f"parameter signature mismatch for {operator!r}")
    _validate_role(parameters["background_role"], background_role=True)
    if operator in {"container_fill", "nested_recolor", "container_symmetry"}:
        _require_domain(parameters, "container_kind", {"frame", "closed"})
    if operator == "container_fill":
        _require_domain(parameters, "container_selector", {
            "all", "largest_area_unique", "smallest_area_unique",
            "largest_hole_unique", "smallest_hole_unique",
        })
        _validate_role(parameters["paint_role"])
        for key in ("background_only", "protect_payload_bbox"):
            if not isinstance(parameters[key], bool):
                raise TypeError(f"{key} must be Boolean")
    elif operator == "nested_recolor":
        _require_domain(parameters, "container_scope", {"outermost", "all"})
        _validate_role(parameters["paint_role"])
    elif operator == "container_symmetry":
        _require_domain(parameters, "container_selector", {
            "all", "largest_area_unique", "smallest_area_unique",
        })
        _require_domain(parameters, "symmetry", {
            "horizontal", "vertical", "halfturn", "rectangle_group",
        })
        _require_domain(parameters, "color_mode", {"source", "container"})
        if not isinstance(parameters["background_only"], bool):
            raise TypeError("background_only must be Boolean")
    elif operator == "frame_color_template":
        _require_domain(parameters, "conflict_policy", {"abstain", "union"})
        if parameters["require_group"] is not True:
            raise ValueError("frame templates always require a peer group")
    elif operator == "keyed_payload_recolor":
        _require_domain(parameters, "marker_frequency", {1, 2})
        _require_domain(parameters, "payload_frequency", {3, 4, 5})
        if not isinstance(parameters["require_all_markers"], bool):
            raise TypeError("require_all_markers must be Boolean")
    elif operator == "empty_boundary_channels":
        _require_domain(parameters, "axis_requirement", {"both", "either"})
        _validate_role(parameters["paint_role"])
    elif operator == "arrow_boundary_projection":
        _validate_role(parameters["opposite_role"])
    elif operator == "recolor_topology":
        _require_domain(parameters, "predicate", {
            "has_holes", "without_holes", "contained", "uncontained",
        })
        _validate_role(parameters["paint_role"])


@dataclass(frozen=True, slots=True)
class AmbientTopologyProgram:
    operator: str
    parameters: tuple[tuple[str, Any], ...]
    cost: int
    schema_version: int = SCHEMA_VERSION

    def __post_init__(self) -> None:
        if self.operator not in SAFE_FAMILIES:
            raise ValueError(f"operator {self.operator!r} is not in the promoted grammar")
        if self.schema_version != SCHEMA_VERSION:
            raise ValueError("unsupported ambient/topology program schema version")
        object.__setattr__(self, "parameters", tuple(self.parameters))
        if any(not isinstance(key, str) or not key for key, _ in self.parameters):
            raise TypeError("program parameter names must be nonempty strings")
        if len({key for key, _ in self.parameters}) != len(self.parameters):
            raise ValueError("program parameters contain duplicate keys")
        if self.parameters != tuple(sorted(self.parameters)):
            raise ValueError("program parameters must use canonical sorted order")
        if self.cost != _FAMILY_COSTS[self.operator]:
            raise ValueError("program cost does not match its family contract")
        _validate_program_parameters(self.operator, self.parameter_map)

    @property
    def parameter_map(self) -> dict[str, Any]:
        return dict(self.parameters)

    @property
    def promotion_status(self) -> str:
        return "stable" if self.operator in STABLE_FAMILIES else "provisional"

    @property
    def program_id(self) -> str:
        return digest(self.to_record(include_id=False))

    def to_record(self, *, include_id: bool = True) -> dict[str, Any]:
        record: dict[str, Any] = {
            "schema": PROGRAM_SCHEMA,
            "schema_version": self.schema_version,
            "operator": self.operator,
            "promotion_status": self.promotion_status,
            "parameters": {key: value for key, value in self.parameters},
            "cost": self.cost,
        }
        if include_id:
            record["program_id"] = self.program_id
        return record

    @classmethod
    def create(
        cls, operator: str, cost: int | None = None, **parameters: Any,
    ) -> "AmbientTopologyProgram":
        if operator not in SAFE_FAMILIES:
            raise ValueError(f"operator {operator!r} is not in the promoted grammar")
        family_cost = _FAMILY_COSTS[operator]
        if cost is not None and cost != family_cost:
            raise ValueError("explicit program cost disagrees with the family contract")
        return cls(operator, tuple(sorted(parameters.items())), family_cost)

    @classmethod
    def from_record(cls, record: Mapping[str, Any]) -> "AmbientTopologyProgram":
        if not isinstance(record, Mapping):
            raise TypeError("program record must be a mapping")
        allowed = {
            "schema", "schema_version", "operator", "promotion_status",
            "parameters", "cost", "program_id",
        }
        if set(record) - allowed or _FORBIDDEN_PROGRAM_FIELDS & set(record):
            raise ValueError("program record contains unexpected or forbidden fields")
        if record.get("schema") != PROGRAM_SCHEMA or record.get("schema_version") != SCHEMA_VERSION:
            raise ValueError("program schema mismatch")
        parameters = record.get("parameters")
        if not isinstance(parameters, Mapping):
            raise TypeError("program parameters must be a mapping")
        if _FORBIDDEN_PROGRAM_FIELDS & set(parameters):
            raise ValueError("program parameters contain forbidden fields")
        value = cls(
            str(record.get("operator")),
            tuple(sorted(parameters.items())),
            int(record.get("cost")),
            SCHEMA_VERSION,
        )
        claimed = record.get("program_id")
        if claimed is not None and claimed != value.program_id:
            raise ValueError("program identity mismatch")
        claimed_status = record.get("promotion_status")
        if claimed_status is not None and claimed_status != value.promotion_status:
            raise ValueError("program promotion status mismatch")
        return value

    def execute(self, value: Any) -> Grid:
        return execute_program(self, value)


Program = AmbientTopologyProgram


def family_status(family: str) -> str:
    """Return the frozen promotion status of an admitted family."""

    if family in STABLE_FAMILIES:
        return "stable"
    if family in PROVISIONAL_FAMILIES:
        return "provisional"
    raise ValueError("family is outside the promoted ambient/topology grammar")


def select_by_metric(items: Sequence[Any], selector: str, metric) -> tuple[Any, ...]:
    if selector == "all":
        return tuple(items)
    if not items:
        raise Inapplicable("selector has no candidates")
    values = [metric(item) for item in items]
    wanted = max(values) if selector.startswith("largest") else min(values)
    selected = tuple(item for item, value in zip(items, values) if value == wanted)
    if selector.endswith("unique") and len(selected) != 1:
        raise Inapplicable("extremum selector is ambiguous")
    return selected


def selected_containers(packets: Sequence[ObjectPacket], kind: str, selector: str) -> tuple[ObjectPacket, ...]:
    if kind == "frame":
        candidates = tuple(item for item in packets if item.is_frame)
    elif kind == "closed":
        candidates = tuple(item for item in packets if item.holes)
    else:
        raise Inapplicable("unknown container kind")
    if selector in {"all", "largest_area_unique", "smallest_area_unique"}:
        return select_by_metric(candidates, selector, lambda item: item.area)
    if selector in {"largest_hole_unique", "smallest_hole_unique"}:
        return select_by_metric(candidates, selector, lambda item: item.hole_area)
    raise Inapplicable("unknown container selector")






def container_marker_color(grid: Grid, bg: int, container: ObjectPacket) -> int:
    colors = {
        grid[row][column]
        for row, column in container.void
        if grid[row][column] not in {bg, container.color}
    }
    if len(colors) != 1:
        raise Inapplicable("container marker color is ambiguous")
    return next(iter(colors))


def _execute_container_fill(program: Program, grid: Grid, bg: int) -> Grid:
    params = program.parameter_map
    packets = objects(grid, bg)
    container_packets = rectangle_frames(grid, bg) if params["container_kind"] == "frame" else packets
    selected = selected_containers(container_packets, params["container_kind"], params["container_selector"])
    canvas = thaw(grid)
    changed = 0
    for container in selected:
        role = params["paint_role"]
        if role == "container_color":
            color = container.color
        elif role == "marker_color":
            color = container_marker_color(grid, bg, container)
        else:
            color = resolve_color(grid, role, bg)
        protected: set[tuple[int, int]] = set()
        if params["protect_payload_bbox"]:
            payload = [
                (row, column)
                for row, column in container.void
                if grid[row][column] not in {bg, container.color}
            ]
            if not payload:
                raise Inapplicable("payload bounding box is unavailable")
            top, left, bottom, right = bounding_box(payload)
            protected.update(
                (row, column)
                for row in range(top, bottom + 1)
                for column in range(left, right + 1)
            )
        for row, column in container.void:
            if (row, column) in protected:
                continue
            if params["background_only"] and canvas[row][column] != bg:
                continue
            if canvas[row][column] != color:
                canvas[row][column] = color
                changed += 1
    if not changed:
        raise Inapplicable("container fill is a no-op")
    return validate_grid(canvas)


def _execute_nested_recolor(program: Program, grid: Grid, bg: int) -> Grid:
    params = program.parameter_map
    packets = objects(grid, bg)
    containers = list(selected_containers(packets, params["container_kind"], "all"))
    candidates = [
        item for item in containers
        if any(item.contains(other) for other in packets)
    ]
    if params["container_scope"] == "outermost":
        candidates = [
            item for item in candidates
            if not any(other.contains(item) for other in containers)
        ]
    if not candidates:
        raise Inapplicable("no nested container")
    canvas = thaw(grid)
    changed = 0
    # Outermost-first is deterministic.  In immediate-parent mode the later,
    # smaller container therefore overwrites the enclosing color.
    candidates.sort(key=lambda item: (-item.hole_area, item.top, item.left))
    for container in candidates:
        if params["paint_role"] == "container_color":
            color = container.color
        elif params["paint_role"] == "marker_color":
            color = container_marker_color(grid, bg, container)
        else:
            color = resolve_color(grid, params["paint_role"], bg)
        for other in packets:
            if not container.contains(other):
                continue
            for row, column in other.cells:
                if canvas[row][column] != color:
                    canvas[row][column] = color
                    changed += 1
    if not changed:
        raise Inapplicable("nested recolor is a no-op")
    return validate_grid(canvas)






def _execute_frame_color_template(program: Program, grid: Grid, bg: int) -> Grid:
    """Propagate a same-color interior motif among same-color peer frames."""

    params = program.parameter_map
    frames = rectangle_frames(grid, bg)
    grouped: dict[tuple[int, int, int], list[ObjectPacket]] = defaultdict(list)
    for frame in frames:
        grouped[(frame.height, frame.width, frame.color)].append(frame)
    canvas = thaw(grid)
    changed = 0
    activated_groups = 0
    for group in grouped.values():
        if len(group) < 2:
            continue
        supports = []
        for frame in group:
            support = frozenset(
                (row - frame.top, column - frame.left)
                for row in range(frame.top + 1, frame.bottom)
                for column in range(frame.left + 1, frame.right)
                if grid[row][column] == frame.color
            )
            supports.append(support)
        nonempty = {support for support in supports if support}
        if len(nonempty) != 1:
            if params["conflict_policy"] == "union" and nonempty:
                wanted = frozenset().union(*nonempty)
            else:
                continue
        else:
            wanted = next(iter(nonempty))
        if not wanted:
            continue
        activated_groups += 1
        for frame in group:
            for relative_row, relative_column in wanted:
                row = frame.top + relative_row
                column = frame.left + relative_column
                if canvas[row][column] == bg:
                    canvas[row][column] = frame.color
                    changed += 1
                elif canvas[row][column] != frame.color:
                    raise Inapplicable("frame template collides with a foreign payload")
    if params["require_group"] and activated_groups == 0:
        raise Inapplicable("no reusable same-color frame template")
    if not changed:
        raise Inapplicable("frame template transfer is a no-op")
    return validate_grid(canvas)


def _execute_frame_lattice_span(program: Program, grid: Grid, bg: int) -> Grid:
    """Close same-color anomaly spans at fixed coordinates of a frame lattice."""

    frames = rectangle_frames(grid, bg)
    grouped: dict[tuple[int, int, int], list[ObjectPacket]] = defaultdict(list)
    for frame in frames:
        grouped[(frame.height, frame.width, frame.color)].append(frame)
    edits: dict[tuple[int, int], int] = {}
    activated = 0
    for group in grouped.values():
        if len(group) < 3:
            continue
        tops = sorted({item.top for item in group})
        lefts = sorted({item.left for item in group})
        by_position = {(item.top, item.left): item for item in group}
        if len(tops) * len(lefts) != len(group) or any(
            (top, left) not in by_position for top in tops for left in lefts
        ):
            continue
        height, width = group[0].height, group[0].width
        for relative_row in range(1, height - 1):
            for relative_column in range(1, width - 1):
                values = {
                    (row_index, column_index): grid[top + relative_row][left + relative_column]
                    for row_index, top in enumerate(tops)
                    for column_index, left in enumerate(lefts)
                }
                counts = Counter(values.values())
                maximum = max(counts.values())
                baselines = [color for color, count in counts.items() if count == maximum]
                if len(baselines) != 1:
                    continue
                baseline = baselines[0]
                for color in sorted(set(values.values()) - {baseline}):
                    color_positions = {
                        position for position, value in values.items() if value == color
                    }
                    if len(color_positions) < 2:
                        continue
                    wanted: set[tuple[int, int]] = set()
                    for row_index in range(len(tops)):
                        columns = sorted(
                            column_index
                            for candidate_row, column_index in color_positions
                            if candidate_row == row_index
                        )
                        if len(columns) >= 2:
                            wanted.update(
                                (row_index, column_index)
                                for column_index in range(columns[0], columns[-1] + 1)
                            )
                    for column_index in range(len(lefts)):
                        rows = sorted(
                            row_index
                            for row_index, candidate_column in color_positions
                            if candidate_column == column_index
                        )
                        if len(rows) >= 2:
                            wanted.update(
                                (row_index, column_index)
                                for row_index in range(rows[0], rows[-1] + 1)
                            )
                    for row_index, column_index in wanted - color_positions:
                        if values[(row_index, column_index)] != baseline:
                            raise Inapplicable("frame-lattice anomaly spans conflict")
                        cell = (
                            tops[row_index] + relative_row,
                            lefts[column_index] + relative_column,
                        )
                        if cell in edits and edits[cell] != color:
                            raise Inapplicable("frame-lattice closures disagree")
                        edits[cell] = color
                        activated += 1
    if not edits or not activated:
        raise Inapplicable("frame-lattice span closure is a no-op")
    canvas = thaw(grid)
    for (row, column), color in edits.items():
        canvas[row][column] = color
    return validate_grid(canvas)




def _execute_keyed_payload_recolor(program: Program, grid: Grid, bg: int) -> Grid:
    """Use rare marker colors to recolor aligned repeated-color payloads."""

    params = program.parameter_map
    height, width = shape(grid)
    counts = Counter(item for row in grid for item in row)
    separator_colors = {
        color
        for color in counts
        if color != bg and (
            any(all(grid[row][column] == color for column in range(width)) for row in range(height))
            or any(all(grid[row][column] == color for row in range(height)) for column in range(width))
        )
    }
    marker_colors = {
        color for color, count in counts.items()
        if color != bg and color not in separator_colors and count <= params["marker_frequency"]
    }
    payload_colors = {
        color for color, count in counts.items()
        if color != bg and color not in separator_colors and count >= params["payload_frequency"]
    } - marker_colors
    if len(payload_colors) != 1 or len(marker_colors) < 2:
        raise Inapplicable("keyed payload palette roles are ambiguous")
    payload_color = next(iter(payload_colors))
    markers = [
        (row, column, grid[row][column])
        for row in range(height)
        for column in range(width)
        if grid[row][column] in marker_colors
    ]
    payload = [
        (row, column)
        for row in range(height)
        for column in range(width)
        if grid[row][column] == payload_color
    ]
    marker_rows = [row for row, _, _ in markers]
    marker_columns = [column for _, column, _ in markers]
    payload_rows = [row for row, _ in payload]
    payload_columns = [column for _, column in payload]
    horizontally_separated = max(marker_columns) < min(payload_columns) or max(payload_columns) < min(marker_columns)
    vertically_separated = max(marker_rows) < min(payload_rows) or max(payload_rows) < min(marker_rows)
    if horizontally_separated == vertically_separated:
        raise Inapplicable("marker/payload orientation is ambiguous")
    coordinate = (lambda item: item[0]) if horizontally_separated else (lambda item: item[1])
    canvas = thaw(grid)
    changed = 0
    assigned = set()
    for row, column in payload:
        distances = [abs(coordinate((row, column)) - coordinate(marker)) for marker in markers]
        minimum = min(distances)
        winners = [index for index, distance in enumerate(distances) if distance == minimum]
        if len(winners) != 1:
            raise Inapplicable("payload-to-marker assignment is tied")
        marker = markers[winners[0]]
        assigned.add(winners[0])
        if canvas[row][column] != marker[2]:
            canvas[row][column] = marker[2]
            changed += 1
    if params["require_all_markers"] and len(assigned) != len(markers):
        raise Inapplicable("some marker has no payload support")
    if not changed:
        raise Inapplicable("keyed payload recolor is a no-op")
    return validate_grid(canvas)






def _execute_empty_boundary_channels(program: Program, grid: Grid, bg: int) -> Grid:
    """Paint empty rows/columns spanning two non-background boundary cells."""

    params = program.parameter_map
    height, width = shape(grid)
    if height < 3 or width < 3:
        raise Inapplicable("channel canvas is too small")
    rows = [
        row
        for row in range(1, height - 1)
        if grid[row][0] != bg
        and grid[row][-1] != bg
        and all(grid[row][column] == bg for column in range(1, width - 1))
    ]
    columns = [
        column
        for column in range(1, width - 1)
        if grid[0][column] != bg
        and grid[-1][column] != bg
        and all(grid[row][column] == bg for row in range(1, height - 1))
    ]
    if params["axis_requirement"] == "both" and (not rows or not columns):
        raise Inapplicable("both channel axes are required")
    if params["axis_requirement"] == "either" and not (rows or columns):
        raise Inapplicable("no empty boundary channel")
    color = resolve_color(grid, params["paint_role"], bg)
    canvas = thaw(grid)
    changed = 0
    for row in rows:
        for column in range(1, width - 1):
            if canvas[row][column] == bg:
                canvas[row][column] = color
                changed += 1
    for column in columns:
        for row in range(1, height - 1):
            if canvas[row][column] == bg:
                canvas[row][column] = color
                changed += 1
    if not changed:
        raise Inapplicable("boundary channels are a no-op")
    return validate_grid(canvas)


def _arrow_direction(item: ObjectPacket) -> tuple[int, int, tuple[int, int]]:
    row_counts = Counter(row for row, _ in item.cells)
    column_counts = Counter(column for _, column in item.cells)
    maximum_row = max(row_counts.values())
    maximum_column = max(column_counts.values())
    rows = [row for row, count in row_counts.items() if count == maximum_row]
    columns = [column for column, count in column_counts.items() if count == maximum_column]
    if len(rows) != 1 or len(columns) != 1 or max(maximum_row, maximum_column) < 3:
        raise Inapplicable("object lacks a unique arrow cross")
    center = rows[0], columns[0]
    if center not in item.cells:
        raise Inapplicable("arrow cross intersection is absent")
    up, down = center[0] - item.top, item.bottom - center[0]
    left, right = center[1] - item.left, item.right - center[1]
    vertical_asymmetric = up != down
    horizontal_asymmetric = left != right
    if vertical_asymmetric == horizontal_asymmetric:
        raise Inapplicable("arrow direction is ambiguous")
    if vertical_asymmetric:
        return ((-1, 0, center) if up < down else (1, 0, center))
    return ((0, -1, center) if left < right else (0, 1, center))


def _execute_arrow_boundary_projection(program: Program, grid: Grid, bg: int) -> Grid:
    params = program.parameter_map
    height, width = shape(grid)
    frames = [
        item for item in rectangle_frames(grid, bg)
        if item.top == 0 and item.left == 0 and item.bottom == height - 1 and item.right == width - 1
    ]
    if len(frames) != 1:
        raise Inapplicable("unique canvas frame is unavailable")
    frame = frames[0]
    packets = [
        item for item in objects(grid, bg)
        if item.color != frame.color and frame.contains(item)
    ]
    if len(packets) < 2:
        raise Inapplicable("arrow cohort is too small")
    erase = resolve_color(grid, params["opposite_role"], bg)
    edits: dict[tuple[int, int], int] = {}
    for item in packets:
        delta_row, delta_column, center = _arrow_direction(item)
        if delta_row < 0:
            head, tail = (frame.top, center[1]), (frame.bottom, center[1])
        elif delta_row > 0:
            head, tail = (frame.bottom, center[1]), (frame.top, center[1])
        elif delta_column < 0:
            head, tail = (center[0], frame.left), (center[0], frame.right)
        else:
            head, tail = (center[0], frame.right), (center[0], frame.left)
        for cell, color in ((head, item.color), (tail, erase)):
            if cell in edits and edits[cell] != color:
                raise Inapplicable("arrow projections conflict")
            edits[cell] = color
    canvas = thaw(grid)
    changed = 0
    for (row, column), color in edits.items():
        if canvas[row][column] != frame.color:
            raise Inapplicable("arrow endpoint does not land on frame")
        canvas[row][column] = color
        changed += 1
    if not changed:
        raise Inapplicable("arrow boundary projection is a no-op")
    return validate_grid(canvas)


def _execute_tail_boundary_punch(program: Program, grid: Grid, bg: int) -> Grid:
    """Continue opposite a marker-attached straight tail and open its boundary."""

    height, width = shape(grid)
    counts = Counter(item for row in grid for item in row)
    markers = [
        (row, column)
        for row in range(1, height - 1)
        for column in range(1, width - 1)
        if grid[row][column] != bg and counts[grid[row][column]] == 1
    ]
    directions = (
        (-1, -1), (-1, 0), (-1, 1),
        (0, -1), (0, 1),
        (1, -1), (1, 0), (1, 1),
    )
    edits: set[tuple[int, int]] = set()
    for marker_row, marker_column in markers:
        marker_color = grid[marker_row][marker_column]
        for tail_row_delta, tail_column_delta in directions:
            row = marker_row + tail_row_delta
            column = marker_column + tail_column_delta
            if not (0 <= row < height and 0 <= column < width):
                continue
            tail_color = grid[row][column]
            if tail_color in {bg, marker_color}:
                continue
            length = 0
            while 0 <= row < height and 0 <= column < width and grid[row][column] == tail_color:
                length += 1
                row += tail_row_delta
                column += tail_column_delta
            if length < 3:
                continue
            row = marker_row - tail_row_delta
            column = marker_column - tail_column_delta
            traversed = 0
            while 0 <= row < height and 0 <= column < width and grid[row][column] == bg:
                traversed += 1
                row -= tail_row_delta
                column -= tail_column_delta
            if traversed == 0 or not (0 <= row < height and 0 <= column < width):
                continue
            edits.add((row, column))
    if len(edits) != 1:
        raise Inapplicable("tail-to-boundary continuation is ambiguous")
    row, column = next(iter(edits))
    canvas = thaw(grid)
    if canvas[row][column] == bg:
        raise Inapplicable("boundary punch is a no-op")
    canvas[row][column] = bg
    return validate_grid(canvas)










def reflect_cell(cell: tuple[int, int], container: ObjectPacket, symmetry: str) -> tuple[int, int]:
    row, column = cell
    if symmetry == "horizontal":
        return row, container.left + container.right - column
    if symmetry == "vertical":
        return container.top + container.bottom - row, column
    if symmetry == "halfturn":
        return container.top + container.bottom - row, container.left + container.right - column
    raise Inapplicable("unknown reflection")


def _execute_container_symmetry(program: Program, grid: Grid, bg: int) -> Grid:
    params = program.parameter_map
    packets = objects(grid, bg)
    container_packets = rectangle_frames(grid, bg) if params["container_kind"] == "frame" else packets
    selected = selected_containers(container_packets, params["container_kind"], params["container_selector"])
    symmetries = (
        ("horizontal", "vertical", "halfturn")
        if params["symmetry"] == "rectangle_group"
        else (params["symmetry"],)
    )
    canvas = thaw(grid)
    changed = 0
    for container in selected:
        payload = [
            (row, column, grid[row][column])
            for row, column in container.void
            if grid[row][column] not in {bg, container.color}
        ]
        if not payload:
            continue
        for row, column, source_color in payload:
            for symmetry in symmetries:
                target_row, target_column = reflect_cell((row, column), container, symmetry)
                if (target_row, target_column) not in container.void:
                    raise Inapplicable("reflected payload leaves container void")
                color = source_color if params["color_mode"] == "source" else container.color
                if params["background_only"] and canvas[target_row][target_column] != bg:
                    continue
                if canvas[target_row][target_column] != color:
                    canvas[target_row][target_column] = color
                    changed += 1
    if not changed:
        raise Inapplicable("container symmetry is a no-op")
    return validate_grid(canvas)




def _execute_recolor_topology(program: Program, grid: Grid, bg: int) -> Grid:
    params = program.parameter_map
    packets = objects(grid, bg)
    containers = tuple(item for item in packets if item.holes)
    contained = {
        index
        for index, item in enumerate(packets)
        if any(container.contains(item) for container in containers)
    }
    if params["predicate"] == "has_holes":
        selected = [item for item in packets if item.holes]
    elif params["predicate"] == "without_holes":
        selected = [item for item in packets if not item.holes]
    elif params["predicate"] == "contained":
        selected = [item for index, item in enumerate(packets) if index in contained]
    elif params["predicate"] == "uncontained":
        selected = [item for index, item in enumerate(packets) if index not in contained]
    else:
        raise Inapplicable("unknown recolor topology predicate")
    if not selected or len(selected) == len(packets):
        raise Inapplicable("topology recolor needs positive and negative examples")
    color = resolve_color(grid, params["paint_role"], bg)
    canvas = thaw(grid)
    changed = 0
    for item in selected:
        for row, column in item.cells:
            if canvas[row][column] != color:
                canvas[row][column] = color
                changed += 1
    if not changed:
        raise Inapplicable("topology recolor is a no-op")
    return validate_grid(canvas)






def execute_program(program: AmbientTopologyProgram | Mapping[str, Any], value: Any) -> Grid:
    parsed = (
        program
        if isinstance(program, AmbientTopologyProgram)
        else AmbientTopologyProgram.from_record(program)
    )
    grid = validate_grid(value)
    params = parsed.parameter_map
    bg = background(grid, params["background_role"])
    operators = {
        "container_fill": _execute_container_fill,
        "nested_recolor": _execute_nested_recolor,
        "frame_color_template": _execute_frame_color_template,
        "frame_lattice_span": _execute_frame_lattice_span,
        "keyed_payload_recolor": _execute_keyed_payload_recolor,
        "empty_boundary_channels": _execute_empty_boundary_channels,
        "arrow_boundary_projection": _execute_arrow_boundary_projection,
        "tail_boundary_punch": _execute_tail_boundary_punch,
        "container_symmetry": _execute_container_symmetry,
        "recolor_topology": _execute_recolor_topology,
    }
    try:
        executor = operators[parsed.operator]
    except KeyError as error:
        raise Inapplicable(f"unknown operator {parsed.operator!r}") from error
    return executor(parsed, grid, bg)


execute = execute_program


def background_roles(inputs: Sequence[Grid]) -> tuple[str, ...]:
    candidates = ["mode", "corner"]
    common = set(item for row in inputs[0] for item in row)
    for grid in inputs[1:]:
        common &= {item for row in grid for item in row}
    candidates.extend(f"literal:{color}" for color in sorted(common))
    accepted: dict[tuple[int, ...], str] = {}
    for role in candidates:
        try:
            behavior = tuple(background(grid, role) for grid in inputs)
        except (Inapplicable, ValueError):
            continue
        accepted.setdefault(behavior, role)
    return tuple(accepted.values())


def paint_roles(inputs: Sequence[Grid], targets: Sequence[Grid]) -> tuple[str, ...]:
    roles = ["unique_foreground", "rarest_foreground", "most_foreground"]
    changed_target_colors: set[int] = set()
    for source, target in zip(inputs, targets):
        if shape(source) != shape(target):
            continue
        for row in range(len(source)):
            for column in range(len(source[0])):
                if source[row][column] != target[row][column]:
                    changed_target_colors.add(target[row][column])
    roles.extend(f"literal:{color}" for color in sorted(changed_target_colors))
    # Collapse role aliases that resolve to the same color vector on all
    # training inputs.  Literals absent from an input are still executable and
    # therefore remain as constant vectors.
    accepted: dict[tuple[int, ...], str] = {}
    available_backgrounds = background_roles(inputs)
    if not available_backgrounds:
        return ()
    for role in roles:
        try:
            vector = []
            for grid in inputs:
                bg = background(grid, available_backgrounds[0])
                vector.append(resolve_color(grid, role, bg))
        except (Inapplicable, ValueError):
            continue
        accepted.setdefault(tuple(vector), role)
    return tuple(accepted.values())


def enumerate_programs(
    inputs: Sequence[Grid],
    targets: Sequence[Grid],
) -> tuple[AmbientTopologyProgram, ...]:
    """Enumerate every coordinate of all ten promoted structural families."""

    if not inputs or len(inputs) != len(targets):
        raise ValueError("enumeration requires paired nonempty demonstrations")
    programs: dict[str, AmbientTopologyProgram] = {}

    def add(program: AmbientTopologyProgram) -> None:
        programs[program.program_id] = program

    colors = paint_roles(inputs, targets)
    for bg_role in background_roles(inputs):
        for kind in ("frame", "closed"):
            for selector in (
                "all", "largest_area_unique", "smallest_area_unique",
                "largest_hole_unique", "smallest_hole_unique",
            ):
                for paint in (*colors, "container_color", "marker_color"):
                    for background_only in (True, False):
                        for protect_payload_bbox in (False, True):
                            add(AmbientTopologyProgram.create(
                                "container_fill",
                                background_role=bg_role,
                                container_kind=kind,
                                container_selector=selector,
                                paint_role=paint,
                                background_only=background_only,
                                protect_payload_bbox=protect_payload_bbox,
                            ))

            for scope in ("outermost", "all"):
                for paint in (*colors, "container_color", "marker_color"):
                    add(AmbientTopologyProgram.create(
                        "nested_recolor",
                        background_role=bg_role,
                        container_kind=kind,
                        container_scope=scope,
                        paint_role=paint,
                    ))

            for selector in ("all", "largest_area_unique", "smallest_area_unique"):
                for symmetry in ("horizontal", "vertical", "halfturn", "rectangle_group"):
                    for color_mode in ("source", "container"):
                        for background_only in (True, False):
                            add(AmbientTopologyProgram.create(
                                "container_symmetry",
                                background_role=bg_role,
                                container_kind=kind,
                                container_selector=selector,
                                symmetry=symmetry,
                                color_mode=color_mode,
                                background_only=background_only,
                            ))

        for conflict_policy in ("abstain", "union"):
            add(AmbientTopologyProgram.create(
                "frame_color_template",
                background_role=bg_role,
                conflict_policy=conflict_policy,
                require_group=True,
            ))
        add(AmbientTopologyProgram.create(
            "frame_lattice_span",
            background_role=bg_role,
        ))

        for marker_frequency in (1, 2):
            for payload_frequency in (3, 4, 5):
                for require_all in (True, False):
                    add(AmbientTopologyProgram.create(
                        "keyed_payload_recolor",
                        background_role=bg_role,
                        marker_frequency=marker_frequency,
                        payload_frequency=payload_frequency,
                        require_all_markers=require_all,
                    ))

        for axis_requirement in ("both", "either"):
            for paint in colors:
                add(AmbientTopologyProgram.create(
                    "empty_boundary_channels",
                    background_role=bg_role,
                    axis_requirement=axis_requirement,
                    paint_role=paint,
                ))

        for opposite_role in colors:
            add(AmbientTopologyProgram.create(
                "arrow_boundary_projection",
                background_role=bg_role,
                opposite_role=opposite_role,
            ))

        add(AmbientTopologyProgram.create(
            "tail_boundary_punch",
            background_role=bg_role,
        ))

        for predicate in ("has_holes", "without_holes", "contained", "uncontained"):
            for paint in colors:
                add(AmbientTopologyProgram.create(
                    "recolor_topology",
                    background_role=bg_role,
                    predicate=predicate,
                    paint_role=paint,
                ))

    return tuple(sorted(programs.values(), key=lambda item: (item.cost, item.program_id)))

GRAMMAR_CONTRACT = {
    "schema": "komorebi.lasm_transfer.ambient_topology_grammar",
    "schema_version": SCHEMA_VERSION,
    "safe_families": sorted(SAFE_FAMILIES),
    "family_status": {
        family: "stable" if family in STABLE_FAMILIES else "provisional"
        for family in sorted(SAFE_FAMILIES)
    },
    "stability_rule": "at least two distinct exact tasks and zero wrong or ambiguous activations",
    "excluded_after_complete_frozen_audit": sorted(EXCLUDED_FAMILIES),
    "maximum_programs_per_task": MAXIMUM_PROGRAMS,
    "background_role_domain": ["mode", "corner", "literal color common to demonstrations"],
    "paint_role_domain": [
        "unique_foreground", "rarest_foreground", "most_foreground",
        "demonstrated changed-to literal color",
    ],
    "family_coordinates": {
        "container_fill": {
            "container_kind": ["frame", "closed"],
            "container_selector": [
                "all", "largest_area_unique", "smallest_area_unique",
                "largest_hole_unique", "smallest_hole_unique",
            ],
            "paint_extensions": ["container_color", "marker_color"],
            "background_only": [True, False],
            "protect_payload_bbox": [False, True],
        },
        "nested_recolor": {
            "container_kind": ["frame", "closed"],
            "container_scope": ["outermost", "all"],
            "paint_extensions": ["container_color", "marker_color"],
        },
        "container_symmetry": {
            "container_kind": ["frame", "closed"],
            "container_selector": ["all", "largest_area_unique", "smallest_area_unique"],
            "symmetry": ["horizontal", "vertical", "halfturn", "rectangle_group"],
            "color_mode": ["source", "container"],
            "background_only": [True, False],
        },
        "frame_color_template": {
            "conflict_policy": ["abstain", "union"],
            "require_group": [True],
        },
        "frame_lattice_span": {},
        "keyed_payload_recolor": {
            "marker_frequency": [1, 2],
            "payload_frequency": [3, 4, 5],
            "require_all_markers": [True, False],
        },
        "empty_boundary_channels": {"axis_requirement": ["both", "either"]},
        "arrow_boundary_projection": {},
        "tail_boundary_punch": {},
        "recolor_topology": {
            "predicate": ["has_holes", "without_holes", "contained", "uncontained"],
        },
    },
    "selection": "exact demonstration replay then complete test-behavior quotient",
}
GRAMMAR_HASH = digest(GRAMMAR_CONTRACT)


@dataclass(frozen=True, slots=True)
class AmbientTopologyLimits:
    """Finite input bounds and the immutable audited program cap."""

    max_training_examples: int = 10
    max_test_examples: int = 10
    maximum_programs: int = MAXIMUM_PROGRAMS

    def __post_init__(self) -> None:
        for name in ("max_training_examples", "max_test_examples", "maximum_programs"):
            value = getattr(self, name)
            if isinstance(value, bool) or not isinstance(value, int) or value < 1:
                raise ValueError(f"{name} must be a positive integer")
        if self.maximum_programs != MAXIMUM_PROGRAMS:
            raise ValueError(f"maximum_programs is frozen at {MAXIMUM_PROGRAMS}")


@dataclass(frozen=True, slots=True)
class AmbientTopologyBehavior:
    behavior_hash: str
    predictions: tuple[Grid, ...]
    programs: tuple[AmbientTopologyProgram, ...]

    @property
    def representative(self) -> AmbientTopologyProgram:
        return self.programs[0]

    @property
    def equivalent_program_ids(self) -> tuple[str, ...]:
        return tuple(program.program_id for program in self.programs)

    def to_record(self) -> dict[str, Any]:
        return {
            "behavior_hash": self.behavior_hash,
            "predictions": self.predictions,
            "representative_program": self.representative.to_record(),
            "equivalent_program_count": len(self.programs),
            "equivalent_program_ids": self.equivalent_program_ids,
            "equivalent_program_ids_hash": digest(self.equivalent_program_ids),
        }


@dataclass(frozen=True, slots=True)
class AmbientTopologyReceipt:
    routed: bool
    complete: bool
    grammar_hash: str
    maximum_programs: int
    programs_enumerated: int
    demonstration_executions: int
    inapplicable_executions: int
    mismatch_executions: int
    exact_programs: int
    admitted_programs: int
    test_program_executions: int
    test_grid_executions: int
    runtime_failures: int
    behavior_classes: int
    limit_reached: str = ""

    def to_record(self) -> dict[str, Any]:
        return {
            "routed": self.routed,
            "complete": self.complete,
            "grammar_hash": self.grammar_hash,
            "maximum_programs": self.maximum_programs,
            "programs_enumerated": self.programs_enumerated,
            "demonstration_executions": self.demonstration_executions,
            "inapplicable_executions": self.inapplicable_executions,
            "mismatch_executions": self.mismatch_executions,
            "exact_programs": self.exact_programs,
            "admitted_programs": self.admitted_programs,
            "test_program_executions": self.test_program_executions,
            "test_grid_executions": self.test_grid_executions,
            "runtime_failures": self.runtime_failures,
            "behavior_classes": self.behavior_classes,
            "limit_reached": self.limit_reached,
        }


@dataclass(frozen=True, slots=True)
class AmbientTopologyCompilation:
    exact_programs: tuple[AmbientTopologyProgram, ...]
    surviving_programs: tuple[AmbientTopologyProgram, ...]
    behaviors: tuple[AmbientTopologyBehavior, ...]
    receipt: AmbientTopologyReceipt
    allow_provisional: bool = False

    def __post_init__(self) -> None:
        if not isinstance(self.allow_provisional, bool):
            raise TypeError("allow_provisional must be Boolean")

    @property
    def policy_hash(self) -> str:
        return digest({
            "schema": "komorebi.lasm_transfer.ambient_topology_policy",
            "schema_version": SCHEMA_VERSION,
            "allow_provisional": self.allow_provisional,
        })

    @property
    def selected_behavior(self) -> AmbientTopologyBehavior | None:
        return self.behaviors[0] if len(self.behaviors) == 1 else None

    @property
    def selected_prediction(self) -> tuple[Grid, ...] | None:
        selected = self.selected_behavior
        return None if selected is None else selected.predictions

    @property
    def ambiguous(self) -> bool:
        return len(self.behaviors) > 1

    @property
    def status(self) -> str:
        if not self.receipt.complete:
            return "limit_abstention"
        if not self.receipt.routed:
            return "not_routed"
        if self.ambiguous:
            return "ambiguous_abstention"
        if self.selected_behavior is not None:
            return "unique"
        return "no_candidate"

    def to_record(self) -> dict[str, Any]:
        body = {
            "schema": COMPILATION_SCHEMA,
            "schema_version": SCHEMA_VERSION,
            "status": self.status,
            "allow_provisional": self.allow_provisional,
            "policy_hash": self.policy_hash,
            "exact_programs": [program.to_record() for program in self.exact_programs],
            "surviving_program_ids": [
                program.program_id for program in self.surviving_programs
            ],
            "behaviors": [behavior.to_record() for behavior in self.behaviors],
            "selected_behavior_hash": (
                self.selected_behavior.behavior_hash if self.selected_behavior else ""
            ),
            "ambiguous": self.ambiguous,
            "receipt": self.receipt.to_record(),
        }
        body["content_hash"] = digest(body)
        return body


_EXECUTION_ERRORS = (
    AssertionError,
    IndexError,
    KeyError,
    OverflowError,
    RuntimeError,
    TypeError,
    ValueError,
    ZeroDivisionError,
)


def _empty_compilation(
    *,
    routed: bool,
    complete: bool,
    allow_provisional: bool = False,
    limit_reached: str = "",
    programs_enumerated: int = 0,
) -> AmbientTopologyCompilation:
    return AmbientTopologyCompilation(
        (), (), (),
        AmbientTopologyReceipt(
            routed=routed,
            complete=complete,
            grammar_hash=GRAMMAR_HASH,
            maximum_programs=MAXIMUM_PROGRAMS,
            programs_enumerated=programs_enumerated,
            demonstration_executions=0,
            inapplicable_executions=0,
            mismatch_executions=0,
            exact_programs=0,
            admitted_programs=0,
            test_program_executions=0,
            test_grid_executions=0,
            runtime_failures=0,
            behavior_classes=0,
            limit_reached=limit_reached,
        ),
        allow_provisional,
    )


def compile_ambient_topology(
    task: Mapping[str, Any],
    *,
    allow_provisional: bool = False,
    limits: AmbientTopologyLimits | None = None,
) -> AmbientTopologyCompilation:
    """Compile the complete promoted grammar without observing a test target."""

    if not isinstance(allow_provisional, bool):
        raise TypeError("allow_provisional must be Boolean")
    limits = limits or AmbientTopologyLimits()
    safe_task = sanitized_task_mapping(task)
    training = safe_task["train"]
    tests = safe_task["test"]
    if len(training) > limits.max_training_examples:
        return _empty_compilation(
            routed=False, complete=False, allow_provisional=allow_provisional,
            limit_reached="training_example_limit",
        )
    if len(tests) > limits.max_test_examples:
        return _empty_compilation(
            routed=False, complete=False, allow_provisional=allow_provisional,
            limit_reached="test_example_limit",
        )
    inputs = tuple(validate_grid(example["input"]) for example in training)
    targets = tuple(validate_grid(example["output"]) for example in training)
    test_inputs = tuple(validate_grid(example["input"]) for example in tests)
    routed = (
        bool(inputs)
        and all(shape(source) == shape(target) for source, target in zip(inputs, targets))
        and any(source != target for source, target in zip(inputs, targets))
    )
    if not routed:
        return _empty_compilation(
            routed=False, complete=True, allow_provisional=allow_provisional,
        )

    programs = enumerate_programs(inputs, targets)
    if len(programs) > MAXIMUM_PROGRAMS:
        return _empty_compilation(
            routed=True,
            complete=False,
            allow_provisional=allow_provisional,
            limit_reached="program_enumeration_limit",
            programs_enumerated=len(programs),
        )

    exact: list[AmbientTopologyProgram] = []
    demonstration_executions = 0
    inapplicable_executions = 0
    mismatch_executions = 0
    for program in programs:
        matches = True
        for source, target in zip(inputs, targets):
            demonstration_executions += 1
            try:
                observed = execute_program(program, source)
            except _EXECUTION_ERRORS:
                inapplicable_executions += 1
                matches = False
                break
            if observed != target:
                mismatch_executions += 1
                matches = False
                break
        if matches:
            exact.append(program)

    admitted = [
        program
        for program in exact
        if program.operator in STABLE_FAMILIES or allow_provisional
    ]
    groups: dict[str, dict[str, Any]] = {}
    surviving: list[AmbientTopologyProgram] = []
    test_program_executions = 0
    test_grid_executions = 0
    runtime_failures = 0
    for program in admitted:
        test_program_executions += 1
        predictions = []
        valid = True
        for source in test_inputs:
            test_grid_executions += 1
            try:
                predictions.append(execute_program(program, source))
            except _EXECUTION_ERRORS:
                runtime_failures += 1
                valid = False
                break
        if not valid:
            continue
        behavior = tuple(predictions)
        behavior_hash = digest(behavior)
        item = groups.setdefault(
            behavior_hash,
            {"predictions": behavior, "programs": []},
        )
        item["programs"].append(program)
        surviving.append(program)

    behaviors = tuple(
        AmbientTopologyBehavior(
            behavior_hash,
            groups[behavior_hash]["predictions"],
            tuple(sorted(
                groups[behavior_hash]["programs"],
                key=lambda program: (program.cost, program.program_id),
            )),
        )
        for behavior_hash in sorted(groups)
    )
    exact.sort(key=lambda program: (program.cost, program.program_id))
    surviving.sort(key=lambda program: (program.cost, program.program_id))
    receipt = AmbientTopologyReceipt(
        routed=True,
        complete=True,
        grammar_hash=GRAMMAR_HASH,
        maximum_programs=MAXIMUM_PROGRAMS,
        programs_enumerated=len(programs),
        demonstration_executions=demonstration_executions,
        inapplicable_executions=inapplicable_executions,
        mismatch_executions=mismatch_executions,
        exact_programs=len(exact),
        admitted_programs=len(admitted),
        test_program_executions=test_program_executions,
        test_grid_executions=test_grid_executions,
        runtime_failures=runtime_failures,
        behavior_classes=len(behaviors),
    )
    return AmbientTopologyCompilation(
        tuple(exact), tuple(surviving), behaviors, receipt, allow_provisional,
    )


compile_programs = compile_ambient_topology


__all__ = [
    "AmbientTopologyBehavior",
    "AmbientTopologyCompilation",
    "AmbientTopologyLimits",
    "AmbientTopologyProgram",
    "AmbientTopologyReceipt",
    "COMPILATION_SCHEMA",
    "EXCLUDED_FAMILIES",
    "GRAMMAR_CONTRACT",
    "GRAMMAR_HASH",
    "Grid",
    "Inapplicable",
    "MAXIMUM_PROGRAMS",
    "PROGRAM_SCHEMA",
    "PROVISIONAL_FAMILIES",
    "Program",
    "SAFE_FAMILIES",
    "SCHEMA_VERSION",
    "STABLE_FAMILIES",
    "background",
    "compile_ambient_topology",
    "compile_programs",
    "components",
    "digest",
    "enumerate_programs",
    "execute",
    "execute_program",
    "family_status",
    "objects",
    "validate_grid",
]
