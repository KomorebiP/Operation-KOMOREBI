"""Finite and symbolic certificates for Projector-Resolved Seed Calculus I.

The package evaluates the finite-dimensional identities used in the
accompanying paper through symbolic computations and floating-point tests: packet analysis/synthesis, transfer blocks, cyclic spans,
semisimple seed-rank formulas, graph examples, quotient transport, and the
elliptic coordinate-ring example.  It is a verification companion, not a
replacement for the proofs in the paper.
"""

__version__ = "1.1.2"

from .core import (
    analysis,
    synthesis,
    projector_residuals,
    transfer_blocks,
    reconstruct_operator,
    cyclic_span,
    cyclic_span_dimension,
    krylov_rank_profile,
    semisimple_seed_rank,
    single_operator_seed_rank,
    transport_projectors,
    intertwining_residual,
    packet_transfer_graph,
    packet_reachability,
    matrix_units,
)
from .algebra import elliptic_reduce, elliptic_product, elliptic_packet_matrix
from .graphs import path_adjacency, cycle_adjacency, symmetric_graph_seed_rank

__all__ = [
    "__version__",
    "analysis",
    "synthesis",
    "projector_residuals",
    "transfer_blocks",
    "reconstruct_operator",
    "cyclic_span",
    "cyclic_span_dimension",
    "krylov_rank_profile",
    "semisimple_seed_rank",
    "single_operator_seed_rank",
    "transport_projectors",
    "intertwining_residual",
    "packet_transfer_graph",
    "packet_reachability",
    "matrix_units",
    "elliptic_reduce",
    "elliptic_product",
    "elliptic_packet_matrix",
    "path_adjacency",
    "cycle_adjacency",
    "symmetric_graph_seed_rank",
]
