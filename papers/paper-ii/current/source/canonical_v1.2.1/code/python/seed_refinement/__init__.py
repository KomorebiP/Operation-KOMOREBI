"""Exact finite models for Projector-Resolved Seed Calculus II.

The package implements nested packet systems, residue/polyphase projectors,
Chinese-remainder factorization, weighted transfer walks, filtered inverses,
dyadic delayed separation, Smith-weighted correction, and refinement-defect
identities.  The code supplies finite certificates for the accompanying paper.
"""

__version__ = "1.2.1"

from .projectors import (
    residue_masks,
    residue_projectors,
    analyze_residues,
    synthesize_residues,
    refinement_incidence,
    root_of_unity_projectors,
    crt_index,
    dyadic_odd_index,
)
from .weighted import (
    Edge,
    weighted_adjacency,
    path_counts,
    path_zeta,
    neumann_inverse_mod,
    direct_inverse_mod,
)
from .dyadic import (
    valuation,
    resultant_weight,
    delayed_separation_example,
    smith_diagonal_solve,
)
from .stability import (
    power_defect,
    power_defect_expansion,
    resolvent_defect,
    compatible_replication_tower,
)
from .smith_chart import (
    gamma_from_impedance,
    impedance_from_gamma,
    phase_transform,
    polyphase_orbit,
    smith_weight,
)

__all__ = [
    "residue_masks", "residue_projectors", "analyze_residues",
    "synthesize_residues", "refinement_incidence", "root_of_unity_projectors",
    "crt_index", "dyadic_odd_index", "Edge", "weighted_adjacency",
    "path_counts", "path_zeta", "neumann_inverse_mod", "direct_inverse_mod",
    "valuation", "resultant_weight", "delayed_separation_example",
    "smith_diagonal_solve", "power_defect", "power_defect_expansion",
    "resolvent_defect", "compatible_replication_tower", "gamma_from_impedance",
    "impedance_from_gamma", "phase_transform", "polyphase_orbit", "smith_weight",
]
