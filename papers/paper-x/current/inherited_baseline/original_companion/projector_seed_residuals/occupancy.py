from __future__ import annotations

from typing import Iterable, Sequence

import sympy as sp


def lagrange_projector(
    operator: sp.Matrix,
    target: int | sp.Rational,
    spectrum: Sequence[int | sp.Rational],
) -> sp.Matrix:
    target = sp.Rational(target)
    values = [sp.Rational(x) for x in spectrum]
    if target not in values:
        return sp.zeros(operator.rows)
    projector = sp.eye(operator.rows)
    for eigenvalue in sorted(set(values)):
        if eigenvalue == target:
            continue
        projector = projector * (operator - eigenvalue * sp.eye(operator.rows)) / (target - eigenvalue)
    return sp.simplify(projector)


def joint_projector(
    operators: Sequence[sp.Matrix],
    targets: Sequence[int | sp.Rational],
    spectra: Sequence[Sequence[int | sp.Rational]],
) -> sp.Matrix:
    if not operators:
        raise ValueError("at least one operator is required")
    if not (len(operators) == len(targets) == len(spectra)):
        raise ValueError("operator data mismatch")
    result = sp.eye(operators[0].rows)
    for operator, target, spectrum in zip(operators, targets, spectra, strict=True):
        result = result * lagrange_projector(operator, target, spectrum)
    return sp.simplify(result)


def projector_trace_rank(projector: sp.Matrix) -> tuple[int, int]:
    return int(sp.trace(projector)), int(projector.rank())
