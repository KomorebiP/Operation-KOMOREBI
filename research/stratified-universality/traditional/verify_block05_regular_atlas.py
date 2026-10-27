from __future__ import annotations

from collections import Counter, deque
from dataclasses import dataclass
from fractions import Fraction
from itertools import product
from math import comb
from pathlib import Path
import json

import sympy as sp

ROOT = Path(__file__).resolve().parent
GEN = ROOT / "generated"
GEN.mkdir(parents=True, exist_ok=True)
OUT = GEN / "block05_regular_atlas_validation.json"


def inv_mod(a: int, p: int) -> int:
    a %= p
    if a == 0:
        raise ZeroDivisionError("zero has no inverse")
    return pow(a, p - 2, p)


def rref_mod(rows: list[list[int]], p: int) -> list[list[int]]:
    if not rows:
        return []
    n = len(rows[0])
    M = [[x % p for x in row] for row in rows if any(x % p for x in row)]
    if not M:
        return []
    r = 0
    for c in range(n):
        pivot = next((i for i in range(r, len(M)) if M[i][c] % p), None)
        if pivot is None:
            continue
        M[r], M[pivot] = M[pivot], M[r]
        z = inv_mod(M[r][c], p)
        M[r] = [(z * x) % p for x in M[r]]
        for i in range(len(M)):
            if i != r and M[i][c] % p:
                f = M[i][c] % p
                M[i] = [(M[i][j] - f * M[r][j]) % p for j in range(n)]
        r += 1
        if r == len(M):
            break
    M = [row for row in M if any(row)]
    M.sort(key=lambda row: next(i for i, x in enumerate(row) if x))
    return M


def rank_mod(rows: list[list[int]], p: int) -> int:
    return len(rref_mod(rows, p))


def mat_vec_mod(A: list[list[int]], x: tuple[int, ...], p: int) -> tuple[int, ...]:
    return tuple(sum(A[i][j] * x[j] for j in range(len(x))) % p for i in range(len(A)))


def row_dot_mod(row: tuple[int, ...] | list[int], x: tuple[int, ...], p: int) -> int:
    return sum(a * b for a, b in zip(row, x)) % p


def invert_matrix_mod(A: list[list[int]], p: int) -> list[list[int]]:
    n = len(A)
    if n == 0:
        return []
    M = [[A[i][j] % p for j in range(n)] + [1 if i == j else 0 for j in range(n)] for i in range(n)]
    r = 0
    for c in range(n):
        pivot = next((i for i in range(r, n) if M[i][c] % p), None)
        if pivot is None:
            raise ValueError("singular matrix")
        M[r], M[pivot] = M[pivot], M[r]
        z = inv_mod(M[r][c], p)
        M[r] = [(z * x) % p for x in M[r]]
        for i in range(n):
            if i != r and M[i][c] % p:
                f = M[i][c]
                M[i] = [(M[i][j] - f * M[r][j]) % p for j in range(2 * n)]
        r += 1
    return [row[n:] for row in M]


def matmul_mod(A: list[list[int]], B: list[list[int]], p: int) -> list[list[int]]:
    if not A:
        return []
    if not B:
        return [[] for _ in A]
    m, t, n = len(A), len(B), len(B[0])
    return [[sum(A[i][h] * B[h][j] for h in range(t)) % p for j in range(n)] for i in range(m)]


def column(M: list[list[int]], j: int) -> tuple[int, ...]:
    return tuple(row[j] for row in M)


def independent_column_indices(M: list[list[int]], p: int) -> list[int]:
    if not M:
        return []
    r = len(M)
    indices: list[int] = []
    cols: list[list[int]] = []
    for j in range(len(M[0])):
        candidate = cols + [[M[i][j] for i in range(r)]]
        if rank_mod([list(v) for v in candidate], p) > len(cols):
            indices.append(j)
            cols.append([M[i][j] for i in range(r)])
            if len(indices) == r:
                break
    if len(indices) != r:
        raise AssertionError("columns do not span row-space dual")
    return indices


def words_upto(k: int, max_length: int) -> list[tuple[int, ...]]:
    out: list[tuple[int, ...]] = [()]
    for ell in range(1, max_length + 1):
        out.extend(tuple(w) for w in product(range(k), repeat=ell))
    return out


def digits_lsd(n: int, k: int) -> tuple[int, ...]:
    if n == 0:
        return ()
    out = []
    while n:
        out.append(n % k)
        n //= k
    return tuple(out)


@dataclass(frozen=True)
class Automaton:
    k: int
    p: int
    delta: tuple[tuple[int, ...], ...]
    output: tuple[int, ...]
    initial: int = 0

    @property
    def states(self) -> int:
        return len(self.delta)

    def step_word(self, state: int, word: tuple[int, ...]) -> int:
        for d in word:
            state = self.delta[state][d]
        return state

    def value_word(self, word: tuple[int, ...]) -> int:
        return self.output[self.step_word(self.initial, word)] % self.p

    def value_n(self, n: int) -> int:
        return self.value_word(digits_lsd(n, self.k))


def reachable_states(auto: Automaton) -> list[int]:
    seen = {auto.initial}
    q = deque([auto.initial])
    while q:
        s = q.popleft()
        for d in range(auto.k):
            t = auto.delta[s][d]
            if t not in seen:
                seen.add(t)
                q.append(t)
    return sorted(seen)


def minimize_automaton(auto: Automaton) -> Automaton:
    reach = reachable_states(auto)
    idx = {q: i for i, q in enumerate(reach)}
    delta = tuple(tuple(idx[auto.delta[q][d]] for d in range(auto.k)) for q in reach)
    output = tuple(auto.output[q] % auto.p for q in reach)
    initial = idx[auto.initial]
    n = len(reach)

    blocks: list[list[int]] = []
    by_output: dict[int, list[int]] = {}
    for q, y in enumerate(output):
        by_output.setdefault(y, []).append(q)
    blocks = [by_output[y] for y in sorted(by_output)]

    while True:
        block_of = {}
        for bi, block in enumerate(blocks):
            for q in block:
                block_of[q] = bi
        refined: list[list[int]] = []
        changed = False
        for block in blocks:
            groups: dict[tuple[int, ...], list[int]] = {}
            for q in block:
                sig = (output[q],) + tuple(block_of[delta[q][d]] for d in range(auto.k))
                groups.setdefault(sig, []).append(q)
            if len(groups) > 1:
                changed = True
            refined.extend(groups[sig] for sig in sorted(groups))
        blocks = refined
        if not changed:
            break

    block_of = {}
    for bi, block in enumerate(blocks):
        for q in block:
            block_of[q] = bi
    qdelta = tuple(tuple(block_of[delta[block[0]][d]] for d in range(auto.k)) for block in blocks)
    qoutput = tuple(output[block[0]] for block in blocks)
    qinitial = block_of[initial]

    # Canonical BFS renumbering from the initial state, digits in increasing order.
    order = []
    seen = {qinitial}
    queue = deque([qinitial])
    while queue:
        q = queue.popleft()
        order.append(q)
        for d in range(auto.k):
            t = qdelta[q][d]
            if t not in seen:
                seen.add(t)
                queue.append(t)
    ren = {q: i for i, q in enumerate(order)}
    cdelta = tuple(tuple(ren[qdelta[q][d]] for d in range(auto.k)) for q in order)
    coutput = tuple(qoutput[q] for q in order)
    return Automaton(auto.k, auto.p, cdelta, coutput, 0)


def row_after_digit(row: list[int], auto: Automaton, d: int) -> list[int]:
    return [row[auto.delta[q][d]] % auto.p for q in range(auto.states)]


def observability_basis(auto: Automaton) -> list[list[int]]:
    basis = rref_mod([list(auto.output)], auto.p)
    while True:
        candidates = [row[:] for row in basis]
        for row in basis:
            for d in range(auto.k):
                candidates.append(row_after_digit(row, auto, d))
        new_basis = rref_mod(candidates, auto.p)
        if len(new_basis) == len(basis):
            return new_basis
        basis = new_basis


def canonical_linear_quotient(auto: Automaton) -> dict:
    O = observability_basis(auto)
    r = len(O)
    coords_raw = [column(O, q) for q in range(auto.states)] if r else [tuple() for _ in range(auto.states)]
    if r == 0:
        matrices = [[[] for _ in range(0)] for _ in range(auto.k)]
        return {
            "rank": 0,
            "state_coords": coords_raw,
            "basis_states": [],
            "matrices": matrices,
            "initial": tuple(),
            "output": tuple(),
        }

    basis_states = independent_column_indices(O, auto.p)
    B = [[O[i][q] for q in basis_states] for i in range(r)]
    B_inv = invert_matrix_mod(B, auto.p)
    coords = [tuple(mat_vec_mod(B_inv, c, auto.p)) for c in coords_raw]

    matrices: list[list[list[int]]] = []
    for d in range(auto.k):
        # The j-th basis column maps to the coordinate of delta(basis_state_j,d).
        A = [[0] * r for _ in range(r)]
        for j, q in enumerate(basis_states):
            target = coords[auto.delta[q][d]]
            for i in range(r):
                A[i][j] = target[i]
        matrices.append(A)

    out = tuple(auto.output[q] % auto.p for q in basis_states)
    initial = coords[auto.initial]
    return {
        "rank": r,
        "state_coords": coords,
        "basis_states": basis_states,
        "matrices": matrices,
        "initial": initial,
        "output": out,
    }


def simulate_linear(rep: dict, word: tuple[int, ...], p: int) -> int:
    x = rep["initial"]
    if rep["rank"] == 0:
        return 0
    for d in word:
        x = mat_vec_mod(rep["matrices"][d], x, p)
    return row_dot_mod(rep["output"], x, p)


def hankel_rank(auto: Automaton, max_length: int) -> int:
    words = words_upto(auto.k, max_length)
    H = [[auto.value_word(u + v) for v in words] for u in words]
    return rank_mod(H, auto.p)


@dataclass
class Ledger:
    checks: int = 0
    failures: list[dict] | None = None

    def __post_init__(self) -> None:
        if self.failures is None:
            self.failures = []

    def check(self, condition: bool, label: str, context: dict) -> None:
        self.checks += 1
        if not condition:
            self.failures.append({"label": label, "context": context})


def validate_minimal_automaton(auto: Automaton, ledger: Ledger) -> dict:
    auto = minimize_automaton(auto)
    ctx = {"k": auto.k, "p": auto.p, "states": auto.states, "delta": auto.delta, "output": auto.output}
    ledger.check(len(reachable_states(auto)) == auto.states, "minimal automaton reachable", ctx)

    rep = canonical_linear_quotient(auto)
    r = rep["rank"]
    kappa = auto.states
    coords = rep["state_coords"]
    ledger.check(len(set(coords)) == kappa, "minimal automaton behavior vectors distinct", {**ctx, "rank": r, "coords": coords})
    ledger.check(r <= kappa, "regular rank at most automatic states", {**ctx, "rank": r})
    ledger.check(kappa <= auto.p ** r, "finite-field orbit bound", {**ctx, "rank": r})

    # Transition equivariance of the quotient state embedding.
    for q in range(kappa):
        for d in range(auto.k):
            lhs = mat_vec_mod(rep["matrices"][d], coords[q], auto.p) if r else tuple()
            rhs = coords[auto.delta[q][d]]
            ledger.check(lhs == rhs, "state embedding transition equivariance", {**ctx, "q": q, "digit": d, "lhs": lhs, "rhs": rhs})
        y = row_dot_mod(rep["output"], coords[q], auto.p) if r else 0
        ledger.check(y == auto.output[q] % auto.p, "state embedding output preservation", {**ctx, "q": q, "linear_output": y})

    # Word semantics and leading-zero consistency.
    for n in range(96):
        w = digits_lsd(n, auto.k)
        ledger.check(simulate_linear(rep, w, auto.p) == auto.value_n(n), "linear quotient coefficient semantics", {**ctx, "n": n, "word": w})
        ledger.check(auto.value_word(w + (0,)) == auto.value_word(w), "leading-zero consistency", {**ctx, "n": n, "word": w})

    # The finite word Hankel matrix stabilizes by the number of minimal states.
    hr = hankel_rank(auto, max_length=max(1, auto.states))
    ledger.check(hr == r, "word Hankel rank equals regular rank", {**ctx, "hankel_rank": hr, "rank": r})

    # The orbit in the quotient is precisely the minimal state set.
    seen = {rep["initial"]}
    queue = deque([rep["initial"]])
    while queue:
        x = queue.popleft()
        for d in range(auto.k):
            y = mat_vec_mod(rep["matrices"][d], x, auto.p) if r else tuple()
            if y not in seen:
                seen.add(y)
                queue.append(y)
    ledger.check(seen == set(coords), "linear orbit equals minimal automaton state set", {**ctx, "orbit": sorted(seen), "coords": sorted(set(coords))})

    return {
        "k": auto.k,
        "p": auto.p,
        "states": kappa,
        "rank": r,
        "rank_drop": kappa - r,
        "delta": [list(row) for row in auto.delta],
        "output": list(auto.output),
    }


def enumerate_automata(k: int, p: int, max_states: int, ledger: Ledger) -> dict:
    unique: dict[tuple, Automaton] = {}
    raw = 0
    admissible_raw = 0
    for s in range(1, max_states + 1):
        for flat_delta in product(range(s), repeat=s * k):
            delta = tuple(tuple(flat_delta[q * k + d] for d in range(k)) for q in range(s))
            for output in product(range(p), repeat=s):
                raw += 1
                m = minimize_automaton(Automaton(k, p, delta, tuple(output), 0))
                # LSD-first integer semantics require that a terminal high zero
                # does not change the output of any reachable residual state.
                if any(m.output[m.delta[q][0]] != m.output[q] for q in range(m.states)):
                    continue
                admissible_raw += 1
                key = (m.delta, m.output)
                unique[key] = m
    records = [validate_minimal_automaton(a, ledger) for a in unique.values()]
    dist = Counter((r["rank"], r["states"]) for r in records)
    return {
        "k": k,
        "p": p,
        "max_raw_states": max_states,
        "raw_automata": raw,
        "admissible_raw_automata": admissible_raw,
        "unique_minimal_automata": len(records),
        "strict_rank_drop": sum(1 for r in records if r["rank_drop"] > 0),
        "rank_equal": sum(1 for r in records if r["rank_drop"] == 0),
        "distribution": {f"r{r}_s{s}": c for (r, s), c in sorted(dist.items())},
        "records": records,
    }


def polynomial_transition_matrix(k: int, d: int, m: int) -> sp.Matrix:
    # Basis is (1,n,...,n^m), columns are images of n^j under n -> kn+d.
    A = sp.zeros(m + 1, m + 1)
    for j in range(m + 1):
        for ell in range(j + 1):
            A[ell, j] = comb(j, ell) * (k ** ell) * (d ** (j - ell))
    return A


def simulate_sympy(mats: list[sp.Matrix], initial: sp.Matrix, output: sp.Matrix, n: int, k: int) -> int:
    x = initial
    for d in digits_lsd(n, k):
        x = mats[d] * x
    return int((output * x)[0])


def validate_polynomial_and_affine_examples(ledger: Ledger) -> dict:
    polynomial_records = []
    for k in (2, 3):
        for m in range(0, 7):
            mats = [polynomial_transition_matrix(k, d, m) for d in range(k)]
            initial = sp.zeros(m + 1, 1)
            initial[m, 0] = 1
            output = sp.zeros(1, m + 1)
            output[0, 0] = 1
            for n in range(120):
                ledger.check(simulate_sympy(mats, initial, output, n, k) == n ** m,
                             "polynomial digit-linear semantics", {"k": k, "m": m, "n": n})
            ell = 0
            while k ** ell <= m:
                ell += 1
            coeff_rows = []
            for r in range(m + 1):
                poly = sp.Poly((k ** ell * sp.Symbol('x') + r) ** m, sp.Symbol('x'))
                coeff_rows.append([poly.nth(j) for j in range(m + 1)])
            section_rank = sp.Matrix(coeff_rows).rank()
            ledger.check(section_rank == m + 1, "polynomial section rank", {"k": k, "m": m, "section_rank": section_rank})
            polynomial_records.append({"k": k, "degree": m, "rank": m + 1})

    digit_sum_records = []
    for k in (2, 3, 4):
        mats = []
        for d in range(k):
            mats.append(sp.Matrix([[1, d], [0, 1]]))  # basis (1,s_k), columns are images
        initial = sp.Matrix([0, 1])
        output = sp.Matrix([[1, 0]])

        def digit_sum(n: int) -> int:
            s = 0
            while n:
                s += n % k
                n //= k
            return s

        for n in range(240):
            ledger.check(simulate_sympy(mats, initial, output, n, k) == digit_sum(n),
                         "digit-sum linear semantics", {"k": k, "n": n})
        growth = []
        for ell in range(1, 9):
            constants = {digit_sum(r) for r in range(k ** ell)}
            expected = (k - 1) * ell + 1
            ledger.check(len(constants) == expected, "digit-sum kernel orbit growth", {"k": k, "length": ell, "count": len(constants), "expected": expected})
            growth.append(len(constants))
        digit_sum_records.append({"k": k, "rank": 2, "kernel_counts_by_length": growth})

    return {"polynomial_sequences": polynomial_records, "digit_sum_sequences": digit_sum_records}


def named_examples(ledger: Ledger) -> dict:
    examples: dict[str, dict] = {}

    # Ternary Cantor-digit indicator: digits 0 or 1 remain alive, digit 2 enters the zero state.
    cantor = minimize_automaton(Automaton(3, 3, ((0, 0, 1), (1, 1, 1)), (1, 0), 0))
    rec = validate_minimal_automaton(cantor, ledger)
    examples["cantor_indicator_F3"] = {**rec, "label": "Ternary Cantor-digit indicator", "automatic": True, "regular_nonautomatic": False}

    # Thue-Morse parity over F_2.
    tm = minimize_automaton(Automaton(2, 2, ((0, 1), (1, 0)), (0, 1), 0))
    rec = validate_minimal_automaton(tm, ledger)
    examples["thue_morse_F2"] = {**rec, "label": "Thue-Morse parity", "automatic": True, "regular_nonautomatic": False}

    examples["identity_Q"] = {"label": "Identity sequence $n$", "k": 2, "field": "Q", "rank": 2, "kernel": "infinite", "automatic": False, "regular_nonautomatic": True}
    examples["binary_digit_sum_Q"] = {"label": "Binary digit sum $s_2(n)$", "k": 2, "field": "Q", "rank": 2, "kernel": "infinite", "automatic": False, "regular_nonautomatic": True}
    examples["square_Q"] = {"label": "Square sequence $n^2$", "k": 2, "field": "Q", "rank": 3, "kernel": "infinite", "automatic": False, "regular_nonautomatic": True}
    return examples


def write_tex_tables(summary: dict) -> None:
    cfgs = summary["automata_enumeration"]
    lines = [
        r'\begin{table}[htbp]',
        r'\centering',
        r'\caption{Exact finite validation of the Block 05 fixed-radix regular atlas.}',
        r'\label{tab:block05-validation}',
        r'\small',
        r'\begin{tabularx}{\textwidth}{@{}L{0.27\textwidth}Y@{}}',
        r'\toprule',
        r'Check & Recorded result\\',
        r'\midrule',
    ]
    enum_parts = []
    for c in cfgs:
        enum_parts.append(
            f"base {c['k']} over $\\mathbb F_{c['p']}$ through {c['max_raw_states']} raw states: "
            f"{c['raw_automata']:,} raw candidates, {c['admissible_raw_automata']:,} leading-zero-consistent candidates, "
            f"{c['unique_minimal_automata']:,} distinct minimized automata"
        )
    lines.append("Exhaustive finite-state enumeration & " + "; ".join(enum_parts) + r'.\\')
    lines.append(
        f"Automatic-to-linear checks & {summary['automata_checks']:,} exact checks; "
        f"{summary['strict_rank_drop_total']:,} minimized automata with strict state-to-rank compression.\\\\"
    )
    lines.append(
        f"Unbounded regular examples & Polynomial sequences $n^m$ for bases 2 and 3 through degree 6, "
        f"plus digit sums in bases 2, 3, and 4; {summary['example_checks']:,} exact checks.\\\\"
    )
    lines.append(f"Combined Block 05 checks & {summary['checks']:,} checks; {len(summary['failures'])} failures.\\\\")
    lines.append(f"Overall status & {'PASS' if summary['passed'] else 'FAIL'}.\\\\")
    lines.append(r'Boundary & The computation validates the bounded automata and named exact examples. It does not prove an all-radix, all-ring, semiring, or all-moduli minimality theorem.\\')
    lines += [r'\bottomrule', r'\end{tabularx}', r'\end{table}']
    (GEN / "block05_validation_table.tex").write_text("\n".join(lines) + "\n", encoding="utf-8")

    ex = summary["named_examples"]
    order = ["cantor_indicator_F3", "thue_morse_F2", "identity_Q", "binary_digit_sum_Q", "square_Q"]
    lines = [
        r'\begin{table}[htbp]',
        r'\centering',
        r'\caption{Named examples at the automatic--regular boundary.}',
        r'\label{tab:block05-examples}',
        r'\small',
        r'\begin{tabularx}{\textwidth}{@{}L{0.25\textwidth}L{0.13\textwidth}L{0.11\textwidth}L{0.13\textwidth}Y@{}}',
        r'\toprule',
        r'Example & Base / field & Regular rank & Kernel or states & Classification\\',
        r'\midrule',
    ]
    for key in order:
        row = ex[key]
        if "p" in row:
            bf = f"{row['k']} / $\\mathbb F_{row['p']}$"
            kernel = str(row["states"])
            cls = "automatic and regular"
        else:
            bf = f"{row['k']} / $\\mathbb Q$"
            kernel = row["kernel"]
            cls = "regular, not automatic"
        lines.append(f"{row['label']} & {bf} & {row['rank']} & {kernel} & {cls}\\\\")
    lines += [r'\bottomrule', r'\end{tabularx}', r'\end{table}']
    (GEN / "block05_examples_table.tex").write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    ledger = Ledger()
    configs = []
    checks_before = ledger.checks
    for k, p, s in ((2, 2, 3), (2, 3, 3), (3, 2, 2)):
        configs.append(enumerate_automata(k, p, s, ledger))
    automata_checks = ledger.checks - checks_before

    checks_before = ledger.checks
    examples_structural = validate_polynomial_and_affine_examples(ledger)
    example_checks = ledger.checks - checks_before

    named = named_examples(ledger)

    strict_rank_drop_total = sum(c["strict_rank_drop"] for c in configs)
    unique_total = sum(c["unique_minimal_automata"] for c in configs)
    raw_total = sum(c["raw_automata"] for c in configs)

    summary = {
        "artifact": "Komorebi Stratified Universality Block 05 fixed-radix regular atlas validation",
        "arithmetic": "exact finite-field Gaussian elimination and exact integer/rational symbolic matrices",
        "automata_enumeration": configs,
        "raw_automata_total": raw_total,
        "unique_minimal_automata_total": unique_total,
        "strict_rank_drop_total": strict_rank_drop_total,
        "automata_checks": automata_checks,
        "example_checks": example_checks,
        "structural_examples": examples_structural,
        "named_examples": named,
        "checks": ledger.checks,
        "failures": ledger.failures,
        "passed": not ledger.failures,
    }
    OUT.write_text(json.dumps(summary, indent=2, sort_keys=True), encoding="utf-8")
    write_tex_tables(summary)
    print(f"BLOCK05_REGULAR_ATLAS={'PASS' if summary['passed'] else 'FAIL'}")
    print(f"RAW_AUTOMATA={raw_total}")
    print(f"UNIQUE_MINIMAL_AUTOMATA={unique_total}")
    print(f"STRICT_RANK_DROP={strict_rank_drop_total}")
    print(f"CHECKS={ledger.checks}")
    print(f"FAILURES={len(ledger.failures)}")
    if ledger.failures:
        print(json.dumps(ledger.failures[:10], indent=2))
        raise SystemExit(1)


if __name__ == "__main__":
    main()
