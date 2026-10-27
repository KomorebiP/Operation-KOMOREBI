#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Bayesian PR-LASM ARC2 Entry.

The solver retains each ARC grid in exact spatial, color, Fourier, Haar,
polyphase, and object-relational atlases. Typed base, projector, structural,
and residual-refinement programs form a finite proposal portfolio. A calibrated
Bayesian posterior combines exact demonstration evidence, family and route
reliability, atlas and resolution compatibility, predictive uncertainty, and
program complexity. Programs producing the same test grid share posterior
mass, and two distinct posterior-supported attempts are emitted when possible.

The runtime is offline and uses only Python's standard library and NumPy.
Exact verification always uses array equality, including output dimensions.

Kaggle usage:
    python arc2_entry.py --data-dir /kaggle/input --split test \
        --output /kaggle/working/submission.json --time-limit 8

Local usage:
    python arc2_entry.py --self-test
    python arc2_entry.py --input /path/to/arc-agi_test_challenges.json \
        --output submission.json
"""

from __future__ import annotations

import argparse
import csv
import html
import itertools
import glob
import json
import os
import random
import sys
import time
import tempfile
from collections import Counter, defaultdict, deque
from dataclasses import dataclass
from fractions import Fraction
from pathlib import Path
from typing import Callable, Dict, Iterable, List, Optional, Sequence, Tuple

import numpy as np

try:
    from .lasm_bayesian import (
        BayesianProjectorResolvedLargeSignalModel,
        LASMCalibration,
        load_calibration,
    )
except ImportError:  # standalone Kaggle runtime
    from lasm_bayesian import (
        BayesianProjectorResolvedLargeSignalModel,
        LASMCalibration,
        load_calibration,
    )

Grid = List[List[int]]
Array = np.ndarray

SOLVER_NAME = "PR-LASM ARC2 Bayesian Entry"
SOLVER_VERSION = "0.4.0"
AUTHOR = "Komorebi P."

RNG_SEED = 20260615
random.seed(RNG_SEED)
np.random.seed(RNG_SEED)

MAX_SIDE = 30
MAX_CANDIDATE_PROGRAMS = 1200
TOP_PROGRAMS_TO_APPLY = 80
DEFAULT_TIME_LIMIT_PER_TASK = 8.0


def as_array(grid: Grid | Array) -> Array:
    a = np.asarray(grid, dtype=np.int16)
    if a.ndim != 2:
        return np.zeros((1, 1), dtype=np.int16)
    return a


def grid_to_list(a: Array) -> Grid:
    a = sanitize_grid(a)
    return [[int(x) for x in row] for row in a.tolist()]


def sanitize_grid(a: Array) -> Array:
    a = np.asarray(a, dtype=np.int16)
    if a.ndim != 2 or a.size == 0:
        return np.zeros((1, 1), dtype=np.int16)
    h, w = a.shape
    h = int(max(1, min(MAX_SIDE, h)))
    w = int(max(1, min(MAX_SIDE, w)))
    a = a[:h, :w].copy()
    a = np.where((0 <= a) & (a <= 9), a, 0).astype(np.int16)
    return a


def canonical(a: Array) -> str:
    a = sanitize_grid(a)
    return json.dumps(grid_to_list(a), separators=(",", ":"))


def infer_bg(g: Array) -> int:
    vals, counts = np.unique(g, return_counts=True)
    if 0 in vals:
        return 0
    return int(vals[int(np.argmax(counts))])


def grid_error(a: Array, b: Array) -> int:
    a = sanitize_grid(a)
    b = sanitize_grid(b)
    if a.shape == b.shape:
        return int(np.sum(a != b))
    return 1000 + 40 * abs(a.shape[0] - b.shape[0]) + 40 * abs(a.shape[1] - b.shape[1]) + abs(a.size - b.size)


def exact(a: Array, b: Array) -> bool:
    a = sanitize_grid(a)
    b = sanitize_grid(b)
    return a.shape == b.shape and bool(np.array_equal(a, b))


def majority_color(g: Array) -> int:
    vals, counts = np.unique(g, return_counts=True)
    return int(vals[int(np.argmax(counts))])


def non_bg_colors(g: Array, bg: Optional[int] = None) -> List[int]:
    if bg is None:
        bg = infer_bg(g)
    return [int(c) for c in np.unique(g) if int(c) != int(bg)]


def rare_color(g: Array, bg: Optional[int] = None) -> int:
    if bg is None:
        bg = infer_bg(g)
    vals, counts = np.unique(g, return_counts=True)
    pairs = [(int(v), int(c)) for v, c in zip(vals, counts) if int(v) != int(bg)]
    if not pairs:
        return int(bg)
    pairs.sort(key=lambda p: (p[1], p[0]))
    return pairs[0][0]


def marker_color(g: Array, bg: Optional[int] = None) -> int:
    if bg is None:
        bg = infer_bg(g)
    vals, counts = np.unique(g, return_counts=True)
    singles = [int(v) for v, c in zip(vals, counts) if int(v) != bg and int(c) == 1]
    if singles:
        return singles[-1]
    return rare_color(g, bg)


def bbox_from_mask(mask: Array) -> Optional[Tuple[int, int, int, int]]:
    coords = np.argwhere(mask)
    if coords.size == 0:
        return None
    r0, c0 = coords.min(axis=0)
    r1, c1 = coords.max(axis=0)
    return int(r0), int(c0), int(r1), int(c1)


def crop_bbox_non_bg(g: Array, bg: Optional[int] = None) -> Array:
    if bg is None:
        bg = infer_bg(g)
    bb = bbox_from_mask(g != bg)
    if bb is None:
        return g.copy()
    r0, c0, r1, c1 = bb
    return g[r0 : r1 + 1, c0 : c1 + 1].copy()


@dataclass
class Obj:
    color: int
    cells: List[Tuple[int, int]]
    bbox: Tuple[int, int, int, int]

    @property
    def size(self) -> int:
        return len(self.cells)

    @property
    def height(self) -> int:
        return self.bbox[2] - self.bbox[0] + 1

    @property
    def width(self) -> int:
        return self.bbox[3] - self.bbox[1] + 1



def components(g: Array, bg: Optional[int] = None, exclude: Optional[set[int]] = None) -> List[Obj]:
    g = sanitize_grid(g)
    h, w = g.shape
    if bg is None:
        bg = infer_bg(g)
    if exclude is None:
        exclude = {int(bg)}
    else:
        exclude = set(exclude) | {int(bg)}
    seen = np.zeros((h, w), dtype=bool)
    out: List[Obj] = []
    for r in range(h):
        for c in range(w):
            col = int(g[r, c])
            if seen[r, c] or col in exclude:
                continue
            q = deque([(r, c)])
            seen[r, c] = True
            cells: List[Tuple[int, int]] = []
            while q:
                x, y = q.popleft()
                cells.append((x, y))
                for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                    nx, ny = x + dx, y + dy
                    if 0 <= nx < h and 0 <= ny < w and not seen[nx, ny] and int(g[nx, ny]) == col:
                        seen[nx, ny] = True
                        q.append((nx, ny))
            rs = [x for x, _ in cells]
            cs = [y for _, y in cells]
            out.append(Obj(col, cells, (min(rs), min(cs), max(rs), max(cs))))
    return out


def select_obj(g: Array, selector: str, bg: Optional[int] = None) -> Optional[Obj]:
    objs = components(g, bg=bg)
    if not objs:
        return None
    if selector == "largest":
        return max(objs, key=lambda o: (o.size, -o.bbox[0], -o.bbox[1], -o.color))
    if selector == "smallest":
        return min(objs, key=lambda o: (o.size, o.bbox[0], o.bbox[1], o.color))
    if selector == "leftmost":
        return min(objs, key=lambda o: (o.bbox[1], o.bbox[0], o.size, o.color))
    if selector == "rightmost":
        return max(objs, key=lambda o: (o.bbox[3], -o.bbox[0], o.size, -o.color))
    if selector == "topmost":
        return min(objs, key=lambda o: (o.bbox[0], o.bbox[1], o.size, o.color))
    if selector == "bottommost":
        return max(objs, key=lambda o: (o.bbox[2], -o.bbox[1], o.size, -o.color))
    if selector == "rarest_color":
        rc = rare_color(g, bg)
        candidates = [o for o in objs if o.color == rc]
        return max(candidates, key=lambda o: o.size) if candidates else None
    if selector == "marker_color":
        mc = marker_color(g, bg)
        candidates = [o for o in objs if o.color == mc]
        return max(candidates, key=lambda o: o.size) if candidates else None
    return None


def clear_object(out: Array, obj: Obj, bg: int) -> None:
    for r, c in obj.cells:
        out[r, c] = bg


def paste_object(out: Array, obj: Obj, top: int, left: int, color: Optional[int] = None) -> None:
    r0, c0, _, _ = obj.bbox
    col = obj.color if color is None else int(color)
    for r, c in obj.cells:
        nr, nc = top + (r - r0), left + (c - c0)
        if 0 <= nr < out.shape[0] and 0 <= nc < out.shape[1]:
            out[nr, nc] = col


def corner_position(g: Array, obj: Obj, corner: str) -> Tuple[int, int]:
    h, w = g.shape
    oh, ow = obj.height, obj.width
    if corner == "tl":
        return 0, 0
    if corner == "tr":
        return 0, w - ow
    if corner == "bl":
        return h - oh, 0
    if corner == "br":
        return h - oh, w - ow
    if corner == "center":
        return max(0, (h - oh) // 2), max(0, (w - ow) // 2)
    return 0, 0


@dataclass(frozen=True)
class Op:
    name: str
    fn: Callable[[Array], Array]
    cost: int
    kind: str

    def __call__(self, g: Array) -> Array:
        try:
            return sanitize_grid(self.fn(sanitize_grid(g)))
        except Exception:
            return sanitize_grid(g)



def op_geo(name: str, fn: Callable[[Array], Array]) -> Op:
    return Op(name, lambda g: fn(g).copy(), 2, "geo")


def op_crop_bbox() -> Op:
    return Op("crop_bbox", lambda g: crop_bbox_non_bg(g), 3, "crop")


def op_crop_object(selector: str) -> Op:
    def fn(g: Array) -> Array:
        bg = infer_bg(g)
        obj = select_obj(g, selector, bg)
        if obj is None:
            return g.copy()
        r0, c0, r1, c1 = obj.bbox
        return g[r0 : r1 + 1, c0 : c1 + 1].copy()

    return Op(f"crop_{selector}", fn, 4, "crop_object")


def op_fill_holes() -> Op:
    def fn(g: Array) -> Array:
        bg = infer_bg(g)
        out = g.copy()
        for obj in components(g, bg=bg):
            col = obj.color
            r0, c0, r1, c1 = obj.bbox
            if r1 - r0 < 2 or c1 - c0 < 2:
                continue
            ok = True
            for c in range(c0, c1 + 1):
                ok &= int(g[r0, c]) == col and int(g[r1, c]) == col
            for r in range(r0, r1 + 1):
                ok &= int(g[r, c0]) == col and int(g[r, c1]) == col
            if ok:
                out[r0 : r1 + 1, c0 : c1 + 1] = col
        return out

    return Op("fill_holes", fn, 4, "fill")


def op_extend_lines(axis: str) -> Op:
    def fn(g: Array) -> Array:
        bg = infer_bg(g)
        out = g.copy()
        for obj in components(g, bg=bg):
            col = obj.color
            r0, c0, r1, c1 = obj.bbox
            if axis in ("h", "both") and r0 == r1 and c1 - c0 + 1 >= 2:
                out[r0, :] = col
            if axis in ("v", "both") and c0 == c1 and r1 - r0 + 1 >= 2:
                out[:, c0] = col
        return out

    return Op(f"extend_lines_{axis}", fn, 4, "extend")


def op_sym(direction: str) -> Op:
    def fn(g: Array) -> Array:
        bg = infer_bg(g)
        out = g.copy()
        h, w = g.shape
        if direction == "lr":
            for r in range(h):
                for c in range(w // 2):
                    if int(g[r, c]) != bg:
                        out[r, w - 1 - c] = g[r, c]
        elif direction == "rl":
            for r in range(h):
                for c in range((w + 1) // 2, w):
                    if int(g[r, c]) != bg:
                        out[r, w - 1 - c] = g[r, c]
        elif direction == "tb":
            for r in range(h // 2):
                for c in range(w):
                    if int(g[r, c]) != bg:
                        out[h - 1 - r, c] = g[r, c]
        elif direction == "bt":
            for r in range((h + 1) // 2, h):
                for c in range(w):
                    if int(g[r, c]) != bg:
                        out[h - 1 - r, c] = g[r, c]
        return out

    return Op(f"sym_{direction}", fn, 4, "sym")


def op_recolor(selector: str, target: str) -> Op:
    def fn(g: Array) -> Array:
        bg = infer_bg(g)
        out = g.copy()
        obj = select_obj(g, selector, bg)
        if obj is None:
            return out
        if target == "marker":
            col = marker_color(g, bg)
        elif target == "bg":
            col = bg
        elif target == "majority":
            col = majority_color(g)
        elif target == "rare":
            col = rare_color(g, bg)
        else:
            col = int(target)
        for r, c in obj.cells:
            out[r, c] = col
        return out

    return Op(f"recolor_{selector}_to_{target}", fn, 4, "recolor")


def op_erase(selector: str) -> Op:
    return op_recolor(selector, "bg")


def op_move(selector: str, corner: str) -> Op:
    def fn(g: Array) -> Array:
        bg = infer_bg(g)
        out = g.copy()
        obj = select_obj(g, selector, bg)
        if obj is None:
            return out
        clear_object(out, obj, bg)
        paste_object(out, obj, *corner_position(g, obj, corner))
        return out

    return Op(f"move_{selector}_{corner}", fn, 5, "move")


def op_copy(selector: str, corner: str) -> Op:
    def fn(g: Array) -> Array:
        bg = infer_bg(g)
        out = g.copy()
        obj = select_obj(g, selector, bg)
        if obj is None:
            return out
        paste_object(out, obj, *corner_position(g, obj, corner))
        return out

    return Op(f"copy_{selector}_{corner}", fn, 5, "copy")


def op_remove_uniform_border() -> Op:
    def fn(g: Array) -> Array:
        out = g.copy()
        changed = True
        while changed and out.shape[0] > 1 and out.shape[1] > 1:
            changed = False
            h, w = out.shape
            top = out[0, :]
            bottom = out[-1, :]
            left = out[:, 0]
            right = out[:, -1]
            edges = [top, bottom, left, right]
            colors = [int(e[0]) if np.all(e == e[0]) else None for e in edges]
            counts = Counter(c for c in colors if c is not None)
            if not counts:
                break
            col, _ = counts.most_common(1)[0]
            r0, r1, c0, c1 = 0, h, 0, w
            if colors[0] == col:
                r0 += 1
                changed = True
            if colors[1] == col:
                r1 -= 1
                changed = True
            if colors[2] == col:
                c0 += 1
                changed = True
            if colors[3] == col:
                c1 -= 1
                changed = True
            if changed and r0 < r1 and c0 < c1:
                out = out[r0:r1, c0:c1].copy()
            else:
                break
        return out

    return Op("remove_uniform_border", fn, 4, "border")


def op_upscale(k: int) -> Op:
    return Op(f"upscale_{k}", lambda g, k=k: np.repeat(np.repeat(g, k, axis=0), k, axis=1), 4 + k, "scale")


def op_downscale(k: int, mode: str) -> Op:
    def fn(g: Array) -> Array:
        h, w = g.shape
        if h % k != 0 or w % k != 0:
            return g.copy()
        blocks = g.reshape(h // k, k, w // k, k).transpose(0, 2, 1, 3)
        out = np.zeros((h // k, w // k), dtype=np.int16)
        for i in range(h // k):
            for j in range(w // k):
                vals = blocks[i, j].ravel()
                if mode == "top_left":
                    out[i, j] = vals[0]
                else:
                    vc = Counter(int(x) for x in vals)
                    out[i, j] = vc.most_common(1)[0][0]
        return out

    return Op(f"downscale_{k}_{mode}", fn, 5 + k, "scale")


def build_primitives() -> List[Op]:
    prims: List[Op] = []
    prims += [
        op_geo("rot90", lambda g: np.rot90(g, 1)),
        op_geo("rot180", lambda g: np.rot90(g, 2)),
        op_geo("rot270", lambda g: np.rot90(g, 3)),
        op_geo("flip_h", lambda g: np.fliplr(g)),
        op_geo("flip_v", lambda g: np.flipud(g)),
        op_geo("transpose", lambda g: g.T),
        op_geo("anti_transpose", lambda g: np.fliplr(np.flipud(g).T)),
    ]
    prims += [op_crop_bbox(), op_remove_uniform_border(), op_fill_holes()]
    prims += [op_extend_lines("h"), op_extend_lines("v"), op_extend_lines("both")]
    prims += [op_sym(d) for d in ["lr", "rl", "tb", "bt"]]
    prims += [op_upscale(2), op_upscale(3), op_downscale(2, "majority"), op_downscale(3, "majority")]
    selectors = ["largest", "smallest", "leftmost", "rightmost", "topmost", "bottommost", "rarest_color"]
    corners = ["tl", "tr", "bl", "br", "center"]
    for s in selectors:
        prims += [op_crop_object(s), op_erase(s)]
        for target in ["marker", "rare", "majority"]:
            prims.append(op_recolor(s, target))
    for s in ["largest", "smallest", "leftmost", "topmost"]:
        for c in corners:
            prims.append(op_move(s, c))
            prims.append(op_copy(s, c))
    # Deduplicate by name.
    out = []
    seen = set()
    for p in prims:
        if p.name not in seen:
            out.append(p)
            seen.add(p.name)
    return out


PRIMS = build_primitives()


def program_name(program: Tuple[Op, ...]) -> str:
    return "identity" if not program else " ; ".join(op.name for op in program)


def program_cost(program: Tuple[Op, ...]) -> int:
    return sum(op.cost for op in program) + len(program)


def apply_program(g: Array, program: Tuple[Op, ...]) -> Array:
    out = sanitize_grid(g)
    for op in program:
        out = op(out)
    return sanitize_grid(out)


def valid_program(program: Tuple[Op, ...]) -> bool:
    names = [p.name for p in program]
    kinds = [p.kind for p in program]
    for a, b, ka in zip(names, names[1:], kinds):
        if a == b and ka in {"geo", "crop", "fill", "sym", "border", "scale"}:
            return False
    # Avoid crop after crop variants too often; it is usually redundant.
    for ka, kb in zip(kinds, kinds[1:]):
        if ka.startswith("crop") and kb.startswith("crop"):
            return False
    return True


def generate_programs(train: List[Tuple[Array, Array]], max_depth: int = 2) -> List[Tuple[Op, ...]]:
    # Use output shapes to decide whether expensive shape-changing ops are plausible.
    shape_changes = any(x.shape != y.shape for x, y in train)
    if shape_changes:
        active = PRIMS
    else:
        active = [p for p in PRIMS if p.kind not in {"scale"} or p.name.startswith("downscale") is False]
    programs: List[Tuple[Op, ...]] = [tuple()]
    for d in range(1, max_depth + 1):
        for p in itertools_product_limited(active, d):
            if valid_program(p):
                programs.append(p)
            if len(programs) >= MAX_CANDIDATE_PROGRAMS:
                break
        if len(programs) >= MAX_CANDIDATE_PROGRAMS:
            break
    programs.sort(key=lambda p: (program_cost(p), len(p), program_name(p)))
    return programs


def itertools_product_limited(items: Sequence[Op], depth: int) -> Iterable[Tuple[Op, ...]]:
    # Small custom wrapper so we can change ordering later. Lower-cost primitives first.
    items = sorted(items, key=lambda op: (op.cost, op.name))
    return __import__("itertools").product(items, repeat=depth)


@dataclass
class RuleCandidate:
    name: str
    grids: List[Array]
    train_error: int
    complexity: int
    family: str
    train_grids: Tuple[Array, ...] = ()
    metadata: Optional[Dict[str, object]] = None

    @property
    def score(self) -> float:
        return float(self.train_error) + 0.01 * float(self.complexity)


def candidate_from_function(
    name: str,
    fn: Callable[[Array], Array],
    train: List[Tuple[Array, Array]],
    tests: List[Array],
    complexity: int,
    family: str,
    *,
    metadata: Optional[Dict[str, object]] = None,
) -> RuleCandidate:
    train_grids = tuple(sanitize_grid(fn(x)) for x, _ in train)
    error = sum(grid_error(prediction, target) for prediction, (_, target) in zip(train_grids, train))
    return RuleCandidate(
        name=name,
        grids=[sanitize_grid(fn(test)) for test in tests],
        train_error=int(error),
        complexity=int(complexity),
        family=family,
        train_grids=train_grids,
        metadata=metadata,
    )


def train_error_for_func(train: List[Tuple[Array, Array]], fn: Callable[[Array], Array]) -> int:
    err = 0
    for x, y in train:
        err += grid_error(fn(x), y)
    return int(err)


def fit_color_map(train: List[Tuple[Array, Array]], pre: Callable[[Array], Array], name: str) -> Optional[Tuple[str, Callable[[Array], Array], int]]:
    mapping: Dict[int, int] = {}
    ok = True
    for x, y in train:
        tx = sanitize_grid(pre(x))
        if tx.shape != y.shape:
            ok = False
            break
        for a, b in zip(tx.ravel(), y.ravel()):
            a, b = int(a), int(b)
            if a in mapping and mapping[a] != b:
                ok = False
                break
            mapping[a] = b
        if not ok:
            break
    if not ok or not mapping:
        return None

    def fn(g: Array) -> Array:
        tx = sanitize_grid(pre(g))
        out = tx.copy()
        for src, dst in mapping.items():
            out[tx == src] = dst
        return out

    return f"color_map_after_{name}", fn, len(mapping) + 3


def learned_transform_rules(train: List[Tuple[Array, Array]], tests: List[Array]) -> List[RuleCandidate]:
    out: List[RuleCandidate] = []
    transforms: List[Tuple[str, Callable[[Array], Array], int]] = [
        ("identity", lambda g: g.copy(), 1),
        ("rot90", lambda g: np.rot90(g, 1), 2),
        ("rot180", lambda g: np.rot90(g, 2), 2),
        ("rot270", lambda g: np.rot90(g, 3), 2),
        ("flip_h", lambda g: np.fliplr(g), 2),
        ("flip_v", lambda g: np.flipud(g), 2),
        ("transpose", lambda g: g.T, 2),
        ("anti_transpose", lambda g: np.fliplr(np.flipud(g).T), 2),
        ("crop_bbox", lambda g: crop_bbox_non_bg(g), 3),
        ("remove_uniform_border", op_remove_uniform_border(), 4),
        ("fill_holes", op_fill_holes(), 4),
    ]

    # Exact simple transforms.
    for nm, fn, comp in transforms:
        err = train_error_for_func(train, fn)
        if err <= 5:
            out.append(candidate_from_function(nm, fn, train, tests, comp, "learned_transform"))

    # Transform + consistent color map.
    for nm, fn, comp in transforms:
        fit = fit_color_map(train, fn, nm)
        if fit is None:
            continue
        rname, rfn, extra = fit
        err = train_error_for_func(train, rfn)
        if err <= 2:
            out.append(candidate_from_function(rname, rfn, train, tests, comp + extra, "color_map"))

    # Upscale/tile rules.
    for k in [2, 3, 4]:
        fn = lambda g, k=k: np.repeat(np.repeat(g, k, axis=0), k, axis=1)
        err = train_error_for_func(train, fn)
        if err == 0:
            out.append(candidate_from_function(f"upscale_{k}", fn, train, tests, 5 + k, "scale"))
        fit = fit_color_map(train, fn, f"upscale_{k}")
        if fit:
            rname, rfn, extra = fit
            err = train_error_for_func(train, rfn)
            if err == 0:
                out.append(candidate_from_function(rname, rfn, train, tests, 8 + extra, "scale_color"))

    for k in [2, 3, 4]:
        for mode in ["top_left", "majority"]:
            op = op_downscale(k, mode)
            fn = op.fn
            err = train_error_for_func(train, fn)
            if err == 0:
                out.append(candidate_from_function(f"downscale_{k}_{mode}", fn, train, tests, 6 + k, "scale"))

    # Constant-shape blank/output-size fallback learned from training output dimensions.
    shapes = [tuple(y.shape) for _, y in train]
    if shapes:
        shape = Counter(shapes).most_common(1)[0][0]
        bg = majority_color(train[-1][1])
        grids = [np.full(shape, bg, dtype=np.int16) for _ in tests]
        err = sum(grid_error(np.full(shape, bg, dtype=np.int16), y) for _, y in train)
        train_grids = tuple(np.full(shape, bg, dtype=np.int16) for _ in train)
        out.append(RuleCandidate("blank_common_output_shape", grids, err, 20, "fallback", train_grids=train_grids))

    # Last train output as pattern fallback. Bad but occasionally useful as second attempt.
    last_y = train[-1][1]
    out.append(candidate_from_function("last_train_output", lambda g: last_y.copy(), train, tests, 50, "fallback"))
    return out


def synthesize_program_rules(train: List[Tuple[Array, Array]], tests: List[Array], start_time: float, time_limit: float) -> List[RuleCandidate]:
    out: List[RuleCandidate] = []
    max_depth = 2
    # For tiny grids, try a little depth-3 search with a stricter program cap.
    if max(max(x.shape) for x, _ in train) <= 12 and max(max(y.shape) for _, y in train) <= 12:
        max_depth = 2  # keep Kaggle-safe; switch to 3 manually if you have compute.
    programs = generate_programs(train, max_depth=max_depth)
    best_cut = 10**9
    scored: List[Tuple[float, int, int, Tuple[Op, ...]]] = []
    for idx, program in enumerate(programs):
        if time.time() - start_time > time_limit * 0.7:
            break
        err = 0
        for x, y in train:
            pred = apply_program(x, program)
            err += grid_error(pred, y)
            if err > min(best_cut + 20, 2000):
                break
        comp = program_cost(program)
        score = err + 0.01 * comp
        if err < best_cut:
            best_cut = err
        if err <= max(3, best_cut + 8) or len(scored) < TOP_PROGRAMS_TO_APPLY:
            scored.append((score, err, comp, program))
    scored.sort(key=lambda z: (z[0], z[2], program_name(z[3])))
    for score, err, comp, program in scored[:TOP_PROGRAMS_TO_APPLY]:
        grids = [apply_program(t, program) for t in tests]
        out.append(
            RuleCandidate(
                f"program:{program_name(program)}",
                grids,
                err,
                comp,
                "program",
                train_grids=tuple(apply_program(x, program) for x, _ in train),
                metadata={"program": program_name(program)},
            )
        )
    return out


def object_color_frequency_rules(train: List[Tuple[Array, Array]], tests: List[Array]) -> List[RuleCandidate]:
    out: List[RuleCandidate] = []
    # Rules of the form: same shape, replace one input color by one output color.
    colors = list(range(10))
    for src in colors:
        for dst in colors:
            if src == dst:
                continue
            def fn(g: Array, src=src, dst=dst) -> Array:
                z = g.copy()
                z[z == src] = dst
                return z
            err = train_error_for_func(train, fn)
            if err == 0:
                out.append(candidate_from_function(f"replace_color_{src}_to_{dst}", fn, train, tests, 5, "color_replace"))
    # Fill all non-background cells with a color inferred from rare marker/output.
    for target in ["rare", "marker", "majority"]:
        def fn(g: Array, target=target) -> Array:
            bg = infer_bg(g)
            if target == "rare":
                col = rare_color(g, bg)
            elif target == "marker":
                col = marker_color(g, bg)
            else:
                col = majority_color(g)
            z = g.copy()
            z[g != bg] = col
            return z
        err = train_error_for_func(train, fn)
        if err == 0:
            out.append(candidate_from_function(f"recolor_all_nonbg_to_{target}", fn, train, tests, 6, "recolor_all"))
    return out



# ---------------- projector-exact proposal channel ----------------

def _try_exact_rule(
    out: List[RuleCandidate],
    train: List[Tuple[Array, Array]],
    tests: List[Array],
    name: str,
    fn: Callable[[Array], Array],
    complexity: int,
    family: str,
) -> None:
    """Append a rule only when it reproduces every demonstration exactly."""
    try:
        predictions = [sanitize_grid(fn(x)) for x, _ in train]
        if all(exact(pred, y) for pred, (_, y) in zip(predictions, train)):
            out.append(
                RuleCandidate(
                    name=name,
                    grids=[sanitize_grid(fn(t)) for t in tests],
                    train_error=0,
                    complexity=complexity,
                    family=family,
                    train_grids=tuple(predictions),
                )
            )
    except Exception:
        return


def cell_gravity(g: Array, direction: str) -> Array:
    g = sanitize_grid(g)
    bg = infer_bg(g)
    out = np.full_like(g, bg)
    if direction in ("down", "up"):
        for c in range(g.shape[1]):
            values = g[:, c]
            fg = values[values != bg]
            if len(fg):
                if direction == "down":
                    out[-len(fg):, c] = fg
                else:
                    out[:len(fg), c] = fg
    elif direction in ("right", "left"):
        for r in range(g.shape[0]):
            values = g[r]
            fg = values[values != bg]
            if len(fg):
                if direction == "right":
                    out[r, -len(fg):] = fg
                else:
                    out[r, :len(fg)] = fg
    else:
        raise ValueError(direction)
    return out


def object_gravity_exact(g: Array, direction: str) -> Array:
    """Move monochrome connected components rigidly until blocked."""
    g = sanitize_grid(g)
    bg = infer_bg(g)
    objs = components(g, bg=bg)
    out = np.full_like(g, bg)
    occupied = np.zeros(g.shape, dtype=bool)
    if direction == "down":
        objs = sorted(objs, key=lambda o: o.bbox[2], reverse=True)
        step = (1, 0)
    elif direction == "up":
        objs = sorted(objs, key=lambda o: o.bbox[0])
        step = (-1, 0)
    elif direction == "right":
        objs = sorted(objs, key=lambda o: o.bbox[3], reverse=True)
        step = (0, 1)
    elif direction == "left":
        objs = sorted(objs, key=lambda o: o.bbox[1])
        step = (0, -1)
    else:
        raise ValueError(direction)
    h, w = g.shape
    for obj in objs:
        cells = np.asarray(obj.cells, dtype=int)
        dr = dc = 0
        while True:
            trial = cells + np.asarray([dr + step[0], dc + step[1]])
            if (
                np.any(trial[:, 0] < 0)
                or np.any(trial[:, 0] >= h)
                or np.any(trial[:, 1] < 0)
                or np.any(trial[:, 1] >= w)
                or any(occupied[int(r), int(c)] for r, c in trial)
            ):
                break
            dr += step[0]
            dc += step[1]
        for r, c in cells + np.asarray([dr, dc]):
            out[int(r), int(c)] = int(obj.color)
            occupied[int(r), int(c)] = True
    return out


def split_equal_panels(g: Array) -> Optional[Tuple[Array, Array]]:
    g = sanitize_grid(g)
    h, w = g.shape
    for c in range(1, w - 1):
        line = g[:, c]
        if np.all(line == line[0]):
            left, right = g[:, :c], g[:, c + 1:]
            if left.shape == right.shape:
                return left.copy(), right.copy()
    for r in range(1, h - 1):
        line = g[r, :]
        if np.all(line == line[0]):
            top, bottom = g[:r, :], g[r + 1:, :]
            if top.shape == bottom.shape:
                return top.copy(), bottom.copy()
    return None


def panel_boolean_exact(g: Array, operation: str, output_color: int, background: int = 0) -> Array:
    panels = split_equal_panels(g)
    if panels is None:
        raise ValueError("no equal panels")
    a0, b0 = panels
    a, b = a0 != background, b0 != background
    masks = {
        "intersection": a & b,
        "union": a | b,
        "xor": a ^ b,
        "left_minus_right": a & ~b,
        "right_minus_left": b & ~a,
    }
    return np.where(masks[operation], int(output_color), int(background)).astype(np.int16)


def kronecker_self_mask_exact(g: Array) -> Array:
    g = sanitize_grid(g)
    bg = infer_bg(g)
    return sanitize_grid(np.kron((g != bg).astype(np.int16), g))


def diagonal_fill_from_seed(g: Array, period: int, background: int = 0) -> Array:
    g = sanitize_grid(g)
    phase_values: List[List[int]] = [[] for _ in range(period)]
    for r, c in np.argwhere(g != background):
        phase_values[(int(r) + int(c)) % period].append(int(g[r, c]))
    sequence: List[int] = []
    for values in phase_values:
        if not values or len(set(values)) != 1:
            raise ValueError("phase seed incomplete or inconsistent")
        sequence.append(values[0])
    rr, cc = np.indices(g.shape)
    return np.asarray(sequence, dtype=np.int16)[(rr + cc) % period]


def row_marker_recode_exact(g: Array, marker: int, position_to_color: Dict[int, int]) -> Array:
    g = sanitize_grid(g)
    out = np.zeros_like(g)
    for r in range(g.shape[0]):
        positions = np.flatnonzero(g[r] == marker)
        if positions.size != 1 or int(positions[0]) not in position_to_color:
            raise ValueError("row marker contract failed")
        out[r, :] = int(position_to_color[int(positions[0])])
    return out


def vertical_bars(g: Array) -> List[Obj]:
    bg = infer_bg(g)
    return [o for o in components(g, bg=bg) if o.width == 1]


def recolor_vertical_bars(g: Array, rank_colors: Tuple[int, ...], longest_first: bool) -> Array:
    out = sanitize_grid(g).copy()
    bars = sorted(vertical_bars(out), key=lambda o: (o.size, -o.bbox[1]), reverse=longest_first)
    if len(bars) != len(rank_colors):
        raise ValueError("rank/color count mismatch")
    for rank, obj in enumerate(bars):
        for r, c in obj.cells:
            out[r, c] = int(rank_colors[rank])
    return out


def projector_exact_rules(train: List[Tuple[Array, Array]], tests: List[Array]) -> List[RuleCandidate]:
    """Exact, input-dependent proposals recovered from the projector ARC release."""
    out: List[RuleCandidate] = []
    same_shape = all(x.shape == y.shape for x, y in train)

    if same_shape:
        for direction in ("down", "up", "left", "right"):
            _try_exact_rule(out, train, tests, f"cell_gravity_{direction}", lambda g, d=direction: cell_gravity(g, d), 5, "projector_gravity")
            _try_exact_rule(out, train, tests, f"object_gravity_{direction}", lambda g, d=direction: object_gravity_exact(g, d), 7, "projector_object_gravity")

    # Grid multiplication and tiling inferred from output dimensions. Avoid
    # allocating a Kronecker product unless every demonstration has its exact
    # expected shape.
    if all(y.shape == (x.shape[0] * x.shape[0], x.shape[1] * x.shape[1]) for x, y in train):
        _try_exact_rule(out, train, tests, "kronecker_self_mask", kronecker_self_mask_exact, 8, "projector_kronecker")
    factors: set[Tuple[int, int]] = set()
    scale_valid = True
    for x, y in train:
        if y.shape[0] % x.shape[0] or y.shape[1] % x.shape[1]:
            scale_valid = False
            break
        factors.add((y.shape[0] // x.shape[0], y.shape[1] // x.shape[1]))
    if scale_valid and len(factors) == 1:
        rr, cc = next(iter(factors))
        if rr > 0 and cc > 0 and (rr, cc) != (1, 1):
            _try_exact_rule(out, train, tests, f"tile_{rr}x{cc}", lambda g, a=rr, b=cc: np.tile(g, (a, b)), 6, "projector_tile")

    output_colors = sorted({int(v) for _, y in train for v in np.unique(y) if int(v) != 0})
    candidate_colors = output_colors if output_colors else list(range(1, 10))
    for operation in ("intersection", "union", "xor", "left_minus_right", "right_minus_left"):
        for color in candidate_colors[:9]:
            _try_exact_rule(
                out, train, tests,
                f"panel_{operation}_{color}",
                lambda g, op=operation, col=color: panel_boolean_exact(g, op, col),
                7,
                "projector_panel",
            )

    # Learn row-marker position semantics from all demonstrations.
    input_colors = sorted({int(v) for x, _ in train for v in np.unique(x) if int(v) != 0}) if same_shape else []
    for marker in input_colors:
        mapping: Dict[int, int] = {}
        valid = True
        for x, y in train:
            if x.shape != y.shape:
                valid = False
                break
            for r in range(x.shape[0]):
                pos = np.flatnonzero(x[r] == marker)
                if pos.size != 1 or len(set(int(v) for v in y[r])) != 1:
                    valid = False
                    break
                p, color = int(pos[0]), int(y[r, 0])
                if p in mapping and mapping[p] != color:
                    valid = False
                    break
                mapping[p] = color
            if not valid:
                break
        if valid and mapping:
            _try_exact_rule(
                out, train, tests,
                f"row_marker_{marker}",
                lambda g, m=marker, mp=dict(mapping): row_marker_recode_exact(g, m, mp),
                6 + len(mapping),
                "projector_row_marker",
            )

    # Diagonal polyphase completion. Limit the period to keep the rule auditable.
    unique_counts = {len(np.unique(y)) for _, y in train}
    if same_shape and len(unique_counts) == 1:
        period = next(iter(unique_counts))
        if 2 <= period <= 6:
            _try_exact_rule(
                out, train, tests,
                f"diagonal_seed_period_{period}",
                lambda g, p=period: diagonal_fill_from_seed(g, p),
                7 + period,
                "projector_polyphase",
            )

    # Vertical-bar rank rule. Infer the rank palette directly rather than
    # enumerating permutations, so this channel remains within a hard budget.
    for longest_first in ((True, False) if same_shape else ()):
        inferred: Dict[int, int] = {}
        valid = True
        bar_count: Optional[int] = None
        for x, y in train:
            if x.shape != y.shape:
                valid = False
                break
            bars = sorted(vertical_bars(x), key=lambda o: (o.size, -o.bbox[1]), reverse=longest_first)
            if not bars or (bar_count is not None and len(bars) != bar_count):
                valid = False
                break
            bar_count = len(bars)
            # The transformation must preserve the foreground support.
            if not np.array_equal(x != infer_bg(x), y != infer_bg(y)):
                valid = False
                break
            for rank, obj in enumerate(bars):
                values = {int(y[r, c]) for r, c in obj.cells}
                if len(values) != 1:
                    valid = False
                    break
                color = next(iter(values))
                if rank in inferred and inferred[rank] != color:
                    valid = False
                    break
                inferred[rank] = color
            if not valid:
                break
        if valid and bar_count and len(inferred) == bar_count <= 9:
            order = tuple(inferred[i] for i in range(bar_count))
            _try_exact_rule(
                out, train, tests,
                f"bar_rank_{order}_{'long' if longest_first else 'short'}",
                lambda g, colors=order, lf=longest_first: recolor_vertical_bars(g, colors, lf),
                8 + len(order),
                "projector_bar_rank",
            )
    return out


# ---------------- structural exact proposal channel ----------------

def object_mask_signature(obj: Obj) -> Tuple[Tuple[int, ...], ...]:
    mask = np.zeros((obj.height, obj.width), dtype=np.int8)
    r0, c0, _, _ = obj.bbox
    for r, c in obj.cells:
        mask[r - r0, c - c0] = 1
    return tuple(tuple(int(v) for v in row) for row in mask)


def crop_object_cells(g: Array, obj: Obj) -> Array:
    g = sanitize_grid(g); bg = infer_bg(g)
    r0, c0, r1, c1 = obj.bbox
    crop = g[r0:r1 + 1, c0:c1 + 1].copy()
    keep = np.zeros(crop.shape, dtype=bool)
    for r, c in obj.cells:
        keep[r - r0, c - c0] = True
    return np.where(keep, crop, bg).astype(np.int16)


def select_most_repeated_shape_exact(g: Array) -> Array:
    g = sanitize_grid(g)
    objs = generic_components(g, 8, True)
    if not objs:
        raise ValueError("no objects")
    groups: Dict[Tuple[Tuple[int, ...], ...], List[Obj]] = defaultdict(list)
    for obj in objs:
        groups[object_mask_signature(obj)].append(obj)
    ordered = sorted(groups.values(), key=lambda xs: (len(xs), xs[0].size), reverse=True)
    if not ordered or (len(ordered) > 1 and len(ordered[0]) == len(ordered[1])):
        raise ValueError("most repeated shape is not unique")
    return crop_object_cells(g, ordered[0][0])


def _mask_symmetry(obj: Obj, mode: str) -> bool:
    mask = np.asarray(object_mask_signature(obj), dtype=np.int8)
    if mode == "horizontal": return bool(np.array_equal(mask, np.fliplr(mask)))
    if mode == "vertical": return bool(np.array_equal(mask, np.flipud(mask)))
    if mode == "rot180": return bool(np.array_equal(mask, np.rot90(mask, 2)))
    if mode == "diagonal": return mask.shape[0] == mask.shape[1] and bool(np.array_equal(mask, mask.T))
    raise ValueError(mode)


def select_unique_symmetric_object_exact(g: Array, mode: str) -> Array:
    g = sanitize_grid(g)
    objs = generic_components(g, 8, True)
    matches = [obj for obj in objs if _mask_symmetry(obj, mode)]
    if len(matches) != 1:
        raise ValueError("symmetric object is not unique")
    return crop_object_cells(g, matches[0])


def select_object_by_color_contrast_exact(
    g: Array,
    positive_color: int,
    negative_color: int,
    maximize: bool,
) -> Array:
    g = sanitize_grid(g)
    objs = generic_components(g, 4, False)
    if not objs:
        raise ValueError("no multicolor packets")
    scored: List[Tuple[int, Obj]] = []
    for obj in objs:
        counts = Counter(int(g[r, c]) for r, c in obj.cells)
        score = counts.get(int(positive_color), 0) - counts.get(int(negative_color), 0)
        scored.append((score, obj))
    target = (max if maximize else min)(score for score, _ in scored)
    matches = [obj for score, obj in scored if score == target]
    if len(matches) != 1:
        raise ValueError("color contrast does not select a unique packet")
    return crop_object_cells(g, matches[0])


def anomaly_color_in_patterns_exact(g: Array) -> Array:
    g = sanitize_grid(g)
    candidates: List[int] = []
    for obj in generic_components(g, 4, False):
        counts = Counter(int(g[r, c]) for r, c in obj.cells)
        if obj.size < 4 or len(counts) < 2:
            continue
        ordered = counts.most_common()
        if len(ordered) >= 2 and ordered[-1][1] < ordered[0][1]:
            least_count = ordered[-1][1]
            least = [color for color, count in ordered if count == least_count]
            if len(least) == 1:
                candidates.append(int(least[0]))
    if not candidates or len(set(candidates)) != 1:
        raise ValueError("no unique anomaly color")
    return np.asarray([[candidates[0]]], dtype=np.int16)


def relational_object_rules(train: List[Tuple[Array, Array]], tests: List[Array]) -> List[RuleCandidate]:
    out: List[RuleCandidate] = []
    _try_exact_rule(out, train, tests, "most_repeated_shape", select_most_repeated_shape_exact, 7, "struct_relational_object")
    for mode in ("horizontal", "vertical", "rot180", "diagonal"):
        _try_exact_rule(out, train, tests, f"unique_{mode}_object", lambda g, m=mode: select_unique_symmetric_object_exact(g, m), 7, "struct_relational_object")
    colors = sorted({int(v) for x, _ in train for v in np.unique(x) if int(v) != infer_bg(x)})
    if len(colors) <= 6:
        for positive in colors:
            for negative in colors:
                if positive == negative:
                    continue
                for maximize in (True, False):
                    _try_exact_rule(
                        out,
                        train,
                        tests,
                        f"packet_contrast_{positive}_{negative}_{'max' if maximize else 'min'}",
                        lambda g, p=positive, n=negative, mx=maximize: select_object_by_color_contrast_exact(g, p, n, mx),
                        9,
                        "struct_relational_object",
                    )
    _try_exact_rule(out, train, tests, "anomaly_color_in_patterns", anomaly_color_in_patterns_exact, 6, "struct_relational_color")
    return out



def _foreground_mask(g: Array) -> Array:
    return sanitize_grid(g) != infer_bg(sanitize_grid(g))


def _output_candidate_colors(train: List[Tuple[Array, Array]]) -> List[int]:
    input_colors = {int(v) for x, _ in train for v in np.unique(x)}
    output_colors = {int(v) for _, y in train for v in np.unique(y)}
    added = sorted(output_colors - input_colors)
    nonbg = sorted({int(v) for _, y in train for v in np.unique(y) if int(v) != infer_bg(y)})
    return (added + [c for c in nonbg if c not in added])[:9]


def mirror_concat_exact(g: Array, mode: str) -> Array:
    g = sanitize_grid(g)
    if mode == "right":
        return sanitize_grid(np.concatenate([g, np.fliplr(g)], axis=1))
    if mode == "left":
        return sanitize_grid(np.concatenate([np.fliplr(g), g], axis=1))
    if mode == "down":
        return sanitize_grid(np.concatenate([g, np.flipud(g)], axis=0))
    if mode == "up":
        return sanitize_grid(np.concatenate([np.flipud(g), g], axis=0))
    if mode == "right_seam":
        return sanitize_grid(np.concatenate([g, np.fliplr(g)[:, 1:]], axis=1))
    if mode == "left_seam":
        return sanitize_grid(np.concatenate([np.fliplr(g)[:, :-1], g], axis=1))
    if mode == "down_seam":
        return sanitize_grid(np.concatenate([g, np.flipud(g)[1:, :]], axis=0))
    if mode == "up_seam":
        return sanitize_grid(np.concatenate([np.flipud(g)[:-1, :], g], axis=0))
    raise ValueError(mode)


def complete_reflection_exact(g: Array, mode: str, new_color: Optional[int] = None) -> Array:
    g = sanitize_grid(g)
    bg = infer_bg(g)
    reflected: Optional[Array]
    if mode == "horizontal":
        reflected = np.fliplr(g)
    elif mode == "vertical":
        reflected = np.flipud(g)
    elif mode == "rot180":
        reflected = np.rot90(g, 2)
    elif mode == "diagonal":
        reflected = g.T if g.shape[0] == g.shape[1] else None
    elif mode == "anti_diagonal":
        reflected = np.fliplr(np.flipud(g).T) if g.shape[0] == g.shape[1] else None
    else:
        raise ValueError(mode)
    if reflected is None or reflected.shape != g.shape:
        raise ValueError("incompatible reflection")
    out = g.copy()
    mask = (out == bg) & (reflected != bg)
    out[mask] = reflected[mask] if new_color is None else int(new_color)
    return out


def shift_grid_exact(g: Array, dr: int, dc: int) -> Array:
    g = sanitize_grid(g)
    bg = infer_bg(g)
    out = np.full_like(g, bg)
    h, w = g.shape
    src_r0, src_r1 = max(0, -dr), min(h, h - dr)
    src_c0, src_c1 = max(0, -dc), min(w, w - dc)
    dst_r0, dst_r1 = src_r0 + dr, src_r1 + dr
    dst_c0, dst_c1 = src_c0 + dc, src_c1 + dc
    if src_r0 < src_r1 and src_c0 < src_c1:
        out[dst_r0:dst_r1, dst_c0:dst_c1] = g[src_r0:src_r1, src_c0:src_c1]
    return out


def _bbox_nonbg_tuple(g: Array) -> Optional[Tuple[int, int, int, int]]:
    return bbox_from_mask(_foreground_mask(g))


def generic_components(g: Array, connectivity: int = 4, separate_colors: bool = False) -> List[Obj]:
    g = sanitize_grid(g)
    bg = infer_bg(g)
    h, w = g.shape
    seen = np.zeros((h, w), dtype=bool)
    neighbors = ((1, 0), (-1, 0), (0, 1), (0, -1))
    if connectivity == 8:
        neighbors = neighbors + ((1, 1), (1, -1), (-1, 1), (-1, -1))
    out: List[Obj] = []
    for r in range(h):
        for c in range(w):
            if seen[r, c] or int(g[r, c]) == bg:
                continue
            seed_color = int(g[r, c])
            q = deque([(r, c)])
            seen[r, c] = True
            cells: List[Tuple[int, int]] = []
            while q:
                x, y = q.popleft()
                cells.append((x, y))
                for dr, dc in neighbors:
                    nr, nc = x + dr, y + dc
                    if not (0 <= nr < h and 0 <= nc < w) or seen[nr, nc] or int(g[nr, nc]) == bg:
                        continue
                    if separate_colors and int(g[nr, nc]) != seed_color:
                        continue
                    seen[nr, nc] = True
                    q.append((nr, nc))
            rs = [x for x, _ in cells]
            cs = [y for _, y in cells]
            out.append(Obj(seed_color if separate_colors else -1, cells, (min(rs), min(cs), max(rs), max(cs))))
    return out


def select_generic_object(g: Array, selector: str, connectivity: int, separate_colors: bool) -> Optional[Obj]:
    objs = generic_components(g, connectivity, separate_colors)
    if not objs:
        return None
    def density(o: Obj) -> float:
        return o.size / max(1, o.height * o.width)
    keys: Dict[str, Callable[[Obj], object]] = {
        "largest": lambda o: (o.size, o.height * o.width, -o.bbox[0], -o.bbox[1]),
        "smallest": lambda o: (-o.size, -(o.height * o.width), -o.bbox[0], -o.bbox[1]),
        "leftmost": lambda o: (-o.bbox[1], -o.bbox[0], o.size),
        "rightmost": lambda o: (o.bbox[3], -o.bbox[0], o.size),
        "topmost": lambda o: (-o.bbox[0], -o.bbox[1], o.size),
        "bottommost": lambda o: (o.bbox[2], -o.bbox[1], o.size),
        "densest": lambda o: (density(o), o.size),
        "sparsest": lambda o: (-density(o), o.size),
    }
    if selector not in keys:
        raise ValueError(selector)
    return max(objs, key=keys[selector])


def extract_generic_object(g: Array, selector: str, connectivity: int, separate_colors: bool, masked: bool) -> Array:
    g = sanitize_grid(g)
    bg = infer_bg(g)
    obj = select_generic_object(g, selector, connectivity, separate_colors)
    if obj is None:
        raise ValueError("no object")
    r0, c0, r1, c1 = obj.bbox
    crop = g[r0:r1 + 1, c0:c1 + 1].copy()
    if not masked:
        return crop
    keep = np.zeros(crop.shape, dtype=bool)
    for r, c in obj.cells:
        keep[r - r0, c - c0] = True
    return np.where(keep, crop, bg).astype(np.int16)


def keep_generic_object(g: Array, selector: str, connectivity: int, separate_colors: bool, keep: bool) -> Array:
    g = sanitize_grid(g)
    bg = infer_bg(g)
    obj = select_generic_object(g, selector, connectivity, separate_colors)
    if obj is None:
        raise ValueError("no object")
    out = np.full_like(g, bg) if keep else g.copy()
    if keep:
        for r, c in obj.cells:
            out[r, c] = g[r, c]
    else:
        for r, c in obj.cells:
            out[r, c] = bg
    return out


def _separator_segments(length: int, separators: List[int]) -> List[Tuple[int, int]]:
    if not separators:
        return [(0, length)]
    groups: List[Tuple[int, int]] = []
    start = prev = separators[0]
    for x in separators[1:]:
        if x == prev + 1:
            prev = x
        else:
            groups.append((start, prev + 1)); start = prev = x
    groups.append((start, prev + 1))
    bounds = [0] + [b for grp in groups for b in grp] + [length]
    # Regions are before, between and after separator groups.
    regions: List[Tuple[int, int]] = []
    cursor = 0
    for a, b in groups:
        if cursor < a:
            regions.append((cursor, a))
        cursor = b
    if cursor < length:
        regions.append((cursor, length))
    return regions


def split_uniform_panels(g: Array) -> List[Array]:
    g = sanitize_grid(g)
    sep_rows = [r for r in range(g.shape[0]) if np.all(g[r, :] == g[r, 0])]
    sep_cols = [c for c in range(g.shape[1]) if np.all(g[:, c] == g[0, c])]
    row_regions = _separator_segments(g.shape[0], sep_rows)
    col_regions = _separator_segments(g.shape[1], sep_cols)
    panels = [g[r0:r1, c0:c1].copy() for r0, r1 in row_regions for c0, c1 in col_regions if r1 > r0 and c1 > c0]
    # Require at least one actual separation.
    return panels if len(panels) > 1 else []


def select_panel_exact(g: Array, selector: str) -> Array:
    panels = split_uniform_panels(g)
    if not panels:
        raise ValueError("no panels")
    if selector.startswith("index_"):
        idx = int(selector.split("_")[1])
        if idx >= len(panels):
            raise ValueError("panel index")
        return panels[idx]
    def fg_count(p: Array) -> int:
        return int(np.count_nonzero(p != infer_bg(p)))
    if selector == "max_foreground":
        return max(panels, key=lambda p: (fg_count(p), p.size))
    if selector == "min_foreground":
        return min(panels, key=lambda p: (fg_count(p), p.size))
    if selector == "max_colors":
        return max(panels, key=lambda p: (len(np.unique(p)), fg_count(p)))
    if selector == "min_colors":
        return min(panels, key=lambda p: (len(np.unique(p)), fg_count(p)))
    raise ValueError(selector)


def panel_preserving_exact(g: Array, operation: str) -> Array:
    panels = split_equal_panels(g)
    if panels is None:
        raise ValueError("no two equal panels")
    left, right = panels
    bg_l, bg_r = infer_bg(left), infer_bg(right)
    ml, mr = left != bg_l, right != bg_r
    out_bg = bg_l
    out = np.full(left.shape, out_bg, dtype=np.int16)
    if operation == "left_intersection":
        out[ml & mr] = left[ml & mr]
    elif operation == "right_intersection":
        out[ml & mr] = right[ml & mr]
    elif operation == "left_union":
        out[mr] = right[mr]; out[ml] = left[ml]
    elif operation == "right_union":
        out[ml] = left[ml]; out[mr] = right[mr]
    elif operation == "left_minus_right":
        out[ml & ~mr] = left[ml & ~mr]
    elif operation == "right_minus_left":
        out[mr & ~ml] = right[mr & ~ml]
    elif operation == "equal_values":
        mask = left == right
        out[mask] = left[mask]
    else:
        raise ValueError(operation)
    return out


def block_reduce_exact(g: Array, rh: int, cw: int, mode: str, count_map: Optional[Dict[int, int]] = None) -> Array:
    g = sanitize_grid(g)
    h, w = g.shape
    if h % rh or w % cw:
        raise ValueError("bad block factors")
    bg = infer_bg(g)
    out = np.full((h // rh, w // cw), bg, dtype=np.int16)
    for i in range(out.shape[0]):
        for j in range(out.shape[1]):
            block = g[i * rh:(i + 1) * rh, j * cw:(j + 1) * cw]
            flat = block.ravel()
            if mode == "top_left": value = int(block[0, 0])
            elif mode == "top_right": value = int(block[0, -1])
            elif mode == "bottom_left": value = int(block[-1, 0])
            elif mode == "bottom_right": value = int(block[-1, -1])
            elif mode == "center": value = int(block[(rh - 1) // 2, (cw - 1) // 2])
            elif mode == "majority": value = Counter(int(v) for v in flat).most_common(1)[0][0]
            elif mode == "majority_nonbg":
                vals = [int(v) for v in flat if int(v) != bg]
                value = Counter(vals).most_common(1)[0][0] if vals else bg
            elif mode == "first_nonbg":
                vals = [int(v) for v in flat if int(v) != bg]
                value = vals[0] if vals else bg
            elif mode == "unique_nonbg":
                vals = sorted({int(v) for v in flat if int(v) != bg})
                value = vals[0] if len(vals) == 1 else bg
            elif mode == "count_map":
                if count_map is None:
                    raise ValueError("missing count map")
                count = int(np.count_nonzero(block != bg))
                if count not in count_map:
                    raise ValueError("unseen count")
                value = int(count_map[count])
            else: raise ValueError(mode)
            out[i, j] = value
    return out


def polyphase_extract_exact(g: Array, rh: int, cw: int, ro: int, co: int) -> Array:
    return sanitize_grid(g)[ro::rh, co::cw].copy()


def _object_attribute_candidates(train: List[Tuple[Array, Array]], tests: List[Array]) -> List[RuleCandidate]:
    out: List[RuleCandidate] = []
    if not all(x.shape == y.shape and np.array_equal(_foreground_mask(x), _foreground_mask(y)) for x, y in train):
        return out
    for connectivity in (4, 8):
        for separate in (True, False):
            # Absolute attribute maps.
            attrs: Dict[str, Callable[[Obj], object]] = {
                "area": lambda o: o.size,
                "height": lambda o: o.height,
                "width": lambda o: o.width,
                "shape": lambda o: (o.height, o.width, o.size),
                "bbox_area": lambda o: o.height * o.width,
                "holes": object_hole_count,
                "border": lambda o: (o.bbox[0] == 0 or o.bbox[1] == 0),
            }
            for attr_name, attr_fn in attrs.items():
                mapping: Dict[object, int] = {}
                valid = True
                for x, y in train:
                    objs = generic_components(x, connectivity, separate)
                    for obj in objs:
                        vals = {int(y[r, c]) for r, c in obj.cells}
                        if len(vals) != 1:
                            valid = False; break
                        key, val = attr_fn(obj), next(iter(vals))
                        if key in mapping and mapping[key] != val:
                            valid = False; break
                        mapping[key] = val
                    if not valid: break
                if valid and mapping:
                    def fn(g: Array, mp=dict(mapping), af=attr_fn, conn=connectivity, sep=separate) -> Array:
                        z = sanitize_grid(g).copy()
                        for obj in generic_components(z, conn, sep):
                            key = af(obj)
                            if key not in mp:
                                raise ValueError("unseen object attribute")
                            for r, c in obj.cells: z[r, c] = int(mp[key])
                        return z
                    _try_exact_rule(out, train, tests, f"object_{attr_name}_map_c{connectivity}_{int(separate)}", fn, 10 + len(mapping), "struct_object_attribute")

            # Rank-conditioned colors generalize to unseen absolute sizes.
            rank_specs = {
                "area_asc": lambda o: (o.size, o.bbox[0], o.bbox[1]),
                "area_desc": lambda o: (-o.size, o.bbox[0], o.bbox[1]),
                "left": lambda o: (o.bbox[1], o.bbox[0]),
                "top": lambda o: (o.bbox[0], o.bbox[1]),
            }
            for rank_name, key_fn in rank_specs.items():
                rank_map: Dict[int, int] = {}; count: Optional[int] = None; valid = True
                for x, y in train:
                    objs = sorted(generic_components(x, connectivity, separate), key=key_fn)
                    if not objs or (count is not None and len(objs) != count): valid = False; break
                    count = len(objs)
                    for rank, obj in enumerate(objs):
                        vals = {int(y[r, c]) for r, c in obj.cells}
                        if len(vals) != 1: valid = False; break
                        val = next(iter(vals))
                        if rank in rank_map and rank_map[rank] != val: valid = False; break
                        rank_map[rank] = val
                    if not valid: break
                if valid and count and len(rank_map) == count <= 12:
                    def fn(g: Array, mp=dict(rank_map), kf=key_fn, conn=connectivity, sep=separate, n=count) -> Array:
                        z = sanitize_grid(g).copy(); objs = sorted(generic_components(z, conn, sep), key=kf)
                        if len(objs) != n: raise ValueError("object count changed")
                        for rank, obj in enumerate(objs):
                            for r, c in obj.cells: z[r, c] = int(mp[rank])
                        return z
                    _try_exact_rule(out, train, tests, f"object_rank_{rank_name}_c{connectivity}_{int(separate)}", fn, 10 + count, "struct_object_rank")
    return out


def connect_markers_exact(g: Array, mode: str, group_same_color: bool, line_color: Optional[int]) -> Array:
    g = sanitize_grid(g); bg = infer_bg(g); out = g.copy()
    coords = [(int(r), int(c), int(g[r, c])) for r, c in np.argwhere(g != bg)]
    for i in range(len(coords)):
        r1, c1, col1 = coords[i]
        for j in range(i + 1, len(coords)):
            r2, c2, col2 = coords[j]
            if group_same_color and col1 != col2: continue
            dr, dc = r2 - r1, c2 - c1
            step: Optional[Tuple[int, int]] = None
            if dr == 0 and mode in ("h", "hv", "all"): step = (0, 1 if dc > 0 else -1)
            elif dc == 0 and mode in ("v", "hv", "all"): step = (1 if dr > 0 else -1, 0)
            elif abs(dr) == abs(dc) and mode in ("diag", "all"): step = (1 if dr > 0 else -1, 1 if dc > 0 else -1)
            if step is None: continue
            rr, cc = r1, c1; color = col1 if line_color is None else int(line_color)
            while (rr, cc) != (r2, c2):
                out[rr, cc] = color; rr += step[0]; cc += step[1]
            out[r2, c2] = color
    return out


def bbox_draw_exact(g: Array, fill: bool, color: Optional[int]) -> Array:
    g = sanitize_grid(g); bg = infer_bg(g); bb = bbox_from_mask(g != bg)
    if bb is None: raise ValueError("empty")
    r0, c0, r1, c1 = bb; out = g.copy(); col = int(color) if color is not None else marker_color(g, bg)
    if fill: out[r0:r1 + 1, c0:c1 + 1] = col
    else:
        out[r0, c0:c1 + 1] = col; out[r1, c0:c1 + 1] = col
        out[r0:r1 + 1, c0] = col; out[r0:r1 + 1, c1] = col
    return out


def frequency_select_exact(g: Array, selector: str, crop: bool, recolor: Optional[int]) -> Array:
    g = sanitize_grid(g); bg = infer_bg(g)
    vals, counts = np.unique(g, return_counts=True)
    pairs = [(int(v), int(c)) for v, c in zip(vals, counts) if int(v) != bg]
    if not pairs: raise ValueError("no foreground colors")
    if selector == "rarest": chosen = min(pairs, key=lambda p: (p[1], p[0]))[0]
    elif selector == "most": chosen = max(pairs, key=lambda p: (p[1], -p[0]))[0]
    else: raise ValueError(selector)
    out = np.full_like(g, bg); out[g == chosen] = chosen if recolor is None else int(recolor)
    return crop_bbox_non_bg(out, bg) if crop else out


def solid_count_exact(g: Array, measure: str, orientation: str, color: int, connectivity: int = 4) -> Array:
    g = sanitize_grid(g); bg = infer_bg(g)
    if measure == "objects": n = len(generic_components(g, connectivity, False))
    elif measure == "colored_objects": n = len(generic_components(g, connectivity, True))
    elif measure == "colors": n = len([v for v in np.unique(g) if int(v) != bg])
    elif measure == "cells": n = int(np.count_nonzero(g != bg))
    else: raise ValueError(measure)
    if not 1 <= n <= 30: raise ValueError("count outside grid limit")
    if orientation == "row": return np.full((1, n), int(color), dtype=np.int16)
    if orientation == "col": return np.full((n, 1), int(color), dtype=np.int16)
    if orientation == "square": return np.full((n, n), int(color), dtype=np.int16)
    raise ValueError(orientation)




def _normalized_binary_signature(mask: Array, *, canonical_dihedral: bool = False) -> Tuple[Tuple[int, ...], ...]:
    values = np.asarray(mask, dtype=bool)
    bb = bbox_from_mask(values)
    if bb is None:
        raise ValueError("empty mask")
    r0, c0, r1, c1 = bb
    cropped = values[r0 : r1 + 1, c0 : c1 + 1]

    def signature(array: Array) -> Tuple[Tuple[int, ...], ...]:
        return tuple(tuple(int(value) for value in row) for row in np.asarray(array, dtype=np.int8))

    if not canonical_dihedral:
        return signature(cropped)
    variants: List[Array] = []
    for k in range(4):
        rotated = np.rot90(cropped, k)
        variants.append(rotated)
        variants.append(np.fliplr(rotated))
    return min(signature(variant) for variant in variants)


def object_hole_count(obj: Obj) -> int:
    height, width = obj.height, obj.width
    mask = np.zeros((height, width), dtype=bool)
    top, left, _, _ = obj.bbox
    for row, column in obj.cells:
        mask[row - top, column - left] = True
    seen = np.zeros_like(mask, dtype=bool)
    holes = 0
    for row in range(height):
        for column in range(width):
            if mask[row, column] or seen[row, column]:
                continue
            queue = deque([(row, column)])
            seen[row, column] = True
            touches_border = False
            while queue:
                current_row, current_column = queue.popleft()
                touches_border = touches_border or current_row in {0, height - 1} or current_column in {0, width - 1}
                for delta_row, delta_column in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                    next_row = current_row + delta_row
                    next_column = current_column + delta_column
                    if 0 <= next_row < height and 0 <= next_column < width and not mask[next_row, next_column] and not seen[next_row, next_column]:
                        seen[next_row, next_column] = True
                        queue.append((next_row, next_column))
            if not touches_border:
                holes += 1
    return holes


def marker_shape_recolor_rules(train: List[Tuple[Array, Array]], tests: List[Array]) -> List[RuleCandidate]:
    """Infer a small marker glyph that names the output color of a larger packet.

    The rule is retained only when every demonstration consists of one dominant
    foreground color plus a smaller marker, the marker disappears, and the
    dominant packet is recolored uniformly. Marker signatures are learned from
    demonstrations and must be observed again at application time.
    """
    mapping: Dict[Tuple[Tuple[int, ...], ...], int] = {}
    valid = True
    for source, target in train:
        source = sanitize_grid(source)
        target = sanitize_grid(target)
        if source.shape != target.shape:
            valid = False
            break
        background = infer_bg(source)
        foreground = [(int(color), int(np.count_nonzero(source == color))) for color in np.unique(source) if int(color) != background]
        if len(foreground) < 2:
            valid = False
            break
        main_color = max(foreground, key=lambda item: (item[1], -item[0]))[0]
        marker_mask = (source != background) & (source != main_color)
        if not np.any(marker_mask):
            valid = False
            break
        signature = _normalized_binary_signature(marker_mask, canonical_dihedral=False)
        output_colors = [int(color) for color in np.unique(target) if int(color) != background]
        if len(output_colors) != 1:
            valid = False
            break
        output_color = output_colors[0]
        expected = np.full_like(source, background)
        expected[source == main_color] = output_color
        if not exact(expected, target):
            valid = False
            break
        previous = mapping.get(signature)
        if previous is not None and previous != output_color:
            valid = False
            break
        mapping[signature] = output_color
    if not valid or not mapping:
        return []

    def apply(grid: Array) -> Array:
        grid = sanitize_grid(grid)
        background = infer_bg(grid)
        foreground = [(int(color), int(np.count_nonzero(grid == color))) for color in np.unique(grid) if int(color) != background]
        if len(foreground) < 2:
            raise ValueError("marker-conditioned recoloring requires at least two foreground colors")
        main_color = max(foreground, key=lambda item: (item[1], -item[0]))[0]
        marker_mask = (grid != background) & (grid != main_color)
        signature = _normalized_binary_signature(marker_mask, canonical_dihedral=False)
        if signature not in mapping:
            raise ValueError("unseen marker signature")
        output = np.full_like(grid, background)
        output[grid == main_color] = int(mapping[signature])
        return output

    output: List[RuleCandidate] = []
    _try_exact_rule(
        output,
        train,
        tests,
        "marker_shape_recolor_main",
        apply,
        9 + len(mapping),
        "struct_marker_conditioned_recolor",
    )
    return output


def background_components(grid: Array, connectivity: int = 4) -> List[Obj]:
    grid = sanitize_grid(grid)
    background = infer_bg(grid)
    height, width = grid.shape
    neighbors = ((1, 0), (-1, 0), (0, 1), (0, -1))
    if connectivity == 8:
        neighbors = neighbors + ((1, 1), (1, -1), (-1, 1), (-1, -1))
    seen = np.zeros((height, width), dtype=bool)
    output: List[Obj] = []
    for row in range(height):
        for column in range(width):
            if seen[row, column] or int(grid[row, column]) != background:
                continue
            queue = deque([(row, column)])
            seen[row, column] = True
            cells: List[Tuple[int, int]] = []
            while queue:
                current_row, current_column = queue.popleft()
                cells.append((current_row, current_column))
                for delta_row, delta_column in neighbors:
                    next_row = current_row + delta_row
                    next_column = current_column + delta_column
                    if (
                        0 <= next_row < height
                        and 0 <= next_column < width
                        and not seen[next_row, next_column]
                        and int(grid[next_row, next_column]) == background
                    ):
                        seen[next_row, next_column] = True
                        queue.append((next_row, next_column))
            rows = [value[0] for value in cells]
            columns = [value[1] for value in cells]
            output.append(Obj(background, cells, (min(rows), min(columns), max(rows), max(columns))))
    return output


def enclosed_background_components(grid: Array, connectivity: int = 4) -> List[Obj]:
    height, width = sanitize_grid(grid).shape
    return [
        component
        for component in background_components(grid, connectivity)
        if not any(row in {0, height - 1} or column in {0, width - 1} for row, column in component.cells)
    ]


def fill_enclosed_constant_exact(grid: Array, color: int, connectivity: int = 4) -> Array:
    output = sanitize_grid(grid).copy()
    regions = enclosed_background_components(output, connectivity)
    if not regions:
        raise ValueError("no enclosed background region")
    for region in regions:
        for row, column in region.cells:
            output[row, column] = int(color)
    return output


def _enclosed_region_key(region: Obj, mode: str) -> object:
    height = region.height
    width = region.width
    if mode == "area":
        return region.size
    if mode == "shape":
        return (height, width)
    if mode == "height":
        return height
    if mode == "width":
        return width
    if mode == "max_side":
        return max(height, width)
    if mode == "min_side":
        return min(height, width)
    raise ValueError(mode)


def enclosed_region_rules(train: List[Tuple[Array, Array]], tests: List[Array]) -> List[RuleCandidate]:
    output: List[RuleCandidate] = []
    colors = _output_candidate_colors(train)
    for connectivity in (4, 8):
        for color in colors:
            _try_exact_rule(
                output,
                train,
                tests,
                f"fill_enclosed_{color}_c{connectivity}",
                lambda grid, value=color, conn=connectivity: fill_enclosed_constant_exact(grid, value, conn),
                7,
                "struct_enclosed_fill",
            )
        for mode in ("area", "shape", "height", "width", "max_side", "min_side"):
            mapping: Dict[object, int] = {}
            valid = True
            for source, target in train:
                source = sanitize_grid(source)
                target = sanitize_grid(target)
                if source.shape != target.shape:
                    valid = False
                    break
                regions = enclosed_background_components(source, connectivity)
                if not regions:
                    valid = False
                    break
                region_mask = np.zeros_like(source, dtype=bool)
                for region in regions:
                    for row, column in region.cells:
                        region_mask[row, column] = True
                if not np.array_equal(source[~region_mask], target[~region_mask]):
                    valid = False
                    break
                for region in regions:
                    values = {int(target[row, column]) for row, column in region.cells}
                    if len(values) != 1:
                        valid = False
                        break
                    key = _enclosed_region_key(region, mode)
                    value = next(iter(values))
                    previous = mapping.get(key)
                    if previous is not None and previous != value:
                        valid = False
                        break
                    mapping[key] = value
                if not valid:
                    break
            if not valid or not mapping:
                continue

            def apply(grid: Array, mp=dict(mapping), key_mode=mode, conn=connectivity) -> Array:
                result = sanitize_grid(grid).copy()
                regions = enclosed_background_components(result, conn)
                if not regions:
                    raise ValueError("no enclosed regions")
                for region in regions:
                    key = _enclosed_region_key(region, key_mode)
                    if key not in mp:
                        raise ValueError("unseen enclosed-region attribute")
                    for row, column in region.cells:
                        result[row, column] = int(mp[key])
                return result

            _try_exact_rule(
                output,
                train,
                tests,
                f"fill_enclosed_map_{mode}_c{connectivity}",
                apply,
                9 + len(mapping),
                "struct_enclosed_attribute_fill",
            )
    return output


def _minimal_axis_period(grid: Array, axis: int) -> int:
    values = sanitize_grid(grid)
    length = values.shape[axis]
    for period in range(1, length + 1):
        valid = True
        for index in range(length):
            left = np.take(values, index, axis=axis)
            right = np.take(values, index % period, axis=axis)
            if not np.array_equal(left, right):
                valid = False
                break
        if valid:
            return period
    return length


def periodic_resize_exact(grid: Array, output_shape: Tuple[int, int]) -> Array:
    grid = sanitize_grid(grid)
    target_height, target_width = output_shape
    if not (1 <= target_height <= MAX_SIDE and 1 <= target_width <= MAX_SIDE):
        raise ValueError("periodic output shape outside ARC bounds")
    row_period = _minimal_axis_period(grid, 0)
    column_period = _minimal_axis_period(grid, 1)
    motif = grid[:row_period, :column_period]
    row_repeats = (target_height + row_period - 1) // row_period
    column_repeats = (target_width + column_period - 1) // column_period
    return np.tile(motif, (row_repeats, column_repeats))[:target_height, :target_width].astype(np.int16)


def _output_shape_specs(train: List[Tuple[Array, Array]]) -> List[Tuple[str, Callable[[Array], Tuple[int, int]]]]:
    specs: List[Tuple[str, Callable[[Array], Tuple[int, int]]]] = []
    output_shapes = [tuple(target.shape) for _, target in train]
    if len(set(output_shapes)) == 1:
        shape = output_shapes[0]
        specs.append((f"constant_{shape[0]}x{shape[1]}", lambda grid, value=shape: value))
    deltas = [(target.shape[0] - source.shape[0], target.shape[1] - source.shape[1]) for source, target in train]
    if len(set(deltas)) == 1:
        delta_height, delta_width = deltas[0]
        specs.append((
            f"delta_{delta_height}_{delta_width}",
            lambda grid, dh=delta_height, dw=delta_width: (grid.shape[0] + dh, grid.shape[1] + dw),
        ))
    ratios = [
        (Fraction(target.shape[0], source.shape[0]), Fraction(target.shape[1], source.shape[1]))
        for source, target in train
    ]
    if len(set(ratios)) == 1:
        ratio_height, ratio_width = ratios[0]

        def ratio_shape(grid: Array, rh=ratio_height, rw=ratio_width) -> Tuple[int, int]:
            height = Fraction(grid.shape[0]) * rh
            width = Fraction(grid.shape[1]) * rw
            if height.denominator != 1 or width.denominator != 1:
                raise ValueError("non-integral periodic resize")
            return int(height), int(width)

        specs.append((f"ratio_{ratio_height}_{ratio_width}", ratio_shape))
    unique: Dict[str, Callable[[Array], Tuple[int, int]]] = {}
    for name, function in specs:
        unique[name] = function
    return list(unique.items())


def periodic_resize_rules(train: List[Tuple[Array, Array]], tests: List[Array]) -> List[RuleCandidate]:
    output: List[RuleCandidate] = []
    for shape_name, shape_function in _output_shape_specs(train):
        transformed: List[Array] = []
        valid = True
        for source, target in train:
            try:
                prediction = periodic_resize_exact(source, shape_function(source))
            except Exception:
                valid = False
                break
            if prediction.shape != target.shape:
                valid = False
                break
            transformed.append(prediction)
        if not valid:
            continue
        mapping: Dict[int, int] = {}
        for prediction, (_, target) in zip(transformed, train):
            for source_color, target_color in zip(prediction.ravel(), target.ravel()):
                source_value = int(source_color)
                target_value = int(target_color)
                previous = mapping.get(source_value)
                if previous is not None and previous != target_value:
                    valid = False
                    break
                mapping[source_value] = target_value
            if not valid:
                break
        if not valid or not mapping:
            continue

        def apply(grid: Array, shape_fn=shape_function, color_map=dict(mapping)) -> Array:
            prediction = periodic_resize_exact(grid, shape_fn(sanitize_grid(grid)))
            result = prediction.copy()
            for source_color, target_color in color_map.items():
                result[prediction == int(source_color)] = int(target_color)
            return result

        _try_exact_rule(
            output,
            train,
            tests,
            f"periodic_resize_{shape_name}_color_map",
            apply,
            8 + len(mapping),
            "struct_periodic_resize",
        )
    return output


def kronecker_mask_motif_exact(grid: Array, motif_mode: str, outer_complement: bool = False) -> Array:
    grid = sanitize_grid(grid)
    background = infer_bg(grid)
    foreground_colors = [int(color) for color in np.unique(grid) if int(color) != background]
    if len(foreground_colors) != 1:
        raise ValueError("Kronecker mask motif requires one foreground color")
    color = foreground_colors[0]
    mask = grid != background
    outer = ~mask if outer_complement else mask
    transforms: Dict[str, Array] = {
        "same": mask,
        "complement": ~mask,
        "flip_h": np.fliplr(mask),
        "flip_v": np.flipud(mask),
        "rot180": np.rot90(mask, 2),
        "flip_h_complement": ~np.fliplr(mask),
        "flip_v_complement": ~np.flipud(mask),
        "rot180_complement": ~np.rot90(mask, 2),
    }
    if motif_mode not in transforms:
        raise ValueError(motif_mode)
    motif = transforms[motif_mode]
    if grid.shape[0] * motif.shape[0] > MAX_SIDE or grid.shape[1] * motif.shape[1] > MAX_SIDE:
        raise ValueError("Kronecker output exceeds ARC bounds")
    expanded = np.kron(outer.astype(np.int8), motif.astype(np.int8)).astype(bool)
    return np.where(expanded, color, background).astype(np.int16)


def kronecker_variant_rules(train: List[Tuple[Array, Array]], tests: List[Array]) -> List[RuleCandidate]:
    output: List[RuleCandidate] = []
    for motif_mode in (
        "same",
        "complement",
        "flip_h",
        "flip_v",
        "rot180",
        "flip_h_complement",
        "flip_v_complement",
        "rot180_complement",
    ):
        for outer_complement in (False, True):
            _try_exact_rule(
                output,
                train,
                tests,
                f"kronecker_{'outer_complement_' if outer_complement else ''}{motif_mode}",
                lambda grid, mode=motif_mode, outer=outer_complement: kronecker_mask_motif_exact(grid, mode, outer),
                8,
                "struct_kronecker_motif",
            )
    return output


def _fit_modular_affine(terms: List[Tuple[int, int, int, int, int]], desired: List[int], modulus: int) -> Optional[Tuple[int, int, int, int, int]]:
    if modulus <= 0 or modulus**5 > 100_000:
        return None
    for coefficients in itertools.product(range(modulus), repeat=5):
        if all(sum(coefficient * term for coefficient, term in zip(coefficients, row)) % modulus == target for row, target in zip(terms, desired)):
            return tuple(int(value) for value in coefficients)
    return None


def affine_index_tile_rules(train: List[Tuple[Array, Array]], tests: List[Array]) -> List[RuleCandidate]:
    if not train:
        return []
    source_shapes = {tuple(source.shape) for source, _ in train}
    if len(source_shapes) != 1:
        return []
    source_height, source_width = next(iter(source_shapes))
    factors: set[Tuple[int, int]] = set()
    row_terms: List[Tuple[int, int, int, int, int]] = []
    column_terms: List[Tuple[int, int, int, int, int]] = []
    desired_rows: List[int] = []
    desired_columns: List[int] = []
    for source, target in train:
        if target.shape[0] % source_height or target.shape[1] % source_width:
            return []
        factors.add((target.shape[0] // source_height, target.shape[1] // source_width))
        values = source.ravel().tolist()
        if len(set(int(value) for value in values)) == source.size:
            coordinate_by_value = {int(source[row, column]): (row, column) for row in range(source_height) for column in range(source_width)}
            for row in range(target.shape[0]):
                for column in range(target.shape[1]):
                    value = int(target[row, column])
                    if value not in coordinate_by_value:
                        return []
                    source_row, source_column = coordinate_by_value[value]
                    terms = (row % source_height, column % source_width, row // source_height, column // source_width, 1)
                    row_terms.append(terms)
                    column_terms.append(terms)
                    desired_rows.append(source_row)
                    desired_columns.append(source_column)
    if len(factors) != 1 or not row_terms or not column_terms:
        return []
    factor_height, factor_width = next(iter(factors))
    row_coefficients = _fit_modular_affine(row_terms, desired_rows, source_height)
    column_coefficients = _fit_modular_affine(column_terms, desired_columns, source_width)
    if row_coefficients is None or column_coefficients is None:
        return []

    def apply(grid: Array) -> Array:
        grid = sanitize_grid(grid)
        if grid.shape != (source_height, source_width):
            raise ValueError("affine tile source shape changed")
        target_height = source_height * factor_height
        target_width = source_width * factor_width
        result = np.zeros((target_height, target_width), dtype=np.int16)
        for row in range(target_height):
            for column in range(target_width):
                terms = (row % source_height, column % source_width, row // source_height, column // source_width, 1)
                source_row = sum(coefficient * term for coefficient, term in zip(row_coefficients, terms)) % source_height
                source_column = sum(coefficient * term for coefficient, term in zip(column_coefficients, terms)) % source_width
                result[row, column] = int(grid[source_row, source_column])
        return result

    output: List[RuleCandidate] = []
    _try_exact_rule(
        output,
        train,
        tests,
        "affine_modular_index_tile",
        apply,
        12,
        "struct_affine_tile",
    )
    return output


def pack_object_chain_exact(grid: Array, order: str, connectivity: int = 4) -> Array:
    grid = sanitize_grid(grid)
    background = infer_bg(grid)
    objects = generic_components(grid, connectivity, True)
    if len(objects) < 2:
        raise ValueError("object chain requires multiple objects")
    order_keys: Dict[str, Callable[[Obj], object]] = {
        "left": lambda obj: (obj.bbox[1], obj.bbox[0], -obj.size, obj.color),
        "reading": lambda obj: (obj.bbox[0], obj.bbox[1], -obj.size, obj.color),
        "area_desc": lambda obj: (-obj.size, obj.bbox[1], obj.bbox[0], obj.color),
        "area_asc": lambda obj: (obj.size, obj.bbox[1], obj.bbox[0], obj.color),
    }
    if order not in order_keys:
        raise ValueError(order)
    objects = sorted(objects, key=order_keys[order])
    output = np.full_like(grid, background)
    top = 0
    left = 0
    for obj in objects:
        source_top, source_left, _, _ = obj.bbox
        if top + obj.height > output.shape[0] or left + obj.width > output.shape[1]:
            raise ValueError("packed object chain exceeds canvas")
        for row, column in obj.cells:
            output[top + row - source_top, left + column - source_left] = obj.color
        top += obj.height - 1
        left += obj.width - 1
    return output


def object_chain_rules(train: List[Tuple[Array, Array]], tests: List[Array]) -> List[RuleCandidate]:
    output: List[RuleCandidate] = []
    for connectivity in (4, 8):
        for order in ("left", "reading", "area_desc", "area_asc"):
            _try_exact_rule(
                output,
                train,
                tests,
                f"pack_object_chain_{order}_c{connectivity}",
                lambda grid, ordering=order, conn=connectivity: pack_object_chain_exact(grid, ordering, conn),
                10,
                "struct_object_chain",
            )
    return output


def object_shape_recolor_rules(train: List[Tuple[Array, Array]], tests: List[Array]) -> List[RuleCandidate]:
    output: List[RuleCandidate] = []
    for connectivity in (4, 8):
        for canonical_dihedral in (False, True):
            mapping: Dict[Tuple[Tuple[int, ...], ...], int] = {}
            valid = True
            for source, target in train:
                source = sanitize_grid(source)
                target = sanitize_grid(target)
                if source.shape != target.shape or not np.array_equal(source != infer_bg(source), target != infer_bg(target)):
                    valid = False
                    break
                objects = generic_components(source, connectivity, True)
                if not objects:
                    valid = False
                    break
                for obj in objects:
                    mask = np.zeros_like(source, dtype=bool)
                    for row, column in obj.cells:
                        mask[row, column] = True
                    signature = _normalized_binary_signature(mask, canonical_dihedral=canonical_dihedral)
                    values = {int(target[row, column]) for row, column in obj.cells}
                    if len(values) != 1:
                        valid = False
                        break
                    value = next(iter(values))
                    previous = mapping.get(signature)
                    if previous is not None and previous != value:
                        valid = False
                        break
                    mapping[signature] = value
                if not valid:
                    break
            if not valid or not mapping:
                continue

            def apply(grid: Array, mp=dict(mapping), conn=connectivity, canon=canonical_dihedral) -> Array:
                grid = sanitize_grid(grid)
                background = infer_bg(grid)
                result = np.full_like(grid, background)
                objects = generic_components(grid, conn, True)
                if not objects:
                    raise ValueError("no objects")
                for obj in objects:
                    mask = np.zeros_like(grid, dtype=bool)
                    for row, column in obj.cells:
                        mask[row, column] = True
                    signature = _normalized_binary_signature(mask, canonical_dihedral=canon)
                    if signature not in mp:
                        raise ValueError("unseen object shape")
                    for row, column in obj.cells:
                        result[row, column] = int(mp[signature])
                return result

            _try_exact_rule(
                output,
                train,
                tests,
                f"object_shape_recolor_c{connectivity}_{'dihedral' if canonical_dihedral else 'oriented'}",
                apply,
                10 + len(mapping),
                "struct_object_shape_recolor",
            )
    return output


def periodic_stripes_from_markers_exact(grid: Array) -> Array:
    grid = sanitize_grid(grid)
    background = infer_bg(grid)
    coordinates = [(int(row), int(column), int(grid[row, column])) for row, column in np.argwhere(grid != background)]
    if len(coordinates) != 2 or coordinates[0][2] == coordinates[1][2]:
        raise ValueError("periodic stripe rule requires two differently colored singleton markers")
    first, second = coordinates
    delta_row = abs(second[0] - first[0])
    delta_column = abs(second[1] - first[1])
    if delta_row == 0 and delta_column == 0:
        raise ValueError("coincident markers")
    horizontal = delta_column == 0 or (delta_row > 0 and delta_row <= delta_column)
    axis_values = sorted([(first[0] if horizontal else first[1], first[2]), (second[0] if horizontal else second[1], second[2])])
    start, first_color = axis_values[0]
    next_position, second_color = axis_values[1]
    step = next_position - start
    if step <= 0:
        raise ValueError("invalid marker spacing")
    output = np.full_like(grid, background)
    limit = grid.shape[0] if horizontal else grid.shape[1]
    position = start
    index = 0
    while position < limit:
        color = first_color if index % 2 == 0 else second_color
        if horizontal:
            output[position, :] = color
        else:
            output[:, position] = color
        position += step
        index += 1
    return output


def periodic_stripe_rules(train: List[Tuple[Array, Array]], tests: List[Array]) -> List[RuleCandidate]:
    output: List[RuleCandidate] = []
    _try_exact_rule(
        output,
        train,
        tests,
        "periodic_stripes_from_two_markers",
        periodic_stripes_from_markers_exact,
        8,
        "struct_periodic_stripes",
    )
    return output

def structural_exact_rules(train: List[Tuple[Array, Array]], tests: List[Array]) -> List[RuleCandidate]:
    out: List[RuleCandidate] = []
    same_shape = all(x.shape == y.shape for x, y in train)
    smaller = all(y.shape[0] <= x.shape[0] and y.shape[1] <= x.shape[1] for x, y in train)
    larger = all(y.shape[0] >= x.shape[0] and y.shape[1] >= x.shape[1] for x, y in train)
    colors = _output_candidate_colors(train)

    if larger:
        for mode in ("right", "left", "down", "up", "right_seam", "left_seam", "down_seam", "up_seam"):
            _try_exact_rule(out, train, tests, f"mirror_concat_{mode}", lambda g, m=mode: mirror_concat_exact(g, m), 7, "struct_mirror_concat")

    if same_shape:
        for mode in ("horizontal", "vertical", "rot180", "diagonal", "anti_diagonal"):
            _try_exact_rule(out, train, tests, f"complete_{mode}", lambda g, m=mode: complete_reflection_exact(g, m), 6, "struct_symmetry")
            for color in colors[:3]:
                _try_exact_rule(out, train, tests, f"complete_{mode}_{color}", lambda g, m=mode, c=color: complete_reflection_exact(g, m, c), 7, "struct_symmetry")

        # Infer one global translation from foreground bounding boxes.
        offsets: List[Tuple[int, int]] = []
        valid = True
        for x, y in train:
            bx, by = _bbox_nonbg_tuple(x), _bbox_nonbg_tuple(y)
            if bx is None or by is None or np.count_nonzero(_foreground_mask(x)) != np.count_nonzero(_foreground_mask(y)):
                valid = False; break
            offsets.append((by[0] - bx[0], by[1] - bx[1]))
        if valid and offsets and len(set(offsets)) == 1:
            dr, dc = offsets[0]
            if (dr, dc) != (0, 0):
                _try_exact_rule(out, train, tests, f"translate_{dr}_{dc}", lambda g, a=dr, b=dc: shift_grid_exact(g, a, b), 5, "struct_translation")

    if smaller:
        # Generic positional extraction fit demonstrations but generalized 0/7
        # on public training tests. It remains implemented for diagnostics but
        # is deliberately excluded from the competition proposal channel.

        # Panel selection.
        max_panels = 0
        try: max_panels = max(len(split_uniform_panels(x)) for x, _ in train)
        except Exception: max_panels = 0
        for idx in range(min(max_panels, 9)):
            _try_exact_rule(out, train, tests, f"panel_index_{idx}", lambda g, i=idx: select_panel_exact(g, f"index_{i}"), 6, "struct_panel_select")
        for selector in ("max_foreground", "min_foreground", "max_colors", "min_colors"):
            _try_exact_rule(out, train, tests, f"panel_{selector}", lambda g, s=selector: select_panel_exact(g, s), 7, "struct_panel_select")
        for operation in ("left_intersection", "right_intersection", "left_union", "right_union", "left_minus_right", "right_minus_left", "equal_values"):
            _try_exact_rule(out, train, tests, f"panel_preserve_{operation}", lambda g, op=operation: panel_preserving_exact(g, op), 8, "struct_panel_preserve")

        # Block reductions and polyphase selectors inferred from shape ratios.
        ratios: set[Tuple[int, int]] = set(); valid = True
        for x, y in train:
            if x.shape[0] % y.shape[0] or x.shape[1] % y.shape[1]: valid = False; break
            ratios.add((x.shape[0] // y.shape[0], x.shape[1] // y.shape[1]))
        if valid and len(ratios) == 1:
            rh, cw = next(iter(ratios))
            if rh >= 1 and cw >= 1 and (rh, cw) != (1, 1) and rh * cw <= 100:
                for mode in ("top_left", "top_right", "bottom_left", "bottom_right", "center", "majority", "majority_nonbg", "first_nonbg", "unique_nonbg"):
                    _try_exact_rule(out, train, tests, f"block_{rh}x{cw}_{mode}", lambda g, a=rh, b=cw, m=mode: block_reduce_exact(g, a, b, m), 7, "struct_block_reduce")
                for ro in range(rh):
                    for co in range(cw):
                        _try_exact_rule(out, train, tests, f"phase_{rh}x{cw}_{ro}_{co}", lambda g, a=rh, b=cw, r=ro, c=co: polyphase_extract_exact(g, a, b, r, c), 6, "struct_polyphase_extract")
                # Learn count -> output color at the block level.
                count_map: Dict[int, int] = {}; map_valid = True
                for x, y in train:
                    bg = infer_bg(x)
                    for i in range(y.shape[0]):
                        for j in range(y.shape[1]):
                            block = x[i * rh:(i + 1) * rh, j * cw:(j + 1) * cw]
                            key, val = int(np.count_nonzero(block != bg)), int(y[i, j])
                            if key in count_map and count_map[key] != val: map_valid = False; break
                            count_map[key] = val
                        if not map_valid: break
                    if not map_valid: break
                if map_valid and count_map:
                    _try_exact_rule(out, train, tests, f"block_count_map_{rh}x{cw}", lambda g, a=rh, b=cw, mp=dict(count_map): block_reduce_exact(g, a, b, "count_map", mp), 8 + len(count_map), "struct_block_count")

    if same_shape:
        # Keep or remove one structurally selected packet.
        for connectivity in (4, 8):
            for separate in (False, True):
                for selector in ("largest", "smallest", "leftmost", "rightmost", "topmost", "bottommost", "densest", "sparsest"):
                    for keep in (True, False):
                        _try_exact_rule(out, train, tests, f"{'keep' if keep else 'remove'}_{selector}_c{connectivity}_{int(separate)}", lambda g, s=selector, c=connectivity, sep=separate, k=keep: keep_generic_object(g, s, c, sep, k), 8, "struct_object_filter")

        # Drawing and completion rules only when the output adds foreground.
        adds_support = all(np.all(~_foreground_mask(x) | _foreground_mask(y)) for x, y in train)
        if adds_support:
            line_colors: List[Optional[int]] = [None] + colors[:3]
            for mode in ("h", "v", "hv", "diag", "all"):
                for grouped in (True, False):
                    for color in line_colors:
                        _try_exact_rule(out, train, tests, f"connect_{mode}_{int(grouped)}_{color}", lambda g, m=mode, gp=grouped, c=color: connect_markers_exact(g, m, gp, c), 9, "struct_line_draw")
            for fill in (False, True):
                for color in line_colors:
                    _try_exact_rule(out, train, tests, f"bbox_{'fill' if fill else 'outline'}_{color}", lambda g, f=fill, c=color: bbox_draw_exact(g, f, c), 8, "struct_bbox_draw")

    # Color-frequency packet selection can change or preserve dimensions.
    for selector in ("rarest", "most"):
        for crop in (False, True):
            for color in [None] + colors[:3]:
                _try_exact_rule(out, train, tests, f"frequency_{selector}_{int(crop)}_{color}", lambda g, s=selector, cr=crop, c=color: frequency_select_exact(g, s, cr, c), 7, "struct_frequency_select")

    out.extend(relational_object_rules(train, tests))
    out.extend(_object_attribute_candidates(train, tests))

    # Version 0.4 model families: generic exact-fit extensions derived from
    # recurring public-training residual classes. Each family is admitted only
    # when it reproduces every demonstration exactly.
    out.extend(marker_shape_recolor_rules(train, tests))
    out.extend(enclosed_region_rules(train, tests))
    out.extend(periodic_resize_rules(train, tests))
    out.extend(kronecker_variant_rules(train, tests))
    out.extend(affine_index_tile_rules(train, tests))
    out.extend(object_chain_rules(train, tests))
    out.extend(object_shape_recolor_rules(train, tests))
    out.extend(periodic_stripe_rules(train, tests))

    # Unary count outputs.
    if all(len(np.unique(y)) == 1 for _, y in train):
        fill_colors = sorted({int(y.flat[0]) for _, y in train})
        if len(fill_colors) == 1:
            color = fill_colors[0]
            for measure in ("objects", "colored_objects", "colors", "cells"):
                for orientation in ("row", "col", "square"):
                    for connectivity in (4, 8):
                        _try_exact_rule(out, train, tests, f"count_{measure}_{orientation}_c{connectivity}", lambda g, m=measure, o=orientation, col=color, c=connectivity: solid_count_exact(g, m, o, col, c), 8, "struct_count")

    # Deduplicate candidates by family/name and prediction signature.
    dedup: List[RuleCandidate] = []; seen: set[Tuple[str, ...]] = set()
    for cand in sorted(out, key=lambda c: (c.complexity, c.family, c.name)):
        sig = tuple(canonical(g) for g in cand.grids)
        if sig in seen: continue
        seen.add(sig); dedup.append(cand)
    return dedup


def _neighbor_count_map(grid: Array) -> Array:
    grid = sanitize_grid(grid)
    background = infer_bg(grid)
    mask = grid != background
    count = np.zeros_like(grid, dtype=np.int16)
    count[1:, :] += mask[:-1, :]
    count[:-1, :] += mask[1:, :]
    count[:, 1:] += mask[:, :-1]
    count[:, :-1] += mask[:, 1:]
    return count


def _residual_lookup_candidate(
    seed: RuleCandidate,
    train: List[Tuple[Array, Array]],
    tests: List[Array],
    mode: str,
    modulus: int = 1,
) -> Optional[RuleCandidate]:
    if len(seed.train_grids) != len(train) or len(seed.grids) != len(tests):
        return None
    mapping: Dict[Tuple[int, ...], int] = {}

    def keys(input_grid: Array, prediction: Array) -> Optional[List[List[Tuple[int, ...]]]]:
        prediction = sanitize_grid(prediction)
        input_grid = sanitize_grid(input_grid)
        if mode in {"input_color", "object_context"} and input_grid.shape != prediction.shape:
            return None
        neighbor = _neighbor_count_map(input_grid) if mode == "object_context" else None
        output: List[List[Tuple[int, ...]]] = []
        for row in range(prediction.shape[0]):
            row_keys: List[Tuple[int, ...]] = []
            for column in range(prediction.shape[1]):
                predicted_color = int(prediction[row, column])
                if mode == "color":
                    key = (predicted_color,)
                elif mode == "input_color":
                    key = (int(input_grid[row, column]), predicted_color)
                elif mode == "polyphase":
                    key = (row % modulus, column % modulus, predicted_color)
                elif mode == "input_polyphase":
                    if input_grid.shape != prediction.shape:
                        return None
                    key = (row % modulus, column % modulus, int(input_grid[row, column]), predicted_color)
                elif mode == "object_context":
                    assert neighbor is not None
                    key = (int(input_grid[row, column]), predicted_color, int(neighbor[row, column]))
                else:
                    return None
                row_keys.append(key)
            output.append(row_keys)
        return output

    train_key_grids: List[List[List[Tuple[int, ...]]]] = []
    for prediction, (input_grid, target) in zip(seed.train_grids, train):
        prediction = sanitize_grid(prediction)
        target = sanitize_grid(target)
        if prediction.shape != target.shape:
            return None
        key_grid = keys(input_grid, prediction)
        if key_grid is None:
            return None
        train_key_grids.append(key_grid)
        for row in range(target.shape[0]):
            for column in range(target.shape[1]):
                key = key_grid[row][column]
                value = int(target[row, column])
                previous = mapping.get(key)
                if previous is not None and previous != value:
                    return None
                mapping[key] = value
    if not mapping or len(mapping) > 48:
        return None

    def apply(input_grid: Array, prediction: Array) -> Array:
        prediction = sanitize_grid(prediction)
        key_grid = keys(input_grid, prediction)
        if key_grid is None:
            return prediction.copy()
        output = prediction.copy()
        for row in range(output.shape[0]):
            for column in range(output.shape[1]):
                output[row, column] = mapping.get(key_grid[row][column], int(output[row, column]))
        return output

    refined_train = tuple(
        apply(input_grid, prediction)
        for prediction, (input_grid, _) in zip(seed.train_grids, train)
    )
    if not all(exact(prediction, target) for prediction, (_, target) in zip(refined_train, train)):
        return None
    refined_tests = [apply(input_grid, prediction) for input_grid, prediction in zip(tests, seed.grids)]
    if all(exact(before, after) for before, after in zip(seed.train_grids, refined_train)):
        return None
    suffix = f"_{modulus}" if "polyphase" in mode else ""
    return RuleCandidate(
        name=f"residual:{mode}{suffix}:after:{seed.name}",
        grids=refined_tests,
        train_error=0,
        complexity=seed.complexity + 3 + len(mapping),
        family=f"residual_{mode}",
        train_grids=refined_train,
        metadata={"seed": seed.name, "lookup_size": len(mapping), "modulus": modulus},
    )


def residual_refinement_rules(
    base_candidates: List[RuleCandidate],
    train: List[Tuple[Array, Array]],
    tests: List[Array],
    maximum_seeds: int = 10,
) -> List[RuleCandidate]:
    """Refine the best candidate residuals through typed local lookup programs.

    The lookup grammar is deliberately restricted to global color, input-color,
    local object context, and low-modulus polyphase keys. It cannot memorize an
    arbitrary coordinate table, and every retained refinement must still
    reproduce every demonstration exactly.
    """
    seeds = sorted(
        base_candidates,
        key=lambda candidate: (candidate.train_error, candidate.complexity, candidate.family, candidate.name),
    )[:maximum_seeds]
    output: List[RuleCandidate] = []
    for seed in seeds:
        for mode in ("color", "input_color", "object_context"):
            candidate = _residual_lookup_candidate(seed, train, tests, mode)
            if candidate is not None:
                output.append(candidate)
        for modulus in (2, 3, 4):
            for mode in ("polyphase", "input_polyphase"):
                candidate = _residual_lookup_candidate(seed, train, tests, mode, modulus)
                if candidate is not None:
                    output.append(candidate)
    deduplicated: List[RuleCandidate] = []
    seen: set[Tuple[str, ...]] = set()
    for candidate in sorted(output, key=lambda item: (item.complexity, item.family, item.name)):
        signature = tuple(canonical(grid) for grid in candidate.grids)
        if signature in seen:
            continue
        seen.add(signature)
        deduplicated.append(candidate)
    return deduplicated


def collect_base_candidates(train: List[Tuple[Array, Array]], tests: List[Array], time_limit: float) -> List[RuleCandidate]:
    start_time = time.time()
    candidates: List[RuleCandidate] = []
    candidates.extend(learned_transform_rules(train, tests))
    candidates.extend(object_color_frequency_rules(train, tests))
    candidates.extend(synthesize_program_rules(train, tests, start_time, time_limit))

    # Basic fallbacks always included.
    candidates.append(candidate_from_function("fallback_input", lambda g: g.copy(), train, tests, 100, "fallback"))
    candidates.append(candidate_from_function("fallback_crop_bbox", crop_bbox_non_bg, train, tests, 100, "fallback"))
    for color in [0, majority_color(train[-1][1])]:
        grids = [np.full_like(t, color) for t in tests]
        err = sum(grid_error(np.full_like(x, color), y) for x, y in train)
        train_grids = tuple(np.full_like(x, color) for x, _ in train)
        candidates.append(RuleCandidate(f"fallback_full_{color}_input_shape", grids, err, 120, "fallback", train_grids=train_grids))
    return candidates


def collect_candidates(train: List[Tuple[Array, Array]], tests: List[Array], time_limit: float) -> List[RuleCandidate]:
    """Return base, residual-refined, projector, and structural proposal channels."""
    base = collect_base_candidates(train, tests, time_limit)
    refined = residual_refinement_rules(base, train, tests)
    return base + refined + projector_exact_rules(train, tests) + structural_exact_rules(train, tests)

def legacy_rank_predictions(candidates: List[RuleCandidate], test_index: int, k: int = 2) -> List[Array]:
    """Retained deterministic MDL ranker for regression comparisons."""
    records: Dict[str, Dict[str, object]] = {}
    for cand in candidates:
        if test_index >= len(cand.grids):
            continue
        g = sanitize_grid(cand.grids[test_index])
        key = canonical(g)
        if key not in records:
            records[key] = {
                "grid": g,
                "best_score": cand.score,
                "best_error": cand.train_error,
                "best_complexity": cand.complexity,
                "votes": 0,
                "families": set(),
                "names": [],
            }
        rec = records[key]
        rec["votes"] = int(rec["votes"]) + 1
        rec["families"].add(cand.family)
        rec["names"].append(cand.name)
        if cand.score < float(rec["best_score"]):
            rec["best_score"] = cand.score
            rec["best_error"] = cand.train_error
            rec["best_complexity"] = cand.complexity
            rec["grid"] = g
    ranked = []
    for key, rec in records.items():
        votes = int(rec["votes"])
        family_bonus = len(rec["families"])
        rank_score = float(rec["best_score"]) - 0.02 * votes - 0.03 * family_bonus
        ranked.append((rank_score, int(rec["best_error"]), int(rec["best_complexity"]), -votes, key, rec["grid"]))
    ranked.sort(key=lambda z: (z[0], z[1], z[2], z[3], z[4]))
    preds = [r[-1] for r in ranked[:k]]
    while len(preds) < k:
        preds.append(preds[0].copy() if preds else np.zeros((1, 1), dtype=np.int16))
    return preds[:k]


def deduplicate_candidates(candidates: List[RuleCandidate]) -> List[RuleCandidate]:
    """Remove exact duplicate program records without collapsing family evidence."""
    seen: set[Tuple[str, str, Tuple[str, ...], Tuple[str, ...]]] = set()
    output: List[RuleCandidate] = []
    for candidate in candidates:
        key = (
            candidate.family,
            candidate.name,
            tuple(canonical(grid) for grid in candidate.train_grids),
            tuple(canonical(grid) for grid in candidate.grids),
        )
        if key in seen:
            continue
        seen.add(key)
        output.append(candidate)
    return output


def _candidate_family_priority(candidate: RuleCandidate) -> tuple[int, int, str, str]:
    """Order candidate families by expected structural generality.

    Exact residual lookups are useful proposal refinements, but they are also
    the easiest exact-fit programs to over-specialize to a few demonstrations.
    General typed operators therefore receive portfolio coverage before local
    residual tables.  The Bayesian posterior remains responsible for the final
    probability assignment.
    """
    family = candidate.family.lower()
    if family.startswith("residual_"):
        tier = 3
    elif family in {"fallback", "program"} or family.startswith("program"):
        tier = 2
    elif family.startswith("struct_") or family.startswith("projector"):
        tier = 0
    else:
        tier = 1
    return (tier, candidate.complexity, candidate.family, candidate.name)


def prune_candidates_for_bayesian(
    candidates: List[RuleCandidate],
    maximum: int = 36,
    maximum_residual_per_family: int = 2,
) -> List[RuleCandidate]:
    """Build a family-diverse posterior portfolio.

    Multi-atlas scoring is more expensive than primitive execution, so the
    Bayesian stage receives a bounded portfolio.  The bound is applied by
    round-robin family coverage rather than a global complexity sort.  This
    prevents a large set of exact but highly local residual tables from
    evicting typed projector, object, panel, or geometry programs.
    """
    exact_candidates = sorted(
        (candidate for candidate in candidates if candidate.train_error == 0),
        key=_candidate_family_priority,
    )
    approximate = sorted(
        (candidate for candidate in candidates if candidate.train_error != 0),
        key=lambda candidate: (candidate.train_error, *_candidate_family_priority(candidate)),
    )
    selected: List[RuleCandidate] = []
    prediction_seen: set[Tuple[str, ...]] = set()
    residual_family_counts: Dict[str, int] = {}

    def add(candidate: RuleCandidate) -> bool:
        signature = tuple(canonical(grid) for grid in candidate.grids)
        if signature in prediction_seen:
            return False
        if candidate.family.startswith("residual_"):
            count = residual_family_counts.get(candidate.family, 0)
            if count >= maximum_residual_per_family:
                return False
            residual_family_counts[candidate.family] = count + 1
        prediction_seen.add(signature)
        selected.append(candidate)
        return True

    # First pass: one exact representative from every family.  Families are
    # ordered so reusable typed operators are covered before local lookup
    # refinements.
    exact_by_family: Dict[str, List[RuleCandidate]] = {}
    for candidate in exact_candidates:
        exact_by_family.setdefault(candidate.family, []).append(candidate)
    ordered_families = sorted(
        exact_by_family,
        key=lambda family: _candidate_family_priority(exact_by_family[family][0]),
    )
    for family in ordered_families:
        add(exact_by_family[family][0])
        if len(selected) >= maximum:
            return selected

    # Second pass: round-robin additional exact predictions.  This preserves
    # ambiguity within a family without allowing one family to consume the
    # entire posterior budget.
    depth = 1
    while len(selected) < maximum:
        added = False
        for family in ordered_families:
            family_candidates = exact_by_family[family]
            if depth < len(family_candidates):
                added = add(family_candidates[depth]) or added
                if len(selected) >= maximum:
                    return selected
        if not added and all(depth >= len(exact_by_family[family]) for family in ordered_families):
            break
        depth += 1

    # Preserve one approximate representative of each remaining family, then
    # fill the Pareto frontier by train error and complexity.
    approximate_family_seen: set[str] = set()
    for candidate in approximate:
        if candidate.family in approximate_family_seen:
            continue
        approximate_family_seen.add(candidate.family)
        add(candidate)
        if len(selected) >= maximum:
            return selected
    for candidate in approximate:
        add(candidate)
        if len(selected) >= maximum:
            break
    return selected


_DEFAULT_LASM_MODEL: Optional[BayesianProjectorResolvedLargeSignalModel] = None
_DEFAULT_LASM_CALIBRATION_PATH: Optional[str] = None


def default_lasm_model(calibration_path: Optional[str] = None) -> BayesianProjectorResolvedLargeSignalModel:
    global _DEFAULT_LASM_MODEL, _DEFAULT_LASM_CALIBRATION_PATH
    normalized = None if calibration_path is None else str(Path(calibration_path).resolve())
    if _DEFAULT_LASM_MODEL is None or normalized != _DEFAULT_LASM_CALIBRATION_PATH:
        calibration = load_calibration(normalized)
        _DEFAULT_LASM_MODEL = BayesianProjectorResolvedLargeSignalModel(calibration=calibration)
        _DEFAULT_LASM_CALIBRATION_PATH = normalized
    return _DEFAULT_LASM_MODEL


def solve_task(
    task: dict,
    time_limit: float = DEFAULT_TIME_LIMIT_PER_TASK,
    *,
    lasm_model: Optional[BayesianProjectorResolvedLargeSignalModel] = None,
    legacy_ranking: bool = False,
    diagnostics: Optional[Dict[str, object]] = None,
) -> List[Dict[str, Grid]]:
    train = [(as_array(p["input"]), as_array(p["output"])) for p in task.get("train", []) if "input" in p and "output" in p]
    tests = [as_array(p["input"]) for p in task.get("test", []) if "input" in p]
    if not tests:
        return []
    if not train:
        return [{"attempt_1": grid_to_list(t), "attempt_2": grid_to_list(crop_bbox_non_bg(t))} for t in tests]

    candidates = prune_candidates_for_bayesian(
        deduplicate_candidates(collect_candidates(train, tests, time_limit=time_limit))
    )
    if not candidates:
        return [{"attempt_1": grid_to_list(t), "attempt_2": grid_to_list(crop_bbox_non_bg(t))} for t in tests]

    if legacy_ranking:
        results = []
        for index in range(len(tests)):
            first, second = legacy_rank_predictions(candidates, index, k=2)
            results.append({"attempt_1": grid_to_list(first), "attempt_2": grid_to_list(second)})
        if diagnostics is not None:
            diagnostics.update({"mode": "legacy", "candidate_count": len(candidates)})
        return results

    model = lasm_model or default_lasm_model()
    try:
        posterior = model.fit_posterior(candidates, train, tests)
        results = []
        selected_diagnostics: List[List[Dict[str, object]]] = []
        for index in range(len(tests)):
            selected_outputs = model.select_output_posteriors(posterior, index, k=2)
            selected_grids = [output.grid for output in selected_outputs]
            if not selected_grids:
                selected_grids = [tests[index].copy()]
            while len(selected_grids) < 2:
                selected_grids.append(selected_grids[0].copy())
            first, second = selected_grids[:2]
            results.append({"attempt_1": grid_to_list(first), "attempt_2": grid_to_list(second)})
            selected_diagnostics.append([
                {
                    "attempt": attempt_index + 1,
                    "probability": output.probability,
                    "exact_fit_probability": output.exact_fit_probability,
                    "exact_fit_candidate_count": output.exact_fit_candidate_count,
                    "best_candidate_probability": output.best_candidate_probability,
                    "families": list(output.families),
                    "names": list(output.names),
                    "channel_probabilities": dict(output.channel_probabilities),
                    "shape": list(output.grid.shape),
                }
                for attempt_index, output in enumerate(selected_outputs[:2])
            ])
        if diagnostics is not None:
            exact_candidate_count = sum(candidate.train_error == 0 for candidate in candidates)
            family_counts = dict(Counter(candidate.family for candidate in candidates))
            diagnostics.update({
                "mode": "bayesian_pr_lasm",
                "candidate_count": len(candidates),
                "exact_fit_candidate_count": exact_candidate_count,
                "candidate_family_counts": family_counts,
                "calibration_version": model.calibration.model_version,
                "selected_attempts": selected_diagnostics,
                **posterior.diagnostics(),
            })
        return results
    except Exception as exc:
        # A schema-valid legacy fallback is preferable to losing the task in a
        # hard-isolated competition worker. The exception is retained in the
        # optional diagnostic record.
        results = []
        for index in range(len(tests)):
            first, second = legacy_rank_predictions(candidates, index, k=2)
            results.append({"attempt_1": grid_to_list(first), "attempt_2": grid_to_list(second)})
        if diagnostics is not None:
            diagnostics.update({
                "mode": "legacy_fallback",
                "candidate_count": len(candidates),
                "bayesian_error": f"{type(exc).__name__}: {exc}",
            })
        return results


# -------------------- Kaggle/file IO, validation, local scoring --------------------

ChallengeDict = Dict[str, dict]
SolutionDict = Dict[str, List[Grid]]


def _json_load(path: str | Path):
    with open(path, "r") as f:
        return json.load(f)


def _json_dump(obj, path: str | Path, compact: bool = True) -> None:
    path = Path(path)
    if str(path.parent) not in {"", "."}:
        path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w") as f:
        if compact:
            json.dump(obj, f, separators=(",", ":"))
        else:
            json.dump(obj, f, indent=2)


def _is_grid(x: object) -> bool:
    return isinstance(x, list) and len(x) > 0 and all(isinstance(row, list) and len(row) > 0 for row in x)


def _is_task_dict(v: object) -> bool:
    return isinstance(v, dict) and isinstance(v.get("train"), list) and isinstance(v.get("test"), list)


def load_tasks_from_path(path: str | Path) -> ChallengeDict:
    """Load ARC challenges from a Kaggle JSON file or a directory of per-task JSON files."""
    p = Path(path)
    if p.is_dir():
        tasks: ChallengeDict = {}
        for fp in sorted(p.glob("*.json")):
            name = fp.name.lower()
            if "solution" in name or "submission" in name:
                continue
            data = _json_load(fp)
            if _is_task_dict(data):
                tasks[fp.stem] = data
            elif isinstance(data, dict) and all(_is_task_dict(v) for v in data.values()):
                tasks.update({str(k): v for k, v in data.items()})
        if tasks:
            return tasks
        raise ValueError(f"No ARC task JSON files found in directory: {p}")

    data = _json_load(p)
    if isinstance(data, dict):
        if all(_is_task_dict(v) for v in data.values()):
            return {str(k): v for k, v in data.items()}
        if _is_task_dict(data):
            return {p.stem: data}
    raise ValueError(f"Could not parse ARC challenges from {p}")


def _normalize_solution_entry(value: object) -> List[Grid]:
    """Normalize common ARC solution encodings to a list of output grids."""
    if isinstance(value, dict):
        if "output" in value:
            return _normalize_solution_entry(value["output"])
        if "test" in value:
            return _normalize_solution_entry(value["test"])
        return []
    if _is_grid(value):
        # A single grid is a list of rows. A list of grids is list[list[list[int]]].
        if all(all(isinstance(x, int) for x in row) for row in value):
            return [value]  # type: ignore[list-item]
    if isinstance(value, list):
        grids: List[Grid] = []
        for item in value:
            if isinstance(item, dict) and "output" in item:
                item = item["output"]
            if _is_grid(item):
                grids.append(item)  # type: ignore[arg-type]
        return grids
    return []


def load_solutions_from_path(path: str | Path) -> SolutionDict:
    """Load ARC-AGI-2 solutions JSON.

    Expected format is normally:
        {"task_id": [grid_for_test_0, grid_for_test_1, ...], ...}
    The parser also accepts a few older/local fixture variants.
    """
    data = _json_load(path)
    if not isinstance(data, dict):
        raise ValueError(f"Solutions file must contain a dictionary: {path}")
    out: SolutionDict = {}
    for task_id, value in data.items():
        out[str(task_id)] = _normalize_solution_entry(value)
    return out


def solution_from_embedded_outputs(tasks: ChallengeDict) -> SolutionDict:
    sols: SolutionDict = {}
    for task_id, task in tasks.items():
        grids: List[Grid] = []
        for pair in task.get("test", []):
            if isinstance(pair, dict) and "output" in pair:
                grids.append(pair["output"])
        if grids:
            sols[task_id] = grids
    return sols


def attach_solutions(tasks: ChallengeDict, solutions: SolutionDict) -> ChallengeDict:
    """Return a copy of tasks with test outputs attached for local debugging/scoring.

    The solver itself ignores test outputs, so attaching them is only for reporting.
    """
    out: ChallengeDict = {}
    for task_id, task in tasks.items():
        new_task = {"train": list(task.get("train", [])), "test": []}
        sol = solutions.get(task_id, [])
        for i, pair in enumerate(task.get("test", [])):
            p = dict(pair)
            if i < len(sol):
                p["output"] = sol[i]
            new_task["test"].append(p)
        out[task_id] = new_task
    return out


def validate_grid(grid: object, *, name: str = "grid") -> List[str]:
    errors: List[str] = []
    if not isinstance(grid, list) or not grid:
        return [f"{name}: grid must be a non-empty list of rows"]
    if not all(isinstance(row, list) and row for row in grid):
        return [f"{name}: each row must be a non-empty list"]
    h, w = len(grid), len(grid[0])
    if not (1 <= h <= MAX_SIDE and 1 <= w <= MAX_SIDE):
        errors.append(f"{name}: grid shape {h}x{w} outside 1..{MAX_SIDE}")
    for r, row in enumerate(grid):
        if len(row) != w:
            errors.append(f"{name}: row {r} has width {len(row)}, expected {w}")
            break
        for c, val in enumerate(row):
            if isinstance(val, bool) or not isinstance(val, int) or not (0 <= val <= 9):
                errors.append(f"{name}: cell ({r},{c})={val!r} is not an integer in [0,9]")
                return errors
    return errors


def validate_submission(submission: dict, tasks: ChallengeDict, *, strict_keys: bool = True) -> List[str]:
    """Validate Kaggle submission format: task_id -> list of {attempt_1, attempt_2}."""
    errors: List[str] = []
    if not isinstance(submission, dict):
        return ["submission must be a dictionary: task_id -> list of predictions"]
    task_ids = set(tasks.keys())
    sub_ids = set(str(k) for k in submission.keys())
    missing = sorted(task_ids - sub_ids)
    extra = sorted(sub_ids - task_ids)
    if missing:
        errors.append(f"missing predictions for {len(missing)} task(s), first few: {missing[:5]}")
    if strict_keys and extra:
        errors.append(f"submission has {len(extra)} extra task id(s), first few: {extra[:5]}")
    for task_id, task in tasks.items():
        preds = submission.get(task_id)
        expected_n = len(task.get("test", []))
        if not isinstance(preds, list):
            errors.append(f"{task_id}: predictions must be a list")
            continue
        if len(preds) != expected_n:
            errors.append(f"{task_id}: got {len(preds)} prediction entries, expected {expected_n}")
            continue
        for i, entry in enumerate(preds):
            if not isinstance(entry, dict):
                errors.append(f"{task_id}[{i}]: prediction must be a dict with attempt_1 and attempt_2")
                continue
            for key in ["attempt_1", "attempt_2"]:
                if key not in entry:
                    errors.append(f"{task_id}[{i}]: missing {key}")
                else:
                    errors.extend(validate_grid(entry[key], name=f"{task_id}[{i}].{key}"))
            if len(errors) > 50:
                return errors[:50]
    return errors


def score_submission(submission: dict, solutions: SolutionDict) -> Dict[str, object]:
    """Return exact-match score using Kaggle's two-attempt rule."""
    ok = 0
    total = 0
    a1_ok = 0
    a2_ok = 0
    per_task: Dict[str, int] = {}
    for task_id, true_grids in solutions.items():
        preds = submission.get(task_id, []) if isinstance(submission, dict) else []
        task_ok = 0
        for i, y_grid in enumerate(true_grids):
            total += 1
            if i >= len(preds) or not isinstance(preds[i], dict):
                continue
            y = as_array(y_grid)
            p1 = as_array(preds[i].get("attempt_1", [[0]]))
            p2 = as_array(preds[i].get("attempt_2", [[0]]))
            hit1 = exact(p1, y)
            hit2 = exact(p2, y)
            hit = hit1 or hit2
            ok += int(hit)
            a1_ok += int(hit1)
            a2_ok += int(hit2)
            task_ok += int(hit)
        per_task[task_id] = task_ok
    return {
        "score": ok / total if total else None,
        "ok": ok,
        "total": total,
        "attempt_1_ok": a1_ok,
        "attempt_2_ok": a2_ok,
        "per_task": per_task,
    }



ARC_HTML_COLORS = (
    "#000000",
    "#0074D9",
    "#FF4136",
    "#2ECC40",
    "#FFDC00",
    "#AAAAAA",
    "#F012BE",
    "#FF851B",
    "#7FDBFF",
    "#870C25",
)


def _color_counts(grid: Array) -> Dict[str, int]:
    values, counts = np.unique(sanitize_grid(grid), return_counts=True)
    return {str(int(value)): int(count) for value, count in zip(values, counts)}


def compare_prediction(expected: Array, prediction: Array, max_mismatches: int = 30) -> Dict[str, object]:
    expected = sanitize_grid(expected)
    prediction = sanitize_grid(prediction)
    shape_match = expected.shape == prediction.shape
    record: Dict[str, object] = {
        "exact": bool(shape_match and np.array_equal(expected, prediction)),
        "shape_match": shape_match,
        "expected_shape": list(expected.shape),
        "prediction_shape": list(prediction.shape),
        "expected_color_counts": _color_counts(expected),
        "prediction_color_counts": _color_counts(prediction),
    }
    overlap_height = min(expected.shape[0], prediction.shape[0])
    overlap_width = min(expected.shape[1], prediction.shape[1])
    overlap_expected = expected[:overlap_height, :overlap_width]
    overlap_prediction = prediction[:overlap_height, :overlap_width]
    overlap_correct = int(np.count_nonzero(overlap_expected == overlap_prediction))
    overlap_total = int(overlap_height * overlap_width)
    record["overlap_correct_cells"] = overlap_correct
    record["overlap_total_cells"] = overlap_total
    record["overlap_cell_accuracy"] = overlap_correct / overlap_total if overlap_total else 0.0
    if not shape_match:
        record.update({
            "correct_cells": overlap_correct,
            "wrong_cells": None,
            "total_cells": int(expected.size),
            "cell_accuracy": 0.0,
            "mismatch_bbox": None,
            "first_mismatches": [],
            "color_confusion": [],
        })
        return record

    mismatch = expected != prediction
    coordinates = np.argwhere(mismatch)
    wrong_cells = int(coordinates.shape[0])
    correct_cells = int(expected.size - wrong_cells)
    first_mismatches = [
        {
            "row": int(row),
            "column": int(column),
            "expected": int(expected[row, column]),
            "predicted": int(prediction[row, column]),
        }
        for row, column in coordinates[:max_mismatches]
    ]
    confusion = Counter(
        (int(expected[row, column]), int(prediction[row, column]))
        for row, column in coordinates
    )
    confusion_rows = [
        {"expected": expected_color, "predicted": predicted_color, "count": count}
        for (expected_color, predicted_color), count in sorted(
            confusion.items(),
            key=lambda item: (-item[1], item[0][0], item[0][1]),
        )
    ]
    mismatch_bbox = None
    if coordinates.size:
        minimum = coordinates.min(axis=0)
        maximum = coordinates.max(axis=0)
        mismatch_bbox = [int(minimum[0]), int(minimum[1]), int(maximum[0]), int(maximum[1])]
    record.update({
        "correct_cells": correct_cells,
        "wrong_cells": wrong_cells,
        "total_cells": int(expected.size),
        "cell_accuracy": correct_cells / max(1, int(expected.size)),
        "mismatch_bbox": mismatch_bbox,
        "first_mismatches": first_mismatches,
        "color_confusion": confusion_rows,
    })
    return record



def residual_category_grid(expected: Array, prediction: Array) -> Array:
    """Return an ARC-colored diagnostic residual map.

    Codes are diagnostic rather than task colors:
      0 correct, 1 extra predicted support, 2 missing expected support,
      4 wrong nonbackground color, 8 shape-only region.
    """
    expected = sanitize_grid(expected)
    prediction = sanitize_grid(prediction)
    height = max(expected.shape[0], prediction.shape[0])
    width = max(expected.shape[1], prediction.shape[1])
    residual = np.full((height, width), 8, dtype=np.int16)
    overlap_height = min(expected.shape[0], prediction.shape[0])
    overlap_width = min(expected.shape[1], prediction.shape[1])
    expected_overlap = expected[:overlap_height, :overlap_width]
    prediction_overlap = prediction[:overlap_height, :overlap_width]
    expected_background = infer_bg(expected)
    prediction_background = infer_bg(prediction)
    overlap = np.zeros((overlap_height, overlap_width), dtype=np.int16)
    equal = expected_overlap == prediction_overlap
    expected_support = expected_overlap != expected_background
    prediction_support = prediction_overlap != prediction_background
    overlap[~equal & ~expected_support & prediction_support] = 1
    overlap[~equal & expected_support & ~prediction_support] = 2
    overlap[~equal & expected_support & prediction_support] = 4
    # Cases where the inferred backgrounds differ but neither value is treated
    # as support are still wrong colors.
    overlap[~equal & ~expected_support & ~prediction_support] = 4
    residual[:overlap_height, :overlap_width] = overlap
    return residual


def residual_category_counts(residual: Array) -> Dict[str, int]:
    values = sanitize_grid(residual)
    labels = {0: "correct", 1: "extra", 2: "missing", 4: "wrong_color", 8: "shape_only"}
    return {
        labels[value]: int(np.count_nonzero(values == value))
        for value in labels
        if np.any(values == value)
    }


def summarize_transformation(input_grid: Array, expected: Array) -> Dict[str, object]:
    input_grid = sanitize_grid(input_grid)
    expected = sanitize_grid(expected)
    summary: Dict[str, object] = {
        "input_shape": list(input_grid.shape),
        "output_shape": list(expected.shape),
        "shape_changed": input_grid.shape != expected.shape,
        "input_color_counts": _color_counts(input_grid),
        "output_color_counts": _color_counts(expected),
        "input_object_count_4": len(generic_components(input_grid, 4, True)),
        "output_object_count_4": len(generic_components(expected, 4, True)),
        "input_object_count_8": len(generic_components(input_grid, 8, True)),
        "output_object_count_8": len(generic_components(expected, 8, True)),
    }
    if input_grid.shape != expected.shape:
        input_area = input_grid.size
        output_area = expected.size
        if output_area > input_area:
            transformation_class = "expansion_or_construction"
        elif output_area < input_area:
            transformation_class = "compression_or_extraction"
        else:
            transformation_class = "shape_relayout"
        summary["transformation_class"] = transformation_class
        return summary
    input_background = infer_bg(input_grid)
    output_background = infer_bg(expected)
    input_support = input_grid != input_background
    output_support = expected != output_background
    added = int(np.count_nonzero(~input_support & output_support))
    removed = int(np.count_nonzero(input_support & ~output_support))
    recolored = int(np.count_nonzero(input_support & output_support & (input_grid != expected)))
    unchanged = int(np.count_nonzero(input_grid == expected))
    summary.update({
        "support_added_cells": added,
        "support_removed_cells": removed,
        "recolored_existing_cells": recolored,
        "unchanged_cells": unchanged,
    })
    if added and not removed and not recolored:
        transformation_class = "drawing_or_completion"
    elif removed and not added and not recolored:
        transformation_class = "deletion_or_selection"
    elif recolored and not added and not removed:
        transformation_class = "recolor"
    elif added == removed and added > 0 and recolored == 0:
        transformation_class = "movement_or_permutation"
    elif added or removed or recolored:
        transformation_class = "mixed_edit"
    else:
        transformation_class = "identity"
    summary["transformation_class"] = transformation_class
    return summary


def _ascii_grid(grid: Array) -> str:
    return "\n".join("".join(str(int(value)) for value in row) for row in sanitize_grid(grid))


def _grid_html(grid: Array, title: str, expected: Optional[Array] = None) -> str:
    values = sanitize_grid(grid)
    expected_values = None if expected is None or sanitize_grid(expected).shape != values.shape else sanitize_grid(expected)
    rows: List[str] = []
    for row in range(values.shape[0]):
        cells: List[str] = []
        for column in range(values.shape[1]):
            value = int(values[row, column])
            mismatch = expected_values is not None and int(expected_values[row, column]) != value
            css_class = "cell mismatch" if mismatch else "cell"
            cell_title = f"r={row}, c={column}, value={value}"
            if mismatch:
                cell_title += f", expected={int(expected_values[row, column])}"
            cells.append(
                f'<td class="{css_class}" style="background:{ARC_HTML_COLORS[value]}" title="{html.escape(cell_title)}"></td>'
            )
        rows.append("<tr>" + "".join(cells) + "</tr>")
    return (
        '<div class="grid-card">'
        f'<h4>{html.escape(title)}</h4>'
        f'<div class="shape">{values.shape[0]} × {values.shape[1]}</div>'
        '<table class="arc-grid" cellspacing="0" cellpadding="0">'
        + "".join(rows)
        + "</table>"
        f'<pre>{html.escape(_ascii_grid(values))}</pre>'
        "</div>"
    )



def _svg_grid(
    grid: Array,
    title: str,
    x: int,
    y: int,
    *,
    expected: Optional[Array] = None,
    cell_size: int = 12,
) -> str:
    values = sanitize_grid(grid)
    expected_values = None
    if expected is not None:
        candidate = sanitize_grid(expected)
        if candidate.shape == values.shape:
            expected_values = candidate
    parts = [
        f'<g transform="translate({x},{y})">',
        f'<text x="0" y="14" font-size="14" font-weight="700">{html.escape(title)}</text>',
        f'<text x="0" y="31" font-size="11" opacity="0.75">{values.shape[0]} × {values.shape[1]}</text>',
    ]
    top = 40
    for row in range(values.shape[0]):
        for column in range(values.shape[1]):
            value = int(values[row, column])
            mismatch = expected_values is not None and int(expected_values[row, column]) != value
            stroke = '#ff1744' if mismatch else '#ffffff44'
            stroke_width = 2 if mismatch else 0.5
            title_text = f'r={row}, c={column}, value={value}'
            if mismatch:
                title_text += f', expected={int(expected_values[row, column])}'
            parts.append(
                f'<rect x="{column * cell_size}" y="{top + row * cell_size}" '
                f'width="{cell_size}" height="{cell_size}" fill="{ARC_HTML_COLORS[value]}" '
                f'stroke="{stroke}" stroke-width="{stroke_width}"><title>{html.escape(title_text)}</title></rect>'
            )
    parts.append('</g>')
    return ''.join(parts)


def _task_diagnostic_svg(record: Dict[str, object]) -> str:
    card_width = 400
    row_height = 430
    training = list(record.get('training_examples', []))
    width = card_width * 4
    height = 90 + row_height * (len(training) + 1)
    expected = as_array(record['expected'])
    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">',
        '<rect width="100%" height="100%" fill="#f8f8f8"/>',
        '<style>text{font-family:Inter,Segoe UI,Arial,sans-serif;fill:#111}</style>',
        f'<text x="20" y="30" font-size="22" font-weight="700">{html.escape(str(record["task_id"]))}[{int(record["test_index"])}] diagnostic</text>',
        f'<text x="20" y="55" font-size="14">Exact ARC result: {"SOLVED" if record.get("solved") else "MISS"}; best cell agreement: {float(record.get("best_cell_accuracy", 0.0)):.3%}</text>',
    ]
    y = 75
    for number, pair in enumerate(training, 1):
        parts.append(f'<text x="20" y="{y + 18}" font-size="16" font-weight="700">Training example {number}</text>')
        parts.append(_svg_grid(as_array(pair['input']), 'Input', 20, y + 25))
        parts.append(_svg_grid(as_array(pair['output']), 'Output', card_width + 20, y + 25))
        y += row_height
    parts.append(f'<text x="20" y="{y + 18}" font-size="16" font-weight="700">Held-out problem and expected solution</text>')
    parts.append(_svg_grid(as_array(record['test_input']), 'Test input', 20, y + 25))
    parts.append(_svg_grid(expected, 'Expected solution', card_width + 20, y + 25))
    parts.append(_svg_grid(as_array(record['attempt_1']), 'Attempt 1', card_width * 2 + 20, y + 25, expected=expected))
    parts.append(_svg_grid(as_array(record['attempt_2']), 'Attempt 2', card_width * 3 + 20, y + 25, expected=expected))
    parts.append('</svg>')
    return ''.join(parts)


def _diagnostic_css() -> str:
    return """
:root { color-scheme: light dark; font-family: Inter, Segoe UI, Arial, sans-serif; }
body { margin: 24px; max-width: 1600px; }
a { color: #4c9aff; }
table.summary { border-collapse: collapse; width: 100%; }
table.summary th, table.summary td { border: 1px solid #7776; padding: 6px 8px; text-align: left; }
.metric-good { color: #2eaf62; font-weight: 700; }
.metric-bad { color: #e34b4b; font-weight: 700; }
.grid-row { display: flex; flex-wrap: wrap; gap: 14px; align-items: flex-start; margin: 10px 0 22px; }
.grid-card { border: 1px solid #7776; border-radius: 8px; padding: 8px; background: #8881; }
.grid-card h4 { margin: 0 0 4px; }
.shape { font-size: 12px; opacity: .75; margin-bottom: 6px; }
.arc-grid { border-collapse: collapse; background: #111; }
.arc-grid .cell { width: 14px; height: 14px; border: 1px solid #ffffff28; padding: 0; }
.arc-grid .mismatch { outline: 2px solid #ff1744; outline-offset: -2px; }
pre { font-size: 10px; line-height: 1.05; max-height: 260px; overflow: auto; background: #0002; padding: 6px; }
details { border: 1px solid #7775; border-radius: 8px; padding: 8px 12px; margin: 10px 0; }
code { white-space: pre-wrap; }
"""


def _posterior_task_record(posterior_diagnostics: Optional[Dict[str, object]], task_id: str) -> Dict[str, object]:
    if not posterior_diagnostics:
        return {}
    tasks = posterior_diagnostics.get("tasks") if isinstance(posterior_diagnostics, dict) else None
    if isinstance(tasks, dict):
        value = tasks.get(task_id, {})
        return value if isinstance(value, dict) else {}
    value = posterior_diagnostics.get(task_id, {}) if isinstance(posterior_diagnostics, dict) else {}
    return value if isinstance(value, dict) else {}



def diagnose_problem_solution(record: Dict[str, object]) -> Dict[str, object]:
    """Convert residual evidence into an auditable failure-stage diagnosis."""
    if bool(record.get("solved")):
        return {
            "failure_stage": "solved",
            "severity": "none",
            "likely_missing_families": [],
            "explanation": "At least one attempt is an exact ARC match.",
        }
    posterior = record.get("posterior") if isinstance(record.get("posterior"), dict) else {}
    selected_attempts = record.get("selected_attempts") if isinstance(record.get("selected_attempts"), list) else []
    selected_exact_counts = [int(value.get("exact_fit_candidate_count", 0) or 0) for value in selected_attempts if isinstance(value, dict)]
    exact_fit_count = max(selected_exact_counts, default=int(posterior.get("exact_fit_candidate_count", 0) or 0))
    transformation = record.get("transformation") if isinstance(record.get("transformation"), dict) else {}
    transformation_class = str(transformation.get("transformation_class", "unknown"))
    best_accuracy = float(record.get("best_cell_accuracy", 0.0) or 0.0)
    shape_match = bool(
        record.get("attempt_1_comparison", {}).get("shape_match")
        or record.get("attempt_2_comparison", {}).get("shape_match")
    )
    if exact_fit_count <= 0:
        failure_stage = "operator_or_representation_coverage"
    else:
        failure_stage = "posterior_selection_or_few_shot_generalization"
    family_map = {
        "recolor": [
            "marker-conditioned recoloring",
            "object-attribute classification",
            "containment-conditioned color transfer",
        ],
        "drawing_or_completion": [
            "paired-object connection",
            "path or ray drawing",
            "boundary and symmetry completion",
            "periodic continuation",
        ],
        "movement_or_permutation": [
            "move-until-contact",
            "relative alignment",
            "object matching and permutation",
            "packing or serialization",
        ],
        "deletion_or_selection": [
            "relational object selection",
            "topological or frequency-based filtering",
        ],
        "compression_or_extraction": [
            "object selection and crop",
            "object-to-grid serialization",
            "panel reduction",
        ],
        "expansion_or_construction": [
            "motif substitution",
            "Kronecker or tensor expansion",
            "periodic resizing",
            "recursive construction",
        ],
        "shape_relayout": [
            "output-shape inference",
            "panel rearrangement",
            "object serialization",
        ],
        "mixed_edit": [
            "typed relational composition",
            "multi-stage residual refinement",
            "object graph rewrite",
        ],
        "identity": ["identity prior calibration"],
        "unknown": ["representation routing and operator coverage"],
    }
    likely = list(family_map.get(transformation_class, family_map["unknown"]))
    if not shape_match:
        likely.insert(0, "output-shape inference")
    if best_accuracy >= 0.97:
        severity = "near_miss"
        explanation = (
            "The best attempt is locally close. A small residual operator, tie-break rule, "
            "or test-time parameter inference is more likely than a wholesale representation failure."
        )
    elif best_accuracy >= 0.75:
        severity = "partial_structure"
        explanation = (
            "The selected program preserves substantial structure but misses the task-defining edit. "
            "Inspect the residual map and color-confusion ledger."
        )
    else:
        severity = "representation_failure"
        explanation = (
            "The best attempt has low cell agreement or the wrong shape. The active atlas or operator "
            "family likely does not express the intended transformation."
        )
    if exact_fit_count > 0:
        explanation += (
            " At least one program fit every demonstration exactly, so the remaining failure is "
            "few-shot ambiguity, posterior ranking, or poor generalization to the test input."
        )
    else:
        explanation += (
            " No candidate fit all demonstrations exactly, so increasing posterior sophistication alone "
            "cannot solve this task without expanding or refining the program grammar."
        )
    return {
        "failure_stage": failure_stage,
        "severity": severity,
        "shape_inference_correct": shape_match,
        "best_cell_accuracy": best_accuracy,
        "exact_fit_candidate_count": exact_fit_count,
        "transformation_class": transformation_class,
        "likely_missing_families": likely,
        "explanation": explanation,
    }



def _selected_attempt_records(posterior_task: Optional[Dict[str, object]], test_index: int) -> List[Dict[str, object]]:
    if not isinstance(posterior_task, dict):
        return []
    values = posterior_task.get("selected_attempts")
    if not isinstance(values, list):
        return []
    if values and isinstance(values[0], list):
        if test_index >= len(values) or not isinstance(values[test_index], list):
            return []
        values = values[test_index]
    return [value for value in values if isinstance(value, dict)]


def build_problem_solution_record(
    task_id: str,
    test_index: int,
    task: dict,
    expected_grid: Grid,
    prediction_entry: Dict[str, Grid],
    posterior_task: Optional[Dict[str, object]] = None,
) -> Dict[str, object]:
    test_input = task.get("test", [{}])[test_index].get("input", [[0]])
    expected = as_array(expected_grid)
    attempt_1 = as_array(prediction_entry.get("attempt_1", [[0]]))
    attempt_2 = as_array(prediction_entry.get("attempt_2", [[0]]))
    comparison_1 = compare_prediction(expected, attempt_1)
    comparison_2 = compare_prediction(expected, attempt_2)
    record: Dict[str, object] = {
        "task_id": task_id,
        "test_index": test_index,
        "solved": bool(comparison_1["exact"] or comparison_2["exact"]),
        "transformation": summarize_transformation(as_array(test_input), expected),
        "training_examples": [
            {"input": pair.get("input", [[0]]), "output": pair.get("output", [[0]])}
            for pair in task.get("train", [])
        ],
        "test_input": test_input,
        "expected": grid_to_list(expected),
        "attempt_1": grid_to_list(attempt_1),
        "attempt_2": grid_to_list(attempt_2),
        "attempt_1_comparison": comparison_1,
        "attempt_2_comparison": comparison_2,
        "attempt_1_residual_grid": grid_to_list(residual_category_grid(expected, attempt_1)),
        "attempt_2_residual_grid": grid_to_list(residual_category_grid(expected, attempt_2)),
        "attempt_1_residual_counts": residual_category_counts(residual_category_grid(expected, attempt_1)),
        "attempt_2_residual_counts": residual_category_counts(residual_category_grid(expected, attempt_2)),
        "best_cell_accuracy": max(float(comparison_1["cell_accuracy"]), float(comparison_2["cell_accuracy"])),
        "posterior": posterior_task or {},
        "selected_attempts": _selected_attempt_records(posterior_task, test_index),
    }
    record["diagnosis"] = diagnose_problem_solution(record)
    return record


def _task_diagnostic_html(record: Dict[str, object]) -> str:
    task_id = str(record["task_id"])
    test_index = int(record["test_index"])
    expected = as_array(record["expected"])
    comparison_1 = dict(record["attempt_1_comparison"])
    comparison_2 = dict(record["attempt_2_comparison"])
    metric_rows = []
    for label, comparison in (("Attempt 1", comparison_1), ("Attempt 2", comparison_2)):
        wrong = comparison.get("wrong_cells")
        wrong_text = "shape mismatch" if wrong is None else str(wrong)
        metric_rows.append(
            "<tr>"
            f"<td>{label}</td>"
            f"<td>{comparison.get('exact')}</td>"
            f"<td>{comparison.get('shape_match')}</td>"
            f"<td>{float(comparison.get('cell_accuracy', 0.0)):.3%}</td>"
            f"<td>{wrong_text}</td>"
            f"<td>{html.escape(json.dumps(comparison.get('color_confusion', [])[:6]))}</td>"
            "</tr>"
        )
    training_html = []
    for number, pair in enumerate(record.get("training_examples", []), 1):
        training_html.append(
            f"<h3>Training example {number}</h3><div class='grid-row'>"
            + _grid_html(as_array(pair["input"]), "Input")
            + _grid_html(as_array(pair["output"]), "Output")
            + "</div>"
        )
    posterior = record.get("posterior") or {}
    return f"""<!doctype html>
<html><head><meta charset="utf-8"><title>{html.escape(task_id)}[{test_index}] diagnostic</title><style>{_diagnostic_css()}</style></head>
<body>
<p><a href="../index.html">← Failure atlas index</a></p>
<h1>{html.escape(task_id)}[{test_index}]</h1>
<p><a href="{html.escape(task_id)}_{test_index}.svg">Open the static problem/solution SVG</a> · <a href="{html.escape(task_id)}_{test_index}.json">Open the complete JSON record</a></p>
<p>Exact ARC result: <span class="{'metric-good' if record.get('solved') else 'metric-bad'}">{'SOLVED' if record.get('solved') else 'MISS'}</span></p>
<h2>Comparison</h2>
<table class="summary"><thead><tr><th>Prediction</th><th>Exact</th><th>Shape</th><th>Cell agreement</th><th>Wrong cells</th><th>Top color confusions</th></tr></thead><tbody>{''.join(metric_rows)}</tbody></table>
<h2>Problem and solution</h2>
{''.join(training_html)}
<h3>Held-out test</h3><div class="grid-row">
{_grid_html(as_array(record['test_input']), 'Test input')}
{_grid_html(expected, 'Expected solution')}
{_grid_html(as_array(record['attempt_1']), 'Attempt 1', expected)}
{_grid_html(as_array(record['attempt_2']), 'Attempt 2', expected)}
</div>
<h3>Residual category maps</h3>
<p>Diagnostic colors: black = correct, blue = extra predicted support, red = missing expected support, yellow = wrong foreground color, cyan = shape-only region.</p>
<div class="grid-row">
{_grid_html(as_array(record['attempt_1_residual_grid']), 'Attempt 1 residual')}
{_grid_html(as_array(record['attempt_2_residual_grid']), 'Attempt 2 residual')}
</div>
<details open><summary>Failure-stage diagnosis</summary><pre>{html.escape(json.dumps(record.get('diagnosis', {}), indent=2))}</pre></details>
<details open><summary>Transformation summary</summary><pre>{html.escape(json.dumps(record.get('transformation', {}), indent=2))}</pre></details>
<details><summary>Attempt 1 mismatch details</summary><pre>{html.escape(json.dumps(comparison_1, indent=2))}</pre></details>
<details><summary>Attempt 2 mismatch details</summary><pre>{html.escape(json.dumps(comparison_2, indent=2))}</pre></details>
<details><summary>Selected attempts</summary><pre>{html.escape(json.dumps(record.get('selected_attempts', []), indent=2))}</pre></details>
<details><summary>Bayesian posterior and candidate portfolio</summary><pre>{html.escape(json.dumps(posterior, indent=2))}</pre></details>
</body></html>"""


def write_diagnostic_bundle(
    tasks: ChallengeDict,
    solutions: SolutionDict,
    submission: dict,
    output_dir: str | Path,
    *,
    posterior_diagnostics: Optional[Dict[str, object]] = None,
    include_solved: bool = False,
    maximum_records: Optional[int] = None,
) -> Dict[str, object]:
    root = Path(output_dir)
    task_root = root / "tasks"
    task_root.mkdir(parents=True, exist_ok=True)
    records: List[Dict[str, object]] = []
    ledger_rows: List[Dict[str, object]] = []
    exact_outputs = 0
    shape_correct_but_wrong = 0
    shape_wrong = 0
    transformation_counts: Counter[str] = Counter()
    failure_stage_counts: Counter[str] = Counter()
    severity_counts: Counter[str] = Counter()
    best_accuracies: List[float] = []
    for task_id, task in tasks.items():
        answers = solutions.get(task_id, [])
        predictions = submission.get(task_id, []) if isinstance(submission, dict) else []
        posterior_task = _posterior_task_record(posterior_diagnostics, task_id)
        for test_index, answer in enumerate(answers):
            prediction_entry = predictions[test_index] if test_index < len(predictions) and isinstance(predictions[test_index], dict) else {}
            record = build_problem_solution_record(task_id, test_index, task, answer, prediction_entry, posterior_task)
            selected_attempts = record.get("selected_attempts", []) if isinstance(record.get("selected_attempts"), list) else []
            selected_1 = selected_attempts[0] if len(selected_attempts) > 0 and isinstance(selected_attempts[0], dict) else {}
            selected_2 = selected_attempts[1] if len(selected_attempts) > 1 and isinstance(selected_attempts[1], dict) else {}
            ledger_rows.append({
                "task_id": task_id,
                "test_index": test_index,
                "solved": bool(record["solved"]),
                "transformation_class": record["transformation"].get("transformation_class"),
                "failure_stage": record.get("diagnosis", {}).get("failure_stage") if isinstance(record.get("diagnosis"), dict) else None,
                "severity": record.get("diagnosis", {}).get("severity") if isinstance(record.get("diagnosis"), dict) else None,
                "likely_missing_families": " | ".join(record.get("diagnosis", {}).get("likely_missing_families", [])) if isinstance(record.get("diagnosis"), dict) else "",
                "expected_shape": "x".join(str(value) for value in record["attempt_1_comparison"].get("expected_shape", [])),
                "attempt_1_shape_match": record["attempt_1_comparison"].get("shape_match"),
                "attempt_1_cell_accuracy": record["attempt_1_comparison"].get("cell_accuracy"),
                "attempt_1_wrong_cells": record["attempt_1_comparison"].get("wrong_cells"),
                "attempt_2_shape_match": record["attempt_2_comparison"].get("shape_match"),
                "attempt_2_cell_accuracy": record["attempt_2_comparison"].get("cell_accuracy"),
                "attempt_2_wrong_cells": record["attempt_2_comparison"].get("wrong_cells"),
                "best_cell_accuracy": record.get("best_cell_accuracy"),
                "selected_program_1": " | ".join(str(value) for value in selected_1.get("names", [])) if isinstance(selected_1.get("names"), list) else selected_1.get("program_name"),
                "selected_family_1": " | ".join(str(value) for value in selected_1.get("families", [])) if isinstance(selected_1.get("families"), list) else selected_1.get("family"),
                "selected_program_2": " | ".join(str(value) for value in selected_2.get("names", [])) if isinstance(selected_2.get("names"), list) else selected_2.get("program_name"),
                "selected_family_2": " | ".join(str(value) for value in selected_2.get("families", [])) if isinstance(selected_2.get("families"), list) else selected_2.get("family"),
                "posterior_entropy": record.get("posterior", {}).get("posterior_entropy") if isinstance(record.get("posterior"), dict) else None,
                "model_disagreement": record.get("posterior", {}).get("model_disagreement") if isinstance(record.get("posterior"), dict) else None,
            })
            if record["solved"]:
                exact_outputs += 1
            else:
                comparisons = [record["attempt_1_comparison"], record["attempt_2_comparison"]]
                if any(bool(comparison.get("shape_match")) for comparison in comparisons):
                    shape_correct_but_wrong += 1
                else:
                    shape_wrong += 1
            transformation_counts[str(record["transformation"].get("transformation_class", "unknown"))] += 1
            if not record["solved"] and isinstance(record.get("diagnosis"), dict):
                failure_stage_counts[str(record["diagnosis"].get("failure_stage", "unknown"))] += 1
                severity_counts[str(record["diagnosis"].get("severity", "unknown"))] += 1
            best_accuracies.append(float(record["best_cell_accuracy"]))
            if not include_solved and record["solved"]:
                continue
            if maximum_records is not None and len(records) >= maximum_records:
                continue
            records.append(record)

    jsonl_path = root / "problems_and_solutions.jsonl"
    with jsonl_path.open("w", encoding="utf-8") as handle:
        for record in records:
            handle.write(json.dumps(record, separators=(",", ":")) + "\n")
    index_rows: List[str] = []
    for record in records:
        task_id = str(record["task_id"])
        test_index = int(record["test_index"])
        stem = f"{task_id}_{test_index}"
        (task_root / f"{stem}.json").write_text(json.dumps(record, indent=2), encoding="utf-8")
        (task_root / f"{stem}.html").write_text(_task_diagnostic_html(record), encoding="utf-8")
        (task_root / f"{stem}.svg").write_text(_task_diagnostic_svg(record), encoding="utf-8")
        comparison_1 = record["attempt_1_comparison"]
        comparison_2 = record["attempt_2_comparison"]
        index_rows.append(
            "<tr>"
            f"<td><a href='tasks/{stem}.html'>{html.escape(task_id)}[{test_index}]</a> <a href='tasks/{stem}.svg'>SVG</a></td>"
            f"<td>{html.escape(str(record['transformation'].get('transformation_class')))}</td>"
            f"<td>{float(comparison_1.get('cell_accuracy', 0.0)):.3%}</td>"
            f"<td>{comparison_1.get('wrong_cells')}</td>"
            f"<td>{float(comparison_2.get('cell_accuracy', 0.0)):.3%}</td>"
            f"<td>{comparison_2.get('wrong_cells')}</td>"
            f"<td>{float(record['posterior'].get('posterior_entropy', 0.0)):.4f}</td>"
            "</tr>"
        )
    ledger_path = root / "output_ledger.csv"
    if ledger_rows:
        with ledger_path.open("w", encoding="utf-8", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=list(ledger_rows[0]))
            writer.writeheader()
            writer.writerows(ledger_rows)
    near_misses = sorted(
        (row for row in ledger_rows if not row["solved"]),
        key=lambda row: (-float(row.get("best_cell_accuracy") or 0.0), str(row["task_id"]), int(row["test_index"])),
    )
    (root / "near_misses.json").write_text(json.dumps(near_misses, indent=2), encoding="utf-8")
    total_outputs = sum(len(values) for values in solutions.values())
    summary = {
        "solver_name": SOLVER_NAME,
        "solver_version": SOLVER_VERSION,
        "total_outputs": total_outputs,
        "exact_outputs": exact_outputs,
        "missed_outputs": total_outputs - exact_outputs,
        "shape_correct_but_cell_wrong": shape_correct_but_wrong,
        "shape_wrong": shape_wrong,
        "mean_best_cell_accuracy": float(np.mean(best_accuracies)) if best_accuracies else None,
        "median_best_cell_accuracy": float(np.median(best_accuracies)) if best_accuracies else None,
        "records_written": len(records),
        "include_solved": include_solved,
        "transformation_class_counts": dict(transformation_counts),
        "failure_stage_counts": dict(failure_stage_counts),
        "severity_counts": dict(severity_counts),
        "index_html": str(root / "index.html"),
        "jsonl": str(jsonl_path),
        "output_ledger_csv": str(ledger_path),
        "near_misses_json": str(root / "near_misses.json"),
    }
    (root / "summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    index_html = f"""<!doctype html>
<html><head><meta charset="utf-8"><title>PR-LASM ARC2 failure atlas</title><style>{_diagnostic_css()}</style></head>
<body>
<h1>PR-LASM ARC2 diagnostic atlas</h1>
<p>Version {SOLVER_VERSION}. Exact ARC scoring is unchanged. Cell agreement is diagnostic only.</p>
<pre>{html.escape(json.dumps(summary, indent=2))}</pre>
<table class="summary"><thead><tr><th>Task</th><th>Transformation</th><th>Attempt 1 agreement</th><th>Attempt 1 wrong</th><th>Attempt 2 agreement</th><th>Attempt 2 wrong</th><th>Posterior entropy</th></tr></thead><tbody>{''.join(index_rows)}</tbody></table>
</body></html>"""
    (root / "index.html").write_text(index_html, encoding="utf-8")
    return summary


def _glob_first(root: str | Path, patterns: Sequence[str]) -> Optional[str]:
    root = str(root)
    hits: List[str] = []
    for pat in patterns:
        hits.extend(glob.glob(os.path.join(root, pat), recursive=True))
    cleaned = []
    for h in hits:
        bn = os.path.basename(h).lower()
        if bn.endswith(".json") and "sample_submission" not in bn:
            cleaned.append(h)
    if not cleaned:
        return None
    cleaned = sorted(set(cleaned), key=lambda x: (len(Path(x).parts), len(os.path.basename(x)), x))
    return cleaned[0]


def find_challenge_json(root: str | Path, split: str = "auto") -> Optional[str]:
    """Find official challenge files, supporting hyphen and underscore variants."""
    split_order = ["test", "evaluation", "training"] if split == "auto" else [split]
    for sp in split_order:
        patterns = [
            f"**/arc-agi_{sp}-challenges.json",
            f"**/arc-agi_{sp}_challenges.json",
            f"**/arc_agi_{sp}_challenges.json",
            f"**/*{sp}*challenge*.json",
        ]
        hit = _glob_first(root, patterns)
        if hit and "solution" not in os.path.basename(hit).lower():
            return hit
    return None


def find_input_json(root: str | Path = "/kaggle/input", split: str = "auto") -> Optional[str]:
    return find_challenge_json(root, split)


def find_solution_json(root: str | Path, split: str = "auto") -> Optional[str]:
    split_order = ["evaluation", "training", "test"] if split == "auto" else [split]
    for sp in split_order:
        patterns = [
            f"**/arc-agi_{sp}-solutions.json",
            f"**/arc-agi_{sp}_solutions.json",
            f"**/arc_agi_{sp}_solutions.json",
            f"**/*{sp}*solution*.json",
        ]
        hit = _glob_first(root, patterns)
        if hit:
            return hit
    return None


def list_candidate_jsons(root: str | Path = "/kaggle/input") -> List[str]:
    if not os.path.exists(root):
        return []
    return sorted(glob.glob(os.path.join(str(root), "**", "*.json"), recursive=True))


def discover_data_files(data_dir: str | Path = "/kaggle/input", split: str = "auto") -> Tuple[Optional[str], Optional[str]]:
    challenge = find_challenge_json(data_dir, split=split)
    solution = find_solution_json(data_dir, split=split)
    return challenge, solution


def load_kaggle_or_local(input_path: Optional[str], data_dir: str = "/kaggle/input", split: str = "auto") -> Tuple[ChallengeDict, str, Optional[str]]:
    if input_path:
        tasks = load_tasks_from_path(input_path)
        # Look for a same-directory solution if the split is validation/training.
        p = Path(input_path)
        auto_solution = find_solution_json(p.parent, split=split if split != "auto" else "auto")
        return tasks, str(input_path), auto_solution
    for root in [data_dir, "/kaggle/input", ".", "/mnt/data"]:
        challenge, solution = discover_data_files(root, split=split)
        if challenge:
            return load_tasks_from_path(challenge), challenge, solution
    raise FileNotFoundError("No ARC-AGI-2 challenge JSON found. Pass --input or attach the Kaggle competition dataset.")


def build_submission(
    tasks: ChallengeDict,
    time_limit_per_task: float = DEFAULT_TIME_LIMIT_PER_TASK,
    verbose: bool = True,
    max_tasks: Optional[int] = None,
    *,
    calibration_path: Optional[str] = None,
    legacy_ranking: bool = False,
    diagnostics_path: Optional[str] = None,
) -> Dict[str, List[Dict[str, Grid]]]:
    sub: Dict[str, List[Dict[str, Grid]]] = {}
    t0 = time.time()
    items = list(tasks.items())[:max_tasks] if max_tasks else list(tasks.items())
    model = None if legacy_ranking else default_lasm_model(calibration_path)
    diagnostic_records: Dict[str, object] = {}
    for n, (task_id, task) in enumerate(items, 1):
        st = time.time()
        task_diagnostics: Optional[Dict[str, object]] = {} if diagnostics_path else None
        sub[task_id] = solve_task(
            task,
            time_limit=time_limit_per_task,
            lasm_model=model,
            legacy_ranking=legacy_ranking,
            diagnostics=task_diagnostics,
        )
        if task_diagnostics is not None:
            task_diagnostics["elapsed_seconds"] = time.time() - st
            diagnostic_records[task_id] = task_diagnostics
        if verbose and (n <= 3 or n % 25 == 0 or n == len(items)):
            print(f"[{n:4d}/{len(items):4d}] {task_id}  tests={len(sub[task_id])}  {time.time()-st:.2f}s  elapsed={time.time()-t0:.1f}s")
    if diagnostics_path:
        write_report(
            {
                "solver_name": SOLVER_NAME,
                "solver_version": SOLVER_VERSION,
                "mode": "legacy" if legacy_ranking else "bayesian_pr_lasm",
                "calibration_version": None if model is None else model.calibration.model_version,
                "tasks": diagnostic_records,
            },
            diagnostics_path,
        )
    return sub


def write_submission(submission: Dict[str, List[Dict[str, Grid]]], output_path: str | Path) -> None:
    _json_dump(submission, output_path, compact=True)


def write_report(report: Dict[str, object], report_path: str | Path) -> None:
    # Remove bulky per-task details from default report if necessary remains JSON-safe.
    _json_dump(report, report_path, compact=False)


def _format_confusions(comparison: Dict[str, object], limit: int = 5) -> str:
    rows = comparison.get("color_confusion") or []
    if not rows:
        return "none"
    parts = []
    for row in list(rows)[:limit]:
        parts.append(f"{row.get('expected')}→{row.get('predicted')}:{row.get('count')}")
    return ", ".join(parts)


def _format_mismatch_coordinates(comparison: Dict[str, object], limit: int = 8) -> str:
    rows = comparison.get("first_mismatches") or []
    if not rows:
        return "none"
    parts = []
    for row in list(rows)[:limit]:
        parts.append(
            f"({row.get('row')},{row.get('column')}):{row.get('expected')}→{row.get('predicted')}"
        )
    return ", ".join(parts)


def print_failure_report(
    submission: dict,
    solutions: SolutionDict,
    tasks: ChallengeDict,
    max_failures: int = 5,
    *,
    posterior_diagnostics: Optional[Dict[str, object]] = None,
) -> None:
    """Print exact ARC misses with cell-level diagnostics.

    Shape equality is reported separately from exact equality. Cell agreement is
    diagnostic only and never changes the exact ARC score.
    """
    shown = 0
    for task_id, true_grids in solutions.items():
        preds = submission.get(task_id, []) if isinstance(submission, dict) else []
        posterior_task = _posterior_task_record(posterior_diagnostics, task_id)
        for i, y_grid in enumerate(true_grids):
            y = as_array(y_grid)
            entry = preds[i] if i < len(preds) and isinstance(preds[i], dict) else {}
            p1 = as_array(entry.get("attempt_1", [[0]]))
            p2 = as_array(entry.get("attempt_2", [[0]]))
            comparison_1 = compare_prediction(y, p1)
            comparison_2 = compare_prediction(y, p2)
            if comparison_1["exact"] or comparison_2["exact"]:
                continue

            print(f"MISS {task_id}[{i}]")
            test_examples = tasks.get(task_id, {}).get("test", [])
            test_input = test_examples[i].get("input", [[0]]) if i < len(test_examples) else [[0]]
            print(
                " input shape:", as_array(test_input).shape,
                " expected shape:", y.shape,
                " transformation:", summarize_transformation(as_array(test_input), y).get("transformation_class"),
            )
            for label, comparison in (("attempt_1", comparison_1), ("attempt_2", comparison_2)):
                if comparison["shape_match"]:
                    print(
                        f" {label}: shape={tuple(comparison['prediction_shape'])} "
                        f"exact=False wrong={comparison['wrong_cells']}/{comparison['total_cells']} "
                        f"agreement={float(comparison['cell_accuracy']):.3%} "
                        f"bbox={comparison['mismatch_bbox']}"
                    )
                    print(f"   confusions: {_format_confusions(comparison)}")
                    print(f"   first mismatches: {_format_mismatch_coordinates(comparison)}")
                else:
                    print(
                        f" {label}: shape={tuple(comparison['prediction_shape'])} "
                        f"exact=False shape_match=False overlap_agreement="
                        f"{float(comparison['overlap_cell_accuracy']):.3%}"
                    )
            selected = _selected_attempt_records(posterior_task, i)
            if selected:
                for attempt_index, selected_record in enumerate(selected[:2], 1):
                    if isinstance(selected_record, dict):
                        print(
                            f"   selected_{attempt_index}: "
                            f"programs={selected_record.get('names', selected_record.get('program_name'))} "
                            f"families={selected_record.get('families', selected_record.get('family'))} "
                            f"posterior={selected_record.get('probability', selected_record.get('posterior_probability'))} "
                            f"exact_fit_probability={selected_record.get('exact_fit_probability')}"
                        )
            shown += 1
            if shown >= max_failures:
                return


# -------------------- synthetic smoke fixtures --------------------

def place_rect(g: Array, color: int, top: int, left: int, h: int, w: int, hollow: bool = False) -> None:
    g[top : top + h, left : left + w] = color
    if hollow and h >= 3 and w >= 3:
        g[top + 1 : top + h - 1, left + 1 : left + w - 1] = 0


def synthetic_task(kind: str, n: int = 8) -> Tuple[dict, Grid]:
    def base(seed: int) -> Array:
        g = np.zeros((n, n), dtype=np.int16)
        place_rect(g, 2, 1 + seed % 2, 2, 2, 2)
        place_rect(g, 5, max(1, n - 4), max(1, n - 4), 3, 2)
        g[0, n - 1] = 9
        return g

    def transform(g: Array) -> Array:
        if kind == "crop_bbox":
            return crop_bbox_non_bg(g)
        if kind == "recolor_largest":
            return op_recolor("largest", "marker")(g)
        if kind == "fill_crop":
            return crop_bbox_non_bg(op_fill_holes()(g))
        if kind == "mirror":
            return np.fliplr(g)
        if kind == "rotate_color":
            z = np.rot90(g, 2).copy()
            z[z == 2] = 7
            return z
        if kind == "copy_br":
            return op_copy("largest", "br")(g)
        return g.copy()

    train = []
    for s in [1, 2, 3]:
        x = base(s)
        if kind == "fill_crop":
            x = np.zeros((n, n), dtype=np.int16)
            place_rect(x, 6, 2, 1 + s % 2, 4, 4, hollow=True)
            x[1, min(n - 1, 6)] = 9
        train.append({"input": grid_to_list(x), "output": grid_to_list(transform(x))})
    x = base(8)
    if kind == "fill_crop":
        x = np.zeros((n, n), dtype=np.int16)
        place_rect(x, 6, 2, max(1, n - 5), 4, 4, hollow=True)
        x[1, 1] = 9
    return {"train": train, "test": [{"input": grid_to_list(x)}]}, grid_to_list(transform(x))


def make_synthetic_challenge_solution(num_tasks: Optional[int] = None) -> Tuple[ChallengeDict, SolutionDict]:
    base_kinds = ["crop_bbox", "recolor_largest", "fill_crop", "mirror", "rotate_color", "copy_br"]
    if num_tasks is None:
        kinds = base_kinds
    else:
        kinds = [base_kinds[i % len(base_kinds)] for i in range(num_tasks)]
    tasks: ChallengeDict = {}
    sols: SolutionDict = {}
    for i, k in enumerate(kinds):
        task, answer = synthetic_task(k, n=7 + (i % 5))
        tid = f"synthetic_{i:04d}_{k}" if num_tasks is not None else f"synthetic_{k}"
        tasks[tid] = task
        sols[tid] = [answer]
    return tasks, sols


def make_mini_dataset(out_dir: str | Path) -> str:
    """Write a tiny local fixture with the same file layout as the Kaggle data page."""
    root = Path(out_dir)
    root.mkdir(parents=True, exist_ok=True)
    tasks, sols = make_synthetic_challenge_solution()
    for split in ["training", "evaluation"]:
        _json_dump(tasks, root / f"arc-agi_{split}-challenges.json", compact=True)
        _json_dump(sols, root / f"arc-agi_{split}-solutions.json", compact=True)
    _json_dump(tasks, root / "arc-agi_test-challenges.json", compact=True)
    sample = {tid: [{"attempt_1": [[0]], "attempt_2": [[0]]} for _ in task["test"]] for tid, task in tasks.items()}
    _json_dump(sample, root / "sample_submission.json", compact=True)
    return str(root)


def run_self_test() -> None:
    tasks, sols = make_synthetic_challenge_solution()
    sub = build_submission(tasks, time_limit_per_task=2.0, verbose=False)
    errors = validate_submission(sub, tasks)
    report = score_submission(sub, sols)
    print(f"{SOLVER_NAME} {SOLVER_VERSION} self-test")
    print(f"tasks={len(tasks)} exact={report['ok']}/{report['total']} score={float(report['score']):.3f} validation_errors={len(errors)}")
    if errors:
        print("First validation error:", errors[0])
    for tid, preds in list(sub.items())[:6]:
        print(tid, "attempt_1_shape=", np.asarray(preds[0]["attempt_1"]).shape, "attempt_2_shape=", np.asarray(preds[0]["attempt_2"]).shape)
    root = make_mini_dataset(Path(tempfile.gettempdir()) / "pr_lasm_arc2_mini_data")
    ev_ch = str(Path(root) / "arc-agi_evaluation-challenges.json")
    ev_sol = str(Path(root) / "arc-agi_evaluation-solutions.json")
    mini_report = evaluate_split(ev_ch, ev_sol, str(Path(root) / "mini_submission.json"), None, 2.0, True)
    print(f"mini_file_layout_test={mini_report['ok']}/{mini_report['total']} score={float(mini_report['score']):.3f} root={root}")
    if report["ok"] != report["total"] or errors or mini_report["ok"] != mini_report["total"]:
        raise SystemExit(1)


def run_synthetic_benchmark(num_tasks: int = 80, time_limit: float = 2.0) -> Dict[str, object]:
    tasks, sols = make_synthetic_challenge_solution(num_tasks)
    sub = build_submission(tasks, time_limit_per_task=time_limit, verbose=False)
    errors = validate_submission(sub, tasks)
    report = score_submission(sub, sols)
    report.update({"valid_submission": len(errors) == 0, "validation_errors": errors[:10], "num_tasks": len(tasks)})
    return report


def evaluate_split(
    challenge_path: str,
    solution_path: Optional[str],
    output_path: Optional[str],
    report_path: Optional[str],
    time_limit: float,
    quiet: bool,
    max_tasks: Optional[int] = None,
    *,
    calibration_path: Optional[str] = None,
    legacy_ranking: bool = False,
    diagnostics_path: Optional[str] = None,
    diagnostic_bundle_dir: Optional[str] = None,
    include_solved_diagnostics: bool = False,
    diagnostic_limit: Optional[int] = None,
) -> Dict[str, object]:
    tasks = load_tasks_from_path(challenge_path)
    if max_tasks is not None:
        tasks = dict(list(tasks.items())[:max_tasks])
    solutions: SolutionDict = {}
    if solution_path:
        all_solutions = load_solutions_from_path(solution_path)
        solutions = {tid: all_solutions[tid] for tid in tasks if tid in all_solutions}
    else:
        solutions = solution_from_embedded_outputs(tasks)

    submission = build_submission(
        tasks,
        time_limit_per_task=time_limit,
        verbose=not quiet,
        calibration_path=calibration_path,
        legacy_ranking=legacy_ranking,
        diagnostics_path=diagnostics_path,
    )
    errors = validate_submission(submission, tasks)
    if output_path:
        write_submission(submission, output_path)
    report = score_submission(submission, solutions) if solutions else {"score": None, "ok": 0, "total": 0, "attempt_1_ok": 0, "attempt_2_ok": 0, "per_task": {}}
    report.update({
        "challenge_path": challenge_path,
        "solution_path": solution_path,
        "output_path": output_path,
        "num_tasks": len(tasks),
        "valid_submission": len(errors) == 0,
        "validation_errors": errors[:25],
        "inference_mode": "legacy" if legacy_ranking else "bayesian_pr_lasm",
        "calibration_version": None if legacy_ranking else default_lasm_model(calibration_path).calibration.model_version,
        "posterior_diagnostics_path": diagnostics_path,
    })
    if diagnostic_bundle_dir and solutions:
        posterior_records: Optional[Dict[str, object]] = None
        if diagnostics_path and Path(diagnostics_path).exists():
            loaded = _json_load(diagnostics_path)
            if isinstance(loaded, dict):
                posterior_records = loaded
        diagnostic_summary = write_diagnostic_bundle(
            tasks,
            solutions,
            submission,
            diagnostic_bundle_dir,
            posterior_diagnostics=posterior_records,
            include_solved=include_solved_diagnostics,
            maximum_records=diagnostic_limit,
        )
        report["diagnostic_bundle_dir"] = str(Path(diagnostic_bundle_dir))
        report["diagnostic_summary"] = diagnostic_summary
    if report_path:
        write_report(report, report_path)
    return report


def print_score_report(label: str, report: Dict[str, object]) -> None:
    print(f"\n{label}")
    print("-" * len(label))
    print(f"tasks:              {report.get('num_tasks')}")
    print(f"valid submission:   {report.get('valid_submission')}")
    score = report.get("score")
    if score is None:
        print("score:              n/a; no ground-truth outputs attached")
    else:
        print(f"score:              {report.get('ok')}/{report.get('total')} = {float(score):.4f}")
        print(f"attempt_1 exact:    {report.get('attempt_1_ok')}/{report.get('total')}")
        print(f"attempt_2 exact:    {report.get('attempt_2_ok')}/{report.get('total')}")
    diagnostics_dir = report.get("diagnostic_bundle_dir")
    if diagnostics_dir:
        print(f"diagnostic atlas:   {Path(str(diagnostics_dir)) / 'index.html'}")
        summary = report.get("diagnostic_summary") or {}
        if isinstance(summary, dict):
            print(f"diagnostic records: {summary.get('records_written')}")
    errors = report.get("validation_errors") or []
    if errors:
        print("validation errors:")
        for e in list(errors)[:10]:
            print("  -", e)


def main(argv: Optional[List[str]] = None) -> int:
    parser = argparse.ArgumentParser(description=f"{SOLVER_NAME} {SOLVER_VERSION}: Kaggle and local ARC-AGI-2 runner")
    parser.add_argument("--version", action="version", version=f"%(prog)s {SOLVER_VERSION}")
    parser.add_argument("--input", default=None, help="ARC challenge JSON file or directory of task JSON files")
    parser.add_argument("--solutions", default=None, help="optional ARC solutions JSON for local scoring")
    parser.add_argument("--output", default=None, help="submission output path")
    parser.add_argument("--report", default=None, help="optional local score/validation report JSON")
    parser.add_argument("--data-dir", default="/kaggle/input", help="directory used for auto-discovery")
    parser.add_argument("--split", default="test", choices=["auto", "test", "evaluation", "training"], help="split to auto-discover when --input is omitted")
    parser.add_argument("--run-public-eval", action="store_true", help="run both training and evaluation if challenge+solution files are present")
    parser.add_argument("--max-tasks", type=int, default=None, help="limit number of tasks for quick local tests")
    parser.add_argument("--time-limit", type=float, default=DEFAULT_TIME_LIMIT_PER_TASK, help="soft seconds per task")
    parser.add_argument("--make-mini-data", default=None, help="write a tiny ARC-AGI-2-shaped fixture to this directory and exit")
    parser.add_argument("--list-inputs", action="store_true", help="list JSON files discovered under --data-dir and exit")
    parser.add_argument("--self-test", action="store_true", help="run deterministic smoke tests")
    parser.add_argument("--synthetic-benchmark", type=int, default=0, help="run N synthetic ARC-like tasks and exit")
    parser.add_argument("--score-submission", default=None, help="validate/score an existing submission JSON instead of generating one")
    parser.add_argument("--validate-only", action="store_true", help="only validate --score-submission format; do not generate predictions")
    parser.add_argument("--report-failures", type=int, default=0, help="print up to N local misses when solutions are available")
    parser.add_argument("--bayesian-calibration", default=None, help="optional PR-LASM Bayesian calibration JSON")
    parser.add_argument("--legacy-ranking", action="store_true", help="use the version 0.2 deterministic ranker for comparison")
    parser.add_argument("--posterior-diagnostics", default=None, help="write per-task Bayesian posterior diagnostics JSON")
    parser.add_argument("--diagnostics-dir", default=None, help="write a browsable problem/solution diagnostic atlas")
    parser.add_argument("--diagnostic-limit", type=int, default=None, help="maximum number of diagnostic task outputs to render")
    parser.add_argument("--include-solved-diagnostics", action="store_true", help="include solved outputs in the diagnostic atlas")
    parser.add_argument("--quiet", action="store_true")
    args = parser.parse_args(argv)

    if args.validate_only and not args.score_submission:
        parser.error("--validate-only requires --score-submission PATH")

    if args.list_inputs:
        for fp in list_candidate_jsons(args.data_dir):
            print(fp)
        return 0

    if args.make_mini_data:
        root = make_mini_dataset(args.make_mini_data)
        print(f"Wrote mini ARC-AGI-2 fixture to {root}")
        print(f"Try: python {Path(__file__).name} --input {root}/arc-agi_evaluation-challenges.json --solutions {root}/arc-agi_evaluation-solutions.json --output {root}/submission.json")
        return 0

    if args.self_test:
        run_self_test()
        return 0

    if args.synthetic_benchmark:
        report = run_synthetic_benchmark(args.synthetic_benchmark, time_limit=args.time_limit)
        print_score_report(f"Synthetic benchmark ({args.synthetic_benchmark} tasks)", report)
        if args.report:
            write_report(report, args.report)
        return 0

    if args.score_submission:
        try:
            if args.input:
                challenge_path = args.input
                auto_solution = find_solution_json(Path(args.input).parent, args.split)
            else:
                challenge_path = find_challenge_json(args.data_dir, args.split) or find_input_json(args.data_dir, args.split)
                auto_solution = find_solution_json(args.data_dir, args.split)
            if not challenge_path:
                raise FileNotFoundError(f"No ARC challenge file found under {args.data_dir}; pass --input explicitly")
            tasks = load_tasks_from_path(challenge_path)
            if args.max_tasks is not None:
                tasks = dict(list(tasks.items())[:args.max_tasks])
            submission = _json_load(args.score_submission)
            errors = validate_submission(submission, tasks)
            print(f"Loaded challenge file: {challenge_path}")
            print(f"Validated submission: {args.score_submission}")
            print(f"validation errors: {len(errors)}")
            for e in errors[:10]:
                print("  -", e)
            solution_path = args.solutions or auto_solution
            if solution_path and not args.validate_only:
                all_solutions = load_solutions_from_path(solution_path)
                solutions = {tid: all_solutions[tid] for tid in tasks if tid in all_solutions}
                report = score_submission(submission, solutions)
                print_score_report("Existing submission local score", {**report, "num_tasks": len(tasks), "valid_submission": len(errors) == 0, "validation_errors": errors[:25]})
                posterior_records = None
                if args.posterior_diagnostics and Path(args.posterior_diagnostics).exists():
                    loaded = _json_load(args.posterior_diagnostics)
                    if isinstance(loaded, dict):
                        posterior_records = loaded
                if args.report_failures:
                    print_failure_report(
                        submission,
                        solutions,
                        tasks,
                        max_failures=args.report_failures,
                        posterior_diagnostics=posterior_records,
                    )
                if args.diagnostics_dir:
                    diagnostic_summary = write_diagnostic_bundle(
                        tasks,
                        solutions,
                        submission,
                        args.diagnostics_dir,
                        posterior_diagnostics=posterior_records,
                        include_solved=args.include_solved_diagnostics,
                        maximum_records=args.diagnostic_limit,
                    )
                    print(f"Wrote diagnostic atlas: {Path(args.diagnostics_dir) / 'index.html'}")
                    print(f"Diagnostic records: {diagnostic_summary['records_written']}")
            elif not args.validate_only:
                print("No solutions available; validation-only result shown.")
            return 1 if errors else 0
        except Exception as e:
            print(str(e), file=sys.stderr)
            return 2

    if args.run_public_eval:
        combined = {"splits": {}}
        for split in ["training", "evaluation"]:
            challenge = find_challenge_json(args.data_dir, split)
            solutions = find_solution_json(args.data_dir, split)
            if not challenge:
                print(f"Skipping {split}: challenge file not found under {args.data_dir}")
                continue
            label = f"{SOLVER_NAME} local {split} evaluation"
            out_path = None
            if args.output:
                base = Path(args.output)
                out_path = str(base.with_name(f"{base.stem}_{split}{base.suffix or '.json'}"))
            rep_path = None
            if args.report:
                base = Path(args.report)
                rep_path = str(base.with_name(f"{base.stem}_{split}{base.suffix or '.json'}"))
            diagnostic_path = None
            if args.posterior_diagnostics:
                base = Path(args.posterior_diagnostics)
                diagnostic_path = str(base.with_name(f"{base.stem}_{split}{base.suffix or '.json'}"))
            diagnostic_bundle_dir = None
            if args.diagnostics_dir:
                diagnostic_bundle_dir = str(Path(args.diagnostics_dir) / split)
            report = evaluate_split(
                challenge,
                solutions,
                out_path,
                rep_path,
                args.time_limit,
                args.quiet,
                args.max_tasks,
                calibration_path=args.bayesian_calibration,
                legacy_ranking=args.legacy_ranking,
                diagnostics_path=diagnostic_path,
                diagnostic_bundle_dir=diagnostic_bundle_dir,
                include_solved_diagnostics=args.include_solved_diagnostics,
                diagnostic_limit=args.diagnostic_limit,
            )
            print_score_report(label, report)
            combined["splits"][split] = {k: v for k, v in report.items() if k != "per_task"}
        if args.report:
            write_report(combined, args.report)
        return 0

    try:
        if args.input:
            challenge_path = args.input
            auto_solution = find_solution_json(Path(args.input).parent, "auto")
        else:
            tasks, challenge_path, auto_solution = load_kaggle_or_local(None, args.data_dir, args.split)
        if args.input:
            # Delay loading to evaluate_split to keep one path through scoring.
            pass
        solution_path = args.solutions
        if solution_path is None and auto_solution and "test" not in os.path.basename(auto_solution).lower():
            solution_path = auto_solution
        elif solution_path is None and args.split in {"training", "evaluation", "auto"}:
            solution_path = auto_solution
        out_path = args.output or ("/kaggle/working/submission.json" if os.path.exists("/kaggle/working") else "submission.json")
        print(f"Loaded challenge file: {challenge_path}")
        if solution_path:
            print(f"Loaded solutions file: {solution_path}")

        report = evaluate_split(
            challenge_path,
            solution_path,
            out_path,
            args.report,
            args.time_limit,
            args.quiet,
            args.max_tasks,
            calibration_path=args.bayesian_calibration,
            legacy_ranking=args.legacy_ranking,
            diagnostics_path=args.posterior_diagnostics,
            diagnostic_bundle_dir=args.diagnostics_dir,
            include_solved_diagnostics=args.include_solved_diagnostics,
            diagnostic_limit=args.diagnostic_limit,
        )
        print(f"Wrote submission: {out_path}")
        print_score_report(f"{SOLVER_NAME} run report", report)
        if args.report_failures and solution_path:
            try:
                tasks_for_report = load_tasks_from_path(challenge_path)
                if args.max_tasks is not None:
                    tasks_for_report = dict(list(tasks_for_report.items())[:args.max_tasks])
                submission_for_report = _json_load(out_path)
                all_solutions = load_solutions_from_path(solution_path)
                solutions_for_report = {tid: all_solutions[tid] for tid in tasks_for_report if tid in all_solutions}
                posterior_records = None
                if args.posterior_diagnostics and Path(args.posterior_diagnostics).exists():
                    loaded = _json_load(args.posterior_diagnostics)
                    if isinstance(loaded, dict):
                        posterior_records = loaded
                print_failure_report(
                    submission_for_report,
                    solutions_for_report,
                    tasks_for_report,
                    max_failures=args.report_failures,
                    posterior_diagnostics=posterior_records,
                )
            except Exception as inner:
                print(f"Could not print failure report: {inner}", file=sys.stderr)
        return 0
    except Exception as e:
        print(str(e), file=sys.stderr)
        print("No runnable ARC input detected; running self-test instead.", file=sys.stderr)
        run_self_test()
        return 0


if __name__ == "__main__":
    raise SystemExit(main())
