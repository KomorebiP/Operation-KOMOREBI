from __future__ import annotations

from dataclasses import dataclass
import math

import numpy as np
from scipy.optimize import minimize_scalar

from kcos_v2 import adaptive_kcos_logsf


@dataclass(frozen=True)
class ResidualSpectrumCertificate:
    core_eigenvalues: np.ndarray
    residual_trace: float
    residual_cap: float
    residual_square_trace: float
    residual_rank_bound: int
    exact_total_trace: float


@dataclass(frozen=True)
class TraceCapTailBracket:
    lower_log_p: float
    upper_log_p: float
    lower_log10_p: float
    upper_log10_p: float
    bracket_width_decades: float
    q: float
    optimized_theta: float
    upper_method: str
    lower_method: str
    residual_trace: float
    residual_cap: float
    residual_square_trace: float


def orthonormalize(U: np.ndarray) -> np.ndarray:
    U = np.asarray(U, dtype=np.float64)
    if U.ndim == 1:
        U = U[:, None]
    if U.size == 0:
        return np.zeros((U.shape[0], 0), dtype=np.float64)
    Q, R = np.linalg.qr(U, mode='reduced')
    if R.size == 0:
        return Q
    diag = np.abs(np.diag(R))
    scale = max(float(diag.max()) if diag.size else 0.0, 1.0)
    keep = diag > 1e-12 * scale
    return Q[:, keep]


def residual_spectrum_certificate(A, U, *, compute_square_trace=True):
    """Exact range-core residual invariants.

    With U orthonormal,
      B = U^T A,
      F = (I-UU^T)A,
      A^T A = B^T B + F^T F.
    """
    A = np.asarray(A, dtype=np.float64)
    U = orthonormalize(U)
    B = U.T @ A
    F = A - U @ B

    core_sv = np.linalg.svd(B, compute_uv=False)
    core_eigs = core_sv**2

    residual_trace = float(np.sum(F * F))
    residual_cap = float(np.linalg.norm(F, ord=2) ** 2) if F.size else 0.0

    if compute_square_trace and F.size:
        S = F @ F.T
        residual_square_trace = float(np.sum(S * S))
    else:
        residual_square_trace = float(residual_cap * residual_trace)

    rank_bound = int(min(F.shape))
    exact_total_trace = float(np.sum(core_eigs) + residual_trace)

    return ResidualSpectrumCertificate(
        core_eigenvalues=np.asarray(core_eigs, dtype=np.float64),
        residual_trace=residual_trace,
        residual_cap=residual_cap,
        residual_square_trace=residual_square_trace,
        residual_rank_bound=rank_bound,
        exact_total_trace=exact_total_trace,
    )


def _core_log_mgf(theta, core_eigenvalues):
    lam = np.asarray(core_eigenvalues, dtype=np.float64)
    if lam.size == 0 or theta == 0:
        return 0.0
    if theta < 0 or np.any(2.0 * theta * lam >= 1.0):
        return math.inf
    return float(-0.5 * np.sum(np.log1p(-2.0 * theta * lam)))


def _extremal_convex_sum(total_mass, cap, dimension, f):
    """Max sum f(x_i) on 0<=x_i<=cap, sum x_i<=total_mass."""
    total_mass = max(float(total_mass), 0.0)
    cap = max(float(cap), 0.0)
    dimension = max(int(dimension), 0)
    if total_mass == 0.0 or cap == 0.0 or dimension == 0:
        return 0.0

    s = min(total_mass, dimension * cap)
    ratio = s / cap
    k = min(int(math.floor(ratio + 1e-14)), dimension)
    remainder = s - k * cap
    if remainder < 1e-14 * max(1.0, s) or k == dimension:
        remainder = 0.0

    out = k * f(cap)
    if remainder > 0:
        out += f(remainder)
    return float(out)


def trace_cap_log_mgf_upper(theta, cert):
    """Upper bound on log E exp(theta Z^T(C+R)Z).

    C=B^T B is known. R=F^T F is PSD with known trace and spectral cap.
    """
    theta = float(theta)
    if theta < 0:
        raise ValueError('theta must be nonnegative')
    if theta == 0:
        return 0.0

    core = np.asarray(cert.core_eigenvalues, dtype=np.float64)
    cmax = float(core[0]) if core.size else 0.0
    rho = float(cert.residual_cap)
    t = float(cert.residual_trace)

    if rho == 0.0:
        return _core_log_mgf(theta, core)
    if 2.0 * theta * (cmax + rho) >= 1.0:
        return math.inf

    alpha = 1.0 / (1.0 - 2.0 * theta * cmax)
    trace_T_bound = alpha * t
    cap_T_bound = alpha * rho

    def f(x):
        u = 2.0 * theta * x
        if u >= 1.0:
            return math.inf
        return -0.5 * math.log1p(-u)

    residual_increment = _extremal_convex_sum(
        trace_T_bound,
        cap_T_bound,
        cert.residual_rank_bound,
        f,
    )
    return _core_log_mgf(theta, core) + residual_increment


def trace_cap_chernoff_upper(q, cert):
    """Return (log upper probability, optimized theta)."""
    q = float(q)
    if q <= float(cert.exact_total_trace):
        return 0.0, 0.0

    core = np.asarray(cert.core_eigenvalues, dtype=np.float64)
    cmax = float(core[0]) if core.size else 0.0
    rho = float(cert.residual_cap)
    scale = cmax + rho
    if scale <= 0:
        return (-math.inf if q > 0 else 0.0), 0.0

    theta_hi = (0.5 / scale) * (1.0 - 1e-10)

    def objective(theta):
        K = trace_cap_log_mgf_upper(theta, cert)
        return 1e300 if not math.isfinite(K) else K - theta * q

    res = minimize_scalar(
        objective,
        bounds=(1e-14, theta_hi),
        method='bounded',
        options={'xatol': max(1e-14, theta_hi * 1e-12)},
    )
    return min(0.0, float(res.fun)), float(res.x)


def residual_subgamma_threshold(x, cert, *, use_exact_square_trace=True):
    """b(x) with P(Z^T R Z > b(x)) <= exp(-x)."""
    x = max(float(x), 0.0)
    t = float(cert.residual_trace)
    rho = float(cert.residual_cap)
    v = (
        float(cert.residual_square_trace)
        if use_exact_square_trace
        else rho * t
    )
    return float(t + 2.0 * math.sqrt(max(v * x, 0.0)) + 2.0 * rho * x)


def split_residual_upper(q, cert, *, relative_tolerance=1e-9, use_exact_square_trace=True):
    """Union-bound upper tail from core K-COS + residual concentration."""
    core = np.asarray(cert.core_eigenvalues, dtype=np.float64)
    q = float(q)
    core_mean = float(np.sum(core))
    if q <= cert.exact_total_trace:
        return 0.0, 0.0

    def log_upper_at_x(x):
        b = residual_subgamma_threshold(
            x, cert, use_exact_square_trace=use_exact_square_trace
        )
        qcore = q - b
        if core.size == 0:
            core_sf = 0.0 if qcore > 0 else 1.0
        elif qcore <= core_mean:
            core_sf = 1.0
        else:
            r = adaptive_kcos_logsf(qcore, core, relative_tolerance=relative_tolerance)
            core_sf = math.exp(r.log_p) if r.log_p > -745 else 0.0
        residual_prob = math.exp(-x) if x < 745 else 0.0
        p = min(1.0, core_sf + residual_prob)
        return math.log(p) if p > 0 else -math.inf

    grid = np.unique(np.r_[np.linspace(0.0, 20.0, 161), np.linspace(20.0, 80.0, 121)])
    vals = np.array([log_upper_at_x(float(x)) for x in grid])
    j = int(np.nanargmin(vals))
    left = float(grid[max(0, j - 1)])
    right = float(grid[min(len(grid) - 1, j + 1)])
    if right > left:
        res = minimize_scalar(lambda xx: log_upper_at_x(float(xx)), bounds=(left, right), method='bounded')
        return float(res.fun), float(res.x)
    return float(vals[j]), float(grid[j])


def core_lower_logsf(q, cert, *, relative_tolerance=1e-9):
    """Safe stochastic lower bound because C <= C+R in Loewner order."""
    core = np.asarray(cert.core_eigenvalues, dtype=np.float64)
    if core.size == 0:
        return -math.inf if q > 0 else 0.0
    if q <= float(np.sum(core)):
        return -math.inf
    return float(adaptive_kcos_logsf(q, core, relative_tolerance=relative_tolerance).log_p)


def trace_cap_tail_bracket(q, cert, *, relative_tolerance=1e-9, combine_split_bound=True):
    lower = core_lower_logsf(q, cert, relative_tolerance=relative_tolerance)
    upper, theta = trace_cap_chernoff_upper(q, cert)
    method = 'trace-cap determinant Chernoff'

    if combine_split_bound:
        split_upper, _ = split_residual_upper(
            q, cert, relative_tolerance=relative_tolerance, use_exact_square_trace=True
        )
        if split_upper < upper:
            upper = split_upper
            method = 'residual sub-gamma split'

    lo10 = lower / math.log(10) if math.isfinite(lower) else -math.inf
    hi10 = upper / math.log(10) if math.isfinite(upper) else -math.inf
    width = float(hi10 - lo10) if math.isfinite(lo10) and math.isfinite(hi10) else math.inf

    return TraceCapTailBracket(
        lower_log_p=lower,
        upper_log_p=upper,
        lower_log10_p=lo10,
        upper_log10_p=hi10,
        bracket_width_decades=width,
        q=float(q),
        optimized_theta=theta,
        upper_method=method,
        lower_method='core stochastic lower bound',
        residual_trace=cert.residual_trace,
        residual_cap=cert.residual_cap,
        residual_square_trace=cert.residual_square_trace,
    )


def split_residual_lower(q, cert, *, relative_tolerance=1e-9, use_exact_square_trace=True):
    """Lower tail bound using the residual lower-concentration inequality.

    For x>=0 and a(x)=tr(R)-2 sqrt(tr(R^2)x),
      P(Q_R < a(x)) <= exp(-x).
    Hence
      P(Q_core+Q_R >= q) >= P(Q_core >= q-a(x)) - exp(-x).
    """
    core = np.asarray(cert.core_eigenvalues, dtype=np.float64)
    q = float(q)
    t = float(cert.residual_trace)
    if use_exact_square_trace:
        v = float(cert.residual_square_trace)
    else:
        v = float(cert.residual_cap * cert.residual_trace)

    if core.size == 0 or t <= 0.0 or v <= 0.0:
        return core_lower_logsf(q, cert, relative_tolerance=relative_tolerance), 0.0

    core_mean = float(np.sum(core))
    xmax = t * t / (4.0 * v)
    if xmax <= 0:
        return core_lower_logsf(q, cert, relative_tolerance=relative_tolerance), 0.0

    def log_lower_at_x(x):
        x = max(float(x), 0.0)
        a = max(0.0, t - 2.0 * math.sqrt(max(v * x, 0.0)))
        qcore = q - a
        if qcore <= core_mean:
            # Current positive-tilt K-COS path cannot evaluate this safely.
            return -math.inf
        core_res = adaptive_kcos_logsf(
            qcore, core, relative_tolerance=relative_tolerance
        )
        pcore = math.exp(core_res.log_p) if core_res.log_p > -745 else 0.0
        fail = math.exp(-x) if x < 745 else 0.0
        p = max(0.0, pcore - fail)
        return math.log(p) if p > 0 else -math.inf

    # The optimum may be near the boundary where the residual-failure term
    # becomes smaller than the shifted core tail.  Use a dense deterministic grid.
    grid = np.linspace(0.0, xmax, 321)
    vals = np.array([log_lower_at_x(float(x)) for x in grid])
    if not np.any(np.isfinite(vals)):
        return -math.inf, 0.0
    j = int(np.nanargmax(vals))
    return float(vals[j]), float(grid[j])


def trace_cap_tail_bracket_v2(q, cert, *, relative_tolerance=1e-9):
    """Two-sided trace/cap/Frobenius bracket.

    Lower bound: maximum of the core-only stochastic lower bound and the
    residual lower-concentration split bound.
    Upper bound: minimum of determinant Chernoff and residual upper split.
    """
    core_lower = core_lower_logsf(q, cert, relative_tolerance=relative_tolerance)
    split_lower, _ = split_residual_lower(
        q, cert, relative_tolerance=relative_tolerance, use_exact_square_trace=True
    )
    lower = max(core_lower, split_lower)

    upper_chernoff, theta = trace_cap_chernoff_upper(q, cert)
    upper_split, _ = split_residual_upper(
        q, cert, relative_tolerance=relative_tolerance, use_exact_square_trace=True
    )
    upper = min(upper_chernoff, upper_split)
    method = (
        'trace-cap determinant Chernoff'
        if upper_chernoff <= upper_split
        else 'residual sub-gamma split'
    )

    lo10 = lower / math.log(10) if math.isfinite(lower) else -math.inf
    hi10 = upper / math.log(10) if math.isfinite(upper) else -math.inf
    width = float(hi10 - lo10) if math.isfinite(lo10) and math.isfinite(hi10) else math.inf

    return TraceCapTailBracket(
        lower_log_p=lower,
        upper_log_p=upper,
        lower_log10_p=lo10,
        upper_log10_p=hi10,
        bracket_width_decades=width,
        q=float(q),
        optimized_theta=theta,
        upper_method=method,
        lower_method=(
            'residual lower-concentration split'
            if split_lower >= core_lower
            else 'core stochastic lower bound'
        ),
        residual_trace=cert.residual_trace,
        residual_cap=cert.residual_cap,
        residual_square_trace=cert.residual_square_trace,
    )


def trace_frobenius_cap_log_mgf_upper(theta, cert):
    """MGF upper bound using residual trace, Frobenius-square trace, and cap.

    Write H=C+R and T=(I-2 theta C)^(-1/2) R (I-2 theta C)^(-1/2).
    If alpha=(1-2 theta lambda_max(C))^(-1), then
        tr(T) <= alpha tr(R),
        tr(T^2) <= alpha^2 tr(R^2),
        ||T|| <= alpha ||R||.
    For 0<=x<=a,
        -1/2 log(1-2 theta x)
        <= theta x + theta^2 x^2/(1-2 theta a).
    Summing yields the stated certificate.
    """
    theta = float(theta)
    if theta < 0:
        raise ValueError('theta must be nonnegative')
    if theta == 0:
        return 0.0

    core = np.asarray(cert.core_eigenvalues, dtype=np.float64)
    cmax = float(core[0]) if core.size else 0.0
    rho = float(cert.residual_cap)
    t = float(cert.residual_trace)
    v = float(cert.residual_square_trace)

    if rho == 0.0:
        return _core_log_mgf(theta, core)
    if 2.0 * theta * (cmax + rho) >= 1.0:
        return math.inf

    alpha = 1.0 / (1.0 - 2.0 * theta * cmax)
    a = alpha * rho
    denom = 1.0 - 2.0 * theta * a
    if denom <= 0:
        return math.inf

    residual_increment = (
        theta * alpha * t
        + (theta * theta * alpha * alpha * v) / denom
    )
    return _core_log_mgf(theta, core) + residual_increment


def trace_frobenius_cap_chernoff_upper(q, cert):
    q = float(q)
    if q <= float(cert.exact_total_trace):
        return 0.0, 0.0

    core = np.asarray(cert.core_eigenvalues, dtype=np.float64)
    cmax = float(core[0]) if core.size else 0.0
    rho = float(cert.residual_cap)
    if rho <= 1e-28 and cert.residual_trace <= 1e-26:
        # The core is numerically the whole spectrum.  Evaluate it directly.
        if core.size and q > float(np.sum(core)):
            r = adaptive_kcos_logsf(q, core, relative_tolerance=1e-10)
            return float(r.log_p), 0.0
        return (0.0 if q <= float(np.sum(core)) else -math.inf), 0.0

    scale = cmax + rho
    if scale <= 0:
        return (-math.inf if q > 0 else 0.0), 0.0
    theta_hi = (0.5 / scale) * (1.0 - 1e-10)

    def objective(theta):
        K = trace_frobenius_cap_log_mgf_upper(theta, cert)
        return 1e300 if not math.isfinite(K) else K - theta * q

    res = minimize_scalar(
        objective,
        bounds=(1e-14, theta_hi),
        method='bounded',
        options={'xatol': max(1e-14, theta_hi * 1e-12)},
    )
    return min(0.0, float(res.fun)), float(res.x)


def trace_moment_tail_bracket(q, cert, *, relative_tolerance=1e-9):
    """Fast two-sided bracket using the core lower tail and best MGF upper."""
    lower = core_lower_logsf(q, cert, relative_tolerance=relative_tolerance)

    up_tc, th_tc = trace_cap_chernoff_upper(q, cert)
    up_tfc, th_tfc = trace_frobenius_cap_chernoff_upper(q, cert)
    if up_tfc <= up_tc:
        upper, theta = up_tfc, th_tfc
        method = 'trace-Frobenius-cap Chernoff'
    else:
        upper, theta = up_tc, th_tc
        method = 'trace-cap extremal Chernoff'

    # Numerically complete range: exact core distribution is both endpoints.
    if cert.residual_trace <= 1e-26 and cert.residual_cap <= 1e-28:
        lower = upper
        method = 'exact captured spectrum'

    lo10 = lower / math.log(10) if math.isfinite(lower) else -math.inf
    hi10 = upper / math.log(10) if math.isfinite(upper) else -math.inf
    width = float(hi10 - lo10) if math.isfinite(lo10) and math.isfinite(hi10) else math.inf
    return TraceCapTailBracket(
        lower_log_p=lower,
        upper_log_p=upper,
        lower_log10_p=lo10,
        upper_log10_p=hi10,
        bracket_width_decades=width,
        q=float(q),
        optimized_theta=theta,
        upper_method=method,
        lower_method='core stochastic lower bound',
        residual_trace=cert.residual_trace,
        residual_cap=cert.residual_cap,
        residual_square_trace=cert.residual_square_trace,
    )
