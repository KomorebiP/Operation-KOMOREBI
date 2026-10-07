from __future__ import annotations

from dataclasses import dataclass
import math
from typing import Sequence

import mpmath as mp
from mpmath import iv
import numpy as np

from accuracy_driven import certified_positive_logsf
from directed_accuracy import (directed_relative_accuracy, interval_endpoint_strings,
                               interval_midpoint, positive_decimal, scaled_accuracy_budget,
                               outward_interval_string)


@dataclass(frozen=True)
class VerifiedSpectrum:
    lower: tuple[str, ...]
    upper: tuple[str, ...]
    candidates: tuple[str, ...]
    orthogonality_defect_upper: str
    reconstruction_residual_upper: str
    candidate_digits: int
    interval_dps: int
    rank: int
    source: str


@dataclass(frozen=True)
class MatrixTailCertificate:
    certified: bool
    requested_relative_accuracy: str
    achieved_relative_ratio_minus_one: str
    log10_interval: str
    log10_midpoint: str
    spectral_enclosure: VerifiedSpectrum
    lower_tail_interval: str
    upper_tail_interval: str
    candidate_digits: int
    spectral_refinements: int
    failure_reason: str | None


def _iv_endpoint_strings(x) -> tuple[str, str]:
    s = outward_interval_string(x).strip()
    if not (s.startswith("[") and s.endswith("]")):
        raise ValueError(f"not an interval: {s}")
    left, right = s[1:-1].split(",", 1)
    return left.strip(), right.strip()


def _iv_endpoints(x) -> tuple[mp.mpf, mp.mpf]:
    left, right = _iv_endpoint_strings(x)
    return mp.mpf(left), mp.mpf(right)


def _iv_abs_upper(x) -> mp.mpf:
    a, b = _iv_endpoints(x)
    return max(abs(a), abs(b))


def _iv_frobenius_upper_interval(entries):
    total = iv.mpf("0")
    for x in entries:
        total += abs(x) ** 2
    return iv.sqrt(total)


def _float64_exact_mpf(x: float) -> mp.mpf:
    n, d = float(x).as_integer_ratio()
    return mp.mpf(n) / d


def _float64_exact_iv(x: float):
    n, d = float(x).as_integer_ratio()
    return iv.mpf(n) / d


def _matrix_from_float64_exact(A: np.ndarray, *, interval: bool):
    A = np.asarray(A, dtype=np.float64)
    n, m = A.shape
    if interval:
        return [[_float64_exact_iv(A[i, j]) for j in range(m)] for i in range(n)]
    return mp.matrix([
        [_float64_exact_mpf(A[i, j]) for j in range(m)]
        for i in range(n)
    ])


def _gram_point(Amp: mp.matrix) -> mp.matrix:
    return Amp * Amp.T


def _gram_interval(Aiv):
    n = len(Aiv)
    m = len(Aiv[0]) if n else 0
    H = [[iv.mpf("0") for _ in range(n)] for _ in range(n)]
    for i in range(n):
        for j in range(i, n):
            s = iv.mpf("0")
            for k in range(m):
                s += Aiv[i][k] * Aiv[j][k]
            H[i][j] = s
            H[j][i] = s
    return H


def _candidate_eigendecomposition(H: mp.matrix, *, candidate_digits: int):
    # eigsy is only a candidate generator.  Its output is certified afterward.
    vals, vecs = mp.eigsy(H)
    order = list(range(len(vals) - 1, -1, -1))
    d = []
    Q = []
    for i in range(H.rows):
        Q.append([])
    for idx in order:
        value = vals[idx]
        # H is a Gram matrix.  Tiny negative candidate values are harmless as
        # candidate-generation noise; use zero and let the reconstruction
        # residual certificate absorb the change.
        if value < 0:
            value = mp.mpf("0")
        d.append(mp.nstr(value, candidate_digits))
        for i in range(H.rows):
            Q[i].append(mp.nstr(vecs[i, idx], candidate_digits))
    return d, Q


def certify_float64_factor_spectrum(
    A: np.ndarray,
    *,
    candidate_digits: int = 80,
    interval_dps: int = 90,
    working_dps: int | None = None,
) -> VerifiedSpectrum:
    """Certify eigenvalue intervals for H = A A^T.

    The binary64 entries of A are treated as exact input values.

    Let D=diag(d_i) and Q be any candidate eigensystem.  Set B=Q D Q^T.
    If
        ||Q^T Q-I||_2 <= eta < 1
    and
        ||H-B||_2 <= rho,
    then, for sorted d_i >= 0,

        max(0,(1-eta)d_i-rho) <= lambda_i(H)
        <= (1+eta)d_i+rho.

    We certify eta and rho by directed-rounding interval arithmetic, using
    Frobenius norms as computable upper bounds on spectral norms.
    """
    A = np.asarray(A, dtype=np.float64)
    if A.ndim != 2 or A.shape[0] == 0 or A.shape[1] == 0:
        raise ValueError("A must be a nonempty matrix")

    n = A.shape[0]
    if working_dps is None:
        working_dps = max(candidate_digits + 30, interval_dps + 30)

    with mp.workdps(int(working_dps)):
        Amp = _matrix_from_float64_exact(A, interval=False)
        Hmp = _gram_point(Amp)
        d_str, q_str = _candidate_eigendecomposition(
            Hmp, candidate_digits=int(candidate_digits)
        )

    iv.dps = int(interval_dps)
    Aiv = _matrix_from_float64_exact(A, interval=True)
    Hiv = _gram_interval(Aiv)
    Qiv = [[iv.mpf(q_str[i][j]) for j in range(n)] for i in range(n)]
    Div = [iv.mpf(x) for x in d_str]

    # S = Q^T Q - I.
    Sentries = []
    for i in range(n):
        for j in range(n):
            s = iv.mpf("0")
            for k in range(n):
                s += Qiv[k][i] * Qiv[k][j]
            if i == j:
                s -= 1
            Sentries.append(s)
    eta_iv = _iv_frobenius_upper_interval(Sentries)
    eta_lo_s, eta_hi_s = _iv_endpoint_strings(eta_iv)
    eta = mp.mpf(eta_hi_s)
    if not eta < 1:
        raise RuntimeError(
            f"candidate basis is not certifiably invertible: eta={eta_hi_s}"
        )

    # R = H - Q D Q^T.
    Rentries = []
    for i in range(n):
        for j in range(n):
            b = iv.mpf("0")
            for k in range(n):
                b += Qiv[i][k] * Div[k] * Qiv[j][k]
            Rentries.append(Hiv[i][j] - b)
    rho_iv = _iv_frobenius_upper_interval(Rentries)
    rho_lo_s, rho_hi_s = _iv_endpoint_strings(rho_iv)
    rho = mp.mpf(rho_hi_s)

    # Final coefficient bounds are evaluated with interval arithmetic and the
    # literal outward endpoint strings are preserved.  No conversion through
    # default-precision mp.mpf strings is allowed here.
    eta_box = iv.mpf(eta_hi_s)
    rho_box = iv.mpf(rho_hi_s)
    lower = []
    upper = []
    for ds in d_str:
        dbox = iv.mpf(ds)
        lo_box = (1 - eta_box) * dbox - rho_box
        hi_box = (1 + eta_box) * dbox + rho_box
        lo_left_s, _ = _iv_endpoint_strings(lo_box)
        _, hi_right_s = _iv_endpoint_strings(hi_box)
        if mp.mpf(lo_left_s) < 0:
            lo_left_s = "0"
        lower.append(lo_left_s)
        upper.append(hi_right_s)

    return VerifiedSpectrum(
        lower=tuple(lower),
        upper=tuple(upper),
        candidates=tuple(d_str),
        orthogonality_defect_upper=eta_hi_s,
        reconstruction_residual_upper=rho_hi_s,
        candidate_digits=int(candidate_digits),
        interval_dps=int(interval_dps),
        rank=n,
        source="exact binary64 factor A -> H=A A^T",
    )


def _parse_log_interval(s: str) -> tuple[str, str]:
    # Preserve the literal outer endpoints. No default-precision point conversion.
    return interval_endpoint_strings(s)


def certified_float64_factor_logsf(
    q_decimal: str,
    A: np.ndarray,
    *,
    relative_accuracy: str | float = "1e-10",
    initial_candidate_digits: int = 50,
    max_candidate_digits: int = 140,
    candidate_step: int = 30,
    interval_dps: int = 90,
    tail_accuracy_fraction: str = "0.1",
    tail_kwargs: dict | None = None,
) -> MatrixTailCertificate:
    """End-to-end certified tail from a binary64 factor.

    The exact input object is the binary64 matrix A and exact decimal q.
    The eigensolver is not trusted: each candidate decomposition is checked by
    interval arithmetic.  Coefficient monotonicity then brackets the true
    quadratic-form tail between the lower- and upper-spectrum tails.
    """
    eps_text = positive_decimal(relative_accuracy)
    tail_eps_text = scaled_accuracy_budget(
        eps_text, tail_accuracy_fraction,
        dps=max(int(interval_dps) + 40, int(max_candidate_digits) + 60, 120),
    )
    if (int(initial_candidate_digits) <= 0 or int(candidate_step) <= 0
            or int(max_candidate_digits) < int(initial_candidate_digits)):
        raise ValueError("candidate precision bounds and step must be positive and ordered")

    kwargs = dict(tail_kwargs or {})
    refinements = 0
    last = None

    digits = int(initial_candidate_digits)
    while digits <= int(max_candidate_digits):
        spec = certify_float64_factor_spectrum(
            A,
            candidate_digits=digits,
            interval_dps=max(int(interval_dps), digits + 10),
            working_dps=digits + 50,
        )
        refinements += 1

        lower = [x for x in spec.lower if mp.mpf(x) > 0]
        upper = [x for x in spec.upper if mp.mpf(x) > 0]
        if len(lower) <= 2:
            raise RuntimeError("lower spectral enclosure has rank <= 2")

        lo_tail = certified_positive_logsf(
            q_decimal,
            lower,
            relative_accuracy=tail_eps_text,
            **kwargs,
        )
        hi_tail = certified_positive_logsf(
            q_decimal,
            upper,
            relative_accuracy=tail_eps_text,
            **kwargs,
        )

        if not lo_tail.certified or not hi_tail.certified:
            last = (spec, lo_tail, hi_tail, None)
            digits += int(candidate_step)
            continue

        lo_a, _ = _parse_log_interval(lo_tail.log10_interval)
        _, hi_b = _parse_log_interval(hi_tail.log10_interval)
        outer_interval = f"[{lo_a}, {hi_b}]"
        decision = directed_relative_accuracy(
            outer_interval, eps_text, dps=max(digits + 60, 120)
        )
        midpoint = interval_midpoint(outer_interval, dps=max(digits + 60, 120))

        if decision.accepted:
            return MatrixTailCertificate(
                certified=True,
                requested_relative_accuracy=eps_text,
                achieved_relative_ratio_minus_one=decision.ratio_upper,
                log10_interval=outer_interval,
                log10_midpoint=midpoint,
                spectral_enclosure=spec,
                lower_tail_interval=lo_tail.log10_interval,
                upper_tail_interval=hi_tail.log10_interval,
                candidate_digits=digits,
                spectral_refinements=refinements,
                failure_reason=None,
            )

        last = (spec, lo_tail, hi_tail, decision.ratio_upper)
        digits += int(candidate_step)

    spec, lo_tail, hi_tail, ratio = last
    if lo_tail.certified and hi_tail.certified:
        lo_a, _ = _parse_log_interval(lo_tail.log10_interval)
        _, hi_b = _parse_log_interval(hi_tail.log10_interval)
        interval_s = f"[{lo_a}, {hi_b}]"
        midpoint = interval_midpoint(interval_s, dps=max(int(max_candidate_digits) + 60, 120))
        ratio_s = ratio
    else:
        midpoint = "nan"
        ratio_s = "inf"
        interval_s = "[-inf,+inf]"

    return MatrixTailCertificate(
        certified=False,
        requested_relative_accuracy=eps_text,
        achieved_relative_ratio_minus_one=ratio_s,
        log10_interval=interval_s,
        log10_midpoint=midpoint,
        spectral_enclosure=spec,
        lower_tail_interval=lo_tail.log10_interval,
        upper_tail_interval=hi_tail.log10_interval,
        candidate_digits=int(max_candidate_digits),
        spectral_refinements=refinements,
        failure_reason="spectral/tail resource caps reached before requested end-to-end accuracy was proved",
    )


__all__ = [
    "VerifiedSpectrum",
    "MatrixTailCertificate",
    "certify_float64_factor_spectrum",
    "certified_float64_factor_logsf",
]
