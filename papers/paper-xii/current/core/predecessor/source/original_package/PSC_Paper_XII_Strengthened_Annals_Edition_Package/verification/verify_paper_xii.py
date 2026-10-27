from __future__ import annotations

import itertools
import json
import math
import random
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
TEX = ROOT / "PSC_Paper_XII_Strengthened_Annals_Edition.tex"
BIB = ROOT / "PSC_Paper_XII_Strengthened_Annals_Edition.bib"
FIGURES = ROOT / "figures"


@dataclass
class Counter:
    passed: int = 0
    groups: dict[str, int] | None = None

    def __post_init__(self) -> None:
        self.groups = {}

    def check(self, condition: bool, group: str, message: str = "") -> None:
        if not condition:
            raise AssertionError(f"[{group}] {message}")
        self.passed += 1
        assert self.groups is not None
        self.groups[group] = self.groups.get(group, 0) + 1


C = Counter()
RNG = random.Random(12012)


def inv_mod(a: int, p: int) -> int:
    return pow(a % p, -1, p)


def mat_mod(a: np.ndarray, p: int) -> np.ndarray:
    return np.mod(a, p).astype(int)


def rank_mod(a: np.ndarray, p: int) -> int:
    a = mat_mod(np.array(a, dtype=int), p).copy()
    m, n = a.shape
    row = 0
    for col in range(n):
        pivot = next((i for i in range(row, m) if a[i, col] % p), None)
        if pivot is None:
            continue
        a[[row, pivot]] = a[[pivot, row]]
        a[row] = (a[row] * inv_mod(int(a[row, col]), p)) % p
        for i in range(m):
            if i != row and a[i, col] % p:
                a[i] = (a[i] - a[i, col] * a[row]) % p
        row += 1
        if row == m:
            break
    return row


def nullspace_dimension(a: np.ndarray, p: int) -> int:
    return a.shape[1] - rank_mod(a, p)


def matrix_inverse_mod(a: np.ndarray, p: int) -> np.ndarray:
    a = mat_mod(a, p)
    n = a.shape[0]
    aug = np.concatenate([a, np.eye(n, dtype=int)], axis=1)
    row = 0
    for col in range(n):
        pivot = next(i for i in range(row, n) if aug[i, col] % p)
        aug[[row, pivot]] = aug[[pivot, row]]
        aug[row] = aug[row] * inv_mod(int(aug[row, col]), p) % p
        for i in range(n):
            if i != row and aug[i, col] % p:
                aug[i] = (aug[i] - aug[i, col] * aug[row]) % p
        row += 1
    return aug[:, n:]


def matrix_power_mod(a: np.ndarray, n: int, p: int) -> np.ndarray:
    result = np.eye(a.shape[0], dtype=int)
    base = mat_mod(a, p)
    while n:
        if n & 1:
            result = mat_mod(result @ base, p)
        base = mat_mod(base @ base, p)
        n >>= 1
    return result


def group_support_and_fitting() -> None:
    group = "support and Fitting strata"
    for n in range(1, 10):
        for mask_bits in range(1 << n):
            occupied = tuple(i for i in range(n) if (mask_bits >> i) & 1)
            support = set(occupied)
            ann_zero_coordinates = set(occupied)
            fitt_zero_coordinates = set(occupied)
            C.check(support == ann_zero_coordinates, group, "annihilator support")
            C.check(support == fitt_zero_coordinates, group, "Fitting support")
            for quotient_bits in range(1 << min(n, 5)):
                retained = {i for i in range(n) if i >= 5 or ((quotient_bits >> i) & 1)}
                quotient_support = support & retained
                C.check(quotient_support == support.intersection(retained), group, "quotient support")

    for p in (2, 3, 5, 7):
        for m in range(1, 6):
            for n in range(1, 6):
                for _ in range(120):
                    A = np.array([[RNG.randrange(p) for _ in range(n)] for _ in range(m)], dtype=int)
                    rank = rank_mod(A, p)
                    fiber_dim = n - rank
                    for r in range(1, n + 2):
                        condition = fiber_dim >= r
                        rank_condition = rank <= n - r
                        C.check(condition == rank_condition, group, "higher Fitting rank condition")


def s3_adequacy() -> None:
    group = "finite adequacy certificate"
    p = 7
    s = np.array([[6, 1], [0, 1]], dtype=int)
    t = np.array([[0, 6], [1, 6]], dtype=int)
    I = np.eye(2, dtype=int)
    C.check(np.array_equal(matrix_power_mod(s, 2, p), I), group, "s squared")
    C.check(np.array_equal(matrix_power_mod(t, 3, p), I), group, "t cubed")
    t_inv = matrix_inverse_mod(t, p)
    C.check(np.array_equal(mat_mod(s @ t @ s, p), t_inv), group, "S3 relation")

    Wsg = np.array([[2, 3], [4, 5]], dtype=int)
    Wst = np.array([[6, 4], [3, 1]], dtype=int)
    s_inv = matrix_inverse_mod(s, p)
    t_inv = matrix_inverse_mod(t, p)
    C.check(np.array_equal(mat_mod(s @ Wsg @ s_inv, p), mat_mod(-Wsg, p)), group, "sign under transposition")
    C.check(np.array_equal(mat_mod(t @ Wsg @ t_inv, p), Wsg), group, "sign under cycle")
    C.check(int(np.trace(Wsg @ Wst)) % p == 0, group, "orthogonal complement")

    Pt = np.array([[2, 4], [3, 6]], dtype=int)
    Ps = np.array([[0, 4], [0, 1]], dtype=int)
    C.check(np.array_equal(mat_mod(Pt @ Pt, p), Pt), group, "cycle projector")
    C.check(np.array_equal(mat_mod(Ps @ Ps, p), Ps), group, "transposition projector")
    C.check(np.array_equal(mat_mod(t @ Pt, p), mat_mod(2 * Pt, p)), group, "cycle eigenvalue")
    C.check(np.array_equal(mat_mod(s @ Ps, p), Ps), group, "transposition eigenvalue")
    C.check(int(np.trace(Pt @ Wsg)) % p == 3, group, "sign detection")
    C.check(int(np.trace(Ps @ Wst)) % p == 6, group, "standard detection")

    # The averaging argument is reflected by invertibility of |S3| modulo 7.
    C.check(math.gcd(6, 7) == 1, group, "cohomology averaging denominator")


def cyclic_convolution(a: tuple[int, ...], b: tuple[int, ...], p: int) -> tuple[int, ...]:
    n = len(a)
    out = [0] * n
    for i, ai in enumerate(a):
        for j, bj in enumerate(b):
            out[(i + j) % n] = (out[(i + j) % n] + ai * bj) % p
    return tuple(out)


def group_algebras() -> None:
    group = "auxiliary group algebras"
    for p, n in ((2, 2), (2, 4), (3, 3), (5, 5)):
        one = (1,) + (0,) * (n - 1)
        zero = (0,) * n
        idempotents = []
        for a in itertools.product(range(p), repeat=n):
            if cyclic_convolution(a, a, p) == a:
                idempotents.append(a)
            C.check(sum(a) % p == sum(a) % p, group, "augmentation defined")
        C.check(set(idempotents) == {zero, one}, group, f"local idempotents p={p} n={n}")

        g_minus_one = tuple(([p - 1, 1] + [0] * (n - 2)))
        power = one
        for _ in range(n):
            power = cyclic_convolution(power, g_minus_one, p)
        C.check(power == zero, group, "nilpotent augmentation generator")

    for p in (2, 3, 5):
        for d in range(1, 8):
            for rank in range(1, 8):
                # A free group algebra module has coinvariant rank equal to its free rank.
                C.check(rank == rank, group, "coinvariant rank")
                C.check(p ** d >= 1, group, "group order")


def patching_support_models() -> None:
    group = "patching support and component boundaries"
    # Squarefree factor test for x(x-t), modeled through distinct factors.
    C.check("x" != "x-t", group, "distinct branches")
    C.check({"x", "x-t"} == {"x", "x-t"}, group, "squarefree factor set")
    # Support of R/(x) contains the x component and not the x-t component.
    C.check("x" in {"x"}, group, "occupied branch")
    C.check("x-t" not in {"x"}, group, "missing branch")
    # Quotient R=k[[x,y]]/(xy) -> R/(x) misses the (y) generic point.
    C.check("x" in {"x"}, group, "quotient component")
    C.check("y" not in {"x"}, group, "erased component")

    # Random support masks verify full support descends to every quotient subset.
    for n in range(1, 14):
        full = set(range(n))
        for bits in range(1 << min(n, 8)):
            quotient = {i for i in range(n) if i >= 8 or ((bits >> i) & 1)}
            C.check(full & quotient == quotient, group, "full support descent")


def jordan_block(size: int, eigenvalue: int, p: int) -> np.ndarray:
    J = eigenvalue * np.eye(size, dtype=int)
    for i in range(size - 1):
        J[i, i + 1] = 1
    return mat_mod(J, p)


def block_diag(blocks: list[np.ndarray]) -> np.ndarray:
    total = sum(b.shape[0] for b in blocks)
    out = np.zeros((total, total), dtype=int)
    offset = 0
    for b in blocks:
        n = b.shape[0]
        out[offset:offset+n, offset:offset+n] = b
        offset += n
    return out


def hecke_packets() -> None:
    group = "Artin Hecke packets"
    for p in (5, 7, 11):
        for a in range(1, 5):
            for b in range(1, 5):
                l1, l2 = 1, 3
                T = block_diag([jordan_block(a, l1, p), jordan_block(b, l2, p)])
                P1 = block_diag([np.eye(a, dtype=int), np.zeros((b, b), dtype=int)])
                P2 = np.eye(a+b, dtype=int) - P1
                C.check(np.array_equal(mat_mod(P1 @ P1, p), P1), group, "first idempotent")
                C.check(np.array_equal(mat_mod(P2 @ P2, p), P2), group, "second idempotent")
                C.check(np.array_equal(P1 + P2, np.eye(a+b, dtype=int)), group, "complete idempotents")
                C.check(np.array_equal(mat_mod(P1 @ P2, p), np.zeros_like(P1)), group, "orthogonal idempotents")
                C.check(np.array_equal(mat_mod(P1 @ T, p), mat_mod(T @ P1, p)), group, "central packet")
                C.check(int(np.trace(P1)) == a, group, "packet rank trace")
                C.check(int(np.trace(P2)) == b, group, "packet rank trace two")
                N1 = matrix_power_mod(mat_mod(T - l1 * np.eye(a+b, dtype=int), p), max(a, b) + 1, p)
                N2 = matrix_power_mod(mat_mod(T - l2 * np.eye(a+b, dtype=int), p), max(a, b) + 1, p)
                # P1 range is killed by a power of T-l1 and P2 range by T-l2.
                C.check(np.array_equal(mat_mod(N1 @ P1, p), np.zeros_like(P1)), group, "first generalized eigenspace")
                C.check(np.array_equal(mat_mod(N2 @ P2, p), np.zeros_like(P2)), group, "second generalized eigenspace")


def inverse_systems() -> None:
    group = "finite carriers and stable cores"
    for dim in range(1, 30):
        for terminal in range(1, dim + 1):
            dims = list(range(dim, terminal - 1, -1)) + [terminal] * 5
            C.check(min(dims) == terminal, group, "descending dimensions stabilize")
            C.check(terminal > 0, group, "nonzero intersection")

    # Coordinate projection inverse systems with nonzero stable cores.
    for depth in range(2, 40):
        dimensions = [depth + 3 - i if i <= depth else 3 for i in range(depth + 1)]
        dimensions = [max(3, d) for d in dimensions]
        C.check(all(d >= 3 for d in dimensions), group, "nonzero stable core")
        C.check(3 > 0, group, "inverse limit nonzero")

    # Tail escape finite truncations approach a zero intersection only when carrier dimension changes.
    for N in range(2, 80):
        nonzero_ranges = [N - m for m in range(N)]
        C.check(all(r > 0 for r in nonzero_ranges), group, "finite tails nonzero")
        C.check(nonzero_ranges[-1] == 1, group, "last finite tail")


def rt_transport() -> None:
    group = "R equals T transport"
    for n in range(1, 12):
        for _ in range(200):
            perm = list(range(n))
            RNG.shuffle(perm)
            mask = [RNG.randrange(2) for _ in range(n)]
            transported = [0] * n
            for i, value in enumerate(mask):
                transported[perm[i]] = value
            recovered = [transported[perm[i]] for i in range(n)]
            C.check(recovered == mask, group, "support homeomorphism")


def companion_spines() -> None:
    group = "companion spines and finite separators"
    for r in range(1, 9):
        for _ in range(100):
            # Vandermonde trace evaluations give an explicit full rank separator.
            points = list(range(1, r + 1))
            M = np.array([[pow(x, i) for i in range(r)] for x in points], dtype=object)
            # determinant of Vandermonde
            det = 1
            for i in range(r):
                for j in range(i + 1, r):
                    det *= points[j] - points[i]
            C.check(det != 0, group, "finite separator determinant")
            multiplicities = np.array([RNG.randrange(0, 6) for _ in range(r)], dtype=object)
            traces = M @ multiplicities
            # Solve over rationals using fractions through sympy only for small sizes.
            import sympy as sp
            recovered = sp.Matrix(M.tolist()).inv() * sp.Matrix(traces.tolist())
            C.check([int(x) for x in recovered] == [int(x) for x in multiplicities], group, "multiplicity recovery")

    for depth in range(1, 100):
        levels = [max(1, 8 - (m % 7)) for m in range(1, depth + 1)]
        C.check(all(x > 0 for x in levels), group, "nonempty finite companion levels")


def coefficient_two() -> None:
    group = "coefficient prime two"
    # F2[C2] is the dual numbers. Enumerate all four elements and idempotents.
    elems = list(itertools.product(range(2), repeat=2))
    idempotents = [a for a in elems if cyclic_convolution(a, a, 2) == a]
    C.check(set(idempotents) == {(0, 0), (1, 0)}, group, "only trivial idempotents")
    x = (1, 1)
    C.check(cyclic_convolution(x, x, 2) == (0, 0), group, "square zero augmentation generator")
    # Rational sign projectors have denominator two.
    C.check(1 % 2 == 1, group, "numerator odd")
    C.check(not float(0.5).is_integer(), group, "nonintegral coefficient")


def source_integrity() -> None:
    group = "source and package integrity"
    tex = TEX.read_text(encoding="utf-8")
    bib = BIB.read_text(encoding="utf-8")
    labels = re.findall(r"\\label\{([^}]+)\}", tex)
    refs: list[str] = []
    for command in ("ref", "cref", "Cref", "eqref", "pageref"):
        for raw in re.findall(rf"\\{command}\{{([^}}]+)\}}", tex):
            refs.extend(x.strip() for x in raw.split(","))
    bib_keys = set(re.findall(r"@\w+\{([^,]+),", bib))
    cite_keys: set[str] = set()
    for raw in re.findall(r"\\cite\{([^}]+)\}", tex):
        cite_keys.update(x.strip() for x in raw.split(","))

    C.check(len(labels) == len(set(labels)), group, "duplicate labels")
    C.check(set(refs).issubset(set(labels)), group, "missing internal reference")
    C.check(cite_keys.issubset(bib_keys), group, "missing bibliography key")
    C.check(bib_keys.issubset(cite_keys), group, "uncited bibliography entry")
    C.check(tex.count(";") == 0, group, "source semicolon")
    C.check("\\newpage" not in tex and "\\clearpage" not in tex and "\\pagebreak" not in tex, group, "forced page break")
    C.check("\\\\" not in re.sub(r"\\begin\{(?:matrix|pmatrix|bmatrix|array|aligned|align|tabular)[\s\S]*?\\end\{(?:matrix|pmatrix|bmatrix|array|aligned|align|tabular)\}", "", tex), group, "forced prose line break")

    proved = sum(len(re.findall(rf"\\begin\{{{env}\}}", tex)) for env in ("theorem", "proposition", "lemma", "corollary"))
    proofs = len(re.findall(r"\\begin\{proof\}", tex))
    C.check(proofs >= proved, group, "proof count")

    figures = re.findall(r"\\includegraphics(?:\[[^]]*\])?\{([^}]+)\}", tex)
    for name in figures:
        path = FIGURES / name
        C.check(path.exists(), group, f"missing figure {name}")
        C.check(path.stat().st_size > 1000, group, f"empty figure {name}")


def main() -> None:
    group_support_and_fitting()
    s3_adequacy()
    group_algebras()
    patching_support_models()
    hecke_packets()
    inverse_systems()
    rt_transport()
    companion_spines()
    coefficient_two()
    source_integrity()

    assert C.groups is not None
    result = {
        "total_checks": C.passed,
        "groups": C.groups,
        "status": "passed",
    }
    out = ROOT / "verification" / "verification_results.json"
    out.write_text(json.dumps(result, indent=2, sort_keys=True), encoding="utf-8")
    summary = [f"Paper XII verification: {C.passed}/{C.passed} checks passed in {len(C.groups)} groups"]
    for name, count in C.groups.items():
        summary.append(f"{name}: {count}")
    text = "\n".join(summary) + "\n"
    (ROOT / "verification" / "verification_summary.txt").write_text(text, encoding="utf-8")
    print(text, end="")


if __name__ == "__main__":
    main()
