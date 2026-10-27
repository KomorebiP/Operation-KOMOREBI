#!/usr/bin/env python3
"""Reproduce the finite arithmetic/Fourier/quantum bridge.

Exact checks use Python integers, fractions.Fraction, and the ring
Z[z]/(z^4-z^2+1). No rounded complex number is used as an exact certificate.
Optional NumPy checks report floating-point residuals separately.

Usage: python verify_bridge.py --output verification.json
"""
from __future__ import annotations
import argparse
import json
from fractions import Fraction
from math import gcd
from pathlib import Path
from typing import Sequence

Ring = tuple[int, int, int, int]
ZERO: Ring = (0, 0, 0, 0)
ONE: Ring = (1, 0, 0, 0)


def mobius(n: int) -> int:
    if n < 1:
        raise ValueError("mobius requires n >= 1")
    sign, p = 1, 2
    while p * p <= n:
        if n % p == 0:
            n //= p
            sign = -sign
            if n % p == 0:
                return 0
        p += 1
    return -sign if n > 1 else sign


def divisors(n: int) -> list[int]:
    if n < 1:
        raise ValueError("divisors requires n >= 1")
    return [d for d in range(1, n + 1) if n % d == 0]


def ramanujan(q: int, n: int) -> int:
    return sum(d * mobius(q // d) for d in divisors(gcd(q, n)))


def add(a: Ring, b: Ring) -> Ring:
    return tuple(a[i] + b[i] for i in range(4))  # type: ignore[return-value]


def scale(k: int, a: Ring) -> Ring:
    return tuple(k * x for x in a)  # type: ignore[return-value]


def times_z(a: Ring) -> Ring:
    # z^4 = z^2 - 1.
    return (-a[3], a[0], a[1] + a[3], a[2])


def convolution(a: Sequence[int], b: Sequence[int]) -> list[int]:
    if len(a) != len(b):
        raise ValueError("circular convolution requires equal lengths")
    n = len(a)
    return [sum(a[j] * b[(i-j) % n] for j in range(n)) for i in range(n)]


def main() -> dict:
    checks: dict[str, int] = {}

    def check(name: str, condition: bool) -> None:
        if not condition:
            raise AssertionError(name)
        checks[name] = checks.get(name, 0) + 1

    N = 12
    U = [a for a in range(N) if gcd(a, N) == 1]
    powers = [ONE]
    for _ in range(12):
        powers.append(times_z(powers[-1]))
    check("cyclotomic_order", powers[12] == ONE)
    for d in (1, 2, 3, 4, 6):
        check("cyclotomic_order", powers[d] != ONE)

    c = [ramanujan(N, n) for n in range(N)]
    check("explicit_signal", c == [4,0,2,0,-2,0,-4,0,-2,0,2,0])
    for n in range(N):
        phase_sum = ZERO
        for a in U:
            phase_sum = add(phase_sum, powers[(a*n) % N])
        check("phase_sum_equals_integer_formula", phase_sum == (c[n],0,0,0))

    # Every DFT coefficient is checked exactly in the cyclotomic ring.
    for k in range(N):
        coefficient = ZERO
        for n in range(N):
            coefficient = add(coefficient, scale(c[n], powers[(-k*n) % N]))
        check("exact_DFT_support", coefficient == (N if k in U else 0,0,0,0))

    C = [[c[(i-j) % N] for j in range(N)] for i in range(N)]
    for i in range(N):
        for j in range(N):
            check("rational_projector_idempotence", sum(C[i][k]*C[k][j] for k in range(N)) == N*C[i][j])
            check("rational_projector_symmetry", C[i][j] == C[j][i])
    check("rational_projector_trace", Fraction(sum(C[i][i] for i in range(N)),N) == len(U))

    # A fully integer signal: c_12(n) + 3*cos(pi*n/2) + 2.
    cos3 = [1,0,-1,0] * 3
    x = [c[i] + 3*cos3[i] + 2 for i in range(N)]
    projected = [Fraction(sum(C[i][j]*x[j] for j in range(N)),N) for i in range(N)]
    residual = [Fraction(x[i])-projected[i] for i in range(N)]
    check("filter_recovers_primitive_component", projected == c)
    check("filter_residual_orthogonality", sum(projected[i]*residual[i] for i in range(N)) == 0)
    check("filter_energy_split", sum(v*v for v in x) == sum(v*v for v in projected)+sum(v*v for v in residual))
    check("filter_exact_energies", (sum(v*v for v in x), sum(v*v for v in projected), sum(v*v for v in residual)) == (150,48,102))

    # All six divisor shells in the common ambient space C^12.
    ds = divisors(N)
    shells = {d: [ramanujan(d,n) for n in range(N)] for d in ds}
    for d in ds:
        for e in ds:
            product = convolution(shells[d], shells[e])
            for n in range(N):
                check("divisor_shell_orthogonality", product[n] == (N*shells[d][n] if d==e else 0))
    for n in range(N):
        check("divisor_shell_completeness", sum(shells[d][n] for d in ds) == (N if n==0 else 0))

    p_before = [Fraction(v*v,N*len(U)) for v in c]
    p_after = [Fraction(1,len(U)) if k in U else Fraction(0) for k in range(N)]
    check("quantum_normalization_exact", sum(v*v for v in c) == N*len(U))
    check("quantum_normalization_exact", sum(p_before) == 1 and sum(p_after) == 1)

    # Replacing c by |c| keeps probabilities in the sample basis but changes phases.
    for n in range(N):
        check("phase_erasure_preserves_sample_probabilities", abs(c[n])**2 == c[n]**2)
        check("phase_erasure_has_period_six", abs(c[(n+6)%N]) == abs(c[n]))
    for k in U:
        coefficient = ZERO
        for n in range(N):
            coefficient = add(coefficient, scale(abs(c[n]), powers[(-k*n)%N]))
        check("phase_erasure_removes_all_primitive_modes", coefficient == ZERO)

    # Finite regression beyond the illustrated modulus. This is NOT a universal proof.
    for q in range(2,65):
        cq = [ramanujan(q,n) for n in range(q)]
        phi = sum(gcd(a,q)==1 for a in range(q))
        check("q_2_to_64_energy_identity", sum(v*v for v in cq) == q*phi)
        check("q_2_to_64_idempotent_kernel", convolution(cq,cq) == [q*v for v in cq])
        for n in range(q):
            check("q_2_to_64_divisor_reconstruction", sum(ramanujan(d,n) for d in divisors(q)) == (q if n==0 else 0))

    result = {
        "status": "PASS", "modulus": N, "coprime_modes": U, "signal": c,
        "exact_checks": checks, "exact_assertion_count": sum(checks.values()),
        "classical_filter_input": x,
        "classical_filter_output": [str(v) for v in projected],
        "classical_filter_residual": [str(v) for v in residual],
        "energy_split": {"input":150,"retained":48,"residual":102},
        "probabilities_before": [str(v) for v in p_before],
        "probabilities_after": [str(v) for v in p_after],
        "normalization": "psi_n = c_12(n)/sqrt(48); u_k = 1/2 on {1,5,7,11}",
        "proof_boundary": "Finite exact checks plus separately stated algebraic proofs. No Lean run, hardware run, circuit synthesis, or quantum speedup claim."
    }
    try:
        import numpy as np
    except ImportError:
        result["numerical_checks"] = {"status":"NOT RUN", "reason":"NumPy unavailable; exact checks completed."}
    else:
        index = np.arange(N)
        F = np.exp(2j*np.pi*np.outer(index,index)/N)/np.sqrt(N)
        u = np.array([0.5 if k in U else 0.0 for k in range(N)])
        psi = np.array(c, dtype=float)/np.sqrt(48)
        D = np.diag([1 if k in U else 0 for k in range(N)])
        P = np.array(C,dtype=float)/N
        metrics = {
            "unitarity_max_error": float(np.max(np.abs(F.conj().T@F-np.eye(N)))),
            "state_preparation_max_error": float(np.max(np.abs(F@u-psi))),
            "inverse_QFT_max_error": float(np.max(np.abs(F.conj().T@psi-u))),
            "projector_transport_max_error": float(np.max(np.abs(F@D@F.conj().T-P))),
            "phase_erased_primitive_probability": float(np.sum(np.abs((F.conj().T@np.abs(psi))[U])**2)),
        }
        tolerance = 1e-12
        if max(metrics.values()) >= tolerance:
            raise AssertionError(f"numerical check exceeds {tolerance}: {metrics}")
        result["numerical_checks"] = {"status":"PASS", "tolerance":tolerance, **metrics}
    return result


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=Path("verification.json"))
    args = parser.parse_args()
    report = main()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report,indent=2)+"\n", encoding="utf-8")
    print(json.dumps(report,indent=2))
