#!/usr/bin/env python3
"""Exact finite examples for the six Operator guide reference chapters.

Uses only Python's standard library. These checks cover specified rational
matrices and finite witnesses. They do not certify general theorems,
infinite-dimensional convergence, or theorem-to-Lean correspondence.
"""
from fractions import Fraction as F
import json


def M(rows):
    return tuple(tuple(F(x) for x in row) for row in rows)


def v(*values):
    return M([[x] for x in values])


def eye(n):
    return M([[int(i == j) for j in range(n)] for i in range(n)])


def zero(rows, cols):
    return M([[0] * cols for _ in range(rows)])


def mm(a, b):
    assert len(a[0]) == len(b)
    return tuple(tuple(sum(x * y for x, y in zip(row, col)) for col in zip(*b))
                 for row in a)


def add(a, b):
    assert len(a) == len(b) and len(a[0]) == len(b[0])
    return tuple(tuple(x + y for x, y in zip(r, s)) for r, s in zip(a, b))


def scale(c, a):
    return tuple(tuple(c * x for x in row) for row in a)


def sub(a, b):
    return add(a, scale(-1, b))


def transpose(a):
    return tuple(zip(*a))


def inverse2(a):
    det = a[0][0] * a[1][1] - a[0][1] * a[1][0]
    assert det
    return scale(1 / det, M([[a[1][1], -a[0][1]], [-a[1][0], a[0][0]]]))


def rank(a):
    rows = [list(row) for row in a]
    pivot = 0
    for col in range(len(rows[0])):
        found = next((i for i in range(pivot, len(rows)) if rows[i][col]), None)
        if found is None:
            continue
        rows[pivot], rows[found] = rows[found], rows[pivot]
        leading = rows[pivot][col]
        rows[pivot] = [x / leading for x in rows[pivot]]
        for i in range(len(rows)):
            if i != pivot:
                multiple = rows[i][col]
                rows[i] = [x - multiple * y for x, y in zip(rows[i], rows[pivot])]
        pivot += 1
        if pivot == len(rows):
            break
    return pivot


def norm_inf(a):
    return max(sum(abs(x) for x in row) for row in a)


def length_squared(x):
    return sum(row[0] ** 2 for row in x)


def kron(a, b):
    return tuple(tuple(x * y for x in row_a for y in row_b)
                 for row_a in a for row_b in b)


I = eye(2)
T = M([[1, 2], [3, 4]])
P = M([[1, 0], [0, 0]])
Q = sub(I, P)
N = M([[0, 1], [0, 0]])
X = v(2, 3)
A = M([[1, 0], [0, 1], [1, 1]])
S = scale(F(1, 3), M([[2, -1, 1], [-1, 2, 1]]))


def basics():
    R, B = M([[1, 1]]), v(1, 0)
    assert mm(R, B) == eye(1) and mm(B, R) != I
    linear = lambda x: 2 * x[0] - x[1]
    assert linear((5, 7)) == 2 * linear((1, 2)) + 3 * linear((1, 1))
    assert (1 * 0 + 0 * 1) != (1 + 0) * (0 + 1)
    assert mm(T, I) == mm(I, T) == T and mm(zero(2, 2), X) == v(0, 0)
    assert mm(R, v(1, -1)) == v(0) and rank(R) == 1
    assert rank(B) == 1 and len(B) > rank(B)
    BR = mm(B, R)
    assert mm(BR, BR) == BR and mm(BR, v(0, 1)) == v(1, 0)
    D = M([[2, 0], [0, 3]])
    assert mm(D, v(1, 0)) == v(2, 0) and mm(T, v(1, 0)) == v(1, 3)
    W, swap = M([[1, 0], [0, 3]]), M([[0, 1], [1, 0]])
    adjoint = mm(mm(inverse2(W), transpose(swap)), W)
    assert adjoint == M([[0, 3], [F(1, 3), 0]])
    assert mm(transpose(swap), W) == mm(W, adjoint)
    a, b = M([[2, -1]]), v(F(1, 2), 0)
    assert mm(a, b) == eye(1) and mm(b, a) == M([[1, F(-1, 2)], [0, 0]])
    assert mm(a, v(1, 2)) == v(0)
    return ('typed paths', 'linearity controls', 'identity and zero', 'kernel and rank',
            'rectangular map', 'one-sided inverse', 'invariant directions', 'weighted adjoint')


def algebra():
    U = M([[2, 0], [0, 1]])
    assert mm(U, mm(T, X)) == v(16, 18) and mm(T, mm(U, X)) == v(10, 24)
    assert mm(N, N) == zero(2, 2)
    assert mm(add(I, scale(2, N)), sub(I, scale(2, N))) == I
    assert sub(mm(P, T), mm(T, P)) == M([[0, 2], [-3, 0]])
    R, swap = M([[1, 1]]), M([[0, 1], [1, 0]])
    assert mm(R, swap) == R
    C, D = M([[1, 1], [0, 1]]), M([[2, 0], [0, 3]])
    assert mm(mm(C, D), inverse2(C)) == M([[2, 1], [0, 3]])
    assert mm(N, v(0, 1)) == v(1, 0) and mm(N, v(1, 0)) == v(0, 0)
    assert rank(M([[0, 1], [1, 0]])) == 2
    product = kron(D, swap)
    assert product == M([[0, 2, 0, 0], [2, 0, 0, 0], [0, 0, 0, 3], [0, 0, 3, 0]])
    assert mm(product, v(1, 2, 0, 0)) == v(4, 2, 0, 0)
    assert mm(kron(D, swap), kron(C, N)) == kron(mm(D, C), mm(swap, N))
    schur, rhs = F(3) - F(1, 2), F(5) - F(5, 2)
    y = rhs / schur
    x = (5 - y) / 2
    assert (x, y) == (2, 1) and (2 * x + y, x + 3 * y) == (5, 5)
    assert mm(P, N) == N and mm(N, P) == zero(2, 2)
    return ('composition', 'polynomials', 'commutator', 'intertwiner',
            'similarity', 'seeds', 'tensor product', 'Schur complement')


def packets():
    oblique = M([[1, 1], [0, 0]])
    assert mm(oblique, oblique) == oblique and mm(oblique, v(1, -1)) == v(0, 0)
    assert add(P, Q) == I and mm(P, Q) == mm(Q, P) == zero(2, 2)
    assert mm(scale(2, I), scale(2, I)) != scale(2, I)
    first, second = mm(oblique, X), mm(sub(I, oblique), X)
    assert first == v(5, 0) and second == v(-3, 3)
    assert length_squared(first) + length_squared(second) == 43
    assert length_squared(X) == 13
    assert mm(S, A) == I and mm(S, mm(A, X)) == X
    AS = mm(A, S)
    assert mm(AS, AS) == AS and AS != eye(3)
    E = [M([[int(i == j == k) for j in range(3)] for i in range(3)]) for k in range(3)]
    components = [mm(mm(S, e), A) for e in E]
    assert add(add(components[0], components[1]), components[2]) == I
    assert mm(components[0], components[0]) == scale(F(2, 3), components[0])
    assert [mm(c, X) for c in components] == [v(F(4, 3), F(-2, 3)), v(-1, 2), v(F(5, 3), F(5, 3))]
    signal, kept = v(3, 1, 4, 2), v(3, 1, 0, 2)
    assert sub(signal, kept) == v(0, 0, 4, 0)
    triangular = M([[1, 2], [0, 3]])
    assert mm(Q, mm(triangular, P)) == zero(2, 2)
    assert mm(P, mm(triangular, Q)) != zero(2, 2)
    spectral = M([[2, 1], [0, 3]])
    p2, p3 = sub(scale(3, I), spectral), sub(spectral, scale(2, I))
    assert mm(p2, p2) == p2 and mm(p3, p3) == p3
    assert mm(p2, p3) == mm(p3, p2) == zero(2, 2)
    assert add(p2, p3) == I and add(scale(2, p2), scale(3, p3)) == spectral
    assert M([[2, 1], [0, 2]]) != scale(2, I)
    exercise = M([[1, 2], [0, 0]])
    assert mm(exercise, X) == v(8, 0) and mm(sub(I, exercise), X) == v(-6, 3)
    return ('idempotence', 'complete family', 'oblique energy', 'analysis and synthesis',
            'redundant components', 'refinement residual', 'invariance and leakage', 'spectral projectors')


def transfer():
    projectors = (P, Q)
    assert mm(mm(P, T), Q) == M([[0, 2], [0, 0]])
    blocks = [mm(mm(q, T), p) for q in projectors for p in projectors]
    total = zero(2, 2)
    for block in blocks:
        total = add(total, block)
    assert total == T
    U = M([[2, 0], [0, 1]])
    for pk in projectors:
        for pi in projectors:
            routed = zero(2, 2)
            for qj in projectors:
                routed = add(routed, mm(mm(mm(pk, U), qj), mm(mm(qj, T), pi)))
            assert routed == mm(mm(pk, mm(U, T)), pi)
    C, R = M([[1, 1], [0, 1]]), M([[1, 1]])
    transformed = mm(scale(2, R), inverse2(C))
    assert transformed == M([[2, 0]]) and mm(transformed, mm(C, X)) == v(10)
    D, swap = M([[2, 0], [0, 3]]), M([[0, 1], [1, 0]])
    assert mm(R, swap) == R and mm(R, mm(D, v(1, -1))) == v(-1)
    assert mm(mm(R, D), v(1, 0)) == v(2) and mm(R, mm(D, v(0, 1))) == v(3)
    residual = sub(T, mm(mm(P, T), P))
    expanded = add(add(mm(mm(Q, T), P), mm(mm(P, T), Q)), mm(mm(Q, T), Q))
    assert residual == expanded
    assert mm(mm(Q, T), v(2, 0)) == v(0, 6)
    assert F(2 * 3) - F((2 + 3) ** 2, 4) == F(-1, 4)
    assert 2 + 0 == 1 + 1 and 2 * 0 != 1 * 1
    upper = M([[1, 2], [0, 1]])
    assert mm(M([[0, 1]]), upper) == M([[0, 1]])
    assert mm(M([[1, 0]]), mm(upper, v(0, 1))) == v(2)
    return ('source-target block', 'reconstruction', 'intermediate packets', 'rectangular transport',
            'exact and failed closure', 'leakage residual', 'nonlinear defect')


def recovery():
    R = M([[1, 1]])
    assert mm(R, v(2, 3)) == mm(R, v(7, -2)) == v(5)
    domain = [(a, b) for a in range(-2, 3) for b in range(-2, 3)]
    for a, b in domain:
        assert 2 * (a + b) == 2 * a + 2 * b
    assert sum((1, 0)) == sum((0, 1)) and (1, 0)[0] != (0, 1)[0]
    measured = M([[1, 1, 0], [0, 1, 1]])
    target, B = M([[1, 2, 1]]), M([[1, 1]])
    assert mm(B, measured) == target
    w, first = v(1, -1, 1), M([[1, 0, 0]])
    assert mm(measured, w) == v(0, 0) and mm(first, w) == v(1)
    assert rank(M([[1, 1], [1, 0]])) - rank(R) == 1
    assert rank(M([[1, 1], [2, 2]])) - rank(R) == 0
    for a, b in domain:
        assert F((a + b) + (a - b), 2) == a
    for c in (F(0), F(1), F(3, 2), F(2), F(7, 3)):
        risk = F(1, 4) * c ** 2 + F(3, 4) * (2 - c) ** 2
        assert risk == F(3, 4) + (c - F(3, 2)) ** 2
    for u0, hidden in domain:
        sequence = [F(u0 + n * hidden) for n in range(6)]
        assert all(sequence[n + 2] == 2 * sequence[n + 1] - sequence[n] for n in range(4))
    differences = M([[1, -1, 0], [0, 1, -1]])
    assert mm(M([[1, 1]]), differences) == M([[1, 0, -1]])
    assert mm(differences, v(1, 1, 1)) == v(0, 0)
    return ('fibers', 'finite recovery controls', 'row-space rule', 'kernel witness',
            'repair dimension', 'weighted estimation', 'retained memory')


def stability():
    E = M([[0, 2], [3, 0]])
    assert mm(transpose(E), E) == M([[9, 0], [0, 4]])
    assert norm_inf(E) == norm_inf(transpose(E)) == 3
    assert mm(P, Q) == zero(2, 2) and norm_inf(P) * norm_inf(Q) == 1
    assert length_squared(mm(E, X)) == 72 <= 9 * length_squared(X) == 117
    approx, eta = M([[1, 0], [0, 4]]), v(0, F(1, 10))
    assert sub(mm(T, X), mm(approx, add(X, eta))) == sub(mm(E, X), mm(approx, eta))
    C, D = M([[1, 10], [0, 1]]), M([[1, 0], [0, 2]])
    assert norm_inf(C) * norm_inf(inverse2(C)) == 121
    changed = mm(mm(C, D), inverse2(C))
    assert changed == M([[1, 10], [0, 2]]) and norm_inf(changed) == 11
    oblique = M([[1, 10], [0, 0]])
    assert mm(oblique, oblique) == oblique
    assert mm(oblique, transpose(oblique)) == M([[101, 0], [0, 0]])
    high = scale(100, N)
    assert mm(high, high) == zero(2, 2)
    assert mm(high, transpose(high)) != mm(transpose(high), high)
    power = I
    for n in range(9):
        assert power == add(I, scale(n, high))
        power = mm(add(I, high), power)
    # Finite unit-vector witnesses only; the text supplies the l2 convergence argument.
    for m in range(1, 6):
        projection = M([[int(i == j and i < m) for j in range(6)] for i in range(6)])
        omitted = v(*(int(i == m) for i in range(6)))
        assert mm(projection, omitted) == zero(6, 1) and length_squared(omitted) == 1
    system = M([[1, 0], [0, F(1, 1000)]])
    b, exact, candidate = v(1, F(1, 1000)), v(1, 1), v(1, 0)
    r = sub(b, mm(system, candidate))
    assert r == v(0, F(1, 1000))
    assert sub(exact, candidate) == mm(inverse2(system), r) == v(0, 1)
    assert mm(E, v(1, 0)) == v(0, 3) and mm(E, v(0, 1)) == v(2, 0)
    return ('induced norms', 'composition bound control', 'error decomposition', 'conditioning',
            'oblique projector norm', 'nonnormal powers', 'finite truncation witnesses', 'residual and forward error')


CHECKS = {'BASICS': basics, 'ALGEBRA': algebra, 'PACKETS': packets,
          'TRANSFER': transfer, 'RECOVERY': recovery, 'STABILITY': stability}

SOURCE_BINDINGS = {
    'BASICS': r'T^*=\begin{pmatrix}0&3\\1/3&0\end{pmatrix}',
    'ALGEBRA': r'\begin{pmatrix}0&2&0&0\\2&0&0&0\\0&0&0&3\\0&0&3&0\end{pmatrix}',
    'PACKETS': r'C_1^2=\frac23C_1\ne C_1',
    'TRANSFER': r"T'=[2\ \ 0]",
    'RECOVERY': r'F=\begin{pmatrix}1&2&1\end{pmatrix}',
    'STABILITY': r'A=\operatorname{diag}(1,1/1000)',
}


def run_checks():
    groups = {name: list(check()) for name, check in CHECKS.items()}
    return {'result': 'PASS', 'finite_example_groups': sum(map(len, groups.values())),
            'chapters': groups, 'arithmetic': 'exact rational',
            'scope': 'Specified finite examples and failure controls; no general theorem or Lean certification.'}


if __name__ == '__main__':
    print(json.dumps(run_checks(), indent=2))
