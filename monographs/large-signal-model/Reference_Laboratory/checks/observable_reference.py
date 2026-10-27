"""Small exact reference implementation of Propositions 14--15 and 25.

This module takes rational observations, not hidden matrices. It certifies
relations on the observed span. Coverage of the true predictive state space is
an external assumption and is never claimed merely from a fitted matrix.
Requires SymPy. No downloads, random sampling or external task data.
"""
from __future__ import annotations
from dataclasses import dataclass
from typing import Sequence
import sympy as sp


def rational_matrix(value: object, name: str) -> sp.Matrix:
    try:
        matrix = sp.Matrix(value)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"{name} must be a two-dimensional rational matrix.") from exc
    if any(v.is_Rational is not True for v in matrix):
        raise ValueError(f"{name} must contain exact rational values, not floats or symbols.")
    return matrix


def zero(matrix: sp.MatrixBase) -> bool:
    return all(sp.simplify(value) == 0 for value in matrix)


@dataclass(frozen=True)
class SpanModel:
    """Coordinates z=left_inverse @ history on the certified observed span."""
    basis: sp.ImmutableMatrix
    left_inverse: sp.ImmutableMatrix
    transition: sp.ImmutableMatrix
    input_rank: int
    sample_pairs: int
    ambient_dimension: int

    @property
    def ambient_transition(self) -> sp.ImmutableMatrix:
        return sp.ImmutableMatrix(self.basis * self.transition * self.left_inverse)

    def certificate(self) -> dict[str, object]:
        def strings(m: sp.MatrixBase) -> list[list[str]]:
            return [[str(v) for v in row] for row in m.tolist()]
        return {
            "arithmetic": "exact rational",
            "kernel_consistency": True,
            "successors_in_observed_span": True,
            "input_rank": self.input_rank,
            "sample_pairs": self.sample_pairs,
            "ambient_dimension": self.ambient_dimension,
            "basis": strings(self.basis),
            "left_inverse": strings(self.left_inverse),
            "transition": strings(self.transition),
            "ambient_transition": strings(self.ambient_transition),
            "true_state_space_coverage": "NOT_CERTIFIED_BY_THESE_SAMPLES",
            "true_linear_closure": "EXTERNAL_MODEL_ASSUMPTION",
            "scope": "Unique exact transition on the observed invariant span only.",
        }


def fit_closed_span(inputs: object, successors: object) -> SpanModel:
    """Fit the unique transition on a rational observed invariant span.

    A failure of the successor-span test means this data span is not closed.
    It does not establish that the generating system has no larger closure.
    """
    x = rational_matrix(inputs, "inputs")
    y = rational_matrix(successors, "successors")
    if x.shape != y.shape or x.rows < 1 or x.cols < 1:
        raise ValueError("Inputs and successors must have the same nonempty shape.")
    if any(not zero(y * vector) for vector in x.nullspace()):
        raise ValueError("Inconsistent paired data: an input dependence has unequal successors.")
    columns = x.columnspace()
    r = len(columns)
    if not r:
        return SpanModel(sp.ImmutableMatrix(sp.zeros(x.rows, 0)),
                         sp.ImmutableMatrix(sp.zeros(0, x.rows)),
                         sp.ImmutableMatrix(sp.zeros(0, 0)), 0, x.cols, x.rows)
    u = sp.Matrix.hstack(*columns)
    left = (u.T * u).inv() * u.T
    if not zero(u * left * y - y):
        raise ValueError("Successors leave the observed input span; a closed observed-span model is not certified.")
    xr, yr = left * x, left * y
    right = xr.T * (xr * xr.T).inv()
    b = yr * right
    if not zero(b * xr - yr):
        raise ArithmeticError("Internal exact replay check failed.")
    return SpanModel(sp.ImmutableMatrix(u), sp.ImmutableMatrix(left),
                     sp.ImmutableMatrix(b), r, x.cols, x.rows)


def delay_pairs(outputs: Sequence[object], h: int) -> tuple[sp.Matrix, sp.Matrix]:
    """Consecutive scalar-output windows; no future samples enter an initial window."""
    if isinstance(h, bool) or not isinstance(h, int) or h < 1:
        raise ValueError("Delay length must be a positive integer.")
    values = list(outputs)
    if len(values) < h + 1:
        raise ValueError("At least h+1 outputs are needed for one paired window.")
    column = rational_matrix([[v] for v in values], "outputs")
    n = len(values) - h
    x = sp.Matrix(h, n, lambda i, j: column[i + j])
    y = sp.Matrix(h, n, lambda i, j: column[i + j + 1])
    return x, y


def learn_delay(outputs: Sequence[object], h: int) -> SpanModel:
    """Identify from supplied outputs within a declared delay-state model class."""
    return fit_closed_span(*delay_pairs(outputs, h))


def forecast_scalar(model: SpanModel, history: Sequence[object], steps: int) -> list[sp.Expr]:
    """Return the next `steps` scalar outputs after the supplied observed history."""
    if isinstance(steps, bool) or not isinstance(steps, int) or steps < 0:
        raise ValueError("Steps must be a nonnegative integer.")
    window = rational_matrix([[v] for v in history], "history")
    if window.shape != (model.ambient_dimension, 1):
        raise ValueError("History must match the fitted delay dimension.")
    if not zero(model.basis * model.left_inverse * window - window):
        raise ValueError("History is outside the certified observed span.")
    coordinate = model.left_inverse * window
    out: list[sp.Expr] = []
    for _ in range(steps):
        coordinate = model.transition * coordinate
        represented = model.basis * coordinate
        out.append(sp.simplify(represented[-1]))
    return out
