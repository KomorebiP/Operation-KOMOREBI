from __future__ import annotations

from dataclasses import dataclass
import math
import numpy as np

from kcos_v2 import adaptive_kcos_logsf


@dataclass(frozen=True)
class OperatorErrorCertificate:
    exact_operator_error: float
    block_norm_error_bound: float
    block_transfer_matrix: np.ndarray


@dataclass(frozen=True)
class SpectralInterval:
    lower: np.ndarray
    upper: np.ndarray
    epsilon: float
    approximate_eigenvalues: np.ndarray


@dataclass(frozen=True)
class TailBracket:
    lower_log_p: float
    upper_log_p: float
    lower_log10_p: float
    upper_log10_p: float
    lower_p: float
    upper_p: float
    bracket_width_decades: float
    q: float
    note: str


@dataclass(frozen=True)
class RangeCoreCertificate:
    core_singular_values: np.ndarray
    residual_norm: float
    lower_singular_values: np.ndarray
    upper_singular_values: np.ndarray
    lower_eigenvalues: np.ndarray
    upper_eigenvalues: np.ndarray
    ambient_spectral_count: int


def phase_slices(widths):
    start = 0
    out = []
    for w in widths:
        out.append(slice(start, start + int(w)))
        start += int(w)
    return out


def block_norm_matrix(E: np.ndarray, widths) -> np.ndarray:
    E = np.asarray(E, dtype=np.float64)
    sl = phase_slices(widths)
    C = np.zeros((len(sl), len(sl)), dtype=np.float64)
    for h, sh in enumerate(sl):
        for g, sg in enumerate(sl):
            block = E[sh, sg]
            if block.size:
                C[h, g] = np.linalg.norm(block, ord=2)
    return C


def certify_operator_pruning(H, H0, widths) -> OperatorErrorCertificate:
    H = np.asarray(H, dtype=np.float64)
    H0 = np.asarray(H0, dtype=np.float64)
    E = H - H0
    C = block_norm_matrix(E, widths)
    exact = float(np.linalg.norm(E, ord=2))
    bound = float(np.linalg.norm(C, ord=2))
    return OperatorErrorCertificate(
        exact_operator_error=exact,
        block_norm_error_bound=bound,
        block_transfer_matrix=C,
    )


def spectral_interval_from_pruned_operator(H0, epsilon) -> SpectralInterval:
    H0 = np.asarray(H0, dtype=np.float64)
    mu = np.linalg.eigvalsh(0.5 * (H0 + H0.T))[::-1]
    eps = float(epsilon)
    lower = np.maximum(0.0, mu - eps)
    upper = np.maximum(0.0, mu + eps)
    return SpectralInterval(
        lower=lower,
        upper=upper,
        epsilon=eps,
        approximate_eigenvalues=mu,
    )


def positive_quadratic_tail_bracket(q, interval, *, relative_tolerance=1e-9):
    """Tail bracket from coefficient-wise spectral intervals.

    The current K-COS evaluator is an upper-tail positive-tilt routine and
    requires q above the mean of the supplied coefficient set.  When an
    interval endpoint is too coarse for that condition, return the strongest
    trivial stochastic bound available rather than evaluating outside domain.
    """
    lower = np.asarray(interval.lower, dtype=np.float64)
    upper = np.asarray(interval.upper, dtype=np.float64)

    lower = lower[lower > 0]
    upper = upper[upper > 0]

    lower_mean = float(np.sum(lower))
    upper_mean = float(np.sum(upper))

    lower_trivial = False
    upper_trivial = False

    if lower.size and q > lower_mean:
        lo = adaptive_kcos_logsf(
            q, lower, relative_tolerance=relative_tolerance
        )
        lower_log_p = float(lo.log_p)
    elif lower.size:
        # Safe but intentionally coarse until a general-CDF evaluator is used.
        lower_log_p = -math.inf
        lower_trivial = True
    else:
        lower_log_p = -math.inf if q > 0 else 0.0
        lower_trivial = True

    if upper.size and q > upper_mean:
        hi = adaptive_kcos_logsf(
            q, upper, relative_tolerance=relative_tolerance
        )
        upper_log_p = float(hi.log_p)
    elif upper.size:
        upper_log_p = 0.0  # SF <= 1
        upper_trivial = True
    else:
        upper_log_p = -math.inf if q > 0 else 0.0
        upper_trivial = True

    lower_log10 = (
        lower_log_p / math.log(10)
        if math.isfinite(lower_log_p) else -math.inf
    )
    upper_log10 = (
        upper_log_p / math.log(10)
        if math.isfinite(upper_log_p) else -math.inf
    )
    width = (
        float(upper_log10 - lower_log10)
        if math.isfinite(lower_log10) and math.isfinite(upper_log10)
        else math.inf
    )

    return TailBracket(
        lower_log_p=lower_log_p,
        upper_log_p=upper_log_p,
        lower_log10_p=lower_log10,
        upper_log10_p=upper_log10,
        lower_p=math.exp(lower_log_p) if lower_log_p > -745 else 0.0,
        upper_p=math.exp(upper_log_p) if upper_log_p > -745 else 0.0,
        bracket_width_decades=width,
        q=float(q),
        note=(
            "Weyl coefficient enclosure plus common-Z stochastic ordering. "
            f"Lower endpoint trivial={lower_trivial}; upper endpoint trivial={upper_trivial}. "
            "K-COS numerical certificates are separate from the spectral enclosure."
        ),
    )


def range_core_certificate(A, U) -> RangeCoreCertificate:
    """Certify a sample-space range basis against the exact factor A.

    If B=U^T A and F=(I-UU^T)A, then
        |sigma_i(A)-sigma_i(B_padded)| <= ||F||_2.
    """
    A = np.asarray(A, dtype=np.float64)
    U = np.asarray(U, dtype=np.float64)
    if U.ndim == 1:
        U = U[:, None]
    U, _ = np.linalg.qr(U, mode="reduced")

    B = U.T @ A
    F = A - U @ B
    delta = float(np.linalg.norm(F, ord=2))

    core_sv = np.linalg.svd(B, compute_uv=False)
    N = min(A.shape)
    padded = np.zeros(N, dtype=np.float64)
    padded[: min(N, core_sv.size)] = core_sv[:N]

    lower_sv = np.maximum(0.0, padded - delta)
    upper_sv = padded + delta

    return RangeCoreCertificate(
        core_singular_values=core_sv,
        residual_norm=delta,
        lower_singular_values=lower_sv,
        upper_singular_values=upper_sv,
        lower_eigenvalues=lower_sv**2,
        upper_eigenvalues=upper_sv**2,
        ambient_spectral_count=N,
    )


def range_core_tail_bracket(q, cert, *, relative_tolerance=1e-9):
    interval = SpectralInterval(
        lower=cert.lower_eigenvalues,
        upper=cert.upper_eigenvalues,
        epsilon=cert.residual_norm,
        approximate_eigenvalues=cert.core_singular_values**2,
    )
    return positive_quadratic_tail_bracket(
        q, interval, relative_tolerance=relative_tolerance
    )


@dataclass(frozen=True)
class DualBudgetSchedule:
    omitted_pairs: tuple[tuple[int, int], ...]
    retained_pairs: tuple[tuple[int, int], ...]
    additive_query_bound: float
    operator_norm_bound: float
    query_budget: float
    operator_budget: float
    certificate_valid: bool


def omitted_block_norm_matrix(B, omitted_pairs):
    B = np.asarray(B, dtype=np.float64)
    C = np.zeros_like(B)
    for h, g in omitted_pairs:
        C[h, g] = B[h, g]
        C[g, h] = B[g, h]
    return C


def dual_budget_greedy_schedule(
    B,
    edge_risks,
    *,
    query_budget,
    operator_budget,
):
    """Certified equal-cost heuristic under simultaneous query/operator budgets.

    Edges are considered in increasing query-risk order.  A candidate is
    omitted only if both:
        sum beta_e <= query_budget
    and
        ||C_omitted||_2 <= operator_budget.
    """
    risks = sorted(edge_risks, key=lambda r: (r.scalar_risk, r.pair))
    omitted = []
    qbound = 0.0

    for r in risks:
        trial = omitted + [r.pair]
        trial_q = qbound + r.scalar_risk
        C = omitted_block_norm_matrix(B, trial)
        op = float(np.linalg.norm(C, ord=2))
        if (
            trial_q <= float(query_budget) + 1e-15
            and op <= float(operator_budget) + 1e-15
        ):
            omitted = trial
            qbound = trial_q

    all_pairs = tuple(r.pair for r in risks)
    omitted_set = set(omitted)
    retained = tuple(p for p in all_pairs if p not in omitted_set)
    C = omitted_block_norm_matrix(B, omitted)
    op = float(np.linalg.norm(C, ord=2))

    return DualBudgetSchedule(
        omitted_pairs=tuple(omitted),
        retained_pairs=retained,
        additive_query_bound=float(qbound),
        operator_norm_bound=op,
        query_budget=float(query_budget),
        operator_budget=float(operator_budget),
        certificate_valid=bool(
            qbound <= query_budget + 1e-15
            and op <= operator_budget + 1e-15
        ),
    )
