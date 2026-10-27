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
class LogAdaptiveCertificate:
    requested_relative_tolerance: float
    certified_relative_bound: float
    packet_tilted_bound: float
    support_alias_tilted_bound: float
    cos_series_tilted_bound: float
    tilted_sum: float
    log_prefactor: float
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
class LogAdaptiveResult:
    log_p: float
    log10_p: float
    p_value: float
    certificate: LogAdaptiveCertificate
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

    @property
    def splittable(self) -> bool:
        return self.end - self.start > 1


def _validate_spectrum(eigenvalues: Iterable[float]) -> np.ndarray:
    lam = np.asarray(tuple(eigenvalues), dtype=np.float64)
    if lam.ndim != 1 or lam.size == 0:
        raise ValueError("eigenvalues must be a nonempty one-dimensional sequence")
    if np.any(lam < 0.0):
        raise ValueError("this certified implementation requires nonnegative eigenvalues")
    lam = np.sort(lam)[::-1]
    if lam[0] <= 0.0:
        raise ValueError("at least one eigenvalue must be positive")
    return lam[lam > lam[0] * 1e-14]


def spectral_metrics(eigenvalues: Iterable[float]) -> dict:
    lam = _validate_spectrum(eigenvalues)
    trace = float(np.sum(lam))
    sq = float(np.sum(lam * lam))
    effective_rank = trace * trace / sq
    top_share = float(lam[0] / trace)
    if lam.size > 1:
        ratios = lam[:-1] / np.maximum(lam[1:], np.finfo(float).tiny)
        max_gap_ratio = float(np.max(ratios))
        max_gap_index = int(np.argmax(ratios) + 1)
    else:
        max_gap_ratio = math.inf
        max_gap_index = 1
    return {
        "rank": int(lam.size),
        "trace": trace,
        "effective_rank": effective_rank,
        "top_trace_share": top_share,
        "max_gap_ratio": max_gap_ratio,
        "max_gap_index": max_gap_index,
        "condition_number": float(lam[0] / lam[-1]),
    }


def _make_node(remainder, start, end, order, s_grid):
    block = remainder[start:end]
    if block.size == 0:
        raise ValueError("empty packet")
    center = float(block.mean())
    delta = block - center
    moments = np.empty(order + 1, dtype=np.float64)
    moments[0] = block.size
    if order >= 1:
        moments[1] = 0.0
    if order >= 2:
        power = delta.copy()
        for n in range(2, order + 1):
            power *= delta
            moments[n] = float(np.sum(power))
    radius = max(abs(float(block[0]) - center), abs(float(block[-1]) - center))
    denominator = 1.0 - 2.0 * s_grid * center
    alpha = 2.0 * s_grid / denominator
    rho = np.abs(alpha) * radius
    if np.any(rho >= 1.0):
        bound = np.full(s_grid.size, np.inf, dtype=np.float64)
    else:
        bound = 0.5 * block.size * rho ** (order + 1) / ((order + 1) * (1.0 - rho))
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


def _passport_from_nodes(eigenvalues, nodes, *, order, exact_top):
    exact = np.asarray(eigenvalues[:exact_top], dtype=np.float64)
    if nodes:
        centers = np.array([x.center for x in nodes], dtype=np.float64)
        moments = np.stack([x.moments for x in nodes])
        radii = np.array([x.radius for x in nodes], dtype=np.float64)
        minima = np.array([x.minimum for x in nodes], dtype=np.float64)
        maxima = np.array([x.maximum for x in nodes], dtype=np.float64)
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


def _initial_nodes(remainder, order, s_grid, *, gap_ratio=3.0, max_clusters=16):
    n = remainder.size
    if n == 0:
        return []
    if n == 1:
        return [_make_node(remainder, 0, 1, order, s_grid)]
    ratios = remainder[:-1] / np.maximum(remainder[1:], np.finfo(float).tiny)
    candidates = np.flatnonzero(ratios >= gap_ratio) + 1
    if candidates.size > max_clusters - 1:
        score = ratios[candidates - 1]
        keep = np.argsort(score)[-(max_clusters - 1):]
        candidates = np.sort(candidates[keep])
    bounds = [0] + [int(x) for x in candidates] + [n]
    return [
        _make_node(remainder, a, b, order, s_grid)
        for a, b in zip(bounds[:-1], bounds[1:]) if b > a
    ]


def _payoff_integrals(q, theta, upper, K):
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


def _tilted_sum(q, passport, *, theta, upper, K, exact_log_mgf_theta):
    _, s_grid, weighted_integrals = _payoff_integrals(q, theta, upper, K)
    # The full-spectrum scalar K(theta) is cheap and exact (for the supplied spectrum).
    phi_hat = np.exp(passport_cgf(s_grid, passport) - exact_log_mgf_theta)
    terms = weighted_integrals * np.real(phi_hat)
    s = (2.0 / upper) * math.fsum(float(x) for x in terms)
    return float(s), weighted_integrals, s_grid


def _packet_tilted_error_bound(total_bound, weighted_integrals, upper):
    if np.any(~np.isfinite(total_bound)):
        return math.inf
    growth = np.expm1(np.minimum(total_bound, 700.0))
    return float((2.0 / upper) * np.sum(np.abs(weighted_integrals) * growth))


def _tilted_chernoff_bound(eigenvalues, *, theta, upper):
    singularity = 1.0 / (2.0 * float(eigenvalues[0]))
    eta_hi = singularity * (1.0 - 1e-12)
    eta = float(optimize.brentq(
        lambda value: exact_cgf_derivative(value, eigenvalues, 1) - upper,
        theta, eta_hi, xtol=1e-14, rtol=1e-13,
    ))
    log_bound = float(np.real(
        exact_cgf(eta, eigenvalues)
        - exact_cgf(theta, eigenvalues)
        - (eta - theta) * upper
    ))
    return min(1.0, math.exp(log_bound)), eta


def _support_alias_tilted_bound(eigenvalues, *, q, theta, upper):
    tail, _ = _tilted_chernoff_bound(eigenvalues, theta=theta, upper=upper)
    return float(tail * (1.0 + math.exp(-theta * (upper - q))))


def _cos_series_tilted_bound(eigenvalues, *, theta, upper, K):
    h = math.pi / upper
    t0 = K * h
    a = 2.0 * eigenvalues / (1.0 - 2.0 * theta * eigenvalues)
    x = (a * t0) ** 2
    log_phi0 = float(-0.25 * np.sum(np.log1p(x)))
    beta = float(0.5 * np.sum(x / (1.0 + x)))
    if beta <= 0.0:
        return math.inf
    log_bound = (
        math.log(4.0 / math.pi)
        + log_phi0
        + math.log(1.0 / K + 1.0 / beta)
    )
    return 0.0 if log_bound < -745.0 else float(math.exp(log_bound))


def _total_bound(nodes):
    return np.sum(np.vstack([n.log_cgf_bound_vector for n in nodes]), axis=0)


def _choose_split(nodes):
    candidates = [(i, float(np.max(n.log_cgf_bound_vector)))
                  for i, n in enumerate(nodes) if n.splittable]
    if not candidates:
        return None
    return max(candidates, key=lambda x: x[1])[0]


def _split_node(nodes, index, remainder, order, s_grid):
    parent = nodes.pop(index)
    middle = (parent.start + parent.end) // 2
    nodes.extend([
        _make_node(remainder, parent.start, middle, order, s_grid),
        _make_node(remainder, middle, parent.end, order, s_grid),
    ])


def _compile_passport_logsafe(
    eigenvalues, q, *, theta, upper, K, order, exact_top,
    packet_relative_target, max_packets=None, gap_ratio=3.0,
):
    exact_top = min(max(int(exact_top), 0), eigenvalues.size)
    remainder = np.asarray(eigenvalues[exact_top:], dtype=np.float64)
    max_packets = remainder.size if max_packets is None else min(int(max_packets), remainder.size)
    _, s_grid, weighted_integrals = _payoff_integrals(q, theta, upper, K)
    exact_log_mgf_theta = float(np.real(exact_cgf(theta, eigenvalues)))

    if remainder.size == 0:
        passport = _passport_from_nodes(eigenvalues, [], order=order, exact_top=exact_top)
        s, _, _ = _tilted_sum(q, passport, theta=theta, upper=upper, K=K,
                              exact_log_mgf_theta=exact_log_mgf_theta)
        return passport, 0.0, 0.0, s, 0

    nodes = _initial_nodes(remainder, order, s_grid, gap_ratio=gap_ratio)

    # Make every packet expansion convergent first.
    while any(np.any(~np.isfinite(n.log_cgf_bound_vector)) for n in nodes):
        bad = [(i, float(np.max(n.log_cgf_bound_vector))) for i, n in enumerate(nodes)
               if n.splittable and np.any(~np.isfinite(n.log_cgf_bound_vector))]
        if not bad:
            raise RuntimeError("non-finite packet bound remains with no splittable packet")
        if len(nodes) >= max_packets:
            raise RuntimeError("packet cap reached before centered expansion converged")
        _split_node(nodes, max(bad, key=lambda x: x[1])[0], remainder, order, s_grid)

    passport = _passport_from_nodes(eigenvalues, nodes, order=order, exact_top=exact_top)
    s_hat, _, _ = _tilted_sum(q, passport, theta=theta, upper=upper, K=K,
                              exact_log_mgf_theta=exact_log_mgf_theta)
    if not np.isfinite(s_hat) or s_hat <= 0.0:
        return passport, math.inf, math.inf, s_hat, len(nodes)

    target = packet_relative_target / (1.0 + packet_relative_target) * s_hat
    tb = _total_bound(nodes)
    packet_bound = _packet_tilted_error_bound(tb, weighted_integrals, upper)

    while packet_bound > target:
        idx = _choose_split(nodes)
        if idx is None:
            # All packets are singletons, hence exact.  Recompute to remove
            # subtraction/accumulation residue rather than crashing.
            tb = _total_bound(nodes)
            packet_bound = _packet_tilted_error_bound(tb, weighted_integrals, upper)
            break
        if len(nodes) >= max_packets:
            raise RuntimeError("packet cap reached before requested packet tolerance")
        _split_node(nodes, idx, remainder, order, s_grid)
        tb = _total_bound(nodes)
        packet_bound = _packet_tilted_error_bound(tb, weighted_integrals, upper)

    passport = _passport_from_nodes(eigenvalues, nodes, order=order, exact_top=exact_top)
    s_hat, _, _ = _tilted_sum(q, passport, theta=theta, upper=upper, K=K,
                              exact_log_mgf_theta=exact_log_mgf_theta)
    denom = s_hat - packet_bound
    rel = packet_bound / denom if denom > 0 else math.inf
    return passport, float(packet_bound), float(rel), float(s_hat), len(nodes)


def adaptive_kcos_logsf(
    q: float,
    eigenvalues: Iterable[float],
    *,
    relative_tolerance: float = 1e-8,
    K_initial: int = 64,
    L_initial: float = 10.0,
    packet_order: int = 8,
    exact_top: int = 8,
    max_packets: int | None = None,
    max_outer_refinements: int = 24,
    max_K: int = 262144,
    gap_ratio: float = 3.0,
) -> LogAdaptiveResult:
    if relative_tolerance <= 0:
        raise ValueError("relative_tolerance must be positive")
    lam = _validate_spectrum(eigenvalues)
    theta = exact_saddlepoint(q, lam)
    if theta <= 0:
        raise ValueError("upper-tail tilted path requires q above the mean")

    exact_log_mgf_theta = float(np.real(exact_cgf(theta, lam)))
    log_prefactor = exact_log_mgf_theta - theta * q
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
        try:
            passport, pbound, _, s_hat, packet_count = _compile_passport_logsafe(
                lam, q, theta=theta, upper=upper, K=K, order=order,
                exact_top=exact_top, packet_relative_target=packet_target,
                max_packets=max_packets, gap_ratio=gap_ratio,
            )
        except RuntimeError:
            # Tighten polynomial order before surrendering compression.
            order += 2
            if order > 16:
                raise
            continue

        support = _support_alias_tilted_bound(lam, q=q, theta=theta, upper=upper)
        series = _cos_series_tilted_bound(lam, theta=theta, upper=upper, K=K)
        total = pbound + support + series
        denom = s_hat - total
        rel = total / denom if denom > 0 else math.inf
        last = (passport, pbound, support, series, total, rel, s_hat, packet_count, upper, K, L, order)

        if rel <= relative_tolerance and s_hat > 0:
            log_p = log_prefactor + math.log(s_hat)
            p_value = math.exp(log_p) if log_p > math.log(np.nextafter(0.0, 1.0)) else 0.0
            cert = LogAdaptiveCertificate(
                requested_relative_tolerance=float(relative_tolerance),
                certified_relative_bound=float(rel),
                packet_tilted_bound=float(pbound),
                support_alias_tilted_bound=float(support),
                cos_series_tilted_bound=float(series),
                tilted_sum=float(s_hat),
                log_prefactor=float(log_prefactor),
                theta=float(theta), interval_upper=float(upper),
                K=int(K), L=float(L), packet_count=int(packet_count),
                exact_count=min(int(exact_top), int(lam.size)),
                packet_order=int(order), rank=int(lam.size), passed=True,
                note=("Relative certificate is evaluated in the exponentially tilted measure, "
                      "so it remains finite below float64 probability underflow. "
                      "Directed-rounding machine-error enclosure is still not included."),
            )
            return LogAdaptiveResult(log_p=float(log_p), log10_p=float(log_p / math.log(10.0)),
                                     p_value=float(p_value), certificate=cert, passport=passport)

        dominant = max((pbound, "packet"), (support, "support"), (series, "series"))[1]
        if dominant == "support":
            L += 1.0
        elif dominant == "series":
            if K >= max_K:
                break
            K = min(max_K, K * 2)
        else:
            packet_target *= 0.25
            if packet_target < relative_tolerance * 1e-7:
                order += 2
                packet_target = relative_tolerance / 16.0

    if last is None:
        raise RuntimeError("adaptive refinement did not execute")
    passport, pbound, support, series, total, rel, s_hat, packet_count, upper, K, L, order = last
    log_p = log_prefactor + math.log(s_hat) if s_hat > 0 else -math.inf
    p_value = math.exp(log_p) if log_p > math.log(np.nextafter(0.0, 1.0)) else 0.0
    cert = LogAdaptiveCertificate(
        requested_relative_tolerance=float(relative_tolerance), certified_relative_bound=float(rel),
        packet_tilted_bound=float(pbound), support_alias_tilted_bound=float(support),
        cos_series_tilted_bound=float(series), tilted_sum=float(s_hat),
        log_prefactor=float(log_prefactor), theta=float(theta), interval_upper=float(upper),
        K=int(K), L=float(L), packet_count=int(packet_count),
        exact_count=min(int(exact_top), int(lam.size)), packet_order=int(order),
        rank=int(lam.size), passed=False,
        note="Requested relative certificate was not achieved before the refinement/resource cap.",
    )
    return LogAdaptiveResult(log_p=float(log_p), log10_p=float(log_p / math.log(10.0)),
                             p_value=float(p_value), certificate=cert, passport=passport)


def exact_tilted_logsf(q, eigenvalues, *, K=1024, L=16.0):
    lam = _validate_spectrum(eigenvalues)
    theta = exact_saddlepoint(q, lam)
    if theta <= 0:
        raise ValueError("q must exceed the mean")
    Ktheta = float(np.real(exact_cgf(theta, lam)))
    log_pref = Ktheta - theta*q
    c2 = exact_cgf_derivative(theta, lam, 2)
    c4 = exact_cgf_derivative(theta, lam, 4)
    upper = q + L*math.sqrt(c2 + math.sqrt(c4))
    _, s_grid, weighted = _payoff_integrals(q, theta, upper, K)
    phi = np.exp(exact_cgf(s_grid, lam) - Ktheta)
    s = (2.0/upper) * math.fsum(float(x) for x in weighted*np.real(phi))
    if s <= 0:
        raise RuntimeError("finite COS grid produced a nonpositive tilted tail sum")
    logp = log_pref + math.log(s)
    return float(logp), {"log10_p": float(logp/math.log(10.0)), "theta":theta,
                         "upper":upper, "K":K, "L":L, "tilted_sum":s}
