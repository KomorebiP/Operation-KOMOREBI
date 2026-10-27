"""Observable table realization for Foundations 0.3.0.

The fitter accepts only finite word-probability tables, never a hidden generator.
It certifies the finite linear identities it checks. Global rank coverage and a
probability-invariant cone are separate assumptions, not inferred by this fitter.
"""
from __future__ import annotations
from dataclasses import dataclass
from collections.abc import Mapping, Sequence
from typing import Any
import sympy as sp
import numpy as np

Symbol = tuple[int, int]
Word = tuple[Symbol, ...]


def _rational_matrix(value: Any, name: str) -> sp.ImmutableMatrix:
    try:
        matrix = sp.ImmutableMatrix(value)
    except (TypeError, ValueError) as exc:
        raise ValueError(f'{name} must be a rectangular matrix.') from exc
    if any(not entry.is_Rational for entry in matrix):
        raise ValueError(f'{name} must contain exact rational values, not floats or symbols.')
    return matrix


def _symbol(value: Any) -> Symbol:
    if (not isinstance(value, tuple) or len(value) != 2 or
            any(not isinstance(v, int) or isinstance(v, bool) for v in value)):
        raise ValueError('Each symbol must be a tuple of two integer labels.')
    return value


@dataclass(frozen=True)
class ObservableModel:
    """Exact finite table fit with an empty-test mass coordinate."""
    operators: Mapping[Symbol, sp.ImmutableMatrix]
    initial: sp.ImmutableMatrix
    core: sp.ImmutableMatrix
    shifted: Mapping[Symbol, sp.ImmutableMatrix]
    global_rank_upper_bound: int | None = None

    @property
    def dimension(self) -> int:
        return self.core.rows

    @property
    def mass(self) -> sp.ImmutableMatrix:
        return sp.ImmutableMatrix([[1] + [0] * (self.dimension - 1)])

    def _state(self, z: Any) -> sp.ImmutableMatrix:
        z = _rational_matrix(z, 'state')
        if z.shape != (self.dimension, 1):
            raise ValueError('State has the wrong shape.')
        return z

    def unnormalized(self, word: Sequence[Symbol]) -> sp.ImmutableMatrix:
        z = self.initial
        for symbol in word:
            symbol = _symbol(symbol)
            if symbol not in self.operators:
                raise ValueError(f'Unknown action/observation symbol: {symbol}')
            z = self.operators[symbol] * z
        return sp.ImmutableMatrix(z)

    def probability(self, word: Sequence[Symbol]) -> sp.Rational:
        # This does not claim universal nonnegativity for an unvalidated model.
        return sp.Rational((self.mass * self.unnormalized(word))[0])

    def update(self, z: Any, symbol: Symbol) -> tuple[sp.Rational, sp.ImmutableMatrix]:
        z = self._state(z)
        if (self.mass * z)[0] != 1:
            raise ValueError('State mass must be one before a conditional update.')
        symbol = _symbol(symbol)
        if symbol not in self.operators:
            raise ValueError(f'Unknown action/observation symbol: {symbol}')
        u = self.operators[symbol] * z
        probability = sp.Rational((self.mass * u)[0])
        if not 0 < probability <= 1:
            raise ValueError('Branch likelihood must be in (0, 1]; no numerical flooring is applied.')
        return probability, sp.ImmutableMatrix(u / probability)

    def certificate(self) -> dict[str, Any]:
        actions = sorted({s[0] for s in self.operators})
        conservation = {}
        for a in actions:
            total = sp.zeros(self.dimension)
            for s, operator in self.operators.items():
                if s[0] == a:
                    total += operator
            conservation[str(a)] = self.mass * total == self.mass
        return {
            'dimension': self.dimension,
            'core_determinant': str(self.core.det()),
            'exact_shift_interpolation': all(self.operators[s] * self.core == g
                                            for s, g in self.shifted.items()),
            'empty_test_mass_row': list(map(str, self.mass)),
            'initial_mass_one': (self.mass * self.initial)[0] == 1,
            'per_action_mass_conservation': conservation,
            'global_rank_upper_bound_assumed': self.global_rank_upper_bound,
            'global_rank_bound_verified_from_finite_table': False,
            'global_cone_invariance_certified_by_fitter': False,
            'exact_all_word_result': 'conditional on correct population tables and a true rank bound',
            'input_scope': 'only core table, shifted tables, initial core-test probabilities',
        }


def fit_core(core: Any, shifted: Mapping[Symbol, Any], initial: Any,
             *, rank_upper_bound: int | None = None) -> ObservableModel:
    """Fit Proposition 28 exactly. The first selected test must be empty.

    The schema and observable conservation law are checked, but no finite input
    can itself certify the global rank upper bound or all future positivity.
    """
    h = _rational_matrix(core, 'core')
    if h.rows == 0 or h.rows != h.cols:
        raise ValueError('Core must be a nonempty square matrix.')
    if h.det() == 0:
        raise ValueError('Core must be invertible.')
    if any(not 0 <= v <= 1 for v in h):
        raise ValueError('Core entries must be probabilities in [0, 1].')
    if rank_upper_bound is not None:
        if (not isinstance(rank_upper_bound, int) or isinstance(rank_upper_bound, bool)
                or rank_upper_bound < h.rows):
            raise ValueError('Rank upper bound cannot be smaller than the observed core rank.')
        if rank_upper_bound > h.rows:
            raise ValueError('A larger rank bound does not establish full-core coverage.')
    b = _rational_matrix(initial, 'initial')
    if b.shape != (h.rows, 1) or b[0] != 1 or any(not 0 <= v <= 1 for v in b):
        raise ValueError('Initial core probabilities must be a column with first entry one.')
    if not shifted:
        raise ValueError('At least one action/observation matrix is required.')
    gs, operators = {}, {}
    for symbol, raw in shifted.items():
        symbol = _symbol(symbol)
        g = _rational_matrix(raw, 'shifted')
        if g.shape != h.shape or any(not 0 <= v <= 1 for v in g):
            raise ValueError('Shifted tables must match the core and contain probabilities.')
        gs[symbol] = g
        operators[symbol] = sp.ImmutableMatrix(g * h.inv())
    model = ObservableModel(operators, b, h, gs, rank_upper_bound)
    if not all(model.certificate()['per_action_mass_conservation'].values()):
        raise ValueError('Shifted tables violate the declared per-action mass conservation law.')
    return model


def finite_subspace_report(matrix: Any, rank: int, error_budget: float) -> dict[str, Any]:
    """Observable gap report, not a certificate of global process dimension."""
    y = np.asarray(matrix, dtype=float)
    if y.ndim != 2 or min(y.shape) == 0 or not np.isfinite(y).all():
        raise ValueError('Matrix must be finite, nonempty and two dimensional.')
    if not isinstance(rank, int) or isinstance(rank, bool) or not 1 <= rank <= min(y.shape):
        raise ValueError('Rank is outside the finite matrix range.')
    if not np.isfinite(error_budget) or error_budget < 0:
        raise ValueError('Error budget must be finite and nonnegative.')
    singular = np.linalg.svd(y, compute_uv=False)
    lower = float(singular[rank - 1] - error_budget)
    tail = float(singular[rank]) if rank < len(singular) else 0.0
    return {'singular_values': singular.tolist(), 'assumed_true_matrix_rank': rank,
            'rank_assumption_proved': False, 'global_process_rank_proved': False,
            'smallest_retained_true_singular_lower_bound': lower,
            'observed_discarded_singular_value': tail,
            'subspace_bound': (2*error_budget/lower) if lower > 2*error_budget else None,
            'tail_compatible_with_budget': tail <= error_budget + 1e-14}


def noisy_core_bound(h_observed: Any, g_observed: Any, *, h_error: float,
                     g_error: float) -> dict[str, Any]:
    """Numerical solve and Proposition 33's data-based bound."""
    h, g = np.asarray(h_observed, float), np.asarray(g_observed, float)
    if h.ndim != 2 or h.shape[0] == 0 or h.shape[0] != h.shape[1] or g.shape != h.shape:
        raise ValueError('Both inputs must have the same nonempty square shape.')
    if not np.isfinite(h).all() or not np.isfinite(g).all():
        raise ValueError('Matrices must be finite.')
    if any(not np.isfinite(v) or v < 0 for v in [h_error, g_error]):
        raise ValueError('Error budgets must be finite and nonnegative.')
    s = float(np.linalg.svd(h, compute_uv=False)[-1])
    if s <= h_error:
        raise ValueError('Observed singular gap does not exceed the core error budget.')
    b = np.linalg.solve(h.T, g.T).T
    solve_residual = float(np.linalg.norm(b @ h - g, 2))
    # Floating solve residual is included explicitly, rather than claimed zero.
    bound = (g_error + np.linalg.norm(b, 2)*h_error + solve_residual)/(s-h_error)
    return {'operator': b, 'bound': float(bound), 'observed_singular_gap': s,
            'solve_residual': solve_residual, 'global_positivity_certified': False}
