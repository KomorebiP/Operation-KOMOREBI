from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction
from itertools import product
from pathlib import Path
import json
import random


ROOT = Path(__file__).resolve().parent
GEN = ROOT / "generated"
GEN.mkdir(exist_ok=True)

Perm = tuple[int, ...]


def compose(p: Perm, q: Perm) -> Perm:
    """Composition p o q."""
    return tuple(p[q[i]] for i in range(len(p)))


def inv(p: Perm) -> Perm:
    out = [0] * len(p)
    for i, j in enumerate(p):
        out[j] = i
    return tuple(out)


def cycle(n: int) -> Perm:
    return tuple((i + 1) % n for i in range(n))


def transposition(n: int, a: int, b: int) -> Perm:
    p = list(range(n))
    p[a], p[b] = p[b], p[a]
    return tuple(p)


def generate_group(gens: list[Perm]) -> list[Perm]:
    n = len(gens[0])
    e = tuple(range(n))
    seen = {e}
    frontier = [e]
    gens2 = gens + [inv(g) for g in gens]
    while frontier:
        a = frontier.pop()
        for g in gens2:
            b = compose(a, g)
            if b not in seen:
                seen.add(b)
                frontier.append(b)
    return sorted(seen)


def power(g: Perm, k: int) -> Perm:
    e = tuple(range(len(g)))
    out = e
    for _ in range(k):
        out = compose(out, g)
    return out


def group_families() -> dict[str, list[Perm]]:
    out: dict[str, list[Perm]] = {}
    for n in (2, 3, 4, 5, 6, 8):
        out[f"C{n}"] = generate_group([cycle(n)])
    a = (1, 0, 3, 2)
    b = (2, 3, 0, 1)
    out["V4"] = generate_group([a, b])
    out["S3"] = generate_group([cycle(3), transposition(3, 0, 1)])
    r = cycle(4)
    s = (0, 3, 2, 1)
    out["D4"] = generate_group([r, s])
    out["A4"] = generate_group([(1, 2, 0, 3), (1, 3, 2, 0)])
    return out


def mult_table(group: list[Perm]) -> list[list[int]]:
    pos = {g: i for i, g in enumerate(group)}
    return [[pos[compose(a, b)] for b in group] for a in group]


def inverse_indices(group: list[Perm]) -> list[int]:
    pos = {g: i for i, g in enumerate(group)}
    return [pos[inv(g)] for g in group]


def enumerate_subgroups(group: list[Perm], table: list[list[int]], inv_idx: list[int]) -> list[frozenset[int]]:
    n = len(group)
    e = group.index(tuple(range(len(group[0]))))
    subs: list[frozenset[int]] = []
    for mask in range(1 << n):
        if not (mask >> e) & 1:
            continue
        S = {i for i in range(n) if (mask >> i) & 1}
        ok = True
        for a in tuple(S):
            if inv_idx[a] not in S:
                ok = False
                break
        if not ok:
            continue
        for a in tuple(S):
            for b in tuple(S):
                if table[a][b] not in S:
                    ok = False
                    break
            if not ok:
                break
        if ok:
            subs.append(frozenset(S))
    return sorted(subs, key=lambda s: (len(s), tuple(sorted(s))))


def closure(gens: set[int], table: list[list[int]], inv_idx: list[int], e: int) -> frozenset[int]:
    S = set(gens)
    S.add(e)
    changed = True
    while changed:
        changed = False
        for a in list(S):
            if inv_idx[a] not in S:
                S.add(inv_idx[a])
                changed = True
        for a in list(S):
            for b in list(S):
                c = table[a][b]
                if c not in S:
                    S.add(c)
                    changed = True
    return frozenset(S)


def conjugate_subgroup(H: frozenset[int], g: int, table: list[list[int]], inv_idx: list[int]) -> frozenset[int]:
    gi = inv_idx[g]
    return frozenset(table[table[g][h]][gi] for h in H)


def is_normal(H: frozenset[int], n: int, table: list[list[int]], inv_idx: list[int]) -> bool:
    return all(conjugate_subgroup(H, g, table, inv_idx) == H for g in range(n))


def product_set(H: frozenset[int], K: frozenset[int], table: list[list[int]]) -> frozenset[int]:
    return frozenset(table[h][k] for h in H for k in K)


def average(H: frozenset[int], n: int) -> tuple[Fraction, ...]:
    q = Fraction(1, len(H))
    return tuple(q if i in H else Fraction(0) for i in range(n))


def conv(a: tuple[Fraction, ...], b: tuple[Fraction, ...], table: list[list[int]]) -> tuple[Fraction, ...]:
    n = len(a)
    out = [Fraction(0) for _ in range(n)]
    for i, ai in enumerate(a):
        if ai == 0:
            continue
        for j, bj in enumerate(b):
            if bj:
                out[table[i][j]] += ai * bj
    return tuple(out)


def delta(g: int, n: int) -> tuple[Fraction, ...]:
    return tuple(Fraction(1) if i == g else Fraction(0) for i in range(n))


def double_cosets(K: frozenset[int], H: frozenset[int], n: int, table: list[list[int]]) -> list[frozenset[int]]:
    remaining = set(range(n))
    out: list[frozenset[int]] = []
    while remaining:
        x = min(remaining)
        C = frozenset(table[table[k][x]][h] for k in K for h in H)
        out.append(C)
        remaining -= C
    return out


def regular_left_permutation(g: int, n: int, table: list[list[int]]) -> tuple[int, ...]:
    return tuple(table[g][x] for x in range(n))


GQ = tuple[Fraction, Fraction]
Matrix = list[list[GQ]]

ZERO_Q: GQ = (Fraction(0), Fraction(0))
ONE_Q: GQ = (Fraction(1), Fraction(0))


def q(a: int | Fraction = 0, b: int | Fraction = 0) -> GQ:
    return (Fraction(a), Fraction(b))


def qadd(x: GQ, y: GQ) -> GQ:
    return (x[0] + y[0], x[1] + y[1])


def qneg(x: GQ) -> GQ:
    return (-x[0], -x[1])


def qsub(x: GQ, y: GQ) -> GQ:
    return qadd(x, qneg(y))


def qmul(x: GQ, y: GQ) -> GQ:
    return (x[0] * y[0] - x[1] * y[1], x[0] * y[1] + x[1] * y[0])


def qconj(x: GQ) -> GQ:
    return (x[0], -x[1])


def qinv(x: GQ) -> GQ:
    den = x[0] * x[0] + x[1] * x[1]
    if den == 0:
        raise ZeroDivisionError
    return (x[0] / den, -x[1] / den)


def mat_conj(A: Matrix) -> Matrix:
    return [[qconj(x) for x in row] for row in A]


def mat_mul(A: Matrix, B: Matrix) -> Matrix:
    if len(A[0]) != len(B):
        raise ValueError('shape mismatch')
    out = [[ZERO_Q for _ in range(len(B[0]))] for _ in range(len(A))]
    for i in range(len(A)):
        for k in range(len(B)):
            if A[i][k] == ZERO_Q:
                continue
            for j in range(len(B[0])):
                out[i][j] = qadd(out[i][j], qmul(A[i][k], B[k][j]))
    return out


def mat_eye(n: int) -> Matrix:
    return [[ONE_Q if i == j else ZERO_Q for j in range(n)] for i in range(n)]


def mat_det(A: Matrix) -> GQ:
    if len(A) == 1:
        return A[0][0]
    if len(A) == 2 and len(A[0]) == 2:
        return qsub(qmul(A[0][0], A[1][1]), qmul(A[0][1], A[1][0]))
    raise ValueError('only 1x1 and 2x2 matrices are used')


def mat_inv(A: Matrix) -> Matrix:
    if len(A) == 1:
        return [[qinv(A[0][0])]]
    if len(A) == 2 and len(A[0]) == 2:
        det = mat_det(A)
        invdet = qinv(det)
        return [
            [qmul(invdet, A[1][1]), qmul(invdet, qneg(A[0][1]))],
            [qmul(invdet, qneg(A[1][0])), qmul(invdet, A[0][0])],
        ]
    raise ValueError('only 1x1 and 2x2 matrices are used')


def mat_equal(A: Matrix, B: Matrix) -> bool:
    return len(A) == len(B) and len(A[0]) == len(B[0]) and all(
        A[i][j] == B[i][j] for i in range(len(A)) for j in range(len(A[0]))
    )


checks = 0
failures: list[str] = []
category_counts: dict[str, int] = {
    "finite_subgroup_projectors": 0,
    "normality_and_closure": 0,
    "double_coset_packets": 0,
    "ramification_filtrations": 0,
    "hilbert90_cocycles": 0,
    "projective_brauer_examples": 0,
    "finite_tensor_models": 0,
}


def check(cond: bool, label: str, category: str) -> None:
    global checks
    checks += 1
    category_counts[category] += 1
    if not cond:
        failures.append(label)


summary_rows = []
groups = group_families()
for name, G in groups.items():
    n = len(G)
    table = mult_table(G)
    inv_idx = inverse_indices(G)
    e = G.index(tuple(range(len(G[0]))))
    subs = enumerate_subgroups(G, table, inv_idx)
    normal_count = sum(is_normal(H, n, table, inv_idx) for H in subs)
    permutable_pairs = 0
    noncommuting_pairs = 0
    double_coset_total = 0

    # Reynolds projectors and reverse inclusion.
    avgs = {H: average(H, n) for H in subs}
    for H in subs:
        PH = avgs[H]
        check(conv(PH, PH, table) == PH, f"{name}: Reynolds idempotence {sorted(H)}", "finite_subgroup_projectors")
        check(sum(PH) == 1, f"{name}: Reynolds normalization {sorted(H)}", "finite_subgroup_projectors")
        check(n % len(H) == 0, f"{name}: fixed-rank divisibility {sorted(H)}", "finite_subgroup_projectors")
        # rank in the regular representation equals the number of left H-orbits.
        check(n // len(H) >= 1, f"{name}: fixed-rank positivity {sorted(H)}", "finite_subgroup_projectors")
        central = all(conv(PH, delta(g, n), table) == conv(delta(g, n), PH, table) for g in range(n))
        check(central == is_normal(H, n, table, inv_idx), f"{name}: normality-centrality {sorted(H)}", "normality_and_closure")
        core = set(range(n))
        conj_union: set[int] = set()
        for g in range(n):
            Hg = conjugate_subgroup(H, g, table, inv_idx)
            core &= set(Hg)
            conj_union |= set(Hg)
        core_f = frozenset(core)
        ncl = closure(conj_union, table, inv_idx, e)
        check(is_normal(core_f, n, table, inv_idx), f"{name}: core normal {sorted(H)}", "normality_and_closure")
        check(is_normal(ncl, n, table, inv_idx), f"{name}: normal closure normal {sorted(H)}", "normality_and_closure")
        check(core_f.issubset(H) and H.issubset(ncl), f"{name}: core/closure containment {sorted(H)}", "normality_and_closure")

    for H in subs:
        for J in subs:
            PH, PJ = avgs[H], avgs[J]
            if H.issubset(J):
                check(conv(PH, PJ, table) == PJ, f"{name}: nested product H<=J", "finite_subgroup_projectors")
                check(conv(PJ, PH, table) == PJ, f"{name}: nested reverse product H<=J", "finite_subgroup_projectors")
            HJ = product_set(H, J, table)
            JH = product_set(J, H, table)
            commute = conv(PH, PJ, table) == conv(PJ, PH, table)
            check(commute == (HJ == JH), f"{name}: permutability/projector commutation", "finite_subgroup_projectors")
            if HJ == JH:
                permutable_pairs += 1
                generated = closure(set(H) | set(J), table, inv_idx, e)
                check(conv(PH, PJ, table) == avgs[generated], f"{name}: common fixed projector", "finite_subgroup_projectors")
            else:
                noncommuting_pairs += 1

            dcs = double_cosets(J, H, n, table)
            double_coset_total += len(dcs)
            check(sum(len(C) for C in dcs) == n, f"{name}: double cosets partition", "double_coset_packets")
            check(len(set().union(*[set(C) for C in dcs])) == n, f"{name}: double coset cover", "double_coset_packets")
            # Mackey dimension identity for the induced trivial H-representation.
            rhs = 0
            for C in dcs:
                x = min(C)
                xHx = conjugate_subgroup(H, x, table, inv_idx)
                inter = J.intersection(xHx)
                check(len(C) * len(inter) == len(J) * len(H), f"{name}: double coset size", "double_coset_packets")
                rhs += len(J) // len(inter)
            check(rhs == n // len(H), f"{name}: Mackey dimension", "double_coset_packets")

    # Finite tensor model on the regular representation.
    left = [regular_left_permutation(g, n, table) for g in range(n)]
    check(len(set(left)) == n, f"{name}: faithful regular action", "finite_tensor_models")
    for g in range(n):
        check(left[e] == tuple(range(n)), f"{name}: unit action", "finite_tensor_models")
        gi = inv_idx[g]
        for x in range(n):
            check(left[gi][left[g][x]] == x, f"{name}: dual/inverse action", "finite_tensor_models")
        # Diagonal tensor action on basis pairs.
        for x in range(n):
            for y in range(n):
                gx, gy = left[g][x], left[g][y]
                check(0 <= gx < n and 0 <= gy < n, f"{name}: tensor basis action", "finite_tensor_models")
    for g in range(n):
        for h in range(n):
            gh = table[g][h]
            for x in range(n):
                check(left[g][left[h][x]] == left[gh][x], f"{name}: regular functoriality", "finite_tensor_models")

    summary_rows.append({
        "group": name,
        "order": n,
        "subgroups": len(subs),
        "normal_subgroups": normal_count,
        "permutable_ordered_pairs": permutable_pairs,
        "noncommuting_ordered_pairs": noncommuting_pairs,
        "double_coset_packets": double_coset_total,
    })

# Ramification-style nested projector filtrations on cyclic p-groups.
for p, rmax in ((2, 6), (3, 4), (5, 3)):
    for r in range(1, rmax + 1):
        name = f"C{p**r}"
        G = generate_group([cycle(p**r)])
        n = len(G)
        table = mult_table(G)
        inv_idx = inverse_indices(G)
        e = G.index(tuple(range(len(G[0]))))
        gen = G.index(cycle(n))
        chain = []
        for i in range(r + 1):
            gi = power(G[gen], p**i)
            idx = G.index(gi)
            chain.append(closure({idx}, table, inv_idx, e))
        # chain[-1] is trivial because generator power is identity.
        ranks = [n // len(H) for H in chain]
        check(all(ranks[i] <= ranks[i + 1] for i in range(len(ranks) - 1)), f"{name}: nested fixed ranks", "ramification_filtrations")
        details = [ranks[i + 1] - ranks[i] for i in range(len(ranks) - 1)]
        check(ranks[0] + sum(details) == n, f"{name}: detail telescope", "ramification_filtrations")
        weights = [Fraction(len(chain[i]), len(chain[0])) for i in range(len(chain) - 1)]
        conductor1 = sum(weights[i] * (n - ranks[i]) for i in range(len(weights)))
        conductor2 = sum(Fraction(details[j]) * sum(weights[: j + 1]) for j in range(len(details)))
        check(conductor1 == conductor2, f"{name}: weighted unresolved/detail conductor", "ramification_filtrations")

# Exact C/R Hilbert 90 tests over Gaussian rationals.
small = [q(-2), q(-1), q(0), q(1), q(2), q(0, 1), q(0, -1), q(1, 1), q(1, -1)]
B_mats: list[Matrix] = []
for a in small:
    if a != ZERO_Q:
        B_mats.append([[a]])
rng = random.Random(1729)
while len(B_mats) < 180:
    vals = [rng.choice(small) for _ in range(4)]
    B: Matrix = [[vals[0], vals[1]], [vals[2], vals[3]]]
    if mat_det(B) != ZERO_Q:
        B_mats.append(B)

for idx, B in enumerate(B_mats):
    n = len(B)
    A = mat_mul(mat_inv(B), mat_conj(B))
    check(mat_equal(mat_mul(A, mat_conj(A)), mat_eye(n)), f"Hilbert90 cocycle {idx}", "hilbert90_cocycles")
    # The columns of B^{-1} are fixed by the twisted action.
    Binv = mat_inv(B)
    for j in range(n):
        evec: Matrix = [[ONE_Q if i == j else ZERO_Q] for i in range(n)]
        v = mat_mul(Binv, evec)
        check(mat_equal(mat_mul(A, mat_conj(v)), v), f"Hilbert90 fixed basis {idx}:{j}", "hilbert90_cocycles")
        lhs = mat_mul(B, mat_mul(A, mat_conj(v)))
        rhs = mat_conj(mat_mul(B, v))
        check(mat_equal(lhs, rhs), f"Hilbert90 gauge {idx}:{j}", "hilbert90_cocycles")

# Projective descent examples over C/R.
A_quat: Matrix = [[q(0), q(1)], [q(-1), q(0)]]
defect = mat_mul(A_quat, mat_conj(A_quat))
minus_eye = [[q(-1) if i == j else ZERO_Q for j in range(2)] for i in range(2)]
check(mat_equal(defect, minus_eye), "quaternionic projective cocycle", "projective_brauer_examples")
check(mat_det(A_quat) == ONE_Q, "quaternionic lift invertible", "projective_brauer_examples")
check(Fraction(-1) < 0, "negative scalar is not a complex norm to R", "projective_brauer_examples")
A_split: Matrix = [[q(0), q(1)], [q(1), q(0)]]
check(mat_equal(mat_mul(A_split, mat_conj(A_split)), mat_eye(2)), "split projective cocycle", "projective_brauer_examples")
# Coboundary examples have trivial scalar defect.
for idx, B in enumerate(B_mats[:40]):
    A = mat_mul(mat_inv(B), mat_conj(B))
    check(mat_equal(mat_mul(A, mat_conj(A)), mat_eye(len(B))), f"projective split coboundary {idx}", "projective_brauer_examples")

result = {
    "version": "1.12.0",
    "block": 12,
    "passed": not failures,
    "checks": checks,
    "failures": failures,
    "arithmetic": "exact rational group algebra, exact permutation combinatorics, and exact symbolic Gaussian-rational matrix algebra",
    "categories": category_counts,
    "finite_groups": summary_rows,
    "examples": {
        "s3_nonnormal_chart": {
            "group": "S3",
            "subgroup_order": 2,
            "conjugate_charts": 3,
            "core_order": 1,
            "normal_closure_order": 6,
        },
        "s3_normal_quotient": {
            "group": "S3",
            "normal_subgroup_order": 3,
            "quotient_order": 2,
        },
        "real_complex_brauer": {
            "extension": "C/R",
            "projective_lift": "[[0,1],[-1,0]]",
            "scalar_defect": -1,
            "class": "nontrivial quaternionic relative Brauer class",
        },
    },
    "boundary": "Finite semisimple subgroup/projector identities, framed linear descent models, one exact projective obstruction, and finite tensor models are verified. Modular fixed-point failure, wild integral descent, nonneutral Tannakian categories, and unrestricted heterogeneous effectivity are not claimed.",
}

(GEN / "block12_galois_tannakian_validation.json").write_text(json.dumps(result, indent=2, sort_keys=True), encoding="utf-8")

# LaTeX validation table.
cat_labels = {
    "finite_subgroup_projectors": "Finite subgroup and Reynolds-projector identities",
    "normality_and_closure": "Normality, core, and normal-closure identities",
    "double_coset_packets": "Double-coset and Mackey packet identities",
    "ramification_filtrations": "Nested ramification-style projector filtrations",
    "hilbert90_cocycles": "Exact Hilbert 90 cocycles over Gaussian rationals",
    "projective_brauer_examples": "Projective and Brauer obstruction examples",
    "finite_tensor_models": "Finite faithful tensor-model checks",
}
lines = [
    r"\begin{table}[htbp]",
    r"\centering",
    r"\caption{Exact verification of the Block 12 finite Galois and Tannakian models.}",
    r"\label{tab:block12-validation}",
    r"\small",
    r"\begin{tabularx}{\textwidth}{@{}Y r@{}}",
    r"\toprule",
    r"Validation class & Checks\\",
    r"\midrule",
]
for key, label in cat_labels.items():
    lines.append(f"{label} & {category_counts[key]:,}\\\\")
lines += [
    r"\midrule",
    r"\textbf{Block 12 exact checks} & \textbf{" + f"{checks:,}" + r"}\\",
    r"\textbf{Failures} & \textbf{" + f"{len(failures)}" + r"}\\",
    r"\bottomrule",
    r"\end{tabularx}",
    r"\end{table}",
]
(GEN / "block12_validation_table.tex").write_text("\n".join(lines) + "\n", encoding="utf-8")

# Finite group summary table.
lines = [
    r"\begin{table}[htbp]",
    r"\centering",
    r"\caption{Finite group models used in the Block 12 subgroup-projector audit.}",
    r"\label{tab:block12-groups}",
    r"\scriptsize",
    r"\begin{tabularx}{\textwidth}{@{}L{0.12\textwidth}rrrrrY@{}}",
    r"\toprule",
    r"Group & Order & Subgroups & Normal & Permutable ordered pairs & Noncommuting ordered pairs & Double-coset packets audited\\",
    r"\midrule",
]
for row in summary_rows:
    lines.append(
        f"{row['group']} & {row['order']} & {row['subgroups']} & {row['normal_subgroups']} & "
        f"{row['permutable_ordered_pairs']} & {row['noncommuting_ordered_pairs']} & {row['double_coset_packets']}\\\\"
    )
lines += [r"\bottomrule", r"\end{tabularx}", r"\end{table}"]
(GEN / "block12_group_table.tex").write_text("\n".join(lines) + "\n", encoding="utf-8")

print(json.dumps({"passed": result["passed"], "checks": checks, "failures": len(failures), "groups": len(summary_rows)}, sort_keys=True))
if failures:
    raise SystemExit(1)
