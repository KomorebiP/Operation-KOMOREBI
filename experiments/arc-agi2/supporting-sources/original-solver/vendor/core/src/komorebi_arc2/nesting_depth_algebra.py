"""Bounded color algebra over clean concentric boundary packets.

The compiler in this module is deliberately narrow.  It recognizes filled,
axis-aligned rectangular packets whose cells are constant at each rectangular
depth.  A packet may contain bands thicker than one cell and a color may recur
at several depths, but the packet geometry must form one unambiguous chain.

Two palette-equivariant programs are available:

``reverse_depth_colors``
    Reverse the first-occurrence order of colors from the outside inward.

``rotate_deepest_color_outward``
    Move the deepest first-occurring color to the outside of the color cycle.
    This is a color substitution, so repeated occurrences of one color remain
    consistent and the raster geometry is unchanged.

Every program is applied atomically to every packet in a scene.  Touching
packets, non-rectangular components, branching containment, ambiguous
backgrounds, and resource-limit violations cause an explicit abstention.  The
task compiler emits a candidate only when exactly one program reproduces every
demonstration exactly.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
import json
from typing import Dict, Iterable, Mapping, Optional, Sequence, Tuple

import numpy as np

try:
    from .planar_incidence import AmbiguousBackgroundError, infer_background
except ImportError:  # standalone Kaggle runtime
    from planar_incidence import AmbiguousBackgroundError, infer_background


Array = np.ndarray
Box = Tuple[int, int, int, int]

NESTING_DEPTH_ALGEBRA_VERSION = "1.0"
FAMILY = "causal_nesting_depth_color_algebra"
REVERSE_DEPTH_COLORS = "reverse_depth_colors"
ROTATE_DEEPEST_COLOR_OUTWARD = "rotate_deepest_color_outward"
SUPPORTED_OPERATIONS = (REVERSE_DEPTH_COLORS, ROTATE_DEEPEST_COLOR_OUTWARD)


class NestingDepthError(ValueError):
    """Base class for invalid inputs and explicit structural abstentions."""


class NestingDepthAbstention(NestingDepthError):
    """Raised when a scene lacks one unambiguous concentric interpretation."""


class NestingDepthLimitError(NestingDepthError):
    """Raised before a configured hard resource limit would be exceeded."""


@dataclass(frozen=True)
class NestingDepthLimits:
    """Hard bounds for analysis and compilation."""

    maximum_height: int = 30
    maximum_width: int = 30
    maximum_cells: int = 900
    maximum_palette: int = 16
    maximum_packets: int = 16
    maximum_layers: int = 15
    maximum_examples: int = 16

    def to_record(self) -> Dict[str, int]:
        return {str(key): int(value) for key, value in asdict(self).items()}


DEFAULT_LIMITS = NestingDepthLimits()


@dataclass(frozen=True)
class ConcentricPacket:
    """One completely filled rectangular packet with uniform depth layers."""

    box: Box
    layer_colors: Tuple[int, ...]
    whole_canvas: bool = False

    @property
    def top(self) -> int:
        return self.box[0]

    @property
    def left(self) -> int:
        return self.box[1]

    @property
    def bottom(self) -> int:
        return self.box[2]

    @property
    def right(self) -> int:
        return self.box[3]

    @property
    def height(self) -> int:
        return self.bottom - self.top + 1

    @property
    def width(self) -> int:
        return self.right - self.left + 1

    @property
    def layer_count(self) -> int:
        return len(self.layer_colors)

    @property
    def depth_color_order(self) -> Tuple[int, ...]:
        """Colors in first-occurrence order from outermost to innermost."""

        seen = set()
        output = []
        for color in self.layer_colors:
            if color in seen:
                continue
            seen.add(color)
            output.append(int(color))
        return tuple(output)

    def normalized_profile(self) -> Tuple[int, int, int, int, int]:
        """Palette-, location-, and D4-invariant packet evidence."""

        return (
            min(self.height, self.width),
            max(self.height, self.width),
            self.layer_count,
            len(self.depth_color_order),
            int(self.whole_canvas),
        )


@dataclass(frozen=True)
class NestingDepthScene:
    shape: Tuple[int, int]
    background: Optional[int]
    packets: Tuple[ConcentricPacket, ...]
    extraction_mode: str

    def normalized_profile(self) -> Tuple[object, ...]:
        return (
            min(self.shape),
            max(self.shape),
            self.extraction_mode,
            tuple(sorted(packet.normalized_profile() for packet in self.packets)),
        )


@dataclass(frozen=True)
class NestingDepthCandidate:
    """Entry-independent exact candidate with a canonical JSON record."""

    name: str
    operation: str
    grids: Tuple[Array, ...]
    train_grids: Tuple[Array, ...]
    complexity: int
    metadata: Mapping[str, object]
    family: str = FAMILY
    train_error: int = 0

    def to_record(self, *, include_grids: bool = True) -> Dict[str, object]:
        record: Dict[str, object] = {
            "name": str(self.name),
            "family": str(self.family),
            "operation": str(self.operation),
            "train_error": int(self.train_error),
            "complexity": int(self.complexity),
            "metadata": _json_safe(dict(self.metadata)),
        }
        if include_grids:
            record["grids"] = [np.asarray(grid, dtype=np.int64).tolist() for grid in self.grids]
            record["train_grids"] = [
                np.asarray(grid, dtype=np.int64).tolist() for grid in self.train_grids
            ]
        # Enforce the public contract here rather than leaving a latent NumPy
        # scalar failure for a release auditor to discover.
        json.dumps(record, sort_keys=True)
        return record


def _json_safe(value: object) -> object:
    if isinstance(value, Mapping):
        return {str(key): _json_safe(item) for key, item in value.items()}
    if isinstance(value, (tuple, list)):
        return [_json_safe(item) for item in value]
    if isinstance(value, np.ndarray):
        return value.tolist()
    if isinstance(value, np.integer):
        return int(value)
    if isinstance(value, np.floating):
        return float(value)
    if value is None or isinstance(value, (str, int, float, bool)):
        return value
    raise TypeError(f"value is not JSON-safe: {type(value).__name__}")


def _validated_grid(grid: Array, limits: NestingDepthLimits) -> Array:
    raw = np.asarray(grid)
    if raw.ndim != 2 or raw.size == 0:
        raise NestingDepthError("nesting-depth analysis requires a nonempty 2D grid")
    height, width = raw.shape
    if height > limits.maximum_height or width > limits.maximum_width:
        raise NestingDepthLimitError(
            f"grid shape {raw.shape} exceeds {limits.maximum_height}x{limits.maximum_width}"
        )
    if raw.size > limits.maximum_cells:
        raise NestingDepthLimitError("cell budget exceeded")
    if not np.issubdtype(raw.dtype, np.integer):
        if not np.all(np.equal(raw, np.floor(raw))):
            raise NestingDepthError("grid values must be integers")
    if len(np.unique(raw)) > limits.maximum_palette:
        raise NestingDepthLimitError("palette budget exceeded")
    return np.array(raw, dtype=np.int64, copy=True)


def _rectangular_depth_colors(rectangle: Array) -> Tuple[int, ...]:
    """Return uniform rectangular-layer colors or explicitly abstain."""

    height, width = rectangle.shape
    layer_count = (min(height, width) + 1) // 2
    output = []
    for depth in range(layer_count):
        top = depth
        left = depth
        bottom = height - depth - 1
        right = width - depth - 1
        cells = []
        cells.extend(int(value) for value in rectangle[top, left : right + 1])
        if bottom != top:
            cells.extend(int(value) for value in rectangle[bottom, left : right + 1])
        if bottom - top >= 2:
            cells.extend(int(value) for value in rectangle[top + 1 : bottom, left])
            if right != left:
                cells.extend(int(value) for value in rectangle[top + 1 : bottom, right])
        colors = set(cells)
        if len(colors) != 1:
            raise NestingDepthAbstention("a rectangular depth has multiple colors")
        output.append(int(next(iter(colors))))
    return tuple(output)


def _packet_from_box(
    grid: Array,
    box: Box,
    limits: NestingDepthLimits,
    *,
    whole_canvas: bool,
) -> ConcentricPacket:
    top, left, bottom, right = box
    rectangle = np.asarray(grid[top : bottom + 1, left : right + 1])
    layer_colors = _rectangular_depth_colors(rectangle)
    if len(layer_colors) > limits.maximum_layers:
        raise NestingDepthLimitError("nesting-layer budget exceeded")
    packet = ConcentricPacket(box, layer_colors, whole_canvas)
    # Two colors make reversal and a one-step cycle observationally identical.
    # Requiring three distinct depth colors prevents that semantic tie.
    if len(packet.depth_color_order) < 3:
        raise NestingDepthAbstention("fewer than three distinct depth colors")
    return packet


def _component_boxes(mask: Array) -> Tuple[Tuple[Tuple[int, int], ...], ...]:
    height, width = mask.shape
    visited = np.zeros(mask.shape, dtype=bool)
    output = []
    for row in range(height):
        for column in range(width):
            if not bool(mask[row, column]) or bool(visited[row, column]):
                continue
            stack = [(row, column)]
            visited[row, column] = True
            cells = []
            while stack:
                current_row, current_column = stack.pop()
                cells.append((current_row, current_column))
                for dr, dc in ((-1, 0), (0, 1), (1, 0), (0, -1)):
                    nr, nc = current_row + dr, current_column + dc
                    if (
                        0 <= nr < height
                        and 0 <= nc < width
                        and bool(mask[nr, nc])
                        and not bool(visited[nr, nc])
                    ):
                        visited[nr, nc] = True
                        stack.append((nr, nc))
            output.append(tuple(sorted(cells)))
    return tuple(output)


def _box(cells: Sequence[Tuple[int, int]]) -> Box:
    rows = [cell[0] for cell in cells]
    columns = [cell[1] for cell in cells]
    return min(rows), min(columns), max(rows), max(columns)


def _boxes_touch(first: Box, second: Box) -> bool:
    """Return whether two full rectangles touch cardinally or diagonally."""

    first_top, first_left, first_bottom, first_right = first
    second_top, second_left, second_bottom, second_right = second
    row_distance = max(first_top - second_bottom, second_top - first_bottom, 0)
    column_distance = max(first_left - second_right, second_left - first_right, 0)
    return max(row_distance, column_distance) <= 1


def analyze_concentric_packets(
    grid: Array,
    limits: NestingDepthLimits = DEFAULT_LIMITS,
) -> NestingDepthScene:
    """Extract one unambiguous collection of clean concentric packets.

    A fully layered canvas is treated as one packet.  Otherwise the unique
    structurally inferred background is removed and every remaining connected
    component must be a completely filled layered rectangle.  No residual
    foreground objects are ignored.
    """

    value = _validated_grid(grid, limits)
    height, width = value.shape

    try:
        whole = _packet_from_box(
            value,
            (0, 0, height - 1, width - 1),
            limits,
            whole_canvas=True,
        )
    except NestingDepthAbstention as exc:
        # A perfectly layered whole canvas with too few color roles is an
        # operation tie, not evidence that an inner foreground packet should
        # be recovered by choosing one of those colors as background.
        if "fewer than three distinct depth colors" in str(exc):
            raise
        whole = None
    if whole is not None:
        return NestingDepthScene(value.shape, None, (whole,), "whole_canvas_layered")

    try:
        background = int(infer_background(value))
    except AmbiguousBackgroundError as exc:
        raise NestingDepthAbstention("background is structurally ambiguous") from exc

    components = _component_boxes(value != background)
    if not components:
        raise NestingDepthAbstention("no foreground packet")
    if len(components) > limits.maximum_packets:
        raise NestingDepthLimitError("packet budget exceeded")

    packets = []
    for cells in components:
        box = _box(cells)
        top, left, bottom, right = box
        expected_area = (bottom - top + 1) * (right - left + 1)
        if len(cells) != expected_area:
            raise NestingDepthAbstention("a foreground component is not a filled rectangle")
        packets.append(_packet_from_box(value, box, limits, whole_canvas=False))

    packets.sort(key=lambda packet: packet.box)
    for index, first in enumerate(packets):
        for second in packets[index + 1 :]:
            if _boxes_touch(first.box, second.box):
                raise NestingDepthAbstention("distinct packets touch or overlap")

    return NestingDepthScene(
        value.shape,
        background,
        tuple(packets),
        "foreground_rectangular_components",
    )


def _depth_color_mapping(packet: ConcentricPacket, operation: str) -> Dict[int, int]:
    order = packet.depth_color_order
    if len(order) < 3:
        raise NestingDepthAbstention("depth-color operation is tied")
    if operation == REVERSE_DEPTH_COLORS:
        destinations = tuple(reversed(order))
    elif operation == ROTATE_DEEPEST_COLOR_OUTWARD:
        destinations = (order[-1], *order[:-1])
    else:
        raise NestingDepthError(f"unsupported depth-color operation: {operation}")
    return {int(source): int(target) for source, target in zip(order, destinations)}


def apply_nesting_depth_operation(
    grid: Array,
    operation: str,
    limits: NestingDepthLimits = DEFAULT_LIMITS,
) -> Array:
    """Apply one operation atomically to every packet in ``grid``."""

    value = _validated_grid(grid, limits)
    scene = analyze_concentric_packets(value, limits)
    output = value.copy()
    for packet in scene.packets:
        mapping = _depth_color_mapping(packet, operation)
        top, left, bottom, right = packet.box
        source = value[top : bottom + 1, left : right + 1]
        target = output[top : bottom + 1, left : right + 1]
        for color, replacement in mapping.items():
            target[source == color] = replacement
    if np.array_equal(output, value):
        raise NestingDepthAbstention("depth-color operation made no change")
    return output


def _profile_record(profile: Tuple[object, ...]) -> Dict[str, object]:
    minimum, maximum, mode, packet_profiles = profile
    return {
        "shape_short": int(minimum),
        "shape_long": int(maximum),
        "extraction_mode": str(mode),
        "packets": [
            {
                "height_short": int(item[0]),
                "height_long": int(item[1]),
                "layer_count": int(item[2]),
                "depth_color_count": int(item[3]),
                "whole_canvas": bool(item[4]),
            }
            for item in packet_profiles
        ],
    }


def _sorted_profile_records(scenes: Iterable[NestingDepthScene]) -> list[Dict[str, object]]:
    profiles = sorted(scene.normalized_profile() for scene in scenes)
    return [_profile_record(profile) for profile in profiles]


def compile_nesting_depth_candidates(
    train: Sequence[Tuple[Array, Array]],
    tests: Sequence[Array],
    limits: NestingDepthLimits = DEFAULT_LIMITS,
) -> Tuple[NestingDepthCandidate, ...]:
    """Compile the unique exact nesting-depth program for one ARC task.

    Ordinary structural failures return no candidates.  Resource-limit errors
    remain visible and are never converted into partial predictions.
    """

    if not train or not tests:
        return ()
    if len(train) + len(tests) > limits.maximum_examples:
        raise NestingDepthLimitError("example budget exceeded")

    try:
        train_sources = tuple(_validated_grid(source, limits) for source, _ in train)
        train_targets = tuple(_validated_grid(target, limits) for _, target in train)
        test_sources = tuple(_validated_grid(test, limits) for test in tests)
        train_scenes = tuple(analyze_concentric_packets(source, limits) for source in train_sources)
        test_scenes = tuple(analyze_concentric_packets(source, limits) for source in test_sources)
    except NestingDepthLimitError:
        raise
    except NestingDepthError:
        return ()

    modes = {scene.extraction_mode for scene in (*train_scenes, *test_scenes)}
    if len(modes) != 1:
        return ()
    if any(source.shape != target.shape for source, target in zip(train_sources, train_targets)):
        return ()

    exact_programs = []
    for operation in SUPPORTED_OPERATIONS:
        try:
            predicted_train = tuple(
                apply_nesting_depth_operation(source, operation, limits)
                for source in train_sources
            )
            if not all(
                np.array_equal(prediction, target)
                for prediction, target in zip(predicted_train, train_targets)
            ):
                continue
            predicted_tests = tuple(
                apply_nesting_depth_operation(source, operation, limits)
                for source in test_sources
            )
        except NestingDepthLimitError:
            raise
        except NestingDepthError:
            continue
        exact_programs.append((operation, predicted_train, predicted_tests))

    # A semantic tie is unsafe even if both programs happen to make the same
    # held-out raster on the supplied inputs.
    if len(exact_programs) != 1:
        return ()

    operation, predicted_train, predicted_tests = exact_programs[0]
    train_profiles = _sorted_profile_records(train_scenes)
    test_profiles = _sorted_profile_records(test_scenes)
    packet_count = sum(len(scene.packets) for scene in train_scenes)
    maximum_colors = max(
        len(packet.depth_color_order)
        for scene in (*train_scenes, *test_scenes)
        for packet in scene.packets
    )
    metadata: Dict[str, object] = {
        "schema": "komorebi.arc.nesting-depth-color-algebra.v1",
        "module_version": NESTING_DEPTH_ALGEBRA_VERSION,
        "operation": operation,
        "quantifier": "FOR_EACH",
        "atomic_scene_application": True,
        "geometry_preserved": True,
        "input_grounded": True,
        "test_input_grounded": True,
        "provenance_kind": "test_input_transform",
        "permutation_invariant": True,
        "d4_equivariant": True,
        "palette_equivariant": True,
        "admissible": True,
        "exact_demonstration_fit": True,
        "training_packet_count": int(packet_count),
        "training_scene_profiles": train_profiles,
        "test_scene_profiles": test_profiles,
        "limits": limits.to_record(),
    }
    complexity = 7 + int(maximum_colors) + int(packet_count)
    candidate = NestingDepthCandidate(
        name=f"nesting_depth:{operation}:for_each_packet",
        operation=operation,
        grids=tuple(np.array(grid, dtype=np.int64, copy=True) for grid in predicted_tests),
        train_grids=tuple(np.array(grid, dtype=np.int64, copy=True) for grid in predicted_train),
        complexity=complexity,
        metadata=metadata,
    )
    # Final serialization is part of candidate admission.
    candidate.to_record()
    return (candidate,)


def nesting_depth_candidate_records(
    train: Sequence[Tuple[Array, Array]],
    tests: Sequence[Array],
    limits: NestingDepthLimits = DEFAULT_LIMITS,
    *,
    include_grids: bool = True,
) -> Tuple[Dict[str, object], ...]:
    """Return canonical JSON-safe records for an external candidate portfolio."""

    return tuple(
        candidate.to_record(include_grids=include_grids)
        for candidate in compile_nesting_depth_candidates(train, tests, limits)
    )


__all__ = [
    "ConcentricPacket",
    "DEFAULT_LIMITS",
    "FAMILY",
    "NESTING_DEPTH_ALGEBRA_VERSION",
    "NestingDepthAbstention",
    "NestingDepthCandidate",
    "NestingDepthError",
    "NestingDepthLimitError",
    "NestingDepthLimits",
    "NestingDepthScene",
    "REVERSE_DEPTH_COLORS",
    "ROTATE_DEEPEST_COLOR_OUTWARD",
    "SUPPORTED_OPERATIONS",
    "analyze_concentric_packets",
    "apply_nesting_depth_operation",
    "compile_nesting_depth_candidates",
    "nesting_depth_candidate_records",
]
