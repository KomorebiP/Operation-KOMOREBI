"""Exact, finite repair-calculus prototype (rational numbers or prime fields).

Research experiment only. Not a replacement for Komorebi's existing library.
All algebra uses Python's Fraction or residues modulo a declared small prime.
No floating-point rank or solve routines are used.
"""
from dataclasses import dataclass
from fractions import Fraction
from itertools import combinations


@dataclass(frozen=True)
class Field:
    p: int | None = None

    def __post_init__(self):
        if self.p is not None:
            if self.p < 2 or any(self.p % k == 0 for k in range(2, int(self.p ** .5) + 1)):
                raise ValueError("p must be a prime")

    def c(self, x):
        if isinstance(x, float):
            raise TypeError("Floating-point values are forbidden in exact repair certificates")
        if self.p is None:
            return Fraction(x)
        if isinstance(x, Fraction):
            return (x.numerator * pow(x.denominator, -1, self.p)) % self.p
        return int(x) % self.p

    def add(self, a, b):
        return self.c(a + b)

    def neg(self, a):
        return self.c(-a)

    def mul(self, a, b):
        return self.c(a * b)

    def inv(self, a):
        a = self.c(a)
        if not a:
            raise ZeroDivisionError("cannot invert 0")
        return Fraction(1, a) if self.p is None else pow(a, -1, self.p)


def matrix_from_columns(n, cols, F):
    if any(len(v) != n for v in cols):
        raise ValueError("Column shape mismatch")
    return [[F.c(col[i]) for col in cols] for i in range(n)]


def colcount(A):
    return len(A[0]) if A else 0


def rref(A, F):
    if A and any(len(row) != len(A[0]) for row in A):
        raise ValueError("Jagged matrix")
    M = [[F.c(z) for z in row] for row in A]
    m = len(M)
    n = colcount(M)
    pivots = []
    row = 0
    for col in range(n):
        k = next((i for i in range(row, m) if M[i][col] != 0), None)
        if k is None:
            continue
        M[row], M[k] = M[k], M[row]
        a = F.inv(M[row][col])
        M[row] = [F.mul(a, x) for x in M[row]]
        for i in range(m):
            if i == row:
                continue
            a = M[i][col]
            if a:
                M[i] = [F.add(x, F.neg(F.mul(a, y))) for x, y in zip(M[i], M[row])]
        pivots.append(col)
        row += 1
        if row == m:
            break
    return M, pivots


def rank_of_columns(n, cols, F):
    return len(rref(matrix_from_columns(n, cols, F), F)[1])


def solve_columns(n, cols, rhs, F):
    if len(rhs) != n:
        raise ValueError("RHS shape mismatch")
    M = matrix_from_columns(n, cols, F)
    Maug = [row + [F.c(rhs[i])] for i, row in enumerate(M)]
    red, pivots = rref(Maug, F)
    nvars = len(cols)
    if nvars in pivots:  # inconsistent augmented column
        return None
    sol = [F.c(0) for _ in range(nvars)]
    for i, j in enumerate(pivots):
        sol[j] = red[i][-1]
    assert matvec_columns(n, cols, sol, F) == [F.c(x) for x in rhs]
    return sol


def matvec_columns(n, cols, x, F):
    if len(cols) != len(x):
        raise ValueError("Coefficient count mismatch")
    return [sum((F.mul(col[i], v) for col, v in zip(cols, x)), F.c(0)) % F.p
            if F.p is not None else sum((F.mul(col[i], v) for col, v in zip(cols, x)), F.c(0))
            for i in range(n)]


def free_obstruction_basis(n, D, residuals, F):
    """Subset of residual columns independent modulo im(D); hence minimal free repair basis."""
    chosen = []
    have = rank_of_columns(n, D, F)
    for i, r in enumerate(residuals):
        now = rank_of_columns(n, D + [residuals[j] for j in chosen] + [r], F)
        if now > have:
            chosen.append(i)
            have = now
    assert len(chosen) == rank_of_columns(n, D + residuals, F) - rank_of_columns(n, D, F)
    return chosen


def feasibility_certificate(n, D, residuals, repair_cols, F):
    """Find correction coefficients for every residual, or return a failure with exact ranks."""
    allcols = D + repair_cols
    ranks = {"base": rank_of_columns(n, D, F),
             "with_repairs": rank_of_columns(n, allcols, F),
             "with_residuals": rank_of_columns(n, allcols + residuals, F)}
    witnesses = []
    for r in residuals:
        w = solve_columns(n, allcols, [F.neg(F.c(x)) for x in r], F)
        if w is None:
            return {"status": "NO_REPAIR_IN_SELECTED_CLASS", "ranks": ranks, "witnesses": None}
        witnesses.append(w)
    assert ranks["with_repairs"] == ranks["with_residuals"]
    return {"status": "EXACT_REPAIR_CERTIFIED", "ranks": ranks, "witnesses": witnesses}


def min_menu_repair(n, D, residuals, candidates, costs, F, allowed=None):
    """Exhaustive *global optimum* for finite menus, minimize (total cost, size, index tuple)."""
    if len(candidates) != len(costs) or any(c < 0 for c in costs):
        raise ValueError("Costs must be nonnegative and one per candidate")
    if allowed is None:
        allowed = [True] * len(candidates)
    if len(allowed) != len(candidates):
        raise ValueError("Allowed mask length mismatch")
    usable = [i for i, yes in enumerate(allowed) if yes]
    best = None
    for k in range(len(usable) + 1):
        for indices in combinations(usable, k):
            c = sum(costs[i] for i in indices)
            key = (c, k, indices)
            if best is not None and key >= best["key"]:
                continue
            cert = feasibility_certificate(n, D, residuals, [candidates[i] for i in indices], F)
            if cert["status"] == "EXACT_REPAIR_CERTIFIED":
                best = {"key": key, "indices": indices, "cost": c, "certificate": cert}
    if best is None:
        return {"status": "NO_REPAIR_IN_ADMISSIBLE_MENU", "indices": [], "tested_subsets": 2 ** len(usable)}
    return {"status": "OPTIMAL_REPAIR_CERTIFIED_BY_EXHAUSTION", "indices": list(best["indices"]),
            "cost": best["cost"], "certificate": best["certificate"],
            "tested_subsets": 2 ** len(usable)}


def admissible_under_conservation(candidates, conserved_rows, F):
    """Permit only columns annihilated by all conserved linear functionals."""
    return [all(F.c(sum(F.mul(a, b) for a, b in zip(ell, e))) == 0 for ell in conserved_rows)
            for e in candidates]


def product(A, B, F):
    if not A or not B or len(A[0]) != len(B):
        raise ValueError("Invalid matrix multiplication shapes")
    return [[F.c(sum(F.mul(A[i][k], B[k][j]) for k in range(len(B))))
             for j in range(len(B[0]))] for i in range(len(A))]


def scalar(A, s, F):
    return [[F.mul(s, a) for a in row] for row in A]


def inverse(A, F):
    n = len(A)
    if any(len(row) != n for row in A):
        raise ValueError("Square matrix expected")
    cols = [[F.c(A[i][j]) for i in range(n)] for j in range(n)]
    basis = [[F.c(int(i == j)) for i in range(n)] for j in range(n)]
    xcols = [solve_columns(n, cols, b, F) for b in basis]
    if any(x is None for x in xcols):
        return None
    return matrix_from_columns(n, xcols, F)


def eye(n, F):
    return [[F.c(int(i == j)) for j in range(n)] for i in range(n)]


def check_triangle_gluing(A01, A12, A02, B01, B12, B02, U0, F):
    """Tree path 0->1->2, and chord 0->2: fixed-root intertwining test."""
    U1 = product(product(B01, U0, F), inverse(A01, F), F)
    U2 = product(product(B12, U1, F), inverse(A12, F), F)
    left = product(U2, A02, F)
    right = product(B02, U0, F)
    assert product(U1, A01, F) == product(B01, U0, F)
    assert product(U2, A12, F) == product(B12, U1, F)
    Aloop = product(product(inverse(A02, F), A12, F), A01, F)
    Bloop = product(product(inverse(B02, F), B12, F), B01, F)
    holonomy_agree = product(U0, Aloop, F) == product(Bloop, U0, F)
    assert (left == right) == holonomy_agree
    return {"status": "GLUING_CERTIFIED" if holonomy_agree else "HOLONOMY_OBSTRUCTION",
            "U1": U1, "U2": U2, "chord_left": left, "chord_right": right,
            "holonomy_A": Aloop, "holonomy_B": Bloop}
