from __future__ import annotations

from dataclasses import dataclass
from itertools import combinations
from typing import Iterable, Sequence

import numpy as np

Array = np.ndarray
Pair = tuple[int, int]


@dataclass(frozen=True)
class EdgeRisk:
    pair: Pair
    vector: Array
    scalar_risk: float
    saved_cost: float


@dataclass(frozen=True)
class ScheduleResult:
    omitted_pairs: tuple[Pair, ...]
    retained_pairs: tuple[Pair, ...]
    additive_risk_bound: float
    exact_transfer_envelope: float
    saved_cost: float
    retained_cost: float
    budget: float
    certificate_valid: bool
    method: str


@dataclass(frozen=True)
class PipelineEstimate:
    single_buffer_time: float
    double_buffer_time: float
    ideal_speedup: float
    resident_bytes_single: int
    resident_bytes_double: int


def symmetric_offdiag_pairs(q: int) -> list[Pair]:
    return [(h, g) for h in range(int(q)) for g in range(h + 1, int(q))]


def pair_delta(B: Array, pair: Pair) -> Array:
    B = np.asarray(B, dtype=np.float64)
    h, g = pair
    D = np.zeros_like(B)
    D[h, g] = B[h, g]
    D[g, h] = B[g, h]
    return D


def matrix_powers(B: Array, max_power: int) -> list[Array]:
    B = np.asarray(B, dtype=np.float64)
    q = B.shape[0]
    out = [np.eye(q, dtype=np.float64)]
    for _ in range(max_power):
        out.append(out[-1] @ B)
    return out


def depth_edge_risk_vector(
    B: Array,
    rho0: Array,
    depth: int,
    pair: Pair,
    *,
    powers: Sequence[Array] | None = None,
) -> Array:
    """Additive safe risk vector for symmetrically omitting one phase pair.

    q_e^(k) = sum_{j=0}^{k-1} B^(k-1-j) Delta_e B^j rho0.
    """
    B = np.asarray(B, dtype=np.float64)
    rho0 = np.asarray(rho0, dtype=np.float64)
    depth = int(depth)
    if depth < 1:
        return np.zeros_like(rho0)
    if powers is None:
        powers = matrix_powers(B, depth)
    D = pair_delta(B, pair)
    out = np.zeros_like(rho0)
    for j in range(depth):
        out += powers[depth - 1 - j] @ D @ (powers[j] @ rho0)
    return out


def polynomial_edge_risk_vector(
    B: Array,
    rho0: Array,
    coefficients: Iterable[float],
    pair: Pair,
) -> Array:
    """Safe additive risk vector for a polynomial Krylov combination."""
    coeff = np.asarray(tuple(coefficients), dtype=np.float64)
    if coeff.size <= 1:
        return np.zeros_like(np.asarray(rho0, dtype=np.float64))
    powers = matrix_powers(B, coeff.size - 1)
    out = np.zeros_like(np.asarray(rho0, dtype=np.float64))
    for depth, a in enumerate(coeff):
        if depth == 0 or a == 0:
            continue
        out += abs(float(a)) * depth_edge_risk_vector(
            B, rho0, depth, pair, powers=powers
        )
    return out


def edge_risks_depth(
    B: Array,
    rho0: Array,
    depth: int,
    *,
    pairs: Sequence[Pair] | None = None,
    costs: dict[Pair, float] | None = None,
) -> list[EdgeRisk]:
    B = np.asarray(B, dtype=np.float64)
    q = B.shape[0]
    if pairs is None:
        pairs = symmetric_offdiag_pairs(q)
    powers = matrix_powers(B, int(depth))
    risks = []
    for pair in pairs:
        vec = depth_edge_risk_vector(B, rho0, depth, pair, powers=powers)
        cost = 1.0 if costs is None else float(costs[pair])
        risks.append(
            EdgeRisk(
                pair=pair,
                vector=vec,
                scalar_risk=float(np.linalg.norm(vec)),
                saved_cost=cost,
            )
        )
    return risks


def edge_risks_polynomial(
    B: Array,
    rho0: Array,
    coefficients: Iterable[float],
    *,
    pairs: Sequence[Pair] | None = None,
    costs: dict[Pair, float] | None = None,
) -> list[EdgeRisk]:
    B = np.asarray(B, dtype=np.float64)
    q = B.shape[0]
    if pairs is None:
        pairs = symmetric_offdiag_pairs(q)
    risks = []
    for pair in pairs:
        vec = polynomial_edge_risk_vector(B, rho0, coefficients, pair)
        cost = 1.0 if costs is None else float(costs[pair])
        risks.append(
            EdgeRisk(
                pair=pair,
                vector=vec,
                scalar_risk=float(np.linalg.norm(vec)),
                saved_cost=cost,
            )
        )
    return risks


def prune_pairs(B: Array, omitted_pairs: Iterable[Pair]) -> Array:
    B0 = np.asarray(B, dtype=np.float64).copy()
    for h, g in omitted_pairs:
        B0[h, g] = 0.0
        B0[g, h] = 0.0
    return B0


def exact_depth_transfer_envelope(
    B: Array,
    rho0: Array,
    depth: int,
    omitted_pairs: Iterable[Pair],
) -> float:
    B = np.asarray(B, dtype=np.float64)
    rho0 = np.asarray(rho0, dtype=np.float64)
    B0 = prune_pairs(B, omitted_pairs)
    diff = (
        np.linalg.matrix_power(B, int(depth))
        - np.linalg.matrix_power(B0, int(depth))
    ) @ rho0
    return float(np.linalg.norm(diff))


def additive_scalar_bound(
    risks: Sequence[EdgeRisk],
    omitted_pairs: Iterable[Pair],
) -> float:
    omitted = set(omitted_pairs)
    return float(sum(r.scalar_risk for r in risks if r.pair in omitted))


def additive_vector_bound(
    risks: Sequence[EdgeRisk],
    omitted_pairs: Iterable[Pair],
) -> float:
    omitted = set(omitted_pairs)
    selected = [r.vector for r in risks if r.pair in omitted]
    if not selected:
        return 0.0
    return float(np.linalg.norm(np.sum(selected, axis=0)))


def unit_cost_optimal_additive_schedule(
    B: Array,
    rho0: Array,
    depth: int,
    budget: float,
    *,
    pairs: Sequence[Pair] | None = None,
) -> ScheduleResult:
    """Globally cardinality-optimal under the scalar additive certificate."""
    risks = edge_risks_depth(B, rho0, depth, pairs=pairs)
    ordered = sorted(risks, key=lambda r: (r.scalar_risk, r.pair))
    omitted = []
    used = 0.0
    for r in ordered:
        if used + r.scalar_risk <= budget + 1e-15:
            omitted.append(r.pair)
            used += r.scalar_risk
        else:
            break
    all_pairs = tuple(r.pair for r in risks)
    omitted_set = set(omitted)
    retained = tuple(p for p in all_pairs if p not in omitted_set)
    exact = exact_depth_transfer_envelope(B, rho0, depth, omitted)
    return ScheduleResult(
        omitted_pairs=tuple(omitted),
        retained_pairs=retained,
        additive_risk_bound=float(used),
        exact_transfer_envelope=exact,
        saved_cost=float(len(omitted)),
        retained_cost=float(len(retained)),
        budget=float(budget),
        certificate_valid=bool(used <= budget + 1e-15),
        method="unit-cost additive optimum",
    )


def exact_envelope_refinement(
    B: Array,
    rho0: Array,
    depth: int,
    budget: float,
    initial_omitted: Iterable[Pair],
    *,
    pairs: Sequence[Pair] | None = None,
) -> ScheduleResult:
    """Greedily use slack in the exact transfer envelope.

    This remains certified but is not claimed globally optimal.
    """
    if pairs is None:
        pairs = symmetric_offdiag_pairs(np.asarray(B).shape[0])
    omitted = list(initial_omitted)
    omitted_set = set(omitted)
    remaining = [p for p in pairs if p not in omitted_set]
    current = exact_depth_transfer_envelope(B, rho0, depth, omitted)

    while True:
        feasible = []
        for pair in remaining:
            trial = omitted + [pair]
            value = exact_depth_transfer_envelope(B, rho0, depth, trial)
            if value <= budget + 1e-15:
                feasible.append((value - current, value, pair))
        if not feasible:
            break
        feasible.sort(key=lambda x: (x[0], x[1], x[2]))
        _, current, chosen = feasible[0]
        omitted.append(chosen)
        remaining.remove(chosen)

    risks = edge_risks_depth(B, rho0, depth, pairs=pairs)
    retained = tuple(p for p in pairs if p not in set(omitted))
    return ScheduleResult(
        omitted_pairs=tuple(omitted),
        retained_pairs=retained,
        additive_risk_bound=additive_scalar_bound(risks, omitted),
        exact_transfer_envelope=current,
        saved_cost=float(len(omitted)),
        retained_cost=float(len(retained)),
        budget=float(budget),
        certificate_valid=bool(current <= budget + 1e-15),
        method="exact-envelope greedy refinement",
    )


def weighted_greedy_schedule(
    B: Array,
    rho0: Array,
    depth: int,
    budget: float,
    costs: dict[Pair, float],
    *,
    pairs: Sequence[Pair] | None = None,
) -> ScheduleResult:
    """Certified cost-aware heuristic for unequal communication costs."""
    risks = edge_risks_depth(B, rho0, depth, pairs=pairs, costs=costs)

    def key(r: EdgeRisk):
        if r.scalar_risk == 0:
            return (float("inf"), r.saved_cost, r.pair)
        return (r.saved_cost / r.scalar_risk, r.saved_cost, r.pair)

    ordered = sorted(risks, key=key, reverse=True)
    omitted = []
    used = 0.0
    saved = 0.0
    for r in ordered:
        if used + r.scalar_risk <= budget + 1e-15:
            omitted.append(r.pair)
            used += r.scalar_risk
            saved += r.saved_cost

    all_pairs = tuple(r.pair for r in risks)
    omitted_set = set(omitted)
    retained = tuple(p for p in all_pairs if p not in omitted_set)
    total_cost = float(sum(r.saved_cost for r in risks))
    exact = exact_depth_transfer_envelope(B, rho0, depth, omitted)
    return ScheduleResult(
        omitted_pairs=tuple(omitted),
        retained_pairs=retained,
        additive_risk_bound=float(used),
        exact_transfer_envelope=exact,
        saved_cost=float(saved),
        retained_cost=float(total_cost - saved),
        budget=float(budget),
        certificate_valid=bool(used <= budget + 1e-15),
        method="weighted greedy by saved-cost/risk",
    )


def fractional_knapsack_upper_bound(
    risks: Sequence[EdgeRisk],
    budget: float,
) -> float:
    """Upper bound on maximum saveable cost under the scalar additive surrogate."""
    items = sorted(
        risks,
        key=lambda r: float("inf") if r.scalar_risk == 0 else r.saved_cost / r.scalar_risk,
        reverse=True,
    )
    remaining = float(budget)
    value = 0.0
    for r in items:
        if r.scalar_risk == 0:
            value += r.saved_cost
            continue
        if r.scalar_risk <= remaining:
            remaining -= r.scalar_risk
            value += r.saved_cost
        else:
            value += r.saved_cost * (remaining / r.scalar_risk)
            break
    return float(value)


def brute_force_unit_optimum(
    B: Array,
    rho0: Array,
    depth: int,
    budget: float,
    *,
    pairs: Sequence[Pair] | None = None,
    use_exact_envelope: bool = True,
) -> ScheduleResult:
    """Exact small-graph optimizer; intended only for audits (<= 20 pairs)."""
    if pairs is None:
        pairs = symmetric_offdiag_pairs(np.asarray(B).shape[0])
    pairs = list(pairs)
    if len(pairs) > 20:
        raise ValueError("brute-force audit limited to at most 20 pairs")
    risks = edge_risks_depth(B, rho0, depth, pairs=pairs)

    best = ()
    best_cert = 0.0
    for r in range(len(pairs) + 1):
        for subset in combinations(pairs, r):
            if use_exact_envelope:
                cert = exact_depth_transfer_envelope(B, rho0, depth, subset)
            else:
                cert = additive_scalar_bound(risks, subset)
            if cert <= budget + 1e-15:
                if len(subset) > len(best):
                    best = subset
                    best_cert = cert
            # subsets of the same cardinality all have equal objective

    retained = tuple(p for p in pairs if p not in set(best))
    add = additive_scalar_bound(risks, best)
    exact = exact_depth_transfer_envelope(B, rho0, depth, best)
    return ScheduleResult(
        omitted_pairs=tuple(best),
        retained_pairs=retained,
        additive_risk_bound=add,
        exact_transfer_envelope=exact,
        saved_cost=float(len(best)),
        retained_cost=float(len(retained)),
        budget=float(budget),
        certificate_valid=bool(best_cert <= budget + 1e-15),
        method=(
            "brute-force exact-envelope optimum"
            if use_exact_envelope
            else "brute-force additive optimum"
        ),
    )


def double_buffer_pipeline_estimate(
    io_times: Sequence[float],
    compute_times: Sequence[float],
    *,
    resident_block_bytes: int,
    fixed_working_bytes: int = 0,
) -> PipelineEstimate:
    """Ideal two-buffer overlap model.

    Transfer of block b+1 overlaps computation on block b.
    """
    io = np.asarray(io_times, dtype=np.float64)
    comp = np.asarray(compute_times, dtype=np.float64)
    if io.ndim != 1 or comp.ndim != 1 or io.size != comp.size or io.size == 0:
        raise ValueError("io_times and compute_times must be equal nonempty vectors")
    sequential = float(np.sum(io + comp))
    if io.size == 1:
        double = sequential
    else:
        double = float(
            io[0]
            + np.sum(np.maximum(comp[:-1], io[1:]))
            + comp[-1]
        )
    return PipelineEstimate(
        single_buffer_time=sequential,
        double_buffer_time=double,
        ideal_speedup=sequential / double if double > 0 else float("inf"),
        resident_bytes_single=int(resident_block_bytes + fixed_working_bytes),
        resident_bytes_double=int(2 * resident_block_bytes + fixed_working_bytes),
    )
