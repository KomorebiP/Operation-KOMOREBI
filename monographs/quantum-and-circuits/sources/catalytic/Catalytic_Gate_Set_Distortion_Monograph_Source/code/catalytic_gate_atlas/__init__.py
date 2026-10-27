"""Catalytic gate-set distortion atlas.

This package supports the symbolic and finite-search experiments accompanying
*Catalytic Gate-Set Distortion*.  It is deliberately small, exact, and suitable
for audit rather than optimized for large-scale synthesis.
"""
from .linear import (
    RowGate,
    canonical_ambient_word,
    canonical_restricted_word,
    canonical_six_target,
    snapshot_target,
    verify_canonical_atom,
)
from .clifford import exact_census as exact_clifford_census
from .reversible import exact_affine_toffoli_census
from .qasm import gate_word_to_openqasm

__all__ = [
    "RowGate",
    "canonical_ambient_word",
    "canonical_restricted_word",
    "canonical_six_target",
    "snapshot_target",
    "verify_canonical_atom",
    "exact_clifford_census",
    "exact_affine_toffoli_census",
    "gate_word_to_openqasm",
]
