#!/usr/bin/env python3
"""Eight exact finite groups for the operator observation study.

Contract: rational fixtures for the displayed three-state, unforced linear
model. Compare matrix powers and a separate scalar recurrence for three
initial states at n=0,...,12. Check each specified inverse, intertwiner and
orthogonal projection as an exact matrix identity. Enumerate every sign
corner of the stated three- or four-reading noise cubes. These checks do
not certify an unspecified physical model or any new formal theorem.

Run: python -B examples/operator_observation.py
Uses only the standard library and the sibling guide arithmetic helpers.
Prints JSON; does not write files.
"""
from fractions import Fraction as F
from itertools import product
import json

from operator_guide import M, v, eye, zero, mm, add, sub, scale, transpose, rank


T = M([[1, 1, 0], [0, 1, 1], [0, 0, 1]])
R = M([[1, 0, 0]])
O3 = M([[1, 0, 0], [1, 1, 0], [1, 2, 1]])
B3 = M([[1, 0, 0], [-1, 1, 0], [1, -2, 1]])
K = M([[0, 1, 0], [0, 0, 1], [1, -3, 3]])
O4 = O3 + M([[1, 3, 3]])
C = M([[-1, 3, -3, 1]])
L = M([[F(19, 20), F(3, 20), F(-3, 20), F(1, 20)],
       [F(-4, 5), F(2, 5), F(3, 5), F(-1, 5)],
       [F(1, 2), F(-1, 2), F(-1, 2), F(1, 2)]])
X = v(2, 3, 1)
DELTA = F(1, 100)


def power(a, n):
    answer = eye(len(a))
    for _ in range(n):
        answer = mm(answer, a)
    return answer


def values(column):
    return tuple(row[0] for row in column)


def row_gains(a):
    return tuple(sum(abs(x) for x in row) for row in a)


def corner_maxima(a, delta):
    maxima = [F(0)] * len(a)
    for signs in product((-delta, delta), repeat=len(a[0])):
        output = values(mm(a, v(*signs)))
        maxima = [max(old, abs(new)) for old, new in zip(maxima, output)]
    return tuple(maxima)


def run_audit():
    groups = {}
    nilpotent = sub(T, eye(3))
    assert power(nilpotent, 3) == zero(3, 3)
    fixtures = ((2, 3, 1), (0, 0, 0), (-1, 2, -2))
    for initial in fixtures:
        u, velocity, acceleration = map(F, initial)
        for n in range(13):
            matrix_state = values(mm(power(T, n), v(*initial)))
            assert matrix_state == (u, velocity, acceleration)
            assert u == initial[0] + n * initial[1] + F(n * (n - 1), 2) * initial[2]
            assert power(T, n) == add(add(eye(3), scale(n, nilpotent)),
                                         scale(F(n * (n - 1), 2), power(nilpotent, 2)))
            u, velocity = u + velocity, velocity + acceleration
    states = tuple(values(mm(power(T, n), X)) for n in range(5))
    readings = tuple(state[0] for state in states)
    groups['dynamics'] = {'initial_states': fixtures, 'times_checked': [0, 12],
                          'states': states, 'readings': readings}

    assert O3 == R + mm(R, T) + mm(R, power(T, 2))
    assert mm(B3, O3) == mm(O3, B3) == eye(3)
    assert mm(B3, v(*readings[:3])) == X
    O2 = O3[:2]
    witness = v(0, 0, 1)
    assert rank(O2) == 2 and mm(O2, witness) == v(0, 0)
    assert mm(mm(R, power(T, 2)), witness) == v(1)
    groups['exact-recovery'] = {'O3': O3, 'B3': B3, 'recovered': values(mm(B3, v(*readings[:3]))),
                                'two-reading-witness': values(witness)}

    assert mm(O3, T) == mm(K, O3)
    for n in range(10):
        history = mm(O3, mm(power(T, n), X))
        next_history = mm(O3, mm(power(T, n + 1), X))
        assert mm(K, history) == next_history
        a, b, d = values(history)
        assert next_history[-1][0] == a - 3 * b + 3 * d
    groups['history-update'] = {'K': K, 'next_reading': readings[3], 'following_reading': readings[4]}

    predict = M([[1, -3, 3]])
    assert row_gains(B3) == (1, 2, 4)
    assert corner_maxima(B3, DELTA) == (DELTA, 2 * DELTA, 4 * DELTA)
    assert corner_maxima(predict, DELTA) == (7 * DELTA,)
    noise3 = v(DELTA, -DELTA, DELTA)
    noisy3 = add(v(*readings[:3]), noise3)
    groups['noisy-recovery'] = {'delta': DELTA, 'measured': values(noisy3),
        'reconstructed': values(mm(B3, noisy3)), 'predicted_next': mm(predict, noisy3)[0][0],
        'gains': row_gains(B3), 'noise_corners_checked': 8}

    assert mm(C, O4) == zero(1, 3)
    assert mm(C, transpose(C)) == M([[20]])
    assert corner_maxima(C, DELTA) == (8 * DELTA,)
    noise4 = v(DELTA, -DELTA, DELTA, -DELTA)
    clean4 = mm(O4, X)
    noisy4 = add(clean4, noise4)
    rho = mm(C, noisy4)[0][0]
    assert rho == -8 * DELTA
    offset = v(DELTA, DELTA, DELTA, DELTA)
    assert mm(C, add(clean4, offset)) == v(0)
    assert mm(B3, add(v(*readings[:3]), v(DELTA, DELTA, DELTA))) == add(X, v(DELTA, 0, 0))
    exercise = v(1, 3, 6, 9)
    assert mm(C, exercise) == v(-1) and 1 > 8 * F(1, 10)
    groups['consistency'] = {'C': C, 'measured': values(noisy4), 'rho': rho,
        'bound': 8 * DELTA, 'noise_corners_checked': 16, 'exercise_residual': F(-1)}

    projection = mm(O4, L)
    assert mm(L, O4) == eye(3)
    assert projection == sub(eye(4), scale(F(1, 20), mm(transpose(C), C)))
    assert transpose(projection) == projection == mm(projection, projection)
    estimate = mm(L, noisy4)
    residual = sub(noisy4, mm(O4, estimate))
    assert mm(transpose(O4), residual) == v(0, 0, 0)
    residual_squared = mm(transpose(residual), residual)[0][0]
    assert residual_squared == rho ** 2 / 20
    # The constant-offset control changes the estimated u despite zero residual.
    assert mm(L, offset) == v(DELTA, 0, 0)
    groups['squared-error-fit'] = {'L': L, 'estimate': values(estimate),
        'residual': values(residual), 'residual_squared': residual_squared}

    assert row_gains(L) == (F(13, 10), 2, 2)
    assert corner_maxima(L, DELTA) == tuple(DELTA * gain for gain in row_gains(L))
    assert max(map(abs, values(residual))) > DELTA
    assert max(map(abs, values(sub(noisy4, clean4)))) == DELTA
    groups['fitting-criteria'] = {'coordinate_gains': row_gains(L), 'noise_corners_checked': 16,
        'squared_error_fit_max_residual': max(map(abs, values(residual))),
        'feasible_original_state_max_residual': DELTA}

    O024 = R + mm(R, power(T, 2)) + mm(R, power(T, 4))
    B024 = M([[1, 0, 0], [F(-5, 8), F(3, 4), F(-1, 8)], [F(1, 4), F(-1, 2), F(1, 4)]])
    assert mm(B024, O024) == mm(O024, B024) == eye(3)
    assert row_gains(B024) == (1, F(3, 2), 1)
    assert corner_maxima(B024, DELTA) == (DELTA, F(3, 2) * DELTA, DELTA)
    groups['sample-times'] = {'times': [0, 2, 4], 'observation': O024,
        'reconstruction': B024, 'readings': values(mm(O024, X)), 'coordinate_gains': row_gains(B024),
        'noise_corners_checked': 8}
    # The exercise restricting w=0 has a two-dimensional admissible state space.
    for u, velocity in ((0, 0), (1, 2), (-2, 3)):
        y0, y1, y2 = values(mm(O3, v(u, velocity, 0)))
        assert (y0, y1 - y0, 0) == (u, velocity, 0)
        assert y2 == 2 * y1 - y0
    assert mm(B3, v(1, 3, 6)) == v(1, 2, 1)
    assert mm(predict, v(1, 3, 6)) == v(10)
    return {'result': 'PASS', 'finite_example_groups': len(groups), 'arithmetic': 'exact rational',
            'groups': groups, 'scope': 'Specified finite model, identities and failure controls; no new Lean or physical-model certification.'}


if __name__ == '__main__':
    print(json.dumps(run_audit(), indent=2, default=str))
