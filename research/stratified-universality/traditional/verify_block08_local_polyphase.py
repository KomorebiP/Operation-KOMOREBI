from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction
from itertools import product
from math import comb, gcd
from pathlib import Path
import json

import sympy as sp

ROOT = Path(__file__).resolve().parent
GEN = ROOT / "generated"
GEN.mkdir(parents=True, exist_ok=True)
OUT = GEN / "block08_local_polyphase_validation.json"


@dataclass
class Ledger:
    checks: int = 0
    failures: list[str] | None = None

    def __post_init__(self) -> None:
        if self.failures is None:
            self.failures = []

    def check(self, condition: bool, message: str) -> None:
        self.checks += 1
        if not condition:
            assert self.failures is not None
            self.failures.append(message)


def theta(M: int, s: int, r: int, k: int) -> int:
    return sum((-1) ** (k - j) * comb(k, j) * comb(M * j + s, r) for j in range(k + 1))


def theta_row_generating(M: int, s: int, k: int) -> list[int]:
    # Coefficients of (1+z)^s ((1+z)^M - 1)^k.
    poly = [1]
    base = [comb(M, j) for j in range(M + 1)]
    base[0] -= 1

    def mul(a: list[int], b: list[int]) -> list[int]:
        c = [0] * (len(a) + len(b) - 1)
        for i, x in enumerate(a):
            for j, y in enumerate(b):
                c[i + j] += x * y
        return c

    for _ in range(k):
        poly = mul(poly, base)
    poly = mul([comb(s, j) for j in range(s + 1)], poly)
    return poly


def A_matrix(M: int, s: int, d: int) -> list[list[int]]:
    return [[theta(M, s, r, k) for r in range(d + 1)] for k in range(d + 1)]


def matmul(A: list[list[int]], B: list[list[int]]) -> list[list[int]]:
    n = len(A)
    m = len(B[0])
    inner = len(B)
    return [[sum(A[i][t] * B[t][j] for t in range(inner)) for j in range(m)] for i in range(n)]


def matvec(A: list[list[int]], v: list[int]) -> list[int]:
    return [sum(x * y for x, y in zip(row, v)) for row in A]


def rank_mod_p(A: list[list[int]], p: int) -> int:
    if not A:
        return 0
    M = [[x % p for x in row] for row in A]
    rows, cols = len(M), len(M[0])
    rank = 0
    col = 0
    while rank < rows and col < cols:
        pivot = next((r for r in range(rank, rows) if M[r][col] % p), None)
        if pivot is None:
            col += 1
            continue
        M[rank], M[pivot] = M[pivot], M[rank]
        inv = pow(M[rank][col], -1, p)
        M[rank] = [(inv * x) % p for x in M[rank]]
        for r in range(rows):
            if r != rank and M[r][col] % p:
                factor = M[r][col]
                M[r] = [(M[r][j] - factor * M[rank][j]) % p for j in range(cols)]
        rank += 1
        col += 1
    return rank


def stack_channels(M: int, shifts: list[int], d: int) -> list[list[int]]:
    out: list[list[int]] = []
    for s in shifts:
        out.extend(A_matrix(M, s, d))
    return out


def pvaluation(n: int, p: int, infinity: int = 10**9) -> int:
    if n == 0:
        return infinity
    n = abs(n)
    v = 0
    while n % p == 0:
        n //= p
        v += 1
    return v


def prime_factors(n: int) -> list[int]:
    out: list[int] = []
    d = 2
    while d * d <= n:
        if n % d == 0:
            out.append(d)
            while n % d == 0:
                n //= d
        d += 1
    if n > 1:
        out.append(n)
    return out


def largest_primary_component(M: int) -> int:
    best = 1
    for p in prime_factors(M):
        x = M
        e = 0
        while x % p == 0:
            x //= p
            e += 1
        best = max(best, p**e)
    return best


def eval_binomial_series(c: list[int], x: int) -> int:
    return sum(c[r] * comb(x, r) for r in range(min(len(c) - 1, x) + 1))


def forward_differences(values: list[int]) -> list[int]:
    out: list[int] = []
    row = values[:]
    while row:
        out.append(row[0])
        row = [row[i + 1] - row[i] for i in range(len(row) - 1)]
    return out


ledger = Ledger()
counters: dict[str, int] = {}

# ---------------------------------------------------------------------------
# 1. Kernel identity, support, triangularity, determinant, and exact transport.
# ---------------------------------------------------------------------------
kernel_cases = 0
for M in range(1, 8):
    for s in range(0, min(M + 2, 7)):
        for k in range(0, 8):
            coeffs = theta_row_generating(M, s, k)
            for r in range(0, max(len(coeffs), M * k + s + 2)):
                expected = coeffs[r] if r < len(coeffs) else 0
                ledger.check(theta(M, s, r, k) == expected, f"row identity M={M},s={s},r={r},k={k}")
                ledger.check((theta(M, s, r, k) == 0) or (k <= r <= M * k + s), f"support M={M},s={s},r={r},k={k}")
            kernel_cases += 1
counters["kernel_rows"] = kernel_cases

transport_cases = 0
patterns = [
    lambda d: [1] + [0] * d,
    lambda d: list(range(d + 1)),
    lambda d: [(-1) ** r * (r + 1) for r in range(d + 1)],
    lambda d: [((r * r + 3 * r + 1) % 7) - 3 for r in range(d + 1)],
]
for d in range(0, 9):
    for M in range(1, 7):
        for s in range(0, min(M + 1, 6)):
            A = A_matrix(M, s, d)
            for r in range(d + 1):
                for k in range(d + 1):
                    ledger.check((A[k][r] == 0) if k > r else True, f"triangular M={M},s={s},d={d},k={k},r={r}")
                ledger.check(A[r][r] == M**r, f"diagonal M={M},s={s},d={d},r={r}")
            det_expected = M ** (d * (d + 1) // 2)
            det_actual = int(sp.Matrix(A).det())
            ledger.check(det_actual == det_expected, f"det M={M},s={s},d={d}")
            for pat in patterns:
                c = pat(d)
                dc = matvec(A, c)
                for q in range(0, d + 4):
                    lhs = eval_binomial_series(c, M * q + s)
                    rhs = eval_binomial_series(dc, q)
                    ledger.check(lhs == rhs, f"transport M={M},s={s},d={d},q={q},c={c}")
                transport_cases += 1
counters["finite_transport_cases"] = transport_cases

# ---------------------------------------------------------------------------
# 2. Mixed-radix composition, CRT diamonds, and branch-address coherence.
# ---------------------------------------------------------------------------
composition_cases = 0
for d in range(0, 8):
    for M in range(1, 5):
        for N in range(1, 5):
            for s in range(M):
                for t in range(N):
                    lhs = matmul(A_matrix(N, t, d), A_matrix(M, s, d))
                    rhs = A_matrix(M * N, M * t + s, d)
                    for i in range(d + 1):
                        for j in range(d + 1):
                            ledger.check(lhs[i][j] == rhs[i][j], f"composition M={M},N={N},s={s},t={t},d={d},i={i},j={j}")
                    composition_cases += 1
counters["composition_cases"] = composition_cases

crt_cases = 0
for d in range(0, 7):
    for M in range(2, 7):
        for N in range(2, 7):
            if gcd(M, N) != 1:
                continue
            for r in range(M):
                for u in range(N):
                    a = next(x for x in range(M * N) if x % M == r and x % N == u)
                    t = (a - r) // M
                    v = (a - u) // N
                    left = matmul(A_matrix(N, t, d), A_matrix(M, r, d))
                    right = matmul(A_matrix(M, v, d), A_matrix(N, u, d))
                    direct = A_matrix(M * N, a, d)
                    ledger.check(left == right == direct, f"CRT M={M},N={N},r={r},u={u},d={d}")
                    crt_cases += 1
counters["crt_diamonds"] = crt_cases

branch_address_checks = 0
for p in (2, 3, 5):
    for a in (1, 2):
        for b in (1, 2):
            pa, pb = p**a, p**b
            for s in range(pa):
                for t in range(pb):
                    combined = s + pa * t
                    for q in range(0, 12):
                        left = pa * (pb * q + t) + s
                        right = p ** (a + b) * q + combined
                        ledger.check(left == right, f"branch address p={p},a={a},b={b},s={s},t={t},q={q}")
                        branch_address_checks += 1
counters["branch_address_checks"] = branch_address_checks

# ---------------------------------------------------------------------------
# 3. Prime-power sparsity, single-channel rank, packet rank, and minimality.
# ---------------------------------------------------------------------------
prime_power_cases = 0
for p in (2, 3, 5):
    for alpha in (1, 2):
        M = p**alpha
        if M > 10:
            continue
        for d in range(0, 19):
            for s in range(M):
                A = A_matrix(M, s, d)
                for k in range(d + 1):
                    for r in range(d + 1):
                        u = r - M * k
                        expected = comb(s, u) if 0 <= u <= s else 0
                        ledger.check(A[k][r] % p == expected % p, f"sparse p={p},a={alpha},s={s},d={d},k={k},r={r}")
                ledger.check(rank_mod_p(A, p) == d // M + 1, f"local rank p={p},a={alpha},s={s},d={d}")
            hstar = min(M, d + 1)
            for h in range(1, hstar):
                ledger.check(rank_mod_p(stack_channels(M, list(range(h)), d), p) < d + 1, f"prefix below minimum p={p},a={alpha},d={d},h={h}")
            ledger.check(rank_mod_p(stack_channels(M, list(range(hstar)), d), p) == d + 1, f"minimal prefix p={p},a={alpha},d={d}")
            prime_power_cases += 1
counters["prime_power_degree_cases"] = prime_power_cases

# ---------------------------------------------------------------------------
# 4. Universal integer decoder and sharp composite prefix.
# ---------------------------------------------------------------------------
decoder_cases = 0
for M in range(1, 13):
    Bprimary = largest_primary_component(M)
    for d in range(0, 13):
        hcanonical = min(M, d + 1)
        # Unitriangular selected minor using row n = M*k+s from channel s.
        Bmat: list[list[int]] = []
        for n in range(d + 1):
            k, s = divmod(n, M)
            Bmat.append(A_matrix(M, s, d)[k])
        Bsym = sp.Matrix(Bmat)
        ledger.check(int(Bsym.det()) == 1, f"unit minor M={M},d={d}")
        Binv = Bsym.inv()
        ledger.check(all(x.q == 1 for x in Binv), f"integer inverse M={M},d={d}")
        for c in ([r - 2 for r in range(d + 1)], [(-1) ** r * (r + 1) for r in range(d + 1)]):
            selected = []
            for n in range(d + 1):
                k, s = divmod(n, M)
                selected.append(matvec(A_matrix(M, s, d), c)[k])
            recovered = [int(x) for x in Binv * sp.Matrix(selected)]
            ledger.check(recovered == c, f"decoder M={M},d={d},c={c}")
        # Sharp composite prefix is decided at each primary component.
        Lz = min(d + 1, Bprimary)
        for p in prime_factors(M):
            ledger.check(rank_mod_p(stack_channels(M, list(range(Lz)), d), p) == d + 1, f"composite prefix M={M},d={d},p={p}")
        if M > 1 and Lz > 1:
            obstructing = max(prime_factors(M), key=lambda p: p ** pvaluation(M, p))
            ledger.check(rank_mod_p(stack_channels(M, list(range(Lz - 1)), d), obstructing) < d + 1, f"composite sharpness M={M},d={d}")
        decoder_cases += 1
counters["integer_decoder_cases"] = decoder_cases

# ---------------------------------------------------------------------------
# 5. Valuation ledgers and monotone precision preservation.
# ---------------------------------------------------------------------------
valuation_cases = 0
for p in (2, 3, 5, 7):
    for M in range(1, 8):
        for s in range(0, min(M, 5)):
            for d in range(1, 18):
                for slope in (1, 2, 3):
                    c = []
                    for r in range(d + 1):
                        sign = -1 if (r + M + s) % 2 else 1
                        c.append(sign * (r + 1) * p ** (slope * r))
                    dc = matvec(A_matrix(M, s, d), c)
                    for k in range(d + 1):
                        vals = [pvaluation(c[r], p) + pvaluation(theta(M, s, r, k), p) for r in range(k, d + 1) if theta(M, s, r, k) != 0]
                        lower = min(vals) if vals else 10**9
                        ledger.check(pvaluation(dc[k], p) >= lower, f"valuation ledger p={p},M={M},s={s},d={d},k={k}")
                        ledger.check(pvaluation(dc[k], p) >= slope * k, f"monotone ladder p={p},M={M},s={s},d={d},k={k}")
                    valuation_cases += 1
counters["valuation_cases"] = valuation_cases

# ---------------------------------------------------------------------------
# 6. Scalar and matrix precision amplification.
# ---------------------------------------------------------------------------
scalar_precision = 0
for p in (3, 5, 7):
    for u in range(1, 50):
        if u % p == 0:
            continue
        for a in range(0, 6):
            H = (p - 1) * p**a
            v = pvaluation(pow(u, H) - 1, p)
            ledger.check(v >= a + 1, f"odd precision p={p},u={u},a={a},v={v}")
            for r in range(0, 5):
                ledger.check(pvaluation((pow(u, H) - 1) ** r, p) >= (a + 1) * r, f"odd diff p={p},u={u},a={a},r={r}")
            scalar_precision += 1
for u in range(1, 64, 2):
    for a in range(0, 7):
        H = 2 ** (a + 1)
        v = pvaluation(pow(u, H) - 1, 2)
        ledger.check(v >= a + 3, f"dyadic precision u={u},a={a},v={v}")
        for r in range(0, 5):
            ledger.check(pvaluation((pow(u, H) - 1) ** r, 2) >= (a + 3) * r, f"dyadic diff u={u},a={a},r={r}")
        scalar_precision += 1
counters["scalar_precision_cases"] = scalar_precision

C = sp.Matrix([[1, 1], [1, 0]])
C12 = C**12
B = (C12 - sp.eye(2)) / 8
ledger.check(all(x.q == 1 for x in B), "Fibonacci B integral")
ledger.check(C12 == sp.eye(2) + 8 * B, "Fibonacci base congruence")
matrix_precision = 0
for a in range(0, 9):
    X = C ** (12 * 2**a) - sp.eye(2)
    modulus = 2 ** (a + 3)
    for x in X:
        ledger.check(int(x) % modulus == 0, f"Fibonacci amplification a={a},x={x}")
    matrix_precision += 1
counters["matrix_precision_cases"] = matrix_precision

# ---------------------------------------------------------------------------
# 7. Worked examples used in the manuscript.
# ---------------------------------------------------------------------------
examples: list[dict[str, object]] = []

# x^2 in the Mahler basis: x^2 = b_1 + 2 b_2.
c_x2 = [0, 1, 2]
for s in (0, 1):
    d = matvec(A_matrix(2, s, 2), c_x2)
    examples.append({"name": f"x^2, branch 2q+{s}", "source": c_x2, "branch": d})
    for q in range(0, 12):
        ledger.check(eval_binomial_series(d, q) == (2 * q + s) ** 2, f"x2 example s={s},q={q}")

# Unit exponential (1+p)^x has c_r=p^r; one p-power refinement raises the slope.
for p in (2, 3, 5):
    u = 1 + p
    max_k = 6
    source_degree = p * max_k
    c = [p**r for r in range(source_degree + 1)]
    d0_full = matvec(A_matrix(p, 0, source_degree), c)
    d0 = d0_full[: max_k + 1]
    expected = [(pow(u, p) - 1) ** k for k in range(max_k + 1)]
    ledger.check(d0 == expected, f"unit exponential p={p}")
    examples.append({"name": f"(1+{p})^x, branch {p}q", "source": c[:5], "branch": d0[:5]})

# One rank-loss example at p=2, M=2, d=3.
A20 = A_matrix(2, 0, 3)
A21 = A_matrix(2, 1, 3)
examples.append({
    "name": "mod-2 rank distribution, M=2,d=3",
    "source": [rank_mod_p(A20, 2), rank_mod_p(A21, 2)],
    "branch": [rank_mod_p(A20 + A21, 2), 4],
})
ledger.check(rank_mod_p(A20, 2) == 2 and rank_mod_p(A21, 2) == 2, "rank-loss example local")
ledger.check(rank_mod_p(A20 + A21, 2) == 4, "rank-loss example packet")

# Functional-vs-Newton lifting negative control: same residue sequence, distinct lifts.
# The two integer lifts agree mod p but have different first forward differences.
for p in (2, 3, 5):
    vals1 = [1, 0, 1, 0, 1, 0]
    vals2 = [vals1[n] + p * n for n in range(len(vals1))]
    c1 = forward_differences(vals1)
    c2 = forward_differences(vals2)
    ledger.check(all((x - y) % p == 0 for x, y in zip(vals1, vals2)), f"lift residues p={p}")
    ledger.check(c1 != c2, f"distinct Newton lifts p={p}")

# ---------------------------------------------------------------------------
# Output machine-readable record and LaTeX tables.
# ---------------------------------------------------------------------------
status = "PASS" if not ledger.failures else "FAIL"
record = {
    "status": status,
    "checks": ledger.checks,
    "failures": ledger.failures,
    "counters": counters,
    "examples": examples,
    "boundary": {
        "continuous_mahler": "Uses the classical Mahler coordinate theorem on C(Z_p,Z_p).",
        "polyphase": "Exact for declared affine branches and complete clopen packets.",
        "finite_degree": "Single characteristic-zero charts, integral split packets, and modular rank loss are distinct claims.",
        "functional_boundary": "No unrestricted equivalence with functional-Mahler masks is asserted.",
    },
}
OUT.write_text(json.dumps(record, indent=2), encoding="utf-8")

# Example table.
rows = []
for row in examples:
    name = row["name"]
    source_tex = rf"\( {str(row['source']).replace('[', '(').replace(']', ')')} \)"
    branch_tex = rf"\( {str(row['branch']).replace('[', '(').replace(']', ')')} \)"
    name = name.replace("x^2", r"\(x^2\)")
    for base in (2, 3, 5):
        token = f"(1+{base})^x"
        if token in name:
            name = name.replace(token, rf"\((1+{base})^x\)")
            amp = (1 + base) ** base - 1
            source_tex = rf"\(c_r={base}^r,\ 0\leq r\leq4\)"
            branch_tex = rf"\(d_k={amp}^k,\ 0\leq k\leq4\)"
    rows.append(rf"{name} & {source_tex} & {branch_tex}\\")
example_tex = "\n".join([
    r"\begin{table}[htbp]",
    r"\centering",
    r"\caption{Exact local Mahler and polyphase examples used in Block 08.}",
    r"\label{tab:block08-examples}",
    r"\small",
    r"\begin{tabularx}{\textwidth}{@{}L{0.31\textwidth}L{0.29\textwidth}Y@{}}",
    r"\toprule",
    r"Example & Source Mahler data & Refined data or rank\\",
    r"\midrule",
    *rows,
    r"\bottomrule",
    r"\end{tabularx}",
    r"\end{table}",
]) + "\n"
(GEN / "block08_examples_table.tex").write_text(example_tex, encoding="utf-8")

validation_tex = "\n".join([
    r"\begin{table}[htbp]",
    r"\centering",
    r"\caption{Block 08 exact verification summary.}",
    r"\label{tab:block08-validation}",
    r"\small",
    r"\begin{tabularx}{\textwidth}{@{}L{0.38\textwidth}Y@{}}",
    r"\toprule",
    r"Validation class & Recorded result\\",
    r"\midrule",
    rf"Affine-kernel rows & {counters['kernel_rows']:,} exact row cases\\",
    rf"Finite coefficient transports & {counters['finite_transport_cases']:,} source/chart cases\\",
    rf"Mixed-radix compositions and CRT diamonds & {counters['composition_cases'] + counters['crt_diamonds']:,} exact diagrams\\",
    rf"Prime-power rank and sparsity cases & {counters['prime_power_degree_cases']:,} degree/radix cases\\",
    rf"Integral decoder and composite-minimum cases & {counters['integer_decoder_cases']:,} cases\\",
    rf"Valuation-ledger cases & {counters['valuation_cases']:,} coefficient ladders\\",
    rf"Scalar and matrix precision cases & {counters['scalar_precision_cases'] + counters['matrix_precision_cases']:,} cases\\",
    rf"\textbf{{Total exact checks}} & \textbf{{{ledger.checks:,}}}\\",
    rf"Failures & {len(ledger.failures)}\\",
    r"\bottomrule",
    r"\end{tabularx}",
    r"\end{table}",
]) + "\n"
(GEN / "block08_validation_table.tex").write_text(validation_tex, encoding="utf-8")

print(f"BLOCK08_STATUS={status}")
print(f"BLOCK08_CHECKS={ledger.checks}")
print(f"BLOCK08_FAILURES={len(ledger.failures)}")
if ledger.failures:
    for msg in ledger.failures[:20]:
        print("FAIL:", msg)
    raise SystemExit(1)
