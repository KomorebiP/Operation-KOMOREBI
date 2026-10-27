from __future__ import annotations

from functools import lru_cache

from dataclasses import dataclass

import sympy as sp


@dataclass(frozen=True)
class BayesCertificate:
    measure: sp.Matrix
    observable: sp.Matrix
    expectation_matrix: sp.Matrix
    projected_observable: sp.Matrix
    expectation_idempotence_residual: sp.Matrix
    weighted_adjoint_residual: sp.Matrix
    sufficient_fine_posterior: sp.Matrix
    sufficient_coarse_posterior: sp.Matrix
    sufficient_residual: sp.Matrix
    nonsufficient_exact_coarse: sp.Matrix
    nonsufficient_nominal_coarse: sp.Matrix
    defect: sp.Matrix
    factorized_defect: sp.Matrix
    factorization_residual: sp.Matrix


def coarsen(v: sp.Matrix, blocks: tuple[tuple[int, ...], ...]) -> sp.Matrix:
    return sp.Matrix([sum(v[i] for i in block) for block in blocks])


def bayes_update(prior: sp.Matrix, likelihood: sp.Matrix) -> sp.Matrix:
    weights = prior.multiply_elementwise(likelihood)
    z = sp.simplify(sum(weights))
    if z == 0:
        raise ValueError("normalizing constant is zero")
    return sp.simplify(weights / z)


def conditional_expectation_matrix(mu: sp.Matrix, blocks: tuple[tuple[int, ...], ...]) -> sp.Matrix:
    n = mu.rows
    E = sp.zeros(n)
    for block in blocks:
        mass = sp.simplify(sum(mu[j] for j in block))
        for i in block:
            for j in block:
                E[i, j] = sp.simplify(mu[j] / mass)
    return E


def effective_likelihood(prior: sp.Matrix, likelihood: sp.Matrix, blocks: tuple[tuple[int, ...], ...]) -> sp.Matrix:
    vals = []
    for block in blocks:
        mass = sp.simplify(sum(prior[i] for i in block))
        numerator = sp.simplify(sum(prior[i] * likelihood[i] for i in block))
        vals.append(sp.simplify(numerator / mass))
    return sp.Matrix(vals)


def matrix_is_zero(M: sp.Matrix) -> bool:
    return all(sp.simplify(v) == 0 for v in M)


@lru_cache(maxsize=None)
def build_certificate() -> BayesCertificate:
    blocks = ((0, 1), (2, 3))
    mu = sp.Matrix([sp.Rational(1, 10), sp.Rational(2, 10), sp.Rational(3, 10), sp.Rational(4, 10)])
    f = sp.Matrix([1, 4, -2, 3])
    E = conditional_expectation_matrix(mu, blocks)
    Ef = sp.simplify(E * f)
    expectation_idempotence_residual = sp.simplify(E * E - E)
    M = sp.diag(*list(mu))
    weighted_adjoint_residual = sp.simplify(M * E - E.T * M)

    prior = mu
    lam_sufficient = sp.Matrix([2, 2, 1, 1])
    fine_post = bayes_update(prior, lam_sufficient)
    coarse_prior = coarsen(prior, blocks)
    coarse_lam = sp.Matrix([2, 1])
    coarse_post = bayes_update(coarse_prior, coarse_lam)
    sufficient_residual = sp.simplify(coarsen(fine_post, blocks) - coarse_post)

    lam = sp.Matrix([1, 3, 2, 4])
    fine_post_ns = bayes_update(prior, lam)
    exact_coarse = coarsen(fine_post_ns, blocks)
    r = effective_likelihood(prior, lam, blocks)
    exact_via_r = bayes_update(coarse_prior, r)
    assert matrix_is_zero(sp.simplify(exact_coarse - exact_via_r))

    nominal_lam = sp.Matrix([2, 3])
    nominal_coarse = bayes_update(coarse_prior, nominal_lam)
    defect = sp.simplify(exact_coarse - nominal_coarse)

    delta = sp.simplify(r - nominal_lam)
    Zr = sp.simplify((coarse_prior.T * r)[0])
    factor_matrix = sp.diag(*list(coarse_prior)) - nominal_coarse * coarse_prior.T
    factorized = sp.simplify(factor_matrix * delta / Zr)
    factorization_residual = sp.simplify(defect - factorized)

    assert matrix_is_zero(expectation_idempotence_residual)
    assert matrix_is_zero(weighted_adjoint_residual)
    assert matrix_is_zero(sufficient_residual)
    assert matrix_is_zero(factorization_residual)
    assert Ef == sp.Matrix([3, 3, sp.Rational(6, 7), sp.Rational(6, 7)])

    return BayesCertificate(
        measure=mu,
        observable=f,
        expectation_matrix=E,
        projected_observable=Ef,
        expectation_idempotence_residual=expectation_idempotence_residual,
        weighted_adjoint_residual=weighted_adjoint_residual,
        sufficient_fine_posterior=fine_post,
        sufficient_coarse_posterior=coarse_post,
        sufficient_residual=sufficient_residual,
        nonsufficient_exact_coarse=exact_coarse,
        nonsufficient_nominal_coarse=nominal_coarse,
        defect=defect,
        factorized_defect=factorized,
        factorization_residual=factorization_residual,
    )
