from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
from dataclasses import asdict, dataclass
from functools import reduce
from pathlib import Path
from typing import Iterable

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch, Rectangle
from sympy import factorint
from sympy.ntheory.modular import crt

PI = math.pi

INK = "#18212A"
MUTED = "#5B6770"
BLUE = "#2E6F9E"
TEAL = "#2A8C82"
ORANGE = "#D88745"
MAGENTA = "#9B4F83"
RED = "#C95C54"
GOLD = "#D6A84B"
PAPER = "#FAFAF7"
GRID = "#CCD4D8"
PALE_BLUE = "#E9F1F7"
PALE_TEAL = "#E7F3F0"
PALE_ORANGE = "#F8EEE5"
PALE_MAGENTA = "#F4EAF1"

plt.rcParams.update({
    "figure.facecolor": PAPER,
    "axes.facecolor": PAPER,
    "savefig.facecolor": PAPER,
    "font.family": "DejaVu Serif",
    "axes.edgecolor": INK,
    "axes.labelcolor": INK,
    "xtick.color": INK,
    "ytick.color": INK,
    "text.color": INK,
})


def exact_int(value: object, name: str = "value") -> int:
    if isinstance(value, bool):
        raise TypeError(f"{name} must be an integer, not bool")
    try:
        out = int(value)
    except Exception as exc:
        raise TypeError(f"{name} must be integer-like") from exc
    if str(value).strip() not in {str(out), f"+{out}"}:
        # numpy and pandas integer scalars pass through int exactly.  Decimal
        # strings with whitespace also remain safe.  Reject floats such as 3.5.
        try:
            if float(value) != float(out):
                raise TypeError(f"{name} is not integral")
        except Exception:
            pass
    return out


def vp_int(n: int, p: int) -> int:
    n = abs(exact_int(n, "n"))
    p = exact_int(p, "p")
    if p < 2:
        raise ValueError("p must be at least two")
    if n == 0:
        return 10**9
    value = 0
    while n % p == 0:
        value += 1
        n //= p
    return value


def radical_from_factors(factors: dict[int, int]) -> int:
    out = 1
    for p in factors:
        out *= int(p)
    return out


def p_adic_log_one_unit(u: int, p: int, precision: int) -> int:
    """Return log_p(u) modulo p**precision.

    The input must satisfy u=1 mod p for odd p and u=1 mod 4 for p=2.
    Terms are evaluated p-adically, so division by the p-free part of n uses
    a modular inverse while the p-power part is cancelled explicitly.
    """
    p = exact_int(p, "p")
    precision = exact_int(precision, "precision")
    modulus = p**precision
    u %= modulus
    t = (u - 1) % modulus
    if t == 0:
        return 0
    v = vp_int(t, p)
    if p == 2 and v < 2:
        raise ValueError("2-adic logarithm requires a principal unit in 1+4Z_2")
    if p > 2 and v < 1:
        raise ValueError("p-adic logarithm requires a principal unit")
    t0 = t // (p**v)
    total = 0
    n = 1
    while True:
        p_part = vp_int(n, p)
        term_valuation = n * v - p_part
        if term_valuation >= precision:
            # n*v-v_p(n) is eventually strictly increasing.  Ten consecutive
            # omitted terms are more than enough at the small precisions here.
            if all(m * v - vp_int(m, p) >= precision for m in range(n, n + 10)):
                break
        if term_valuation < precision:
            free_part = n // (p**p_part)
            reduced_modulus = p ** (precision - term_valuation)
            coefficient = (
                pow(t0, n, reduced_modulus)
                * pow(free_part, -1, reduced_modulus)
            ) % reduced_modulus
            term = (p**term_valuation) * coefficient
            total = (total + term if n % 2 else total - term) % modulus
        n += 1
        if n > 100000:
            raise RuntimeError("p-adic logarithm series did not terminate")
    return total % modulus


def odd_log_coordinate(q: int, p: int, e: int) -> int:
    """p^{-1} log_p(<q>) modulo p^(e-1), for odd p."""
    q = exact_int(q, "q")
    p = exact_int(p, "p")
    e = exact_int(e, "e")
    if p == 2 or q % p == 0:
        raise ValueError("odd_log_coordinate requires odd p not dividing q")
    if e <= 1:
        return 0
    modulus = p**e
    powered = pow(q, p - 1, modulus)
    raw = p_adic_log_one_unit(powered, p, e)
    principal_log = (raw * pow(p - 1, -1, modulus)) % modulus
    if principal_log % p:
        raise ArithmeticError("principal logarithm lost p-divisibility")
    return (principal_log // p) % (p ** (e - 1))


def dyadic_coordinates(q: int, e: int) -> tuple[int, int]:
    """Return sign and 4^{-1}log_2 principal coordinate for odd q."""
    q = exact_int(q, "q")
    e = exact_int(e, "e")
    if q % 2 == 0:
        raise ValueError("dyadic input generator must be odd")
    sign = 0 if q % 4 == 1 else 1
    if e <= 2:
        return sign, 0
    modulus = 2**e
    principal = (q if sign == 0 else -q) % modulus
    raw = p_adic_log_one_unit(principal, 2, e)
    if raw % 4:
        raise ArithmeticError("principal 2-adic logarithm lost 4-divisibility")
    return sign, (raw // 4) % (2 ** (e - 2))


def signed_input_exponents(a: int, b: int) -> tuple[list[int], list[int]]:
    fa = factorint(exact_int(a, "a"))
    fb = factorint(exact_int(b, "b"))
    primes = sorted(int(q) for q in set(fa) | set(fb))
    values = [int(fb.get(q, 0) - fa.get(q, 0)) for q in primes]
    return primes, values


def balanced_kummer_kernel(a: int, b: int, M: int) -> tuple[int, int]:
    """Return exact order and kernel of [-b/a] in Q*/Q*^M."""
    _, exponents = signed_input_exponents(a, b)
    g_val = reduce(math.gcd, [M, *[abs(v) for v in exponents]])
    valuation_order = M // max(g_val, 1)
    if M % 2 == 0 and valuation_order % 2 == 1:
        order = 2 * valuation_order
    else:
        order = valuation_order
    return order, M // order


@dataclass(frozen=True)
class LocalChannel:
    p: int
    exponent: int
    contact_depth: int
    sign_depth: int
    kummer_depth: int
    wieferich_depth: int
    coherence_depth: int
    local_modulus: int
    row_coefficients: tuple[int, ...]
    normalized_coefficients: tuple[int, ...]
    relation_residual: int


@dataclass(frozen=True)
class TripleAnalysis:
    a: int
    b: int
    c: int
    radical: int
    quality: float
    source: str
    input_primes: tuple[int, ...]
    signed_exponents: tuple[int, ...]
    primitive_exponents: tuple[int, ...]
    powerful_part: int
    dyadic_sign_factor: int
    kummer_factor: int
    wieferich_factor: int
    coherence_factor: int
    principal_contact_order: int
    log_image_order: int
    coherence_rank: int
    exponent_height: int
    random_lattice_scale: float
    relation_compression: float
    local_channels: tuple[LocalChannel, ...]


def analyze_triple(a: int, b: int, c: int, source: str = "") -> TripleAnalysis:
    a = exact_int(a, "a")
    b = exact_int(b, "b")
    c = exact_int(c, "c")
    if a <= 0 or b <= 0 or a + b != c or math.gcd(a, b) != 1:
        raise ValueError("expected a positive primitive triple a+b=c")

    fa = {int(p): int(e) for p, e in factorint(a).items()}
    fb = {int(p): int(e) for p, e in factorint(b).items()}
    fc = {int(p): int(e) for p, e in factorint(c).items()}
    primes, nu = signed_input_exponents(a, b)
    radical = radical_from_factors({**fa, **fb, **fc})
    quality = math.log(c) / math.log(radical)

    M = 1
    for p, e in fc.items():
        M *= p ** max(e - 1, 0)

    _, kummer_kernel = balanced_kummer_kernel(a, b, M)
    if any(v % kummer_kernel for v in nu):
        raise ArithmeticError("balanced Kummer kernel did not divide exponent vector")
    nu0 = [v // max(kummer_kernel, 1) for v in nu]

    sign_factor = 1
    W = 1
    C = 1
    channels: list[LocalChannel] = []

    for p, e in sorted(fc.items()):
        if e <= 1:
            continue
        if p == 2:
            sign_depth = 1
            sign_factor *= 2
            if e == 2:
                channels.append(
                    LocalChannel(
                        p=2,
                        exponent=e,
                        contact_depth=1,
                        sign_depth=1,
                        kummer_depth=0,
                        wieferich_depth=0,
                        coherence_depth=0,
                        local_modulus=1,
                        row_coefficients=tuple(0 for _ in primes),
                        normalized_coefficients=tuple(0 for _ in primes),
                        relation_residual=0,
                    )
                )
                continue
            local_depth = e - 2
            raw = [dyadic_coordinates(q, e)[1] for q in primes]
            # The finite principal contact channel has depth e-2.  Remove the
            # Kummer depth first, then measure the residual logarithmic image
            # defect.  This sequential normalization prevents double-counting
            # if both depths are large in a hypothetical edge case.
            r = min(local_depth, vp_int(kummer_kernel, 2))
            raw_d = min(min(local_depth, vp_int(value, 2)) for value in raw)
            d = min(local_depth - r, raw_d)
            chi = local_depth - r - d
            if chi < 0:
                raise ArithmeticError("negative dyadic coherence depth")
            W *= 2**d
            C *= 2**chi
            modulus = 2**chi if chi else 1
            if chi:
                unit = (kummer_kernel // (2**r)) % modulus
                normalized = tuple(
                    (unit * ((value // (2**d)) % modulus)) % modulus
                    for value in raw
                )
                residual = sum(x * y for x, y in zip(nu0, normalized)) % modulus
            else:
                normalized = tuple(0 for _ in raw)
                residual = 0
            channels.append(
                LocalChannel(
                    p=p,
                    exponent=e,
                    contact_depth=e - 1,
                    sign_depth=sign_depth,
                    kummer_depth=r,
                    wieferich_depth=d,
                    coherence_depth=chi,
                    local_modulus=modulus,
                    row_coefficients=tuple(raw),
                    normalized_coefficients=normalized,
                    relation_residual=residual,
                )
            )
        else:
            sign_depth = 0
            local_depth = e - 1
            raw = [odd_log_coordinate(q, p, e) for q in primes]
            r = min(local_depth, vp_int(kummer_kernel, p))
            raw_d = min(min(local_depth, vp_int(value, p)) for value in raw)
            d = min(local_depth - r, raw_d)
            chi = local_depth - r - d
            if chi < 0:
                raise ArithmeticError("negative odd coherence depth")
            W *= p**d
            C *= p**chi
            modulus = p**chi if chi else 1
            if chi:
                unit = (kummer_kernel // (p**r)) % modulus
                normalized = tuple(
                    (unit * ((value // (p**d)) % modulus)) % modulus
                    for value in raw
                )
                residual = sum(x * y for x, y in zip(nu0, normalized)) % modulus
            else:
                normalized = tuple(0 for _ in raw)
                residual = 0
            channels.append(
                LocalChannel(
                    p=p,
                    exponent=e,
                    contact_depth=e - 1,
                    sign_depth=0,
                    kummer_depth=r,
                    wieferich_depth=d,
                    coherence_depth=chi,
                    local_modulus=modulus,
                    row_coefficients=tuple(raw),
                    normalized_coefficients=normalized,
                    relation_residual=residual,
                )
            )

    if sign_factor * kummer_kernel * W * C != M:
        raise ArithmeticError(
            f"factorization failed: {sign_factor}*{kummer_kernel}*{W}*{C}!={M}"
        )
    if any(channel.relation_residual for channel in channels):
        raise ArithmeticError("normalized exponent packet missed a coherence channel")

    principal_contact = M // sign_factor
    log_image_order = principal_contact // W
    rank = len(primes)
    height = max(abs(v) for v in nu0) if nu0 else 0
    random_scale = C ** (1.0 / rank) if C > 0 and rank else 1.0
    compression = height / random_scale if random_scale else 0.0

    return TripleAnalysis(
        a=a,
        b=b,
        c=c,
        radical=radical,
        quality=quality,
        source=source,
        input_primes=tuple(primes),
        signed_exponents=tuple(nu),
        primitive_exponents=tuple(nu0),
        powerful_part=M,
        dyadic_sign_factor=sign_factor,
        kummer_factor=kummer_kernel,
        wieferich_factor=W,
        coherence_factor=C,
        principal_contact_order=principal_contact,
        log_image_order=log_image_order,
        coherence_rank=rank,
        exponent_height=height,
        random_lattice_scale=random_scale,
        relation_compression=compression,
        local_channels=tuple(channels),
    )


def crt_coherence_row(record: TripleAnalysis) -> tuple[int, tuple[int, ...]]:
    moduli = [ch.local_modulus for ch in record.local_channels if ch.local_modulus > 1]
    rows = [ch.normalized_coefficients for ch in record.local_channels if ch.local_modulus > 1]
    if not moduli:
        return 1, tuple(0 for _ in record.input_primes)
    coefficients: list[int] = []
    for column in range(len(record.input_primes)):
        value, modulus = crt(moduli, [row[column] for row in rows], check=True)
        if value is None:
            raise ArithmeticError("CRT coherence row failed")
        coefficients.append(int(value % modulus))
    C = math.prod(moduli)
    if C != record.coherence_factor:
        raise ArithmeticError("CRT modulus disagrees with coherence factor")
    residual = sum(x * y for x, y in zip(record.primitive_exponents, coefficients)) % C
    if residual:
        raise ArithmeticError("CRT row does not annihilate primitive exponent vector")
    if math.gcd(C, *coefficients) != 1:
        raise ArithmeticError("CRT row is not primitive")
    return C, tuple(coefficients)


def arbitrary_index_annihilator(vector: Iterable[int], modulus: int) -> tuple[int, ...]:
    """Construct a primitive row mod modulus annihilating a primitive vector.

    This witnesses the no-go theorem that a short primitive relation and a
    cyclic quotient place no upper bound on the quotient order.
    """
    v = [exact_int(x) for x in vector]
    modulus = exact_int(modulus)
    if len(v) < 2 or reduce(math.gcd, [abs(x) for x in v]) != 1:
        raise ValueError("vector must be primitive of rank at least two")
    # Find a pair after a unimodular-style Bezout reduction.  A simple exact
    # construction is obtained from a Bezout vector u with u.v=1 and any
    # coordinate vector e_j not proportional to v.  The row e_j-u_j v^* is
    # cumbersome to express directly, so solve one modular equation with a
    # coefficient guaranteed to be invertible after a unimodular combination.
    # We use sympy's gcdex implicitly through iterative Bezout coefficients.
    coeff = [0] * len(v)
    g = 0
    bez = []
    for x in v:
        old_g = g
        g = math.gcd(g, abs(x))
        bez.append((old_g, x, g))
    # Build an integral Bezout vector by a forward extended-gcd recursion.
    u = [0] * len(v)
    current_g = 0
    for i, x in enumerate(v):
        if current_g == 0:
            current_g = abs(x)
            u[i] = 1 if x >= 0 else -1
            continue
        gg, s, t = extended_gcd(current_g, x)
        u = [s * item for item in u]
        u[i] = t
        current_g = abs(gg)
    if sum(ui * vi for ui, vi in zip(u, v)) not in {1, -1}:
        raise ArithmeticError("Bezout construction failed")
    if sum(ui * vi for ui, vi in zip(u, v)) == -1:
        u = [-x for x in u]
    # Pick j and set row = e_j - v_j*u.  Then row.v = v_j-v_j=0.
    j = next(i for i, x in enumerate(v) if x != 0)
    coeff = [-v[j] * ui for ui in u]
    coeff[j] += 1
    coeff = [x % modulus for x in coeff]
    if sum(x * y for x, y in zip(coeff, v)) % modulus:
        raise ArithmeticError("annihilator construction failed")
    # If the row is zero, use another coordinate.  A primitive vector of rank
    # at least two always has a nonzero integral annihilator.
    if all(x % modulus == 0 for x in coeff):
        for j in range(len(v)):
            trial = [-v[j] * ui for ui in u]
            trial[j] += 1
            trial = [x % modulus for x in trial]
            if any(trial) and sum(x * y for x, y in zip(trial, v)) % modulus == 0:
                coeff = trial
                break
    # Divide a common unit-free gcd only if it is also coprime to modulus.
    if math.gcd(modulus, *coeff) != 1:
        # Search a small integer annihilator basis v_j e_i-v_i e_j.
        found = None
        for i in range(len(v)):
            for j in range(i + 1, len(v)):
                trial = [0] * len(v)
                trial[i] = v[j]
                trial[j] = -v[i]
                trial = [x % modulus for x in trial]
                if math.gcd(modulus, *trial) == 1:
                    found = trial
                    break
            if found is not None:
                break
        if found is None:
            # Apply a unimodular shear by adding a multiple of an annihilator.
            # Exhaustive small search is deterministic and only used in tests.
            for bound in range(1, 20):
                for trial in integer_vectors(len(v), bound):
                    if sum(x * y for x, y in zip(trial, v)) == 0 and math.gcd(modulus, *trial) == 1:
                        found = [x % modulus for x in trial]
                        break
                if found is not None:
                    break
        if found is None:
            raise ArithmeticError("could not construct primitive annihilator")
        coeff = found
    return tuple(coeff)


def extended_gcd(a: int, b: int) -> tuple[int, int, int]:
    if b == 0:
        return (a, 1, 0)
    g, x1, y1 = extended_gcd(b, a % b)
    return (g, y1, x1 - (a // b) * y1)


def integer_vectors(dimension: int, bound: int):
    if dimension == 0:
        yield ()
        return
    import itertools
    for vector in itertools.product(range(-bound, bound + 1), repeat=dimension):
        if any(vector):
            yield vector


def signed_contact_height_lower_bound(A: int, B: int, c: int) -> bool:
    A = exact_int(A)
    B = exact_int(B)
    c = exact_int(c)
    if A <= 0 or B <= 0 or (A + B) % c:
        raise ValueError("expected positive A,B with c dividing A+B")
    return max(A, B) * 2 >= c


def save_figure(fig: plt.Figure, directory: Path, stem: str) -> None:
    directory.mkdir(parents=True, exist_ok=True)
    fig.savefig(directory / f"{stem}.pdf", bbox_inches="tight")
    fig.savefig(directory / f"{stem}.png", dpi=240, bbox_inches="tight")
    plt.close(fig)


def diagram_axes(figsize=(13.0, 6.5)):
    fig, ax = plt.subplots(figsize=figsize)
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis("off")
    return fig, ax


def box(ax, xy, width, height, text, face, edge, fontsize=11):
    patch = FancyBboxPatch(
        xy,
        width,
        height,
        boxstyle="round,pad=.012,rounding_size=.018",
        facecolor=face,
        edgecolor=edge,
        linewidth=1.8,
    )
    ax.add_patch(patch)
    ax.text(xy[0] + width / 2, xy[1] + height / 2, text, ha="center", va="center", fontsize=fontsize)
    return patch


def arrow(ax, start, end, color=INK, lw=1.8):
    ax.add_patch(FancyArrowPatch(start, end, arrowstyle="-|>", mutation_scale=13, color=color, linewidth=lw))


def generate_figures(records: list[TripleAnalysis], base: Path) -> None:
    out = base / "figures"
    frame = pd.DataFrame([record_to_row(r) for r in records])

    # 1. Architecture.
    fig, ax = diagram_axes((13.0, 6.4))
    ax.text(0.5, 0.95, "The exact contact-depth filtration", ha="center", fontsize=22, weight="bold")
    box(ax, (0.03, 0.58), 0.18, 0.18, "principal contact\npacket $J_c$\norder $M/\\epsilon_2$", PALE_BLUE, BLUE, 13)
    box(ax, (0.28, 0.58), 0.18, 0.18, "input logarithm\nimage $G_{\\log}$\nindex $W$", PALE_TEAL, TEAL, 13)
    box(ax, (0.53, 0.58), 0.18, 0.18, "Kummer orbit\n$H_\\beta$\norder $K$", PALE_ORANGE, ORANGE, 13)
    box(ax, (0.78, 0.58), 0.18, 0.18, "coherence quotient\n$G_{\\log}/H_\\beta$\norder $C$", PALE_MAGENTA, MAGENTA, 13)
    arrow(ax, (0.21, 0.67), (0.28, 0.67), BLUE)
    arrow(ax, (0.46, 0.67), (0.53, 0.67), TEAL)
    arrow(ax, (0.71, 0.67), (0.78, 0.67), ORANGE)
    ax.text(0.5, 0.39, r"$M=\epsilon_2\,K\,W\,C$", ha="center", fontsize=24, color=BLUE, weight="bold")
    ax.text(0.5, 0.27, "known dyadic sign  |  global power preload  |  local Wieferich defect  |  genuine cross-channel cancellation", ha="center", fontsize=11.5, color=MUTED)
    ax.text(0.5, 0.10, "The final lattice is the kernel of the cyclic coherence character after the first three layers are removed.", ha="center", fontsize=12.5)
    save_figure(fig, out, "01_contact_filtration")

    # 2. Local depth decomposition for selected high quality examples.
    selected = sorted(records, key=lambda r: r.quality, reverse=True)[:12]
    labels = [str(r.c) for r in selected]
    components = []
    for r in selected:
        total = math.log(max(r.powerful_part, 1))
        if total == 0:
            components.append((0, 0, 0, 0))
        else:
            components.append((
                math.log(r.dyadic_sign_factor) / total,
                math.log(r.kummer_factor) / total,
                math.log(r.wieferich_factor) / total,
                math.log(r.coherence_factor) / total,
            ))
    arr = np.array(components)
    fig, ax = plt.subplots(figsize=(13.0, 6.0))
    bottom = np.zeros(len(selected))
    names = ["dyadic sign", "Kummer", "Wieferich", "coherence"]
    colors = [BLUE, ORANGE, RED, TEAL]
    for index, (name, color) in enumerate(zip(names, colors)):
        ax.bar(np.arange(len(selected)), arr[:, index], bottom=bottom, label=name, color=color)
        bottom += arr[:, index]
    ax.set_xticks(np.arange(len(selected)), labels, rotation=38, ha="right")
    ax.set_ylabel("share of $\\log(c/\\operatorname{rad}(c))$")
    ax.set_title("Where the powerful part lives in the highest-quality corpus rows", weight="bold", fontsize=17)
    ax.legend(ncol=4, loc="upper center", bbox_to_anchor=(0.5, -0.19), frameon=False)
    ax.grid(axis="y", alpha=0.18)
    fig.tight_layout(rect=[0, 0.09, 1, 1])
    save_figure(fig, out, "02_factor_shares")

    # 3. Corpus factor frequency.
    counts = [
        sum(r.kummer_factor == 1 for r in records),
        sum(r.wieferich_factor == 1 for r in records),
        sum(r.coherence_factor == 1 for r in records),
    ]
    fig, ax = plt.subplots(figsize=(10.5, 5.3))
    bars = ax.bar(["$K=1$", "$W=1$", "$C=1$"], counts, color=[ORANGE, RED, TEAL])
    ax.set_ylim(0, len(records) * 1.08)
    ax.set_ylabel("triple count")
    ax.set_title("The coherence packet is the persistent layer", weight="bold", fontsize=18)
    for bar, count in zip(bars, counts):
        ax.text(bar.get_x() + bar.get_width()/2, count + 5, f"{count}/{len(records)}", ha="center", fontsize=12, weight="bold")
    ax.grid(axis="y", alpha=0.17)
    fig.tight_layout()
    save_figure(fig, out, "03_factor_frequency")

    # 4. Exact Wieferich defects.
    defect_records = [r for r in records if r.wieferich_factor > 1]
    fig, ax = plt.subplots(figsize=(12.0, 5.8))
    if defect_records:
        defect_records = sorted(defect_records, key=lambda r: r.wieferich_factor, reverse=True)
        ax.bar(np.arange(len(defect_records)), [math.log10(r.wieferich_factor) for r in defect_records], color=RED)
        ax.set_xticks(np.arange(len(defect_records)), [str(r.c) for r in defect_records], rotation=42, ha="right")
    ax.set_ylabel(r"$\log_{10} W$")
    ax.set_title("The generalized Wieferich defect is rare but can be deep", weight="bold", fontsize=17)
    ax.grid(axis="y", alpha=0.18)
    fig.tight_layout()
    save_figure(fig, out, "04_wieferich_defects")

    # 5. Coherence vs quality.
    fig, ax = plt.subplots(figsize=(10.5, 6.2))
    x = [math.log(r.coherence_factor) / math.log(r.radical) if r.coherence_factor > 1 else 0 for r in records]
    y = [r.quality for r in records]
    sizes = [24 + 13 * r.coherence_rank for r in records]
    ax.scatter(x, y, s=sizes, alpha=0.72, color=TEAL, edgecolor=INK, linewidth=0.35)
    ax.set_xlabel(r"coherence load $\log C/\log R$")
    ax.set_ylabel(r"$abc$ quality $\log c/\log R$")
    ax.set_title("High quality is carried mainly by coherent logarithmic cancellation", weight="bold", fontsize=16)
    ax.grid(alpha=0.17)
    fig.tight_layout()
    save_figure(fig, out, "05_coherence_vs_quality")

    # 6. Relation compression relative to a random congruence lattice.
    fig, ax = plt.subplots(figsize=(10.8, 6.2))
    x = [max(r.random_lattice_scale, 1e-12) for r in records]
    y = [max(r.exponent_height, 1e-12) for r in records]
    ax.loglog(x, y, "o", alpha=0.68, color=MAGENTA, markeredgecolor=INK, markeredgewidth=0.3)
    lo = min(min(x), min(y)); hi = max(max(x), max(y))
    ax.plot([lo, hi], [lo, hi], linestyle="--", color=MUTED, label=r"$H=C^{1/s}$")
    ax.set_xlabel(r"random-lattice scale $C^{1/s}$")
    ax.set_ylabel(r"observed primitive exponent height $\|\nu_0\|_\infty$")
    ax.set_title("The additive relation is far shorter than a random modular relation", weight="bold", fontsize=16)
    ax.legend()
    ax.grid(alpha=0.17, which="both")
    fig.tight_layout()
    save_figure(fig, out, "06_relation_compression")

    # 7. Nested prime-power coherence filtration.
    example = analyze_triple(3, 125, 128, "worked")
    fig, ax = diagram_axes((13.0, 6.3))
    ax.text(0.5, 0.95, "Dyadic coherence filtration for $3+125=128$", ha="center", fontsize=21, weight="bold")
    levels = 5
    for j in range(levels + 1):
        x0 = 0.08 + j * 0.15
        width = 0.13
        box(ax, (x0, 0.55), width, 0.15, rf"$\Lambda_{{2,{j}}}$\nmod $2^{j}$", PALE_BLUE if j < levels else PALE_TEAL, BLUE if j < levels else TEAL, 11)
        if j < levels:
            arrow(ax, (x0 + width, 0.625), (x0 + 0.15, 0.625), BLUE, 1.4)
            ax.text(x0 + width + 0.012, 0.67, r"index $2$", fontsize=9, color=MUTED)
    ax.text(0.5, 0.37, r"normalized row: $29x_3+31x_5\equiv0\; (\mathrm{mod}\;32)$", ha="center", fontsize=16)
    ax.text(0.5, 0.27, r"primitive exponent packet: $\nu_0=(-1,3)$", ha="center", fontsize=15, color=MAGENTA)
    ax.text(0.5, 0.12, "The same packet survives five consecutive dyadic phase tests.  Their product is the coherence factor $C=32$.", ha="center", fontsize=11.7)
    save_figure(fig, out, "07_nested_coherence_filtration")

    # 8. Lattice example mod 32.
    fig, ax = plt.subplots(figsize=(8.6, 7.0))
    points_x=[]; points_y=[]
    for x0 in range(-16,17):
        for y0 in range(-16,17):
            if (29*x0 + 31*y0) % 32 == 0:
                points_x.append(x0); points_y.append(y0)
    ax.scatter(points_x, points_y, s=20, color=GRID, edgecolor=INK, linewidth=0.25)
    ax.scatter([-1], [3], s=130, color=MAGENTA, edgecolor=INK, linewidth=1.0, zorder=5, label=r"$\nu_0=(-1,3)$")
    ax.axhline(0, color=INK, lw=0.7); ax.axvline(0, color=INK, lw=0.7)
    ax.set_xlabel(r"exponent coordinate at $3$")
    ax.set_ylabel(r"exponent coordinate at $5$")
    ax.set_title(r"The coherence lattice $29x+31y\equiv0\; (\mathrm{mod}\;32)$", weight="bold", fontsize=16)
    ax.legend()
    ax.grid(alpha=0.12)
    ax.set_aspect("equal")
    fig.tight_layout()
    save_figure(fig, out, "08_worked_coherence_lattice")

    # 9. Giant high-quality local rows.
    giant = max(records, key=lambda r: r.powerful_part)
    fig, ax = diagram_axes((13.0, 6.6))
    ax.text(0.5, 0.95, f"Coherence rows for c={giant.c}", ha="center", fontsize=19, weight="bold")
    y = 0.78
    for channel in giant.local_channels:
        if channel.coherence_depth == 0:
            continue
        coeffs = list(channel.normalized_coefficients)
        chunks = [coeffs[i:i+3] for i in range(0, len(coeffs), 3)]
        row_text = "row: " + "\n     ".join(str(chunk) for chunk in chunks)
        text = (
            rf"$p={channel.p}$, $\chi_p={channel.coherence_depth}$, modulus $p^{{\chi_p}}={channel.local_modulus}$" + "\n" +
            row_text
        )
        box(ax, (0.08, y-0.09), 0.84, 0.15, text, PALE_TEAL, TEAL, 9.3)
        y -= 0.20
    ax.text(0.5, 0.13, "Every row is primitive and annihilates the same exponent packet.  Their CRT product has order equal to the full coherence factor.", ha="center", fontsize=11.5)
    save_figure(fig, out, "09_high_quality_rows")

    # 10. Pure lattice no-go.
    fig, ax = diagram_axes((13.0, 6.3))
    ax.text(0.5, 0.94, "Why lattice geometry alone cannot bound the coherence modulus", ha="center", fontsize=20, weight="bold")
    box(ax, (0.05, 0.59), 0.22, 0.18, "any primitive\nshort vector $v$", PALE_BLUE, BLUE, 14)
    box(ax, (0.39, 0.59), 0.22, 0.18, "any prescribed\nmodulus $C$", PALE_ORANGE, ORANGE, 14)
    box(ax, (0.73, 0.59), 0.22, 0.18, r"a primitive row $g$" + "\n" + r"with $g\cdot v=0\; (\mathrm{mod}\;C)$", PALE_MAGENTA, MAGENTA, 13)
    arrow(ax, (0.27,0.68),(0.39,0.68),INK)
    arrow(ax, (0.61,0.68),(0.73,0.68),INK)
    ax.text(0.5, 0.38, r"$\ker(g:\mathbb{Z}^s\to\mathbb{Z}/C)$ contains $v$ and has index $C$.", ha="center", fontsize=17)
    ax.text(0.5, 0.20, "A short relation plus a large cyclic quotient is possible at every scale.  The proof must use that the row entries are p-adic logarithms of actual input primes.", ha="center", fontsize=11.8, color=MUTED)
    save_figure(fig, out, "10_abstract_lattice_nogo")

    # 11. Dual coherence character.
    fig, ax = diagram_axes((13.0, 6.4))
    ax.text(0.5, 0.95, "Dual form of the coherence lattice", ha="center", fontsize=21, weight="bold")
    box(ax, (0.04,0.58),0.20,0.18,"input exponent\n" + r"signal $\mathbb{Z}^{S_{ab}}$",PALE_BLUE,BLUE,13)
    box(ax, (0.31,0.58),0.20,0.18,"p-adic log\nfilter rows",PALE_TEAL,TEAL,13)
    box(ax, (0.58,0.58),0.17,0.18,"cyclic phase\n" + r"packet $\mathbb{Z}/C$",PALE_ORANGE,ORANGE,13)
    box(ax, (0.82,0.58),0.14,0.18,"dual ray\ncharacter",PALE_MAGENTA,MAGENTA,12)
    arrow(ax,(0.24,0.67),(0.31,0.67),BLUE)
    arrow(ax,(0.51,0.67),(0.58,0.67),TEAL)
    arrow(ax,(0.75,0.67),(0.82,0.67),ORANGE)
    ax.text(0.5,0.37,r"$\nu_0$ lies in the zero phase of every local filter.",ha="center",fontsize=16)
    ax.text(0.5,0.24,"The quotient is one sparse character channel.  Its conductor and Jacobi or regulator realizations are the next place where a nontrivial global bound could appear.",ha="center",fontsize=11.5,color=MUTED)
    save_figure(fig,out,"11_dual_character_packet")

    # 12. Final target.
    fig, ax = diagram_axes((13.0, 6.5))
    ax.text(0.5,0.95,"The corrected finishing target",ha="center",fontsize=22,weight="bold")
    box(ax,(0.05,0.59),0.20,0.18,"known\n" + r"$K\leq\log c$" + "\n" + r"$\epsilon_2\leq2$",PALE_BLUE,BLUE,13)
    box(ax,(0.31,0.59),0.20,0.18,"local defect\n$W$\nWieferich depth",PALE_ORANGE,ORANGE,13)
    box(ax,(0.57,0.59),0.20,0.18,"global lattice\n$C$\ncoherence depth",PALE_TEAL,TEAL,13)
    box(ax,(0.83,0.59),0.13,0.18,"$abc$\nbound",PALE_MAGENTA,MAGENTA,14)
    arrow(ax,(0.25,0.68),(0.31,0.68),INK)
    arrow(ax,(0.51,0.68),(0.57,0.68),INK)
    arrow(ax,(0.77,0.68),(0.83,0.68),INK)
    ax.text(0.5,0.39,r"$M=\epsilon_2KWC$",ha="center",fontsize=23,color=BLUE,weight="bold")
    ax.text(0.5,0.27,r"Strong $abc$ is equivalent, up to the absorbable logarithmic factor $K$, to $WC\leq R_aR_bR^\varepsilon$.",ha="center",fontsize=13)
    ax.text(0.5,0.12,"The remaining proof must control the arithmetic origin of the logarithm rows.  Abstract lattice reduction cannot do it.",ha="center",fontsize=11.8,color=MUTED)
    save_figure(fig,out,"12_final_target")


def record_to_row(record: TripleAnalysis) -> dict[str, object]:
    return {
        "a": record.a,
        "b": record.b,
        "c": record.c,
        "radical": record.radical,
        "quality": record.quality,
        "source": record.source,
        "input_rank": record.coherence_rank,
        "input_primes": " ".join(map(str, record.input_primes)),
        "signed_exponents": " ".join(map(str, record.signed_exponents)),
        "primitive_exponents": " ".join(map(str, record.primitive_exponents)),
        "powerful_part_M": record.powerful_part,
        "dyadic_sign_factor": record.dyadic_sign_factor,
        "kummer_factor_K": record.kummer_factor,
        "wieferich_factor_W": record.wieferich_factor,
        "coherence_factor_C": record.coherence_factor,
        "principal_contact_order": record.principal_contact_order,
        "log_image_order": record.log_image_order,
        "exponent_height": record.exponent_height,
        "random_lattice_scale": record.random_lattice_scale,
        "relation_compression": record.relation_compression,
        "local_channels": "; ".join(
            f"p={ch.p}:e={ch.exponent}:r={ch.kummer_depth}:d={ch.wieferich_depth}:chi={ch.coherence_depth}"
            for ch in record.local_channels
        ),
    }


def write_outputs(records: list[TripleAnalysis], base: Path) -> dict[str, object]:
    base.mkdir(parents=True, exist_ok=True)
    table_dir = base / "tables"
    result_dir = base / "results"
    table_dir.mkdir(exist_ok=True)
    result_dir.mkdir(exist_ok=True)
    rows = [record_to_row(r) for r in records]
    pd.DataFrame(rows).to_csv(table_dir / "coherence_corpus.csv", index=False)

    defect_rows = [row for row in rows if int(row["wieferich_factor_W"]) > 1]
    pd.DataFrame(defect_rows).to_csv(table_dir / "wieferich_defects.csv", index=False)

    selected = sorted(records, key=lambda r: r.quality, reverse=True)[:20]
    selected_rows=[]
    for r in selected:
        C, coeff = crt_coherence_row(r)
        selected_rows.append({
            **record_to_row(r),
            "crt_coherence_modulus": C,
            "crt_coherence_row": " ".join(map(str, coeff)),
        })
    pd.DataFrame(selected_rows).to_csv(table_dir / "top_quality_coherence_rows.csv", index=False)

    summary = {
        "corpus_rows": len(records),
        "factorization_checks": sum(
            r.dyadic_sign_factor * r.kummer_factor * r.wieferich_factor * r.coherence_factor == r.powerful_part
            for r in records
        ),
        "kummer_factor_one": sum(r.kummer_factor == 1 for r in records),
        "wieferich_factor_one": sum(r.wieferich_factor == 1 for r in records),
        "coherence_factor_one": sum(r.coherence_factor == 1 for r in records),
        "largest_wieferich_factor": max(r.wieferich_factor for r in records),
        "largest_coherence_factor": max(r.coherence_factor for r in records),
        "median_relation_compression": float(np.median([r.relation_compression for r in records])),
        "minimum_relation_compression": min(r.relation_compression for r in records),
        "quality_coherence_correlation": float(np.corrcoef(
            [r.quality for r in records],
            [math.log(r.coherence_factor) for r in records],
        )[0, 1]),
        "worked_example": {
            "triple": [3, 125, 128],
            "factorization": {"epsilon_2": 2, "K": 1, "W": 1, "C": 32},
            "coherence_row_mod_32": [29, 31],
            "primitive_exponent_packet": [-1, 3],
        },
    }
    (result_dir / "summary.json").write_text(json.dumps(summary, indent=2) + "\n")
    return summary


def load_records(csv_path: Path) -> list[TripleAnalysis]:
    frame = pd.read_csv(csv_path, dtype=str)
    records=[]
    for row in frame.itertuples(index=False):
        records.append(analyze_triple(int(row.a), int(row.b), int(row.c), str(row.source)))
    return records


def sha256(path: Path) -> str:
    h=hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1<<20), b""):
            h.update(block)
    return h.hexdigest()


def main() -> None:
    parser=argparse.ArgumentParser()
    parser.add_argument("--base", type=Path, default=Path(__file__).resolve().parent)
    parser.add_argument("--corpus", type=Path)
    args=parser.parse_args()
    base=args.base.resolve()
    corpus=(args.corpus or (base/"input_corpus.csv")).resolve()
    records=load_records(corpus)
    summary=write_outputs(records,base)
    generate_figures(records,base)
    print(json.dumps(summary,indent=2))


if __name__ == "__main__":
    main()
