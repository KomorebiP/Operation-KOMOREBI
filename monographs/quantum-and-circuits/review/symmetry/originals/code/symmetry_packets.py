from __future__ import annotations

from dataclasses import dataclass
from itertools import combinations
from math import comb, lgamma, log
from typing import Iterable, Sequence

import numpy as np


def hamming_weight(x: int) -> int:
    return int(x).bit_count()


def weight_basis(n: int, k: int) -> list[int]:
    """Computational-basis indices of n qubits having Hamming weight k."""
    if n < 0 or k < 0 or k > n:
        return []
    out: list[int] = []
    for positions in combinations(range(n), k):
        x = 0
        for q in positions:
            x |= 1 << q
        out.append(x)
    return out


def residue_basis(n: int, modulus: int, residue: int) -> list[int]:
    """Basis indices whose Hamming weight is congruent to residue mod modulus."""
    if modulus <= 0:
        raise ValueError("modulus must be positive")
    residue %= modulus
    return [x for x in range(1 << n) if hamming_weight(x) % modulus == residue]


def symmetric_subspace_dimension(n: int, local_dimension: int = 2) -> int:
    """Dimension of Sym^n(C^d)."""
    if n < 0 or local_dimension <= 0:
        raise ValueError("invalid dimensions")
    return comb(n + local_dimension - 1, local_dimension - 1)


def boson_fixed_number_dimension(modes: int, particles: int) -> int:
    """Number of weak compositions of particles into modes."""
    if modes <= 0 or particles < 0:
        raise ValueError("invalid modes or particles")
    return comb(modes + particles - 1, particles)


def fermion_fixed_number_dimension(modes: int, particles: int) -> int:
    """Dimension of a fixed-particle fermionic sector."""
    if modes < 0 or particles < 0 or particles > modes:
        return 0
    return comb(modes, particles)


def rz(theta: float) -> np.ndarray:
    return np.array(
        [[np.exp(-0.5j * theta), 0.0], [0.0, np.exp(0.5j * theta)]],
        dtype=np.complex128,
    )


def xy_exchange(theta: float, phase: float = 0.0) -> np.ndarray:
    """Number-preserving exchange on |01>, |10>."""
    c = np.cos(theta)
    s = np.sin(theta)
    em = np.exp(-1j * phase)
    ep = np.exp(1j * phase)
    return np.array(
        [
            [1.0, 0.0, 0.0, 0.0],
            [0.0, c, -1j * em * s, 0.0],
            [0.0, -1j * ep * s, c, 0.0],
            [0.0, 0.0, 0.0, 1.0],
        ],
        dtype=np.complex128,
    )


def _replace_bits(index: int, qubits: Sequence[int], local_state: int) -> int:
    out = index
    for pos, q in enumerate(qubits):
        bit = (local_state >> pos) & 1
        if bit:
            out |= 1 << q
        else:
            out &= ~(1 << q)
    return out


def _extract_bits(index: int, qubits: Sequence[int]) -> int:
    out = 0
    for pos, q in enumerate(qubits):
        out |= ((index >> q) & 1) << pos
    return out


def apply_local_gate_full(
    state: np.ndarray,
    gate: np.ndarray,
    qubits: Sequence[int],
    n: int,
) -> np.ndarray:
    """Apply a 1- or 2-qubit gate to a full state vector."""
    qubits = tuple(qubits)
    size = 1 << len(qubits)
    if gate.shape != (size, size):
        raise ValueError("gate dimension does not match qubits")
    if state.shape != (1 << n,):
        raise ValueError("state has the wrong dimension")
    out = np.zeros_like(state)
    for x, amp in enumerate(state):
        if amp == 0:
            continue
        local_in = _extract_bits(x, qubits)
        for local_out in range(size):
            coefficient = gate[local_out, local_in]
            if coefficient != 0:
                y = _replace_bits(x, qubits, local_out)
                out[y] += coefficient * amp
    return out


@dataclass(frozen=True)
class PacketPlan:
    n: int
    basis: tuple[int, ...]

    @classmethod
    def fixed_weight(cls, n: int, k: int) -> "PacketPlan":
        return cls(n=n, basis=tuple(weight_basis(n, k)))

    @property
    def dimension(self) -> int:
        return len(self.basis)

    @property
    def index_map(self) -> dict[int, int]:
        return {x: i for i, x in enumerate(self.basis)}

    def embed(self, packet_state: np.ndarray) -> np.ndarray:
        if packet_state.shape != (self.dimension,):
            raise ValueError("packet state has the wrong dimension")
        full = np.zeros(1 << self.n, dtype=np.complex128)
        full[list(self.basis)] = packet_state
        return full

    def restrict(self, full_state: np.ndarray) -> np.ndarray:
        if full_state.shape != (1 << self.n,):
            raise ValueError("full state has the wrong dimension")
        return full_state[list(self.basis)].copy()

    def restrict_gate(self, gate: np.ndarray, qubits: Sequence[int]) -> np.ndarray:
        """Compile a full local gate into the packet basis.

        Raises ValueError if the gate leaks from the packet.
        """
        qubits = tuple(qubits)
        size = 1 << len(qubits)
        if gate.shape != (size, size):
            raise ValueError("gate dimension does not match qubits")
        idx = self.index_map
        out = np.zeros((self.dimension, self.dimension), dtype=np.complex128)
        leakage = 0.0
        for column, x in enumerate(self.basis):
            local_in = _extract_bits(x, qubits)
            for local_out in range(size):
                coefficient = gate[local_out, local_in]
                if coefficient == 0:
                    continue
                y = _replace_bits(x, qubits, local_out)
                if y in idx:
                    out[idx[y], column] += coefficient
                else:
                    leakage += float(abs(coefficient) ** 2)
        if leakage > 1e-12:
            raise ValueError(f"gate leaks from packet: total column leakage {leakage:.3e}")
        return out


def random_packet_state(plan: PacketPlan, seed: int = 0) -> np.ndarray:
    rng = np.random.default_rng(seed)
    v = rng.normal(size=plan.dimension) + 1j * rng.normal(size=plan.dimension)
    v = v.astype(np.complex128)
    return v / np.linalg.norm(v)


def simulate_fixed_weight_demo(n: int, k: int, seed: int = 0) -> float:
    """Return full-vs-packet reconstruction error for a short exact circuit."""
    plan = PacketPlan.fixed_weight(n, k)
    packet = random_packet_state(plan, seed=seed)
    full = plan.embed(packet)
    operations: list[tuple[np.ndarray, tuple[int, ...]]] = []
    for q in range(n):
        operations.append((rz(0.07 * (q + 1)), (q,)))
    for q in range(n - 1):
        operations.append((xy_exchange(0.13 + 0.01 * q, phase=0.03 * q), (q, q + 1)))
    packet_evolved = packet
    full_evolved = full
    for gate, qubits in operations:
        full_evolved = apply_local_gate_full(full_evolved, gate, qubits, n)
        packet_evolved = plan.restrict_gate(gate, qubits) @ packet_evolved
    return float(np.linalg.norm(full_evolved - plan.embed(packet_evolved)))


def hypercube_quotient(n: int) -> np.ndarray:
    """Adjacency of the n-dimensional hypercube in the normalized weight-orbit basis."""
    out = np.zeros((n + 1, n + 1), dtype=float)
    for k in range(n):
        value = np.sqrt((k + 1) * (n - k))
        out[k, k + 1] = value
        out[k + 1, k] = value
    return out


def circuit_leakage_bound(local_leakages: Iterable[float]) -> float:
    """Telescoping upper bound for state-vector error."""
    return float(sum(max(0.0, x) for x in local_leakages))


def hamiltonian_leakage_bound(time: float, commutator_norm: float) -> float:
    return abs(float(time)) * max(0.0, float(commutator_norm))


def log2_binomial(n: int, k: int) -> float:
    """Stable base-2 logarithm of a binomial coefficient."""
    if n < 0 or k < 0 or k > n:
        return float("-inf")
    k = min(k, n - k)
    return float((lgamma(n + 1) - lgamma(k + 1) - lgamma(n - k + 1)) / log(2.0))


def qubit_commutant_parameter_count(n: int) -> int:
    """Sum of squared total-spin carrier dimensions for n qubits."""
    if n < 0:
        raise ValueError("n must be nonnegative")
    return sum((n - 2 * r + 1) ** 2 for r in range(n // 2 + 1))


def _random_unitary(dimension: int, rng: np.random.Generator) -> np.ndarray:
    z = rng.normal(size=(dimension, dimension)) + 1j * rng.normal(size=(dimension, dimension))
    q, r = np.linalg.qr(z)
    phases = np.diag(r)
    phases = np.where(np.abs(phases) > 0, phases / np.abs(phases), 1.0)
    return q @ np.diag(np.conjugate(phases))


def moving_frame_demo(seed: int = 7) -> float:
    """Validate an exact rank-two moving-packet schedule in dimension four."""
    rng = np.random.default_rng(seed)
    frames = [_random_unitary(4, rng) for _ in range(3)]
    block_gates: list[np.ndarray] = []
    for _ in range(2):
        active = _random_unitary(2, rng)
        inactive = _random_unitary(2, rng)
        block = np.zeros((4, 4), dtype=np.complex128)
        block[:2, :2] = active
        block[2:, 2:] = inactive
        block_gates.append(block)

    full_gates = [
        frames[t + 1] @ block_gates[t] @ frames[t].conj().T
        for t in range(2)
    ]
    z0 = rng.normal(size=2) + 1j * rng.normal(size=2)
    z0 = z0.astype(np.complex128)
    z0 /= np.linalg.norm(z0)

    full = frames[0][:, :2] @ z0
    for gate in full_gates:
        full = gate @ full

    reduced = z0
    for t, gate in enumerate(full_gates):
        update = frames[t + 1][:, :2].conj().T @ gate @ frames[t][:, :2]
        reduced = update @ reduced
    embedded = frames[2][:, :2] @ reduced
    return float(np.linalg.norm(full - embedded))
