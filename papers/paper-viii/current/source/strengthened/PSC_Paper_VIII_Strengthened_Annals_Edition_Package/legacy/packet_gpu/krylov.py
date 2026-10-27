from __future__ import annotations

from dataclasses import dataclass
from typing import Callable

import numpy as np

Array = np.ndarray


def preconditioned_condition_bound(eta: float) -> float:
    if not 0 <= eta < 1:
        raise ValueError("eta must satisfy 0 <= eta < 1")
    return (1.0 + eta) / (1.0 - eta)


@dataclass(frozen=True)
class CGResult:
    x: Array
    residual_norms: tuple[float, ...]
    iterations: int
    converged: bool


def conjugate_gradient(
    apply: Callable[[Array], Array],
    b: Array,
    *,
    precondition: Callable[[Array], Array] | None = None,
    x0: Array | None = None,
    tol: float = 1e-10,
    maxiter: int | None = None,
) -> CGResult:
    b = np.asarray(b, dtype=float)
    x = np.zeros_like(b) if x0 is None else np.asarray(x0, dtype=float).copy()
    n = b.size
    maxiter = maxiter or (10 * n)
    r = b - apply(x)
    z = precondition(r) if precondition else r.copy()
    p = z.copy()
    rz_old = float(np.dot(r, z))
    residuals = [float(np.linalg.norm(r))]
    if residuals[-1] <= tol:
        return CGResult(x, tuple(residuals), 0, True)
    for k in range(1, maxiter + 1):
        ap = apply(p)
        denom = float(np.dot(p, ap))
        if denom <= 0:
            raise ValueError("operator is not positive definite in the generated direction")
        alpha = rz_old / denom
        x += alpha * p
        r -= alpha * ap
        residuals.append(float(np.linalg.norm(r)))
        if residuals[-1] <= tol:
            return CGResult(x, tuple(residuals), k, True)
        z = precondition(r) if precondition else r.copy()
        rz_new = float(np.dot(r, z))
        beta = rz_new / rz_old
        p = z + beta * p
        rz_old = rz_new
    return CGResult(x, tuple(residuals), maxiter, False)


def lanczos_tridiagonal(
    apply: Callable[[Array], Array],
    dimension: int,
    steps: int,
    *,
    seed: int = 0,
) -> tuple[Array, Array, Array]:
    if not 1 <= steps <= dimension:
        raise ValueError("steps must lie between 1 and dimension")
    rng = np.random.default_rng(seed)
    q = rng.normal(size=dimension)
    q /= np.linalg.norm(q)
    q_prev = np.zeros_like(q)
    beta_prev = 0.0
    basis: list[Array] = []
    alpha: list[float] = []
    beta: list[float] = []
    for j in range(steps):
        basis.append(q.copy())
        z = apply(q) - beta_prev * q_prev
        a = float(np.dot(q, z))
        alpha.append(a)
        z -= a * q
        # Full reorthogonalization keeps the finite certificate stable.
        for qi in basis:
            z -= np.dot(qi, z) * qi
        b = float(np.linalg.norm(z))
        if j < steps - 1:
            beta.append(b)
        if b < 1e-14:
            break
        q_prev, q = q, z / b
        beta_prev = b
    m = len(alpha)
    t = np.diag(alpha)
    if m > 1:
        bvals = np.array(beta[: m - 1])
        t += np.diag(bvals, 1) + np.diag(bvals, -1)
    qmat = np.column_stack(basis[:m])
    return t, qmat, np.array(alpha)
