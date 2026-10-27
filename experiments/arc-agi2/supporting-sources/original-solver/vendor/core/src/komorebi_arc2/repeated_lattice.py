"""Bounded, input-only quotient graphs for repeated separator lattices.

This module recognizes a deliberately narrow but useful ARC representation:
full foreground row and column bands divide an input raster into an ordered
lattice of faces.  The raster geometry remains available in the runtime
objects, while :meth:`RepeatedLatticeQuotient.symbolic_trace` compiles only
lattice-relative facts.  In particular, a compiled trace never contains
absolute cell coordinates, bounding boxes, or raster offsets.

The recognizer is conservative.  It abstains on a missing axis of separators,
unequal face extents (a common symptom of a broken separator), large
off-lattice objects, ambiguous background choices, and every configured
resource overflow.  It never looks at a demonstration output and it does not
implement an output rule.
"""

from __future__ import annotations

from collections import Counter, deque
from dataclasses import dataclass, replace
import json
from typing import Dict, Iterable, List, Optional, Sequence, Tuple

import numpy as np


Array = np.ndarray
Cell = Tuple[int, int]
Box = Tuple[int, int, int, int]  # inclusive top, left, bottom, right
Span = Tuple[int, int]  # half-open

REPEATED_LATTICE_VERSION = "1.0"


class RepeatedLatticeError(ValueError):
    """Base class for an explicit repeated-lattice abstention."""


class AmbiguousLatticeBackgroundError(RepeatedLatticeError):
    """Raised when more than one background yields equal structural support."""


class MissingSeparatorError(RepeatedLatticeError):
    """Raised when both physical separator axes are not present."""


class IrregularLatticeError(RepeatedLatticeError):
    """Raised when separator evidence does not form repeated face extents."""


class OffLatticeNoiseError(RepeatedLatticeError):
    """Raised when residual foreground cannot be treated as bounded markers."""


class RepeatedLatticeLimitError(RepeatedLatticeError):
    """Raised before a configured resource cap would be exceeded."""


@dataclass(frozen=True)
class LatticeLimits:
    """Hard resource bounds for one input raster."""

    maximum_height: int = 30
    maximum_width: int = 30
    maximum_palette: int = 32
    maximum_row_bands: int = 15
    maximum_column_bands: int = 15
    maximum_faces: int = 144
    maximum_markers: int = 64
    maximum_marker_area: int = 16
    maximum_marker_cells: int = 128
    maximum_shared_walls: int = 512
    maximum_marker_band_relations: int = 2048


DEFAULT_LIMITS = LatticeLimits()


@dataclass(frozen=True)
class SeparatorBand:
    """One maximal, full-foreground row or column band.

    ``start``, ``stop``, and ``cells`` are runtime evidence.  They are omitted
    from every compiled symbolic trace.
    """

    axis: str
    band_id: int
    lattice_index: int
    start: int
    stop: int
    thickness: int
    cells: Tuple[Cell, ...]
    color_count: int
    color_area_profile: Tuple[int, ...]


@dataclass(frozen=True)
class LatticeFace:
    """One open face cell in row-major lattice order."""

    face_id: int
    lattice_row: int
    lattice_column: int
    row_start: int
    row_stop: int
    column_start: int
    column_stop: int
    cells: Tuple[Cell, ...]
    face_class: str
    marker_ids: Tuple[int, ...]
    neighbor_face_ids: Tuple[int, ...]

    @property
    def is_border(self) -> bool:
        """Whether this face touches the quotient's outer lattice boundary."""

        return self.face_class != "interior"


@dataclass(frozen=True)
class SharedWall:
    """Incidence between two orthogonally adjacent lattice faces."""

    wall_id: int
    first_face_id: int
    second_face_id: int
    axis: str
    separator_band_id: int
    thickness: int
    contact_length: int


@dataclass(frozen=True)
class LatticeMarker:
    """A bounded monochrome residual object contained by one face."""

    marker_id: int
    color: int
    cells: Tuple[Cell, ...]
    bounding_box: Box
    area: int
    face_id: int
    lattice_row: int
    lattice_column: int
    shape_signature: Tuple[int, ...]
    same_color_multiplicity: int


@dataclass(frozen=True)
class MarkerBandRelation:
    """Exact relation from one marker to one physical separator band."""

    relation_id: int
    marker_id: int
    axis: str
    direction: str
    separator_band_id: int
    band_lattice_index: int
    relative_face_offset: int
    gap: int
    touches: bool
    adjacent_to_face: bool
    orthogonal_overlap: int
    band_thickness: int


@dataclass(frozen=True)
class RepeatedLatticeQuotient:
    """Runtime quotient graph for a repeated separator lattice."""

    shape: Tuple[int, int]
    background: int
    lattice_shape: Tuple[int, int]
    face_shape: Tuple[int, int]
    row_bands: Tuple[SeparatorBand, ...]
    column_bands: Tuple[SeparatorBand, ...]
    faces: Tuple[LatticeFace, ...]
    shared_walls: Tuple[SharedWall, ...]
    markers: Tuple[LatticeMarker, ...]
    marker_band_relations: Tuple[MarkerBandRelation, ...]

    def face_at(self, lattice_row: int, lattice_column: int) -> LatticeFace:
        """Return the face at a lattice coordinate."""

        rows, columns = self.lattice_shape
        if not (0 <= lattice_row < rows and 0 <= lattice_column < columns):
            raise IndexError("lattice coordinate is outside the quotient")
        return self.faces[lattice_row * columns + lattice_column]

    def symbolic_trace(self) -> Dict[str, object]:
        """Compile an oriented, JSON-safe trace without absolute coordinates."""

        face_coordinates = {
            face.face_id: [face.lattice_row, face.lattice_column] for face in self.faces
        }
        row_profile = [_band_trace(band) for band in self.row_bands]
        column_profile = [_band_trace(band) for band in self.column_bands]
        trace: Dict[str, object] = {
            "schema": "repeated_lattice_quotient.v1",
            "lattice_shape": list(self.lattice_shape),
            "face_shape": list(self.face_shape),
            "separator_profiles": {
                "row": row_profile,
                "column": column_profile,
            },
            "faces": [
                {
                    "face_id": face.face_id,
                    "lattice_coordinate": [face.lattice_row, face.lattice_column],
                    "face_class": face.face_class,
                    "is_border": face.is_border,
                    "marker_ids": list(face.marker_ids),
                    "neighbors": [face_coordinates[item] for item in face.neighbor_face_ids],
                }
                for face in self.faces
            ],
            "shared_walls": [
                {
                    "wall_id": wall.wall_id,
                    "face_coordinates": [
                        face_coordinates[wall.first_face_id],
                        face_coordinates[wall.second_face_id],
                    ],
                    "axis": wall.axis,
                    "band_lattice_index": _wall_band(self, wall).lattice_index,
                    "thickness": wall.thickness,
                    "contact_length": wall.contact_length,
                }
                for wall in self.shared_walls
            ],
            "markers": [
                {
                    "marker_id": marker.marker_id,
                    "face_coordinate": [marker.lattice_row, marker.lattice_column],
                    "area": marker.area,
                    "shape_signature": list(marker.shape_signature),
                    "same_color_multiplicity": marker.same_color_multiplicity,
                }
                for marker in self.markers
            ],
            "marker_band_relations": [
                {
                    "relation_id": relation.relation_id,
                    "marker_id": relation.marker_id,
                    "axis": relation.axis,
                    "direction": relation.direction,
                    "band_lattice_index": relation.band_lattice_index,
                    "relative_face_offset": relation.relative_face_offset,
                    "gap": relation.gap,
                    "touches": relation.touches,
                    "adjacent_to_face": relation.adjacent_to_face,
                    "orthogonal_overlap": relation.orthogonal_overlap,
                    "band_thickness": relation.band_thickness,
                }
                for relation in self.marker_band_relations
            ],
        }
        # Keep the JSON contract executable rather than documentary.
        json.dumps(trace, sort_keys=True, separators=(",", ":"))
        return trace

    def normalized_summary(self) -> Dict[str, object]:
        """Return a JSON-safe D4- and palette-invariant structural summary.

        This summary intentionally forgets orientation.  The oriented
        :meth:`symbolic_trace` remains available when a later symbolic rule
        needs exact lattice coordinates.
        """

        rows, columns = self.lattice_shape
        face_height, face_width = self.face_shape
        row_axis = _normalized_axis_signature(
            rows, face_height, self.row_bands
        )
        column_axis = _normalized_axis_signature(
            columns, face_width, self.column_bands
        )
        axis_signatures = sorted((row_axis, column_axis))

        marker_relations: Dict[int, Dict[str, List[Tuple[int, ...]]]] = {
            marker.marker_id: {"row": [], "column": []} for marker in self.markers
        }
        for relation in self.marker_band_relations:
            marker = self.markers[relation.marker_id]
            face_index = (
                marker.lattice_row if relation.axis == "row" else marker.lattice_column
            )
            # Twice the distance from the face center to the lattice line.
            center_distance = abs(2 * relation.band_lattice_index - (2 * face_index + 1))
            marker_relations[relation.marker_id][relation.axis].append(
                (
                    center_distance,
                    relation.gap,
                    int(relation.touches),
                    int(relation.adjacent_to_face),
                    relation.orthogonal_overlap,
                    relation.band_thickness,
                )
            )

        marker_signatures = []
        for marker in self.markers:
            face = self.faces[marker.face_id]
            axes = sorted(
                (
                    tuple(sorted(marker_relations[marker.marker_id]["row"])),
                    tuple(sorted(marker_relations[marker.marker_id]["column"])),
                )
            )
            marker_signatures.append(
                (
                    _canonical_lattice_position(
                        marker.lattice_row, marker.lattice_column, rows, columns
                    ),
                    face.face_class,
                    marker.area,
                    marker.shape_signature,
                    marker.same_color_multiplicity,
                    tuple(axes),
                )
            )

        face_signatures = sorted(
            (
                _canonical_lattice_position(
                    face.lattice_row, face.lattice_column, rows, columns
                ),
                face.face_class,
                len(face.marker_ids),
                len(face.neighbor_face_ids),
            )
            for face in self.faces
        )
        wall_signatures = sorted(
            (
                tuple(
                    sorted(
                        (
                            self.faces[wall.first_face_id].face_class,
                            self.faces[wall.second_face_id].face_class,
                        )
                    )
                ),
                wall.thickness,
                wall.contact_length,
            )
            for wall in self.shared_walls
        )
        class_counts = Counter(face.face_class for face in self.faces)
        summary: Dict[str, object] = {
            "schema": "repeated_lattice_normalized.v1",
            "axis_signatures": [_nested_lists(item) for item in axis_signatures],
            "face_class_counts": {
                key: int(class_counts.get(key, 0)) for key in ("corner", "edge", "interior")
            },
            "face_signatures": [_nested_lists(item) for item in face_signatures],
            "wall_signatures": [_nested_lists(item) for item in wall_signatures],
            "marker_signatures": [_nested_lists(item) for item in sorted(marker_signatures)],
        }
        json.dumps(summary, sort_keys=True, separators=(",", ":"))
        return summary

    def canonical_summary(self) -> Dict[str, object]:
        """Alias for :meth:`normalized_summary`."""

        return self.normalized_summary()


def _nested_lists(value: object) -> object:
    if isinstance(value, tuple):
        return [_nested_lists(item) for item in value]
    if isinstance(value, list):
        return [_nested_lists(item) for item in value]
    return value


def _band_trace(band: SeparatorBand) -> Dict[str, object]:
    return {
        "band_id": band.band_id,
        "lattice_index": band.lattice_index,
        "thickness": band.thickness,
        "color_count": band.color_count,
        "color_area_profile": list(band.color_area_profile),
    }


def _wall_band(graph: RepeatedLatticeQuotient, wall: SharedWall) -> SeparatorBand:
    bands = graph.row_bands if wall.axis == "row" else graph.column_bands
    return bands[wall.separator_band_id]


def _validate_grid(grid: Array, limits: LatticeLimits) -> Array:
    value = np.asarray(grid)
    if value.ndim != 2 or value.size == 0:
        raise RepeatedLatticeError("a repeated lattice requires a nonempty 2D grid")
    height, width = value.shape
    if height > limits.maximum_height or width > limits.maximum_width:
        raise RepeatedLatticeLimitError(
            f"grid shape {value.shape} exceeds the configured canvas cap"
        )
    if not np.issubdtype(value.dtype, np.integer):
        if not np.all(np.isfinite(value)) or not np.all(value == np.floor(value)):
            raise RepeatedLatticeError("grid colors must be finite integer labels")
    result = np.asarray(value, dtype=np.int64)
    if len(np.unique(result)) > limits.maximum_palette:
        raise RepeatedLatticeLimitError("palette exceeds the configured cap")
    return result


def _runs(indices: Iterable[int]) -> Tuple[Span, ...]:
    ordered = tuple(sorted(int(item) for item in indices))
    if not ordered:
        return ()
    result: List[Span] = []
    start = ordered[0]
    previous = ordered[0]
    for item in ordered[1:]:
        if item != previous + 1:
            result.append((start, previous + 1))
            start = item
        previous = item
    result.append((start, previous + 1))
    return tuple(result)


def _complement_spans(length: int, bands: Sequence[Span]) -> Tuple[Span, ...]:
    result: List[Span] = []
    cursor = 0
    for start, stop in bands:
        if cursor < start:
            result.append((cursor, start))
        cursor = stop
    if cursor < length:
        result.append((cursor, length))
    return tuple(result)


def _band_lattice_index(span: Span, face_spans: Sequence[Span]) -> int:
    start, _ = span
    return sum(face_stop <= start for _, face_stop in face_spans)


def _cells_for_band(shape: Tuple[int, int], axis: str, span: Span) -> Tuple[Cell, ...]:
    height, width = shape
    start, stop = span
    if axis == "row":
        return tuple((row, column) for row in range(start, stop) for column in range(width))
    return tuple((row, column) for row in range(height) for column in range(start, stop))


def _make_bands(
    grid: Array,
    background: int,
    axis: str,
    raw_spans: Sequence[Span],
    face_spans: Sequence[Span],
) -> Tuple[SeparatorBand, ...]:
    result = []
    for band_id, span in enumerate(raw_spans):
        cells = _cells_for_band(grid.shape, axis, span)
        counts = Counter(int(grid[cell]) for cell in cells)
        counts.pop(int(background), None)
        result.append(
            SeparatorBand(
                axis=axis,
                band_id=band_id,
                lattice_index=_band_lattice_index(span, face_spans),
                start=span[0],
                stop=span[1],
                thickness=span[1] - span[0],
                cells=cells,
                color_count=len(counts),
                color_area_profile=tuple(sorted(counts.values())),
            )
        )
    return tuple(result)


def _face_class(row: int, column: int, rows: int, columns: int) -> str:
    row_border = row in (0, rows - 1)
    column_border = column in (0, columns - 1)
    if row_border and column_border:
        return "corner"
    if row_border or column_border:
        return "edge"
    return "interior"


def _binary_shape_signature(cells: Sequence[Cell], box: Box) -> Tuple[int, ...]:
    top, left, bottom, right = box
    mask = np.zeros((bottom - top + 1, right - left + 1), dtype=np.int8)
    for row, column in cells:
        mask[row - top, column - left] = 1
    reflected = np.fliplr(mask)
    views = (
        mask,
        np.rot90(mask, 1),
        np.rot90(mask, 2),
        np.rot90(mask, 3),
        reflected,
        np.rot90(reflected, 1),
        np.rot90(reflected, 2),
        np.rot90(reflected, 3),
    )
    signatures = []
    for view in views:
        signatures.append(
            (int(view.shape[0]), int(view.shape[1]), *(int(item) for item in view.ravel()))
        )
    return min(signatures)


def _box(cells: Sequence[Cell]) -> Box:
    rows = [cell[0] for cell in cells]
    columns = [cell[1] for cell in cells]
    return min(rows), min(columns), max(rows), max(columns)


def _monochrome_components(grid: Array, mask: Array) -> Tuple[Tuple[Cell, ...], ...]:
    height, width = grid.shape
    visited = np.zeros(grid.shape, dtype=bool)
    result: List[Tuple[Cell, ...]] = []
    for row in range(height):
        for column in range(width):
            if bool(visited[row, column]) or not bool(mask[row, column]):
                continue
            color = int(grid[row, column])
            queue = deque([(row, column)])
            visited[row, column] = True
            cells: List[Cell] = []
            while queue:
                current_row, current_column = queue.popleft()
                cells.append((current_row, current_column))
                for dr, dc in ((-1, 0), (0, 1), (1, 0), (0, -1)):
                    nr, nc = current_row + dr, current_column + dc
                    if (
                        0 <= nr < height
                        and 0 <= nc < width
                        and bool(mask[nr, nc])
                        and not bool(visited[nr, nc])
                        and int(grid[nr, nc]) == color
                    ):
                        visited[nr, nc] = True
                        queue.append((nr, nc))
            result.append(tuple(sorted(cells)))
    return tuple(sorted(result, key=lambda item: item[0]))


def _span_index(value: int, spans: Sequence[Span]) -> Optional[int]:
    for index, (start, stop) in enumerate(spans):
        if start <= value < stop:
            return index
    return None


def _separator_evidence(grid: Array, background: int) -> Tuple[Tuple[Span, ...], Tuple[Span, ...]]:
    foreground = grid != int(background)
    row_indices = np.flatnonzero(np.all(foreground, axis=1))
    column_indices = np.flatnonzero(np.all(foreground, axis=0))
    return _runs(row_indices), _runs(column_indices)


def _require_repeated_extents(axis: str, spans: Sequence[Span]) -> int:
    extents = tuple(stop - start for start, stop in spans)
    if len(set(extents)) != 1:
        raise IrregularLatticeError(
            f"{axis} face extents {extents} are not repeated; a separator may be missing"
        )
    return extents[0]


def _internal_band_by_index(
    bands: Sequence[SeparatorBand], lattice_index: int, axis: str
) -> SeparatorBand:
    matches = [band for band in bands if band.lattice_index == lattice_index]
    if len(matches) != 1:
        raise MissingSeparatorError(
            f"{axis} separator at lattice index {lattice_index} is absent or ambiguous"
        )
    return matches[0]


def _build_for_background(
    grid: Array,
    background: int,
    limits: LatticeLimits,
) -> RepeatedLatticeQuotient:
    height, width = grid.shape
    raw_row_bands, raw_column_bands = _separator_evidence(grid, background)
    if not raw_row_bands or not raw_column_bands:
        raise MissingSeparatorError("a repeated lattice requires row and column separator bands")
    if len(raw_row_bands) > limits.maximum_row_bands:
        raise RepeatedLatticeLimitError("row separator bands exceed the configured cap")
    if len(raw_column_bands) > limits.maximum_column_bands:
        raise RepeatedLatticeLimitError("column separator bands exceed the configured cap")

    row_spans = _complement_spans(height, raw_row_bands)
    column_spans = _complement_spans(width, raw_column_bands)
    if len(row_spans) < 2 or len(column_spans) < 2:
        raise MissingSeparatorError("separator bands do not expose at least a 2 by 2 lattice")
    face_height = _require_repeated_extents("row", row_spans)
    face_width = _require_repeated_extents("column", column_spans)
    face_count = len(row_spans) * len(column_spans)
    if face_count > limits.maximum_faces:
        raise RepeatedLatticeLimitError("lattice faces exceed the configured cap")

    row_bands = _make_bands(
        grid, background, "row", raw_row_bands, row_spans
    )
    column_bands = _make_bands(
        grid, background, "column", raw_column_bands, column_spans
    )
    for lattice_index in range(1, len(row_spans)):
        _internal_band_by_index(row_bands, lattice_index, "row")
    for lattice_index in range(1, len(column_spans)):
        _internal_band_by_index(column_bands, lattice_index, "column")

    rows, columns = len(row_spans), len(column_spans)
    raw_faces: List[LatticeFace] = []
    for lattice_row, row_span in enumerate(row_spans):
        for lattice_column, column_span in enumerate(column_spans):
            face_id = lattice_row * columns + lattice_column
            cells = tuple(
                (row, column)
                for row in range(row_span[0], row_span[1])
                for column in range(column_span[0], column_span[1])
            )
            raw_faces.append(
                LatticeFace(
                    face_id=face_id,
                    lattice_row=lattice_row,
                    lattice_column=lattice_column,
                    row_start=row_span[0],
                    row_stop=row_span[1],
                    column_start=column_span[0],
                    column_stop=column_span[1],
                    cells=cells,
                    face_class=_face_class(lattice_row, lattice_column, rows, columns),
                    marker_ids=(),
                    neighbor_face_ids=(),
                )
            )

    shared_walls: List[SharedWall] = []
    neighbors: Dict[int, List[int]] = {face.face_id: [] for face in raw_faces}
    for lattice_row in range(rows):
        for lattice_column in range(columns):
            face_id = lattice_row * columns + lattice_column
            if lattice_row + 1 < rows:
                other = (lattice_row + 1) * columns + lattice_column
                band = _internal_band_by_index(row_bands, lattice_row + 1, "row")
                shared_walls.append(
                    SharedWall(
                        wall_id=len(shared_walls),
                        first_face_id=face_id,
                        second_face_id=other,
                        axis="row",
                        separator_band_id=band.band_id,
                        thickness=band.thickness,
                        contact_length=face_width,
                    )
                )
                neighbors[face_id].append(other)
                neighbors[other].append(face_id)
            if lattice_column + 1 < columns:
                other = lattice_row * columns + lattice_column + 1
                band = _internal_band_by_index(column_bands, lattice_column + 1, "column")
                shared_walls.append(
                    SharedWall(
                        wall_id=len(shared_walls),
                        first_face_id=face_id,
                        second_face_id=other,
                        axis="column",
                        separator_band_id=band.band_id,
                        thickness=band.thickness,
                        contact_length=face_height,
                    )
                )
                neighbors[face_id].append(other)
                neighbors[other].append(face_id)
    if len(shared_walls) > limits.maximum_shared_walls:
        raise RepeatedLatticeLimitError("shared walls exceed the configured cap")

    separator_mask = np.zeros(grid.shape, dtype=bool)
    for band in (*row_bands, *column_bands):
        for cell in band.cells:
            separator_mask[cell] = True
    marker_mask = (grid != int(background)) & ~separator_mask
    marker_cell_count = int(np.count_nonzero(marker_mask))
    if marker_cell_count > limits.maximum_marker_cells:
        raise OffLatticeNoiseError("off-lattice foreground exceeds the marker-cell cap")

    components = _monochrome_components(grid, marker_mask)
    if len(components) > limits.maximum_markers:
        raise RepeatedLatticeLimitError("marker count exceeds the configured cap")
    marker_records: List[Tuple[int, Tuple[Cell, ...], Box, int, int, int]] = []
    for component in components:
        if len(component) > limits.maximum_marker_area:
            raise OffLatticeNoiseError(
                f"off-lattice component of area {len(component)} exceeds the marker cap"
            )
        locations = {
            (_span_index(row, row_spans), _span_index(column, column_spans))
            for row, column in component
        }
        if len(locations) != 1 or None in next(iter(locations)):
            raise OffLatticeNoiseError("an off-lattice component crosses a separator face")
        lattice_row, lattice_column = next(iter(locations))
        assert lattice_row is not None and lattice_column is not None
        marker_records.append(
            (
                int(grid[component[0]]),
                component,
                _box(component),
                lattice_row * columns + lattice_column,
                lattice_row,
                lattice_column,
            )
        )
    color_multiplicity = Counter(record[0] for record in marker_records)
    markers = tuple(
        LatticeMarker(
            marker_id=marker_id,
            color=record[0],
            cells=record[1],
            bounding_box=record[2],
            area=len(record[1]),
            face_id=record[3],
            lattice_row=record[4],
            lattice_column=record[5],
            shape_signature=_binary_shape_signature(record[1], record[2]),
            same_color_multiplicity=color_multiplicity[record[0]],
        )
        for marker_id, record in enumerate(marker_records)
    )

    relations: List[MarkerBandRelation] = []
    for marker in markers:
        top, left, bottom, right = marker.bounding_box
        for axis, bands in (("row", row_bands), ("column", column_bands)):
            face_index = marker.lattice_row if axis == "row" else marker.lattice_column
            for band in bands:
                if axis == "row":
                    if band.stop <= top:
                        direction = "before"
                        gap = top - band.stop
                    elif band.start > bottom:
                        direction = "after"
                        gap = band.start - bottom - 1
                    else:
                        raise OffLatticeNoiseError("marker overlaps a row separator band")
                    overlap = right - left + 1
                else:
                    if band.stop <= left:
                        direction = "before"
                        gap = left - band.stop
                    elif band.start > right:
                        direction = "after"
                        gap = band.start - right - 1
                    else:
                        raise OffLatticeNoiseError("marker overlaps a column separator band")
                    overlap = bottom - top + 1
                adjacent = band.lattice_index in (face_index, face_index + 1)
                relations.append(
                    MarkerBandRelation(
                        relation_id=len(relations),
                        marker_id=marker.marker_id,
                        axis=axis,
                        direction=direction,
                        separator_band_id=band.band_id,
                        band_lattice_index=band.lattice_index,
                        relative_face_offset=band.lattice_index - face_index,
                        gap=gap,
                        touches=gap == 0,
                        adjacent_to_face=adjacent,
                        orthogonal_overlap=overlap,
                        band_thickness=band.thickness,
                    )
                )
    if len(relations) > limits.maximum_marker_band_relations:
        raise RepeatedLatticeLimitError("marker-band relations exceed the configured cap")

    markers_by_face: Dict[int, List[int]] = {face.face_id: [] for face in raw_faces}
    for marker in markers:
        markers_by_face[marker.face_id].append(marker.marker_id)
    faces = tuple(
        replace(
            face,
            marker_ids=tuple(markers_by_face[face.face_id]),
            neighbor_face_ids=tuple(sorted(neighbors[face.face_id])),
        )
        for face in raw_faces
    )
    return RepeatedLatticeQuotient(
        shape=(height, width),
        background=int(background),
        lattice_shape=(rows, columns),
        face_shape=(face_height, face_width),
        row_bands=row_bands,
        column_bands=column_bands,
        faces=faces,
        shared_walls=tuple(shared_walls),
        markers=markers,
        marker_band_relations=tuple(relations),
    )


def _background_score(graph: RepeatedLatticeQuotient, grid: Array) -> Tuple[int, ...]:
    """Palette-independent evidence used only to disambiguate valid parses."""

    marker_cells = sum(marker.area for marker in graph.markers)
    background_cells = int(np.count_nonzero(grid == graph.background))
    # Prefer richer repeated topology, then cleaner faces, then support.
    return (
        len(graph.faces),
        min(graph.lattice_shape),
        -marker_cells,
        background_cells,
    )


def infer_lattice_background(
    grid: Array,
    *,
    limits: LatticeLimits = DEFAULT_LIMITS,
) -> int:
    """Infer the unique color that supports the best valid lattice parse."""

    value = _validate_grid(grid, limits)
    candidates = []
    failures: List[RepeatedLatticeError] = []
    for raw_color in np.unique(value):
        color = int(raw_color)
        try:
            graph = _build_for_background(value, color, limits)
        except RepeatedLatticeError as error:
            failures.append(error)
            continue
        candidates.append((_background_score(graph, value), color))
    if not candidates:
        # Preserve a strong abstention discovered under a structurally
        # plausible role instead of degrading every invalid input to the
        # generic missing-separator case.  This is especially useful for a
        # valid grid skeleton whose residual foreground exceeds a hard cap.
        for error_type in (
            RepeatedLatticeLimitError,
            OffLatticeNoiseError,
            IrregularLatticeError,
        ):
            for error in failures:
                if isinstance(error, error_type):
                    raise error
        raise MissingSeparatorError("no palette role supports a valid repeated lattice")
    best_score = max(score for score, _ in candidates)
    best = [color for score, color in candidates if score == best_score]
    if len(best) != 1:
        raise AmbiguousLatticeBackgroundError(
            f"{len(best)} palette roles have identical repeated-lattice support"
        )
    return best[0]


def build_repeated_lattice_quotient(
    grid: Array,
    *,
    background: Optional[int] = None,
    limits: LatticeLimits = DEFAULT_LIMITS,
) -> RepeatedLatticeQuotient:
    """Build a bounded repeated-lattice quotient from one input grid only."""

    value = _validate_grid(grid, limits)
    if background is None:
        inferred = infer_lattice_background(value, limits=limits)
    else:
        inferred = int(background)
        if inferred not in {int(item) for item in np.unique(value)}:
            raise RepeatedLatticeError("the designated background does not occur in the grid")
    return _build_for_background(value, inferred, limits)


def build_repeated_lattice(
    grid: Array,
    *,
    background: Optional[int] = None,
    limits: LatticeLimits = DEFAULT_LIMITS,
) -> RepeatedLatticeQuotient:
    """Short alias for :func:`build_repeated_lattice_quotient`."""

    return build_repeated_lattice_quotient(grid, background=background, limits=limits)


def analyze_repeated_lattice(
    grid: Array,
    *,
    background: Optional[int] = None,
    limits: LatticeLimits = DEFAULT_LIMITS,
) -> RepeatedLatticeQuotient:
    """Analysis-oriented alias for :func:`build_repeated_lattice_quotient`."""

    return build_repeated_lattice_quotient(grid, background=background, limits=limits)


def _normalized_axis_signature(
    face_count: int,
    face_extent: int,
    bands: Sequence[SeparatorBand],
) -> Tuple[object, ...]:
    by_index = {band.lattice_index: band for band in bands}
    profile = tuple(
        (
            by_index[index].thickness,
            by_index[index].color_count,
            by_index[index].color_area_profile,
        )
        if index in by_index
        else (0, 0, ())
        for index in range(face_count + 1)
    )
    reverse = tuple(reversed(profile))
    return face_count, face_extent, min(profile, reverse)


def _canonical_lattice_position(
    row: int,
    column: int,
    rows: int,
    columns: int,
) -> Tuple[int, int, int, int]:
    positions = (
        (rows, columns, row, column),
        (columns, rows, columns - 1 - column, row),
        (rows, columns, rows - 1 - row, columns - 1 - column),
        (columns, rows, column, rows - 1 - row),
        (rows, columns, row, columns - 1 - column),
        (columns, rows, column, row),
        (rows, columns, rows - 1 - row, column),
        (columns, rows, columns - 1 - column, rows - 1 - row),
    )
    return min(positions)


__all__ = [
    "AmbiguousLatticeBackgroundError",
    "DEFAULT_LIMITS",
    "IrregularLatticeError",
    "LatticeFace",
    "LatticeLimits",
    "LatticeMarker",
    "MarkerBandRelation",
    "MissingSeparatorError",
    "OffLatticeNoiseError",
    "REPEATED_LATTICE_VERSION",
    "RepeatedLatticeError",
    "RepeatedLatticeLimitError",
    "RepeatedLatticeQuotient",
    "SeparatorBand",
    "SharedWall",
    "analyze_repeated_lattice",
    "build_repeated_lattice",
    "build_repeated_lattice_quotient",
    "infer_lattice_background",
]
