"""Packet algorithms and benchmark analysis for Seed Calculus VIII.

The package implements exact finite packet operators, complexity models,
structured solvers, mixed-precision error certificates, and reproducible
analysis of the supplied CPU/GPU benchmark corpus.
"""

from .operators import (
    BlockDiagonal,
    BDLRMatrix,
    BlockSparseMatrix,
    materialize_blocks,
    packet_blocks,
)
from .complexity import (
    dense_apply_flops,
    block_apply_flops,
    bdlr_apply_flops,
    dense_storage,
    block_storage,
    bdlr_storage,
    ideal_bdlr_speedup,
    amortized_break_even,
    graph_break_even,
)
from .mixed_precision import (
    packet_error_bound,
    optimal_precision_tolerances,
    quantize_by_packet,
)
from .krylov import (
    preconditioned_condition_bound,
    conjugate_gradient,
    lanczos_tridiagonal,
)

__all__ = [
    "BlockDiagonal",
    "BDLRMatrix",
    "BlockSparseMatrix",
    "materialize_blocks",
    "packet_blocks",
    "dense_apply_flops",
    "block_apply_flops",
    "bdlr_apply_flops",
    "dense_storage",
    "block_storage",
    "bdlr_storage",
    "ideal_bdlr_speedup",
    "amortized_break_even",
    "graph_break_even",
    "packet_error_bound",
    "optimal_precision_tolerances",
    "quantize_by_packet",
    "preconditioned_condition_bound",
    "conjugate_gradient",
    "lanczos_tridiagonal",
]
