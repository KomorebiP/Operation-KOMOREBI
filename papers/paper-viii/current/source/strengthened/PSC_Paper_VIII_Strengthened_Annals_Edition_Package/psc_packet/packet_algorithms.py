from __future__ import annotations

from dataclasses import dataclass
from math import floor
from typing import Dict, Iterable, Mapping, Sequence, Tuple

import numpy as np

Array = np.ndarray


@dataclass(frozen=True)
class PacketLayout:
    sizes: tuple[int, ...]

    def __post_init__(self) -> None:
        if not self.sizes or any(int(s) <= 0 for s in self.sizes):
            raise ValueError("packet sizes must be positive")
        object.__setattr__(self, "sizes", tuple(int(s) for s in self.sizes))
        starts = np.cumsum((0,) + self.sizes)
        object.__setattr__(self, "slices", tuple(slice(int(starts[i]), int(starts[i + 1])) for i in range(len(self.sizes))))
        object.__setattr__(self, "n", int(starts[-1]))


@dataclass(frozen=True)
class PacketIR:
    layout: PacketLayout
    blocks: Mapping[tuple[int, int], Array]

    def __post_init__(self) -> None:
        checked: dict[tuple[int, int], Array] = {}
        q = len(self.layout.sizes)
        for (beta, alpha), block in self.blocks.items():
            if not (0 <= alpha < q and 0 <= beta < q):
                raise ValueError("block address is outside the packet layout")
            arr = np.asarray(block)
            expected = (self.layout.sizes[beta], self.layout.sizes[alpha])
            if arr.shape != expected:
                raise ValueError(f"block {(beta, alpha)} has shape {arr.shape}, expected {expected}")
            checked[(beta, alpha)] = arr.copy()
        object.__setattr__(self, "blocks", checked)

    def materialize(self) -> Array:
        dtype = np.result_type(*[b.dtype for b in self.blocks.values()]) if self.blocks else float
        out = np.zeros((self.layout.n, self.layout.n), dtype=dtype)
        for (beta, alpha), block in self.blocks.items():
            out[self.layout.slices[beta], self.layout.slices[alpha]] += block
        return out

    def apply(self, x: Array) -> Array:
        x = np.asarray(x)
        vector = x.ndim == 1
        if vector:
            x = x[:, None]
        if x.ndim != 2 or x.shape[0] != self.layout.n:
            raise ValueError("right hand side has incompatible shape")
        dtype = np.result_type(x.dtype, *[b.dtype for b in self.blocks.values()]) if self.blocks else x.dtype
        out = np.zeros((self.layout.n, x.shape[1]), dtype=dtype)
        for (beta, alpha), block in self.blocks.items():
            out[self.layout.slices[beta]] += block @ x[self.layout.slices[alpha]]
        return out[:, 0] if vector else out

    def adjoint(self) -> "PacketIR":
        return PacketIR(self.layout, {(alpha, beta): block.conj().T for (beta, alpha), block in self.blocks.items()})

    def compose(self, other: "PacketIR", *, atol: float = 0.0) -> "PacketIR":
        if self.layout != other.layout:
            raise ValueError("packet layouts must agree")
        q = len(self.layout.sizes)
        result: dict[tuple[int, int], Array] = {}
        for gamma in range(q):
            for alpha in range(q):
                acc = None
                for beta in range(q):
                    left = self.blocks.get((gamma, beta))
                    right = other.blocks.get((beta, alpha))
                    if left is None or right is None:
                        continue
                    term = left @ right
                    acc = term if acc is None else acc + term
                if acc is not None and (atol == 0.0 or np.linalg.norm(acc) > atol):
                    result[(gamma, alpha)] = acc
        return PacketIR(self.layout, result)

    @property
    def support(self) -> frozenset[tuple[int, int]]:
        return frozenset(self.blocks)

    @property
    def stored_entries(self) -> int:
        return int(sum(block.size for block in self.blocks.values()))


@dataclass(frozen=True)
class RecompressionResult:
    left: Array
    right: Array
    spectral_error: float
    frobenius_error: float
    singular_values: Array

    def materialize(self) -> Array:
        return self.left @ self.right.conj().T


def recompress_factors(left: Array, right: Array, rank: int) -> RecompressionResult:
    left = np.asarray(left)
    right = np.asarray(right)
    if left.ndim != 2 or right.ndim != 2 or left.shape[1] != right.shape[1]:
        raise ValueError("factor shapes are incompatible")
    if not 0 <= rank <= left.shape[1]:
        raise ValueError("rank is outside the factor range")
    ql, rl = np.linalg.qr(left, mode="reduced")
    qr, rr = np.linalg.qr(right, mode="reduced")
    core = rl @ rr.conj().T
    u, s, vh = np.linalg.svd(core, full_matrices=False)
    k = min(rank, s.size)
    root = np.sqrt(s[:k])
    left_k = (ql @ u[:, :k]) * root[None, :]
    right_k = (qr @ vh.conj().T[:, :k]) * root[None, :]
    spectral_error = float(s[k]) if k < s.size else 0.0
    frobenius_error = float(np.linalg.norm(s[k:]))
    return RecompressionResult(left_k, right_k, spectral_error, frobenius_error, s)


def product_chain_error_bound(
    exact_factors: Sequence[Array],
    approximate_factors: Sequence[Array],
) -> float:
    if len(exact_factors) != len(approximate_factors) or not exact_factors:
        raise ValueError("factor lists must have the same positive length")
    total = 0.0
    m = len(exact_factors)
    exact_norms = [float(np.linalg.norm(a, 2)) for a in exact_factors]
    approx_norms = [float(np.linalg.norm(a, 2)) for a in approximate_factors]
    errors = [float(np.linalg.norm(ah - a, 2)) for a, ah in zip(exact_factors, approximate_factors, strict=True)]
    for j in range(m):
        left = np.prod(approx_norms[j + 1 :], dtype=float) if j + 1 < m else 1.0
        right = np.prod(exact_norms[:j], dtype=float) if j > 0 else 1.0
        total += left * errors[j] * right
    return float(total)


def dense_apply_flops(n: int, rhs: int) -> int:
    if n <= 0 or rhs <= 0:
        raise ValueError("dimensions must be positive")
    return 2 * n * n * rhs


def packet_apply_flops(layout: PacketLayout, support: Iterable[tuple[int, int]], rhs: int) -> int:
    if rhs <= 0:
        raise ValueError("rhs must be positive")
    return int(2 * rhs * sum(layout.sizes[b] * layout.sizes[a] for b, a in support))


def packet_streaming_bytes(
    layout: PacketLayout,
    support: Iterable[tuple[int, int]],
    rhs: int,
    itemsize: int,
) -> int:
    """Declared one pass model.

    Every active matrix block is read once. Every source packet is read once for
    each outgoing active edge. Every target packet is read and written once for
    each incoming active edge. This deliberately does not assume cache reuse.
    """
    if rhs <= 0 or itemsize <= 0:
        raise ValueError("rhs and itemsize must be positive")
    total = 0
    for beta, alpha in support:
        total += layout.sizes[beta] * layout.sizes[alpha]
        total += layout.sizes[alpha] * rhs
        total += 2 * layout.sizes[beta] * rhs
    return int(total * itemsize)


def roofline_time_lower_bound(flops: float, bytes_moved: float, peak_flops_per_second: float, bandwidth_bytes_per_second: float) -> float:
    if min(flops, bytes_moved, peak_flops_per_second, bandwidth_bytes_per_second) < 0:
        raise ValueError("model quantities cannot be negative")
    if peak_flops_per_second == 0 or bandwidth_bytes_per_second == 0:
        raise ValueError("device rates must be positive")
    return max(flops / peak_flops_per_second, bytes_moved / bandwidth_bytes_per_second)


def amortization_threshold(setup: float, baseline: float, candidate: float) -> int | None:
    if min(setup, baseline, candidate) < 0:
        raise ValueError("times cannot be negative")
    gain = baseline - candidate
    if gain <= 0:
        return None
    return max(1, floor(setup / gain) + 1)


def support_product(left: Iterable[tuple[int, int]], right: Iterable[tuple[int, int]]) -> frozenset[tuple[int, int]]:
    left_set = set(left)
    right_set = set(right)
    return frozenset((gamma, alpha) for gamma, beta in left_set for beta2, alpha in right_set if beta == beta2)


def support_power(support: Iterable[tuple[int, int]], power: int) -> frozenset[tuple[int, int]]:
    if power < 1:
        raise ValueError("power must be positive")
    result = frozenset(support)
    base = frozenset(support)
    for _ in range(1, power):
        result = support_product(base, result)
    return result


def topological_levels(vertex_count: int, edges: Iterable[tuple[int, int]]) -> tuple[tuple[int, ...], ...]:
    """Return source to target levels for a directed acyclic graph.

    Edges use the convention source to target.
    """
    adjacency = {v: [] for v in range(vertex_count)}
    indegree = [0] * vertex_count
    for source, target in edges:
        adjacency[source].append(target)
        indegree[target] += 1
    current = sorted(v for v in range(vertex_count) if indegree[v] == 0)
    levels: list[tuple[int, ...]] = []
    seen = 0
    while current:
        levels.append(tuple(current))
        nxt: list[int] = []
        for source in current:
            seen += 1
            for target in adjacency[source]:
                indegree[target] -= 1
                if indegree[target] == 0:
                    nxt.append(target)
        current = sorted(nxt)
    if seen != vertex_count:
        raise ValueError("graph contains a directed cycle")
    return tuple(levels)


def schur_fill_support(
    retained: Sequence[int],
    hidden: Sequence[int],
    support: Iterable[tuple[int, int]],
) -> frozenset[tuple[int, int]]:
    """Support inclusion for one Schur complement.

    A retained block beta, alpha may become active through a path
    alpha to hidden to beta. Hidden internal connectivity is replaced by its
    transitive closure.
    """
    support = set(support)
    hidden_set = set(hidden)
    closure = set(support)
    changed = True
    while changed:
        changed = False
        new = {(c, a) for c, b in closure for b2, a in closure if b == b2 and b in hidden_set}
        for edge in new:
            if edge not in closure:
                closure.add(edge)
                changed = True
    result = {(b, a) for b, a in closure if b in retained and a in retained}
    result |= {(b, a) for b, a in support if b in retained and a in retained}
    return frozenset(result)


@dataclass(frozen=True)
class TreeNode:
    name: str
    keep_cost: float
    keep_error: float
    split_cost: float = 0.0
    children: tuple["TreeNode", ...] = ()


@dataclass(frozen=True)
class TreePlan:
    objective: float
    cost: float
    error: float
    leaves: tuple[str, ...]


def compile_tree_lagrangian(root: TreeNode, penalty: float) -> TreePlan:
    if penalty < 0:
        raise ValueError("penalty must be nonnegative")

    def solve(node: TreeNode) -> TreePlan:
        keep = TreePlan(
            objective=node.keep_cost + penalty * node.keep_error,
            cost=node.keep_cost,
            error=node.keep_error,
            leaves=(node.name,),
        )
        if not node.children:
            return keep
        child_plans = tuple(solve(child) for child in node.children)
        split = TreePlan(
            objective=node.split_cost + sum(p.objective for p in child_plans),
            cost=node.split_cost + sum(p.cost for p in child_plans),
            error=sum(p.error for p in child_plans),
            leaves=tuple(name for p in child_plans for name in p.leaves),
        )
        return keep if keep.objective <= split.objective else split

    return solve(root)


def compile_tree_budget(root: TreeNode, budget: int, scale: float = 1.0) -> TreePlan | None:
    """Exact dynamic program after quantizing errors to integer units.

    The plan minimizes cost among prunings whose quantized error is at most the
    supplied budget. The function is exact for the quantized model.
    """
    if budget < 0 or scale <= 0:
        raise ValueError("budget and scale are invalid")

    def units(error: float) -> int:
        return int(np.ceil(error / scale - 1e-14))

    def solve(node: TreeNode) -> dict[int, TreePlan]:
        table: dict[int, TreePlan] = {}
        e = units(node.keep_error)
        if e <= budget:
            table[e] = TreePlan(node.keep_cost, node.keep_cost, node.keep_error, (node.name,))
        if not node.children:
            return table
        merged: dict[int, TreePlan] = {0: TreePlan(node.split_cost, node.split_cost, 0.0, ())}
        for child in node.children:
            child_table = solve(child)
            nxt: dict[int, TreePlan] = {}
            for e0, p0 in merged.items():
                for e1, p1 in child_table.items():
                    et = e0 + e1
                    if et > budget:
                        continue
                    candidate = TreePlan(
                        objective=p0.cost + p1.cost,
                        cost=p0.cost + p1.cost,
                        error=p0.error + p1.error,
                        leaves=p0.leaves + p1.leaves,
                    )
                    old = nxt.get(et)
                    if old is None or candidate.cost < old.cost:
                        nxt[et] = candidate
            merged = nxt
        for e2, p2 in merged.items():
            old = table.get(e2)
            if old is None or p2.cost < old.cost:
                table[e2] = p2
        return table

    table = solve(root)
    if not table:
        return None
    return min(table.values(), key=lambda p: (p.cost, p.error, p.leaves))


@dataclass(frozen=True)
class DTypeChoice:
    name: str
    cost: float
    error_units: int


def assign_discrete_precisions(options: Sequence[Sequence[DTypeChoice]], budget: int) -> tuple[float, tuple[str, ...]] | None:
    if budget < 0:
        raise ValueError("budget must be nonnegative")
    table: dict[int, tuple[float, tuple[str, ...]]] = {0: (0.0, ())}
    for edge_options in options:
        if not edge_options:
            raise ValueError("every edge must have at least one dtype option")
        nxt: dict[int, tuple[float, tuple[str, ...]]] = {}
        for used, (cost, names) in table.items():
            for choice in edge_options:
                new_error = used + choice.error_units
                if new_error > budget:
                    continue
                candidate = (cost + choice.cost, names + (choice.name,))
                old = nxt.get(new_error)
                if old is None or candidate[0] < old[0]:
                    nxt[new_error] = candidate
        table = nxt
    if not table:
        return None
    return min(table.values(), key=lambda x: (x[0], x[1]))


def clipped_precision_allocation(
    sensitivities: Sequence[float],
    costs: Sequence[float],
    tolerance: float,
    maxima: Sequence[float],
) -> Array:
    s = np.asarray(sensitivities, dtype=float)
    c = np.asarray(costs, dtype=float)
    m = np.asarray(maxima, dtype=float)
    if not (s.ndim == c.ndim == m.ndim == 1 and s.size == c.size == m.size and s.size > 0):
        raise ValueError("inputs must be nonempty vectors of equal length")
    if np.any(s <= 0) or np.any(c <= 0) or np.any(m <= 0) or tolerance <= 0:
        raise ValueError("all parameters must be positive")
    if tolerance > float(np.dot(s, m)) + 1e-12:
        raise ValueError("tolerance exceeds the maximum feasible weighted error")

    maximum = float(np.dot(s, m))
    if abs(tolerance - maximum) <= 1e-14 * max(1.0, maximum):
        return m.copy()

    def weighted(lam: float) -> float:
        return float(np.dot(s, np.minimum(m, c / (lam * s))))

    lo, hi = 0.0, 1.0
    while weighted(hi) > tolerance:
        hi *= 2.0
    for _ in range(220):
        lam = (lo + hi) / 2.0
        if weighted(lam) > tolerance:
            lo = lam
        else:
            hi = lam
    eps = np.minimum(m, c / (hi * s))
    return eps


def block_banded_block_count(packet_count: int, half_bandwidth: int) -> int:
    if packet_count <= 0 or not 0 <= half_bandwidth < packet_count:
        raise ValueError("invalid packet count or half bandwidth")
    p = int(packet_count)
    w = int(half_bandwidth)
    return p * (2 * w + 1) - w * (w + 1)


def circulant_matrix(first_column: Array) -> Array:
    c = np.asarray(first_column)
    if c.ndim != 1 or c.size == 0:
        raise ValueError("first column must be a nonempty vector")
    n = c.size
    return np.asarray([[c[(j - k) % n] for k in range(n)] for j in range(n)])


def circulant_apply_fft(first_column: Array, x: Array) -> Array:
    c = np.asarray(first_column)
    x = np.asarray(x)
    if c.ndim != 1 or x.shape[0] != c.size:
        raise ValueError("incompatible circulant data")
    if x.ndim == 1:
        return np.fft.ifft(np.fft.fft(c) * np.fft.fft(x))
    if x.ndim == 2:
        return np.fft.ifft(np.fft.fft(c)[:, None] * np.fft.fft(x, axis=0), axis=0)
    raise ValueError("right hand side must be a vector or matrix")


def toeplitz_apply_embedding(first_column: Array, first_row: Array, x: Array) -> Array:
    c = np.asarray(first_column)
    r = np.asarray(first_row)
    x = np.asarray(x)
    if c.ndim != 1 or r.ndim != 1 or c.shape != r.shape or x.ndim != 1 or x.size != c.size:
        raise ValueError("incompatible Toeplitz data")
    if not np.allclose(c[0], r[0]):
        raise ValueError("Toeplitz corner entries must agree")
    n = c.size
    g = np.concatenate((c, np.zeros(1, dtype=np.result_type(c, r, x)), r[:0:-1]))
    padded = np.concatenate((x, np.zeros(n, dtype=np.result_type(c, r, x))))
    return circulant_apply_fft(g, padded)[:n]


def kronecker_modewise_apply(a: Array, b: Array, x: Array) -> Array:
    a = np.asarray(a)
    b = np.asarray(b)
    x = np.asarray(x)
    if a.ndim != 2 or b.ndim != 2 or x.shape != (b.shape[1], a.shape[1]):
        raise ValueError("incompatible Kronecker data")
    return b @ x @ a.T


def walsh_hadamard_transform(x: Array, *, normalized: bool = False) -> Array:
    y = np.asarray(x).copy()
    if y.ndim != 1 or y.size == 0 or y.size & (y.size - 1):
        raise ValueError("input length must be a positive power of two")
    h = 1
    while h < y.size:
        for start in range(0, y.size, 2 * h):
            u = y[start : start + h].copy()
            v = y[start + h : start + 2 * h].copy()
            y[start : start + h] = u + v
            y[start + h : start + 2 * h] = u - v
        h *= 2
    if normalized:
        y = y / np.sqrt(y.size)
    return y


def block_diagonal_projection(matrix: Array, layout: PacketLayout) -> Array:
    a = np.asarray(matrix)
    if a.shape != (layout.n, layout.n):
        raise ValueError("matrix has incompatible shape")
    out = np.zeros_like(a)
    for sl in layout.slices:
        out[sl, sl] = a[sl, sl]
    return out


def repeated_recompression_bound(factors: Sequence[Array], errors: Sequence[Array]) -> float:
    if len(factors) != len(errors) or not factors:
        raise ValueError("factor and error lists must have equal positive length")
    norms = [float(np.linalg.norm(a, 2)) for a in factors]
    total = 0.0
    m = len(factors)
    for j, error in enumerate(errors):
        suffix = float(np.prod(norms[j + 1 :], dtype=float)) if j + 1 < m else 1.0
        total += suffix * float(np.linalg.norm(error, 2))
    return total
