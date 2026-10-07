from __future__ import annotations

from dataclasses import dataclass
import math
from typing import Iterable

import numpy as np
from scipy import optimize

from kcos import (
    SpectralPassport,
    exact_cgf,
    exact_cgf_derivative,
    exact_saddlepoint,
    passport_cgf,
)


@dataclass(frozen=True)
class AdaptiveCertificate:
    requested_relative_tolerance: float
    analytic_absolute_bound: float
    certified_relative_bound: float
    packet_absolute_bound: float
    support_alias_absolute_bound: float
    cos_series_absolute_bound: float
    theta: float
    interval_upper: float
    K: int
    L: float
    packet_count: int
    exact_count: int
    packet_order: int
    rank: int
    passed: bool
    note: str


@dataclass(frozen=True)
class AdaptiveResult:
    p_value: float
    certificate: AdaptiveCertificate
    passport: SpectralPassport


@dataclass
class _PacketNode:
    start: int
    end: int
    center: float
    moments: np.ndarray
    radius: float
    minimum: float
    maximum: float
    log_cgf_bound_vector: np.ndarray


def _validate_spectrum(eigenvalues: Iterable[float]) -> np.ndarray:
    lam = np.asarray(tuple(eigenvalues), dtype=np.float64)
    if lam.ndim != 1 or lam.size == 0:
        raise ValueError("eigenvalues must be a nonempty one-dimensional sequence")
    if np.any(lam < 0.0):
        raise ValueError("eigenvalues must be nonnegative")
    lam = np.sort(lam)[::-1]
    if lam[0] <= 0.0:
        raise ValueError("at least one eigenvalue must be positive")
    return lam[lam > lam[0] * 1e-14]


def _make_node(
    remainder: np.ndarray,
    start: int,
    end: int,
    order: int,
    s_grid: np.ndarray,
) -> _PacketNode:
    block = remainder[start:end]
    if block.size == 0:
        raise ValueError("empty packet")
    center = float(block.mean())
    delta = block - center

    moments = np.empty(order + 1, dtype=np.float64)
    moments[0] = block.size
    if order >= 1:
        moments[1] = 0.0
    power = delta.copy()
    for n in range(2, order + 1):
        power *= delta
        moments[n] = float(np.sum(power))
    if order == 1:
        pass

    radius = max(
        abs(float(block[0]) - center),
        abs(float(block[-1]) - center),
    )

    denominator = 1.0 - 2.0 * s_grid * center
    alpha = 2.0 * s_grid / denominator
    rho = np.abs(alpha) * radius

    if np.any(rho >= 1.0):
        bound = np.full(s_grid.size, np.inf, dtype=np.float64)
    else:
        bound = (
            0.5
            * block.size
            * rho ** (order + 1)
            / ((order + 1) * (1.0 - rho))
        )

    return _PacketNode(
        start=start,
        end=end,
        center=center,
        moments=moments,
        radius=radius,
        minimum=float(block[-1]),
        maximum=float(block[0]),
        log_cgf_bound_vector=bound,
    )


def _passport_from_nodes(
    eigenvalues: np.ndarray,
    nodes: list[_PacketNode],
    *,
    order: int,
    exact_top: int,
) -> SpectralPassport:
    exact = np.asarray(eigenvalues[:exact_top], dtype=np.float64)

    if nodes:
        centers = np.array([node.center for node in nodes], dtype=np.float64)
        moments = np.stack([node.moments for node in nodes])
        radii = np.array([node.radius for node in nodes], dtype=np.float64)
        minima = np.array([node.minimum for node in nodes], dtype=np.float64)
        maxima = np.array([node.maximum for node in nodes], dtype=np.float64)
    else:
        centers = np.empty(0, dtype=np.float64)
        moments = np.empty((0, order + 1), dtype=np.float64)
        radii = np.empty(0, dtype=np.float64)
        minima = np.empty(0, dtype=np.float64)
        maxima = np.empty(0, dtype=np.float64)

    return SpectralPassport(
        exact=exact,
        centers=centers,
        moments=moments,
        max_abs_delta=radii,
        min_eigenvalue=minima,
        max_eigenvalue=maxima,
        order=order,
        original_rank=int(eigenvalues.size),
    )


def _payoff_integrals(
    q: float,
    theta: float,
    upper: float,
    K: int,
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    u = np.arange(K, dtype=np.float64) * math.pi / upper
    s_grid = theta + 1j * u
    ell = upper - q
    integrals = np.real(
        np.exp(1j * u * q)
        * (1.0 - np.exp((-theta + 1j * u) * ell))
        / (theta - 1j * u)
    )
    weights = np.ones(K, dtype=np.float64)
    weights[0] = 0.5
    return u, s_grid, weights * integrals


def _evaluate_passport_fixed_grid(
    q: float,
    passport: SpectralPassport,
    *,
    theta: float,
    upper: float,
    K: int,
) -> tuple[float, np.ndarray, np.ndarray]:
    _, s_grid, weighted_integrals = _payoff_integrals(q, theta, upper, K)

    # Multiplying the tilted density coefficient by the likelihood-ratio
    # prefactor cancels K(theta).  Computing the combined exponent directly
    # improves both stability and the packet-error derivation.
    combined = np.exp(passport_cgf(s_grid, passport) - theta * q)
    p_value = (
        2.0
        / upper
        * float(np.sum(weighted_integrals * np.real(combined)))
    )
    return p_value, weighted_integrals, s_grid


def exact_tilted_a0_upper_tail(
    q: float,
    eigenvalues: Iterable[float],
    *,
    K: int = 128,
    L: float = 12.0,
) -> tuple[float, dict]:
    lam = _validate_spectrum(eigenvalues)
    theta = exact_saddlepoint(q, lam)
    if theta <= 0.0:
        raise ValueError("q must exceed the mean for the tilted upper-tail path")

    c2 = exact_cgf_derivative(theta, lam, 2)
    c4 = exact_cgf_derivative(theta, lam, 4)
    upper = q + L * math.sqrt(c2 + math.sqrt(c4))
    _, s_grid, weighted_integrals = _payoff_integrals(q, theta, upper, K)
    combined = np.exp(exact_cgf(s_grid, lam) - theta * q)
    p_value = 2.0 / upper * float(
        np.sum(weighted_integrals * np.real(combined))
    )
    return p_value, {
        "theta": theta,
        "upper": upper,
        "K": K,
        "L": L,
    }


def _packet_tail_error_bound(
    total_log_cgf_bound: np.ndarray,
    weighted_integrals: np.ndarray,
    *,
    q: float,
    theta: float,
    upper: float,
    exact_log_mgf_theta: float,
) -> float:
    if np.any(~np.isfinite(total_log_cgf_bound)):
        return math.inf

    log_prefactor = exact_log_mgf_theta - theta * q
    prefactor = math.exp(log_prefactor)

    # |phi_theta| <= 1 and
    # |exp(delta)-1| <= exp(|delta|)-1.
    growth = np.expm1(np.minimum(total_log_cgf_bound, 700.0))
    return float(
        prefactor
        * 2.0
        / upper
        * np.sum(np.abs(weighted_integrals) * growth)
    )


def _tilted_chernoff_bound(
    eigenvalues: np.ndarray,
    *,
    theta: float,
    upper: float,
) -> tuple[float, float]:
    singularity = 1.0 / (2.0 * float(eigenvalues[0]))
    eta_hi = singularity * (1.0 - 1e-12)

    eta = float(
        optimize.brentq(
            lambda value: exact_cgf_derivative(
                value, eigenvalues, 1
            ) - upper,
            theta,
            eta_hi,
            xtol=1e-14,
            rtol=1e-13,
        )
    )

    log_bound = float(
        np.real(
            exact_cgf(eta, eigenvalues)
            - exact_cgf(theta, eigenvalues)
            - (eta - theta) * upper
        )
    )
    return min(1.0, math.exp(log_bound)), eta


def _support_alias_error_bound(
    eigenvalues: np.ndarray,
    *,
    q: float,
    theta: float,
    upper: float,
) -> float:
    tilted_tail, _ = _tilted_chernoff_bound(
        eigenvalues,
        theta=theta,
        upper=upper,
    )
    log_prefactor = float(np.real(exact_cgf(theta, eigenvalues))) - theta * q
    prefactor = math.exp(log_prefactor)

    # The full-CF cosine coefficients reconstruct the even 2b-periodization.
    # On [0,b], its alias mass is the tilted mass above b.  The original
    # omitted tail receives one additional exp(-theta(b-q)) factor.
    return float(
        prefactor
        * tilted_tail
        * (1.0 + math.exp(-theta * (upper - q)))
    )


def _cos_series_error_bound(
    eigenvalues: np.ndarray,
    *,
    q: float,
    theta: float,
    upper: float,
    K: int,
) -> float:
    # For the tilted characteristic function,
    # |phi_theta(t)| = product_j (1 + (a_j t)^2)^(-1/4),
    # a_j = 2 lambda_j / (1 - 2 theta lambda_j).
    #
    # Its logarithmic slope in log(t) is monotone:
    # beta(t) = 1/2 sum_j x_j/(1+x_j), x_j=(a_j t)^2.
    # Hence for t >= t0,
    # |phi(t)| <= |phi(t0)| (t/t0)^(-beta(t0)).
    h = math.pi / upper
    t0 = K * h

    a = 2.0 * eigenvalues / (1.0 - 2.0 * theta * eigenvalues)
    x = (a * t0) ** 2
    log_phi0 = float(-0.25 * np.sum(np.log1p(x)))
    beta = float(0.5 * np.sum(x / (1.0 + x)))

    if beta <= 0.0:
        return math.inf

    log_prefactor = float(np.real(exact_cgf(theta, eigenvalues))) - theta * q
    # |payoff Fourier integral| <= 2/u_k.  Summing the p-series envelope
    # gives K^beta * sum_{k>=K} k^(-beta-1) <= 1/K + 1/beta.
    log_bound = (
        log_prefactor
        + math.log(4.0 / math.pi)
        + log_phi0
        + math.log(1.0 / K + 1.0 / beta)
    )
    if log_bound < -745.0:
        return 0.0
    return float(math.exp(log_bound))


def _compile_packet_passport(
    eigenvalues: np.ndarray,
    q: float,
    *,
    theta: float,
    upper: float,
    K: int,
    order: int,
    exact_top: int,
    packet_relative_target: float,
    max_packets: int,
) -> tuple[SpectralPassport, float, float, int]:
    exact_top = min(max(int(exact_top), 0), eigenvalues.size)
    remainder = np.asarray(eigenvalues[exact_top:], dtype=np.float64)

    _, s_grid, weighted_integrals = _payoff_integrals(q, theta, upper, K)
    exact_log_mgf_theta = float(np.real(exact_cgf(theta, eigenvalues)))

    if remainder.size == 0:
        passport = _passport_from_nodes(
            eigenvalues, [], order=order, exact_top=exact_top
        )
        return passport, 0.0, 0.0, 0

    nodes = [_make_node(remainder, 0, remainder.size, order, s_grid)]

    # First obtain a convergent centered expansion without repeatedly
    # evaluating the tail probability.
    while any(
        not np.all(np.isfinite(node.log_cgf_bound_vector))
        for node in nodes
    ):
        if len(nodes) >= max_packets:
            raise RuntimeError("max_packets reached before packet convergence")
        index = next(
            i
            for i, node in enumerate(nodes)
            if not np.all(np.isfinite(node.log_cgf_bound_vector))
        )
        parent = nodes.pop(index)
        if parent.end - parent.start <= 1:
            raise RuntimeError("nonconvergent singleton packet")
        middle = (parent.start + parent.end) // 2
        nodes.extend(
            [
                _make_node(
                    remainder, parent.start, middle, order, s_grid
                ),
                _make_node(
                    remainder, middle, parent.end, order, s_grid
                ),
            ]
        )

    total_bound = np.sum(
        np.vstack([node.log_cgf_bound_vector for node in nodes]),
        axis=0,
    )

    # One coarse p estimate converts the requested relative budget into an
    # absolute packet budget.  Splitting then proceeds without rescanning or
    # repeatedly recomputing p.
    passport = _passport_from_nodes(
        eigenvalues, nodes, order=order, exact_top=exact_top
    )
    p_hat, _, _ = _evaluate_passport_fixed_grid(
        q, passport, theta=theta, upper=upper, K=K
    )
    target_abs = (
        packet_relative_target
        / (1.0 + packet_relative_target)
        * abs(p_hat)
    )
    packet_bound = _packet_tail_error_bound(
        total_bound,
        weighted_integrals,
        q=q,
        theta=theta,
        upper=upper,
        exact_log_mgf_theta=exact_log_mgf_theta,
    )

    while packet_bound > target_abs:
        if len(nodes) >= max_packets:
            raise RuntimeError("max_packets reached before packet tolerance")
        index = int(
            np.argmax(
                [
                    float(np.max(node.log_cgf_bound_vector))
                    for node in nodes
                ]
            )
        )
        parent = nodes.pop(index)
        if parent.end - parent.start <= 1:
            raise RuntimeError("cannot refine singleton packet")
        middle = (parent.start + parent.end) // 2
        left = _make_node(
            remainder, parent.start, middle, order, s_grid
        )
        right = _make_node(
            remainder, middle, parent.end, order, s_grid
        )
        nodes.extend([left, right])

        total_bound = (
            total_bound
            - parent.log_cgf_bound_vector
            + left.log_cgf_bound_vector
            + right.log_cgf_bound_vector
        )
        packet_bound = _packet_tail_error_bound(
            total_bound,
            weighted_integrals,
            q=q,
            theta=theta,
            upper=upper,
            exact_log_mgf_theta=exact_log_mgf_theta,
        )

    # Rebuild and verify once at the end.
    passport = _passport_from_nodes(
        eigenvalues, nodes, order=order, exact_top=exact_top
    )
    p_hat, _, _ = _evaluate_passport_fixed_grid(
        q, passport, theta=theta, upper=upper, K=K
    )
    denominator = abs(p_hat) - packet_bound
    packet_relative_bound = (
        packet_bound / denominator if denominator > 0.0 else math.inf
    )

    # If the coarse estimate shifted enough to invalidate the requested
    # packet-relative certificate, refine against the corrected target.
    if packet_relative_bound > packet_relative_target:
        target_abs = (
            packet_relative_target
            / (1.0 + packet_relative_target)
            * abs(p_hat)
        )
        while packet_bound > target_abs:
            if len(nodes) >= max_packets:
                raise RuntimeError(
                    "max_packets reached during packet re-verification"
                )
            index = int(
                np.argmax(
                    [
                        float(np.max(node.log_cgf_bound_vector))
                        for node in nodes
                    ]
                )
            )
            parent = nodes.pop(index)
            middle = (parent.start + parent.end) // 2
            left = _make_node(
                remainder, parent.start, middle, order, s_grid
            )
            right = _make_node(
                remainder, middle, parent.end, order, s_grid
            )
            nodes.extend([left, right])
            total_bound = (
                total_bound
                - parent.log_cgf_bound_vector
                + left.log_cgf_bound_vector
                + right.log_cgf_bound_vector
            )
            packet_bound = _packet_tail_error_bound(
                total_bound,
                weighted_integrals,
                q=q,
                theta=theta,
                upper=upper,
                exact_log_mgf_theta=exact_log_mgf_theta,
            )

        passport = _passport_from_nodes(
            eigenvalues, nodes, order=order, exact_top=exact_top
        )
        p_hat, _, _ = _evaluate_passport_fixed_grid(
            q, passport, theta=theta, upper=upper, K=K
        )
        denominator = abs(p_hat) - packet_bound
        packet_relative_bound = (
            packet_bound / denominator if denominator > 0.0 else math.inf
        )

    return (
        passport,
        float(packet_bound),
        float(packet_relative_bound),
        len(nodes),
    )


def adaptive_kcos_upper_tail(
    q: float,
    eigenvalues: Iterable[float],
    *,
    relative_tolerance: float = 1e-8,
    K_initial: int = 64,
    L_initial: float = 10.0,
    packet_order: int = 8,
    exact_top: int = 8,
    max_packets: int = 256,
    max_outer_refinements: int = 20,
) -> AdaptiveResult:
    """Tolerance-driven K-COS upper-tail evaluation for positive mixtures.

    The analytic certificate covers:
      1. centered spectral-packet truncation,
      2. upper-support truncation plus cosine periodization aliasing,
      3. omitted COS modes.

    It does not constitute a directed-rounding floating-point proof for
    libm/NumPy transcendental operations.
    """
    if not (relative_tolerance > 0.0):
        raise ValueError("relative_tolerance must be positive")
    if K_initial < 2:
        raise ValueError("K_initial must be at least two")
    if L_initial <= 0.0:
        raise ValueError("L_initial must be positive")

    lam = _validate_spectrum(eigenvalues)
    theta = exact_saddlepoint(q, lam)
    if theta <= 0.0:
        raise ValueError(
            "adaptive upper-tail path currently expects q above the mean"
        )

    c2 = exact_cgf_derivative(theta, lam, 2)
    c4 = exact_cgf_derivative(theta, lam, 4)
    scale = math.sqrt(c2 + math.sqrt(c4))

    K = int(K_initial)
    L = float(L_initial)
    order = int(packet_order)
    packet_target = relative_tolerance / 4.0

    last = None

    for _ in range(int(max_outer_refinements)):
        upper = q + L * scale

        passport, packet_bound, _, packet_count = _compile_packet_passport(
            lam,
            q,
            theta=theta,
            upper=upper,
            K=K,
            order=order,
            exact_top=exact_top,
            packet_relative_target=packet_target,
            max_packets=max_packets,
        )
        p_hat, _, _ = _evaluate_passport_fixed_grid(
            q,
            passport,
            theta=theta,
            upper=upper,
            K=K,
        )

        support_bound = _support_alias_error_bound(
            lam,
            q=q,
            theta=theta,
            upper=upper,
        )
        series_bound = _cos_series_error_bound(
            lam,
            q=q,
            theta=theta,
            upper=upper,
            K=K,
        )

        total_bound = packet_bound + support_bound + series_bound
        denominator = abs(p_hat) - total_bound
        relative_bound = (
            total_bound / denominator if denominator > 0.0 else math.inf
        )

        last = (
            p_hat,
            passport,
            packet_bound,
            support_bound,
            series_bound,
            total_bound,
            relative_bound,
            packet_count,
            upper,
            K,
            L,
            order,
        )

        if relative_bound <= relative_tolerance:
            certificate = AdaptiveCertificate(
                requested_relative_tolerance=float(relative_tolerance),
                analytic_absolute_bound=float(total_bound),
                certified_relative_bound=float(relative_bound),
                packet_absolute_bound=float(packet_bound),
                support_alias_absolute_bound=float(support_bound),
                cos_series_absolute_bound=float(series_bound),
                theta=float(theta),
                interval_upper=float(upper),
                K=int(K),
                L=float(L),
                packet_count=int(packet_count),
                exact_count=min(int(exact_top), int(lam.size)),
                packet_order=int(order),
                rank=int(lam.size),
                passed=True,
                note=(
                    "Analytic compression/truncation certificate; "
                    "floating-point transcendental roundoff is not "
                    "directed-rounding certified."
                ),
            )
            return AdaptiveResult(
                p_value=float(p_hat),
                certificate=certificate,
                passport=passport,
            )

        # Refine the dominant analytic error source.
        if support_bound >= max(packet_bound, series_bound):
            L += 1.0
        elif series_bound >= max(packet_bound, support_bound):
            K *= 2
        else:
            packet_target *= 0.25
            if packet_target < relative_tolerance * 1e-6:
                order += 2
                packet_target = relative_tolerance / 16.0

    if last is None:
        raise RuntimeError("adaptive refinement did not execute")

    (
        p_hat,
        passport,
        packet_bound,
        support_bound,
        series_bound,
        total_bound,
        relative_bound,
        packet_count,
        upper,
        K,
        L,
        order,
    ) = last

    certificate = AdaptiveCertificate(
        requested_relative_tolerance=float(relative_tolerance),
        analytic_absolute_bound=float(total_bound),
        certified_relative_bound=float(relative_bound),
        packet_absolute_bound=float(packet_bound),
        support_alias_absolute_bound=float(support_bound),
        cos_series_absolute_bound=float(series_bound),
        theta=float(theta),
        interval_upper=float(upper),
        K=int(K),
        L=float(L),
        packet_count=int(packet_count),
        exact_count=min(int(exact_top), int(lam.size)),
        packet_order=int(order),
        rank=int(lam.size),
        passed=False,
        note=(
            "Requested analytic tolerance was not reached before the "
            "refinement limit; floating-point roundoff is also excluded."
        ),
    )
    return AdaptiveResult(
        p_value=float(p_hat),
        certificate=certificate,
        passport=passport,
    )
