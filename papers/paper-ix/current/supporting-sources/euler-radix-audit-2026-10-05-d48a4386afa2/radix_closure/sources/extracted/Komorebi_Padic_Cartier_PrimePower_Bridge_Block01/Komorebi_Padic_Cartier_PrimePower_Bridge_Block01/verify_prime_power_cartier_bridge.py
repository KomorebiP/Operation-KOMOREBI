from __future__ import annotations

from dataclasses import dataclass
from itertools import product
from math import ceil, comb
from random import Random
import hashlib
import json
from pathlib import Path

SEED = 20260917
PRIMES = (2, 3, 5, 7)
EXPONENTS = (1, 2, 3, 4)
RANDOM_MASKS_PER_PAIR = 5
NMAX = 120


def trim(a):
    a = list(a)
    while len(a) > 1 and a[-1] == 0:
        a.pop()
    return a


def padd(a, b, m=None):
    n = max(len(a), len(b))
    c = [0] * n
    for i in range(n):
        c[i] = (a[i] if i < len(a) else 0) + (b[i] if i < len(b) else 0)
        if m is not None:
            c[i] %= m
    return trim(c)


def pmul(a, b, m=None):
    c = [0] * (len(a) + len(b) - 1)
    for i, x in enumerate(a):
        for j, y in enumerate(b):
            c[i + j] += x * y
            if m is not None:
                c[i + j] %= m
    if m is not None:
        c = [x % m for x in c]
    return trim(c)


def ppow(a, n, m=None):
    out = [1]
    base = list(a)
    while n:
        if n & 1:
            out = pmul(out, base, m)
        n //= 2
        if n:
            base = pmul(base, base, m)
    return out


def pscale(a, c, m=None):
    out = [c * x for x in a]
    if m is not None:
        out = [x % m for x in out]
    return trim(out)


def subst_p(a, p):
    out = [0] * ((len(a) - 1) * p + 1)
    for i, x in enumerate(a):
        out[p * i] = x
    return trim(out)


def cartier_poly(a, d, p, m):
    if d >= len(a):
        return [0]
    out = [a[i] % m for i in range(d, len(a), p)]
    return trim(out or [0])


def frobenius_defect(B, p):
    bp = ppow(B, p)
    bz = subst_p(B, p)
    n = max(len(bp), len(bz))
    diff = [
        (bp[i] if i < len(bp) else 0) - (bz[i] if i < len(bz) else 0)
        for i in range(n)
    ]
    assert all(x % p == 0 for x in diff)
    return trim([x // p for x in diff])


@dataclass(frozen=True)
class Bounds:
    layers: int
    degree: int
    defect_degree: int
    max_remainder_power: int


def bridge_bounds(A, B, p, r):
    a = len(trim(A)) - 1
    b = len(trim(B)) - 1
    E = frobenius_defect(B, p)
    e = 0 if E == [0] else len(E) - 1
    s = ceil(r / (p - 1))
    L = (r - 1) + s
    ts = []
    for ell in range(1, L + 1):
        q = ceil((ell + 1) / p)
        t = p * q - (ell + 1)
        assert 0 <= t <= p - 1
        assert q + r - 1 <= L
        ts.append(t)
    T = max(ts, default=0)
    C = a + T * b + (r - 1) * e
    D = max(b, ceil(C / (p - 1)))
    # r=1 must reproduce the original mod-p degree bound exactly.
    if r == 1:
        old = max(b, ceil((a + (p - 2) * b) / (p - 1)))
        assert L == 1 and D == old
    return Bounds(L, D, e, T), E


def apply_digit(state, digit, A, B, p, r, bounds, E):
    m = p ** r
    L, D = bounds.layers, bounds.degree
    out = [[0] for _ in range(L)]
    for ell in range(1, L + 1):
        P = state[ell - 1]
        if all((x % m) == 0 for x in P):
            continue
        q = ceil((ell + 1) / p)
        t = p * q - (ell + 1)
        H0 = pmul(P, A, m)
        if t:
            H0 = pmul(H0, ppow(B, t, m), m)
        Epow = [1]
        for k in range(r):
            if k:
                Epow = pmul(Epow, E, m)
            ell2 = q + k
            assert 1 <= ell2 <= L
            coeff = ((-1) ** k * comb(q + k - 1, k) * (p ** k)) % m
            H = pscale(pmul(H0, Epow, m), coeff, m)
            Q = cartier_poly(H, digit, p, m)
            assert len(Q) - 1 <= D
            out[ell2 - 1] = padd(out[ell2 - 1], Q, m)
    return out


def state_output(state, B, p, r):
    m = p ** r
    b0 = B[0] % m
    invb0 = pow(b0, -1, m)
    return sum((P[0] if P else 0) * pow(invb0, ell, m)
               for ell, P in enumerate(state, 1)) % m


def state_coefficient(n, A, B, p, r):
    bounds, E = bridge_bounds(A, B, p, r)
    m = p ** r
    state = [[0] for _ in range(bounds.layers)]
    state[0] = [x % m for x in B]  # (B/B)F = F
    x = n
    while x:
        d = x % p
        x //= p
        state = apply_digit(state, d, A, B, p, r, bounds, E)
    return state_output(state, B, p, r), bounds


def direct_coefficients(A, B, p, r, nmax):
    m = p ** r
    A = [x % m for x in A]
    B = [x % m for x in B]
    assert (A[0] - B[0]) % m == 0
    assert B[0] % p != 0
    invb0 = pow(B[0], -1, m)
    f = [0] * (nmax + 1)
    f[0] = 1
    for n in range(1, nmax + 1):
        rhs = 0
        for i, a in enumerate(A):
            if i <= n and (n - i) % p == 0:
                rhs = (rhs + a * f[(n - i) // p]) % m
        lhs_prev = 0
        for i in range(1, len(B)):
            if i <= n:
                lhs_prev = (lhs_prev + B[i] * f[n - i]) % m
        f[n] = (rhs - lhs_prev) * invb0 % m
    return f


def run():
    rng = Random(SEED)
    cases = 0
    coefficient_checks = 0
    max_layers = 0
    max_degree = 0
    examples = []

    curated = [
        ([1, 1], [1, -1], 3, 2),
        ([1, 1], [1, -1], 3, 4),
        ([1, 1, 1], [1], 2, 3),
        ([1, 0, 1], [1, 1], 2, 2),
        ([1, 2], [1, -1, 1], 5, 2),
    ]
    for A, B, p, r in curated:
        f = direct_coefficients(A, B, p, r, NMAX)
        last_bounds = None
        for n in range(NMAX + 1):
            g, bounds = state_coefficient(n, A, B, p, r)
            assert g == f[n], ("curated mismatch", A, B, p, r, n, g, f[n])
            last_bounds = bounds
            coefficient_checks += 1
        cases += 1
        max_layers = max(max_layers, last_bounds.layers)
        max_degree = max(max_degree, last_bounds.degree)
        examples.append({"A": A, "B": B, "p": p, "r": r,
                         "layers": last_bounds.layers, "degree": last_bounds.degree})

    for p in PRIMES:
        for r in EXPONENTS:
            for _ in range(RANDOM_MASKS_PER_PAIR):
                da = rng.randint(0, 3)
                db = rng.randint(0, 3)
                A = [rng.randint(-3, 3) for _ in range(da + 1)]
                B = [rng.randint(-3, 3) for _ in range(db + 1)]
                c = rng.choice(list(range(1, p)))
                A[0] = c
                B[0] = c
                if da and all(x == 0 for x in A[1:]):
                    A[-1] = 1
                if db and all(x == 0 for x in B[1:]):
                    B[-1] = 1
                A, B = trim(A), trim(B)
                f = direct_coefficients(A, B, p, r, NMAX)
                last_bounds = None
                for n in range(NMAX + 1):
                    g, bounds = state_coefficient(n, A, B, p, r)
                    assert g == f[n], ("random mismatch", A, B, p, r, n, g, f[n])
                    last_bounds = bounds
                    coefficient_checks += 1
                cases += 1
                max_layers = max(max_layers, last_bounds.layers)
                max_degree = max(max_degree, last_bounds.degree)

    result = {
        "schema": "komorebi-prime-power-cartier-bridge-verification-v1",
        "seed": SEED,
        "primes": list(PRIMES),
        "exponents": list(EXPONENTS),
        "random_masks_per_prime_exponent_pair": RANDOM_MASKS_PER_PAIR,
        "nmax": NMAX,
        "cases": cases,
        "coefficient_checks": coefficient_checks,
        "failures": 0,
        "max_layers_observed": max_layers,
        "max_degree_bound_observed": max_degree,
        "curated_examples": examples,
        "claim_boundary": (
            "This finite exact computation checks the derived correction-layer transition formula "
            "against an independent direct coefficient recurrence on the stated finite range. "
            "It does not by itself prove the unbounded theorem; the theorem requires the algebraic argument."
        ),
    }
    return result


if __name__ == "__main__":
    result = run()
    out = Path(__file__).with_name("verification_results.json")
    out.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2, sort_keys=True))
