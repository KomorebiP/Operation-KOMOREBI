from __future__ import annotations

from dataclasses import dataclass
import math
from collections import OrderedDict
from decimal import Decimal
from typing import Iterable, Sequence

import mpmath as mp
from mpmath import iv
from directed_accuracy import outward_interval_string


@dataclass(frozen=True)
class IntervalLogTailResult:
    log10_interval: str
    log10_lower: float
    log10_upper: float
    width_decades: float
    multiplicative_ratio_minus_one: float
    finite_sum_interval: str
    arithmetic_only_log10_interval: str
    arithmetic_only_width_decades: float
    support_alias_bound_interval: str
    series_tail_bound_interval: str
    total_tilted_error_interval: str
    q_decimal: str
    theta_decimal: str
    upper_decimal: str
    eta_decimal: str
    K: int
    interval_dps: int
    rank: int
    passed_positive_sum: bool
    note: str


def _as_decimal_string(x, digits=180) -> str:
    if isinstance(x, str):
        return x
    return mp.nstr(mp.mpf(x), digits)


def _interval_endpoints_as_strings(x) -> tuple[str, str]:
    s = outward_interval_string(x)
    if not (s.startswith("[") and s.endswith("]")):
        raise ValueError(f"not a real interval string: {s}")
    body = s[1:-1]
    left, right = body.split(",", 1)
    return left.strip(), right.strip()


def _float_endpoints(x) -> tuple[float, float]:
    return float(x.a), float(x.b)


def _group_decimal_eigenvalues(values: Sequence[str]) -> list[tuple[str, int]]:
    counts: OrderedDict[str, int] = OrderedDict()
    for value in values:
        key = str(value)
        counts[key] = counts.get(key, 0) + 1
    return list(counts.items())


def _cgf_real(theta, groups):
    total = iv.mpf("0")
    for lam_s, count in groups:
        lam = iv.mpf(lam_s)
        total += -iv.mpf(count) / 2 * iv.log(1 - 2 * theta * lam)
    return total


def _cgf_derivative_point(theta: mp.mpf, lams: Sequence[mp.mpf], order: int) -> mp.mpf:
    if order < 1:
        raise ValueError("order must be >=1")
    coefficient = (mp.mpf(2) ** (order - 1)) * mp.factorial(order - 1)
    return coefficient * mp.fsum(
        lam**order / (1 - 2 * theta * lam) ** order
        for lam in lams
    )


def _solve_monotone_derivative(target, lams, lo, hi, *, iterations=300):
    target = mp.mpf(target)
    lo = mp.mpf(lo)
    hi = mp.mpf(hi)
    for _ in range(iterations):
        mid = (lo + hi) / 2
        value = _cgf_derivative_point(mid, lams, 1)
        if value < target:
            lo = mid
        else:
            hi = mid
    return (lo + hi) / 2


def design_positive_tail_parameters(
    q_decimal: str,
    eigenvalue_decimals: Sequence[str],
    *,
    L: str = "10",
    working_dps: int = 220,
    output_digits: int = 180,
) -> dict:
    """Choose efficient point parameters.

    The resulting decimal values are *design points*, not assumptions of exact
    saddlepoint roots.  The interval theorem remains valid for any theta, eta,
    and U that satisfy the checked inequalities.
    """
    with mp.workdps(working_dps):
        q = mp.mpf(q_decimal)
        lams = [mp.mpf(x) for x in eigenvalue_decimals]
        if not lams or min(lams) <= 0:
            raise ValueError("positive eigenvalues are required")
        mean = mp.fsum(lams)
        if q <= mean:
            raise ValueError("q must be above the mean for the positive-tilt backend")

        singularity = 1 / (2 * max(lams))
        eps = mp.power(10, -(working_dps // 2))
        theta = _solve_monotone_derivative(
            q, lams, mp.mpf("0"), singularity * (1 - eps)
        )

        c2 = _cgf_derivative_point(theta, lams, 2)
        c4 = _cgf_derivative_point(theta, lams, 4)
        scale = mp.sqrt(c2 + mp.sqrt(c4))
        U = q + mp.mpf(L) * scale

        eta = _solve_monotone_derivative(
            U, lams, theta, singularity * (1 - eps)
        )

        return {
            "q": mp.nstr(q, output_digits),
            "theta": mp.nstr(theta, output_digits),
            "upper": mp.nstr(U, output_digits),
            "eta": mp.nstr(eta, output_digits),
            "L": str(L),
        }


def _re_tilted_cf(u, theta, groups):
    """Directed-rounding enclosure of Re phi_theta(u).

    For each coefficient,
      (1 - i a_j u)^(-1/2)
    has magnitude (1+(a_j u)^2)^(-1/4) and phase
    +atan(a_j u)/2.
    """
    logmag = iv.mpf("0")
    phase = iv.mpf("0")
    one = iv.mpf("1")

    for lam_s, count in groups:
        lam = iv.mpf(lam_s)
        a = 2 * lam / (1 - 2 * theta * lam)
        x = a * u
        c = iv.mpf(count)
        logmag += -c / 4 * iv.log(1 + x * x)
        phase += c / 2 * iv.atan2(x, one)

    return iv.exp(logmag) * iv.cos(phase)


def _payoff_integral(k: int, q, theta, U):
    """Integral of exp(-theta(x-q))*cos(k*pi*x/U) on [q,U].

    The endpoint identity u_k U = k*pi is used exactly to avoid an interval
    dependency blowup at the upper endpoint.
    """
    u = iv.mpf(k) * iv.pi / U
    ell = U - q
    uq = u * q
    parity = iv.mpf("1") if (k % 2 == 0) else iv.mpf("-1")

    numerator = (
        theta * iv.cos(uq)
        - u * iv.sin(uq)
        - theta * iv.exp(-theta * ell) * parity
    )
    denominator = theta * theta + u * u
    return numerator / denominator


def _tilted_chernoff_support_alias_bound(q, theta, U, eta, groups):
    """Support + cosine-periodization alias bound.

    For eta>theta,
      P_theta(Q>U)
      <= exp(K(eta)-K(theta)-(eta-theta)U).

    The desired payoff omitted above U is at most
      exp(-theta(U-q))*P_theta(Q>U).

    The full-characteristic-function cosine series periodizes the tilted
    density; its positive-tail alias mass on [0,U] is at most P_theta(Q>U).

    Adding both gives the returned bound.
    """
    log_tail = (
        _cgf_real(eta, groups)
        - _cgf_real(theta, groups)
        - (eta - theta) * U
    )
    tail = iv.exp(log_tail)
    return tail * (1 + iv.exp(-theta * (U - q)))


def _power_series_tail_bound(theta, U, K: int, groups, rank: int):
    """Rigorous omitted-COS-mode bound for rank > 2.

    Under the theta tilt,
      |phi_theta(t)|
      = prod_j (1+(a_j t)^2)^(-1/4)
      <= C t^(-rank/2),
      C = prod_j a_j^(-1/2).

    Also |I_k| <= 1/theta.  Therefore
      R_K <= 2/(U theta) C (U/pi)^p sum_{k=K}^inf k^-p,
      p=rank/2.

    We bound
      sum_{k=K}^inf k^-p
      <= K^-p + K^(1-p)/(p-1).
    """
    if rank <= 2:
        raise ValueError("the simple power-tail certificate requires rank > 2")
    if K < 1:
        raise ValueError("K must be >=1")

    logC = iv.mpf("0")
    for lam_s, count in groups:
        lam = iv.mpf(lam_s)
        a = 2 * lam / (1 - 2 * theta * lam)
        logC += -iv.mpf(count) / 2 * iv.log(a)

    C = iv.exp(logC)
    p = iv.mpf(rank) / 2
    Kiv = iv.mpf(K)
    zeta_tail = Kiv ** (-p) + Kiv ** (1 - p) / (p - 1)

    return (
        2 / (U * theta)
        * C
        * (U / iv.pi) ** p
        * zeta_tail
    )


def interval_positive_logsf(
    q_decimal: str,
    eigenvalue_decimals: Sequence[str],
    *,
    theta_decimal: str,
    upper_decimal: str,
    eta_decimal: str,
    K: int = 128,
    interval_dps: int = 90,
) -> IntervalLogTailResult:
    """Directed-rounding interval enclosure for a positive central tail.

    The input decimals are treated as the mathematical input values.

    The current rigorous mode-tail proof requires rank > 2.
    """
    if int(K) <= 0 or int(interval_dps) <= 0:
        raise ValueError("K and interval_dps must be positive")
    values = [str(x) for x in eigenvalue_decimals]
    literals = [str(q_decimal), str(theta_decimal), str(upper_decimal),
                str(eta_decimal)] + values
    if not all(Decimal(x).is_finite() for x in literals):
        raise ValueError("all tail inputs must be finite decimals")
    iv.dps = int(interval_dps)

    q = iv.mpf(q_decimal)
    theta = iv.mpf(theta_decimal)
    U = iv.mpf(upper_decimal)
    eta = iv.mpf(eta_decimal)

    if not values:
        raise ValueError("eigenvalue list must be nonempty")
    rank = len(values)
    if rank <= 2:
        raise ValueError("the rigorous series-tail bound requires rank > 2")
    groups = _group_decimal_eigenvalues(values)

    coefficients = [iv.mpf(x) for x in values]
    if not all(bool(lam.a > 0) for lam in coefficients):
        raise ValueError("positive eigenvalues are required")
    if not bool(q.a >= 0):
        raise ValueError("q must be nonnegative for integration on [0,U]")
    if not bool(theta.a > 0):
        raise ValueError("theta must be positive")
    if not bool(U.a > q.b):
        raise ValueError("upper must exceed q")
    if not bool(eta.a > theta.b):
        raise ValueError("eta must exceed theta")
    if not all(bool((2 * eta * lam).b < 1) for lam in coefficients):
        raise ValueError("theta and eta must lie inside the MGF domain")

    finite_sum = iv.mpf("0")
    for k in range(int(K)):
        u = iv.mpf(k) * iv.pi / U
        payoff = _payoff_integral(k, q, theta, U)
        rephi = _re_tilted_cf(u, theta, groups)
        weight = iv.mpf("0.5") if k == 0 else iv.mpf("1")
        finite_sum += weight * payoff * rephi
    finite_sum *= 2 / U

    support = _tilted_chernoff_support_alias_bound(
        q, theta, U, eta, groups
    )
    series = _power_series_tail_bound(
        theta, U, int(K), groups, rank
    )
    total_error = support + series

    true_tilted_sum = finite_sum + iv.mpf([-1, 1]) * total_error

    lo_sum, hi_sum = _float_endpoints(true_tilted_sum)
    if lo_sum <= 0:
        return IntervalLogTailResult(
            log10_interval="[-inf, +inf]",
            log10_lower=-math.inf,
            log10_upper=math.inf,
            width_decades=math.inf,
            multiplicative_ratio_minus_one=math.inf,
            finite_sum_interval=outward_interval_string(finite_sum),
            arithmetic_only_log10_interval="undefined",
            arithmetic_only_width_decades=math.inf,
            support_alias_bound_interval=outward_interval_string(support),
            series_tail_bound_interval=outward_interval_string(series),
            total_tilted_error_interval=outward_interval_string(total_error),
            q_decimal=str(q_decimal),
            theta_decimal=str(theta_decimal),
            upper_decimal=str(upper_decimal),
            eta_decimal=str(eta_decimal),
            K=int(K),
            interval_dps=int(interval_dps),
            rank=rank,
            passed_positive_sum=False,
            note="analytic error bound is too large to prove a positive lower tail sum",
        )

    log_prefactor = _cgf_real(theta, groups) - theta * q

    arithmetic_log10 = (
        log_prefactor + iv.log(finite_sum)
    ) / iv.log(10)

    log10_interval = (
        log_prefactor + iv.log(true_tilted_sum)
    ) / iv.log(10)

    lo, hi = _float_endpoints(log10_interval)
    # Compute differences before converting to binary64. Subtracting rounded
    # endpoint summaries destroys narrow widths at large negative logarithms.
    # These float fields are advisory; certification uses the outward endpoint
    # strings and the separate directed_relative_accuracy acceptance routine.
    width_iv = log10_interval.b - log10_interval.a
    arithmetic_width_iv = arithmetic_log10.b - arithmetic_log10.a
    width = float(width_iv.b)
    arithmetic_width = float(arithmetic_width_iv.b)
    ratio_minus_one = float(iv.expm1(iv.log(10) * width_iv).b)

    return IntervalLogTailResult(
        log10_interval=outward_interval_string(log10_interval),
        log10_lower=lo,
        log10_upper=hi,
        width_decades=width,
        multiplicative_ratio_minus_one=ratio_minus_one,
        finite_sum_interval=outward_interval_string(finite_sum),
        arithmetic_only_log10_interval=outward_interval_string(arithmetic_log10),
        arithmetic_only_width_decades=arithmetic_width,
        support_alias_bound_interval=outward_interval_string(support),
        series_tail_bound_interval=outward_interval_string(series),
        total_tilted_error_interval=outward_interval_string(total_error),
        q_decimal=str(q_decimal),
        theta_decimal=str(theta_decimal),
        upper_decimal=str(upper_decimal),
        eta_decimal=str(eta_decimal),
        K=int(K),
        interval_dps=int(interval_dps),
        rank=rank,
        passed_positive_sum=True,
        note=(
            "Finite transform and prefactor enclosed with mpmath.iv directed "
            "rounding; support/alias and omitted-mode tails are analytic bounds. "
            "Guarantee is conditional on correctness of the interval library implementation."
        ),
    )


def even_df_scaled_chi_square_logsf_interval(
    q_decimal: str,
    *,
    coefficient_decimal: str,
    df: int,
    interval_dps: int = 90,
):
    """Independent exact interval control for coefficient * chi2_df.

    For even df, shape n=df/2 is integer and
      P(chi2_df >= x)
      = exp(-x/2) sum_{k=0}^{n-1} (x/2)^k/k!.

    With Q = coefficient * chi2_df,
      x/2 = q/(2*coefficient).
    """
    if df <= 0 or df % 2:
        raise ValueError("df must be a positive even integer")
    iv.dps = int(interval_dps)
    q = iv.mpf(q_decimal)
    coefficient = iv.mpf(coefficient_decimal)
    x = q / (2 * coefficient)
    n = df // 2

    term = iv.mpf("1")
    total = iv.mpf("1")
    for k in range(1, n):
        term = term * x / k
        total += term

    sf = iv.exp(-x) * total
    log10sf = iv.log(sf) / iv.log(10)
    lo, hi = _float_endpoints(log10sf)
    return {
        "log10_interval": outward_interval_string(log10sf),
        "log10_lower": lo,
        "log10_upper": hi,
        "width_decades": float((log10sf.b - log10sf.a).b),
    }


def scaled_chi_square_target_point(
    target_log10_p: int,
    *,
    coefficient_decimal: str = "0.02",
    df: int = 80,
    working_dps: int = 240,
    output_digits: int = 190,
) -> str:
    """High-precision design point q near the requested exact tail.

    This function is *not* itself the rigorous reference.  The returned decimal
    q is subsequently checked by
    even_df_scaled_chi_square_logsf_interval().
    """
    if df <= 0 or df % 2:
        raise ValueError("df must be a positive even integer")

    with mp.workdps(working_dps):
        coefficient = mp.mpf(coefficient_decimal)
        n = df // 2
        target = mp.mpf(target_log10_p) * mp.log(10)

        def logsf(q):
            x = q / (2 * coefficient)
            term = mp.mpf(1)
            total = mp.mpf(1)
            for k in range(1, n):
                term = term * x / k
                total += term
            return -x + mp.log(total)

        # Asymptotic initialization q ~ 2*coefficient*T*ln 10.
        T = -mp.mpf(target_log10_p)
        guess = 2 * coefficient * T * mp.log(10)
        lo = max(mp.mpf("1e-30"), guess * mp.mpf("0.5"))
        hi = guess * mp.mpf("2.0") + df * coefficient

        while logsf(lo) < target:
            lo *= mp.mpf("0.5")
        while logsf(hi) > target:
            hi *= mp.mpf("1.5")

        for _ in range(working_dps * 4):
            mid = (lo + hi) / 2
            if logsf(mid) > target:
                lo = mid
            else:
                hi = mid

        q = (lo + hi) / 2
        return mp.nstr(q, output_digits)


__all__ = [
    "IntervalLogTailResult",
    "design_positive_tail_parameters",
    "interval_positive_logsf",
    "even_df_scaled_chi_square_logsf_interval",
    "scaled_chi_square_target_point",
]
