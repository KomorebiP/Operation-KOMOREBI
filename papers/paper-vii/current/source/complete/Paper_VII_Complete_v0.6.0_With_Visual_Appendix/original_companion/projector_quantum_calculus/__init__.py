"""Finite projector-resolved quantum models for Seed Calculus VII.

The package implements exact finite-dimensional identities and numerical
certificates used by the accompanying paper.  It is not a solver for quantum
gravity and does not claim a continuum construction.
"""
from .basic import (
    I2, X, Y, Z, H_GATE, S_GATE, T_GATE, CNOT,
    basis_state, normalize, ketbra, kron_all, embed_one_qubit,
    embed_two_qubit_adjacent, packet_blocks, reconstruct_blocks,
    cyclic_span_rank, reachable_span_rank,
)
from .symmetry import (
    cyclic_projectors, parity_operator, parity_projectors,
    tensor_packet_projectors, coarse_mod_projectors, sector_populations,
    off_block_norm,
)
from .circuits import (
    CircuitGate, circuit_unitary, apply_circuit, packet_path_block,
    packet_path_reconstruction, bell_circuit,
)
from .dynamics import (
    unitary_evolution, leakage_amplitude, leakage_bound,
    feshbach_effective, projected_resolvent, moving_frame_generator,
    canonical_projector_connection, bloch_projector, bloch_curvature,
)
from .channels import (
    apply_channel, kraus_completeness_error, measurement_probabilities,
    packet_dephase, amplitude_damping_kraus,
)
from .geometry import (
    cycle_laplacian, cycle_eigenvalues, torus_eigenvalues,
    heat_trace, spectral_dimension, low_mode_error_bound,
    causal_volume_hamiltonian, euclidean_transfer,
)

__all__ = [name for name in globals() if not name.startswith("_")]
# Descriptive alias retained for the public API.
feshbach_effective_hamiltonian = feshbach_effective

from .codes import (
    bit_flip_codewords, bit_flip_code_projector, bit_flip_errors,
    syndrome_projectors, knill_laflamme_residual, encode_logical_state,
    bit_flip_channel, bit_flip_recovery,
)
