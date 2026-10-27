"""Bounded, input-only planar incidence analysis for ARC grids.

The module deliberately does not inspect demonstrations or outputs.  It turns
one input raster into a finite collection of background faces, monochrome
boundary components, color-agnostic boundary clusters, and explicit
incidence evidence.  The two boundary resolutions are both useful: components
retain color roles, while clusters recognize a wall assembled from several
touching colors.

Canvas edges are represented as a virtual boundary.  Consequently a region
that is closed by a foreground wall and the edge of the raster remains a
first-class face rather than being discarded as an "outside" component.

All searches are bounded for ARC's 30 by 30 canvas limit.  Pathological inputs
raise :class:`PlanarIncidenceLimitError` instead of silently returning a
partial graph.
"""

from __future__ import annotations

from collections import Counter, defaultdict, deque
from dataclasses import dataclass
import hashlib
from typing import Dict, Iterator, Optional, Sequence, Tuple

import numpy as np


Array = np.ndarray
Cell = Tuple[int, int]
Box = Tuple[int, int, int, int]
SideContacts = Tuple[int, int, int, int]  # top, right, bottom, left

PLANAR_INCIDENCE_VERSION = "1.0"


class PlanarIncidenceError(ValueError):
    """Base class for explicit planar-incidence abstentions."""


class AmbiguousBackgroundError(PlanarIncidenceError):
    """Raised when no palette-invariant background choice is unique."""


class PlanarIncidenceLimitError(PlanarIncidenceError):
    """Raised before a configured resource bound would be exceeded."""


@dataclass(frozen=True)
class IncidenceLimits:
    """Hard resource limits for a single raster.

    The defaults comfortably cover ordinary ARC scenes while refusing dense
    checkerboards whose hundreds of singleton regions provide little useful
    structural evidence.
    """

    maximum_height: int = 30
    maximum_width: int = 30
    maximum_palette: int = 32
    maximum_faces: int = 256
    maximum_boundary_components: int = 256
    maximum_boundary_clusters: int = 256
    maximum_evidence_records: int = 8192


DEFAULT_LIMITS = IncidenceLimits()


@dataclass(frozen=True)
class BackgroundHypothesis:
    """One input-only background proposal in a palette-equivariant ranking."""

    color: int
    score: Tuple[int, int, int, int]
    rank: int
    tied: bool


def _d4_views(array: Array) -> Tuple[Array, ...]:
    base = np.asarray(array)
    reflected = np.fliplr(base)
    return tuple(
        np.ascontiguousarray(view)
        for view in (
            base,
            np.rot90(base, 1),
            np.rot90(base, 2),
            np.rot90(base, 3),
            reflected,
            np.rot90(reflected, 1),
            np.rot90(reflected, 2),
            np.rot90(reflected, 3),
        )
    )


def d4_views(array: Array) -> Tuple[Array, ...]:
    """Return the eight rectangular dihedral views of ``array``."""

    if np.asarray(array).ndim != 2:
        raise PlanarIncidenceError("D4 views require a two-dimensional array")
    return _d4_views(np.asarray(array))


def _palette_normalized_flat(view: Array, background: int) -> Tuple[int, ...]:
    mapping: Dict[int, int] = {int(background): 0}
    next_label = 1
    encoded = []
    for raw in np.asarray(view).ravel(order="C"):
        value = int(raw)
        if value not in mapping:
            mapping[value] = next_label
            next_label += 1
        encoded.append(mapping[value])
    return tuple(encoded)


def canonical_palette_signature(array: Array, background: int) -> Tuple[int, ...]:
    """Return an exact signature invariant to D4 and palette renaming.

    The designated background is always label zero.  Other colors are
    assigned labels in first-occurrence order separately in each D4 view, and
    the lexicographically least encoding is selected.
    """

    value = np.asarray(array)
    if value.ndim != 2 or value.size == 0:
        raise PlanarIncidenceError("canonical signatures require a nonempty 2D array")
    signatures = []
    for view in _d4_views(value):
        signatures.append(
            (int(view.shape[0]), int(view.shape[1]), *_palette_normalized_flat(view, background))
        )
    return min(signatures)


def _binary_shape_signature(cells: Sequence[Cell], box: Box) -> Tuple[int, ...]:
    top, left, bottom, right = box
    mask = np.zeros((bottom - top + 1, right - left + 1), dtype=np.int8)
    for row, column in cells:
        mask[row - top, column - left] = 1
    return canonical_palette_signature(mask, 0)


def _box(cells: Sequence[Cell]) -> Box:
    rows = [cell[0] for cell in cells]
    columns = [cell[1] for cell in cells]
    return min(rows), min(columns), max(rows), max(columns)


def _box_dimensions(box: Box) -> Tuple[int, int]:
    return box[2] - box[0] + 1, box[3] - box[1] + 1


def _perimeter(cells: Sequence[Cell], shape: Tuple[int, int]) -> int:
    member = set(cells)
    height, width = shape
    total = 0
    for row, column in cells:
        for dr, dc in ((-1, 0), (0, 1), (1, 0), (0, -1)):
            nr, nc = row + dr, column + dc
            if nr < 0 or nr >= height or nc < 0 or nc >= width or (nr, nc) not in member:
                total += 1
    return total


def _side_contacts(cells: Sequence[Cell], shape: Tuple[int, int]) -> SideContacts:
    height, width = shape
    member = set(cells)
    return (
        sum((0, column) in member for column in range(width)),
        sum((row, width - 1) in member for row in range(height)),
        sum((height - 1, column) in member for column in range(width)),
        sum((row, 0) in member for row in range(height)),
    )


def _component_cells(mask: Array, connectivity: int = 4) -> Tuple[Tuple[Cell, ...], ...]:
    if connectivity not in (4, 8):
        raise PlanarIncidenceError("connectivity must be four or eight")
    height, width = mask.shape
    visited = np.zeros(mask.shape, dtype=bool)
    neighbors = [(-1, 0), (0, 1), (1, 0), (0, -1)]
    if connectivity == 8:
        neighbors.extend([(-1, -1), (-1, 1), (1, -1), (1, 1)])
    result = []
    for row in range(height):
        for column in range(width):
            if not bool(mask[row, column]) or bool(visited[row, column]):
                continue
            queue = deque([(row, column)])
            visited[row, column] = True
            cells = []
            while queue:
                current_row, current_column = queue.popleft()
                cells.append((current_row, current_column))
                for dr, dc in neighbors:
                    nr, nc = current_row + dr, current_column + dc
                    if (
                        0 <= nr < height
                        and 0 <= nc < width
                        and bool(mask[nr, nc])
                        and not bool(visited[nr, nc])
                    ):
                        visited[nr, nc] = True
                        queue.append((nr, nc))
            result.append(tuple(sorted(cells)))
    return tuple(result)


def _monochrome_components(grid: Array, background: int) -> Tuple[Tuple[Cell, ...], ...]:
    height, width = grid.shape
    visited = np.zeros(grid.shape, dtype=bool)
    result = []
    for row in range(height):
        for column in range(width):
            if bool(visited[row, column]) or int(grid[row, column]) == int(background):
                continue
            color = int(grid[row, column])
            queue = deque([(row, column)])
            visited[row, column] = True
            cells = []
            while queue:
                current_row, current_column = queue.popleft()
                cells.append((current_row, current_column))
                for dr, dc in ((-1, 0), (0, 1), (1, 0), (0, -1)):
                    nr, nc = current_row + dr, current_column + dc
                    if (
                        0 <= nr < height
                        and 0 <= nc < width
                        and not bool(visited[nr, nc])
                        and int(grid[nr, nc]) == color
                    ):
                        visited[nr, nc] = True
                        queue.append((nr, nc))
            result.append(tuple(sorted(cells)))
    return tuple(result)


def _background_scores(grid: Array) -> Dict[int, Tuple[int, int, int, int]]:
    value = np.asarray(grid)
    if value.ndim != 2 or value.size == 0:
        raise PlanarIncidenceError("background inference requires a nonempty 2D grid")
    scores: Dict[int, Tuple[int, int, int, int]] = {}
    for raw in np.unique(value):
        color = int(raw)
        mask = value == color
        components = _component_cells(mask, 4)
        border_count = int(np.count_nonzero(mask[0, :]))
        if value.shape[0] > 1:
            border_count += int(np.count_nonzero(mask[-1, :]))
        border_count += int(np.count_nonzero(mask[:, 0]))
        if value.shape[1] > 1:
            border_count += int(np.count_nonzero(mask[:, -1]))
        scores[color] = (
            int(np.count_nonzero(mask)),
            border_count,
            max((len(component) for component in components), default=0),
            -len(components),
        )
    return scores


def rank_background_hypotheses(grid: Array) -> Tuple[BackgroundHypothesis, ...]:
    """Rank every possible background while preserving explicit score ties.

    ``rank`` is the authoritative ordering.  Callers must search or abstain
    when more than one hypothesis has rank zero.  Tuple order inside an exact
    tie is only a presentation detail.
    """

    value = np.asarray(grid)
    scores = _background_scores(value)
    distinct_scores = sorted(set(scores.values()), reverse=True)
    rank_by_score = {score: rank for rank, score in enumerate(distinct_scores)}
    tier_sizes = Counter(scores.values())
    records = [
        BackgroundHypothesis(
            color=color,
            score=score,
            rank=rank_by_score[score],
            tied=tier_sizes[score] > 1,
        )
        for color, score in scores.items()
    ]
    # Binary signatures stabilize nonidentical ties under D4. Raw color is a
    # final display order only and must never be used to resolve a score tie.
    return tuple(
        sorted(
            records,
            key=lambda item: (
                item.rank,
                canonical_palette_signature((value == item.color).astype(np.int8), 0),
                item.color,
            ),
        )
    )


def infer_background(grid: Array) -> int:
    """Infer a unique background without using numeric palette order.

    Colors are ranked by total area, canvas contact, largest four-connected
    component, then by fewer disconnected components. A remaining tie is an
    explicit ambiguity. Use :func:`rank_background_hypotheses` when a caller
    intends to retain multiple interpretations.
    """

    scores = _background_scores(np.asarray(grid))
    best = max(scores.values())
    winners = [color for color, score in scores.items() if score == best]
    if len(winners) != 1:
        raise AmbiguousBackgroundError(
            "background is structurally ambiguous; supply it explicitly"
        )
    return winners[0]


@dataclass(frozen=True)
class BackgroundFace:
    face_id: int
    cells: Tuple[Cell, ...]
    area: int
    box: Box
    perimeter: int
    canvas_contacts: SideContacts
    incident_boundary_ids: Tuple[int, ...]
    incident_cluster_ids: Tuple[int, ...]
    containing_cluster_ids: Tuple[int, ...]
    shape_signature: Tuple[int, ...]

    @property
    def touches_canvas(self) -> bool:
        return any(self.canvas_contacts)

    @property
    def uses_virtual_canvas(self) -> bool:
        return self.touches_canvas

    @property
    def containment_depth(self) -> int:
        return len(self.containing_cluster_ids)

    def normalized_feature(self) -> Tuple[object, ...]:
        height, width = _box_dimensions(self.box)
        return (
            self.area,
            min(height, width),
            max(height, width),
            self.perimeter,
            sum(value > 0 for value in self.canvas_contacts),
            tuple(sorted(self.canvas_contacts)),
            len(self.incident_boundary_ids),
            len(self.incident_cluster_ids),
            self.containment_depth,
            self.shape_signature,
        )


@dataclass(frozen=True)
class BoundaryComponent:
    boundary_id: int
    color: int
    cells: Tuple[Cell, ...]
    area: int
    box: Box
    perimeter: int
    canvas_contacts: SideContacts
    cluster_id: int
    incident_face_ids: Tuple[int, ...]
    same_color_component_count: int
    same_color_total_area: int
    shape_signature: Tuple[int, ...]

    @property
    def touches_canvas(self) -> bool:
        return any(self.canvas_contacts)

    def normalized_feature(self) -> Tuple[object, ...]:
        height, width = _box_dimensions(self.box)
        return (
            self.area,
            min(height, width),
            max(height, width),
            self.perimeter,
            sum(value > 0 for value in self.canvas_contacts),
            tuple(sorted(self.canvas_contacts)),
            len(self.incident_face_ids),
            self.same_color_component_count,
            self.same_color_total_area,
            self.shape_signature,
        )


@dataclass(frozen=True)
class BoundaryCluster:
    cluster_id: int
    cells: Tuple[Cell, ...]
    area: int
    box: Box
    perimeter: int
    canvas_contacts: SideContacts
    boundary_ids: Tuple[int, ...]
    incident_face_ids: Tuple[int, ...]
    containing_cluster_ids: Tuple[int, ...]
    contained_face_ids: Tuple[int, ...]
    contained_cluster_ids: Tuple[int, ...]
    color_area_profile: Tuple[int, ...]
    shape_signature: Tuple[int, ...]

    @property
    def touches_canvas(self) -> bool:
        return any(self.canvas_contacts)

    @property
    def color_count(self) -> int:
        return len(self.color_area_profile)

    @property
    def containment_depth(self) -> int:
        return len(self.containing_cluster_ids)

    def normalized_feature(self) -> Tuple[object, ...]:
        height, width = _box_dimensions(self.box)
        return (
            self.area,
            min(height, width),
            max(height, width),
            self.perimeter,
            sum(value > 0 for value in self.canvas_contacts),
            tuple(sorted(self.canvas_contacts)),
            len(self.boundary_ids),
            len(self.incident_face_ids),
            self.containment_depth,
            len(self.contained_face_ids),
            len(self.contained_cluster_ids),
            self.color_area_profile,
            self.shape_signature,
        )


@dataclass(frozen=True)
class FaceBoundaryIncidence:
    face_id: int
    boundary_id: int
    shared_wall: int
    corner_touches: int


@dataclass(frozen=True)
class FaceClusterIncidence:
    face_id: int
    cluster_id: int
    shared_wall: int
    corner_touches: int


@dataclass(frozen=True)
class BoundaryTouchEvidence:
    first_boundary_id: int
    second_boundary_id: int
    shared_wall: int
    corner_touches: int


@dataclass(frozen=True)
class ClusterTouchEvidence:
    first_cluster_id: int
    second_cluster_id: int
    corner_touches: int


@dataclass(frozen=True)
class FaceSeparationEvidence:
    """Evidence that two faces occupy opposite sides of one boundary cluster."""

    first_face_id: int
    second_face_id: int
    cluster_id: int
    horizontal_samples: int
    vertical_samples: int

    @property
    def shared_wall_evidence(self) -> int:
        return self.horizontal_samples + self.vertical_samples


@dataclass(frozen=True)
class ContainmentEvidence:
    container_cluster_id: int
    child_kind: str  # ``face`` or ``cluster``
    child_id: int
    direct: bool


@dataclass(frozen=True)
class CanvasIncidence:
    entity_kind: str  # ``face`` or ``cluster``
    entity_id: int
    side_contacts: SideContacts

    @property
    def contact_length(self) -> int:
        return sum(self.side_contacts)


@dataclass(frozen=True)
class FaceClosureEvidence:
    face_id: int
    physical_cluster_ids: Tuple[int, ...]
    uses_virtual_canvas: bool


@dataclass(frozen=True)
class VirtualCanvasBoundary:
    height: int
    width: int
    face_ids: Tuple[int, ...]
    cluster_ids: Tuple[int, ...]

    @property
    def perimeter_slots(self) -> int:
        return 2 * self.height + 2 * self.width


@dataclass(frozen=True)
class PlanarIncidenceGraph:
    shape: Tuple[int, int]
    background: int
    faces: Tuple[BackgroundFace, ...]
    boundaries: Tuple[BoundaryComponent, ...]
    boundary_clusters: Tuple[BoundaryCluster, ...]
    face_boundary_incidence: Tuple[FaceBoundaryIncidence, ...]
    face_cluster_incidence: Tuple[FaceClusterIncidence, ...]
    boundary_touches: Tuple[BoundaryTouchEvidence, ...]
    cluster_touches: Tuple[ClusterTouchEvidence, ...]
    face_separations: Tuple[FaceSeparationEvidence, ...]
    containment: Tuple[ContainmentEvidence, ...]
    canvas_incidence: Tuple[CanvasIncidence, ...]
    face_closures: Tuple[FaceClosureEvidence, ...]
    virtual_canvas: VirtualCanvasBoundary
    canonical_grid_signature: Tuple[int, ...]

    def normalized_features(self) -> Tuple[object, ...]:
        """Return graph evidence invariant to D4 and palette renaming."""

        face_features = {item.face_id: item.normalized_feature() for item in self.faces}
        boundary_features = {
            item.boundary_id: item.normalized_feature() for item in self.boundaries
        }
        cluster_features = {
            item.cluster_id: item.normalized_feature() for item in self.boundary_clusters
        }

        face_boundary = tuple(
            sorted(
                (
                    face_features[item.face_id],
                    boundary_features[item.boundary_id],
                    item.shared_wall,
                    item.corner_touches,
                )
                for item in self.face_boundary_incidence
            )
        )
        face_cluster = tuple(
            sorted(
                (
                    face_features[item.face_id],
                    cluster_features[item.cluster_id],
                    item.shared_wall,
                    item.corner_touches,
                )
                for item in self.face_cluster_incidence
            )
        )
        boundary_touch = tuple(
            sorted(
                (
                    tuple(
                        sorted(
                            (
                                boundary_features[item.first_boundary_id],
                                boundary_features[item.second_boundary_id],
                            )
                        )
                    ),
                    item.shared_wall,
                    item.corner_touches,
                )
                for item in self.boundary_touches
            )
        )
        cluster_touch = tuple(
            sorted(
                (
                    tuple(
                        sorted(
                            (
                                cluster_features[item.first_cluster_id],
                                cluster_features[item.second_cluster_id],
                            )
                        )
                    ),
                    item.corner_touches,
                )
                for item in self.cluster_touches
            )
        )
        separations = tuple(
            sorted(
                (
                    tuple(
                        sorted(
                            (
                                face_features[item.first_face_id],
                                face_features[item.second_face_id],
                            )
                        )
                    ),
                    cluster_features[item.cluster_id],
                    tuple(sorted((item.horizontal_samples, item.vertical_samples))),
                )
                for item in self.face_separations
            )
        )
        containment = tuple(
            sorted(
                (
                    cluster_features[item.container_cluster_id],
                    item.child_kind,
                    (
                        face_features[item.child_id]
                        if item.child_kind == "face"
                        else cluster_features[item.child_id]
                    ),
                    item.direct,
                )
                for item in self.containment
            )
        )
        canvas = tuple(
            sorted(
                (
                    item.entity_kind,
                    (
                        face_features[item.entity_id]
                        if item.entity_kind == "face"
                        else cluster_features[item.entity_id]
                    ),
                    tuple(sorted(item.side_contacts)),
                )
                for item in self.canvas_incidence
            )
        )
        closures = tuple(
            sorted(
                (
                    face_features[item.face_id],
                    tuple(
                        sorted(cluster_features[index] for index in item.physical_cluster_ids)
                    ),
                    item.uses_virtual_canvas,
                )
                for item in self.face_closures
            )
        )
        return (
            "planar-incidence-normalized-v1",
            (min(self.shape), max(self.shape)),
            self.canonical_grid_signature,
            tuple(sorted(item.normalized_feature() for item in self.faces)),
            tuple(sorted(item.normalized_feature() for item in self.boundaries)),
            tuple(sorted(item.normalized_feature() for item in self.boundary_clusters)),
            face_boundary,
            face_cluster,
            boundary_touch,
            cluster_touch,
            separations,
            containment,
            canvas,
            closures,
        )

    def normalized_digest(self) -> str:
        """Compact stable digest of :meth:`normalized_features`."""

        payload = repr(self.normalized_features()).encode("utf-8")
        return hashlib.sha256(payload).hexdigest()

    def normalized_metadata(self) -> Dict[str, object]:
        """Return coordinate-free, palette-free, JSON-safe graph metadata.

        Runtime nodes retain cells for exact rendering. This projection is the
        safe form for candidate metadata and audit records: it contains no raw
        cell coordinates, node IDs, or palette labels.
        """

        normalized = self.normalized_features()
        grid_digest = hashlib.sha256(
            repr(self.canonical_grid_signature).encode("utf-8")
        ).hexdigest()
        relation_names = (
            "face_boundary",
            "face_cluster",
            "boundary_touch",
            "cluster_touch",
            "face_separation",
            "containment",
            "canvas_incidence",
            "face_closure",
        )
        return {
            "schema": "planar-incidence-metadata-v1",
            "analysis_version": PLANAR_INCIDENCE_VERSION,
            "shape_orbit": [min(self.shape), max(self.shape)],
            "normalized_digest": self.normalized_digest(),
            "canonical_grid_digest": grid_digest,
            "counts": {
                "faces": len(self.faces),
                "boundary_components": len(self.boundaries),
                "boundary_clusters": len(self.boundary_clusters),
            },
            "node_features": {
                "faces": _json_safe(normalized[3]),
                "boundary_components": _json_safe(normalized[4]),
                "boundary_clusters": _json_safe(normalized[5]),
            },
            "relation_features": {
                name: _json_safe(normalized[index])
                for index, name in enumerate(relation_names, start=6)
            },
        }

    def face(self, face_id: int) -> BackgroundFace:
        return self.faces[int(face_id)]

    def boundary(self, boundary_id: int) -> BoundaryComponent:
        return self.boundaries[int(boundary_id)]

    def cluster(self, cluster_id: int) -> BoundaryCluster:
        return self.boundary_clusters[int(cluster_id)]

    def direct_containers(self, child_kind: str, child_id: int) -> Tuple[int, ...]:
        return tuple(
            item.container_cluster_id
            for item in self.containment
            if item.child_kind == child_kind and item.child_id == child_id and item.direct
        )


def _json_safe(value: object) -> object:
    if isinstance(value, tuple):
        return [_json_safe(item) for item in value]
    if isinstance(value, list):
        return [_json_safe(item) for item in value]
    if isinstance(value, dict):
        return {str(key): _json_safe(item) for key, item in value.items()}
    if isinstance(value, np.integer):
        return int(value)
    if isinstance(value, np.bool_):
        return bool(value)
    return value


def _validated_grid(grid: Array, limits: IncidenceLimits) -> Array:
    raw = np.asarray(grid)
    if raw.ndim != 2 or raw.size == 0:
        raise PlanarIncidenceError("planar incidence requires a nonempty 2D grid")
    height, width = raw.shape
    if height > limits.maximum_height or width > limits.maximum_width:
        raise PlanarIncidenceLimitError(
            f"grid shape {raw.shape} exceeds {limits.maximum_height}x{limits.maximum_width}"
        )
    if not np.issubdtype(raw.dtype, np.integer):
        if not np.all(np.equal(raw, np.floor(raw))):
            raise PlanarIncidenceError("grid values must be integers")
    values = np.unique(raw)
    if len(values) > limits.maximum_palette:
        raise PlanarIncidenceLimitError("palette budget exceeded")
    return np.array(raw, dtype=np.int64, copy=True)


def _label_map(shape: Tuple[int, int], groups: Sequence[Sequence[Cell]]) -> Array:
    labels = np.full(shape, -1, dtype=np.int32)
    for group_id, cells in enumerate(groups):
        for row, column in cells:
            labels[row, column] = group_id
    return labels


def _contact_records(
    face_labels: Array,
    boundary_labels: Array,
    cluster_labels: Array,
) -> Tuple[
    Dict[Tuple[int, int], list[int]],
    Dict[Tuple[int, int], list[int]],
]:
    height, width = face_labels.shape
    component_contact: Dict[Tuple[int, int], list[int]] = defaultdict(lambda: [0, 0])
    cluster_contact: Dict[Tuple[int, int], list[int]] = defaultdict(lambda: [0, 0])
    cardinal = ((-1, 0), (0, 1), (1, 0), (0, -1))
    diagonal = ((-1, -1), (-1, 1), (1, -1), (1, 1))
    for row in range(height):
        for column in range(width):
            face_id = int(face_labels[row, column])
            if face_id < 0:
                continue
            for dr, dc in cardinal:
                nr, nc = row + dr, column + dc
                if 0 <= nr < height and 0 <= nc < width:
                    boundary_id = int(boundary_labels[nr, nc])
                    if boundary_id >= 0:
                        component_contact[(face_id, boundary_id)][0] += 1
                    cluster_id = int(cluster_labels[nr, nc])
                    if cluster_id >= 0:
                        cluster_contact[(face_id, cluster_id)][0] += 1
            for dr, dc in diagonal:
                nr, nc = row + dr, column + dc
                if 0 <= nr < height and 0 <= nc < width:
                    boundary_id = int(boundary_labels[nr, nc])
                    if boundary_id >= 0:
                        component_contact[(face_id, boundary_id)][1] += 1
                    cluster_id = int(cluster_labels[nr, nc])
                    if cluster_id >= 0:
                        cluster_contact[(face_id, cluster_id)][1] += 1
    return component_contact, cluster_contact


def _boundary_touch_records(
    boundary_labels: Array,
    cluster_labels: Array,
) -> Tuple[Dict[Tuple[int, int], list[int]], Dict[Tuple[int, int], int]]:
    height, width = boundary_labels.shape
    component_touch: Dict[Tuple[int, int], list[int]] = defaultdict(lambda: [0, 0])
    cluster_touch: Dict[Tuple[int, int], int] = defaultdict(int)
    for row in range(height):
        for column in range(width):
            first_boundary = int(boundary_labels[row, column])
            first_cluster = int(cluster_labels[row, column])
            if first_boundary < 0:
                continue
            for dr, dc in ((0, 1), (1, 0)):
                nr, nc = row + dr, column + dc
                if nr >= height or nc >= width:
                    continue
                second_boundary = int(boundary_labels[nr, nc])
                if second_boundary >= 0 and second_boundary != first_boundary:
                    key = tuple(sorted((first_boundary, second_boundary)))
                    component_touch[key][0] += 1
            for dr, dc in ((1, -1), (1, 1)):
                nr, nc = row + dr, column + dc
                if nr >= height or nc < 0 or nc >= width:
                    continue
                second_boundary = int(boundary_labels[nr, nc])
                second_cluster = int(cluster_labels[nr, nc])
                if second_boundary >= 0 and second_boundary != first_boundary:
                    key = tuple(sorted((first_boundary, second_boundary)))
                    component_touch[key][1] += 1
                if second_cluster >= 0 and second_cluster != first_cluster:
                    key = tuple(sorted((first_cluster, second_cluster)))
                    cluster_touch[key] += 1
    return component_touch, cluster_touch


def _runs(values: Array) -> Iterator[Tuple[int, int]]:
    start: Optional[int] = None
    for index, active in enumerate(np.asarray(values, dtype=bool)):
        if bool(active) and start is None:
            start = index
        if start is not None and (not bool(active) or index == len(values) - 1):
            end = index if bool(active) and index == len(values) - 1 else index - 1
            yield start, end
            start = None


def _face_separation_records(
    cluster_labels: Array,
    face_labels: Array,
    cluster_count: int,
) -> Dict[Tuple[int, int, int], list[int]]:
    height, width = cluster_labels.shape
    result: Dict[Tuple[int, int, int], list[int]] = defaultdict(lambda: [0, 0])
    for cluster_id in range(cluster_count):
        mask = cluster_labels == cluster_id
        for row in range(height):
            for left, right in _runs(mask[row, :]):
                if left == 0 or right == width - 1:
                    continue
                first = int(face_labels[row, left - 1])
                second = int(face_labels[row, right + 1])
                if first >= 0 and second >= 0 and first != second:
                    key = (*sorted((first, second)), cluster_id)
                    result[key][0] += 1
        for column in range(width):
            for top, bottom in _runs(mask[:, column]):
                if top == 0 or bottom == height - 1:
                    continue
                first = int(face_labels[top - 1, column])
                second = int(face_labels[bottom + 1, column])
                if first >= 0 and second >= 0 and first != second:
                    key = (*sorted((first, second)), cluster_id)
                    result[key][1] += 1
    return result


def _reachable_around_cluster(cluster_mask: Array) -> Array:
    height, width = cluster_mask.shape
    reachable = np.zeros(cluster_mask.shape, dtype=bool)
    queue: deque[Cell] = deque()
    border = []
    border.extend((0, column) for column in range(width))
    if height > 1:
        border.extend((height - 1, column) for column in range(width))
    border.extend((row, 0) for row in range(height))
    if width > 1:
        border.extend((row, width - 1) for row in range(height))
    for row, column in border:
        if not bool(cluster_mask[row, column]) and not bool(reachable[row, column]):
            reachable[row, column] = True
            queue.append((row, column))
    while queue:
        row, column = queue.popleft()
        for dr, dc in ((-1, 0), (0, 1), (1, 0), (0, -1)):
            nr, nc = row + dr, column + dc
            if (
                0 <= nr < height
                and 0 <= nc < width
                and not bool(cluster_mask[nr, nc])
                and not bool(reachable[nr, nc])
            ):
                reachable[nr, nc] = True
                queue.append((nr, nc))
    return reachable


def _containment_records(
    cluster_labels: Array,
    face_cells: Sequence[Sequence[Cell]],
    cluster_cells: Sequence[Sequence[Cell]],
) -> Tuple[set[Tuple[int, int]], set[Tuple[int, int]]]:
    contains_faces: set[Tuple[int, int]] = set()
    contains_clusters: set[Tuple[int, int]] = set()
    for container_id, _ in enumerate(cluster_cells):
        reachable = _reachable_around_cluster(cluster_labels == container_id)
        for face_id, cells in enumerate(face_cells):
            if cells and all(not bool(reachable[row, column]) for row, column in cells):
                contains_faces.add((container_id, face_id))
        for child_id, cells in enumerate(cluster_cells):
            if child_id == container_id:
                continue
            if cells and all(not bool(reachable[row, column]) for row, column in cells):
                contains_clusters.add((container_id, child_id))
    return contains_faces, contains_clusters


def _direct_cluster_relation(
    container: int,
    child: int,
    contains_clusters: set[Tuple[int, int]],
) -> bool:
    return not any(
        intermediate not in (container, child)
        and (container, intermediate) in contains_clusters
        and (intermediate, child) in contains_clusters
        for intermediate in {item for pair in contains_clusters for item in pair}
    )


def _direct_face_relation(
    container: int,
    face: int,
    contains_faces: set[Tuple[int, int]],
    contains_clusters: set[Tuple[int, int]],
) -> bool:
    return not any(
        outer == container
        and (intermediate, face) in contains_faces
        for outer, intermediate in contains_clusters
    )


def build_planar_incidence(
    grid: Array,
    *,
    background: Optional[int] = None,
    limits: IncidenceLimits = DEFAULT_LIMITS,
) -> PlanarIncidenceGraph:
    """Compile one ARC input grid into a bounded planar incidence graph."""

    value = _validated_grid(grid, limits)
    background_value = infer_background(value) if background is None else int(background)
    shape = (int(value.shape[0]), int(value.shape[1]))

    face_cells = _component_cells(value == background_value, 4)
    boundary_cells = _monochrome_components(value, background_value)
    cluster_cells = _component_cells(value != background_value, 4)
    if len(face_cells) > limits.maximum_faces:
        raise PlanarIncidenceLimitError("background-face budget exceeded")
    if len(boundary_cells) > limits.maximum_boundary_components:
        raise PlanarIncidenceLimitError("boundary-component budget exceeded")
    if len(cluster_cells) > limits.maximum_boundary_clusters:
        raise PlanarIncidenceLimitError("boundary-cluster budget exceeded")

    face_labels = _label_map(shape, face_cells)
    boundary_labels = _label_map(shape, boundary_cells)
    cluster_labels = _label_map(shape, cluster_cells)
    component_contact, cluster_contact = _contact_records(
        face_labels,
        boundary_labels,
        cluster_labels,
    )
    component_touch, cluster_touch = _boundary_touch_records(
        boundary_labels, cluster_labels
    )
    separation = _face_separation_records(cluster_labels, face_labels, len(cluster_cells))
    contains_faces, contains_clusters = _containment_records(
        cluster_labels, face_cells, cluster_cells
    )

    evidence_count = sum(
        len(records)
        for records in (
            component_contact,
            cluster_contact,
            component_touch,
            cluster_touch,
            separation,
            contains_faces,
            contains_clusters,
        )
    )
    evidence_count += len(face_cells)  # one closure record per face
    evidence_count += sum(any(_side_contacts(cells, shape)) for cells in face_cells)
    evidence_count += sum(any(_side_contacts(cells, shape)) for cells in cluster_cells)
    if evidence_count > limits.maximum_evidence_records:
        raise PlanarIncidenceLimitError("incidence-evidence budget exceeded")

    component_cluster = {
        boundary_id: int(cluster_labels[cells[0][0], cells[0][1]])
        for boundary_id, cells in enumerate(boundary_cells)
    }
    colors = [int(value[cells[0][0], cells[0][1]]) for cells in boundary_cells]
    color_component_counts = Counter(colors)
    color_total_areas: Counter[int] = Counter()
    for color, cells in zip(colors, boundary_cells):
        color_total_areas[color] += len(cells)

    faces = []
    for face_id, cells in enumerate(face_cells):
        box = _box(cells)
        faces.append(
            BackgroundFace(
                face_id=face_id,
                cells=tuple(cells),
                area=len(cells),
                box=box,
                perimeter=_perimeter(cells, shape),
                canvas_contacts=_side_contacts(cells, shape),
                incident_boundary_ids=tuple(
                    sorted(
                        boundary_id
                        for (f_id, boundary_id), counts in component_contact.items()
                        if f_id == face_id and counts[0] > 0
                    )
                ),
                incident_cluster_ids=tuple(
                    sorted(
                        cluster_id
                        for (f_id, cluster_id), counts in cluster_contact.items()
                        if f_id == face_id and counts[0] > 0
                    )
                ),
                containing_cluster_ids=tuple(
                    sorted(container for container, f_id in contains_faces if f_id == face_id)
                ),
                shape_signature=_binary_shape_signature(cells, box),
            )
        )

    boundaries = []
    for boundary_id, cells in enumerate(boundary_cells):
        box = _box(cells)
        color = colors[boundary_id]
        boundaries.append(
            BoundaryComponent(
                boundary_id=boundary_id,
                color=color,
                cells=tuple(cells),
                area=len(cells),
                box=box,
                perimeter=_perimeter(cells, shape),
                canvas_contacts=_side_contacts(cells, shape),
                cluster_id=component_cluster[boundary_id],
                incident_face_ids=tuple(
                    sorted(
                        face_id
                        for (face_id, b_id), counts in component_contact.items()
                        if b_id == boundary_id and counts[0] > 0
                    )
                ),
                same_color_component_count=color_component_counts[color],
                same_color_total_area=color_total_areas[color],
                shape_signature=_binary_shape_signature(cells, box),
            )
        )

    clusters = []
    for cluster_id, cells in enumerate(cluster_cells):
        box = _box(cells)
        color_profile = Counter(int(value[row, column]) for row, column in cells)
        top, left, bottom, right = box
        crop = np.full(
            (bottom - top + 1, right - left + 1),
            background_value,
            dtype=value.dtype,
        )
        for row, column in cells:
            crop[row - top, column - left] = value[row, column]
        clusters.append(
            BoundaryCluster(
                cluster_id=cluster_id,
                cells=tuple(cells),
                area=len(cells),
                box=box,
                perimeter=_perimeter(cells, shape),
                canvas_contacts=_side_contacts(cells, shape),
                boundary_ids=tuple(
                    sorted(
                        boundary_id
                        for boundary_id, owner in component_cluster.items()
                        if owner == cluster_id
                    )
                ),
                incident_face_ids=tuple(
                    sorted(
                        face_id
                        for (face_id, c_id), counts in cluster_contact.items()
                        if c_id == cluster_id and counts[0] > 0
                    )
                ),
                containing_cluster_ids=tuple(
                    sorted(container for container, child in contains_clusters if child == cluster_id)
                ),
                contained_face_ids=tuple(
                    sorted(face_id for owner, face_id in contains_faces if owner == cluster_id)
                ),
                contained_cluster_ids=tuple(
                    sorted(child for owner, child in contains_clusters if owner == cluster_id)
                ),
                color_area_profile=tuple(sorted(color_profile.values())),
                shape_signature=canonical_palette_signature(crop, background_value),
            )
        )

    face_boundary_incidence = tuple(
        FaceBoundaryIncidence(face_id, boundary_id, counts[0], counts[1])
        for (face_id, boundary_id), counts in sorted(component_contact.items())
    )
    face_cluster_incidence = tuple(
        FaceClusterIncidence(face_id, cluster_id, counts[0], counts[1])
        for (face_id, cluster_id), counts in sorted(cluster_contact.items())
    )
    boundary_touches = tuple(
        BoundaryTouchEvidence(first, second, counts[0], counts[1])
        for (first, second), counts in sorted(component_touch.items())
    )
    cluster_touches = tuple(
        ClusterTouchEvidence(first, second, count)
        for (first, second), count in sorted(cluster_touch.items())
    )
    face_separations = tuple(
        FaceSeparationEvidence(first, second, cluster_id, counts[0], counts[1])
        for (first, second, cluster_id), counts in sorted(separation.items())
    )
    containment = []
    for container, face_id in sorted(contains_faces):
        containment.append(
            ContainmentEvidence(
                container,
                "face",
                face_id,
                _direct_face_relation(container, face_id, contains_faces, contains_clusters),
            )
        )
    for container, child in sorted(contains_clusters):
        containment.append(
            ContainmentEvidence(
                container,
                "cluster",
                child,
                _direct_cluster_relation(container, child, contains_clusters),
            )
        )

    canvas_incidence = []
    for face in faces:
        if face.touches_canvas:
            canvas_incidence.append(CanvasIncidence("face", face.face_id, face.canvas_contacts))
    for cluster in clusters:
        if cluster.touches_canvas:
            canvas_incidence.append(
                CanvasIncidence("cluster", cluster.cluster_id, cluster.canvas_contacts)
            )
    face_closures = tuple(
        FaceClosureEvidence(
            face.face_id,
            face.incident_cluster_ids,
            face.uses_virtual_canvas,
        )
        for face in faces
    )
    virtual_canvas = VirtualCanvasBoundary(
        height=shape[0],
        width=shape[1],
        face_ids=tuple(face.face_id for face in faces if face.touches_canvas),
        cluster_ids=tuple(cluster.cluster_id for cluster in clusters if cluster.touches_canvas),
    )
    return PlanarIncidenceGraph(
        shape=shape,
        background=background_value,
        faces=tuple(faces),
        boundaries=tuple(boundaries),
        boundary_clusters=tuple(clusters),
        face_boundary_incidence=face_boundary_incidence,
        face_cluster_incidence=face_cluster_incidence,
        boundary_touches=boundary_touches,
        cluster_touches=cluster_touches,
        face_separations=face_separations,
        containment=tuple(containment),
        canvas_incidence=tuple(canvas_incidence),
        face_closures=face_closures,
        virtual_canvas=virtual_canvas,
        canonical_grid_signature=canonical_palette_signature(value, background_value),
    )


__all__ = [
    "AmbiguousBackgroundError",
    "BackgroundHypothesis",
    "BackgroundFace",
    "BoundaryCluster",
    "BoundaryComponent",
    "BoundaryTouchEvidence",
    "CanvasIncidence",
    "ClusterTouchEvidence",
    "ContainmentEvidence",
    "DEFAULT_LIMITS",
    "FaceBoundaryIncidence",
    "FaceClosureEvidence",
    "FaceClusterIncidence",
    "FaceSeparationEvidence",
    "IncidenceLimits",
    "PLANAR_INCIDENCE_VERSION",
    "PlanarIncidenceError",
    "PlanarIncidenceGraph",
    "PlanarIncidenceLimitError",
    "VirtualCanvasBoundary",
    "build_planar_incidence",
    "canonical_palette_signature",
    "d4_views",
    "infer_background",
    "rank_background_hypotheses",
]
