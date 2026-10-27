"""ARC realization of LASM Program IR v2.

The runtime exposes two coupled packet systems:

* foreground objects, represented as color-connected components
* ambient faces, represented as background-connected components

The representation is deliberately finite, immutable, and role based.  Object
identifiers are deterministic scene-local addresses, never task identifiers.
"""

from __future__ import annotations

import math
from collections import Counter, deque
from dataclasses import dataclass
from typing import Iterable, Iterator, Sequence

import numpy as np

from .interpreter import DefaultRuntimeAdapter, ExecutionError, ExecutionLimitError, ExecutionLimits
from .registry import OperatorDefinition, OperatorRegistry
from .types import ValueType

Grid = tuple[tuple[int, ...], ...]


class SceneError(ValueError):
    pass


class SceneAmbiguityError(SceneError):
    pass


@dataclass(frozen=True, order=True)
class Cell:
    row: int
    column: int

    def shifted(self, delta_row: int, delta_column: int) -> "Cell":
        return Cell(self.row + int(delta_row), self.column + int(delta_column))


@dataclass(frozen=True, order=True)
class Box:
    top: int
    left: int
    bottom: int
    right: int

    def __post_init__(self) -> None:
        if self.bottom < self.top or self.right < self.left:
            raise ValueError("box bounds are inverted")

    @property
    def height(self) -> int:
        return self.bottom - self.top + 1

    @property
    def width(self) -> int:
        return self.right - self.left + 1

    @property
    def area(self) -> int:
        return self.height * self.width

    @property
    def center(self) -> tuple[float, float]:
        return ((self.top + self.bottom) / 2.0, (self.left + self.right) / 2.0)


@dataclass(frozen=True)
class ArcObject:
    object_id: str
    color: int
    cells: tuple[Cell, ...]
    box: Box
    source_shape: tuple[int, int]

    @property
    def area(self) -> int:
        return len(self.cells)

    @property
    def height(self) -> int:
        return self.box.height

    @property
    def width(self) -> int:
        return self.box.width

    @property
    def bbox_area(self) -> int:
        return self.box.area

    @property
    def density(self) -> float:
        return self.area / self.bbox_area

    @property
    def normalized_cells(self) -> tuple[Cell, ...]:
        return tuple(
            Cell(cell.row - self.box.top, cell.column - self.box.left)
            for cell in self.cells
        )

    @property
    def shape_key(self) -> tuple[tuple[int, int], ...]:
        return tuple((cell.row, cell.column) for cell in self.normalized_cells)

    def with_cells(self, cells: Iterable[Cell], *, color: int | None = None) -> "ArcObject":
        ordered = tuple(sorted(set(cells)))
        if not ordered:
            raise SceneError("an object cannot have empty support")
        rows = [cell.row for cell in ordered]
        columns = [cell.column for cell in ordered]
        return ArcObject(
            object_id=self.object_id,
            color=self.color if color is None else int(color),
            cells=ordered,
            box=Box(min(rows), min(columns), max(rows), max(columns)),
            source_shape=self.source_shape,
        )


@dataclass(frozen=True)
class AmbientFace:
    face_id: str
    cells: tuple[Cell, ...]
    box: Box
    touches_border: bool
    source_shape: tuple[int, int]

    @property
    def area(self) -> int:
        return len(self.cells)

    @property
    def is_hole(self) -> bool:
        return not self.touches_border


@dataclass(frozen=True)
class Relation:
    kind: str
    source: str
    target: str
    value: float | int | str | bool


@dataclass(frozen=True)
class Edit:
    edit_id: str
    kind: str
    cells: tuple[Cell, ...]
    source_color: int | None
    target_color: int | None
    source_shape: tuple[int, int]
    target_shape: tuple[int, int]

    @property
    def size(self) -> int:
        return len(self.cells)


@dataclass(frozen=True)
class Scene:
    grid: Grid
    background: int
    objects: tuple[ArcObject, ...]
    faces: tuple[AmbientFace, ...]
    relations: tuple[Relation, ...]

    @property
    def shape(self) -> tuple[int, int]:
        return (len(self.grid), len(self.grid[0]))


@dataclass(frozen=True)
class Canvas:
    grid: Grid
    background: int

    @property
    def shape(self) -> tuple[int, int]:
        return (len(self.grid), len(self.grid[0]))


@dataclass(frozen=True)
class Layout:
    items: tuple[Grid, ...]
    axis: str
    gap: int
    background: int
    columns: int | None = None


def _array(grid: object) -> np.ndarray:
    raw = np.asarray(grid)
    if raw.ndim != 2 or raw.size == 0:
        raise SceneError("ARC grids must be nonempty two-dimensional arrays")
    if not np.issubdtype(raw.dtype, np.integer):
        if not np.all(np.isfinite(raw)) or not np.all(raw == np.rint(raw)):
            raise SceneError("ARC grids require finite integer colors")
    value = np.asarray(raw, dtype=np.int16)
    if np.any(value < 0) or np.any(value > 9):
        raise SceneError("ARC colors must lie in [0, 9]")
    if value.shape[0] > 60 or value.shape[1] > 60:
        raise SceneError("grid exceeds the Program IR v2 safety envelope")
    return value.copy()


def freeze_grid(grid: object) -> Grid:
    a = _array(grid)
    return tuple(tuple(int(value) for value in row) for row in a.tolist())


def infer_background(grid: object) -> int:
    a = _array(grid)
    counts = Counter(int(value) for value in a.ravel())
    maximum = max(counts.values())
    modes = sorted(color for color, count in counts.items() if count == maximum)
    if len(modes) == 1:
        return modes[0]
    corners = [int(a[0, 0]), int(a[0, -1]), int(a[-1, 0]), int(a[-1, -1])]
    corner_counts = Counter(corners)
    corner_maximum = max(corner_counts.values())
    corner_modes = sorted(color for color, count in corner_counts.items() if count == corner_maximum)
    candidates = [color for color in corner_modes if color in modes]
    if len(candidates) == 1:
        return candidates[0]
    raise SceneAmbiguityError("background color is not uniquely determined")


def _components(mask: np.ndarray) -> tuple[tuple[Cell, ...], ...]:
    height, width = mask.shape
    seen = np.zeros_like(mask, dtype=bool)
    output: list[tuple[Cell, ...]] = []
    for row in range(height):
        for column in range(width):
            if not bool(mask[row, column]) or bool(seen[row, column]):
                continue
            queue: deque[tuple[int, int]] = deque([(row, column)])
            seen[row, column] = True
            cells: list[Cell] = []
            while queue:
                current_row, current_column = queue.popleft()
                cells.append(Cell(current_row, current_column))
                for delta_row, delta_column in ((-1, 0), (1, 0), (0, -1), (0, 1)):
                    neighbor_row = current_row + delta_row
                    neighbor_column = current_column + delta_column
                    if (
                        0 <= neighbor_row < height
                        and 0 <= neighbor_column < width
                        and bool(mask[neighbor_row, neighbor_column])
                        and not bool(seen[neighbor_row, neighbor_column])
                    ):
                        seen[neighbor_row, neighbor_column] = True
                        queue.append((neighbor_row, neighbor_column))
            output.append(tuple(sorted(cells)))
    return tuple(output)


def _box(cells: Sequence[Cell]) -> Box:
    return Box(
        min(cell.row for cell in cells),
        min(cell.column for cell in cells),
        max(cell.row for cell in cells),
        max(cell.column for cell in cells),
    )


def _touching(left: ArcObject, right: ArcObject, *, diagonal: bool = False) -> bool:
    right_cells = set(right.cells)
    directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]
    if diagonal:
        directions += [(-1, -1), (-1, 1), (1, -1), (1, 1)]
    return any(
        Cell(cell.row + delta_row, cell.column + delta_column) in right_cells
        for cell in left.cells
        for delta_row, delta_column in directions
    )


def _manhattan(left: ArcObject, right: ArcObject) -> int:
    return min(
        abs(a.row - b.row) + abs(a.column - b.column)
        for a in left.cells
        for b in right.cells
    )


def analyze_grid(grid: object) -> Scene:
    a = _array(grid)
    background = infer_background(a)
    shape = (int(a.shape[0]), int(a.shape[1]))
    objects: list[ArcObject] = []
    for color in sorted(int(value) for value in np.unique(a) if int(value) != background):
        for cells in _components(a == color):
            objects.append(
                ArcObject(
                    object_id="",
                    color=color,
                    cells=cells,
                    box=_box(cells),
                    source_shape=shape,
                )
            )
    objects.sort(key=lambda item: (item.box.top, item.box.left, item.color, item.area, item.shape_key))
    objects = [
        ArcObject(
            object_id=f"object:{index}",
            color=item.color,
            cells=item.cells,
            box=item.box,
            source_shape=item.source_shape,
        )
        for index, item in enumerate(objects)
    ]

    faces: list[AmbientFace] = []
    for cells in _components(a == background):
        touches = any(
            cell.row in {0, shape[0] - 1} or cell.column in {0, shape[1] - 1}
            for cell in cells
        )
        faces.append(AmbientFace("", cells, _box(cells), touches, shape))
    faces.sort(key=lambda item: (not item.touches_border, item.box.top, item.box.left, -item.area))
    faces = [
        AmbientFace(
            face_id=f"face:{index}",
            cells=item.cells,
            box=item.box,
            touches_border=item.touches_border,
            source_shape=item.source_shape,
        )
        for index, item in enumerate(faces)
    ]

    relations: list[Relation] = []
    for left in objects:
        for right in objects:
            if left.object_id == right.object_id:
                continue
            left_center = left.box.center
            right_center = right.box.center
            if left.box.right < right.box.left:
                relations.append(Relation("left_of", left.object_id, right.object_id, True))
            if left.box.bottom < right.box.top:
                relations.append(Relation("above", left.object_id, right.object_id, True))
            if left.shape_key == right.shape_key:
                relations.append(Relation("same_shape", left.object_id, right.object_id, True))
            if left.color == right.color:
                relations.append(Relation("same_color", left.object_id, right.object_id, True))
            if _touching(left, right):
                relations.append(Relation("touching4", left.object_id, right.object_id, True))
            if _touching(left, right, diagonal=True):
                relations.append(Relation("touching8", left.object_id, right.object_id, True))
            relations.append(Relation("manhattan", left.object_id, right.object_id, _manhattan(left, right)))
            relations.append(Relation("center_delta_row", left.object_id, right.object_id, right_center[0] - left_center[0]))
            relations.append(Relation("center_delta_column", left.object_id, right.object_id, right_center[1] - left_center[1]))
    for obj in objects:
        obj_cells = set(obj.cells)
        for face in faces:
            face_cells = set(face.cells)
            boundary_contact = any(
                Cell(cell.row + delta_row, cell.column + delta_column) in face_cells
                for cell in obj_cells
                for delta_row, delta_column in ((-1, 0), (1, 0), (0, -1), (0, 1))
            )
            if boundary_contact:
                relations.append(Relation("bounds_face", obj.object_id, face.face_id, True))
    relations.sort(key=lambda item: (item.kind, item.source, item.target, repr(item.value)))
    return Scene(freeze_grid(a), background, tuple(objects), tuple(faces), tuple(relations))


def scene_grid(scene: Scene) -> np.ndarray:
    return np.asarray(scene.grid, dtype=np.int16).copy()


def foreground_objects(scene: Scene) -> tuple[ArcObject, ...]:
    return scene.objects


def ambient_faces(scene: Scene) -> tuple[AmbientFace, ...]:
    return scene.faces


def scene_relations(scene: Scene) -> tuple[Relation, ...]:
    return scene.relations


def background_color(scene: Scene) -> int:
    return scene.background


def object_area(obj: ArcObject) -> float:
    return float(obj.area)


def object_bbox_area(obj: ArcObject) -> float:
    return float(obj.bbox_area)


def object_height(obj: ArcObject) -> float:
    return float(obj.height)


def object_width(obj: ArcObject) -> float:
    return float(obj.width)


def object_density(obj: ArcObject) -> float:
    return float(obj.density)


def object_color(obj: ArcObject) -> int:
    return obj.color


def object_cells(obj: ArcObject) -> tuple[Cell, ...]:
    return obj.cells


def object_box(obj: ArcObject) -> Box:
    return obj.box


def object_is_singleton(obj: ArcObject) -> bool:
    return obj.area == 1


def object_is_square(obj: ArcObject) -> bool:
    return obj.height == obj.width


def object_is_solid_rectangle(obj: ArcObject) -> bool:
    return obj.area == obj.bbox_area


def same_shape(left: ArcObject, right: ArcObject) -> bool:
    return left.shape_key == right.shape_key


def same_color(left: ArcObject, right: ArcObject) -> bool:
    return left.color == right.color


def manhattan_distance(left: ArcObject, right: ArcObject) -> float:
    return float(_manhattan(left, right))


def face_area(face: AmbientFace) -> float:
    return float(face.area)


def face_cells(face: AmbientFace) -> tuple[Cell, ...]:
    return face.cells


def face_is_hole(face: AmbientFace) -> bool:
    return face.is_hole


def relation_kind(relation: Relation) -> str:
    return relation.kind


def relation_value(relation: Relation) -> float:
    if isinstance(relation.value, bool):
        return float(int(relation.value))
    if isinstance(relation.value, (int, float)):
        return float(relation.value)
    raise SceneError("relation value is not numeric")


def object_set_singleton(obj: ArcObject) -> tuple[ArcObject, ...]:
    return (obj,)


def face_set_singleton(face: AmbientFace) -> tuple[AmbientFace, ...]:
    return (face,)


def cell_set_singleton(cell: Cell) -> tuple[Cell, ...]:
    return (cell,)


def object_set_count(objects: Sequence[ArcObject]) -> int:
    return len(objects)


def face_set_count(faces: Sequence[AmbientFace]) -> int:
    return len(faces)


def cell_set_count(cells: Sequence[Cell]) -> int:
    return len(cells)


def integer_equal(left: int, right: int) -> bool:
    return int(left) == int(right)


def scalar_equal(left: float, right: float) -> bool:
    return float(left) == float(right)


def scalar_less(left: float, right: float) -> bool:
    return float(left) < float(right)


def scalar_greater(left: float, right: float) -> bool:
    return float(left) > float(right)


def bool_not(value: bool) -> bool:
    return not bool(value)


def bool_and(left: bool, right: bool) -> bool:
    return bool(left) and bool(right)


def bool_or(left: bool, right: bool) -> bool:
    return bool(left) or bool(right)


def _mask(shape: tuple[int, int], cells: Iterable[Cell]) -> np.ndarray:
    output = np.zeros(shape, dtype=bool)
    for cell in cells:
        if 0 <= cell.row < shape[0] and 0 <= cell.column < shape[1]:
            output[cell.row, cell.column] = True
    return output


def object_mask(scene: Scene, obj: ArcObject) -> np.ndarray:
    return _mask(scene.shape, obj.cells)


def face_mask(scene: Scene, face: AmbientFace) -> np.ndarray:
    return _mask(scene.shape, face.cells)


def foreground_mask(scene: Scene) -> np.ndarray:
    return _mask(scene.shape, (cell for obj in scene.objects for cell in obj.cells))


def mask_union(left: object, right: object) -> np.ndarray:
    a, b = np.asarray(left, dtype=bool), np.asarray(right, dtype=bool)
    if a.shape != b.shape:
        raise SceneError("mask shapes do not match")
    return np.logical_or(a, b)


def mask_intersection(left: object, right: object) -> np.ndarray:
    a, b = np.asarray(left, dtype=bool), np.asarray(right, dtype=bool)
    if a.shape != b.shape:
        raise SceneError("mask shapes do not match")
    return np.logical_and(a, b)


def mask_difference(left: object, right: object) -> np.ndarray:
    a, b = np.asarray(left, dtype=bool), np.asarray(right, dtype=bool)
    if a.shape != b.shape:
        raise SceneError("mask shapes do not match")
    return np.logical_and(a, np.logical_not(b))


def mask_dilate4(mask: object) -> np.ndarray:
    a = np.asarray(mask, dtype=bool)
    output = a.copy()
    output[1:, :] |= a[:-1, :]
    output[:-1, :] |= a[1:, :]
    output[:, 1:] |= a[:, :-1]
    output[:, :-1] |= a[:, 1:]
    return output


def mask_dilate_within(mask: object, allowed: object) -> np.ndarray:
    a, permitted = np.asarray(mask, dtype=bool), np.asarray(allowed, dtype=bool)
    if a.shape != permitted.shape:
        raise SceneError("mask shapes do not match")
    return np.logical_and(mask_dilate4(a), permitted)


def mask_erode4(mask: object) -> np.ndarray:
    a = np.asarray(mask, dtype=bool)
    output = a.copy()
    output[0, :] = False
    output[-1, :] = False
    output[:, 0] = False
    output[:, -1] = False
    interior = a[1:-1, 1:-1]
    output[1:-1, 1:-1] = (
        interior
        & a[:-2, 1:-1]
        & a[2:, 1:-1]
        & a[1:-1, :-2]
        & a[1:-1, 2:]
    )
    return output


def _direction(value: str) -> tuple[int, int]:
    directions = {
        "north": (-1, 0), "south": (1, 0), "west": (0, -1), "east": (0, 1),
        "north_west": (-1, -1), "north_east": (-1, 1),
        "south_west": (1, -1), "south_east": (1, 1),
    }
    try:
        return directions[str(value)]
    except KeyError as error:
        raise SceneError(f"unknown direction {value!r}") from error


def translate_object(obj: ArcObject, direction: str, distance: int) -> ArcObject:
    delta_row, delta_column = _direction(direction)
    return obj.with_cells(
        (cell.shifted(delta_row * int(distance), delta_column * int(distance)) for cell in obj.cells)
    )


def recolor_object(obj: ArcObject, color: int) -> ArcObject:
    if not 0 <= int(color) <= 9:
        raise SceneError("ARC colors must lie in [0, 9]")
    return obj.with_cells(obj.cells, color=int(color))


def normalize_object(obj: ArcObject) -> ArcObject:
    return obj.with_cells(obj.normalized_cells)


def rotate_object_90(obj: ArcObject) -> ArcObject:
    normalized = obj.normalized_cells
    rotated = [Cell(cell.column, obj.height - 1 - cell.row) for cell in normalized]
    return obj.with_cells(rotated)


def reflect_object_horizontal(obj: ArcObject) -> ArcObject:
    normalized = obj.normalized_cells
    reflected = [Cell(cell.row, obj.width - 1 - cell.column) for cell in normalized]
    return obj.with_cells(reflected)


def canvas_from_grid(grid: object) -> Canvas:
    frozen = freeze_grid(grid)
    return Canvas(frozen, infer_background(frozen))


def blank_canvas_like(grid: object, color: int) -> Canvas:
    a = _array(grid)
    if not 0 <= int(color) <= 9:
        raise SceneError("ARC colors must lie in [0, 9]")
    return Canvas(freeze_grid(np.full(a.shape, int(color), dtype=np.int16)), int(color))


def blank_canvas(height: int, width: int, color: int) -> Canvas:
    if not (1 <= int(height) <= 60 and 1 <= int(width) <= 60):
        raise SceneError("canvas dimensions must lie in [1, 60]")
    return Canvas(
        freeze_grid(np.full((int(height), int(width)), int(color), dtype=np.int16)),
        int(color),
    )


def canvas_grid(canvas: Canvas) -> np.ndarray:
    return np.asarray(canvas.grid, dtype=np.int16).copy()


def _object_grid(obj: ArcObject, background: int, *, normalize: bool = True) -> np.ndarray:
    if normalize:
        height, width = obj.height, obj.width
        output = np.full((height, width), background, dtype=np.int16)
        for cell in obj.normalized_cells:
            output[cell.row, cell.column] = obj.color
        return output
    output = np.full(obj.source_shape, background, dtype=np.int16)
    for cell in obj.cells:
        if 0 <= cell.row < output.shape[0] and 0 <= cell.column < output.shape[1]:
            output[cell.row, cell.column] = obj.color
    return output


def layout_row(objects: Sequence[ArcObject], gap: int, background: int) -> Layout:
    return Layout(tuple(freeze_grid(_object_grid(obj, background)) for obj in objects), "row", int(gap), int(background))


def layout_column(objects: Sequence[ArcObject], gap: int, background: int) -> Layout:
    return Layout(tuple(freeze_grid(_object_grid(obj, background)) for obj in objects), "column", int(gap), int(background))


def layout_grid(objects: Sequence[ArcObject], columns: int, gap: int, background: int) -> Layout:
    if int(columns) <= 0:
        raise SceneError("layout columns must be positive")
    return Layout(tuple(freeze_grid(_object_grid(obj, background)) for obj in objects), "grid", int(gap), int(background), int(columns))


def _pack_arrays(arrays: Sequence[np.ndarray], background: int, axis: str, gap: int, columns: int | None = None) -> np.ndarray:
    if not arrays:
        raise SceneAmbiguityError("cannot pack an empty collection")
    if axis == "row":
        height = max(a.shape[0] for a in arrays)
        width = sum(a.shape[1] for a in arrays) + gap * (len(arrays) - 1)
        output = np.full((height, width), background, dtype=np.int16)
        cursor = 0
        for a in arrays:
            output[: a.shape[0], cursor : cursor + a.shape[1]] = a
            cursor += a.shape[1] + gap
        return output
    if axis == "column":
        height = sum(a.shape[0] for a in arrays) + gap * (len(arrays) - 1)
        width = max(a.shape[1] for a in arrays)
        output = np.full((height, width), background, dtype=np.int16)
        cursor = 0
        for a in arrays:
            output[cursor : cursor + a.shape[0], : a.shape[1]] = a
            cursor += a.shape[0] + gap
        return output
    if axis == "grid":
        column_count = int(columns or math.ceil(math.sqrt(len(arrays))))
        row_count = math.ceil(len(arrays) / column_count)
        cell_height = max(a.shape[0] for a in arrays)
        cell_width = max(a.shape[1] for a in arrays)
        output = np.full(
            (row_count * cell_height + gap * (row_count - 1), column_count * cell_width + gap * (column_count - 1)),
            background,
            dtype=np.int16,
        )
        for index, a in enumerate(arrays):
            row, column = divmod(index, column_count)
            top = row * (cell_height + gap)
            left = column * (cell_width + gap)
            output[top : top + a.shape[0], left : left + a.shape[1]] = a
        return output
    raise SceneError(f"unknown layout axis {axis!r}")


def render_layout(layout: Layout) -> np.ndarray:
    arrays = [np.asarray(grid, dtype=np.int16) for grid in layout.items]
    return _pack_arrays(arrays, layout.background, layout.axis, layout.gap, layout.columns)



def grid_height(grid: object) -> int:
    return int(_array(grid).shape[0])


def grid_width(grid: object) -> int:
    return int(_array(grid).shape[1])


def integer_add(left: int, right: int) -> int:
    return int(left) + int(right)


def integer_multiply(left: int, right: int) -> int:
    return int(left) * int(right)


def integer_maximum(left: int, right: int) -> int:
    return max(int(left), int(right))


def integer_ceil_sqrt(value: int) -> int:
    if int(value) < 0:
        raise SceneError("ceil_sqrt requires a nonnegative integer")
    return int(math.ceil(math.sqrt(int(value))))


def object_to_grid(obj: ArcObject, background: int) -> np.ndarray:
    return _object_grid(obj, int(background), normalize=True)


def grid_set_singleton(grid: object) -> tuple[np.ndarray, ...]:
    return (_array(grid),)


def derive_edits(source: object, target: object) -> tuple[Edit, ...]:
    left, right = _array(source), _array(target)
    if left.shape != right.shape:
        return (
            Edit(
                edit_id="edit:0",
                kind="reshape",
                cells=(),
                source_color=None,
                target_color=None,
                source_shape=(int(left.shape[0]), int(left.shape[1])),
                target_shape=(int(right.shape[0]), int(right.shape[1])),
            ),
        )
    changed = left != right
    if not np.any(changed):
        return ()
    source_background = infer_background(left)
    try:
        target_background = infer_background(right)
    except SceneAmbiguityError:
        target_background = source_background
    edits: list[Edit] = []
    for index, cells in enumerate(_components(changed)):
        source_colors = Counter(int(left[cell.row, cell.column]) for cell in cells)
        target_colors = Counter(int(right[cell.row, cell.column]) for cell in cells)
        source_color = source_colors.most_common(1)[0][0] if len(source_colors) == 1 else None
        target_color = target_colors.most_common(1)[0][0] if len(target_colors) == 1 else None
        if source_color == source_background and target_color != target_background:
            kind = "construct"
        elif target_color == target_background and source_color != source_background:
            kind = "erase"
        elif source_color is not None and target_color is not None:
            kind = "recolor"
        else:
            kind = "mixed_edit"
        edits.append(
            Edit(
                edit_id=f"edit:{index}",
                kind=kind,
                cells=cells,
                source_color=source_color,
                target_color=target_color,
                source_shape=(int(left.shape[0]), int(left.shape[1])),
                target_shape=(int(right.shape[0]), int(right.shape[1])),
            )
        )
    return tuple(edits)


def edit_kind(edit: Edit) -> str:
    return edit.kind


def edit_size(edit: Edit) -> float:
    return float(edit.size)


def edit_cells(edit: Edit) -> tuple[Cell, ...]:
    return edit.cells


def edit_source_color(edit: Edit) -> int:
    if edit.source_color is None:
        raise SceneAmbiguityError("edit has no unique source color")
    return int(edit.source_color)


def edit_target_color(edit: Edit) -> int:
    if edit.target_color is None:
        raise SceneAmbiguityError("edit has no unique target color")
    return int(edit.target_color)



def symbol_equal(left: str, right: str) -> bool:
    return str(left) == str(right)


def color_equal(left: int, right: int) -> bool:
    return int(left) == int(right)


def integer_less(left: int, right: int) -> bool:
    return int(left) < int(right)


def integer_greater(left: int, right: int) -> bool:
    return int(left) > int(right)


def integer_subtract(left: int, right: int) -> int:
    return int(left) - int(right)


def integer_minimum(left: int, right: int) -> int:
    return min(int(left), int(right))


def scalar_add(left: float, right: float) -> float:
    return float(left) + float(right)


def scalar_subtract(left: float, right: float) -> float:
    return float(left) - float(right)


def scalar_multiply(left: float, right: float) -> float:
    return float(left) * float(right)


def scalar_absolute(value: float) -> float:
    return abs(float(value))


def cell_row(cell: Cell) -> int:
    return int(cell.row)


def cell_column(cell: Cell) -> int:
    return int(cell.column)


def cell_manhattan(left: Cell, right: Cell) -> float:
    return float(abs(left.row - right.row) + abs(left.column - right.column))


def box_top(box: Box) -> int:
    return int(box.top)


def box_left(box: Box) -> int:
    return int(box.left)


def box_bottom(box: Box) -> int:
    return int(box.bottom)


def box_right(box: Box) -> int:
    return int(box.right)


def box_height(box: Box) -> int:
    return int(box.height)


def box_width(box: Box) -> int:
    return int(box.width)


def box_area(box: Box) -> int:
    return int(box.area)


def box_contains(outer: Box, inner: Box) -> bool:
    return (
        outer.top <= inner.top
        and outer.left <= inner.left
        and outer.bottom >= inner.bottom
        and outer.right >= inner.right
    )


def box_intersects(left: Box, right: Box) -> bool:
    return not (
        left.right < right.left
        or right.right < left.left
        or left.bottom < right.top
        or right.bottom < left.top
    )


def box_cells(box: Box) -> tuple[Cell, ...]:
    return tuple(
        Cell(row, column)
        for row in range(box.top, box.bottom + 1)
        for column in range(box.left, box.right + 1)
    )


def box_border_cells(box: Box) -> tuple[Cell, ...]:
    return tuple(
        Cell(row, column)
        for row in range(box.top, box.bottom + 1)
        for column in range(box.left, box.right + 1)
        if row in {box.top, box.bottom} or column in {box.left, box.right}
    )


def object_id(obj: ArcObject) -> str:
    return obj.object_id


def object_top(obj: ArcObject) -> int:
    return int(obj.box.top)


def object_left(obj: ArcObject) -> int:
    return int(obj.box.left)


def object_bottom(obj: ArcObject) -> int:
    return int(obj.box.bottom)


def object_right(obj: ArcObject) -> int:
    return int(obj.box.right)


def object_center_row(obj: ArcObject) -> float:
    return float(obj.box.center[0])


def object_center_column(obj: ArcObject) -> float:
    return float(obj.box.center[1])


def object_touches_border(obj: ArcObject) -> bool:
    height, width = obj.source_shape
    return any(
        cell.row in {0, height - 1} or cell.column in {0, width - 1}
        for cell in obj.cells
    )


def object_is_horizontal_line(obj: ArcObject) -> bool:
    return obj.height == 1 and obj.area == obj.width


def object_is_vertical_line(obj: ArcObject) -> bool:
    return obj.width == 1 and obj.area == obj.height


def object_is_hollow_rectangle(obj: ArcObject) -> bool:
    if obj.height < 2 or obj.width < 2:
        return False
    return set(obj.normalized_cells) == set(
        Cell(row, column)
        for row in range(obj.height)
        for column in range(obj.width)
        if row in {0, obj.height - 1} or column in {0, obj.width - 1}
    )


def object_box_contains(outer: ArcObject, inner: ArcObject) -> bool:
    return box_contains(outer.box, inner.box)


def object_boxes_intersect(left: ArcObject, right: ArcObject) -> bool:
    return box_intersects(left.box, right.box)


def object_same_row(left: ArcObject, right: ArcObject) -> bool:
    return left.box.center[0] == right.box.center[0]


def object_same_column(left: ArcObject, right: ArcObject) -> bool:
    return left.box.center[1] == right.box.center[1]


def face_id(face: AmbientFace) -> str:
    return face.face_id


def face_box(face: AmbientFace) -> Box:
    return face.box


def face_touches_border(face: AmbientFace) -> bool:
    return bool(face.touches_border)


def face_height(face: AmbientFace) -> float:
    return float(face.box.height)


def face_width(face: AmbientFace) -> float:
    return float(face.box.width)


def relation_source(relation: Relation) -> str:
    return relation.source


def relation_target(relation: Relation) -> str:
    return relation.target


def relation_is_kind(relation: Relation, kind: str) -> bool:
    return relation.kind == str(kind)


def scene_colors(scene: Scene) -> tuple[int, ...]:
    return tuple(sorted(set(int(value) for row in scene.grid for value in row)))


def foreground_colors(scene: Scene) -> tuple[int, ...]:
    return tuple(sorted(set(obj.color for obj in scene.objects)))


def color_set_count(colors: Sequence[int]) -> int:
    return len(tuple(colors))


def color_set_singleton(color: int) -> tuple[int, ...]:
    return (int(color),)


def color_frequency(grid: object, color: int) -> int:
    return int(np.count_nonzero(_array(grid) == int(color)))


def resolve_color_role(scene: Scene, role: str) -> int:
    role_name = str(role)
    counts = Counter(int(value) for row in scene.grid for value in row)
    nonbackground = {color: count for color, count in counts.items() if color != scene.background}

    def unique_extreme(values: dict[int, int], *, maximum: bool) -> int:
        if not values:
            raise SceneAmbiguityError("color role has no candidates")
        extreme = (max if maximum else min)(values.values())
        winners = sorted(color for color, count in values.items() if count == extreme)
        if len(winners) != 1:
            raise SceneAmbiguityError("color role is tied")
        return winners[0]

    if role_name == "background":
        return int(scene.background)
    if role_name == "most_frequent_color":
        return unique_extreme(dict(counts), maximum=True)
    if role_name == "rarest_color":
        return unique_extreme(dict(counts), maximum=False)
    if role_name == "most_frequent_nonbackground":
        return unique_extreme(nonbackground, maximum=True)
    if role_name == "rarest_nonbackground":
        return unique_extreme(nonbackground, maximum=False)
    if role_name == "unique_nonbackground":
        colors = sorted(nonbackground)
        if len(colors) != 1:
            raise SceneAmbiguityError("nonbackground color is not unique")
        return colors[0]
    if role_name in {"largest_object_color", "smallest_object_color"}:
        if not scene.objects:
            raise SceneAmbiguityError("object color role has no objects")
        areas = [obj.area for obj in scene.objects]
        extreme = max(areas) if role_name.startswith("largest") else min(areas)
        winners = [obj for obj in scene.objects if obj.area == extreme]
        colors = sorted(set(obj.color for obj in winners))
        if len(winners) != 1 or len(colors) != 1:
            raise SceneAmbiguityError("object color role is tied")
        return colors[0]
    raise SceneError(f"unknown color role {role_name!r}")


def mask_complement(mask: object) -> np.ndarray:
    return np.logical_not(np.asarray(mask, dtype=bool))


def mask_symmetric_difference(left: object, right: object) -> np.ndarray:
    a, b = np.asarray(left, dtype=bool), np.asarray(right, dtype=bool)
    if a.shape != b.shape:
        raise SceneError("mask shapes do not match")
    return np.logical_xor(a, b)


def mask_count(mask: object) -> int:
    return int(np.count_nonzero(np.asarray(mask, dtype=bool)))


def mask_equal(left: object, right: object) -> bool:
    a, b = np.asarray(left, dtype=bool), np.asarray(right, dtype=bool)
    return a.shape == b.shape and bool(np.array_equal(a, b))


def mask_rotate_90(mask: object) -> np.ndarray:
    return np.rot90(np.asarray(mask, dtype=bool), 1).copy()


def mask_rotate_180(mask: object) -> np.ndarray:
    return np.rot90(np.asarray(mask, dtype=bool), 2).copy()


def mask_reflect_horizontal(mask: object) -> np.ndarray:
    return np.fliplr(np.asarray(mask, dtype=bool)).copy()


def mask_reflect_vertical(mask: object) -> np.ndarray:
    return np.flipud(np.asarray(mask, dtype=bool)).copy()


def mask_box(mask: object) -> Box:
    a = np.asarray(mask, dtype=bool)
    rows, columns = np.nonzero(a)
    if len(rows) == 0:
        raise SceneAmbiguityError("empty mask has no bounding box")
    return Box(int(rows.min()), int(columns.min()), int(rows.max()), int(columns.max()))


def mask_cells(mask: object) -> tuple[Cell, ...]:
    a = np.asarray(mask, dtype=bool)
    if a.ndim != 2:
        raise SceneError("mask must be two-dimensional")
    return tuple(Cell(int(row), int(column)) for row, column in zip(*np.nonzero(a)))


def cells_mask(scene: Scene, cells: Sequence[Cell]) -> np.ndarray:
    return _mask(scene.shape, cells)


def box_mask(scene: Scene, box: Box) -> np.ndarray:
    if not (0 <= box.top <= box.bottom < scene.shape[0] and 0 <= box.left <= box.right < scene.shape[1]):
        raise SceneError("box lies outside the scene")
    return _mask(scene.shape, box_cells(box))


def box_border_mask(scene: Scene, box: Box) -> np.ndarray:
    if not (0 <= box.top <= box.bottom < scene.shape[0] and 0 <= box.left <= box.right < scene.shape[1]):
        raise SceneError("box lies outside the scene")
    return _mask(scene.shape, box_border_cells(box))


def grid_crop_box(grid: object, box: Box) -> np.ndarray:
    a = _array(grid)
    if not (0 <= box.top <= box.bottom < a.shape[0] and 0 <= box.left <= box.right < a.shape[1]):
        raise SceneError("crop box lies outside the grid")
    return a[box.top : box.bottom + 1, box.left : box.right + 1].copy()


def grid_rotate_90(grid: object) -> np.ndarray:
    return np.rot90(_array(grid), 1).copy()


def grid_rotate_180(grid: object) -> np.ndarray:
    return np.rot90(_array(grid), 2).copy()


def grid_reflect_horizontal(grid: object) -> np.ndarray:
    return np.fliplr(_array(grid)).copy()


def grid_reflect_vertical(grid: object) -> np.ndarray:
    return np.flipud(_array(grid)).copy()


def grid_replace_color(grid: object, source: int, target: int) -> np.ndarray:
    a = _array(grid)
    if not 0 <= int(source) <= 9 or not 0 <= int(target) <= 9:
        raise SceneError("ARC colors must lie in [0, 9]")
    output = a.copy()
    output[a == int(source)] = int(target)
    return output


def fill_object_box(obj: ArcObject) -> ArcObject:
    return obj.with_cells(box_cells(obj.box))


def outline_object_box(obj: ArcObject) -> ArcObject:
    return obj.with_cells(box_border_cells(obj.box))


def rotate_object_180(obj: ArcObject) -> ArcObject:
    return rotate_object_90(rotate_object_90(obj))


def rotate_object_270(obj: ArcObject) -> ArcObject:
    return rotate_object_90(rotate_object_180(obj))


def reflect_object_vertical(obj: ArcObject) -> ArcObject:
    normalized = obj.normalized_cells
    reflected = [Cell(obj.height - 1 - cell.row, cell.column) for cell in normalized]
    return obj.with_cells(reflected)


def direction_between(left: ArcObject, right: ArcObject) -> str:
    delta_row = right.box.center[0] - left.box.center[0]
    delta_column = right.box.center[1] - left.box.center[1]
    if delta_row == 0 and delta_column == 0:
        raise SceneAmbiguityError("objects have the same center")
    vertical = "south" if delta_row > 0 else "north"
    horizontal = "east" if delta_column > 0 else "west"
    if delta_row == 0:
        return horizontal
    if delta_column == 0:
        return vertical
    return f"{vertical}_{horizontal}"


def opposite_direction(direction: str) -> str:
    delta_row, delta_column = _direction(direction)
    inverse = {value: key for key, value in {
        "north": (-1, 0), "south": (1, 0), "west": (0, -1), "east": (0, 1),
        "north_west": (-1, -1), "north_east": (-1, 1),
        "south_west": (1, -1), "south_east": (1, 1),
    }.items()}
    return inverse[(-delta_row, -delta_column)]


def rotate_direction_90(direction: str) -> str:
    delta_row, delta_column = _direction(direction)
    rotated = (delta_column, -delta_row)
    inverse = {value: key for key, value in {
        "north": (-1, 0), "south": (1, 0), "west": (0, -1), "east": (0, 1),
        "north_west": (-1, -1), "north_east": (-1, 1),
        "south_west": (1, -1), "south_east": (1, 1),
    }.items()}
    return inverse[rotated]


def edit_is_kind(edit: Edit, kind: str) -> bool:
    return edit.kind == str(kind)


def edit_box(edit: Edit) -> Box:
    if not edit.cells:
        raise SceneAmbiguityError("edit has no finite cell support")
    return _box(edit.cells)


def edit_source_height(edit: Edit) -> int:
    return int(edit.source_shape[0])


def edit_source_width(edit: Edit) -> int:
    return int(edit.source_shape[1])


def edit_target_height(edit: Edit) -> int:
    return int(edit.target_shape[0])


def edit_target_width(edit: Edit) -> int:
    return int(edit.target_shape[1])


def edit_mask(grid: object, edit: Edit) -> np.ndarray:
    a = _array(grid)
    return _mask((int(a.shape[0]), int(a.shape[1])), edit.cells)

def standard_arc_registry() -> OperatorRegistry:
    op = OperatorDefinition
    definitions = [
        op("grid_height", (ValueType.GRID,), ValueType.INTEGER, grid_height),
        op("grid_width", (ValueType.GRID,), ValueType.INTEGER, grid_width),
        op("integer_add", (ValueType.INTEGER, ValueType.INTEGER), ValueType.INTEGER, integer_add),
        op("integer_multiply", (ValueType.INTEGER, ValueType.INTEGER), ValueType.INTEGER, integer_multiply),
        op("integer_maximum", (ValueType.INTEGER, ValueType.INTEGER), ValueType.INTEGER, integer_maximum),
        op("integer_ceil_sqrt", (ValueType.INTEGER,), ValueType.INTEGER, integer_ceil_sqrt),
        op("derive_edits", (ValueType.GRID, ValueType.GRID), ValueType.EDIT_SET, derive_edits, 8, "derive typed input-output delta packets"),
        op("edit_kind", (ValueType.EDIT,), ValueType.SYMBOL, edit_kind),
        op("edit_size", (ValueType.EDIT,), ValueType.SCALAR, edit_size),
        op("edit_cells", (ValueType.EDIT,), ValueType.CELL_SET, edit_cells),
        op("edit_source_color", (ValueType.EDIT,), ValueType.COLOR, edit_source_color),
        op("edit_target_color", (ValueType.EDIT,), ValueType.COLOR, edit_target_color),
        op("analyze", (ValueType.GRID,), ValueType.SCENE, analyze_grid, 8, "build foreground and ambient packet graphs"),
        op("scene_grid", (ValueType.SCENE,), ValueType.GRID, scene_grid),
        op("foreground_objects", (ValueType.SCENE,), ValueType.OBJECT_SET, foreground_objects),
        op("ambient_faces", (ValueType.SCENE,), ValueType.FACE_SET, ambient_faces),
        op("scene_relations", (ValueType.SCENE,), ValueType.RELATION_SET, scene_relations),
        op("background_color", (ValueType.SCENE,), ValueType.COLOR, background_color),
        op("object_area", (ValueType.OBJECT,), ValueType.SCALAR, object_area),
        op("object_bbox_area", (ValueType.OBJECT,), ValueType.SCALAR, object_bbox_area),
        op("object_height", (ValueType.OBJECT,), ValueType.SCALAR, object_height),
        op("object_width", (ValueType.OBJECT,), ValueType.SCALAR, object_width),
        op("object_density", (ValueType.OBJECT,), ValueType.SCALAR, object_density),
        op("object_color", (ValueType.OBJECT,), ValueType.COLOR, object_color),
        op("object_cells", (ValueType.OBJECT,), ValueType.CELL_SET, object_cells),
        op("object_box", (ValueType.OBJECT,), ValueType.BOX, object_box),
        op("object_is_singleton", (ValueType.OBJECT,), ValueType.BOOL, object_is_singleton),
        op("object_is_square", (ValueType.OBJECT,), ValueType.BOOL, object_is_square),
        op("object_is_solid_rectangle", (ValueType.OBJECT,), ValueType.BOOL, object_is_solid_rectangle),
        op("same_shape", (ValueType.OBJECT, ValueType.OBJECT), ValueType.BOOL, same_shape),
        op("same_color", (ValueType.OBJECT, ValueType.OBJECT), ValueType.BOOL, same_color),
        op("manhattan_distance", (ValueType.OBJECT, ValueType.OBJECT), ValueType.SCALAR, manhattan_distance),
        op("face_area", (ValueType.FACE,), ValueType.SCALAR, face_area),
        op("face_cells", (ValueType.FACE,), ValueType.CELL_SET, face_cells),
        op("face_is_hole", (ValueType.FACE,), ValueType.BOOL, face_is_hole),
        op("relation_kind", (ValueType.RELATION,), ValueType.SYMBOL, relation_kind),
        op("relation_value", (ValueType.RELATION,), ValueType.SCALAR, relation_value),
        op("object_set_singleton", (ValueType.OBJECT,), ValueType.OBJECT_SET, object_set_singleton),
        op("object_to_grid", (ValueType.OBJECT, ValueType.COLOR), ValueType.GRID, object_to_grid),
        op("grid_set_singleton", (ValueType.GRID,), ValueType.GRID_SET, grid_set_singleton),
        op("face_set_singleton", (ValueType.FACE,), ValueType.FACE_SET, face_set_singleton),
        op("cell_set_singleton", (ValueType.CELL,), ValueType.CELL_SET, cell_set_singleton),
        op("object_set_count", (ValueType.OBJECT_SET,), ValueType.INTEGER, object_set_count),
        op("face_set_count", (ValueType.FACE_SET,), ValueType.INTEGER, face_set_count),
        op("cell_set_count", (ValueType.CELL_SET,), ValueType.INTEGER, cell_set_count),
        op("integer_equal", (ValueType.INTEGER, ValueType.INTEGER), ValueType.BOOL, integer_equal),
        op("scalar_equal", (ValueType.SCALAR, ValueType.SCALAR), ValueType.BOOL, scalar_equal),
        op("scalar_less", (ValueType.SCALAR, ValueType.SCALAR), ValueType.BOOL, scalar_less),
        op("scalar_greater", (ValueType.SCALAR, ValueType.SCALAR), ValueType.BOOL, scalar_greater),
        op("bool_not", (ValueType.BOOL,), ValueType.BOOL, bool_not),
        op("bool_and", (ValueType.BOOL, ValueType.BOOL), ValueType.BOOL, bool_and),
        op("bool_or", (ValueType.BOOL, ValueType.BOOL), ValueType.BOOL, bool_or),
        op("object_mask", (ValueType.SCENE, ValueType.OBJECT), ValueType.MASK, object_mask),
        op("face_mask", (ValueType.SCENE, ValueType.FACE), ValueType.MASK, face_mask),
        op("foreground_mask", (ValueType.SCENE,), ValueType.MASK, foreground_mask),
        op("mask_union", (ValueType.MASK, ValueType.MASK), ValueType.MASK, mask_union),
        op("mask_intersection", (ValueType.MASK, ValueType.MASK), ValueType.MASK, mask_intersection),
        op("mask_difference", (ValueType.MASK, ValueType.MASK), ValueType.MASK, mask_difference),
        op("mask_dilate4", (ValueType.MASK,), ValueType.MASK, mask_dilate4),
        op("mask_dilate_within", (ValueType.MASK, ValueType.MASK), ValueType.MASK, mask_dilate_within),
        op("mask_erode4", (ValueType.MASK,), ValueType.MASK, mask_erode4),
        op("translate_object", (ValueType.OBJECT, ValueType.DIRECTION, ValueType.INTEGER), ValueType.OBJECT, translate_object),
        op("recolor_object", (ValueType.OBJECT, ValueType.COLOR), ValueType.OBJECT, recolor_object),
        op("normalize_object", (ValueType.OBJECT,), ValueType.OBJECT, normalize_object),
        op("rotate_object_90", (ValueType.OBJECT,), ValueType.OBJECT, rotate_object_90),
        op("reflect_object_horizontal", (ValueType.OBJECT,), ValueType.OBJECT, reflect_object_horizontal),
        op("canvas_from_grid", (ValueType.GRID,), ValueType.CANVAS, canvas_from_grid),
        op("blank_canvas_like", (ValueType.GRID, ValueType.COLOR), ValueType.CANVAS, blank_canvas_like),
        op("blank_canvas", (ValueType.INTEGER, ValueType.INTEGER, ValueType.COLOR), ValueType.CANVAS, blank_canvas),
        op("canvas_grid", (ValueType.CANVAS,), ValueType.GRID, canvas_grid),
        op("layout_row", (ValueType.OBJECT_SET, ValueType.INTEGER, ValueType.COLOR), ValueType.LAYOUT, layout_row),
        op("layout_column", (ValueType.OBJECT_SET, ValueType.INTEGER, ValueType.COLOR), ValueType.LAYOUT, layout_column),
        op("layout_grid", (ValueType.OBJECT_SET, ValueType.INTEGER, ValueType.INTEGER, ValueType.COLOR), ValueType.LAYOUT, layout_grid),
        op("render_layout", (ValueType.LAYOUT,), ValueType.GRID, render_layout),
        op("symbol_equal", (ValueType.SYMBOL, ValueType.SYMBOL), ValueType.BOOL, symbol_equal),
        op("color_equal", (ValueType.COLOR, ValueType.COLOR), ValueType.BOOL, color_equal),
        op("integer_less", (ValueType.INTEGER, ValueType.INTEGER), ValueType.BOOL, integer_less),
        op("integer_greater", (ValueType.INTEGER, ValueType.INTEGER), ValueType.BOOL, integer_greater),
        op("integer_subtract", (ValueType.INTEGER, ValueType.INTEGER), ValueType.INTEGER, integer_subtract),
        op("integer_minimum", (ValueType.INTEGER, ValueType.INTEGER), ValueType.INTEGER, integer_minimum),
        op("scalar_add", (ValueType.SCALAR, ValueType.SCALAR), ValueType.SCALAR, scalar_add),
        op("scalar_subtract", (ValueType.SCALAR, ValueType.SCALAR), ValueType.SCALAR, scalar_subtract),
        op("scalar_multiply", (ValueType.SCALAR, ValueType.SCALAR), ValueType.SCALAR, scalar_multiply),
        op("scalar_absolute", (ValueType.SCALAR,), ValueType.SCALAR, scalar_absolute),
        op("cell_row", (ValueType.CELL,), ValueType.INTEGER, cell_row),
        op("cell_column", (ValueType.CELL,), ValueType.INTEGER, cell_column),
        op("cell_manhattan", (ValueType.CELL, ValueType.CELL), ValueType.SCALAR, cell_manhattan),
        op("box_top", (ValueType.BOX,), ValueType.INTEGER, box_top),
        op("box_left", (ValueType.BOX,), ValueType.INTEGER, box_left),
        op("box_bottom", (ValueType.BOX,), ValueType.INTEGER, box_bottom),
        op("box_right", (ValueType.BOX,), ValueType.INTEGER, box_right),
        op("box_height", (ValueType.BOX,), ValueType.INTEGER, box_height),
        op("box_width", (ValueType.BOX,), ValueType.INTEGER, box_width),
        op("box_area", (ValueType.BOX,), ValueType.INTEGER, box_area),
        op("box_contains", (ValueType.BOX, ValueType.BOX), ValueType.BOOL, box_contains),
        op("box_intersects", (ValueType.BOX, ValueType.BOX), ValueType.BOOL, box_intersects),
        op("box_cells", (ValueType.BOX,), ValueType.CELL_SET, box_cells),
        op("box_border_cells", (ValueType.BOX,), ValueType.CELL_SET, box_border_cells),
        op("object_id", (ValueType.OBJECT,), ValueType.SYMBOL, object_id),
        op("object_top", (ValueType.OBJECT,), ValueType.INTEGER, object_top),
        op("object_left", (ValueType.OBJECT,), ValueType.INTEGER, object_left),
        op("object_bottom", (ValueType.OBJECT,), ValueType.INTEGER, object_bottom),
        op("object_right", (ValueType.OBJECT,), ValueType.INTEGER, object_right),
        op("object_center_row", (ValueType.OBJECT,), ValueType.SCALAR, object_center_row),
        op("object_center_column", (ValueType.OBJECT,), ValueType.SCALAR, object_center_column),
        op("object_touches_border", (ValueType.OBJECT,), ValueType.BOOL, object_touches_border),
        op("object_is_horizontal_line", (ValueType.OBJECT,), ValueType.BOOL, object_is_horizontal_line),
        op("object_is_vertical_line", (ValueType.OBJECT,), ValueType.BOOL, object_is_vertical_line),
        op("object_is_hollow_rectangle", (ValueType.OBJECT,), ValueType.BOOL, object_is_hollow_rectangle),
        op("object_box_contains", (ValueType.OBJECT, ValueType.OBJECT), ValueType.BOOL, object_box_contains),
        op("object_boxes_intersect", (ValueType.OBJECT, ValueType.OBJECT), ValueType.BOOL, object_boxes_intersect),
        op("object_same_row", (ValueType.OBJECT, ValueType.OBJECT), ValueType.BOOL, object_same_row),
        op("object_same_column", (ValueType.OBJECT, ValueType.OBJECT), ValueType.BOOL, object_same_column),
        op("face_id", (ValueType.FACE,), ValueType.SYMBOL, face_id),
        op("face_box", (ValueType.FACE,), ValueType.BOX, face_box),
        op("face_touches_border", (ValueType.FACE,), ValueType.BOOL, face_touches_border),
        op("face_height", (ValueType.FACE,), ValueType.SCALAR, face_height),
        op("face_width", (ValueType.FACE,), ValueType.SCALAR, face_width),
        op("relation_source", (ValueType.RELATION,), ValueType.SYMBOL, relation_source),
        op("relation_target", (ValueType.RELATION,), ValueType.SYMBOL, relation_target),
        op("relation_is_kind", (ValueType.RELATION, ValueType.SYMBOL), ValueType.BOOL, relation_is_kind),
        op("scene_colors", (ValueType.SCENE,), ValueType.COLOR_SET, scene_colors),
        op("foreground_colors", (ValueType.SCENE,), ValueType.COLOR_SET, foreground_colors),
        op("color_set_count", (ValueType.COLOR_SET,), ValueType.INTEGER, color_set_count),
        op("color_set_singleton", (ValueType.COLOR,), ValueType.COLOR_SET, color_set_singleton),
        op("color_frequency", (ValueType.GRID, ValueType.COLOR), ValueType.INTEGER, color_frequency),
        op("resolve_color_role", (ValueType.SCENE, ValueType.COLOR_ROLE), ValueType.COLOR, resolve_color_role, 2, "resolve a role without embedding a literal palette identity"),
        op("mask_complement", (ValueType.MASK,), ValueType.MASK, mask_complement),
        op("mask_symmetric_difference", (ValueType.MASK, ValueType.MASK), ValueType.MASK, mask_symmetric_difference),
        op("mask_count", (ValueType.MASK,), ValueType.INTEGER, mask_count),
        op("mask_equal", (ValueType.MASK, ValueType.MASK), ValueType.BOOL, mask_equal),
        op("mask_rotate_90", (ValueType.MASK,), ValueType.MASK, mask_rotate_90),
        op("mask_rotate_180", (ValueType.MASK,), ValueType.MASK, mask_rotate_180),
        op("mask_reflect_horizontal", (ValueType.MASK,), ValueType.MASK, mask_reflect_horizontal),
        op("mask_reflect_vertical", (ValueType.MASK,), ValueType.MASK, mask_reflect_vertical),
        op("mask_box", (ValueType.MASK,), ValueType.BOX, mask_box),
        op("mask_cells", (ValueType.MASK,), ValueType.CELL_SET, mask_cells),
        op("cells_mask", (ValueType.SCENE, ValueType.CELL_SET), ValueType.MASK, cells_mask),
        op("box_mask", (ValueType.SCENE, ValueType.BOX), ValueType.MASK, box_mask),
        op("box_border_mask", (ValueType.SCENE, ValueType.BOX), ValueType.MASK, box_border_mask),
        op("grid_crop_box", (ValueType.GRID, ValueType.BOX), ValueType.GRID, grid_crop_box),
        op("grid_rotate_90", (ValueType.GRID,), ValueType.GRID, grid_rotate_90),
        op("grid_rotate_180", (ValueType.GRID,), ValueType.GRID, grid_rotate_180),
        op("grid_reflect_horizontal", (ValueType.GRID,), ValueType.GRID, grid_reflect_horizontal),
        op("grid_reflect_vertical", (ValueType.GRID,), ValueType.GRID, grid_reflect_vertical),
        op("grid_replace_color", (ValueType.GRID, ValueType.COLOR, ValueType.COLOR), ValueType.GRID, grid_replace_color),
        op("fill_object_box", (ValueType.OBJECT,), ValueType.OBJECT, fill_object_box),
        op("outline_object_box", (ValueType.OBJECT,), ValueType.OBJECT, outline_object_box),
        op("rotate_object_180", (ValueType.OBJECT,), ValueType.OBJECT, rotate_object_180),
        op("rotate_object_270", (ValueType.OBJECT,), ValueType.OBJECT, rotate_object_270),
        op("reflect_object_vertical", (ValueType.OBJECT,), ValueType.OBJECT, reflect_object_vertical),
        op("direction_between", (ValueType.OBJECT, ValueType.OBJECT), ValueType.DIRECTION, direction_between),
        op("opposite_direction", (ValueType.DIRECTION,), ValueType.DIRECTION, opposite_direction),
        op("rotate_direction_90", (ValueType.DIRECTION,), ValueType.DIRECTION, rotate_direction_90),
        op("edit_is_kind", (ValueType.EDIT, ValueType.SYMBOL), ValueType.BOOL, edit_is_kind),
        op("edit_box", (ValueType.EDIT,), ValueType.BOX, edit_box),
        op("edit_source_height", (ValueType.EDIT,), ValueType.INTEGER, edit_source_height),
        op("edit_source_width", (ValueType.EDIT,), ValueType.INTEGER, edit_source_width),
        op("edit_target_height", (ValueType.EDIT,), ValueType.INTEGER, edit_target_height),
        op("edit_target_width", (ValueType.EDIT,), ValueType.INTEGER, edit_target_width),
        op("edit_mask", (ValueType.GRID, ValueType.EDIT), ValueType.MASK, edit_mask),
    ]
    return OperatorRegistry(definitions)


class ArcRuntimeAdapter(DefaultRuntimeAdapter):
    """Concrete renderer, packer, and exact-value comparator for ARC packets."""

    def collection(self, value: object) -> tuple[object, ...]:
        if isinstance(value, tuple):
            return value
        if isinstance(value, list):
            return tuple(value)
        return super().collection(value)

    def equal(self, left: object, right: object) -> bool:
        if isinstance(left, (np.ndarray, list, tuple)) or isinstance(right, (np.ndarray, list, tuple)):
            try:
                a, b = np.asarray(left), np.asarray(right)
                if a.dtype != object and b.dtype != object:
                    return bool(np.array_equal(a, b))
            except Exception:
                pass
        return left == right

    def _cells_and_colors(self, items: object, color: object | None, canvas: Canvas) -> list[tuple[Cell, int]]:
        if isinstance(items, (ArcObject, AmbientFace, Cell, np.ndarray)):
            values = (items,)
        elif isinstance(items, (tuple, list)):
            values = tuple(items)
        else:
            raise TypeError(f"unsupported render payload {type(items)!r}")
        output: list[tuple[Cell, int]] = []
        for item in values:
            if isinstance(item, ArcObject):
                item_color = item.color if color is None else int(color)
                output.extend((cell, item_color) for cell in item.cells)
            elif isinstance(item, AmbientFace):
                if color is None:
                    raise SceneError("rendering an ambient face requires an explicit color")
                output.extend((cell, int(color)) for cell in item.cells)
            elif isinstance(item, Cell):
                if color is None:
                    raise SceneError("rendering cells requires an explicit color")
                output.append((item, int(color)))
            elif isinstance(item, np.ndarray):
                if item.ndim != 2:
                    raise SceneError("render masks must be two-dimensional")
                if item.shape != canvas.shape:
                    raise SceneError("render mask and canvas shapes do not match")
                if color is None:
                    raise SceneError("rendering a mask requires an explicit color")
                output.extend((Cell(int(row), int(column)), int(color)) for row, column in zip(*np.nonzero(item)))
            else:
                raise TypeError(f"unsupported render item {type(item)!r}")
        return output

    def render(self, canvas: object, items: object, color: object | None, mode: str) -> np.ndarray:
        if not isinstance(canvas, Canvas):
            raise TypeError("ARC rendering requires a Canvas")
        output = np.asarray(canvas.grid, dtype=np.int16).copy()
        writes: dict[tuple[int, int], int] = {}
        for cell, item_color in self._cells_and_colors(items, color, canvas):
            if not (0 <= cell.row < output.shape[0] and 0 <= cell.column < output.shape[1]):
                raise SceneError("render requested an out-of-bounds write")
            write_color = canvas.background if mode == "erase" else item_color
            if mode == "preserve" and int(output[cell.row, cell.column]) != canvas.background:
                continue
            address = (cell.row, cell.column)
            if address in writes and writes[address] != write_color:
                raise SceneAmbiguityError("render payload requests conflicting colors")
            writes[address] = write_color
        for (row, column), write_color in writes.items():
            output[row, column] = write_color
        return output

    def pack(self, items: object, background: object, axis: str, gap: int, normalize: bool) -> np.ndarray:
        values = self.collection(items)
        arrays: list[np.ndarray] = []
        for item in values:
            if isinstance(item, ArcObject):
                arrays.append(_object_grid(item, int(background), normalize=normalize))
            else:
                arrays.append(_array(item))
        return _pack_arrays(arrays, int(background), axis, int(gap))

    def tile(self, tile: object, rows: int, columns: int) -> np.ndarray:
        a = _array(tile)
        return np.tile(a, (int(rows), int(columns))).astype(np.int16, copy=False)

    def validate_result(self, value: object, limits: ExecutionLimits) -> object:
        if isinstance(value, np.ndarray):
            if value.ndim == 2 and value.size > limits.maximum_grid_cells:
                raise ExecutionLimitError("grid or mask cell budget exceeded")
        return value


__all__ = [
    "AmbientFace", "ArcObject", "ArcRuntimeAdapter", "Box", "Canvas", "Cell", "Edit",
    "Grid", "Layout", "Relation", "Scene", "SceneAmbiguityError", "SceneError",
    "analyze_grid", "freeze_grid", "infer_background", "standard_arc_registry",
]
