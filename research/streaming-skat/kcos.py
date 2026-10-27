from __future__ import annotations

from dataclasses import dataclass
import math
from typing import Iterable

import numpy as np
from scipy import optimize


@dataclass(frozen=True)
class SpectralPassport:
    exact: np.ndarray
    centers: np.ndarray
    moments: np.ndarray
    max_abs_delta: np.ndarray
    min_eigenvalue: np.ndarray
    max_eigenvalue: np.ndarray
    order: int
    original_rank: int

    @property
    def packet_count(self) -> int:
        return int(self.centers.size)

    @property
    def exact_count(self) -> int:
        return int(self.exact.size)

    @property
    def lambda_max(self) -> float:
        vals = []
        if self.exact.size:
            vals.append(float(self.exact.max()))
        if self.max_eigenvalue.size:
            vals.append(float(self.max_eigenvalue.max()))
        return max(vals, default=0.0)


def compile_centered_passport(
    eigenvalues: Iterable[float],
    *,
    order: int = 8,
    packet_count: int = 32,
    exact_top: int = 8,
    relative_floor: float = 1e-14,
) -> SpectralPassport:
    lam = np.asarray(tuple(eigenvalues), dtype=np.float64)
    if lam.ndim != 1 or lam.size == 0:
        raise ValueError("eigenvalues must be nonempty and one-dimensional")
    if np.any(lam < 0.0):
        raise ValueError("eigenvalues must be nonnegative")
    lam = np.sort(lam)[::-1]
    if lam[0] <= 0.0:
        raise ValueError("at least one eigenvalue must be positive")
    lam = lam[lam > lam[0] * relative_floor]

    order = int(order)
    packet_count = int(packet_count)
    exact_top = min(max(int(exact_top), 0), lam.size)
    if order < 1 or packet_count < 1:
        raise ValueError("order and packet_count must be positive")

    exact = lam[:exact_top].copy()
    rest = lam[exact_top:]
    rows = []

    if rest.size:
        for block in np.array_split(rest, min(packet_count, rest.size)):
            if block.size == 0:
                continue
            mu = float(block.mean())
            delta = block - mu
            moments = np.empty(order + 1, dtype=np.float64)
            moments[0] = block.size
            for n in range(1, order + 1):
                moments[n] = np.sum(delta ** n)
            rows.append(
                (
                    mu,
                    moments,
                    float(np.max(np.abs(delta))),
                    float(block.min()),
                    float(block.max()),
                )
            )

    if rows:
        centers = np.array([x[0] for x in rows], dtype=np.float64)
        moments = np.stack([x[1] for x in rows])
        max_abs_delta = np.array([x[2] for x in rows], dtype=np.float64)
        min_eigenvalue = np.array([x[3] for x in rows], dtype=np.float64)
        max_eigenvalue = np.array([x[4] for x in rows], dtype=np.float64)
    else:
        centers = np.empty(0, dtype=np.float64)
        moments = np.empty((0, order + 1), dtype=np.float64)
        max_abs_delta = np.empty(0, dtype=np.float64)
        min_eigenvalue = np.empty(0, dtype=np.float64)
        max_eigenvalue = np.empty(0, dtype=np.float64)

    return SpectralPassport(
        exact=exact,
        centers=centers,
        moments=moments,
        max_abs_delta=max_abs_delta,
        min_eigenvalue=min_eigenvalue,
        max_eigenvalue=max_eigenvalue,
        order=order,
        original_rank=int(lam.size),
    )


def exact_cgf(s, eigenvalues):
    lam = np.asarray(eigenvalues, dtype=np.float64)
    values = np.atleast_1d(np.asarray(s, dtype=np.complex128))
    out = -0.5 * np.sum(
        np.log(1.0 - 2.0 * values[:, None] * lam[None, :]),
        axis=1,
    )
    return out if np.ndim(s) else out[0]


def passport_cgf(s, passport: SpectralPassport):
    values = np.atleast_1d(np.asarray(s, dtype=np.complex128))
    out = np.zeros(values.shape, dtype=np.complex128)

    if passport.exact.size:
        out += -0.5 * np.sum(
            np.log(1.0 - 2.0 * values[:, None] * passport.exact[None, :]),
            axis=1,
        )

    if passport.centers.size:
        d = 1.0 - 2.0 * values[:, None] * passport.centers[None, :]
        alpha = 2.0 * values[:, None] / d
        out += np.sum(
            -0.5 * passport.moments[:, 0][None, :] * np.log(d),
            axis=1,
        )
        for n in range(1, passport.order + 1):
            out += np.sum(
                0.5 * alpha**n * passport.moments[:, n][None, :] / n,
                axis=1,
            )

    return out if np.ndim(s) else out[0]


def packet_log_cgf_remainder_bound(s, passport: SpectralPassport):
    values = np.atleast_1d(np.asarray(s, dtype=np.complex128))
    if not passport.centers.size:
        return np.zeros(values.size, dtype=np.float64)

    d = 1.0 - 2.0 * values[:, None] * passport.centers[None, :]
    alpha = 2.0 * values[:, None] / d
    rho = np.abs(alpha) * passport.max_abs_delta[None, :]
    p = passport.order
    denom = np.maximum(1.0 - rho, np.finfo(float).tiny)

    terms = (
        0.5
        * passport.moments[:, 0][None, :]
        * rho ** (p + 1)
        / ((p + 1) * denom)
    )
    bound = np.sum(terms, axis=1)
    bound[np.any(rho >= 1.0, axis=1)] = np.inf
    return bound


def exact_cgf_derivative(theta, eigenvalues, order):
    lam = np.asarray(eigenvalues, dtype=np.float64)
    r = int(order)
    prefactor = (2 ** (r - 1)) * math.factorial(r - 1)
    return float(
        prefactor
        * np.sum(lam**r / (1.0 - 2.0 * theta * lam) ** r)
    )


def passport_cgf_derivative(theta, passport: SpectralPassport, order):
    r = int(order)
    if r < 1:
        raise ValueError("order must be at least one")
    prefactor = (2 ** (r - 1)) * math.factorial(r - 1)
    total = 0.0

    if passport.exact.size:
        total += prefactor * np.sum(
            passport.exact**r
            / (1.0 - 2.0 * theta * passport.exact) ** r
        )

    if passport.centers.size:
        mu = passport.centers
        d = 1.0 - 2.0 * theta * mu
        alpha = 2.0 * theta / d
        expansion = np.zeros_like(mu)

        for n in range(passport.order + 1):
            coefficient = np.zeros_like(mu)
            for j in range(0, min(r, n) + 1):
                k = n - j
                coefficient += (
                    math.comb(r, j)
                    * mu ** (r - j)
                    * math.comb(r + k - 1, k)
                    * alpha**k
                )
            expansion += coefficient * passport.moments[:, n]

        total += prefactor * np.sum(expansion / d**r)

    return float(total)


def exact_saddlepoint(q, eigenvalues):
    lam = np.asarray(eigenvalues, dtype=np.float64)
    mean = exact_cgf_derivative(0.0, lam, 1)
    if q <= mean:
        return 0.0
    upper = (1.0 / (2.0 * float(lam.max()))) * (1.0 - 1e-12)
    return float(
        optimize.brentq(
            lambda t: exact_cgf_derivative(t, lam, 1) - q,
            0.0,
            upper,
            xtol=1e-14,
            rtol=1e-13,
        )
    )


def passport_saddlepoint(q, passport: SpectralPassport):
    mean = passport_cgf_derivative(0.0, passport, 1)
    if q <= mean:
        return 0.0
    upper = (1.0 / (2.0 * passport.lambda_max)) * (1.0 - 1e-10)
    return float(
        optimize.brentq(
            lambda t: passport_cgf_derivative(t, passport, 1) - q,
            0.0,
            upper,
            xtol=1e-13,
            rtol=1e-12,
        )
    )


def standard_cos_upper_tail(q, eigenvalues, *, K=256, L=12.0):
    """Legacy-style global COS CDF followed by 1-F(q)."""
    lam = np.asarray(eigenvalues, dtype=np.float64)
    c1 = exact_cgf_derivative(0.0, lam, 1)
    c2 = exact_cgf_derivative(0.0, lam, 2)
    c4 = exact_cgf_derivative(0.0, lam, 4)
    width = L * math.sqrt(c2 + math.sqrt(c4))
    a = max(0.0, c1 - width)
    b = c1 + width

    u = np.arange(K, dtype=np.float64) * math.pi / (b - a)
    phi = np.exp(exact_cgf(1j * u, lam))
    coeff = 2.0 / (b - a) * np.real(phi * np.exp(-1j * u * a))
    coeff[0] *= 0.5

    integ = np.empty_like(u)
    integ[0] = q - a
    integ[1:] = np.sin(u[1:] * (q - a)) / u[1:]
    return float(1.0 - np.sum(coeff * integ))


def tilted_cos_upper_tail_exact(q, eigenvalues, *, K=128, L=12.0):
    lam = np.asarray(eigenvalues, dtype=np.float64)
    theta = exact_saddlepoint(q, lam)
    if theta <= 0.0:
        raise ValueError("q must exceed the mean for this tilted path")

    c2 = exact_cgf_derivative(theta, lam, 2)
    c4 = exact_cgf_derivative(theta, lam, 4)
    width = L * math.sqrt(c2 + math.sqrt(c4))
    a = max(0.0, q - width)
    b = q + width

    u = np.arange(K, dtype=np.float64) * math.pi / (b - a)
    log_m = exact_cgf(theta, lam)
    phi = np.exp(exact_cgf(theta + 1j * u, lam) - log_m)

    coeff = 2.0 / (b - a) * np.real(phi * np.exp(-1j * u * a))
    coeff[0] *= 0.5

    ell = b - q
    payoff_integral = np.real(
        np.exp(1j * u * (q - a))
        * (1.0 - np.exp((-theta + 1j * u) * ell))
        / (theta - 1j * u)
    )
    tail = (
        math.exp(float(np.real(log_m)) - theta * q)
        * float(np.sum(coeff * payoff_integral))
    )
    return float(tail), {"theta": float(theta), "a": float(a), "b": float(b)}


def tilted_cos_upper_tail_passport(q, passport: SpectralPassport, *, K=128, L=12.0):
    theta = passport_saddlepoint(q, passport)
    if theta <= 0.0:
        raise ValueError("q must exceed the mean for this tilted path")

    c2 = passport_cgf_derivative(theta, passport, 2)
    c4 = passport_cgf_derivative(theta, passport, 4)
    width = L * math.sqrt(c2 + math.sqrt(max(c4, 0.0)))
    a = max(0.0, q - width)
    b = q + width

    u = np.arange(K, dtype=np.float64) * math.pi / (b - a)
    s_grid = theta + 1j * u
    log_m = passport_cgf(theta, passport)
    phi = np.exp(passport_cgf(s_grid, passport) - log_m)

    coeff = 2.0 / (b - a) * np.real(phi * np.exp(-1j * u * a))
    coeff[0] *= 0.5

    ell = b - q
    payoff_integral = np.real(
        np.exp(1j * u * (q - a))
        * (1.0 - np.exp((-theta + 1j * u) * ell))
        / (theta - 1j * u)
    )
    tail = (
        math.exp(float(np.real(log_m)) - theta * q)
        * float(np.sum(coeff * payoff_integral))
    )

    remainder = packet_log_cgf_remainder_bound(s_grid, passport)
    if passport.centers.size:
        d = 1.0 - 2.0 * s_grid[:, None] * passport.centers[None, :]
        rho = (
            np.abs(2.0 * s_grid[:, None] / d)
            * passport.max_abs_delta[None, :]
        )
        max_rho = float(np.max(rho))
    else:
        max_rho = 0.0

    return float(tail), {
        "theta": float(theta),
        "a": float(a),
        "b": float(b),
        "max_packet_rho": max_rho,
        "max_log_cgf_remainder_bound": float(np.max(remainder)),
        "packet_count": passport.packet_count,
        "exact_count": passport.exact_count,
        "original_rank": passport.original_rank,
    }
