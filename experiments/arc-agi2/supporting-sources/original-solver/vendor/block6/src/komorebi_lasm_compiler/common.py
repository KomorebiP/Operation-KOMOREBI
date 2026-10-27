"""Small deterministic grid helpers shared by Block 6 synthesis lanes."""
from __future__ import annotations

from collections import Counter
from typing import Any, Iterable, Mapping, Sequence

import numpy as np

Grid = tuple[tuple[int, ...], ...]


def arr(value: Any) -> np.ndarray:
    a = np.asarray(value, dtype=np.int16)
    if a.ndim != 2 or a.size == 0:
        raise ValueError("grid must be a nonempty two-dimensional array")
    return a


def freeze(value: Any) -> Grid:
    return tuple(tuple(int(v) for v in row) for row in arr(value).tolist())


def equal(left: Any, right: Any) -> bool:
    a, b = arr(left), arr(right)
    return a.shape == b.shape and bool(np.array_equal(a, b))


def infer_background(a: Any) -> int:
    value = arr(a)
    return Counter(int(v) for v in value.ravel()).most_common(1)[0][0]


def background_roles(a: Any) -> list[tuple[str, int]]:
    value = arr(a)
    counts = Counter(int(v) for v in value.ravel())
    corners = Counter([int(value[0, 0]), int(value[0, -1]), int(value[-1, 0]), int(value[-1, -1])])
    values = [("most", counts.most_common(1)[0][0]), ("corner", corners.most_common(1)[0][0]), ("zero", 0)]
    result: list[tuple[str, int]] = []
    seen: set[int] = set()
    for name, color in values:
        if color not in seen:
            seen.add(color)
            result.append((name, color))
    return result


def role_color(a: Any, role: str) -> int:
    value = arr(a)
    counts = Counter(int(v) for v in value.ravel())
    bg = counts.most_common(1)[0][0]
    if role == "zero":
        return 0
    if role in dict(background_roles(value)):
        return int(dict(background_roles(value))[role])
    foreground = {c: n for c, n in counts.items() if c != bg}
    if not foreground:
        return int(bg)
    if role == "most_foreground":
        maximum = max(foreground.values())
        winners = [c for c, n in foreground.items() if n == maximum]
        if len(winners) != 1:
            raise ValueError("most_foreground role is ambiguous")
        return int(winners[0])
    if role == "rarest_foreground":
        minimum = min(foreground.values())
        winners = [c for c, n in foreground.items() if n == minimum]
        if len(winners) != 1:
            raise ValueError("rarest_foreground role is ambiguous")
        return int(winners[0])
    if role == "unique_foreground":
        if len(foreground) != 1:
            raise ValueError("unique_foreground role is ambiguous")
        return int(next(iter(foreground)))
    raise KeyError(role)


def bbox(mask: Any) -> tuple[int, int, int, int] | None:
    m = np.asarray(mask, dtype=bool)
    ys, xs = np.nonzero(m)
    if len(ys) == 0:
        return None
    return int(ys.min()), int(ys.max()) + 1, int(xs.min()), int(xs.max()) + 1


def crop_to_mask(a: Any, mask: Any) -> np.ndarray | None:
    value = arr(a)
    box = bbox(mask)
    if box is None:
        return None
    y0, y1, x0, x1 = box
    return value[y0:y1, x0:x1].copy()


def components(mask: Any, connectivity: int = 4) -> list[list[tuple[int, int]]]:
    m = np.asarray(mask, dtype=bool)
    h, w = m.shape
    seen = np.zeros_like(m, dtype=bool)
    directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]
    if connectivity == 8:
        directions += [(-1, -1), (-1, 1), (1, -1), (1, 1)]
    result: list[list[tuple[int, int]]] = []
    for y in range(h):
        for x in range(w):
            if not m[y, x] or seen[y, x]:
                continue
            stack = [(y, x)]
            seen[y, x] = True
            component: list[tuple[int, int]] = []
            while stack:
                cy, cx = stack.pop()
                component.append((cy, cx))
                for dy, dx in directions:
                    ny, nx = cy + dy, cx + dx
                    if 0 <= ny < h and 0 <= nx < w and m[ny, nx] and not seen[ny, nx]:
                        seen[ny, nx] = True
                        stack.append((ny, nx))
            result.append(component)
    return result


def d4(a: Any) -> list[tuple[str, np.ndarray]]:
    value = arr(a)
    variants = [
        ("id", value),
        ("r90", np.rot90(value, 1)),
        ("r180", np.rot90(value, 2)),
        ("r270", np.rot90(value, 3)),
        ("fh", np.fliplr(value)),
        ("fv", np.flipud(value)),
        ("t", value.T),
        ("at", np.rot90(value.T, 2)),
    ]
    result: list[tuple[str, np.ndarray]] = []
    seen: set[Grid] = set()
    for name, candidate in variants:
        key = freeze(candidate)
        if key not in seen:
            seen.add(key)
            result.append((name, np.asarray(candidate, dtype=np.int16)))
    return result


def transform(a: Any, name: str) -> np.ndarray:
    try:
        return d4_map(a)[name].copy()
    except KeyError as error:
        raise ValueError(f"D4 transform {name!r} is unavailable") from error


def infer_recolor(sources: Sequence[Any], targets: Sequence[Any]) -> dict[int, int] | None:
    mapping: dict[int, int] = {}
    for source, target in zip(sources, targets):
        a, b = arr(source), arr(target)
        if a.shape != b.shape:
            return None
        for x, y in zip(a.ravel(), b.ravel()):
            source_color, target_color = int(x), int(y)
            if source_color in mapping and mapping[source_color] != target_color:
                return None
            mapping[source_color] = target_color
    return mapping


def apply_recolor(a: Any, mapping: Mapping[int, int] | Sequence[Sequence[int]]) -> np.ndarray:
    value = arr(a)
    result = value.copy()
    items = mapping.items() if isinstance(mapping, Mapping) else mapping
    for source, target in items:
        result[value == int(source)] = int(target)
    return result


def training_hashes(task: Mapping[str, Any]) -> tuple[str, ...]:
    import hashlib, json
    hashes = []
    for example in task.get("train", []):
        payload = json.dumps({"input": freeze(example["input"]), "output": freeze(example["output"])}, separators=(",", ":"), sort_keys=True)
        hashes.append(hashlib.sha256(payload.encode("utf-8")).hexdigest())
    return tuple(hashes)


def d4_map(a: Any) -> dict[str, np.ndarray]:
    """All eight named D4 actions, retaining names even when values coincide."""
    value = arr(a)
    return {
        "id": value.copy(),
        "r90": np.rot90(value, 1).copy(),
        "r180": np.rot90(value, 2).copy(),
        "r270": np.rot90(value, 3).copy(),
        "fh": np.fliplr(value).copy(),
        "fv": np.flipud(value).copy(),
        "t": value.T.copy(),
        "at": np.rot90(value.T, 2).copy(),
    }
