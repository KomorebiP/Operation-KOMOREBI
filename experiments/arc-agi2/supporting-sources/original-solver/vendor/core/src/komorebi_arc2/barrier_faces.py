"""Input-only barrier-face hypotheses for bounded ARC canvases.

Ordinary color segmentation treats every non-background packet as an object.
That is often the wrong topology for tasks in which one color is a wall and
the remaining colors are payloads or distractors. This module constructs a
small, explicit portfolio of alternative planar interpretations:

* one hypothesis for each non-background color acting as the barrier; and
* one hypothesis in which the entire foreground acts as the barrier.

For a per-color hypothesis, other colors remain traversable occupants. A
short, monochromatic, one-cell-wide component may be absorbed when it exactly
fills a gap bracketed by barrier support.  This conservative test recognizes
a differently colored segment embedded in a wall without mistaking a solid
payload between two walls for wall support.  Background gaps are never
repaired, so a broken contour remains open.

The analysis is input-only. It never inspects demonstrations or expected
outputs, and it does not render predictions. Runtime records retain cells for
later execution, while :meth:`BarrierFaceHypothesis.normalized_summary`
provides coordinate-free and palette-free JSON provenance.
"""

from __future__ import annotations

from collections import Counter, defaultdict, deque
from dataclasses import dataclass
import hashlib
from typing import Dict, Optional, Sequence, Tuple

import numpy as np

try:
    from .planar_incidence import (
        BackgroundHypothesis,
        canonical_palette_signature,
        rank_background_hypotheses,
    )
except ImportError:  # standalone Kaggle runtime
    from planar_incidence import (
        BackgroundHypothesis,
        canonical_palette_signature,
        rank_background_hypotheses,
    )


Array = np.ndarray
Cell = Tuple[int, int]
Box = Tuple[int, int, int, int]
SideContacts = Tuple[int, int, int, int]  # top, right, bottom, left

BARRIER_FACE_VERSION = "1.2"


class BarrierFaceError(ValueError):
    """Base class for explicit barrier-face abstentions."""


class BarrierFaceLimitError(BarrierFaceError):
    """Raised before a configured representation budget would be exceeded."""


def _canonical_integral_role(value: object, label: str) -> int:
    if isinstance(value, bool) or not isinstance(value, (int, np.integer)):
        raise BarrierFaceError(f"{label} must be an integer color role")
    return int(value)


@dataclass(frozen=True)
class BarrierFaceLimits:
    maximum_height: int = 30
    maximum_width: int = 30
    maximum_palette: int = 16
    maximum_background_hypotheses: int = 4
    maximum_policies_per_background: int = 17
    maximum_faces_per_hypothesis: int = 256
    maximum_components_per_hypothesis: int = 256
    maximum_total_faces: int = 2048
    maximum_total_evidence: int = 8192
    maximum_structural_bridge: int = 4

    def __post_init__(self) -> None:
        positive = ("maximum_height", "maximum_width", "maximum_palette")
        for name in positive:
            value = getattr(self, name)
            if isinstance(value, bool) or not isinstance(value, (int, np.integer)) or int(value) <= 0:
                raise BarrierFaceLimitError(f"{name} must be a positive integer")
        for name in (
            "maximum_background_hypotheses",
            "maximum_policies_per_background",
            "maximum_faces_per_hypothesis",
            "maximum_components_per_hypothesis",
            "maximum_total_faces",
            "maximum_total_evidence",
            "maximum_structural_bridge",
        ):
            value = getattr(self, name)
            if isinstance(value, bool) or not isinstance(value, (int, np.integer)) or int(value) < 0:
                raise BarrierFaceLimitError(f"{name} must be a nonnegative integer")


DEFAULT_LIMITS = BarrierFaceLimits()


@dataclass(frozen=True)
class BarrierPolicy:
    kind: str  # ``per_color`` or ``whole_foreground``
    seed_color: Optional[int]

    def __post_init__(self) -> None:
        if self.kind not in ("per_color", "whole_foreground"):
            raise BarrierFaceError(f"unknown barrier policy {self.kind!r}")
        if self.kind == "per_color" and self.seed_color is None:
            raise BarrierFaceError("per-color policy requires a seed color")
        if self.kind == "per_color":
            _canonical_integral_role(self.seed_color, "barrier seed")
        if self.kind == "whole_foreground" and self.seed_color is not None:
            raise BarrierFaceError("whole-foreground policy has no seed color")


@dataclass(frozen=True)
class BarrierFace:
    face_id: int
    cells: Tuple[Cell, ...]
    area: int
    box: Box
    perimeter: int
    canvas_contacts: SideContacts
    background_area: int
    occupant_color_profile: Tuple[Tuple[int, int], ...]
    incident_component_ids: Tuple[int, ...]
    containing_component_ids: Tuple[int, ...]
    shape_signature: Tuple[int, ...]

    @property
    def touches_canvas(self) -> bool:
        return any(self.canvas_contacts)

    @property
    def uses_virtual_canvas(self) -> bool:
        return self.touches_canvas

    @property
    def strictly_enclosed(self) -> bool:
        return not self.touches_canvas

    @property
    def occupant_cells(self) -> int:
        return sum(count for _, count in self.occupant_color_profile)

    def normalized_feature(self) -> Tuple[object, ...]:
        height, width = _box_dimensions(self.box)
        return (
            self.area,
            min(height, width),
            max(height, width),
            self.perimeter,
            sum(value > 0 for value in self.canvas_contacts),
            tuple(sorted(self.canvas_contacts)),
            self.background_area,
            tuple(sorted(count for _, count in self.occupant_color_profile)),
            len(self.occupant_color_profile),
            len(self.incident_component_ids),
            len(self.containing_component_ids),
            self.shape_signature if self.strictly_enclosed else (),
        )


@dataclass(frozen=True)
class BarrierComponent:
    component_id: int
    cells: Tuple[Cell, ...]
    area: int
    box: Box
    perimeter: int
    canvas_contacts: SideContacts
    seed_cells: int
    absorbed_cells: int
    color_area_profile: Tuple[Tuple[int, int], ...]
    incident_face_ids: Tuple[int, ...]
    contained_face_ids: Tuple[int, ...]
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
            self.seed_cells,
            self.absorbed_cells,
            tuple(sorted(count for _, count in self.color_area_profile)),
            len(self.color_area_profile),
            len(self.incident_face_ids),
            len(self.contained_face_ids),
            self.shape_signature,
        )


@dataclass(frozen=True)
class BarrierIncidence:
    face_id: int
    component_id: int
    shared_wall: int
    contact_color_profile: Tuple[Tuple[int, int], ...]


@dataclass(frozen=True)
class BarrierCanvasClosure:
    face_id: int
    component_ids: Tuple[int, ...]
    uses_virtual_canvas: bool


@dataclass(frozen=True)
class BarrierFaceHypothesis:
    shape: Tuple[int, int]
    background: int
    background_rank: int
    background_tied: bool
    policy: BarrierPolicy
    wall_cells: Tuple[Cell, ...]
    seed_wall_cells: int
    absorbed_wall_cells: int
    wall_color_profile: Tuple[Tuple[int, int], ...]
    faces: Tuple[BarrierFace, ...]
    components: Tuple[BarrierComponent, ...]
    incidence: Tuple[BarrierIncidence, ...]
    canvas_closures: Tuple[BarrierCanvasClosure, ...]
    @property
    def enclosed_faces(self) -> Tuple[BarrierFace, ...]:
        return tuple(face for face in self.faces if face.strictly_enclosed)

    @property
    def canvas_faces(self) -> Tuple[BarrierFace, ...]:
        return tuple(face for face in self.faces if face.touches_canvas)

    def normalized_features(self) -> Tuple[object, ...]:
        face_features = {face.face_id: face.normalized_feature() for face in self.faces}
        component_features = {
            component.component_id: component.normalized_feature()
            for component in self.components
        }
        incidence = tuple(
            sorted(
                (
                    face_features[item.face_id],
                    component_features[item.component_id],
                    item.shared_wall,
                    tuple(sorted(count for _, count in item.contact_color_profile)),
                    len(item.contact_color_profile),
                )
                for item in self.incidence
            )
        )
        closures = tuple(
            sorted(
                (
                    face_features[item.face_id],
                    tuple(
                        sorted(component_features[index] for index in item.component_ids)
                    ),
                    item.uses_virtual_canvas,
                )
                for item in self.canvas_closures
            )
        )
        return (
            "barrier-face-normalized-v2",
            (min(self.shape), max(self.shape)),
            self.background_rank,
            self.background_tied,
            self.policy.kind,
            self.seed_wall_cells,
            self.absorbed_wall_cells,
            tuple(sorted(count for _, count in self.wall_color_profile)),
            tuple(sorted(face.normalized_feature() for face in self.faces)),
            tuple(sorted(component.normalized_feature() for component in self.components)),
            incidence,
            closures,
        )

    def normalized_digest(self) -> str:
        return hashlib.sha256(repr(self.normalized_features()).encode("utf-8")).hexdigest()

    def normalized_summary(self) -> Dict[str, object]:
        """Return coordinate-free, palette-free, JSON-safe provenance."""

        features = self.normalized_features()
        return {
            "schema": "barrier-face-summary-v2",
            "analysis_version": BARRIER_FACE_VERSION,
            "shape_orbit": [min(self.shape), max(self.shape)],
            "background_rank": int(self.background_rank),
            "background_tied": bool(self.background_tied),
            "policy": self.policy.kind,
            "normalized_digest": self.normalized_digest(),
            "counts": {
                "wall_cells": len(self.wall_cells),
                "seed_wall_cells": int(self.seed_wall_cells),
                "absorbed_wall_cells": int(self.absorbed_wall_cells),
                "wall_color_roles": len(self.wall_color_profile),
                "faces": len(self.faces),
                "strictly_enclosed_faces": len(self.enclosed_faces),
                "canvas_faces": len(self.canvas_faces),
                "barrier_components": len(self.components),
                "incidence_records": len(self.incidence),
            },
            "face_features": _json_safe(features[8]),
            "component_features": _json_safe(features[9]),
            "incidence_features": _json_safe(features[10]),
            "closure_features": _json_safe(features[11]),
        }


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


def _validated_grid(grid: Array, limits: BarrierFaceLimits) -> Array:
    raw = np.asarray(grid)
    if raw.ndim != 2 or raw.size == 0:
        raise BarrierFaceError("barrier-face analysis requires a nonempty 2D grid")
    height, width = raw.shape
    shape_orbit = (min(height, width), max(height, width))
    limit_orbit = (
        min(limits.maximum_height, limits.maximum_width),
        max(limits.maximum_height, limits.maximum_width),
    )
    if shape_orbit[0] > limit_orbit[0] or shape_orbit[1] > limit_orbit[1]:
        raise BarrierFaceLimitError(
            f"grid shape {raw.shape} exceeds {limits.maximum_height}x{limits.maximum_width}"
        )
    if not np.issubdtype(raw.dtype, np.number):
        raise BarrierFaceError("grid values must be numeric")
    if not np.all(np.isfinite(raw)):
        raise BarrierFaceError("grid values must be finite")
    if np.issubdtype(raw.dtype, np.floating):
        outside_int64 = np.any(raw < -float(2**63)) or np.any(raw >= float(2**63))
    elif np.issubdtype(raw.dtype, np.unsignedinteger):
        outside_int64 = bool(np.any(raw > np.iinfo(np.int64).max))
    else:
        outside_int64 = False
    if outside_int64:
        raise BarrierFaceError("grid values exceed the signed 64-bit range")
    if not np.issubdtype(raw.dtype, np.integer):
        if not np.all(np.equal(raw, np.floor(raw))):
            raise BarrierFaceError("grid values must be integers")
    if len(np.unique(raw)) > limits.maximum_palette:
        raise BarrierFaceLimitError("palette budget exceeded")
    return np.array(raw, dtype=np.int64, copy=True)


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


def _component_cells(mask: Array) -> Tuple[Tuple[Cell, ...], ...]:
    height, width = mask.shape
    visited = np.zeros(mask.shape, dtype=bool)
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
                for dr, dc in ((-1, 0), (0, 1), (1, 0), (0, -1)):
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


def _label_map(shape: Tuple[int, int], groups: Sequence[Sequence[Cell]]) -> Array:
    labels = np.full(shape, -1, dtype=np.int32)
    for group_id, cells in enumerate(groups):
        for row, column in cells:
            labels[row, column] = group_id
    return labels


def _box(cells: Sequence[Cell]) -> Box:
    rows = [row for row, _ in cells]
    columns = [column for _, column in cells]
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


def _binary_signature(cells: Sequence[Cell], box: Box) -> Tuple[int, ...]:
    top, left, bottom, right = box
    mask = np.zeros((bottom - top + 1, right - left + 1), dtype=np.int8)
    for row, column in cells:
        mask[row - top, column - left] = 1
    return canonical_palette_signature(mask, 0)


def _absorb_inline_wall_cells(
    grid: Array,
    background: int,
    seed_mask: Array,
    maximum_bridge: int,
) -> Array:
    """Absorb only isolated line components that exactly replace wall cells.

    Merely lying between two seed-wall cells is insufficient: every cell in
    the gap must form one complete monochromatic 4-connected component, and
    that component must be exactly the collinear gap.  In particular, rows or
    columns through a two-dimensional payload cannot be promoted into a wall.
    """

    wall = np.array(seed_mask, dtype=bool, copy=True)
    if maximum_bridge <= 0:
        return wall
    height, width = wall.shape

    component_for_cell: Dict[Cell, Tuple[Cell, ...]] = {}
    visited = np.zeros(wall.shape, dtype=bool)
    for start_row in range(height):
        for start_column in range(width):
            if (
                bool(visited[start_row, start_column])
                or int(grid[start_row, start_column]) == int(background)
                or bool(seed_mask[start_row, start_column])
            ):
                visited[start_row, start_column] = True
                continue
            color = int(grid[start_row, start_column])
            queue: deque[Cell] = deque([(start_row, start_column)])
            visited[start_row, start_column] = True
            cells = []
            while queue:
                row, column = queue.popleft()
                cells.append((row, column))
                for dr, dc in ((-1, 0), (0, 1), (1, 0), (0, -1)):
                    nr, nc = row + dr, column + dc
                    if (
                        0 <= nr < height
                        and 0 <= nc < width
                        and not bool(visited[nr, nc])
                        and not bool(seed_mask[nr, nc])
                        and int(grid[nr, nc]) == color
                    ):
                        visited[nr, nc] = True
                        queue.append((nr, nc))
            component = tuple(sorted(cells))
            for cell in component:
                component_for_cell[cell] = component

    additions = np.zeros(wall.shape, dtype=bool)

    def structurally_matches(segment: Tuple[Cell, ...]) -> bool:
        if not segment or len(segment) > maximum_bridge:
            return False
        colors = {int(grid[row, column]) for row, column in segment}
        if len(colors) != 1 or int(background) in colors:
            return False
        component = component_for_cell.get(segment[0], ())
        return component == tuple(sorted(segment))

    for row in range(height):
        positions = np.flatnonzero(seed_mask[row, :])
        for first, second in zip(positions[:-1], positions[1:]):
            segment = tuple((row, column) for column in range(first + 1, second))
            if structurally_matches(segment):
                for cell in segment:
                    additions[cell] = True
    for column in range(width):
        positions = np.flatnonzero(seed_mask[:, column])
        for first, second in zip(positions[:-1], positions[1:]):
            segment = tuple((row, column) for row in range(first + 1, second))
            if structurally_matches(segment):
                for cell in segment:
                    additions[cell] = True
    wall |= additions
    return wall


def _reachable_around_component(component_mask: Array) -> Array:
    height, width = component_mask.shape
    reachable = np.zeros(component_mask.shape, dtype=bool)
    queue: deque[Cell] = deque()
    border = [(0, column) for column in range(width)]
    if height > 1:
        border.extend((height - 1, column) for column in range(width))
    border.extend((row, 0) for row in range(height))
    if width > 1:
        border.extend((row, width - 1) for row in range(height))
    for row, column in border:
        if not bool(component_mask[row, column]) and not bool(reachable[row, column]):
            reachable[row, column] = True
            queue.append((row, column))
    while queue:
        row, column = queue.popleft()
        for dr, dc in ((-1, 0), (0, 1), (1, 0), (0, -1)):
            nr, nc = row + dr, column + dc
            if (
                0 <= nr < height
                and 0 <= nc < width
                and not bool(component_mask[nr, nc])
                and not bool(reachable[nr, nc])
            ):
                reachable[nr, nc] = True
                queue.append((nr, nc))
    return reachable


def _build_hypothesis(
    grid: Array,
    background: BackgroundHypothesis,
    policy: BarrierPolicy,
    limits: BarrierFaceLimits,
) -> BarrierFaceHypothesis:
    background_value = int(background.color)
    if policy.kind == "whole_foreground":
        seed = grid != background_value
        wall = seed.copy()
    else:
        seed = grid == int(policy.seed_color)
        wall = _absorb_inline_wall_cells(
            grid,
            background_value,
            seed,
            limits.maximum_structural_bridge,
        )
    if not np.any(wall):
        raise BarrierFaceError("barrier policy has empty wall support")

    face_cells = _component_cells(~wall)
    component_cells = _component_cells(wall)
    if len(face_cells) > limits.maximum_faces_per_hypothesis:
        raise BarrierFaceLimitError("face budget exceeded")
    if len(component_cells) > limits.maximum_components_per_hypothesis:
        raise BarrierFaceLimitError("barrier-component budget exceeded")
    shape = (int(grid.shape[0]), int(grid.shape[1]))
    component_labels = _label_map(shape, component_cells)

    contacts: Dict[Tuple[int, int], Counter[int]] = defaultdict(Counter)
    for face_id, cells in enumerate(face_cells):
        for row, column in cells:
            for dr, dc in ((-1, 0), (0, 1), (1, 0), (0, -1)):
                nr, nc = row + dr, column + dc
                if 0 <= nr < shape[0] and 0 <= nc < shape[1]:
                    component_id = int(component_labels[nr, nc])
                    if component_id >= 0:
                        contacts[(face_id, component_id)][int(grid[nr, nc])] += 1

    contains: set[Tuple[int, int]] = set()
    for component_id in range(len(component_cells)):
        reachable = _reachable_around_component(component_labels == component_id)
        for face_id, cells in enumerate(face_cells):
            if cells and all(not bool(reachable[row, column]) for row, column in cells):
                contains.add((component_id, face_id))

    faces = []
    for face_id, cells in enumerate(face_cells):
        box = _box(cells)
        occupants = Counter(
            int(grid[row, column])
            for row, column in cells
            if int(grid[row, column]) != background_value
        )
        faces.append(
            BarrierFace(
                face_id=face_id,
                cells=tuple(cells),
                area=len(cells),
                box=box,
                perimeter=_perimeter(cells, shape),
                canvas_contacts=_side_contacts(cells, shape),
                background_area=sum(
                    int(grid[row, column]) == background_value for row, column in cells
                ),
                occupant_color_profile=tuple(sorted(occupants.items())),
                incident_component_ids=tuple(
                    sorted(component for f_id, component in contacts if f_id == face_id)
                ),
                containing_component_ids=tuple(
                    sorted(component for component, f_id in contains if f_id == face_id)
                ),
                shape_signature=_binary_signature(cells, box),
            )
        )

    components = []
    for component_id, cells in enumerate(component_cells):
        box = _box(cells)
        profile = Counter(int(grid[row, column]) for row, column in cells)
        components.append(
            BarrierComponent(
                component_id=component_id,
                cells=tuple(cells),
                area=len(cells),
                box=box,
                perimeter=_perimeter(cells, shape),
                canvas_contacts=_side_contacts(cells, shape),
                seed_cells=sum(bool(seed[row, column]) for row, column in cells),
                absorbed_cells=sum(
                    bool(wall[row, column]) and not bool(seed[row, column])
                    for row, column in cells
                ),
                color_area_profile=tuple(sorted(profile.items())),
                incident_face_ids=tuple(
                    sorted(face_id for face_id, c_id in contacts if c_id == component_id)
                ),
                contained_face_ids=tuple(
                    sorted(face_id for c_id, face_id in contains if c_id == component_id)
                ),
                shape_signature=_binary_signature(cells, box),
            )
        )

    incidence = tuple(
        BarrierIncidence(
            face_id,
            component_id,
            sum(profile.values()),
            tuple(sorted(profile.items())),
        )
        for (face_id, component_id), profile in sorted(contacts.items())
    )
    closures = tuple(
        BarrierCanvasClosure(
            face.face_id,
            face.incident_component_ids,
            face.uses_virtual_canvas,
        )
        for face in faces
    )
    evidence_count = len(incidence) + len(closures) + len(contains)
    if evidence_count > limits.maximum_total_evidence:
        raise BarrierFaceLimitError("barrier evidence budget exceeded")

    wall_profile = Counter(int(grid[row, column]) for row, column in zip(*np.nonzero(wall)))
    wall_cells = tuple((int(row), int(column)) for row, column in zip(*np.nonzero(wall)))
    return BarrierFaceHypothesis(
        shape=shape,
        background=background_value,
        background_rank=int(background.rank),
        background_tied=bool(background.tied),
        policy=policy,
        wall_cells=wall_cells,
        seed_wall_cells=int(np.count_nonzero(seed)),
        absorbed_wall_cells=int(np.count_nonzero(wall & ~seed)),
        wall_color_profile=tuple(sorted(wall_profile.items())),
        faces=tuple(faces),
        components=tuple(components),
        incidence=incidence,
        canvas_closures=closures,
    )


def build_barrier_face_hypotheses(
    grid: Array,
    *,
    backgrounds: Optional[Sequence[int]] = None,
    maximum_background_rank: int = 0,
    limits: BarrierFaceLimits = DEFAULT_LIMITS,
) -> Tuple[BarrierFaceHypothesis, ...]:
    """Build a bounded portfolio of per-color and whole-foreground faces.

    With no explicit ``backgrounds``, every hypothesis at or above
    ``maximum_background_rank`` is retained. The default therefore keeps all
    top-ranked backgrounds when structural evidence is tied.
    """

    value = _validated_grid(grid, limits)
    if limits.maximum_structural_bridge < 0:
        raise BarrierFaceError("maximum structural bridge must be nonnegative")
    ranked = rank_background_hypotheses(value)
    if backgrounds is None:
        selected_backgrounds = tuple(
            record for record in ranked if record.rank <= maximum_background_rank
        )
    else:
        requested = tuple(
            dict.fromkeys(
                _canonical_integral_role(color, "explicit background")
                for color in backgrounds
            )
        )
        available = {record.color: record for record in ranked}
        missing = [color for color in requested if color not in available]
        if missing:
            raise BarrierFaceError(f"explicit background colors are absent: {missing}")
        selected_backgrounds = tuple(available[color] for color in requested)
    if not selected_backgrounds:
        raise BarrierFaceError("no background hypotheses selected")
    if len(selected_backgrounds) > limits.maximum_background_hypotheses:
        raise BarrierFaceLimitError("background-hypothesis budget exceeded")

    result = []
    total_faces = 0
    total_evidence = 0
    for background in selected_backgrounds:
        foreground_colors = tuple(
            int(color) for color in np.unique(value) if int(color) != background.color
        )
        if not foreground_colors:
            continue
        policies = tuple(
            [BarrierPolicy("per_color", color) for color in foreground_colors]
            + [BarrierPolicy("whole_foreground", None)]
        )
        if len(policies) > limits.maximum_policies_per_background:
            raise BarrierFaceLimitError("barrier-policy budget exceeded")
        for policy in policies:
            hypothesis = _build_hypothesis(value, background, policy, limits)
            total_faces += len(hypothesis.faces)
            total_evidence += len(hypothesis.incidence) + len(hypothesis.canvas_closures)
            total_evidence += sum(
                len(face.containing_component_ids) for face in hypothesis.faces
            )
            if total_faces > limits.maximum_total_faces:
                raise BarrierFaceLimitError("portfolio face budget exceeded")
            if total_evidence > limits.maximum_total_evidence:
                raise BarrierFaceLimitError("portfolio evidence budget exceeded")
            result.append(hypothesis)
    # Raw palette labels never determine portfolio priority. Exact normalized
    # ties are semantically interchangeable and remain adjacent.
    return tuple(sorted(result, key=lambda item: item.normalized_features()))


def build_barrier_face_hypothesis(
    grid: Array,
    *,
    background: int,
    policy: BarrierPolicy,
    limits: BarrierFaceLimits = DEFAULT_LIMITS,
) -> BarrierFaceHypothesis:
    """Build exactly one explicitly chosen input-only barrier hypothesis."""

    value = _validated_grid(grid, limits)
    if limits.maximum_structural_bridge < 0:
        raise BarrierFaceError("maximum structural bridge must be nonnegative")
    available = {item.color: item for item in rank_background_hypotheses(value)}
    background_value = _canonical_integral_role(background, "explicit background")
    if background_value not in available:
        raise BarrierFaceError("explicit background color is absent")
    if policy.kind == "per_color":
        if int(policy.seed_color) == background_value:
            raise BarrierFaceError("barrier seed cannot equal the background")
        if not np.any(value == int(policy.seed_color)):
            raise BarrierFaceError("barrier seed color is absent")
    elif not np.any(value != background_value):
        raise BarrierFaceError("whole-foreground barrier support is empty")
    return _build_hypothesis(value, available[background_value], policy, limits)


__all__ = [
    "BARRIER_FACE_VERSION",
    "BarrierCanvasClosure",
    "BarrierComponent",
    "BarrierFace",
    "BarrierFaceError",
    "BarrierFaceHypothesis",
    "BarrierFaceLimitError",
    "BarrierFaceLimits",
    "BarrierIncidence",
    "BarrierPolicy",
    "DEFAULT_LIMITS",
    "build_barrier_face_hypotheses",
    "build_barrier_face_hypothesis",
]
