from __future__ import annotations

from collections import deque
from collections.abc import Sequence
from operator import index as integer_index
from typing import Iterable

import numpy as np
import sympy as sp

Array = np.ndarray


def _as_square(matrix: Array) -> Array:
    a = np.asarray(matrix, dtype=complex)
    if a.ndim != 2 or a.shape[0] != a.shape[1]:
        raise ValueError("matrix must be square")
    return a


def analysis(projectors: Sequence[Array], vector: Sequence[complex]) -> list[Array]:
    """Numerically evaluate finite packet analysis in ambient coordinates."""
    if not projectors:
        raise ValueError("at least one projector is required")
    v = np.asarray(vector, dtype=complex).reshape(-1)
    n = v.size
    packets = []
    for p in projectors:
        q = _as_square(p)
        if q.shape != (n, n):
            raise ValueError("projector and vector dimensions do not agree")
        packets.append(q @ v)
    return packets


def synthesis(packets: Sequence[Sequence[complex]]) -> Array:
    """Sum packet coordinates in the ambient space."""
    if not packets:
        raise ValueError("at least one packet is required")
    arrays = [np.asarray(x, dtype=complex).reshape(-1) for x in packets]
    if any(x.shape != arrays[0].shape for x in arrays):
        raise ValueError("packet dimensions do not agree")
    return np.sum(np.stack(arrays), axis=0)


def projector_residuals(projectors: Sequence[Array]) -> dict[str, float]:
    """Numerical certificate for idempotence, annihilation, and completeness."""
    if not projectors:
        raise ValueError("at least one projector is required")
    ps = [_as_square(p) for p in projectors]
    n = ps[0].shape[0]
    if any(p.shape != (n, n) for p in ps):
        raise ValueError("projectors must have one common size")
    idem = max(float(np.linalg.norm(p @ p - p)) for p in ps)
    annih = 0.0
    for i, p in enumerate(ps):
        for j, q in enumerate(ps):
            if i != j:
                annih = max(annih, float(np.linalg.norm(p @ q)))
    complete = float(np.linalg.norm(sum(ps, np.zeros((n, n), dtype=complex)) - np.eye(n)))
    return {"idempotence": idem, "annihilation": annih, "completeness": complete}


def transfer_blocks(operator: Array, projectors: Sequence[Array]) -> list[list[Array]]:
    """Return blocks P_beta T P_alpha with rows indexed by beta."""
    t = _as_square(operator)
    ps = [_as_square(p) for p in projectors]
    if any(p.shape != t.shape for p in ps):
        raise ValueError("operator and projectors must have one size")
    return [[p_beta @ t @ p_alpha for p_alpha in ps] for p_beta in ps]


def reconstruct_operator(blocks: Sequence[Sequence[Array]]) -> Array:
    if not blocks or not blocks[0]:
        raise ValueError("a nonempty block matrix is required")
    shape = np.asarray(blocks[0][0]).shape
    out = np.zeros(shape, dtype=complex)
    for row in blocks:
        for block in row:
            b = np.asarray(block, dtype=complex)
            if b.shape != shape:
                raise ValueError("all embedded blocks must have one ambient shape")
            out += b
    return out


def cyclic_span(
    operators: Sequence[Array],
    seeds: Sequence[Sequence[complex]],
    *,
    tolerance: float = 1e-10,
    max_rounds: int | None = None,
) -> Array:
    """Compute a numerical basis for the finite-dimensional operator hull.

    The operators are repeatedly applied to newly discovered directions.  The
    returned columns form a numerically independent orbit family. If a supplied
    max_rounds limit stops the search early, the returned span can be proper.
    Numerical tolerance decisions are not exact mathematical certificates.
    """
    if not seeds:
        raise ValueError("at least one seed is required")
    ops = [_as_square(op) for op in operators]
    first = np.asarray(seeds[0], dtype=complex).reshape(-1)
    n = first.size
    if any(op.shape != (n, n) for op in ops):
        raise ValueError("operators and seeds must have one dimension")
    seed_vectors = [np.asarray(v, dtype=complex).reshape(-1) for v in seeds]
    if any(v.size != n for v in seed_vectors):
        raise ValueError("operators and seeds must have one dimension")

    basis: list[Array] = []

    def add(candidate: Array) -> bool:
        if np.linalg.norm(candidate) <= tolerance:
            return False
        old = np.column_stack(basis) if basis else np.zeros((n, 0), dtype=complex)
        old_rank = np.linalg.matrix_rank(old, tol=tolerance)
        trial = np.column_stack([*basis, candidate])
        new_rank = np.linalg.matrix_rank(trial, tol=tolerance)
        if new_rank > old_rank:
            basis.append(candidate)
            return True
        return False

    frontier: list[Array] = []
    for seed in seed_vectors:
        if add(seed):
            frontier.append(seed)
    rounds = 0
    limit = max_rounds if max_rounds is not None else n * max(1, len(ops)) + 2
    while frontier and len(basis) < n and rounds < limit:
        next_frontier: list[Array] = []
        for vector in frontier:
            for op in ops:
                candidate = op @ vector
                if add(candidate):
                    next_frontier.append(candidate)
        frontier = next_frontier
        rounds += 1
    return np.column_stack(basis) if basis else np.zeros((n, 0), dtype=complex)


def cyclic_span_dimension(
    operators: Sequence[Array],
    seeds: Sequence[Sequence[complex]],
    *,
    tolerance: float = 1e-10,
) -> int:
    return int(cyclic_span(operators, seeds, tolerance=tolerance).shape[1])


def krylov_rank_profile(operator: Array, seed: Sequence[complex], *, tolerance: float = 1e-10) -> list[int]:
    t = _as_square(operator)
    v = np.asarray(seed, dtype=complex).reshape(-1)
    if v.size != t.shape[0]:
        raise ValueError("operator and seed dimensions do not agree")
    columns: list[Array] = []
    profile: list[int] = []
    current = v
    for _ in range(t.shape[0]):
        columns.append(current)
        profile.append(int(np.linalg.matrix_rank(np.column_stack(columns), tol=tolerance)))
        current = t @ current
    return profile


def semisimple_seed_rank(block_dimensions: Sequence[int], multiplicities: Sequence[int]) -> int:
    """Return the exact generator count for a supplied split matrix module.

    For the coordinatewise product action of M_{d_i}(k) on the modules
    (k^{d_i})^{m_i}, this is max_i ceil(m_i / d_i). The field need not be
    algebraically closed once this split presentation is supplied. This
    integer calculation does not construct a semisimple decomposition.
    """
    def natural(value: int, label: str) -> int:
        if isinstance(value, (bool, np.bool_)):
            raise ValueError(f"{label} must be an integer, not a boolean")
        try:
            return integer_index(value)
        except TypeError as exc:
            raise ValueError(f"{label} must be an exact integer") from exc

    ds = [natural(d, "block dimension") for d in block_dimensions]
    ms = [natural(m, "multiplicity") for m in multiplicities]
    if not ds or len(ds) != len(ms) or any(d <= 0 for d in ds) or any(m < 0 for m in ms):
        raise ValueError("positive block dimensions and nonnegative matching multiplicities are required")
    # Never divide through float: counts beyond 2**53 must remain exact.
    return max((m + d - 1) // d for d, m in zip(ds, ms, strict=True))



def _nullity(matrix: sp.Matrix) -> int:
    return matrix.cols - matrix.rank()


def single_operator_seed_rank(operator: Sequence[Sequence[complex]]) -> int:
    """Exact seed rank of a finite-dimensional module generated by one operator.

    Over an algebraically closed field this is the maximum geometric
    multiplicity among eigenvalues, equivalently the maximum number of Jordan
    blocks in one primary component.  Input entries should be exact SymPy data
    when exact certification is desired.
    """
    t = sp.Matrix(operator)
    if t.rows != t.cols:
        raise ValueError("operator must be square")
    eigenvalues = list(t.eigenvals().keys())
    return max((_nullity(t - lam * sp.eye(t.rows)) for lam in eigenvalues), default=0)


def transport_projectors(intertwiner: Array, projectors: Sequence[Array]) -> list[Array]:
    u = _as_square(intertwiner)
    inv = np.linalg.inv(u)
    return [u @ _as_square(p) @ inv for p in projectors]


def intertwining_residual(phi: Array, source_operator: Array, target_operator: Array) -> float:
    p = np.asarray(phi, dtype=complex)
    a = _as_square(source_operator)
    b = _as_square(target_operator)
    if p.shape != (b.shape[0], a.shape[0]):
        raise ValueError("intertwiner has incompatible shape")
    return float(np.linalg.norm(p @ a - b @ p))


def packet_transfer_graph(operators: Sequence[Array], projectors: Sequence[Array], *, tolerance: float = 1e-10) -> Array:
    """Adjacency matrix: alpha -> beta if some P_beta O P_alpha is nonzero."""
    ps = [_as_square(p) for p in projectors]
    adjacency = np.zeros((len(ps), len(ps)), dtype=int)
    for alpha, p_alpha in enumerate(ps):
        for beta, p_beta in enumerate(ps):
            if any(np.linalg.norm(p_beta @ _as_square(op) @ p_alpha) > tolerance for op in operators):
                adjacency[alpha, beta] = 1
    return adjacency


def packet_reachability(adjacency: Array, starts: Iterable[int]) -> set[int]:
    graph = np.asarray(adjacency, dtype=int)
    if graph.ndim != 2 or graph.shape[0] != graph.shape[1]:
        raise ValueError("adjacency matrix must be square")
    seen = set(int(s) for s in starts)
    queue = deque(seen)
    while queue:
        i = queue.popleft()
        for j in np.flatnonzero(graph[i]):
            jj = int(j)
            if jj not in seen:
                seen.add(jj)
                queue.append(jj)
    return seen


def matrix_units(n: int) -> list[Array]:
    if n < 1:
        raise ValueError("n must be positive")
    units: list[Array] = []
    for i in range(n):
        for j in range(n):
            e = np.zeros((n, n), dtype=complex)
            e[i, j] = 1.0
            units.append(e)
    return units
