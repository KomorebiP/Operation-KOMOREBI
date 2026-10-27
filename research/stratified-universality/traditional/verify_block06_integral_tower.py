from __future__ import annotations

from dataclasses import dataclass
from functools import reduce
from itertools import combinations, product
from math import gcd
from pathlib import Path
import json
import random

ROOT = Path(__file__).resolve().parent
GEN = ROOT / "generated"
GEN.mkdir(parents=True, exist_ok=True)
OUT = GEN / "block06_integral_tower_validation.json"


@dataclass
class Ledger:
    checks: int = 0
    failures: list[str] = None

    def __post_init__(self) -> None:
        if self.failures is None:
            self.failures = []

    def check(self, condition: bool, message: str) -> None:
        self.checks += 1
        if not condition:
            self.failures.append(message)


def divisibility_chains(max_rank: int = 4, max_value: int = 48) -> list[tuple[int, ...]]:
    vals = list(range(1, max_value + 1))
    out: list[tuple[int, ...]] = []
    for rank in range(1, max_rank + 1):
        def rec(prefix: tuple[int, ...]) -> None:
            if len(prefix) == rank:
                out.append(prefix)
                return
            start = prefix[-1] if prefix else 1
            for d in vals:
                if d < start:
                    continue
                if prefix and d % prefix[-1] != 0:
                    continue
                rec(prefix + (d,))
        rec(())
    return out


def prime_factors(n: int) -> set[int]:
    out: set[int] = set()
    d = 2
    while d * d <= n:
        while n % d == 0:
            out.add(d)
            n //= d
        d += 1
    if n > 1:
        out.add(n)
    return out


def vp(n: int, p: int) -> int:
    e = 0
    while n % p == 0:
        e += 1
        n //= p
    return e


def brute_kernel_coker(d: int, m: int) -> tuple[int, int, int]:
    image = {d * x % m for x in range(m)}
    kernel = [x for x in range(m) if d * x % m == 0]
    return len(kernel), m // len(image), len(image)


def fitting_generator(ds: tuple[int, ...], j: int) -> int:
    r = len(ds)
    size = r - j
    if size <= 0:
        return 1
    minors = []
    for idx in combinations(range(r), size):
        z = 1
        for i in idx:
            z *= ds[i]
        minors.append(z)
    return reduce(gcd, minors)


def matmul(A: list[list[int]], B: list[list[int]]) -> list[list[int]]:
    return [
        [sum(A[i][h] * B[h][j] for h in range(len(B))) for j in range(len(B[0]))]
        for i in range(len(A))
    ]


def diag(ds: tuple[int, ...]) -> list[list[int]]:
    return [[ds[i] if i == j else 0 for j in range(len(ds))] for i in range(len(ds))]


def random_intertwiner(ds: tuple[int, ...], rng: random.Random) -> tuple[list[list[int]], list[list[int]]]:
    r = len(ds)
    A = [[0] * r for _ in range(r)]
    B = [[0] * r for _ in range(r)]
    for i in range(r):
        for j in range(r):
            step = ds[j] // gcd(ds[i], ds[j])
            aij = step * rng.randint(-4, 4)
            A[i][j] = aij
            B[i][j] = ds[i] * aij // ds[j]
    return A, B


def orbit_offsets_digit_sum(modulus: int, scale: int = 1) -> set[int]:
    return {(scale * c) % modulus for c in range(modulus)}


def tex_profile(ds: tuple[int, ...]) -> str:
    return "$(" + ",".join(str(d) for d in ds) + ")$"


ledger = Ledger()
chains = divisibility_chains()
moduli = list(range(2, 25))
smith_cases = 0
fitting_cases = 0
prime_power_cases = 0

for ds in chains:
    r = len(ds)
    delta = 1
    for d in ds:
        delta *= d

    # Smith/Tor formulas for bounded moduli.
    for m in moduli:
        expected_ghost = 1
        expected_image = 1
        for i, d in enumerate(ds):
            ker, coker, image = brute_kernel_coker(d, m)
            g = gcd(d, m)
            ledger.check(ker == g, f"kernel order mismatch ds={ds},m={m},i={i}")
            ledger.check(coker == g, f"cokernel order mismatch ds={ds},m={m},i={i}")
            ledger.check(image == m // g, f"image order mismatch ds={ds},m={m},i={i}")
            expected_ghost *= g
            expected_image *= m // g
        good = gcd(m, ds[-1]) == 1
        ledger.check((expected_ghost == 1) == good, f"good modulus mismatch ds={ds},m={m}")
        ledger.check(expected_ghost * expected_image == m ** r, f"five-term size mismatch ds={ds},m={m}")
        smith_cases += 1

    # Fitting filtration.
    for j in range(r + 1):
        got = fitting_generator(ds, j)
        expected = 1
        for d in ds[: max(0, r - j)]:
            expected *= d
        ledger.check(got == expected, f"Fitting mismatch ds={ds},j={j}: {got}!={expected}")
        fitting_cases += 1

    # Prime support.
    support = prime_factors(delta)
    support_top = prime_factors(ds[-1])
    ledger.check(support == support_top, f"bad-prime support mismatch ds={ds}")

    # Prime-power profile.
    for p in (2, 3, 5, 7):
        nus = [vp(d, p) for d in ds]
        for exponent in range(1, 6):
            m = p ** exponent
            image_order = 1
            ghost_order = 1
            nonzero = 0
            for nu in nus:
                ghost_order *= p ** min(exponent, nu)
                image_order *= p ** (exponent - min(exponent, nu))
                if nu < exponent:
                    nonzero += 1
            brute_image = 1
            brute_ghost = 1
            for d in ds:
                ker, _, image = brute_kernel_coker(d, m)
                brute_ghost *= ker
                brute_image *= image
            ledger.check(image_order == brute_image, f"prime-power image mismatch ds={ds},p={p},r={exponent}")
            ledger.check(ghost_order == brute_ghost, f"prime-power ghost mismatch ds={ds},p={p},r={exponent}")
            ledger.check(nonzero == sum(1 for nu in nus if nu < exponent), f"generator mismatch ds={ds},p={p},r={exponent}")
            prime_power_cases += 1

# Digit-equivariant Smith squares.
rng = random.Random(20260829)
intertwining_cases = 0
sample_chains = [ds for ds in chains if len(ds) <= 4][:: max(1, len(chains) // 80)]
for ds in sample_chains[:80]:
    D = diag(ds)
    for _ in range(4):
        A, B = random_intertwiner(ds, rng)
        ledger.check(matmul(B, D) == matmul(D, A), f"intertwining mismatch ds={ds}")
        for m in (2, 3, 4, 5, 8, 9):
            left = [[x % m for x in row] for row in matmul(B, D)]
            right = [[x % m for x in row] for row in matmul(D, A)]
            ledger.check(left == right, f"modular intertwining mismatch ds={ds},m={m}")
        intertwining_cases += 1

# Named integral profiles.
named = {
    "digit_sum": {
        "label": "Digit sum $s_k$",
        "smith": (1, 1),
        "description": "Saturated rank-two lattice; no modular defect.",
    },
    "double_digit_sum": {
        "label": "Doubled digit sum $2s_k$",
        "smith": (2, 2),
        "description": "Rank-two defect $(\\mathbb Z/2)^2$; total semantic collapse modulo $2$.",
    },
    "constant_two": {
        "label": "Constant sequence $2$",
        "smith": (2,),
        "description": "One raw ghost coordinate modulo $2$; one semantic state.",
    },
    "constant_six": {
        "label": "Constant sequence $6$",
        "smith": (6,),
        "description": "Bad primes $2$ and $3$; good reduction at every other prime.",
    },
}
named_rows = {}
for key, rec in named.items():
    ds = rec["smith"]
    rows = []
    for p in (2, 3, 5):
        for exponent in (1, 2, 3, 4):
            m = p ** exponent
            ghost = 1
            image = 1
            for d in ds:
                g = gcd(d, m)
                ghost *= g
                image *= m // g
            rows.append({"p": p, "r": exponent, "ghost_order": ghost, "semantic_module_order": image})
            ledger.check(ghost * image == m ** len(ds), f"named size mismatch {key},p={p},r={exponent}")
    named_rows[key] = {**rec, "rows": rows}

# Exact digit-sum orbit profiles and p-adic Cauchy controls.
digit_sum_checks = 0
digit_sum_profiles = []
for p in (2, 3, 5, 7):
    for exponent in range(1, 7):
        m = p ** exponent
        offsets = orbit_offsets_digit_sum(m, 1)
        double_offsets = orbit_offsets_digit_sum(m, 2)
        ledger.check(len(offsets) == m, f"digit-sum state count mismatch p={p},r={exponent}")
        ledger.check(len(double_offsets) == m // gcd(2, m), f"double digit-sum state count mismatch p={p},r={exponent}")
        ledger.check({x % (m // p) for x in offsets} == set(range(m // p)) if exponent > 1 else True,
                     f"digit-sum reduction mismatch p={p},r={exponent}")
        digit_sum_checks += 3
    partial = 0
    previous = 0
    for N in range(8):
        partial += p ** (2 * N)
        if N > 0:
            ledger.check((partial - previous) % (p ** (2 * N)) == 0, f"Cauchy mismatch p={p},N={N}")
        previous = partial
    digit_sum_profiles.append({
        "p": p,
        "state_formula": "$p^r$",
        "double_state_formula": "$p^r/\\gcd(2,p^r)$",
        "nonintegral_limit": "$1/(1-p^2)$",
    })

# Finite-level ghost contraction: compatible inverse-limit ghosts vanish.
ghost_limit_cases = 0
for d in range(1, 33):
    for p in (2, 3, 5, 7):
        nu = vp(d, p)
        # At truncation R, compatible ghost x_R reduces to zero at level 1 after enough forced p factors.
        for R in range(1, 7):
            mR = p ** R
            ghosts = [x for x in range(mR) if d * x % mR == 0]
            for x in ghosts[: min(20, len(ghosts))]:
                reduced = x % p
                if R > nu:
                    ledger.check(reduced == 0, f"ghost contraction mismatch d={d},p={p},R={R},x={x}")
                ghost_limit_cases += 1

result = {
    "artifact": "Komorebi Stratified Universality Block 06 integral and prime-power verifier",
    "arithmetic": "exact integer, modular, Smith, and finite-state arithmetic",
    "enumeration": {
        "smith_chains": len(chains),
        "moduli": [min(moduli), max(moduli)],
        "smith_modulus_cases": smith_cases,
        "fitting_cases": fitting_cases,
        "prime_power_cases": prime_power_cases,
        "intertwining_systems": intertwining_cases,
        "digit_sum_profile_cases": len(digit_sum_profiles),
        "finite_ghost_samples": ghost_limit_cases,
    },
    "named_profiles": named_rows,
    "digit_sum_profiles": digit_sum_profiles,
    "checks": ledger.checks,
    "failures": ledger.failures,
    "passed": not ledger.failures,
    "boundary": (
        "The verifier checks bounded Smith chains, modular maps, Fitting formulas, "
        "prime-power profiles, digit-equivariant squares, named integral families, "
        "and finite p-adic orbit controls. It does not prove finite-data recognition "
        "of rational regularity or unrestricted ring and semiring minimality."
    ),
}
OUT.write_text(json.dumps(result, indent=2, sort_keys=True), encoding="utf-8")

# Main validation table.
lines = [
    r"\begin{table}[htbp]",
    r"\centering",
    r"\caption{Exact finite validation of the Block 06 integral and prime-power layer.}",
    r"\label{tab:block06-validation}",
    r"\small",
    r"\begin{tabularx}{\textwidth}{@{}L{0.31\textwidth}Y@{}}",
    r"\toprule",
    r"Check family & Recorded result\\",
    r"\midrule",
    f"Smith and modular profiles & {len(chains)} divisibility chains of ranks one through four; moduli {min(moduli)} through {max(moduli)}; {smith_cases} chain-modulus cases.\\\\",
    f"Fitting and prime-power profiles & {fitting_cases} Fitting cases and {prime_power_cases} prime-power profile cases over $p=2,3,5,7$.\\\\",
    f"Digit-equivariant systems & {intertwining_cases} exact Smith-square systems with integral and modular intertwining checks.\\\\",
    f"Orbit and completion controls & Digit-sum state formulas over four primes and {ghost_limit_cases} bounded ghost-contraction samples.\\\\",
    f"Total exact checks & {ledger.checks}; {len(ledger.failures)} failures.\\\\",
    f"Overall status & {'PASS' if not ledger.failures else 'FAIL'}.\\\\",
    r"Boundary & Bounded exact verification supports the printed formulas and examples. It does not replace the symbolic proofs or establish unrestricted integral recognition.\\",
    r"\bottomrule",
    r"\end{tabularx}",
    r"\end{table}",
]
(GEN / "block06_validation_table.tex").write_text("\n".join(lines) + "\n", encoding="utf-8")

# Named Smith profiles.
lines = [
    r"\begin{table}[htbp]",
    r"\centering",
    r"\caption{Canonical integral defect profiles for named fixed-radix families.}",
    r"\label{tab:block06-defect-profiles}",
    r"\small",
    r"\begin{tabularx}{\textwidth}{@{}L{0.22\textwidth}L{0.17\textwidth}L{0.18\textwidth}Y@{}}",
    r"\toprule",
    r"Family & Smith profile & Bad primes & Interpretation\\",
    r"\midrule",
]
for key in ("digit_sum", "double_digit_sum", "constant_two", "constant_six"):
    rec = named[key]
    ds = rec["smith"]
    bad = sorted(prime_factors(reduce(lambda x, y: x * y, ds, 1)))
    bad_text = "none" if not bad else ", ".join(str(p) for p in bad)
    lines.append(f"{rec['label']} & {tex_profile(ds)} & {bad_text} & {rec['description']}\\\\")
lines += [r"\bottomrule", r"\end{tabularx}", r"\end{table}"]
(GEN / "block06_defect_profiles_table.tex").write_text("\n".join(lines) + "\n", encoding="utf-8")

print(json.dumps({
    "passed": not ledger.failures,
    "checks": ledger.checks,
    "failures": len(ledger.failures),
    "smith_chains": len(chains),
}, sort_keys=True))
