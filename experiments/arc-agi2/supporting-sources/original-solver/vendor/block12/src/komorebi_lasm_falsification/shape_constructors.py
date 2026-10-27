"""Production-safe relational constructor grammar for PR-LASM Block 12.

The compiler consumes ARC training input/output demonstrations and test inputs.
It has no solution-file API.  Every program is immutable, task-ID-free, and
executable from its typed parameter record.  Programs that replay all training
demonstrations are quotiented by their complete tuple of test rasters.

This remains an exploratory public-training experiment.  It does not claim
prospective, evaluation, or hidden-test performance.

Author: Komorebi P.
"""
from __future__ import annotations

from collections import Counter, deque
from dataclasses import dataclass
from functools import lru_cache
import hashlib
import json
import math
from typing import Any, Iterable, Iterator, Mapping, Sequence

from komorebi_lasm_composition.task import sanitized_task_mapping


Grid = tuple[tuple[int, ...], ...]
D4 = ("id", "fliplr", "flipud", "r180", "transpose", "r90", "r270", "anti_transpose")
SCHEMA_VERSION = 1
PROGRAM_SCHEMA = "komorebi.lasm.block12.relational_shape_program"
COMPILATION_SCHEMA = "komorebi.lasm.block12.relational_shape_compilation"
SAMPLE_SALT = "block12:shape_constructors:"
FORBIDDEN_PROGRAM_FIELDS = frozenset(
    {"task_id", "target", "targets", "output", "outputs", "prediction", "predictions", "answer", "label"}
)

STABLE_FAMILIES = frozenset({
    "dynamic_palette_layout",
    "frame_object_overlay",
    "hollow_object_pack",
})
PROVISIONAL_FAMILIES = frozenset({
    "bridged_diagonal_duplication",
    "component_count_histogram",
    "component_rank_serialization",
    "counted_copy_square",
    "diagonal_stamp_closure",
    "edge_profile_expansion",
    "foreground_cardinality_serialization",
    "keyed_payload_tiling",
    "mirror_complement_layout",
    "singleton_boustrophedon_pack",
    "support_complement_tile",
})
SAFE_FAMILIES = STABLE_FAMILIES | PROVISIONAL_FAMILIES
REJECTED_EXPERIMENTAL_FAMILIES = frozenset({"pairwise_panel_algebra"})
PALETTE_ZERO_SENSITIVE_FAMILIES = frozenset({
    "counted_copy_square",
    "dynamic_palette_layout",
    "foreground_cardinality_serialization",
    "mirror_complement_layout",
})
LITERAL_ZERO_FAMILIES = PALETTE_ZERO_SENSITIVE_FAMILIES
D4_PARTIAL_FAMILIES = frozenset({
    "bridged_diagonal_duplication",
    "counted_copy_square",
    "singleton_boustrophedon_pack",
})
D4_COMPLETE_FAMILIES = SAFE_FAMILIES - D4_PARTIAL_FAMILIES
MAXIMUM_PROGRAMS = 8192


class ContractError(ValueError):
    """Raised when a shape-constructor program violates the frozen contract."""

_PARAMETER_DOMAINS: Mapping[str, Mapping[str, frozenset[Any]]] = {
    "dynamic_palette_layout": {
        "transform": frozenset(D4),
        "count_role": frozenset({"palette_nonzero", "palette_all", "nonzero_cells", "zero_cells", "foreground_cells", "background_cells"}),
        "background_role": frozenset({"zero", "mode"}),
        "layout": frozenset({"pixel", "tile"}),
    },
    "edge_profile_expansion": {"transform": frozenset(D4)},
    "diagonal_stamp_closure": {
        "transform": frozenset(D4), "background_role": frozenset({"zero", "mode"}),
        "vertical_direction": frozenset({"forward", "reverse"}),
        "horizontal_direction": frozenset({"forward", "reverse"}),
    },
    "counted_copy_square": {
        "transform": frozenset(D4), "background_role": frozenset({"zero", "mode"}),
        "side_role": frozenset({"zero_cells", "background_cells", "nonzero_cells", "foreground_cells"}),
        "copy_role": frozenset({"zero_cells", "background_cells", "nonzero_cells", "foreground_cells"}),
        "traversal": frozenset({"row_major", "boustrophedon"}),
    },
    "mirror_complement_layout": {
        "background_role": frozenset({"zero", "mode"}), "axis": frozenset({"horizontal", "vertical"}),
        "target_color": frozenset(range(10)), "seam_rule": frozenset({"toward", "away"}),
    },
    "foreground_cardinality_serialization": {
        "background_role": frozenset({"zero"}), "axis": frozenset({"horizontal", "vertical"}),
    },
    "bridged_diagonal_duplication": {
        "background_role": frozenset({"zero", "mode"}), "axis": frozenset({"rows", "columns"}),
        "bridge_color": frozenset(range(10)),
    },
    "keyed_payload_tiling": {
        "background_role": frozenset({"zero", "mode"}),
        "vertical_align": frozenset({"top", "center", "bottom"}),
        "horizontal_align": frozenset({"left", "center", "right"}),
        "axis": frozenset({"horizontal", "vertical"}), "transform": frozenset(D4),
    },
    "component_rank_serialization": {
        "background_role": frozenset({"zero", "mode"}), "connectivity": frozenset({4, 8}),
        "metric": frozenset({"area", "bbox"}), "order": frozenset({"ascending", "descending"}),
        "axis": frozenset({"horizontal", "vertical"}),
    },
    "singleton_boustrophedon_pack": {
        "background_role": frozenset({"zero", "mode"}), "sort_axis": frozenset({"columns", "rows"}),
        "tie_direction": frozenset({"ascending", "descending"}), "snake": frozenset({False, True}),
    },
    "component_count_histogram": {
        "background_role": frozenset({"zero", "mode"}), "connectivity": frozenset({4, 8}),
        "align": frozenset({"left", "right"}), "order": frozenset({"ascending", "descending"}),
        "orientation": frozenset({"rows", "columns"}),
    },
    "hollow_object_pack": {
        "background_role": frozenset({"zero", "mode"}), "connectivity": frozenset({4, 8}),
        "axis": frozenset({"dominant", "horizontal", "vertical"}),
    },
    "support_complement_tile": {
        "background_role": frozenset({"zero", "mode"}),
        "layout": frozenset({"square_2", "horizontal_2", "vertical_2"}),
    },
    "frame_object_overlay": {
        "background_role": frozenset({"zero", "mode"}), "connectivity": frozenset({4, 8}),
    },
}


def canonical_json(value: Any) -> str:
    return json.dumps(
        value, sort_keys=True, separators=(",", ":"), ensure_ascii=True,
        allow_nan=False,
    )


def digest(value: Any) -> str:
    return hashlib.sha256(canonical_json(value).encode("ascii")).hexdigest()


def grid(value: Any) -> Grid:
    if not isinstance(value, Sequence) or isinstance(value, (str, bytes, bytearray)):
        raise TypeError("grid must be a row sequence")
    rows = []
    for row in value:
        if not isinstance(row, Sequence) or isinstance(row, (str, bytes, bytearray)):
            raise TypeError("grid row must be a sequence")
        cells = []
        for cell in row:
            if isinstance(cell, bool) or not isinstance(cell, int) or not 0 <= cell <= 9:
                raise ValueError("ARC cells must be integer colors in [0, 9]")
            cells.append(int(cell))
        rows.append(tuple(cells))
    result = tuple(rows)
    if not result or not result[0] or any(len(row) != len(result[0]) for row in result):
        raise ValueError("grid must be nonempty and rectangular")
    if len(result) > 30 or len(result[0]) > 30:
        raise ValueError("grid exceeds ARC's 30x30 limit")
    return result


def shape(value: Grid) -> tuple[int, int]:
    return len(value), len(value[0])


def _mode(values: Iterable[int]) -> int:
    counts = Counter(values)
    if not counts:
        raise ValueError("empty color collection")
    return min(counts, key=lambda value: (-counts[value], value))


def _background(source: Grid, role: str) -> int:
    if role == "zero":
        return 0
    if role == "mode":
        return _mode(cell for row in source for cell in row)
    if role == "corner":
        return _mode((source[0][0], source[0][-1], source[-1][0], source[-1][-1]))
    raise ValueError("unknown background role")


def _transform(source: Grid, name: str) -> Grid:
    if name == "id":
        return source
    if name == "fliplr":
        return tuple(tuple(reversed(row)) for row in source)
    if name == "flipud":
        return tuple(reversed(source))
    if name == "r180":
        return _transform(_transform(source, "fliplr"), "flipud")
    transposed = tuple(tuple(source[y][x] for y in range(len(source))) for x in range(len(source[0])))
    if name == "transpose":
        return transposed
    if name == "r90":
        return tuple(tuple(reversed(row)) for row in transposed)
    if name == "r270":
        return tuple(reversed(transposed))
    if name == "anti_transpose":
        return _transform(transposed, "r180")
    raise ValueError("unknown D4 transform")


def _count(source: Grid, role: str, background_role: str = "zero") -> int:
    flat = tuple(cell for row in source for cell in row)
    background = _background(source, background_role)
    if role == "palette_nonzero":
        return len(set(flat) - {0})
    if role == "palette_all":
        return len(set(flat))
    if role == "nonzero_cells":
        return sum(cell != 0 for cell in flat)
    if role == "zero_cells":
        return sum(cell == 0 for cell in flat)
    if role == "foreground_cells":
        return sum(cell != background for cell in flat)
    if role == "background_cells":
        return sum(cell == background for cell in flat)
    raise ValueError("unknown count role")


def _repeat_pixels(source: Grid, factor: int) -> Grid:
    if factor < 1:
        raise ValueError("factor must be positive")
    height, width = shape(source)
    if height * factor > 30 or width * factor > 30:
        raise ValueError("replication exceeds ARC's finite canvas")
    return tuple(
        tuple(cell for cell in row for _ in range(factor))
        for row in source
        for _ in range(factor)
    )


def _tile(source: Grid, rows: int, columns: int) -> Grid:
    height, width = shape(source)
    if rows < 1 or columns < 1 or height * rows > 30 or width * columns > 30:
        raise ValueError("tiling exceeds ARC's finite canvas")
    return tuple(tuple(cell for _ in range(columns) for cell in row) for _ in range(rows) for row in source)


@dataclass(frozen=True, slots=True)
class ObjectPacket:
    cells: tuple[tuple[int, int], ...]
    bbox: tuple[int, int, int, int]
    crop: Grid
    area: int
    color: int


def _objects(source: Grid, background: int, connectivity: int, *, same_color: bool = False) -> tuple[ObjectPacket, ...]:
    height, width = shape(source)
    unseen = {(y, x) for y in range(height) for x in range(width) if source[y][x] != background}
    offsets = [(-1, 0), (0, -1), (0, 1), (1, 0)]
    if connectivity == 8:
        offsets += [(-1, -1), (-1, 1), (1, -1), (1, 1)]
    result = []
    while unseen:
        seed = min(unseen)
        unseen.remove(seed)
        queue = deque((seed,))
        cells = {seed}
        seed_color = source[seed[0]][seed[1]]
        while queue:
            y, x = queue.popleft()
            for dy, dx in offsets:
                neighbor = (y + dy, x + dx)
                if neighbor in unseen and (not same_color or source[neighbor[0]][neighbor[1]] == seed_color):
                    unseen.remove(neighbor)
                    cells.add(neighbor)
                    queue.append(neighbor)
        ys = [item[0] for item in cells]
        xs = [item[1] for item in cells]
        y0, y1, x0, x1 = min(ys), max(ys) + 1, min(xs), max(xs) + 1
        crop = tuple(tuple(source[y][x] for x in range(x0, x1)) for y in range(y0, y1))
        colors = Counter(source[y][x] for y, x in cells)
        color = min(colors, key=lambda value: (-colors[value], value))
        result.append(ObjectPacket(tuple(sorted(cells)), (y0, y1, x0, x1), crop, len(cells), color))
    return tuple(result)


def _crop_color(source: Grid, color: int, background: int) -> Grid:
    cells = [(y, x) for y, row in enumerate(source) for x, cell in enumerate(row) if cell == color]
    if not cells:
        raise ValueError("selected color is absent")
    ys, xs = [v[0] for v in cells], [v[1] for v in cells]
    y0, y1, x0, x1 = min(ys), max(ys) + 1, min(xs), max(xs) + 1
    return tuple(
        tuple(source[y][x] if source[y][x] == color else background for x in range(x0, x1))
        for y in range(y0, y1)
    )


def _pad_square(source: Grid, fill: int, vertical: str, horizontal: str) -> Grid:
    height, width = shape(source)
    side = max(height, width)
    if vertical == "top":
        top = 0
    elif vertical == "bottom":
        top = side - height
    elif vertical == "center":
        top = (side - height) // 2
    else:
        raise ValueError("invalid vertical alignment")
    if horizontal == "left":
        left = 0
    elif horizontal == "right":
        left = side - width
    elif horizontal == "center":
        left = (side - width) // 2
    else:
        raise ValueError("invalid horizontal alignment")
    output = [[fill for _ in range(side)] for _ in range(side)]
    for y, row in enumerate(source):
        for x, cell in enumerate(row):
            output[top + y][left + x] = cell
    return grid(output)


def _component_histogram(source: Grid, background: int, connectivity: int, align: str, order: str) -> Grid:
    packets = _objects(source, background, connectivity, same_color=True)
    counts = Counter(packet.color for packet in packets)
    if not counts:
        raise ValueError("no components")
    colors = sorted(counts, key=lambda color: ((-counts[color] if order == "descending" else counts[color]), color))
    width = max(counts.values())
    rows = []
    for color in colors:
        padding = [background] * (width - counts[color])
        run = [color] * counts[color]
        rows.append(tuple(padding + run if align == "right" else run + padding))
    return tuple(rows)


@dataclass(frozen=True, slots=True)
class Program:
    family: str
    parameters_json: str

    def __post_init__(self) -> None:
        if self.family not in SAFE_FAMILIES:
            raise ContractError(f"unapproved shape-constructor family {self.family!r}")
        if not isinstance(self.parameters_json, str):
            raise TypeError("parameters_json must be text")
        parameters = self.parameters
        domains = _PARAMETER_DOMAINS[self.family]
        if set(parameters) != set(domains):
            raise ContractError("parameter keys do not match the frozen family contract")
        for name, domain in domains.items():
            value = parameters[name]
            exemplar = next(iter(domain))
            if isinstance(exemplar, bool):
                typed = isinstance(value, bool)
            elif isinstance(exemplar, int):
                typed = isinstance(value, int) and not isinstance(value, bool)
            else:
                typed = isinstance(value, str)
            if not typed:
                raise ContractError(f"parameter {name!r} has the wrong type")
            if value not in domain:
                raise ContractError(f"parameter {name!r} is outside its frozen typed domain")
        if self.parameters_json != canonical_json(parameters):
            raise ContractError("parameters_json must be canonical")

    @property
    def parameters(self) -> Mapping[str, Any]:
        value = json.loads(self.parameters_json)
        if not isinstance(value, Mapping) or FORBIDDEN_PROGRAM_FIELDS & set(value):
            raise ValueError("invalid target-bearing parameter record")
        return value

    @property
    def parameter_map(self) -> dict[str, Any]:
        return dict(self.parameters)

    @classmethod
    def create(cls, family: str, **parameters: Any) -> "Program":
        return cls(family, canonical_json(parameters))

    @property
    def program_id(self) -> str:
        return digest(self.identity_record())

    @property
    def provisional(self) -> bool:
        return self.family in PROVISIONAL_FAMILIES

    @property
    def literal_zero(self) -> bool:
        parameters = self.parameters
        if self.family == "foreground_cardinality_serialization":
            return True
        if parameters.get("background_role") == "zero":
            return True
        return any(
            parameters.get(name) in {
                "palette_nonzero", "nonzero_cells", "zero_cells",
            }
            for name in ("count_role", "side_role", "copy_role")
        )

    @property
    def cost(self) -> int:
        # Prefer role-bound equivalents as behavior representatives. Literal
        # zero programs remain visible when no equivalent role-safe program
        # exists, and their families are explicitly declared when inherent.
        return 1 + len(self.parameters) + (100 if self.literal_zero else 0)

    def identity_record(self) -> dict[str, Any]:
        return {"schema": PROGRAM_SCHEMA, "schema_version": SCHEMA_VERSION, "family": self.family, "parameters": self.parameters}

    def to_record(self) -> dict[str, Any]:
        body = self.identity_record()
        body["program_id"] = self.program_id
        body["provisional"] = self.provisional
        body["literal_zero"] = self.literal_zero
        body["cost"] = self.cost
        return body

    def execute(self, value: Any) -> Grid:
        return self._execute_grid(grid(value))

    @lru_cache(maxsize=16384)
    def _execute_grid(self, source: Grid) -> Grid:
        p = self.parameters
        family = self.family
        if family == "dynamic_palette_layout":
            base = _transform(source, str(p["transform"]))
            factor = _count(source, str(p["count_role"]), str(p["background_role"]))
            result = _repeat_pixels(base, factor) if p["layout"] == "pixel" else _tile(base, factor, factor)
        elif family == "edge_profile_expansion":
            base = _transform(source, str(p["transform"]))
            row_profile = [2 if index in (0, len(base) - 1) else 1 for index in range(len(base))]
            col_profile = [2 if index in (0, len(base[0]) - 1) else 1 for index in range(len(base[0]))]
            result = tuple(
                tuple(base[y][x] for x, count in enumerate(col_profile) for _ in range(count))
                for y, count in enumerate(row_profile) for _ in range(count)
            )
        elif family == "diagonal_stamp_closure":
            base = _transform(source, str(p["transform"]))
            background = _background(base, str(p["background_role"]))
            height, width = shape(base)
            output = [[background for _ in range(2 * width)] for _ in range(2 * height)]
            for offset in range(max(2 * height, 2 * width)):
                oy = offset if p["vertical_direction"] == "forward" else 2 * height - height - offset
                ox = offset if p["horizontal_direction"] == "forward" else 2 * width - width - offset
                for y, row in enumerate(base):
                    for x, cell in enumerate(row):
                        yy, xx = oy + y, ox + x
                        if cell != background and 0 <= yy < 2 * height and 0 <= xx < 2 * width:
                            output[yy][xx] = cell
            result = grid(output)
        elif family == "counted_copy_square":
            base = _transform(source, str(p["transform"]))
            background = _background(source, str(p["background_role"]))
            side = _count(source, str(p["side_role"]), str(p["background_role"]))
            copies = _count(source, str(p["copy_role"]), str(p["background_role"]))
            height, width = shape(base)
            if side < 1 or copies > side * side or side * height > 30 or side * width > 30:
                raise ValueError("counted layout exceeds its finite canvas")
            output = [[background for _ in range(side * width)] for _ in range(side * height)]
            slots = [(y, x) for y in range(side) for x in range(side)]
            if p["traversal"] == "boustrophedon":
                slots = [(y, x if y % 2 == 0 else side - 1 - x) for y in range(side) for x in range(side)]
            for row_slot, col_slot in slots[:copies]:
                for y, row in enumerate(base):
                    for x, cell in enumerate(row):
                        output[row_slot * height + y][col_slot * width + x] = cell
            result = grid(output)
        elif family == "mirror_complement_layout":
            background = _background(source, str(p["background_role"]))
            target = int(p["target_color"])
            height, width = shape(source)
            active = [(y, x) for y, row in enumerate(source) for x, cell in enumerate(row) if cell != background]
            if not active:
                raise ValueError("empty foreground")
            complement = tuple(tuple(target if cell == background else background for cell in row) for row in source)
            if p["axis"] == "horizontal":
                companion = _transform(complement, "fliplr")
                centroid = sum(x for _, x in active) / len(active)
                source_first = centroid > (width - 1) / 2
                if p["seam_rule"] == "away":
                    source_first = not source_first
                result = tuple((source[y] + companion[y]) if source_first else (companion[y] + source[y]) for y in range(height))
            else:
                companion = _transform(complement, "flipud")
                centroid = sum(y for y, _ in active) / len(active)
                source_first = centroid > (height - 1) / 2
                if p["seam_rule"] == "away":
                    source_first = not source_first
                result = source + companion if source_first else companion + source
        elif family == "foreground_cardinality_serialization":
            background = _background(source, str(p["background_role"]))
            colors = Counter(cell for row in source for cell in row if cell != background)
            if len(colors) != 1:
                raise ValueError("serialization requires one foreground color")
            color, count = next(iter(colors.items()))
            result = (tuple(color for _ in range(count)),) if p["axis"] == "horizontal" else tuple((color,) for _ in range(count))
        elif family == "bridged_diagonal_duplication":
            background = _background(source, str(p["background_role"]))
            bridge = int(p["bridge_color"])
            height, width = shape(source)
            output = [[background for _ in range(2 * width)] for _ in range(2 * height)]
            for oy, ox in ((0, 0), (height, width)):
                for y, row in enumerate(source):
                    output[oy + y][ox:ox + width] = row
            if p["axis"] == "rows":
                for y in range(1, height - 1):
                    if all(cell == background for cell in source[y]) and source[y - 1] == source[y + 1] and any(cell != background for cell in source[y - 1]):
                        output[y] = [bridge] * (2 * width)
                        output[height + y] = [bridge] * (2 * width)
            else:
                for x in range(1, width - 1):
                    column = tuple(source[y][x] for y in range(height))
                    before = tuple(source[y][x - 1] for y in range(height))
                    after = tuple(source[y][x + 1] for y in range(height))
                    if all(cell == background for cell in column) and before == after and any(cell != background for cell in before):
                        for y in range(2 * height):
                            output[y][x] = bridge
                            output[y][width + x] = bridge
            result = grid(output)
        elif family == "keyed_payload_tiling":
            background = _background(source, str(p["background_role"]))
            counts = Counter(cell for row in source for cell in row if cell != background)
            if len(counts) != 2:
                raise ValueError("keyed payload requires exactly two foreground colors")
            ordered = sorted(counts, key=lambda color: (-counts[color], color))
            payload, key = ordered[0], ordered[1]
            packet = _crop_color(source, payload, background)
            packet = _pad_square(packet, background, str(p["vertical_align"]), str(p["horizontal_align"]))
            packet = _transform(packet, str(p["transform"]))
            copies = counts[key]
            result = _tile(packet, 1, copies) if p["axis"] == "horizontal" else _tile(packet, copies, 1)
        elif family == "component_rank_serialization":
            background = _background(source, str(p["background_role"]))
            packets = list(_objects(source, background, int(p["connectivity"]), same_color=True))
            if not packets:
                raise ValueError("no objects")
            metric = (lambda item: item.area) if p["metric"] == "area" else (lambda item: (item.bbox[1] - item.bbox[0]) * (item.bbox[3] - item.bbox[2]))
            packets.sort(key=lambda item: ((-metric(item) if p["order"] == "descending" else metric(item)), item.bbox, item.color))
            values = tuple(packet.color for packet in packets)
            result = (values,) if p["axis"] == "horizontal" else tuple((value,) for value in values)
        elif family == "singleton_boustrophedon_pack":
            background = _background(source, str(p["background_role"]))
            points = [(y, x, cell) for y, row in enumerate(source) for x, cell in enumerate(row) if cell != background]
            if not points:
                raise ValueError("no payload cells")
            if p["sort_axis"] == "columns":
                points.sort(key=lambda item: (item[1], item[0] if p["tie_direction"] == "ascending" else -item[0], item[2]))
            else:
                points.sort(key=lambda item: (item[0], item[1] if p["tie_direction"] == "ascending" else -item[1], item[2]))
            side = math.ceil(math.sqrt(len(points)))
            values = [item[2] for item in points]
            rows = []
            for row_index in range(side):
                row = values[row_index * side:(row_index + 1) * side]
                row += [background] * (side - len(row))
                if p["snake"] and row_index % 2:
                    row.reverse()
                rows.append(tuple(row))
            result = tuple(rows)
        elif family == "component_count_histogram":
            background = _background(source, str(p["background_role"]))
            result = _component_histogram(source, background, int(p["connectivity"]), str(p["align"]), str(p["order"]))
            if p["orientation"] == "columns":
                result = _transform(result, "transpose")
        elif family == "hollow_object_pack":
            background = _background(source, str(p["background_role"]))
            packets = [packet for packet in _objects(source, background, int(p["connectivity"])) if any(cell == background for row in packet.crop for cell in row)]
            if len(packets) < 2 or len({shape(packet.crop) for packet in packets}) != 1:
                raise ValueError("hollow packets must share a shape")
            y_range = max(packet.bbox[0] for packet in packets) - min(packet.bbox[0] for packet in packets)
            x_range = max(packet.bbox[2] for packet in packets) - min(packet.bbox[2] for packet in packets)
            axis = str(p["axis"])
            if axis == "dominant":
                axis = "horizontal" if x_range > y_range else "vertical"
            if axis == "horizontal":
                packets.sort(key=lambda item: (item.bbox[2], item.bbox[0]))
                result = tuple(tuple(cell for packet in packets for cell in packet.crop[y]) for y in range(len(packets[0].crop)))
            else:
                packets.sort(key=lambda item: (item.bbox[0], item.bbox[2]))
                result = tuple(row for packet in packets for row in packet.crop)
        elif family == "support_complement_tile":
            background = _background(source, str(p["background_role"]))
            colors = Counter(cell for row in source for cell in row if cell != background)
            if len(colors) != 1:
                raise ValueError("support complement requires one foreground color")
            foreground = next(iter(colors))
            packet = tuple(tuple(foreground if cell == background else background for cell in row) for row in source)
            if p["layout"] == "square_2":
                result = _tile(packet, 2, 2)
            elif p["layout"] == "horizontal_2":
                result = _tile(packet, 1, 2)
            else:
                result = _tile(packet, 2, 1)
        elif family == "frame_object_overlay":
            background = _background(source, str(p["background_role"]))
            packets = _objects(source, background, int(p["connectivity"]))
            if len(packets) < 2 or len({shape(packet.crop) for packet in packets}) != 1:
                raise ValueError("frame packets must share one shape")
            colors = Counter(cell for packet in packets for row in packet.crop for cell in row if cell != background)
            frame = min(colors, key=lambda color: (-colors[color], color))
            height, width = shape(packets[0].crop)
            output = [[frame for _ in range(width)] for _ in range(height)]
            for y in range(height):
                for x in range(width):
                    payload = {packet.crop[y][x] for packet in packets if packet.crop[y][x] not in (background, frame)}
                    if len(payload) > 1:
                        raise ValueError("conflicting frame payloads")
                    if payload:
                        output[y][x] = next(iter(payload))
                    elif all(packet.crop[y][x] == background for packet in packets):
                        output[y][x] = background
            result = grid(output)
        else:
            raise ValueError(f"unknown family {family!r}")
        return grid(result)


def program(family: str, parameters: Mapping[str, Any]) -> Program:
    return Program(family, canonical_json(parameters))


def _enumerate_seeded_programs(first_input: Grid, first_output: Grid) -> Iterator[Program]:
    """Enumerate one demo-seeded view of the complete finite grammar."""

    target_shape = shape(first_output)
    emitted: dict[str, Program] = {}

    def consider(candidate: Program) -> None:
        try:
            if shape(candidate.execute(first_input)) == target_shape:
                emitted.setdefault(candidate.program_id, candidate)
        except (IndexError, KeyError, TypeError, ValueError, ZeroDivisionError):
            pass

    for transform in D4:
        for count_role in ("palette_nonzero", "palette_all", "nonzero_cells", "zero_cells", "foreground_cells", "background_cells"):
            for background_role in ("zero", "mode"):
                for layout in ("pixel", "tile"):
                    consider(program("dynamic_palette_layout", {"transform": transform, "count_role": count_role, "background_role": background_role, "layout": layout}))
        consider(program("edge_profile_expansion", {"transform": transform}))
        for background_role in ("zero", "mode"):
            for vertical_direction in ("forward", "reverse"):
                for horizontal_direction in ("forward", "reverse"):
                    consider(program("diagonal_stamp_closure", {"transform": transform, "background_role": background_role, "vertical_direction": vertical_direction, "horizontal_direction": horizontal_direction}))
            for side_role in ("zero_cells", "background_cells", "nonzero_cells", "foreground_cells"):
                for copy_role in ("zero_cells", "background_cells", "nonzero_cells", "foreground_cells"):
                    for traversal in ("row_major", "boustrophedon"):
                        consider(program("counted_copy_square", {"transform": transform, "background_role": background_role, "side_role": side_role, "copy_role": copy_role, "traversal": traversal}))
            for axis in ("horizontal", "vertical"):
                for target_color in range(10):
                    for seam_rule in ("toward", "away"):
                        consider(program("mirror_complement_layout", {"background_role": background_role, "axis": axis, "target_color": target_color, "seam_rule": seam_rule}))
            for vertical_align in ("top", "center", "bottom"):
                for horizontal_align in ("left", "center", "right"):
                    for axis in ("horizontal", "vertical"):
                        consider(program("keyed_payload_tiling", {"background_role": background_role, "vertical_align": vertical_align, "horizontal_align": horizontal_align, "axis": axis, "transform": transform}))
    for background_role in ("zero", "mode"):
        for axis in ("horizontal", "vertical"):
            # Zero is a semantic canvas role in this schema, not a mode alias.
            # Retaining both aliases can fit demonstrations yet diverge when a
            # held-out foreground becomes the modal color.
            if background_role == "zero":
                consider(program("foreground_cardinality_serialization", {"background_role": background_role, "axis": axis}))
            for bridge_color in range(10):
                consider(program("bridged_diagonal_duplication", {"background_role": background_role, "axis": "rows" if axis == "horizontal" else "columns", "bridge_color": bridge_color}))
        for connectivity in (4, 8):
            for metric in ("area", "bbox"):
                for order in ("ascending", "descending"):
                    for axis in ("horizontal", "vertical"):
                        consider(program("component_rank_serialization", {"background_role": background_role, "connectivity": connectivity, "metric": metric, "order": order, "axis": axis}))
            for align in ("left", "right"):
                for order in ("ascending", "descending"):
                    for orientation in ("rows", "columns"):
                        consider(program("component_count_histogram", {"background_role": background_role, "connectivity": connectivity, "align": align, "order": order, "orientation": orientation}))
            for axis in ("dominant", "horizontal", "vertical"):
                consider(program("hollow_object_pack", {"background_role": background_role, "connectivity": connectivity, "axis": axis}))
            consider(program("frame_object_overlay", {"background_role": background_role, "connectivity": connectivity}))
        for sort_axis in ("columns", "rows"):
            for tie_direction in ("ascending", "descending"):
                for snake in (False, True):
                    consider(program("singleton_boustrophedon_pack", {"background_role": background_role, "sort_axis": sort_axis, "tie_direction": tie_direction, "snake": snake}))
        for layout in ("square_2", "horizontal_2", "vertical_2"):
            consider(program("support_complement_tile", {"background_role": background_role, "layout": layout}))
    yield from (emitted[key] for key in sorted(emitted))


def enumerate_programs(
    demonstrations: Sequence[tuple[Grid, Grid]],
) -> tuple[Program, ...]:
    """Return the canonical union of programs seeded from every demonstration.

    Union seeding makes the finite search invariant to demonstration order while
    retaining target-shape pruning.  A program must still replay every pair.
    """
    emitted: dict[str, Program] = {}
    for source, target in demonstrations:
        for candidate in _enumerate_seeded_programs(source, target):
            emitted.setdefault(candidate.program_id, candidate)
    return tuple(emitted[key] for key in sorted(emitted))


GRAMMAR_CONTRACT = {
    "schema": "komorebi.lasm.block12.relational_shape_grammar",
    "schema_version": SCHEMA_VERSION,
    "stable_families": sorted(STABLE_FAMILIES),
    "provisional_families": sorted(PROVISIONAL_FAMILIES),
    "rejected_experimental_families": sorted(REJECTED_EXPERIMENTAL_FAMILIES),
    "literal_zero_families": sorted(LITERAL_ZERO_FAMILIES),
    "d4_complete_families": sorted(D4_COMPLETE_FAMILIES),
    "d4_partial_families": sorted(D4_PARTIAL_FAMILIES),
    "d4": D4,
    "maximum_programs": MAXIMUM_PROGRAMS,
    "sample_salt": SAMPLE_SALT,
    "parameter_domain_revision": 3,
    "demo_seed_policy": "canonical union across every demonstration",
    "selection": "exact demo replay then complete exact-raster quotient",
    "screen_32_unique_exact": 2,
    "screen_96_unique_exact": 12,
    "escalation_63_unique_exact": 5,
    "full_public_training_tasks": 1000,
    "full_shape_routed_tasks": 320,
    "full_unique_exact": 20,
    "full_wrong": 0,
    "full_ambiguous": 0,
    "net_new_whole_tasks_over_block11": 19,
    "net_new_exact_outputs_over_block11": 20,
    "d4_recompile_pass": 142,
    "d4_recompile_total": 160,
    "zero_fixed_palette_recompile_pass": 20,
    "zero_fixed_palette_recompile_total": 20,
    "all_color_cycle_recompile_pass": 15,
    "all_color_cycle_recompile_total": 20,
}
GRAMMAR_HASH = digest(GRAMMAR_CONTRACT)
GRAMMAR_CONTRACT_HASH = GRAMMAR_HASH


@dataclass(frozen=True, slots=True)
class ShapeConstructorLimits:
    max_training_examples: int = 10
    max_test_examples: int = 10
    maximum_programs: int = MAXIMUM_PROGRAMS

    def __post_init__(self) -> None:
        for field in ("max_training_examples", "max_test_examples", "maximum_programs"):
            value = getattr(self, field)
            if isinstance(value, bool) or not isinstance(value, int) or value < 1:
                raise ValueError(f"{field} must be a positive integer")
        if self.maximum_programs != MAXIMUM_PROGRAMS:
            raise ValueError(f"maximum_programs is frozen at {MAXIMUM_PROGRAMS}")


@dataclass(frozen=True, slots=True)
class ShapeConstructorBehavior:
    behavior_hash: str
    predictions: tuple[Grid, ...]
    programs: tuple[Program, ...]

    def __post_init__(self) -> None:
        if not self.programs:
            raise ValueError("a behavior requires at least one program")
        if self.behavior_hash != digest(self.predictions):
            raise ValueError("behavior hash does not authenticate predictions")
        if self.programs != tuple(sorted(
            self.programs, key=lambda candidate: (candidate.cost, candidate.program_id)
        )):
            raise ValueError("behavior programs must use canonical order")

    @property
    def representative(self) -> Program:
        return self.programs[0]

    def to_record(self) -> dict[str, Any]:
        return {
            "behavior_hash": self.behavior_hash,
            "predictions": self.predictions,
            "representative_program": self.representative.to_record(),
            "equivalent_program_count": len(self.programs),
            "equivalent_program_ids": [candidate.program_id for candidate in self.programs],
            "families": sorted({candidate.family for candidate in self.programs}),
        }


@dataclass(frozen=True, slots=True)
class ShapeConstructorReceipt:
    routed: bool
    complete: bool
    effect_coordinate: Mapping[str, Any]
    programs_enumerated: int
    demonstration_executions: int
    execution_rejections: int
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
            "grammar_hash": GRAMMAR_HASH,
            "effect_coordinate": dict(self.effect_coordinate),
            "maximum_programs": MAXIMUM_PROGRAMS,
            "programs_enumerated": self.programs_enumerated,
            "demonstration_executions": self.demonstration_executions,
            "execution_rejections": self.execution_rejections,
            "exact_programs": self.exact_programs,
            "admitted_programs": self.admitted_programs,
            "test_program_executions": self.test_program_executions,
            "test_grid_executions": self.test_grid_executions,
            "runtime_failures": self.runtime_failures,
            "behavior_classes": self.behavior_classes,
            "limit_reached": self.limit_reached,
        }


@dataclass(frozen=True, slots=True)
class ShapeConstructorCompilation:
    exact_programs: tuple[Program, ...]
    surviving_programs: tuple[Program, ...]
    behaviors: tuple[ShapeConstructorBehavior, ...]
    receipt: ShapeConstructorReceipt
    allow_provisional: bool = False

    def __post_init__(self) -> None:
        if not isinstance(self.allow_provisional, bool):
            raise TypeError("allow_provisional must be Boolean")
        if self.receipt.behavior_classes != len(self.behaviors):
            raise ValueError("receipt behavior count is inconsistent")

    @property
    def selected_behavior(self) -> ShapeConstructorBehavior | None:
        return self.behaviors[0] if len(self.behaviors) == 1 else None

    @property
    def selected_prediction(self) -> tuple[Grid, ...] | None:
        return None if self.selected_behavior is None else self.selected_behavior.predictions

    @property
    def ambiguous(self) -> bool:
        return len(self.behaviors) > 1

    @property
    def behavior_program_map(self) -> Mapping[str, tuple[Program, ...]]:
        return {behavior.behavior_hash: behavior.programs for behavior in self.behaviors}

    @property
    def status(self) -> str:
        if not self.receipt.complete:
            return "limit_abstention"
        if not self.receipt.routed:
            return "not_routed"
        if self.ambiguous:
            return "ambiguous_abstention"
        return "unique" if self.selected_behavior is not None else "no_candidate"

    def to_record(self) -> dict[str, Any]:
        body: dict[str, Any] = {
            "schema": COMPILATION_SCHEMA,
            "schema_version": SCHEMA_VERSION,
            "status": self.status,
            "allow_provisional": self.allow_provisional,
            "exact_programs": [candidate.to_record() for candidate in self.exact_programs],
            "surviving_program_ids": [candidate.program_id for candidate in self.surviving_programs],
            "behavior_program_map": {
                behavior.behavior_hash: [candidate.program_id for candidate in behavior.programs]
                for behavior in self.behaviors
            },
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
    AssertionError, IndexError, KeyError, OverflowError, RuntimeError,
    TypeError, ValueError, ZeroDivisionError,
)


def _effect_coordinate(pairs: Sequence[tuple[Grid, Grid]]) -> dict[str, Any]:
    relations = tuple(
        "same" if shape(source) == shape(target) else "changed"
        for source, target in pairs
    )
    return {
        "kind": "shape_constructor" if "changed" in relations else "shape_preserving",
        "shape_relation_counts": {
            "changed": relations.count("changed"),
            "same": relations.count("same"),
        },
    }


def _empty_compilation(
    *, routed: bool, complete: bool, effect: Mapping[str, Any],
    allow_provisional: bool, programs_enumerated: int = 0, limit_reached: str = "",
) -> ShapeConstructorCompilation:
    return ShapeConstructorCompilation(
        (), (), (),
        ShapeConstructorReceipt(
            routed, complete, effect, programs_enumerated, 0, 0, 0, 0, 0, 0, 0, 0,
            limit_reached,
        ),
        allow_provisional,
    )


def compile_shape_constructors(
    task: Mapping[str, Any], *, allow_provisional: bool = False,
    limits: ShapeConstructorLimits | None = None,
) -> ShapeConstructorCompilation:
    """Compile the complete locked grammar without observing test targets."""
    if not isinstance(allow_provisional, bool):
        raise TypeError("allow_provisional must be Boolean")
    limits = limits or ShapeConstructorLimits()
    safe_task = sanitized_task_mapping(task)
    training = safe_task["train"]
    tests = safe_task["test"]
    if not training or not tests:
        return _empty_compilation(
            routed=False, complete=True, effect={"kind": "empty_task"},
            allow_provisional=allow_provisional,
        )
    if len(training) > limits.max_training_examples:
        return _empty_compilation(
            routed=False, complete=False, effect={"kind": "limit"},
            allow_provisional=allow_provisional, limit_reached="training_example_limit",
        )
    if len(tests) > limits.max_test_examples:
        return _empty_compilation(
            routed=False, complete=False, effect={"kind": "limit"},
            allow_provisional=allow_provisional, limit_reached="test_example_limit",
        )
    pairs = tuple(
        (grid(example["input"]), grid(example["output"]))
        for example in training
    )
    test_inputs = tuple(grid(example["input"]) for example in tests)
    effect = _effect_coordinate(pairs)
    if not any(shape(source) != shape(target) for source, target in pairs):
        return _empty_compilation(
            routed=False, complete=True, effect=effect,
            allow_provisional=allow_provisional,
        )
    programs = enumerate_programs(pairs)
    if len(programs) > limits.maximum_programs:
        return _empty_compilation(
            routed=True, complete=False, effect=effect,
            allow_provisional=allow_provisional, programs_enumerated=len(programs),
            limit_reached="program_enumeration_limit",
        )

    exact: list[Program] = []
    demonstration_executions = 0
    execution_rejections = 0
    for candidate in programs:
        accepted = True
        for source, target in pairs:
            demonstration_executions += 1
            try:
                observed = candidate.execute(source)
            except _EXECUTION_ERRORS:
                execution_rejections += 1
                accepted = False
                continue
            if observed != target:
                accepted = False
        if accepted:
            exact.append(candidate)
    admitted = [
        candidate for candidate in exact
        if allow_provisional or not candidate.provisional
    ]

    groups: dict[str, dict[str, Any]] = {}
    surviving: list[Program] = []
    test_program_executions = 0
    test_grid_executions = 0
    runtime_failures = 0
    for candidate in admitted:
        test_program_executions += 1
        outputs = []
        try:
            for source in test_inputs:
                test_grid_executions += 1
                outputs.append(candidate.execute(source))
        except _EXECUTION_ERRORS:
            runtime_failures += 1
            continue
        surviving.append(candidate)
        predictions = tuple(outputs)
        behavior_hash = digest(predictions)
        group = groups.setdefault(behavior_hash, {"predictions": predictions, "programs": []})
        if group["predictions"] != predictions:
            raise AssertionError("behavior hash collision")
        group["programs"].append(candidate)

    behaviors = []
    for behavior_hash, group in sorted(groups.items()):
        behavior_programs = tuple(sorted(
            group["programs"], key=lambda candidate: (candidate.cost, candidate.program_id)
        ))
        behaviors.append(ShapeConstructorBehavior(
            behavior_hash, group["predictions"], behavior_programs,
        ))
    receipt = ShapeConstructorReceipt(
        routed=True,
        complete=True,
        effect_coordinate=effect,
        programs_enumerated=len(programs),
        demonstration_executions=demonstration_executions,
        execution_rejections=execution_rejections,
        exact_programs=len(exact),
        admitted_programs=len(admitted),
        test_program_executions=test_program_executions,
        test_grid_executions=test_grid_executions,
        runtime_failures=runtime_failures,
        behavior_classes=len(behaviors),
    )
    return ShapeConstructorCompilation(
        tuple(exact), tuple(surviving), tuple(behaviors), receipt, allow_provisional,
    )


def compile_task(task: Mapping[str, Any]) -> ShapeConstructorCompilation:
    """Compatibility alias for the exploratory compiler's permissive policy."""
    return compile_shape_constructors(task, allow_provisional=True)


def sample_order(task_ids: Iterable[str]) -> tuple[str, ...]:
    return tuple(sorted(task_ids, key=lambda task_id: hashlib.sha256(f"{SAMPLE_SALT}{task_id}".encode("ascii")).hexdigest()))


__all__ = [
    "COMPILATION_SCHEMA", "D4", "GRAMMAR_CONTRACT", "GRAMMAR_CONTRACT_HASH", "GRAMMAR_HASH",
    "ContractError", "D4_COMPLETE_FAMILIES", "D4_PARTIAL_FAMILIES", "Grid", "LITERAL_ZERO_FAMILIES",
    "MAXIMUM_PROGRAMS", "PALETTE_ZERO_SENSITIVE_FAMILIES", "PROVISIONAL_FAMILIES", "Program",
    "REJECTED_EXPERIMENTAL_FAMILIES", "SAFE_FAMILIES", "SAMPLE_SALT", "STABLE_FAMILIES",
    "ShapeConstructorBehavior", "ShapeConstructorCompilation", "ShapeConstructorLimits",
    "ShapeConstructorReceipt", "canonical_json", "compile_shape_constructors", "compile_task",
    "digest", "enumerate_programs", "grid", "sample_order", "shape",
]

ShapeConstructorProgram = Program
__all__.append("ShapeConstructorProgram")
