from __future__ import annotations

from dataclasses import dataclass
from itertools import product
from math import comb, gcd
from pathlib import Path
import json

ROOT = Path(__file__).resolve().parent
GEN = ROOT / "generated"
GEN.mkdir(parents=True, exist_ok=True)
OUT = GEN / "block07_product_multiplicative_validation.json"


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


def divisors(n: int) -> list[int]:
    return [d for d in range(1, n + 1) if n % d == 0]


def mobius(n: int) -> int:
    if n == 1:
        return 1
    x = n
    primes = 0
    p = 2
    while p * p <= x:
        if x % p == 0:
            x //= p
            primes += 1
            if x % p == 0:
                return 0
            while x % p == 0:
                x //= p
        p += 1
    if x > 1:
        primes += 1
    return -1 if primes % 2 else 1


def primes_upto(n: int) -> list[int]:
    out: list[int] = []
    for x in range(2, n + 1):
        if all(x % p for p in out if p * p <= x):
            out.append(x)
    return out


def factorization(n: int, primes: list[int]) -> dict[int, int]:
    x = n
    out: dict[int, int] = {}
    for p in primes:
        if p * p > x:
            break
        while x % p == 0:
            out[p] = out.get(p, 0) + 1
            x //= p
    if x > 1:
        out[x] = out.get(x, 0) + 1
    return out


def vp(n: int, p: int) -> int:
    e = 0
    while n % p == 0:
        n //= p
        e += 1
    return e


def factor_series(m: int, exponent: int, N: int) -> list[int]:
    out = [0] * (N + 1)
    if exponent == 0:
        out[0] = 1
        return out
    if exponent > 0:
        j = 0
        while j * m <= N:
            out[j * m] = comb(exponent + j - 1, j)
            j += 1
        return out
    r = -exponent
    for j in range(0, min(r, N // m) + 1):
        out[j * m] = (-1) ** j * comb(r, j)
    return out


def series_mul(a: list[int], b: list[int], N: int) -> list[int]:
    out = [0] * (N + 1)
    for i, ai in enumerate(a[: N + 1]):
        if ai == 0:
            continue
        for j, bj in enumerate(b[: N + 1 - i]):
            if bj:
                out[i + j] += ai * bj
    return out


def euler_from_b(b: list[int], N: int) -> list[int]:
    out = [1] + [0] * N
    for m in range(1, min(N, len(b) - 1) + 1):
        out = series_mul(out, factor_series(m, b[m], N), N)
    return out


def ghost_from_b(b: list[int], N: int) -> list[int]:
    c = [0] * (N + 1)
    for n in range(1, N + 1):
        c[n] = sum(d * b[d] for d in divisors(n))
    return c


def ghost_from_a(a: list[int], N: int) -> list[int]:
    c = [0] * (N + 1)
    for n in range(1, N + 1):
        c[n] = n * a[n] - sum(c[k] * a[n - k] for k in range(1, n))
    return c


def b_from_ghost(c: list[int], N: int) -> tuple[list[int], list[int]]:
    b = [0] * (N + 1)
    remainders = [0] * (N + 1)
    for n in range(1, N + 1):
        numerator = sum(mobius(n // d) * c[d] for d in divisors(n))
        b[n], remainders[n] = divmod(numerator, n)
    return b, remainders


def series_equal(a: list[int], b: list[int], N: int) -> bool:
    return a[: N + 1] == b[: N + 1]


def dirichlet_convolution(f: list[int], g: list[int], N: int) -> list[int]:
    h = [0] * (N + 1)
    for n in range(1, N + 1):
        h[n] = sum(f[d] * g[n // d] for d in divisors(n))
    return h


def local_beta(seed: int, p: int, E: int) -> list[int]:
    beta = [0] * (E + 1)
    for m in range(1, E + 1):
        v = ((seed * (p + 5) + 3 * p + 7 * m + seed // 3) % 5) - 2
        # Force a substantial number of sparse local systems.
        if (seed + p + m) % 4 == 0:
            v = 0
        beta[m] = v
    return beta


def multiplicative_from_local(local: dict[int, list[int]], N: int, primes: list[int]) -> list[int]:
    f = [0] * (N + 1)
    f[1] = 1
    for n in range(2, N + 1):
        val = 1
        for p, e in factorization(n, primes).items():
            val *= local[p][e]
        f[n] = val
    return f


def local_series_from_beta(beta: list[int], E: int) -> list[int]:
    return euler_from_b(beta, E)


def local_ghost(beta: list[int], E: int) -> list[int]:
    return ghost_from_b(beta, E)


def is_multiplicative(f: list[int], N: int, ledger: Ledger, tag: str) -> None:
    ledger.check(f[1] == 1, f"{tag}: f(1) != 1")
    for m in range(1, N + 1):
        for n in range(1, N // m + 1):
            if gcd(m, n) == 1:
                ledger.check(f[m * n] == f[m] * f[n], f"{tag}: multiplicativity failed at {m},{n}")


def divisor_ghost(b_values: list[int], N: int) -> list[int]:
    c = [0] * (N + 1)
    for n in range(1, N + 1):
        c[n] = sum(d * b_values[d] for d in divisors(n))
    return c


def inverse_divisor_ghost(c: list[int], N: int) -> tuple[list[int], list[int]]:
    b = [0] * (N + 1)
    rem = [0] * (N + 1)
    for n in range(1, N + 1):
        numerator = sum(mobius(n // d) * c[d] for d in divisors(n))
        b[n], rem[n] = divmod(numerator, n)
    return b, rem


ledger = Ledger()
counters: dict[str, int] = {}

# ---------------------------------------------------------------------------
# 1. Euler-coordinate, ghost, and coefficient recurrence atlas.
# ---------------------------------------------------------------------------
N_EULER = 6
euler_vectors = 0
for vals in product(range(-2, 3), repeat=N_EULER):
    b = [0] + list(vals)
    a = euler_from_b(b, N_EULER)
    c = ghost_from_b(b, N_EULER)
    c_from_a = ghost_from_a(a, N_EULER)
    b_back, rem = b_from_ghost(c, N_EULER)
    for n in range(1, N_EULER + 1):
        ledger.check(c_from_a[n] == c[n], f"Euler ghost mismatch b={vals},n={n}")
        ledger.check(rem[n] == 0, f"Euler integrality mismatch b={vals},n={n}")
        ledger.check(b_back[n] == b[n], f"Euler inverse mismatch b={vals},n={n}")
        lhs = n * a[n]
        rhs = sum(c[k] * a[n - k] for k in range(1, n + 1))
        ledger.check(lhs == rhs, f"Euler recurrence mismatch b={vals},n={n}")
    ledger.check(series_equal(euler_from_b(b_back, N_EULER), a, N_EULER), f"Euler roundtrip mismatch b={vals}")

    # A deterministic partner tests the group law without quadratic enumeration.
    partner = [0] + [(-1 if i % 2 else 1) * vals[N_EULER - 1 - i] for i in range(N_EULER)]
    a_partner = euler_from_b(partner, N_EULER)
    summed = [0] + [b[i] + partner[i] for i in range(1, N_EULER + 1)]
    ledger.check(
        series_equal(series_mul(a, a_partner, N_EULER), euler_from_b(summed, N_EULER), N_EULER),
        f"Euler product law mismatch b={vals}",
    )
    c_partner = ghost_from_b(partner, N_EULER)
    c_sum = ghost_from_b(summed, N_EULER)
    ledger.check(all(c_sum[i] == c[i] + c_partner[i] for i in range(1, N_EULER + 1)), f"ghost additivity mismatch b={vals}")
    euler_vectors += 1
counters["euler_exponent_vectors"] = euler_vectors

# Surjectivity from arbitrary integral unit coefficients on a bounded prefix.
coefficient_vectors = 0
N_COEFF = 5
for vals in product(range(-2, 3), repeat=N_COEFF):
    a = [1] + list(vals)
    c = ghost_from_a(a, N_COEFF)
    b, rem = b_from_ghost(c, N_COEFF)
    for n in range(1, N_COEFF + 1):
        ledger.check(rem[n] == 0, f"arbitrary coefficient Euler divisibility failed a={vals},n={n}")
    ledger.check(series_equal(euler_from_b(b, N_COEFF), a, N_COEFF), f"arbitrary coefficient roundtrip failed a={vals}")
    coefficient_vectors += 1
counters["arbitrary_unit_prefixes"] = coefficient_vectors

# ---------------------------------------------------------------------------
# 2. Multiplicative functions, local series, prime-Euler coordinates.
# ---------------------------------------------------------------------------
N_MULT = 60
E_MULT = 6
PRIMES = primes_upto(N_MULT)
mult_systems: list[dict] = []
for seed in range(96):
    beta_by_p: dict[int, list[int]] = {}
    local_by_p: dict[int, list[int]] = {}
    gamma_by_p: dict[int, list[int]] = {}
    for p in PRIMES:
        beta = local_beta(seed, p, E_MULT)
        beta_by_p[p] = beta
        local_by_p[p] = local_series_from_beta(beta, E_MULT)
        gamma_by_p[p] = local_ghost(beta, E_MULT)
    f = multiplicative_from_local(local_by_p, N_MULT, PRIMES)
    is_multiplicative(f, N_MULT, ledger, f"system {seed}")

    # Prime-power reconstruction and local recurrence.
    for n in range(1, N_MULT + 1):
        val = 1
        for p, e in factorization(n, PRIMES).items():
            val *= local_by_p[p][e]
        ledger.check(val == f[n], f"prime-power reconstruction failed seed={seed},n={n}")
    for p in PRIMES:
        local = local_by_p[p]
        gamma = gamma_by_p[p]
        beta_back, rem = b_from_ghost(gamma, E_MULT)
        for e in range(1, E_MULT + 1):
            ledger.check(rem[e] == 0, f"local ghost divisibility failed seed={seed},p={p},e={e}")
            ledger.check(beta_back[e] == beta_by_p[p][e], f"local beta inverse failed seed={seed},p={p},e={e}")
            lhs = e * local[e]
            rhs = sum(gamma[j] * local[e - j] for j in range(1, e + 1))
            ledger.check(lhs == rhs, f"local recurrence failed seed={seed},p={p},e={e}")

    # Valuation logarithmic derivative identity for selected primes.
    for p in (2, 3, 5, 7):
        gamma = gamma_by_p[p]
        for n in range(1, N_MULT + 1):
            e = vp(n, p)
            rhs = sum(gamma[j] * f[n // (p ** j)] for j in range(1, e + 1))
            ledger.check(e * f[n] == rhs, f"valuation derivative failed seed={seed},p={p},n={n}")

    mult_systems.append({"seed": seed, "beta": beta_by_p, "local": local_by_p, "gamma": gamma_by_p, "f": f})
counters["multiplicative_systems"] = len(mult_systems)

# Dirichlet convolution, local Cauchy product, beta/ghost additivity, and residue packets.
convolution_pairs = 0
for pair_index in range(48):
    left = mult_systems[(7 * pair_index + 3) % len(mult_systems)]
    right = mult_systems[(11 * pair_index + 5) % len(mult_systems)]
    f = left["f"]
    g = right["f"]
    h = dirichlet_convolution(f, g, N_MULT)
    is_multiplicative(h, N_MULT, ledger, f"convolution {pair_index}")

    for p in PRIMES:
        expected_local = series_mul(left["local"][p], right["local"][p], E_MULT)
        for e in range(0, E_MULT + 1):
            ledger.check(h[p ** e] == expected_local[e] if p ** e <= N_MULT else True,
                         f"local convolution failed pair={pair_index},p={p},e={e}")
        beta_h, rem = b_from_ghost(ghost_from_a(expected_local, E_MULT), E_MULT)
        gamma_h = ghost_from_a(expected_local, E_MULT)
        for e in range(1, E_MULT + 1):
            ledger.check(rem[e] == 0, f"convolution beta divisibility failed pair={pair_index},p={p},e={e}")
            ledger.check(beta_h[e] == left["beta"][p][e] + right["beta"][p][e],
                         f"beta additivity failed pair={pair_index},p={p},e={e}")
            ledger.check(gamma_h[e] == left["gamma"][p][e] + right["gamma"][p][e],
                         f"ghost additivity failed pair={pair_index},p={p},e={e}")

    # Residue packet law, tested coefficientwise and grouped by divisor residues.
    for modulus in (5, 6, 8):
        for n in range(1, N_MULT + 1):
            k = n % modulus
            grouped = 0
            for r in range(modulus):
                for s in range(modulus):
                    if (r * s) % modulus != k:
                        continue
                    grouped += sum(
                        f[d] * g[n // d]
                        for d in divisors(n)
                        if d % modulus == r and (n // d) % modulus == s
                    )
            ledger.check(grouped == h[n], f"residue packet law failed pair={pair_index},N={modulus},n={n}")
    convolution_pairs += 1
counters["dirichlet_convolution_pairs"] = convolution_pairs

# ---------------------------------------------------------------------------
# 3. Divisor-ghost bridge on the multiplicative Euler-exponent overlap.
# ---------------------------------------------------------------------------
N_BRIDGE = 32
bridge_systems = 0
for seed in range(128):
    # Build a multiplicative exponent function b from bounded prime-power seeds.
    b_local: dict[int, list[int]] = {}
    for p in primes_upto(N_BRIDGE):
        vals = [1]
        for e in range(1, 6):
            vals.append(((seed + p * (e + 1) + e * e) % 5) - 2)
        b_local[p] = vals
    b_values = multiplicative_from_local(b_local, N_BRIDGE, primes_upto(N_BRIDGE))
    is_multiplicative(b_values, N_BRIDGE, ledger, f"bridge exponent {seed}")
    c_values = divisor_ghost(b_values, N_BRIDGE)
    is_multiplicative(c_values, N_BRIDGE, ledger, f"bridge ghost {seed}")
    b_back, rem = inverse_divisor_ghost(c_values, N_BRIDGE)
    for n in range(1, N_BRIDGE + 1):
        ledger.check(rem[n] == 0, f"divisor ghost integrality failed seed={seed},n={n}")
        ledger.check(b_back[n] == b_values[n], f"divisor ghost inverse failed seed={seed},n={n}")

    # Prime-power comparison and ordinary Euler recurrence.
    for p in primes_upto(N_BRIDGE):
        previous = 0
        for e in range(0, 6):
            pe = p ** e
            if pe > N_BRIDGE:
                break
            if e == 0:
                previous = c_values[1]
                continue
            ledger.check(c_values[pe] == sum((p ** j) * b_local[p][j] for j in range(e + 1)),
                         f"prime-power ghost formula failed seed={seed},p={p},e={e}")
            ledger.check(c_values[pe] - previous == pe * b_local[p][e],
                         f"prime-power inverse difference failed seed={seed},p={p},e={e}")
            previous = c_values[pe]

    N_SER = 16
    A = euler_from_b(b_values[: N_SER + 1], N_SER)
    for n in range(1, N_SER + 1):
        ledger.check(n * A[n] == sum(c_values[k] * A[n - k] for k in range(1, n + 1)),
                     f"bridge Euler recurrence failed seed={seed},n={n}")
    bridge_systems += 1
counters["multiplicative_euler_overlap_systems"] = bridge_systems

# Named power family b(n)=n^r gives ghost sigma_{r+1}.
power_family_rows = []
for r in range(0, 6):
    N = 40
    b_values = [0] + [n ** r for n in range(1, N + 1)]
    c_values = divisor_ghost(b_values, N)
    for n in range(1, N + 1):
        sigma = sum(d ** (r + 1) for d in divisors(n))
        ledger.check(c_values[n] == sigma, f"power divisor ghost failed r={r},n={n}")
    coeffs = euler_from_b(b_values[:13], 12)
    power_family_rows.append({
        "r": r,
        "ghost": f"sigma_{r+1}",
        "coefficients": coeffs[:8],
    })
counters["power_bridge_families"] = len(power_family_rows)

# Named local Euler coordinates.
named_local = {
    "one": {"seed": [1] * 9, "beta": {1: 1}},
    "mobius": {"seed": [1, -1] + [0] * 7, "beta": {1: -1}},
    "liouville": {"seed": [(-1) ** e for e in range(9)], "beta": {1: -1, 2: 1}},
    "squarefree": {"seed": [1, 1] + [0] * 7, "beta": {1: 1, 2: -1}},
    "tau3": {"seed": [comb(e + 2, 2) for e in range(9)], "beta": {1: 3}},
}
named_rows = []
for name, rec in named_local.items():
    beta = [0] * 9
    for i, v in rec["beta"].items():
        beta[i] = v
    got = euler_from_b(beta, 8)
    for e in range(9):
        ledger.check(got[e] == rec["seed"][e], f"named local coordinate failed {name},e={e}")
    gamma = ghost_from_b(beta, 8)
    named_rows.append({"name": name, "beta": rec["beta"], "seed": rec["seed"][:6], "gamma": gamma[1:7]})
counters["named_local_families"] = len(named_rows)

# Completely multiplicative geometric modes and necklace coordinates.
necklace_rows = []
for q in (-2, -1, 0, 1, 2, 3):
    E = 10
    gamma = [0] + [q ** e for e in range(1, E + 1)]
    beta, rem = b_from_ghost(gamma, E)
    for e in range(1, E + 1):
        ledger.check(rem[e] == 0, f"necklace integrality failed q={q},e={e}")
    local = euler_from_b(beta, E)
    for e in range(E + 1):
        ledger.check(local[e] == q ** e, f"geometric local series failed q={q},e={e}")
    necklace_rows.append({"q": q, "beta": beta[1:7]})
counters["necklace_modes"] = len(necklace_rows)

result = {
    "status": "PASS" if not ledger.failures else "FAIL",
    "checks": ledger.checks,
    "failures": ledger.failures,
    "counters": counters,
    "power_family_rows": power_family_rows,
    "named_local_rows": named_rows,
    "necklace_rows": necklace_rows,
    "boundary": (
        "Bounded exact verification supports the Euler-coordinate, prime-power seed, "
        "Dirichlet convolution, divisor-ghost, and named-family formulas. It does not "
        "prove compact finite grammars for arbitrary exponent arrays or a global isomorphism "
        "between Cauchy and Dirichlet convolution."
    ),
}
OUT.write_text(json.dumps(result, indent=2), encoding="utf-8")

# LaTeX validation table.
validation_tex = r"""\begin{table}[htbp]
\centering
\caption{Exact finite validation of the Block 07 filtered-product and multiplicative layer.}
\label{tab:block07-validation}
\small
\begin{tabularx}{\textwidth}{@{}L{0.31\textwidth}Y@{}}
\toprule
Check family & Recorded result\\
\midrule
Euler-coordinate atlas & %d exponent prefixes and %d arbitrary integral unit-series prefixes.\\
Prime-power multiplicative atlas & %d deterministic local systems and %d Dirichlet-convolution pairs.\\
Divisor-ghost overlap & %d multiplicative exponent systems and %d power families.\\
Named local coordinates & %d arithmetic families and %d geometric necklace modes.\\
Total exact checks & %d; %d failures.\\
Overall status & %s.\\
Boundary & Bounded exact verification supports the printed formulas and examples. It does not establish compactness or minimality for arbitrary product grammars, nor a global Cauchy--Dirichlet algebra isomorphism.\\
\bottomrule
\end{tabularx}
\end{table}
""" % (
    counters["euler_exponent_vectors"],
    counters["arbitrary_unit_prefixes"],
    counters["multiplicative_systems"],
    counters["dirichlet_convolution_pairs"],
    counters["multiplicative_euler_overlap_systems"],
    counters["power_bridge_families"],
    counters["named_local_families"],
    counters["necklace_modes"],
    ledger.checks,
    len(ledger.failures),
    result["status"],
)
(GEN / "block07_validation_table.tex").write_text(validation_tex, encoding="utf-8")

# Named examples table.
name_map = {
    "one": r"Constant-one function $\mathbf 1$",
    "mobius": r"M\"obius $\mu$",
    "liouville": r"Liouville $\lambda$",
    "squarefree": r"Squarefree indicator $\mu^2$",
    "tau3": r"Three-fold divisor function $\tau_3$",
}
rows = []
for rec in named_rows:
    beta_text = ", ".join(f"$\\beta_{{{k}}}={v}$" for k, v in sorted(rec["beta"].items()))
    seed_text = "$" + ",".join(str(x) for x in rec["seed"]) + ",\\ldots$"
    gamma_text = "$" + ",".join(str(x) for x in rec["gamma"]) + ",\\ldots$"
    rows.append(f"{name_map[rec['name']]} & {beta_text} & {seed_text} & {gamma_text}\\\\")
examples_tex = "\n".join([
    r"\begin{table}[htbp]",
    r"\centering",
    r"\caption{Named prime-power seed families in local Euler coordinates.}",
    r"\label{tab:block07-named-local}",
    r"\scriptsize",
    r"\begin{tabularx}{\textwidth}{@{}L{0.24\textwidth}L{0.23\textwidth}L{0.25\textwidth}Y@{}}",
    r"\toprule",
    r"Arithmetic function & Nonzero local Euler exponents & Prime-power seed & Local ghost\\",
    r"\midrule",
    *rows,
    r"\bottomrule",
    r"\end{tabularx}",
    r"\end{table}",
]) + "\n"
(GEN / "block07_named_local_table.tex").write_text(examples_tex, encoding="utf-8")

print(json.dumps({"status": result["status"], "checks": ledger.checks, "failures": len(ledger.failures), **counters}, indent=2))
if ledger.failures:
    raise SystemExit(1)
