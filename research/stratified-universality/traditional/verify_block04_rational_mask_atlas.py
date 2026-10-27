from __future__ import annotations

from dataclasses import dataclass
from itertools import product
from pathlib import Path
from collections import deque
import json
import math

ROOT = Path(__file__).resolve().parent
OUT = ROOT / "generated" / "block04_rational_mask_atlas_validation.json"


def inv_mod(a: int, p: int) -> int:
    a %= p
    if a == 0:
        raise ZeroDivisionError("zero has no inverse")
    return pow(a, p - 2, p)


def trim(a: list[int] | tuple[int, ...], p: int) -> tuple[int, ...]:
    out = [x % p for x in a]
    while len(out) > 1 and out[-1] == 0:
        out.pop()
    return tuple(out or [0])


def degree(a: tuple[int, ...]) -> int:
    return -1 if a == (0,) else len(a) - 1


def poly_add(a: tuple[int, ...], b: tuple[int, ...], p: int) -> tuple[int, ...]:
    n = max(len(a), len(b))
    return trim([
        (a[i] if i < len(a) else 0) + (b[i] if i < len(b) else 0)
        for i in range(n)
    ], p)


def poly_sub(a: tuple[int, ...], b: tuple[int, ...], p: int) -> tuple[int, ...]:
    n = max(len(a), len(b))
    return trim([
        (a[i] if i < len(a) else 0) - (b[i] if i < len(b) else 0)
        for i in range(n)
    ], p)


def poly_mul(a: tuple[int, ...], b: tuple[int, ...], p: int) -> tuple[int, ...]:
    if a == (0,) or b == (0,):
        return (0,)
    out = [0] * (len(a) + len(b) - 1)
    for i, ai in enumerate(a):
        for j, bj in enumerate(b):
            out[i + j] = (out[i + j] + ai * bj) % p
    return trim(out, p)


def poly_pow(a: tuple[int, ...], n: int, p: int) -> tuple[int, ...]:
    out = (1,)
    base = a
    while n:
        if n & 1:
            out = poly_mul(out, base, p)
        base = poly_mul(base, base, p)
        n >>= 1
    return out


def poly_scale(a: tuple[int, ...], c: int, p: int) -> tuple[int, ...]:
    return trim([(c * x) % p for x in a], p)


def poly_divmod(a: tuple[int, ...], b: tuple[int, ...], p: int) -> tuple[tuple[int, ...], tuple[int, ...]]:
    a = list(trim(a, p))
    b = trim(b, p)
    if b == (0,):
        raise ZeroDivisionError("polynomial division by zero")
    if degree(tuple(a)) < degree(b):
        return (0,), tuple(a)
    q = [0] * (degree(tuple(a)) - degree(b) + 1)
    inv_lc = inv_mod(b[-1], p)
    while trim(a, p) != (0,) and degree(trim(a, p)) >= degree(b):
        aa = list(trim(a, p))
        k = degree(tuple(aa)) - degree(b)
        c = aa[-1] * inv_lc % p
        q[k] = c
        for j, bj in enumerate(b):
            aa[j + k] = (aa[j + k] - c * bj) % p
        a = list(trim(aa, p))
    return trim(q, p), trim(a, p)


def poly_exact_div(a: tuple[int, ...], b: tuple[int, ...], p: int) -> tuple[int, ...]:
    q, r = poly_divmod(a, b, p)
    if r != (0,):
        raise ValueError("non-exact polynomial division")
    return q


def poly_gcd(a: tuple[int, ...], b: tuple[int, ...], p: int) -> tuple[int, ...]:
    a = trim(a, p)
    b = trim(b, p)
    while b != (0,):
        _, r = poly_divmod(a, b, p)
        a, b = b, r
    if a == (0,):
        return (0,)
    return poly_scale(a, inv_mod(a[-1], p), p)


def cartier(poly: tuple[int, ...], digit: int, p: int) -> tuple[int, ...]:
    coeffs = [poly[i] for i in range(digit, len(poly), p)]
    return trim(coeffs or [0], p)


def compiler_degree_bound(A: tuple[int, ...], B: tuple[int, ...], p: int) -> int:
    a = degree(A)
    b = degree(B)
    c = a + (p - 2) * b
    return max(b, math.ceil(c / (p - 1)))


def transition(P: tuple[int, ...], A: tuple[int, ...], B: tuple[int, ...], digit: int, p: int) -> tuple[int, ...]:
    H = poly_mul(A, poly_pow(B, p - 2, p), p)
    return cartier(poly_mul(P, H, p), digit, p)


def series_coefficients(A: tuple[int, ...], B: tuple[int, ...], p: int, count: int) -> list[int]:
    """Solve B(z)F(z)=A(z)F(z^p), F(0)=1, recursively."""
    coeffs = [0] * count
    coeffs[0] = 1
    for n in range(1, count):
        rhs = 0
        for j, aj in enumerate(A):
            m = n - j
            if m >= 0 and m % p == 0:
                rhs = (rhs + aj * coeffs[m // p]) % p
        lhs_known = 0
        for i in range(1, len(B)):
            if n - i >= 0:
                lhs_known = (lhs_known + B[i] * coeffs[n - i]) % p
        coeffs[n] = (rhs - lhs_known) * inv_mod(B[0], p) % p
    return coeffs


def compiler_coefficient(A: tuple[int, ...], B: tuple[int, ...], p: int, n: int) -> int:
    P = B
    if n == 0:
        return P[0] * inv_mod(B[0], p) % p
    while n:
        digit = n % p
        n //= p
        P = transition(P, A, B, digit, p)
    return P[0] * inv_mod(B[0], p) % p


def reachable_numerators(A: tuple[int, ...], B: tuple[int, ...], p: int) -> tuple[int, set[tuple[int, ...]], dict[tuple[int, ...], tuple[tuple[int, ...], ...]]]:
    D = compiler_degree_bound(A, B, p)
    start = B
    seen = {start}
    queue: deque[tuple[int, ...]] = deque([start])
    transitions: dict[tuple[int, ...], tuple[tuple[int, ...], ...]] = {}
    while queue:
        P = queue.popleft()
        row = tuple(transition(P, A, B, d, p) for d in range(p))
        transitions[P] = row
        for Q in row:
            if degree(Q) > D:
                raise AssertionError("degree bound failed")
            if Q not in seen:
                seen.add(Q)
                queue.append(Q)
    return D, seen, transitions


def vector(poly: tuple[int, ...], width: int) -> list[int]:
    return [poly[i] if i < len(poly) else 0 for i in range(width)]


def rank_mod(rows: list[list[int]], p: int) -> int:
    if not rows:
        return 0
    M = [[x % p for x in row] for row in rows]
    m = len(M)
    n = len(M[0])
    r = 0
    for c in range(n):
        pivot = next((i for i in range(r, m) if M[i][c] % p), None)
        if pivot is None:
            continue
        M[r], M[pivot] = M[pivot], M[r]
        inv = inv_mod(M[r][c], p)
        M[r] = [(x * inv) % p for x in M[r]]
        for i in range(m):
            if i != r and M[i][c] % p:
                factor = M[i][c] % p
                M[i] = [(M[i][j] - factor * M[r][j]) % p for j in range(n)]
        r += 1
        if r == m:
            break
    return r


def word_digits(n: int, p: int) -> list[int]:
    if n == 0:
        return []
    out = []
    while n:
        out.append(n % p)
        n //= p
    return out


def state_output_after(P: tuple[int, ...], A: tuple[int, ...], B: tuple[int, ...], p: int, n: int) -> int:
    for digit in word_digits(n, p):
        P = transition(P, A, B, digit, p)
    return P[0] * inv_mod(B[0], p) % p


def first_difference_witness(P: tuple[int, ...], Q: tuple[int, ...], A: tuple[int, ...], B: tuple[int, ...], p: int, D: int) -> int | None:
    """Find a coefficient position proving distinct future behavior.

    Theta(P)-Theta(Q)=(P-Q)F/B and F/B is a unit. The first nonzero
    coefficient therefore occurs no later than degree(P-Q)<=D.
    """
    for n in range(D + 1):
        if state_output_after(P, A, B, p, n) != state_output_after(Q, A, B, p, n):
            return n
    return None


def polynomial_nth_root(poly: tuple[int, ...], n: int, p: int) -> tuple[int, ...] | None:
    """Brute exact root, sufficient for the finite validation ranges."""
    poly = trim(poly, p)
    if poly == (0,):
        return (0,)
    if degree(poly) % n != 0:
        return None
    root_degree = degree(poly) // n
    for tail in product(range(p), repeat=root_degree):
        candidate = trim((1, *tail), p)
        if degree(candidate) != root_degree:
            continue
        if poly_pow(candidate, n, p) == poly:
            return candidate
    return None


def rational_collapse_roots(A: tuple[int, ...], B: tuple[int, ...], p: int) -> tuple[tuple[int, ...], tuple[int, ...]] | None:
    n = p - 1
    root_A = polynomial_nth_root(A, n, p)
    root_B = polynomial_nth_root(B, n, p)
    if root_A is None or root_B is None:
        return None
    # F^(p-1)=B/A, so F=root_B/root_A with constant term one.
    return root_B, root_A


def primitive_polynomials(p: int, max_degree: int) -> list[tuple[int, ...]]:
    """All polynomials of degree at most max_degree with constant term one."""
    out = []
    for tail in product(range(p), repeat=max_degree):
        out.append(trim((1, *tail), p))
    return sorted(set(out), key=lambda q: (degree(q), q))


@dataclass
class Ledger:
    checks: int = 0
    failures: list[dict] | None = None

    def __post_init__(self) -> None:
        if self.failures is None:
            self.failures = []

    def check(self, condition: bool, label: str, context: dict) -> None:
        self.checks += 1
        if not condition:
            self.failures.append({"label": label, "context": context})


def validate_mask(A: tuple[int, ...], B: tuple[int, ...], p: int, ledger: Ledger, coefficient_count: int = 180) -> dict:
    context = {"p": p, "A": list(A), "B": list(B)}
    ledger.check(A[0] == 1 and B[0] == 1, "unit normalization", context)
    ledger.check(poly_gcd(A, B, p) == (1,), "reduced mask", context)

    D, states, transitions = reachable_numerators(A, B, p)
    width = D + 1
    rank = rank_mod([vector(P, width) for P in states], p)
    kappa = len(states)

    # Verify invariant degree on the entire finite ambient numerator space.
    ambient = [trim(v, p) for v in product(range(p), repeat=width)]
    for P in ambient:
        for d in range(p):
            Q = transition(P, A, B, d, p)
            ledger.check(degree(Q) <= D, "ambient degree invariance", {**context, "P": list(P), "digit": d, "D": D, "Q": list(Q)})

    # Compare two independent coefficient constructions.
    direct = series_coefficients(A, B, p, coefficient_count)
    compiled = [compiler_coefficient(A, B, p, n) for n in range(coefficient_count)]
    ledger.check(direct == compiled, "compiler coefficient semantics", {**context, "count": coefficient_count})

    # Every distinct reachable numerator has distinguishable future output.
    ordered_states = sorted(states, key=lambda q: (degree(q), q))
    for i, P in enumerate(ordered_states):
        for Q in ordered_states[i + 1:]:
            witness = first_difference_witness(P, Q, A, B, p, D)
            ledger.check(witness is not None, "reachable numerator behavioral injectivity", {**context, "P": list(P), "Q": list(Q), "D": D})

    ledger.check(rank <= kappa, "rank at most kernel states", {**context, "rank": rank, "kappa": kappa})
    ledger.check(kappa <= p ** rank, "kernel states at most field vectors", {**context, "rank": rank, "kappa": kappa})
    ledger.check(rank <= D + 1, "Cartier rank compiler bound", {**context, "rank": rank, "D": D})
    ledger.check(kappa <= p ** (D + 1), "automaton compiler bound", {**context, "kappa": kappa, "D": D})

    collapse = rational_collapse_roots(A, B, p)
    if p == 2:
        ledger.check(collapse is not None, "characteristic two collapse", context)
    if collapse is not None:
        num_F, den_F = collapse
        # Check B*F=A*F(z^p) by cross multiplication:
        # B*num_F/den_F = A*num_F(z^p)/den_F(z^p).
        num_F_p = tuple(x if i % p == 0 else 0 for i, x in enumerate([0] * ((len(num_F)-1)*p + 1)))
        # Build substitution directly.
        num_sub = [0] * ((len(num_F) - 1) * p + 1)
        den_sub = [0] * ((len(den_F) - 1) * p + 1)
        for i, x in enumerate(num_F):
            num_sub[i * p] = x
        for i, x in enumerate(den_F):
            den_sub[i * p] = x
        left = poly_mul(poly_mul(B, num_F, p), trim(den_sub, p), p)
        right = poly_mul(poly_mul(A, trim(num_sub, p), p), den_F, p)
        ledger.check(left == right, "rational collapse functional equation", {**context, "F_num": list(num_F), "F_den": list(den_F)})

    return {
        "p": p,
        "A": list(A),
        "B": list(B),
        "D": D,
        "ambient_dimension": D + 1,
        "ambient_state_bound": p ** (D + 1),
        "reachable_numerator_states": kappa,
        "cartier_rank": rank,
        "collapse": collapse is not None,
        "prefix": direct[:36],
        "states": [list(P) for P in ordered_states],
        "transitions": {
            ",".join(map(str, P)): [list(Q) for Q in transitions[P]]
            for P in ordered_states
        },
        "outputs": {",".join(map(str, P)): P[0] % p for P in ordered_states},
    }


def main() -> None:
    OUT.parent.mkdir(parents=True, exist_ok=True)
    ledger = Ledger()
    ranges = {2: 3, 3: 2, 5: 1}
    records = []
    masks_considered = 0
    collapse_count = 0
    noncollapse_count = 0

    for p, max_degree in ranges.items():
        polys = primitive_polynomials(p, max_degree)
        for A in polys:
            for B in polys:
                if poly_gcd(A, B, p) != (1,):
                    continue
                masks_considered += 1
                row = validate_mask(A, B, p, ledger)
                records.append(row)
                if row["collapse"]:
                    collapse_count += 1
                else:
                    noncollapse_count += 1

    named_specs = {
        "cantor_digit_indicator_F3": (3, (1, 1), (1,)),
        "square_root_denominator_F3": (3, (1,), (1, 1)),
        "alternating_collapse_F3": (3, (1, 2, 1), (1,)),
        "finite_transient_F2": (2, (1,), (1, 1, 1)),
    }
    named = {}
    by_key = {(r["p"], tuple(r["A"]), tuple(r["B"])): r for r in records}
    for name, key in named_specs.items():
        if key not in by_key:
            # Named masks may have degree below the enumerated maximum but should always occur.
            p, A, B = key
            by_key[key] = validate_mask(A, B, p, ledger)
        named[name] = by_key[key]

    payload = {
        "passed": not ledger.failures,
        "checks": ledger.checks,
        "failures": ledger.failures,
        "arithmetic": "exact polynomial, finite-field, Cartier-transition, and formal-series arithmetic",
        "enumeration": {
            "prime_fields_and_max_mask_degree": {str(k): v for k, v in ranges.items()},
            "reduced_unit_masks": masks_considered,
            "rational_collapse_masks": collapse_count,
            "noncollapse_masks": noncollapse_count,
        },
        "named_examples": named,
        "state_hierarchy": "r_p(F) <= kappa_p(F) <= p^{r_p(F)} <= p^{D+1}",
    }
    OUT.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    print(f"BLOCK04_RATIONAL_MASK_ATLAS={'PASS' if payload['passed'] else 'FAIL'}")
    print(f"masks={masks_considered}")
    print(f"checks={ledger.checks}")
    print(f"failures={len(ledger.failures)}")
    print(f"output={OUT}")
    if ledger.failures:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
