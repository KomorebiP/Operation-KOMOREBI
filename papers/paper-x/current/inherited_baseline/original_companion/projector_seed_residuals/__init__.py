"""Exact finite models for residual seed forests and system completion.

The package supplies finite arithmetic and linear-algebra certificates used by
*Projector-Resolved Seed Calculus X*.  It does not implement general Galois
deformation rings or prove automorphic occupancy.
"""

from .residual import (
    partition_by_residual,
    compatible_residue_tower,
    reconstruct_digits,
    first_separation_depth,
    full_digit_levels,
)
from .zeta import (
    smooth_count,
    weighted_count,
    weighted_zeta_expression,
    singular_power_count,
    singular_square_zeta_expression,
    exact_singular_dimension,
)
from .transport import (
    DirectedGraph,
    strongly_connected_components,
    source_components,
    minimum_seed_representatives,
    transport_closure,
)
from .cohomology import (
    rank_mod_p,
    cohomology_dimensions,
    packet_cohomology_dimensions,
)
from .companion import (
    roots_mod_prime_power,
    build_root_forest,
    enumerate_branches,
)
from .system import (
    spine_is_compatible,
    select_frobenius_separators,
    recover_multiplicities,
)
from .occupancy import (
    lagrange_projector,
    joint_projector,
    projector_trace_rank,
)

__all__ = [
    "partition_by_residual",
    "compatible_residue_tower",
    "reconstruct_digits",
    "first_separation_depth",
    "full_digit_levels",
    "smooth_count",
    "weighted_count",
    "weighted_zeta_expression",
    "singular_power_count",
    "singular_square_zeta_expression",
    "exact_singular_dimension",
    "DirectedGraph",
    "strongly_connected_components",
    "source_components",
    "minimum_seed_representatives",
    "transport_closure",
    "rank_mod_p",
    "cohomology_dimensions",
    "packet_cohomology_dimensions",
    "roots_mod_prime_power",
    "build_root_forest",
    "enumerate_branches",
    "spine_is_compatible",
    "select_frobenius_separators",
    "recover_multiplicities",
    "lagrange_projector",
    "joint_projector",
    "projector_trace_rank",
]
