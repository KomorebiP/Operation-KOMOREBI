from __future__ import annotations

from dataclasses import dataclass
from itertools import product
from pathlib import Path
from typing import Iterable
import json
import math

ROOT = Path(__file__).resolve().parent
OUT = ROOT / "generated" / "block03_periodic_atlas_validation.json"


def inv_mod(a: int, p: int) -> int:
    a %= p
    if a == 0:
        raise ZeroDivisionError("zero has no inverse")
    return pow(a, p - 2, p)


def trim(a: list[int], p: int) -> list[int]:
    a = [x % p for x in a]
    while len(a) > 1 and a[-1] == 0:
        a.pop()
    return a or [0]


def poly_add(a: list[int], b: list[int], p: int) -> list[int]:
    n = max(len(a), len(b))
    out = [0] * n
    for i in range(n):
        out[i] = ((a[i] if i < len(a) else 0) + (b[i] if i < len(b) else 0)) % p
    return trim(out, p)


def poly_sub(a: list[int], b: list[int], p: int) -> list[int]:
    n = max(len(a), len(b))
    out = [0] * n
    for i in range(n):
        out[i] = ((a[i] if i < len(a) else 0) - (b[i] if i < len(b) else 0)) % p
    return trim(out, p)


def poly_mul(a: list[int], b: list[int], p: int) -> list[int]:
    out = [0] * (len(a) + len(b) - 1)
    for i, ai in enumerate(a):
        for j, bj in enumerate(b):
            out[i + j] = (out[i + j] + ai * bj) % p
    return trim(out, p)


def poly_scale(a: list[int], c: int, p: int) -> list[int]:
    return trim([(c * x) % p for x in a], p)


def poly_divmod(a: list[int], b: list[int], p: int) -> tuple[list[int], list[int]]:
    a = trim(a[:], p)
    b = trim(b[:], p)
    if b == [0]:
        raise ZeroDivisionError("polynomial division by zero")
    if len(a) < len(b):
        return [0], a
    q = [0] * (len(a) - len(b) + 1)
    inv_lc = inv_mod(b[-1], p)
    while a != [0] and len(a) >= len(b):
        k = len(a) - len(b)
        c = a[-1] * inv_lc % p
        q[k] = c
        for j, bj in enumerate(b):
            a[j + k] = (a[j + k] - c * bj) % p
        a = trim(a, p)
    return trim(q, p), a


def poly_exact_div(a: list[int], b: list[int], p: int) -> list[int]:
    q, r = poly_divmod(a, b, p)
    if r != [0]:
        raise ValueError("non-exact polynomial division")
    return q


def poly_gcd(a: list[int], b: list[int], p: int) -> list[int]:
    a = trim(a, p)
    b = trim(b, p)
    while b != [0]:
        _, r = poly_divmod(a, b, p)
        a, b = b, r
    if a == [0]:
        return [0]
    return poly_scale(a, inv_mod(a[-1], p), p)


def poly_substitute_power(a: list[int], power: int, p: int) -> list[int]:
    out = [0] * ((len(a) - 1) * power + 1)
    for i, ai in enumerate(a):
        out[i * power] = ai % p
    return trim(out, p)


def normalized_fraction(num: list[int], den: list[int], p: int) -> tuple[list[int], list[int]]:
    g = poly_gcd(num, den, p)
    num = poly_exact_div(num, g, p)
    den = poly_exact_div(den, g, p)
    scale = inv_mod(den[0], p)
    return poly_scale(num, scale, p), poly_scale(den, scale, p)


def poly_divides(a: list[int], b: list[int], p: int) -> bool:
    # a divides b
    _, r = poly_divmod(b, a, p)
    return r == [0]


def berlekamp_massey(sequence: list[int], p: int) -> list[int]:
    """Return Q=[1,c1,...,cL] with s_n+sum c_i s_{n-i}=0 mod p."""
    c = [1]
    b = [1]
    L = 0
    m = 1
    bb = 1
    for n in range(len(sequence)):
        d = sequence[n] % p
        for i in range(1, L + 1):
            d = (d + c[i] * sequence[n - i]) % p
        if d == 0:
            m += 1
            continue
        t = c[:]
        coef = d * inv_mod(bb, p) % p
        needed = len(b) + m
        if len(c) < needed:
            c += [0] * (needed - len(c))
        for j, bj in enumerate(b):
            c[j + m] = (c[j + m] - coef * bj) % p
        if 2 * L <= n:
            L = n + 1 - L
            b = t
            bb = d
            m = 1
        else:
            m += 1
    return trim(c[: L + 1], p)


def minimal_period(word: tuple[int, ...]) -> int:
    T = len(word)
    for d in range(1, T + 1):
        if T % d == 0 and all(word[i] == word[i % d] for i in range(T)):
            return d
    return T


def periodic_terms(word: tuple[int, ...], n: int) -> list[int]:
    return [word[i % len(word)] for i in range(n)]


def multiplicative_order_mod(a: int, m: int) -> int:
    if m == 1:
        return 1
    if math.gcd(a, m) != 1:
        raise ValueError("multiplicative order requires coprimality")
    r = 1
    v = a % m
    while v != 1:
        v = (v * a) % m
        r += 1
        if r > m + 1:
            raise RuntimeError("order search failed")
    return r


def u_set(p: int, T: int) -> set[int]:
    seen: set[int] = set()
    u = 1 % T
    while u not in seen:
        seen.add(u)
        u = (p * u) % T
    return seen


def predicted_u_size(p: int, T: int) -> int:
    nu = 0
    M = T
    while M % p == 0:
        M //= p
        nu += 1
    return nu + multiplicative_order_mod(p, M)


def kernel_automaton(word: tuple[int, ...], p: int) -> dict:
    T = len(word)
    queue = [(1 % T, 0)]
    seen_pairs: set[tuple[int, int]] = set()
    pair_semantics: dict[tuple[int, int], tuple[int, ...]] = {}
    while queue:
        u, r = queue.pop(0)
        pair = (u % T, r % T)
        if pair in seen_pairs:
            continue
        seen_pairs.add(pair)
        pair_semantics[pair] = tuple(word[(pair[0] * n + pair[1]) % T] for n in range(T))
        for d in range(p):
            nxt = ((p * pair[0]) % T, (pair[1] + pair[0] * d) % T)
            if nxt not in seen_pairs:
                queue.append(nxt)
    semantic_to_id: dict[tuple[int, ...], int] = {}
    reps: dict[tuple[int, ...], tuple[int, int]] = {}
    for pair, sem in pair_semantics.items():
        if sem not in semantic_to_id:
            semantic_to_id[sem] = len(semantic_to_id)
            reps[sem] = pair
    transitions: dict[int, list[int]] = {}
    outputs: dict[int, int] = {}
    for sem, sid in semantic_to_id.items():
        u, r = reps[sem]
        outputs[sid] = word[r]
        row = []
        for d in range(p):
            nxt = ((p * u) % T, (r + u * d) % T)
            nxt_sem = pair_semantics[nxt]
            row.append(semantic_to_id[nxt_sem])
        transitions[sid] = row
    start_sem = tuple(word[n % T] for n in range(T))
    return {
        "state_count": len(semantic_to_id),
        "reachable_pair_count": len(seen_pairs),
        "transitions": transitions,
        "outputs": outputs,
        "start_state": semantic_to_id[start_sem],
        "semantic_states": [list(s) for s, _ in sorted(semantic_to_id.items(), key=lambda kv: kv[1])],
    }


def compiler_degree_bound(mask_num: list[int], mask_den: list[int], p: int) -> int:
    a = len(trim(mask_num, p)) - 1
    b = len(trim(mask_den, p)) - 1
    c = a + (p - 2) * b
    return max(b, math.ceil(c / (p - 1)))


@dataclass
class CheckLedger:
    checks: int = 0
    failures: list[dict] | None = None

    def __post_init__(self) -> None:
        if self.failures is None:
            self.failures = []

    def check(self, condition: bool, label: str, context: dict) -> None:
        self.checks += 1
        if not condition:
            self.failures.append({"label": label, "context": context})


def validate_case(p: int, word: tuple[int, ...], ledger: CheckLedger) -> dict:
    T = len(word)
    context = {"p": p, "word": list(word), "T": T}
    terms = periodic_terms(word, max(8 * T, 32))
    Q = berlekamp_massey(terms, p)  # low-to-high reduced OGF denominator
    L = len(Q) - 1
    m = list(reversed(Q))  # low-to-high coefficients of x-polynomial

    xT_minus_1 = [(-1) % p] + [0] * (T - 1) + [1]
    one_minus_zT = [1] + [0] * (T - 1) + [(-1) % p]
    ledger.check(poly_divides(m, xT_minus_1, p), "minimal recurrence divides x^T-1", context)
    ledger.check(poly_divides(Q, one_minus_zT, p), "reduced denominator divides 1-z^T", context)
    least_m = next(N for N in range(1, T + 1)
                   if poly_divides(m, [(-1) % p] + [0] * (N - 1) + [1], p))
    least_q = next(N for N in range(1, T + 1)
                   if poly_divides(Q, [1] + [0] * (N - 1) + [(-1) % p], p))
    ledger.check(least_m == T, "minimal period recovered from recurrence", context)
    ledger.check(least_q == T, "minimal period recovered from denominator", context)

    P = []
    for n in range(L + 1):
        val = 0
        for i in range(min(n, L) + 1):
            val += Q[i] * terms[n - i]
        P.append(val % p)
    P = trim(P, p)
    P, Qred = normalized_fraction(P, Q, p)
    ledger.check(Qred == Q, "BM denominator is reduced against OGF numerator", context)

    Pp = poly_substitute_power(P, p, p)
    Qp = poly_substitute_power(Qred, p, p)
    Araw = poly_mul(P, Qp, p)
    Braw = poly_mul(Qred, Pp, p)
    A, B = normalized_fraction(Araw, Braw, p)
    # Check F = (A/B) F(z^p) by cross multiplication.
    lhs = poly_mul(poly_mul(P, B, p), Qp, p)
    rhs = poly_mul(poly_mul(A, Pp, p), Qred, p)
    ledger.check(trim(lhs, p) == trim(rhs, p), "functional Mahler identity", context)

    aut = kernel_automaton(word, p)
    ledger.check(aut["state_count"] <= aut["reachable_pair_count"],
                 "kernel quotient does not increase states", context)
    U = u_set(p, T)
    ledger.check(len(U) == predicted_u_size(p, T), "exact U_p(T) size", context)
    ledger.check(aut["reachable_pair_count"] <= T * len(U), "reachable pair bound", context)
    ledger.check(aut["state_count"] <= T * len(U), "minimal DFAO state bound", context)

    transitions = aut["transitions"]
    outputs = aut["outputs"]
    for n in range(8 * T + 8):
        state = aut["start_state"]
        nn = n
        digits = [0] if nn == 0 else []
        while nn:
            digits.append(nn % p)
            nn //= p
        for d in digits:
            state = transitions[state][d]
        ledger.check(outputs[state] == word[n % T], "DFAO coefficient output", {**context, "n": n})

    D = compiler_degree_bound(A, B, p)
    ledger.check(aut["state_count"] <= p ** (D + 1), "Cartier compiler state bound", context)

    return {
        "p": p,
        "word": list(word),
        "period": T,
        "minimal_recurrence_coefficients_high_to_low": list(reversed(m)),
        "reduced_ogf_numerator_coefficients_low_to_high": P,
        "reduced_ogf_denominator_coefficients_low_to_high": Qred,
        "mask_numerator_coefficients_low_to_high": A,
        "mask_denominator_coefficients_low_to_high": B,
        "recurrence_order": L,
        "p_kernel_states": aut["state_count"],
        "reachable_pair_states": aut["reachable_pair_count"],
        "u_set_size": len(U),
        "compiler_degree_bound": D,
        "compiler_automaton_bound": p ** (D + 1),
        "automaton": aut,
    }


def main() -> None:
    ledger = CheckLedger()
    cases: list[dict] = []
    ranges = {2: 8, 3: 6}
    for p, max_T in ranges.items():
        for T in range(1, max_T + 1):
            for tail in product(range(p), repeat=T - 1):
                word = (1,) + tuple(tail)
                if minimal_period(word) != T:
                    continue
                cases.append(validate_case(p, word, ledger))

    named_words = {
        "even_indicator_F2": (2, (1, 0)),
        "alternating_unit_F3": (3, (1, 2)),
        "period_three_F2": (2, (1, 1, 0)),
    }
    named = {}
    for name, (p, word) in named_words.items():
        named[name] = next(row for row in cases if row["p"] == p and tuple(row["word"]) == word)

    result = {
        "artifact": "Block 03 periodic linear-digital-functional-Mahler atlas validation",
        "arithmetic": "exact prime-field and polynomial arithmetic",
        "enumeration": {
            "prime_fields_and_max_period": ranges,
            "primitive_unit_periodic_words": len(cases),
        },
        "checks": ledger.checks,
        "failures": ledger.failures,
        "passed": not ledger.failures,
        "named_examples": named,
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({
        "passed": result["passed"],
        "cases": len(cases),
        "checks": ledger.checks,
        "failures": len(ledger.failures),
        "output": str(OUT),
    }, indent=2))
    if ledger.failures:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
