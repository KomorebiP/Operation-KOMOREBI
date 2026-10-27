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
import hashlib
import html
import itertools
import glob
import heapq
import inspect
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

try:
    from .aggregate_render_program import (
        AggregateRenderError,
        aggregate_render_implementation_fingerprint,
        compile_aggregate_render_programs,
    )
    from .barrier_face_compiler import compile_barrier_face_fill_rule
    from .closed_container_rewrite import compile_closed_container_zone_rewrites
    from .crossing_line_normalization import compile_crossing_line_normalizations
    from .boundary_run_marker_relocation import (
        boundary_run_marker_relocation_implementation_fingerprint,
        compile_boundary_run_marker_relocation_program,
    )
    from .directed_ray_line_program import (
        compile_directed_ray_line_programs,
        directed_ray_line_implementation_fingerprint,
    )
    from .nesting_depth_algebra import compile_nesting_depth_candidates
    from .multi_object_role_allocation import (
        compile_multi_object_role_allocation_program,
        multi_object_role_allocation_implementation_fingerprint,
    )
    from .planar_effect_compiler import compile_planar_face_effects
    from .planar_face_parity import compile_face_parity_candidates
    from .role_bound_object_program import (
        RoleBindingAmbiguityError,
        RoleBindingError,
        RoleBindingLimitError,
        RoleBoundObjectProgram,
        compile_role_bound_object_rewrites,
        role_bound_implementation_fingerprint,
    )
    from .role_lifted_object_rewrite import compile_role_lifted_object_rewrite
    from .orthogonal_bar_boundary import (
        OrthogonalBarError,
        compile_orthogonal_bar_boundary_complement,
        orthogonal_bar_implementation_fingerprint,
    )
    from .regular_square_corner_mark import (
        RegularSquareCornerMarkError,
        compile_regular_square_corner_mark_program,
        regular_square_corner_mark_implementation_fingerprint,
    )
    from .repeated_local_lattice_completion import (
        compile_repeated_local_lattice_completion_programs,
        repeated_local_lattice_completion_implementation_fingerprint,
    )
except ImportError:  # standalone Kaggle runtime
    from aggregate_render_program import (
        AggregateRenderError,
        aggregate_render_implementation_fingerprint,
        compile_aggregate_render_programs,
    )
    from barrier_face_compiler import compile_barrier_face_fill_rule
    from closed_container_rewrite import compile_closed_container_zone_rewrites
    from crossing_line_normalization import compile_crossing_line_normalizations
    from boundary_run_marker_relocation import (
        boundary_run_marker_relocation_implementation_fingerprint,
        compile_boundary_run_marker_relocation_program,
    )
    from directed_ray_line_program import (
        compile_directed_ray_line_programs,
        directed_ray_line_implementation_fingerprint,
    )
    from nesting_depth_algebra import compile_nesting_depth_candidates
    from multi_object_role_allocation import (
        compile_multi_object_role_allocation_program,
        multi_object_role_allocation_implementation_fingerprint,
    )
    from planar_effect_compiler import compile_planar_face_effects
    from planar_face_parity import compile_face_parity_candidates
    from role_bound_object_program import (
        RoleBindingAmbiguityError,
        RoleBindingError,
        RoleBindingLimitError,
        RoleBoundObjectProgram,
        compile_role_bound_object_rewrites,
        role_bound_implementation_fingerprint,
    )
    from role_lifted_object_rewrite import compile_role_lifted_object_rewrite
    from orthogonal_bar_boundary import (
        OrthogonalBarError,
        compile_orthogonal_bar_boundary_complement,
        orthogonal_bar_implementation_fingerprint,
    )
    from regular_square_corner_mark import (
        RegularSquareCornerMarkError,
        compile_regular_square_corner_mark_program,
        regular_square_corner_mark_implementation_fingerprint,
    )
    from repeated_local_lattice_completion import (
        compile_repeated_local_lattice_completion_programs,
        repeated_local_lattice_completion_implementation_fingerprint,
    )

Grid = List[List[int]]
Array = np.ndarray

SOLVER_NAME = "PR-LASM ARC2 Bayesian Entry"
SOLVER_VERSION = "1.6.0.dev2"
AUTHOR = "Komorebi P."

RNG_SEED = 20260615
random.seed(RNG_SEED)
np.random.seed(RNG_SEED)

MAX_SIDE = 30
MAX_CANDIDATE_PROGRAMS = 1200
TOP_PROGRAMS_TO_APPLY = 80
DEFAULT_TIME_LIMIT_PER_TASK = 8.0

_ROLE_BOUND_PUBLIC_TRAINING_AUDIT: Dict[str, object] = {
    "schema": "komorebi.arc.role-bound-promotion-evidence.v1",
    "artifact": "release/ROLE_BOUND_PROGRAM_VALIDATION_1.5.0.dev1.json",
    "official_source_commit": "f3283f727488ad98fe575ea6a5ac981e4a188e49",
    "official_corpus_sha256": "aa3385893c765ab10251f48bb7b886e3e2e3d79be6b9d70c673248805048cbae",
    "baseline_submission_sha256": "b61b1db61eb919ba9c66441fc5c386a69f914f9bce4f2cd3519c3cfd46138f19",
    "tasks": 1000,
    "test_outputs": 1076,
    "activated_outputs": 5,
    "exact_activations": 5,
    "wrong_activations": 0,
    "pass_at_2_gains": 4,
    "pass_at_2_losses": 0,
    "attempt_1_changes": 0,
    "interpreter_sha256": "b24c2b838d9986dc954e257386e96a4c9b0ddf8417ec9ff52b72f404d39584e1",
    "entry_contract_sha256": "feae5c4464dcce16f3869220638c002170c62b74037e6c331764d9ac20218072",
    "promotion_approved_program_hashes": [
        "4a55647815ca13b8c5a17a44b410d41e54ae414644bc28620e0fd7f83c885129",
        "95a2f32e65219548cfcafaba623d683f63807069134dd96c8a19802f828c93db",
        "ad66bad9068ceed60baf030b66b30e5c0d94b8d5bcf1afdbe89a31c731b701e0",
    ],
}
_ROLE_BOUND_AUDITED_PROGRAM_HASHES = frozenset(
    str(value)
    for value in _ROLE_BOUND_PUBLIC_TRAINING_AUDIT[
        "promotion_approved_program_hashes"
    ]
)
_ROLE_BOUND_AUDITED_INTERPRETER_SHA256 = str(
    _ROLE_BOUND_PUBLIC_TRAINING_AUDIT["interpreter_sha256"]
)

_STRUCTURAL_CONSTRUCTOR_PUBLIC_TRAINING_AUDIT: Dict[str, object] = {
    "schema": "komorebi.arc.structural-constructor-promotion-evidence.v1",
    "artifact": "benchmarks/structural_constructor_public_training_validation.json",
    "audit_script_sha256": "cf38960dd133f10f6d6129271ee2d04f5815e9c6bc9ad1144977c2b67b3da1d7",
    "entry_contract_sha256": "b94af135dd7f70d6c4d7ce757d8f6a4e756782843eb58209ce215aa24a04c834",
    "official_source_commit": "f3283f727488ad98fe575ea6a5ac981e4a188e49",
    "official_challenges_sha256": "779eaba89790ebad9af02514a7efc0aefaf2cf8236f046a31bbf8b9ec48f20f5",
    "official_solutions_sha256": "9f07a38bd25af5e83aa5bf85c5cb1a1fefdb30f6a755256fa65429e697ca97f9",
    "tasks": 1000,
    "test_outputs": 1076,
    "activation_tasks": 12,
    "activated_outputs": 18,
    "exact_activations": 18,
    "wrong_activations": 0,
    "families": {
        "causal_aggregate_render": {
            "compiler": "aggregate_render",
            "candidate_schema": "komorebi.arc.aggregate-render-candidate.v1",
            "implementation_sha256": "20b51c00a63367b55cb133eed9a7cb4046b496c1f34c625a50ea5080633a981f",
            "activation_tasks": 3,
            "activated_outputs": 4,
            "exact_activations": 4,
            "wrong_activations": 0,
            "minimum_distinct_witness_groups": 2,
            "approved_program_hashes": [
                "04069ace7082f6b62abb1a47ebfb3ba80495c3c32cc311ae3c4a3bc7f34858ea",
                "0a102a2e68f29517778957c5f82b470b9cb8fd1f79a51eef0facc0197cc7d156",
                "b04e4bef9c3c27b5b03cfc1aef13452c867a2290285724631cec31993b9a1e95",
            ],
        },
        "causal_orthogonal_bar_boundary_complement": {
            "compiler": "orthogonal_bar_boundary",
            "candidate_schema": "komorebi.arc.orthogonal-bar-boundary-candidate.v1",
            "implementation_sha256": "6df954b4a77c2d269f48e5ec9ae97658ef44a40314bded69ef1ad99828dc886b",
            "activation_tasks": 1,
            "activated_outputs": 4,
            "exact_activations": 4,
            "wrong_activations": 0,
            "minimum_distinct_witness_groups": 3,
            "approved_program_hashes": [
                "0744259f0e0c17375b529ceea720eaa1376ed533a0a6742ede9e8a817c3dad8b"
            ],
        },
        "causal_regular_square_corner_mark": {
            "compiler": "regular_square_corner_mark",
            "candidate_schema": "komorebi.arc.regular-square-corner-mark-candidate.v1",
            "implementation_sha256": "87b0924a9a2a0b3c16604ec6b1c02e13b3e01db8728eaf5a5efa5cc0b5969fdb",
            "activation_tasks": 1,
            "activated_outputs": 1,
            "exact_activations": 1,
            "wrong_activations": 0,
            "minimum_distinct_witness_groups": 2,
            "approved_program_hashes": [
                "0e25b92336f02d568e8d62e79aa316148148c475bcd281db8ad9225313715f13"
            ],
        },
        "causal_directed_ray_line": {
            "compiler": "directed_ray_line",
            "candidate_schema": "komorebi.arc.directed-ray-line-candidate.v1",
            "implementation_sha256": "b99f1e931dc5c2952d70853b101f4cfb37c3c9727d9476c6a4b0bef6806d98cf",
            "activation_tasks": 3,
            "activated_outputs": 4,
            "exact_activations": 4,
            "wrong_activations": 0,
            "minimum_distinct_witness_groups": 3,
            "approved_program_hashes": [
                "1521f35b3a3bcbe5a7f50d75603f65b68926df02ca9528abc86240c0e9730e4b",
                "6665d476492148f49ba11064443efe4905fa6a4e8c1ff9a52f016ef39ffc64b3",
                "f925f2390095dcba1626a2245ad259c60b027586308f30e333ad8f716775ae89",
            ],
        },
        "causal_repeated_local_lattice_completion": {
            "compiler": "repeated_local_lattice_completion",
            "candidate_schema": "komorebi.arc.repeated-local-lattice-completion-candidate.v1",
            "implementation_sha256": "198e3d39dc547a137cdf9c5738ba003f520115441032b2f70108611d24dbcbb9",
            "activation_tasks": 2,
            "activated_outputs": 3,
            "exact_activations": 3,
            "wrong_activations": 0,
            "minimum_distinct_witness_groups": 2,
            "approved_program_hashes": [
                "01efb5d2554ebbe9339e9f0916e11dcd9a3104ad37e34de2c1594c824a87916a",
                "45367051766be2d78649178136b957afa091fd40e21528f1e086c4abfa06f27a",
            ],
        },
        "causal_multi_object_role_allocation": {
            "compiler": "multi_object_role_allocation",
            "candidate_schema": "komorebi.arc.multi-object-role-allocation-candidate.v1",
            "implementation_sha256": "9c88cee54283f580a50d02c79559b285f3f193ffbf3a77bfc7b4f462953fe384",
            "activation_tasks": 2,
            "activated_outputs": 2,
            "exact_activations": 2,
            "wrong_activations": 0,
            "minimum_distinct_witness_groups": 3,
            "approved_program_hashes": [
                "570bb40ae71510fed5213bd17a47a70190b322095a83a29d7fddddc0a0975d79",
                "c9377231554af887a96099d8a45db8e7720e4024bc8c45232d15a67b5ab33b28",
            ],
        },
    },
}

_STRUCTURAL_CONSTRUCTOR_COMPILERS = (
    (
        "aggregate_render",
        compile_aggregate_render_programs,
        aggregate_render_implementation_fingerprint,
    ),
    (
        "orthogonal_bar_boundary",
        compile_orthogonal_bar_boundary_complement,
        orthogonal_bar_implementation_fingerprint,
    ),
    (
        "regular_square_corner_mark",
        compile_regular_square_corner_mark_program,
        regular_square_corner_mark_implementation_fingerprint,
    ),
    (
        "directed_ray_line",
        compile_directed_ray_line_programs,
        directed_ray_line_implementation_fingerprint,
    ),
    (
        "repeated_local_lattice_completion",
        compile_repeated_local_lattice_completion_programs,
        repeated_local_lattice_completion_implementation_fingerprint,
    ),
    (
        "multi_object_role_allocation",
        compile_multi_object_role_allocation_program,
        multi_object_role_allocation_implementation_fingerprint,
    ),
)


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


_GRAPH_OBJECT_STENCIL_WITNESS_PROTOCOL = (
    "leave_one_distinct_nonidentity_group_out_reinduction"
)


def _graph_object_stencil_witness_admissible(
    candidate: RuleCandidate,
) -> bool:
    """Require complete support across distinct nonidentity groups."""
    if not candidate.family.startswith("graph_object_stencil_"):
        return True
    metadata = candidate.metadata or {}
    loo_exact_count = metadata.get("loo_exact_count")
    loo_total_count = metadata.get("loo_total_count")
    minimum_support = metadata.get("minimum_nonempty_key_group_support")
    return bool(
        metadata.get("witness_protocol")
        == _GRAPH_OBJECT_STENCIL_WITNESS_PROTOCOL
        and type(loo_exact_count) is int
        and type(loo_total_count) is int
        and loo_total_count >= 2
        and loo_exact_count == loo_total_count
        and type(minimum_support) is int
        and minimum_support >= 2
        and metadata.get("witness_reconstructible") is True
    )


def candidate_admissibility(candidate: RuleCandidate) -> Tuple[bool, str]:
    """Return whether a proposal has a valid held-out prediction contract.

    Older typed operators predate explicit provenance metadata and remain
    admissible by default. Explicitly marked candidates are rejected when
    they copy a particular demonstration, depend on demonstration ordering,
    or otherwise declare themselves inadmissible. The same contract is
    checked again by the Bayesian layer so a caller cannot bypass it by
    constructing a portfolio directly.
    """
    metadata = candidate.metadata or {}
    provenance_kind = str(metadata.get("provenance_kind", "legacy_unverified"))
    if not _graph_object_stencil_witness_admissible(candidate):
        return False, "object stencil lacks complete leave-one-out support"
    if metadata.get("admissible") is False:
        return False, str(metadata.get("abstention_reason", "candidate declared inadmissible"))
    if metadata.get("permutation_invariant") is False:
        return False, "candidate depends on demonstration ordering"
    if provenance_kind == "training_example_literal":
        return False, "prediction copies a particular training output"
    return True, "admissible"


def admissible_candidates(candidates: Sequence[RuleCandidate]) -> List[RuleCandidate]:
    """Remove proposals that violate the held-out provenance contract."""
    return [candidate for candidate in candidates if candidate_admissibility(candidate)[0]]


_CAUSAL_RELATIONAL_COMPILERS: Tuple[Tuple[str, Callable[..., object]], ...] = (
    ("planar_face_effect", compile_planar_face_effects),
    ("barrier_face_fill", compile_barrier_face_fill_rule),
    ("nesting_depth", compile_nesting_depth_candidates),
    ("closed_container", compile_closed_container_zone_rewrites),
    ("crossing_line", compile_crossing_line_normalizations),
    ("planar_face_parity", compile_face_parity_candidates),
)

_AUDITED_RELATIONAL_PROMOTION_FAMILIES = frozenset(
    {
        "causal_barrier_face_fill",
        "causal_closed_container_zone_rewrite",
        "causal_crossing_line_normalization",
        "causal_nesting_depth_color_algebra",
    }
)
_AUDITED_PLANAR_PROMOTION_SCHEMAS = frozenset(
    {
        "boolean_face_predicate_literal_fill",
        "canvas_side_signature_literal_fill",
        "literal_color_incident_face_fill",
        "relative_face_area_category_literal_fill",
        "unique_related_color_face_fill",
        "unique_relative_face_area_category_literal_fill",
    }
)


def _audited_relational_promotion_certificate(
    family: str,
    metadata: Dict[str, object],
) -> bool:
    """Return the explicit exhaustive public-activation certificate.

    This gate encodes only semantic families and schemas, never task IDs or
    raster literals.  Its evidence boundary is deliberately labeled: every
    activation on all 1,000 public-training tasks was compared exhaustively,
    yielding 24/24 exact candidate outputs and zero false predictions.
    """

    if family in _AUDITED_RELATIONAL_PROMOTION_FAMILIES:
        return True
    return (
        family
        in {
            "causal_planar_face_literal_effect",
            "causal_planar_face_related_color",
        }
        and str(metadata.get("schema", "")) in _AUDITED_PLANAR_PROMOTION_SCHEMAS
    )


def _validated_external_candidate_grid(grid: object) -> Array:
    """Validate a separately compiled ARC grid without clipping bad values."""

    raw = np.asarray(grid)
    if raw.ndim != 2 or raw.size == 0:
        raise ValueError("external candidate grid must be nonempty and two-dimensional")
    if raw.shape[0] > MAX_SIDE or raw.shape[1] > MAX_SIDE:
        raise ValueError("external candidate grid exceeds the ARC size contract")
    if not (
        np.issubdtype(raw.dtype, np.integer)
        or np.issubdtype(raw.dtype, np.floating)
    ):
        raise ValueError("external candidate grid must contain real numeric values")
    if not np.all(np.isfinite(raw)):
        raise ValueError("external candidate grid contains nonfinite values")
    if not np.issubdtype(raw.dtype, np.integer) and not np.all(
        np.equal(raw, np.floor(raw))
    ):
        raise ValueError("external candidate grid contains nonintegral values")
    # Check the lossless source values before narrowing to int16. Otherwise,
    # values such as +/-65536 wrap to zero and bypass the ARC color contract.
    if np.any(raw < 0) or np.any(raw > 9):
        raise ValueError("external candidate grid contains an invalid ARC color")
    validated = np.array(raw, dtype=np.int16, copy=True)
    return np.ascontiguousarray(validated)


def causal_planar_relational_rules(
    train: List[Tuple[Array, Array]],
    tests: List[Array],
) -> List[RuleCandidate]:
    """Adapt bounded planar/container compilers into an additive shadow lane.

    Every compiler is independently exception-contained, every returned grid
    is validated before conversion, and the demonstrations are rechecked here
    with exact array equality.  Promotion remains false unless a later release
    audit certifies a complete semantic family; exact fit alone is not treated
    as held-out evidence.
    """

    adapted: List[RuleCandidate] = []
    for compiler_name, compiler in _CAUSAL_RELATIONAL_COMPILERS:
        try:
            external_candidates = compiler(train, tests)
        except Exception:
            continue
        for external in external_candidates or ():
            try:
                if int(getattr(external, "train_error")) != 0:
                    continue
                train_grids = tuple(
                    _validated_external_candidate_grid(grid)
                    for grid in getattr(external, "train_grids")
                )
                grids = [
                    _validated_external_candidate_grid(grid)
                    for grid in getattr(external, "grids")
                ]
                if len(train_grids) != len(train) or len(grids) != len(tests):
                    continue
                if not all(
                    exact(prediction, target)
                    for prediction, (_, target) in zip(train_grids, train)
                ):
                    continue
                metadata = json.loads(
                    json.dumps(dict(getattr(external, "metadata")), sort_keys=True)
                )
                family = str(getattr(external, "family"))
                promotion_eligible = _audited_relational_promotion_certificate(
                    family,
                    metadata,
                )
                metadata["empirical_promotion_eligible"] = promotion_eligible
                metadata.update(
                    {
                        "compiler_adapter": "causal_planar_relational_rules_v1",
                        "compiler_name": compiler_name,
                        "portfolio_lane": "planar_relational_shadow",
                        "exact_demonstration_recheck": True,
                        "admissible": True,
                    }
                )
                if promotion_eligible:
                    metadata["empirical_promotion_evidence"] = {
                        "scope": "exhaustive_public_training_1000_activation_audit",
                        "tasks_audited": 1000,
                        "outputs_audited": 1076,
                        "activation_tasks": 22,
                        "candidate_outputs": 24,
                        "exact_candidate_outputs": 24,
                        "false_candidate_outputs": 0,
                        "selected_attempt_2_gains": 22,
                        "selected_attempt_2_losses": 0,
                        "raw_tensors_used_at_runtime": False,
                    }
                candidate = RuleCandidate(
                    name=str(getattr(external, "name")),
                    grids=grids,
                    train_error=0,
                    complexity=max(1, int(getattr(external, "complexity"))),
                    family=family,
                    train_grids=train_grids,
                    metadata=metadata,
                )
            except (AttributeError, TypeError, ValueError, OverflowError):
                continue
            if candidate_admissibility(candidate)[0]:
                adapted.append(candidate)
    return deduplicate_candidates(
        sorted(adapted, key=_candidate_family_priority)
    )



def boundary_run_marker_relocation_rules(
    train: List[Tuple[Array, Array]],
    tests: List[Array],
) -> List[RuleCandidate]:
    """Adapt the exact marker-relocation compiler into the base portfolio.

    This family is admitted through exact replay and full leave-one-out
    evidence, but it deliberately remains outside empirical Attempt-2 override
    until a complete corpus activation and gain-loss scan is attached.
    """

    try:
        external_candidates = compile_boundary_run_marker_relocation_program(
            train,
            tests,
        )
    except Exception:
        return []
    adapted: List[RuleCandidate] = []
    for external in external_candidates or ():
        try:
            if int(getattr(external, "train_error")) != 0:
                continue
            train_grids = tuple(
                _validated_external_candidate_grid(grid)
                for grid in getattr(external, "train_grids")
            )
            grids = [
                _validated_external_candidate_grid(grid)
                for grid in getattr(external, "grids")
            ]
            if len(train_grids) != len(train) or len(grids) != len(tests):
                continue
            if not all(
                exact(prediction, target)
                for prediction, (_, target) in zip(train_grids, train)
            ):
                continue
            metadata = json.loads(
                json.dumps(dict(getattr(external, "metadata")), sort_keys=True)
            )
            current_fingerprint = (
                boundary_run_marker_relocation_implementation_fingerprint()
            )
            if metadata.get("implementation_fingerprint") != current_fingerprint:
                continue
            metadata.update(
                {
                    "compiler_adapter": (
                        "boundary_run_marker_relocation_rules_v1"
                    ),
                    "compiler_name": "boundary_run_marker_relocation",
                    "portfolio_lane": "protected_base_exact_compiler",
                    "exact_demonstration_recheck": True,
                    "admissible": True,
                    "provenance_kind": "test_input_transform",
                    "permutation_invariant": True,
                    "empirical_promotion_eligible": False,
                    "complete_public_training_activation_scan": False,
                    "promotion_gate": (
                        "complete_public_training_activation_and_gain_loss_scan"
                    ),
                }
            )
            candidate = RuleCandidate(
                name=str(getattr(external, "name")),
                grids=grids,
                train_error=0,
                complexity=max(1, int(getattr(external, "complexity"))),
                family=str(getattr(external, "family")),
                train_grids=train_grids,
                metadata=metadata,
            )
        except (AttributeError, TypeError, ValueError, OverflowError):
            continue
        if candidate_admissibility(candidate)[0]:
            adapted.append(candidate)
    return deduplicate_candidates(
        sorted(adapted, key=_candidate_family_priority)
    )

def _structural_constructor_candidate_audit_valid(
    candidate: object,
    compiler_name: str,
    fingerprint: Callable[[], str],
) -> bool:
    """Bind constructor promotion to its exact compiler and public scan."""

    family = str(getattr(candidate, "family", ""))
    families = _STRUCTURAL_CONSTRUCTOR_PUBLIC_TRAINING_AUDIT.get("families")
    if not isinstance(families, dict):
        return False
    evidence = families.get(family)
    if not isinstance(evidence, dict) or evidence.get("compiler") != compiler_name:
        return False
    metadata = getattr(candidate, "metadata", None)
    if not isinstance(metadata, dict):
        return False
    expected_fingerprint = str(evidence.get("implementation_sha256", ""))
    try:
        current_fingerprint = str(fingerprint())
    except (OSError, TypeError, ValueError):
        return False
    if not (
        expected_fingerprint
        and current_fingerprint == expected_fingerprint
        and metadata.get("implementation_fingerprint") == expected_fingerprint
        and metadata.get("schema") == evidence.get("candidate_schema")
        and getattr(candidate, "train_error", None) == 0
        and metadata.get("exact_demonstration_contract") is True
        and metadata.get("test_target_isolation") is True
        and metadata.get("test_input_grounded") is True
        and metadata.get("task_identifier_free") is True
    ):
        return False
    program = getattr(candidate, "program", None)
    try:
        program_hash = str(program.program_hash())
        program_record = program.to_record()
    except (AttributeError, TypeError, ValueError):
        return False
    if not (
        metadata.get("program_hash") == program_hash
        and metadata.get("program") == program_record
    ):
        return False
    approved_hashes = evidence.get("approved_program_hashes")
    if not isinstance(approved_hashes, list) or not approved_hashes:
        return False
    if program_hash not in {
        str(value) for value in approved_hashes
    }:
        return False
    witness_groups = metadata.get("distinct_witness_groups")
    minimum_groups = evidence.get("minimum_distinct_witness_groups")
    loo_exact = metadata.get("loo_exact_count")
    loo_total = metadata.get("loo_total_count")
    if not (
        type(witness_groups) is int
        and type(minimum_groups) is int
        and witness_groups >= minimum_groups
        and type(loo_exact) is int
        and type(loo_total) is int
        and loo_total >= minimum_groups
        and loo_exact == loo_total
    ):
        return False
    if family == "causal_orthogonal_bar_boundary_complement" and (
        metadata.get("both_defect_polarities_witnessed") is not True
    ):
        return False
    if family == "causal_regular_square_corner_mark":
        group_exact = metadata.get("distinct_group_loo_exact_count")
        group_total = metadata.get("distinct_group_loo_total_count")
        if not (
            type(group_exact) is int
            and type(group_total) is int
            and group_total >= minimum_groups
            and group_exact == group_total
            and metadata.get("witness_reconstructible") is True
        ):
            return False
    try:
        entry_contract_current = (
            _structural_constructor_entry_contract_fingerprint()
        )
    except (OSError, TypeError, ValueError):
        return False
    return bool(
        evidence.get("activated_outputs") == evidence.get("exact_activations")
        and evidence.get("wrong_activations") == 0
        and _STRUCTURAL_CONSTRUCTOR_PUBLIC_TRAINING_AUDIT.get(
            "wrong_activations"
        )
        == 0
        and entry_contract_current
        == _STRUCTURAL_CONSTRUCTOR_PUBLIC_TRAINING_AUDIT.get(
            "entry_contract_sha256"
        )
    )


def audited_structural_constructor_rules(
    train: List[Tuple[Array, Array]],
    tests: List[Array],
) -> List[RuleCandidate]:
    """Adapt the exhaustively scanned structural constructors.

    The public scan is an empirical development gate, not a proof of hidden
    correctness.  Any source drift, malformed program record, incomplete LOO
    evidence, or exact-replay mismatch removes override eligibility.
    """

    output: List[RuleCandidate] = []
    for compiler_name, compiler, fingerprint in _STRUCTURAL_CONSTRUCTOR_COMPILERS:
        try:
            external_candidates = compiler(train, tests)
        except Exception:
            continue
        for external in external_candidates or ():
            try:
                train_grids = tuple(
                    _validated_external_candidate_grid(grid)
                    for grid in getattr(external, "train_grids")
                )
                grids = [
                    _validated_external_candidate_grid(grid)
                    for grid in getattr(external, "grids")
                ]
                if len(train_grids) != len(train) or len(grids) != len(tests):
                    continue
                if not all(
                    exact(prediction, target)
                    for prediction, (_, target) in zip(train_grids, train)
                ):
                    continue
                raw_metadata = getattr(external, "metadata")
                metadata = json.loads(
                    json.dumps(dict(raw_metadata), sort_keys=True)
                )
                promotion_eligible = _structural_constructor_candidate_audit_valid(
                    external,
                    compiler_name,
                    fingerprint,
                )
                family = str(getattr(external, "family"))
                family_evidence = dict(
                    _STRUCTURAL_CONSTRUCTOR_PUBLIC_TRAINING_AUDIT["families"][family]
                )
                metadata.update(
                    {
                        "compiler_adapter": "audited_structural_constructor_rules_v1",
                        "compiler_name": compiler_name,
                        "portfolio_lane": "audited_structural_constructor_challenger",
                        "exact_demonstration_recheck": True,
                        "admissible": True,
                        "provenance_kind": "test_input_transform",
                        "permutation_invariant": True,
                        "empirical_promotion_eligible": promotion_eligible,
                        "promotion_gate": "complete_public_training_activation_scan",
                        "complete_public_training_activation_scan": promotion_eligible,
                        "promotion_audit": {
                            "schema": _STRUCTURAL_CONSTRUCTOR_PUBLIC_TRAINING_AUDIT[
                                "schema"
                            ],
                            "artifact": _STRUCTURAL_CONSTRUCTOR_PUBLIC_TRAINING_AUDIT[
                                "artifact"
                            ],
                            "official_source_commit": _STRUCTURAL_CONSTRUCTOR_PUBLIC_TRAINING_AUDIT[
                                "official_source_commit"
                            ],
                            "official_challenges_sha256": _STRUCTURAL_CONSTRUCTOR_PUBLIC_TRAINING_AUDIT[
                                "official_challenges_sha256"
                            ],
                            "official_solutions_sha256": _STRUCTURAL_CONSTRUCTOR_PUBLIC_TRAINING_AUDIT[
                                "official_solutions_sha256"
                            ],
                            "tasks": _STRUCTURAL_CONSTRUCTOR_PUBLIC_TRAINING_AUDIT[
                                "tasks"
                            ],
                            "test_outputs": _STRUCTURAL_CONSTRUCTOR_PUBLIC_TRAINING_AUDIT[
                                "test_outputs"
                            ],
                            "family": family,
                            "family_evidence": family_evidence,
                        },
                    }
                )
                candidate = RuleCandidate(
                    name=str(getattr(external, "name")),
                    grids=grids,
                    train_error=0,
                    complexity=max(1, int(getattr(external, "complexity"))),
                    family=family,
                    train_grids=train_grids,
                    metadata=metadata,
                )
            except (AttributeError, KeyError, TypeError, ValueError, OverflowError):
                continue
            if candidate_admissibility(candidate)[0]:
                output.append(candidate)
    return deduplicate_candidates(
        sorted(output, key=lambda item: (item.complexity, item.family, item.name))
    )


def _structural_constructor_entry_contract_fingerprint() -> str:
    """Bind constructor evidence to adapter, lane, and promotion semantics."""

    solve_contract = globals().get("solve_task")
    if not callable(solve_contract):
        raise ValueError("solve_task is unavailable for contract fingerprinting")
    audited_facts = {
        key: value
        for key, value in _STRUCTURAL_CONSTRUCTOR_PUBLIC_TRAINING_AUDIT.items()
        if key != "entry_contract_sha256"
    }
    functions = (
        _validated_external_candidate_grid,
        _structural_constructor_candidate_audit_valid,
        audited_structural_constructor_rules,
        semantic_behavior_quotient,
        build_monotone_candidate_portfolio,
        _promote_monotone_portfolio_outputs,
        solve_contract,
    )
    payload = {
        "audit_facts": audited_facts,
        "sources": [inspect.getsource(function) for function in functions],
    }
    encoded = json.dumps(
        payload,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=True,
    ).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


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
    contract_metadata: Dict[str, object] = {
        "provenance_kind": "test_input_transform",
        "test_input_grounded": True,
        "permutation_invariant": True,
        "admissible": True,
    }
    contract_metadata.update(metadata or {})
    return RuleCandidate(
        name=name,
        grids=[sanitize_grid(fn(test)) for test in tests],
        train_error=int(error),
        complexity=int(complexity),
        family=family,
        train_grids=train_grids,
        metadata=contract_metadata,
    )


def deduplicate_prediction_grids(candidates: Sequence[RuleCandidate]) -> List[RuleCandidate]:
    """Keep the simplest candidate for each complete test prediction tuple."""
    output: List[RuleCandidate] = []
    seen: set[Tuple[str, ...]] = set()
    for candidate in sorted(candidates, key=lambda item: (item.complexity, item.family, item.name)):
        signature = tuple(canonical(grid) for grid in candidate.grids)
        if signature in seen:
            continue
        seen.add(signature)
        output.append(candidate)
    return output


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

    # A constant output is a legitimate task contract only when every
    # demonstration supplies exactly the same complete tensor. Unlike a
    # pointer to the final demonstration, this witness is order-invariant.
    common_output = train[0][1]
    if len(train) >= 2 and all(
        exact(common_output, target) for _, target in train[1:]
    ):
        common_output = sanitize_grid(common_output)
        out.append(
            RuleCandidate(
                "constant_common_output",
                [common_output.copy() for _ in tests],
                0,
                12,
                "fallback",
                train_grids=tuple(common_output.copy() for _ in train),
                metadata={
                    "provenance_kind": "common_output_contract",
                    "test_input_grounded": False,
                    "permutation_invariant": True,
                    "admissible": True,
                    "output_contract": "identical_training_outputs",
                },
            )
        )

    # Constant-shape blank/output-size fallback learned through symmetric
    # aggregates. Stable tie-breaking makes the proposal independent of the
    # order in which demonstrations are supplied.
    shapes = [tuple(y.shape) for _, y in train]
    if shapes:
        shape_counts = Counter(shapes)
        shape = min(shape_counts, key=lambda value: (-shape_counts[value], value))
        backgrounds = [majority_color(y) for _, y in train]
        background_counts = Counter(backgrounds)
        bg = min(background_counts, key=lambda value: (-background_counts[value], value))
        grids = [np.full(shape, bg, dtype=np.int16) for _ in tests]
        err = sum(grid_error(np.full(shape, bg, dtype=np.int16), y) for _, y in train)
        train_grids = tuple(np.full(shape, bg, dtype=np.int16) for _ in train)
        out.append(
            RuleCandidate(
                "blank_common_output_shape",
                grids,
                err,
                20,
                "fallback",
                train_grids=train_grids,
                metadata={
                    "provenance_kind": "symmetric_training_aggregate",
                    "test_input_grounded": False,
                    "permutation_invariant": True,
                    "admissible": True,
                    "output_contract": "modal_training_shape_and_background",
                },
            )
        )

    # A literal training output has no provenance path from the held-out input
    # and changes when demonstrations are reordered. It is deliberately not
    # emitted, even as a second-attempt fallback.
    return out


def _legacy_program_evaluation_cap(
    train: List[Tuple[Array, Array]],
    tests: List[Array],
    time_limit: float,
) -> int:
    """Choose a deterministic legacy-search cap from the nominal budget tier."""
    seconds = max(0.0, float(time_limit))
    if seconds <= 0.1:
        cap = 192
    elif seconds <= 2.0:
        cap = 640
    else:
        cap = MAX_CANDIDATE_PROGRAMS
    workload = sum(source.size + target.size for source, target in train)
    workload += sum(test.size for test in tests)
    if workload > 4096:
        cap = min(cap, 128 if seconds <= 0.1 else 384)
    return max(1, int(cap))


def synthesize_program_rules(
    train: List[Tuple[Array, Array]],
    tests: List[Array],
    time_limit: float,
) -> List[RuleCandidate]:
    """Evaluate a deterministic prefix of the legacy depth-two grammar."""
    out: List[RuleCandidate] = []
    # ARC demonstrations are an exchangeable set.  The bounded legacy search
    # used an early-error cutoff, so evaluating them in caller order could
    # change which approximate programs survived the cap.  Canonicalize only
    # the search/evaluation view; emitted train grids remain aligned with the
    # caller's original order for the Bayesian likelihood.
    ordered_train = sorted(
        train,
        key=lambda pair: (
            pair[0].shape,
            canonical(pair[0]),
            pair[1].shape,
            canonical(pair[1]),
        ),
    )
    max_depth = 2
    # For tiny grids, try a little depth-3 search with a stricter program cap.
    if max(max(x.shape) for x, _ in train) <= 12 and max(max(y.shape) for _, y in train) <= 12:
        max_depth = 2  # keep Kaggle-safe; switch to 3 manually if you have compute.
    programs = generate_programs(ordered_train, max_depth=max_depth)
    evaluation_cap = _legacy_program_evaluation_cap(ordered_train, tests, time_limit)
    best_cut = 10**9
    scored: List[Tuple[float, int, int, Tuple[Op, ...]]] = []
    for program in programs[:evaluation_cap]:
        err = 0
        for x, y in ordered_train:
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
    *,
    metadata: Optional[Dict[str, object]] = None,
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
                    metadata=metadata,
                )
            )
    except Exception:
        return


# ---------------- typed frame extraction proposal channel ----------------

@dataclass(frozen=True)
class TypedFrame:
    """A complete one-cell monochrome rectangular perimeter.

    Frames are enumerated directly from row and column incidence. They are
    deliberately independent of connected components because unrelated cells
    can touch a frame and because its interior can contain arbitrary colors.
    """

    color: int
    top: int
    left: int
    bottom: int
    right: int

    @property
    def bbox(self) -> Tuple[int, int, int, int]:
        return self.top, self.left, self.bottom, self.right

    @property
    def height(self) -> int:
        return self.bottom - self.top + 1

    @property
    def width(self) -> int:
        return self.right - self.left + 1

    @property
    def outer_area(self) -> int:
        return self.height * self.width

    @property
    def interior_height(self) -> int:
        return self.height - 2

    @property
    def interior_width(self) -> int:
        return self.width - 2

    @property
    def interior_area(self) -> int:
        return self.interior_height * self.interior_width

    @property
    def perimeter(self) -> int:
        return 2 * self.height + 2 * self.width - 4


def enumerate_complete_monochrome_frames(grid: Array) -> Tuple[TypedFrame, ...]:
    """Enumerate exact non-background rectangular perimeters.

    Only the perimeter is constrained. The strict interior remains a payload
    and may contain any ARC colors. A uniformly frame-colored interior is
    excluded because it is a solid rectangle rather than an evidenced frame.
    """

    grid = sanitize_grid(grid)
    height, width = grid.shape
    if height < 3 or width < 3:
        return ()
    background = infer_bg(grid)
    found: set[Tuple[int, int, int, int, int]] = set()
    for color in non_bg_colors(grid, background):
        mask = grid == int(color)
        for top in range(height - 2):
            for bottom in range(top + 2, height):
                shared = mask[top] & mask[bottom]
                column = 0
                while column < width:
                    if not bool(shared[column]):
                        column += 1
                        continue
                    run_left = column
                    while column + 1 < width and bool(shared[column + 1]):
                        column += 1
                    run_right = column
                    if run_right - run_left >= 2:
                        for left in range(run_left, run_right - 1):
                            if not bool(np.all(mask[top : bottom + 1, left])):
                                continue
                            for right in range(left + 2, run_right + 1):
                                if not bool(np.all(mask[top : bottom + 1, right])):
                                    continue
                                interior = mask[top + 1 : bottom, left + 1 : right]
                                if interior.size and not bool(np.all(interior)):
                                    found.add((int(color), top, left, bottom, right))
                    column += 1
    return tuple(
        TypedFrame(color, top, left, bottom, right)
        for color, top, left, bottom, right in sorted(
            found,
            key=lambda item: (item[1], item[2], item[3], item[4], item[0]),
        )
    )


def _typed_frame_measure(frame: TypedFrame, selector: str) -> int:
    if selector == "only_frame":
        return 1
    if selector == "max_interior_area":
        return frame.interior_area
    if selector == "max_outer_area":
        return frame.outer_area
    if selector == "max_perimeter":
        return frame.perimeter
    if selector == "max_height":
        return frame.height
    if selector == "max_width":
        return frame.width
    raise ValueError(f"unknown frame selector {selector!r}")


def _select_typed_frame(frames: Sequence[TypedFrame], selector: str) -> TypedFrame:
    """Apply a partial unique-argmax selector without positional tie-breaking."""

    if selector == "only_frame":
        if len(frames) != 1:
            raise ValueError("only_frame requires exactly one complete frame")
        return frames[0]
    if not frames:
        raise ValueError("no complete monochrome frame")
    values = [_typed_frame_measure(frame, selector) for frame in frames]
    maximum = max(values)
    selected = [frame for frame, value in zip(frames, values) if value == maximum]
    if len(selected) != 1:
        raise ValueError(f"frame selector {selector!r} is tied")
    return selected[0]


def _typed_frame_descriptor(frame: TypedFrame, selector: str) -> Dict[str, object]:
    return {
        "color": int(frame.color),
        "bbox": [int(value) for value in frame.bbox],
        "height": int(frame.height),
        "width": int(frame.width),
        "outer_area": int(frame.outer_area),
        "interior_shape": [int(frame.interior_height), int(frame.interior_width)],
        "interior_area": int(frame.interior_area),
        "perimeter": int(frame.perimeter),
        "selector_value": int(_typed_frame_measure(frame, selector)),
    }


def _frame_extraction_trace(
    grid: Array,
    selector: str,
    renderer: str,
    *,
    frames: Optional[Sequence[TypedFrame]] = None,
) -> Tuple[Array, Tuple[TypedFrame, ...], TypedFrame]:
    grid = sanitize_grid(grid)
    frame_set = (
        tuple(frames)
        if frames is not None
        else enumerate_complete_monochrome_frames(grid)
    )
    selected = _select_typed_frame(frame_set, selector)
    if renderer != "interior":
        raise ValueError(f"unknown frame renderer {renderer!r}")
    output = grid[
        selected.top + 1 : selected.bottom,
        selected.left + 1 : selected.right,
    ].copy()
    if output.shape != (selected.interior_height, selected.interior_width):
        raise ValueError("frame interior shape contract failed")
    return sanitize_grid(output), frame_set, selected


def frame_extract_exact(
    grid: Array,
    selector: str = "max_interior_area",
    renderer: str = "interior",
) -> Array:
    """Select one typed frame and emit its strict interior as a new grid."""

    output, _, _ = _frame_extraction_trace(grid, selector, renderer)
    return output


def frame_extraction_rules(
    train: List[Tuple[Array, Array]],
    tests: List[Array],
) -> List[RuleCandidate]:
    """Compile exact, provenance-bearing frame-to-grid extraction programs."""

    if not train or not tests:
        return []
    if not all(
        target.shape[0] < source.shape[0] and target.shape[1] < source.shape[1]
        for source, target in train
    ):
        return []
    output: List[RuleCandidate] = []
    selector_costs = {
        "only_frame": -1,
        "max_interior_area": 0,
        "max_outer_area": 1,
        "max_perimeter": 1,
        "max_height": 2,
        "max_width": 2,
    }
    try:
        train_frames_by_scene = tuple(
            enumerate_complete_monochrome_frames(source) for source, _ in train
        )
        test_frames_by_scene = tuple(
            enumerate_complete_monochrome_frames(source) for source in tests
        )
    except (TypeError, ValueError):
        return []
    for selector, selector_cost in selector_costs.items():
        renderer = "interior"
        try:
            train_traces = [
                _frame_extraction_trace(
                    source,
                    selector,
                    renderer,
                    frames=frames,
                )
                for (source, _), frames in zip(train, train_frames_by_scene)
            ]
            train_predictions = tuple(trace[0] for trace in train_traces)
            if not all(
                exact(prediction, target)
                for prediction, (_, target) in zip(train_predictions, train)
            ):
                continue
            test_traces = [
                _frame_extraction_trace(
                    source,
                    selector,
                    renderer,
                    frames=frames,
                )
                for source, frames in zip(tests, test_frames_by_scene)
            ]
        except (TypeError, ValueError):
            continue
        train_frame_sets = [trace[1] for trace in train_traces]
        test_frame_sets = [trace[1] for trace in test_traces]
        train_selected = [trace[2] for trace in train_traces]
        test_selected = [trace[2] for trace in test_traces]
        metadata: Dict[str, object] = {
            "compiler_block": "causal_quotient_provenance",
            "typed_entity": "frame",
            "frame_definition": "complete_one_cell_monochrome_rectangular_perimeter",
            "selector": selector,
            "selector_policy": (
                "unique_cardinality"
                if selector == "only_frame"
                else "unique_argmax_without_positional_tie_break"
            ),
            "renderer": "strict_interior_crop",
            "output_shape_contract": "selected_frame.interior_shape",
            "shape_source": "selected_frame.interior_shape",
            "provenance_kind": "test_input_subgrid",
            "test_input_grounded": True,
            "permutation_invariant": True,
            "admissible": True,
            "source_provenance": {
                "kind": "input_subgrid",
                "row_interval": "selected_frame.(top+1):bottom",
                "column_interval": "selected_frame.(left+1):right",
            },
            "partial_program": True,
            "undefined_when": (
                ["frame_count_not_one"]
                if selector == "only_frame"
                else ["no_complete_frame", "selector_tie"]
            ),
            "translation_equivariant": True,
            "color_role_invariant": True,
            "exact_demonstration_contract": True,
            "train_frame_counts": [len(frames) for frames in train_frame_sets],
            "test_frame_counts": [len(frames) for frames in test_frame_sets],
            "train_frame_measurements": [
                [_typed_frame_descriptor(frame, selector) for frame in frames]
                for frames in train_frame_sets
            ],
            "test_frame_measurements": [
                [_typed_frame_descriptor(frame, selector) for frame in frames]
                for frames in test_frame_sets
            ],
            "train_selected_frames": [
                _typed_frame_descriptor(frame, selector) for frame in train_selected
            ],
            "test_selected_frames": [
                _typed_frame_descriptor(frame, selector) for frame in test_selected
            ],
        }
        output.append(
            RuleCandidate(
                name=f"frame_extract_{selector}_interior",
                grids=[trace[0] for trace in test_traces],
                train_error=0,
                complexity=6 + selector_cost,
                family="causal_frame_extract",
                train_grids=train_predictions,
                metadata=metadata,
            )
        )
    return deduplicate_prediction_grids(output)


# -------- quantified, effect-conditioned structural frame roles --------

@dataclass(frozen=True)
class FrameRoleFeatures:
    """Coordinate-free attributes of one clean, typed frame packet.

    Runtime coordinates remain in ``TypedFrame`` for rendering, but compiled
    role programs retain only the attribute, predicate, quantifier, zone, and
    action names.  This prevents a task-local learner from storing a location
    or copying one demonstration's crop into a held-out prediction.
    """

    outer_area: int
    interior_area: int
    height: int
    width: int
    perimeter: int
    payload_cells: int
    payload_colors: int
    payload_components4: int
    payload_density: Fraction
    exterior_cells: int
    exterior_colors: int
    boundary_color_multiplicity: int
    payload_shape_multiplicity: int
    contains_global_rare_color: bool
    inside_more_than_outside: bool
    inside_less_than_outside: bool
    inside_equals_outside: bool
    payload_shape_key: Tuple[int, int, Tuple[int, ...]]


_FRAME_ROLE_NUMERIC_FEATURES: Tuple[str, ...] = (
    "payload_cells",
    "payload_colors",
    "payload_components4",
    "payload_density",
    "interior_area",
    "outer_area",
    "height",
    "width",
    "perimeter",
    "exterior_cells",
    "exterior_colors",
)

_FRAME_ROLE_BOOLEAN_SELECTORS: Tuple[str, ...] = (
    "contains_global_rare_color",
    "inside_more_than_outside",
    "inside_less_than_outside",
    "inside_equals_outside",
    "payload_nonempty",
    "payload_empty",
    "unique_payload_shape",
    "repeated_payload_shape",
    "unique_boundary_color",
    "repeated_boundary_color",
)

_FRAME_ROLE_MASK_MODES: Tuple[str, ...] = (
    "boundary",
    "strict_interior",
    "interior_foreground",
    "interior_background",
    "full_bbox",
    "local_exterior_band_1",
)


def _frame_rectangles_have_clearance(left: TypedFrame, right: TypedFrame) -> bool:
    """Return whether two frame boxes are disjoint with a one-cell gap."""

    return bool(
        left.right + 1 < right.left
        or right.right + 1 < left.left
        or left.bottom + 1 < right.top
        or right.bottom + 1 < left.top
    )


def _enumerate_clean_frames_bounded(
    grid: Array,
    *,
    maximum_frames: int = 64,
) -> Tuple[TypedFrame, ...]:
    """Enumerate frame candidates with an early ambiguity/resource guard.

    The legacy detector intentionally enumerates every complete perimeter.  A
    nearly solid 30x30 rectangle can therefore contain tens of thousands of
    overlapping perimeter aliases.  The quantified-role adapter cannot use
    such a scene (its domain requires a small set of disjoint frames), so it
    aborts as soon as that fact is witnessed instead of completing the
    combinatorial enumeration.
    """

    source = sanitize_grid(grid)
    height, width = source.shape
    if height < 3 or width < 3:
        return ()
    # Unlike the legacy ARC-wide helper, the role adapter does not assume that
    # color 0 is background merely because it occurs.  A majority policy is
    # input-only and correctly supports stable nonzero-background scenes.
    background = majority_color(source)
    found: set[Tuple[int, int, int, int, int]] = set()
    limit = max(1, int(maximum_frames))
    for color in non_bg_colors(source, background):
        mask = source == int(color)
        for top in range(height - 2):
            for bottom in range(top + 2, height):
                shared = mask[top] & mask[bottom]
                column = 0
                while column < width:
                    if not bool(shared[column]):
                        column += 1
                        continue
                    run_left = column
                    while column + 1 < width and bool(shared[column + 1]):
                        column += 1
                    run_right = column
                    if run_right - run_left >= 2:
                        for left in range(run_left, run_right - 1):
                            if not bool(np.all(mask[top : bottom + 1, left])):
                                continue
                            for right in range(left + 2, run_right + 1):
                                if not bool(np.all(mask[top : bottom + 1, right])):
                                    continue
                                interior = mask[top + 1 : bottom, left + 1 : right]
                                if interior.size and not bool(np.all(interior)):
                                    found.add((int(color), top, left, bottom, right))
                                    if len(found) > limit:
                                        raise ValueError(
                                            "clean-frame candidate budget exceeded"
                                        )
                    column += 1
    return tuple(
        TypedFrame(color, top, left, bottom, right)
        for color, top, left, bottom, right in sorted(
            found,
            key=lambda item: (item[1], item[2], item[3], item[4], item[0]),
        )
    )


def _clean_typed_frames(grid: Array) -> Tuple[TypedFrame, ...]:
    """Enumerate the deliberately narrow v1.3 clean-frame domain.

    Nested, touching, and shared-wall frames are left for the later
    boundary-face incidence representation.  Explicit abstention here is
    preferable to silently assigning the same pixels to incompatible packets.
    """

    frames = _enumerate_clean_frames_bounded(grid)
    if not frames:
        raise ValueError("no complete monochrome frames")
    for index, left in enumerate(frames):
        for right in frames[index + 1 :]:
            if not _frame_rectangles_have_clearance(left, right):
                raise ValueError("frames are nested, touching, or share a wall")
    return frames


def _frame_boundary_mask(grid: Array, frame: TypedFrame) -> Array:
    source = sanitize_grid(grid)
    mask = np.zeros(source.shape, dtype=bool)
    top, left, bottom, right = frame.bbox
    mask[top, left : right + 1] = True
    mask[bottom, left : right + 1] = True
    mask[top : bottom + 1, left] = True
    mask[top : bottom + 1, right] = True
    return mask


def _frame_interior_mask(grid: Array, frame: TypedFrame) -> Array:
    source = sanitize_grid(grid)
    mask = np.zeros(source.shape, dtype=bool)
    top, left, bottom, right = frame.bbox
    mask[top + 1 : bottom, left + 1 : right] = True
    return mask


def _frame_local_exterior_mask(grid: Array, frame: TypedFrame, radius: int = 1) -> Array:
    source = sanitize_grid(grid)
    radius = max(1, int(radius))
    top, left, bottom, right = frame.bbox
    outer_top = max(0, top - radius)
    outer_left = max(0, left - radius)
    outer_bottom = min(source.shape[0] - 1, bottom + radius)
    outer_right = min(source.shape[1] - 1, right + radius)
    mask = np.zeros(source.shape, dtype=bool)
    mask[outer_top : outer_bottom + 1, outer_left : outer_right + 1] = True
    mask[top : bottom + 1, left : right + 1] = False
    if not np.any(mask):
        raise ValueError("frame has no visible local exterior band")
    return mask


def _frame_role_mask(
    grid: Array,
    frame: TypedFrame,
    mode: str,
    *,
    background: Optional[int] = None,
) -> Array:
    source = sanitize_grid(grid)
    background = majority_color(source) if background is None else int(background)
    if mode == "boundary":
        mask = _frame_boundary_mask(source, frame)
    elif mode == "strict_interior":
        mask = _frame_interior_mask(source, frame)
    elif mode == "interior_foreground":
        mask = _frame_interior_mask(source, frame) & (source != background)
    elif mode == "interior_background":
        mask = _frame_interior_mask(source, frame) & (source == background)
    elif mode == "full_bbox":
        mask = np.zeros(source.shape, dtype=bool)
        top, left, bottom, right = frame.bbox
        mask[top : bottom + 1, left : right + 1] = True
    elif mode == "local_exterior_band_1":
        mask = _frame_local_exterior_mask(source, frame, radius=1)
    else:
        raise ValueError(f"unknown frame-role mask mode {mode!r}")
    if not np.any(mask):
        raise ValueError("frame-role mask is empty")
    return mask


def _palette_shape_key(grid: Array, background: int) -> Tuple[int, int, Tuple[int, ...]]:
    """Return a palette-renaming-invariant raster signature."""

    source = sanitize_grid(grid)
    mapping: Dict[int, int] = {int(background): 0}
    next_value = 1
    normalized: List[int] = []
    for raw in source.ravel():
        color = int(raw)
        if color not in mapping:
            mapping[color] = next_value
            next_value += 1
        normalized.append(mapping[color])
    return source.shape[0], source.shape[1], tuple(normalized)


def _frame_payload_component_count(interior: Array, background: int) -> int:
    return len(components(interior, bg=background))


def _frame_role_feature_records(
    grid: Array,
    frames: Sequence[TypedFrame],
) -> Tuple[FrameRoleFeatures, ...]:
    source = sanitize_grid(grid)
    background = majority_color(source)
    non_background = [
        int(value) for value in source.ravel() if int(value) != int(background)
    ]
    rare = None
    if non_background:
        counts = Counter(non_background)
        minimum = min(counts.values())
        rare_colors = [color for color, count in counts.items() if count == minimum]
        # A frequency tie is a set-valued relation, not permission to select a
        # packet by numeric palette order.
        if len(rare_colors) == 1:
            rare = int(rare_colors[0])

    payload_keys: List[Tuple[int, int, Tuple[int, ...]]] = []
    raw_records: List[Dict[str, object]] = []
    boundary_counts = Counter(int(frame.color) for frame in frames)
    for frame in frames:
        top, left, bottom, right = frame.bbox
        interior = source[top + 1 : bottom, left + 1 : right]
        interior_mask = interior != int(background)
        payload_cells = int(np.count_nonzero(interior_mask))
        payload_colors = len(
            {int(value) for value in interior.ravel() if int(value) != int(background)}
        )
        payload_key = _palette_shape_key(interior, background)
        payload_keys.append(payload_key)
        exterior_mask = _frame_local_exterior_mask(source, frame, radius=1)
        exterior_values = source[exterior_mask]
        exterior_cells = int(np.count_nonzero(exterior_values != int(background)))
        exterior_colors = len(
            {
                int(value)
                for value in exterior_values
                if int(value) != int(background)
            }
        )
        raw_records.append(
            {
                "frame": frame,
                "payload_cells": payload_cells,
                "payload_colors": payload_colors,
                "payload_components4": _frame_payload_component_count(
                    interior,
                    background,
                ),
                "payload_density": Fraction(payload_cells, max(1, frame.interior_area)),
                "exterior_cells": exterior_cells,
                "exterior_colors": exterior_colors,
                "contains_global_rare_color": bool(
                    rare is not None and np.any(interior == int(rare))
                ),
                "payload_shape_key": payload_key,
            }
        )
    payload_counts = Counter(payload_keys)
    return tuple(
        FrameRoleFeatures(
            outer_area=int(record["frame"].outer_area),
            interior_area=int(record["frame"].interior_area),
            height=int(record["frame"].height),
            width=int(record["frame"].width),
            perimeter=int(record["frame"].perimeter),
            payload_cells=int(record["payload_cells"]),
            payload_colors=int(record["payload_colors"]),
            payload_components4=int(record["payload_components4"]),
            payload_density=record["payload_density"],
            exterior_cells=int(record["exterior_cells"]),
            exterior_colors=int(record["exterior_colors"]),
            boundary_color_multiplicity=int(
                boundary_counts[int(record["frame"].color)]
            ),
            payload_shape_multiplicity=int(
                payload_counts[record["payload_shape_key"]]
            ),
            contains_global_rare_color=bool(record["contains_global_rare_color"]),
            inside_more_than_outside=(
                int(record["payload_cells"]) > int(record["exterior_cells"])
            ),
            inside_less_than_outside=(
                int(record["payload_cells"]) < int(record["exterior_cells"])
            ),
            inside_equals_outside=(
                int(record["payload_cells"]) == int(record["exterior_cells"])
            ),
            payload_shape_key=record["payload_shape_key"],
        )
        for record in raw_records
    )


def _select_frame_role_indices(
    features: Sequence[FrameRoleFeatures],
    selector: str,
) -> Tuple[int, ...]:
    values = tuple(features)
    if not values:
        raise ValueError("empty frame-role domain")
    if selector == "all":
        return tuple(range(len(values)))
    if selector == "only_frame":
        if len(values) != 1:
            raise ValueError("only_frame role requires one packet")
        return (0,)

    for prefix, maximum, require_unique in (
        ("unique_max_", True, True),
        ("unique_min_", False, True),
        ("all_max_", True, False),
        ("all_min_", False, False),
    ):
        if selector.startswith(prefix):
            attribute = selector[len(prefix) :]
            if attribute not in _FRAME_ROLE_NUMERIC_FEATURES:
                raise ValueError(f"unknown frame-role feature {attribute!r}")
            extracted = [getattr(item, attribute) for item in values]
            target = max(extracted) if maximum else min(extracted)
            selected = tuple(
                index for index, value in enumerate(extracted) if value == target
            )
            if require_unique and len(selected) != 1:
                raise ValueError("frame-role extremum is tied")
            return selected

    if selector == "payload_nonempty":
        selected = tuple(index for index, item in enumerate(values) if item.payload_cells > 0)
    elif selector == "payload_empty":
        selected = tuple(index for index, item in enumerate(values) if item.payload_cells == 0)
    elif selector == "unique_payload_shape":
        selected = tuple(
            index
            for index, item in enumerate(values)
            if item.payload_shape_multiplicity == 1
        )
    elif selector == "repeated_payload_shape":
        selected = tuple(
            index
            for index, item in enumerate(values)
            if item.payload_shape_multiplicity > 1
        )
    elif selector == "unique_boundary_color":
        selected = tuple(
            index
            for index, item in enumerate(values)
            if item.boundary_color_multiplicity == 1
        )
    elif selector == "repeated_boundary_color":
        selected = tuple(
            index
            for index, item in enumerate(values)
            if item.boundary_color_multiplicity > 1
        )
    elif selector in {
        "contains_global_rare_color",
        "inside_more_than_outside",
        "inside_less_than_outside",
        "inside_equals_outside",
    }:
        selected = tuple(
            index for index, item in enumerate(values) if bool(getattr(item, selector))
        )
    else:
        raise ValueError(f"unknown frame-role selector {selector!r}")
    if not selected:
        raise ValueError("frame-role predicate selected no packets")
    return selected


def _frame_role_quantifier_valid(
    quantifier: str,
    selector: str,
    selections: Sequence[Sequence[int]],
    domain_sizes: Sequence[int],
) -> bool:
    if not selections or len(selections) != len(domain_sizes):
        return False
    if quantifier == "THE":
        return all(len(selected) == 1 for selected in selections) and any(
            size > 1 for size in domain_sizes
        )
    if quantifier == "FOR_EACH":
        return all(len(selected) >= 1 for selected in selections) and any(
            len(selected) >= 2 for selected in selections
        )
    if quantifier in {"ALL_ARGMAX", "ALL_ARGMIN"}:
        required_prefix = "all_max_" if quantifier == "ALL_ARGMAX" else "all_min_"
        return selector.startswith(required_prefix) and any(
            len(selected) >= 2 for selected in selections
        )
    return False


def _frame_role_selector_specs() -> Tuple[Tuple[str, str], ...]:
    # Put relational/class predicates before the much larger extremum grid so
    # every semantic kind receives deterministic search budget on frame-rich
    # scenes. ``only_frame`` is retained for same-cardinality completeness but
    # its THE evidence gate deliberately rejects one-frame-only ambiguity.
    specs: List[Tuple[str, str]] = [("all", "FOR_EACH")]
    for selector in _FRAME_ROLE_BOOLEAN_SELECTORS:
        specs.extend(((selector, "THE"), (selector, "FOR_EACH")))
    for feature in _FRAME_ROLE_NUMERIC_FEATURES:
        specs.extend(
            (
                (f"unique_max_{feature}", "THE"),
                (f"unique_min_{feature}", "THE"),
                (f"all_max_{feature}", "ALL_ARGMAX"),
                (f"all_min_{feature}", "ALL_ARGMIN"),
            )
        )
    specs.append(("only_frame", "THE"))
    return tuple(specs)


def _frame_role_selector_cost(selector: str) -> int:
    if selector == "all":
        return 0
    if selector in {"payload_nonempty", "payload_empty"}:
        return 1
    if selector in {
        "inside_more_than_outside",
        "inside_less_than_outside",
        "inside_equals_outside",
        "unique_payload_shape",
        "repeated_payload_shape",
        "unique_boundary_color",
        "repeated_boundary_color",
    }:
        return 2
    if selector == "contains_global_rare_color":
        return 3
    if selector.startswith(("unique_max_", "unique_min_")):
        return 2
    if selector.startswith(("all_max_", "all_min_")):
        return 3
    return 1


def _frame_role_action_value(
    source: Array,
    frame: TypedFrame,
    action: str,
    color: Optional[int],
) -> int:
    if action == "paint_constant" and color is not None:
        return int(color)
    if action == "erase_to_background":
        return int(majority_color(source))
    if action == "paint_boundary_color":
        return int(frame.color)
    raise ValueError(f"unknown frame-role action {action!r}")


def _render_frame_role_rewrite(
    grid: Array,
    frames: Sequence[TypedFrame],
    selected: Sequence[int],
    mask_mode: str,
    action: str,
    color: Optional[int],
) -> Tuple[Array, Tuple[Array, ...]]:
    source = sanitize_grid(grid)
    output = source.copy()
    assignments: Dict[Tuple[int, int], int] = {}
    masks: List[Array] = []
    for index in selected:
        frame = frames[int(index)]
        mask = _frame_role_mask(source, frame, mask_mode)
        masks.append(mask)
        value = _frame_role_action_value(source, frame, action, color)
        for raw_row, raw_column in np.argwhere(mask):
            coordinate = (int(raw_row), int(raw_column))
            previous = assignments.get(coordinate)
            if previous is not None and previous != value:
                raise ValueError("overlapping frame roles request conflicting writes")
            assignments[coordinate] = value
    if not assignments:
        raise ValueError("frame-role rewrite has no assignments")
    for (row, column), value in assignments.items():
        output[row, column] = int(value)
    return sanitize_grid(output), tuple(masks)


def _frame_role_effect_evidence(
    source: Array,
    target: Array,
    frames: Sequence[TypedFrame],
    selected: Sequence[int],
    mask_mode: str,
    action: str,
    color: Optional[int],
) -> Dict[str, int]:
    source = sanitize_grid(source)
    target = sanitize_grid(target)
    if source.shape != target.shape:
        raise ValueError("effect evidence requires same-shape input and output")
    selected_set = {int(index) for index in selected}
    positive = 0
    vacuous = 0
    negative_counterfactual = 0
    for index, frame in enumerate(frames):
        mask = _frame_role_mask(source, frame, mask_mode)
        value = _frame_role_action_value(source, frame, action, color)
        would_change = bool(np.any(source[mask] != int(value)))
        actual_change = bool(np.any(source[mask] != target[mask]))
        if index in selected_set:
            if would_change and actual_change:
                positive += 1
            else:
                vacuous += 1
        elif would_change and bool(np.array_equal(source[mask], target[mask])):
            negative_counterfactual += 1
    return {
        "positive_effect_support": int(positive),
        "negative_counterfactual_support": int(negative_counterfactual),
        "vacuous_selected_support": int(vacuous),
        "selected_support": int(len(selected_set)),
        "unselected_support": int(len(frames) - len(selected_set)),
    }


def _frame_role_crop(
    grid: Array,
    frames: Sequence[TypedFrame],
    selected: Sequence[int],
    zone: str,
    pack_mode: str,
) -> Array:
    source = sanitize_grid(grid)
    ordered = sorted(
        (frames[int(index)] for index in selected),
        key=lambda frame: (frame.top, frame.left, frame.bottom, frame.right, frame.color),
    )
    if not ordered:
        raise ValueError("frame-role crop selected no packets")
    crops: List[Array] = []
    for frame in ordered:
        if zone == "strict_interior":
            crop = source[frame.top + 1 : frame.bottom, frame.left + 1 : frame.right]
        elif zone == "full_frame":
            crop = source[frame.top : frame.bottom + 1, frame.left : frame.right + 1]
        else:
            raise ValueError(f"unknown frame-role crop zone {zone!r}")
        crops.append(sanitize_grid(crop))
    if len(crops) == 1:
        return crops[0].copy()
    if pack_mode == "horizontal":
        if len({crop.shape[0] for crop in crops}) != 1:
            raise ValueError("horizontal frame-role crops have unequal heights")
        result = np.concatenate(crops, axis=1)
    elif pack_mode == "vertical":
        if len({crop.shape[1] for crop in crops}) != 1:
            raise ValueError("vertical frame-role crops have unequal widths")
        result = np.concatenate(crops, axis=0)
    else:
        raise ValueError(f"unknown frame-role pack mode {pack_mode!r}")
    if result.shape[0] > MAX_SIDE or result.shape[1] > MAX_SIDE:
        raise ValueError("packed frame-role output exceeds ARC bounds")
    return sanitize_grid(result)


def _frame_selection_signature(
    grid: Array,
    frames: Sequence[TypedFrame],
    selected: Sequence[int],
    mask_mode: str,
) -> str:
    source = sanitize_grid(grid)
    combined = np.zeros(source.shape, dtype=np.int16)
    for index in selected:
        combined[_frame_role_mask(source, frames[int(index)], mask_mode)] = 1
    return hashlib.sha256(combined.tobytes()).hexdigest()


def _quotient_frame_role_candidates(
    candidates: Sequence[RuleCandidate],
) -> List[RuleCandidate]:
    """Collapse selector aliases with identical observed behavior.

    Hypotheses that diverge on the held-out inputs remain separate.  Exact-fit
    aliases that choose the same packets and emit the same grids receive one
    posterior vote rather than manufacturing support through different names.
    """

    groups: Dict[Tuple[object, ...], List[RuleCandidate]] = defaultdict(list)
    for candidate in candidates:
        metadata = candidate.metadata or {}
        key = (
            candidate.family,
            str(metadata.get("renderer")),
            str(metadata.get("action")),
            tuple(metadata.get("train_selection_signatures", [])),
            tuple(metadata.get("test_selection_signatures", [])),
            tuple(canonical(grid) for grid in candidate.grids),
        )
        groups[key].append(candidate)
    output: List[RuleCandidate] = []
    for key in sorted(groups, key=repr):
        aliases = sorted(
            groups[key],
            key=lambda candidate: (candidate.complexity, candidate.name),
        )
        chosen = aliases[0]
        metadata = dict(chosen.metadata or {})
        metadata["semantic_alias_count"] = len(aliases)
        metadata["semantic_aliases"] = [candidate.name for candidate in aliases]
        output.append(
            RuleCandidate(
                name=chosen.name,
                grids=[grid.copy() for grid in chosen.grids],
                train_error=chosen.train_error,
                complexity=chosen.complexity,
                family=chosen.family,
                train_grids=tuple(grid.copy() for grid in chosen.train_grids),
                metadata=metadata,
            )
        )
    return sorted(output, key=lambda candidate: (candidate.complexity, candidate.family, candidate.name))


def quantified_structural_role_rules(
    train: List[Tuple[Array, Array]],
    tests: List[Array],
    maximum_programs: int = 768,
    maximum_exact: int = 20,
) -> List[RuleCandidate]:
    """Learn bounded structural roles over clean frame packets.

    Geometry is enumerated from each input before outputs are consulted.
    Demonstration outputs only score a finite role/quantifier/renderer grammar.
    The strict first release requires witnessed competitors, witnessed
    multi-instance effects, or witnessed tied extrema as appropriate.
    """

    if len(train) < 2 or not tests:
        return []
    try:
        train_frames = tuple(_clean_typed_frames(source) for source, _ in train)
        test_frames = tuple(_clean_typed_frames(source) for source in tests)
        train_features = tuple(
            _frame_role_feature_records(source, frames)
            for (source, _), frames in zip(train, train_frames)
        )
        test_features = tuple(
            _frame_role_feature_records(source, frames)
            for source, frames in zip(tests, test_frames)
        )
    except (TypeError, ValueError):
        return []

    output: List[RuleCandidate] = []
    attempted = 0
    changed_target_colors = {
        int(target[row, column])
        for source, target in train
        if source.shape == target.shape
        for row, column in np.argwhere(source != target)
    }
    target_colors = sorted(changed_target_colors)
    if not target_colors:
        target_colors = sorted(
            {
                int(value)
                for _, target in train
                for value in sanitize_grid(target).ravel()
            }
        )
    for selector, quantifier in _frame_role_selector_specs():
        try:
            selected_train = tuple(
                _select_frame_role_indices(features, selector)
                for features in train_features
            )
            selected_tests = tuple(
                _select_frame_role_indices(features, selector)
                for features in test_features
            )
        except (TypeError, ValueError):
            continue
        if not _frame_role_quantifier_valid(
            quantifier,
            selector,
            selected_train,
            [len(frames) for frames in train_frames],
        ):
            continue

        # Same-shape structural rewrites with packet-level effect evidence.
        if all(source.shape == target.shape for source, target in train):
            action_specs: List[Tuple[str, Optional[int]]] = [
                ("erase_to_background", None),
                ("paint_boundary_color", None),
            ]
            action_specs.extend(("paint_constant", color) for color in target_colors)
            for mask_mode in _FRAME_ROLE_MASK_MODES:
                for action, color in action_specs:
                    if attempted >= max(1, int(maximum_programs)):
                        return _quotient_frame_role_candidates(output)[:maximum_exact]
                    attempted += 1
                    try:
                        train_predictions: List[Array] = []
                        evidence_records: List[Dict[str, int]] = []
                        train_signatures: List[str] = []
                        for (source, target), frames, selected in zip(
                            train,
                            train_frames,
                            selected_train,
                        ):
                            prediction, _ = _render_frame_role_rewrite(
                                source,
                                frames,
                                selected,
                                mask_mode,
                                action,
                                color,
                            )
                            if not exact(prediction, target) or exact(source, target):
                                raise ValueError("rewrite does not exactly explain a nonempty delta")
                            evidence = _frame_role_effect_evidence(
                                source,
                                target,
                                frames,
                                selected,
                                mask_mode,
                                action,
                                color,
                            )
                            if evidence["positive_effect_support"] != len(selected):
                                raise ValueError("selected frame role is vacuous")
                            train_predictions.append(prediction)
                            evidence_records.append(evidence)
                            train_signatures.append(
                                _frame_selection_signature(
                                    source,
                                    frames,
                                    selected,
                                    mask_mode,
                                )
                            )
                        evidence_totals = {
                            key: sum(record[key] for record in evidence_records)
                            for key in evidence_records[0]
                        }
                        if quantifier == "THE" and evidence_totals[
                            "negative_counterfactual_support"
                        ] <= 0:
                            continue
                        if quantifier == "FOR_EACH" and not any(
                            record["positive_effect_support"] >= 2
                            for record in evidence_records
                        ):
                            continue
                        test_predictions: List[Array] = []
                        test_signatures: List[str] = []
                        for source, frames, selected in zip(
                            tests,
                            test_frames,
                            selected_tests,
                        ):
                            prediction, _ = _render_frame_role_rewrite(
                                source,
                                frames,
                                selected,
                                mask_mode,
                                action,
                                color,
                            )
                            test_predictions.append(prediction)
                            test_signatures.append(
                                _frame_selection_signature(
                                    source,
                                    frames,
                                    selected,
                                    mask_mode,
                                )
                            )
                    except (TypeError, ValueError):
                        continue
                    mechanism_key = (
                        f"frame_role|{selector}|{quantifier}|{mask_mode}|"
                        f"{action}|{color if color is not None else 'dynamic'}"
                    )
                    output.append(
                        RuleCandidate(
                            name=f"quantified_{mechanism_key}",
                            grids=[grid.copy() for grid in test_predictions],
                            train_error=0,
                            complexity=(
                                9
                                + _frame_role_selector_cost(selector)
                                + int(action == "paint_constant")
                            ),
                            family="causal_frame_role_rewrite",
                            train_grids=tuple(grid.copy() for grid in train_predictions),
                            metadata={
                                "compiler_block": "quantified_structural_role",
                                "typed_entity": "complete_monochrome_frame_packet",
                                "domain": "clean_complete_frames",
                                "background_policy": "input_grid_majority_color",
                                "selector": selector,
                                "quantifier": quantifier,
                                "selector_policy": "coordinate_free_partial_selector",
                                "mask_mode": mask_mode,
                                "renderer": "same_shape_frame_zone_rewrite",
                                "action": action,
                                "target_color": color,
                                "effect_conditioned": True,
                                "effect_evidence": evidence_totals,
                                "semantic_mechanism_key": mechanism_key,
                                "version_space_key": f"{selector}|{quantifier}",
                                "train_selection_signatures": train_signatures,
                                "test_selection_signatures": test_signatures,
                                "output_lineage": {
                                    "kind": "test_input_frame_zone_transform",
                                    "zone": mask_mode,
                                },
                                "provenance_kind": "test_input_structural_role_transform",
                                "test_input_grounded": True,
                                "permutation_invariant": True,
                                "admissible": True,
                                "partial_program": True,
                                "stores_coordinates": False,
                                "stores_numeric_thresholds": False,
                                "exact_demonstration_contract": True,
                            },
                        )
                    )

        # Structural crops and demonstrated multi-packet packing.
        for zone in ("strict_interior", "full_frame"):
            pack_modes = ("horizontal", "vertical") if quantifier != "THE" else ("horizontal",)
            for pack_mode in pack_modes:
                if attempted >= max(1, int(maximum_programs)):
                    return _quotient_frame_role_candidates(output)[:maximum_exact]
                attempted += 1
                try:
                    train_predictions = [
                        _frame_role_crop(source, frames, selected, zone, pack_mode)
                        for (source, _), frames, selected in zip(
                            train,
                            train_frames,
                            selected_train,
                        )
                    ]
                    if not all(
                        exact(prediction, target)
                        for prediction, (_, target) in zip(train_predictions, train)
                    ):
                        continue
                    test_predictions = [
                        _frame_role_crop(source, frames, selected, zone, pack_mode)
                        for source, frames, selected in zip(
                            tests,
                            test_frames,
                            selected_tests,
                        )
                    ]
                except (TypeError, ValueError):
                    continue
                mechanism_key = (
                    f"frame_role_extract|{selector}|{quantifier}|{zone}|{pack_mode}"
                )
                output.append(
                    RuleCandidate(
                        name=f"quantified_{mechanism_key}",
                        grids=[grid.copy() for grid in test_predictions],
                        train_error=0,
                        complexity=(
                            7
                            + _frame_role_selector_cost(selector)
                            + int(quantifier != "THE")
                        ),
                        family="causal_frame_role_extract",
                        train_grids=tuple(grid.copy() for grid in train_predictions),
                        metadata={
                            "compiler_block": "quantified_structural_role",
                            "typed_entity": "complete_monochrome_frame_packet",
                            "domain": "clean_complete_frames",
                            "background_policy": "input_grid_majority_color",
                            "selector": selector,
                            "quantifier": quantifier,
                            "selector_policy": "coordinate_free_partial_selector",
                            "renderer": "frame_zone_extract_and_pack",
                            "action": "extract",
                            "crop_zone": zone,
                            "pack_mode": pack_mode,
                            "ordering_policy": "spatial_reading_order",
                            "effect_conditioned": True,
                            "effect_evidence": {
                                "lineage_supported_demonstrations": len(train),
                                "multi_packet_demonstrations": sum(
                                    len(selected) >= 2 for selected in selected_train
                                ),
                            },
                            "semantic_mechanism_key": mechanism_key,
                            "version_space_key": f"{selector}|{quantifier}",
                            "train_selection_signatures": [
                                hashlib.sha256(
                                    repr(tuple(selected)).encode("utf-8")
                                ).hexdigest()
                                for selected in selected_train
                            ],
                            "test_selection_signatures": [
                                hashlib.sha256(
                                    repr(tuple(selected)).encode("utf-8")
                                ).hexdigest()
                                for selected in selected_tests
                            ],
                            "output_lineage": {
                                "kind": "test_input_frame_subgrids",
                                "zone": zone,
                                "pack_mode": pack_mode,
                            },
                            "provenance_kind": "test_input_subgrid",
                            "test_input_grounded": True,
                            "permutation_invariant": True,
                            "admissible": True,
                            "partial_program": True,
                            "stores_coordinates": False,
                            "stores_numeric_thresholds": False,
                            "exact_demonstration_contract": True,
                        },
                    )
                )
    return _quotient_frame_role_candidates(output)[: max(1, int(maximum_exact))]


def frame_parity_fill_rules(
    train: List[Tuple[Array, Array]],
    tests: List[Array],
) -> List[RuleCandidate]:
    """Learn a witnessed parity-to-color renderer over every clean square face."""

    if len(train) < 2 or not tests:
        return []
    def parity_frames(grid: Array) -> Tuple[TypedFrame, ...]:
        frames = _enumerate_clean_frames_bounded(grid)
        if not frames:
            raise ValueError("no complete parity frames")
        for index, left in enumerate(frames):
            for right in frames[index + 1 :]:
                boxes_disjoint = bool(
                    left.right < right.left
                    or right.right < left.left
                    or left.bottom < right.top
                    or right.bottom < left.top
                )
                if not boxes_disjoint:
                    raise ValueError("parity frame boxes overlap or nest")
        return frames

    mapping: Dict[int, int] = {}
    train_predictions: List[Array] = []
    train_records: List[Dict[str, object]] = []
    total_positive = 0
    try:
        for source, target in train:
            source = sanitize_grid(source)
            target = sanitize_grid(target)
            if source.shape != target.shape:
                raise ValueError("frame parity fill requires same-shape outputs")
            frames = parity_frames(source)
            combined = np.zeros(source.shape, dtype=bool)
            observed_parities: List[int] = []
            observed_colors: List[int] = []
            for frame in frames:
                if frame.interior_height != frame.interior_width:
                    raise ValueError("frame parity fill requires square interiors")
                mask = _frame_interior_mask(source, frame)
                values = {int(value) for value in target[mask]}
                if len(values) != 1:
                    raise ValueError("frame interior is not uniformly rendered")
                value = next(iter(values))
                parity = int(frame.interior_height % 2)
                previous = mapping.get(parity)
                if previous is not None and previous != value:
                    raise ValueError("frame parity maps to conflicting colors")
                mapping[parity] = value
                if not bool(np.any(source[mask] != value)):
                    raise ValueError("frame parity effect is vacuous")
                total_positive += 1
                combined |= mask
                observed_parities.append(parity)
                observed_colors.append(value)
            if not bool(np.array_equal(source[~combined], target[~combined])):
                raise ValueError("frame parity renderer changes cells outside faces")
            prediction = source.copy()
            for frame, parity in zip(frames, observed_parities, strict=True):
                prediction[_frame_interior_mask(source, frame)] = mapping[parity]
            if not exact(prediction, target):
                raise ValueError("frame parity renderer does not fit demonstration")
            train_predictions.append(sanitize_grid(prediction))
            train_records.append(
                {
                    "frame_count": len(frames),
                    "interior_parities": observed_parities,
                    "rendered_colors": observed_colors,
                }
            )
        if set(mapping) != {0, 1} or total_positive < 4:
            return []

        test_predictions: List[Array] = []
        test_records: List[Dict[str, object]] = []
        for source in tests:
            source = sanitize_grid(source)
            frames = parity_frames(source)
            prediction = source.copy()
            parities: List[int] = []
            for frame in frames:
                if frame.interior_height != frame.interior_width:
                    raise ValueError("held-out frame is not square")
                parity = int(frame.interior_height % 2)
                if parity not in mapping:
                    raise ValueError("held-out parity was not witnessed")
                prediction[_frame_interior_mask(source, frame)] = mapping[parity]
                parities.append(parity)
            test_predictions.append(sanitize_grid(prediction))
            test_records.append(
                {"frame_count": len(frames), "interior_parities": parities}
            )
    except (TypeError, ValueError):
        return []

    return [
        RuleCandidate(
            name="quantified_for_each_square_face_fill_by_interior_parity",
            grids=[grid.copy() for grid in test_predictions],
            train_error=0,
            complexity=8,
            family="causal_frame_role_parity_fill",
            train_grids=tuple(grid.copy() for grid in train_predictions),
            metadata={
                "compiler_block": "quantified_structural_role",
                "typed_entity": "clean_square_frame_face",
                "selector": "all",
                "quantifier": "FOR_EACH",
                "predicate": "interior_side_length_parity",
                "renderer": "uniform_strict_interior_fill",
                "parity_color_mapping": {
                    "even": int(mapping[0]),
                    "odd": int(mapping[1]),
                },
                "train_traces": train_records,
                "test_traces": test_records,
                "effect_evidence": {
                    "positive_faces": total_positive,
                    "witnessed_parity_classes": 2,
                    "outside_cells_preserved": True,
                },
                "semantic_mechanism_key": "frame_role|all|FOR_EACH|interior_parity|uniform_fill",
                "output_lineage": {
                    "kind": "test_input_frame_face_transform",
                    "zone": "strict_interior",
                },
                "provenance_kind": "test_input_structural_role_transform",
                "test_input_grounded": True,
                "permutation_invariant": True,
                "translation_equivariant": True,
                "admissible": True,
                "partial_program": True,
                "stores_coordinates": False,
                "stores_numeric_thresholds": False,
                "exact_demonstration_contract": True,
                "empirical_promotion_eligible": True,
            },
        )
    ]


def _background_regions_for_color(grid: Array, background: int) -> Tuple[Obj, ...]:
    source = sanitize_grid(grid)
    height, width = source.shape
    seen = np.zeros(source.shape, dtype=bool)
    output: List[Obj] = []
    for row in range(height):
        for column in range(width):
            if seen[row, column] or int(source[row, column]) != int(background):
                continue
            queue = deque([(row, column)])
            seen[row, column] = True
            cells: List[Tuple[int, int]] = []
            while queue:
                current_row, current_column = queue.popleft()
                cells.append((current_row, current_column))
                for delta_row, delta_column in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                    next_row = current_row + delta_row
                    next_column = current_column + delta_column
                    if (
                        0 <= next_row < height
                        and 0 <= next_column < width
                        and not seen[next_row, next_column]
                        and int(source[next_row, next_column]) == int(background)
                    ):
                        seen[next_row, next_column] = True
                        queue.append((next_row, next_column))
            rows = [value[0] for value in cells]
            columns = [value[1] for value in cells]
            output.append(
                Obj(
                    int(background),
                    cells,
                    (min(rows), min(columns), max(rows), max(columns)),
                )
            )
    return tuple(output)


def _is_selected_rectangular_face(
    grid: Array,
    region: Obj,
    background: int,
) -> bool:
    """Recognize a rectangular face closed by a junction-bearing barrier."""

    source = sanitize_grid(grid)
    if region.size != region.height * region.width:
        return False
    height, width = source.shape
    canvas_sides: set[str] = set()
    adjacent_barrier: set[Tuple[int, int]] = set()
    for row, column in region.cells:
        if row == 0:
            canvas_sides.add("top")
        if row == height - 1:
            canvas_sides.add("bottom")
        if column == 0:
            canvas_sides.add("left")
        if column == width - 1:
            canvas_sides.add("right")
        for delta_row, delta_column in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            next_row = row + delta_row
            next_column = column + delta_column
            if (
                0 <= next_row < height
                and 0 <= next_column < width
                and int(source[next_row, next_column]) != int(background)
            ):
                adjacent_barrier.add((next_row, next_column))
    if len(canvas_sides) > 1:
        return False
    return any(
        sum(
            0 <= row + delta_row < height
            and 0 <= column + delta_column < width
            and int(source[row + delta_row, column + delta_column]) != int(background)
            for delta_row, delta_column in ((1, 0), (-1, 0), (0, 1), (0, -1))
        )
        >= 3
        for row, column in adjacent_barrier
    )


def rectangular_face_fill_rules(
    train: List[Tuple[Array, Array]],
    tests: List[Array],
) -> List[RuleCandidate]:
    """Fill rectangular planar faces, treating the canvas edge as a wall."""

    if len(train) < 2 or not tests:
        return []
    fill_color: Optional[int] = None
    train_predictions: List[Array] = []
    train_records: List[Dict[str, object]] = []
    selected_border_faces = 0
    selected_enclosed_faces = 0
    negative_faces = 0
    try:
        for source, target in train:
            source = sanitize_grid(source)
            target = sanitize_grid(target)
            if source.shape != target.shape:
                raise ValueError("rectangular face fill requires same-shape output")
            background = majority_color(source)
            regions = _background_regions_for_color(source, background)
            selected = tuple(
                region
                for region in regions
                if _is_selected_rectangular_face(source, region, background)
            )
            unselected = tuple(region for region in regions if region not in selected)
            if not selected or not unselected:
                raise ValueError("rectangular face role lacks positive/negative support")
            prediction = source.copy()
            local_color: Optional[int] = None
            for region in selected:
                values = {int(target[row, column]) for row, column in region.cells}
                if len(values) != 1:
                    raise ValueError("selected face is not rendered uniformly")
                value = next(iter(values))
                if value == int(background):
                    raise ValueError("selected rectangular face effect is vacuous")
                if local_color is not None and local_color != value:
                    raise ValueError("selected faces use inconsistent colors")
                local_color = value
                for row, column in region.cells:
                    prediction[row, column] = value
                touches = any(
                    row in {0, source.shape[0] - 1}
                    or column in {0, source.shape[1] - 1}
                    for row, column in region.cells
                )
                selected_border_faces += int(touches)
                selected_enclosed_faces += int(not touches)
            if local_color is None:
                raise ValueError("no rectangular face color")
            if fill_color is not None and fill_color != local_color:
                raise ValueError("face fill color changes across demonstrations")
            fill_color = local_color
            if not exact(prediction, target):
                raise ValueError("rectangular face renderer does not fit demonstration")
            negative_faces += sum(
                all(int(target[row, column]) == int(background) for row, column in region.cells)
                for region in unselected
            )
            train_predictions.append(sanitize_grid(prediction))
            train_records.append(
                {
                    "background": int(background),
                    "face_count": len(regions),
                    "selected_rectangular_faces": len(selected),
                    "unselected_nonrectangular_faces": len(unselected),
                }
            )
        if (
            fill_color is None
            or selected_border_faces <= 0
            or selected_enclosed_faces <= 0
            or negative_faces <= 0
        ):
            return []

        test_predictions: List[Array] = []
        test_records: List[Dict[str, object]] = []
        for source in tests:
            source = sanitize_grid(source)
            background = majority_color(source)
            regions = _background_regions_for_color(source, background)
            selected = tuple(
                region
                for region in regions
                if _is_selected_rectangular_face(source, region, background)
            )
            unselected = tuple(region for region in regions if region not in selected)
            if not selected or not unselected:
                raise ValueError("held-out planar face role is undefined")
            prediction = source.copy()
            for region in selected:
                for row, column in region.cells:
                    prediction[row, column] = int(fill_color)
            test_predictions.append(sanitize_grid(prediction))
            test_records.append(
                {
                    "background": int(background),
                    "face_count": len(regions),
                    "selected_rectangular_faces": len(selected),
                    "unselected_nonrectangular_faces": len(unselected),
                }
            )
    except (TypeError, ValueError):
        return []

    return [
        RuleCandidate(
            name="planar_face_fill_all_rectangular_with_virtual_canvas_wall",
            grids=[grid.copy() for grid in test_predictions],
            train_error=0,
            complexity=9,
            family="causal_planar_rectangular_face_fill",
            train_grids=tuple(grid.copy() for grid in train_predictions),
            metadata={
                "compiler_block": "boundary_face_incidence",
                "typed_entity": "background_planar_face",
                "selector": "rectangular_face_with_adjacent_barrier_junction",
                "quantifier": "FOR_EACH",
                "renderer": "constant_face_fill",
                "fill_color": int(fill_color),
                "canvas_boundary_policy": "virtual_closing_wall",
                "train_traces": train_records,
                "test_traces": test_records,
                "effect_evidence": {
                    "selected_border_faces": selected_border_faces,
                    "selected_enclosed_faces": selected_enclosed_faces,
                    "negative_nonrectangular_faces": negative_faces,
                },
                "semantic_mechanism_key": "planar_faces|rectangular_junction_closed|FOR_EACH|constant_fill|virtual_canvas_wall",
                "output_lineage": {"kind": "test_input_face_incidence_transform"},
                "provenance_kind": "test_input_structural_role_transform",
                "test_input_grounded": True,
                "permutation_invariant": True,
                "translation_equivariant": False,
                "boundary_incidence_equivariant": True,
                "admissible": True,
                "partial_program": True,
                "stores_coordinates": False,
                "exact_demonstration_contract": True,
                "empirical_promotion_eligible": True,
            },
        )
    ]


# -------- exact periodic workspace reconstruction behind occlusions --------

def _solid_unique_color_rectangles(grid: Array) -> Tuple[TypedFrame, ...]:
    """Return colors whose complete support is one filled rectangle.

    These are treated as candidate occluders only.  Requiring the color to be
    absent everywhere outside its rectangle prevents a periodic background
    stripe or tile fragment from being relabeled as an occlusion.
    """

    source = sanitize_grid(grid)
    output: List[TypedFrame] = []
    for raw_color in np.unique(source):
        color = int(raw_color)
        coordinates = np.argwhere(source == color)
        if coordinates.size == 0:
            continue
        top, left = np.min(coordinates, axis=0)
        bottom, right = np.max(coordinates, axis=0)
        top, left, bottom, right = map(int, (top, left, bottom, right))
        height = bottom - top + 1
        width = right - left + 1
        if height < 2 or width < 2:
            continue
        if int(coordinates.shape[0]) != height * width:
            continue
        if not bool(np.all(source[top : bottom + 1, left : right + 1] == color)):
            continue
        output.append(TypedFrame(color, top, left, bottom, right))
    return tuple(
        sorted(
            output,
            key=lambda item: (item.top, item.left, item.bottom, item.right, item.color),
        )
    )


def _infer_exact_periodic_workspace(
    grid: Array,
    occlusions: Sequence[TypedFrame],
    *,
    maximum_period: int = 10,
) -> Tuple[Array, int, int, int]:
    """Reconstruct the smallest exact 2-D period outside occluder boxes."""

    source = sanitize_grid(grid)
    usable = np.ones(source.shape, dtype=bool)
    for occlusion in occlusions:
        usable[
            occlusion.top : occlusion.bottom + 1,
            occlusion.left : occlusion.right + 1,
        ] = False
    if int(np.count_nonzero(usable)) < 8:
        raise ValueError("insufficient visible periodic workspace")

    height, width = source.shape
    row_limit = min(max(1, int(maximum_period)), height // 2)
    column_limit = min(max(1, int(maximum_period)), width // 2)
    programs: List[Tuple[int, int, int, int, Dict[Tuple[int, int], int], int]] = []
    visible_rows, visible_columns = np.where(usable)
    for row_period in range(1, row_limit + 1):
        for column_period in range(1, column_limit + 1):
            phase_values: Dict[Tuple[int, int], int] = {}
            phase_support: Counter[Tuple[int, int]] = Counter()
            valid = True
            for row, column in zip(visible_rows, visible_columns, strict=True):
                phase = (int(row) % row_period, int(column) % column_period)
                value = int(source[int(row), int(column)])
                previous = phase_values.get(phase)
                if previous is not None and previous != value:
                    valid = False
                    break
                phase_values[phase] = value
                phase_support[phase] += 1
            if not valid or len(phase_values) != row_period * column_period:
                continue
            minimum_support = min(phase_support.values())
            if minimum_support < 2:
                continue
            programs.append(
                (
                    row_period * column_period,
                    row_period + column_period,
                    row_period,
                    column_period,
                    phase_values,
                    int(minimum_support),
                )
            )
    if not programs:
        raise ValueError("visible workspace has no repeated exact 2-D period")
    _, _, row_period, column_period, phase_values, minimum_support = min(
        programs,
        key=lambda item: (item[0], item[1], item[2], item[3]),
    )
    reconstructed = np.empty(source.shape, dtype=np.int16)
    for row in range(height):
        for column in range(width):
            reconstructed[row, column] = phase_values[
                (row % row_period, column % column_period)
            ]
    if not bool(np.array_equal(reconstructed[usable], source[usable])):
        raise ValueError("periodic workspace reconstruction violated visible cells")
    return sanitize_grid(reconstructed), row_period, column_period, minimum_support


def _periodic_occlusion_reconstruction_trace(
    grid: Array,
) -> Tuple[Array, Tuple[TypedFrame, ...], TypedFrame, int, int, int]:
    source = sanitize_grid(grid)
    occlusions = _solid_unique_color_rectangles(source)
    if len(occlusions) < 2:
        raise ValueError("periodic occlusion task requires at least two rectangles")
    maximum_area = max(item.outer_area for item in occlusions)
    selected = tuple(item for item in occlusions if item.outer_area == maximum_area)
    if len(selected) != 1:
        raise ValueError("largest periodic occlusion is tied")
    chosen = selected[0]
    reconstructed, row_period, column_period, minimum_support = (
        _infer_exact_periodic_workspace(source, occlusions)
    )
    crop = reconstructed[
        chosen.top : chosen.bottom + 1,
        chosen.left : chosen.right + 1,
    ].copy()
    observed = source[
        chosen.top : chosen.bottom + 1,
        chosen.left : chosen.right + 1,
    ]
    if exact(crop, observed):
        raise ValueError("selected occlusion is vacuous")
    if int(chosen.color) in set(int(value) for value in reconstructed.ravel()):
        raise ValueError("occlusion color also belongs to the periodic workspace")
    return (
        sanitize_grid(crop),
        occlusions,
        chosen,
        int(row_period),
        int(column_period),
        int(minimum_support),
    )


def periodic_occlusion_reconstruction_rules(
    train: List[Tuple[Array, Array]],
    tests: List[Array],
) -> List[RuleCandidate]:
    """Extract the reconstructed largest occlusion from an exact workspace.

    The period and occlusion coordinates are re-inferred independently from
    every held-out input.  No training raster, absolute coordinate, or task ID
    is retained by the compiled program.
    """

    if len(train) < 2 or not tests:
        return []
    try:
        train_traces = tuple(
            _periodic_occlusion_reconstruction_trace(source)
            for source, _ in train
        )
        if not all(
            exact(trace[0], target)
            for trace, (_, target) in zip(train_traces, train, strict=True)
        ):
            return []
        test_traces = tuple(
            _periodic_occlusion_reconstruction_trace(source) for source in tests
        )
    except (TypeError, ValueError):
        return []

    def summary(trace: Tuple[Array, Tuple[TypedFrame, ...], TypedFrame, int, int, int]) -> Dict[str, object]:
        _, domain, selected, row_period, column_period, minimum_support = trace
        return {
            "occlusion_count": len(domain),
            "selected_shape": [selected.height, selected.width],
            "selected_area": selected.outer_area,
            "row_period": row_period,
            "column_period": column_period,
            "minimum_phase_support": minimum_support,
        }

    return [
        RuleCandidate(
            name="periodic_workspace_reconstruct_unique_largest_occlusion",
            grids=[trace[0].copy() for trace in test_traces],
            train_error=0,
            complexity=9,
            family="causal_periodic_occlusion_reconstruction",
            train_grids=tuple(trace[0].copy() for trace in train_traces),
            metadata={
                "compiler_block": "boundary_incidence_workspace_reconstruction",
                "typed_entity": "solid_unique_color_occlusion",
                "selector": "unique_argmax_area",
                "quantifier": "THE",
                "renderer": "reconstruct_exact_periodic_workspace_then_crop_bbox",
                "period_policy": "minimum_exact_2d_period_with_two_supports_per_phase",
                "train_traces": [summary(trace) for trace in train_traces],
                "test_traces": [summary(trace) for trace in test_traces],
                "semantic_mechanism_key": "periodic_workspace|solid_occlusions|unique_argmax_area|reconstruct_crop",
                "output_lineage": {
                    "kind": "test_input_periodic_reconstruction",
                    "shape": "selected_test_occlusion_bbox",
                },
                "provenance_kind": "test_input_periodic_reconstruction",
                "test_input_grounded": True,
                "permutation_invariant": True,
                "translation_equivariant": True,
                "admissible": True,
                "partial_program": True,
                "stores_coordinates": False,
                "stores_training_raster": False,
                "exact_demonstration_contract": True,
                "empirical_promotion_eligible": True,
                "promotion_evidence": {
                    "minimum_training_examples": 2,
                    "minimum_occlusions_per_scene": 2,
                    "unique_selector_witnessed": True,
                    "nonvacuous_hidden_cells": True,
                    "period_reinferred_per_scene": True,
                },
            },
        )
    ]


# ---------------- fixed-corner extraction proposal channel ----------------

@dataclass(frozen=True)
class FixedCornerExtractionContract:
    """A demonstration-identified output shape and canvas corner."""

    height: int
    width: int
    corner: str


_FIXED_CORNERS: Tuple[str, ...] = (
    "top_left",
    "top_right",
    "bottom_left",
    "bottom_right",
)


def fixed_corner_crop_exact(
    grid: Array,
    height: int,
    width: int,
    corner: str,
) -> Array:
    """Copy one fixed-size corner subgrid from the supplied input."""

    grid = sanitize_grid(grid)
    height, width = int(height), int(width)
    if height <= 0 or width <= 0:
        raise ValueError("corner crop dimensions must be positive")
    if height > grid.shape[0] or width > grid.shape[1]:
        raise ValueError("corner crop exceeds input dimensions")
    if corner == "top_left":
        row_start, column_start = 0, 0
    elif corner == "top_right":
        row_start, column_start = 0, grid.shape[1] - width
    elif corner == "bottom_left":
        row_start, column_start = grid.shape[0] - height, 0
    elif corner == "bottom_right":
        row_start = grid.shape[0] - height
        column_start = grid.shape[1] - width
    else:
        raise ValueError(f"unknown fixed corner {corner!r}")
    return grid[
        row_start : row_start + height,
        column_start : column_start + width,
    ].copy()


def infer_fixed_corner_extraction_contract(
    train: List[Tuple[Array, Array]],
) -> Optional[FixedCornerExtractionContract]:
    """Infer one permutation-invariant corner and output-shape contract.

    A task is undefined for this family unless every demonstration has the
    same output shape and exactly one of the four corner relations reproduces
    every output. This rejects symmetric or uniform examples whose corner role
    cannot be identified from the supplied evidence.
    """

    if not train:
        return None
    output_shapes = {tuple(sanitize_grid(target).shape) for _, target in train}
    if len(output_shapes) != 1:
        return None
    height, width = next(iter(output_shapes))
    valid_corners: List[str] = []
    for corner in _FIXED_CORNERS:
        try:
            if all(
                exact(
                    fixed_corner_crop_exact(source, height, width, corner),
                    target,
                )
                for source, target in train
            ):
                valid_corners.append(corner)
        except (TypeError, ValueError):
            continue
    if len(valid_corners) != 1:
        return None
    return FixedCornerExtractionContract(
        height=int(height),
        width=int(width),
        corner=valid_corners[0],
    )


def fixed_corner_extraction_rules(
    train: List[Tuple[Array, Array]],
    tests: List[Array],
) -> List[RuleCandidate]:
    """Compile one exact fixed-corner extraction rule or abstain."""

    if not tests:
        return []
    contract = infer_fixed_corner_extraction_contract(train)
    if contract is None:
        return []
    try:
        train_predictions = tuple(
            fixed_corner_crop_exact(
                source,
                contract.height,
                contract.width,
                contract.corner,
            )
            for source, _ in train
        )
        if not all(
            exact(prediction, target)
            for prediction, (_, target) in zip(train_predictions, train)
        ):
            return []
        test_predictions = [
            fixed_corner_crop_exact(
                source,
                contract.height,
                contract.width,
                contract.corner,
            )
            for source in tests
        ]
    except (TypeError, ValueError):
        return []
    row_interval = {
        "top_left": "0:height",
        "top_right": "0:height",
        "bottom_left": "(input_height-height):input_height",
        "bottom_right": "(input_height-height):input_height",
    }[contract.corner]
    column_interval = {
        "top_left": "0:width",
        "top_right": "(input_width-width):input_width",
        "bottom_left": "0:width",
        "bottom_right": "(input_width-width):input_width",
    }[contract.corner]
    metadata: Dict[str, object] = {
        "compiler_block": "causal_quotient_provenance",
        "typed_entity": "canvas_corner_region",
        "selector": contract.corner,
        "selector_policy": "unique_exact_corner_contract_across_demonstrations",
        "renderer": "direct_corner_subgrid_copy",
        "output_shape_contract": "fixed_shape_shared_by_all_demonstrations",
        "shape_source": "permutation_invariant_training_output_shape_contract",
        "output_shape": [contract.height, contract.width],
        "provenance_kind": "test_input_subgrid",
        "test_input_grounded": True,
        "permutation_invariant": True,
        "admissible": True,
        "source_provenance": {
            "kind": "input_subgrid",
            "corner": contract.corner,
            "row_interval": row_interval,
            "column_interval": column_interval,
        },
        "partial_program": True,
        "undefined_when": [
            "training_output_shapes_disagree",
            "no_common_corner_contract",
            "multiple_common_corner_contracts",
            "test_input_smaller_than_output_contract",
        ],
        "exact_demonstration_contract": True,
    }
    return [
        RuleCandidate(
            name=(
                f"fixed_corner_extract_{contract.corner}_"
                f"{contract.height}x{contract.width}"
            ),
            grids=test_predictions,
            train_error=0,
            complexity=5,
            family="causal_corner_extract",
            train_grids=train_predictions,
            metadata=metadata,
        )
    ]


def unique_dominant_foreground_color(grid: Array) -> int:
    """Return the uniquely most frequent non-background color.

    The selector is partial: an empty foreground or a frequency tie carries
    no demonstrated role and is never resolved by numeric color order.
    """

    grid = sanitize_grid(grid)
    background = infer_bg(grid)
    values, counts = np.unique(grid[grid != background], return_counts=True)
    if len(values) == 0:
        raise ValueError("scene has no foreground color")
    maximum = int(np.max(counts))
    winners = [int(value) for value, count in zip(values, counts) if int(count) == maximum]
    if len(winners) != 1:
        raise ValueError("dominant foreground color is tied")
    return winners[0]


def dominant_color_template_rules(
    train: List[Tuple[Array, Array]],
    tests: List[Array],
) -> List[RuleCandidate]:
    """Compile a repeated-support input-class to output-template mapping.

    Every input class needs at least two exchangeable witnesses, witnesses of
    a class must agree exactly, at least two classes must be demonstrated, and
    every held-out input must select a known class using its own scene.  This
    makes the rule a witnessed classification program rather than a literal
    last-demonstration fallback.
    """

    if not train or not tests:
        return []
    output_shapes = {tuple(sanitize_grid(target).shape) for _, target in train}
    if len(output_shapes) != 1:
        return []
    try:
        train_keys = [unique_dominant_foreground_color(source) for source, _ in train]
        test_keys = [unique_dominant_foreground_color(source) for source in tests]
    except (TypeError, ValueError):
        return []
    support = Counter(train_keys)
    if len(support) < 2 or any(count < 2 for count in support.values()):
        return []
    templates: Dict[int, Array] = {}
    for key, (_, target) in zip(train_keys, train):
        target = sanitize_grid(target)
        previous = templates.get(key)
        if previous is not None and not exact(previous, target):
            return []
        templates[key] = target.copy()
    if any(key not in templates for key in test_keys):
        return []
    train_predictions = tuple(templates[key].copy() for key in train_keys)
    test_predictions = [templates[key].copy() for key in test_keys]
    metadata: Dict[str, object] = {
        "compiler_block": "causal_quotient_provenance",
        "typed_entity": "scene_equivalence_class",
        "selector": "unique_dominant_foreground_color",
        "selector_policy": "unique_argmax_without_color_tie_break",
        "renderer": "repeated_support_class_template",
        "output_shape_contract": "single_shape_shared_by_all_demonstrations",
        "shape_source": "permutation_invariant_training_class_contract",
        "provenance_kind": "held_out_input_keyed_equivalence_class_template",
        "test_input_grounded": True,
        "permutation_invariant": True,
        "admissible": True,
        "minimum_class_support": 2,
        "class_support": {str(key): int(value) for key, value in sorted(support.items())},
        "demonstrated_classes": [int(key) for key in sorted(templates)],
        "test_classes": [int(key) for key in test_keys],
        "partial_program": True,
        "undefined_when": [
            "foreground_absent",
            "dominant_color_tie",
            "fewer_than_two_demonstrated_classes",
            "class_support_below_two",
            "inconsistent_template_within_class",
            "unseen_test_class",
        ],
        "exact_demonstration_contract": True,
    }
    return [
        RuleCandidate(
            name="dominant_color_repeated_support_template",
            grids=test_predictions,
            train_error=0,
            complexity=10 + len(templates),
            family="causal_dominant_color_lookup",
            train_grids=train_predictions,
            metadata=metadata,
        )
    ]


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


# ---------------- semantic scene graph and typed scalar-mask compiler ----------------

@dataclass(frozen=True)
class SceneUnit:
    """One coordinate-free semantic unit in a finite ARC scene graph.

    ``SceneUnit`` deliberately stores geometry and attributes, not a learned
    task coordinate.  Programs select units through relational predicates such
    as maximum area, unique shape, containment, or border contact and rebuild
    the selection for every new input.
    """

    kind: str
    cells: Tuple[Tuple[int, int], ...]
    bbox: Tuple[int, int, int, int]
    colors: Tuple[int, ...]
    area: int
    height: int
    width: int
    holes: int
    density: float
    touches_border: bool
    symmetric: bool
    shape_key: Tuple[Tuple[int, ...], ...]
    shape_multiplicity: int
    color_multiplicity: int


@dataclass(frozen=True)
class SceneGraph:
    """Typed object, region, and scalar views of one exact raster."""

    grid: Array
    background: int
    objects4_color: Tuple[SceneUnit, ...]
    objects8_color: Tuple[SceneUnit, ...]
    objects4_union: Tuple[SceneUnit, ...]
    objects8_union: Tuple[SceneUnit, ...]
    regions4_enclosed: Tuple[SceneUnit, ...]
    regions8_enclosed: Tuple[SceneUnit, ...]


def _scene_local_mask(obj: Obj) -> Array:
    mask = np.zeros((obj.height, obj.width), dtype=bool)
    top, left, _, _ = obj.bbox
    for row, column in obj.cells:
        mask[row - top, column - left] = True
    return mask


def _scene_units_from_objects(
    grid: Array,
    objects: Sequence[Obj],
    kind: str,
) -> Tuple[SceneUnit, ...]:
    grid = sanitize_grid(grid)
    height, width = grid.shape
    records: List[Tuple[Obj, Tuple[int, ...], Tuple[Tuple[int, ...], ...], bool]] = []
    for obj in sorted(objects, key=lambda item: (item.bbox[0], item.bbox[1], item.bbox[2], item.bbox[3])):
        local_mask = _scene_local_mask(obj)
        colors = tuple(sorted({int(grid[row, column]) for row, column in obj.cells}))
        shape_key = _normalized_binary_signature(local_mask, canonical_dihedral=True)
        symmetry_variants = [
            np.fliplr(local_mask),
            np.flipud(local_mask),
            np.rot90(local_mask, 2),
        ]
        if local_mask.shape[0] == local_mask.shape[1]:
            symmetry_variants.extend(
                [
                    local_mask.T,
                    np.rot90(local_mask, 1),
                    np.rot90(local_mask, 3),
                    np.fliplr(np.rot90(local_mask, 1)),
                ]
            )
        symmetric = any(
            variant.shape == local_mask.shape
            and np.array_equal(local_mask, variant)
            for variant in symmetry_variants
        )
        records.append((obj, colors, shape_key, symmetric))
    shape_counts = Counter(record[2] for record in records)
    color_counts = Counter(record[1] for record in records)
    units: List[SceneUnit] = []
    for obj, colors, shape_key, symmetric in records:
        top, left, bottom, right = obj.bbox
        units.append(
            SceneUnit(
                kind=kind,
                cells=tuple(sorted((int(row), int(column)) for row, column in obj.cells)),
                bbox=(int(top), int(left), int(bottom), int(right)),
                colors=colors,
                area=int(obj.size),
                height=int(obj.height),
                width=int(obj.width),
                holes=int(object_hole_count(obj)) if kind == "object" else 0,
                density=float(obj.size / max(1, obj.height * obj.width)),
                touches_border=bool(
                    top == 0
                    or left == 0
                    or bottom == height - 1
                    or right == width - 1
                ),
                symmetric=symmetric,
                shape_key=shape_key,
                shape_multiplicity=int(shape_counts[shape_key]),
                color_multiplicity=int(color_counts[colors]),
            )
        )
    return tuple(units)


def build_scene_graph(grid: Array) -> SceneGraph:
    """Construct all bounded object and enclosed-region interpretations."""
    source = sanitize_grid(grid)
    background = infer_bg(source)
    return SceneGraph(
        grid=source.copy(),
        background=int(background),
        objects4_color=_scene_units_from_objects(
            source,
            generic_components(source, connectivity=4, separate_colors=True),
            "object",
        ),
        objects8_color=_scene_units_from_objects(
            source,
            generic_components(source, connectivity=8, separate_colors=True),
            "object",
        ),
        objects4_union=_scene_units_from_objects(
            source,
            generic_components(source, connectivity=4, separate_colors=False),
            "object",
        ),
        objects8_union=_scene_units_from_objects(
            source,
            generic_components(source, connectivity=8, separate_colors=False),
            "object",
        ),
        regions4_enclosed=_scene_units_from_objects(
            source,
            enclosed_background_components(source, connectivity=4),
            "background_region",
        ),
        regions8_enclosed=_scene_units_from_objects(
            source,
            enclosed_background_components(source, connectivity=8),
            "background_region",
        ),
    )


# ---------------- inverse source-object extraction proposal channel ----------------

_INVERSE_SUBGRID_OBJECT_DOMAINS = (
    "objects4_union",
    "objects8_union",
)


def _scene_unit_tight_crop(graph: SceneGraph, unit: SceneUnit) -> Array:
    """Copy the exact input rectangle witnessed by one semantic scene unit."""

    top, left, bottom, right = unit.bbox
    if not (
        0 <= top <= bottom < graph.grid.shape[0]
        and 0 <= left <= right < graph.grid.shape[1]
    ):
        raise ValueError("scene-unit bounding box is outside the input")
    output = graph.grid[top : bottom + 1, left : right + 1].copy()
    if output.shape != (unit.height, unit.width):
        raise ValueError("scene-unit crop shape contract failed")
    return sanitize_grid(output)


def _inverse_unique_max_color_trace(
    grid: Array,
    domain: str,
    graph: Optional[SceneGraph] = None,
) -> Tuple[Array, Tuple[SceneUnit, ...], SceneUnit]:
    """Select the sole multicolor component with maximum color cardinality."""

    if domain not in _INVERSE_SUBGRID_OBJECT_DOMAINS:
        raise ValueError(f"unsupported inverse-subgrid domain {domain!r}")
    graph = graph if graph is not None else build_scene_graph(grid)
    units = tuple(getattr(graph, domain))
    if not units:
        raise ValueError("inverse-subgrid domain is empty")
    maximum = max(len(unit.colors) for unit in units)
    if maximum < 2:
        raise ValueError("no multicolor component is evidenced")
    selected = tuple(unit for unit in units if len(unit.colors) == maximum)
    if len(selected) != 1:
        raise ValueError("maximum foreground-color cardinality is tied")
    return _scene_unit_tight_crop(graph, selected[0]), units, selected[0]


def _frame_full_crop(grid: Array, frame: TypedFrame) -> Array:
    source = sanitize_grid(grid)
    output = source[
        frame.top : frame.bottom + 1,
        frame.left : frame.right + 1,
    ].copy()
    if output.shape != (frame.height, frame.width):
        raise ValueError("frame full-bbox shape contract failed")
    return sanitize_grid(output)


def _inverse_unique_frame_crop_trace(
    grid: Array,
) -> Tuple[Array, Tuple[TypedFrame, ...], TypedFrame]:
    """Return the sole complete frame whose exact full crop is non-repeated.

    The selection is over content-equivalence classes, not positions.  This
    handles scenes containing several complete frames when all distractor
    frames instantiate one repeated packet and exactly one packet differs.
    """

    source = sanitize_grid(grid)
    frames = enumerate_complete_monochrome_frames(source)
    if not frames:
        raise ValueError("no complete monochrome frame")
    crops = tuple(_frame_full_crop(source, frame) for frame in frames)
    signatures = tuple(canonical(crop) for crop in crops)
    multiplicities = Counter(signatures)
    selected_indices = [
        index
        for index, signature in enumerate(signatures)
        if multiplicities[signature] == 1
    ]
    if len(selected_indices) != 1:
        raise ValueError("complete-frame content class is not uniquely non-repeated")
    index = selected_indices[0]
    return crops[index], frames, frames[index]


def _inverse_repeated_component_trace(
    grid: Array,
    domain: str,
    graph: Optional[SceneGraph] = None,
) -> Tuple[Array, Tuple[SceneUnit, ...], Tuple[SceneUnit, SceneUnit]]:
    """Return the sole multicolor component crop occurring exactly twice.

    Exact raster equality is required.  Dihedral or palette-normalized aliases
    are intentionally not merged because that would require an unsupported
    orientation or recoloring choice at emission time.
    """

    if domain not in _INVERSE_SUBGRID_OBJECT_DOMAINS:
        raise ValueError(f"unsupported inverse-subgrid domain {domain!r}")
    graph = graph if graph is not None else build_scene_graph(grid)
    units = tuple(
        unit
        for unit in getattr(graph, domain)
        if len(unit.colors) >= 2
    )
    if len(units) < 2:
        raise ValueError("fewer than two multicolor components")
    crops = tuple(_scene_unit_tight_crop(graph, unit) for unit in units)
    signatures = tuple(canonical(crop) for crop in crops)
    by_signature: Dict[str, List[int]] = defaultdict(list)
    for index, signature in enumerate(signatures):
        by_signature[signature].append(index)
    repeated_classes = [
        indices
        for indices in by_signature.values()
        if len(indices) == 2
    ]
    if len(repeated_classes) != 1:
        raise ValueError("there is not exactly one multiplicity-two component class")
    first_index, second_index = repeated_classes[0]
    if not exact(crops[first_index], crops[second_index]):
        raise ValueError("multiplicity-two components lack a common raster representative")
    return (
        crops[first_index],
        units,
        (units[first_index], units[second_index]),
    )


def _inverse_unit_support(unit: SceneUnit) -> Array:
    support = np.zeros((unit.height, unit.width), dtype=bool)
    top, left, _, _ = unit.bbox
    for row, column in unit.cells:
        support[row - top, column - left] = True
    return support


def _inverse_unit_color_counts(graph: SceneGraph, unit: SceneUnit) -> Counter[int]:
    return Counter(int(graph.grid[row, column]) for row, column in unit.cells)


def _inverse_component_feature_trace(
    grid: Array,
    domain: str,
    selector: str,
    *,
    target_color: Optional[int] = None,
    graph: Optional[SceneGraph] = None,
) -> Tuple[Array, Tuple[SceneUnit, ...], SceneUnit, int]:
    """Select one component by a coordinate-free scalar or Boolean feature."""

    if domain not in _INVERSE_SUBGRID_OBJECT_DOMAINS:
        raise ValueError(f"unsupported inverse-subgrid domain {domain!r}")
    graph = graph if graph is not None else build_scene_graph(grid)
    domain_units = tuple(getattr(graph, domain))
    if selector == "sole_left_right_asymmetric":
        if len(domain_units) < 2:
            raise ValueError("asymmetry selector requires competing components")
        scored = [
            (
                0
                if np.array_equal(
                    _inverse_unit_support(unit),
                    np.fliplr(_inverse_unit_support(unit)),
                )
                else 1,
                unit,
            )
            for unit in domain_units
        ]
        selected = [unit for value, unit in scored if value == 1]
        selector_value = 1
    elif selector == "unique_argmin_modal_defect_count":
        eligible = tuple(
            unit
            for unit in domain_units
            if len(unit.colors) >= 2 and unit.area == unit.height * unit.width
        )
        if len(eligible) < 2:
            raise ValueError("modal-defect selector requires competing dense multicolor components")
        scored = []
        for unit in eligible:
            counts = _inverse_unit_color_counts(graph, unit)
            scored.append((unit.area - max(counts.values()), unit))
        selector_value = min(value for value, _ in scored)
        selected = [unit for value, unit in scored if value == selector_value]
        domain_units = eligible
    elif selector == "unique_argmax_literal_color_count":
        if target_color is None:
            raise ValueError("literal-color-count selector requires a target color")
        eligible = tuple(
            unit
            for unit in domain_units
            if len(unit.colors) >= 2 and unit.area == unit.height * unit.width
        )
        if len(eligible) < 2:
            raise ValueError("color-count selector requires competing dense multicolor components")
        scored = [
            (_inverse_unit_color_counts(graph, unit)[int(target_color)], unit)
            for unit in eligible
        ]
        selector_value = max(value for value, _ in scored)
        if selector_value <= 0:
            raise ValueError("selected literal color is absent from every component")
        selected = [unit for value, unit in scored if value == selector_value]
        domain_units = eligible
    else:
        raise ValueError(f"unsupported inverse-subgrid selector {selector!r}")
    if len(selected) != 1:
        raise ValueError(f"inverse-subgrid selector {selector!r} is tied")
    return (
        _scene_unit_tight_crop(graph, selected[0]),
        domain_units,
        selected[0],
        int(selector_value),
    )


def _inverse_scene_unit_summary(unit: SceneUnit) -> Dict[str, object]:
    return {
        "kind": unit.kind,
        "foreground_color_cardinality": len(unit.colors),
        "area": int(unit.area),
        "shape": [int(unit.height), int(unit.width)],
        "density": float(unit.density),
    }


def inverse_subgrid_object_rules(
    train: List[Tuple[Array, Array]],
    tests: List[Array],
) -> List[RuleCandidate]:
    """Compile exact input-grounded object crops with partial selectors.

    Every selector must be unique independently in every demonstration and
    held-out input.  A tied or unsupported scene causes family-local
    abstention; no positional fallback is available.
    """

    if not train or not tests:
        return []
    output: List[RuleCandidate] = []
    train_graphs = tuple(build_scene_graph(source) for source, _ in train)
    test_graphs = tuple(build_scene_graph(source) for source in tests)

    for domain in _INVERSE_SUBGRID_OBJECT_DOMAINS:
        try:
            train_traces = tuple(
                _inverse_unique_max_color_trace(source, domain, graph)
                for (source, _), graph in zip(train, train_graphs)
            )
            if not all(
                exact(trace[0], target)
                for trace, (_, target) in zip(train_traces, train)
            ):
                raise ValueError("unique-max-color program does not fit demonstrations")
            test_traces = tuple(
                _inverse_unique_max_color_trace(source, domain, graph)
                for source, graph in zip(tests, test_graphs)
            )
        except (TypeError, ValueError):
            pass
        else:
            output.append(
                RuleCandidate(
                    name=f"inverse_subgrid_{domain}_unique_max_color_cardinality",
                    grids=[trace[0] for trace in test_traces],
                    train_error=0,
                    complexity=6,
                    family="causal_inverse_subgrid",
                    train_grids=tuple(trace[0] for trace in train_traces),
                    metadata={
                        "compiler_block": "causal_quotient_provenance",
                        "typed_entity": "multicolor_connected_component",
                        "connectivity": 4 if domain == "objects4_union" else 8,
                        "selector": "unique_argmax_foreground_color_cardinality",
                        "selector_policy": "unique_argmax_without_positional_tie_break",
                        "renderer": "selected_entity_tight_input_crop",
                        "output_shape_contract": "selected_entity.bbox_shape",
                        "provenance_kind": "test_input_subgrid",
                        "test_input_grounded": True,
                        "permutation_invariant": True,
                        "admissible": True,
                        "partial_program": True,
                        "undefined_when": [
                            "empty_component_domain",
                            "no_multicolor_component",
                            "selector_tie",
                        ],
                        "translation_equivariant": True,
                        "color_role_invariant": True,
                        "exact_demonstration_contract": True,
                        "train_domain_sizes": [len(trace[1]) for trace in train_traces],
                        "test_domain_sizes": [len(trace[1]) for trace in test_traces],
                        "train_selected": [
                            _inverse_scene_unit_summary(trace[2]) for trace in train_traces
                        ],
                        "test_selected": [
                            _inverse_scene_unit_summary(trace[2]) for trace in test_traces
                        ],
                        "source_provenance": {
                            "kind": "input_subgrid",
                            "row_interval": "selected_entity.top:(bottom+1)",
                            "column_interval": "selected_entity.left:(right+1)",
                        },
                    },
                )
            )

    feature_specs: List[Tuple[str, Optional[int], int]] = [
        ("sole_left_right_asymmetric", None, 6),
        ("unique_argmin_modal_defect_count", None, 7),
    ] + [
        ("unique_argmax_literal_color_count", color, 8)
        for color in range(10)
    ]
    for domain in _INVERSE_SUBGRID_OBJECT_DOMAINS:
        for selector, target_color, complexity in feature_specs:
            try:
                train_traces = tuple(
                    _inverse_component_feature_trace(
                        source,
                        domain,
                        selector,
                        target_color=target_color,
                        graph=graph,
                    )
                    for (source, _), graph in zip(train, train_graphs)
                )
                if not all(
                    exact(trace[0], target)
                    for trace, (_, target) in zip(train_traces, train)
                ):
                    raise ValueError("component-feature program does not fit demonstrations")
                test_traces = tuple(
                    _inverse_component_feature_trace(
                        source,
                        domain,
                        selector,
                        target_color=target_color,
                        graph=graph,
                    )
                    for source, graph in zip(tests, test_graphs)
                )
            except (TypeError, ValueError):
                continue
            selector_name = selector
            if target_color is not None:
                selector_name = f"{selector}_c{target_color}"
            output.append(
                RuleCandidate(
                    name=f"inverse_subgrid_{domain}_{selector_name}",
                    grids=[trace[0] for trace in test_traces],
                    train_error=0,
                    complexity=complexity,
                    family="causal_inverse_subgrid",
                    train_grids=tuple(trace[0] for trace in train_traces),
                    metadata={
                        "compiler_block": "causal_quotient_provenance",
                        "typed_entity": "connected_component",
                        "connectivity": 4 if domain == "objects4_union" else 8,
                        "selector": selector,
                        "selector_target_color": target_color,
                        "selector_policy": "unique_feature_extremum_without_positional_tie_break",
                        "renderer": "selected_entity_tight_input_crop",
                        "output_shape_contract": "selected_entity.bbox_shape",
                        "provenance_kind": "test_input_subgrid",
                        "test_input_grounded": True,
                        "permutation_invariant": True,
                        "admissible": True,
                        "partial_program": True,
                        "undefined_when": [
                            "insufficient_competing_components",
                            "selector_tie",
                            "selector_feature_absent",
                        ],
                        "translation_equivariant": True,
                        "color_role_invariant": target_color is None,
                        "exact_demonstration_contract": True,
                        "train_domain_sizes": [len(trace[1]) for trace in train_traces],
                        "test_domain_sizes": [len(trace[1]) for trace in test_traces],
                        "train_selector_values": [trace[3] for trace in train_traces],
                        "test_selector_values": [trace[3] for trace in test_traces],
                        "train_selected": [
                            _inverse_scene_unit_summary(trace[2]) for trace in train_traces
                        ],
                        "test_selected": [
                            _inverse_scene_unit_summary(trace[2]) for trace in test_traces
                        ],
                        "source_provenance": {
                            "kind": "input_subgrid",
                            "row_interval": "selected_entity.top:(bottom+1)",
                            "column_interval": "selected_entity.left:(right+1)",
                        },
                    },
                )
            )

    try:
        train_frame_traces = tuple(
            _inverse_unique_frame_crop_trace(source)
            for source, _ in train
        )
        if not all(
            exact(trace[0], target)
            for trace, (_, target) in zip(train_frame_traces, train)
        ):
            raise ValueError("unique-frame program does not fit demonstrations")
        test_frame_traces = tuple(
            _inverse_unique_frame_crop_trace(source)
            for source in tests
        )
    except (TypeError, ValueError):
        pass
    else:
        output.append(
            RuleCandidate(
                name="inverse_subgrid_unique_complete_frame_content",
                grids=[trace[0] for trace in test_frame_traces],
                train_error=0,
                complexity=6,
                family="causal_inverse_subgrid",
                train_grids=tuple(trace[0] for trace in train_frame_traces),
                metadata={
                    "compiler_block": "causal_quotient_provenance",
                    "typed_entity": "complete_monochrome_frame",
                    "selector": "sole_non_repeated_exact_full_crop",
                    "selector_policy": "unique_content_class_without_positional_tie_break",
                    "renderer": "selected_frame_full_input_crop",
                    "output_shape_contract": "selected_frame.outer_shape",
                    "provenance_kind": "test_input_subgrid",
                    "test_input_grounded": True,
                    "permutation_invariant": True,
                    "admissible": True,
                    "partial_program": True,
                    "undefined_when": [
                        "no_complete_frame",
                        "zero_or_multiple_non_repeated_frame_classes",
                    ],
                    "translation_equivariant": True,
                    "color_role_invariant": True,
                    "exact_demonstration_contract": True,
                    "train_frame_counts": [
                        len(trace[1]) for trace in train_frame_traces
                    ],
                    "test_frame_counts": [
                        len(trace[1]) for trace in test_frame_traces
                    ],
                    "source_provenance": {
                        "kind": "input_subgrid",
                        "row_interval": "selected_frame.top:(bottom+1)",
                        "column_interval": "selected_frame.left:(right+1)",
                    },
                },
            )
        )

    for domain in _INVERSE_SUBGRID_OBJECT_DOMAINS:
        try:
            train_traces = tuple(
                _inverse_repeated_component_trace(source, domain, graph)
                for (source, _), graph in zip(train, train_graphs)
            )
            if not all(
                exact(trace[0], target)
                for trace, (_, target) in zip(train_traces, train)
            ):
                raise ValueError("repeated-component program does not fit demonstrations")
            test_traces = tuple(
                _inverse_repeated_component_trace(source, domain, graph)
                for source, graph in zip(tests, test_graphs)
            )
        except (TypeError, ValueError):
            continue
        output.append(
            RuleCandidate(
                name=f"inverse_subgrid_{domain}_sole_exact_pair",
                grids=[trace[0] for trace in test_traces],
                train_error=0,
                complexity=7,
                family="causal_inverse_subgrid",
                train_grids=tuple(trace[0] for trace in train_traces),
                metadata={
                    "compiler_block": "causal_quotient_provenance",
                    "typed_entity": "multicolor_connected_component_class",
                    "connectivity": 4 if domain == "objects4_union" else 8,
                    "selector": "sole_exact_crop_class_with_multiplicity_two",
                    "selector_policy": "content_equivalence_without_positional_tie_break",
                    "representative_policy": "emit_common_exact_raster",
                    "renderer": "equivalence_class_tight_input_crop",
                    "output_shape_contract": "common_component.bbox_shape",
                    "provenance_kind": "test_input_subgrid_equivalence_class",
                    "test_input_grounded": True,
                    "permutation_invariant": True,
                    "admissible": True,
                    "partial_program": True,
                    "undefined_when": [
                        "fewer_than_two_multicolor_components",
                        "zero_or_multiple_multiplicity_two_classes",
                        "class_members_not_exactly_identical",
                    ],
                    "translation_equivariant": True,
                    "color_role_invariant": True,
                    "exact_demonstration_contract": True,
                    "train_domain_sizes": [len(trace[1]) for trace in train_traces],
                    "test_domain_sizes": [len(trace[1]) for trace in test_traces],
                    "source_provenance": {
                        "kind": "input_subgrid_equivalence_class",
                        "member_count": 2,
                        "coordinates_used_for_selection": False,
                    },
                },
            )
        )

    return deduplicate_prediction_grids(output)


_SCENE_DOMAINS = (
    "objects4_color",
    "objects8_color",
    "objects4_union",
    "objects8_union",
    "regions4_enclosed",
    "regions8_enclosed",
)

_SCENE_DOMAIN_FAIR_ORDER = (
    "objects4_color",
    "regions4_enclosed",
    "objects4_union",
    "regions8_enclosed",
    "objects8_color",
    "objects8_union",
)

_SCENE_PREDICATES = (
    "largest_area",
    "smallest_area",
    "largest_bbox",
    "smallest_bbox",
    "tallest",
    "widest",
    "densest",
    "sparsest",
    "most_holes",
    "has_hole",
    "no_hole",
    "touches_border",
    "interior",
    "unique_shape",
    "repeated_shape",
    "unique_color",
    "repeated_color",
    "symmetric",
    "asymmetric",
)

_SCENE_MASK_MODES = (
    "cells",
    "bbox",
    "bbox_outline",
    "bbox_interior",
    "holes",
)


def scene_domain_units(graph: SceneGraph, domain: str) -> Tuple[SceneUnit, ...]:
    if domain not in _SCENE_DOMAINS:
        raise ValueError(f"unknown scene domain {domain!r}")
    return tuple(getattr(graph, domain))


def scene_scalar_values(graph: SceneGraph) -> Dict[str, int]:
    """Return only input-derived cardinalities usable by renderer programs."""
    color_objects = graph.objects4_color
    union_objects = graph.objects4_union
    colors = {
        int(value)
        for value in graph.grid.ravel()
        if int(value) != int(graph.background)
    }
    return {
        "objects4_color": len(color_objects),
        "objects4_union": len(union_objects),
        "objects8_color": len(graph.objects8_color),
        "objects8_union": len(graph.objects8_union),
        "background_regions4": len(background_components(graph.grid, connectivity=4)),
        "background_regions8": len(background_components(graph.grid, connectivity=8)),
        "foreground_colors": len(colors),
        "foreground_cells": int(np.count_nonzero(graph.grid != graph.background)),
        "enclosed_regions4": len(graph.regions4_enclosed),
        "enclosed_regions8": len(graph.regions8_enclosed),
        "objects_with_holes": sum(unit.holes > 0 for unit in union_objects),
        "border_objects": sum(unit.touches_border for unit in union_objects),
        "interior_objects": sum(not unit.touches_border for unit in union_objects),
        "unique_shapes": sum(unit.shape_multiplicity == 1 for unit in union_objects),
        "repeated_shape_members": sum(unit.shape_multiplicity > 1 for unit in union_objects),
    }


def _scene_select_units(
    units: Sequence[SceneUnit],
    predicate: str,
) -> Tuple[SceneUnit, ...]:
    values = tuple(units)
    if not values:
        raise ValueError("empty scene domain")

    def extrema(attribute: str, maximum: bool) -> Tuple[SceneUnit, ...]:
        extracted = [getattr(unit, attribute) for unit in values]
        target = max(extracted) if maximum else min(extracted)
        return tuple(unit for unit in values if getattr(unit, attribute) == target)

    if predicate == "largest_area":
        selected = extrema("area", True)
    elif predicate == "smallest_area":
        selected = extrema("area", False)
    elif predicate == "largest_bbox":
        target = max(unit.height * unit.width for unit in values)
        selected = tuple(unit for unit in values if unit.height * unit.width == target)
    elif predicate == "smallest_bbox":
        target = min(unit.height * unit.width for unit in values)
        selected = tuple(unit for unit in values if unit.height * unit.width == target)
    elif predicate == "tallest":
        selected = extrema("height", True)
    elif predicate == "widest":
        selected = extrema("width", True)
    elif predicate == "densest":
        selected = extrema("density", True)
    elif predicate == "sparsest":
        selected = extrema("density", False)
    elif predicate == "most_holes":
        selected = extrema("holes", True)
    elif predicate == "has_hole":
        selected = tuple(unit for unit in values if unit.holes > 0)
    elif predicate == "no_hole":
        selected = tuple(unit for unit in values if unit.holes == 0)
    elif predicate == "touches_border":
        selected = tuple(unit for unit in values if unit.touches_border)
    elif predicate == "interior":
        selected = tuple(unit for unit in values if not unit.touches_border)
    elif predicate == "unique_shape":
        selected = tuple(unit for unit in values if unit.shape_multiplicity == 1)
    elif predicate == "repeated_shape":
        selected = tuple(unit for unit in values if unit.shape_multiplicity > 1)
    elif predicate == "unique_color":
        selected = tuple(unit for unit in values if unit.color_multiplicity == 1)
    elif predicate == "repeated_color":
        selected = tuple(unit for unit in values if unit.color_multiplicity > 1)
    elif predicate == "symmetric":
        selected = tuple(unit for unit in values if unit.symmetric)
    elif predicate == "asymmetric":
        selected = tuple(unit for unit in values if not unit.symmetric)
    else:
        raise ValueError(predicate)
    if not selected:
        raise ValueError(f"predicate {predicate} selected no units")
    return selected


def _scene_hole_mask(graph: SceneGraph, unit: SceneUnit) -> Array:
    """Return geometric hole cells that are actual scene background.

    A packet may surround another foreground packet.  The surrounded packet is
    not part of the enclosing object's paintable hole, so the final mask is
    intersected with the graph's background support.
    """
    mask = np.zeros(graph.grid.shape, dtype=bool)
    top, left, bottom, right = unit.bbox
    local = np.zeros((unit.height, unit.width), dtype=bool)
    for row, column in unit.cells:
        local[row - top, column - left] = True
    seen = np.zeros_like(local, dtype=bool)
    for row in range(unit.height):
        for column in range(unit.width):
            if local[row, column] or seen[row, column]:
                continue
            queue = deque([(row, column)])
            seen[row, column] = True
            region: List[Tuple[int, int]] = []
            touches_local_border = False
            while queue:
                current_row, current_column = queue.popleft()
                region.append((current_row, current_column))
                touches_local_border = touches_local_border or (
                    current_row in {0, unit.height - 1}
                    or current_column in {0, unit.width - 1}
                )
                for delta_row, delta_column in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                    next_row = current_row + delta_row
                    next_column = current_column + delta_column
                    if (
                        0 <= next_row < unit.height
                        and 0 <= next_column < unit.width
                        and not local[next_row, next_column]
                        and not seen[next_row, next_column]
                    ):
                        seen[next_row, next_column] = True
                        queue.append((next_row, next_column))
            if not touches_local_border:
                for local_row, local_column in region:
                    row = top + local_row
                    column = left + local_column
                    if int(graph.grid[row, column]) == int(graph.background):
                        mask[row, column] = True
    return mask


def scene_unit_mask(
    graph: SceneGraph,
    units: Sequence[SceneUnit],
    mode: str,
) -> Array:
    output = np.zeros(graph.grid.shape, dtype=bool)
    for unit in units:
        top, left, bottom, right = unit.bbox
        if mode == "cells":
            for row, column in unit.cells:
                output[row, column] = True
        elif mode == "bbox":
            output[top : bottom + 1, left : right + 1] = True
        elif mode == "bbox_outline":
            output[top, left : right + 1] = True
            output[bottom, left : right + 1] = True
            output[top : bottom + 1, left] = True
            output[top : bottom + 1, right] = True
        elif mode == "bbox_interior":
            if bottom - top >= 2 and right - left >= 2:
                output[top + 1 : bottom, left + 1 : right] = True
        elif mode == "holes":
            output |= _scene_hole_mask(graph, unit)
        else:
            raise ValueError(mode)
    if not np.any(output):
        raise ValueError("typed scene mask is empty")
    return output


def _scene_masks_with_support(
    graphs: Sequence[SceneGraph],
    domain: str,
    predicate: str,
    mode: str,
    *,
    require_branch_support: bool,
) -> Optional[Tuple[List[Array], int, int]]:
    masks: List[Array] = []
    selected_support = 0
    unselected_support = 0
    try:
        for graph in graphs:
            units = scene_domain_units(graph, domain)
            selected = _scene_select_units(units, predicate)
            selected_support += len(selected)
            unselected_support += len(units) - len(selected)
            masks.append(scene_unit_mask(graph, selected, mode))
    except Exception:
        return None
    if selected_support <= 0:
        return None
    if require_branch_support and unselected_support <= 0:
        return None
    return masks, selected_support, unselected_support


def scene_predicate_paint_exact(
    grid: Array,
    domain: str,
    predicate: str,
    mask_mode: str,
    action: str,
    color: Optional[int] = None,
) -> Array:
    source = sanitize_grid(grid)
    graph = build_scene_graph(source)
    units = _scene_select_units(scene_domain_units(graph, domain), predicate)
    mask = scene_unit_mask(graph, units, mask_mode)
    output = source.copy()
    if action == "background":
        output[mask] = int(graph.background)
    elif action == "paint" and color is not None:
        output[mask] = int(color)
    else:
        raise ValueError(action)
    if exact(output, source):
        raise ValueError("typed scalar-mask action made no change")
    return output


def _typed_mask_seed_candidates(
    seeds: Sequence[RuleCandidate],
    train: List[Tuple[Array, Array]],
    tests: List[Array],
    *,
    maximum_programs: int,
    maximum_exact: int,
    include_identity: bool,
) -> List[RuleCandidate]:
    if not train or not tests:
        return []
    identity = RuleCandidate(
        name="typed_identity_seed",
        grids=[test.copy() for test in tests],
        train_error=sum(grid_error(source, target) for source, target in train),
        complexity=0,
        family="learned_transform",
        train_grids=tuple(source.copy() for source, _ in train),
        metadata={"typed_scalar_mask_identity_seed": True},
    )
    identity_same_shape = all(source.shape == target.shape for source, target in train)
    ordered: List[RuleCandidate] = (
        [identity] if include_identity and identity_same_shape else []
    )
    family_seen: set[str] = set()
    for seed in sorted(
        seeds,
        key=lambda candidate: (
            candidate.train_error,
            candidate.complexity,
            candidate.family,
            candidate.name,
        ),
    ):
        if len(seed.train_grids) != len(train) or len(seed.grids) != len(tests):
            continue
        if seed.family in family_seen:
            continue
        if any(seed_grid.shape != target.shape for seed_grid, (_, target) in zip(seed.train_grids, train)):
            continue
        family_seen.add(seed.family)
        ordered.append(seed)
        if len(ordered) >= 12:
            break
    if len(ordered) < 12:
        ordered_ids = {id(candidate) for candidate in ordered}
        for seed in sorted(
            seeds,
            key=lambda candidate: (
                candidate.train_error,
                candidate.complexity,
                candidate.family,
                candidate.name,
            ),
        ):
            if id(seed) in ordered_ids or len(seed.train_grids) != len(train) or len(seed.grids) != len(tests):
                continue
            if any(seed_grid.shape != target.shape for seed_grid, (_, target) in zip(seed.train_grids, train)):
                continue
            ordered.append(seed)
            ordered_ids.add(id(seed))
            if len(ordered) >= 12:
                break

    if not ordered:
        return []

    graph_cache: Dict[Tuple[Tuple[int, int], bytes], SceneGraph] = {}

    def cached_scene_graphs(values: Sequence[Array]) -> List[SceneGraph]:
        graphs: List[SceneGraph] = []
        for value in values:
            normalized = sanitize_grid(value)
            key = (normalized.shape, normalized.tobytes())
            graph = graph_cache.get(key)
            if graph is None:
                graph = build_scene_graph(normalized)
                graph_cache[key] = graph
            graphs.append(graph)
        return graphs

    contexts: List[
        Tuple[
            RuleCandidate,
            str,
            List[Array],
            List[Array],
            List[SceneGraph],
            List[SceneGraph],
            bool,
        ]
    ] = []
    source_train = [source for source, _ in train]
    for seed in ordered:
        basis_options = ("source",) if seed is identity else ("source", "seed")
        for basis in basis_options:
            basis_train = source_train if basis == "source" else list(seed.train_grids)
            basis_tests = tests if basis == "source" else list(seed.grids)
            if any(
                basis_grid.shape != seed_grid.shape
                for basis_grid, seed_grid in zip(basis_train, seed.train_grids)
            ) or any(
                basis_grid.shape != seed_grid.shape
                for basis_grid, seed_grid in zip(basis_tests, seed.grids)
            ):
                continue
            try:
                basis_train_graphs = cached_scene_graphs(basis_train)
                basis_test_graphs = cached_scene_graphs(basis_tests)
            except Exception:
                continue
            contexts.append(
                (
                    seed,
                    basis,
                    list(basis_train),
                    list(basis_tests),
                    basis_train_graphs,
                    basis_test_graphs,
                    seed is identity,
                )
            )

    output: List[RuleCandidate] = []
    prediction_seen: set[Tuple[str, Tuple[str, ...]]] = set()
    attempted = 0
    colors = sorted(
        {
            int(value)
            for _, target in train
            for value in sanitize_grid(target).ravel()
        }
    )
    for mask_mode in _SCENE_MASK_MODES:
        for domain in _SCENE_DOMAIN_FAIR_ORDER:
            for predicate in _SCENE_PREDICATES:
                # Search every seed/basis context at the same semantic depth
                # before advancing.  This prevents an early seed from
                # exhausting the deterministic program cap.
                for (
                    seed,
                    basis,
                    basis_train,
                    basis_tests,
                    basis_train_graphs,
                    basis_test_graphs,
                    direct,
                ) in contexts:
                    if attempted >= maximum_programs or len(output) >= maximum_exact:
                        return output
                    attempted += 1
                    support = _scene_masks_with_support(
                        basis_train_graphs,
                        domain,
                        predicate,
                        mask_mode,
                        require_branch_support=True,
                    )
                    if support is None:
                        continue
                    train_masks, selected_support, unselected_support = support
                    test_support = _scene_masks_with_support(
                        basis_test_graphs,
                        domain,
                        predicate,
                        mask_mode,
                        require_branch_support=False,
                    )
                    if test_support is None:
                        continue
                    test_masks = test_support[0]
                    actions: List[Tuple[str, Optional[int]]] = [("background", None)]
                    actions.extend(("paint", color) for color in colors)
                    for action, color in actions:
                        train_predictions: List[Array] = []
                        changed = False
                        for index, (baseline, mask) in enumerate(
                            zip(seed.train_grids, train_masks)
                        ):
                            prediction = sanitize_grid(baseline).copy()
                            value = (
                                basis_train_graphs[index].background
                                if action == "background"
                                else int(color)
                            )
                            prediction[mask] = int(value)
                            train_predictions.append(prediction)
                            changed = changed or not exact(prediction, baseline)
                        if not changed or not all(
                            exact(prediction, target)
                            for prediction, (_, target) in zip(train_predictions, train)
                        ):
                            continue
                        test_predictions: List[Array] = []
                        for index, (baseline, mask) in enumerate(
                            zip(seed.grids, test_masks)
                        ):
                            prediction = sanitize_grid(baseline).copy()
                            value = (
                                basis_test_graphs[index].background
                                if action == "background"
                                else int(color)
                            )
                            prediction[mask] = int(value)
                            test_predictions.append(prediction)
                        if direct and domain.startswith("regions"):
                            family = "struct_region_predicate_rewrite"
                        elif direct:
                            family = "struct_object_predicate_rewrite"
                        else:
                            family = "composition_scalar_mask"
                        signature = tuple(canonical(grid) for grid in test_predictions)
                        prediction_key = (family, signature)
                        if prediction_key in prediction_seen:
                            continue
                        prediction_seen.add(prediction_key)
                        translation_equivariant = not (
                            domain.startswith("regions")
                            or predicate in {"touches_border", "interior"}
                        )
                        output.append(
                            RuleCandidate(
                                name=(
                                    f"typed_mask:{seed.name}:{basis}:{domain}:"
                                    f"{predicate}:{mask_mode}:{action}:"
                                    f"{color if color is not None else 'bg'}"
                                ),
                                grids=[grid.copy() for grid in test_predictions],
                                train_error=0,
                                complexity=min(40, int(seed.complexity)) + 7,
                                family=family,
                                train_grids=tuple(
                                    grid.copy() for grid in train_predictions
                                ),
                                metadata={
                                    "semantic_scene_graph": True,
                                    "typed_scalar_mask": True,
                                    "seed_name": seed.name,
                                    "seed_family": seed.family,
                                    "basis": basis,
                                    "domain": domain,
                                    "predicate": predicate,
                                    "mask_mode": mask_mode,
                                    "action": action,
                                    "target_color": color,
                                    "selected_support": int(selected_support),
                                    "unselected_support": int(unselected_support),
                                    "branch_support_observed": True,
                                    "translation_equivariant": translation_equivariant,
                                    "size_general": True,
                                    "stores_coordinates": False,
                                    "exact_demonstration_contract": True,
                                },
                            )
                        )
    return output


def typed_scalar_mask_refinement_rules(
    seeds: Sequence[RuleCandidate],
    train: List[Tuple[Array, Array]],
    tests: List[Array],
    maximum_programs: int = 2048,
    maximum_exact: int = 24,
    *,
    include_identity: bool = True,
) -> List[RuleCandidate]:
    return deduplicate_candidates(
        _typed_mask_seed_candidates(
            seeds,
            train,
            tests,
            maximum_programs=max(1, int(maximum_programs)),
            maximum_exact=max(1, int(maximum_exact)),
            include_identity=bool(include_identity),
        )
    )


def scene_cardinality_renderer_rules(
    train: List[Tuple[Array, Array]],
    tests: List[Array],
) -> List[RuleCandidate]:
    output: List[RuleCandidate] = []
    if len(train) < 2 or not all(len(np.unique(target)) == 1 for _, target in train):
        return output
    colors = {int(target.flat[0]) for _, target in train}
    if len(colors) != 1:
        return output
    color = next(iter(colors))
    graphs = [build_scene_graph(source) for source, _ in train]
    scalar_names = sorted(set.intersection(*(set(scene_scalar_values(graph)) for graph in graphs)))
    for scalar_name in scalar_names:
        values = [scene_scalar_values(graph)[scalar_name] for graph in graphs]
        if len(set(values)) < 2 or not all(1 <= value <= MAX_SIDE for value in values):
            continue
        for orientation in ("row", "col", "square"):
            def apply(
                grid: Array,
                key: str = scalar_name,
                direction: str = orientation,
                value: int = color,
            ) -> Array:
                count = int(scene_scalar_values(build_scene_graph(grid))[key])
                if not 1 <= count <= MAX_SIDE:
                    raise ValueError("scene cardinality outside ARC bounds")
                if direction == "row":
                    return np.full((1, count), value, dtype=np.int16)
                if direction == "col":
                    return np.full((count, 1), value, dtype=np.int16)
                if count * count > MAX_SIDE * MAX_SIDE:
                    raise ValueError("scene cardinality square outside ARC bounds")
                return np.full((count, count), value, dtype=np.int16)

            _try_exact_rule(
                output,
                train,
                tests,
                f"scene_cardinality_{scalar_name}_{orientation}",
                apply,
                7,
                "struct_cardinality_renderer",
                metadata={
                    "semantic_scene_graph": True,
                    "scalar": scalar_name,
                    "renderer": orientation,
                    "observed_distinct_scalar_values": len(set(values)),
                    "stores_numeric_threshold": False,
                    "exact_demonstration_contract": True,
                },
            )
    return output


_CAUSAL_AFFINE_COUNT_SCALARS = (
    "objects4_color",
    "objects4_union",
    "objects8_color",
    "objects8_union",
    "background_regions4",
    "background_regions8",
    "foreground_colors",
)


def causal_affine_cardinality_rules(
    train: List[Tuple[Array, Array]],
    tests: List[Array],
) -> List[RuleCandidate]:
    """Compile a small affine semantic-count renderer.

    The output side length is derived from the held-out scene as ``count + b``
    with ``b`` restricted to ``[-2, 2]``.  Only semantic counts that vary in
    the demonstrations are eligible, and every demonstration output must be a
    uniform grid of one shared color.  Consequently neither the held-out
    shape nor its contents can be copied from a particular demonstration.

    The renderer is deliberately partial: an absent/degenerate scene count or
    an out-of-bounds affine size raises ``ValueError`` and the proposal
    abstains instead of coercing the result to a fallback grid.
    """
    output: List[RuleCandidate] = []
    if len(train) < 2 or not train or not tests:
        return output
    if not all(target.size and len(np.unique(target)) == 1 for _, target in train):
        return output
    fill_colors = {int(target.flat[0]) for _, target in train}
    if len(fill_colors) != 1:
        return output
    fill_color = next(iter(fill_colors))
    train_graphs = [build_scene_graph(source) for source, _ in train]
    scalar_records = [scene_scalar_values(graph) for graph in train_graphs]

    for scalar_name in _CAUSAL_AFFINE_COUNT_SCALARS:
        counts = [int(record[scalar_name]) for record in scalar_records]
        # Requiring at least two observed counts prevents a single constant
        # output size from supporting arbitrary affine offsets.
        if len(set(counts)) < 2:
            continue
        for offset in range(-2, 3):
            sizes = [count + offset for count in counts]
            if not all(1 <= size <= MAX_SIDE for size in sizes):
                continue
            for orientation in ("row", "col", "square"):
                def apply(
                    grid: Array,
                    key: str = scalar_name,
                    b: int = offset,
                    direction: str = orientation,
                    value: int = fill_color,
                ) -> Array:
                    semantic_count = int(
                        scene_scalar_values(build_scene_graph(grid))[key]
                    )
                    side = semantic_count + b
                    if not 1 <= side <= MAX_SIDE:
                        raise ValueError("affine semantic count outside ARC bounds")
                    if direction == "row":
                        shape = (1, side)
                    elif direction == "col":
                        shape = (side, 1)
                    else:
                        shape = (side, side)
                    return np.full(shape, value, dtype=np.int16)

                _try_exact_rule(
                    output,
                    train,
                    tests,
                    (
                        f"causal_affine_cardinality_{scalar_name}_"
                        f"plus_{offset}_{orientation}"
                    ),
                    apply,
                    6 if offset == 0 else 9 + abs(offset),
                    "causal_affine_cardinality",
                    metadata={
                        "compiler_block": "causal_quotient_provenance",
                        "semantic_scene_graph": True,
                        "typed_scalar": True,
                        "scalar": scalar_name,
                        "affine_scale": 1,
                        "affine_offset": offset,
                        "renderer": orientation,
                        "fill_color": fill_color,
                        "fill_color_contract": "uniform_shared_demo_color",
                        "output_shape_contract": "test_semantic_count_plus_offset",
                        "shape_source": "test_input_scene_graph",
                        "provenance_kind": "test_input_semantic_count",
                        "source_provenance": {
                            "kind": "test_input_scene_graph",
                            "measure": scalar_name,
                        },
                        "test_input_grounded": True,
                        "permutation_invariant": True,
                        "admissible": True,
                        "partial_operator": True,
                        "undefined_policy": "abstain",
                        "observed_distinct_scalar_values": len(set(counts)),
                        "stores_coordinates": False,
                        "exact_demonstration_contract": True,
                    },
                )
    return deduplicate_candidates(output)


@dataclass(frozen=True)
class SeparatorBarRatioRecord:
    """One boundary-anchored bar measured on both sides of a separator."""

    color: int
    column: int
    upper_length: int
    lower_length: int


def _separator_bar_ratio_scene(
    grid: Array,
) -> Tuple[int, int, Tuple[SeparatorBarRatioRecord, ...]]:
    """Parse two vertical bars around one full-width horizontal separator.

    Upper runs must be contiguous from the canvas top; lower runs must be
    contiguous from the first row below the separator. These strict anchors
    make the length ratio an input relation rather than an arbitrary count of
    scattered cells.
    """

    source = sanitize_grid(grid)
    height, width = source.shape
    if height < 5 or width < 3:
        raise ValueError("separator-bar scene is too small")
    background = infer_bg(source)
    separators: List[Tuple[int, int]] = []
    for row in range(1, height - 1):
        values = np.unique(source[row])
        if len(values) == 1 and int(values[0]) != int(background):
            separators.append((row, int(values[0])))
    if len(separators) != 1:
        raise ValueError("separator-bar scene requires one full-width separator")
    separator_row, separator_color = separators[0]
    separator_cells = np.argwhere(source == separator_color)
    if len(separator_cells) != width or any(
        int(row) != separator_row for row, _ in separator_cells
    ):
        raise ValueError("separator color must be confined to its boundary row")

    colors = sorted(
        int(value)
        for value in np.unique(source)
        if int(value) not in {int(background), int(separator_color)}
    )
    if len(colors) != 2:
        raise ValueError("separator-bar scene requires exactly two bar colors")
    records: List[SeparatorBarRatioRecord] = []
    for color in colors:
        cells = np.argwhere(source == color)
        columns = {int(column) for _, column in cells}
        if len(columns) != 1:
            raise ValueError("each bar color must occupy one shared column")
        column = next(iter(columns))
        upper_rows = sorted(
            int(row) for row, _ in cells if int(row) < separator_row
        )
        lower_rows = sorted(
            int(row) for row, _ in cells if int(row) > separator_row
        )
        if not upper_rows or not lower_rows:
            raise ValueError("each bar needs nonempty upper and lower runs")
        if upper_rows != list(range(len(upper_rows))):
            raise ValueError("upper bar run is not anchored to the canvas top")
        if lower_rows != list(
            range(separator_row + 1, separator_row + 1 + len(lower_rows))
        ):
            raise ValueError("lower bar run is not anchored to the separator")
        records.append(
            SeparatorBarRatioRecord(
                color=int(color),
                column=int(column),
                upper_length=len(upper_rows),
                lower_length=len(lower_rows),
            )
        )
    records.sort(key=lambda record: record.column)
    if records[0].column == records[1].column:
        raise ValueError("bar columns are not distinct")
    return int(separator_row), int(separator_color), tuple(records)


def _separator_bar_ratio_winners(
    records: Sequence[SeparatorBarRatioRecord],
) -> Tuple[SeparatorBarRatioRecord, ...]:
    """Return every exact maximizer of lower_length / upper_length."""

    if not records:
        raise ValueError("separator-bar ratio domain is empty")
    winners: List[SeparatorBarRatioRecord] = []
    for candidate in records:
        if all(
            candidate.lower_length * other.upper_length
            >= other.lower_length * candidate.upper_length
            for other in records
        ):
            winners.append(candidate)
    if not winners:
        raise ValueError("separator-bar ratios have no maximizer")
    return tuple(winners)


def _separator_bar_ratio_trace(
    grid: Array,
) -> Tuple[
    Array,
    int,
    int,
    Tuple[SeparatorBarRatioRecord, ...],
    SeparatorBarRatioRecord,
    bool,
]:
    separator_row, separator_color, records = _separator_bar_ratio_scene(grid)
    winners = _separator_bar_ratio_winners(records)
    tied = len(winners) > 1
    # The rightmost tie policy is only admissible after the rule compiler has
    # observed at least one tied demonstration with this exact output role.
    selected = max(winners, key=lambda record: record.column)
    side = len(records)
    output = np.full((side, side), selected.color, dtype=np.int16)
    return output, separator_row, separator_color, records, selected, tied


def separator_bar_ratio_select_exact(grid: Array) -> Array:
    """Select the maximal lower/upper bar ratio, breaking ties to the right."""

    return _separator_bar_ratio_trace(grid)[0]


def _separator_bar_ratio_signature(
    trace: Tuple[
        Array,
        int,
        int,
        Tuple[SeparatorBarRatioRecord, ...],
        SeparatorBarRatioRecord,
        bool,
    ],
) -> Tuple[object, ...]:
    _, _, _, records, selected, tied = trace
    return (
        tuple(
            (
                record.upper_length,
                record.lower_length,
                "selected" if record.color == selected.color else "unselected",
            )
            for record in records
        ),
        "tie" if tied else "strict",
    )


def separator_bar_ratio_rules(
    train: List[Tuple[Array, Array]],
    tests: List[Array],
) -> List[RuleCandidate]:
    """Compile a witnessed separator-bar ratio selector or abstain.

    At least one strict comparison and one tied demonstration are required.
    This prevents the rightmost tie policy from being introduced only when a
    held-out scene happens to need it.
    """

    if len(train) < 2 or not tests:
        return []
    try:
        train_traces = tuple(
            _separator_bar_ratio_trace(source) for source, _ in train
        )
        if not all(
            exact(trace[0], target)
            for trace, (_, target) in zip(train_traces, train)
        ):
            return []
        tie_support = sum(bool(trace[5]) for trace in train_traces)
        strict_support = len(train_traces) - tie_support
        if tie_support < 1 or strict_support < 1:
            return []
        test_traces = tuple(_separator_bar_ratio_trace(source) for source in tests)
    except (TypeError, ValueError):
        return []

    train_signatures = sorted(
        {_separator_bar_ratio_signature(trace) for trace in train_traces},
        key=repr,
    )
    test_signatures = [
        _separator_bar_ratio_signature(trace) for trace in test_traces
    ]
    metadata: Dict[str, object] = {
        "compiler_block": "causal_quotient_provenance",
        "typed_entity": "separator_anchored_vertical_bar_pair",
        "selector": "argmax_lower_to_upper_length_ratio",
        "ratio_comparison": "exact_integer_cross_multiplication",
        "tie_policy": "rightmost_ratio_maximizer",
        "tie_policy_evidence": "at_least_one_exact_training_tie",
        "strict_support_count": int(strict_support),
        "tie_support_count": int(tie_support),
        "renderer": "uniform_square_in_selected_input_color",
        "output_shape_contract": "bar_count_by_bar_count",
        "shape_source": "test_input_bar_count",
        "provenance_kind": "test_input_relational_measurement",
        "test_input_grounded": True,
        "permutation_invariant": True,
        "admissible": True,
        "source_provenance": {
            "kind": "test_input_bar_lengths",
            "upper_anchor": "canvas_top",
            "lower_anchor": "first_row_below_separator",
        },
        "partial_program": True,
        "undefined_when": [
            "separator_not_unique_or_not_full_width",
            "bar_color_count_not_two",
            "bar_not_single_column_or_not_contiguous",
            "upper_or_lower_bar_run_empty",
            "rightmost_tie_policy_not_demonstrated",
        ],
        "color_role_invariant": True,
        "exact_demonstration_contract": True,
        "train_relation_signatures": train_signatures,
        "test_relation_signatures": test_signatures,
    }
    return [
        RuleCandidate(
            name="separator_bar_ratio_select_rightmost_tie",
            grids=[trace[0] for trace in test_traces],
            train_error=0,
            complexity=8,
            family="causal_object_separator_bar_ratio_select",
            train_grids=tuple(trace[0] for trace in train_traces),
            metadata=metadata,
        )
    ]


def _contiguous_index_run_count(indices: Sequence[int]) -> int:
    """Count nonempty contiguous runs in an ordered index collection."""

    ordered = sorted({int(value) for value in indices})
    if not ordered:
        return 0
    return 1 + sum(
        int(right != left + 1)
        for left, right in zip(ordered, ordered[1:])
    )


def _separator_region_summary_trace(
    grid: Array,
) -> Tuple[Array, int, int, Tuple[int, ...], Tuple[int, ...], int, int]:
    """Summarize a full-row/full-column separator lattice by region count.

    The input must contain exactly one background color and one separator
    color. Every separator cell must belong to a complete interior row or
    complete interior column. Contiguous thick lines count as one boundary.
    The returned grid has one cell for every rectangular region induced by
    those separator bands and is filled with the input background color.
    """

    source = sanitize_grid(grid)
    height, width = source.shape
    if height < 3 or width < 3:
        raise ValueError("separator lattice is too small")
    values = sorted(int(value) for value in np.unique(source))
    if len(values) != 2:
        raise ValueError("separator lattice requires exactly two colors")
    background = int(infer_bg(source))
    separator_values = [value for value in values if value != background]
    if len(separator_values) != 1:
        raise ValueError("separator color is ambiguous")
    separator = int(separator_values[0])

    full_rows = tuple(
        int(row)
        for row in range(height)
        if bool(np.all(source[row, :] == separator))
    )
    full_columns = tuple(
        int(column)
        for column in range(width)
        if bool(np.all(source[:, column] == separator))
    )
    if not full_rows or not full_columns:
        raise ValueError("separator lattice needs row and column boundaries")
    if any(row in {0, height - 1} for row in full_rows) or any(
        column in {0, width - 1} for column in full_columns
    ):
        raise ValueError("separator boundaries must be interior")

    covered = np.zeros(source.shape, dtype=bool)
    covered[list(full_rows), :] = True
    covered[:, list(full_columns)] = True
    separator_mask = source == separator
    if not bool(np.array_equal(separator_mask, covered)):
        raise ValueError("separator color is not exactly a union of full lines")
    if not bool(np.all(source[~covered] == background)):
        raise ValueError("separator regions contain unsupported marks")

    row_boundaries = _contiguous_index_run_count(full_rows)
    column_boundaries = _contiguous_index_run_count(full_columns)
    output = np.full(
        (row_boundaries + 1, column_boundaries + 1),
        background,
        dtype=np.int16,
    )
    return (
        output,
        background,
        separator,
        full_rows,
        full_columns,
        row_boundaries,
        column_boundaries,
    )


def separator_region_summary_exact(grid: Array) -> Array:
    """Render one background cell for each separator-lattice region."""

    return _separator_region_summary_trace(grid)[0]


def separator_region_summary_rules(
    train: List[Tuple[Array, Array]],
    tests: List[Array],
) -> List[RuleCandidate]:
    """Compile the separator-region summary when every demonstration agrees."""

    if len(train) < 2 or not tests:
        return []
    try:
        train_traces = tuple(
            _separator_region_summary_trace(source) for source, _ in train
        )
        if not all(
            exact(trace[0], target)
            for trace, (_, target) in zip(train_traces, train)
        ):
            return []
        test_traces = tuple(
            _separator_region_summary_trace(source) for source in tests
        )
    except (TypeError, ValueError):
        return []

    return [
        RuleCandidate(
            name="separator_region_count_background_grid",
            grids=[trace[0] for trace in test_traces],
            train_error=0,
            complexity=6,
            family="causal_separator_region_summary",
            train_grids=tuple(trace[0] for trace in train_traces),
            metadata={
                "compiler_block": "separator_lattice_region_quotient",
                "typed_entity": "full_line_separator_lattice",
                "selector": "all_complete_interior_separator_bands",
                "renderer": "background_region_incidence_grid",
                "output_shape_contract": "row_separator_runs_plus_one_by_column_separator_runs_plus_one",
                "provenance_kind": "test_input_relational_measurement",
                "test_input_grounded": True,
                "permutation_invariant": True,
                "admissible": True,
                "partial_program": True,
                "undefined_when": [
                    "color_cardinality_not_two",
                    "missing_row_or_column_separator",
                    "separator_touches_canvas_boundary",
                    "separator_color_not_exact_full_line_union",
                    "unsupported_mark_inside_region",
                ],
                "color_role_invariant": True,
                "exact_demonstration_contract": True,
                "train_boundary_counts": [
                    [int(trace[5]), int(trace[6])] for trace in train_traces
                ],
                "test_boundary_counts": [
                    [int(trace[5]), int(trace[6])] for trace in test_traces
                ],
                "source_provenance": {
                    "kind": "input_separator_incidence",
                    "rows": "complete separator-color row bands",
                    "columns": "complete separator-color column bands",
                },
            },
        )
    ]


def role_lifted_object_rewrite_rules(
    train: List[Tuple[Array, Array]],
    tests: List[Array],
) -> List[RuleCandidate]:
    """Adapt the protected color-role rewrite into the solver portfolio."""

    try:
        compiled = compile_role_lifted_object_rewrite(train, tests)
    except (TypeError, ValueError):
        return []
    return [
        RuleCandidate(
            name=candidate.name,
            grids=[sanitize_grid(grid) for grid in candidate.grids],
            train_error=int(candidate.train_error),
            complexity=int(candidate.complexity),
            family=candidate.family,
            train_grids=tuple(
                sanitize_grid(grid) for grid in candidate.train_grids
            ),
            metadata=dict(candidate.metadata),
        )
        for candidate in compiled
    ]


def role_bound_object_rewrite_rules(
    train: List[Tuple[Array, Array]],
    tests: List[Array],
) -> List[RuleCandidate]:
    """Adapt exact role-bound programs without entering the frozen baseline.

    The runtime uses this adapter only through the isolated role challenger
    lane.  It deliberately does not participate in ``collect_candidates``:
    literal-free role programs must not evict a legacy baseline proposal or
    manufacture support through a shared cap.
    """

    try:
        compiled = compile_role_bound_object_rewrites(train, tests)
    except (RoleBindingAmbiguityError, RoleBindingLimitError):
        raise
    except (RoleBindingError, TypeError, ValueError):
        return []
    candidates: List[RuleCandidate] = []
    for candidate in compiled:
        grids = [sanitize_grid(grid) for grid in candidate.grids]
        train_grids = tuple(
            sanitize_grid(grid) for grid in candidate.train_grids
        )
        if len(grids) != len(tests) or len(train_grids) != len(train):
            continue
        if any(
            not exact(prediction, target)
            for prediction, (_, target) in zip(train_grids, train)
        ):
            continue
        metadata = dict(candidate.metadata)
        metadata.update(
            {
                "portfolio_lane": "isolated_role_bound_challenger",
                "challenger_origin": "bounded_role_program_compiler",
                "test_input_grounded": True,
                "provenance_kind": "test_input_role_binding",
                "admissible": True,
            }
        )
        if bool(metadata.get("empirical_promotion_eligible", False)):
            metadata.update(
                {
                    "promotion_gate": "complete_public_training_gain_loss_audit",
                    "complete_public_training_gain_loss_audit": True,
                    "promotion_audit": dict(_ROLE_BOUND_PUBLIC_TRAINING_AUDIT),
                    "implementation_fingerprint": (
                        role_bound_implementation_fingerprint()
                    ),
                }
            )
            metadata["empirical_promotion_eligible"] = (
                _role_bound_candidate_audit_valid(metadata)
            )
        candidates.append(
            RuleCandidate(
                name=str(candidate.name),
                grids=grids,
                train_error=0,
                complexity=int(candidate.complexity),
                family=str(candidate.family),
                train_grids=train_grids,
                metadata=metadata,
            )
        )
    return candidates


def _role_bound_candidate_audit_valid(metadata: object) -> bool:
    """Verify the complete executable promotion receipt, not a caller flag."""

    if not isinstance(metadata, dict):
        return False
    program_hash = str(metadata.get("program_hash", ""))
    if program_hash not in _ROLE_BOUND_AUDITED_PROGRAM_HASHES:
        return False
    try:
        serialized_program = RoleBoundObjectProgram.from_record(
            metadata.get("program")
        )
    except (RoleBindingError, TypeError, ValueError):
        return False
    if serialized_program.program_hash() != program_hash:
        return False
    if metadata.get("promotion_gate") != "complete_public_training_gain_loss_audit":
        return False
    if metadata.get("complete_public_training_gain_loss_audit") is not True:
        return False
    audit = metadata.get("promotion_audit")
    if not isinstance(audit, dict):
        return False
    required = {
        "schema": "komorebi.arc.role-bound-promotion-evidence.v1",
        "artifact": "release/ROLE_BOUND_PROGRAM_VALIDATION_1.5.0.dev1.json",
        "official_source_commit": "f3283f727488ad98fe575ea6a5ac981e4a188e49",
        "official_corpus_sha256": "aa3385893c765ab10251f48bb7b886e3e2e3d79be6b9d70c673248805048cbae",
        "baseline_submission_sha256": "b61b1db61eb919ba9c66441fc5c386a69f914f9bce4f2cd3519c3cfd46138f19",
        "tasks": 1000,
        "test_outputs": 1076,
        "activated_outputs": 5,
        "exact_activations": 5,
        "wrong_activations": 0,
        "pass_at_2_gains": 4,
        "pass_at_2_losses": 0,
        "attempt_1_changes": 0,
        "interpreter_sha256": _ROLE_BOUND_AUDITED_INTERPRETER_SHA256,
        "entry_contract_sha256": str(
            _ROLE_BOUND_PUBLIC_TRAINING_AUDIT["entry_contract_sha256"]
        ),
    }
    if any(audit.get(key) != value for key, value in required.items()):
        return False
    audited_hashes = audit.get("promotion_approved_program_hashes")
    if not isinstance(audited_hashes, list) or frozenset(
        str(value) for value in audited_hashes
    ) != _ROLE_BOUND_AUDITED_PROGRAM_HASHES:
        return False
    try:
        current_fingerprint = role_bound_implementation_fingerprint()
    except (OSError, ValueError):
        return False
    try:
        entry_contract = _role_bound_entry_contract_fingerprint()
    except (OSError, TypeError, ValueError):
        return False
    return bool(
        metadata.get("implementation_fingerprint") == current_fingerprint
        and current_fingerprint == _ROLE_BOUND_AUDITED_INTERPRETER_SHA256
        and entry_contract
        == _ROLE_BOUND_PUBLIC_TRAINING_AUDIT["entry_contract_sha256"]
    )


def _role_bound_support_audit_valid(support: object) -> bool:
    """Require at least one audited candidate receipt for this exact behavior."""

    if not isinstance(support, dict):
        return False
    records = support.get("candidate_metadata")
    if not isinstance(records, list):
        return False
    return any(
        isinstance(record, dict)
        and _role_bound_candidate_audit_valid(record.get("metadata"))
        for record in records
    )


def _role_bound_support_execution_valid(
    support: object,
    challenger: Array,
    test_input: Array,
) -> bool:
    """Re-execute an audited serialized program on the actual test source."""

    if not isinstance(support, dict):
        return False
    challenger = sanitize_grid(challenger)
    if support.get("output_hash") != _sric_grid_hash(challenger):
        return False
    records = support.get("candidate_metadata")
    if not isinstance(records, list):
        return False
    for record in records:
        if not isinstance(record, dict):
            continue
        metadata = record.get("metadata")
        if not _role_bound_candidate_audit_valid(metadata):
            continue
        try:
            assert isinstance(metadata, dict)
            program = RoleBoundObjectProgram.from_record(metadata.get("program"))
            prediction = program.apply(test_input)
        except (AssertionError, RoleBindingError, TypeError, ValueError):
            continue
        if exact(prediction, challenger):
            return True
    return False


def _role_bound_entry_contract_fingerprint() -> str:
    """Bind promotion evidence to adapter, lane, and promotion semantics."""

    audited_facts = {
        key: value
        for key, value in _ROLE_BOUND_PUBLIC_TRAINING_AUDIT.items()
        if key != "entry_contract_sha256"
    }
    functions = (
        role_bound_object_rewrite_rules,
        _role_bound_candidate_audit_valid,
        _role_bound_support_audit_valid,
        _role_bound_support_execution_valid,
        role_bound_object_challenger_lane,
        _promote_role_bound_outputs,
    )
    payload = {
        "audit_facts": audited_facts,
        "sources": [inspect.getsource(function) for function in functions],
    }
    encoded = json.dumps(
        payload,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=True,
    ).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def _scene_dihedral(grid: Array, transform: str) -> Array:
    source = sanitize_grid(grid)
    transforms: Dict[str, Callable[[Array], Array]] = {
        "same": lambda value: value,
        "flip_h": np.fliplr,
        "flip_v": np.flipud,
        "rot180": lambda value: np.rot90(value, 2),
        "transpose": lambda value: value.T,
    }
    if transform not in transforms:
        raise ValueError(transform)
    return sanitize_grid(transforms[transform](source))


def _panel_mask(
    panel: Array,
    policy: str,
    background: Optional[int] = None,
) -> Array:
    panel = sanitize_grid(panel)
    background = infer_bg(panel) if background is None else int(background)
    if policy == "support":
        mask = panel != background
    elif policy == "rarest_color":
        mask = panel == rare_color(panel, background)
    elif policy == "marker_color":
        mask = panel == marker_color(panel, background)
    elif policy == "largest_object":
        foreground = panel != background
        seen = np.zeros(panel.shape, dtype=bool)
        components: List[List[Tuple[int, int]]] = []
        for row in range(panel.shape[0]):
            for column in range(panel.shape[1]):
                if seen[row, column] or not foreground[row, column]:
                    continue
                queue = deque([(row, column)])
                seen[row, column] = True
                cells: List[Tuple[int, int]] = []
                while queue:
                    current_row, current_column = queue.popleft()
                    cells.append((current_row, current_column))
                    for delta_row, delta_column in (
                        (1, 0),
                        (-1, 0),
                        (0, 1),
                        (0, -1),
                    ):
                        next_row = current_row + delta_row
                        next_column = current_column + delta_column
                        if (
                            0 <= next_row < panel.shape[0]
                            and 0 <= next_column < panel.shape[1]
                            and foreground[next_row, next_column]
                            and not seen[next_row, next_column]
                        ):
                            seen[next_row, next_column] = True
                            queue.append((next_row, next_column))
                components.append(cells)
        if not components:
            raise ValueError("panel has no foreground object")
        cells = max(components, key=lambda values: len(values))
        mask = np.zeros(panel.shape, dtype=bool)
        for row, column in cells:
            mask[row, column] = True
    else:
        raise ValueError(policy)
    if not np.any(mask):
        raise ValueError("panel mask has no active cells")
    return np.asarray(mask, dtype=bool)


def _panel_corner_values(panel: Array) -> Tuple[int, ...]:
    values = sanitize_grid(panel)
    return (
        int(values[0, 0]),
        int(values[0, -1]),
        int(values[-1, 0]),
        int(values[-1, -1]),
    )


def _stable_panel_backgrounds(
    grid: Array,
    panels: Tuple[Array, Array],
    mask_side: int,
    policy: str,
) -> Tuple[int, int]:
    """Infer mask/motif backgrounds from stable, input-derived evidence."""
    mask_panel = panels[int(mask_side)]
    motif_panel = panels[1 - int(mask_side)]
    if policy == "panel_infer":
        return infer_bg(mask_panel), infer_bg(motif_panel)
    if policy == "shared_panel_corners":
        first_corners = _panel_corner_values(panels[0])
        second_corners = _panel_corner_values(panels[1])
        shared = set(first_corners).intersection(second_corners)
        if not shared:
            raise ValueError("panels have no shared corner-background candidate")
        counts = Counter(first_corners + second_corners)
        background = min(shared, key=lambda value: (-counts[value], value))
    elif policy == "grid_corners":
        counts = Counter(_panel_corner_values(grid))
        background = min(counts, key=lambda value: (-counts[value], value))
    elif policy == "grid_majority":
        background = majority_color(sanitize_grid(grid))
    else:
        raise ValueError(f"unknown panel background policy {policy!r}")
    return int(background), int(background)


def _panel_broadcast_output_shape(
    grid: Array,
    panel_mode: str,
    mask_side: int,
    mask_transform: str,
    motif_transform: str,
) -> Tuple[int, int]:
    panels = _scene_panel_pair(grid, panel_mode)
    mask_shape = panels[int(mask_side)].shape
    motif_shape = panels[1 - int(mask_side)].shape
    if mask_transform == "transpose":
        mask_shape = (mask_shape[1], mask_shape[0])
    if motif_transform == "transpose":
        motif_shape = (motif_shape[1], motif_shape[0])
    return (
        int(mask_shape[0] * motif_shape[0]),
        int(mask_shape[1] * motif_shape[1]),
    )


def render_panel_mask_motif_exact(
    grid: Array,
    panel_mode: str,
    mask_side: int,
    mask_policy: str,
    mask_transform: str,
    motif_transform: str,
    complement: bool,
    background_policy: str = "panel_infer",
) -> Array:
    first, second = _scene_panel_pair(grid, panel_mode)
    panels = (first, second)
    mask_panel = _scene_dihedral(panels[int(mask_side)], mask_transform)
    motif = _scene_dihedral(panels[1 - int(mask_side)], motif_transform)
    mask_background, motif_background = _stable_panel_backgrounds(
        grid,
        panels,
        mask_side,
        background_policy,
    )
    mask = _panel_mask(mask_panel, mask_policy, mask_background)
    if complement:
        mask = ~mask
    if not np.any(mask) or not np.any(~mask):
        raise ValueError("mask/motif broadcast requires active and inactive blocks")
    output_height = mask.shape[0] * motif.shape[0]
    output_width = mask.shape[1] * motif.shape[1]
    if output_height > MAX_SIDE or output_width > MAX_SIDE:
        raise ValueError("mask/motif broadcast exceeds ARC bounds")
    output = np.full(
        (output_height, output_width),
        motif_background,
        dtype=np.int16,
    )
    for row, column in np.argwhere(mask):
        top = int(row) * motif.shape[0]
        left = int(column) * motif.shape[1]
        output[top : top + motif.shape[0], left : left + motif.shape[1]] = motif
    return output


def mask_motif_broadcast_rules(
    train: List[Tuple[Array, Array]],
    tests: List[Array],
    maximum_programs: int = 512,
) -> List[RuleCandidate]:
    output: List[RuleCandidate] = []
    if not train:
        return output
    common_modes = sorted(
        set.intersection(
            *[
                {mode for mode, _, _ in _scene_panel_pairs(source)}
                for source, _ in train
            ]
        )
    )
    transforms = ("same", "flip_h", "flip_v", "rot180", "transpose")
    policies = ("support", "rarest_color", "marker_color", "largest_object")
    background_policies = (
        "shared_panel_corners",
        "grid_corners",
        "grid_majority",
        "panel_infer",
    )
    buckets = [
        (mode, mask_side, policy)
        for mode in common_modes
        for mask_side in (0, 1)
        for policy in policies
    ]
    variants = [
        (mask_transform, motif_transform, complement, background_policy)
        for mask_transform in transforms
        for motif_transform in transforms
        for complement in (False, True)
        for background_policy in background_policies
    ]
    transform_rank = {name: index for index, name in enumerate(transforms)}
    background_rank = {
        name: index for index, name in enumerate(background_policies)
    }
    variants.sort(
        key=lambda value: (
            int(value[0] != "same") + int(value[1] != "same"),
            transform_rank[value[0]] + transform_rank[value[1]],
            int(value[2]),
            background_rank[value[3]],
            transform_rank[value[0]],
            transform_rank[value[1]],
        )
    )
    attempted = 0
    for mask_transform, motif_transform, complement, background_policy in variants:
        for mode, mask_side, policy in buckets:
            if attempted >= max(1, int(maximum_programs)):
                return deduplicate_candidates(output)
            if not all(
                _panel_broadcast_output_shape(
                    source,
                    mode,
                    mask_side,
                    mask_transform,
                    motif_transform,
                )
                == target.shape
                for source, target in train
            ):
                continue
            attempted += 1
            fn = lambda grid, panel_mode=mode, side=mask_side, mask_kind=policy, mask_tx=mask_transform, motif_tx=motif_transform, inverted=complement, bg_policy=background_policy: render_panel_mask_motif_exact(
                grid,
                panel_mode,
                side,
                mask_kind,
                mask_tx,
                motif_tx,
                inverted,
                bg_policy,
            )
            _try_exact_rule(
                output,
                train,
                tests,
                (
                    f"mask_motif:{mode}:{mask_side}:{policy}:"
                    f"{mask_transform}:{motif_transform}:{int(complement)}:"
                    f"{background_policy}"
                ),
                fn,
                10,
                "struct_mask_motif_broadcast",
                metadata={
                    "semantic_scene_graph": True,
                    "typed_scalar_mask": True,
                    "panel_mode": mode,
                    "mask_side": mask_side,
                    "mask_policy": policy,
                    "mask_transform": mask_transform,
                    "motif_transform": motif_transform,
                    "complement": complement,
                    "background_policy": background_policy,
                    "input_derived_mask": True,
                    "input_derived_motif": True,
                    "translation_equivariant": False,
                    "stores_coordinates": False,
                    "exact_demonstration_contract": True,
                },
            )
    return deduplicate_candidates(output)


def typed_scalar_mask_rules(
    train: List[Tuple[Array, Array]],
    tests: List[Array],
) -> List[RuleCandidate]:
    output = typed_scalar_mask_refinement_rules(
        [],
        train,
        tests,
        maximum_programs=640,
        maximum_exact=24,
        include_identity=True,
    )
    output.extend(scene_cardinality_renderer_rules(train, tests))
    output.extend(causal_affine_cardinality_rules(train, tests))
    output.extend(mask_motif_broadcast_rules(train, tests))
    return deduplicate_candidates(output)


def typed_scalar_mask_terminal_rules(
    train: List[Tuple[Array, Array]],
    tests: List[Array],
) -> List[RuleCandidate]:
    """Narrow predicate-only scalar terminal for deep composition tiers."""
    return typed_scalar_mask_refinement_rules(
        [],
        train,
        tests,
        maximum_programs=640,
        maximum_exact=8,
        include_identity=True,
    )


# ---------------- SRIC witness-separated relational repair lane ----------------

@dataclass(frozen=True)
class SRICRelationalSchema:
    """A coordinate-free repair synthesized from a representation collision.

    The schema deliberately contains only a semantic anchor, a pairwise
    relation, and a typed cell action.  Absolute task coordinates, task IDs,
    and test-derived parameters are not representable in this object.
    """

    anchor_policy: str
    relation: str
    action: str
    target_color: Optional[int] = None
    anchor_hole_class: str = "any"
    domain: str = "objects4_color"
    schema_version: str = "sric.arc.relational.v2"

    def program_ast(self) -> Dict[str, object]:
        return {
            "schema_version": self.schema_version,
            "domain": self.domain,
            "anchor_policy": self.anchor_policy,
            "relation": self.relation,
            "action": self.action,
            "target_color": self.target_color,
            "anchor_hole_class": self.anchor_hole_class,
        }

    def program_hash(self) -> str:
        encoded = json.dumps(
            self.program_ast(),
            sort_keys=True,
            separators=(",", ":"),
        ).encode("utf-8")
        return hashlib.sha256(encoded).hexdigest()


_SRIC_ANCHOR_POLICIES = (
    "unique_singleton",
    "unique_holed",
    "unique_largest",
    "unique_smallest_non_singleton",
    "sole_unique_shape",
    "sole_unique_color",
)

_SRIC_RELATIONS = (
    "nearest",
    "farthest",
    "axis_aligned",
    "diagonal_aligned",
    "touching",
    "above_anchor",
    "below_anchor",
    "left_of_anchor",
    "right_of_anchor",
)

_SRIC_D4_INVARIANT_RELATIONS = frozenset(
    {
        "nearest",
        "farthest",
        "axis_aligned",
        "diagonal_aligned",
        "touching",
    }
)

_SRIC_SCHEMA_KEYS = frozenset(
    {
        "schema_version",
        "domain",
        "anchor_policy",
        "relation",
        "action",
        "target_color",
        "anchor_hole_class",
    }
)
_SRIC_RUNTIME_SEMANTICS_VERSION = "sric.arc.relational.runtime.v3"
_SRIC_MAX_SCENE_UNITS = 24
_SRIC_MAX_SCHEMA_CHECKS = len(_SRIC_ANCHOR_POLICIES) * len(_SRIC_RELATIONS)
_SRIC_MAX_WITNESS_GROUPS = 5
_SRIC_PROMOTION_POLICIES = frozenset({"shadow", "conservative", "replace_attempt2"})


def _sric_json_hash(value: object) -> str:
    encoded = json.dumps(value, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def _sric_grid_hash(grid: Array) -> str:
    return _sric_json_hash(sanitize_grid(grid).astype(int).tolist())


def _sric_example_hash(source: Array, target: Array) -> str:
    return _sric_json_hash(
        {
            "input": sanitize_grid(source).astype(int).tolist(),
            "output": sanitize_grid(target).astype(int).tolist(),
        }
    )


def _sric_schema_from_ast(value: object) -> SRICRelationalSchema:
    """Parse the closed SRIC AST instead of trusting candidate metadata."""
    if not isinstance(value, dict) or set(value) != _SRIC_SCHEMA_KEYS:
        raise ValueError("SRIC program AST has an invalid key set")
    schema_version = value.get("schema_version")
    domain = value.get("domain")
    anchor_policy = value.get("anchor_policy")
    relation = value.get("relation")
    action = value.get("action")
    target_color = value.get("target_color")
    anchor_hole_class = value.get("anchor_hole_class")
    if schema_version != "sric.arc.relational.v2":
        raise ValueError("unsupported SRIC schema version")
    if domain != "objects4_color":
        raise ValueError("unsupported SRIC scene domain")
    if anchor_policy not in _SRIC_ANCHOR_POLICIES:
        raise ValueError("unknown SRIC anchor policy")
    if relation not in _SRIC_RELATIONS:
        raise ValueError("unknown SRIC relation")
    if anchor_hole_class not in {"any", "holed", "unholed"}:
        raise ValueError("unknown SRIC anchor hole class")
    if action in {"erase", "paint_anchor_color"}:
        if target_color is not None:
            raise ValueError(f"{action} schemas cannot carry a target color")
    elif action == "paint":
        if isinstance(target_color, bool) or not isinstance(target_color, int):
            raise ValueError("paint schemas require an integer target color")
        if not 0 <= int(target_color) <= 9:
            raise ValueError("paint target color is outside the ARC palette")
    else:
        raise ValueError("unknown SRIC action")
    return SRICRelationalSchema(
        anchor_policy=str(anchor_policy),
        relation=str(relation),
        action=str(action),
        target_color=None if target_color is None else int(target_color),
        anchor_hole_class=str(anchor_hole_class),
        domain=str(domain),
        schema_version=str(schema_version),
    )


def _sric_unit_signature(unit: SceneUnit) -> Tuple[object, ...]:
    """Current coordinate-free description used to expose collisions."""
    return (
        unit.kind,
        unit.colors,
        unit.area,
        unit.height,
        unit.width,
        unit.holes,
        round(float(unit.density), 12),
        unit.touches_border,
        unit.symmetric,
        unit.shape_key,
        unit.shape_multiplicity,
        unit.color_multiplicity,
    )


def _sric_unit_action(
    source: Array,
    target: Array,
    unit: SceneUnit,
) -> Tuple[str, Optional[int]]:
    """Classify direct object-cell actions without inferring a correspondence."""
    source = sanitize_grid(source)
    target = sanitize_grid(target)
    if source.shape != target.shape:
        return ("unsupported", None)
    before = np.asarray([source[row, column] for row, column in unit.cells], dtype=np.int16)
    after = np.asarray([target[row, column] for row, column in unit.cells], dtype=np.int16)
    if np.array_equal(before, after):
        return ("keep", None)
    if after.size and bool(np.all(after == infer_bg(target))):
        return ("erase", None)
    unique = np.unique(after)
    if unique.size == 1:
        return ("paint", int(unique[0]))
    return ("unsupported", None)


def _sric_representation_collision_summary(
    train: List[Tuple[Array, Array]],
    graphs: Optional[Sequence[SceneGraph]] = None,
) -> Dict[str, object]:
    """Find equal current descriptions that require incompatible cell actions."""
    if graphs is None:
        graphs = tuple(build_scene_graph(source) for source, _ in train)
    if len(graphs) != len(train):
        raise ValueError("SRIC graph cache does not match the demonstrations")
    action_sets: Dict[Tuple[object, ...], set[Tuple[str, Optional[int]]]] = defaultdict(set)
    observations = 0
    for (source, target), graph in zip(train, graphs):
        for unit in graph.objects4_color:
            action = _sric_unit_action(source, target, unit)
            if action[0] == "unsupported":
                continue
            action_sets[_sric_unit_signature(unit)].add(action)
            observations += 1
    collisions = [
        actions
        for actions in action_sets.values()
        if len(actions) > 1
        and any(action[0] == "keep" for action in actions)
        and any(action[0] in {"paint", "erase"} for action in actions)
    ]
    return {
        "observations": int(observations),
        "signature_classes": int(len(action_sets)),
        "collision_classes": int(len(collisions)),
        "action_pairs": sorted(
            {
                tuple(sorted(action[0] for action in actions))
                for actions in collisions
            }
        ),
    }


def _sric_unique_anchor(
    units: Sequence[SceneUnit],
    policy: str,
) -> Optional[SceneUnit]:
    units = tuple(units)
    if not units:
        return None
    if policy == "unique_singleton":
        candidates = [unit for unit in units if unit.area == 1]
    elif policy == "unique_holed":
        candidates = [unit for unit in units if unit.holes > 0]
    elif policy == "unique_largest":
        maximum = max(unit.area for unit in units)
        candidates = [unit for unit in units if unit.area == maximum]
    elif policy == "unique_smallest_non_singleton":
        non_singletons = [unit for unit in units if unit.area > 1]
        if not non_singletons:
            return None
        minimum = min(unit.area for unit in non_singletons)
        candidates = [unit for unit in non_singletons if unit.area == minimum]
    elif policy == "sole_unique_shape":
        candidates = [unit for unit in units if unit.shape_multiplicity == 1]
    elif policy == "sole_unique_color":
        candidates = [unit for unit in units if unit.color_multiplicity == 1]
    else:
        raise ValueError(f"unknown SRIC anchor policy {policy!r}")
    return candidates[0] if len(candidates) == 1 else None


def _sric_same_unit(left: SceneUnit, right: SceneUnit) -> bool:
    return left.cells == right.cells and left.colors == right.colors


def _sric_cell_distance(left: SceneUnit, right: SceneUnit) -> int:
    return min(
        abs(left_row - right_row) + abs(left_column - right_column)
        for left_row, left_column in left.cells
        for right_row, right_column in right.cells
    )


def _sric_bbox_contains(outer: SceneUnit, inner: SceneUnit) -> bool:
    ot, ol, ob, oright = outer.bbox
    it, il, ib, iright = inner.bbox
    return ot <= it and ol <= il and ob >= ib and oright >= iright and outer.bbox != inner.bbox


def _sric_select_relation(
    units: Sequence[SceneUnit],
    anchor: SceneUnit,
    relation: str,
) -> Tuple[SceneUnit, ...]:
    payloads = tuple(unit for unit in units if not _sric_same_unit(unit, anchor))
    if not payloads:
        return ()
    if relation in {"nearest", "farthest"}:
        distances = [(int(_sric_cell_distance(unit, anchor)), unit) for unit in payloads]
        extreme = (
            min(distance for distance, _ in distances)
            if relation == "nearest"
            else max(distance for distance, _ in distances)
        )
        selected = tuple(unit for distance, unit in distances if distance == extreme)
        return selected if len(selected) == 1 else ()

    at, al, ab, aright = anchor.bbox
    anchor_row2 = at + ab
    anchor_column2 = al + aright
    selected: List[SceneUnit] = []
    for unit in payloads:
        top, left, bottom, right = unit.bbox
        row2 = top + bottom
        column2 = left + right
        keep = False
        if relation == "axis_aligned":
            keep = not (bottom < at or top > ab) or not (right < al or left > aright)
        elif relation == "diagonal_aligned":
            keep = abs(row2 - anchor_row2) == abs(column2 - anchor_column2)
        elif relation == "touching":
            keep = _sric_cell_distance(unit, anchor) == 1
        elif relation == "inside_anchor":
            keep = _sric_bbox_contains(anchor, unit)
        elif relation == "contains_anchor":
            keep = _sric_bbox_contains(unit, anchor)
        elif relation == "same_shape":
            keep = unit.shape_key == anchor.shape_key
        elif relation == "same_color":
            keep = unit.colors == anchor.colors
        elif relation == "above_anchor":
            keep = bottom < at
        elif relation == "below_anchor":
            keep = top > ab
        elif relation == "left_of_anchor":
            keep = right < al
        elif relation == "right_of_anchor":
            keep = left > aright
        else:
            raise ValueError(f"unknown SRIC relation {relation!r}")
        if keep:
            selected.append(unit)
    return tuple(selected)


def sric_apply_relational_schema(grid: Array, schema: SRICRelationalSchema) -> Array:
    source = sanitize_grid(grid)
    graph = build_scene_graph(source)
    units = scene_domain_units(graph, schema.domain)
    anchor = _sric_unique_anchor(units, schema.anchor_policy)
    if anchor is None:
        raise ValueError("SRIC schema has no unique semantic anchor")
    if schema.anchor_hole_class == "holed" and anchor.holes <= 0:
        raise ValueError("SRIC anchor violates the holed precondition")
    if schema.anchor_hole_class == "unholed" and anchor.holes != 0:
        raise ValueError("SRIC anchor violates the unholed precondition")
    selected = _sric_select_relation(units, anchor, schema.relation)
    if not selected:
        raise ValueError("SRIC relational branch has no supported object")
    output = source.copy()
    if schema.action == "erase":
        value = int(graph.background)
    elif schema.action == "paint_anchor_color" and len(anchor.colors) == 1:
        value = int(anchor.colors[0])
    elif schema.action == "paint" and schema.target_color is not None:
        value = int(schema.target_color)
    else:
        raise ValueError("invalid SRIC relational action")
    for unit in selected:
        for row, column in unit.cells:
            output[row, column] = value
    return sanitize_grid(output)


def sric_relational_separator_rules(
    train: List[Tuple[Array, Array]],
    tests: List[Array],
    *,
    maximum_schema_checks: int = _SRIC_MAX_SCHEMA_CHECKS,
    maximum_scene_units: int = _SRIC_MAX_SCENE_UNITS,
) -> List[RuleCandidate]:
    """Synthesize relation features only after a current-description collision.

    This is a bounded implementation of SRIC's representation-separation
    trigger.  It supports direct paint/erase repairs and refuses coordinate
    tables, unsupported mixed edits, ambiguous anchors, and relation ties.
    """
    maximum_schema_checks = max(0, min(int(maximum_schema_checks), _SRIC_MAX_SCHEMA_CHECKS))
    maximum_scene_units = max(1, int(maximum_scene_units))
    if not train or maximum_schema_checks == 0:
        return []
    all_inputs = [source for source, _ in train] + list(tests)
    # The cheap connected-component preflight prevents this auxiliary lane
    # from consuming a hard-isolated worker on dense repeated-object scenes.
    if any(len(components(grid)) > maximum_scene_units for grid in all_inputs):
        return []
    graphs = tuple(build_scene_graph(source) for source, _ in train)
    if any(len(graph.objects4_color) > maximum_scene_units for graph in graphs):
        return []
    collision = _sric_representation_collision_summary(train, graphs)
    if int(collision["collision_classes"]) <= 0:
        return []

    candidates: List[RuleCandidate] = []
    seen_programs: set[str] = set()
    schema_checks = 0
    for anchor_policy in _SRIC_ANCHOR_POLICIES:
        for relation in _SRIC_RELATIONS:
            if schema_checks >= maximum_schema_checks:
                break
            schema_checks += 1
            selected_actions: List[Tuple[str, Optional[int]]] = []
            anchor_colors: List[Optional[int]] = []
            anchor_holes: List[int] = []
            selected_support = 0
            unselected_support = 0
            valid = True
            for (source, target), graph in zip(train, graphs):
                units = graph.objects4_color
                anchor = _sric_unique_anchor(units, anchor_policy)
                if anchor is None:
                    valid = False
                    break
                selected = _sric_select_relation(units, anchor, relation)
                if not selected:
                    valid = False
                    break
                selected_keys = {(unit.cells, unit.colors) for unit in selected}
                unselected = [
                    unit
                    for unit in units
                    if (unit.cells, unit.colors) not in selected_keys
                ]
                if not unselected:
                    valid = False
                    break
                actions = [_sric_unit_action(source, target, unit) for unit in selected]
                other_actions = [_sric_unit_action(source, target, unit) for unit in unselected]
                if (
                    any(action[0] not in {"paint", "erase"} for action in actions)
                    or any(action[0] != "keep" for action in other_actions)
                    or len(set(actions)) != 1
                ):
                    valid = False
                    break
                selected_actions.append(actions[0])
                anchor_colors.append(
                    int(anchor.colors[0]) if len(anchor.colors) == 1 else None
                )
                anchor_holes.append(int(anchor.holes))
                selected_support += len(selected)
                unselected_support += len(unselected)
            if not valid or not selected_actions:
                continue
            action_kinds = {action for action, _ in selected_actions}
            if action_kinds == {"erase"}:
                schema_options = [("erase", None)]
            elif action_kinds == {"paint"}:
                targets = {target for _, target in selected_actions}
                anchor_parameter_supported = all(
                    anchor_color is not None and target == anchor_color
                    for (_, target), anchor_color in zip(selected_actions, anchor_colors)
                )
                schema_options: List[Tuple[str, Optional[int]]] = []
                if anchor_parameter_supported:
                    schema_options.append(("paint_anchor_color", None))
                if len(targets) == 1:
                    schema_options.append(("paint", selected_actions[0][1]))
                if not schema_options:
                    continue
            else:
                continue
            if all(holes > 0 for holes in anchor_holes):
                anchor_hole_class = "holed"
            elif all(holes == 0 for holes in anchor_holes):
                anchor_hole_class = "unholed"
            else:
                anchor_hole_class = "any"
            for action, target_color in schema_options:
                schema = SRICRelationalSchema(
                    anchor_policy=anchor_policy,
                    relation=relation,
                    action=action,
                    target_color=target_color,
                    anchor_hole_class=anchor_hole_class,
                )
                program_hash = schema.program_hash()
                if program_hash in seen_programs:
                    continue
                try:
                    train_grids = tuple(sric_apply_relational_schema(source, schema) for source, _ in train)
                    test_grids = [sric_apply_relational_schema(test, schema) for test in tests]
                except (ValueError, IndexError, KeyError):
                    continue
                if not all(exact(prediction, target) for prediction, (_, target) in zip(train_grids, train)):
                    continue
                seen_programs.add(program_hash)
                transport_contract = (
                    "d4_invariant_with_parameter_transport"
                    if relation in _SRIC_D4_INVARIANT_RELATIONS
                    else "global_canvas_frame_only_no_d4_transport"
                )
                candidates.append(
                    RuleCandidate(
                        name=(
                            f"sric_separator:{anchor_policy}:{relation}:"
                            f"{action}:{target_color if target_color is not None else 'semantic'}"
                        ),
                        grids=test_grids,
                        train_error=0,
                        complexity=14 + len(relation.split("_")),
                        family="sric_relational_separator",
                        train_grids=train_grids,
                        metadata={
                            "sric_repair": True,
                            "sric_program_ast": schema.program_ast(),
                            "sric_program_hash": program_hash,
                            "representation_collision": dict(collision),
                            "selected_support": int(selected_support),
                            "unselected_support": int(unselected_support),
                            "branch_support_required": True,
                            "stores_coordinates": False,
                            "stores_task_ids": False,
                            "test_conditioned_parameters": False,
                            "exact_demonstration_contract": True,
                            "transport_contract": transport_contract,
                            "palette_transport_requires_parameter_map": True,
                            "schema_checks_consumed": int(schema_checks),
                            "schema_check_cap": int(maximum_schema_checks),
                            "scene_unit_cap": int(maximum_scene_units),
                        },
                    )
                )
        if schema_checks >= maximum_schema_checks:
            break
    return deduplicate_candidates(candidates)


def _sric_task_witness_hash(train: List[Tuple[Array, Array]]) -> str:
    payload = [
        {
            "input": sanitize_grid(source).astype(int).tolist(),
            "output": sanitize_grid(target).astype(int).tolist(),
        }
        for source, target in train
    ]
    return _sric_json_hash(payload)


def _sric_runtime_code_hash() -> str:
    """Bind receipts to the executable interpreter contract, not AST text alone."""
    try:
        module_sha256 = hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
    except (OSError, TypeError):
        module_sha256 = None
    sources: Dict[str, str] = {}
    for value in (
        SRICRelationalSchema,
        _sric_schema_from_ast,
        _sric_unique_anchor,
        _sric_select_relation,
        sric_apply_relational_schema,
    ):
        name = getattr(value, "__name__", type(value).__name__)
        try:
            sources[name] = inspect.getsource(value)
        except (OSError, TypeError):
            sources[name] = f"unavailable:{name}"
    return _sric_json_hash(
        {
            "semantics_version": _SRIC_RUNTIME_SEMANTICS_VERSION,
            "solver_version": SOLVER_VERSION,
            "module_sha256": module_sha256,
            "sources": sources,
        }
    )


def _sric_witness_groups(
    train: List[Tuple[Array, Array]],
) -> List[Tuple[str, Tuple[int, ...]]]:
    """Group identical examples so copies cannot masquerade as witnesses."""
    grouped: Dict[str, List[int]] = {}
    for index, (source, target) in enumerate(train):
        grouped.setdefault(_sric_example_hash(source, target), []).append(index)
    return [(pair_hash, tuple(indices)) for pair_hash, indices in grouped.items()]


def _sric_candidate_submission_hash(candidate: RuleCandidate) -> str:
    metadata = candidate.metadata if isinstance(candidate.metadata, dict) else {}
    return _sric_json_hash(
        {
            "name": str(candidate.name),
            "family": str(candidate.family),
            "complexity": int(candidate.complexity),
            "declared_train_error": int(candidate.train_error),
            "program_ast": metadata.get("sric_program_ast"),
            "declared_program_hash": metadata.get("sric_program_hash"),
            "stored_train_prediction_hashes": [
                _sric_grid_hash(grid) for grid in candidate.train_grids
            ],
            "stored_test_prediction_hashes": [
                _sric_grid_hash(grid) for grid in candidate.grids
            ],
        }
    )


def _sric_seal_candidate(
    candidate: RuleCandidate,
    train: List[Tuple[Array, Array]],
    tests: List[Array],
    runtime_code_hash: str,
) -> Dict[str, object]:
    """Canonicalize and deep-copy a proposed artifact before any witness run."""
    reasons: List[str] = []
    metadata: Dict[str, object]
    if not isinstance(candidate.metadata, dict):
        metadata = {}
        reasons.append("candidate metadata is not a mapping")
    else:
        try:
            metadata = json.loads(json.dumps(candidate.metadata, sort_keys=True))
        except (TypeError, ValueError):
            metadata = {}
            reasons.append("candidate metadata is not canonical JSON")
    if candidate.family != "sric_relational_separator":
        reasons.append("candidate family is not SRIC relational separator")
    if isinstance(candidate.train_error, bool) or int(candidate.train_error) != 0:
        reasons.append("candidate declares nonzero training error")
    schema: Optional[SRICRelationalSchema] = None
    try:
        schema = _sric_schema_from_ast(metadata.get("sric_program_ast"))
    except (TypeError, ValueError) as exc:
        reasons.append(f"invalid program AST: {exc}")
    program_hash = schema.program_hash() if schema is not None else ""
    if str(metadata.get("sric_program_hash", "")) != program_hash:
        reasons.append("declared program hash does not match canonical AST")
    if metadata.get("sric_repair") is not True:
        reasons.append("missing SRIC repair marker")
    if len(candidate.train_grids) != len(train):
        reasons.append("stored training prediction count mismatch")
    if len(candidate.grids) != len(tests):
        reasons.append("stored test prediction count mismatch")
    submission_hash = _sric_candidate_submission_hash(candidate)
    sealed_body = {
        "schema": "sric.arc.sealed-candidate.v2",
        "solver_version": SOLVER_VERSION,
        "runtime_code_hash": runtime_code_hash,
        "candidate_submission_hash": submission_hash,
        "name": str(candidate.name),
        "family": str(candidate.family),
        "complexity": int(candidate.complexity),
        "program_ast": None if schema is None else schema.program_ast(),
        "program_hash": program_hash,
        "train_input_hashes": [_sric_grid_hash(source) for source, _ in train],
        "train_target_hashes": [_sric_grid_hash(target) for _, target in train],
        "test_input_hashes": [_sric_grid_hash(test) for test in tests],
    }
    return {
        "candidate": candidate,
        "metadata": metadata,
        "schema_object": schema,
        "program_hash": program_hash,
        "submission_hash": submission_hash,
        "sealed_body": sealed_body,
        "sealed_hash": _sric_json_hash(sealed_body),
        "rejection_reasons": reasons,
    }


def _sric_execute_sealed_candidate(
    sealed: Dict[str, object],
    train: List[Tuple[Array, Array]],
    tests: List[Array],
) -> Dict[str, object]:
    """Re-execute a sealed AST and reject every stored-grid inconsistency."""
    reasons = list(sealed.get("rejection_reasons", []))
    candidate = sealed.get("candidate")
    schema = sealed.get("schema_object")
    if not isinstance(candidate, RuleCandidate) or not isinstance(schema, SRICRelationalSchema):
        return {**sealed, "rejection_reasons": reasons, "executed": False}
    try:
        train_predictions = tuple(
            sric_apply_relational_schema(source, schema) for source, _ in train
        )
        test_predictions = tuple(
            sric_apply_relational_schema(test, schema) for test in tests
        )
    except (ValueError, IndexError, KeyError) as exc:
        reasons.append(f"sealed program execution failed: {exc}")
        return {**sealed, "rejection_reasons": reasons, "executed": False}
    if not all(
        exact(prediction, target)
        for prediction, (_, target) in zip(train_predictions, train)
    ):
        reasons.append("re-executed program does not fit every demonstration")
    if len(candidate.train_grids) == len(train_predictions) and not all(
        exact(stored, regenerated)
        for stored, regenerated in zip(candidate.train_grids, train_predictions)
    ):
        reasons.append("stored training grids differ from sealed execution")
    if len(candidate.grids) == len(test_predictions) and not all(
        exact(stored, regenerated)
        for stored, regenerated in zip(candidate.grids, test_predictions)
    ):
        reasons.append("stored test grids differ from sealed execution")
    artifact_body = {
        **dict(sealed["sealed_body"]),
        "sealed_hash": str(sealed["sealed_hash"]),
        "train_prediction_hashes": [
            _sric_grid_hash(prediction) for prediction in train_predictions
        ],
        "test_prediction_hashes": [
            _sric_grid_hash(prediction) for prediction in test_predictions
        ],
    }
    return {
        **sealed,
        "rejection_reasons": reasons,
        "executed": True,
        "train_predictions": train_predictions,
        "test_predictions": test_predictions,
        "artifact_body": artifact_body,
        "artifact_hash": _sric_json_hash(artifact_body),
    }


def sric_certify_relational_challengers(
    candidates: Sequence[RuleCandidate],
    train: List[Tuple[Array, Array]],
    tests: Optional[List[Array]] = None,
) -> Tuple[List[RuleCandidate], Dict[str, object]]:
    if tests is None:
        if any(candidate.grids for candidate in candidates):
            raise ValueError(
                "test inputs are required to certify candidates with test predictions"
            )
        tests = []
    return sric_certify_relational_challengers_for_tests(candidates, train, tests)


def sric_certify_relational_challengers_for_tests(
    candidates: Sequence[RuleCandidate],
    train: List[Tuple[Array, Array]],
    tests: List[Array],
    *,
    maximum_schema_checks: int = _SRIC_MAX_SCHEMA_CHECKS,
    maximum_scene_units: int = _SRIC_MAX_SCENE_UNITS,
) -> Tuple[List[RuleCandidate], Dict[str, object]]:
    """Seal, re-execute, and group-LOO certify relational challengers."""
    if not candidates:
        empty_body = {
            "schema": "sric.arc.receipt-envelope.v2",
            "candidate_count": 0,
            "receipt_count": 0,
            "candidate_set_hash": _sric_json_hash([]),
            "head_hash": None,
            "maximum_schema_checks": int(maximum_schema_checks),
            "maximum_scene_units": int(maximum_scene_units),
            "receipts": [],
        }
        return [], {**empty_body, "envelope_hash": _sric_json_hash(empty_body)}

    runtime_code_hash = _sric_runtime_code_hash()
    # PREPARED -> SEALED: every candidate is canonicalized and hashed before
    # any group-held-out target is used.
    sealed_candidates = [
        _sric_seal_candidate(candidate, train, tests, runtime_code_hash)
        for candidate in sorted(candidates, key=lambda item: (item.complexity, item.name))
    ]
    candidate_set_hash = _sric_json_hash(
        [str(sealed["submission_hash"]) for sealed in sealed_candidates]
    )

    witness_groups = _sric_witness_groups(train)
    fold_maps: List[Dict[str, List[SRICRelationalSchema]]] = []
    for _, witness_indices in witness_groups:
        excluded = set(witness_indices)
        construction = [pair for index, pair in enumerate(train) if index not in excluded]
        if not construction:
            fold_maps.append({})
            continue
        witness_input = train[witness_indices[0]][0]
        proposals = sric_relational_separator_rules(
            construction,
            [witness_input],
            maximum_schema_checks=maximum_schema_checks,
            maximum_scene_units=maximum_scene_units,
        )
        by_hash: Dict[str, List[SRICRelationalSchema]] = defaultdict(list)
        for proposal in proposals:
            metadata = proposal.metadata if isinstance(proposal.metadata, dict) else {}
            try:
                schema = _sric_schema_from_ast(metadata.get("sric_program_ast"))
            except (TypeError, ValueError):
                continue
            if str(metadata.get("sric_program_hash", "")) == schema.program_hash():
                by_hash[schema.program_hash()].append(schema)
        fold_maps.append(dict(by_hash))

    task_hash = _sric_task_witness_hash(train)
    accepted: List[RuleCandidate] = []
    receipts: List[Dict[str, object]] = []
    previous_receipt_hash: Optional[str] = None
    for sealed in sealed_candidates:
        executed = _sric_execute_sealed_candidate(sealed, train, tests)
        candidate = executed["candidate"]
        assert isinstance(candidate, RuleCandidate)
        metadata = dict(executed.get("metadata", {}))
        schema = executed.get("schema_object")
        program_hash = str(executed.get("program_hash", ""))
        fold_records: List[Dict[str, object]] = []
        successes = failures = abstentions = 0
        for group_index, (pair_hash, witness_indices) in enumerate(witness_groups):
            witness_input, witness_target = train[witness_indices[0]]
            matches = fold_maps[group_index].get(program_hash, [])
            predictions: Dict[str, Array] = {}
            for match_schema in matches:
                try:
                    prediction = sric_apply_relational_schema(witness_input, match_schema)
                except (ValueError, IndexError, KeyError):
                    continue
                predictions[canonical(prediction)] = prediction
            if not isinstance(schema, SRICRelationalSchema) or not matches or not predictions:
                outcome = "ABSTAIN"
                abstentions += 1
                prediction_hash = None
            elif len(predictions) != 1:
                outcome = "FAIL_AMBIGUOUS"
                failures += 1
                prediction_hash = _sric_json_hash(sorted(predictions.keys()))
            else:
                prediction = next(iter(predictions.values()))
                prediction_hash = _sric_grid_hash(prediction)
                if exact(prediction, witness_target):
                    outcome = "PASS"
                    successes += 1
                else:
                    outcome = "FAIL"
                    failures += 1
            fold_records.append(
                {
                    "witness_group_index": int(group_index),
                    "witness_indices": [int(index) for index in witness_indices],
                    "witness_pair_hash": pair_hash,
                    "input_hash": _sric_grid_hash(witness_input),
                    "outcome": outcome,
                    "prediction_hash": prediction_hash,
                    "target_hash": _sric_grid_hash(witness_target),
                }
            )
        full_coverage = successes + failures == len(witness_groups)
        reasons = list(executed.get("rejection_reasons", []))
        if len(witness_groups) < 2:
            reasons.append("fewer than two distinct witness groups")
        if not full_coverage:
            reasons.append("witness coverage incomplete")
        if failures:
            reasons.append("held-out witness failure")
        commit = not reasons
        receipt_body: Dict[str, object] = {
            "schema": "sric.arc.transaction.v2",
            "phase_trace": [
                "PREPARED",
                "SEALED",
                "EXECUTED",
                "REVEALED",
                "DECIDED",
                "FINALIZED",
            ],
            "parent_solver_version": SOLVER_VERSION,
            "runtime_semantics_version": _SRIC_RUNTIME_SEMANTICS_VERSION,
            "runtime_code_hash": runtime_code_hash,
            "task_witness_hash": task_hash,
            "candidate_set_hash": candidate_set_hash,
            "candidate_submission_hash": str(executed["submission_hash"]),
            "sealed_candidate_hash": str(executed["sealed_hash"]),
            "candidate_artifact_hash": executed.get("artifact_hash"),
            "program_ast": None if not isinstance(schema, SRICRelationalSchema) else schema.program_ast(),
            "candidate_program_hash": program_hash,
            "previous_receipt_hash": previous_receipt_hash,
            "train_input_hashes": [_sric_grid_hash(source) for source, _ in train],
            "train_target_hashes": [_sric_grid_hash(target) for _, target in train],
            "train_prediction_hashes": [
                _sric_grid_hash(prediction)
                for prediction in executed.get("train_predictions", ())
            ],
            "test_input_hashes": [_sric_grid_hash(test) for test in tests],
            "test_prediction_hashes": [
                _sric_grid_hash(prediction)
                for prediction in executed.get("test_predictions", ())
            ],
            "folds": fold_records,
            "raw_witness_rows": int(len(train)),
            "distinct_witness_groups": int(len(witness_groups)),
            "successes": int(successes),
            "failures": int(failures),
            "abstentions": int(abstentions),
            "full_witness_coverage": bool(full_coverage),
            "decision": "COMMIT" if commit else "QUARANTINE",
            "rejection_reasons": reasons,
        }
        receipt_hash = _sric_json_hash(receipt_body)
        receipt = {**receipt_body, "receipt_hash": receipt_hash}
        previous_receipt_hash = receipt_hash
        receipts.append(receipt)
        if commit:
            regenerated_train = tuple(
                prediction.copy() for prediction in executed.get("train_predictions", ())
            )
            regenerated_tests = [
                prediction.copy() for prediction in executed.get("test_predictions", ())
            ]
            metadata["sric_receipt_hash"] = receipt_hash
            metadata["sric_candidate_artifact_hash"] = executed.get("artifact_hash")
            accepted.append(
                RuleCandidate(
                    name=str(candidate.name),
                    grids=regenerated_tests,
                    train_error=0,
                    complexity=int(candidate.complexity),
                    family="sric_relational_separator",
                    train_grids=regenerated_train,
                    metadata=metadata,
                )
            )
    envelope_body: Dict[str, object] = {
        "schema": "sric.arc.receipt-envelope.v2",
        "candidate_count": int(len(sealed_candidates)),
        "receipt_count": int(len(receipts)),
        "candidate_set_hash": candidate_set_hash,
        "head_hash": previous_receipt_hash,
        "maximum_schema_checks": int(maximum_schema_checks),
        "maximum_scene_units": int(maximum_scene_units),
        "receipts": receipts,
    }
    envelope = {**envelope_body, "envelope_hash": _sric_json_hash(envelope_body)}
    return accepted, envelope


def sric_verify_receipt_envelope(
    accepted: Sequence[RuleCandidate],
    envelope: Dict[str, object],
    train: List[Tuple[Array, Array]],
    tests: List[Array],
    *,
    expected_maximum_schema_checks: int = _SRIC_MAX_SCHEMA_CHECKS,
    expected_maximum_scene_units: int = _SRIC_MAX_SCENE_UNITS,
) -> Tuple[bool, List[str]]:
    """Verify chain completeness and re-execute every committed artifact."""
    errors: List[str] = []
    if not isinstance(envelope, dict) or envelope.get("schema") != "sric.arc.receipt-envelope.v2":
        return False, ["invalid receipt envelope schema"]
    receipts = envelope.get("receipts")
    if not isinstance(receipts, list):
        return False, ["receipt envelope has no receipt list"]
    body = {key: value for key, value in envelope.items() if key != "envelope_hash"}
    if envelope.get("envelope_hash") != _sric_json_hash(body):
        errors.append("receipt envelope hash mismatch")
    if int(envelope.get("receipt_count", -1)) != len(receipts):
        errors.append("receipt count mismatch")
    if int(envelope.get("candidate_count", -1)) != len(receipts):
        errors.append("candidate/receipt count mismatch")
    expected_maximum_schema_checks = max(
        0,
        min(int(expected_maximum_schema_checks), _SRIC_MAX_SCHEMA_CHECKS),
    )
    expected_maximum_scene_units = max(1, int(expected_maximum_scene_units))
    if envelope.get("maximum_schema_checks") != expected_maximum_schema_checks:
        errors.append("receipt schema-check cap differs from trusted execution policy")
    if envelope.get("maximum_scene_units") != expected_maximum_scene_units:
        errors.append("receipt scene-unit cap differs from trusted execution policy")
    previous: Optional[str] = None
    committed_by_artifact: Dict[str, Dict[str, object]] = {}
    submission_hashes: List[str] = []
    for receipt in receipts:
        if not isinstance(receipt, dict):
            errors.append("non-mapping receipt")
            continue
        receipt_body = {key: value for key, value in receipt.items() if key != "receipt_hash"}
        receipt_hash = _sric_json_hash(receipt_body)
        if receipt.get("receipt_hash") != receipt_hash:
            errors.append("receipt hash mismatch")
        if receipt.get("previous_receipt_hash") != previous:
            errors.append("receipt chain link mismatch")
        previous = str(receipt.get("receipt_hash"))
        submission_hashes.append(str(receipt.get("candidate_submission_hash", "")))
        if receipt.get("decision") == "COMMIT":
            artifact_hash = str(receipt.get("candidate_artifact_hash", ""))
            if not artifact_hash:
                errors.append("committed receipt lacks an artifact hash")
            committed_by_artifact[artifact_hash] = receipt
    if envelope.get("head_hash") != previous:
        errors.append("receipt head mismatch")
    if envelope.get("candidate_set_hash") != _sric_json_hash(submission_hashes):
        errors.append("candidate set hash mismatch")
    try:
        expected_proposals = sric_relational_separator_rules(
            train,
            tests,
            maximum_schema_checks=expected_maximum_schema_checks,
            maximum_scene_units=expected_maximum_scene_units,
        )
        expected_proposals = sorted(
            expected_proposals,
            key=lambda candidate: (candidate.complexity, candidate.name),
        )
        expected_submission_hashes = [
            _sric_candidate_submission_hash(candidate)
            for candidate in expected_proposals
        ]
        if int(envelope.get("candidate_count", -1)) != len(expected_proposals):
            errors.append("reconstructed candidate count mismatch")
        if envelope.get("candidate_set_hash") != _sric_json_hash(
            expected_submission_hashes
        ):
            errors.append("reconstructed candidate set hash mismatch")
        _, reconstructed_envelope = sric_certify_relational_challengers_for_tests(
            expected_proposals,
            train,
            tests,
            maximum_schema_checks=expected_maximum_schema_checks,
            maximum_scene_units=expected_maximum_scene_units,
        )
        if envelope != reconstructed_envelope:
            errors.append("reconstructed receipt envelope mismatch")
    except Exception as exc:
        errors.append(
            f"candidate-set reconstruction failed: {type(exc).__name__}: {exc}"
        )
    if len(accepted) != len(committed_by_artifact):
        errors.append("accepted artifact count mismatch")
    runtime_code_hash = _sric_runtime_code_hash()
    accepted_artifact_hashes: List[str] = []
    for candidate in accepted:
        sealed = _sric_seal_candidate(candidate, train, tests, runtime_code_hash)
        executed = _sric_execute_sealed_candidate(sealed, train, tests)
        reasons = list(executed.get("rejection_reasons", []))
        if reasons:
            errors.append("accepted artifact failed re-execution: " + "; ".join(reasons))
            continue
        artifact_hash = str(executed.get("artifact_hash", ""))
        accepted_artifact_hashes.append(artifact_hash)
        receipt = committed_by_artifact.get(artifact_hash)
        if receipt is None:
            errors.append("accepted artifact is not bound to a committed receipt")
            continue
        metadata = candidate.metadata if isinstance(candidate.metadata, dict) else {}
        if metadata.get("sric_candidate_artifact_hash") != artifact_hash:
            errors.append("accepted artifact metadata digest mismatch")
        if metadata.get("sric_receipt_hash") != receipt.get("receipt_hash"):
            errors.append("accepted artifact receipt link mismatch")
        if receipt.get("runtime_code_hash") != runtime_code_hash:
            errors.append("committed artifact runtime hash mismatch")
        if receipt.get("train_prediction_hashes") != [
            _sric_grid_hash(prediction)
            for prediction in executed.get("train_predictions", ())
        ]:
            errors.append("committed training prediction digest mismatch")
        if receipt.get("test_prediction_hashes") != [
            _sric_grid_hash(prediction)
            for prediction in executed.get("test_predictions", ())
        ]:
            errors.append("committed test prediction digest mismatch")
    committed_artifact_hashes = list(committed_by_artifact)
    if len(set(accepted_artifact_hashes)) != len(accepted_artifact_hashes):
        errors.append("accepted artifact set contains duplicates")
    if set(accepted_artifact_hashes) != set(committed_artifact_hashes):
        errors.append("accepted artifact set does not match committed receipts")
    if accepted_artifact_hashes != committed_artifact_hashes:
        errors.append("accepted artifact order does not match committed receipts")
    return not errors, errors


def sric_relational_challenger_lane(
    train: List[Tuple[Array, Array]],
    tests: List[Array],
    *,
    maximum_schema_checks: int = _SRIC_MAX_SCHEMA_CHECKS,
    maximum_scene_units: int = _SRIC_MAX_SCENE_UNITS,
    maximum_witness_groups: int = _SRIC_MAX_WITNESS_GROUPS,
) -> Tuple[List[Optional[Array]], Dict[str, object]]:
    """Return only uniquely witnessed challenger outputs; otherwise abstain."""
    distinct_witness_groups = len(_sric_witness_groups(train))
    if distinct_witness_groups > int(maximum_witness_groups):
        return [None for _ in tests], {
            "lane": "sric_relational_challenger",
            "status": "RESOURCE_ABSTAIN",
            "reason": "distinct witness group cap exceeded",
            "distinct_witness_groups": int(distinct_witness_groups),
            "maximum_witness_groups": int(maximum_witness_groups),
            "proposed_candidates": 0,
            "committed_candidates": 0,
            "quarantined_candidates": 0,
            "receipt_envelope": None,
            "receipt_verification": {"valid": True, "errors": []},
            "schema_check_cap": int(maximum_schema_checks),
            "scene_unit_cap": int(maximum_scene_units),
            "outputs": [
                {
                    "test_index": int(index),
                    "status": "RESOURCE_ABSTAIN",
                    "distinct_committed_outputs": 0,
                }
                for index in range(len(tests))
            ],
        }
    if len(tests) > 1:
        combined_outputs: List[Optional[Array]] = []
        combined_records: List[Dict[str, object]] = []
        per_test_lanes: List[Dict[str, object]] = []
        for test_index, test in enumerate(tests):
            single_outputs, single_lane = sric_relational_challenger_lane(
                train,
                [test],
                maximum_schema_checks=maximum_schema_checks,
                maximum_scene_units=maximum_scene_units,
                maximum_witness_groups=maximum_witness_groups,
            )
            combined_outputs.append(single_outputs[0] if single_outputs else None)
            output_record = dict((single_lane.get("outputs") or [{}])[0])
            output_record["test_index"] = int(test_index)
            combined_records.append(output_record)
            per_test_lanes.append(single_lane)
        verification_errors = [
            str(error)
            for lane in per_test_lanes
            for error in (lane.get("receipt_verification") or {}).get("errors", [])
        ]
        return combined_outputs, {
            "lane": "sric_relational_challenger",
            "status": "PER_TEST_CERTIFIED",
            "test_isolation_contract": True,
            "proposed_candidates": int(
                sum(int(lane.get("proposed_candidates", 0)) for lane in per_test_lanes)
            ),
            "committed_candidates": int(
                sum(int(lane.get("committed_candidates", 0)) for lane in per_test_lanes)
            ),
            "quarantined_candidates": int(
                sum(int(lane.get("quarantined_candidates", 0)) for lane in per_test_lanes)
            ),
            "receipt_envelope": None,
            "receipt_envelopes": [lane.get("receipt_envelope") for lane in per_test_lanes],
            "receipt_verification": {
                "valid": not verification_errors,
                "errors": verification_errors,
            },
            "schema_check_cap": int(maximum_schema_checks),
            "scene_unit_cap": int(maximum_scene_units),
            "distinct_witness_groups": int(distinct_witness_groups),
            "maximum_witness_groups": int(maximum_witness_groups),
            "outputs": combined_records,
        }
    proposed = sric_relational_separator_rules(
        train,
        tests,
        maximum_schema_checks=maximum_schema_checks,
        maximum_scene_units=maximum_scene_units,
    )
    accepted, envelope = sric_certify_relational_challengers_for_tests(
        proposed,
        train,
        tests,
        maximum_schema_checks=maximum_schema_checks,
        maximum_scene_units=maximum_scene_units,
    )
    verified, verification_errors = sric_verify_receipt_envelope(
        accepted,
        envelope,
        train,
        tests,
        expected_maximum_schema_checks=maximum_schema_checks,
        expected_maximum_scene_units=maximum_scene_units,
    )
    if not verified:
        accepted = []
    outputs: List[Optional[Array]] = []
    output_records: List[Dict[str, object]] = []
    for test_index in range(len(tests)):
        groups: Dict[str, List[RuleCandidate]] = defaultdict(list)
        for candidate in accepted:
            if test_index < len(candidate.grids):
                groups[canonical(candidate.grids[test_index])].append(candidate)
        if len(groups) == 1:
            supporting = next(iter(groups.values()))
            output = supporting[0].grids[test_index].copy()
            outputs.append(output)
            output_records.append(
                {
                    "test_index": int(test_index),
                    "status": "UNIQUE_COMMITTED_OUTPUT",
                    "output_hash": _sric_json_hash(output.astype(int).tolist()),
                    "families": sorted({candidate.family for candidate in supporting}),
                    "names": [candidate.name for candidate in supporting],
                    "program_hashes": [
                        str((candidate.metadata or {}).get("sric_program_hash", ""))
                        for candidate in supporting
                    ],
                    "candidate_metadata": [dict(candidate.metadata or {}) for candidate in supporting],
                }
            )
        else:
            outputs.append(None)
            output_records.append(
                {
                    "test_index": int(test_index),
                    "status": "ABSTAIN" if not groups else "UNRESOLVED_DISAGREEMENT",
                    "distinct_committed_outputs": int(len(groups)),
                }
            )
    return outputs, {
        "lane": "sric_relational_challenger",
        "proposed_candidates": int(len(proposed)),
        "committed_candidates": int(len(accepted)),
        "quarantined_candidates": int(len(proposed) - len(accepted)),
        "receipt_envelope": envelope,
        "receipt_verification": {
            "valid": bool(verified),
            "errors": verification_errors,
        },
        "schema_check_cap": int(maximum_schema_checks),
        "scene_unit_cap": int(maximum_scene_units),
        "distinct_witness_groups": int(distinct_witness_groups),
        "maximum_witness_groups": int(maximum_witness_groups),
        "outputs": output_records,
    }


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



# ---------------- object scene algebra and serialization channel ----------------


def _scene_panel_pairs(grid: Array) -> List[Tuple[str, Array, Array]]:
    """Return exact two-panel decompositions without discarding orientation.

    ARC panels may be separated by a uniform line or may occupy two equal
    halves without an explicit separator.  The returned modes are stable and
    can therefore be learned from demonstrations and replayed on a test grid.
    """
    grid = sanitize_grid(grid)
    pairs: List[Tuple[str, Array, Array]] = []
    explicit = split_equal_panels(grid)
    if explicit is not None:
        pairs.append(("explicit", explicit[0], explicit[1]))
    height, width = grid.shape
    if width % 2 == 0:
        pairs.append(("implicit_lr", grid[:, : width // 2].copy(), grid[:, width // 2 :].copy()))
    if height % 2 == 0:
        pairs.append(("implicit_tb", grid[: height // 2, :].copy(), grid[height // 2 :, :].copy()))
    uniform = split_uniform_panels(grid)
    if len(uniform) == 2 and uniform[0].shape == uniform[1].shape:
        pairs.append(("uniform_two", uniform[0], uniform[1]))
    output: List[Tuple[str, Array, Array]] = []
    seen: set[Tuple[Tuple[int, int], bytes, bytes]] = set()
    for mode, first, second in pairs:
        key = (first.shape, first.tobytes(), second.tobytes())
        if key not in seen:
            seen.add(key)
            output.append((mode, first, second))
    return output


def _scene_panel_pair(grid: Array, mode: str) -> Tuple[Array, Array]:
    for candidate_mode, first, second in _scene_panel_pairs(grid):
        if candidate_mode == mode:
            return first, second
    raise ValueError(f"panel decomposition {mode!r} is unavailable")


def scene_panel_algebra_rules(
    train: List[Tuple[Array, Array]], tests: List[Array]
) -> List[RuleCandidate]:
    """Learn a finite cellwise algebra between two aligned scene panels.

    Three typed feature systems are tried.  ``direct`` preserves literal color
    pairs, ``support`` retains only foreground occupancy, and ``role`` records
    background/equality relations.  A map is admitted only when it reproduces
    every demonstration cell exactly.
    """
    output: List[RuleCandidate] = []
    if not train:
        return output
    modes = sorted(
        set.intersection(
            *[
                {mode for mode, _, _ in _scene_panel_pairs(source)}
                for source, _ in train
            ]
        )
    )
    for mode in modes:
        for feature_mode in ("direct", "support", "role"):
            mapping: Dict[Tuple[object, ...], int] = {}
            valid = True
            for source, target in train:
                first, second = _scene_panel_pair(source, mode)
                if target.shape != first.shape:
                    valid = False
                    break
                first_background = infer_bg(first)
                second_background = infer_bg(second)
                for first_value, second_value, target_value in zip(
                    first.ravel(), second.ravel(), target.ravel()
                ):
                    left = int(first_value)
                    right = int(second_value)
                    if feature_mode == "direct":
                        key: Tuple[object, ...] = (left, right)
                    elif feature_mode == "support":
                        key = (left != first_background, right != second_background)
                    else:
                        key = (
                            left == first_background,
                            right == second_background,
                            left == right,
                        )
                    value = int(target_value)
                    if key in mapping and mapping[key] != value:
                        valid = False
                        break
                    mapping[key] = value
                if not valid:
                    break
            if not valid or not mapping:
                continue

            def apply(
                grid: Array,
                panel_mode: str = mode,
                descriptor_mode: str = feature_mode,
                learned_mapping: Dict[Tuple[object, ...], int] = dict(mapping),
            ) -> Array:
                first, second = _scene_panel_pair(grid, panel_mode)
                first_background = infer_bg(first)
                second_background = infer_bg(second)
                result = np.empty_like(first)
                for index, (first_value, second_value) in enumerate(
                    zip(first.ravel(), second.ravel())
                ):
                    left = int(first_value)
                    right = int(second_value)
                    if descriptor_mode == "direct":
                        key: Tuple[object, ...] = (left, right)
                    elif descriptor_mode == "support":
                        key = (left != first_background, right != second_background)
                    else:
                        key = (
                            left == first_background,
                            right == second_background,
                            left == right,
                        )
                    if key not in learned_mapping:
                        raise ValueError("unseen aligned panel relation")
                    result.ravel()[index] = int(learned_mapping[key])
                return result

            _try_exact_rule(
                output,
                train,
                tests,
                f"scene_panel_{mode}_{feature_mode}",
                apply,
                7 + len(mapping),
                "scene_panel_algebra",
                metadata={
                    "scene_block": "panel_algebra",
                    "panel_mode": mode,
                    "feature_mode": feature_mode,
                    "mapping_size": len(mapping),
                    "exact_demonstration_contract": True,
                },
            )
    return output


def _scene_marker_selected_crop(
    grid: Array,
    marker_color_value: int,
    connectivity: int,
    separate_colors: bool,
    masked: bool,
    metric: str,
) -> Array:
    grid = sanitize_grid(grid)
    marker_locations = np.argwhere(grid == int(marker_color_value))
    if len(marker_locations) != 1:
        raise ValueError("the marker must be a singleton")
    marker_row, marker_column = (int(value) for value in marker_locations[0])
    background = infer_bg(grid)
    scene = grid.copy()
    scene[marker_row, marker_column] = background
    objects = generic_components(scene, connectivity, separate_colors)
    if not objects:
        raise ValueError("no object remains after marker removal")

    def distance(obj: Obj) -> int:
        if metric == "manhattan":
            return min(
                abs(row - marker_row) + abs(column - marker_column)
                for row, column in obj.cells
            )
        if metric == "chebyshev":
            return min(
                max(abs(row - marker_row), abs(column - marker_column))
                for row, column in obj.cells
            )
        top, left, bottom, right = obj.bbox
        row_distance = 0 if top <= marker_row <= bottom else min(
            abs(marker_row - top), abs(marker_row - bottom)
        )
        column_distance = 0 if left <= marker_column <= right else min(
            abs(marker_column - left), abs(marker_column - right)
        )
        return row_distance + column_distance

    distances = [distance(obj) for obj in objects]
    best = min(distances)
    selected = [obj for obj, value in zip(objects, distances) if value == best]
    if len(selected) != 1:
        raise ValueError("marker does not select one object")
    obj = selected[0]
    top, left, bottom, right = obj.bbox
    crop = scene[top : bottom + 1, left : right + 1].copy()
    if masked:
        keep = np.zeros(crop.shape, dtype=bool)
        for row, column in obj.cells:
            keep[row - top, column - left] = True
        crop = np.where(keep, crop, background).astype(np.int16)
    return crop


def scene_marker_extraction_rules(
    train: List[Tuple[Array, Array]], tests: List[Array]
) -> List[RuleCandidate]:
    output: List[RuleCandidate] = []
    if not train:
        return output
    singleton_sets = []
    for source, _ in train:
        counts = Counter(int(value) for value in source.ravel())
        singleton_sets.append({color for color, count in counts.items() if count == 1})
    marker_colors = sorted(set.intersection(*singleton_sets)) if singleton_sets else []
    for marker in marker_colors:
        for connectivity in (4, 8):
            for separate_colors in (True, False):
                for masked in (True, False):
                    for metric in ("manhattan", "chebyshev", "bbox"):
                        _try_exact_rule(
                            output,
                            train,
                            tests,
                            f"scene_marker_crop_{marker}_c{connectivity}_{int(separate_colors)}_"
                            f"{int(masked)}_{metric}",
                            lambda grid, marker_value=marker, conn=connectivity, separate=separate_colors,
                            use_mask=masked, distance_metric=metric: _scene_marker_selected_crop(
                                grid,
                                marker_value,
                                conn,
                                separate,
                                use_mask,
                                distance_metric,
                            ),
                            9,
                            "scene_marker_extraction",
                            metadata={
                                "scene_block": "marker_guided_extraction",
                                "marker_color": marker,
                                "connectivity": connectivity,
                                "separate_colors": separate_colors,
                                "masked": masked,
                                "metric": metric,
                                "exact_demonstration_contract": True,
                            },
                        )
    return output


def _scene_cell_orders(shape: Tuple[int, int]) -> Dict[str, List[Tuple[int, int]]]:
    height, width = shape
    coordinates = [(row, column) for row in range(height) for column in range(width)]
    result: Dict[str, List[Tuple[int, int]]] = {
        "row": coordinates,
        "column": [(row, column) for column in range(width) for row in range(height)],
        "diagonal": sorted(coordinates, key=lambda point: (sum(point), point[0], point[1])),
        "main_diagonal_first": sorted(
            coordinates,
            key=lambda point: (
                0 if point[0] == point[1] else 1,
                sum(point),
                point[0],
                point[1],
            ),
        ),
        "anti_diagonal_first": sorted(
            coordinates,
            key=lambda point: (
                0 if point[0] + point[1] == width - 1 else 1,
                sum(point),
                point[0],
                point[1],
            ),
        ),
    }
    if height == width:
        dice = [
            (0, 0),
            (0, width - 1),
            (height // 2, width // 2),
            (height - 1, 0),
            (height - 1, width - 1),
        ]
        result["dice"] = dice + [point for point in coordinates if point not in dice]
    return result


def _scene_render_prefix(
    count: int,
    order: Sequence[Tuple[int, int]],
    multiplier: int,
    intercept: int,
    background: int,
    foreground: int,
    shape: Tuple[int, int],
) -> Array:
    active = multiplier * int(count) + intercept
    if active < 0 or active > len(order):
        raise ValueError("scene statistic exceeds serializer capacity")
    result = np.full(shape, int(background), dtype=np.int16)
    for row, column in order[:active]:
        result[row, column] = int(foreground)
    return result


def _scene_render_typed_line_glyph(
    glyph: str,
    background: int,
    foreground: int,
    shape: Tuple[int, int],
) -> Array:
    """Render a named line primitive without retaining a demonstration raster."""
    height, width = shape
    if height != width or height < 2:
        raise ValueError("typed line glyphs require a nontrivial square canvas")
    result = np.full(shape, int(background), dtype=np.int16)
    if glyph == "top_row":
        result[0, :] = int(foreground)
    elif glyph == "main_diagonal":
        for index in range(height):
            result[index, index] = int(foreground)
    elif glyph == "anti_diagonal":
        for index in range(height):
            result[index, width - 1 - index] = int(foreground)
    else:
        raise ValueError(f"unknown typed line glyph: {glyph}")
    return result


def _scene_distinct_color_glyph_rules(
    train: List[Tuple[Array, Array]],
    tests: List[Array],
    background: int,
    foreground: int,
    shape: Tuple[int, int],
) -> List[RuleCandidate]:
    """Compile distinct-color cardinality into a symbolic line-glyph code.

    This is intentionally stricter than a raster lookup: the grammar fixes the
    semantic schedule (one color -> top row, two -> main diagonal, three ->
    anti-diagonal); demonstrations only verify it.  All three named primitives
    must occur and predictions are freshly rendered from the held-out input.
    """
    semantic_schedule = {
        1: "top_row",
        2: "main_diagonal",
        3: "anti_diagonal",
    }
    glyph_names = tuple(semantic_schedule.values())
    if shape[0] != shape[1] or shape[0] < 2:
        return []
    if any(source.shape[0] != source.shape[1] for source, _ in train):
        return []
    if any(test.shape[0] != test.shape[1] for test in tests):
        return []
    templates = {
        glyph: _scene_render_typed_line_glyph(
            glyph, background, foreground, shape
        )
        for glyph in glyph_names
    }
    observed_scalars: List[int] = []
    for source, target in train:
        matches = [glyph for glyph, template in templates.items() if exact(target, template)]
        if len(matches) != 1:
            return []
        scalar = int(len(np.unique(source)))
        if scalar not in semantic_schedule or matches[0] != semantic_schedule[scalar]:
            return []
        observed_scalars.append(scalar)
    if set(observed_scalars) != set(semantic_schedule):
        return []
    scalar_support = Counter(observed_scalars)
    if sum(count >= 2 for count in scalar_support.values()) < 2:
        return []
    test_scalars = [int(len(np.unique(test))) for test in tests]
    if any(scalar not in scalar_support for scalar in test_scalars):
        return []

    fixed_schedule = dict(semantic_schedule)

    def apply(grid: Array) -> Array:
        scalar = int(len(np.unique(grid)))
        if scalar not in scalar_support:
            raise ValueError("unseen distinct-color cardinality")
        return _scene_render_typed_line_glyph(
            fixed_schedule[scalar], background, foreground, shape
        )

    result: List[RuleCandidate] = []
    _try_exact_rule(
        result,
        train,
        tests,
        "causal_distinct_color_typed_line_glyph",
        apply,
        10,
        "causal_scene_glyph",
        metadata={
            "compiler_block": "causal_quotient_provenance",
            "scene_block": "typed_scalar_glyph",
            "statistic": "distinct_color_cardinality",
            "renderer": "named_line_primitive",
            "symbolic_mapping": {
                str(key): value for key, value in sorted(fixed_schedule.items())
            },
            "schedule_origin": "fixed_typed_grammar",
            "class_support": {
                str(key): int(value) for key, value in sorted(scalar_support.items())
            },
            "provenance_kind": "test_input_semantic_scalar_renderer",
            "test_input_grounded": True,
            "permutation_invariant": True,
            "admissible": True,
            "partial_program": True,
            "undefined_when": [
                "output_is_not_a_unique_named_line_glyph",
                "demonstration_violates_fixed_semantic_schedule",
                "unseen_test_scalar",
            ],
            "exact_demonstration_contract": True,
        },
    )
    return result


def _scene_statistic_specs(
    train: List[Tuple[Array, Array]],
) -> List[Tuple[str, Callable[[Array], int]]]:
    specifications: List[Tuple[str, Callable[[Array], int]]] = []
    input_colors = sorted(
        {
            int(value)
            for source, _ in train
            for value in np.unique(source)
            if int(value) != infer_bg(source)
        }
    )
    for connectivity in (4, 8):
        for separate_colors in (True, False):
            specifications.extend(
                [
                    (
                        f"objects_c{connectivity}_{int(separate_colors)}",
                        lambda grid, conn=connectivity, separate=separate_colors: len(
                            generic_components(grid, conn, separate)
                        ),
                    ),
                    (
                        f"non_singletons_c{connectivity}_{int(separate_colors)}",
                        lambda grid, conn=connectivity, separate=separate_colors: sum(
                            obj.size > 1 for obj in generic_components(grid, conn, separate)
                        ),
                    ),
                    (
                        f"objects_with_holes_c{connectivity}_{int(separate_colors)}",
                        lambda grid, conn=connectivity, separate=separate_colors: sum(
                            object_hole_count(obj) > 0
                            for obj in generic_components(grid, conn, separate)
                        ),
                    ),
                ]
            )
            sizes = sorted(
                {
                    obj.size
                    for source, _ in train
                    for obj in generic_components(source, connectivity, separate_colors)
                }
            )[:8]
            for size in sizes:
                specifications.append(
                    (
                        f"size_{size}_c{connectivity}_{int(separate_colors)}",
                        lambda grid, target_size=size, conn=connectivity, separate=separate_colors: sum(
                            obj.size == target_size
                            for obj in generic_components(grid, conn, separate)
                        ),
                    )
                )
            signatures = Counter(
                object_mask_signature(obj)
                for source, _ in train
                for obj in generic_components(source, connectivity, separate_colors)
                if obj.size > 1
            )
            for signature_index, (signature, _) in enumerate(signatures.most_common(6)):
                specifications.append(
                    (
                        f"shape_{signature_index}_c{connectivity}_{int(separate_colors)}",
                        lambda grid, target_signature=signature, conn=connectivity,
                        separate=separate_colors: sum(
                            object_mask_signature(obj) == target_signature
                            for obj in generic_components(grid, conn, separate)
                            if obj.size > 1
                        ),
                    )
                )
    for color in input_colors[:8]:
        specifications.extend(
            [
                (f"color_cells_{color}", lambda grid, selected=color: int(np.sum(grid == selected))),
                (
                    f"color_objects_{color}",
                    lambda grid, selected=color: len(
                        components(
                            np.where(grid == selected, selected, infer_bg(grid)).astype(np.int16),
                            bg=infer_bg(grid),
                        )
                    ),
                ),
                (
                    f"color_non_singletons_{color}",
                    lambda grid, selected=color: sum(
                        obj.size > 1
                        for obj in components(
                            np.where(grid == selected, selected, infer_bg(grid)).astype(np.int16),
                            bg=infer_bg(grid),
                        )
                    ),
                ),
            ]
        )
    return specifications


def scene_statistic_serialization_rules(
    train: List[Tuple[Array, Array]], tests: List[Array]
) -> List[RuleCandidate]:
    """Serialize a scene statistic into a small exact output code.

    The channel is deliberately narrow.  Outputs must share one small shape,
    one background, and one foreground color.  The statistic is then rendered
    through a finite prefix order or a nested activation order learned from the
    demonstrations.  A direct lookup is retained as a lower-priority family
    only when at least two distinct statistic values occur, every statistic
    class has at least two exchangeable witnesses, and every test value was
    demonstrated.
    """
    output: List[RuleCandidate] = []
    if not train:
        return output
    targets = [target for _, target in train]
    if len({target.shape for target in targets}) != 1:
        return output
    shape = targets[0].shape
    if int(np.prod(shape)) > 81:
        return output
    backgrounds = [infer_bg(target) for target in targets]
    if len(set(backgrounds)) != 1:
        return output
    background = backgrounds[0]
    foreground_sets = [set(int(value) for value in np.unique(target)) - {background} for target in targets]
    if any(len(values) > 1 for values in foreground_sets):
        return output
    foreground_values = set().union(*foreground_sets)
    if len(foreground_values) != 1:
        return output
    foreground = next(iter(foreground_values))
    active_counts = [int(np.count_nonzero(target != background)) for target in targets]
    orders = _scene_cell_orders(shape)

    output.extend(
        _scene_distinct_color_glyph_rules(
            train, tests, background, foreground, shape
        )
    )

    for statistic_name, statistic in _scene_statistic_specs(train):
        try:
            train_values = [int(statistic(source)) for source, _ in train]
            test_values = [int(statistic(test)) for test in tests]
        except Exception:
            continue
        if len(set(train_values)) < 2:
            continue

        lookup: Dict[int, Array] = {}
        lookup_support = Counter(train_values)
        lookup_valid = True
        for value, target in zip(train_values, targets):
            if value in lookup and not exact(lookup[value], target):
                lookup_valid = False
                break
            lookup[value] = target.copy()
        if (
            lookup_valid
            and all(count >= 2 for count in lookup_support.values())
            and all(value in lookup for value in test_values)
        ):
            _try_exact_rule(
                output,
                train,
                tests,
                f"scene_stat_lookup_{statistic_name}",
                lambda grid, stat=statistic, table={key: value.copy() for key, value in lookup.items()}: (
                    table[int(stat(grid))].copy()
                    if int(stat(grid)) in table
                    else (_ for _ in ()).throw(ValueError("unseen scene statistic"))
                ),
                13 + len(lookup),
                "scene_statistic_lookup",
                metadata={
                    "compiler_block": "causal_quotient_provenance",
                    "scene_block": "statistic_serialization",
                    "statistic": statistic_name,
                    "serializer": "repeated_support_class_template",
                    "minimum_class_support": 2,
                    "class_support": {
                        str(key): int(value)
                        for key, value in sorted(lookup_support.items())
                    },
                    "provenance_kind": "held_out_input_keyed_equivalence_class_template",
                    "test_input_grounded": True,
                    "permutation_invariant": True,
                    "admissible": True,
                    "partial_program": True,
                    "undefined_when": [
                        "class_support_below_two",
                        "inconsistent_template_within_class",
                        "unseen_test_class",
                    ],
                    "exact_demonstration_contract": True,
                },
            )

        affine_counts = []
        for multiplier in range(0, 5):
            for intercept in range(-5, 6):
                if all(
                    multiplier * value + intercept == active
                    for value, active in zip(train_values, active_counts)
                ):
                    affine_counts.append((multiplier, intercept))
        for order_name, order in orders.items():
            for multiplier, intercept in affine_counts:
                if not all(
                    0 <= multiplier * value + intercept <= len(order)
                    for value in test_values
                ):
                    continue
                _try_exact_rule(
                    output,
                    train,
                    tests,
                    f"scene_count_{statistic_name}_{order_name}_{multiplier}_{intercept}",
                    lambda grid, stat=statistic, sequence=tuple(order), a=multiplier, b=intercept,
                    bg=background, fg=foreground, target_shape=shape: _scene_render_prefix(
                        int(stat(grid)), sequence, a, b, bg, fg, target_shape
                    ),
                    9,
                    "scene_count_serializer",
                    metadata={
                        "scene_block": "statistic_serialization",
                        "statistic": statistic_name,
                        "serializer": order_name,
                        "multiplier": multiplier,
                        "intercept": intercept,
                        "exact_demonstration_contract": True,
                    },
                )

        if active_counts == train_values:
            masks: Dict[int, Array] = {}
            nested_valid = True
            for value, target in zip(train_values, targets):
                mask = target != background
                if value in masks and not np.array_equal(masks[value], mask):
                    nested_valid = False
                    break
                masks[value] = mask
            unique_values = sorted(masks)
            if nested_valid and all(
                np.all(~masks[first] | masks[second])
                for first, second in zip(unique_values, unique_values[1:])
            ):
                learned_order: List[Tuple[int, int]] = []
                previous = np.zeros(shape, dtype=bool)
                for value in unique_values:
                    difference = np.argwhere(masks[value] & ~previous)
                    learned_order.extend(sorted(tuple(int(v) for v in row) for row in difference.tolist()))
                    previous = masks[value]
                learned_order.extend(
                    point for point in orders["row"] if point not in learned_order
                )
                if all(0 <= value <= len(learned_order) for value in test_values):
                    _try_exact_rule(
                        output,
                        train,
                        tests,
                        f"scene_count_{statistic_name}_nested",
                        lambda grid, stat=statistic, sequence=tuple(learned_order), bg=background,
                        fg=foreground, target_shape=shape: _scene_render_prefix(
                            int(stat(grid)), sequence, 1, 0, bg, fg, target_shape
                        ),
                        10,
                        "scene_count_serializer",
                        metadata={
                            "scene_block": "statistic_serialization",
                            "statistic": statistic_name,
                            "serializer": "nested_activation",
                            "exact_demonstration_contract": True,
                        },
                    )
    return output


def _scene_fit_count_renderers(
    counts: Sequence[int], panels: Sequence[Array]
) -> List[Tuple[str, Callable[[int], Array]]]:
    if not panels or len({panel.shape for panel in panels}) != 1:
        return []
    shape = panels[0].shape
    backgrounds = [infer_bg(panel) for panel in panels]
    if len(set(backgrounds)) != 1:
        return []
    background = backgrounds[0]
    foreground_sets = [set(int(value) for value in np.unique(panel)) - {background} for panel in panels]
    if any(len(values) > 1 for values in foreground_sets):
        return []
    foreground_values = set().union(*foreground_sets)
    if len(foreground_values) != 1:
        return []
    foreground = next(iter(foreground_values))
    active_counts = [int(np.count_nonzero(panel != background)) for panel in panels]
    renderers: List[Tuple[str, Callable[[int], Array]]] = []
    for order_name, order in _scene_cell_orders(shape).items():
        for multiplier in range(0, 5):
            for intercept in range(-5, 6):
                if not all(
                    multiplier * count + intercept == active
                    for count, active in zip(counts, active_counts)
                ):
                    continue
                if all(
                    exact(
                        _scene_render_prefix(
                            count,
                            order,
                            multiplier,
                            intercept,
                            background,
                            foreground,
                            shape,
                        ),
                        panel,
                    )
                    for count, panel in zip(counts, panels)
                ):
                    renderers.append(
                        (
                            f"{order_name}_{multiplier}_{intercept}",
                            lambda count, sequence=tuple(order), a=multiplier, b=intercept,
                            bg=background, fg=foreground, target_shape=shape: _scene_render_prefix(
                                count, sequence, a, b, bg, fg, target_shape
                            ),
                        )
                    )
    if list(active_counts) == list(counts):
        masks: Dict[int, Array] = {}
        valid = True
        for count, panel in zip(counts, panels):
            mask = panel != background
            if count in masks and not np.array_equal(masks[count], mask):
                valid = False
                break
            masks[count] = mask
        unique_counts = sorted(masks)
        if valid and all(
            np.all(~masks[first] | masks[second])
            for first, second in zip(unique_counts, unique_counts[1:])
        ):
            order: List[Tuple[int, int]] = []
            previous = np.zeros(shape, dtype=bool)
            for count in unique_counts:
                difference = np.argwhere(masks[count] & ~previous)
                order.extend(sorted(tuple(int(v) for v in row) for row in difference.tolist()))
                previous = masks[count]
            order.extend(point for point in _scene_cell_orders(shape)["row"] if point not in order)
            renderers.append(
                (
                    "nested",
                    lambda count, sequence=tuple(order), bg=background, fg=foreground,
                    target_shape=shape: _scene_render_prefix(
                        count, sequence, 1, 0, bg, fg, target_shape
                    ),
                )
            )
    return renderers


def scene_shape_histogram_rules(
    train: List[Tuple[Array, Array]], tests: List[Array]
) -> List[RuleCandidate]:
    """Serialize counts of two oriented object shapes into two output panels."""
    output: List[RuleCandidate] = []
    if not train:
        return output
    targets = [target for _, target in train]
    if len({target.shape for target in targets}) != 1 or targets[0].size > 72:
        return output
    for connectivity in (4, 8):
        for separate_colors in (True, False):
            signatures = sorted(
                {
                    object_mask_signature(obj)
                    for source, _ in train
                    for obj in generic_components(source, connectivity, separate_colors)
                    if obj.size > 1
                },
                key=lambda signature: (len(signature), len(signature[0]), signature),
            )
            if len(signatures) != 2:
                continue
            height, width = targets[0].shape
            panel_specs: List[Tuple[str, List[List[Array]], int]] = []
            if width % 2 == 0:
                half = width // 2
                panel_specs.append(
                    (
                        "horizontal",
                        [
                            [target[:, :half] for target in targets],
                            [target[:, half:] for target in targets],
                        ],
                        1,
                    )
                )
            if height % 2 == 0:
                half = height // 2
                panel_specs.append(
                    (
                        "vertical",
                        [
                            [target[:half, :] for target in targets],
                            [target[half:, :] for target in targets],
                        ],
                        0,
                    )
                )
            for layout_name, panel_sets, axis in panel_specs:
                for assigned_signatures in itertools.permutations(signatures):
                    renderer_options: List[List[Tuple[str, Callable[[int], Array]]]] = []
                    valid = True
                    for signature, panels in zip(assigned_signatures, panel_sets):
                        counts = [
                            sum(
                                object_mask_signature(obj) == signature
                                for obj in generic_components(source, connectivity, separate_colors)
                                if obj.size > 1
                            )
                            for source, _ in train
                        ]
                        renderers = _scene_fit_count_renderers(counts, panels)
                        if not renderers:
                            valid = False
                            break
                        renderer_options.append(renderers[:4])
                    if not valid:
                        continue
                    for renderer_pair in itertools.product(*renderer_options):
                        def apply(
                            grid: Array,
                            signature_order=assigned_signatures,
                            renderers=tuple(renderer for _, renderer in renderer_pair),
                            conn=connectivity,
                            separate=separate_colors,
                            concatenate_axis=axis,
                        ) -> Array:
                            objects = [
                                obj
                                for obj in generic_components(grid, conn, separate)
                                if obj.size > 1
                            ]
                            panels = []
                            for signature, renderer in zip(signature_order, renderers):
                                count = sum(object_mask_signature(obj) == signature for obj in objects)
                                panels.append(renderer(count))
                            return np.concatenate(panels, axis=concatenate_axis)

                        _try_exact_rule(
                            output,
                            train,
                            tests,
                            f"scene_shape_histogram_{layout_name}_c{connectivity}_"
                            f"{int(separate_colors)}_{renderer_pair[0][0]}_{renderer_pair[1][0]}",
                            apply,
                            13,
                            "scene_shape_histogram",
                            metadata={
                                "scene_block": "shape_histogram",
                                "layout": layout_name,
                                "connectivity": connectivity,
                                "separate_colors": separate_colors,
                                "exact_demonstration_contract": True,
                            },
                        )
    return output


def object_scene_algebra_rules(
    train: List[Tuple[Array, Array]], tests: List[Array]
) -> List[RuleCandidate]:
    """Complete proposal block for object extraction and serialization."""
    output: List[RuleCandidate] = []
    output.extend(scene_panel_algebra_rules(train, tests))
    output.extend(scene_marker_extraction_rules(train, tests))
    output.extend(scene_statistic_serialization_rules(train, tests))
    output.extend(scene_shape_histogram_rules(train, tests))
    return output


# ---------------- signal topology and transport proposal channel ----------------

_SIGNAL_DIRECTIONS: Tuple[Tuple[int, int], ...] = (
    (-1, 0),
    (1, 0),
    (0, -1),
    (0, 1),
    (-1, -1),
    (-1, 1),
    (1, -1),
    (1, 1),
)


def _signal_patch_signatures(
    grid: Array,
    *,
    radius: int,
    binary: bool,
    cross: bool,
) -> List[List[Tuple[int, ...]]]:
    """Return translation-equivariant local signal signatures.

    The absolute center color is retained. Surrounding entries may be either
    palette values or foreground indicators. Boundary samples are padded with
    the inferred background, so no coordinate identity enters the signature.
    """
    grid = sanitize_grid(grid)
    background = infer_bg(grid)
    height, width = grid.shape
    values = (grid != background).astype(np.int16) if binary else grid
    padding_value = 0 if binary else background
    padded = np.pad(values, radius, constant_values=padding_value)
    output: List[List[Tuple[int, ...]]] = []
    for row in range(height):
        row_signatures: List[Tuple[int, ...]] = []
        for column in range(width):
            signature: List[int] = [int(grid[row, column])]
            if cross:
                for distance in range(1, radius + 1):
                    for delta_row, delta_column in _SIGNAL_DIRECTIONS[:4]:
                        signature.append(
                            int(
                                padded[
                                    row + radius + delta_row * distance,
                                    column + radius + delta_column * distance,
                                ]
                            )
                        )
            else:
                patch = padded[
                    row : row + 2 * radius + 1,
                    column : column + 2 * radius + 1,
                ].ravel()
                center_index = int(patch.size // 2)
                signature.extend(int(value) for index, value in enumerate(patch) if index != center_index)
            row_signatures.append(tuple(signature))
        output.append(row_signatures)
    return output


def _signal_ray_fields(grid: Array) -> Tuple[Array, Array]:
    """Nearest visible signal color and distance in eight directions."""
    grid = sanitize_grid(grid)
    background = infer_bg(grid)
    height, width = grid.shape
    colors = np.full((8, height, width), background, dtype=np.int16)
    distances = np.zeros((8, height, width), dtype=np.int16)
    limit = max(height, width)
    for direction_index, (delta_row, delta_column) in enumerate(_SIGNAL_DIRECTIONS):
        for row in range(height):
            for column in range(width):
                for distance in range(1, limit + 1):
                    target_row = row + delta_row * distance
                    target_column = column + delta_column * distance
                    if not (0 <= target_row < height and 0 <= target_column < width):
                        break
                    color = int(grid[target_row, target_column])
                    if color != background:
                        colors[direction_index, row, column] = color
                        distances[direction_index, row, column] = distance
                        break
    return colors, distances


def _signal_ray_signatures(grid: Array, mode: str) -> List[List[Tuple[int, ...]]]:
    grid = sanitize_grid(grid)
    height, width = grid.shape
    colors, distances = _signal_ray_fields(grid)
    output: List[List[Tuple[int, ...]]] = []
    for row in range(height):
        row_signatures: List[Tuple[int, ...]] = []
        for column in range(width):
            signature: List[int] = [int(grid[row, column])]
            if mode == "ray":
                signature.extend(int(colors[index, row, column]) for index in range(8))
            elif mode == "ray_dist":
                for index in range(8):
                    signature.extend(
                        (
                            int(colors[index, row, column]),
                            min(int(distances[index, row, column]), 5),
                        )
                    )
            elif mode == "ray_balance":
                signature.extend(int(colors[index, row, column]) for index in range(8))
                signature.extend(
                    (
                        int(distances[0, row, column] == distances[1, row, column] and distances[0, row, column] > 0),
                        int(distances[2, row, column] == distances[3, row, column] and distances[2, row, column] > 0),
                        int(distances[4, row, column] == distances[7, row, column] and distances[4, row, column] > 0),
                        int(distances[5, row, column] == distances[6, row, column] and distances[5, row, column] > 0),
                    )
                )
            else:
                raise ValueError(mode)
            row_signatures.append(tuple(signature))
        output.append(row_signatures)
    return output


def _signal_signature_grid(grid: Array, mode: str) -> List[List[Tuple[int, ...]]]:
    if mode == "patch1":
        return _signal_patch_signatures(grid, radius=1, binary=False, cross=False)
    if mode == "patch1_binary":
        return _signal_patch_signatures(grid, radius=1, binary=True, cross=False)
    if mode == "patch2_binary":
        return _signal_patch_signatures(grid, radius=2, binary=True, cross=False)
    if mode == "cross2":
        return _signal_patch_signatures(grid, radius=2, binary=False, cross=True)
    if mode in {"ray", "ray_dist", "ray_balance"}:
        return _signal_ray_signatures(grid, mode)
    raise ValueError(mode)


def _learn_signal_lookup_candidate(
    train: List[Tuple[Array, Array]],
    tests: List[Array],
    mode: str,
    *,
    minimum_changed_support: int,
    maximum_sparse_mapping: int = 64,
    maximum_sparse_changed_keys: int = 16,
) -> Optional[RuleCandidate]:
    """Fit a finite translation-equivariant signal transducer.

    A palette output may be assigned to a local or line-of-sight signature only
    when the assignment is deterministic across every demonstration. The
    conservative form requires every changed signature to recur. A bounded
    sparse form admits singleton evidence only when the entire rule table is
    small. Unseen test signatures preserve the original cell value.
    """
    mapping: Dict[Tuple[int, ...], int] = {}
    support: Counter[Tuple[int, ...]] = Counter()
    changed_support: Counter[Tuple[int, ...]] = Counter()
    signature_grids: List[List[List[Tuple[int, ...]]]] = []
    for input_grid, target in train:
        if input_grid.shape != target.shape:
            return None
        signatures = _signal_signature_grid(input_grid, mode)
        signature_grids.append(signatures)
        for row in range(input_grid.shape[0]):
            for column in range(input_grid.shape[1]):
                key = signatures[row][column]
                value = int(target[row, column])
                support[key] += 1
                if value != int(input_grid[row, column]):
                    changed_support[key] += 1
                previous = mapping.get(key)
                if previous is not None and previous != value:
                    return None
                mapping[key] = value
    if not changed_support:
        return None
    if any(support[key] < minimum_changed_support for key in changed_support):
        return None
    if minimum_changed_support == 1 and (
        len(mapping) > maximum_sparse_mapping or len(changed_support) > maximum_sparse_changed_keys
    ):
        return None

    def apply(grid: Array) -> Array:
        grid = sanitize_grid(grid)
        signatures = _signal_signature_grid(grid, mode)
        result = grid.copy()
        for row in range(grid.shape[0]):
            for column in range(grid.shape[1]):
                result[row, column] = mapping.get(signatures[row][column], int(grid[row, column]))
        return result

    train_predictions = tuple(apply(input_grid) for input_grid, _ in train)
    if not all(exact(prediction, target) for prediction, (_, target) in zip(train_predictions, train)):
        return None
    test_predictions = [apply(test) for test in tests]
    feature_cost = {
        "patch1": 5,
        "patch1_binary": 4,
        "patch2_binary": 8,
        "cross2": 7,
        "ray": 8,
        "ray_dist": 11,
        "ray_balance": 10,
    }[mode]
    complexity = (
        10
        + feature_cost
        + 2 * len(changed_support)
        + min(len(mapping), 128) // 4
        + (8 if minimum_changed_support == 1 else 0)
    )
    family = "signal_ray_transport" if mode.startswith("ray") else "signal_local_transducer"
    return RuleCandidate(
        name=f"signal_{mode}_support{minimum_changed_support}",
        grids=test_predictions,
        train_error=0,
        complexity=complexity,
        family=family,
        train_grids=train_predictions,
        metadata={
            "mode": mode,
            "mapping_size": len(mapping),
            "changed_key_count": len(changed_support),
            "minimum_changed_support": minimum_changed_support,
            "translation_equivariant": True,
            "unseen_signature_policy": "preserve_input",
        },
    )


def signal_lookup_rules(
    train: List[Tuple[Array, Array]],
    tests: List[Array],
) -> List[RuleCandidate]:
    """Exact-fit local and line-of-sight signal programs."""
    if not train or not all(input_grid.shape == target.shape for input_grid, target in train):
        return []
    output: List[RuleCandidate] = []
    for mode in (
        "patch1",
        "patch1_binary",
        "patch2_binary",
        "cross2",
        "ray",
        "ray_dist",
        "ray_balance",
    ):
        conservative = _learn_signal_lookup_candidate(
            train,
            tests,
            mode,
            minimum_changed_support=2,
        )
        if conservative is not None:
            output.append(conservative)
            continue
        sparse = _learn_signal_lookup_candidate(
            train,
            tests,
            mode,
            minimum_changed_support=1,
        )
        if sparse is not None:
            output.append(sparse)
    return output


def _signal_gap_fill_exact(
    grid: Array,
    axis: str,
    gap: int,
    source_color: Optional[int],
    fill_color: int,
) -> Array:
    grid = sanitize_grid(grid)
    background = infer_bg(grid)
    output = grid.copy()
    height, width = grid.shape
    directions: List[Tuple[int, int]] = []
    if axis in {"h", "hv", "all"}:
        directions.append((0, 1))
    if axis in {"v", "hv", "all"}:
        directions.append((1, 0))
    if axis in {"diag", "all"}:
        directions.extend(((1, 1), (1, -1)))
    changed = 0
    for delta_row, delta_column in directions:
        for row in range(height):
            for column in range(width):
                target_row = row + delta_row * (gap + 1)
                target_column = column + delta_column * (gap + 1)
                if not (0 <= target_row < height and 0 <= target_column < width):
                    continue
                left = int(grid[row, column])
                right = int(grid[target_row, target_column])
                if left == background or right == background or left != right:
                    continue
                if source_color is not None and left != int(source_color):
                    continue
                between = [
                    (row + delta_row * step, column + delta_column * step)
                    for step in range(1, gap + 1)
                ]
                if all(int(grid[r, c]) == background for r, c in between):
                    for target in between:
                        if int(output[target]) != int(fill_color):
                            output[target] = int(fill_color)
                            changed += 1
    if changed == 0:
        raise ValueError("gap interpolation produced no signal")
    return output


def _signal_progression_extrapolation_exact(
    grid: Array,
    source_color: int,
    fill_color: int,
    direction: str,
) -> Array:
    grid = sanitize_grid(grid)
    background = infer_bg(grid)
    coordinates = sorted(tuple(map(int, point)) for point in np.argwhere(grid == int(source_color)))
    if len(coordinates) < 2:
        raise ValueError("not enough source samples")
    delta = (
        coordinates[1][0] - coordinates[0][0],
        coordinates[1][1] - coordinates[0][1],
    )
    if delta == (0, 0):
        raise ValueError("degenerate progression")
    if any(
        (
            coordinates[index][0] - coordinates[index - 1][0],
            coordinates[index][1] - coordinates[index - 1][1],
        )
        != delta
        for index in range(2, len(coordinates))
    ):
        raise ValueError("source is not an arithmetic lattice signal")
    output = grid.copy()
    height, width = grid.shape
    endpoints: List[Tuple[Tuple[int, int], Tuple[int, int]]] = []
    if direction in {"forward", "both"}:
        endpoints.append((coordinates[-1], delta))
    if direction in {"backward", "both"}:
        endpoints.append((coordinates[0], (-delta[0], -delta[1])))
    changed = 0
    for (row, column), (delta_row, delta_column) in endpoints:
        while True:
            row += delta_row
            column += delta_column
            if not (0 <= row < height and 0 <= column < width):
                break
            if int(grid[row, column]) != background:
                break
            output[row, column] = int(fill_color)
            changed += 1
    if changed == 0:
        raise ValueError("progression extrapolation produced no signal")
    return output


def _signal_oriented_bars(grid: Array) -> List[Tuple[Obj, str, int]]:
    grid = sanitize_grid(grid)
    output: List[Tuple[Obj, str, int]] = []
    for obj in generic_components(grid, 4, True):
        if obj.size < 2:
            continue
        row0, column0, _, _ = obj.bbox
        mask = np.zeros((obj.height, obj.width), dtype=bool)
        for row, column in obj.cells:
            mask[row - row0, column - column0] = True
        if not bool(mask.all()):
            continue
        if obj.width > obj.height:
            orientation = "h"
        elif obj.height > obj.width:
            orientation = "v"
        else:
            continue
        first_row, first_column = obj.cells[0]
        output.append((obj, orientation, int(grid[first_row, first_column])))
    return output


def _signal_extend_bars_exact(
    grid: Array,
    mode: str,
    intersection_color: int,
) -> Array:
    grid = sanitize_grid(grid)
    height, width = grid.shape
    bars = _signal_oriented_bars(grid)
    if not bars:
        raise ValueError("no oriented bar signals")
    output = grid.copy()
    multiplicity = np.zeros_like(grid, dtype=np.int16)
    layers: List[Tuple[Array, int]] = []
    for obj, orientation, color in bars:
        row0, column0, row1, column1 = obj.bbox
        mask = np.zeros_like(grid, dtype=bool)
        if orientation == "h":
            if mode == "full":
                mask[row0 : row1 + 1, :] = True
            elif mode == "inward":
                if (column0 + column1) / 2 < width / 2:
                    mask[row0 : row1 + 1, column0:] = True
                else:
                    mask[row0 : row1 + 1, : column1 + 1] = True
            else:
                raise ValueError(mode)
        else:
            if mode == "full":
                mask[:, column0 : column1 + 1] = True
            elif mode == "inward":
                if (row0 + row1) / 2 < height / 2:
                    mask[row0:, column0 : column1 + 1] = True
                else:
                    mask[: row1 + 1, column0 : column1 + 1] = True
            else:
                raise ValueError(mode)
        layers.append((mask, color))
    for mask, color in layers:
        multiplicity += mask
        output[mask] = int(color)
    output[multiplicity >= 2] = int(intersection_color)
    if exact(output, grid):
        raise ValueError("bar transport produced no signal")
    return output


def _signal_balanced_cross_exact(
    grid: Array,
    fill_color: int,
    *,
    require_same_opposite_colors: bool,
    require_oriented_bars: bool,
) -> Array:
    """Mark balanced intersections of horizontal and vertical signal pairs."""
    grid = sanitize_grid(grid)
    background = infer_bg(grid)
    height, width = grid.shape
    orientation_by_cell: Dict[Tuple[int, int], str] = {}
    for obj, orientation, _ in _signal_oriented_bars(grid):
        for cell in obj.cells:
            orientation_by_cell[cell] = orientation
    output = grid.copy()
    changed = 0
    required_orientations = ("v", "v", "h", "h")
    for row in range(height):
        for column in range(width):
            if int(grid[row, column]) != background:
                continue
            rays: List[Optional[Tuple[int, int, Optional[str]]]] = []
            for delta_row, delta_column in _SIGNAL_DIRECTIONS[:4]:
                found: Optional[Tuple[int, int, Optional[str]]] = None
                for distance in range(1, max(height, width) + 1):
                    target_row = row + delta_row * distance
                    target_column = column + delta_column * distance
                    if not (0 <= target_row < height and 0 <= target_column < width):
                        break
                    color = int(grid[target_row, target_column])
                    if color != background:
                        found = (
                            distance,
                            color,
                            orientation_by_cell.get((target_row, target_column)),
                        )
                        break
                rays.append(found)
            if any(ray is None for ray in rays):
                continue
            north, south, west, east = rays
            assert north is not None and south is not None and west is not None and east is not None
            if north[0] != south[0] or west[0] != east[0]:
                continue
            if require_same_opposite_colors and (north[1] != south[1] or west[1] != east[1]):
                continue
            if require_oriented_bars and tuple(ray[2] for ray in rays) != required_orientations:
                continue
            output[row, column] = int(fill_color)
            changed += 1
    if changed == 0:
        raise ValueError("no balanced signal intersections")
    return output


def signal_transport_rules(
    train: List[Tuple[Array, Array]],
    tests: List[Array],
) -> List[RuleCandidate]:
    """Analytic signal interpolation, extrapolation, and transport rules."""
    if not train or not all(input_grid.shape == target.shape for input_grid, target in train):
        return []
    # This block models sparse transport: existing cells are preserved and new
    # support is introduced in background locations.
    if not all(
        np.all((input_grid == target) | (input_grid == infer_bg(input_grid)))
        for input_grid, target in train
    ):
        return []
    output: List[RuleCandidate] = []
    input_colors = sorted({int(value) for grid, _ in train for value in np.unique(grid)})
    source_colors = [
        color
        for color in input_colors
        if all(color != infer_bg(grid) or np.count_nonzero(grid == color) == 0 for grid, _ in train)
        and any(np.count_nonzero(grid == color) > 0 for grid, _ in train)
    ]
    candidate_colors = _output_candidate_colors(train)
    if not candidate_colors:
        candidate_colors = sorted(
            {
                int(value)
                for _, target in train
                for value in np.unique(target)
                if int(value) != infer_bg(target)
            }
        )[:4]

    for gap in (1, 2, 3):
        for axis in ("h", "v", "hv", "diag", "all"):
            for fill_color in candidate_colors[:4]:
                _try_exact_rule(
                    output,
                    train,
                    tests,
                    f"signal_gap_{axis}_{gap}_all_{fill_color}",
                    lambda grid, a=axis, g=gap, f=fill_color: _signal_gap_fill_exact(grid, a, g, None, f),
                    8 + gap,
                    "signal_gap_interpolation",
                )
                for source_color in source_colors[:5]:
                    _try_exact_rule(
                        output,
                        train,
                        tests,
                        f"signal_gap_{axis}_{gap}_{source_color}_{fill_color}",
                        lambda grid, a=axis, g=gap, s=source_color, f=fill_color: _signal_gap_fill_exact(grid, a, g, s, f),
                        9 + gap,
                        "signal_gap_interpolation",
                    )

    for source_color in source_colors[:6]:
        if not all(np.count_nonzero(grid == source_color) >= 2 for grid, _ in train):
            continue
        for fill_color in candidate_colors[:4]:
            for direction in ("forward", "backward", "both"):
                _try_exact_rule(
                    output,
                    train,
                    tests,
                    f"signal_progression_{source_color}_{fill_color}_{direction}",
                    lambda grid, s=source_color, f=fill_color, d=direction: _signal_progression_extrapolation_exact(grid, s, f, d),
                    9,
                    "signal_progression_extrapolation",
                )

    for fill_color in candidate_colors[:4]:
        for mode in ("full", "inward"):
            _try_exact_rule(
                output,
                train,
                tests,
                f"signal_bar_transport_{mode}_{fill_color}",
                lambda grid, m=mode, f=fill_color: _signal_extend_bars_exact(grid, m, f),
                10,
                "signal_bar_transport",
            )
        for same_colors in (True, False):
            for oriented in (True, False):
                _try_exact_rule(
                    output,
                    train,
                    tests,
                    f"signal_balanced_cross_{fill_color}_{int(same_colors)}_{int(oriented)}",
                    lambda grid, f=fill_color, s=same_colors, o=oriented: _signal_balanced_cross_exact(
                        grid,
                        f,
                        require_same_opposite_colors=s,
                        require_oriented_bars=o,
                    ),
                    11,
                    "signal_balanced_intersection",
                )
    return output




# ---------------- multistage object-graph rewrite proposal channel ----------------

_GRAPH_PATH_DIRECTIONS: Tuple[Tuple[int, int], ...] = (
    (-1, 0),
    (1, 0),
    (0, -1),
    (0, 1),
    (-1, -1),
    (-1, 1),
    (1, -1),
    (1, 1),
)


def _graph_sign(value: int) -> int:
    return 0 if value == 0 else (1 if value > 0 else -1)


def _graph_line_cells(
    first: Tuple[int, int],
    second: Tuple[int, int],
    geometry: str,
) -> List[Tuple[int, int]]:
    """Return a discrete path between two packet anchors.

    The path language is intentionally finite and auditable.  Straight paths
    support horizontal, vertical, and 45-degree diagonal relations.  The two
    orthogonal policies provide the two possible one-bend Manhattan routes.
    """
    row0, column0 = first
    row1, column1 = second
    delta_row = row1 - row0
    delta_column = column1 - column0
    if geometry == "straight":
        if delta_row == 0:
            step = (0, _graph_sign(delta_column))
        elif delta_column == 0:
            step = (_graph_sign(delta_row), 0)
        elif abs(delta_row) == abs(delta_column):
            step = (_graph_sign(delta_row), _graph_sign(delta_column))
        else:
            raise ValueError("anchors are not straight-line aligned")
        length = max(abs(delta_row), abs(delta_column))
        return [(row0 + step[0] * index, column0 + step[1] * index) for index in range(length + 1)]
    if geometry not in {"orthogonal_hv", "orthogonal_vh"}:
        raise ValueError(geometry)
    elbow = (row0, column1) if geometry == "orthogonal_hv" else (row1, column0)
    first_segment = _graph_line_cells(first, elbow, "straight")
    second_segment = _graph_line_cells(elbow, second, "straight")
    return first_segment + second_segment[1:]


def graph_connect_color_pairs_exact(
    grid: Array,
    geometry: str = "straight",
    collision_policy: str = "preserve_existing",
    *,
    require_singletons: bool = True,
    connectivity: int = 4,
) -> Array:
    """Connect the two packets of every eligible color.

    The relation is defined on monochrome connected components rather than raw
    coordinates.  Existing packet cells are immutable.  At newly constructed
    intersections the selected collision policy chooses a deterministic color.
    """
    grid = sanitize_grid(grid)
    background = infer_bg(grid)
    height, width = grid.shape
    layers: List[Tuple[int, set[Tuple[int, int]]]] = []
    colors = sorted(int(value) for value in np.unique(grid) if int(value) != background)
    for color in colors:
        objects = [
            obj
            for obj in generic_components(grid, connectivity, True)
            if obj.color == color
        ]
        if len(objects) != 2:
            continue
        if require_singletons and any(obj.size != 1 for obj in objects):
            continue
        anchors: List[Tuple[int, int]] = []
        for obj in objects:
            row0, column0, row1, column1 = obj.bbox
            anchors.append(((row0 + row1) // 2, (column0 + column1) // 2))
        try:
            path = _graph_line_cells(anchors[0], anchors[1], geometry)
        except ValueError:
            continue
        layers.append((color, set(path)))
    if not layers:
        raise ValueError("no eligible packet pairs")

    proposals: Dict[Tuple[int, int], List[int]] = defaultdict(list)
    for color, cells in layers:
        for row, column in cells:
            if 0 <= row < height and 0 <= column < width:
                proposals[(row, column)].append(int(color))

    output = grid.copy()
    changed = 0
    for (row, column), proposed_colors in proposals.items():
        current = int(grid[row, column])
        if current != background:
            continue
        unique = sorted(set(proposed_colors))
        if len(unique) == 1:
            selected = unique[0]
        elif collision_policy == "vertical_over_horizontal":
            vertical_colors: List[int] = []
            horizontal_colors: List[int] = []
            for color, cells in layers:
                if (row, column) not in cells:
                    continue
                same_column = sum(1 for rr, cc in cells if cc == column) >= 2
                same_row = sum(1 for rr, cc in cells if rr == row) >= 2
                if same_column:
                    vertical_colors.append(color)
                if same_row:
                    horizontal_colors.append(color)
            selected = (
                sorted(vertical_colors)[0]
                if vertical_colors
                else sorted(horizontal_colors or unique)[0]
            )
        elif collision_policy == "horizontal_over_vertical":
            horizontal_colors = []
            vertical_colors = []
            for color, cells in layers:
                if (row, column) not in cells:
                    continue
                if sum(1 for rr, cc in cells if rr == row) >= 2:
                    horizontal_colors.append(color)
                if sum(1 for rr, cc in cells if cc == column) >= 2:
                    vertical_colors.append(color)
            selected = (
                sorted(horizontal_colors)[0]
                if horizontal_colors
                else sorted(vertical_colors or unique)[0]
            )
        elif collision_policy == "minimum_color":
            selected = min(unique)
        elif collision_policy == "maximum_color":
            selected = max(unique)
        elif collision_policy == "preserve_existing":
            selected = unique[0]
        else:
            raise ValueError(collision_policy)
        output[row, column] = int(selected)
        changed += 1
    if changed == 0:
        raise ValueError("pair connection produced no new support")
    return output


def graph_project_objects_to_boundary_exact(
    grid: Array,
    direction: str,
    output_color: int,
    coordinate_policy: str = "center_floor",
    *,
    connectivity: int = 4,
    object_policy: str = "non_singleton",
) -> Array:
    """Project object anchors onto one canvas boundary.

    This is a graph rewrite from object nodes to boundary nodes.  It is useful
    when repeated packets encode a list of positions and a new color serializes
    those positions along an edge.
    """
    grid = sanitize_grid(grid)
    background = infer_bg(grid)
    height, width = grid.shape
    objects = generic_components(grid, connectivity, True)
    if object_policy == "non_singleton":
        objects = [obj for obj in objects if obj.size > 1]
    elif object_policy == "all":
        pass
    elif object_policy == "hollow":
        objects = [
            obj
            for obj in objects
            if obj.height >= 2
            and obj.width >= 2
            and obj.size < obj.height * obj.width
        ]
    else:
        raise ValueError(object_policy)
    if not objects:
        raise ValueError("no projectable objects")

    output = grid.copy()
    changed = 0
    for obj in objects:
        row0, column0, row1, column1 = obj.bbox
        if coordinate_policy == "center_floor":
            anchor_row = (row0 + row1) // 2
            anchor_column = (column0 + column1) // 2
        elif coordinate_policy == "center_ceil":
            anchor_row = (row0 + row1 + 1) // 2
            anchor_column = (column0 + column1 + 1) // 2
        elif coordinate_policy == "minimum":
            anchor_row, anchor_column = row0, column0
        elif coordinate_policy == "maximum":
            anchor_row, anchor_column = row1, column1
        else:
            raise ValueError(coordinate_policy)
        if direction == "top":
            target = (0, anchor_column)
        elif direction == "bottom":
            target = (height - 1, anchor_column)
        elif direction == "left":
            target = (anchor_row, 0)
        elif direction == "right":
            target = (anchor_row, width - 1)
        else:
            raise ValueError(direction)
        row, column = target
        if int(output[row, column]) not in {background, int(output_color)}:
            raise ValueError("boundary projection collides with existing signal")
        if int(output[row, column]) != int(output_color):
            output[row, column] = int(output_color)
            changed += 1
    if changed == 0:
        raise ValueError("boundary projection produced no change")
    return output


def graph_fill_objects_to_nearest_corner_exact(
    grid: Array,
    distance_mode: str = "manhattan",
    tie_policy: str = "reading_order",
    *,
    connectivity: int = 4,
    object_policy: str = "single_object",
) -> Array:
    """Expand packet bounding boxes to their nearest canvas corners."""
    grid = sanitize_grid(grid)
    background = infer_bg(grid)
    height, width = grid.shape
    objects = generic_components(grid, connectivity, True)
    if object_policy == "single_object":
        if len(objects) != 1:
            raise ValueError("expected exactly one foreground packet")
    elif object_policy == "singletons":
        objects = [obj for obj in objects if obj.size == 1]
        if not objects:
            raise ValueError("no singleton packets")
    elif object_policy != "all":
        raise ValueError(object_policy)

    corner_order = {
        "reading_order": ("top_left", "top_right", "bottom_left", "bottom_right"),
        "reverse_reading": ("bottom_right", "bottom_left", "top_right", "top_left"),
        "clockwise": ("top_left", "top_right", "bottom_right", "bottom_left"),
    }.get(tie_policy)
    if corner_order is None:
        raise ValueError(tie_policy)

    output = grid.copy()
    changed = 0
    for obj in objects:
        row0, column0, row1, column1 = obj.bbox
        corners = {
            "top_left": (0, 0, abs(row0) + abs(column0)),
            "top_right": (0, width - 1, abs(row0) + abs(width - 1 - column1)),
            "bottom_left": (height - 1, 0, abs(height - 1 - row1) + abs(column0)),
            "bottom_right": (
                height - 1,
                width - 1,
                abs(height - 1 - row1) + abs(width - 1 - column1),
            ),
        }
        if distance_mode == "chebyshev":
            corners = {
                "top_left": (0, 0, max(row0, column0)),
                "top_right": (0, width - 1, max(row0, width - 1 - column1)),
                "bottom_left": (height - 1, 0, max(height - 1 - row1, column0)),
                "bottom_right": (
                    height - 1,
                    width - 1,
                    max(height - 1 - row1, width - 1 - column1),
                ),
            }
        elif distance_mode != "manhattan":
            raise ValueError(distance_mode)
        minimum = min(value[2] for value in corners.values())
        selected_name = next(name for name in corner_order if corners[name][2] == minimum)
        corner_row, corner_column, _ = corners[selected_name]
        fill_row0, fill_row1 = sorted((corner_row, row0 if corner_row == 0 else row1))
        fill_column0, fill_column1 = sorted(
            (corner_column, column0 if corner_column == 0 else column1)
        )
        color = int(grid[obj.cells[0][0], obj.cells[0][1]])
        region = output[fill_row0 : fill_row1 + 1, fill_column0 : fill_column1 + 1]
        collision = (region != background) & (region != color)
        if bool(np.any(collision)):
            raise ValueError("corner expansion collides with another packet")
        changed += int(np.count_nonzero(region != color))
        region[:, :] = color
    if changed == 0:
        raise ValueError("corner expansion produced no change")
    return output


def graph_contract_right_triangle_exact(
    grid: Array,
    center_color: int,
    final_leg: int = 2,
    *,
    connectivity: int = 4,
) -> Array:
    """Contract a three-vertex right-isosceles object graph toward its center."""
    grid = sanitize_grid(grid)
    background = infer_bg(grid)
    objects = generic_components(grid, connectivity, True)
    if len(objects) != 3 or any(obj.size != 1 for obj in objects):
        raise ValueError("triangle contraction requires three singleton packets")
    points = [
        (obj.cells[0][0], obj.cells[0][1], int(grid[obj.cells[0][0], obj.cells[0][1]]))
        for obj in objects
    ]
    configuration = None
    for corner in points:
        horizontal = [point for point in points if point is not corner and point[0] == corner[0]]
        vertical = [point for point in points if point is not corner and point[1] == corner[1]]
        if len(horizontal) == 1 and len(vertical) == 1:
            horizontal_leg = abs(horizontal[0][1] - corner[1])
            vertical_leg = abs(vertical[0][0] - corner[0])
            if horizontal_leg == vertical_leg:
                configuration = (corner, horizontal[0], vertical[0], horizontal_leg)
                break
    if configuration is None:
        raise ValueError("singleton packets do not form a right-isosceles triangle")
    corner, horizontal, vertical, leg = configuration
    if leg <= final_leg or (leg - final_leg) % 2:
        raise ValueError("triangle leg cannot contract to requested terminal size")
    shift = (leg - final_leg) // 2
    horizontal_sign = _graph_sign(horizontal[1] - corner[1])
    vertical_sign = _graph_sign(vertical[0] - corner[0])
    contracted = [
        (
            corner[0] + vertical_sign * shift,
            corner[1] + horizontal_sign * shift,
            corner[2],
        ),
        (
            horizontal[0] + vertical_sign * shift,
            horizontal[1] - horizontal_sign * shift,
            horizontal[2],
        ),
        (
            vertical[0] - vertical_sign * shift,
            vertical[1] + horizontal_sign * shift,
            vertical[2],
        ),
    ]
    center_row = (contracted[1][0] + contracted[2][0]) // 2
    center_column = (contracted[1][1] + contracted[2][1]) // 2
    output = grid.copy()
    for row, column, color in contracted:
        if not (0 <= row < grid.shape[0] and 0 <= column < grid.shape[1]):
            raise ValueError("contracted triangle leaves canvas")
        if int(output[row, column]) not in {background, color}:
            raise ValueError("contracted triangle collides")
        output[row, column] = int(color)
    if int(output[center_row, center_column]) not in {background, int(center_color)}:
        raise ValueError("triangle center collides")
    output[center_row, center_column] = int(center_color)
    if exact(output, grid):
        raise ValueError("triangle contraction produced no change")
    return output


def _graph_component_center(obj: Obj) -> Tuple[float, float]:
    row0, column0, row1, column1 = obj.bbox
    return ((row0 + row1) / 2.0, (column0 + column1) / 2.0)


def _graph_template_vector_candidates(
    template: Obj,
    marker: Obj,
    *,
    maximum_norm: int,
) -> List[Tuple[int, int]]:
    template_cells = set(template.cells)
    marker_cells = set(marker.cells)
    candidates: set[Tuple[int, int]] = set()
    for marker_row, marker_column in marker_cells:
        for template_row, template_column in template_cells:
            delta = (marker_row - template_row, marker_column - template_column)
            if delta == (0, 0):
                continue
            delta_row, delta_column = delta
            if not (
                delta_row == 0
                or delta_column == 0
                or abs(delta_row) == abs(delta_column)
            ):
                continue
            if max(abs(delta_row), abs(delta_column)) > maximum_norm:
                continue
            if all(
                (row - delta_row, column - delta_column) in template_cells
                for row, column in marker_cells
            ):
                candidates.add(delta)
    template_center = _graph_component_center(template)
    marker_center = _graph_component_center(marker)
    relative = (
        marker_center[0] - template_center[0],
        marker_center[1] - template_center[1],
    )
    filtered = [
        delta
        for delta in candidates
        if delta[0] * relative[0] + delta[1] * relative[1] > 0
        and set((row + delta[0], column + delta[1]) for row, column in template_cells).isdisjoint(template_cells)
    ]
    return sorted(filtered)


def graph_repeat_template_along_marker_rays_exact(
    grid: Array,
    vector_policy: str = "maximum",
    collision_policy: str = "background_only",
    *,
    connectivity: int = 4,
) -> Array:
    """Complete and repeat a template packet along marker-defined rays.

    A marker packet must be a translated subset of the unique largest
    monochrome template.  The inferred translation is then iterated until the
    translated template has no cells inside the canvas.
    """
    grid = sanitize_grid(grid)
    background = infer_bg(grid)
    objects = generic_components(grid, connectivity, True)
    if len(objects) < 2:
        raise ValueError("template propagation requires markers")
    ordered = sorted(objects, key=lambda obj: (obj.size, obj.height * obj.width), reverse=True)
    if len(ordered) > 1 and (ordered[0].size, ordered[0].height * ordered[0].width) == (
        ordered[1].size,
        ordered[1].height * ordered[1].width,
    ):
        raise ValueError("largest template is not unique")
    template = ordered[0]
    markers = ordered[1:]
    maximum_norm = max(8, 2 * max(template.height, template.width) + 2)
    marker_vectors: List[Tuple[Obj, Tuple[int, int]]] = []
    for marker in markers:
        vectors = _graph_template_vector_candidates(
            template,
            marker,
            maximum_norm=maximum_norm,
        )
        if not vectors:
            raise ValueError("marker is not a translated template subset")
        if vector_policy == "maximum":
            vector = max(
                vectors,
                key=lambda value: (
                    max(abs(value[0]), abs(value[1])),
                    abs(value[0]) + abs(value[1]),
                    value,
                ),
            )
        elif vector_policy == "minimum":
            vector = min(
                vectors,
                key=lambda value: (
                    max(abs(value[0]), abs(value[1])),
                    abs(value[0]) + abs(value[1]),
                    value,
                ),
            )
        else:
            raise ValueError(vector_policy)
        marker_vectors.append((marker, vector))

    output = grid.copy()
    template_cells = set(template.cells)
    changed = 0
    for marker, (delta_row, delta_column) in sorted(
        marker_vectors,
        key=lambda item: (
            _graph_component_center(item[0])[0],
            _graph_component_center(item[0])[1],
            item[0].color,
        ),
    ):
        step = 1
        while True:
            translated = [
                (row + step * delta_row, column + step * delta_column)
                for row, column in template_cells
            ]
            visible = [
                (row, column)
                for row, column in translated
                if 0 <= row < grid.shape[0] and 0 <= column < grid.shape[1]
            ]
            if not visible:
                break
            for row, column in visible:
                current = int(output[row, column])
                if collision_policy == "background_only":
                    if current not in {background, marker.color}:
                        raise ValueError("template ray collides with existing packet")
                elif collision_policy == "overwrite_markers":
                    if current != background and current not in {
                        marker.color,
                        template.color,
                    }:
                        raise ValueError("template ray collides with unrelated packet")
                else:
                    raise ValueError(collision_policy)
                if current != marker.color:
                    output[row, column] = int(marker.color)
                    changed += 1
            step += 1
            if step > max(grid.shape) + 2:
                break
    if changed == 0:
        raise ValueError("template propagation produced no change")
    return output



def _graph_symmetry_transforms(
    mode: str,
    row0: int,
    column0: int,
    row1: int,
    column1: int,
) -> List[Callable[[int, int], Tuple[int, int]]]:
    transforms: List[Callable[[int, int], Tuple[int, int]]] = []
    if mode in {"horizontal", "hv", "all"}:
        transforms.append(lambda row, column: (row, column0 + column1 - column))
    if mode in {"vertical", "hv", "all"}:
        transforms.append(lambda row, column: (row0 + row1 - row, column))
    if mode in {"rot180", "hv", "all"}:
        transforms.append(
            lambda row, column: (
                row0 + row1 - row,
                column0 + column1 - column,
            )
        )
    if mode in {"diagonal", "all"}:
        if row1 - row0 != column1 - column0:
            raise ValueError("diagonal closure requires a square packet")
        transforms.append(
            lambda row, column: (
                row0 + column - column0,
                column0 + row - row0,
            )
        )
    if mode in {"anti_diagonal", "all"}:
        if row1 - row0 != column1 - column0:
            raise ValueError("anti-diagonal closure requires a square packet")
        transforms.append(
            lambda row, column: (
                row0 + column1 - column,
                column0 + row1 - row,
            )
        )
    if not transforms:
        raise ValueError(mode)
    return transforms


def graph_complete_local_symmetry_exact(
    grid: Array,
    mode: str,
    scope: str = "global",
    *,
    connectivity: int = 8,
) -> Array:
    """Complete packet-local symmetries without reflecting the whole canvas."""
    grid = sanitize_grid(grid)
    background = infer_bg(grid)
    groups: List[List[Tuple[int, int, int]]] = []
    if scope == "global":
        coordinates = np.argwhere(grid != background)
        if coordinates.size == 0:
            raise ValueError("empty foreground")
        groups.append(
            [
                (int(row), int(column), int(grid[row, column]))
                for row, column in coordinates
            ]
        )
    elif scope == "color":
        for color in sorted(
            int(value) for value in np.unique(grid) if int(value) != background
        ):
            coordinates = np.argwhere(grid == color)
            groups.append(
                [
                    (int(row), int(column), color)
                    for row, column in coordinates
                ]
            )
    elif scope == "component":
        for obj in generic_components(grid, connectivity, True):
            groups.append(
                [
                    (row, column, int(grid[row, column]))
                    for row, column in obj.cells
                ]
            )
    else:
        raise ValueError(scope)

    output = grid.copy()
    changed = 0
    for items in groups:
        rows = [row for row, _, _ in items]
        columns = [column for _, column, _ in items]
        row0, row1 = min(rows), max(rows)
        column0, column1 = min(columns), max(columns)
        transforms = _graph_symmetry_transforms(
            mode,
            row0,
            column0,
            row1,
            column1,
        )
        closure: Dict[Tuple[int, int], int] = {
            (row, column): color for row, column, color in items
        }
        for _ in range(4):
            additions: Dict[Tuple[int, int], int] = {}
            for (row, column), color in list(closure.items()):
                for transform in transforms:
                    target = transform(row, column)
                    existing = closure.get(target)
                    if existing is not None and existing != color:
                        raise ValueError("symmetry closure has a color conflict")
                    additions[target] = color
            previous_size = len(closure)
            closure.update(additions)
            if len(closure) == previous_size:
                break
        for (row, column), color in closure.items():
            if not (0 <= row < grid.shape[0] and 0 <= column < grid.shape[1]):
                raise ValueError("local symmetry leaves canvas")
            current = int(output[row, column])
            if current not in {background, color}:
                raise ValueError("local symmetry collides with another color")
            if current != color:
                output[row, column] = int(color)
                changed += 1
    if changed == 0:
        raise ValueError("local symmetry produced no change")
    return output


def graph_repeat_motif_from_corner_guide_exact(
    grid: Array,
    axis: str = "vertical",
    corner_policy: str = "start",
    *,
    connectivity: int = 4,
) -> Array:
    """Use a corner guide packet to tile its adjacent motif to the boundary."""
    grid = sanitize_grid(grid)
    background = infer_bg(grid)
    objects = generic_components(grid, connectivity, True)
    if axis == "vertical":
        if corner_policy == "start":
            guides = [
                obj
                for obj in objects
                if obj.bbox[0] == 0
                and obj.bbox[1] == 0
                and obj.width == 1
                and obj.size == obj.height
            ]
        elif corner_policy == "end":
            guides = [
                obj
                for obj in objects
                if obj.bbox[0] == 0
                and obj.bbox[3] == grid.shape[1] - 1
                and obj.width == 1
                and obj.size == obj.height
            ]
        else:
            raise ValueError(corner_policy)
    elif axis == "horizontal":
        if corner_policy == "start":
            guides = [
                obj
                for obj in objects
                if obj.bbox[0] == 0
                and obj.bbox[1] == 0
                and obj.height == 1
                and obj.size == obj.width
            ]
        elif corner_policy == "end":
            guides = [
                obj
                for obj in objects
                if obj.bbox[2] == grid.shape[0] - 1
                and obj.bbox[1] == 0
                and obj.height == 1
                and obj.size == obj.width
            ]
        else:
            raise ValueError(corner_policy)
    else:
        raise ValueError(axis)
    if len(guides) != 1:
        raise ValueError("corner guide is not unique")
    guide = guides[0]
    output = grid.copy()

    if axis == "vertical":
        period = guide.height
        motif = grid[:period, :].copy()
        for row, column in guide.cells:
            motif[row, column] = background
        foreground = grid != background
        for row, column in guide.cells:
            foreground[row, column] = False
        coordinates = np.argwhere(foreground)
        if coordinates.size == 0:
            raise ValueError("guide has no adjacent motif")
        start = int(coordinates[:, 0].max()) + 1
        if start >= grid.shape[0]:
            raise ValueError("no vertical tail to fill")
        for row in range(start, grid.shape[0]):
            if bool(np.any(output[row] != background)):
                raise ValueError("vertical motif tail is not empty")
            output[row] = motif[(row - start) % period]
    else:
        period = guide.width
        motif = grid[:, :period].copy()
        for row, column in guide.cells:
            motif[row, column] = background
        foreground = grid != background
        for row, column in guide.cells:
            foreground[row, column] = False
        coordinates = np.argwhere(foreground)
        if coordinates.size == 0:
            raise ValueError("guide has no adjacent motif")
        start = int(coordinates[:, 1].max()) + 1
        if start >= grid.shape[1]:
            raise ValueError("no horizontal tail to fill")
        for column in range(start, grid.shape[1]):
            if bool(np.any(output[:, column] != background)):
                raise ValueError("horizontal motif tail is not empty")
            output[:, column] = motif[:, (column - start) % period]

    if exact(output, grid):
        raise ValueError("guided motif repetition produced no change")
    return output


def _graph_object_shape_signature(obj: Obj) -> Tuple[Tuple[int, ...], ...]:
    cells = set(obj.cells)
    row0, column0, _, _ = obj.bbox
    return tuple(
        tuple(
            1 if (row0 + row, column0 + column) in cells else 0
            for column in range(obj.width)
        )
        for row in range(obj.height)
    )


def _graph_object_stencil_key(
    obj: Obj,
    mode: str,
) -> object:
    shape = _graph_object_shape_signature(obj)
    if mode == "color":
        return (int(obj.color),)
    if mode == "shape":
        return shape
    if mode == "color_shape":
        return (int(obj.color), shape)
    if mode == "color_size":
        return (int(obj.color), obj.size, obj.height, obj.width)
    raise ValueError(mode)


def _graph_distance_to_object(
    row: int,
    column: int,
    obj: Obj,
    metric: str,
) -> int:
    if metric == "chebyshev":
        return min(
            max(abs(row - object_row), abs(column - object_column))
            for object_row, object_column in obj.cells
        )
    if metric == "manhattan":
        return min(
            abs(row - object_row) + abs(column - object_column)
            for object_row, object_column in obj.cells
        )
    raise ValueError(metric)


def _learn_graph_object_stencil_candidate(
    train: List[Tuple[Array, Array]],
    tests: List[Array],
    *,
    radius: int,
    metric: str,
    key_mode: str,
    connectivity: int,
) -> Optional[RuleCandidate]:
    """Learn translation-equivariant residual stencils around object packets."""
    records: Dict[object, List[Tuple[Tuple[int, int, int], ...]]] = defaultdict(list)
    example_records: List[Dict[object, Tuple[Tuple[int, int, int], ...]]] = []
    for input_grid, target in train:
        if input_grid.shape != target.shape:
            return None
        objects = generic_components(input_grid, connectivity, True)
        if not objects:
            return None
        assignments: Dict[int, List[Tuple[int, int, int]]] = {
            id(obj): [] for obj in objects
        }
        for row, column in np.argwhere(input_grid != target):
            row = int(row)
            column = int(column)
            distances = [
                (_graph_distance_to_object(row, column, obj, metric), obj)
                for obj in objects
            ]
            minimum = min(distance for distance, _ in distances)
            nearest = [obj for distance, obj in distances if distance == minimum]
            if minimum > radius or len(nearest) != 1:
                return None
            obj = nearest[0]
            row0, column0, _, _ = obj.bbox
            assignments[id(obj)].append(
                (row - row0, column - column0, int(target[row, column]))
            )
        local_records: Dict[object, List[Tuple[Tuple[int, int, int], ...]]] = defaultdict(list)
        for obj in objects:
            key = _graph_object_stencil_key(obj, key_mode)
            stencil = tuple(sorted(assignments[id(obj)]))
            records[key].append(stencil)
            local_records[key].append(stencil)
        collapsed_local: Dict[object, Tuple[Tuple[int, int, int], ...]] = {}
        for key, observed in local_records.items():
            if len(set(observed)) != 1:
                return None
            collapsed_local[key] = observed[0]
        example_records.append(collapsed_local)

    mapping: Dict[object, Tuple[Tuple[int, int, int], ...]] = {}
    for key, observed in records.items():
        if len(set(observed)) != 1:
            return None
        mapping[key] = observed[0]
    if not any(mapping.values()):
        return None

    def apply_mapping(
        grid: Array,
        active_mapping: Dict[object, Tuple[Tuple[int, int, int], ...]],
    ) -> Array:
        grid = sanitize_grid(grid)
        output = grid.copy()
        pending: Dict[Tuple[int, int], int] = {}
        for obj in generic_components(grid, connectivity, True):
            stencil = active_mapping.get(_graph_object_stencil_key(obj, key_mode))
            if stencil is None:
                continue
            row0, column0, _, _ = obj.bbox
            for delta_row, delta_column, color in stencil:
                row = row0 + delta_row
                column = column0 + delta_column
                if not (0 <= row < grid.shape[0] and 0 <= column < grid.shape[1]):
                    raise ValueError("object stencil leaves canvas")
                previous = pending.get((row, column))
                if previous is not None and previous != color:
                    raise ValueError("object stencils disagree")
                pending[(row, column)] = color
        for (row, column), color in pending.items():
            output[row, column] = int(color)
        return output

    def apply(grid: Array) -> Array:
        return apply_mapping(grid, mapping)

    train_predictions = tuple(apply(input_grid) for input_grid, _ in train)
    if not all(
        exact(prediction, target)
        for prediction, (_, target) in zip(train_predictions, train)
    ):
        return None
    test_predictions = [apply(test) for test in tests]
    nonidentity_groups: Dict[Tuple[str, str], List[int]] = defaultdict(list)
    for example_index, (source, target) in enumerate(train):
        if not exact(source, target):
            nonidentity_groups[(canonical(source), canonical(target))].append(
                example_index
            )
    loo_exact_count = 0
    for held_indices in nonidentity_groups.values():
        held_set = set(held_indices)
        fold_records: Dict[
            object,
            List[Tuple[Tuple[int, int, int], ...]],
        ] = defaultdict(list)
        for example_index, local in enumerate(example_records):
            if example_index in held_set:
                continue
            for key, stencil in local.items():
                fold_records[key].append(stencil)
        fold_mapping: Dict[object, Tuple[Tuple[int, int, int], ...]] = {}
        for key, observed in fold_records.items():
            if len(set(observed)) == 1:
                fold_mapping[key] = observed[0]
        group_exact = True
        for held_index in held_indices:
            held_source, held_target = train[held_index]
            try:
                held_prediction = apply_mapping(held_source, fold_mapping)
            except ValueError:
                group_exact = False
                break
            if not exact(held_prediction, held_target):
                group_exact = False
                break
        loo_exact_count += int(group_exact)
    nonempty_key_supports = [
        sum(
            int(
                any(
                    example_records[index].get(key) == stencil
                    for index in indices
                )
            )
            for indices in nonidentity_groups.values()
        )
        for key, stencil in mapping.items()
        if stencil
    ]
    minimum_nonempty_key_support = (
        min(nonempty_key_supports) if nonempty_key_supports else 0
    )
    complexity = (
        12
        + radius
        + (2 if metric == "manhattan" else 0)
        + len(mapping)
        + sum(len(stencil) for stencil in mapping.values())
    )
    return RuleCandidate(
        name=f"graph_object_stencil_{key_mode}_{metric}_r{radius}_c{connectivity}",
        grids=test_predictions,
        train_error=0,
        complexity=complexity,
        family=f"graph_object_stencil_{key_mode}",
        train_grids=train_predictions,
        metadata={
            "graph_rewrite_block": "object_centered_residual_stencil",
            "key_mode": key_mode,
            "metric": metric,
            "radius": radius,
            "connectivity": connectivity,
            "mapping_size": len(mapping),
            "changed_offsets": sum(len(stencil) for stencil in mapping.values()),
            "translation_equivariant": True,
            "exact_demonstration_contract": True,
            "witness_protocol": (
                "leave_one_distinct_nonidentity_group_out_reinduction"
            ),
            "loo_exact_count": int(loo_exact_count),
            "loo_total_count": int(len(nonidentity_groups)),
            "loo_exact_rate": float(
                loo_exact_count / max(1, len(nonidentity_groups))
            ),
            "distinct_nonidentity_group_count": int(len(nonidentity_groups)),
            "minimum_nonempty_key_group_support": int(
                minimum_nonempty_key_support
            ),
            "witness_reconstructible": bool(
                len(nonidentity_groups) >= 2
                and loo_exact_count == len(nonidentity_groups)
            ),
        },
    )


def graph_object_stencil_rules(
    train: List[Tuple[Array, Array]],
    tests: List[Array],
) -> List[RuleCandidate]:
    output: List[RuleCandidate] = []
    if not train or not all(input_grid.shape == target.shape for input_grid, target in train):
        return output
    for radius in (1, 2, 3, 4):
        for metric in ("chebyshev", "manhattan"):
            for key_mode in ("color", "color_size", "color_shape", "shape"):
                for connectivity in (4, 8):
                    try:
                        candidate = _learn_graph_object_stencil_candidate(
                            train,
                            tests,
                            radius=radius,
                            metric=metric,
                            key_mode=key_mode,
                            connectivity=connectivity,
                        )
                    except Exception:
                        candidate = None
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


def graph_rewrite_rules(
    train: List[Tuple[Array, Array]],
    tests: List[Array],
) -> List[RuleCandidate]:
    """Typed multistage graph rewrites and conditional path constructions."""
    if not train:
        return []
    output: List[RuleCandidate] = []
    same_shape = all(input_grid.shape == target.shape for input_grid, target in train)
    candidate_colors = _output_candidate_colors(train)
    if same_shape:
        for geometry in ("straight", "orthogonal_hv", "orthogonal_vh"):
            for collision_policy in (
                "vertical_over_horizontal",
                "horizontal_over_vertical",
                "minimum_color",
                "maximum_color",
                "preserve_existing",
            ):
                for singletons in (True, False):
                    _try_exact_rule(
                        output,
                        train,
                        tests,
                        f"graph_connect_{geometry}_{collision_policy}_{int(singletons)}",
                        lambda grid, geom=geometry, policy=collision_policy, singles=singletons: graph_connect_color_pairs_exact(
                            grid,
                            geom,
                            policy,
                            require_singletons=singles,
                            connectivity=4,
                        ),
                        10 + (2 if geometry != "straight" else 0),
                        "graph_path_connection",
                        metadata={
                            "graph_rewrite_block": "conditional_pair_connection",
                            "geometry": geometry,
                            "collision_policy": collision_policy,
                            "require_singletons": singletons,
                            "exact_demonstration_contract": True,
                        },
                    )

        for output_color in candidate_colors[:6]:
            for direction in ("top", "bottom", "left", "right"):
                for coordinate_policy in ("center_floor", "center_ceil", "minimum", "maximum"):
                    for object_policy in ("non_singleton", "hollow", "all"):
                        _try_exact_rule(
                            output,
                            train,
                            tests,
                            f"graph_boundary_projection_{direction}_{output_color}_{coordinate_policy}_{object_policy}",
                            lambda grid, d=direction, color=output_color, coordinate=coordinate_policy, objects=object_policy: graph_project_objects_to_boundary_exact(
                                grid,
                                d,
                                color,
                                coordinate,
                                connectivity=4,
                                object_policy=objects,
                            ),
                            9,
                            "graph_boundary_projection",
                            metadata={
                                "graph_rewrite_block": "object_to_boundary_projection",
                                "direction": direction,
                                "output_color": output_color,
                                "coordinate_policy": coordinate_policy,
                                "object_policy": object_policy,
                                "exact_demonstration_contract": True,
                            },
                        )

        for distance_mode in ("manhattan", "chebyshev"):
            for tie_policy in ("reading_order", "reverse_reading", "clockwise"):
                for object_policy in ("single_object", "singletons", "all"):
                    _try_exact_rule(
                        output,
                        train,
                        tests,
                        f"graph_corner_fill_{distance_mode}_{tie_policy}_{object_policy}",
                        lambda grid, distance=distance_mode, tie=tie_policy, objects=object_policy: graph_fill_objects_to_nearest_corner_exact(
                            grid,
                            distance,
                            tie,
                            connectivity=4,
                            object_policy=objects,
                        ),
                        8,
                        "graph_corner_expansion",
                        metadata={
                            "graph_rewrite_block": "nearest_corner_expansion",
                            "distance_mode": distance_mode,
                            "tie_policy": tie_policy,
                            "object_policy": object_policy,
                            "exact_demonstration_contract": True,
                        },
                    )

        for center_color in candidate_colors[:6]:
            for final_leg in (1, 2, 3):
                _try_exact_rule(
                    output,
                    train,
                    tests,
                    f"graph_triangle_contract_{center_color}_{final_leg}",
                    lambda grid, color=center_color, leg=final_leg: graph_contract_right_triangle_exact(
                        grid,
                        color,
                        leg,
                        connectivity=4,
                    ),
                    12,
                    "graph_triangle_contraction",
                    metadata={
                        "graph_rewrite_block": "right_triangle_contraction",
                        "center_color": center_color,
                        "terminal_leg": final_leg,
                        "exact_demonstration_contract": True,
                    },
                )

        for connectivity in (4, 8):
            for vector_policy in ("maximum", "minimum"):
                for collision_policy in ("background_only", "overwrite_markers"):
                    _try_exact_rule(
                        output,
                        train,
                        tests,
                        f"graph_template_rays_c{connectivity}_{vector_policy}_{collision_policy}",
                        lambda grid, conn=connectivity, vector=vector_policy, collision=collision_policy: graph_repeat_template_along_marker_rays_exact(
                            grid,
                            vector,
                            collision,
                            connectivity=conn,
                        ),
                        15,
                        "graph_template_ray_rewrite",
                        metadata={
                            "graph_rewrite_block": "template_ray_completion",
                            "connectivity": connectivity,
                            "vector_policy": vector_policy,
                            "collision_policy": collision_policy,
                            "multistage": [
                                "select_unique_largest_template",
                                "match_marker_to_template_subset",
                                "infer_translation_vector",
                                "complete_near_copy",
                                "iterate_to_boundary",
                            ],
                            "exact_demonstration_contract": True,
                        },
                    )


        for scope in ("global", "color", "component"):
            for mode in (
                "horizontal",
                "vertical",
                "rot180",
                "hv",
                "diagonal",
                "anti_diagonal",
                "all",
            ):
                _try_exact_rule(
                    output,
                    train,
                    tests,
                    f"graph_local_symmetry_{scope}_{mode}",
                    lambda grid, symmetry=mode, symmetry_scope=scope: graph_complete_local_symmetry_exact(
                        grid,
                        symmetry,
                        symmetry_scope,
                        connectivity=8,
                    ),
                    10,
                    "graph_local_symmetry",
                    metadata={
                        "graph_rewrite_block": "packet_local_symmetry_closure",
                        "scope": scope,
                        "mode": mode,
                        "exact_demonstration_contract": True,
                    },
                )

        for axis in ("vertical", "horizontal"):
            for corner_policy in ("start", "end"):
                _try_exact_rule(
                    output,
                    train,
                    tests,
                    f"graph_guide_repeat_{axis}_{corner_policy}",
                    lambda grid, repeat_axis=axis, corner=corner_policy: graph_repeat_motif_from_corner_guide_exact(
                        grid,
                        repeat_axis,
                        corner,
                        connectivity=4,
                    ),
                    11,
                    "graph_guided_motif_repetition",
                    metadata={
                        "graph_rewrite_block": "corner_guide_motif_repetition",
                        "axis": axis,
                        "corner_policy": corner_policy,
                        "exact_demonstration_contract": True,
                    },
                )

        output.extend(graph_object_stencil_rules(train, tests))

    deduplicated: List[RuleCandidate] = []
    seen: set[Tuple[str, ...]] = set()
    for candidate in sorted(output, key=lambda item: (item.complexity, item.family, item.name)):
        signature = tuple(canonical(grid) for grid in candidate.grids)
        if signature in seen:
            continue
        seen.add(signature)
        deduplicated.append(candidate)
    return deduplicated



# ---------------- obstacle routing and bounded recursive construction ----------------

_ROUTE_ORDERS: Dict[str, Tuple[Tuple[int, int], ...]] = {
    "udlr": ((-1, 0), (1, 0), (0, -1), (0, 1)),
    "lrud": ((0, -1), (0, 1), (-1, 0), (1, 0)),
    "rdlu": ((0, 1), (1, 0), (0, -1), (-1, 0)),
    "dlur": ((1, 0), (0, -1), (-1, 0), (0, 1)),
}


def _shortest_background_path(
    grid: Array,
    start: Tuple[int, int],
    goal: Tuple[int, int],
    *,
    neighbor_order: str = "udlr",
    turn_cost: int = 0,
    passable_colors: Optional[Sequence[int]] = None,
) -> List[Tuple[int, int]]:
    """Return a deterministic shortest path through passable cells.

    Nonpassable nonbackground cells are protected obstacles. Start and goal
    are always legal. A positive turn cost breaks equal-length ties in favor
    of fewer bends. It never selects a longer route merely to avoid a turn.
    """
    grid = sanitize_grid(grid)
    if neighbor_order not in _ROUTE_ORDERS:
        raise ValueError("unknown route order")
    height, width = grid.shape
    if not (0 <= start[0] < height and 0 <= start[1] < width):
        raise ValueError("route start outside grid")
    if not (0 <= goal[0] < height and 0 <= goal[1] < width):
        raise ValueError("route goal outside grid")
    background = infer_bg(grid)
    passable = {int(background)}
    if passable_colors is not None:
        passable.update(int(value) for value in passable_colors)

    # State includes incoming direction so the lexicographic objective
    # (steps, weighted bends) remains deterministic.
    start_state = (int(start[0]), int(start[1]), -1)
    queue: List[Tuple[int, int, int, int, int, int]] = [(0, 0, 0, *start_state)]
    distance: Dict[Tuple[int, int, int], Tuple[int, int]] = {start_state: (0, 0)}
    parent: Dict[Tuple[int, int, int], Optional[Tuple[int, int, int]]] = {start_state: None}
    final: Optional[Tuple[int, int, int]] = None
    serial = 0
    directions = _ROUTE_ORDERS[neighbor_order]
    while queue:
        steps, bend_score, _, row, column, incoming = heapq.heappop(queue)
        state = (row, column, incoming)
        recorded = distance.get(state)
        if recorded is None or (steps, bend_score) != recorded:
            continue
        if (row, column) == goal:
            final = state
            break
        for direction_index, (dr, dc) in enumerate(directions):
            nr, nc = row + dr, column + dc
            if not (0 <= nr < height and 0 <= nc < width):
                continue
            if (nr, nc) not in {start, goal} and int(grid[nr, nc]) not in passable:
                continue
            bend = int(incoming >= 0 and incoming != direction_index)
            next_steps = steps + 1
            next_bend_score = bend_score + max(0, int(turn_cost)) * bend
            next_state = (nr, nc, direction_index)
            prior = distance.get(next_state)
            if prior is not None and prior <= (next_steps, next_bend_score):
                continue
            distance[next_state] = (next_steps, next_bend_score)
            parent[next_state] = state
            serial += 1
            heapq.heappush(
                queue,
                (next_steps, next_bend_score, serial, nr, nc, direction_index),
            )
    if final is None:
        raise ValueError("no collision-free route")
    path: List[Tuple[int, int]] = []
    cursor: Optional[Tuple[int, int, int]] = final
    while cursor is not None:
        path.append((cursor[0], cursor[1]))
        cursor = parent[cursor]
    path.reverse()
    return path


def _routing_marker_pairs(grid: Array, pairing: str) -> List[Tuple[Obj, Obj]]:
    grid = sanitize_grid(grid)
    background = infer_bg(grid)
    singleton_objects = [
        obj
        for obj in generic_components(grid, connectivity=4, separate_colors=True)
        if obj.size == 1 and int(obj.color) != int(background)
    ]
    if pairing == "same_color":
        by_color: Dict[int, List[Obj]] = defaultdict(list)
        for obj in singleton_objects:
            by_color[int(obj.color)].append(obj)
        pairs: List[Tuple[Obj, Obj]] = []
        for color in sorted(by_color):
            objects = sorted(by_color[color], key=lambda item: item.cells[0])
            if len(objects) == 2:
                pairs.append((objects[0], objects[1]))
        if not pairs:
            raise ValueError("no same-color singleton pair")
        return pairs
    if pairing == "rarest_pair":
        counts = Counter(int(value) for value in grid.ravel() if int(value) != int(background))
        eligible = sorted(
            singleton_objects,
            key=lambda obj: (counts[int(obj.color)], int(obj.color), obj.cells[0]),
        )
        if len(eligible) != 2:
            raise ValueError("rarest-pair contract requires exactly two singleton markers")
        return [(eligible[0], eligible[1])]
    if pairing == "reading_pairs":
        objects = sorted(singleton_objects, key=lambda item: item.cells[0])
        if len(objects) < 2 or len(objects) % 2:
            raise ValueError("reading-pair contract requires an even singleton count")
        return [(objects[index], objects[index + 1]) for index in range(0, len(objects), 2)]
    raise ValueError(pairing)


def draw_obstacle_path_exact(
    grid: Array,
    pairing: str = "same_color",
    *,
    line_color: Optional[int] = None,
    neighbor_order: str = "udlr",
    turn_cost: int = 0,
    endpoint_policy: str = "preserve",
) -> Array:
    """Connect marker pairs by deterministic obstacle-avoiding paths."""
    source = sanitize_grid(grid)
    output = source.copy()
    background = infer_bg(source)
    pairs = _routing_marker_pairs(source, pairing)
    for left, right in pairs:
        start, goal = left.cells[0], right.cells[0]
        color = int(left.color if line_color is None else line_color)
        path = _shortest_background_path(
            output,
            start,
            goal,
            neighbor_order=neighbor_order,
            turn_cost=turn_cost,
        )
        for row, column in path[1:-1]:
            if int(output[row, column]) != int(background):
                raise ValueError("route crossed a protected obstacle")
            output[row, column] = color
        if endpoint_policy == "line_color":
            output[start] = color
            output[goal] = color
        elif endpoint_policy == "erase":
            output[start] = int(background)
            output[goal] = int(background)
        elif endpoint_policy != "preserve":
            raise ValueError(endpoint_policy)
    return output


def obstacle_path_rules(
    train: List[Tuple[Array, Array]],
    tests: List[Array],
) -> List[RuleCandidate]:
    """Exact-fit shortest-path proposals with explicit collision semantics."""
    output: List[RuleCandidate] = []
    if not train or not all(source.shape == target.shape for source, target in train):
        return output
    if all(exact(source, target) for source, target in train):
        return output
    # Routing is only plausible when every demonstration exposes at least two
    # singleton endpoints and the residual is sparse enough to represent a
    # path rather than a global rewrite.
    for source, target in train:
        singletons = [
            obj
            for obj in generic_components(source, connectivity=4, separate_colors=True)
            if obj.size == 1 and int(obj.color) != infer_bg(source)
        ]
        changed = int(np.count_nonzero(source != target))
        if len(singletons) < 2 or changed == 0 or changed > max(12, source.size // 2):
            return output
    colors = _output_candidate_colors(train)
    line_colors: List[Optional[int]] = [None] + colors[:4]
    for pairing in ("same_color", "rarest_pair", "reading_pairs"):
        for order in sorted(_ROUTE_ORDERS):
            for turn_cost in (0, 4):
                for line_color in line_colors:
                    for endpoint_policy in ("preserve", "line_color", "erase"):
                        _try_exact_rule(
                            output,
                            train,
                            tests,
                            f"obstacle_route_{pairing}_{order}_t{turn_cost}_{line_color}_{endpoint_policy}",
                            lambda grid, p=pairing, color=line_color, tie=order, bends=turn_cost, endpoints=endpoint_policy: draw_obstacle_path_exact(
                                grid,
                                p,
                                line_color=color,
                                neighbor_order=tie,
                                turn_cost=bends,
                                endpoint_policy=endpoints,
                            ),
                            10 + int(turn_cost > 0),
                            "routing_obstacle_path",
                            metadata={
                                "composition_block": "obstacle_aware_routing",
                                "pairing": pairing,
                                "neighbor_order": order,
                                "turn_cost": turn_cost,
                                "line_color": line_color,
                                "endpoint_policy": endpoint_policy,
                                "collision_aware": True,
                                "translation_equivariant": True,
                                "exact_demonstration_contract": True,
                            },
                        )
    return deduplicate_prediction_grids(output)


def _recursive_shape_groups(grid: Array) -> List[List[Obj]]:
    grid = sanitize_grid(grid)
    background = infer_bg(grid)
    grouped: Dict[Tuple[Tuple[int, ...], ...], List[Obj]] = defaultdict(list)
    for obj in generic_components(grid, connectivity=4, separate_colors=True):
        if int(obj.color) == int(background):
            continue
        grouped[_graph_object_shape_signature(obj)].append(obj)
    groups = [
        sorted(objects, key=lambda obj: (obj.bbox[0], obj.bbox[1], int(obj.color)))
        for objects in grouped.values()
        if len(objects) >= 2
    ]
    groups.sort(key=lambda objects: (-len(objects), -objects[0].size, objects[0].bbox))
    return groups


def _recursive_chain_vector(objects: Sequence[Obj]) -> Tuple[int, int, Dict[Tuple[int, int], Obj]]:
    positions = [(obj.bbox[0], obj.bbox[1]) for obj in objects]
    candidates: set[Tuple[int, int]] = set()
    for index, left in enumerate(positions):
        for right in positions[index + 1 :]:
            dr, dc = right[0] - left[0], right[1] - left[1]
            if dr < 0 or (dr == 0 and dc < 0):
                dr, dc = -dr, -dc
            if (dr, dc) != (0, 0):
                candidates.add((dr, dc))
    lookup = {position: obj for position, obj in zip(positions, objects)}
    for dr, dc in sorted(candidates, key=lambda vector: (vector[0] ** 2 + vector[1] ** 2, vector)):
        anchor = min(positions)
        valid = True
        for row, column in positions:
            delta_row, delta_column = row - anchor[0], column - anchor[1]
            if dr == 0:
                valid &= delta_row == 0 and dc != 0 and delta_column % dc == 0
            elif dc == 0:
                valid &= delta_column == 0 and delta_row % dr == 0
            else:
                valid &= delta_row % dr == 0 and delta_column % dc == 0 and delta_row // dr == delta_column // dc
            if not valid:
                break
        if valid:
            return dr, dc, lookup
    raise ValueError("objects do not define an arithmetic motif chain")


def recursive_motif_extension_exact(
    grid: Array,
    *,
    extent: str = "forward",
    color_policy: str = "cycle",
    group_policy: str = "largest",
) -> Array:
    """Repeat an observed object motif along its inferred arithmetic vector."""
    source = sanitize_grid(grid)
    output = source.copy()
    background = infer_bg(source)
    groups = _recursive_shape_groups(source)
    if not groups:
        raise ValueError("no repeated motif")
    if group_policy == "largest":
        groups = groups[:1]
    elif group_policy != "all":
        raise ValueError(group_policy)
    material_changes = 0
    for objects in groups:
        dr, dc, lookup = _recursive_chain_vector(objects)
        positions = sorted(lookup)
        anchor = positions[0]

        def index_of(position: Tuple[int, int]) -> int:
            if dr == 0:
                return (position[1] - anchor[1]) // dc
            return (position[0] - anchor[0]) // dr

        indexed = sorted((index_of(position), lookup[position]) for position in positions)
        known_indices = [index for index, _ in indexed]
        low, high = min(known_indices), max(known_indices)
        observed_colors = [int(obj.color) for _, obj in indexed]
        if color_policy == "same" and len(set(observed_colors)) != 1:
            raise ValueError("same-color recursive contract failed")

        if extent not in {"gaps", "forward", "backward", "both"}:
            raise ValueError(extent)

        mask_template = objects[0]
        r0, c0, _, _ = mask_template.bbox
        offsets = [(row - r0, column - c0) for row, column in mask_template.cells]
        occupied_known = {position for obj in objects for position in obj.cells}
        def render_indices(indices: Iterable[int], *, stop_on_block: bool) -> None:
            nonlocal material_changes
            for chain_index in indices:
                top = anchor[0] + chain_index * dr
                left = anchor[1] + chain_index * dc
                cells = [(top + rr, left + cc) for rr, cc in offsets]
                outside = any(
                    row < 0
                    or row >= source.shape[0]
                    or column < 0
                    or column >= source.shape[1]
                    for row, column in cells
                )
                collision = not outside and any(
                    int(output[row, column]) != int(background)
                    and (row, column) not in occupied_known
                    for row, column in cells
                )
                if outside or collision:
                    if stop_on_block:
                        break
                    continue
                if chain_index in known_indices:
                    continue
                if color_policy == "cycle":
                    color = observed_colors[(chain_index - low) % len(observed_colors)]
                elif color_policy == "repeat_last":
                    color = observed_colors[-1] if chain_index > high else observed_colors[0]
                elif color_policy == "same":
                    color = observed_colors[0]
                else:
                    raise ValueError(color_policy)
                for row, column in cells:
                    output[row, column] = int(color)
                material_changes += 1

        if extent in {"gaps", "both"}:
            render_indices(range(low, high + 1), stop_on_block=False)
        if extent in {"forward", "both"}:
            render_indices(
                range(high + 1, high + 1 + source.size),
                stop_on_block=True,
            )
        if extent in {"backward", "both"}:
            render_indices(
                range(low - 1, low - 1 - source.size, -1),
                stop_on_block=True,
            )
    if material_changes == 0:
        raise ValueError("recursive motif made no change")
    return output


def recursive_neighbor_growth_exact(
    grid: Array,
    seed_color: int,
    *,
    connectivity: int = 4,
    threshold: int = 1,
    iterations: int = 0,
) -> Array:
    """Grow a colored frontier synchronously for a bounded number of steps.

    iterations=0 means fixed point. Other nonbackground colors are protected
    obstacles, and a canonical-state set rejects cycles.
    """
    source = sanitize_grid(grid)
    output = source.copy()
    background = infer_bg(source)
    if int(seed_color) == int(background) or not np.any(output == int(seed_color)):
        raise ValueError("missing recursive seed")
    directions = list(_ROUTE_ORDERS["udlr"])
    if connectivity == 8:
        directions += [(-1, -1), (-1, 1), (1, -1), (1, 1)]
    elif connectivity != 4:
        raise ValueError(connectivity)
    seen = {canonical(output)}
    changed_steps = 0
    maximum = int(iterations) if int(iterations) > 0 else int(output.size)
    for _ in range(maximum):
        births: List[Tuple[int, int]] = []
        for row in range(output.shape[0]):
            for column in range(output.shape[1]):
                if int(output[row, column]) != int(background):
                    continue
                count = sum(
                    0 <= row + dr < output.shape[0]
                    and 0 <= column + dc < output.shape[1]
                    and int(output[row + dr, column + dc]) == int(seed_color)
                    for dr, dc in directions
                )
                if count == int(threshold):
                    births.append((row, column))
        if not births:
            break
        for row, column in births:
            output[row, column] = int(seed_color)
        changed_steps += 1
        key = canonical(output)
        if key in seen:
            raise ValueError("recursive growth cycle")
        seen.add(key)
    if changed_steps == 0:
        raise ValueError("recursive growth made no change")
    return output


def recursive_construction_rules(
    train: List[Tuple[Array, Array]],
    tests: List[Array],
) -> List[RuleCandidate]:
    """Exact bounded repeat-until proposals for motifs and local frontiers."""
    output: List[RuleCandidate] = []
    if not train or not all(source.shape == target.shape for source, target in train):
        return output
    if all(exact(source, target) for source, target in train):
        return output
    motif_possible = all(bool(_recursive_shape_groups(source)) for source, _ in train)
    if motif_possible:
        for extent in ("gaps", "forward", "backward", "both"):
            for color_policy in ("cycle", "repeat_last", "same"):
                for group_policy in ("largest", "all"):
                    _try_exact_rule(
                        output,
                        train,
                        tests,
                        f"recursive_motif_{extent}_{color_policy}_{group_policy}",
                        lambda grid, ex=extent, colors=color_policy, groups=group_policy: recursive_motif_extension_exact(
                            grid,
                            extent=ex,
                            color_policy=colors,
                            group_policy=groups,
                        ),
                        11,
                        "recursive_motif_extension",
                        metadata={
                            "composition_block": "bounded_recursive_construction",
                            "repeat_stop": "boundary_or_collision",
                            "extent": extent,
                            "color_policy": color_policy,
                            "group_policy": group_policy,
                            "recursive": True,
                            "translation_equivariant": True,
                            "exact_demonstration_contract": True,
                        },
                    )
    growth_possible = all(
        np.all(~_foreground_mask(source) | _foreground_mask(target))
        for source, target in train
    )
    if not growth_possible:
        return deduplicate_prediction_grids(output)
    common_colors = sorted(
        set.intersection(
            *(
                {int(value) for value in np.unique(source) if int(value) != infer_bg(source)}
                for source, _ in train
            )
        )
    )
    for seed_color in common_colors[:6]:
        for connectivity in (4, 8):
            for threshold in (1, 2, 3):
                for iterations in (1, 2, 3, 0):
                    _try_exact_rule(
                        output,
                        train,
                        tests,
                        f"recursive_growth_{seed_color}_c{connectivity}_n{threshold}_i{iterations}",
                        lambda grid, color=seed_color, conn=connectivity, count=threshold, steps=iterations: recursive_neighbor_growth_exact(
                            grid,
                            color,
                            connectivity=conn,
                            threshold=count,
                            iterations=steps,
                        ),
                        9 + int(iterations == 0),
                        "recursive_frontier_growth",
                        metadata={
                            "composition_block": "bounded_recursive_construction",
                            "seed_color": seed_color,
                            "connectivity": connectivity,
                            "neighbor_threshold": threshold,
                            "repeat_stop": "fixed_point" if iterations == 0 else "bounded_steps",
                            "max_repeat_steps": iterations,
                            "recursive": True,
                            "exact_demonstration_contract": True,
                        },
                    )
    return deduplicate_prediction_grids(output)



# ---------------- relational object transport proposal channel ----------------

def _transport_color_objects(grid: Array, color: int, connectivity: int = 4) -> List[Obj]:
    """Return monochrome objects of one color under the requested connectivity."""
    return [
        obj
        for obj in generic_components(grid, connectivity=connectivity, separate_colors=True)
        if int(obj.color) == int(color)
    ]


def _transport_bbox_gap(left: Obj, right: Obj) -> Tuple[int, int]:
    """Nonnegative row and column separation between two bounding boxes."""
    row_gap = max(0, right.bbox[0] - left.bbox[2] - 1, left.bbox[0] - right.bbox[2] - 1)
    col_gap = max(0, right.bbox[1] - left.bbox[3] - 1, left.bbox[1] - right.bbox[3] - 1)
    return int(row_gap), int(col_gap)


def _transport_object_center(obj: Obj) -> Tuple[float, float]:
    return (
        0.5 * float(obj.bbox[0] + obj.bbox[2]),
        0.5 * float(obj.bbox[1] + obj.bbox[3]),
    )


def _transport_choose_anchor(mover: Obj, anchors: Sequence[Obj]) -> Obj:
    if not anchors:
        raise ValueError("no transport anchor")
    mr, mc = _transport_object_center(mover)
    return min(
        anchors,
        key=lambda anchor: (
            sum(_transport_bbox_gap(mover, anchor)),
            abs(_transport_object_center(anchor)[0] - mr)
            + abs(_transport_object_center(anchor)[1] - mc),
            anchor.bbox,
        ),
    )


def _transport_direction(
    mover: Obj,
    anchor: Obj,
    policy: str,
) -> Tuple[int, int]:
    """Infer a cardinal or diagonal transport direction toward an anchor."""
    mr, mc = _transport_object_center(mover)
    ar, ac = _transport_object_center(anchor)
    sr = int(np.sign(ar - mr))
    sc = int(np.sign(ac - mc))

    row_overlap = not (mover.bbox[2] < anchor.bbox[0] or anchor.bbox[2] < mover.bbox[0])
    col_overlap = not (mover.bbox[3] < anchor.bbox[1] or anchor.bbox[3] < mover.bbox[1])
    row_gap, col_gap = _transport_bbox_gap(mover, anchor)

    if policy == "chebyshev":
        if sr == 0 and sc == 0:
            raise ValueError("coincident transport objects")
        return sr, sc
    if row_overlap and sc != 0:
        return 0, sc
    if col_overlap and sr != 0:
        return sr, 0
    if policy == "horizontal" and sc != 0:
        return 0, sc
    if policy == "vertical" and sr != 0:
        return sr, 0
    if policy == "diagonal" and sr != 0 and sc != 0:
        return sr, sc
    if policy == "nearest_axis":
        if sr != 0 and sc != 0:
            return (sr, 0) if row_gap <= col_gap else (0, sc)
        if sr != 0:
            return sr, 0
        if sc != 0:
            return 0, sc
    if policy == "dominant_axis":
        if sr != 0 and sc != 0:
            return (sr, 0) if abs(ar - mr) >= abs(ac - mc) else (0, sc)
        if sr != 0:
            return sr, 0
        if sc != 0:
            return 0, sc
    raise ValueError("transport direction is ambiguous")


def _transport_object_cells(
    source: Array,
    obj: Obj,
    dr: int,
    dc: int,
) -> List[Tuple[int, int, int]]:
    return [(int(r + dr), int(c + dc), int(source[r, c])) for r, c in obj.cells]


def _transport_cells_valid(
    cells: Sequence[Tuple[int, int, int]],
    shape: Tuple[int, int],
    occupied: Array,
) -> bool:
    height, width = shape
    return all(
        0 <= row < height
        and 0 <= column < width
        and not bool(occupied[row, column])
        for row, column, _ in cells
    )


def _transport_touches_anchor(
    cells: Sequence[Tuple[int, int, int]],
    anchors: Sequence[Obj],
    diagonal: bool,
) -> bool:
    anchor_cells = {(int(r), int(c)) for anchor in anchors for r, c in anchor.cells}
    for row, column, _ in cells:
        for dr, dc in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            if (row + dr, column + dc) in anchor_cells:
                return True
        if diagonal:
            for dr, dc in ((1, 1), (1, -1), (-1, 1), (-1, -1)):
                if (row + dr, column + dc) in anchor_cells:
                    return True
    return False


def transport_color_relation_exact(
    grid: Array,
    moving_color: int,
    anchor_color: int,
    mode: str,
    direction_policy: str = "nearest_axis",
    connectivity: int = 4,
) -> Array:
    """Move one color's rigid objects toward the nearest anchor color.

    ``mode='contact'`` advances each mover until the next step would collide,
    requiring the final object to touch an anchor. ``mode='step'`` advances one
    Chebyshev or axis-aligned step. All unrelated cells are preserved and every
    placement is collision checked.
    """
    grid = sanitize_grid(grid)
    if int(moving_color) == int(anchor_color):
        raise ValueError("moving and anchor colors must differ")
    background = infer_bg(grid)
    movers = _transport_color_objects(grid, moving_color, connectivity)
    anchors = _transport_color_objects(grid, anchor_color, connectivity)
    if not movers or not anchors:
        raise ValueError("missing mover or anchor")

    output = grid.copy()
    for mover in movers:
        for row, column in mover.cells:
            output[row, column] = background
    occupied = output != background

    ordered = sorted(
        movers,
        key=lambda mover: (
            sum(_transport_bbox_gap(mover, _transport_choose_anchor(mover, anchors))),
            mover.bbox,
        ),
    )
    for mover in ordered:
        anchor = _transport_choose_anchor(mover, anchors)
        dr_step, dc_step = _transport_direction(mover, anchor, direction_policy)
        diagonal = bool(dr_step and dc_step)
        dr = dc = 0
        if mode == "step":
            trial = _transport_object_cells(grid, mover, dr_step, dc_step)
            if not _transport_cells_valid(trial, grid.shape, occupied):
                raise ValueError("transport step is blocked")
            dr, dc = dr_step, dc_step
        elif mode == "contact":
            moved = False
            while True:
                trial = _transport_object_cells(grid, mover, dr + dr_step, dc + dc_step)
                if not _transport_cells_valid(trial, grid.shape, occupied):
                    break
                dr += dr_step
                dc += dc_step
                moved = True
            if not moved:
                raise ValueError("transport object did not move")
            final_cells = _transport_object_cells(grid, mover, dr, dc)
            if not _transport_touches_anchor(final_cells, anchors, diagonal):
                raise ValueError("transport stopped without reaching its anchor")
        else:
            raise ValueError(mode)

        final_cells = _transport_object_cells(grid, mover, dr, dc)
        if not _transport_cells_valid(final_cells, grid.shape, occupied):
            raise ValueError("invalid final transport placement")
        for row, column, color in final_cells:
            output[row, column] = color
            occupied[row, column] = True
    return output


def transport_objects_by_extent_exact(
    grid: Array,
    direction: str,
    connectivity: int = 4,
    separate_colors: bool = False,
    extent_offset: int = 0,
) -> Array:
    """Translate every object by its own bounding-box extent."""
    grid = sanitize_grid(grid)
    background = infer_bg(grid)
    objects = generic_components(grid, connectivity=connectivity, separate_colors=separate_colors)
    if not objects:
        raise ValueError("no objects")
    output = np.full_like(grid, background)
    occupied = np.zeros(grid.shape, dtype=bool)
    for obj in objects:
        amount = (obj.width if direction in {"left", "right"} else obj.height) + int(extent_offset)
        if amount <= 0:
            raise ValueError("nonpositive extent shift")
        dr, dc = {
            "left": (0, -amount),
            "right": (0, amount),
            "up": (-amount, 0),
            "down": (amount, 0),
        }[direction]
        cells = _transport_object_cells(grid, obj, dr, dc)
        if not _transport_cells_valid(cells, grid.shape, occupied):
            raise ValueError("extent transport leaves canvas or collides")
        for row, column, color in cells:
            output[row, column] = color
            occupied[row, column] = True
    return output


def transport_cardinal_markers_exact(grid: Array, keep_sources: bool = False) -> Array:
    """Collapse aligned marker packets onto cardinal neighbors of singleton targets.

    A moving color must have at least two cells and all of its cells must align
    horizontally or vertically with one unique singleton target color. This
    discovers target-marker pairings from each input without using absolute
    colors or coordinates.
    """
    grid = sanitize_grid(grid)
    background = infer_bg(grid)
    color_positions = {
        int(color): [tuple(int(v) for v in point) for point in np.argwhere(grid == int(color))]
        for color in np.unique(grid)
        if int(color) != background
    }
    targets = {color: points[0] for color, points in color_positions.items() if len(points) == 1}
    mappings: Dict[int, Tuple[int, int]] = {}
    for moving_color, points in color_positions.items():
        if len(points) < 2:
            continue
        scored: List[Tuple[int, int, Tuple[int, int]]] = []
        for target_color, target in targets.items():
            if target_color == moving_color:
                continue
            if all(row == target[0] or column == target[1] for row, column in points):
                distance = sum(abs(row - target[0]) + abs(column - target[1]) for row, column in points)
                scored.append((distance, target_color, target))
        if not scored:
            continue
        scored.sort()
        if len(scored) > 1 and scored[0][0] == scored[1][0]:
            continue
        mappings[moving_color] = scored[0][2]
    if not mappings:
        raise ValueError("no cardinal marker-to-target relations")

    output = grid.copy()
    if not keep_sources:
        for moving_color in mappings:
            output[grid == moving_color] = background
    occupied_static = output != background
    destinations: Dict[Tuple[int, int], int] = {}
    for moving_color, target in mappings.items():
        for row, column in color_positions[moving_color]:
            dr = int(np.sign(row - target[0]))
            dc = int(np.sign(column - target[1]))
            if bool(dr) == bool(dc):
                raise ValueError("marker is not cardinally aligned")
            destination = (target[0] + dr, target[1] + dc)
            if not (0 <= destination[0] < grid.shape[0] and 0 <= destination[1] < grid.shape[1]):
                raise ValueError("cardinal destination outside grid")
            existing = destinations.get(destination)
            if existing is not None and existing != moving_color:
                raise ValueError("conflicting marker destinations")
            if occupied_static[destination] and int(output[destination]) != int(moving_color):
                raise ValueError("cardinal destination is occupied")
            destinations[destination] = moving_color
    for (row, column), color in destinations.items():
        output[row, column] = int(color)
    return output



def _transport_color_group(grid: Array, color: int) -> Obj:
    points = [tuple(int(v) for v in point) for point in np.argwhere(sanitize_grid(grid) == int(color))]
    if not points:
        raise ValueError("missing color group")
    rows = [point[0] for point in points]
    columns = [point[1] for point in points]
    return Obj(int(color), points, (min(rows), min(columns), max(rows), max(columns)))


def _transport_global_color_vector(left: Array, right: Array, color: int) -> Optional[Tuple[int, int]]:
    left_points = [tuple(int(v) for v in point) for point in np.argwhere(left == int(color))]
    right_points = {tuple(int(v) for v in point) for point in np.argwhere(right == int(color))}
    if not left_points or len(left_points) != len(right_points):
        return None
    origin = left_points[0]
    for target in right_points:
        dr, dc = target[0] - origin[0], target[1] - origin[1]
        if {(row + dr, column + dc) for row, column in left_points} == right_points:
            return int(dr), int(dc)
    return None


def transport_color_vector_map_exact(grid: Array, vectors: Dict[int, Tuple[int, int]]) -> Array:
    grid = sanitize_grid(grid)
    background = infer_bg(grid)
    output = np.full_like(grid, background)
    occupied = np.zeros(grid.shape, dtype=bool)
    colors = {int(value) for value in np.unique(grid) if int(value) != background}
    if not colors.issubset(vectors):
        raise ValueError("unseen transport color")
    for color in sorted(colors):
        dr, dc = vectors[color]
        for row, column in np.argwhere(grid == color):
            nr, nc = int(row) + dr, int(column) + dc
            if not (0 <= nr < grid.shape[0] and 0 <= nc < grid.shape[1]) or occupied[nr, nc]:
                raise ValueError("color-vector transport collision")
            output[nr, nc] = color
            occupied[nr, nc] = True
    return output


def transport_color_vector_map_rules(
    train: List[Tuple[Array, Array]],
    tests: List[Array],
) -> List[RuleCandidate]:
    vectors: Dict[int, Tuple[int, int]] = {}
    for source, target in train:
        background = infer_bg(source)
        colors = {int(value) for value in np.unique(source) if int(value) != background}
        if colors != {int(value) for value in np.unique(target) if int(value) != infer_bg(target)}:
            return []
        for color in colors:
            vector = _transport_global_color_vector(source, target, color)
            if vector is None:
                return []
            if color in vectors and vectors[color] != vector:
                return []
            vectors[color] = vector
    if not vectors or all(vector == (0, 0) for vector in vectors.values()):
        return []
    try:
        candidate = candidate_from_function(
            "transport_color_vector_map_" + "_".join(f"{color}:{dr}:{dc}" for color, (dr, dc) in sorted(vectors.items())),
            lambda grid, mapping=dict(vectors): transport_color_vector_map_exact(grid, mapping),
            train,
            tests,
            7 + len(vectors),
            "transport_color_vector_map",
            metadata={
                "transport_block": "constant_color_vector_map",
                "vectors": {str(color): [dr, dc] for color, (dr, dc) in vectors.items()},
                "collision_aware": True,
                "exact_demonstration_contract": True,
            },
        )
    except Exception:
        return []
    return [candidate] if candidate.train_error == 0 else []


def transport_align_groups_to_anchor_exact(
    grid: Array,
    anchor_color: int,
    relation: str,
) -> Array:
    """Align every non-anchor color group to one reference group's edge or center."""
    grid = sanitize_grid(grid)
    background = infer_bg(grid)
    anchor = _transport_color_group(grid, anchor_color)
    colors = sorted(int(value) for value in np.unique(grid) if int(value) not in {background, anchor_color})
    if not colors:
        raise ValueError("no groups to align")
    output = grid.copy()
    for color in colors:
        output[grid == color] = background
    occupied = output != background
    for color in colors:
        group = _transport_color_group(grid, color)
        if relation == "top":
            dr, dc = anchor.bbox[0] - group.bbox[0], 0
        elif relation == "bottom":
            dr, dc = anchor.bbox[2] - group.bbox[2], 0
        elif relation == "vcenter":
            dr = int(round(_transport_object_center(anchor)[0] - _transport_object_center(group)[0]))
            dc = 0
        elif relation == "left":
            dr, dc = 0, anchor.bbox[1] - group.bbox[1]
        elif relation == "right":
            dr, dc = 0, anchor.bbox[3] - group.bbox[3]
        elif relation == "hcenter":
            dr = 0
            dc = int(round(_transport_object_center(anchor)[1] - _transport_object_center(group)[1]))
        elif relation == "center":
            dr = int(round(_transport_object_center(anchor)[0] - _transport_object_center(group)[0]))
            dc = int(round(_transport_object_center(anchor)[1] - _transport_object_center(group)[1]))
        else:
            raise ValueError(relation)
        cells = _transport_object_cells(grid, group, dr, dc)
        if not _transport_cells_valid(cells, grid.shape, occupied):
            raise ValueError("aligned groups collide")
        for row, column, value in cells:
            output[row, column] = value
            occupied[row, column] = True
    return output


def transport_reverse_color_groups_exact(grid: Array, axis: str) -> Array:
    """Reverse the order of color groups and repack their bounding boxes without gaps."""
    grid = sanitize_grid(grid)
    background = infer_bg(grid)
    colors = sorted(int(value) for value in np.unique(grid) if int(value) != background)
    groups = [_transport_color_group(grid, color) for color in colors]
    if len(groups) < 2:
        raise ValueError("not enough groups to reverse")
    index = 0 if axis == "vertical" else 1
    groups.sort(key=lambda group: (group.bbox[index], group.bbox[index + 2], group.color))
    # Require a strict source order; overlapping group spans do not define a
    # unique permutation along this axis.
    for left, right in zip(groups, groups[1:]):
        if left.bbox[index + 2] >= right.bbox[index]:
            raise ValueError("color groups overlap along reversal axis")
    output = np.full_like(grid, background)
    occupied = np.zeros(grid.shape, dtype=bool)
    cursor = min(group.bbox[index] for group in groups)
    for group in reversed(groups):
        if axis == "vertical":
            dr, dc = cursor - group.bbox[0], 0
            cursor += group.height
        elif axis == "horizontal":
            dr, dc = 0, cursor - group.bbox[1]
            cursor += group.width
        else:
            raise ValueError(axis)
        cells = _transport_object_cells(grid, group, dr, dc)
        if not _transport_cells_valid(cells, grid.shape, occupied):
            raise ValueError("reversed groups collide")
        for row, column, value in cells:
            output[row, column] = value
            occupied[row, column] = True
    return output


def transport_pack_by_size_exact(
    grid: Array,
    anchor_color: int,
    side: str,
    alignment: str,
    ascending: bool,
) -> Array:
    """Sort color groups by area and pack them against a stationary anchor."""
    grid = sanitize_grid(grid)
    background = infer_bg(grid)
    anchor = _transport_color_group(grid, anchor_color)
    colors = sorted(int(value) for value in np.unique(grid) if int(value) not in {background, anchor_color})
    groups = [_transport_color_group(grid, color) for color in colors]
    if not groups:
        raise ValueError("no payload groups")
    groups.sort(key=lambda group: (group.size, group.height * group.width, group.color), reverse=not ascending)
    output = grid.copy()
    for color in colors:
        output[grid == color] = background
    occupied = output != background

    if side in {"above", "below"}:
        total = sum(group.height for group in groups)
        cursor = anchor.bbox[0] - total if side == "above" else anchor.bbox[2] + 1
        for group in groups:
            if alignment == "left":
                column = anchor.bbox[1]
            elif alignment == "right":
                column = anchor.bbox[3] - group.width + 1
            elif alignment == "center":
                column = int(round(_transport_object_center(anchor)[1] - 0.5 * (group.width - 1)))
            else:
                raise ValueError(alignment)
            dr, dc = cursor - group.bbox[0], column - group.bbox[1]
            cursor += group.height
            cells = _transport_object_cells(grid, group, dr, dc)
            if not _transport_cells_valid(cells, grid.shape, occupied):
                raise ValueError("packed groups collide")
            for row, col, value in cells:
                output[row, col] = value
                occupied[row, col] = True
    elif side in {"left", "right"}:
        total = sum(group.width for group in groups)
        cursor = anchor.bbox[1] - total if side == "left" else anchor.bbox[3] + 1
        for group in groups:
            if alignment == "top":
                row = anchor.bbox[0]
            elif alignment == "bottom":
                row = anchor.bbox[2] - group.height + 1
            elif alignment == "center":
                row = int(round(_transport_object_center(anchor)[0] - 0.5 * (group.height - 1)))
            else:
                raise ValueError(alignment)
            dr, dc = row - group.bbox[0], cursor - group.bbox[1]
            cursor += group.width
            cells = _transport_object_cells(grid, group, dr, dc)
            if not _transport_cells_valid(cells, grid.shape, occupied):
                raise ValueError("packed groups collide")
            for row_value, col_value, value in cells:
                output[row_value, col_value] = value
                occupied[row_value, col_value] = True
    else:
        raise ValueError(side)
    return output


def transport_contact_reflect_anchor_exact(
    grid: Array,
    moving_color: int,
    anchor_color: int,
    direction_policy: str = "nearest_axis",
    connectivity: int = 4,
) -> Array:
    """Dock one rigid mover and reflect its mask into the anchor side."""
    grid = sanitize_grid(grid)
    background = infer_bg(grid)
    movers = _transport_color_objects(grid, moving_color, connectivity)
    anchors = _transport_color_objects(grid, anchor_color, connectivity)
    if len(movers) != 1 or len(anchors) != 1:
        raise ValueError("contact reflection requires one mover and one anchor")
    mover, anchor = movers[0], anchors[0]
    if mover.size != anchor.size:
        raise ValueError("mover and anchor masses differ")
    dr_step, dc_step = _transport_direction(mover, anchor, direction_policy)
    if bool(dr_step) == bool(dc_step):
        raise ValueError("contact reflection requires a cardinal direction")

    output = grid.copy()
    for obj in (mover, anchor):
        for row, column in obj.cells:
            output[row, column] = background
    occupied_other = output != background
    occupied_for_motion = occupied_other.copy()
    for row, column in anchor.cells:
        occupied_for_motion[row, column] = True

    dr = dc = 0
    while True:
        trial = _transport_object_cells(grid, mover, dr + dr_step, dc + dc_step)
        if not _transport_cells_valid(trial, grid.shape, occupied_for_motion):
            break
        dr += dr_step
        dc += dc_step
    if dr == 0 and dc == 0:
        raise ValueError("mover did not dock")
    moved_cells = _transport_object_cells(grid, mover, dr, dc)
    if not _transport_touches_anchor(moved_cells, [anchor], False):
        raise ValueError("mover did not reach anchor")

    moved_rows = [row for row, _, _ in moved_cells]
    moved_columns = [column for _, column, _ in moved_cells]
    top, bottom = min(moved_rows), max(moved_rows)
    left, right = min(moved_columns), max(moved_columns)
    height, width = bottom - top + 1, right - left + 1
    reflected: List[Tuple[int, int, int]] = []
    for row, column, _ in moved_cells:
        relative_row, relative_column = row - top, column - left
        if dc_step > 0:
            target_top, target_left = top, right + 1
            nr, nc = target_top + relative_row, target_left + (width - 1 - relative_column)
        elif dc_step < 0:
            target_top, target_left = top, left - width
            nr, nc = target_top + relative_row, target_left + (width - 1 - relative_column)
        elif dr_step > 0:
            target_top, target_left = bottom + 1, left
            nr, nc = target_top + (height - 1 - relative_row), target_left + relative_column
        else:
            target_top, target_left = top - height, left
            nr, nc = target_top + (height - 1 - relative_row), target_left + relative_column
        reflected.append((nr, nc, int(anchor_color)))

    occupied = occupied_other.copy()
    if not _transport_cells_valid(moved_cells, grid.shape, occupied):
        raise ValueError("moved mask collision")
    for row, column, color in moved_cells:
        output[row, column] = color
        occupied[row, column] = True
    if not _transport_cells_valid(reflected, grid.shape, occupied):
        raise ValueError("reflected anchor collision")
    for row, column, color in reflected:
        output[row, column] = color
        occupied[row, column] = True
    return output


def _transport_frame_objects(grid: Array, frame_color: int) -> List[Obj]:
    grid = sanitize_grid(grid)
    frames: List[Obj] = []
    for obj in _transport_color_objects(grid, frame_color, 4):
        if obj.height < 3 or obj.width < 3:
            continue
        r0, c0, r1, c1 = obj.bbox
        interior = grid[r0 + 1 : r1, c0 + 1 : c1]
        if interior.size == 0 or not np.any(interior != int(frame_color)):
            continue
        perimeter = 2 * obj.height + 2 * obj.width - 4
        if obj.size < max(obj.height + obj.width, int(0.55 * perimeter)):
            continue
        frames.append(obj)
    return sorted(frames, key=lambda obj: obj.bbox)


def _transport_frame_slots(grid: Array, frame: Obj, payload: Obj) -> List[Tuple[int, int]]:
    grid = sanitize_grid(grid)
    r0, c0, r1, c1 = frame.bbox
    slots: List[Tuple[int, int]] = []
    for top in range(r0 + 1, r1 - payload.height + 2):
        for left in range(c0 + 1, c1 - payload.width + 2):
            valid = True
            for row, column in payload.cells:
                nr = top + row - payload.bbox[0]
                nc = left + column - payload.bbox[1]
                if int(grid[nr, nc]) != infer_bg(grid):
                    valid = False
                    break
            if valid:
                slots.append((top, left))
    return slots


def transport_payloads_into_frames_exact(
    grid: Array,
    frame_color: int,
    slot_policy: str = "center",
) -> Array:
    """Assign the tightest-fitting external payload to every frame interior."""
    grid = sanitize_grid(grid)
    background = infer_bg(grid)
    frames = _transport_frame_objects(grid, frame_color)
    if not frames or len(frames) > 4:
        raise ValueError("unsupported frame count")
    payloads = [
        obj
        for obj in generic_components(grid, 4, True)
        if int(obj.color) != int(frame_color) and obj.size > 1
    ]
    if len(payloads) < len(frames) or len(payloads) > 8:
        raise ValueError("unsupported payload count")

    best: Optional[Tuple[int, Tuple[Obj, ...]]] = None
    for assignment in itertools.permutations(payloads, len(frames)):
        total_cost = 0
        valid = True
        for frame, payload in zip(frames, assignment):
            slots = _transport_frame_slots(grid, frame, payload)
            if not slots:
                valid = False
                break
            nominal_area = max(1, (frame.height - 2) * (frame.width - 2))
            slack = max(0, nominal_area - payload.height * payload.width)
            total_cost += 100 * slack + sum(_transport_bbox_gap(frame, payload))
        if valid and (best is None or total_cost < best[0]):
            best = (total_cost, assignment)
    if best is None:
        raise ValueError("no frame assignment")

    output = grid.copy()
    for payload in best[1]:
        for row, column in payload.cells:
            output[row, column] = background
    for frame, payload in zip(frames, best[1]):
        slots = _transport_frame_slots(output, frame, payload)
        if not slots:
            raise ValueError("no slot after payload removal")
        if slot_policy == "center":
            frame_center = _transport_object_center(frame)
            slots.sort(
                key=lambda slot: (
                    abs(slot[0] + 0.5 * (payload.height - 1) - frame_center[0])
                    + abs(slot[1] + 0.5 * (payload.width - 1) - frame_center[1]),
                    slot,
                )
            )
        elif slot_policy == "nearest_source":
            slots.sort(key=lambda slot: (abs(slot[0] - payload.bbox[0]) + abs(slot[1] - payload.bbox[1]), slot))
        elif slot_policy == "top_left":
            slots.sort()
        else:
            raise ValueError(slot_policy)
        top, left = slots[0]
        for row, column in payload.cells:
            output[top + row - payload.bbox[0], left + column - payload.bbox[1]] = grid[row, column]
    return output


def transport_frame_quadrant_ejection_exact(
    grid: Array,
    frame_color: int,
    opposite: bool = True,
) -> Array:
    """Move payloads inside a frame to exterior corners by their quadrant."""
    grid = sanitize_grid(grid)
    background = infer_bg(grid)
    frames = _transport_frame_objects(grid, frame_color)
    if len(frames) != 1:
        raise ValueError("quadrant ejection requires one frame")
    frame = frames[0]
    payloads = [
        obj
        for obj in generic_components(grid, 4, True)
        if int(obj.color) != int(frame_color)
        and frame.bbox[0] < obj.bbox[0]
        and obj.bbox[2] < frame.bbox[2]
        and frame.bbox[1] < obj.bbox[1]
        and obj.bbox[3] < frame.bbox[3]
    ]
    if not payloads:
        raise ValueError("no interior payloads")
    output = grid.copy()
    for payload in payloads:
        for row, column in payload.cells:
            output[row, column] = background
    occupied = output != background
    fr, fc = _transport_object_center(frame)
    for payload in payloads:
        pr, pc = _transport_object_center(payload)
        vertical = "top" if pr < fr else "bottom"
        horizontal = "left" if pc < fc else "right"
        if opposite:
            vertical = "bottom" if vertical == "top" else "top"
            horizontal = "right" if horizontal == "left" else "left"
        top = frame.bbox[0] - payload.height if vertical == "top" else frame.bbox[2] + 1
        left = frame.bbox[1] - payload.width if horizontal == "left" else frame.bbox[3] + 1
        cells = _transport_object_cells(grid, payload, top - payload.bbox[0], left - payload.bbox[1])
        if not _transport_cells_valid(cells, grid.shape, occupied):
            raise ValueError("frame ejection collision")
        for row, column, color in cells:
            output[row, column] = color
            occupied[row, column] = True
    return output


def _transport_unique_frame_color(grid: Array) -> int:
    grid = sanitize_grid(grid)
    background = infer_bg(grid)
    candidates = [
        int(color)
        for color in np.unique(grid)
        if int(color) != background and _transport_frame_objects(grid, int(color))
    ]
    if len(candidates) != 1:
        raise ValueError("frame color is not structurally unique")
    return candidates[0]


def transport_payloads_into_auto_frames_exact(grid: Array, slot_policy: str = "center") -> Array:
    return transport_payloads_into_frames_exact(grid, _transport_unique_frame_color(grid), slot_policy)


def transport_auto_frame_quadrant_ejection_exact(grid: Array, opposite: bool = True) -> Array:
    return transport_frame_quadrant_ejection_exact(grid, _transport_unique_frame_color(grid), opposite)


def transport_radial_to_corners_exact(grid: Array, opposite: bool = False) -> Array:
    """Project singleton packets from their quadrants to canvas corners."""
    grid = sanitize_grid(grid)
    background = infer_bg(grid)
    objects = generic_components(grid, 8, True)
    if not objects or any(obj.size != 1 for obj in objects):
        raise ValueError("radial corner projection requires singleton packets")
    output = np.full_like(grid, background)
    occupied = np.zeros(grid.shape, dtype=bool)
    row_center = 0.5 * (grid.shape[0] - 1)
    col_center = 0.5 * (grid.shape[1] - 1)
    for obj in objects:
        row, column = obj.cells[0]
        top = row < row_center
        left = column < col_center
        if opposite:
            top, left = not top, not left
        target = (0 if top else grid.shape[0] - 1, 0 if left else grid.shape[1] - 1)
        if occupied[target]:
            raise ValueError("corner projection collision")
        output[target] = grid[row, column]
        occupied[target] = True
    return output


def transport_reverse_sides_exact(grid: Array) -> Array:
    """Reverse the two sides of a one-dimensional odd-length signal."""
    grid = sanitize_grid(grid)
    if grid.shape[0] == 1 and grid.shape[1] % 2 == 1:
        values = grid[0].copy()
        center = grid.shape[1] // 2
        return np.concatenate([values[:center][::-1], values[center : center + 1], values[center + 1 :][::-1]])[None, :]
    if grid.shape[1] == 1 and grid.shape[0] % 2 == 1:
        values = grid[:, 0].copy()
        center = grid.shape[0] // 2
        return np.concatenate([values[:center][::-1], values[center : center + 1], values[center + 1 :][::-1]])[:, None]
    raise ValueError("not an odd one-dimensional signal")


def _transport_move_group_to_boundary(grid: Array, direction: str) -> Array:
    grid = sanitize_grid(grid)
    background = infer_bg(grid)
    colors = [int(value) for value in np.unique(grid) if int(value) != background]
    if len(colors) != 1:
        raise ValueError("boundary code requires one foreground color")
    group = _transport_color_group(grid, colors[0])
    if direction == "up":
        dr, dc = -group.bbox[0], 0
    elif direction == "down":
        dr, dc = grid.shape[0] - 1 - group.bbox[2], 0
    elif direction == "left":
        dr, dc = 0, -group.bbox[1]
    elif direction == "right":
        dr, dc = 0, grid.shape[1] - 1 - group.bbox[3]
    else:
        raise ValueError(direction)
    output = np.full_like(grid, background)
    for row, column, color in _transport_object_cells(grid, group, dr, dc):
        output[row, column] = color
    return output


def transport_boundary_code_rules(
    train: List[Tuple[Array, Array]],
    tests: List[Array],
) -> List[RuleCandidate]:
    directions = ("up", "right", "down", "left")
    mapping: Dict[int, str] = {}
    for source, target in train:
        background = infer_bg(source)
        colors = [int(value) for value in np.unique(source) if int(value) != background]
        if len(colors) != 1:
            return []
        color = colors[0]
        matches = [direction for direction in directions if exact(_transport_move_group_to_boundary(source, direction), target)]
        if len(matches) != 1:
            return []
        if color in mapping and mapping[color] != matches[0]:
            return []
        mapping[color] = matches[0]
    if not mapping:
        return []
    unused = [direction for direction in directions if direction not in mapping.values()]

    def apply(grid: Array) -> Array:
        background = infer_bg(grid)
        colors = [int(value) for value in np.unique(grid) if int(value) != background]
        if len(colors) != 1:
            raise ValueError("boundary code test color count")
        color = colors[0]
        if color in mapping:
            direction = mapping[color]
        elif len(unused) == 1:
            direction = unused[0]
        else:
            raise ValueError("unseen boundary code is ambiguous")
        return _transport_move_group_to_boundary(grid, direction)

    try:
        candidate = candidate_from_function(
            "transport_boundary_code_" + "_".join(f"{color}:{direction}" for color, direction in sorted(mapping.items())),
            apply,
            train,
            tests,
            10 + len(mapping),
            "transport_boundary_code",
            metadata={
                "transport_block": "color_coded_boundary_projection",
                "mapping": dict(mapping),
                "unseen_color_completion": unused[0] if len(unused) == 1 else None,
                "collision_aware": True,
                "exact_demonstration_contract": True,
            },
        )
    except Exception:
        return []
    return [candidate] if candidate.train_error == 0 else []


def _transport_marker_progression(points: Sequence[Tuple[int, int]]) -> Optional[Tuple[str, List[Tuple[int, int]]]]:
    ordered = sorted(points)
    if len(points) < 2:
        return None
    rows = {row for row, _ in points}
    columns = {column for _, column in points}
    if len(rows) == 1:
        sequence = sorted(points, key=lambda point: point[1])
        steps = {sequence[i + 1][1] - sequence[i][1] for i in range(len(sequence) - 1)}
        return ("horizontal", sequence) if len(steps) == 1 else None
    if len(columns) == 1:
        sequence = sorted(points, key=lambda point: point[0])
        steps = {sequence[i + 1][0] - sequence[i][0] for i in range(len(sequence) - 1)}
        return ("vertical", sequence) if len(steps) == 1 else None
    return None


def transport_shell_progression_rules(
    train: List[Tuple[Array, Array]],
    tests: List[Array],
) -> List[RuleCandidate]:
    common_colors = sorted(
        set.intersection(*({int(value) for value in np.unique(source) if int(value) != infer_bg(source)} for source, _ in train))
    )
    output: List[RuleCandidate] = []
    for moving_color in common_colors:
        for marker_color in common_colors:
            if moving_color == marker_color:
                continue
            index_delta: Optional[int] = None
            valid = True
            for source, target in train:
                vector = _transport_global_color_vector(source, target, moving_color)
                if vector is None:
                    valid = False
                    break
                if _transport_global_color_vector(source, target, marker_color) != (0, 0):
                    valid = False
                    break
                moving = _transport_color_group(source, moving_color)
                center = (int(round(_transport_object_center(moving)[0])), int(round(_transport_object_center(moving)[1])))
                marker_points = [tuple(int(v) for v in point) for point in np.argwhere(source == marker_color)]
                progression = _transport_marker_progression(marker_points)
                if progression is None or center not in progression[1]:
                    valid = False
                    break
                target_center = (center[0] + vector[0], center[1] + vector[1])
                if target_center not in progression[1]:
                    valid = False
                    break
                delta = progression[1].index(target_center) - progression[1].index(center)
                if index_delta is None:
                    index_delta = delta
                elif index_delta != delta:
                    valid = False
                    break
            if not valid or index_delta in (None, 0):
                continue

            def apply(grid: Array, moving=moving_color, marker=marker_color, delta=index_delta) -> Array:
                grid = sanitize_grid(grid)
                group = _transport_color_group(grid, moving)
                center = (int(round(_transport_object_center(group)[0])), int(round(_transport_object_center(group)[1])))
                points = [tuple(int(v) for v in point) for point in np.argwhere(grid == marker)]
                progression = _transport_marker_progression(points)
                if progression is None or center not in progression[1]:
                    raise ValueError("shell center is not on marker progression")
                index = progression[1].index(center) + int(delta)
                if not (0 <= index < len(progression[1])):
                    raise ValueError("progression step leaves marker sequence")
                target = progression[1][index]
                dr, dc = target[0] - center[0], target[1] - center[1]
                background = infer_bg(grid)
                result = grid.copy()
                result[grid == moving] = background
                occupied = result != background
                cells = _transport_object_cells(grid, group, dr, dc)
                if not _transport_cells_valid(cells, grid.shape, occupied):
                    # The center marker is intentionally retained and may lie
                    # inside a hollow shell, so allow overlap only at marker cells.
                    for row, column, _ in cells:
                        if not (0 <= row < grid.shape[0] and 0 <= column < grid.shape[1]):
                            raise ValueError("shell leaves canvas")
                        if occupied[row, column] and int(result[row, column]) != int(marker):
                            raise ValueError("shell progression collision")
                for row, column, color in cells:
                    if int(result[row, column]) == background:
                        result[row, column] = color
                return result

            try:
                candidate = candidate_from_function(
                    f"transport_shell_{moving_color}_along_{marker_color}_{index_delta:+d}",
                    apply,
                    train,
                    tests,
                    12,
                    "transport_shell_progression",
                    metadata={
                        "transport_block": "shell_on_marker_progression",
                        "moving_color": moving_color,
                        "marker_color": marker_color,
                        "index_delta": index_delta,
                        "translation_equivariant": True,
                        "exact_demonstration_contract": True,
                    },
                )
            except Exception:
                continue
            if candidate.train_error == 0:
                output.append(candidate)
    return output

def relational_transport_rules(
    train: List[Tuple[Array, Array]],
    tests: List[Array],
) -> List[RuleCandidate]:
    """Exact-fit relational transport and constrained placement proposals."""
    output: List[RuleCandidate] = []
    if not train or not all(source.shape == target.shape for source, target in train):
        return output
    # Transport preserves the complete color histogram. This gate prevents the
    # channel from searching recoloring or construction tasks.
    if not all(Counter(int(v) for v in source.ravel()) == Counter(int(v) for v in target.ravel()) for source, target in train):
        return output
    if all(exact(source, target) for source, target in train):
        return output

    output.extend(transport_color_vector_map_rules(train, tests))
    output.extend(transport_boundary_code_rules(train, tests))
    output.extend(transport_shell_progression_rules(train, tests))

    common_colors = sorted(
        set.intersection(
            *(
                {int(value) for value in np.unique(source) if int(value) != infer_bg(source)}
                for source, _ in train
            )
        )
    )
    for opposite in (False, True):
        _try_exact_rule(
            output,
            train,
            tests,
            f"transport_radial_corners_{int(opposite)}",
            lambda grid, invert=opposite: transport_radial_to_corners_exact(grid, invert),
            8,
            "transport_radial_projection",
            metadata={
                "transport_block": "radial_corner_projection",
                "opposite_quadrant": opposite,
                "collision_aware": True,
                "exact_demonstration_contract": True,
            },
        )
    _try_exact_rule(
        output,
        train,
        tests,
        "transport_reverse_signal_sides",
        transport_reverse_sides_exact,
        6,
        "transport_side_reversal",
        metadata={
            "transport_block": "one_dimensional_side_reversal",
            "exact_demonstration_contract": True,
        },
    )

    for slot_policy in ("center", "top_left", "nearest_source"):
        _try_exact_rule(
            output,
            train,
            tests,
            f"transport_frame_dock_auto_{slot_policy}",
            lambda grid, policy=slot_policy: transport_payloads_into_auto_frames_exact(grid, policy),
            13,
            "transport_frame_docking",
            metadata={
                "transport_block": "frame_payload_docking",
                "frame_color": "structurally_inferred",
                "slot_policy": slot_policy,
                "assignment": "minimum_interior_slack",
                "collision_aware": True,
                "exact_demonstration_contract": True,
            },
        )
    for opposite in (True, False):
        _try_exact_rule(
            output,
            train,
            tests,
            f"transport_frame_eject_auto_{int(opposite)}",
            lambda grid, invert=opposite: transport_auto_frame_quadrant_ejection_exact(grid, invert),
            11,
            "transport_frame_ejection",
            metadata={
                "transport_block": "frame_quadrant_ejection",
                "frame_color": "structurally_inferred",
                "opposite_quadrant": opposite,
                "collision_aware": True,
                "exact_demonstration_contract": True,
            },
        )

    for frame_color in common_colors:
        for slot_policy in ("center", "top_left", "nearest_source"):
            _try_exact_rule(
                output,
                train,
                tests,
                f"transport_frame_dock_{frame_color}_{slot_policy}",
                lambda grid, color=frame_color, policy=slot_policy: transport_payloads_into_frames_exact(grid, color, policy),
                14,
                "transport_frame_docking",
                metadata={
                    "transport_block": "frame_payload_docking",
                    "frame_color": frame_color,
                    "slot_policy": slot_policy,
                    "assignment": "minimum_interior_slack",
                    "collision_aware": True,
                    "exact_demonstration_contract": True,
                },
            )
        for opposite in (True, False):
            _try_exact_rule(
                output,
                train,
                tests,
                f"transport_frame_eject_{frame_color}_{int(opposite)}",
                lambda grid, color=frame_color, invert=opposite: transport_frame_quadrant_ejection_exact(grid, color, invert),
                12,
                "transport_frame_ejection",
                metadata={
                    "transport_block": "frame_quadrant_ejection",
                    "frame_color": frame_color,
                    "opposite_quadrant": opposite,
                    "collision_aware": True,
                    "exact_demonstration_contract": True,
                },
            )

    if len(common_colors) <= 7:
        for moving_color in common_colors:
            for anchor_color in common_colors:
                if moving_color == anchor_color:
                    continue
                for connectivity in (4, 8):
                    for policy in ("nearest_axis", "dominant_axis", "horizontal", "vertical", "diagonal"):
                        _try_exact_rule(
                            output,
                            train,
                            tests,
                            f"transport_contact_{moving_color}_to_{anchor_color}_{policy}_c{connectivity}",
                            lambda grid, moving=moving_color, anchor=anchor_color, p=policy, c=connectivity: transport_color_relation_exact(
                                grid,
                                moving,
                                anchor,
                                "contact",
                                p,
                                c,
                            ),
                            9,
                            "transport_contact",
                            metadata={
                                "transport_block": "object_to_anchor_contact",
                                "moving_color": moving_color,
                                "anchor_color": anchor_color,
                                "direction_policy": policy,
                                "connectivity": connectivity,
                                "collision_aware": True,
                                "exact_demonstration_contract": True,
                            },
                        )
                    for policy in ("nearest_axis", "dominant_axis", "horizontal", "vertical"):
                        _try_exact_rule(
                            output,
                            train,
                            tests,
                            f"transport_contact_reflect_{moving_color}_to_{anchor_color}_{policy}_c{connectivity}",
                            lambda grid, moving=moving_color, anchor=anchor_color, p=policy, c=connectivity: transport_contact_reflect_anchor_exact(
                                grid, moving, anchor, p, c
                            ),
                            12,
                            "transport_contact_reflection",
                            metadata={
                                "transport_block": "contact_reflected_docking",
                                "moving_color": moving_color,
                                "anchor_color": anchor_color,
                                "direction_policy": policy,
                                "connectivity": connectivity,
                                "collision_aware": True,
                                "exact_demonstration_contract": True,
                            },
                        )
                    for policy in ("chebyshev", "nearest_axis", "dominant_axis"):
                        _try_exact_rule(
                            output,
                            train,
                            tests,
                            f"transport_step_{moving_color}_to_{anchor_color}_{policy}_c{connectivity}",
                            lambda grid, moving=moving_color, anchor=anchor_color, p=policy, c=connectivity: transport_color_relation_exact(
                                grid,
                                moving,
                                anchor,
                                "step",
                                p,
                                c,
                            ),
                            7,
                            "transport_step",
                            metadata={
                                "transport_block": "object_to_anchor_step",
                                "moving_color": moving_color,
                                "anchor_color": anchor_color,
                                "direction_policy": policy,
                                "connectivity": connectivity,
                                "collision_aware": True,
                                "exact_demonstration_contract": True,
                            },
                        )

    for anchor_color in common_colors:
        for relation in ("top", "bottom", "vcenter", "left", "right", "hcenter", "center"):
            _try_exact_rule(
                output,
                train,
                tests,
                f"transport_align_{anchor_color}_{relation}",
                lambda grid, anchor=anchor_color, rel=relation: transport_align_groups_to_anchor_exact(grid, anchor, rel),
                9,
                "transport_group_alignment",
                metadata={
                    "transport_block": "group_alignment",
                    "anchor_color": anchor_color,
                    "relation": relation,
                    "collision_aware": True,
                    "exact_demonstration_contract": True,
                },
            )
        for side in ("above", "below"):
            for alignment in ("left", "right", "center"):
                for ascending in (True, False):
                    _try_exact_rule(
                        output,
                        train,
                        tests,
                        f"transport_pack_{anchor_color}_{side}_{alignment}_{int(ascending)}",
                        lambda grid, anchor=anchor_color, s=side, align=alignment, asc=ascending: transport_pack_by_size_exact(
                            grid, anchor, s, align, asc
                        ),
                        11,
                        "transport_size_pack",
                        metadata={
                            "transport_block": "size_ordered_packing",
                            "anchor_color": anchor_color,
                            "side": side,
                            "alignment": alignment,
                            "ascending": ascending,
                            "collision_aware": True,
                            "exact_demonstration_contract": True,
                        },
                    )
        for side in ("left", "right"):
            for alignment in ("top", "bottom", "center"):
                for ascending in (True, False):
                    _try_exact_rule(
                        output,
                        train,
                        tests,
                        f"transport_pack_{anchor_color}_{side}_{alignment}_{int(ascending)}",
                        lambda grid, anchor=anchor_color, s=side, align=alignment, asc=ascending: transport_pack_by_size_exact(
                            grid, anchor, s, align, asc
                        ),
                        11,
                        "transport_size_pack",
                        metadata={
                            "transport_block": "size_ordered_packing",
                            "anchor_color": anchor_color,
                            "side": side,
                            "alignment": alignment,
                            "ascending": ascending,
                            "collision_aware": True,
                            "exact_demonstration_contract": True,
                        },
                    )

    for axis in ("vertical", "horizontal"):
        _try_exact_rule(
            output,
            train,
            tests,
            f"transport_reverse_groups_{axis}",
            lambda grid, a=axis: transport_reverse_color_groups_exact(grid, a),
            10,
            "transport_order_reversal",
            metadata={
                "transport_block": "group_order_reversal",
                "axis": axis,
                "collision_aware": True,
                "exact_demonstration_contract": True,
            },
        )

    for direction in ("left", "right", "up", "down"):
        for connectivity in (4, 8):
            for separate_colors in (False, True):
                for offset in (-1, 0, 1):
                    _try_exact_rule(
                        output,
                        train,
                        tests,
                        f"transport_extent_{direction}_c{connectivity}_{int(separate_colors)}_{offset:+d}",
                        lambda grid, d=direction, c=connectivity, separate=separate_colors, off=offset: transport_objects_by_extent_exact(
                            grid,
                            d,
                            c,
                            separate,
                            off,
                        ),
                        8,
                        "transport_extent",
                        metadata={
                            "transport_block": "self_extent_displacement",
                            "direction": direction,
                            "connectivity": connectivity,
                            "separate_colors": separate_colors,
                            "extent_offset": offset,
                            "collision_aware": True,
                            "exact_demonstration_contract": True,
                        },
                    )

    for keep_sources in (False, True):
        _try_exact_rule(
            output,
            train,
            tests,
            f"transport_cardinal_markers_{int(keep_sources)}",
            lambda grid, keep=keep_sources: transport_cardinal_markers_exact(grid, keep),
            10,
            "transport_cardinal_collapse",
            metadata={
                "transport_block": "cardinal_marker_collapse",
                "keep_sources": keep_sources,
                "translation_equivariant": True,
                "collision_aware": True,
                "exact_demonstration_contract": True,
            },
        )

    deduplicated: List[RuleCandidate] = []
    seen: set[Tuple[str, ...]] = set()
    for candidate in sorted(output, key=lambda item: (item.complexity, item.family, item.name)):
        signature = tuple(canonical(grid) for grid in candidate.grids)
        if signature in seen:
            continue
        seen.add(signature)
        deduplicated.append(candidate)
    return deduplicated

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
    out.extend(object_scene_algebra_rules(train, tests))
    out.extend(relational_transport_rules(train, tests))
    out.extend(signal_transport_rules(train, tests))
    out.extend(signal_lookup_rules(train, tests))

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


# ---------------- typed conditional composition proposal channel ----------------

@dataclass(frozen=True)
class CompositionPrimitive:
    name: str
    stage: str
    cost: int
    fn: Callable[[Array], Array]
    selector_key: str = "global"
    mechanism_key: str = "unary"
    repeatable: bool = False
    metadata: Optional[Dict[str, object]] = None

    def apply(self, grid: Array) -> Array:
        # Unlike the legacy Op wrapper, invalid partial operators are never
        # converted to identity. The search rejects the entire successor.
        raw = np.asarray(self.fn(sanitize_grid(grid)))
        if raw.ndim != 2 or raw.size == 0:
            raise ValueError(f"invalid composition output from {self.name}")
        if raw.shape[0] > MAX_SIDE or raw.shape[1] > MAX_SIDE:
            raise ValueError(f"oversized composition output from {self.name}")
        if raw.dtype.kind not in {"i", "u"}:
            raise ValueError(f"non-integral composition output from {self.name}")
        if np.any(raw < 0) or np.any(raw > 9):
            raise ValueError(f"invalid ARC color from {self.name}")
        return raw.astype(np.int16, copy=True)


@dataclass(frozen=True)
class CompositionProgram:
    steps: Tuple[CompositionPrimitive, ...] = ()

    @property
    def cost(self) -> int:
        return sum(step.cost for step in self.steps) + len(self.steps)

    @property
    def stages(self) -> Tuple[str, ...]:
        return tuple(step.stage for step in self.steps)

    def execute(self, grid: Array) -> Array:
        output = sanitize_grid(grid)
        for step in self.steps:
            output = step.apply(output)
        return output


@dataclass(frozen=True)
class CompositionSearchConfig:
    max_depth: int
    beam_width: int
    max_expansions: int
    max_exact_candidates: int
    max_ops_per_stage: int
    completion_width: int
    max_repeat_steps: int

    @classmethod
    def for_time_limit(cls, time_limit: float) -> "CompositionSearchConfig":
        seconds = max(0.0, float(time_limit))
        if seconds <= 0.1:
            return cls(3, 24, 512, 8, 18, 0, 12)
        if seconds <= 2.0:
            return cls(4, 48, 2200, 16, 28, 1, 30)
        return cls(5, 96, 8000, 24, 48, 3, 64)


@dataclass
class CompositionNode:
    program: CompositionProgram
    train_grids: Tuple[Array, ...]
    test_grids: Tuple[Array, ...]
    score: float
    residual_bucket: Tuple[int, ...]


def _composition_role_objects(grid: Array, role: str) -> List[Obj]:
    grid = sanitize_grid(grid)
    background = infer_bg(grid)
    objects = [
        obj
        for obj in generic_components(grid, connectivity=4, separate_colors=True)
        if int(obj.color) != int(background)
    ]
    if not objects:
        raise ValueError("no foreground objects")
    ordered = sorted(objects, key=lambda obj: (obj.bbox[0], obj.bbox[1], int(obj.color)))
    if role == "largest":
        return [max(ordered, key=lambda obj: (obj.size, obj.height * obj.width, -obj.bbox[0], -obj.bbox[1]))]
    if role == "smallest":
        return [min(ordered, key=lambda obj: (obj.size, obj.height * obj.width, obj.bbox[0], obj.bbox[1]))]
    if role == "singletons":
        selected = [obj for obj in ordered if obj.size == 1]
    elif role == "non_singletons":
        selected = [obj for obj in ordered if obj.size > 1]
    elif role == "border_touching":
        selected = [
            obj
            for obj in ordered
            if obj.bbox[0] == 0
            or obj.bbox[1] == 0
            or obj.bbox[2] == grid.shape[0] - 1
            or obj.bbox[3] == grid.shape[1] - 1
        ]
    elif role == "interior":
        selected = [
            obj
            for obj in ordered
            if obj.bbox[0] > 0
            and obj.bbox[1] > 0
            and obj.bbox[2] < grid.shape[0] - 1
            and obj.bbox[3] < grid.shape[1] - 1
        ]
    elif role == "has_hole":
        selected = [obj for obj in ordered if object_hole_count(obj) > 0]
    elif role in {"unique_shape", "repeated_shape"}:
        counts = Counter(_graph_object_shape_signature(obj) for obj in ordered)
        want_unique = role == "unique_shape"
        selected = [
            obj
            for obj in ordered
            if (counts[_graph_object_shape_signature(obj)] == 1) == want_unique
        ]
    elif role == "rarest_color":
        counts = Counter(int(value) for value in grid.ravel() if int(value) != int(background))
        rare = min(counts, key=lambda color: (counts[color], color))
        selected = [obj for obj in ordered if int(obj.color) == int(rare)]
    elif role == "marker_color":
        marker = marker_color(grid, background)
        selected = [obj for obj in ordered if int(obj.color) == int(marker)]
    else:
        raise ValueError(role)
    if not selected:
        raise ValueError(f"role {role} selected no objects")
    return selected


def conditional_object_edit_exact(
    grid: Array,
    role: str,
    action: str,
    *,
    target_color: Optional[int] = None,
    destination: Optional[str] = None,
) -> Array:
    """Apply one explicit edit to every object satisfying a structural role."""
    source = sanitize_grid(grid)
    output = source.copy()
    background = infer_bg(source)
    objects = _composition_role_objects(source, role)
    if action in {"recolor", "erase"}:
        color = int(background if action == "erase" else target_color)
        if action == "recolor" and target_color is None:
            raise ValueError("recolor requires target color")
        changed = 0
        for obj in objects:
            for row, column in obj.cells:
                changed += int(int(output[row, column]) != color)
                output[row, column] = color
        if changed == 0:
            raise ValueError("conditional edit made no change")
        return output
    if action not in {"move", "copy"} or destination is None:
        raise ValueError(action)
    if len(objects) != 1:
        raise ValueError("move/copy requires a unique role object")
    obj = objects[0]
    top, left = corner_position(source, obj, destination)
    translated = [(top + row - obj.bbox[0], left + column - obj.bbox[1]) for row, column in obj.cells]
    occupied = {
        (row, column)
        for row in range(source.shape[0])
        for column in range(source.shape[1])
        if int(source[row, column]) != int(background) and (row, column) not in obj.cells
    }
    if any(position in occupied for position in translated):
        raise ValueError("conditional placement collision")
    if action == "move":
        clear_object(output, obj, background)
    for (row, column), (_, _, color) in zip(translated, [(r, c, int(source[r, c])) for r, c in obj.cells]):
        output[row, column] = color
    if exact(output, source):
        raise ValueError("conditional placement made no change")
    return output


def cleanup_singletons_exact(grid: Array, mode: str = "all") -> Array:
    source = sanitize_grid(grid)
    output = source.copy()
    background = infer_bg(source)
    objects = [
        obj
        for obj in generic_components(source, connectivity=4, separate_colors=True)
        if obj.size == 1 and int(obj.color) != int(background)
    ]
    if mode == "marker_color":
        color = marker_color(source, background)
        objects = [obj for obj in objects if int(obj.color) == int(color)]
    elif mode == "rarest_color":
        color = rare_color(source, background)
        objects = [obj for obj in objects if int(obj.color) == int(color)]
    elif mode != "all":
        raise ValueError(mode)
    if not objects:
        raise ValueError("no cleanup markers")
    for obj in objects:
        output[obj.cells[0]] = int(background)
    return output


def _composition_task_profile(train: List[Tuple[Array, Array]]) -> Dict[str, object]:
    same_shape = all(source.shape == target.shape for source, target in train)
    add_only = same_shape and all(
        np.all(~_foreground_mask(source) | _foreground_mask(target))
        for source, target in train
    )
    remove_only = same_shape and all(
        np.all(~_foreground_mask(target) | _foreground_mask(source))
        for source, target in train
    )
    histogram_conserved = all(
        Counter(int(value) for value in source.ravel())
        == Counter(int(value) for value in target.ravel())
        for source, target in train
    )
    smaller = all(
        target.shape[0] <= source.shape[0] and target.shape[1] <= source.shape[1]
        for source, target in train
    )
    return {
        "same_shape": same_shape,
        "add_only": add_only,
        "remove_only": remove_only,
        "histogram_conserved": histogram_conserved,
        "smaller": smaller,
    }


def composition_primitive_library(
    train: List[Tuple[Array, Array]],
    config: CompositionSearchConfig,
) -> List[CompositionPrimitive]:
    """Build a finite, task-conditioned library of safe partial operators."""
    profile = _composition_task_profile(train)
    target_colors = _output_candidate_colors(train)[:4]
    input_colors = sorted(
        set.union(
            *(
                {int(value) for value in np.unique(source) if int(value) != infer_bg(source)}
                for source, _ in train
            )
        )
    )[:7]
    primitives: List[CompositionPrimitive] = []

    def add(
        name: str,
        stage: str,
        cost: int,
        fn: Callable[[Array], Array],
        selector: str = "global",
        mechanism: str = "unary",
        repeatable: bool = False,
        metadata: Optional[Dict[str, object]] = None,
    ) -> None:
        traits = dict(metadata or {})
        traits.setdefault("translation_equivariant", False)
        traits.setdefault("collision_aware", False)
        primitives.append(
            CompositionPrimitive(
                name,
                stage,
                cost,
                fn,
                selector,
                mechanism,
                repeatable,
                traits,
            )
        )

    geometric = [
        ("rot90", lambda grid: np.rot90(grid, 1)),
        ("rot180", lambda grid: np.rot90(grid, 2)),
        ("rot270", lambda grid: np.rot90(grid, 3)),
        ("flip_h", np.fliplr),
        ("flip_v", np.flipud),
        ("transpose", lambda grid: grid.T),
        ("anti_transpose", lambda grid: np.fliplr(np.flipud(grid).T)),
    ]
    for name, fn in geometric:
        add(name, "transform", 2, fn, mechanism="dihedral")
    if bool(profile["smaller"]):
        add("crop_bbox", "extract", 3, crop_bbox_non_bg, mechanism="bounding_box")
        add("remove_uniform_border", "extract", 4, op_remove_uniform_border().fn, mechanism="border_strip")
    add("fill_holes", "draw", 4, op_fill_holes().fn, mechanism="enclosure_fill")
    for axis in ("h", "v", "both"):
        add(f"extend_lines_{axis}", "draw", 4, op_extend_lines(axis).fn, mechanism="line_extension")
    for mode in ("horizontal", "vertical", "rot180", "diagonal", "anti_diagonal"):
        add(
            f"complete_{mode}",
            "draw",
            6,
            lambda grid, symmetry=mode: complete_reflection_exact(grid, symmetry),
            mechanism="symmetry_completion",
        )
    for direction in ("down", "up", "left", "right"):
        add(
            f"object_gravity_{direction}",
            "transport",
            7,
            lambda grid, move=direction: object_gravity_exact(grid, move),
            mechanism="gravity",
            metadata={"collision_aware": True},
        )
    roles = (
        "largest",
        "smallest",
        "singletons",
        "non_singletons",
        "border_touching",
        "interior",
        "has_hole",
        "unique_shape",
        "repeated_shape",
        "rarest_color",
        "marker_color",
    )
    for role in roles:
        add(
            f"erase_{role}",
            "cleanup",
            5,
            lambda grid, selected=role: conditional_object_edit_exact(grid, selected, "erase"),
            selector=role,
            mechanism="object_erase",
            metadata={
                "translation_equivariant": role
                not in {"border_touching", "interior"},
            },
        )
        for color in target_colors:
            add(
                f"recolor_{role}_to_{color}",
                "recolor",
                5,
                lambda grid, selected=role, value=color: conditional_object_edit_exact(
                    grid,
                    selected,
                    "recolor",
                    target_color=value,
                ),
                selector=role,
                mechanism="object_recolor",
                metadata={
                    "translation_equivariant": role
                    not in {"border_touching", "interior"},
                },
            )
    for role in ("largest", "smallest", "unique_shape", "rarest_color", "marker_color"):
        for destination in ("tl", "tr", "bl", "br", "center"):
            for action in ("move", "copy"):
                add(
                    f"{action}_{role}_{destination}",
                    "transport" if action == "move" else "draw",
                    7,
                    lambda grid, selected=role, verb=action, corner=destination: conditional_object_edit_exact(
                        grid,
                        selected,
                        verb,
                        destination=corner,
                    ),
                    selector=role,
                    mechanism=f"object_{action}",
                    metadata={"collision_aware": True},
                )
    for mode in ("all", "marker_color", "rarest_color"):
        add(
            f"cleanup_singletons_{mode}",
            "cleanup",
            4,
            lambda grid, cleanup=mode: cleanup_singletons_exact(grid, cleanup),
            selector=mode,
            mechanism="marker_cleanup",
            metadata={"translation_equivariant": True},
        )

    for geometry in ("straight", "orthogonal_hv", "orthogonal_vh"):
        for collision in ("preserve_existing", "vertical_over_horizontal", "horizontal_over_vertical"):
            add(
                f"draw_pairs_{geometry}_{collision}",
                "draw",
                8,
                lambda grid, geom=geometry, policy=collision: graph_connect_color_pairs_exact(
                    grid,
                    geom,
                    policy,
                    require_singletons=True,
                ),
                selector="same_color_pairs",
                mechanism="relational_line",
                metadata={
                    "collision_aware": True,
                    "translation_equivariant": True,
                },
            )
    for pairing in ("same_color", "rarest_pair", "reading_pairs"):
        for order in sorted(_ROUTE_ORDERS):
            for color in [None] + target_colors[:2]:
                add(
                    f"route_{pairing}_{order}_{color}",
                    "draw",
                    10,
                    lambda grid, pairs=pairing, tie=order, value=color: draw_obstacle_path_exact(
                        grid,
                        pairs,
                        line_color=value,
                        neighbor_order=tie,
                        turn_cost=2,
                        endpoint_policy="preserve",
                    ),
                    selector=pairing,
                    mechanism="obstacle_route",
                    metadata={
                        "collision_aware": True,
                        "neighbor_order": order,
                    },
                )

    if len(input_colors) <= 7:
        for moving_color in input_colors:
            for anchor_color in input_colors:
                if moving_color == anchor_color:
                    continue
                for mode in ("step", "contact"):
                    for direction_policy in ("nearest_axis", "dominant_axis", "chebyshev"):
                        add(
                            f"{mode}_{moving_color}_to_{anchor_color}_{direction_policy}",
                            "transport",
                            8 if mode == "step" else 10,
                            lambda grid, moving=moving_color, anchor=anchor_color, movement=mode, policy=direction_policy: transport_color_relation_exact(
                                grid,
                                moving,
                                anchor,
                                movement,
                                policy,
                                4,
                            ),
                            selector=f"color:{moving_color}->color:{anchor_color}",
                            mechanism=f"relational_{mode}",
                            metadata={
                                "collision_aware": True,
                                "translation_equivariant": True,
                            },
                        )
    for direction in ("left", "right", "up", "down"):
        add(
            f"transport_extent_{direction}",
            "transport",
            8,
            lambda grid, move=direction: transport_objects_by_extent_exact(grid, move, 4, True, 0),
            selector="all_objects",
            mechanism="self_extent",
            metadata={
                "collision_aware": True,
                "translation_equivariant": True,
            },
        )

    for extent in ("gaps", "forward", "backward", "both"):
        for color_policy in ("cycle", "repeat_last", "same"):
            add(
                f"recursive_motif_{extent}_{color_policy}",
                "recursive",
                11,
                lambda grid, ex=extent, colors=color_policy: recursive_motif_extension_exact(
                    grid,
                    extent=ex,
                    color_policy=colors,
                    group_policy="largest",
                ),
                selector="repeated_shape",
                mechanism="repeat_until_boundary",
                metadata={
                    "recursive": True,
                    "repeat_stop": "boundary_or_collision",
                    "collision_aware": True,
                },
            )
    for seed_color in input_colors[:4]:
        for connectivity in (4, 8):
            for threshold in (1, 2):
                for iterations in (1, 2, 0):
                    add(
                        f"recursive_growth_{seed_color}_c{connectivity}_n{threshold}_i{iterations}",
                        "recursive",
                        9,
                        lambda grid, color=seed_color, conn=connectivity, count=threshold, steps=iterations: recursive_neighbor_growth_exact(
                            grid,
                            color,
                            connectivity=conn,
                            threshold=count,
                            iterations=steps,
                        ),
                        selector=f"color:{seed_color}",
                        mechanism="frontier_growth",
                        metadata={
                            "recursive": True,
                            "repeat_stop": "fixed_point" if iterations == 0 else "bounded_steps",
                            "collision_aware": True,
                        },
                    )

    # Stage-aware ordering removes the lexicographic prefix bias of the old
    # Cartesian enumeration. Each stage receives an explicit bounded share.
    if bool(profile["histogram_conserved"]):
        stage_order = ("transport", "transform", "draw", "recolor", "cleanup", "recursive", "extract")
    elif bool(profile["add_only"]):
        stage_order = ("draw", "recursive", "transport", "recolor", "cleanup", "transform", "extract")
    elif bool(profile["remove_only"]):
        stage_order = ("cleanup", "extract", "transport", "recolor", "transform", "draw", "recursive")
    else:
        stage_order = ("transport", "draw", "recolor", "cleanup", "recursive", "transform", "extract")
    grouped: Dict[str, List[CompositionPrimitive]] = defaultdict(list)
    for primitive in primitives:
        grouped[primitive.stage].append(primitive)
    selected: List[CompositionPrimitive] = []
    for stage in stage_order:
        stage_items = sorted(grouped.get(stage, []), key=lambda item: (item.cost, item.name))
        selected.extend(stage_items[: config.max_ops_per_stage])
    return selected


def _composition_residual(
    grids: Sequence[Array],
    train: List[Tuple[Array, Array]],
    complexity: int,
) -> Tuple[float, Tuple[int, ...]]:
    cell_error = 0
    missing = 0
    extra = 0
    wrong_color = 0
    shape_failures = 0
    object_delta = 0
    for prediction, (_, target) in zip(grids, train):
        prediction = sanitize_grid(prediction)
        target = sanitize_grid(target)
        cell_error += grid_error(prediction, target)
        if prediction.shape != target.shape:
            shape_failures += 1
            continue
        pred_bg, target_bg = infer_bg(prediction), infer_bg(target)
        pred_fg, target_fg = prediction != pred_bg, target != target_bg
        missing += int(np.count_nonzero(~pred_fg & target_fg))
        extra += int(np.count_nonzero(pred_fg & ~target_fg))
        wrong_color += int(np.count_nonzero(pred_fg & target_fg & (prediction != target)))
        object_delta += abs(
            len(generic_components(prediction, 4, True))
            - len(generic_components(target, 4, True))
        )
    score = (
        float(cell_error)
        + 0.35 * float(missing + extra)
        + 0.2 * float(wrong_color)
        + 0.15 * float(object_delta)
        + 0.01 * float(complexity)
    )

    def bucket(value: int) -> int:
        if value <= 0:
            return 0
        if value <= 2:
            return 1
        if value <= 8:
            return 2
        return 3

    residual_bucket = (
        int(shape_failures > 0),
        bucket(missing),
        bucket(extra),
        bucket(wrong_color),
        bucket(object_delta),
    )
    return score, residual_bucket


def _composition_transition_allowed(
    program: CompositionProgram,
    primitive: CompositionPrimitive,
) -> bool:
    if program.steps:
        previous = program.steps[-1]
        if not primitive.repeatable and any(
            step.name == primitive.name for step in program.steps
        ):
            return False
        if previous.stage == "cleanup":
            return False
    counts = Counter(program.stages)
    limits = {
        "transform": 2,
        "extract": 1,
        "transport": 2,
        "draw": 2,
        "recolor": 2,
        "cleanup": 1,
        "recursive": 1,
    }
    return counts[primitive.stage] < limits.get(primitive.stage, 1)


def _composition_admissibility_signature(
    program: CompositionProgram,
) -> Tuple[object, ...]:
    """Return every prefix property that can change legal future steps."""
    if not program.steps:
        return (None, None, (), ())
    counts = Counter(program.stages)
    return (
        program.steps[-1].name,
        program.steps[-1].stage,
        tuple(sorted(step.name for step in program.steps if not step.repeatable)),
        tuple(sorted((stage, int(count)) for stage, count in counts.items())),
    )


def _composition_family(stages: Sequence[str], mechanisms: Sequence[str]) -> str:
    stage_set = set(stages)
    mechanism_set = set(mechanisms)
    if "obstacle_route" in mechanism_set:
        return "composition_obstacle_route"
    if "recursive" in stage_set:
        return "composition_recursive"
    if any(
        mechanism.startswith("struct_object_predicate_rewrite")
        or mechanism.startswith("struct_region_predicate_rewrite")
        or mechanism.startswith("struct_cardinality_renderer")
        or mechanism.startswith("struct_mask_motif_broadcast")
        or mechanism.startswith("composition_scalar_mask")
        for mechanism in mechanism_set
    ):
        return "composition_scalar_mask"
    if {"transport", "draw"}.issubset(stage_set):
        return "composition_transport_draw"
    if {"transport", "recolor"}.issubset(stage_set):
        return "composition_transport_recolor"
    if {"draw", "recolor"}.issubset(stage_set):
        return "composition_draw_recolor"
    if "cleanup" in stage_set:
        return "composition_cleanup"
    return "composition_conditional"


def _composition_candidate_from_node(node: CompositionNode) -> RuleCandidate:
    steps = [
        {
            "name": step.name,
            "stage": step.stage,
            "cost": int(step.cost),
            "selector_key": step.selector_key,
            "mechanism_key": step.mechanism_key,
            **dict(step.metadata or {}),
        }
        for step in node.program.steps
    ]
    stages = list(node.program.stages)
    mechanisms = [step.mechanism_key for step in node.program.steps]
    family = _composition_family(stages, mechanisms)
    return RuleCandidate(
        name="compose:" + " -> ".join(step.name for step in node.program.steps),
        grids=[grid.copy() for grid in node.test_grids],
        train_error=0,
        complexity=node.program.cost,
        family=family,
        train_grids=tuple(grid.copy() for grid in node.train_grids),
        metadata={
            "composition_block": "typed_conditional_program",
            "program_version": "conditional-dag-1",
            "steps": steps,
            "stages": stages,
            "depth": len(steps),
            "cost": node.program.cost,
            "selector_keys": [step.selector_key for step in node.program.steps],
            "mechanism_keys": mechanisms,
            "condition_support": "structural_role_or_relational_precondition",
            "recursive": "recursive" in stages,
            "collision_aware": any(
                bool((step.metadata or {}).get("collision_aware"))
                for step in node.program.steps
            ),
            "translation_equivariant": all(
                bool((step.metadata or {}).get("translation_equivariant"))
                for step in node.program.steps
            ),
            "exact_demonstration_contract": True,
        },
    )


def _composition_terminal_stage(family: str) -> str:
    value = family.lower()
    if "mask_motif_broadcast" in value:
        return "draw"
    if "predicate_rewrite" in value or "scalar_mask" in value:
        return "recolor"
    if "cardinality_renderer" in value:
        return "extract"
    if "recursive" in value:
        return "recursive"
    if "transport" in value or "translation" in value or "gravity" in value:
        return "transport"
    if "route" in value or "path" in value or "line" in value or "draw" in value or "symmetry" in value:
        return "draw"
    if "recolor" in value or "color" in value:
        return "recolor"
    if "remove" in value or "erase" in value or "filter" in value:
        return "cleanup"
    if "panel" in value or "extract" in value or "crop" in value:
        return "extract"
    return "transform"


def _composition_terminal_candidates(
    node: CompositionNode,
    train: List[Tuple[Array, Array]],
    tests: List[Array],
    *,
    deep: bool,
    maximum_candidates: int,
) -> List[RuleCandidate]:
    intermediate_train = [
        (grid.copy(), target)
        for grid, (_, target) in zip(node.train_grids, train)
    ]
    intermediate_tests = [grid.copy() for grid in node.test_grids]
    generators = [
        projector_exact_rules,
        obstacle_path_rules,
        recursive_construction_rules,
    ]
    if deep:
        # Graph completion is costly, so only the deep tier may use it after a
        # high-value intermediate state. The broad structural channel is not
        # re-run here because it already participates directly and would make
        # the nominal task tier needlessly unpredictable.
        generators.extend([graph_rewrite_rules, typed_scalar_mask_terminal_rules])
    output: List[RuleCandidate] = []
    for generator in generators:
        for terminal in generator(intermediate_train, intermediate_tests):
            # Object-centred residual stencils already have their own direct
            # proposal channel and weak held-out reliability. Composing them
            # after arbitrary intermediate states multiplies that ambiguity,
            # so only analytic graph mechanisms may terminate a composition.
            if (
                terminal.family.startswith("graph_object_stencil_")
                or terminal.family == "signal_local_transducer"
                or terminal.family.startswith("residual_")
            ):
                continue
            stage = _composition_terminal_stage(terminal.family)
            terminal_step = CompositionPrimitive(
                terminal.name,
                stage,
                terminal.complexity,
                lambda grid: grid,
                selector_key="terminal_exact_rule",
                mechanism_key=terminal.family,
                metadata=dict(terminal.metadata or {}),
            )
            program = CompositionProgram(node.program.steps + (terminal_step,))
            if len(set(program.stages)) < 2:
                continue
            composite_node = CompositionNode(
                program=program,
                train_grids=tuple(grid.copy() for grid in terminal.train_grids),
                test_grids=tuple(grid.copy() for grid in terminal.grids),
                score=0.0,
                residual_bucket=(0, 0, 0, 0, 0),
            )
            output.append(_composition_candidate_from_node(composite_node))
            if len(output) >= max(1, int(maximum_candidates)):
                return deduplicate_candidates(output)
    return deduplicate_candidates(output)


def conditional_composition_rules(
    train: List[Tuple[Array, Array]],
    tests: List[Array],
    time_limit: float,
    config: Optional[CompositionSearchConfig] = None,
) -> List[RuleCandidate]:
    """Search bounded mixed-stage programs over explicit intermediate states.

    Every emitted program is exact on every demonstration. Nominal task time
    selects a deterministic depth, beam, and expansion tier. Process isolation
    supplies the real hard wall-clock boundary, so machine timing cannot change
    which bounded search prefix enters the posterior.
    """
    if not train or not tests:
        return []
    config = config or CompositionSearchConfig.for_time_limit(time_limit)
    primitives = composition_primitive_library(train, config)
    if not primitives:
        return []
    initial_train = tuple(source.copy() for source, _ in train)
    initial_tests = tuple(test.copy() for test in tests)
    initial_score, initial_bucket = _composition_residual(initial_train, train, 0)
    beam = [CompositionNode(CompositionProgram(), initial_train, initial_tests, initial_score, initial_bucket)]
    exact_candidates: List[RuleCandidate] = []
    exact_predictions: set[Tuple[str, ...]] = set()
    visited: Dict[Tuple[object, ...], float] = {}
    expansions = 0

    for depth in range(1, config.max_depth + 1):
        remaining_depths = config.max_depth - depth + 1
        depth_quota = max(
            1,
            (config.max_expansions - expansions) // remaining_depths,
        )
        depth_expansions = 0
        successors: List[CompositionNode] = []
        for node in beam:
            for primitive in primitives:
                if (
                    expansions >= config.max_expansions
                    or depth_expansions >= depth_quota
                ):
                    break
                if not _composition_transition_allowed(node.program, primitive):
                    continue
                expansions += 1
                depth_expansions += 1
                try:
                    next_train = tuple(primitive.apply(grid) for grid in node.train_grids)
                    next_tests = tuple(primitive.apply(grid) for grid in node.test_grids)
                except Exception:
                    continue
                if all(exact(before, after) for before, after in zip(node.train_grids, next_train)):
                    continue
                program = CompositionProgram(node.program.steps + (primitive,))
                score, bucket = _composition_residual(next_train, train, program.cost)
                key = (
                    _composition_admissibility_signature(program),
                    tuple(canonical(grid) for grid in next_train),
                    tuple(canonical(grid) for grid in next_tests),
                )
                prior = visited.get(key)
                if prior is not None and prior <= score:
                    continue
                visited[key] = score
                successor = CompositionNode(program, next_train, next_tests, score, bucket)
                successors.append(successor)
                if (
                    depth >= 2
                    and len(set(program.stages)) >= 2
                    and all(exact(grid, target) for grid, (_, target) in zip(next_train, train))
                ):
                    signature = tuple(canonical(grid) for grid in next_tests)
                    if signature not in exact_predictions:
                        exact_predictions.add(signature)
                        exact_candidates.append(_composition_candidate_from_node(successor))
                        if len(exact_candidates) >= config.max_exact_candidates:
                            return deduplicate_candidates(exact_candidates)
            if (
                expansions >= config.max_expansions
                or depth_expansions >= depth_quota
            ):
                break
        if not successors:
            break
        successors.sort(
            key=lambda node: (
                node.score,
                node.program.cost,
                tuple(step.name for step in node.program.steps),
            )
        )

        # Preserve one representative per residual/stage bucket before filling
        # the beam globally. This keeps useful temporarily-worse movement states
        # alive long enough for drawing or cleanup to complete them.
        selected: List[CompositionNode] = []
        selected_ids: set[int] = set()
        bucket_seen: set[Tuple[str, Tuple[int, ...]]] = set()
        for index, node in enumerate(successors):
            bucket_key = (node.program.steps[-1].stage, node.residual_bucket)
            if bucket_key in bucket_seen:
                continue
            bucket_seen.add(bucket_key)
            selected.append(node)
            selected_ids.add(index)
            if len(selected) >= config.beam_width:
                break
        if len(selected) < config.beam_width:
            for index, node in enumerate(successors):
                if index in selected_ids:
                    continue
                selected.append(node)
                if len(selected) >= config.beam_width:
                    break
        beam = selected

        if config.completion_width and depth < config.max_depth:
            for node in beam[: config.completion_width]:
                try:
                    terminals = _composition_terminal_candidates(
                        node,
                        train,
                        tests,
                        deep=float(time_limit) > 2.0,
                        maximum_candidates=config.max_exact_candidates
                        - len(exact_candidates),
                    )
                except Exception:
                    terminals = []
                for candidate in terminals:
                    signature = tuple(canonical(grid) for grid in candidate.grids)
                    if signature in exact_predictions:
                        continue
                    exact_predictions.add(signature)
                    exact_candidates.append(candidate)
                    if len(exact_candidates) >= config.max_exact_candidates:
                        return deduplicate_candidates(exact_candidates)
        if expansions >= config.max_expansions:
            break
    return deduplicate_candidates(exact_candidates)


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
    candidates: List[RuleCandidate] = []
    candidates.extend(boundary_run_marker_relocation_rules(train, tests))
    candidates.extend(learned_transform_rules(train, tests))
    candidates.extend(object_color_frequency_rules(train, tests))

    # Retain this common extraction/reflection composition explicitly when it
    # fits every demonstration exactly. The legacy grammar remains bounded and
    # this guard protects an established low-cost hypothesis.
    crop_flip_h = candidate_from_function(
        "program:crop_bbox ; flip_h",
        lambda grid: np.fliplr(crop_bbox_non_bg(grid)),
        train,
        tests,
        5,
        "program",
        metadata={"deterministic_composition_guard": True},
    )
    if crop_flip_h.train_error == 0:
        candidates.append(crop_flip_h)

    candidates.extend(synthesize_program_rules(train, tests, time_limit))

    # Basic fallbacks always included.
    candidates.append(candidate_from_function("fallback_input", lambda g: g.copy(), train, tests, 100, "fallback"))
    candidates.append(candidate_from_function("fallback_crop_bbox", crop_bbox_non_bg, train, tests, 100, "fallback"))
    output_backgrounds = [majority_color(target) for _, target in train]
    background_counts = Counter(output_backgrounds)
    aggregate_background = min(
        background_counts,
        key=lambda value: (-background_counts[value], value),
    )
    for color in [0, aggregate_background]:
        grids = [np.full_like(t, color) for t in tests]
        err = sum(grid_error(np.full_like(x, color), y) for x, y in train)
        train_grids = tuple(np.full_like(x, color) for x, _ in train)
        candidates.append(
            RuleCandidate(
                f"fallback_full_{color}_input_shape",
                grids,
                err,
                120,
                "fallback",
                train_grids=train_grids,
                metadata={
                    "provenance_kind": "test_input_shape_with_symmetric_training_aggregate",
                    "test_input_grounded": True,
                    "permutation_invariant": True,
                    "admissible": True,
                    "output_contract": "input_shape_constant_color",
                },
            )
        )
    return admissible_candidates(deduplicate_candidates(candidates))


def collect_candidates(train: List[Tuple[Array, Array]], tests: List[Array], time_limit: float) -> List[RuleCandidate]:
    """Return every bounded proposal channel, including mixed-stage programs."""
    base = collect_base_candidates(train, tests, time_limit)
    refined = residual_refinement_rules(base, train, tests)
    mask_refined = typed_scalar_mask_refinement_rules(
        base,
        train,
        tests,
        maximum_programs=512,
        maximum_exact=8,
        include_identity=False,
    )
    typed_direct = typed_scalar_mask_rules(train, tests)
    direct = (
        dominant_color_template_rules(train, tests)
        + fixed_corner_extraction_rules(train, tests)
        + frame_extraction_rules(train, tests)
        + inverse_subgrid_object_rules(train, tests)
        + separator_bar_ratio_rules(train, tests)
        + separator_region_summary_rules(train, tests)
        + role_lifted_object_rewrite_rules(train, tests)
        + typed_direct
        + projector_exact_rules(train, tests)
        + structural_exact_rules(train, tests)
        + graph_rewrite_rules(train, tests)
        + obstacle_path_rules(train, tests)
        + recursive_construction_rules(train, tests)
    )
    composed = conditional_composition_rules(train, tests, time_limit)
    return base + refined + mask_refined + direct + composed

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
        tier = 4
    elif family == "signal_local_transducer":
        tier = 3
    elif family in {"fallback", "program"} or family.startswith("program"):
        tier = 2
    elif (
        family.startswith("struct_")
        or family.startswith("causal_")
        or family.startswith("projector")
        or family.startswith("signal_")
        or family.startswith("scene_")
        or family.startswith("transport_")
        or family.startswith("graph_")
        or family.startswith("routing_")
        or family.startswith("recursive_")
    ):
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
    candidates = admissible_candidates(candidates)
    exact_candidates = sorted(
        (candidate for candidate in candidates if candidate.train_error == 0),
        key=_candidate_family_priority,
    )
    approximate = sorted(
        (candidate for candidate in candidates if candidate.train_error != 0),
        key=lambda candidate: (candidate.train_error, *_candidate_family_priority(candidate)),
    )
    selected: List[RuleCandidate] = []
    prediction_seen: set[Tuple[str, Tuple[str, ...]]] = set()
    residual_family_counts: Dict[str, int] = {}

    def add(candidate: RuleCandidate) -> bool:
        signature = tuple(canonical(grid) for grid in candidate.grids)
        prediction_key = (candidate.family, signature)
        if prediction_key in prediction_seen:
            return False
        if candidate.family.startswith("residual_"):
            count = residual_family_counts.get(candidate.family, 0)
            if count >= maximum_residual_per_family:
                return False
            residual_family_counts[candidate.family] = count + 1
        prediction_seen.add(prediction_key)
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


@dataclass(frozen=True)
class MonotoneCandidatePortfolio:
    """A protected v1.2 shallow lane plus bounded additive challengers."""

    baseline: Tuple[RuleCandidate, ...]
    challengers: Tuple[RuleCandidate, ...]
    diagnostics: Dict[str, object]


def _candidate_behavior_key(candidate: RuleCandidate) -> Tuple[Tuple[str, ...], Tuple[str, ...]]:
    return (
        tuple(canonical(grid) for grid in candidate.train_grids),
        tuple(canonical(grid) for grid in candidate.grids),
    )


def _candidate_with_metadata(
    candidate: RuleCandidate,
    **updates: object,
) -> RuleCandidate:
    metadata = dict(candidate.metadata or {})
    metadata.update(updates)
    return RuleCandidate(
        name=candidate.name,
        grids=[grid.copy() for grid in candidate.grids],
        train_error=candidate.train_error,
        complexity=candidate.complexity,
        family=candidate.family,
        train_grids=tuple(grid.copy() for grid in candidate.train_grids),
        metadata=metadata,
    )


def semantic_behavior_quotient(
    candidates: Sequence[RuleCandidate],
) -> List[RuleCandidate]:
    """Keep one canonical representative of each observed behavior class."""

    groups: Dict[Tuple[Tuple[str, ...], Tuple[str, ...]], List[RuleCandidate]] = defaultdict(list)
    for candidate in admissible_candidates(candidates):
        if not candidate.train_grids:
            continue
        groups[_candidate_behavior_key(candidate)].append(candidate)
    output: List[RuleCandidate] = []
    for key in sorted(groups, key=repr):
        aliases = sorted(
            groups[key],
            key=lambda candidate: (
                _candidate_family_priority(candidate),
                candidate.complexity,
                candidate.family,
                candidate.name,
            ),
        )
        chosen = aliases[0]
        mechanisms = sorted(
            {
                str(
                    (candidate.metadata or {}).get(
                        "semantic_mechanism_key",
                        f"{candidate.family}:{candidate.name}",
                    )
                )
                for candidate in aliases
            }
        )
        promotion_eligible = any(
            bool(
                (candidate.metadata or {}).get(
                    "empirical_promotion_eligible",
                    False,
                )
            )
            for candidate in aliases
        )
        output.append(
            _candidate_with_metadata(
                chosen,
                behavior_alias_count=len(aliases),
                behavior_alias_mechanisms=mechanisms,
                behavior_quotiented=True,
                empirical_promotion_eligible=promotion_eligible,
            )
        )
    return sorted(output, key=_candidate_family_priority)


def build_monotone_candidate_portfolio(
    train: List[Tuple[Array, Array]],
    tests: List[Array],
    time_limit: float,
    *,
    baseline_maximum: int = 36,
    challenger_maximum: int = 12,
) -> MonotoneCandidatePortfolio:
    """Collect a frozen shallow lane and a separately capped challenger lane.

    Deep generators are not prefix-monotone, so the shallow tier is executed
    independently.  Challengers are exact-fit only, behavior-quotiented, and
    cannot evict a baseline candidate through a shared global cap.
    """

    requested = max(0.0, float(time_limit))
    baseline_time = min(requested, 0.05)
    baseline_raw = deduplicate_candidates(
        collect_candidates(train, tests, time_limit=baseline_time)
    )
    baseline = prune_candidates_for_bayesian(
        baseline_raw,
        maximum=max(1, int(baseline_maximum)),
    )
    protected_behaviors = {_candidate_behavior_key(candidate) for candidate in baseline}

    deep_raw: List[RuleCandidate] = []
    if requested > 0.1:
        deep_raw = deduplicate_candidates(
            collect_candidates(train, tests, time_limit=requested)
        )
    role_raw = quantified_structural_role_rules(train, tests)
    parity_fill_raw = frame_parity_fill_rules(train, tests)
    rectangular_face_raw = rectangular_face_fill_rules(train, tests)
    periodic_occlusion_raw = periodic_occlusion_reconstruction_rules(train, tests)
    relational_raw = causal_planar_relational_rules(train, tests)
    constructor_raw = audited_structural_constructor_rules(train, tests)
    structural_raw = [
        *constructor_raw,
        *role_raw,
        *parity_fill_raw,
        *rectangular_face_raw,
        *periodic_occlusion_raw,
        *relational_raw,
    ]
    relational_candidate_ids = {id(candidate) for candidate in relational_raw}
    constructor_candidate_ids = {id(candidate) for candidate in constructor_raw}

    proposed: List[RuleCandidate] = []
    for candidate in deep_raw:
        if candidate.train_error != 0 or _candidate_behavior_key(candidate) in protected_behaviors:
            continue
        proposed.append(
            _candidate_with_metadata(
                candidate,
                portfolio_lane="deep_challenger",
                challenger_origin="requested_deep_tier",
            )
        )
    for candidate in structural_raw:
        behavior_key = _candidate_behavior_key(candidate)
        protected_alias = behavior_key in protected_behaviors
        audited_constructor = id(candidate) in constructor_candidate_ids
        certified_protected_alias = bool(
            protected_alias
            and audited_constructor
            and (candidate.metadata or {}).get(
                "empirical_promotion_eligible",
                False,
            )
        )
        if candidate.train_error != 0 or (
            protected_alias and not certified_protected_alias
        ):
            continue
        proposed.append(
            _candidate_with_metadata(
                candidate,
                portfolio_lane=(
                    "planar_relational_challenger"
                    if id(candidate) in relational_candidate_ids
                    else "audited_structural_constructor_challenger"
                    if id(candidate) in constructor_candidate_ids
                    else "structural_role_challenger"
                ),
                challenger_origin=(
                    "causal_planar_relational"
                    if id(candidate) in relational_candidate_ids
                    else "complete_public_training_structural_constructor"
                    if id(candidate) in constructor_candidate_ids
                    else "quantified_structural_role"
                ),
                protected_baseline_behavior_alias=protected_alias,
                certified_protected_baseline_alias=certified_protected_alias,
            )
        )

    quotiented = semantic_behavior_quotient(proposed)
    challengers = prune_candidates_for_bayesian(
        quotiented,
        maximum=max(1, int(challenger_maximum)),
        maximum_residual_per_family=1,
    )
    diagnostics: Dict[str, object] = {
        "policy": "protected_shallow_plus_behavior_quotiented_challengers",
        "requested_time_limit": requested,
        "baseline_time_limit": baseline_time,
        "baseline_cap": int(baseline_maximum),
        "challenger_cap": int(challenger_maximum),
        "baseline_generated_count": len(baseline_raw),
        "baseline_exact_generated_count": sum(
            candidate.train_error == 0 for candidate in baseline_raw
        ),
        "baseline_committed_count": len(baseline),
        "deep_generated_count": len(deep_raw),
        "role_generated_count": len(role_raw),
        "parity_fill_generated_count": len(parity_fill_raw),
        "rectangular_face_generated_count": len(rectangular_face_raw),
        "periodic_occlusion_generated_count": len(periodic_occlusion_raw),
        "planar_relational_generated_count": len(relational_raw),
        "audited_structural_constructor_generated_count": len(constructor_raw),
        "audited_structural_constructor_family_counts": dict(
            Counter(candidate.family for candidate in constructor_raw)
        ),
        "planar_relational_family_counts": dict(
            Counter(candidate.family for candidate in relational_raw)
        ),
        "challenger_proposed_count": len(proposed),
        "challenger_behavior_class_count": len(quotiented),
        "challenger_committed_count": len(challengers),
        "challenger_aliases_removed": max(0, len(proposed) - len(quotiented)),
        "baseline_family_counts": dict(Counter(candidate.family for candidate in baseline)),
        "challenger_family_counts": dict(
            Counter(candidate.family for candidate in challengers)
        ),
        "protected_baseline_behavior_count": len(protected_behaviors),
        "certified_protected_alias_count": sum(
            bool(
                (candidate.metadata or {}).get(
                    "certified_protected_baseline_alias",
                    False,
                )
            )
            for candidate in proposed
        ),
    }
    return MonotoneCandidatePortfolio(
        baseline=tuple(baseline),
        challengers=tuple(challengers),
        diagnostics=diagnostics,
    )


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


def _promote_monotone_portfolio_outputs(
    baseline: List[Dict[str, Grid]],
    challenger_outputs: Sequence[Sequence[Array]],
    challenger_certifications: Optional[Sequence[Sequence[bool]]] = None,
) -> Tuple[List[Dict[str, Grid]], List[Dict[str, object]]]:
    """Protect Attempt 1 and apply an explicit evidence-gated A2 policy.

    Duplicate slots are safe to expand.  A narrow structural compiler may
    additionally mark a challenger as empirically promotion-eligible; that may
    replace a distinct Attempt 2, but it is not a proof of held-out truth and
    its gains and losses must be measured by the release audit.
    """

    final = [
        {
            "attempt_1": [list(row) for row in record["attempt_1"]],
            "attempt_2": [list(row) for row in record["attempt_2"]],
        }
        for record in baseline
    ]
    promotions: List[Dict[str, object]] = []
    for test_index, record in enumerate(final):
        first = as_array(record["attempt_1"])
        second = as_array(record["attempt_2"])
        candidates = (
            challenger_outputs[test_index]
            if test_index < len(challenger_outputs)
            else ()
        )
        certifications = (
            challenger_certifications[test_index]
            if challenger_certifications is not None
            and test_index < len(challenger_certifications)
            else ()
        )
        distinct = [
            (sanitize_grid(candidate), bool(certifications[index]) if index < len(certifications) else False)
            for index, candidate in enumerate(candidates)
            if not exact(candidate, first) and not exact(candidate, second)
        ]
        if not distinct:
            promotions.append(
                {
                    "test_index": int(test_index),
                    "promoted": False,
                    "reason": "no_distinct_challenger",
                }
            )
            continue
        chosen_grid, chosen_certified = distinct[0]
        if not exact(first, second) and not chosen_certified:
            promotions.append(
                {
                    "test_index": int(test_index),
                    "promoted": False,
                    "reason": "two_distinct_baseline_attempts_protected",
                    "challenger_hash": _sric_grid_hash(chosen_grid),
                }
            )
            continue
        record["attempt_2"] = grid_to_list(chosen_grid)
        promotions.append(
            {
                "test_index": int(test_index),
                "promoted": True,
                "policy": (
                    "empirical_structural_attempt_2_override"
                    if chosen_certified and not exact(first, second)
                    else "duplicate_slot_expansion"
                ),
                "empirical_override_eligible": bool(chosen_certified),
                "challenger_hash": _sric_grid_hash(chosen_grid),
            }
        )
    return final, promotions


_ROLE_BOUND_PROMOTION_POLICIES = frozenset(
    {"shadow", "conservative", "certified_replace_attempt2"}
)
_ROLE_BOUND_CANDIDATE_CAP = 24


def role_bound_object_challenger_lane(
    train: List[Tuple[Array, Array]],
    tests: List[Array],
    *,
    maximum_candidates_per_test: int = _ROLE_BOUND_CANDIDATE_CAP,
) -> Tuple[List[Optional[Array]], Dict[str, object]]:
    """Compile each test independently and commit only a unanimous behavior.

    Test-local compilation prevents an ambiguous second test from erasing a
    valid first-test role binding.  The lane is exception-contained and has a
    cap independent of both the 36-candidate baseline and the 12-candidate
    structural challenger portfolio.
    """

    cap = max(0, min(int(maximum_candidates_per_test), _ROLE_BOUND_CANDIDATE_CAP))
    outputs: List[Optional[Array]] = []
    output_records: List[Dict[str, object]] = []
    proposed_total = 0
    committed_total = 0
    quarantined_total = 0
    for test_index, test in enumerate(tests):
        try:
            generated = role_bound_object_rewrite_rules(train, [test])
            proposed_total += len(generated)
            ordered = sorted(
                generated,
                key=lambda candidate: (
                    int(candidate.complexity),
                    str(candidate.family),
                    str(candidate.name),
                ),
            )
            if len(ordered) > cap:
                quarantined_total += len(ordered)
                outputs.append(None)
                output_records.append(
                    {
                        "test_index": int(test_index),
                        "status": "RESOURCE_CAP_ABSTAIN",
                        "generated_candidates": len(generated),
                        "candidate_cap": int(cap),
                        "committed_candidates": 0,
                        "behavior_count": 0,
                        "empirical_promotion_eligible": False,
                    }
                )
                continue
            candidates = ordered
            behavior_groups: Dict[str, List[RuleCandidate]] = defaultdict(list)
            for candidate in candidates:
                behavior_groups[canonical(candidate.grids[0])].append(candidate)
            if not candidates:
                outputs.append(None)
                output_records.append(
                    {
                        "test_index": int(test_index),
                        "status": "NO_EXACT_ROLE_PROGRAM",
                        "generated_candidates": len(generated),
                        "committed_candidates": 0,
                        "behavior_count": 0,
                        "empirical_promotion_eligible": False,
                    }
                )
                continue
            if len(behavior_groups) != 1:
                quarantined_total += len(candidates)
                outputs.append(None)
                output_records.append(
                    {
                        "test_index": int(test_index),
                        "status": "AMBIGUOUS_ROLE_PROGRAM_OUTPUTS",
                        "generated_candidates": len(generated),
                        "capped_candidates": len(candidates),
                        "committed_candidates": 0,
                        "behavior_count": len(behavior_groups),
                        "behavior_hashes": sorted(
                            _sric_grid_hash(group[0].grids[0])
                            for group in behavior_groups.values()
                        ),
                        "empirical_promotion_eligible": False,
                    }
                )
                continue
            support = next(iter(behavior_groups.values()))
            prediction = sanitize_grid(support[0].grids[0])
            eligible_candidates = [
                candidate
                for candidate in support
                if _role_bound_candidate_audit_valid(
                    dict(candidate.metadata or {})
                )
            ]
            eligible = bool(eligible_candidates)
            program_hashes = sorted(
                {
                    str(
                        (candidate.metadata or {}).get(
                            "program_hash", candidate.name
                        )
                    )
                    for candidate in support
                }
            )
            outputs.append(prediction.copy())
            committed_total += len(support)
            output_records.append(
                {
                    "test_index": int(test_index),
                    "status": "UNIQUE_COMMITTED_OUTPUT",
                    "generated_candidates": len(generated),
                    "capped_candidates": len(candidates),
                    "committed_candidates": len(support),
                    "behavior_count": 1,
                    "output_hash": _sric_grid_hash(prediction),
                    "names": [candidate.name for candidate in support],
                    "families": sorted({candidate.family for candidate in support}),
                    "program_hashes": program_hashes,
                    "candidate_metadata": [
                        {
                            "name": candidate.name,
                            "family": candidate.family,
                            "metadata": dict(candidate.metadata or {}),
                        }
                        for candidate in support
                    ],
                    "empirical_promotion_eligible": bool(eligible),
                    "audited_program_hashes": sorted(
                        {
                            str(candidate.metadata.get("program_hash"))
                            for candidate in eligible_candidates
                        }
                    ),
                }
            )
        except RoleBindingAmbiguityError as role_error:
            outputs.append(None)
            output_records.append(
                {
                    "test_index": int(test_index),
                    "status": "AMBIGUOUS_ROLE_PROGRAM_OUTPUTS",
                    "error": f"{type(role_error).__name__}: {role_error}",
                    "generated_candidates": 0,
                    "committed_candidates": 0,
                    "behavior_count": 2,
                    "empirical_promotion_eligible": False,
                }
            )
        except RoleBindingLimitError as role_error:
            outputs.append(None)
            output_records.append(
                {
                    "test_index": int(test_index),
                    "status": "RESOURCE_LIMIT_ABSTAIN",
                    "error": f"{type(role_error).__name__}: {role_error}",
                    "generated_candidates": 0,
                    "committed_candidates": 0,
                    "behavior_count": 0,
                    "empirical_promotion_eligible": False,
                }
            )
        except Exception as role_error:
            outputs.append(None)
            output_records.append(
                {
                    "test_index": int(test_index),
                    "status": "TEST_LOCAL_ROLLBACK",
                    "error": f"{type(role_error).__name__}: {role_error}",
                    "generated_candidates": 0,
                    "committed_candidates": 0,
                    "behavior_count": 0,
                    "empirical_promotion_eligible": False,
                }
            )
    record: Dict[str, object] = {
        "lane": "bounded_role_program_challenger",
        "status": "completed",
        "candidate_cap_per_test": int(cap),
        "proposed_candidates": int(proposed_total),
        "committed_candidates": int(committed_total),
        "quarantined_candidates": int(quarantined_total),
        "test_local_compilation": True,
        "baseline_candidate_cap_shared": False,
        "structural_challenger_cap_shared": False,
        "outputs": output_records,
    }
    return outputs, record


def _promote_role_bound_outputs(
    baseline: List[Dict[str, Grid]],
    challenger_outputs: Sequence[Optional[Array]],
    lane_record: Dict[str, object],
    *,
    policy: str = "certified_replace_attempt2",
    protected_test_indices: Iterable[int] = (),
    test_inputs: Optional[Sequence[Array]] = None,
) -> Tuple[List[Dict[str, Grid]], List[Dict[str, object]]]:
    """Preserve Attempt 1 and never displace an earlier lane's promotion."""

    if policy not in _ROLE_BOUND_PROMOTION_POLICIES:
        raise ValueError(f"unknown role-bound promotion policy {policy!r}")
    protected = {int(index) for index in protected_test_indices}
    final = [
        {
            "attempt_1": [list(row) for row in record["attempt_1"]],
            "attempt_2": [list(row) for row in record["attempt_2"]],
        }
        for record in baseline
    ]
    output_records = lane_record.get("outputs", [])
    promotions: List[Dict[str, object]] = []
    for test_index in range(len(final)):
        challenger = (
            challenger_outputs[test_index]
            if test_index < len(challenger_outputs)
            else None
        )
        support = (
            output_records[test_index]
            if isinstance(output_records, list)
            and test_index < len(output_records)
            and isinstance(output_records[test_index], dict)
            else {}
        )
        if challenger is None:
            promotions.append(
                {
                    "test_index": int(test_index),
                    "promoted": False,
                    "reason": "no_unique_committed_role_output",
                }
            )
            continue
        challenger = sanitize_grid(challenger)
        first = as_array(final[test_index]["attempt_1"])
        second = as_array(final[test_index]["attempt_2"])
        if exact(challenger, first) or exact(challenger, second):
            promotions.append(
                {
                    "test_index": int(test_index),
                    "promoted": False,
                    "reason": "role_output_already_present",
                    "challenger_hash": _sric_grid_hash(challenger),
                }
            )
            continue
        if policy == "shadow":
            promotions.append(
                {
                    "test_index": int(test_index),
                    "promoted": False,
                    "reason": "shadow_policy",
                    "challenger_hash": _sric_grid_hash(challenger),
                }
            )
            continue
        duplicate_slot = exact(first, second)
        audit_receipt_valid = _role_bound_support_audit_valid(support)
        empirically_eligible = bool(
            audit_receipt_valid
            and test_inputs is not None
            and test_index < len(test_inputs)
            and _role_bound_support_execution_valid(
                support,
                challenger,
                as_array(test_inputs[test_index]),
            )
        )
        if test_index in protected and not duplicate_slot:
            promotions.append(
                {
                    "test_index": int(test_index),
                    "promoted": False,
                    "reason": "earlier_challenger_promotion_protected",
                    "challenger_hash": _sric_grid_hash(challenger),
                }
            )
            continue
        if not duplicate_slot and (
            policy != "certified_replace_attempt2" or not empirically_eligible
        ):
            promotions.append(
                {
                    "test_index": int(test_index),
                    "promoted": False,
                    "reason": "two_distinct_attempts_require_empirical_role_gate",
                    "challenger_hash": _sric_grid_hash(challenger),
                    "empirical_promotion_eligible": empirically_eligible,
                    "audit_receipt_valid": audit_receipt_valid,
                }
            )
            continue
        displaced_hash = _sric_grid_hash(second)
        final[test_index]["attempt_2"] = grid_to_list(challenger)
        promotions.append(
            {
                "test_index": int(test_index),
                "promoted": True,
                "policy": (
                    "duplicate_slot_expansion"
                    if duplicate_slot
                    else "certified_role_attempt_2_override"
                ),
                "challenger_hash": _sric_grid_hash(challenger),
                "displaced_attempt_2_hash": displaced_hash,
                "empirical_promotion_eligible": empirically_eligible,
                "audit_receipt_valid": audit_receipt_valid,
                "program_hashes": list(support.get("program_hashes", [])),
            }
        )
    return final, promotions


def _sric_promote_challenger_outputs(
    baseline: List[Dict[str, Grid]],
    challenger_outputs: Sequence[Optional[Array]],
    lane_record: Dict[str, object],
    *,
    policy: str = "conservative",
) -> Tuple[List[Dict[str, Grid]], List[Dict[str, object]]]:
    """Promote without deleting coverage unless an explicit audit opts in."""
    if policy not in _SRIC_PROMOTION_POLICIES:
        raise ValueError(f"unknown SRIC promotion policy {policy!r}")
    final = [
        {
            "attempt_1": [list(row) for row in record["attempt_1"]],
            "attempt_2": [list(row) for row in record["attempt_2"]],
        }
        for record in baseline
    ]
    promotions: List[Dict[str, object]] = []
    output_records = lane_record.get("outputs", [])
    for test_index, challenger in enumerate(challenger_outputs):
        if test_index >= len(final) or challenger is None:
            promotions.append(
                {
                    "test_index": int(test_index),
                    "promoted": False,
                    "reason": "no unique committed challenger",
                }
            )
            continue
        first = as_array(final[test_index]["attempt_1"])
        second = as_array(final[test_index]["attempt_2"])
        if exact(challenger, first) or exact(challenger, second):
            promotions.append(
                {
                    "test_index": int(test_index),
                    "promoted": False,
                    "reason": "challenger already present in baseline attempts",
                    "challenger_hash": _sric_json_hash(challenger.astype(int).tolist()),
                }
            )
            continue
        if policy == "shadow":
            promotions.append(
                {
                    "test_index": int(test_index),
                    "promoted": False,
                    "reason": "shadow policy never changes baseline attempts",
                    "challenger_hash": _sric_grid_hash(challenger),
                }
            )
            continue
        if policy == "conservative" and not exact(first, second):
            promotions.append(
                {
                    "test_index": int(test_index),
                    "promoted": False,
                    "reason": "baseline already contains two distinct outputs",
                    "challenger_hash": _sric_grid_hash(challenger),
                    "policy": "conservative_duplicate_expansion",
                }
            )
            continue
        displaced_hash = _sric_json_hash(second.astype(int).tolist())
        final[test_index]["attempt_2"] = grid_to_list(challenger)
        support = (
            output_records[test_index]
            if isinstance(output_records, list)
            and test_index < len(output_records)
            and isinstance(output_records[test_index], dict)
            else {}
        )
        promotions.append(
            {
                "test_index": int(test_index),
                "promoted": True,
                "policy": (
                    "conservative_duplicate_expansion"
                    if policy == "conservative"
                    else "experimental_replace_attempt2"
                ),
                "challenger_hash": _sric_json_hash(challenger.astype(int).tolist()),
                "displaced_baseline_attempt_2_hash": displaced_hash,
                "families": list(support.get("families", [])),
                "names": list(support.get("names", [])),
                "program_hashes": list(support.get("program_hashes", [])),
            }
        )
    return final, promotions


def _sric_schema_budget(time_limit: float) -> int:
    """Map the declared task tier to a deterministic auxiliary search cap."""
    value = max(0.0, float(time_limit))
    if value <= 0.0:
        return 0
    if value <= 0.1:
        return min(12, _SRIC_MAX_SCHEMA_CHECKS)
    if value <= 1.0:
        return min(27, _SRIC_MAX_SCHEMA_CHECKS)
    return _SRIC_MAX_SCHEMA_CHECKS


_MACRO_PROMOTION_POLICIES = frozenset({"shadow", "conservative", "attempt2"})


def _legacy_macro_runtime():
    """Build the reviewed typed interpreter for persistent macro snapshots.

    The imports remain lazy so ordinary stateless inference and the standalone
    competition path do not load or mutate learner state.
    """

    try:
        from .prequential_learning import (
            legacy_macro_interpreter,
            legacy_macro_interpreter_contract,
        )
    except ImportError:  # standalone runtime with explicitly supplied modules
        from prequential_learning import (
            legacy_macro_interpreter,
            legacy_macro_interpreter_contract,
        )
    return legacy_macro_interpreter(), legacy_macro_interpreter_contract()


def _apply_persistent_macro_lane(
    task: dict,
    train: List[Tuple[Array, Array]],
    tests: List[Array],
    baseline: List[Dict[str, Grid]],
    learner_snapshot: object,
    *,
    policy: str,
    protected_test_indices: Optional[Iterable[int]] = None,
) -> Tuple[List[Dict[str, Grid]], Dict[str, object]]:
    """Execute a sealed learner snapshot as an isolated final challenger.

    Attempt 1 is immutable.  Previously promoted distinct Attempt 2 outputs
    are also protected, which prevents a persistent macro from silently
    erasing a certified structural or role-bound gain.  When multiple active
    exact-demo macros disagree on a test output, the lane abstains instead of
    selecting by incidental bank order.
    """

    if policy not in _MACRO_PROMOTION_POLICIES:
        raise ValueError(f"unknown macro promotion policy {policy!r}")
    try:
        from .macro_runtime import (
            LearnerSnapshot,
            materialize_snapshot_macros,
            task_source_content_hash,
        )
    except ImportError:  # standalone runtime with explicitly supplied modules
        from macro_runtime import (
            LearnerSnapshot,
            materialize_snapshot_macros,
            task_source_content_hash,
        )
    if not isinstance(learner_snapshot, LearnerSnapshot):
        raise TypeError("learner_snapshot must be a LearnerSnapshot")
    interpreter, interpreter_contract = _legacy_macro_runtime()
    learner_snapshot.validate_runtime(
        source_content_hash=task_source_content_hash(task),
        registry=interpreter.registry,
        interpreter_contract=interpreter_contract,
    )
    candidates = materialize_snapshot_macros(
        learner_snapshot,
        interpreter,
        train,
        tests,
        maximum=8,
    )
    protected = {
        int(index) for index in (protected_test_indices or ()) if int(index) >= 0
    }
    final = [
        {
            "attempt_1": [list(row) for row in record["attempt_1"]],
            "attempt_2": [list(row) for row in record["attempt_2"]],
        }
        for record in baseline
    ]
    candidate_records = [
        {
            "name": candidate.name,
            "macro_hash": candidate.macro_hash,
            "program_hash": candidate.program_hash,
            "description_bits": candidate.description_bits,
            "metadata": dict(candidate.metadata),
        }
        for candidate in candidates
    ]
    promotions: List[Dict[str, object]] = []
    for test_index, record in enumerate(final):
        first = as_array(record["attempt_1"])
        second = as_array(record["attempt_2"])
        behavior_groups: Dict[str, list[tuple[object, Array]]] = defaultdict(list)
        for candidate in candidates:
            if test_index >= len(candidate.test_grids):
                continue
            grid = sanitize_grid(candidate.test_grids[test_index])
            if exact(grid, first):
                continue
            behavior_groups[canonical(grid)].append((candidate, grid))

        common = {
            "test_index": int(test_index),
            "policy": policy,
            "behavior_count": len(behavior_groups),
        }
        if not behavior_groups:
            promotions.append(
                {
                    **common,
                    "promoted": False,
                    "reason": "no_distinct_exact_demo_macro",
                }
            )
            continue
        if len(behavior_groups) != 1:
            promotions.append(
                {
                    **common,
                    "promoted": False,
                    "reason": "ambiguous_exact_demo_macro_outputs",
                    "candidate_grid_hashes": sorted(
                        _sric_grid_hash(group[0][1])
                        for group in behavior_groups.values()
                    ),
                }
            )
            continue

        support = next(iter(behavior_groups.values()))
        candidate, grid = support[0]
        candidate_grid_hash = _sric_grid_hash(grid)
        macro_facts = {
            "macro_hash": candidate.macro_hash,
            "program_hash": candidate.program_hash,
            "candidate_grid_hash": candidate_grid_hash,
            "supporting_macro_hashes": sorted(
                item.macro_hash for item, _ in support
            ),
        }
        if exact(grid, second):
            promotions.append(
                {
                    **common,
                    **macro_facts,
                    "promoted": False,
                    "reason": "macro_already_present_as_attempt2",
                }
            )
            continue
        if policy == "shadow":
            promotions.append(
                {
                    **common,
                    **macro_facts,
                    "promoted": False,
                    "reason": "shadow_only",
                }
            )
            continue
        duplicate_slot = exact(first, second)
        if test_index in protected and not duplicate_slot:
            promotions.append(
                {
                    **common,
                    **macro_facts,
                    "promoted": False,
                    "reason": "earlier_challenger_promotion_protected",
                }
            )
            continue
        if policy == "conservative" and not duplicate_slot:
            promotions.append(
                {
                    **common,
                    **macro_facts,
                    "promoted": False,
                    "reason": "protected_distinct_attempt2",
                }
            )
            continue

        displaced_hash = _sric_grid_hash(second)
        record["attempt_2"] = grid_to_list(grid)
        promotions.append(
            {
                **common,
                **macro_facts,
                "promoted": True,
                "reason": (
                    "filled_duplicate_attempt2"
                    if duplicate_slot
                    else "replaced_attempt2"
                ),
                "displaced_attempt_2_hash": displaced_hash,
            }
        )

    return final, {
        "lane": "persistent_macro_challenger",
        "status": "completed",
        "policy": policy,
        "read_only_inference": True,
        "snapshot_hash": learner_snapshot.content_hash(),
        "query_receipt_hash": learner_snapshot.receipt.content_hash(),
        "sequence_index": learner_snapshot.sequence_index,
        "active_macro_count": len(learner_snapshot.macros),
        "exact_current_demo_macro_count": len(candidates),
        "protected_test_indices": sorted(protected),
        "candidates": candidate_records,
        "promotions": promotions,
    }


def solve_task(
    task: dict,
    time_limit: float = DEFAULT_TIME_LIMIT_PER_TASK,
    *,
    lasm_model: Optional[BayesianProjectorResolvedLargeSignalModel] = None,
    legacy_ranking: bool = False,
    sric_challenger: bool = True,
    sric_promotion_policy: str = "conservative",
    role_bound_challenger: bool = True,
    role_bound_promotion_policy: str = "certified_replace_attempt2",
    learner_snapshot: Optional[object] = None,
    macro_promotion_policy: str = "conservative",
    diagnostics: Optional[Dict[str, object]] = None,
) -> List[Dict[str, Grid]]:
    train = [(as_array(p["input"]), as_array(p["output"])) for p in task.get("train", []) if "input" in p and "output" in p]
    tests = [as_array(p["input"]) for p in task.get("test", []) if "input" in p]
    if not tests:
        return []
    if not train:
        return [{"attempt_1": grid_to_list(t), "attempt_2": grid_to_list(crop_bbox_non_bg(t))} for t in tests]
    if sric_promotion_policy not in _SRIC_PROMOTION_POLICIES:
        raise ValueError(f"unknown SRIC promotion policy {sric_promotion_policy!r}")
    if role_bound_promotion_policy not in _ROLE_BOUND_PROMOTION_POLICIES:
        raise ValueError(
            f"unknown role-bound promotion policy {role_bound_promotion_policy!r}"
        )
    if macro_promotion_policy not in _MACRO_PROMOTION_POLICIES:
        raise ValueError(f"unknown macro promotion policy {macro_promotion_policy!r}")

    # Identity demonstrations are a complete, exact, and very common contract.
    # Resolve them before entering the broad proposal portfolio. This also keeps
    # dense 30x30 no-op tasks deterministic and well inside hard isolation.
    if all(exact(source, target) for source, target in train):
        results = [
            {
                "attempt_1": grid_to_list(test),
                "attempt_2": grid_to_list(crop_bbox_non_bg(test)),
            }
            for test in tests
        ]
        if diagnostics is not None:
            model = lasm_model or default_lasm_model()
            diagnostics.update(
                {
                    "mode": "identity_fast_path",
                    "candidate_count": 2,
                    "exact_fit_candidate_count": 1,
                    "candidate_family_counts": {
                        "learned_transform": 1,
                        "fallback": 1,
                    },
                    "calibration_version": model.calibration.model_version,
                    "selected_attempts": [],
                }
            )
        return results

    if legacy_ranking:
        candidates = prune_candidates_for_bayesian(
            deduplicate_candidates(
                collect_candidates(train, tests, time_limit=time_limit)
            )
        )
        if not candidates:
            return [
                {
                    "attempt_1": grid_to_list(test),
                    "attempt_2": grid_to_list(crop_bbox_non_bg(test)),
                }
                for test in tests
            ]
        results = []
        for index in range(len(tests)):
            first, second = legacy_rank_predictions(candidates, index, k=2)
            results.append({"attempt_1": grid_to_list(first), "attempt_2": grid_to_list(second)})
        macro_lane: Dict[str, object] = {
            "lane": "persistent_macro_challenger",
            "status": "disabled",
            "policy": macro_promotion_policy,
            "read_only_inference": True,
            "active_macro_count": 0,
            "exact_current_demo_macro_count": 0,
            "protected_test_indices": [],
            "candidates": [],
            "promotions": [],
        }
        if learner_snapshot is not None:
            try:
                results, macro_lane = _apply_persistent_macro_lane(
                    task,
                    train,
                    tests,
                    results,
                    learner_snapshot,
                    policy=macro_promotion_policy,
                )
            except Exception as macro_error:
                macro_lane = {
                    "lane": "persistent_macro_challenger",
                    "status": "rolled_back_to_baseline",
                    "policy": macro_promotion_policy,
                    "read_only_inference": True,
                    "error": f"{type(macro_error).__name__}: {macro_error}",
                    "active_macro_count": 0,
                    "exact_current_demo_macro_count": 0,
                    "protected_test_indices": [],
                    "candidates": [],
                    "promotions": [],
                }
        if diagnostics is not None:
            diagnostics.update(
                {
                    "mode": "legacy",
                    "candidate_count": len(candidates),
                    "persistent_macro": macro_lane,
                    "macro_promotion_policy": macro_promotion_policy,
                }
            )
        return results

    portfolio = build_monotone_candidate_portfolio(train, tests, time_limit)
    candidates = list(portfolio.baseline)
    challenger_candidates = list(portfolio.challengers)
    if not candidates:
        return [
            {
                "attempt_1": grid_to_list(test),
                "attempt_2": grid_to_list(crop_bbox_non_bg(test)),
            }
            for test in tests
        ]

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
                    "candidate_metadata": [
                        {
                            "name": candidates[candidate_index].name,
                            "family": candidates[candidate_index].family,
                            "metadata": dict(candidates[candidate_index].metadata or {}),
                        }
                        for candidate_index in output.candidate_indices
                        if 0 <= candidate_index < len(candidates)
                    ],
                    "shape": list(output.grid.shape),
                }
                for attempt_index, output in enumerate(selected_outputs[:2])
            ])
        baseline_selected_diagnostics = [list(records) for records in selected_diagnostics]

        monotone_lane: Dict[str, object] = {
            "lane": "monotone_hierarchical_portfolio",
            "status": "no_challengers",
            "portfolio": dict(portfolio.diagnostics),
            "alias_invariant_posterior": True,
            "outputs": [],
        }
        portfolio_promotions: List[Dict[str, object]] = []
        challenger_selected_diagnostics: List[List[Dict[str, object]]] = [
            [] for _ in tests
        ]
        if challenger_candidates:
            try:
                challenger_posterior = model.fit_posterior(
                    challenger_candidates,
                    train,
                    tests,
                    alias_invariant=True,
                )
                challenger_grids: List[List[Array]] = []
                challenger_certifications: List[List[bool]] = []
                for test_index in range(len(tests)):
                    selected_outputs = model.select_output_posteriors(
                        challenger_posterior,
                        test_index,
                        k=2,
                    )
                    selected_grids = [output.grid.copy() for output in selected_outputs]
                    selected_certifications = [
                            any(
                                bool(
                                    (challenger_candidates[candidate_index].metadata or {}).get(
                                        "empirical_promotion_eligible",
                                        False,
                                    )
                                )
                                for candidate_index in output.candidate_indices
                                if 0 <= candidate_index < len(challenger_candidates)
                            )
                            for output in selected_outputs
                    ]
                    certified_candidates = [
                        candidate
                        for candidate in challenger_candidates
                        if bool((candidate.metadata or {}).get("empirical_promotion_eligible", False))
                    ]
                    for candidate in reversed(certified_candidates):
                        certified_grid = sanitize_grid(candidate.grids[test_index])
                        if any(exact(certified_grid, grid) for grid in selected_grids):
                            existing = next(
                                index
                                for index, grid in enumerate(selected_grids)
                                if exact(certified_grid, grid)
                            )
                            selected_certifications[existing] = True
                            continue
                        selected_grids.insert(0, certified_grid.copy())
                        selected_certifications.insert(0, True)
                    challenger_grids.append(selected_grids)
                    challenger_certifications.append(selected_certifications)
                    challenger_selected_diagnostics[test_index] = [
                        {
                            "attempt": attempt_index + 1,
                            "selection_lane": "monotone_challenger",
                            "probability": output.probability,
                            "exact_fit_probability": output.exact_fit_probability,
                            "exact_fit_candidate_count": output.exact_fit_candidate_count,
                            "best_candidate_probability": output.best_candidate_probability,
                            "families": list(output.families),
                            "names": list(output.names),
                            "channel_probabilities": dict(output.channel_probabilities),
                            "candidate_metadata": [
                                {
                                    "name": challenger_candidates[candidate_index].name,
                                    "family": challenger_candidates[candidate_index].family,
                                    "metadata": dict(
                                        challenger_candidates[candidate_index].metadata or {}
                                    ),
                                }
                                for candidate_index in output.candidate_indices
                                if 0 <= candidate_index < len(challenger_candidates)
                            ],
                            "grid_hash": _sric_grid_hash(output.grid),
                            "empirical_promotion_eligible": any(
                                bool(
                                    (challenger_candidates[candidate_index].metadata or {}).get(
                                        "empirical_promotion_eligible",
                                        False,
                                    )
                                )
                                for candidate_index in output.candidate_indices
                                if 0 <= candidate_index < len(challenger_candidates)
                            ),
                            "shape": list(output.grid.shape),
                        }
                        for attempt_index, output in enumerate(selected_outputs[:2])
                    ]
                    for candidate in reversed(certified_candidates):
                        certified_grid = sanitize_grid(candidate.grids[test_index])
                        certified_hash = _sric_grid_hash(certified_grid)
                        if any(
                            record.get("grid_hash") == certified_hash
                            for record in challenger_selected_diagnostics[test_index]
                        ):
                            continue
                        challenger_selected_diagnostics[test_index].insert(
                            0,
                            {
                                "attempt": 1,
                                "selection_lane": "empirical_structural_challenger",
                                "probability": None,
                                "exact_fit_probability": 1.0,
                                "exact_fit_candidate_count": 1,
                                "best_candidate_probability": None,
                                "families": [candidate.family],
                                "names": [candidate.name],
                                "channel_probabilities": {"base": 0.0, "structural": 1.0},
                                "candidate_metadata": [
                                    {
                                        "name": candidate.name,
                                        "family": candidate.family,
                                        "metadata": dict(candidate.metadata or {}),
                                    }
                                ],
                                "grid_hash": certified_hash,
                                "empirical_promotion_eligible": True,
                                "shape": list(certified_grid.shape),
                            },
                        )
                results, portfolio_promotions = _promote_monotone_portfolio_outputs(
                    results,
                    challenger_grids,
                    challenger_certifications,
                )
                monotone_lane.update(
                    {
                        "status": "completed_duplicate_or_empirical_promotion",
                        "outputs": challenger_selected_diagnostics,
                        "promotions": portfolio_promotions,
                        "posterior": challenger_posterior.diagnostics(),
                    }
                )
            except Exception as challenger_error:
                monotone_lane.update(
                    {
                        "status": "rolled_back_to_protected_baseline",
                        "error": f"{type(challenger_error).__name__}: {challenger_error}",
                        "promotions": [],
                    }
                )

        final_selected_diagnostics = [list(records) for records in selected_diagnostics]
        for promotion in portfolio_promotions:
            if not bool(promotion.get("promoted")):
                continue
            test_index = int(promotion["test_index"])
            if not (0 <= test_index < len(final_selected_diagnostics)):
                continue
            matching_record: Optional[Dict[str, object]] = None
            for record in challenger_selected_diagnostics[test_index]:
                if record.get("grid_hash") == promotion.get("challenger_hash"):
                    matching_record = dict(record)
                    break
            if matching_record is None and challenger_selected_diagnostics[test_index]:
                matching_record = dict(challenger_selected_diagnostics[test_index][0])
            if matching_record is not None:
                matching_record["attempt"] = 2
                if final_selected_diagnostics[test_index]:
                    final_selected_diagnostics[test_index] = [
                        final_selected_diagnostics[test_index][0],
                        matching_record,
                    ]
                else:
                    final_selected_diagnostics[test_index] = [matching_record]

        sric_lane: Dict[str, object] = {
            "lane": "sric_relational_challenger",
            "status": "disabled",
            "proposed_candidates": 0,
            "committed_candidates": 0,
            "quarantined_candidates": 0,
            "receipt_envelope": None,
            "receipt_verification": {"valid": True, "errors": []},
            "outputs": [],
        }
        promotions: List[Dict[str, object]] = []
        if sric_challenger:
            try:
                challenger_outputs, sric_lane = sric_relational_challenger_lane(
                    train,
                    tests,
                    maximum_schema_checks=_sric_schema_budget(time_limit),
                )
                results, promotions = _sric_promote_challenger_outputs(
                    results,
                    challenger_outputs,
                    sric_lane,
                    policy=sric_promotion_policy,
                )
                if sric_lane.get("status") != "RESOURCE_ABSTAIN":
                    sric_lane["status"] = f"completed_{sric_promotion_policy}"
            except Exception as sric_error:
                # The challenger is an isolated lane.  Any implementation or
                # applicability error leaves the frozen baseline attempts exact.
                sric_lane = {
                    "lane": "sric_relational_challenger",
                    "status": "rolled_back_to_baseline",
                    "error": f"{type(sric_error).__name__}: {sric_error}",
                    "proposed_candidates": 0,
                    "committed_candidates": 0,
                    "quarantined_candidates": 0,
                    "receipt_envelope": None,
                    "receipt_verification": {"valid": False, "errors": []},
                    "outputs": [],
                }
        output_records = sric_lane.get("outputs", [])
        for promotion in promotions:
            if not bool(promotion.get("promoted")):
                continue
            test_index = int(promotion["test_index"])
            if not (0 <= test_index < len(final_selected_diagnostics)):
                continue
            support = (
                output_records[test_index]
                if isinstance(output_records, list)
                and test_index < len(output_records)
                and isinstance(output_records[test_index], dict)
                else {}
            )
            challenger_record = {
                "attempt": 2,
                "selection_lane": "sric_relational_challenger",
                "probability": None,
                "exact_fit_probability": None,
                "exact_fit_candidate_count": len(support.get("names", [])),
                "best_candidate_probability": None,
                "families": list(support.get("families", [])),
                "names": list(support.get("names", [])),
                "channel_probabilities": {"base": 0.0, "structural": 1.0},
                "candidate_metadata": list(support.get("candidate_metadata", [])),
                "shape": list(as_array(results[test_index]["attempt_2"]).shape),
            }
            if final_selected_diagnostics[test_index]:
                final_selected_diagnostics[test_index] = [
                    final_selected_diagnostics[test_index][0],
                    challenger_record,
                ]
            else:
                final_selected_diagnostics[test_index] = [challenger_record]

        role_bound_lane: Dict[str, object] = {
            "lane": "bounded_role_program_challenger",
            "status": "disabled",
            "candidate_cap_per_test": _ROLE_BOUND_CANDIDATE_CAP,
            "proposed_candidates": 0,
            "committed_candidates": 0,
            "quarantined_candidates": 0,
            "test_local_compilation": True,
            "outputs": [],
        }
        role_bound_promotions: List[Dict[str, object]] = []
        if role_bound_challenger:
            try:
                role_outputs, role_bound_lane = role_bound_object_challenger_lane(
                    train,
                    tests,
                )
                previously_promoted = {
                    int(record["test_index"])
                    for record in [*portfolio_promotions, *promotions]
                    if bool(record.get("promoted"))
                }
                results, role_bound_promotions = _promote_role_bound_outputs(
                    results,
                    role_outputs,
                    role_bound_lane,
                    policy=role_bound_promotion_policy,
                    protected_test_indices=previously_promoted,
                    test_inputs=tests,
                )
            except Exception as role_bound_error:
                role_bound_lane = {
                    "lane": "bounded_role_program_challenger",
                    "status": "rolled_back_to_prior_attempts",
                    "error": (
                        f"{type(role_bound_error).__name__}: {role_bound_error}"
                    ),
                    "candidate_cap_per_test": _ROLE_BOUND_CANDIDATE_CAP,
                    "proposed_candidates": 0,
                    "committed_candidates": 0,
                    "quarantined_candidates": 0,
                    "test_local_compilation": True,
                    "outputs": [],
                }
        role_output_records = role_bound_lane.get("outputs", [])
        for promotion in role_bound_promotions:
            if not bool(promotion.get("promoted")):
                continue
            test_index = int(promotion["test_index"])
            if not (0 <= test_index < len(final_selected_diagnostics)):
                continue
            support = (
                role_output_records[test_index]
                if isinstance(role_output_records, list)
                and test_index < len(role_output_records)
                and isinstance(role_output_records[test_index], dict)
                else {}
            )
            role_record = {
                "attempt": 2,
                "selection_lane": "bounded_role_program_challenger",
                "probability": None,
                "exact_fit_probability": 1.0,
                "exact_fit_candidate_count": int(
                    support.get("committed_candidates", 0)
                ),
                "best_candidate_probability": None,
                "families": list(support.get("families", [])),
                "names": list(support.get("names", [])),
                "channel_probabilities": {"base": 0.0, "structural": 1.0},
                "candidate_metadata": list(
                    support.get("candidate_metadata", [])
                ),
                "shape": list(as_array(results[test_index]["attempt_2"]).shape),
            }
            if final_selected_diagnostics[test_index]:
                final_selected_diagnostics[test_index] = [
                    final_selected_diagnostics[test_index][0],
                    role_record,
                ]
            else:
                final_selected_diagnostics[test_index] = [role_record]

        macro_lane: Dict[str, object] = {
            "lane": "persistent_macro_challenger",
            "status": "disabled",
            "policy": macro_promotion_policy,
            "read_only_inference": True,
            "active_macro_count": 0,
            "exact_current_demo_macro_count": 0,
            "protected_test_indices": [],
            "candidates": [],
            "promotions": [],
        }
        if learner_snapshot is not None:
            prior_promoted = {
                int(record["test_index"])
                for record in [
                    *portfolio_promotions,
                    *promotions,
                    *role_bound_promotions,
                ]
                if bool(record.get("promoted"))
            }
            try:
                results, macro_lane = _apply_persistent_macro_lane(
                    task,
                    train,
                    tests,
                    results,
                    learner_snapshot,
                    policy=macro_promotion_policy,
                    protected_test_indices=prior_promoted,
                )
            except Exception as macro_error:
                macro_lane = {
                    "lane": "persistent_macro_challenger",
                    "status": "rolled_back_to_prior_attempts",
                    "policy": macro_promotion_policy,
                    "read_only_inference": True,
                    "error": f"{type(macro_error).__name__}: {macro_error}",
                    "active_macro_count": 0,
                    "exact_current_demo_macro_count": 0,
                    "protected_test_indices": sorted(prior_promoted),
                    "candidates": [],
                    "promotions": [],
                }
        macro_promotions = macro_lane.get("promotions", [])
        if isinstance(macro_promotions, list):
            for promotion in macro_promotions:
                if not isinstance(promotion, dict) or not bool(
                    promotion.get("promoted")
                ):
                    continue
                test_index = int(promotion["test_index"])
                if not (0 <= test_index < len(final_selected_diagnostics)):
                    continue
                macro_record = {
                    "attempt": 2,
                    "selection_lane": "persistent_macro_challenger",
                    "probability": None,
                    "exact_fit_probability": 1.0,
                    "exact_fit_candidate_count": int(
                        macro_lane.get("exact_current_demo_macro_count", 0)
                    ),
                    "best_candidate_probability": None,
                    "families": ["persistent_typed_macro"],
                    "names": [str(promotion.get("program_hash", ""))],
                    "channel_probabilities": {"base": 0.0, "learned": 1.0},
                    "candidate_metadata": [dict(promotion)],
                    "shape": list(as_array(results[test_index]["attempt_2"]).shape),
                }
                if final_selected_diagnostics[test_index]:
                    final_selected_diagnostics[test_index] = [
                        final_selected_diagnostics[test_index][0],
                        macro_record,
                    ]
                else:
                    final_selected_diagnostics[test_index] = [macro_record]
        if diagnostics is not None:
            exact_candidate_count = sum(candidate.train_error == 0 for candidate in candidates)
            family_counts = dict(Counter(candidate.family for candidate in candidates))
            diagnostics.update({
                "mode": "bayesian_pr_lasm",
                "candidate_count": len(candidates),
                "exact_fit_candidate_count": exact_candidate_count,
                "candidate_family_counts": family_counts,
                "calibration_version": model.calibration.model_version,
                "selected_attempts": final_selected_diagnostics,
                "baseline_selected_attempts": baseline_selected_diagnostics,
                "monotone_portfolio": monotone_lane,
                "monotone_portfolio_promotions": portfolio_promotions,
                "sric_challenger": sric_lane,
                "sric_promotion_policy": sric_promotion_policy,
                "sric_promotions": promotions,
                "role_bound_challenger": role_bound_lane,
                "role_bound_promotion_policy": role_bound_promotion_policy,
                "role_bound_promotions": role_bound_promotions,
                "persistent_macro": macro_lane,
                "macro_promotion_policy": macro_promotion_policy,
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
        macro_lane: Dict[str, object] = {
            "lane": "persistent_macro_challenger",
            "status": "disabled",
            "policy": macro_promotion_policy,
            "read_only_inference": True,
            "active_macro_count": 0,
            "exact_current_demo_macro_count": 0,
            "protected_test_indices": [],
            "candidates": [],
            "promotions": [],
        }
        if learner_snapshot is not None:
            try:
                results, macro_lane = _apply_persistent_macro_lane(
                    task,
                    train,
                    tests,
                    results,
                    learner_snapshot,
                    policy=macro_promotion_policy,
                )
            except Exception as macro_error:
                macro_lane = {
                    "lane": "persistent_macro_challenger",
                    "status": "rolled_back_to_baseline",
                    "policy": macro_promotion_policy,
                    "read_only_inference": True,
                    "error": f"{type(macro_error).__name__}: {macro_error}",
                    "active_macro_count": 0,
                    "exact_current_demo_macro_count": 0,
                    "protected_test_indices": [],
                    "candidates": [],
                    "promotions": [],
                }
        if diagnostics is not None:
            diagnostics.update({
                "mode": "legacy_fallback",
                "candidate_count": len(candidates),
                "bayesian_error": f"{type(exc).__name__}: {exc}",
                "persistent_macro": macro_lane,
                "macro_promotion_policy": macro_promotion_policy,
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
            "signal topology and transport",
            "paired-object connection",
            "path or ray drawing",
            "boundary and symmetry completion",
            "periodic continuation",
        ],
        "movement_or_permutation": [
            "object-conditioned signal transport",
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
            "multi-stage signal transport",
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


def _selected_activation_traits(
    selected_attempts: Sequence[Dict[str, object]],
) -> Dict[str, bool]:
    """Recover multi-label mechanism activations from selected candidates."""
    families: set[str] = set()
    stages: set[str] = set()
    mechanisms: set[str] = set()
    recursive_flag = False
    scalar_mask_flag = False
    for attempt in selected_attempts:
        if not isinstance(attempt, dict):
            continue
        family_values = attempt.get("families", [])
        if isinstance(family_values, list):
            families.update(str(family) for family in family_values)
        candidate_records = attempt.get("candidate_metadata", [])
        if not isinstance(candidate_records, list):
            continue
        for candidate_record in candidate_records:
            if not isinstance(candidate_record, dict):
                continue
            metadata = candidate_record.get("metadata", {})
            if not isinstance(metadata, dict):
                continue
            stage_values = metadata.get("stages", [])
            if isinstance(stage_values, list):
                stages.update(str(stage) for stage in stage_values)
            mechanism_values = metadata.get("mechanism_keys", [])
            if isinstance(mechanism_values, list):
                mechanisms.update(str(mechanism) for mechanism in mechanism_values)
            recursive_flag = recursive_flag or bool(metadata.get("recursive"))
            scalar_mask_flag = scalar_mask_flag or bool(metadata.get("typed_scalar_mask"))
    return {
        "signal": any(family.startswith("signal_") for family in families),
        "transport": (
            any(family.startswith("transport_") for family in families)
            or "transport" in stages
        ),
        "composition": any(family.startswith("composition_") for family in families),
        "routing": (
            any(family.startswith("routing_") for family in families)
            or "obstacle_route" in mechanisms
        ),
        "recursive": (
            any(family.startswith("recursive_") for family in families)
            or "recursive" in stages
            or recursive_flag
        ),
        "scalar_mask": (
            any(
                family.startswith("composition_scalar_mask")
                or "predicate_rewrite" in family
                or "cardinality_renderer" in family
                or "mask_motif_broadcast" in family
                for family in families
            )
            or any(
                mechanism.startswith("struct_object_predicate_rewrite")
                or mechanism.startswith("struct_region_predicate_rewrite")
                or mechanism.startswith("struct_cardinality_renderer")
                or mechanism.startswith("struct_mask_motif_broadcast")
                or mechanism.startswith("composition_scalar_mask")
                for mechanism in mechanisms
            )
            or scalar_mask_flag
        ),
    }


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
    selected_family_counts: Counter[str] = Counter()
    selected_program_counts: Counter[str] = Counter()
    signal_selected_outputs = 0
    signal_solved_outputs = 0
    transport_selected_outputs = 0
    transport_solved_outputs = 0
    composition_selected_outputs = 0
    composition_solved_outputs = 0
    routing_selected_outputs = 0
    routing_solved_outputs = 0
    recursive_selected_outputs = 0
    recursive_solved_outputs = 0
    scalar_mask_selected_outputs = 0
    scalar_mask_solved_outputs = 0
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
            for attempt in selected_attempts:
                if not isinstance(attempt, dict):
                    continue
                for family in attempt.get("families", []) if isinstance(attempt.get("families"), list) else []:
                    family_name = str(family)
                    selected_family_counts[family_name] += 1
                for program_name in attempt.get("names", []) if isinstance(attempt.get("names"), list) else []:
                    selected_program_counts[str(program_name)] += 1
            traits = _selected_activation_traits(selected_attempts)
            selected_signal = traits["signal"]
            selected_transport = traits["transport"]
            selected_composition = traits["composition"]
            selected_routing = traits["routing"]
            selected_recursive = traits["recursive"]
            selected_scalar_mask = traits["scalar_mask"]
            signal_selected_outputs += int(selected_signal)
            signal_solved_outputs += int(selected_signal and bool(record["solved"]))
            transport_selected_outputs += int(selected_transport)
            transport_solved_outputs += int(selected_transport and bool(record["solved"]))
            composition_selected_outputs += int(selected_composition)
            composition_solved_outputs += int(selected_composition and bool(record["solved"]))
            routing_selected_outputs += int(selected_routing)
            routing_solved_outputs += int(selected_routing and bool(record["solved"]))
            recursive_selected_outputs += int(selected_recursive)
            recursive_solved_outputs += int(selected_recursive and bool(record["solved"]))
            scalar_mask_selected_outputs += int(selected_scalar_mask)
            scalar_mask_solved_outputs += int(selected_scalar_mask and bool(record["solved"]))
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
        "selected_family_counts": dict(selected_family_counts),
        "selected_program_counts_top_25": dict(selected_program_counts.most_common(25)),
        "signal_selected_outputs": signal_selected_outputs,
        "signal_solved_outputs": signal_solved_outputs,
        "signal_selected_exact_rate": (signal_solved_outputs / signal_selected_outputs) if signal_selected_outputs else None,
        "transport_selected_outputs": transport_selected_outputs,
        "transport_solved_outputs": transport_solved_outputs,
        "transport_selected_exact_rate": (transport_solved_outputs / transport_selected_outputs) if transport_selected_outputs else None,
        "composition_selected_outputs": composition_selected_outputs,
        "composition_solved_outputs": composition_solved_outputs,
        "composition_selected_exact_rate": (composition_solved_outputs / composition_selected_outputs) if composition_selected_outputs else None,
        "routing_selected_outputs": routing_selected_outputs,
        "routing_solved_outputs": routing_solved_outputs,
        "routing_selected_exact_rate": (routing_solved_outputs / routing_selected_outputs) if routing_selected_outputs else None,
        "recursive_selected_outputs": recursive_selected_outputs,
        "recursive_solved_outputs": recursive_solved_outputs,
        "recursive_selected_exact_rate": (recursive_solved_outputs / recursive_selected_outputs) if recursive_selected_outputs else None,
        "scalar_mask_selected_outputs": scalar_mask_selected_outputs,
        "scalar_mask_solved_outputs": scalar_mask_solved_outputs,
        "scalar_mask_selected_exact_rate": (scalar_mask_solved_outputs / scalar_mask_selected_outputs) if scalar_mask_selected_outputs else None,
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
    sric_challenger: bool = True,
    sric_promotion_policy: str = "conservative",
    role_bound_challenger: bool = True,
    role_bound_promotion_policy: str = "certified_replace_attempt2",
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
            sric_challenger=sric_challenger,
            sric_promotion_policy=sric_promotion_policy,
            role_bound_challenger=role_bound_challenger,
            role_bound_promotion_policy=role_bound_promotion_policy,
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
                "sric_challenger": bool(sric_challenger),
                "sric_promotion_policy": sric_promotion_policy,
                "role_bound_challenger": bool(role_bound_challenger),
                "role_bound_promotion_policy": role_bound_promotion_policy,
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
    sric_challenger: bool = True,
    sric_promotion_policy: str = "conservative",
    role_bound_challenger: bool = True,
    role_bound_promotion_policy: str = "certified_replace_attempt2",
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
        sric_challenger=sric_challenger,
        sric_promotion_policy=sric_promotion_policy,
        role_bound_challenger=role_bound_challenger,
        role_bound_promotion_policy=role_bound_promotion_policy,
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
        "sric_challenger": bool(sric_challenger),
        "sric_promotion_policy": sric_promotion_policy,
        "role_bound_challenger": bool(role_bound_challenger),
        "role_bound_promotion_policy": role_bound_promotion_policy,
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
    parser.add_argument(
        "--sric-mode",
        choices=sorted(_SRIC_PROMOTION_POLICIES),
        default="conservative",
        help=(
            "SRIC challenger handling: conservative only fills a duplicate "
            "baseline slot; shadow records without promotion; replace_attempt2 "
            "is an experimental labeled A/B mode"
        ),
    )
    parser.add_argument(
        "--disable-sric-challenger",
        action="store_true",
        help="disable the isolated SRIC relational challenger lane",
    )
    parser.add_argument(
        "--role-bound-mode",
        choices=sorted(_ROLE_BOUND_PROMOTION_POLICIES),
        default="certified_replace_attempt2",
        help=(
            "role-bound challenger handling: certified_replace_attempt2 may "
            "replace attempt 2 only for empirically gated programs; "
            "conservative only fills a duplicate baseline slot; shadow records "
            "without promotion"
        ),
    )
    parser.add_argument(
        "--disable-role-bound-challenger",
        action="store_true",
        help="disable the isolated causal role-bound object-program lane",
    )
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
                sric_challenger=not args.disable_sric_challenger,
                sric_promotion_policy=args.sric_mode,
                role_bound_challenger=not args.disable_role_bound_challenger,
                role_bound_promotion_policy=args.role_bound_mode,
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
            sric_challenger=not args.disable_sric_challenger,
            sric_promotion_policy=args.sric_mode,
            role_bound_challenger=not args.disable_role_bound_challenger,
            role_bound_promotion_policy=args.role_bound_mode,
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
        if args.input or args.solutions:
            print(
                "An explicit ARC input or solution path failed; refusing to "
                "replace the requested audit with a self-test.",
                file=sys.stderr,
            )
            return 2
        print("No runnable ARC input detected; running self-test instead.", file=sys.stderr)
        run_self_test()
        return 0


if __name__ == "__main__":
    raise SystemExit(main())
