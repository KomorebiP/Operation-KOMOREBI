from __future__ import annotations

from dataclasses import dataclass
import math
import mpmath as mp

from interval_kcos import (
    design_positive_tail_parameters,
    interval_positive_logsf,
)


@dataclass(frozen=True)
class AccuracyDrivenTailResult:
    certified: bool
    requested_relative_accuracy: str
    achieved_relative_ratio_minus_one: str
    log10_interval: str
    log10_midpoint: str
    width_decades: str
    K: int
    L: str
    interval_dps: int
    refinements: int
    support_alias_bound_interval: str
    series_tail_bound_interval: str
    arithmetic_only_log10_interval: str
    failure_reason: str | None


def _interval_width(s: str, dps: int = 120) -> mp.mpf:
    body = s.strip()[1:-1]
    a, b = body.split(",", 1)
    with mp.workdps(dps):
        return mp.mpf(b.strip()) - mp.mpf(a.strip())


def _interval_midpoint(s: str, dps: int = 120) -> mp.mpf:
    body = s.strip()[1:-1]
    a, b = body.split(",", 1)
    with mp.workdps(dps):
        return (mp.mpf(a.strip()) + mp.mpf(b.strip())) / 2


def _upper_interval_endpoint(s: str, dps: int = 120) -> mp.mpf:
    body = s.strip()[1:-1]
    _, b = body.split(",", 1)
    with mp.workdps(dps):
        return mp.mpf(b.strip())


def certified_positive_logsf(
    q_decimal: str,
    eigenvalue_decimals,
    *,
    relative_accuracy: str | float = "1e-10",
    initial_K: int = 32,
    initial_L: str = "8",
    initial_interval_dps: int = 50,
    max_K: int = 131072,
    max_L: int = 24,
    max_interval_dps: int = 180,
    working_dps: int = 260,
) -> AccuracyDrivenTailResult:
    """Accuracy-driven positive central tail solver.

    Public contract:
      p_upper / p_lower - 1 <= relative_accuracy

    The function returns certified=False if it cannot prove that contract
    under the supplied resource caps.
    """
    eps = mp.mpf(str(relative_accuracy))
    if not (eps > 0):
        raise ValueError("relative_accuracy must be positive")

    # Convert requested multiplicative tolerance to an exact log10-width budget.
    with mp.workdps(working_dps):
        width_budget = mp.log(1 + eps, 10)

    K = int(initial_K)
    L = int(mp.mpf(initial_L))
    dps = int(initial_interval_dps)
    refinements = 0
    best = None

    while True:
        params = design_positive_tail_parameters(
            q_decimal,
            list(eigenvalue_decimals),
            L=str(L),
            working_dps=working_dps,
            output_digits=max(180, working_dps - 30),
        )

        r = interval_positive_logsf(
            q_decimal,
            list(eigenvalue_decimals),
            theta_decimal=params["theta"],
            upper_decimal=params["upper"],
            eta_decimal=params["eta"],
            K=K,
            interval_dps=dps,
        )
        refinements += 1
        best = r

        if r.passed_positive_sum and r.log10_interval.startswith("["):
            width = _interval_width(r.log10_interval, dps=max(working_dps, dps+40))
            with mp.workdps(max(working_dps, dps + 40)):
                ratio_minus_one = mp.expm1(mp.log(10) * width)
                accepted = ratio_minus_one <= eps
            if accepted:
                mid = _interval_midpoint(r.log10_interval, dps=max(working_dps, dps+40))
                return AccuracyDrivenTailResult(
                    certified=True,
                    requested_relative_accuracy=mp.nstr(eps, 20),
                    achieved_relative_ratio_minus_one=mp.nstr(ratio_minus_one, 20),
                    log10_interval=r.log10_interval,
                    log10_midpoint=mp.nstr(mid, 40),
                    width_decades=mp.nstr(width, 20),
                    K=K,
                    L=str(L),
                    interval_dps=dps,
                    refinements=refinements,
                    support_alias_bound_interval=r.support_alias_bound_interval,
                    series_tail_bound_interval=r.series_tail_bound_interval,
                    arithmetic_only_log10_interval=r.arithmetic_only_log10_interval,
                    failure_reason=None,
                )

        # If arithmetic interval is a material part of the budget, raise dps.
        if (
            r.passed_positive_sum
            and r.arithmetic_only_log10_interval not in ("undefined",)
        ):
            arithmetic_width = _interval_width(
                r.arithmetic_only_log10_interval,
                dps=max(working_dps, dps+40),
            )
            if arithmetic_width > width_budget / 8 and dps < max_interval_dps:
                dps = min(max_interval_dps, dps + 30)
                continue

        # Refine the dominant analytic source.
        try:
            support = _upper_interval_endpoint(
                r.support_alias_bound_interval,
                dps=max(working_dps, dps+40),
            )
            series = _upper_interval_endpoint(
                r.series_tail_bound_interval,
                dps=max(working_dps, dps+40),
            )
        except Exception:
            support = mp.inf
            series = mp.inf

        if series >= support and K < max_K:
            K = min(max_K, 2*K)
            continue

        if L < max_L:
            L += 2
            continue

        if K < max_K:
            K = min(max_K, 2*K)
            continue

        if dps < max_interval_dps:
            dps = min(max_interval_dps, dps + 30)
            continue

        # Fail closed: return interval, never an uncertified point estimate.
        if best is not None and best.log10_interval.startswith("["):
            width = _interval_width(best.log10_interval, dps=max(working_dps, dps+40))
            with mp.workdps(max(working_dps, dps + 40)):
                ratio_minus_one = mp.expm1(mp.log(10) * width)
            mid = _interval_midpoint(best.log10_interval, dps=max(working_dps, dps+40))
            return AccuracyDrivenTailResult(
                certified=False,
                requested_relative_accuracy=mp.nstr(eps, 20),
                achieved_relative_ratio_minus_one=mp.nstr(ratio_minus_one, 20),
                log10_interval=best.log10_interval,
                log10_midpoint=mp.nstr(mid, 40),
                width_decades=mp.nstr(width, 20),
                K=K,
                L=str(L),
                interval_dps=dps,
                refinements=refinements,
                support_alias_bound_interval=best.support_alias_bound_interval,
                series_tail_bound_interval=best.series_tail_bound_interval,
                arithmetic_only_log10_interval=best.arithmetic_only_log10_interval,
                failure_reason="resource caps reached before requested accuracy was proved",
            )

        return AccuracyDrivenTailResult(
            certified=False,
            requested_relative_accuracy=mp.nstr(eps, 20),
            achieved_relative_ratio_minus_one="inf",
            log10_interval="[-inf,+inf]",
            log10_midpoint="nan",
            width_decades="inf",
            K=K,
            L=str(L),
            interval_dps=dps,
            refinements=refinements,
            support_alias_bound_interval=best.support_alias_bound_interval if best else "unknown",
            series_tail_bound_interval=best.series_tail_bound_interval if best else "unknown",
            arithmetic_only_log10_interval=best.arithmetic_only_log10_interval if best else "unknown",
            failure_reason="no positive certified tail interval under resource caps",
        )
