"""Bounded generic face-effect programs over planar-incidence graphs.

This module is deliberately additive.  It does not import the monolithic ARC
entry module and therefore cannot create an import cycle when an entry-layer
adapter later converts :class:`PlanarEffectCandidate` objects into the
portfolio's native candidate type.

The compiler learns only three small program schemas:

* canvas-side signature to a literal fill or an unchanged face;
* a Boolean face predicate to a literal fill or an unchanged face; and
* a uniquely related boundary or marker colour to a face-background fill.

Every graph is reconstructed from the corresponding input raster.  Target
rasters are used only to fit and exactly verify a finite program.  Rendering
is atomic: all writes are calculated from the immutable source, and
conflicting assignments make the program undefined.
"""

from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json
from typing import Callable, Dict, Iterable, Mapping, Optional, Sequence, Tuple

import numpy as np

try:
    from .planar_incidence import (
        BackgroundFace,
        BoundaryComponent,
        FaceClosureEvidence,
        PlanarIncidenceError,
        PlanarIncidenceGraph,
        build_planar_incidence,
        infer_background,
    )
except ImportError:  # standalone Kaggle runtime
    from planar_incidence import (
        BackgroundFace,
        BoundaryComponent,
        FaceClosureEvidence,
        PlanarIncidenceError,
        PlanarIncidenceGraph,
        build_planar_incidence,
        infer_background,
    )


Array = np.ndarray
Cell = Tuple[int, int]
FaceKey = Tuple[bool, bool, bool, bool]

PLANAR_EFFECT_COMPILER_VERSION = "1.0"
MAX_SIDE = 30
MIN_COLOR = 0
MAX_COLOR = 9


class PlanarEffectError(ValueError):
    """Base class for an undefined bounded face-effect program."""


class AtomicWriteConflict(PlanarEffectError):
    """Raised when two selected roles request different values at one cell."""


class MissingRelatedColor(PlanarEffectError):
    """Raised when a face has no color for an otherwise valid partial relation."""


class AmbiguousRelatedColor(PlanarEffectError):
    """Raised when a face relation supports more than one equally valid color."""


@dataclass(frozen=True)
class FaceAction:
    """One literal face action inferred from demonstration effects."""

    kind: str
    color: Optional[int] = None

    def __post_init__(self) -> None:
        if self.kind not in {"unchanged", "fill_literal"}:
            raise PlanarEffectError(f"unsupported face action {self.kind!r}")
        if self.kind == "unchanged" and self.color is not None:
            raise PlanarEffectError("an unchanged action cannot carry a color")
        if self.kind == "fill_literal":
            _validate_color(self.color)

    def json_record(self) -> Dict[str, object]:
        return {"kind": self.kind, "color": self.color}


@dataclass(frozen=True)
class FaceWrite:
    """A runtime-only write request produced from one freshly parsed face."""

    face_id: int
    cells: Tuple[Cell, ...]
    value: int
    source_kind: str


@dataclass(frozen=True)
class RenderTrace:
    """Coordinate-free summary of one exact atomic rendering execution."""

    selected_faces: int
    unchanged_faces: int
    changed_faces: int
    assigned_cells: int
    changed_cells: int
    selection_signature: str
    relation_signature: str
    output_shape: Tuple[int, int]

    def json_record(self) -> Dict[str, object]:
        return {
            "selected_faces": int(self.selected_faces),
            "unchanged_faces": int(self.unchanged_faces),
            "changed_faces": int(self.changed_faces),
            "assigned_cells": int(self.assigned_cells),
            "changed_cells": int(self.changed_cells),
            "selection_signature": self.selection_signature,
            "relation_signature": self.relation_signature,
            "output_shape": [int(value) for value in self.output_shape],
        }


@dataclass(frozen=True)
class PlanarEffectCandidate:
    """Entry-independent exact candidate returned by the generic compiler."""

    name: str
    grids: Tuple[Array, ...]
    train_grids: Tuple[Array, ...]
    train_error: int
    complexity: int
    family: str
    metadata: Mapping[str, object]

    def __post_init__(self) -> None:
        if self.train_error != 0:
            raise PlanarEffectError("generic planar candidates must fit exactly")
        # Fail at construction time rather than much later in diagnostic JSON.
        json.dumps(dict(self.metadata), sort_keys=True)


@dataclass(frozen=True)
class _Execution:
    grid: Array
    trace: RenderTrace


@dataclass(frozen=True)
class _Program:
    schema: str
    semantic_key: str
    complexity: int
    execute: Callable[[Array, PlanarIncidenceGraph], _Execution]
    metadata: Mapping[str, object]


@dataclass(frozen=True)
class _ProgramContext:
    program: _Program
    train_graphs: Tuple[PlanarIncidenceGraph, ...]
    test_graphs: Tuple[PlanarIncidenceGraph, ...]
    background_policy: str


def _validate_color(color: object) -> int:
    if color is None:
        raise PlanarEffectError("a color value is required")
    value = int(color)
    if value < MIN_COLOR or value > MAX_COLOR:
        raise PlanarEffectError(f"color {value} is outside the ARC palette")
    return value


def _validated_grid(grid: Array) -> Array:
    raw = np.asarray(grid)
    if raw.ndim != 2 or raw.size == 0:
        raise PlanarEffectError("face-effect grids must be nonempty and 2D")
    height, width = raw.shape
    if height > MAX_SIDE or width > MAX_SIDE:
        raise PlanarEffectError("face-effect grid exceeds ARC dimensions")
    if not np.issubdtype(raw.dtype, np.integer):
        if not np.all(np.equal(raw, np.floor(raw))):
            raise PlanarEffectError("face-effect grid contains nonintegral values")
    output = np.array(raw, dtype=np.int16, copy=True)
    if np.any(output < MIN_COLOR) or np.any(output > MAX_COLOR):
        raise PlanarEffectError("face-effect grid contains an invalid ARC color")
    return output


_BACKGROUND_POLICIES: Tuple[str, ...] = (
    "infer_background",
    "zero_if_present",
    "majority",
)


def _background_for_policy(grid: Array, policy: str) -> int:
    source = _validated_grid(grid)
    if policy == "infer_background":
        return _validate_color(infer_background(source))
    if policy == "zero_if_present":
        if not np.any(source == 0):
            raise PlanarEffectError("zero background hypothesis is unavailable")
        return 0
    if policy == "majority":
        values, counts = np.unique(source, return_counts=True)
        maximum = int(np.max(counts))
        winners = [int(value) for value, count in zip(values, counts) if int(count) == maximum]
        if len(winners) != 1:
            raise PlanarEffectError("majority background hypothesis is tied")
        return _validate_color(winners[0])
    raise PlanarEffectError(f"unknown background policy {policy!r}")


def _graphs_for_background_policy(
    grids: Sequence[Array],
    policy: str,
) -> Tuple[PlanarIncidenceGraph, ...]:
    return tuple(
        build_planar_incidence(
            source,
            background=_background_for_policy(source, policy),
        )
        for source in grids
    )


def _exact(left: Array, right: Array) -> bool:
    return bool(
        np.asarray(left).shape == np.asarray(right).shape
        and np.array_equal(np.asarray(left), np.asarray(right))
    )


def _face_mask(shape: Tuple[int, int], cells: Sequence[Cell]) -> Array:
    mask = np.zeros(shape, dtype=bool)
    for row, column in cells:
        mask[int(row), int(column)] = True
    return mask


def _signature(mask: Array, labels: Iterable[str] = ()) -> str:
    digest = hashlib.sha256()
    digest.update(np.ascontiguousarray(mask, dtype=np.uint8).tobytes())
    for label in labels:
        digest.update(b"\0")
        digest.update(str(label).encode("utf-8"))
    return digest.hexdigest()


def _atomic_render(
    source: Array,
    graph: PlanarIncidenceGraph,
    writes: Sequence[FaceWrite],
    *,
    unchanged_face_ids: Sequence[int] = (),
    relation_labels: Sequence[str] = (),
) -> _Execution:
    """Commit immutable-source writes or reject the complete transaction."""

    base = _validated_grid(source)
    if tuple(base.shape) != tuple(graph.shape):
        raise PlanarEffectError("source shape disagrees with incidence graph")
    assignments: Dict[Cell, int] = {}
    selected_mask = np.zeros(base.shape, dtype=bool)
    changed_faces = 0
    for write in writes:
        value = _validate_color(write.value)
        face_changed = False
        for raw_row, raw_column in write.cells:
            row, column = int(raw_row), int(raw_column)
            if not (0 <= row < base.shape[0] and 0 <= column < base.shape[1]):
                raise PlanarEffectError("face write is outside the source grid")
            previous = assignments.get((row, column))
            if previous is not None and previous != value:
                raise AtomicWriteConflict(
                    f"conflicting face writes at {(row, column)}"
                )
            assignments[(row, column)] = value
            selected_mask[row, column] = True
            face_changed = face_changed or int(base[row, column]) != value
        changed_faces += int(face_changed)
    output = base.copy()
    for (row, column), value in assignments.items():
        output[row, column] = value
    changed_mask = output != base
    trace = RenderTrace(
        selected_faces=len({int(write.face_id) for write in writes}),
        unchanged_faces=len({int(value) for value in unchanged_face_ids}),
        changed_faces=int(changed_faces),
        assigned_cells=len(assignments),
        changed_cells=int(np.count_nonzero(changed_mask)),
        selection_signature=_signature(selected_mask),
        relation_signature=_signature(selected_mask, relation_labels),
        output_shape=(int(output.shape[0]), int(output.shape[1])),
    )
    return _Execution(output, trace)


def _observed_face_action(
    source: Array,
    target: Array,
    face: BackgroundFace,
) -> FaceAction:
    source_values = np.asarray([source[row, column] for row, column in face.cells])
    target_values = np.asarray([target[row, column] for row, column in face.cells])
    if np.array_equal(source_values, target_values):
        return FaceAction("unchanged")
    unique = np.unique(target_values)
    if len(unique) != 1:
        raise PlanarEffectError("a face delta is not a uniform literal fill")
    return FaceAction("fill_literal", _validate_color(int(unique[0])))


def _nonface_cells_preserved(
    source: Array,
    target: Array,
    graph: PlanarIncidenceGraph,
) -> bool:
    face_support = np.zeros(source.shape, dtype=bool)
    for face in graph.faces:
        face_support |= _face_mask(source.shape, face.cells)
    return bool(np.array_equal(source[~face_support], target[~face_support]))


def _canvas_side_signature(face: BackgroundFace) -> FaceKey:
    return tuple(bool(value) for value in face.canvas_contacts)  # type: ignore[return-value]


def _canvas_key_name(key: FaceKey) -> str:
    return "".join("1" if value else "0" for value in key)


def _face_is_rectangular(face: BackgroundFace) -> bool:
    top, left, bottom, right = face.box
    return int(face.area) == (int(bottom) - int(top) + 1) * (
        int(right) - int(left) + 1
    )


def _face_contains_canvas_corner(
    face: BackgroundFace,
    shape: Tuple[int, int],
) -> bool:
    height, width = shape
    members = set(face.cells)
    return any(
        corner in members
        for corner in ((0, 0), (0, width - 1), (height - 1, 0), (height - 1, width - 1))
    )


def _face_separation_degree(
    face: BackgroundFace,
    graph: PlanarIncidenceGraph,
) -> int:
    neighbors = set()
    for evidence in graph.face_separations:
        if int(evidence.shared_wall_evidence) <= 0:
            continue
        if int(evidence.first_face_id) == int(face.face_id):
            neighbors.add(int(evidence.second_face_id))
        elif int(evidence.second_face_id) == int(face.face_id):
            neighbors.add(int(evidence.first_face_id))
    return len(neighbors)


def _maximum_face_separation_degree(graph: PlanarIncidenceGraph) -> int:
    return max(
        (_face_separation_degree(face, graph) for face in graph.faces),
        default=0,
    )


def _relative_area_category(
    face: BackgroundFace,
    graph: PlanarIncidenceGraph,
) -> str:
    areas = [int(item.area) for item in graph.faces]
    if not areas or min(areas) == max(areas):
        raise PlanarEffectError("relative face-area extrema are not distinguishable")
    if int(face.area) == min(areas):
        return "ALL_ARGMIN"
    if int(face.area) == max(areas):
        return "ALL_ARGMAX"
    return "MIDDLE"


def _unique_relative_area_category(
    face: BackgroundFace,
    graph: PlanarIncidenceGraph,
) -> str:
    areas = [int(item.area) for item in graph.faces]
    if not areas or min(areas) == max(areas):
        raise PlanarEffectError("unique face-area extrema are not distinguishable")
    minimum, maximum = min(areas), max(areas)
    if areas.count(minimum) != 1 or areas.count(maximum) != 1:
        raise PlanarEffectError("face-area extremum is tied")
    if int(face.area) == minimum:
        return "THE_ARGMIN"
    if int(face.area) == maximum:
        return "THE_ARGMAX"
    return "MIDDLE"


_FACE_PREDICATES: Tuple[Tuple[str, Callable[[BackgroundFace, PlanarIncidenceGraph], bool]], ...] = (
    ("touches_canvas", lambda face, graph: bool(face.touches_canvas)),
    ("enclosed", lambda face, graph: not bool(face.touches_canvas)),
    ("rectangular", lambda face, graph: _face_is_rectangular(face)),
    (
        "rectangular_square",
        lambda face, graph: _face_is_rectangular(face)
        and (int(face.box[2]) - int(face.box[0]))
        == (int(face.box[3]) - int(face.box[1])),
    ),
    (
        "square_rectangular",
        lambda face, graph: _face_is_rectangular(face)
        and (int(face.box[2]) - int(face.box[0]))
        == (int(face.box[3]) - int(face.box[1])),
    ),
    ("nested", lambda face, graph: int(face.containment_depth) > 0),
    (
        "containment_depth_one",
        lambda face, graph: int(face.containment_depth) == 1,
    ),
    (
        "containment_depth_multiple",
        lambda face, graph: int(face.containment_depth) >= 2,
    ),
    (
        "multiple_incident_clusters",
        lambda face, graph: len(face.incident_cluster_ids) >= 2,
    ),
    (
        "single_canvas_side",
        lambda face, graph: sum(bool(value) for value in face.canvas_contacts) == 1,
    ),
    (
        "multiple_canvas_sides",
        lambda face, graph: sum(bool(value) for value in face.canvas_contacts) >= 2,
    ),
    (
        "contains_canvas_corner",
        lambda face, graph: _face_contains_canvas_corner(face, graph.shape),
    ),
    (
        "physical_plus_virtual_closure",
        lambda face, graph: bool(face.touches_canvas)
        and bool(face.incident_cluster_ids),
    ),
    (
        "maximum_face_separation_degree",
        lambda face, graph: _maximum_face_separation_degree(graph) > 0
        and _face_separation_degree(face, graph)
        == _maximum_face_separation_degree(graph),
    ),
    (
        "below_maximum_face_separation_degree",
        lambda face, graph: _maximum_face_separation_degree(graph) > 0
        and _face_separation_degree(face, graph)
        < _maximum_face_separation_degree(graph),
    ),
    (
        "full_cardinal_face_separation_degree",
        lambda face, graph: _face_separation_degree(face, graph) == 4,
    ),
    (
        "border_cardinal_face_separation_degree",
        lambda face, graph: 0 < _face_separation_degree(face, graph) < 4,
    ),
)


def _fit_action_map(
    records: Sequence[Tuple[object, FaceAction]],
) -> Optional[Dict[object, FaceAction]]:
    mapping: Dict[object, FaceAction] = {}
    for key, action in records:
        previous = mapping.get(key)
        if previous is not None and previous != action:
            return None
        mapping[key] = action
    actions = set(mapping.values())
    if len(mapping) < 2:
        return None
    # Multiple categorical branches may all be changed.  What matters is that
    # the demonstrations witness at least two distinct effects rather than a
    # single unconditional fill wearing several selector names.
    if len(actions) < 2:
        return None
    if not any(action.kind == "fill_literal" for action in actions):
        return None
    return mapping


def _literal_program_execution(
    source: Array,
    graph: PlanarIncidenceGraph,
    mapping: Mapping[object, FaceAction],
    key_function: Callable[[BackgroundFace, PlanarIncidenceGraph], object],
    *,
    relation_label: str,
) -> _Execution:
    writes = []
    unchanged = []
    labels = []
    for face in graph.faces:
        key = key_function(face, graph)
        if key not in mapping:
            raise PlanarEffectError("held-out face role was not witnessed")
        action = mapping[key]
        labels.append(f"{key!r}:{action.kind}:{action.color}")
        if action.kind == "unchanged":
            unchanged.append(face.face_id)
        else:
            writes.append(
                FaceWrite(
                    face_id=face.face_id,
                    cells=face.cells,
                    value=_validate_color(action.color),
                    source_kind="demonstrated_literal",
                )
            )
    return _atomic_render(
        source,
        graph,
        writes,
        unchanged_face_ids=unchanged,
        relation_labels=(relation_label, *sorted(labels)),
    )


def _literal_programs(
    train: Sequence[Tuple[Array, Array]],
    train_graphs: Sequence[PlanarIncidenceGraph],
) -> Tuple[_Program, ...]:
    programs = []

    canvas_records = []
    for (source, target), graph in zip(train, train_graphs):
        for face in graph.faces:
            canvas_records.append(
                (_canvas_side_signature(face), _observed_face_action(source, target, face))
            )
    canvas_mapping = _fit_action_map(canvas_records)
    if canvas_mapping is not None:
        mapping = dict(canvas_mapping)
        mapping_json = {
            _canvas_key_name(key): action.json_record()
            for key, action in sorted(mapping.items())
        }
        programs.append(
            _Program(
                schema="canvas_side_signature_literal_fill",
                semantic_key="face|canvas_side_signature|FOR_EACH|literal_or_unchanged",
                complexity=9 + len(mapping),
                execute=lambda source, graph, fitted=mapping: _literal_program_execution(
                    source,
                    graph,
                    fitted,
                    lambda face, _: _canvas_side_signature(face),
                    relation_label="canvas_side_signature",
                ),
                metadata={
                    "selector": "canvas_side_signature",
                    "quantifier": "FOR_EACH",
                    "action_mapping": mapping_json,
                },
            )
        )

    degree_records = []
    for (source, target), graph in zip(train, train_graphs):
        for face in graph.faces:
            degree_records.append(
                (
                    int(_face_separation_degree(face, graph)),
                    _observed_face_action(source, target, face),
                )
            )
    degree_mapping = _fit_action_map(degree_records)
    if degree_mapping is not None:
        mapping = dict(degree_mapping)
        programs.append(
            _Program(
                schema="face_separation_degree_literal_fill",
                semantic_key="face|separation_degree|FOR_EACH|literal_or_unchanged",
                complexity=9 + len(mapping),
                execute=lambda source, graph, fitted=mapping: _literal_program_execution(
                    source,
                    graph,
                    fitted,
                    lambda face, current_graph: int(
                        _face_separation_degree(face, current_graph)
                    ),
                    relation_label="face_separation_degree",
                ),
                metadata={
                    "selector": "exact_face_separation_degree",
                    "quantifier": "FOR_EACH",
                    "action_mapping": {
                        str(int(key)): action.json_record()
                        for key, action in sorted(mapping.items())
                    },
                },
            )
        )

    area_records = []
    tied_extremum_support = False
    middle_support = False
    area_defined = True
    for (source, target), graph in zip(train, train_graphs):
        try:
            categories = [
                _relative_area_category(face, graph) for face in graph.faces
            ]
        except PlanarEffectError:
            area_defined = False
            break
        tied_extremum_support = tied_extremum_support or any(
            categories.count(category) >= 2
            for category in ("ALL_ARGMIN", "ALL_ARGMAX")
        )
        middle_support = middle_support or "MIDDLE" in categories
        for face, category in zip(graph.faces, categories):
            area_records.append(
                (category, _observed_face_action(source, target, face))
            )
    area_mapping = _fit_action_map(area_records) if area_defined else None
    if (
        area_mapping is not None
        and set(area_mapping) == {"ALL_ARGMIN", "MIDDLE", "ALL_ARGMAX"}
        and tied_extremum_support
        and middle_support
    ):
        mapping = dict(area_mapping)
        programs.append(
            _Program(
                schema="relative_face_area_category_literal_fill",
                semantic_key=(
                    "face|relative_area_category|"
                    "ALL_ARGMIN_MIDDLE_ALL_ARGMAX|literal_or_unchanged"
                ),
                complexity=12,
                execute=lambda source, graph, fitted=mapping: _literal_program_execution(
                    source,
                    graph,
                    fitted,
                    lambda face, current_graph: _relative_area_category(
                        face, current_graph
                    ),
                    relation_label="relative_face_area_category",
                ),
                metadata={
                    "selector": "relative_face_area_category",
                    "quantifier": ["ALL_ARGMIN", "MIDDLE", "ALL_ARGMAX"],
                    "tie_policy": "select_all_extrema",
                    "evidence_gate": {
                        "tied_extremum_witnessed": True,
                        "middle_witnessed": True,
                    },
                    "action_mapping": {
                        key: action.json_record()
                        for key, action in sorted(mapping.items())
                    },
                },
            )
        )

    unique_area_records = []
    unique_area_defined = True
    unique_middle_support = False
    for (source, target), graph in zip(train, train_graphs):
        try:
            categories = [
                _unique_relative_area_category(face, graph) for face in graph.faces
            ]
        except PlanarEffectError:
            unique_area_defined = False
            break
        unique_middle_support = unique_middle_support or "MIDDLE" in categories
        for face, category in zip(graph.faces, categories):
            unique_area_records.append(
                (category, _observed_face_action(source, target, face))
            )
    unique_area_mapping = (
        _fit_action_map(unique_area_records) if unique_area_defined else None
    )
    if (
        unique_area_mapping is not None
        and set(unique_area_mapping) == {"THE_ARGMIN", "MIDDLE", "THE_ARGMAX"}
        and unique_middle_support
    ):
        mapping = dict(unique_area_mapping)
        programs.append(
            _Program(
                schema="unique_relative_face_area_category_literal_fill",
                semantic_key=(
                    "face|unique_relative_area_category|"
                    "THE_ARGMIN_MIDDLE_THE_ARGMAX|literal_or_unchanged"
                ),
                complexity=11,
                execute=lambda source, graph, fitted=mapping: _literal_program_execution(
                    source,
                    graph,
                    fitted,
                    lambda face, current_graph: _unique_relative_area_category(
                        face, current_graph
                    ),
                    relation_label="unique_relative_face_area_category",
                ),
                metadata={
                    "selector": "unique_relative_face_area_category",
                    "quantifier": ["THE_ARGMIN", "MIDDLE", "THE_ARGMAX"],
                    "tie_policy": "abstain_on_any_extremum_tie",
                    "evidence_gate": {
                        "unique_extrema_in_every_demonstration": True,
                        "middle_witnessed": True,
                    },
                    "action_mapping": {
                        key: action.json_record()
                        for key, action in sorted(mapping.items())
                    },
                },
            )
        )

    for predicate_name, predicate in _FACE_PREDICATES:
        records = []
        for (source, target), graph in zip(train, train_graphs):
            for face in graph.faces:
                records.append(
                    (bool(predicate(face, graph)), _observed_face_action(source, target, face))
                )
        fitted = _fit_action_map(records)
        if fitted is None or set(fitted) != {False, True}:
            continue
        mapping = dict(fitted)
        programs.append(
            _Program(
                schema="boolean_face_predicate_literal_fill",
                semantic_key=(
                    f"face|boolean:{predicate_name}|FOR_EACH|literal_or_unchanged"
                ),
                complexity=8,
                execute=lambda source, graph, selected=predicate, learned=mapping, name=predicate_name: _literal_program_execution(
                    source,
                    graph,
                    learned,
                    lambda face, current_graph: bool(selected(face, current_graph)),
                    relation_label=f"boolean_face_predicate:{name}",
                ),
                metadata={
                    "selector": predicate_name,
                    "quantifier": "FOR_EACH",
                    "action_mapping": {
                        "false": mapping[False].json_record(),
                        "true": mapping[True].json_record(),
                    },
                },
            )
        )
    return tuple(programs)


def _boundary_colors(
    graph: PlanarIncidenceGraph,
    boundary_ids: Iterable[int],
) -> Tuple[int, ...]:
    by_id: Dict[int, BoundaryComponent] = {
        int(boundary.boundary_id): boundary for boundary in graph.boundaries
    }
    colors = []
    for raw_id in boundary_ids:
        boundary = by_id.get(int(raw_id))
        if boundary is None:
            raise PlanarEffectError("incidence graph references an unknown boundary")
        colors.append(_validate_color(boundary.color))
    return tuple(sorted(set(colors)))


def _cluster_boundary_ids(
    graph: PlanarIncidenceGraph,
    cluster_ids: Iterable[int],
) -> Tuple[int, ...]:
    by_id = {
        int(cluster.cluster_id): cluster for cluster in graph.boundary_clusters
    }
    boundary_ids = []
    for raw_id in cluster_ids:
        cluster = by_id.get(int(raw_id))
        if cluster is None:
            raise PlanarEffectError("incidence graph references an unknown cluster")
        boundary_ids.extend(int(value) for value in cluster.boundary_ids)
    return tuple(sorted(set(boundary_ids)))


def _face_closure(
    graph: PlanarIncidenceGraph,
    face_id: int,
) -> FaceClosureEvidence:
    matches = [
        closure for closure in graph.face_closures if int(closure.face_id) == int(face_id)
    ]
    if len(matches) != 1:
        raise PlanarEffectError("face closure evidence is not unique")
    return matches[0]


def _unique_dominant_boundary_color(graph: PlanarIncidenceGraph) -> int:
    support: Dict[int, int] = {}
    for boundary in graph.boundaries:
        color = _validate_color(boundary.color)
        support[color] = support.get(color, 0) + int(boundary.area)
    if not support:
        raise PlanarEffectError("scene has no physical boundary colors")
    maximum = max(support.values())
    winners = [color for color, area in support.items() if area == maximum]
    if len(winners) != 1:
        raise PlanarEffectError("global structural boundary color is tied")
    return int(winners[0])


def _modal_incident_nonstructural_color(
    graph: PlanarIncidenceGraph,
    face: BackgroundFace,
) -> int:
    structural_color = _unique_dominant_boundary_color(graph)
    by_boundary = {
        int(boundary.boundary_id): boundary for boundary in graph.boundaries
    }
    contact_by_color: Dict[int, int] = {}
    for incidence in graph.face_boundary_incidence:
        if int(incidence.face_id) != int(face.face_id):
            continue
        boundary = by_boundary.get(int(incidence.boundary_id))
        if boundary is None:
            raise PlanarEffectError("face incidence names an unknown boundary")
        color = _validate_color(boundary.color)
        if color == structural_color:
            continue
        shared_wall = int(incidence.shared_wall)
        if shared_wall <= 0:
            continue
        contact_by_color[color] = contact_by_color.get(color, 0) + shared_wall
    if not contact_by_color:
        raise MissingRelatedColor("face has no nonstructural incident color")
    maximum = max(contact_by_color.values())
    winners = [
        color for color, contact in contact_by_color.items() if contact == maximum
    ]
    if len(winners) != 1:
        raise AmbiguousRelatedColor("modal nonstructural face color is tied")
    return int(winners[0])


def _related_color(
    graph: PlanarIncidenceGraph,
    face: BackgroundFace,
    relation: str,
) -> int:
    if relation == "incident_boundary":
        boundary_ids = tuple(int(value) for value in face.incident_boundary_ids)
    elif relation == "containing_boundary":
        boundary_ids = _cluster_boundary_ids(graph, face.containing_cluster_ids)
    elif relation == "closure_boundary":
        boundary_ids = _cluster_boundary_ids(
            graph,
            _face_closure(graph, face.face_id).physical_cluster_ids,
        )
    elif relation == "interior_marker_boundary":
        containing = set(
            _cluster_boundary_ids(graph, face.containing_cluster_ids)
        )
        boundary_ids = tuple(
            int(boundary_id)
            for boundary_id in face.incident_boundary_ids
            if int(boundary_id) not in containing
        )
    elif relation == "modal_incident_nonstructural_color":
        return _modal_incident_nonstructural_color(graph, face)
    else:
        raise PlanarEffectError(f"unknown face-color relation {relation!r}")
    colors = _boundary_colors(graph, boundary_ids)
    if not colors:
        raise MissingRelatedColor("related boundary color is absent")
    if len(colors) != 1:
        raise AmbiguousRelatedColor("related boundary color is ambiguous")
    return int(colors[0])


_FACE_SCOPES: Tuple[Tuple[str, Callable[[BackgroundFace], bool]], ...] = (
    ("all", lambda face: True),
    ("enclosed", lambda face: not bool(face.touches_canvas)),
    ("canvas", lambda face: bool(face.touches_canvas)),
)

_COLOR_RELATIONS: Tuple[str, ...] = (
    "incident_boundary",
    "containing_boundary",
    "closure_boundary",
    "interior_marker_boundary",
    "modal_incident_nonstructural_color",
)


def _boundary_color_statistics(
    graph: PlanarIncidenceGraph,
) -> Dict[int, Dict[str, int]]:
    statistics: Dict[int, Dict[str, int]] = {}
    boundary_colors: Dict[int, int] = {}
    for boundary in graph.boundaries:
        color = _validate_color(boundary.color)
        boundary_colors[int(boundary.boundary_id)] = color
        record = statistics.setdefault(
            color,
            {"area": 0, "components": 0, "cardinal_contact": 0},
        )
        record["area"] += int(boundary.area)
        record["components"] += 1
    for incidence in graph.face_boundary_incidence:
        color = boundary_colors.get(int(incidence.boundary_id))
        if color is not None:
            statistics[color]["cardinal_contact"] += int(incidence.shared_wall)
    return statistics


def _unique_color_extremum(
    graph: PlanarIncidenceGraph,
    attribute: str,
    maximum: bool,
) -> int:
    statistics = _boundary_color_statistics(graph)
    if len(statistics) < 2:
        raise PlanarEffectError("color-role selection requires competing colors")
    values = {color: record[attribute] for color, record in statistics.items()}
    target = max(values.values()) if maximum else min(values.values())
    winners = [color for color, value in values.items() if value == target]
    if len(winners) != 1:
        raise PlanarEffectError("boundary color role is tied")
    return int(winners[0])


_BOUNDARY_COLOR_ROLES: Tuple[Tuple[str, str, bool], ...] = (
    ("unique_argmax_total_support", "area", True),
    ("unique_argmin_total_support", "area", False),
    ("unique_argmax_component_count", "components", True),
    ("unique_argmin_component_count", "components", False),
    ("unique_argmax_cardinal_contact", "cardinal_contact", True),
    ("unique_argmin_cardinal_contact", "cardinal_contact", False),
)


def _color_role_value(graph: PlanarIncidenceGraph, role: str) -> int:
    for name, attribute, maximum in _BOUNDARY_COLOR_ROLES:
        if role == name:
            return _unique_color_extremum(graph, attribute, maximum)
    raise PlanarEffectError(f"unknown boundary color role {role!r}")


def _faces_cardinally_incident_to_color(
    graph: PlanarIncidenceGraph,
    color: int,
) -> Tuple[int, ...]:
    boundary_colors = {
        int(boundary.boundary_id): _validate_color(boundary.color)
        for boundary in graph.boundaries
    }
    selected = {
        int(incidence.face_id)
        for incidence in graph.face_boundary_incidence
        if int(incidence.shared_wall) > 0
        and boundary_colors.get(int(incidence.boundary_id)) == int(color)
    }
    return tuple(sorted(selected))


def _color_role_incident_execution(
    source: Array,
    graph: PlanarIncidenceGraph,
    role: str,
) -> _Execution:
    color = _color_role_value(graph, role)
    selected_ids = set(_faces_cardinally_incident_to_color(graph, color))
    if not selected_ids or len(selected_ids) == len(graph.faces):
        raise PlanarEffectError(
            "color-role face fill requires positive and negative face support"
        )
    writes = [
        FaceWrite(
            face_id=face.face_id,
            cells=face.cells,
            value=color,
            source_kind=f"boundary_color_role:{role}",
        )
        for face in graph.faces
        if int(face.face_id) in selected_ids
    ]
    unchanged = [
        int(face.face_id)
        for face in graph.faces
        if int(face.face_id) not in selected_ids
    ]
    return _atomic_render(
        source,
        graph,
        writes,
        unchanged_face_ids=unchanged,
        relation_labels=(
            "cardinally_incident_to_boundary_color_role",
            role,
            f"selected_faces:{len(selected_ids)}",
        ),
    )


def _color_role_incident_programs(
    train_graphs: Sequence[PlanarIncidenceGraph],
    test_graphs: Sequence[PlanarIncidenceGraph],
) -> Tuple[_Program, ...]:
    programs = []
    for role, _, _ in _BOUNDARY_COLOR_ROLES:
        try:
            train_counts = []
            for graph in train_graphs:
                color = _color_role_value(graph, role)
                selected = _faces_cardinally_incident_to_color(graph, color)
                if not selected or len(selected) == len(graph.faces):
                    raise PlanarEffectError("missing positive or negative face branch")
                train_counts.append(len(selected))
            for graph in test_graphs:
                color = _color_role_value(graph, role)
                selected = _faces_cardinally_incident_to_color(graph, color)
                if not selected or len(selected) == len(graph.faces):
                    raise PlanarEffectError("held-out color role lacks both branches")
            if len(set(train_counts)) < 2:
                continue
        except (PlanarEffectError, PlanarIncidenceError, TypeError, ValueError):
            continue
        programs.append(
            _Program(
                schema="color_role_incident_face_fill",
                semantic_key=(
                    f"face|FOR_EACH|cardinal_incident_color_role:{role}|"
                    "fill_role_color"
                ),
                complexity=11,
                execute=lambda source, graph, selected_role=role: _color_role_incident_execution(
                    source,
                    graph,
                    selected_role,
                ),
                metadata={
                    "selector": "cardinally_incident_to_boundary_color_role",
                    "quantifier": "FOR_EACH",
                    "relation": "cardinal_face_boundary_contact",
                    "color_role": role,
                    "color_source": "test_input_boundary_color_role",
                    "evidence_gate": {
                        "positive_faces": True,
                        "negative_faces": True,
                        "selected_cardinality_varies": True,
                    },
                },
            )
        )
    return tuple(programs)


def _literal_color_incident_execution(
    source: Array,
    graph: PlanarIncidenceGraph,
    color: int,
) -> _Execution:
    value = _validate_color(color)
    selected_ids = set(_faces_cardinally_incident_to_color(graph, value))
    if not selected_ids or len(selected_ids) == len(graph.faces):
        raise PlanarEffectError(
            "literal-color face fill requires positive and negative face support"
        )
    writes = [
        FaceWrite(
            face_id=face.face_id,
            cells=face.cells,
            value=value,
            source_kind="demonstrated_literal_input_color",
        )
        for face in graph.faces
        if int(face.face_id) in selected_ids
    ]
    unchanged = [
        int(face.face_id)
        for face in graph.faces
        if int(face.face_id) not in selected_ids
    ]
    return _atomic_render(
        source,
        graph,
        writes,
        unchanged_face_ids=unchanged,
        relation_labels=(
            "cardinally_incident_to_literal_input_color",
            f"literal_color:{value}",
        ),
    )


def _literal_color_incident_programs(
    train: Sequence[Tuple[Array, Array]],
    tests: Sequence[Array],
    train_graphs: Sequence[PlanarIncidenceGraph],
    test_graphs: Sequence[PlanarIncidenceGraph],
) -> Tuple[_Program, ...]:
    color_sets = [
        {int(value) for value in np.unique(source)}
        for source, _ in train
    ] + [{int(value) for value in np.unique(source)} for source in tests]
    if not color_sets:
        return ()
    common = sorted(set.intersection(*color_sets))
    programs = []
    for color in common:
        try:
            for graph in (*train_graphs, *test_graphs):
                if int(graph.background) == int(color):
                    raise PlanarEffectError("literal role cannot be the background")
                if not any(
                    int(boundary.color) == int(color)
                    for boundary in graph.boundaries
                ):
                    raise PlanarEffectError("literal role is not a boundary color")
                selected = _faces_cardinally_incident_to_color(graph, color)
                if not selected or len(selected) == len(graph.faces):
                    raise PlanarEffectError("literal role lacks both face branches")
        except (PlanarEffectError, PlanarIncidenceError, TypeError, ValueError):
            continue
        programs.append(
            _Program(
                schema="literal_color_incident_face_fill",
                semantic_key=(
                    f"face|FOR_EACH|cardinal_incident_literal_color:{color}|"
                    "fill_same_color"
                ),
                complexity=12,
                execute=lambda source, graph, value=color: _literal_color_incident_execution(
                    source,
                    graph,
                    value,
                ),
                metadata={
                    "selector": "cardinally_incident_to_literal_input_color",
                    "quantifier": "FOR_EACH",
                    "relation": "cardinal_face_boundary_contact",
                    "literal_input_color": int(color),
                    "color_source": "demonstrated_literal_present_in_every_input",
                    "palette_relative": False,
                    "requires_unique_exact_literal_color": True,
                },
            )
        )
    return tuple(programs)


def _related_color_execution(
    source: Array,
    graph: PlanarIncidenceGraph,
    relation: str,
    scope_name: str,
    scope: Callable[[BackgroundFace], bool],
) -> _Execution:
    writes = []
    unchanged = []
    relation_labels = []
    for face in graph.faces:
        if not bool(scope(face)):
            unchanged.append(face.face_id)
            continue
        try:
            color = _related_color(graph, face, relation)
        except MissingRelatedColor:
            unchanged.append(face.face_id)
            continue
        writes.append(
            FaceWrite(
                face_id=face.face_id,
                cells=face.cells,
                value=color,
                source_kind=f"unique_related_color:{relation}",
            )
        )
        relation_labels.append(f"face:{relation}:unique_color")
    if not writes:
        raise PlanarEffectError("related-color program selected no faces")
    return _atomic_render(
        source,
        graph,
        writes,
        unchanged_face_ids=unchanged,
        relation_labels=(relation, scope_name, *relation_labels),
    )


def _related_color_programs() -> Tuple[_Program, ...]:
    programs = []
    for relation in _COLOR_RELATIONS:
        for scope_name, scope in _FACE_SCOPES:
            semantic_key = (
                f"face|{scope_name}|FOR_EACH|unique_{relation}_color|fill_background"
            )
            programs.append(
                _Program(
                    schema="unique_related_color_face_fill",
                    semantic_key=semantic_key,
                    complexity=9 + int(scope_name != "all") + int("marker" in relation),
                    execute=lambda source, graph, rel=relation, scope_key=scope_name, selected=scope: _related_color_execution(
                        source,
                        graph,
                        rel,
                        scope_key,
                        selected,
                    ),
                    metadata={
                        "selector": scope_name,
                        "quantifier": "FOR_EACH",
                        "relation": relation,
                        "color_source": "unique_related_input_boundary_color",
                    },
                )
            )
    return tuple(programs)


def _effect_evidence(
    train: Sequence[Tuple[Array, Array]],
    executions: Sequence[_Execution],
) -> Dict[str, object]:
    changed_cells = 0
    target_delta_cells = 0
    selected_faces = 0
    unchanged_faces = 0
    changed_faces = 0
    for (source, target), execution in zip(train, executions):
        delta = np.asarray(source) != np.asarray(target)
        predicted_delta = np.asarray(source) != np.asarray(execution.grid)
        if not np.array_equal(delta, predicted_delta):
            raise PlanarEffectError("render trace does not cover the exact target delta")
        changed_cells += int(execution.trace.changed_cells)
        target_delta_cells += int(np.count_nonzero(delta))
        selected_faces += int(execution.trace.selected_faces)
        unchanged_faces += int(execution.trace.unchanged_faces)
        changed_faces += int(execution.trace.changed_faces)
    if changed_cells <= 0 or changed_faces <= 0:
        raise PlanarEffectError("face-effect program is vacuous")
    return {
        "demonstrations": len(train),
        "selected_faces": selected_faces,
        "unchanged_faces": unchanged_faces,
        "changed_faces": changed_faces,
        "changed_cells": changed_cells,
        "target_delta_cells": target_delta_cells,
        "delta_coverage_complete": changed_cells == target_delta_cells,
        "spill_cells": 0,
        "write_conflicts": 0,
    }


def _candidate_from_program(
    program: _Program,
    train: Sequence[Tuple[Array, Array]],
    tests: Sequence[Array],
    train_graphs: Sequence[PlanarIncidenceGraph],
    test_graphs: Sequence[PlanarIncidenceGraph],
    background_policy: str,
) -> PlanarEffectCandidate:
    train_executions = tuple(
        program.execute(source, graph)
        for (source, _), graph in zip(train, train_graphs)
    )
    if not all(
        _exact(execution.grid, target)
        for execution, (_, target) in zip(train_executions, train)
    ):
        raise PlanarEffectError("program does not exactly fit every demonstration")
    test_executions = tuple(
        program.execute(source, graph) for source, graph in zip(tests, test_graphs)
    )
    evidence = _effect_evidence(train, train_executions)
    metadata: Dict[str, object] = {
        "compiler_block": "causal_planar_face_effect_1_4",
        "compiler_version": PLANAR_EFFECT_COMPILER_VERSION,
        "incidence_version": "1.0",
        "schema": program.schema,
        "typed_entity": "background_face",
        "domain": "planar_incidence_faces",
        "renderer": "immutable_source_atomic_face_background_fill",
        "action": "witnessed_categorical_or_dynamic_face_fill",
        "output_shape_contract": "same_as_test_input",
        "shape_source": "test_input_grid",
        "effect_conditioned": True,
        "effect_evidence": evidence,
        "background_policy": background_policy,
        "semantic_mechanism_key": (
            f"{program.semantic_key}|background:{background_policy}"
        ),
        "version_space_key": (
            f"{program.semantic_key}|background:{background_policy}"
        ),
        "train_graph_digests": [graph.normalized_digest() for graph in train_graphs],
        "test_graph_digests": [graph.normalized_digest() for graph in test_graphs],
        "train_render_traces": [
            execution.trace.json_record() for execution in train_executions
        ],
        "test_render_traces": [
            execution.trace.json_record() for execution in test_executions
        ],
        "output_lineage": {
            "kind": "test_input_planar_face_transform",
            "preserved_cells": "immutable_test_input",
            "written_cells": "selected_test_input_face_background_cells",
            "value_source": (
                "demonstrated_literal_or_test_input_related_boundary_color"
            ),
        },
        "provenance_kind": "test_input_planar_incidence_transform",
        "test_input_grounded": True,
        "permutation_invariant": True,
        "admissible": True,
        "partial_program": True,
        "undefined_policy": "abstain",
        "undefined_when": [
            "background_is_ambiguous",
            "face_role_is_unwitnessed",
            "related_color_is_absent_or_ambiguous",
            "atomic_writes_conflict",
            "output_shape_or_palette_is_invalid",
        ],
        "stores_coordinates": False,
        "stores_task_ids": False,
        "stores_training_rasters": False,
        "stores_numeric_thresholds": False,
        "exact_demonstration_contract": True,
        "generic_candidate": True,
        "empirical_promotion_eligible": False,
        **dict(program.metadata),
    }
    family = (
        "causal_planar_face_related_color"
        if program.schema
        in {
            "unique_related_color_face_fill",
            "color_role_incident_face_fill",
            "literal_color_incident_face_fill",
        }
        else "causal_planar_face_literal_effect"
    )
    return PlanarEffectCandidate(
        name=(
            f"planar_effect:{program.semantic_key}|background:{background_policy}"
        ),
        grids=tuple(execution.grid.copy() for execution in test_executions),
        train_grids=tuple(execution.grid.copy() for execution in train_executions),
        train_error=0,
        complexity=int(program.complexity),
        family=family,
        metadata=metadata,
    )


def _behavior_key(candidate: PlanarEffectCandidate) -> Tuple[Tuple[object, ...], ...]:
    values = (*candidate.train_grids, *candidate.grids)
    return tuple(
        (
            int(grid.shape[0]),
            int(grid.shape[1]),
            hashlib.sha256(np.ascontiguousarray(grid).tobytes()).hexdigest(),
        )
        for grid in values
    )


def compile_planar_face_effects(
    train: Sequence[Tuple[Array, Array]],
    tests: Sequence[Array],
    *,
    maximum_programs: int = 256,
    maximum_exact: int = 16,
) -> Tuple[PlanarEffectCandidate, ...]:
    """Compile exact bounded face-effect candidates and otherwise abstain.

    Program and exact-output caps are deterministic.  Full observed behavior,
    including every test prediction, is used for alias quotienting, so exact
    programs that diverge on a held-out input remain separate candidates.
    """

    if len(train) < 2 or not tests:
        return ()
    try:
        normalized_train = tuple(
            (_validated_grid(source), _validated_grid(target))
            for source, target in train
        )
        normalized_tests = tuple(_validated_grid(source) for source in tests)
        if any(source.shape != target.shape for source, target in normalized_train):
            return ()
    except (PlanarEffectError, PlanarIncidenceError, TypeError, ValueError):
        return ()

    # Background choice is an explicit input-only version-space coordinate.
    # Each policy builds and executes its own graphs; aliases are collapsed
    # only after complete train and held-out behavior has been observed.
    by_schema: Dict[str, list[_ProgramContext]] = {
        "categorical": [],
        "boolean": [],
        "related": [],
    }
    for background_policy in _BACKGROUND_POLICIES:
        try:
            train_graphs = _graphs_for_background_policy(
                [source for source, _ in normalized_train],
                background_policy,
            )
            test_graphs = _graphs_for_background_policy(
                normalized_tests,
                background_policy,
            )
            if any(
                not _nonface_cells_preserved(source, target, graph)
                for (source, target), graph in zip(normalized_train, train_graphs)
            ):
                continue
            literal_programs = _literal_programs(normalized_train, train_graphs)
        except (PlanarEffectError, PlanarIncidenceError, TypeError, ValueError):
            continue
        for program in literal_programs:
            schema = (
                "boolean"
                if program.schema == "boolean_face_predicate_literal_fill"
                else "categorical"
            )
            by_schema[schema].append(
                _ProgramContext(
                    program,
                    train_graphs,
                    test_graphs,
                    background_policy,
                )
            )
        for program in (
            *_related_color_programs(),
            *_color_role_incident_programs(train_graphs, test_graphs),
            *_literal_color_incident_programs(
                normalized_train,
                normalized_tests,
                train_graphs,
                test_graphs,
            ),
        ):
            by_schema["related"].append(
                _ProgramContext(
                    program,
                    train_graphs,
                    test_graphs,
                    background_policy,
                )
            )

    contexts = []
    depth = 0
    limit = max(1, int(maximum_programs))
    while len(contexts) < limit:
        added = False
        for schema in ("categorical", "boolean", "related"):
            values = by_schema[schema]
            if depth < len(values):
                contexts.append(values[depth])
                added = True
                if len(contexts) >= limit:
                    break
        if not added:
            break
        depth += 1

    exact = []
    for context in contexts:
        try:
            candidate = _candidate_from_program(
                context.program,
                normalized_train,
                normalized_tests,
                context.train_graphs,
                context.test_graphs,
                context.background_policy,
            )
        except (PlanarEffectError, PlanarIncidenceError, TypeError, ValueError):
            continue
        exact.append(candidate)

    exact_literal_colors = {
        int(candidate.metadata["literal_input_color"])
        for candidate in exact
        if candidate.metadata.get("schema") == "literal_color_incident_face_fill"
    }
    if len(exact_literal_colors) > 1:
        exact = [
            candidate
            for candidate in exact
            if candidate.metadata.get("schema")
            != "literal_color_incident_face_fill"
        ]
    elif len(exact_literal_colors) == 1:
        certified = []
        for candidate in exact:
            if candidate.metadata.get("schema") != "literal_color_incident_face_fill":
                certified.append(candidate)
                continue
            metadata = dict(candidate.metadata)
            metadata["sole_exact_literal_input_color"] = True
            certified.append(
                PlanarEffectCandidate(
                    name=candidate.name,
                    grids=tuple(grid.copy() for grid in candidate.grids),
                    train_grids=tuple(
                        grid.copy() for grid in candidate.train_grids
                    ),
                    train_error=0,
                    complexity=candidate.complexity,
                    family=candidate.family,
                    metadata=metadata,
                )
            )
        exact = certified

    # Quotient only complete observed behaviors.  Semantic alternatives that
    # agree on demonstrations but diverge on tests are intentionally retained.
    groups: Dict[Tuple[Tuple[object, ...], ...], list[PlanarEffectCandidate]] = {}
    for candidate in exact:
        groups.setdefault(_behavior_key(candidate), []).append(candidate)
    result = []
    for key in sorted(groups, key=repr):
        aliases = sorted(
            groups[key], key=lambda item: (item.complexity, item.family, item.name)
        )
        chosen = aliases[0]
        metadata = dict(chosen.metadata)
        metadata["semantic_alias_count"] = len(aliases)
        metadata["semantic_aliases"] = [item.name for item in aliases]
        result.append(
            PlanarEffectCandidate(
                name=chosen.name,
                grids=tuple(grid.copy() for grid in chosen.grids),
                train_grids=tuple(grid.copy() for grid in chosen.train_grids),
                train_error=0,
                complexity=chosen.complexity,
                family=chosen.family,
                metadata=metadata,
            )
        )
    result.sort(key=lambda item: (item.complexity, item.family, item.name))
    return tuple(result[: max(1, int(maximum_exact))])


__all__ = [
    "AmbiguousRelatedColor",
    "AtomicWriteConflict",
    "FaceAction",
    "FaceWrite",
    "MissingRelatedColor",
    "PLANAR_EFFECT_COMPILER_VERSION",
    "PlanarEffectCandidate",
    "PlanarEffectError",
    "RenderTrace",
    "compile_planar_face_effects",
]
