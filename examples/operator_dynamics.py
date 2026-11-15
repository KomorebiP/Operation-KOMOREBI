#!/usr/bin/env python3
"""Eight exact finite groups for the stable-update operator study.

Contract: the fixed rational two-state matrix A below, three initial-state
fixtures at n=0,...,16, exact coordinate/energy/resolvent identities, and
every two-coordinate disturbance sign sequence at lengths 0,...,4.
Check scalar recurrences independently of matrix powers. No random sampling,
floating tolerance, physical-model certification or new formal proof.

Run: python -B examples/operator_dynamics.py
Uses only the standard library and sibling guide arithmetic helpers.
Prints JSON; does not write files.
"""
from fractions import Fraction as F
from itertools import product
import json

from operator_guide import M, v, eye, zero, mm, add, sub, scale, transpose


A = M([[F(1, 2), 2], [0, F(1, 2)]])
D = scale(F(1, 2), eye(2))
C = M([[1, 0], [0, 8]])
CI = M([[1, 0], [0, F(1, 8)]])
B = M([[F(1, 2), F(1, 4)], [0, F(1, 2)]])
W = M([[F(4, 3), F(16, 9)], [F(16, 9), F(356, 27)]])
RESOLVENT = M([[2, 8], [0, 2]])
DELTA = F(1, 100)


def power(a, n):
    result = eye(len(a))
    for _ in range(n):
        result = mm(result, a)
    return result


def values(column):
    return tuple(row[0] for row in column)


def norm_inf(a):
    return max(sum(abs(entry) for entry in row) for row in a)


def energy(column):
    return mm(mm(transpose(column), W), column)[0][0]


def run_audit():
    groups = {}
    nmat = sub(A, D)
    assert power(nmat, 2) == zero(2, 2)
    assert mm(transpose(A), A) != mm(A, transpose(A))
    fixtures = ((0, 1), (1, 1), (-2, 3))
    for initial in fixtures:
        u, w = map(F, initial)
        for n in range(17):
            closed = scale(F(1, 2**n), M([[1, 4*n], [0, 1]]))
            assert power(A, n) == closed
            assert values(mm(closed, v(*initial))) == (u, w)
            u, w = u / 2 + 2 * w, w / 2
    states = tuple(values(mm(power(A, n), v(0, 1))) for n in range(6))
    groups['trajectory'] = {'initial_states': fixtures, 'times_checked': [0, 16],
        'states': states, 'euclidean_squared': tuple(sum(x*x for x in state) for state in states)}

    norms = []
    for n in range(17):
        actual = norm_inf(power(A, n))
        assert actual == F(1+4*n, 2**n)
        assert max(abs(x) for x in values(mm(power(A, n), v(1, 1)))) == actual
        norms.append(actual)
    assert max(norms) == F(5, 2) and norms.index(max(norms)) == 1
    groups['transient-gain'] = {'norms': norms, 'maximum_on_tested_times': max(norms), 'attaining_time': 1}

    assert mm(C, CI) == mm(CI, C) == eye(2)
    assert mm(mm(C, A), CI) == B
    assert norm_inf(B) == F(3, 4)
    assert norm_inf(C) * norm_inf(CI) == 8
    for n in range(17):
        assert norm_inf(power(A, n)) <= 8 * F(3, 4)**n
    assert mm(mm(transpose(CI), eye(2)), CI) == M([[1, 0], [0, F(1, 64)]])
    groups['weighted-norm'] = {'C': C, 'B': B, 'contraction': F(3, 4),
        'coordinate_factor': 8, 'one_step_converted_bound': 6}

    assert sub(W, mm(mm(transpose(A), W), A)) == eye(2)
    assert W[0][0] > 0 and W[0][0]*W[1][1] - W[0][1]**2 == F(1168, 81)
    for initial in fixtures:
        x = v(*initial)
        total = F(0)
        for n in range(17):
            u, w = values(x)
            assert energy(x) == F(4, 3)*(u+F(4, 3)*w)**2 + F(292, 27)*w*w
            assert energy(x) + total == energy(v(*initial))
            total += u*u+w*w
            x = mm(A, x)
    energies = tuple(energy(mm(power(A, n), v(0, 1))) for n in range(3))
    # A forced update has cross and disturbance terms, rather than unforced decrease alone.
    x, disturbance = v(0, 1), v(DELTA, -DELTA)
    ax = mm(A, x)
    cross = 2 * mm(mm(transpose(ax), W), disturbance)[0][0]
    assert energy(add(ax, disturbance)) == energy(x)-1+cross+energy(disturbance)
    groups['quadratic-energy'] = {'W': W, 'energies': energies,
        'completed_square_coefficients': (F(4, 3), F(4, 3), F(292, 27)),
        'forced_cross_term': cross, 'forced_disturbance_energy': energy(disturbance)}

    discrepancies = []
    for n in range(17):
        difference = sub(power(A, n), power(D, n))
        assert difference == M([[0, F(4*n, 2**n)], [0, 0]])
        telescoped = zero(2, 2)
        for k in range(n):
            telescoped = add(telescoped, mm(mm(power(A, n-1-k), nmat), power(D, k)))
        assert telescoped == difference
        discrepancies.append(norm_inf(difference))
    groups['discarded-transfer'] = {'D': D, 'discrepancy_norms': discrepancies}

    counts, maxima, worst_errors = [], [], []
    for length in range(5):
        largest = F(0)
        count = 0
        for signs in product((-DELTA, DELTA), repeat=2*length):
            # Scalar recurrence, separate from the propagated matrix sum.
            u, w = F(0), F(0)
            propagated = v(0, 0)
            for j in range(length):
                d = v(signs[2*j], signs[2*j+1])
                u, w = u/2 + 2*w + d[0][0], w/2 + d[1][0]
                propagated = add(propagated, mm(power(A, length-1-j), d))
            assert values(propagated) == (u, w)
            largest = max(largest, abs(u), abs(w))
            count += 1
        sharp = DELTA * (10-F(8*length+10, 2**length))
        assert largest == sharp
        worst = v(0, 0)
        for _ in range(length):
            worst = add(mm(A, worst), v(DELTA, DELTA))
        assert max(abs(x) for x in values(worst)) == sharp
        counts.append(count)
        maxima.append(largest)
        worst_errors.append(values(worst))
    assert counts == [1, 4, 16, 64, 256]
    assert mm(sub(eye(2), A), v(10*DELTA, 2*DELTA)) == v(DELTA, DELTA)
    groups['persistent-disturbances'] = {'delta': DELTA, 'lengths': [0, 1, 2, 3, 4],
        'sign_sequences_per_length': counts, 'sign_sequences_total': sum(counts),
        'maxima': maxima, 'attaining_errors': worst_errors,
        'uniform_sharp_gain': 10, 'weighted_norm_uniform_bound': 32*DELTA}

    equation = sub(eye(2), A)
    assert mm(equation, RESOLVENT) == mm(RESOLVENT, equation) == eye(2)
    fixed = mm(RESOLVENT, v(1, 1))
    estimate = v(F(248, 25), F(99, 50))
    residual = sub(v(1, 1), mm(equation, estimate))
    error = sub(fixed, estimate)
    assert error == mm(RESOLVENT, residual)
    assert norm_inf(RESOLVENT) == 10
    assert mm(RESOLVENT, v(DELTA, DELTA)) == v(10*DELTA, 2*DELTA)
    groups['fixed-point-residual'] = {'inverse': RESOLVENT, 'fixed_point': values(fixed),
        'estimate': values(estimate), 'residual': values(residual), 'error': values(error),
        'inverse_norm': 10}

    affine = v(0, 0)
    for n in range(17):
        assert sub(affine, fixed) == mm(power(A, n), sub(v(0, 0), fixed))
        affine = add(mm(A, affine), v(1, 1))
    groups['exercises-and-affine-error'] = {'one_step': values(mm(A, v(1, 1))),
        'time_two_disturbance_bound': maxima[2], 'residual_budget': F(1, 1000),
        'solution_error_bound': F(1, 100), 'affine_times_checked': [0, 16]}
    assert len(groups) == 8
    return {'status': 'PASS', 'finite_example_groups': len(groups), 'groups': groups}


if __name__ == '__main__':
    print(json.dumps(run_audit(), default=str, indent=2))
