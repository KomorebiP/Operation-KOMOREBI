from __future__ import annotations

import csv
import itertools
import json
import math
import random
import re
from collections import defaultdict
from fractions import Fraction
from pathlib import Path

import sympy as sp

ROOT = Path(__file__).resolve().parents[1]
TEX = ROOT / "PSC_Paper_IX_Strengthened_Annals_Edition.tex"
BIB = ROOT / "PSC_Paper_IX_Strengthened_Annals_Edition.bib"
LEGACY = ROOT / "legacy"

checks = 0
groups: list[tuple[str, int]] = []


def check(condition: bool, message: str = "") -> None:
    global checks
    checks += 1
    if not condition:
        raise AssertionError(message or f"check {checks} failed")


def run_group(name: str, fn) -> None:
    before = checks
    fn()
    groups.append((name, checks - before))


def vp_int(n: int, p: int) -> int:
    if n == 0:
        return 10**9
    n = abs(n)
    v = 0
    while n % p == 0:
        n //= p
        v += 1
    return v


def vp_frac(x: Fraction, p: int) -> int:
    if x == 0:
        return 10**9
    return vp_int(x.numerator, p) - vp_int(x.denominator, p)


def divisors(n: int) -> list[int]:
    return [d for d in range(1, n + 1) if n % d == 0]


def primes_upto(n: int) -> list[int]:
    return list(sp.primerange(2, n + 1))


def compressed_inverse(p: int, m: int, N: int) -> list[int]:
    e = [1]
    for n in range(1, N + 1):
        total = sum(math.comb(m * n, m * q) * e[q] for q in range(n))
        e.append((-total) % p)
    return e


def congruential_coefficients(N: int, j: int, nmax: int) -> list[Fraction]:
    c = [Fraction(1)]
    for n in range(1, nmax + 1):
        total = sum(Fraction(math.comb(N * n + j, N * q)) * c[q] for q in range(n))
        diag = math.comb(N * n + j, N * n)
        c.append(-total / diag)
    return c


def euler_numbers(nmax: int) -> list[int]:
    e = [0] * (nmax + 1)
    e[0] = 1
    for n in range(2, nmax + 1, 2):
        e[n] = -sum(math.comb(n, k) * e[n - k] for k in range(2, n + 1, 2))
    return e


def zigzag_odd(nmax: int, e: list[int]) -> dict[int, int]:
    out: dict[int, int] = {}
    for r in range((nmax + 1) // 2 + 1):
        n = 2 * r
        g = sum(math.comb(n, k) * e[k] * e[n - k] for k in range(0, n + 1))
        out[2 * r + 1] = ((-1) ** r) * g
    return out


def S(n: int, q: int) -> int:
    return sum(((-1) ** a) * (2 * a + 1) ** n for a in range(q))


def beta(r: int) -> Fraction:
    if r == 0:
        return Fraction(1)
    b = sp.bernoulli(2 * r)
    return Fraction(-2 ** (2 * r) * (2 * r - 1) * int(sp.numer(b)), math.factorial(2 * r) * int(sp.denom(b)))


def R_source(n: int) -> Fraction:
    return Fraction(3 ** (n + 2) - 1, 4 * (n + 1) * (n + 2))


def falling(n: int, k: int) -> int:
    if k > n:
        return 0
    return math.factorial(n) // math.factorial(n - k)


def finite_differences(values: list[int | Fraction]) -> list[int | Fraction]:
    row = list(values)
    c = []
    while row:
        c.append(row[0])
        row = [row[i + 1] - row[i] for i in range(len(row) - 1)]
    return c


def resultant_standard(f_expr, g_expr, var):
    f = sp.Poly(f_expr, var)
    g = sp.Poly(g_expr, var)
    m = f.degree()
    n = g.degree()
    fc = f.all_coeffs()
    gc = g.all_coeffs()
    rows = []
    for i in range(n):
        row = [0] * (m + n)
        row[i:i + m + 1] = fc
        rows.append(row)
    for i in range(m):
        row = [0] * (m + n)
        row[i:i + n + 1] = gc
        rows.append(row)
    return sp.expand(sp.Matrix(rows).det())


def matrix_rank_mod(M: tuple[int, ...], r: int, d: int, p: int) -> int:
    A = [[M[i * d + j] % p for j in range(d)] for i in range(r)]
    row = 0
    col = 0
    while row < r and col < d:
        pivot = next((i for i in range(row, r) if A[i][col] % p), None)
        if pivot is None:
            col += 1
            continue
        A[row], A[pivot] = A[pivot], A[row]
        inv = pow(A[row][col], -1, p)
        A[row] = [(x * inv) % p for x in A[row]]
        for i in range(r):
            if i != row and A[i][col] % p:
                c = A[i][col]
                A[i] = [(A[i][j] - c * A[row][j]) % p for j in range(d)]
        row += 1
        col += 1
    return row


def mat_vec_mod(M: tuple[int, ...], y: tuple[int, ...], r: int, d: int, p: int) -> tuple[int, ...]:
    return tuple(sum(M[i * d + j] * y[j] for j in range(d)) % p for i in range(r))


def group_hurwitz_and_period() -> None:
    for p in primes_upto(43):
        if p == 2:
            continue
        for m in divisors(p - 1):
            h = (p - 1) // m
            e = compressed_inverse(p, m, 6 * h + 8)
            for n in range(1, len(e) - h):
                check(e[n + h] == e[n], f"period failed p={p}, m={m}, n={n}")
            for n in range(1, min(len(e), 4 * h + 1)):
                total = sum(math.comb(m * n, m * q) * e[q] for q in range(n + 1)) % p
                check(total == 0, f"inverse recurrence failed p={p}, m={m}, n={n}")


def group_triangular_and_standard_windows() -> None:
    for N in range(1, 9):
        for j in range(N):
            c = congruential_coefficients(N, j, 10)
            for n in range(11):
                total = sum(Fraction(math.comb(N * n + j, N * q)) * c[q] for q in range(n + 1))
                check(total == (1 if n == 0 else 0), f"triangular inverse N={N}, j={j}, n={n}")
                D = math.prod(math.comb(N * r + j, N * r) for r in range(1, n + 1))
                check((c[n] * D).denominator == 1, f"denominator bound N={N}, j={j}, n={n}")
    for p in primes_upto(23):
        if p == 2:
            continue
        for m in divisors(p - 1):
            h = (p - 1) // m
            e = compressed_inverse(p, m, 4 * h + 10)
            addresses = range(p) if p <= 11 else sorted({0, 1, p // 2, p - 1})
            for j in addresses:
                c = congruential_coefficients(m * p, j, 4 * h + 6)
                for n in range(4 * h + 7):
                    den = c[n].denominator
                    check(den % p != 0, f"nonintegral standard coefficient p={p},m={m},j={j},n={n}")
                    residue = (c[n].numerator * pow(den, -1, p)) % p
                    check(residue == e[n] % p, f"address independence p={p},m={m},j={j},n={n}")
                for n in range(1, 3 * h + 4):
                    a = c[n]
                    b = c[n + h]
                    ar = a.numerator * pow(a.denominator, -1, p) % p
                    br = b.numerator * pow(b.denominator, -1, p) % p
                    check(ar == br, f"window period p={p},m={m},j={j},n={n}")


def group_odd_euler_coordinates() -> None:
    nmax = 32
    e = euler_numbers(nmax + 2)
    z = zigzag_odd(nmax + 1, e)
    for q in range(1, 18, 2):
        for n in range(0, nmax + 1, 2):
            rec = sum(((-1) ** r) * z[2 * r + 1] * math.comb(n, 2 * r) * q ** (2 * r) * S(n - 2 * r, q) for r in range(n // 2 + 1))
            check(rec == e[n], f"odd reconstruction q={q},n={n}")
            inv = e[n] + sum(2 ** (2 * r - 1) * math.comb(n, 2 * r) * q ** (2 * r) * e[n - 2 * r] for r in range(1, n // 2 + 1))
            check(inv == S(n, q), f"odd inverse q={q},n={n}")
            if q >= 3:
                for M in range(0, n // 2 + 1):
                    trunc = sum(((-1) ** r) * z[2 * r + 1] * math.comb(n, 2 * r) * q ** (2 * r) * S(n - 2 * r, q) for r in range(min(M, n // 2) + 1))
                    diff = e[n] - trunc
                    if M < n // 2:
                        check(diff % (q ** (2 * M + 2)) == 0, f"odd tail q={q},n={n},M={M}")
                    else:
                        check(diff == 0)


def group_dyadic_coordinates() -> None:
    e = euler_numbers(48)
    for r in range(1, 121):
        b = beta(r)
        check(vp_frac(b, 2) == int(r).bit_count() - 1, f"beta valuation r={r}")
    for n in range(0, 402, 2):
        check(vp_frac(R_source(n), 2) == 0, f"R unit n={n}")
    for n in range(0, 42, 2):
        rec = sum(beta(r) * 2 ** (2 * r) * falling(n, 2 * r) * R_source(n - 2 * r) for r in range(n // 2 + 1))
        check(rec == e[n], f"dyadic reconstruction n={n}")
        inv = sum(Fraction(2 ** (4 * r + 1), math.factorial(2 * r + 2)) * falling(n, 2 * r) * e[n - 2 * r] for r in range(n // 2 + 1))
        check(inv == R_source(n), f"dyadic inverse n={n}")
        for r in range(1, n // 2 + 1):
            term = beta(r) * 2 ** (2 * r) * falling(n, 2 * r) * R_source(n - 2 * r)
            expected = 2 * r + r.bit_count() - 1 + vp_int(falling(n, 2 * r), 2)
            check(vp_frac(term, 2) == expected, f"term valuation n={n},r={r}")
        for M in range(0, n // 2 + 1):
            trunc = sum(beta(r) * 2 ** (2 * r) * falling(n, 2 * r) * R_source(n - 2 * r) for r in range(min(M, n // 2) + 1))
            diff = Fraction(e[n]) - trunc
            if M < n // 2:
                check(vp_frac(diff, 2) >= 2 * M + 2, f"dyadic tail n={n},M={M}")
            else:
                check(diff == 0)


def group_unit_modes_and_mahler() -> None:
    for p in primes_upto(19):
        if p == 2:
            continue
        h = p - 1
        candidates = [u for u in range(1, min(p**3, 220)) if u % p]
        for u in candidates:
            for n in range(4):
                for s in range(1, 4):
                    lhs = sum(((-1) ** (s - k)) * math.comb(s, k) * u ** (n + k * h) for k in range(s + 1))
                    rhs = u**n * (u**h - 1) ** s
                    check(lhs == rhs)
                    check(vp_int(lhs, p) >= s)
    for u in range(1, 64, 2):
        for n in range(4):
            for s in range(1, 5):
                lhs2 = sum(((-1) ** (s - k)) * math.comb(s, k) * u ** (n + 2 * k) for k in range(s + 1))
                check(lhs2 == u**n * (u * u - 1) ** s)
                check(vp_int(lhs2, 2) >= 3 * s)
                if u % 4 == 1:
                    lhs1 = sum(((-1) ** (s - k)) * math.comb(s, k) * u ** (n + k) for k in range(s + 1))
                    check(vp_int(lhs1, 2) >= 2 * s)
    rng = random.Random(91)
    for N in range(1, 22):
        values = [rng.randint(-10**5, 10**5) for _ in range(N + 1)]
        c = finite_differences(values)
        for n in range(N + 1):
            rec = sum(c[r] * math.comb(n, r) for r in range(n + 1))
            check(rec == values[n], f"Mahler reconstruction N={N},n={n}")
            for s in range(n + 1):
                direct = values[n] if s == 0 else None
                if n + s <= N:
                    direct = sum(((-1) ** (s - k)) * math.comb(s, k) * values[n + k] for k in range(s + 1))
                    via = sum(c[r] * math.comb(n, r - s) for r in range(s, N + 1) if 0 <= r - s <= n)
                    check(via == direct, f"difference formula N={N},n={n},s={s}")


def group_linear_lifting() -> None:
    for p in (2, 3, 5):
        for r, d in ((1, 1), (1, 2), (2, 1), (2, 2)):
            matrices = itertools.product(range(p), repeat=r * d)
            for M in matrices:
                rank = matrix_rank_mod(M, r, d, p)
                image = {mat_vec_mod(M, y, r, d, p) for y in itertools.product(range(p), repeat=d)}
                for rho in itertools.product(range(p), repeat=r):
                    target = tuple((-x) % p for x in rho)
                    sols = [y for y in itertools.product(range(p), repeat=d) if mat_vec_mod(M, y, r, d, p) == target]
                    check(bool(sols) == (target in image))
                    if sols:
                        check(len(sols) == p ** (d - rank))
    rng = random.Random(19)
    for p in (2, 3, 5, 7):
        for L in (1, 2, 3):
            mod = p ** (L + 1)
            for _ in range(300):
                r, d = 2, 3
                M = [[rng.randrange(mod) for _ in range(d)] for __ in range(r)]
                x = [rng.randrange(p**L) for _ in range(d)]
                rho = [rng.randrange(p) for _ in range(r)]
                b = [(sum(M[i][j] * x[j] for j in range(d)) - p**L * rho[i]) % mod for i in range(r)]
                Mflat = tuple(M[i][j] % p for i in range(r) for j in range(d))
                solutions = []
                for y in itertools.product(range(p), repeat=d):
                    xnew = [x[j] + p**L * y[j] for j in range(d)]
                    ok = all((sum(M[i][j] * xnew[j] for j in range(d)) - b[i]) % mod == 0 for i in range(r))
                    if ok:
                        solutions.append(y)
                target = tuple((-z) % p for z in rho)
                predicted = [y for y in itertools.product(range(p), repeat=d) if mat_vec_mod(Mflat, y, r, d, p) == target]
                check(set(solutions) == set(predicted))


def group_polynomial_lifting() -> None:
    for p in (2, 3, 5, 7):
        for L in (1, 2, 3):
            modL = p**L
            modN = p ** (L + 1)
            for a0, a1, a2 in itertools.product(range(p), repeat=3):
                for x in range(modL):
                    # Force the chosen x to solve one congruence by adjusting the constant at depth L.
                    base = a0 + a1 * x + a2 * x * x
                    c = (-base) % modL
                    def f(z: int) -> int:
                        return c + a0 + a1 * z + a2 * z * z
                    check(f(x) % modL == 0)
                    rho = (f(x) // modL) % p
                    jac = (a1 + 2 * a2 * x) % p
                    predicted = [y for y in range(p) if (jac * y + rho) % p == 0]
                    actual = [y for y in range(p) if f(x + modL * y) % modN == 0]
                    check(actual == predicted, f"poly lift p={p},L={L}")
    # A small two variable family.
    rng = random.Random(79)
    for p in (2, 3, 5):
        for L in (1, 2):
            modL = p**L
            modN = p ** (L + 1)
            for _ in range(500):
                a, b, c, d, e = [rng.randrange(p) for __ in range(5)]
                x, y = rng.randrange(modL), rng.randrange(modL)
                base = a * x + b * y + c * x * x + d * x * y + e * y * y
                k = (-base) % modL
                def F(X: int, Y: int) -> int:
                    return k + a * X + b * Y + c * X * X + d * X * Y + e * Y * Y
                rho = (F(x, y) // modL) % p
                jx = (a + 2 * c * x + d * y) % p
                jy = (b + d * x + 2 * e * y) % p
                actual = [(u, v) for u, v in itertools.product(range(p), repeat=2) if F(x + modL * u, y + modL * v) % modN == 0]
                predicted = [(u, v) for u, v in itertools.product(range(p), repeat=2) if (rho + jx * u + jy * v) % p == 0]
                check(set(actual) == set(predicted))


def group_recurrences() -> None:
    rng = random.Random(109)
    x = sp.symbols('x')
    y = sp.symbols('y')
    for d in (1, 2, 3):
        for _ in range(55):
            entries = [rng.randint(-4, 4) for __ in range(d * d)]
            C = sp.Matrix(d, d, entries)
            for N in range(1, 6):
                lhs = sp.Poly((C**N).charpoly(x).as_expr(), x)
                chi = sp.Poly(C.charpoly(y).as_expr(), y)
                rhs = sp.Poly(resultant_standard(chi.as_expr(), x - y**N, y), x)
                check(sp.expand(lhs.as_expr() - rhs.as_expr()) == 0, f"resultant d={d},N={N}")
                v0 = sp.Matrix([rng.randint(-5, 5) for __ in range(d)])
                for j in range(N):
                    for k in range(5):
                        check(C ** (N * k + j) * v0 == C**j * (C**N) ** k * v0)
    for P in range(-4, 5):
        for Q in range(-4, 5):
            V = [2, P]
            for n in range(12):
                if len(V) <= n + 2:
                    V.append(P * V[-1] - Q * V[-2])
            seq = [1, 3]
            for n in range(40):
                seq.append(P * seq[-1] - Q * seq[-2])
            for N in range(1, 8):
                for j in range(N):
                    u = [seq[N * k + j] for k in range((len(seq) - 1 - j) // N + 1)]
                    for k in range(len(u) - 2):
                        check(u[k + 2] == V[N] * u[k + 1] - Q**N * u[k])
    # Modular periodicity. Exhaust small spaces and sample the larger ones.
    for p in (2, 3, 5):
        for L in (1, 2, 3):
            mod = p**L
            matrix_count = 20 if mod <= 9 else 8
            for _ in range(matrix_count):
                while True:
                    C = [[rng.randrange(mod) for _ in range(2)] for __ in range(2)]
                    det = (C[0][0] * C[1][1] - C[0][1] * C[1][0]) % p
                    if det:
                        break
                if mod <= 9:
                    states = list(itertools.product(range(mod), repeat=2))
                else:
                    states = [(rng.randrange(mod), rng.randrange(mod)) for __ in range(40)]
                for state in states:
                    seen = {}
                    cur = state
                    for t in range(mod**2 + 1):
                        if cur in seen:
                            check(seen[cur] == 0, "invertible orbit has preperiod")
                            break
                        seen[cur] = t
                        cur = ((C[0][0] * cur[0] + C[0][1] * cur[1]) % mod,
                               (C[1][0] * cur[0] + C[1][1] * cur[1]) % mod)
                    else:
                        check(False, "finite orbit did not repeat")


def group_crt_packets() -> None:
    for A in range(1, 13):
        for B in range(1, 13):
            if math.gcd(A, B) != 1:
                continue
            for ra in range(A):
                for rb in range(B):
                    hits = [n for n in range(A * B) if n % A == ra and n % B == rb]
                    check(len(hits) == 1)
                    r = hits[0]
                    for n in range(4 * A * B):
                        check((n % (A * B) == r) == ((n % A == ra) and (n % B == rb)))
    for a in range(0, 7):
        for m in range(1, 18, 2):
            N = (2**a) * m
            for r in range(N):
                for n in range(2 * N):
                    check((n % N == r) == ((n % (2**a) == r % (2**a)) and (n % m == r % m)))


def group_legacy_tables() -> None:
    e = euler_numbers(64)
    z = zigzag_odd(61, e)
    odd_path = LEGACY / "tables" / "odd_supercongruence_samples.csv"
    with odd_path.open(newline="") as f:
        rows = list(csv.DictReader(f))
    check(len(rows) == 48)
    for row in rows:
        p = int(row["p"])
        n = int(row["n"])
        M = int(row["M"])
        trunc = sum(((-1) ** r) * z[2 * r + 1] * math.comb(n, 2 * r) * p ** (2 * r) * S(n - 2 * r, p) for r in range(min(M, n // 2) + 1))
        diff = e[n] - trunc
        check(trunc == int(row["truncated"]))
        check(diff == int(row["difference"]))
        check(vp_int(diff, p) == int(row["valuation"]))
        check(vp_int(diff, p) >= int(row["bound"]))
        check(row["passed"] == "True")
    dy_path = LEGACY / "tables" / "dyadic_reconstruction_samples.csv"
    with dy_path.open(newline="") as f:
        rows = list(csv.DictReader(f))
    check(len(rows) == 25)
    for row in rows:
        n = int(row["n"])
        M = int(row["M"])
        trunc = sum(beta(r) * 2 ** (2 * r) * falling(n, 2 * r) * R_source(n - 2 * r) for r in range(min(M, n // 2) + 1))
        diff = Fraction(e[n]) - trunc
        check(trunc == Fraction(row["truncated"]))
        check(diff == Fraction(row["difference"]))
        check(vp_frac(diff, 2) == int(row["valuation"]))
        check(vp_frac(diff, 2) >= int(row["bound"]))
        check(row["passed"] == "True")
    data = json.loads((LEGACY / "results" / "arithmetic_results.json").read_text())
    check(data["odd_supercongruence"]["checks"] == 180)
    check(data["dyadic_reconstruction"]["checks"] == 111)
    check(data["crt_checks"]["count"] == 192)
    check(data["packet_reconstruction_residual"] == 0)


def group_source_integrity() -> None:
    tex = TEX.read_text()
    bib = BIB.read_text()
    # Abstract length.
    m = re.search(r"\\begin\{abstract\}(.*?)\\end\{abstract\}", tex, re.S)
    check(m is not None)
    abstract_plain = re.sub(r"\\[A-Za-z]+(?:\{[^{}]*\})?", " ", m.group(1))
    abstract_plain = re.sub(r"[$\\{}^_]", " ", abstract_plain)
    words = re.findall(r"[A-Za-z0-9]+(?:'[A-Za-z]+)?", abstract_plain)
    check(len(words) <= 200, f"abstract has {len(words)} words")
    # Environment and proof counts.
    proved_envs = sum(len(re.findall(rf"\\begin\{{{env}\}}", tex)) for env in ("theorem", "proposition", "lemma", "corollary"))
    proofs = len(re.findall(r"\\begin\{proof\}", tex))
    check(proved_envs == proofs, f"proved environments {proved_envs}, proofs {proofs}")
    # Unique labels and complete references.
    labels = re.findall(r"\\label\{([^}]+)\}", tex)
    check(len(labels) == len(set(labels)), "duplicate labels")
    refs: list[str] = []
    for payload in re.findall(r"\\(?:cref|Cref|ref)\{([^}]+)\}", tex):
        refs.extend(x.strip() for x in payload.split(','))
    missing_refs = sorted(set(refs) - set(labels))
    check(not missing_refs, f"missing references {missing_refs}")
    # Bibliography integrity.
    bibkeys = set(re.findall(r"@\w+\{([^,]+),", bib))
    cites: set[str] = set()
    for payload in re.findall(r"\\cite\{([^}]+)\}", tex):
        cites.update(x.strip() for x in payload.split(','))
    check(not (cites - bibkeys), f"missing bib keys {sorted(cites-bibkeys)}")
    check(not (bibkeys - cites), f"uncited bib keys {sorted(bibkeys-cites)}")
    # Required figures.
    figs = re.findall(r"\\includegraphics(?:\[[^]]*\])?\{([^}]+)\}", tex)
    for fig in figs:
        check((ROOT / "figures" / fig).exists(), f"missing figure {fig}")
    # Language and source hygiene.
    check(';' not in tex, "semicolon in source")
    check('\\newpage' not in tex and '\\pagebreak' not in tex and '\\clearpage' not in tex)
    banned = [
        "delve", "robust framework", "leverage", "seamlessly", "game changer",
        "in conclusion,", "it is important to note", "taken together", "moreover,",
        "furthermore,", "comprehensive framework"
    ]
    low = tex.lower()
    for phrase in banned:
        check(phrase not in low, f"banned phrase {phrase}")


def main() -> None:
    run_group("Hurwitz modes and standard periods", group_hurwitz_and_period)
    run_group("Triangular inverses and standard windows", group_triangular_and_standard_windows)
    run_group("Odd modulus Euler coordinates", group_odd_euler_coordinates)
    run_group("Dyadic Euler coordinates", group_dyadic_coordinates)
    run_group("Unit modes and Mahler coordinates", group_unit_modes_and_mahler)
    run_group("Linear lifting obstructions", group_linear_lifting)
    run_group("Polynomial lifting obstructions", group_polynomial_lifting)
    run_group("Recurrence packets", group_recurrences)
    run_group("Chinese remainder packets", group_crt_packets)
    run_group("Legacy arithmetic tables", group_legacy_tables)
    run_group("Source and package integrity", group_source_integrity)

    lines = [f"Paper IX verification: {checks}/{checks} checks passed in {len(groups)} groups", ""]
    lines.extend(f"{name}: {count}" for name, count in groups)
    summary = "\n".join(lines) + "\n"
    print(summary, end="")
    (Path(__file__).with_name("verification_summary.txt")).write_text(summary)


if __name__ == "__main__":
    main()
