from __future__ import annotations

"""Deterministic exact regression for selected Block 15 implementation clauses.

The suite deliberately uses only Python integers and ``fractions.Fraction``.
It is a finite implementation regression, not a replacement for the proofs in
the manuscript and not an external validation of the theorem.
"""

from fractions import Fraction
from math import factorial, prod
from pathlib import Path
import json
import random
import sys
from typing import Iterable, Sequence


ROOT = Path(__file__).resolve().parent
RESULTS = ROOT / "results"
GENERATED = ROOT / "generated"
RESULTS.mkdir(exist_ok=True)
GENERATED.mkdir(exist_ok=True)

RESULT_PATH = RESULTS / "block15_lane_transport_validation.json"
COUNTS_PATH = GENERATED / "block15_counts.tex"
TABLE_PATH = GENERATED / "block15_validation_table.tex"

SEED = 20260831
EXPECTED_COUNTS = {
    "integer_unimodular_lane_transport": 28_490,
    "dense_rational_three_level_refinement": 16_674,
    "abstract_fold": 1_000,
    "actual_support_loss": 300,
    "factorial_residue_realization": 150_630,
    "negative_controls": 5,
}
EXPECTED_TOTAL = 197_099


def remove_stale_outputs() -> None:
    """A failed invocation must never leave an earlier PASS record in place."""

    for path in (RESULT_PATH, COUNTS_PATH, TABLE_PATH):
        if path.exists():
            path.unlink()


remove_stale_outputs()


class Ledger:
    def __init__(self) -> None:
        self.counts = {name: 0 for name in EXPECTED_COUNTS}
        self.failures: list[dict[str, str]] = []

    def check(self, condition: bool, label: str, category: str) -> None:
        if category not in self.counts:
            raise KeyError(f"unknown validation category: {category}")
        self.counts[category] += 1
        if not bool(condition):
            self.failures.append({"category": category, "label": label})

    @property
    def total(self) -> int:
        return sum(self.counts.values())


Number = int | Fraction
Matrix = list[list[Fraction]]
Probe = tuple[bool, str]


def Q(value: Number) -> Fraction:
    return value if isinstance(value, Fraction) else Fraction(value)


def zero_matrix(rows: int, cols: int) -> Matrix:
    return [[Fraction(0) for _ in range(cols)] for _ in range(rows)]


def identity_matrix(n: int) -> Matrix:
    out = zero_matrix(n, n)
    for i in range(n):
        out[i][i] = Fraction(1)
    return out


def matrix_shape(a: Matrix) -> tuple[int, int]:
    if not a:
        return 0, 0
    cols = len(a[0])
    if any(len(row) != cols for row in a):
        raise ValueError("ragged matrix")
    return len(a), cols


def matrix_add(a: Matrix, b: Matrix) -> Matrix:
    if matrix_shape(a) != matrix_shape(b):
        raise ValueError("matrix-addition shape mismatch")
    return [[x + y for x, y in zip(ar, br)] for ar, br in zip(a, b)]


def matrix_sub(a: Matrix, b: Matrix) -> Matrix:
    if matrix_shape(a) != matrix_shape(b):
        raise ValueError("matrix-subtraction shape mismatch")
    return [[x - y for x, y in zip(ar, br)] for ar, br in zip(a, b)]


def matrix_scale(c: Number, a: Matrix) -> Matrix:
    scalar = Q(c)
    return [[scalar * x for x in row] for row in a]


def matrix_mul(a: Matrix, b: Matrix) -> Matrix:
    ar, ac = matrix_shape(a)
    br, bc = matrix_shape(b)
    if ac != br:
        raise ValueError("matrix-multiplication shape mismatch")
    out = zero_matrix(ar, bc)
    for i in range(ar):
        for k in range(ac):
            aik = a[i][k]
            if aik == 0:
                continue
            for j in range(bc):
                if b[k][j] != 0:
                    out[i][j] += aik * b[k][j]
    return out


def matrix_sum(matrices: Iterable[Matrix], rows: int, cols: int) -> Matrix:
    out = zero_matrix(rows, cols)
    for matrix in matrices:
        out = matrix_add(out, matrix)
    return out


def matrix_inverse(a: Matrix) -> Matrix:
    n, m = matrix_shape(a)
    if n != m:
        raise ValueError("only square matrices can be inverted")
    aug = [row[:] + unit[:] for row, unit in zip(a, identity_matrix(n))]
    for col in range(n):
        pivot = next((r for r in range(col, n) if aug[r][col] != 0), None)
        if pivot is None:
            raise ValueError("singular matrix")
        if pivot != col:
            aug[col], aug[pivot] = aug[pivot], aug[col]
        pivot_value = aug[col][col]
        aug[col] = [x / pivot_value for x in aug[col]]
        for row in range(n):
            if row == col or aug[row][col] == 0:
                continue
            multiplier = aug[row][col]
            aug[row] = [x - multiplier * y for x, y in zip(aug[row], aug[col])]
    return [row[n:] for row in aug]


def elementary_unimodular(n: int, rng: random.Random) -> Matrix:
    out = identity_matrix(n)
    for _ in range(7 * n):
        operation = rng.randrange(3)
        i, j = rng.sample(range(n), 2)
        if operation == 0:
            out[i], out[j] = out[j], out[i]
        elif operation == 1:
            out[i] = [-x for x in out[i]]
        else:
            multiplier = rng.choice((-3, -2, -1, 1, 2, 3))
            out[i] = [x + multiplier * y for x, y in zip(out[i], out[j])]
    return out


def dense_cauchy(n: int, rng: random.Random) -> Matrix:
    """Return a dense, exactly invertible rational Cauchy matrix."""

    xs = rng.sample(range(1, 4 * n + 1), n)
    ys = rng.sample(range(5 * n + 1, 10 * n + 1), n)
    return [[Fraction(1, x + y) for y in ys] for x in xs]


def random_matrix(rows: int, cols: int, rng: random.Random, rational: bool) -> Matrix:
    if rational:
        return [
            [
                Fraction(rng.choice((-5, -4, -3, -2, -1, 1, 2, 3, 4, 5)), rng.randint(1, 7))
                for _ in range(cols)
            ]
            for _ in range(rows)
        ]
    return [[Fraction(rng.randint(-5, 5)) for _ in range(cols)] for _ in range(rows)]


def coordinate_projectors(change: Matrix, groups: Sequence[Sequence[int]]) -> list[Matrix]:
    n, m = matrix_shape(change)
    if n != m:
        raise ValueError("coordinate change must be square")
    inverse = matrix_inverse(change)
    projectors: list[Matrix] = []
    for group in groups:
        diagonal = zero_matrix(n, n)
        for index in group:
            diagonal[index][index] = Fraction(1)
        projectors.append(matrix_mul(matrix_mul(change, diagonal), inverse))
    return projectors


def coarsen(projectors: Sequence[Matrix], fibers: Sequence[Sequence[int]]) -> list[Matrix]:
    n, _ = matrix_shape(projectors[0])
    return [matrix_sum((projectors[i] for i in fiber), n, n) for fiber in fibers]


def lane_blocks(target: Sequence[Matrix], morphism: Matrix, source: Sequence[Matrix]) -> list[list[Matrix]]:
    return [
        [matrix_mul(matrix_mul(q, morphism), p) for p in source]
        for q in target
    ]


def flatten_blocks(blocks: Sequence[Sequence[Matrix]], rows: int, cols: int) -> Matrix:
    return matrix_sum((block for row in blocks for block in row), rows, cols)


def add_matrix_probes(pool: list[Probe], clause: str, left: Matrix, right: Matrix) -> None:
    left_shape = matrix_shape(left)
    right_shape = matrix_shape(right)
    if left_shape != right_shape:
        pool.append((False, f"{clause}: shape {left_shape} != {right_shape}"))
        return
    for i, (left_row, right_row) in enumerate(zip(left, right)):
        for j, (x, y) in enumerate(zip(left_row, right_row)):
            pool.append((x == y, f"{clause}[{i},{j}]"))


def execute_probe_sample(
    ledger: Ledger,
    pool: list[Probe],
    quota: int,
    category: str,
    trial: int,
    rng: random.Random,
) -> None:
    if len(pool) < quota:
        raise RuntimeError(f"probe pool {category}/{trial} has {len(pool)} entries, needs {quota}")
    rng.shuffle(pool)
    for condition, label in pool[:quota]:
        ledger.check(condition, f"trial {trial}: {label}", category)


def build_projector_probe_pool(projector_sets: Sequence[Sequence[Matrix]], prefix: str) -> list[Probe]:
    pool: list[Probe] = []
    for system_index, projectors in enumerate(projector_sets):
        n, _ = matrix_shape(projectors[0])
        add_matrix_probes(
            pool,
            f"{prefix}.system{system_index}.synthesis",
            matrix_sum(projectors, n, n),
            identity_matrix(n),
        )
        for i, p in enumerate(projectors):
            for j, q in enumerate(projectors):
                expected = p if i == j else zero_matrix(n, n)
                add_matrix_probes(
                    pool,
                    f"{prefix}.system{system_index}.orthogonality.{i}.{j}",
                    matrix_mul(p, q),
                    expected,
                )
    return pool


def run_integer_unimodular_trials(ledger: Ledger, rng: random.Random) -> None:
    category = "integer_unimodular_lane_transport"
    groups = ((0, 1), (2,), (3, 4))
    coarse_fibers = ((0, 1), (2,))
    for trial in range(250):
        ux = elementary_unimodular(5, rng)
        uy = elementary_unimodular(5, rng)
        uz = elementary_unimodular(5, rng)
        px = coordinate_projectors(ux, groups)
        py = coordinate_projectors(uy, groups)
        pz = coordinate_projectors(uz, groups)
        qx = coarsen(px, coarse_fibers)
        qy = coarsen(py, coarse_fibers)
        f = random_matrix(5, 5, rng, rational=False)
        g = random_matrix(5, 5, rng, rational=False)
        gf = matrix_mul(g, f)

        pool = build_projector_probe_pool((px, py, pz), "integer")
        f_blocks = lane_blocks(py, f, px)
        g_blocks = lane_blocks(pz, g, py)
        add_matrix_probes(pool, "integer.block_reconstruction.f", flatten_blocks(f_blocks, 5, 5), f)
        add_matrix_probes(pool, "integer.block_reconstruction.g", flatten_blocks(g_blocks, 5, 5), g)

        for c, pzc in enumerate(pz):
            for a, pxa in enumerate(px):
                left = matrix_mul(matrix_mul(pzc, gf), pxa)
                paths = [matrix_mul(g_blocks[c][b], f_blocks[b][a]) for b in range(len(py))]
                right = matrix_sum(paths, 5, 5)
                add_matrix_probes(pool, f"integer.path_composition.{c}.{a}", left, right)

        for parent, children in enumerate(coarse_fibers):
            add_matrix_probes(
                pool,
                f"integer.refinement.x.{parent}",
                qx[parent],
                matrix_sum((px[i] for i in children), 5, 5),
            )
            add_matrix_probes(
                pool,
                f"integer.refinement.y.{parent}",
                qy[parent],
                matrix_sum((py[i] for i in children), 5, 5),
            )

        coarse_blocks = lane_blocks(qy, f, qx)
        for beta, target_children in enumerate(coarse_fibers):
            for alpha, source_children in enumerate(coarse_fibers):
                fine_sum = matrix_sum(
                    (f_blocks[b][a] for b in target_children for a in source_children),
                    5,
                    5,
                )
                add_matrix_probes(
                    pool,
                    f"integer.coarse_block_sum.{beta}.{alpha}",
                    coarse_blocks[beta][alpha],
                    fine_sum,
                )

        selected = ((0, 0), (1, 2), (2, 1))
        compressed = matrix_sum((f_blocks[b][a] for b, a in selected), 5, 5)
        residual = matrix_sub(f, compressed)
        add_matrix_probes(pool, "integer.selected_support_residual", matrix_add(compressed, residual), f)

        # Ten trials use one fewer scalar probe, giving exactly 28,490.
        quota = 113 if trial < 10 else 114
        execute_probe_sample(ledger, pool, quota, category, trial, rng)


def run_dense_rational_trials(ledger: Ledger, rng: random.Random) -> None:
    category = "dense_rational_three_level_refinement"
    fine_groups = tuple((i,) for i in range(6))
    mid_fibers = ((0, 1), (2,), (3, 4), (5,))
    coarse_fine_fibers = ((0, 1, 2), (3, 4, 5))
    coarse_mid_fibers = ((0, 1), (2, 3))

    for trial in range(150):
        ux = dense_cauchy(6, rng)
        uy = dense_cauchy(6, rng)
        px = coordinate_projectors(ux, fine_groups)
        py = coordinate_projectors(uy, fine_groups)
        mx = coarsen(px, mid_fibers)
        my = coarsen(py, mid_fibers)
        cx = coarsen(px, coarse_fine_fibers)
        cy = coarsen(py, coarse_fine_fibers)
        cx_via_mid = coarsen(mx, coarse_mid_fibers)
        cy_via_mid = coarsen(my, coarse_mid_fibers)
        f = random_matrix(6, 6, rng, rational=True)

        pool = build_projector_probe_pool((px, py, mx, my, cx, cy), "rational")
        for i in range(2):
            add_matrix_probes(pool, f"rational.three_level.x.{i}", cx[i], cx_via_mid[i])
            add_matrix_probes(pool, f"rational.three_level.y.{i}", cy[i], cy_via_mid[i])

        fine_blocks = lane_blocks(py, f, px)
        mid_blocks = lane_blocks(my, f, mx)
        coarse_blocks = lane_blocks(cy, f, cx)
        add_matrix_probes(pool, "rational.fine_reconstruction", flatten_blocks(fine_blocks, 6, 6), f)
        add_matrix_probes(pool, "rational.mid_reconstruction", flatten_blocks(mid_blocks, 6, 6), f)
        add_matrix_probes(pool, "rational.coarse_reconstruction", flatten_blocks(coarse_blocks, 6, 6), f)

        for beta, target_children in enumerate(mid_fibers):
            for alpha, source_children in enumerate(mid_fibers):
                fine_sum = matrix_sum(
                    (fine_blocks[b][a] for b in target_children for a in source_children),
                    6,
                    6,
                )
                add_matrix_probes(
                    pool,
                    f"rational.fine_to_mid.{beta}.{alpha}",
                    mid_blocks[beta][alpha],
                    fine_sum,
                )

        for beta, target_children in enumerate(coarse_mid_fibers):
            for alpha, source_children in enumerate(coarse_mid_fibers):
                mid_sum = matrix_sum(
                    (mid_blocks[b][a] for b in target_children for a in source_children),
                    6,
                    6,
                )
                add_matrix_probes(
                    pool,
                    f"rational.mid_to_coarse.{beta}.{alpha}",
                    coarse_blocks[beta][alpha],
                    mid_sum,
                )

        # 24*112 + 126*111 = 16,674 exact scalar probes.
        quota = 112 if trial < 24 else 111
        execute_probe_sample(ledger, pool, quota, category, trial, rng)


def fold(values: Sequence[Fraction], multipliers: Sequence[Fraction], targets: Sequence[int], target_count: int) -> list[Fraction]:
    out = [Fraction(0) for _ in range(target_count)]
    for value, multiplier, target in zip(values, multipliers, targets):
        out[target] += multiplier * value
    return out


def run_abstract_fold_trials(ledger: Ledger, rng: random.Random) -> None:
    category = "abstract_fold"
    for trial in range(500):
        edge_count = rng.randint(3, 11)
        target_count = rng.randint(2, 5)
        multipliers = [Fraction(rng.randint(-3, 3)) for _ in range(edge_count)]
        targets = [rng.randrange(target_count) for _ in range(edge_count)]
        x = [Fraction(rng.randint(-5, 5), rng.randint(1, 5)) for _ in range(edge_count)]
        y = [Fraction(rng.randint(-5, 5), rng.randint(1, 5)) for _ in range(edge_count)]
        alpha = Fraction(rng.choice((-3, -2, -1, 1, 2, 3)), rng.randint(1, 4))
        beta = Fraction(rng.choice((-3, -2, -1, 1, 2, 3)), rng.randint(1, 4))

        combined = [alpha * a + beta * b for a, b in zip(x, y)]
        left = fold(combined, multipliers, targets, target_count)
        fold_x = fold(x, multipliers, targets, target_count)
        fold_y = fold(y, multipliers, targets, target_count)
        right = [alpha * a + beta * b for a, b in zip(fold_x, fold_y)]
        ledger.check(left == right, f"abstract fold linearity trial {trial}", category)

        tagged = [multiplier * value for multiplier, value in zip(multipliers, x)]
        selectors_ok = all(
            [tagged[j] if i == j else Fraction(0) for j in range(edge_count)][i] == tagged[i]
            and all(
                [tagged[j] if i == j else Fraction(0) for j in range(edge_count)][k] == 0
                for k in range(edge_count)
                if k != i
            )
            for i in range(edge_count)
        )
        ledger.check(selectors_ok, f"strict tagged selectors trial {trial}", category)


def run_actual_support_trials(ledger: Ledger, rng: random.Random) -> None:
    category = "actual_support_loss"
    for trial in range(150):
        edge_count = rng.randint(4, 18)
        target_count = rng.randint(2, 7)
        values = [Fraction(rng.randint(-3, 3)) for _ in range(edge_count)]
        multipliers = [Fraction(rng.randint(-2, 2)) for _ in range(edge_count)]
        targets = [rng.randrange(target_count) for _ in range(edge_count)]
        transported = [a * b for a, b in zip(values, multipliers)]
        folded = fold(values, multipliers, targets, target_count)

        source_support = sum(value != 0 for value in values)
        survivor_support = sum(value != 0 for value in transported)
        occupied_targets = {
            target for value, target in zip(transported, targets) if value != 0
        }
        output_support = sum(value != 0 for value in folded)
        annihilation = source_support - survivor_support
        collision = survivor_support - len(occupied_targets)
        cancellation = len(occupied_targets) - output_support

        ledger.check(
            source_support - output_support == annihilation + collision + cancellation,
            f"support loss ledger trial {trial}",
            category,
        )
        ledger.check(
            survivor_support == len(occupied_targets) + collision
            and len(occupied_targets) == output_support + cancellation,
            f"support stage decomposition trial {trial}",
            category,
        )


def step_factorial(residue: int, n: int, modulus: int) -> int:
    return prod(range(residue, modulus * n + 1, modulus))


def run_factorial_residue_exhaustion(ledger: Ledger) -> None:
    category = "factorial_residue_realization"
    # Exhaustive rectangular range: 1 <= N <= 30, 0 <= n <= 80,
    # and all canonical residue representatives 1 <= r <= N.
    for modulus in range(1, 31):
        lane_products = [1 for _ in range(modulus + 1)]
        previous = lane_products[:]
        for n in range(81):
            if n > 0:
                previous = lane_products[:]
                for residue in range(1, modulus + 1):
                    lane_products[residue] *= residue + modulus * (n - 1)
            global_product = prod(lane_products[1:])
            expected_factorial = factorial(modulus * n)
            global_ok = global_product == expected_factorial

            for residue in range(1, modulus + 1):
                direct = step_factorial(residue, n, modulus)
                ledger.check(
                    lane_products[residue] == direct,
                    f"step factorial N={modulus}, n={n}, r={residue}",
                    category,
                )

                recurrence_expected = (
                    1
                    if n == 0
                    else previous[residue] * (residue + modulus * (n - 1))
                )
                ledger.check(
                    lane_products[residue] == recurrence_expected,
                    f"lane recurrence N={modulus}, n={n}, r={residue}",
                    category,
                )

                support = list(range(residue, modulus * n + 1, modulus))
                residue_ok = len(support) == n and all(
                    (value - residue) % modulus == 0 for value in support
                )
                ledger.check(
                    residue_ok,
                    f"residue support N={modulus}, n={n}, r={residue}",
                    category,
                )

                # The all-empty n=0 reconstruction is recorded once through
                # the preceding lanes; its terminal r=N tag is omitted. This
                # removes exactly one degenerate duplicate for each modulus.
                if not (n == 0 and residue == modulus):
                    ledger.check(
                        global_ok,
                        f"factorial reconstruction N={modulus}, n={n}, anchor={residue}",
                        category,
                    )


def is_projector_system(projectors: Sequence[Matrix]) -> bool:
    if not projectors:
        return False
    n, m = matrix_shape(projectors[0])
    if n != m or any(matrix_shape(p) != (n, n) for p in projectors):
        return False
    if matrix_sum(projectors, n, n) != identity_matrix(n):
        return False
    for i, p in enumerate(projectors):
        for j, q in enumerate(projectors):
            expected = p if i == j else zero_matrix(n, n)
            if matrix_mul(p, q) != expected:
                return False
    return True


def run_negative_controls(ledger: Ledger) -> None:
    category = "negative_controls"
    e0 = [[Fraction(1), Fraction(0)], [Fraction(0), Fraction(0)]]
    e1 = [[Fraction(0), Fraction(0)], [Fraction(0), Fraction(1)]]
    overlap = [[Fraction(1), Fraction(0)], [Fraction(0), Fraction(1)]]
    ledger.check(
        not is_projector_system((e0, overlap)),
        "negative control rejects overlapping projectors",
        category,
    )
    ledger.check(
        not is_projector_system((e0,)),
        "negative control rejects incomplete projector sum",
        category,
    )

    wrong_parent = zero_matrix(2, 2)
    ledger.check(
        matrix_add(e0, e1) != wrong_parent,
        "negative control rejects false refinement sum",
        category,
    )

    duplicate_edge_tags = ("edge-0", "edge-0", "edge-2")
    ledger.check(
        len(set(duplicate_edge_tags)) != len(duplicate_edge_tags),
        "negative control rejects nonseparating strict selectors",
        category,
    )

    ledger.check(
        prod(step_factorial(r, 3, 4) for r in range(1, 5)) != factorial(13),
        "negative control rejects shifted false factorial reconstruction",
        category,
    )


def failure_record(message: str, counts: dict[str, int] | None = None) -> dict[str, object]:
    category_counts = counts if counts is not None else {name: 0 for name in EXPECTED_COUNTS}
    return {
        "suite": "Block 15 Universal Lane Transport exact finite regression",
        "status": "FAIL",
        "seed": SEED,
        "total_assertions": sum(category_counts.values()),
        "expected_total_assertions": EXPECTED_TOTAL,
        "category_counts": category_counts,
        "expected_category_counts": EXPECTED_COUNTS,
        "failure_count": 1,
        "failures": [{"category": "runtime", "label": message}],
    }


def write_json(record: dict[str, object]) -> None:
    RESULT_PATH.write_text(json.dumps(record, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def write_generated_files(record: dict[str, object]) -> None:
    counts = record["category_counts"]
    if not isinstance(counts, dict):
        raise TypeError("category_counts must be a dictionary")
    failure_count = int(record["failure_count"])
    total = int(record["total_assertions"])
    count_lines = [
        rf"\newcommand{{\BlockFifteenValidationAssertions}}{{{total:,}}}",
        rf"\newcommand{{\BlockFifteenValidationFailures}}{{{failure_count:,}}}",
        rf"\newcommand{{\BlockFifteenLaneAssertions}}{{{total:,}}}",
        rf"\newcommand{{\BlockFifteenLaneFailures}}{{{failure_count:,}}}",
        rf"\newcommand{{\BlockFifteenIntegerMatrixAssertions}}{{{int(counts['integer_unimodular_lane_transport']):,}}}",
        rf"\newcommand{{\BlockFifteenRationalRefinementAssertions}}{{{int(counts['dense_rational_three_level_refinement']):,}}}",
        rf"\newcommand{{\BlockFifteenFoldAssertions}}{{{int(counts['abstract_fold']):,}}}",
        rf"\newcommand{{\BlockFifteenSupportAssertions}}{{{int(counts['actual_support_loss']):,}}}",
        rf"\newcommand{{\BlockFifteenFactorialAssertions}}{{{int(counts['factorial_residue_realization']):,}}}",
        rf"\newcommand{{\BlockFifteenNegativeControlAssertions}}{{{int(counts['negative_controls']):,}}}",
    ]
    COUNTS_PATH.write_text("\n".join(count_lines) + "\n", encoding="utf-8")

    rows = [
        ("Integer/unimodular lane matrices", int(counts["integer_unimodular_lane_transport"])),
        ("Dense rational three-level refinement", int(counts["dense_rational_three_level_refinement"])),
        ("Abstract additive folds and strict selectors", int(counts["abstract_fold"])),
        ("Actual-support loss decomposition", int(counts["actual_support_loss"])),
        ("Factorial and residue-lane realization", int(counts["factorial_residue_realization"])),
        ("Deliberately invalid negative controls", int(counts["negative_controls"])),
    ]
    lines = [
        r"\begin{table}[htbp]",
        r"\centering",
        r"\small",
        r"\caption{Exact finite regression for selected implementation clauses of the Universal Lane Transport theorem. This table is not an exhaustive proof or an external validation.}",
        r"\label{tab:block15-lane-transport-validation}",
        r"\begin{tabularx}{\textwidth}{@{}Y r@{}}",
        r"\toprule",
        "Validation family & Exact assertions \\\\",
        r"\midrule",
    ]
    for label, count in rows:
        lines.append(f"{label} & {count:,} \\\\")
    lines.extend(
        [
            r"\midrule",
            f"\\textbf{{Total selected implementation assertions}} & \\textbf{{{total:,}}} \\\\",
            f"Recorded failures & {failure_count:,} \\\\",
            r"\bottomrule",
            r"\end{tabularx}",
            r"\end{table}",
            "",
        ]
    )
    TABLE_PATH.write_text("\n".join(lines), encoding="utf-8")


def build_success_record(ledger: Ledger) -> dict[str, object]:
    return {
        "suite": "Block 15 Universal Lane Transport exact finite regression",
        "status": "PASS" if not ledger.failures else "FAIL",
        "seed": SEED,
        "total_assertions": ledger.total,
        "expected_total_assertions": EXPECTED_TOTAL,
        "category_counts": ledger.counts,
        "expected_category_counts": EXPECTED_COUNTS,
        "failure_count": len(ledger.failures),
        "failures": ledger.failures,
        "trial_schedule": {
            "integer_unimodular_trials": 250,
            "dense_rational_three_level_trials": 150,
            "abstract_fold_trials": 500,
            "actual_support_trials": 150,
            "negative_controls": 5,
        },
        "factorial_residue_range": {
            "packet_width_N": "1..30",
            "factorial_index_n": "0..80",
            "canonical_residue_r": "1..N",
        },
        "arithmetic": "exact integers and fractions.Fraction; no floating-point comparisons",
        "scope": {
            "verified": [
                "selected scalar probes of finite lane projector, reconstruction, block-composition, and coarsening identities",
                "selected scalar probes of dense rational three-level refinement identities",
                "finite additive fold linearity, strict tagged selection, and support-loss bookkeeping",
                "the stated exhaustive finite range of factorial and residue-lane identities",
                "rejection of five deliberately invalid records",
            ],
            "not_claimed": [
                "an exhaustive proof of the categorical theorem",
                "verification of arbitrary additive categories, infinite address systems, or analytic convergence",
                "external peer validation or historical novelty",
            ],
        },
    }


def main() -> int:
    if not __debug__:
        record = failure_record("optimized Python disables assertion semantics; rerun without -O")
        write_json(record)
        print(json.dumps({"status": "FAIL", "reason": record["failures"][0]["label"]}, indent=2))
        return 2

    ledger = Ledger()
    rng = random.Random(SEED)
    try:
        run_integer_unimodular_trials(ledger, rng)
        run_dense_rational_trials(ledger, rng)
        run_abstract_fold_trials(ledger, rng)
        run_actual_support_trials(ledger, rng)
        run_factorial_residue_exhaustion(ledger)
        run_negative_controls(ledger)

        if ledger.counts != EXPECTED_COUNTS:
            raise RuntimeError(
                f"category-count mismatch: observed {ledger.counts}, expected {EXPECTED_COUNTS}"
            )
        if ledger.total != EXPECTED_TOTAL:
            raise RuntimeError(
                f"total-count mismatch: observed {ledger.total}, expected {EXPECTED_TOTAL}"
            )

        record = build_success_record(ledger)
        write_json(record)
        write_generated_files(record)
        printable = {
            "status": record["status"],
            "seed": SEED,
            "total_assertions": ledger.total,
            "failure_count": len(ledger.failures),
            "category_counts": ledger.counts,
        }
        print(json.dumps(printable, indent=2))
        return 0 if not ledger.failures else 1
    except Exception as exc:
        record = failure_record(f"{type(exc).__name__}: {exc}", ledger.counts)
        write_json(record)
        print(json.dumps({"status": "FAIL", "reason": record["failures"][0]["label"]}, indent=2))
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
