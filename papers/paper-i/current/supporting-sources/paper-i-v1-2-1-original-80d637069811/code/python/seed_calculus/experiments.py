from __future__ import annotations

import json
import platform
from pathlib import Path

import numpy as np
import sympy as sp

from .algebra import elliptic_packet_matrix, elliptic_reduce, x, y
from .core import (
    cyclic_span_dimension,
    krylov_rank_profile,
    matrix_units,
    projector_residuals,
    reconstruct_operator,
    semisimple_seed_rank,
    single_operator_seed_rank,
    transfer_blocks,
    transport_projectors,
)
from .examples import (
    bilateral_shift_matrix,
    companion_matrix,
    coordinate_projectors,
    full_matrix_orbit_dimension,
    repeated_jordan_operator,
    residue_projectors,
)
from .graphs import cycle_adjacency, endpoint_krylov_determinant_path, path_adjacency, symmetric_graph_seed_rank

MANUSCRIPT_VERSION = "1.2.1"
PYTHON_COMPANION_VERSION = "1.1.1"
RNG_SEED = 20260727
SHIFT_SUPPORT_TOLERANCE = 1e-10
SIMILARITY_DETERMINANT_CUTOFF = 1e-4


def run_experiments(output_path: str | Path | None = None) -> dict:
    rng = np.random.default_rng(RNG_SEED)

    n = 12
    projectors = coordinate_projectors(n, [list(range(0, 4)), list(range(4, 8)), list(range(8, 12))])
    t = rng.normal(size=(n, n))
    blocks = transfer_blocks(t, projectors)
    reconstruction_error = float(np.linalg.norm(reconstruct_operator(blocks) - t))

    companion = np.array(companion_matrix([0, 0, 0, 0, 0, 0]), dtype=float)
    seed = np.zeros(6)
    seed[0] = 1
    companion_profile = krylov_rank_profile(companion, seed)

    repeated = np.array(repeated_jordan_operator([3, 3], eigenvalue=2), dtype=float)
    repeated_profile = krylov_rank_profile(repeated, np.array([0, 0, 1, 0, 0, 1], dtype=float))

    path_ranks = {str(k): symmetric_graph_seed_rank(path_adjacency(k)) for k in range(2, 13)}
    cycle_ranks = {str(k): symmetric_graph_seed_rank(cycle_adjacency(k)) for k in range(3, 13)}

    shift = bilateral_shift_matrix(16)
    residue = residue_projectors(16, 4)
    shift_blocks = transfer_blocks(shift, residue)
    shift_pattern = [
        [int(np.linalg.norm(block) > SHIFT_SUPPORT_TOLERANCE) for block in row]
        for row in shift_blocks
    ]

    q = rng.normal(size=(8, 8))
    while abs(np.linalg.det(q)) < SIMILARITY_DETERMINANT_CUTOFF:
        q = rng.normal(size=(8, 8))
    base_projectors = coordinate_projectors(8, [list(range(0, 3)), list(range(3, 5)), list(range(5, 8))])
    moved = transport_projectors(q, base_projectors)
    transport_residuals = projector_residuals(moved)

    elliptic_example = elliptic_reduce((x**2 + y) * (x - y))

    results = {
        "author": "Komorebi P.",
        "manuscript_title": "Projector-Resolved Seed Calculus I",
        "manuscript_release_version": MANUSCRIPT_VERSION,
        "python_companion_version": PYTHON_COMPANION_VERSION,
        "certificate_metadata": {
            "classification": "exact symbolic checks and finite sampled numerical regressions",
            "python": platform.python_version(),
            "numpy": np.__version__,
            "sympy": sp.__version__,
            "floating_dtype": str(np.dtype(float)),
            "rng_seed": RNG_SEED,
            "shift_support_tolerance": SHIFT_SUPPORT_TOLERANCE,
            "similarity_determinant_cutoff": SIMILARITY_DETERMINANT_CUTOFF,
        },
        "projector_residuals": projector_residuals(projectors),
        "operator_reconstruction_error": reconstruction_error,
        "companion_krylov_rank_profile": companion_profile,
        "repeated_jordan_krylov_rank_profile": repeated_profile,
        "single_operator_seed_ranks": {
            "companion": single_operator_seed_rank(companion_matrix([0, 0, 0, 0, 0, 0])),
            "two_equal_jordan_blocks": single_operator_seed_rank(repeated_jordan_operator([3, 3], eigenvalue=2)),
        },
        "semisimple_formula_examples": {
            "M3_with_7_copies": semisimple_seed_rank([3], [7]),
            "M2xM4_multiplicities_5_9": semisimple_seed_rank([2, 4], [5, 9]),
            "commutative_multiplicities_2_5_3": semisimple_seed_rank([1, 1, 1], [2, 5, 3]),
        },
        "path_graph_seed_ranks": path_ranks,
        "cycle_graph_seed_ranks": cycle_ranks,
        "path_endpoint_krylov_determinants": {str(k): str(endpoint_krylov_determinant_path(k)) for k in range(2, 11)},
        "finite_shift_transfer_pattern": shift_pattern,
        "transported_projector_residuals": transport_residuals,
        "full_matrix_algebra_orbit_dimensions": {
            "n4_seed_e1": full_matrix_orbit_dimension(np.array([1, 0, 0, 0], dtype=float)),
            "n4_generic": full_matrix_orbit_dimension(np.array([1, 2, -1, 3], dtype=float)),
        },
        "elliptic_reduction_example": str(elliptic_example),
        "elliptic_packet_matrix_x": str(elliptic_packet_matrix("x")),
        "elliptic_packet_matrix_y": str(elliptic_packet_matrix("y")),
    }
    if output_path is not None:
        path = Path(output_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(
            json.dumps(results, indent=2, sort_keys=True) + "\n", encoding="utf-8"
        )
    return results
