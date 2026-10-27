"""Exact, bounded parity rewrites over planar background faces.

This module is intentionally independent of the main solver portfolio.  It
compiles one small causal family: construct the face-adjacency graph witnessed
by :class:`~komorebi_arc2.planar_incidence.FaceSeparationEvidence`, choose an
input-grounded anchor, two-color the connected bipartite graph, and recolor
one or both parity classes atomically.

The implementation is conservative by design:

* background hypotheses must be explicit or have a unique best input-only
  rank;
* every face must belong to one connected bipartite graph;
* both parity classes must be witnessed in every demonstration and test;
* anchors are resolved from canvas corners, a unique structural marker, or a
  demonstration-input source color -- never from face IDs or traversal order;
* output colors are literals learned only from demonstration outputs;
* every compiled program reproduces every demonstration exactly; and
* distinct exact programs must agree on all requested test predictions or the
  compiler abstains.

Runtime graph nodes retain coordinates for rendering.  Public candidate and
provenance records contain only JSON-safe, coordinate-free graph metadata.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
import json
from typing import Dict, Iterable, Mapping, Optional, Sequence, Tuple

import numpy as np

try:
    from .planar_incidence import (
        AmbiguousBackgroundError,
        FaceSeparationEvidence,
        PlanarIncidenceError,
        PlanarIncidenceGraph,
        PlanarIncidenceLimitError,
        build_planar_incidence,
        rank_background_hypotheses,
    )
except ImportError:  # standalone Kaggle runtime
    from planar_incidence import (
        AmbiguousBackgroundError,
        FaceSeparationEvidence,
        PlanarIncidenceError,
        PlanarIncidenceGraph,
        PlanarIncidenceLimitError,
        build_planar_incidence,
        rank_background_hypotheses,
    )


Array = np.ndarray
Cell = Tuple[int, int]

PLANAR_FACE_PARITY_VERSION = "1.0"
FAMILY = "causal_planar_face_parity"

CANVAS_CORNERS = "canvas_corners"
UNIQUE_MARKER = "unique_marker"
UNIQUE_SOURCE_COLOR_FACE = "unique_source_color_face"
ANCHOR_MODES = (CANVAS_CORNERS, UNIQUE_MARKER, UNIQUE_SOURCE_COLOR_FACE)

RECOLOR_ONE_PARITY = "recolor_one_parity"
RECOLOR_BOTH_PARITIES = "recolor_both_parities"
RENDER_MODES = (RECOLOR_ONE_PARITY, RECOLOR_BOTH_PARITIES)


class FaceParityError(ValueError):
    """Base class for invalid parity-rewrite requests."""


class FaceParityAbstention(FaceParityError):
    """Raised when the required structural interpretation is not unique."""


class FaceParityLimitError(FaceParityError):
    """Raised before a configured resource bound would be exceeded."""


class FaceParityAmbiguityError(FaceParityAbstention):
    """Raised when exact programs disagree on a held-out prediction."""


@dataclass(frozen=True)
class FaceParityLimits:
    """Hard bounds for compilation and held-out rendering."""

    maximum_height: int = 30
    maximum_width: int = 30
    maximum_cells: int = 900
    maximum_palette: int = 16
    maximum_faces: int = 128
    maximum_separations: int = 512
    maximum_examples: int = 16
    maximum_programs: int = 128
    maximum_marker_area: int = 4

    def to_record(self) -> Dict[str, int]:
        return {str(key): int(value) for key, value in asdict(self).items()}


DEFAULT_LIMITS = FaceParityLimits()


@dataclass(frozen=True)
class FaceAnchor:
    """An input-grounded rule for selecting the parity-zero face."""

    mode: str
    source_color: Optional[int] = None

    def __post_init__(self) -> None:
        if self.mode not in ANCHOR_MODES:
            raise FaceParityError(f"unsupported face anchor mode: {self.mode}")
        if self.mode == UNIQUE_SOURCE_COLOR_FACE:
            if self.source_color is None:
                raise FaceParityError("a source-color anchor requires a color")
        elif self.source_color is not None:
            raise FaceParityError("only a source-color anchor may carry a color")

    def to_record(self) -> Dict[str, object]:
        record: Dict[str, object] = {"mode": self.mode}
        if self.source_color is not None:
            record["source_color"] = int(self.source_color)
            record["source_color_origin"] = "demonstration_inputs"
        return record


@dataclass(frozen=True)
class FaceParityProgram:
    """One exact parity renderer with demo-derived literal output colors."""

    anchor: FaceAnchor
    render_mode: str
    target_parity: Optional[int] = None
    change_color: Optional[int] = None
    even_color: Optional[int] = None
    odd_color: Optional[int] = None

    def __post_init__(self) -> None:
        if self.render_mode not in RENDER_MODES:
            raise FaceParityError(f"unsupported render mode: {self.render_mode}")
        if self.render_mode == RECOLOR_ONE_PARITY:
            if self.target_parity not in (0, 1) or self.change_color is None:
                raise FaceParityError("one-parity rendering requires parity and color")
            if self.even_color is not None or self.odd_color is not None:
                raise FaceParityError("one-parity rendering cannot carry two colors")
        else:
            if self.even_color is None or self.odd_color is None:
                raise FaceParityError("two-parity rendering requires both colors")
            if self.target_parity is not None or self.change_color is not None:
                raise FaceParityError("two-parity rendering cannot carry a target parity")
            if int(self.even_color) == int(self.odd_color):
                raise FaceParityError("the two parity colors must be distinguishable")

    @property
    def complexity(self) -> int:
        anchor_cost = {
            CANVAS_CORNERS: 1,
            UNIQUE_MARKER: 2,
            UNIQUE_SOURCE_COLOR_FACE: 3,
        }[self.anchor.mode]
        render_cost = 2 if self.render_mode == RECOLOR_ONE_PARITY else 3
        return anchor_cost + render_cost

    def to_record(self) -> Dict[str, object]:
        record: Dict[str, object] = {
            "schema": "planar-face-parity-program-v1",
            "anchor": self.anchor.to_record(),
            "render_mode": self.render_mode,
            "literal_output_color_origin": "demonstration_outputs",
        }
        if self.render_mode == RECOLOR_ONE_PARITY:
            record.update(
                {
                    "target_parity": int(self.target_parity),
                    "change_color": int(self.change_color),
                }
            )
        else:
            record.update(
                {
                    "even_color": int(self.even_color),
                    "odd_color": int(self.odd_color),
                }
            )
        return record


@dataclass(frozen=True)
class FaceParityCandidate:
    """Entry-independent exact candidate with immutable prediction arrays."""

    name: str
    program: FaceParityProgram
    grids: Tuple[Array, ...]
    train_grids: Tuple[Array, ...]
    metadata: Mapping[str, object]
    family: str = FAMILY
    train_error: int = 0

    def __post_init__(self) -> None:
        object.__setattr__(self, "grids", tuple(_immutable_grid(item) for item in self.grids))
        object.__setattr__(
            self,
            "train_grids",
            tuple(_immutable_grid(item) for item in self.train_grids),
        )

    @property
    def complexity(self) -> int:
        return self.program.complexity

    def to_record(self, *, include_grids: bool = True) -> Dict[str, object]:
        record: Dict[str, object] = {
            "name": str(self.name),
            "family": str(self.family),
            "train_error": int(self.train_error),
            "complexity": int(self.complexity),
            "program": self.program.to_record(),
            "metadata": _json_safe(dict(self.metadata)),
        }
        if include_grids:
            record["grids"] = [np.asarray(item).tolist() for item in self.grids]
            record["train_grids"] = [
                np.asarray(item).tolist() for item in self.train_grids
            ]
        json.dumps(record, sort_keys=True)
        return record


@dataclass(frozen=True)
class _AnchoredScene:
    grid: Array
    graph: PlanarIncidenceGraph
    background: int
    anchor_face_id: int
    parity_by_face: Tuple[Tuple[int, int], ...]

    def parity_cells(self, parity: int) -> Tuple[Cell, ...]:
        selected = {
            face_id for face_id, value in self.parity_by_face if value == int(parity)
        }
        return tuple(
            cell
            for face in self.graph.faces
            if face.face_id in selected
            for cell in face.cells
        )

    def normalized_anchor_feature(self) -> Tuple[object, ...]:
        return self.graph.face(self.anchor_face_id).normalized_feature()


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


def _immutable_grid(grid: Array) -> Array:
    output = np.array(grid, dtype=np.int64, copy=True)
    output.setflags(write=False)
    return output


def _validated_grid(grid: Array, limits: FaceParityLimits) -> Array:
    raw = np.asarray(grid)
    if raw.ndim != 2 or raw.size == 0:
        raise FaceParityError("face-parity analysis requires a nonempty 2D grid")
    height, width = raw.shape
    if height > limits.maximum_height or width > limits.maximum_width:
        raise FaceParityLimitError(
            f"grid shape {raw.shape} exceeds {limits.maximum_height}x{limits.maximum_width}"
        )
    if raw.size > limits.maximum_cells:
        raise FaceParityLimitError("cell budget exceeded")
    if not np.issubdtype(raw.dtype, np.integer):
        if not np.all(np.equal(raw, np.floor(raw))):
            raise FaceParityError("grid values must be integers")
    if len(np.unique(raw)) > limits.maximum_palette:
        raise FaceParityLimitError("palette budget exceeded")
    return np.array(raw, dtype=np.int64, copy=True)


def _selected_background(grid: Array, explicit: Optional[int]) -> int:
    if explicit is not None:
        background = int(explicit)
        if background not in {int(value) for value in np.unique(grid)}:
            raise FaceParityAbstention("explicit background is absent from the input")
        return background
    hypotheses = rank_background_hypotheses(grid)
    best = tuple(item for item in hypotheses if item.rank == 0)
    if len(best) != 1:
        raise FaceParityAbstention(
            "best input-only background hypothesis is structurally tied"
        )
    return int(best[0].color)


def _build_graph(
    grid: Array,
    background: Optional[int],
    limits: FaceParityLimits,
) -> Tuple[Array, PlanarIncidenceGraph, int]:
    value = _validated_grid(grid, limits)
    selected = _selected_background(value, background)
    try:
        graph = build_planar_incidence(value, background=selected)
    except PlanarIncidenceLimitError as error:
        raise FaceParityLimitError(str(error)) from error
    except (PlanarIncidenceError, AmbiguousBackgroundError) as error:
        raise FaceParityAbstention(str(error)) from error
    if len(graph.faces) > limits.maximum_faces:
        raise FaceParityLimitError("face budget exceeded")
    if len(graph.face_separations) > limits.maximum_separations:
        raise FaceParityLimitError("face-separation budget exceeded")
    return value, graph, selected


def bipartite_face_parity(
    face_ids: Iterable[int],
    separations: Iterable[FaceSeparationEvidence],
    anchor_face_id: int,
    *,
    limits: FaceParityLimits = DEFAULT_LIMITS,
) -> Tuple[Tuple[int, int], ...]:
    """Two-color a connected separation graph from an explicit anchor.

    The returned order is for deterministic serialization only.  Parity is
    defined by graph distance from ``anchor_face_id`` and therefore never by
    a node ID, raster scan, or queue order.
    """

    nodes = tuple(sorted({int(item) for item in face_ids}))
    if len(nodes) < 2:
        raise FaceParityAbstention("both parity classes must be witnessed")
    if len(nodes) > limits.maximum_faces:
        raise FaceParityLimitError("face budget exceeded")
    if int(anchor_face_id) not in set(nodes):
        raise FaceParityAbstention("anchor does not select a graph face")

    adjacency: Dict[int, set[int]] = {node: set() for node in nodes}
    edge_count = 0
    node_set = set(nodes)
    for evidence in separations:
        first = int(evidence.first_face_id)
        second = int(evidence.second_face_id)
        if first == second or first not in node_set or second not in node_set:
            raise FaceParityAbstention("invalid face-separation evidence")
        if second not in adjacency[first]:
            adjacency[first].add(second)
            adjacency[second].add(first)
            edge_count += 1
    if edge_count > limits.maximum_separations:
        raise FaceParityLimitError("face-separation budget exceeded")

    parity: Dict[int, int] = {int(anchor_face_id): 0}
    queue = [int(anchor_face_id)]
    cursor = 0
    while cursor < len(queue):
        node = queue[cursor]
        cursor += 1
        expected = 1 - parity[node]
        for neighbor in sorted(adjacency[node]):
            if neighbor not in parity:
                parity[neighbor] = expected
                queue.append(neighbor)
            elif parity[neighbor] != expected:
                raise FaceParityAbstention("face-separation graph is not bipartite")
    if len(parity) != len(nodes):
        raise FaceParityAbstention("face-separation graph is disconnected")
    if set(parity.values()) != {0, 1}:
        raise FaceParityAbstention("both parity classes must be witnessed")
    return tuple(sorted((node, value) for node, value in parity.items()))


def _corner_anchor(graph: PlanarIncidenceGraph) -> Optional[int]:
    height, width = graph.shape
    corners = {
        (0, 0),
        (0, width - 1),
        (height - 1, 0),
        (height - 1, width - 1),
    }
    counts = [
        (sum(cell in corners for cell in face.cells), face.face_id)
        for face in graph.faces
    ]
    maximum = max((count for count, _ in counts), default=0)
    winners = [face_id for count, face_id in counts if count == maximum and count > 0]
    return winners[0] if len(winners) == 1 else None


def _unique_marker_anchor(
    graph: PlanarIncidenceGraph,
    limits: FaceParityLimits,
) -> Optional[int]:
    separating_clusters = {item.cluster_id for item in graph.face_separations}
    markers = [
        boundary
        for boundary in graph.boundaries
        if boundary.area <= limits.maximum_marker_area
        and boundary.cluster_id not in separating_clusters
        and len(boundary.incident_face_ids) == 1
    ]
    if len(markers) != 1:
        return None
    return int(markers[0].incident_face_ids[0])


def _source_color_anchors(graph: PlanarIncidenceGraph) -> Dict[int, int]:
    by_color: Dict[int, set[int]] = {}
    for boundary in graph.boundaries:
        by_color.setdefault(int(boundary.color), set()).update(
            int(item) for item in boundary.incident_face_ids
        )
    return {
        color: next(iter(face_ids))
        for color, face_ids in by_color.items()
        if len(face_ids) == 1
    }


def available_face_anchors(
    graph: PlanarIncidenceGraph,
    *,
    limits: FaceParityLimits = DEFAULT_LIMITS,
) -> Tuple[Tuple[FaceAnchor, int], ...]:
    """Return every uniquely resolved structural anchor for one input graph."""

    output = []
    corner = _corner_anchor(graph)
    if corner is not None:
        output.append((FaceAnchor(CANVAS_CORNERS), int(corner)))
    marker = _unique_marker_anchor(graph, limits)
    if marker is not None:
        output.append((FaceAnchor(UNIQUE_MARKER), int(marker)))
    for color, face_id in _source_color_anchors(graph).items():
        output.append((FaceAnchor(UNIQUE_SOURCE_COLOR_FACE, color), int(face_id)))
    return tuple(sorted(output, key=lambda item: _anchor_sort_key(item[0])))


def _anchor_sort_key(anchor: FaceAnchor) -> Tuple[int, int]:
    return (
        ANCHOR_MODES.index(anchor.mode),
        -1 if anchor.source_color is None else int(anchor.source_color),
    )


def _resolve_anchor(
    graph: PlanarIncidenceGraph,
    anchor: FaceAnchor,
    limits: FaceParityLimits,
) -> int:
    mapping = dict(available_face_anchors(graph, limits=limits))
    if anchor not in mapping:
        raise FaceParityAbstention("held-out input does not uniquely witness the anchor")
    return int(mapping[anchor])


def analyze_anchored_face_parity(
    grid: Array,
    anchor: FaceAnchor,
    *,
    background: Optional[int] = None,
    limits: FaceParityLimits = DEFAULT_LIMITS,
) -> _AnchoredScene:
    """Analyze one grid under an explicit, input-grounded anchor rule."""

    value, graph, selected = _build_graph(grid, background, limits)
    face_id = _resolve_anchor(graph, anchor, limits)
    parity = bipartite_face_parity(
        (face.face_id for face in graph.faces),
        graph.face_separations,
        face_id,
        limits=limits,
    )
    return _AnchoredScene(value, graph, selected, face_id, parity)


def _render_scene(scene: _AnchoredScene, program: FaceParityProgram) -> Array:
    assignments: Dict[Cell, int] = {}
    parity_by_face = dict(scene.parity_by_face)
    for face in scene.graph.faces:
        parity = parity_by_face[face.face_id]
        if program.render_mode == RECOLOR_ONE_PARITY:
            if parity != int(program.target_parity):
                continue
            color = int(program.change_color)
        else:
            color = int(program.even_color if parity == 0 else program.odd_color)
        for cell in face.cells:
            previous = assignments.get(cell)
            if previous is not None and previous != color:
                raise FaceParityAbstention("atomic parity assignments conflict")
            assignments[cell] = color

    # Validate the complete write set before copying or mutating any cell.
    height, width = scene.grid.shape
    if not assignments:
        raise FaceParityAbstention("parity renderer has an empty write set")
    if any(not (0 <= row < height and 0 <= column < width) for row, column in assignments):
        raise FaceParityAbstention("parity assignment falls outside the canvas")
    output = np.array(scene.grid, dtype=np.int64, copy=True)
    for (row, column), color in assignments.items():
        output[row, column] = color
    output.setflags(write=False)
    return output


def apply_face_parity_program(
    grid: Array,
    program: FaceParityProgram,
    *,
    background: Optional[int] = None,
    limits: FaceParityLimits = DEFAULT_LIMITS,
) -> Array:
    """Apply one program atomically to a held-out input."""

    scene = analyze_anchored_face_parity(
        grid,
        program.anchor,
        background=background,
        limits=limits,
    )
    return _render_scene(scene, program)


def _derived_programs(
    source: Array,
    target: Array,
    scene: _AnchoredScene,
    anchor: FaceAnchor,
) -> set[FaceParityProgram]:
    if source.shape != target.shape:
        return set()
    output: set[FaceParityProgram] = set()
    parity_cells = {parity: scene.parity_cells(parity) for parity in (0, 1)}

    # Both-class recoloring: each class must be uniformly colored in output.
    colors: Dict[int, int] = {}
    uniform = True
    for parity, cells in parity_cells.items():
        observed = {int(target[row, column]) for row, column in cells}
        if len(observed) != 1:
            uniform = False
            break
        colors[parity] = next(iter(observed))
    if uniform and colors[0] != colors[1]:
        program = FaceParityProgram(
            anchor,
            RECOLOR_BOTH_PARITIES,
            even_color=colors[0],
            odd_color=colors[1],
        )
        rendered = _render_scene(scene, program)
        if np.array_equal(rendered, target) and not np.array_equal(source, target):
            output.add(program)

    # One-class recoloring: everything outside the selected class is exactly
    # preserved, and the selected class has one demonstration-derived color.
    all_cells = {(row, column) for row in range(source.shape[0]) for column in range(source.shape[1])}
    for parity, cells in parity_cells.items():
        selected = set(cells)
        if any(
            int(source[row, column]) != int(target[row, column])
            for row, column in all_cells - selected
        ):
            continue
        observed = {int(target[row, column]) for row, column in cells}
        if len(observed) != 1:
            continue
        color = next(iter(observed))
        if not any(int(source[row, column]) != color for row, column in cells):
            continue
        program = FaceParityProgram(
            anchor,
            RECOLOR_ONE_PARITY,
            target_parity=parity,
            change_color=color,
        )
        if np.array_equal(_render_scene(scene, program), target):
            output.add(program)
    return output


def _background_vector(
    values: Optional[Sequence[Optional[int]]],
    length: int,
    label: str,
) -> Tuple[Optional[int], ...]:
    if values is None:
        return (None,) * length
    if len(values) != length:
        raise FaceParityError(f"{label} length does not match its grids")
    return tuple(None if item is None else int(item) for item in values)


def compile_face_parity_programs(
    train_examples: Sequence[Tuple[Array, Array]],
    *,
    backgrounds: Optional[Sequence[Optional[int]]] = None,
    limits: FaceParityLimits = DEFAULT_LIMITS,
) -> Tuple[FaceParityProgram, ...]:
    """Compile all bounded programs that exactly fit every demonstration."""

    if not train_examples:
        return ()
    if len(train_examples) > limits.maximum_examples:
        raise FaceParityLimitError("demonstration budget exceeded")
    selected_backgrounds = _background_vector(backgrounds, len(train_examples), "backgrounds")

    prepared = []
    for (source_raw, target_raw), background in zip(train_examples, selected_backgrounds):
        try:
            source, graph, selected = _build_graph(source_raw, background, limits)
            target = _validated_grid(target_raw, limits)
        except FaceParityLimitError:
            raise
        except FaceParityError:
            return ()
        if source.shape != target.shape:
            return ()
        anchors = dict(available_face_anchors(graph, limits=limits))
        if not anchors:
            return ()
        prepared.append((source, target, graph, selected, anchors))

    common_anchors = set(prepared[0][4])
    for item in prepared[1:]:
        common_anchors.intersection_update(item[4])
    if not common_anchors:
        return ()

    exact_sets = []
    for source, target, graph, selected, anchors in prepared:
        programs = set()
        for anchor in common_anchors:
            face_id = int(anchors[anchor])
            try:
                parity = bipartite_face_parity(
                    (face.face_id for face in graph.faces),
                    graph.face_separations,
                    face_id,
                    limits=limits,
                )
                scene = _AnchoredScene(source, graph, selected, face_id, parity)
                programs.update(_derived_programs(source, target, scene, anchor))
            except (FaceParityAbstention, FaceParityLimitError):
                continue
        exact_sets.append(programs)

    common_programs = set.intersection(*exact_sets) if exact_sets else set()
    if len(common_programs) > limits.maximum_programs:
        raise FaceParityLimitError("exact-program budget exceeded")
    return tuple(sorted(common_programs, key=_program_sort_key))


def _program_sort_key(program: FaceParityProgram) -> Tuple[object, ...]:
    record = program.to_record()
    return (program.complexity, json.dumps(record, sort_keys=True))


def _prediction_signature(grids: Sequence[Array]) -> Tuple[Tuple[Tuple[int, ...], Tuple[int, ...]], ...]:
    return tuple(
        (
            tuple(int(item) for item in np.asarray(grid).shape),
            tuple(int(item) for item in np.asarray(grid).ravel(order="C")),
        )
        for grid in grids
    )


def compile_face_parity_candidates(
    train_examples: Sequence[Tuple[Array, Array]],
    test_inputs: Sequence[Array],
    *,
    train_backgrounds: Optional[Sequence[Optional[int]]] = None,
    test_backgrounds: Optional[Sequence[Optional[int]]] = None,
    limits: FaceParityLimits = DEFAULT_LIMITS,
) -> Tuple[FaceParityCandidate, ...]:
    """Return one unambiguous exact candidate, otherwise abstain.

    Multiple syntactic programs may survive exact fitting.  They are allowed
    only when all of them that cover every test input make the same complete
    prediction.  Distinct held-out predictions are an ambiguity, represented
    by an empty candidate tuple rather than an arbitrary tie-break.
    """

    if not test_inputs:
        return ()
    if len(test_inputs) > limits.maximum_examples:
        raise FaceParityLimitError("test-input budget exceeded")
    programs = compile_face_parity_programs(
        train_examples,
        backgrounds=train_backgrounds,
        limits=limits,
    )
    if not programs:
        return ()
    selected_backgrounds = _background_vector(
        test_backgrounds, len(test_inputs), "test_backgrounds"
    )

    by_prediction: Dict[
        Tuple[Tuple[Tuple[int, ...], Tuple[int, ...]], ...],
        list[Tuple[FaceParityProgram, Tuple[Array, ...], Tuple[_AnchoredScene, ...]]],
    ] = {}
    for program in programs:
        grids = []
        scenes = []
        try:
            for grid, background in zip(test_inputs, selected_backgrounds):
                scene = analyze_anchored_face_parity(
                    grid,
                    program.anchor,
                    background=background,
                    limits=limits,
                )
                scenes.append(scene)
                grids.append(_render_scene(scene, program))
        except (FaceParityAbstention, FaceParityLimitError):
            continue
        frozen = tuple(grids)
        by_prediction.setdefault(_prediction_signature(frozen), []).append(
            (program, frozen, tuple(scenes))
        )
    if len(by_prediction) != 1:
        # Zero means no program had a test-defined anchor. More than one means
        # exact demonstrations did not resolve held-out semantics.
        return ()

    equivalent = next(iter(by_prediction.values()))
    program, grids, scenes = min(equivalent, key=lambda item: _program_sort_key(item[0]))
    train_targets = tuple(_immutable_grid(target) for _, target in train_examples)
    metadata: Dict[str, object] = {
        "schema": "planar-face-parity-candidate-metadata-v1",
        "compiler_version": PLANAR_FACE_PARITY_VERSION,
        "quantifier": "FOR_EACH_FACE",
        "relation": "face_separation",
        "parity_origin": "graph_distance_from_input_grounded_anchor",
        "node_id_or_order_anchor": False,
        "literal_output_color_origin": "demonstration_outputs",
        "exact_demonstrations": len(train_examples),
        "covered_test_inputs": len(test_inputs),
        "equivalent_exact_programs": len(equivalent),
        "atomic_scene_application": True,
        "requirements": {
            "connected": True,
            "bipartite": True,
            "both_parities_witnessed": True,
            "unique_test_anchor": True,
        },
        "limits": limits.to_record(),
        "test_graphs": [
            {
                "background": int(scene.background),
                "anchor_feature": _json_safe(scene.normalized_anchor_feature()),
                "graph": scene.graph.normalized_metadata(),
            }
            for scene in scenes
        ],
    }
    candidate = FaceParityCandidate(
        name=f"{FAMILY}:{program.render_mode}:{program.anchor.mode}",
        program=program,
        grids=grids,
        train_grids=train_targets,
        metadata=metadata,
    )
    candidate.to_record(include_grids=False)
    return (candidate,)


def face_parity_candidate_records(
    train_examples: Sequence[Tuple[Array, Array]],
    test_inputs: Sequence[Array],
    **kwargs: object,
) -> Tuple[Dict[str, object], ...]:
    """JSON-safe convenience wrapper around the candidate compiler."""

    candidates = compile_face_parity_candidates(train_examples, test_inputs, **kwargs)
    return tuple(candidate.to_record() for candidate in candidates)
