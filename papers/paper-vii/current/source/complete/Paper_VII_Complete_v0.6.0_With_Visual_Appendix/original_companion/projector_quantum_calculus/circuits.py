from __future__ import annotations

from dataclasses import dataclass
from itertools import product
from typing import Sequence

import numpy as np

from .basic import CNOT, H_GATE, basis_state, embed_one_qubit, embed_two_qubit_adjacent

Array = np.ndarray


@dataclass(frozen=True)
class CircuitGate:
    name: str
    matrix: Array


def circuit_unitary(gates: Sequence[Array]) -> Array:
    if not gates:
        raise ValueError("at least one gate is required")
    dim = np.asarray(gates[0]).shape[0]
    out = np.eye(dim, dtype=complex)
    for gate in gates:
        g = np.asarray(gate, dtype=complex)
        if g.shape != (dim, dim):
            raise ValueError("all gates must have the same embedded dimension")
        out = g @ out
    return out


def apply_circuit(seed: Array, gates: Sequence[Array]) -> Array:
    return circuit_unitary(gates) @ np.asarray(seed, dtype=complex)


def packet_path_block(gates: Sequence[Array], projectors: Sequence[Array], source: int, target: int) -> Array:
    """Sum all exact packet paths from source to target through a circuit."""
    if not gates:
        return projectors[target] @ projectors[source]
    m = len(gates)
    if m == 1:
        return projectors[target] @ gates[0] @ projectors[source]
    out = np.zeros_like(gates[0], dtype=complex)
    for middle in product(range(len(projectors)), repeat=m - 1):
        addresses = (source,) + middle + (target,)
        term = projectors[addresses[-1]] @ gates[-1]
        for layer in range(m - 2, -1, -1):
            term = term @ projectors[addresses[layer + 1]] @ gates[layer]
        term = term @ projectors[source]
        out += term
    return out


def packet_path_reconstruction(gates: Sequence[Array], projectors: Sequence[Array]) -> Array:
    out = np.zeros_like(gates[0], dtype=complex)
    for source in range(len(projectors)):
        for target in range(len(projectors)):
            out += packet_path_block(gates, projectors, source, target)
    return out


def bell_circuit() -> tuple[Array, list[Array], Array]:
    seed = basis_state(2, 0)
    h0 = embed_one_qubit(H_GATE, 0, 2)
    cnot = embed_two_qubit_adjacent(CNOT, 0, 2)
    gates = [h0, cnot]
    state = apply_circuit(seed, gates)
    return seed, gates, state
