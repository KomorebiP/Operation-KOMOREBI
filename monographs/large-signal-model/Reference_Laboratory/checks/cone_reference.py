"""Exact finite probability-domain certificates for the theory laboratory.

No hidden generator or numerical tolerance is used. A returned certificate proves
internal validity of the supplied finite matrices, not statistical truth or global
rank coverage. The general rational search theorem is broader than the bounded
2D interval search implemented here.
"""
from __future__ import annotations
from dataclasses import dataclass
from fractions import Fraction
from collections.abc import Mapping
from typing import Any
import sympy as sp

Symbol = tuple[int, int]


def rational_matrix(value: Any, name: str) -> sp.ImmutableMatrix:
    try:
        m = sp.ImmutableMatrix(value)
    except (TypeError, ValueError) as exc:
        raise ValueError(f'{name} must be a rectangular matrix.') from exc
    if not m.rows or not m.cols or any(not x.is_Rational for x in m):
        raise ValueError(f'{name} must be nonempty and exactly rational; floats are rejected.')
    return m


def symbols(mapping: Mapping[Symbol, Any]) -> tuple[Symbol, ...]:
    if not mapping:
        raise ValueError('A nonempty operator family is required.')
    keys = tuple(mapping)
    if any(not isinstance(k, tuple) or len(k) != 2 or
           any(not isinstance(v, int) or isinstance(v, bool) for v in k) for k in keys):
        raise ValueError('Symbols must be pairs of integer action/observation labels.')
    actions = {k[0] for k in keys}
    obs = {k[1] for k in keys}
    if set(keys) != {(a, o) for a in actions for o in obs}:
        raise ValueError('Supply every declared action/observation branch, including zero matrices.')
    return tuple(sorted(keys))


def verify_certificate(operators: Mapping[Symbol, Any], mass: Any, initial: Any,
                       generators: Any, lifts: Mapping[Symbol, Any], weights: Any) -> dict[str, Any]:
    """Check Proposition 39 using rational equalities and nonnegative witnesses."""
    keys = symbols(operators)
    if set(lifts) != set(keys):
        raise ValueError('Lift and operator symbols must match exactly.')
    v = rational_matrix(generators, 'generators')
    r, m = v.shape
    lam = rational_matrix(mass, 'mass')
    z = rational_matrix(initial, 'initial')
    alpha = rational_matrix(weights, 'weights')
    if lam.shape != (1, r) or z.shape != (r, 1) or alpha.shape != (m, 1):
        raise ValueError('Mass, initial state or weights have incompatible dimensions.')
    if v.rank() != r:
        raise ValueError('Generators must span the declared predictive space.')
    if lam * v != sp.ones(1, m):
        raise ValueError('Every generator must have mass one.')
    if any(x < 0 for x in alpha) or sum(alpha) != 1 or v * alpha != z:
        raise ValueError('Initial weights must be a probability vector synthesizing the initial state.')
    bs, aa = {}, {}
    for s in keys:
        b = rational_matrix(operators[s], f'operator {s}')
        a = rational_matrix(lifts[s], f'lift {s}')
        if b.shape != (r, r) or a.shape != (m, m):
            raise ValueError(f'Operator/lift shape mismatch at {s}.')
        if any(x < 0 for x in a):
            raise ValueError(f'Negative lift entry at {s}.')
        if b * v != v * a:
            raise ValueError(f'Intertwining equality fails at {s}.')
        bs[s], aa[s] = b, a
    for action in sorted({s[0] for s in keys}):
        btotal = sum((bs[s] for s in keys if s[0] == action), sp.zeros(r))
        atotal = sum((aa[s] for s in keys if s[0] == action), sp.zeros(m))
        if lam * btotal != lam or sp.ones(1, m) * atotal != sp.ones(1, m):
            raise ValueError(f'Mass conservation fails for action {action}.')
    return {
        'status': 'CERTIFIED_INTERNAL_VALIDITY', 'arithmetic': 'exact rational',
        'predictive_dimension': r, 'generator_count': m,
        'all_word_probability_validity': True, 'witness_minimum_entry': str(min(x for a in aa.values() for x in a)),
        'global_rank_coverage_verified': False, 'statistical_truth_verified': False,
        'hidden_generator_used_by_checker': False, 'proof_kernel_run': False,
        'mass': [[str(x) for x in row] for row in lam.tolist()],
        'initial': [[str(x) for x in row] for row in z.tolist()],
        'operators': {f'{s[0]},{s[1]}': [[str(x) for x in row] for row in bs[s].tolist()] for s in keys},
        'generators': [[str(x) for x in row] for row in v.tolist()],
        'initial_weights': list(map(str, alpha)),
        'lifts': {f'{s[0]},{s[1]}': [[str(x) for x in row] for row in aa[s].tolist()] for s in keys},
    }


@dataclass(frozen=True)
class IntervalCertificate:
    lower: sp.Rational
    upper: sp.Rational
    generators: sp.ImmutableMatrix
    lifts: Mapping[Symbol, sp.ImmutableMatrix]
    weights: sp.ImmutableMatrix
    tested_candidates: int
    candidate_count: int
    denominator_bound: int
    report: dict[str, Any]


def search_interval(operators: Mapping[Symbol, Any], initial: Any,
                    *, denominator_bound: int = 8) -> IntervalCertificate | None:
    """Search normalized states (1,q) with q in [0,1], using a finite rational grid.

    Endpoints are sorted by interval width and then lexicographically. Returning
    None means this finite grid supplies no witness, not that the model is invalid.
    """
    if (not isinstance(denominator_bound, int) or isinstance(denominator_bound, bool)
            or denominator_bound < 1):
        raise ValueError('denominator_bound must be a positive integer.')
    keys = symbols(operators)
    bs = {s: rational_matrix(operators[s], str(s)) for s in keys}
    z = rational_matrix(initial, 'initial')
    if z.shape != (2, 1) or z[0] != 1 or any(b.shape != (2, 2) for b in bs.values()):
        raise ValueError('The interval search requires a mass-first two-dimensional model.')
    lam = sp.ImmutableMatrix([[1, 0]])
    for a in sorted({s[0] for s in keys}):
        if lam * sum((bs[s] for s in keys if s[0] == a), sp.zeros(2)) != lam:
            raise ValueError('The supplied family is not mass conserving.')
    grid = sorted({Fraction(n, d) for d in range(1, denominator_bound + 1) for n in range(d + 1)})
    q = Fraction(int(z[1].p), int(z[1].q))
    candidates = sorted((u-l, l, u) for l in grid for u in grid if l < u and l <= q <= u)
    for index, (_, lo, hi) in enumerate(candidates, start=1):
        l, u = sp.Rational(lo.numerator, lo.denominator), sp.Rational(hi.numerator, hi.denominator)
        v = sp.ImmutableMatrix([[1, 1], [l, u]])
        inv = v.inv()
        lifts = {s: sp.ImmutableMatrix(inv * b * v) for s, b in bs.items()}
        weights = sp.ImmutableMatrix(inv * z)
        if any(x < 0 for aa in lifts.values() for x in aa):
            continue
        report = verify_certificate(bs, lam, z, v, lifts, weights)
        report.update({'search_scope': 'finite rational interval grid in a declared probability coordinate',
                       'denominator_bound': denominator_bound, 'tested_candidates': index,
                       'total_grid_candidates': len(candidates), 'minimal_in_grid_order_only': True,
                       'hidden_generator_used_by_search': False})
        return IntervalCertificate(l, u, v, lifts, weights, index, len(candidates), denominator_bound, report)
    return None


def probability(operators: Mapping[Symbol, sp.MatrixBase], mass: sp.MatrixBase,
                initial: sp.MatrixBase, word: tuple[Symbol, ...]) -> sp.Rational:
    z = initial
    for symbol in word:
        if symbol not in operators:
            raise ValueError(f'Unknown symbol {symbol}.')
        z = operators[symbol] * z
    return sp.Rational((mass * z)[0])


def minimum_mixture_repair(lifts: Mapping[Symbol, Any], reference: Mapping[Symbol, Any]) -> tuple[sp.Rational, dict]:
    """Return exact minimal common mixture weight making all lift entries nonnegative.

    This routine checks nonnegativity and per-action column normalization of the
    reference, and normalization (not positivity) of the supplied raw lifts.
    """
    keys = symbols(lifts)
    if set(keys) != set(reference):
        raise ValueError('Reference symbols must match.')
    aa = {s: rational_matrix(lifts[s], str(s)) for s in keys}
    nn = {s: rational_matrix(reference[s], str(s)) for s in keys}
    m = aa[keys[0]].rows
    if any(a.shape != (m, m) for a in [*aa.values(), *nn.values()]):
        raise ValueError('Every lift must be square and of the same size.')
    if any(x <= 0 for n in nn.values() for x in n):
        raise ValueError('The reference must have strictly positive entries.')
    for a in {s[0] for s in keys}:
        for fam in (aa, nn):
            if sp.ones(1, m) * sum((fam[s] for s in keys if s[0] == a), sp.zeros(m)) != sp.ones(1, m):
                raise ValueError('Both families must conserve per-action mass.')
    eta = max([sp.Rational(0)] + [-x/(y-x) for s in keys for x, y in zip(aa[s], nn[s]) if x < 0])
    result = {s: sp.ImmutableMatrix((1-eta)*aa[s]+eta*nn[s]) for s in keys}
    return sp.Rational(eta), result
