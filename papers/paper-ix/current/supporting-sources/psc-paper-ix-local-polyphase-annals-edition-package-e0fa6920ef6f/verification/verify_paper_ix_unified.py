from __future__ import annotations

import importlib.util
import itertools
import json
import math
import random
import re
from fractions import Fraction
from pathlib import Path

import sympy as sp

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
BASE_NAME = "PSC_Paper_IX_Local_Polyphase_Annals_Edition"
TEX = ROOT / f"{BASE_NAME}.tex"
BIB = ROOT / f"{BASE_NAME}.bib"
LEGACY = ROOT / "legacy"

spec = importlib.util.spec_from_file_location("base_ix", HERE / "verify_paper_ix_base.py")
base = importlib.util.module_from_spec(spec)
assert spec.loader is not None
spec.loader.exec_module(base)
base.ROOT = ROOT
base.TEX = TEX
base.BIB = BIB
base.LEGACY = LEGACY
base.checks = 0
base.groups = []


def check(condition: bool, message: str = "") -> None:
    base.check(condition, message)


def vp_int(n: int, p: int) -> int:
    return base.vp_int(n, p)


def vp_frac(x: Fraction, p: int) -> int:
    return base.vp_frac(x, p)


def euler_numbers(nmax: int) -> list[int]:
    return base.euler_numbers(nmax)


def zigzag_odd(nmax: int, e: list[int]) -> dict[int, int]:
    return base.zigzag_odd(nmax, e)


def beta(r: int) -> Fraction:
    return base.beta(r)


def R_source(n: int) -> Fraction:
    return base.R_source(n)


def S(n: int, q: int) -> int:
    return base.S(n, q)


def falling(n: int, k: int) -> int:
    return base.falling(n, k)


def matmul(A: list[list[int]], B: list[list[int]]) -> list[list[int]]:
    return [[sum(A[i][k] * B[k][j] for k in range(len(B))) for j in range(len(B[0]))] for i in range(len(A))]


def matpow(A: list[list[int]], n: int) -> list[list[int]]:
    d = len(A)
    R = [[int(i == j) for j in range(d)] for i in range(d)]
    X = [row[:] for row in A]
    while n:
        if n & 1:
            R = matmul(R, X)
        X = matmul(X, X)
        n >>= 1
    return R


def matvec(A: list[list[int]], x: list[int]) -> list[int]:
    return [sum(A[i][j] * x[j] for j in range(len(x))) for i in range(len(A))]


def theta(M: int, s: int, r: int, k: int) -> int:
    if k < 0 or r < 0:
        return 0
    return sum((-1) ** (k - j) * math.comb(k, j) * (math.comb(M * j + s, r) if 0 <= r <= M * j + s else 0) for j in range(k + 1))


def finite_diff_step(values_fn, n: int, H: int, r: int) -> int:
    return sum((-1) ** (r - j) * math.comb(r, j) * values_fn(n + j * H) for j in range(r + 1))


def group_unified_local_euler() -> None:
    nmax = 48
    e = euler_numbers(nmax + 4)
    z = zigzag_odd(nmax + 3, e)
    for p in (3, 5, 7, 11, 13):
        for n in range(0, nmax + 1, 2):
            forward = sum(((-1) ** r) * z[2 * r + 1] * math.comb(n, 2 * r) * p ** (2 * r) * S(n - 2 * r, p) for r in range(n // 2 + 1))
            check(forward == e[n], f"odd unified forward p={p}, n={n}")
            inverse = e[n] + sum(2 ** (2 * r - 1) * math.comb(n, 2 * r) * p ** (2 * r) * e[n - 2 * r] for r in range(1, n // 2 + 1))
            check(inverse == S(n, p), f"odd unified inverse p={p}, n={n}")
    for n in range(0, nmax + 1, 2):
        forward = sum(beta(r) * 2 ** (2 * r) * falling(n, 2 * r) * R_source(n - 2 * r) for r in range(n // 2 + 1))
        check(forward == e[n], f"dyadic unified forward n={n}")
        inverse = sum(Fraction(2 ** (4 * r + 1), math.factorial(2 * r + 2)) * falling(n, 2 * r) * e[n - 2 * r] for r in range(n // 2 + 1))
        check(inverse == R_source(n), f"dyadic unified inverse n={n}")
    check(S(2, 3) - 2 * 3**2 * S(0, 3) == -1)
    check(R_source(4) + Fraction(-8, 3) * math.comb(4, 2) * R_source(2) + Fraction(128, 5) == 5)


def group_sharp_dyadic_depth() -> None:
    e = euler_numbers(82)
    for r in range(1, 31):
        kappa = beta(r) * 2 ** (2 * r) * math.factorial(2 * r)
        check(vp_frac(kappa, 2) == 4 * r - 1, f"sharp kappa r={r}")
    for n in range(0, 66, 2):
        for M in range(n // 2 + 1):
            trunc = sum(beta(r) * 2 ** (2 * r) * falling(n, 2 * r) * R_source(n - 2 * r) for r in range(min(M, n // 2) + 1))
            err = Fraction(e[n]) - trunc
            if M >= n // 2:
                check(err == 0)
            else:
                check(vp_frac(err, 2) >= 4 * M + 3, f"sharp tail n={n},M={M}")
    for M in range(0, 20):
        n = 2 * M + 2
        trunc = sum(beta(r) * 2 ** (2 * r) * falling(n, 2 * r) * R_source(n - 2 * r) for r in range(M + 1))
        err = Fraction(e[n]) - trunc
        check(vp_frac(err, 2) == 4 * M + 3, f"optimality M={M}")


def group_carmichael_mahler_extensions() -> None:
    for p in (3, 5, 7):
        for L in (1, 2, 3):
            H = (p - 1) * p ** (L - 1)
            for u in range(1, 3 * p):
                if u % p == 0:
                    continue
                q = u**H - 1
                check(vp_int(q, p) >= L)
                for j in range(min(H, 4)):
                    for x in range(8):
                        rhs = u**j * sum(q**r * math.comb(x, r) for r in range(x + 1))
                        check(rhs == u ** (H * x + j))
    for L in (3, 4, 5):
        H = 2 ** (L - 2)
        for u in range(1, 16, 2):
            q = u**H - 1
            check(vp_int(q, 2) >= L)
            for j in range(min(H, 4)):
                for x in range(8):
                    rhs = u**j * sum(q**r * math.comb(x, r) for r in range(x + 1))
                    check(rhs == u ** (H * x + j))

    rng = random.Random(917)
    for p in (3, 5):
        H = p - 1
        for _ in range(240):
            u = rng.randrange(1, 5 * p)
            if u % p == 0:
                continue
            j = rng.randrange(H)
            coeff = [rng.randrange(-4, 5) for _ in range(rng.randrange(1, 5))]
            d = len(coeff) - 1
            def P(n: int) -> int:
                return sum(coeff[k] * n**k for k in range(len(coeff)))
            q = u**H - 1
            for r in range(0, 8):
                vals = [P(H * x + j) * u ** (H * x + j) for x in range(r + 1)]
                actual = sum((-1) ** (r - x) * math.comb(r, x) * vals[x] for x in range(r + 1))
                # finite differences of Q at zero
                Qvals = [P(H * x + j) for x in range(d + 1)]
                row = Qvals[:]
                diffs = []
                while row:
                    diffs.append(row[0])
                    row = [row[i + 1] - row[i] for i in range(len(row) - 1)]
                predicted = u**j * sum(math.comb(r, k) * diffs[k] * (u**H) ** k * q ** (r - k) for k in range(min(d, r) + 1))
                check(actual == predicted, f"poly exponential p={p},r={r}")
                check(vp_int(actual, p) >= max(r - d, 0))

    C = [[1, 1], [1, 0]]
    C12 = matpow(C, 12)
    C24 = matpow(C, 24)
    check(C12 == [[233, 144], [144, 89]])
    check(C24 == [[75025, 46368], [46368, 28657]])
    for i in range(2):
        for j in range(2):
            target = 1 if i == j else 0
            check((C24[i][j] - target) % 24 == 0)
    def fib(n: int) -> int:
        a, b = 0, 1
        for _ in range(n):
            a, b = b, a + b
        return a
    for n in range(25):
        for r in range(6):
            check(finite_diff_step(fib, n, 24, r) % (24**r) == 0)


def group_local_euler_interpolation() -> None:
    e = euler_numbers(60)
    z = zigzag_odd(59, e)
    for p in (3, 5, 7, 11):
        sigma = (-1) ** ((p - 1) // 2)
        for n in range(0, 32, 2):
            sx = S(n, p) - sigma * p**n
            rhs = sum(((-1) ** r) * z[2 * r + 1] * math.comb(n, 2 * r) * p ** (2 * r) * (S(n - 2 * r, p) - sigma * p ** (n - 2 * r)) for r in range(n // 2 + 1))
            check(rhs == (1 - sigma * p**n) * e[n], f"depleted p={p},n={n}")
            check(sx == sum(((-1) ** a) * (2 * a + 1) ** n for a in range(p) if 2 * a + 1 != p))
        for j in range(0, p - 1, 2):
            for x in range(0, 6):
                n = (p - 1) * x + j
                rhs = 0
                for r in range(n // 2 + 1):
                    src = sum(((-1) ** a) * (2 * a + 1) ** (n - 2 * r) for a in range(p) if 2 * a + 1 != p)
                    rhs += ((-1) ** r) * z[2 * r + 1] * math.comb(n, 2 * r) * p ** (2 * r) * src
                check(rhs == (1 - sigma * p**n) * e[n])
    for n in range(0, 25):
        check(Fraction(9 ** (n + 1) - 1, 8 * (n + 1) * (2 * n + 1)) == R_source(2 * n))
        rhs = sum(beta(r) * 2 ** (2 * r) * falling(2 * n, 2 * r) * R_source(2 * n - 2 * r) for r in range(n + 1))
        check(rhs == e[2 * n], f"dyadic interpolation n={n}")


def group_polyphase_extensions() -> None:
    rng = random.Random(481)
    for M in range(2, 9):
        for _ in range(80):
            a = [rng.randrange(-20, 21) for _ in range(rng.randrange(1, 80))]
            phases = [[a[M * q + r] for q in range((len(a) - 1 - r) // M + 1)] if r < len(a) else [] for r in range(M)]
            recon = []
            for n in range(len(a)):
                recon.append(phases[n % M][n // M])
            check(recon == a)
            for N in range(2, 6):
                for r in range(M):
                    for s in range(N):
                        for q in range(0, 5):
                            idx = M * (N * q + s) + r
                            check(idx == M * N * q + r + M * s)
    # Carry law on finite sequences.
    for M in range(2, 7):
        for _ in range(120):
            a = [rng.randrange(-5, 6) for _ in range(12)]
            b = [rng.randrange(-5, 6) for _ in range(12)]
            c = [sum(a[i] * b[n - i] for i in range(n + 1) if i < len(a) and n - i < len(b)) for n in range(23)]
            for r in range(M):
                for q in range(0, 8):
                    lhs = c[M * q + r] if M * q + r < len(c) else 0
                    rhs = 0
                    for u in range(M):
                        for v in range(M):
                            if u + v == r:
                                rhs += sum(a[M * i + u] * b[M * (q - i) + v] for i in range(q + 1) if M * i + u < len(a) and M * (q - i) + v < len(b))
                            if u + v == r + M and q >= 1:
                                rhs += sum(a[M * i + u] * b[M * (q - 1 - i) + v] for i in range(q) if M * i + u < len(a) and M * (q - 1 - i) + v < len(b))
                    check(lhs == rhs, f"carry M={M},r={r},q={q}")
    # Affine kernel identities.
    for M in range(1, 8):
        for s in range(M):
            for k in range(0, 8):
                check(theta(M, s, k, k) == M**k)
                check(theta(M, s, M * k + s, k) == 1)
                for q in range(0, 8):
                    for r in range(0, min(24, M * q + s + 1)):
                        rhs = sum(theta(M, s, r, ell) * math.comb(q, ell) for ell in range(r + 1))
                        check(rhs == math.comb(M * q + s, r))
    for k in range(0, 20):
        for j in range(k + 1):
            check(theta(2, 0, k + j, k) == 2 ** (k - j) * math.comb(k, j))
            check(vp_int(theta(2, 0, k + j, k), 2) == k - j + vp_int(math.comb(k, j), 2))
    for M in range(1, 6):
        for N in range(1, 6):
            for s in range(M):
                for t in range(N):
                    for r in range(0, 18):
                        for ell in range(0, 7):
                            lhs = sum(theta(M, s, r, k) * theta(N, t, k, ell) for k in range(r + 1))
                            check(lhs == theta(M * N, M * t + s, r, ell))
    for p in (2, 3, 5, 7):
        for a in (1, 2):
            M = p**a
            for s in range(min(M, 10)):
                for k in range(0, 6):
                    for r in range(0, M * k + s + 1):
                        u = r - M * k
                        rhs = math.comb(s, u) if 0 <= u <= s else 0
                        check((theta(M, s, r, k) - rhs) % p == 0)
    # Scalar and matrix precision amplification.
    for p in (3, 5, 7):
        for a in range(0, 4):
            H = (p - 1) * p**a
            for u in range(1, 2 * p):
                if u % p == 0:
                    continue
                for n in range(8):
                    for r in range(5):
                        d = finite_diff_step(lambda m: u**m, n, H, r)
                        check(vp_int(d, p) >= (a + 1) * r)
    for a in range(0, 5):
        H = 2 ** (a + 1)
        for u in (3, 5, 7, 11):
            for n in range(8):
                for r in range(5):
                    d = finite_diff_step(lambda m: u**m, n, H, r)
                    check(vp_int(d, 2) >= (a + 3) * r)
    C = [[1, 1], [1, 0]]
    for a in range(0, 5):
        X = matpow(C, 12 * 2**a)
        mod = 2 ** (a + 3)
        for i, j in itertools.product(range(2), repeat=2):
            check((X[i][j] - (1 if i == j else 0)) % mod == 0)


def group_final_source_integrity() -> None:
    # Reuse the baseline source audit after overriding its paths.
    base.group_source_integrity()
    tex = TEX.read_text()
    # Every proved result carries a proof.
    proved = sum(len(re.findall(rf"\\begin\{{{env}\}}", tex)) for env in ("theorem", "proposition", "lemma", "corollary"))
    proofs = len(re.findall(r"\\begin\{proof\}", tex))
    check(proved == 82, f"expected 82 proved records, found {proved}")
    check(proofs == 82)
    required = {
        "thm:unified_local_euler",
        "thm:unified_inverse_local_euler",
        "thm:exact_dyadic_kernel_weight",
        "thm:optimal_dyadic_truncation",
        "thm:carmichael_mahler_scalar",
        "thm:direct_dyadic_interpolation",
        "thm:discrete_polyphase_reconstruction",
        "thm:polyphase_shift_matrix",
        "thm:mahler_polyphase_transfer",
        "prop:affine_kernel_edges",
        "thm:scalar_polyphase_precision",
        "thm:matrix_polyphase_precision",
    }
    labels = set(re.findall(r"\\label\{([^}]+)\}", tex))
    check(required <= labels, f"missing required labels {sorted(required-labels)}")
    check("We develop" not in tex)
    check("Moreover," not in tex)


def run_group(name: str, fn) -> None:
    before = base.checks
    fn()
    base.groups.append((name, base.checks - before))


def main() -> None:
    # Baseline verified theorem blocks retained from the strengthened edition.
    run_group("Hurwitz modes and standard periods", base.group_hurwitz_and_period)
    run_group("Triangular inverses and standard windows", base.group_triangular_and_standard_windows)
    run_group("Odd modulus Euler coordinates", base.group_odd_euler_coordinates)
    run_group("Dyadic Euler coordinates", base.group_dyadic_coordinates)
    run_group("Unit modes and Mahler coordinates", base.group_unit_modes_and_mahler)
    run_group("Linear lifting obstructions", base.group_linear_lifting)
    run_group("Polynomial lifting obstructions", base.group_polynomial_lifting)
    run_group("Recurrence packets", base.group_recurrences)
    run_group("Chinese remainder packets", base.group_crt_packets)
    run_group("Legacy arithmetic tables", base.group_legacy_tables)

    # New local and polyphase extensions.
    run_group("Unified local Euler coordinate pair", group_unified_local_euler)
    run_group("Sharp dyadic transfer depth", group_sharp_dyadic_depth)
    run_group("Carmichael and finite adelic transfer", group_carmichael_mahler_extensions)
    run_group("Local Euler interpolation", group_local_euler_interpolation)
    run_group("Discrete and Mahler polyphase refinement", group_polyphase_extensions)
    run_group("Final source and package integrity", group_final_source_integrity)

    lines = [
        f"Paper IX unified verification: {base.checks}/{base.checks} checks passed in {len(base.groups)} groups",
        "",
    ]
    lines.extend(f"{name}: {count}" for name, count in base.groups)
    summary = "\n".join(lines) + "\n"
    print(summary, end="")
    (HERE / "verification_summary.txt").write_text(summary)
    (HERE / "verification_summary.json").write_text(json.dumps({
        "status": "PASS",
        "checks": base.checks,
        "groups": [{"name": name, "checks": count} for name, count in base.groups],
    }, indent=2))


if __name__ == "__main__":
    main()
