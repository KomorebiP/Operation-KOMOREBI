"""Shape-changing and global structural synthesis lanes.

Every compiler consumes training input/output pairs and returns executable,
role-bound program records.  No task identifier or held-out output is accepted.
"""
from __future__ import annotations

import itertools
from collections import Counter
from typing import Any, Mapping, Sequence

import numpy as np

from .common import (
    apply_recolor, arr, background_roles, bbox, components, crop_to_mask, d4, d4_map,
    equal, freeze, infer_background, infer_recolor, role_color, transform,
)
from .model import CompiledProgram


def _exact_training(task: Mapping[str, Any], family: str, parameters: Mapping[str, Any]) -> bool:
    try:
        return all(equal(execute_family(family, example["input"], parameters), example["output"]) for example in task["train"])
    except Exception:
        return False


def _program(family: str, parameters: Mapping[str, Any], cost: int, origin: str, description: str) -> CompiledProgram:
    return CompiledProgram(family=family, parameters=dict(parameters), cost=cost, origin=origin, description=description)


# ---------------------------------------------------------------------------
# Direct structural constructors
# ---------------------------------------------------------------------------

def execute_kaleido(grid: Any, parameters: Mapping[str, Any]) -> np.ndarray:
    a = arr(grid)
    return np.block([[a, np.fliplr(a)], [np.flipud(a), np.rot90(a, 2)]]).astype(np.int16)


def compile_kaleido(task: Mapping[str, Any]) -> list[CompiledProgram]:
    params: dict[str, Any] = {}
    if _exact_training(task, "kaleido_constructor", params):
        return [_program("kaleido_constructor", params, 4, "shape_constructor", "Four-quadrant D4 kaleidoscopic construction")]
    return []


def execute_fill_bbox(grid: Any, parameters: Mapping[str, Any]) -> np.ndarray:
    a = arr(grid)
    bg = role_color(a, str(parameters["background_role"]))
    counts = Counter(int(v) for v in a.ravel() if int(v) != bg)
    if not counts:
        raise ValueError("fill role has no foreground colors")
    fill_role = str(parameters["fill_role"])
    if fill_role == "most_foreground":
        value = max(counts.values()); winners = [c for c, n in counts.items() if n == value]
    elif fill_role == "rarest_foreground":
        value = min(counts.values()); winners = [c for c, n in counts.items() if n == value]
    elif fill_role == "unique_foreground":
        winners = list(counts) if len(counts) == 1 else []
    else:
        raise KeyError(fill_role)
    if len(winners) != 1:
        raise ValueError("fill role is ambiguous")
    fill = int(winners[0])
    mask = a != bg
    box = bbox(mask)
    if box is None:
        raise ValueError("foreground bounding box is undefined")
    y0, y1, x0, x1 = box
    canvas = str(parameters.get("canvas", "preserve"))
    out = a.copy() if canvas == "preserve" else np.full_like(a, bg)
    out[y0:y1, x0:x1] = fill
    return out


def compile_fill_bbox(task: Mapping[str, Any]) -> list[CompiledProgram]:
    result: list[CompiledProgram] = []
    for background_role in ("most", "corner", "zero"):
        for fill_role in ("most_foreground", "rarest_foreground", "unique_foreground"):
            for canvas in ("preserve", "blank"):
                params = {"background_role": background_role, "fill_role": fill_role, "canvas": canvas}
                if _exact_training(task, "fill_bbox_role", params):
                    result.append(_program("fill_bbox_role", params, 5, "relational_edit", "Fill the foreground bounding box with an input-derived color role"))
    return result


def execute_object_bbox_outline(grid: Any, parameters: Mapping[str, Any]) -> np.ndarray:
    a = arr(grid)
    bg = role_color(a, str(parameters["background_role"]))
    connectivity = int(parameters["connectivity"])
    minimum_area = int(parameters["minimum_area"])
    canvas = str(parameters["canvas"])
    out = a.copy() if canvas == "preserve" else np.full_like(a, bg)
    foreground_components = components(a != bg, connectivity)
    if not foreground_components:
        raise ValueError("no foreground components")
    accepted = 0
    for component in foreground_components:
        if len(component) <= minimum_area:
            if canvas == "preserve":
                for y, x in component:
                    out[y, x] = bg
            continue
        ys = [y for y, _ in component]
        xs = [x for _, x in component]
        y0, y1, x0, x1 = min(ys), max(ys) + 1, min(xs), max(xs) + 1
        color = Counter(int(a[y, x]) for y, x in component).most_common(1)[0][0]
        if canvas == "preserve":
            for y, x in component:
                out[y, x] = bg
        out[y0, x0:x1] = color
        out[y1 - 1, x0:x1] = color
        out[y0:y1, x0] = color
        out[y0:y1, x1 - 1] = color
        accepted += 1
    if accepted == 0:
        raise ValueError("no component passed the area predicate")
    return out


def compile_object_bbox_outline(task: Mapping[str, Any]) -> list[CompiledProgram]:
    result: list[CompiledProgram] = []
    for background_role in ("most", "corner", "zero"):
        for connectivity in (4, 8):
            for minimum_area in (0, 1, 2, 3):
                for canvas in ("blank", "preserve"):
                    params = {
                        "background_role": background_role,
                        "connectivity": connectivity,
                        "minimum_area": minimum_area,
                        "canvas": canvas,
                    }
                    if _exact_training(task, "object_bbox_outline", params):
                        result.append(_program("object_bbox_outline", params, 6, "object_relational_edit", "Replace accepted components by their axis-aligned bounding-box outlines"))
    return result


# ---------------------------------------------------------------------------
# Finite closures
# ---------------------------------------------------------------------------

def _extend_all(a: np.ndarray) -> np.ndarray:
    b = infer_background(a)
    out = a.copy()
    colors = sorted(set(int(v) for v in a.ravel()) - {b})
    h, w = a.shape
    for color in colors:
        points = list(zip(*np.where(a == color)))
        rows = {int(y) for y, _ in points}
        columns = {int(x) for _, x in points}
        for y in rows:
            positions = np.where(a[y] == color)[0]
            if len(positions) >= 2:
                out[y, :] = np.where(a[y, :] == b, color, a[y, :])
        for x in columns:
            positions = np.where(a[:, x] == color)[0]
            if len(positions) >= 2:
                out[:, x] = np.where(a[:, x] == b, color, a[:, x])
        if len(points) == 1:
            y, x = map(int, points[0])
            for dy, dx in ((-1, -1), (-1, 1), (1, -1), (1, 1)):
                cy, cx = y, x
                while 0 <= cy < h and 0 <= cx < w:
                    if out[cy, cx] == b:
                        out[cy, cx] = color
                    cy += dy
                    cx += dx
    return out


def _full_d4_union(a: np.ndarray) -> np.ndarray:
    if a.shape[0] != a.shape[1]:
        raise ValueError("full D4 closure requires a square grid")
    bg = infer_background(a)
    out = a.copy()
    names = ("fh", "fv", "r90", "r180", "r270", "t", "at")
    transforms = d4_map(a)
    for name in names:
        candidate = transforms[name]
        conflict = (out != bg) & (candidate != bg) & (out != candidate)
        if np.any(conflict):
            raise ValueError("D4 closure has a categorical conflict")
        mask = (out == bg) & (candidate != bg)
        out[mask] = candidate[mask]
    return out


def execute_closure(grid: Any, parameters: Mapping[str, Any]) -> np.ndarray:
    key = str(parameters["key"])
    a = arr(grid)
    if key == "extend_all":
        result = _extend_all(a)
    elif key == "full_d4_union":
        result = _full_d4_union(a)
    else:
        raise KeyError(key)
    mapping = parameters.get("recolor", [])
    return apply_recolor(result, mapping) if mapping else result


def compile_closures(task: Mapping[str, Any]) -> list[CompiledProgram]:
    result: list[CompiledProgram] = []
    targets = [arr(example["output"]) for example in task["train"]]
    for key in ("extend_all", "full_d4_union"):
        raw: list[np.ndarray] = []
        try:
            for example in task["train"]:
                raw.append(execute_closure(example["input"], {"key": key}))
        except Exception:
            continue
        mapping: dict[int, int] | None = None
        if not all(equal(a, b) for a, b in zip(raw, targets)):
            mapping = infer_recolor(raw, targets)
            if mapping is None or not all(equal(apply_recolor(a, mapping), b) for a, b in zip(raw, targets)):
                continue
        params = {"key": key, "recolor": sorted((int(k), int(v)) for k, v in (mapping or {}).items())}
        result.append(_program("finite_closure", params, 7 + len(mapping or {}), "fixed_point_closure", "Finite geometric closure inferred from all demonstrations"))
    return result


# ---------------------------------------------------------------------------
# D4 mosaics
# ---------------------------------------------------------------------------

def _base_variants(a: np.ndarray) -> list[tuple[str, np.ndarray]]:
    out: list[tuple[str, np.ndarray]] = []
    for name, value in d4(a):
        out.append((f"full:{name}", value))
    for background_name, background in background_roles(a):
        cropped = crop_to_mask(a, a != background)
        if cropped is not None:
            for name, value in d4(cropped):
                out.append((f"crop:{background_name}:{name}", value))
    h, w = a.shape
    for depth in range(1, min(h, w) // 2 + 1):
        border = np.concatenate([
            a[depth - 1, depth - 1:w - depth + 1],
            a[h - depth, depth - 1:w - depth + 1],
            a[depth:h - depth, depth - 1],
            a[depth:h - depth, w - depth],
        ])
        if len(set(int(v) for v in border)) != 1:
            break
        core = a[depth:h - depth, depth:w - depth]
        for name, value in d4(core):
            out.append((f"strip:{depth}:{name}", value))
    result: list[tuple[str, np.ndarray]] = []
    seen = set()
    for spec, value in out:
        key = freeze(value)
        if key not in seen:
            seen.add(key)
            result.append((spec, value))
    return result


def _get_mosaic_base(grid: Any, spec: str) -> np.ndarray:
    a = arr(grid)
    parts = spec.split(":")
    if parts[0] == "full":
        base, name = a, parts[1]
    elif parts[0] == "crop":
        backgrounds = dict(background_roles(a))
        if parts[1] not in backgrounds:
            raise ValueError("background role unavailable")
        cropped = crop_to_mask(a, a != backgrounds[parts[1]])
        if cropped is None:
            raise ValueError("empty crop")
        base, name = cropped, parts[2]
    elif parts[0] == "strip":
        depth = int(parts[1])
        if min(a.shape) <= 2 * depth:
            raise ValueError("strip depth exceeds grid")
        base, name = a[depth:-depth, depth:-depth], parts[2]
    else:
        raise KeyError(parts[0])
    return transform(base, name)


def execute_mosaic(grid: Any, parameters: Mapping[str, Any]) -> np.ndarray:
    base = _get_mosaic_base(grid, str(parameters["base"]))
    variants = d4_map(base)
    mapping = parameters.get("recolor", [])
    rows: list[np.ndarray] = []
    for row in parameters["pattern"]:
        blocks = []
        for name in row:
            if name not in variants:
                raise ValueError("mosaic transform unavailable")
            value = variants[name]
            blocks.append(apply_recolor(value, mapping) if mapping else value)
        rows.append(np.hstack(blocks))
    return np.vstack(rows).astype(np.int16)


def compile_mosaic(task: Mapping[str, Any]) -> list[CompiledProgram]:
    training = list(task["train"])
    first_input, first_output = arr(training[0]["input"]), arr(training[0]["output"])
    result: list[CompiledProgram] = []
    for base_spec, base in _base_variants(first_input):
        bh, bw = base.shape
        oh, ow = first_output.shape
        if oh % bh or ow % bw:
            continue
        rows, columns = oh // bh, ow // bw
        if rows * columns < 2 or rows > 6 or columns > 6:
            continue
        pattern: list[list[str]] = []
        maps: list[dict[int, int]] = []
        variants = d4(base)
        valid = True
        for row in range(rows):
            pattern_row: list[str] = []
            for column in range(columns):
                block = first_output[row * bh:(row + 1) * bh, column * bw:(column + 1) * bw]
                matches = []
                for name, candidate in variants:
                    if candidate.shape != block.shape:
                        continue
                    mapping = infer_recolor([candidate], [block])
                    if mapping is not None:
                        matches.append((len(mapping), name, mapping))
                if not matches:
                    valid = False
                    break
                matches.sort(key=lambda item: (item[0], item[1]))
                _, name, mapping = matches[0]
                pattern_row.append(name)
                maps.append(mapping)
            if not valid:
                break
            pattern.append(pattern_row)
        if not valid:
            continue
        merged: dict[int, int] = {}
        for mapping in maps:
            for source, target in mapping.items():
                if source in merged and merged[source] != target:
                    valid = False
                    break
                merged[source] = target
            if not valid:
                break
        if not valid:
            continue
        params = {
            "base": base_spec,
            "pattern": pattern,
            "recolor": sorted((int(k), int(v)) for k, v in merged.items()),
        }
        if _exact_training(task, "d4_mosaic", params):
            result.append(_program("d4_mosaic", params, 3 + rows * columns + len(merged), "layout_constructor", "Tile D4 transforms of a discovered base packet"))
    return result


# ---------------------------------------------------------------------------
# Panel partition and overlay
# ---------------------------------------------------------------------------

def _separator_panels(a: np.ndarray) -> list[tuple[str, list[np.ndarray]]]:
    h, w = a.shape
    row_runs: list[tuple[int, int, int]] = []
    index = 0
    while index < h:
        if len(set(int(v) for v in a[index])) == 1:
            color = int(a[index, 0])
            end = index + 1
            while end < h and np.all(a[end] == color):
                end += 1
            row_runs.append((index, end, color))
            index = end
        else:
            index += 1
    column_runs: list[tuple[int, int, int]] = []
    index = 0
    while index < w:
        if len(set(int(v) for v in a[:, index])) == 1:
            color = int(a[0, index])
            end = index + 1
            while end < w and np.all(a[:, end] == color):
                end += 1
            column_runs.append((index, end, color))
            index = end
        else:
            index += 1
    out: list[tuple[str, list[np.ndarray]]] = []
    colors = sorted(set([item[2] for item in row_runs] + [item[2] for item in column_runs]))
    for color in colors:
        rows = [item for item in row_runs if item[2] == color and item[0] > 0 and item[1] < h]
        columns = [item for item in column_runs if item[2] == color and item[0] > 0 and item[1] < w]
        row_intervals: list[tuple[int, int]] = []
        start = 0
        for y0, y1, _ in rows:
            row_intervals.append((start, y0))
            start = y1
        row_intervals.append((start, h))
        column_intervals: list[tuple[int, int]] = []
        start = 0
        for x0, x1, _ in columns:
            column_intervals.append((start, x0))
            start = x1
        column_intervals.append((start, w))
        panels = [a[y0:y1, x0:x1].copy() for y0, y1 in row_intervals for x0, x1 in column_intervals if y1 > y0 and x1 > x0]
        if 2 <= len(panels) <= 16 and len({panel.shape for panel in panels}) == 1:
            out.append((f"sep:{color}:r{tuple(rows)}:c{tuple(columns)}", panels))
    for rows in (1, 2, 3, 4):
        for columns in (1, 2, 3, 4):
            if rows * columns < 2 or h % rows or w % columns:
                continue
            panels = [
                a[row * h // rows:(row + 1) * h // rows, column * w // columns:(column + 1) * w // columns].copy()
                for row in range(rows) for column in range(columns)
            ]
            out.append((f"equal:{rows}x{columns}", panels))
    result = []
    seen = set()
    for spec, panels in out:
        key = tuple(freeze(panel) for panel in panels)
        if key not in seen:
            seen.add(key)
            result.append((spec, panels))
    return result


def _panel_combinations(panels: Sequence[np.ndarray]) -> list[tuple[str, np.ndarray]]:
    if not panels or len({panel.shape for panel in panels}) != 1:
        return []
    count = len(panels)
    shape = panels[0].shape
    background = Counter(int(v) for panel in panels for v in panel.ravel()).most_common(1)[0][0]
    out: list[tuple[str, np.ndarray]] = []
    for index, panel in enumerate(panels):
        for name, value in d4(panel):
            if value.shape == shape:
                out.append((f"select:{index}|{name}", value))
    for order_name, order in (("forward", range(count)), ("reverse", range(count - 1, -1, -1))):
        value = np.full(shape, background, dtype=np.int16)
        for index in order:
            mask = panels[index] != background
            value[mask] = panels[index][mask]
        out.append((f"overlay:{order_name}", value))
    stack = np.stack(panels)
    nonbackground = stack != background
    counts = nonbackground.sum(axis=0)
    colors = sorted(set(int(v) for v in stack.ravel() if int(v) != background))
    role = colors[0] if colors else (1 if background != 1 else 2)
    for k in range(1, count + 1):
        value = np.full(shape, background, dtype=np.int16)
        value[counts == k] = role
        out.append((f"count_eq:{k}:role=minfg", value))
        value = np.full(shape, background, dtype=np.int16)
        value[counts >= k] = role
        out.append((f"count_ge:{k}:role=minfg", value))
    value = np.full(shape, background, dtype=np.int16)
    same = np.all(stack == stack[0], axis=0) & (stack[0] != background)
    value[same] = stack[0][same]
    out.append(("all_equal_nonbg", value))
    value = np.full(shape, background, dtype=np.int16)
    mask = counts == 1
    for panel in panels:
        value[mask & (panel != background)] = panel[mask & (panel != background)]
    out.append(("xor_support", value))
    result = []
    seen = set()
    for name, value in out:
        key = freeze(value)
        if key not in seen:
            seen.add(key)
            result.append((name, value))
    return result


def _find_separator_panels(a: np.ndarray, spec: str) -> list[np.ndarray]:
    for candidate_spec, panels in _separator_panels(a):
        if candidate_spec == spec:
            return panels
    raise ValueError("panel specification unavailable")


def _apply_panel_operation(panels: Sequence[np.ndarray], operation: str) -> np.ndarray:
    if not panels or len({panel.shape for panel in panels}) != 1:
        raise ValueError("panel operation requires equally shaped panels")
    count = len(panels)
    shape = panels[0].shape
    background = Counter(int(v) for panel in panels for v in panel.ravel()).most_common(1)[0][0]
    if operation.startswith("select:"):
        prefix, transform_name = operation.split("|", 1)
        index = int(prefix.split(":", 1)[1])
        if not 0 <= index < count:
            raise ValueError("panel selection index out of range")
        value = d4_map(panels[index]).get(transform_name)
        if value is None or value.shape != shape:
            raise ValueError("panel transform unavailable")
        return value.copy()
    if operation.startswith("overlay:"):
        order_name = operation.split(":", 1)[1]
        order = range(count) if order_name == "forward" else range(count - 1, -1, -1)
        value = np.full(shape, background, dtype=np.int16)
        for index in order:
            mask = panels[index] != background
            value[mask] = panels[index][mask]
        return value
    stack = np.stack(panels)
    nonbackground = stack != background
    counts = nonbackground.sum(axis=0)
    colors = sorted(set(int(v) for v in stack.ravel() if int(v) != background))
    role = colors[0] if colors else (1 if background != 1 else 2)
    if operation.startswith("count_eq:") or operation.startswith("count_ge:"):
        parts = operation.split(":")
        threshold = int(parts[1])
        mask = counts == threshold if operation.startswith("count_eq:") else counts >= threshold
        value = np.full(shape, background, dtype=np.int16)
        value[mask] = role
        return value
    if operation == "all_equal_nonbg":
        value = np.full(shape, background, dtype=np.int16)
        mask = np.all(stack == stack[0], axis=0) & (stack[0] != background)
        value[mask] = stack[0][mask]
        return value
    if operation == "xor_support":
        value = np.full(shape, background, dtype=np.int16)
        mask = counts == 1
        for panel in panels:
            active = mask & (panel != background)
            value[active] = panel[active]
        return value
    raise ValueError("panel operation unavailable")


def execute_panel(grid: Any, parameters: Mapping[str, Any]) -> np.ndarray:
    panels = _find_separator_panels(arr(grid), str(parameters["spec"]))
    value = _apply_panel_operation(panels, str(parameters["operation"]))
    mapping = parameters.get("recolor", [])
    return apply_recolor(value, mapping) if mapping else value


def compile_panel(task: Mapping[str, Any]) -> list[CompiledProgram]:
    training = list(task["train"])
    first_input, first_output = arr(training[0]["input"]), arr(training[0]["output"])
    result: list[CompiledProgram] = []
    for spec, panels in _separator_panels(first_input):
        for operation, candidate in _panel_combinations(panels):
            mapping = infer_recolor([candidate], [first_output])
            if mapping is None:
                continue
            params = {"spec": spec, "operation": operation, "recolor": sorted((int(k), int(v)) for k, v in mapping.items())}
            if _exact_training(task, "panel_program", params):
                result.append(_program("panel_program", params, 5 + len(panels) + len(mapping), "panel_relational_constructor", "Partition around uniform separators and combine aligned panels"))
    return result


# Role-normalized panel compiler used when absolute separator coordinates differ.
def _role_panelizations(a: np.ndarray) -> list[tuple[tuple[Any, ...], list[np.ndarray], int | None]]:
    h, w = a.shape
    row_runs: list[tuple[int, int, int]] = []
    i = 0
    while i < h:
        if len(set(int(v) for v in a[i])) == 1:
            color = int(a[i, 0]); j = i + 1
            while j < h and np.all(a[j] == color): j += 1
            if i > 0 and j < h: row_runs.append((i, j, color))
            i = j
        else: i += 1
    column_runs: list[tuple[int, int, int]] = []
    i = 0
    while i < w:
        if len(set(int(v) for v in a[:, i])) == 1:
            color = int(a[0, i]); j = i + 1
            while j < w and np.all(a[:, j] == color): j += 1
            if i > 0 and j < w: column_runs.append((i, j, color))
            i = j
        else: i += 1
    out: list[tuple[tuple[Any, ...], list[np.ndarray], int | None]] = []
    colors = sorted(set([item[2] for item in row_runs] + [item[2] for item in column_runs]))
    for role, color in enumerate(colors):
        rows = [item for item in row_runs if item[2] == color]
        columns = [item for item in column_runs if item[2] == color]
        row_intervals = []; start = 0
        for y0, y1, _ in rows: row_intervals.append((start, y0)); start = y1
        row_intervals.append((start, h))
        column_intervals = []; start = 0
        for x0, x1, _ in columns: column_intervals.append((start, x0)); start = x1
        column_intervals.append((start, w))
        panels = [a[y0:y1, x0:x1].copy() for y0, y1 in row_intervals for x0, x1 in column_intervals if y1 > y0 and x1 > x0]
        if 2 <= len(panels) <= 9 and len({panel.shape for panel in panels}) == 1:
            out.append((("uniform_separator", len(rows) + 1, len(columns) + 1, role, len(rows), len(columns)), panels, color))
    for rows in (1, 2, 3, 4):
        for columns in (1, 2, 3, 4):
            if rows * columns < 2 or rows * columns > 9 or h % rows or w % columns:
                continue
            panels = [a[r * h // rows:(r + 1) * h // rows, c * w // columns:(c + 1) * w // columns].copy() for r in range(rows) for c in range(columns)]
            out.append((("equal", rows, columns), panels, None))
    result = []; seen = set()
    for spec, panels, separator in out:
        key = tuple(freeze(panel) for panel in panels)
        if key not in seen:
            seen.add(key); result.append((spec, panels, separator))
    return result


def _role_panels(a: np.ndarray, spec: Sequence[Any]) -> tuple[list[np.ndarray], int | None]:
    target = tuple(spec)
    for candidate, panels, separator in _role_panelizations(a):
        if tuple(candidate) == target:
            return panels, separator
    raise ValueError("role-normalized panelization unavailable")


def _role_panel_operations(panels: Sequence[np.ndarray], separator: int | None) -> list[tuple[tuple[Any, ...], np.ndarray]]:
    count = len(panels); shape = panels[0].shape
    background = Counter(int(v) for panel in panels for v in panel.ravel()).most_common(1)[0][0]
    out: list[tuple[tuple[Any, ...], np.ndarray]] = []
    transformed = [d4_map(panel) for panel in panels]
    for index, panel in enumerate(panels):
        for name, value in d4_map(panel).items():
            if value.shape == shape: out.append((("select", index, name), value))
    for order_name, order in (("forward", tuple(range(count))), ("reverse", tuple(reversed(range(count))))):
        value = np.full(shape, background, dtype=np.int16)
        for index in order:
            mask = panels[index] != background; value[mask] = panels[index][mask]
        out.append((("overlay", order_name, tuple("id" for _ in panels)), value))
    for left_index, right_index in itertools.combinations(range(count), 2):
        for left_name, left in transformed[left_index].items():
            if left.shape != shape: continue
            for right_name, right in transformed[right_index].items():
                if right.shape != shape: continue
                left_mask, right_mask = left != background, right != background
                variants = []
                value = left.copy(); value[right_mask] = right[right_mask]; variants.append(("overlay_ab", value))
                value = right.copy(); value[left_mask] = left[left_mask]; variants.append(("overlay_ba", value))
                for name, mask in (("union", left_mask | right_mask), ("inter", left_mask & right_mask), ("xor", left_mask ^ right_mask), ("a_minus_b", left_mask & ~right_mask), ("b_minus_a", right_mask & ~left_mask)):
                    value = np.full(shape, background, dtype=np.int16)
                    value[mask & right_mask] = right[mask & right_mask]
                    value[mask & left_mask] = left[mask & left_mask]
                    variants.append((name, value))
                value = np.where(left == right, left, background); variants.append(("equal_value", value))
                value = np.where(left != right, left, background); variants.append(("different_take_a", value))
                value = np.where(left != right, right, background); variants.append(("different_take_b", value))
                for operation, value in variants:
                    out.append((("pair", left_index, right_index, left_name, right_name, operation), np.asarray(value, dtype=np.int16)))
    stack = np.stack(panels); nonbackground = stack != background; support_count = nonbackground.sum(axis=0)
    colors = sorted(set(int(v) for v in stack.ravel() if int(v) != background))
    role = separator if separator is not None else (colors[0] if colors else (1 if background != 1 else 2))
    for k in range(1, count + 1):
        for name, mask in (("eq", support_count == k), ("ge", support_count >= k), ("le", support_count <= k)):
            value = np.full(shape, background, dtype=np.int16); value[mask] = role
            out.append((("support_count", name, k), value))
    value = np.full(shape, background, dtype=np.int16)
    for y in range(shape[0]):
        for x in range(shape[1]):
            counts = Counter(int(panel[y, x]) for panel in panels if int(panel[y, x]) != background)
            if counts:
                maximum = max(counts.values()); winners = sorted(color for color, number in counts.items() if number == maximum)
                if len(winners) == 1: value[y, x] = winners[0]
    out.append((("majority_nonbg",), value))
    result = []; seen = set()
    for operation, value in out:
        key = freeze(value)
        if key not in seen:
            seen.add(key); result.append((operation, value))
    return result


def _apply_role_panel_operation(
    panels: Sequence[np.ndarray], separator: int | None, operation: Sequence[Any]
) -> np.ndarray:
    if not panels or len({panel.shape for panel in panels}) != 1:
        raise ValueError("role panel operation requires equally shaped panels")
    op = tuple(operation)
    count = len(panels)
    shape = panels[0].shape
    background = Counter(int(v) for panel in panels for v in panel.ravel()).most_common(1)[0][0]
    kind = str(op[0]) if op else ""
    if kind == "select":
        index, transform_name = int(op[1]), str(op[2])
        if not 0 <= index < count:
            raise ValueError("role panel selection index out of range")
        value = d4_map(panels[index]).get(transform_name)
        if value is None or value.shape != shape:
            raise ValueError("role panel transform unavailable")
        return value.copy()
    if kind == "overlay":
        order_name = str(op[1])
        transform_names = tuple(op[2]) if len(op) > 2 else tuple("id" for _ in panels)
        if len(transform_names) != count:
            raise ValueError("role panel overlay transform count mismatch")
        transformed = []
        for panel, name in zip(panels, transform_names):
            value = d4_map(panel).get(str(name))
            if value is None or value.shape != shape:
                raise ValueError("role panel overlay transform unavailable")
            transformed.append(value)
        order = range(count) if order_name == "forward" else range(count - 1, -1, -1)
        value = np.full(shape, background, dtype=np.int16)
        for index in order:
            mask = transformed[index] != background
            value[mask] = transformed[index][mask]
        return value
    if kind == "pair":
        left_index, right_index = int(op[1]), int(op[2])
        left_name, right_name, operation_name = str(op[3]), str(op[4]), str(op[5])
        left = d4_map(panels[left_index]).get(left_name)
        right = d4_map(panels[right_index]).get(right_name)
        if left is None or right is None or left.shape != shape or right.shape != shape:
            raise ValueError("role panel pair transform unavailable")
        left_mask, right_mask = left != background, right != background
        if operation_name == "overlay_ab":
            value = left.copy(); value[right_mask] = right[right_mask]; return value
        if operation_name == "overlay_ba":
            value = right.copy(); value[left_mask] = left[left_mask]; return value
        masks = {
            "union": left_mask | right_mask,
            "inter": left_mask & right_mask,
            "xor": left_mask ^ right_mask,
            "a_minus_b": left_mask & ~right_mask,
            "b_minus_a": right_mask & ~left_mask,
        }
        if operation_name in masks:
            mask = masks[operation_name]
            value = np.full(shape, background, dtype=np.int16)
            value[mask & right_mask] = right[mask & right_mask]
            value[mask & left_mask] = left[mask & left_mask]
            return value
        if operation_name == "equal_value":
            return np.where(left == right, left, background).astype(np.int16)
        if operation_name == "different_take_a":
            return np.where(left != right, left, background).astype(np.int16)
        if operation_name == "different_take_b":
            return np.where(left != right, right, background).astype(np.int16)
        raise ValueError("unknown role panel pair operation")
    stack = np.stack(panels)
    nonbackground = stack != background
    support_count = nonbackground.sum(axis=0)
    colors = sorted(set(int(v) for v in stack.ravel() if int(v) != background))
    role = separator if separator is not None else (colors[0] if colors else (1 if background != 1 else 2))
    if kind == "support_count":
        relation, threshold = str(op[1]), int(op[2])
        if relation == "eq": mask = support_count == threshold
        elif relation == "ge": mask = support_count >= threshold
        elif relation == "le": mask = support_count <= threshold
        else: raise ValueError("unknown support-count relation")
        value = np.full(shape, background, dtype=np.int16); value[mask] = role
        return value
    if kind == "majority_nonbg":
        value = np.full(shape, background, dtype=np.int16)
        for y in range(shape[0]):
            for x in range(shape[1]):
                counts = Counter(int(panel[y, x]) for panel in panels if int(panel[y, x]) != background)
                if counts:
                    maximum = max(counts.values())
                    winners = sorted(color for color, number in counts.items() if number == maximum)
                    if len(winners) == 1:
                        value[y, x] = winners[0]
        return value
    raise ValueError("role panel operation unavailable")


def execute_role_panel(grid: Any, parameters: Mapping[str, Any]) -> np.ndarray:
    panels, separator = _role_panels(arr(grid), parameters["panelization"])
    value = _apply_role_panel_operation(panels, separator, parameters["operation"])
    mapping = parameters.get("recolor", [])
    return apply_recolor(value, mapping) if mapping else value


def compile_role_panel(task: Mapping[str, Any]) -> list[CompiledProgram]:
    training = list(task["train"])
    first_input, first_output = arr(training[0]["input"]), arr(training[0]["output"])
    result: list[CompiledProgram] = []
    for spec, panels, separator in _role_panelizations(first_input):
        for operation, candidate in _role_panel_operations(panels, separator):
            mapping = infer_recolor([candidate], [first_output])
            if mapping is None: continue
            params = {"panelization": list(spec), "operation": list(operation), "recolor": sorted((int(k), int(v)) for k, v in mapping.items())}
            if _exact_training(task, "role_panel_program", params):
                result.append(_program("role_panel_program", params, 8 + len(mapping), "panel_relational_constructor", "Role-normalized panel selection, overlay, or Boolean combination"))
    return result


# ---------------------------------------------------------------------------
# Block reduction
# ---------------------------------------------------------------------------

def execute_block_reduce(grid: Any, parameters: Mapping[str, Any]) -> np.ndarray:
    a = arr(grid)
    fy, fx = map(int, parameters["factor"])
    if a.shape[0] % fy or a.shape[1] % fx:
        raise ValueError("input shape is not divisible by block factor")
    background = infer_background(a)
    output = np.zeros((a.shape[0] // fy, a.shape[1] // fx), dtype=np.int16)
    mode = str(parameters["mode"])
    for y in range(output.shape[0]):
        for x in range(output.shape[1]):
            block = a[y * fy:(y + 1) * fy, x * fx:(x + 1) * fx]
            counts = Counter(int(v) for v in block.ravel())
            if mode == "mode": value = counts.most_common(1)[0][0]
            elif mode == "min": value = min(counts)
            elif mode == "max": value = max(counts)
            elif mode == "top_left": value = int(block[0, 0])
            elif mode == "center": value = int(block[(fy - 1) // 2, (fx - 1) // 2])
            elif mode == "unique_nonbackground":
                colors = [color for color in counts if color != background]
                value = colors[0] if len(colors) == 1 else background
            elif mode == "any_nonbackground":
                colors = [(number, color) for color, number in counts.items() if color != background]
                value = max(colors)[1] if colors else background
            elif mode == "all_same_nonbackground": value = next(iter(counts)) if len(counts) == 1 else background
            else: raise KeyError(mode)
            output[y, x] = value
    mapping = parameters.get("recolor", [])
    return apply_recolor(output, mapping) if mapping else output


def compile_block_reduce(task: Mapping[str, Any]) -> list[CompiledProgram]:
    training = list(task["train"])
    factors = []
    for example in training:
        source, target = arr(example["input"]), arr(example["output"])
        if source.shape[0] % target.shape[0] or source.shape[1] % target.shape[1]:
            return []
        factors.append((source.shape[0] // target.shape[0], source.shape[1] // target.shape[1]))
    if len(set(factors)) != 1:
        return []
    fy, fx = factors[0]
    if fy * fx <= 1 or fy > 15 or fx > 15:
        return []
    result = []
    for mode in ("mode", "min", "max", "top_left", "center", "unique_nonbackground", "any_nonbackground", "all_same_nonbackground"):
        raw = []
        try:
            for example in training:
                raw.append(execute_block_reduce(example["input"], {"factor": [fy, fx], "mode": mode}))
        except Exception:
            continue
        targets = [arr(example["output"]) for example in training]
        mapping = infer_recolor(raw, targets)
        if mapping is None or not all(equal(apply_recolor(candidate, mapping), target) for candidate, target in zip(raw, targets)):
            continue
        params = {"factor": [fy, fx], "mode": mode, "recolor": sorted((int(k), int(v)) for k, v in mapping.items())}
        result.append(_program("block_reduce", params, 4 + len(mapping), "shape_constructor", "Reduce uniform input blocks by a categorical statistic"))
    return result


# ---------------------------------------------------------------------------
# Public dispatch and routed compiler
# ---------------------------------------------------------------------------

def execute_family(family: str, grid: Any, parameters: Mapping[str, Any]) -> np.ndarray:
    if family == "kaleido_constructor": return execute_kaleido(grid, parameters)
    if family == "fill_bbox_role": return execute_fill_bbox(grid, parameters)
    if family == "object_bbox_outline": return execute_object_bbox_outline(grid, parameters)
    if family == "finite_closure": return execute_closure(grid, parameters)
    if family == "d4_mosaic": return execute_mosaic(grid, parameters)
    if family == "panel_program": return execute_panel(grid, parameters)
    if family == "role_panel_program": return execute_role_panel(grid, parameters)
    if family == "block_reduce": return execute_block_reduce(grid, parameters)
    raise KeyError(family)


SAME_SHAPE_COMPILERS = (compile_fill_bbox, compile_object_bbox_outline, compile_closures)
SHAPE_CHANGE_COMPILERS = (compile_kaleido, compile_mosaic, compile_panel, compile_role_panel, compile_block_reduce)


def compile_structural(task: Mapping[str, Any], *, same_shape: bool) -> tuple[list[CompiledProgram], list[str]]:
    programs: list[CompiledProgram] = []
    lanes: list[str] = []
    if same_shape:
        compilers = list(SAME_SHAPE_COMPILERS)
    else:
        examples = list(task.get("train", []))
        source_shapes = [arr(example["input"]).shape for example in examples]
        target_shapes = [arr(example["output"]).shape for example in examples]
        expansions = all(target[0] >= source[0] and target[1] >= source[1] and target != source for source, target in zip(source_shapes, target_shapes))
        contractions = all(target[0] <= source[0] and target[1] <= source[1] and target != source for source, target in zip(source_shapes, target_shapes))
        double = all(target == (2 * source[0], 2 * source[1]) for source, target in zip(source_shapes, target_shapes))
        divisible_down = all(source[0] % target[0] == 0 and source[1] % target[1] == 0 for source, target in zip(source_shapes, target_shapes))
        compilers = []
        if double:
            compilers.append(compile_kaleido)
        if expansions:
            compilers.append(compile_mosaic)
        if contractions:
            first_source = arr(examples[0]["input"]); first_target = arr(examples[0]["output"])
            possible_panel_shape = any(panels and panels[0].shape == first_target.shape for _, panels in _separator_panels(first_source))
            possible_role_panel_shape = any(panels and panels[0].shape == first_target.shape for _, panels, _ in _role_panelizations(first_source))
            if possible_panel_shape:
                compilers.append(compile_panel)
            if possible_role_panel_shape:
                compilers.append(compile_role_panel)
            if divisible_down:
                compilers.append(compile_block_reduce)
    for compiler in compilers:
        lanes.append(compiler.__name__)
        try:
            programs.extend(compiler(task))
        except Exception:
            continue
    by_signature = {program.signature: program for program in programs}
    return list(by_signature.values()), lanes
