#!/usr/bin/env python3
"""Seven exact finite groups for the compression-and-memory operator study.

Contract: fixed rational T below; three initial states at n=0,...,16;
memory updates n=0,...,15; cutoffs m=0,...,4 advanced through time 16;
17 formal generating-function coefficients; exact packet identities.
Compare matrix powers, scalar recurrences and independently generated
series coefficients. No random sampling or floating tolerance. General-time
and general-cutoff proofs are supplied separately in the text.

Run: python -B examples/operator_memory.py
Standard library plus sibling guide helpers. Prints JSON; writes no files.
"""
from fractions import Fraction as F
import json

from operator_guide import M, v, eye, zero, mm, add, sub, scale


T = M([[F(1, 2), F(1, 4)], [F(1, 4), F(1, 2)]])
R = M([[1, 0]])
S = v(1, 0)
P = M([[1, 0], [0, 0]])
PLUS = scale(F(1, 2), M([[1, 1], [1, 1]]))
MINUS = scale(F(1, 2), M([[1, -1], [-1, 1]]))
CHECKPOINT = M([[F(1, 2), 1], [F(1, 16), F(1, 2)]])


def power(a, n):
    result = eye(len(a))
    for _ in range(n):
        result = mm(result, a)
    return result


def values(column):
    return tuple(row[0] for row in column)


def kernel(lag):
    return F(1, 16 * 2**lag)


def trajectory(initial):
    u, w = map(F, initial)
    states = []
    for _ in range(17):
        states.append((u, w))
        u, w = u/2+w/4, u/4+w/2
    return tuple(states)


def truncated(cutoff):
    history = [F(1)]
    for n in range(16):
        retained = sum((kernel(n-1-j)*history[j]
                        for j in range(max(0, n-cutoff), n)), F(0))
        history.append(history[n]/2+retained)
    return tuple(history)


def rational_coefficients(numerator, denominator, count):
    """Coefficient division with a nonzero constant denominator coefficient."""
    coefficients = []
    for n in range(count):
        target = numerator[n] if n < len(numerator) else F(0)
        previous = sum((denominator[j]*coefficients[n-j]
                        for j in range(1, min(n+1, len(denominator)))), F(0))
        coefficients.append((target-previous)/denominator[0])
    return tuple(coefficients)


def run_audit():
    groups = {}
    assert mm(R, S) == M([[1]]) and mm(S, R) == P
    assert mm(R, T) != mm(mm(R, T), mm(S, R))
    witness = v(0, 1)
    assert mm(R, witness) == v(0) and mm(mm(R, T), witness) == v(F(1, 4))
    assert mm(mm(R, power(T, 2)), S) == M([[F(5, 16)]])
    groups['closure-and-return'] = {'R': R, 'S': S, 'P': P,
        'compressed_rule': F(1, 2), 'collision_next_value': F(1, 4),
        'two_step_full': F(5, 16), 'two_step_compressed': F(1, 4), 'return_path': F(1, 16)}

    fixtures = ((1, 0), (0, 1), (-2, 3))
    trajectories = {initial: trajectory(initial) for initial in fixtures}
    for initial, states in trajectories.items():
        for n, state in enumerate(states):
            assert values(mm(power(T, n), v(*initial))) == state
            modes = add(scale(F(3, 4)**n, PLUS), scale(F(1, 4)**n, MINUS))
            assert power(T, n) == modes
            plus, minus = (initial[0]+initial[1])*F(3, 4)**n, (initial[0]-initial[1])*F(1, 4)**n
            assert state == ((plus+minus)/2, (plus-minus)/2)
    states = trajectories[(1, 0)]
    groups['full-trajectory'] = {'initial_states': fixtures, 'times_checked': [0, 16],
        'states': states[:6], 'repeated_compression': tuple(F(1, 2)**n for n in range(6))}

    for initial, states_fixture in trajectories.items():
        for n in range(16):
            full_history = [state[0] for state in states_fixture[:n+1]]
            initial_term = F(1, 4)*F(1, 2)**n*initial[1]
            remembered = sum((kernel(n-1-j)*full_history[j] for j in range(n)), F(0))
            assert states_fixture[n+1][0] == full_history[n]/2+initial_term+remembered
            hidden = F(1, 2)**n*initial[1]+sum((F(1, 2)**(n-1-j)*full_history[j]/4 for j in range(n)), F(0))
            assert hidden == states_fixture[n][1]
    groups['exact-memory'] = {'kernel_coefficients': tuple(kernel(lag) for lag in range(16)),
        'update_indices_checked': [0, 15], 'initial_states': len(fixtures), 'hidden_initial_example': F(1, 4)}
    hidden_packet = sub(eye(2), P)
    hidden_update = mm(mm(hidden_packet, T), hidden_packet)
    enter = mm(mm(hidden_packet, T), S)
    leave = mm(mm(R, T), hidden_packet)
    for lag in range(16):
        assert mm(mm(leave, power(hidden_update, lag)), enter) == M([[kernel(lag)]])

    coordinate = M([[1, 0], [0, F(1, 4)]])
    inverse = M([[1, 0], [0, 4]])
    assert mm(mm(coordinate, T), inverse) == CHECKPOINT
    for initial, state_list in trajectories.items():
        checkpoint = mm(coordinate, v(*initial))
        for n, state in enumerate(state_list):
            assert values(mm(inverse, checkpoint)) == state
            checkpoint = mm(CHECKPOINT, checkpoint)
    u3, v3 = states[3]
    correct_next = u3/2+v3/4
    reset_next = u3/2
    groups['checkpoint'] = {'update': CHECKPOINT, 'saved_time': 3,
        'saved_state': (u3, v3/4), 'correct_next': correct_next,
        'reset_next': reset_next, 'restart_error': correct_next-reset_next}

    cutoffs = []
    exact_u = tuple(state[0] for state in states)
    assert all(abs(u) <= F(3, 4)**n for n, u in enumerate(exact_u))
    for cutoff in range(5):
        approximate = truncated(cutoff)
        q = F(1, 2)+sum((kernel(lag) for lag in range(cutoff)), F(0))
        epsilon = F(1, 8*2**cutoff)
        bound = epsilon/(1-q)
        assert q == (5-F(1, 2**cutoff))/8 and bound == F(1, 3*2**cutoff+1)
        errors = tuple(u-z for u, z in zip(exact_u, approximate))
        assert all(0 <= e <= bound for e in errors)
        assert all(e == 0 for e in errors[:cutoff+2])
        assert errors[cutoff+2] == kernel(cutoff)
        # Full-history tail and propagated recursive error are checked separately.
        for n in range(16):
            tail = sum((kernel(n-1-j)*exact_u[j] for j in range(max(0, n-cutoff))), F(0))
            propagated = errors[n]/2+sum((kernel(n-1-j)*errors[j]
                for j in range(max(0, n-cutoff), n)), F(0))
            assert 0 <= tail <= epsilon
            assert errors[n+1] == propagated+tail
        cutoffs.append({'cutoff': cutoff, 'retained_coefficient_sum': q, 'tail_bound': epsilon,
            'uniform_error_bound': bound, 'first_error_time': cutoff+2,
            'first_error': errors[cutoff+2], 'maximum_tested_error': max(errors),
            'approximation': approximate})
    groups['finite-memory'] = {'initial_state': (1, 0), 'times_checked': [0, 16], 'cutoffs': cutoffs}

    numerator = (F(1), F(-1, 2))
    denominator = (F(1), F(-1), F(3, 16))
    series = rational_coefficients(numerator, denominator, 17)
    naive = rational_coefficients((F(1),), (F(1), F(-1, 2)), 17)
    kernel_series = rational_coefficients((F(1, 16),), (F(1), F(-1, 2)), 17)
    assert series == exact_u and naive == truncated(0)
    assert kernel_series == tuple(kernel(lag) for lag in range(17))
    for n in range(17):
        coefficient = sum((denominator[j]*series[n-j] for j in range(min(n+1, 3))), F(0))
        assert coefficient == (numerator[n] if n < 2 else 0)
    groups['formal-series'] = {'numerator': numerator, 'denominator': denominator,
        'coefficients': series, 'coefficient_count': 17, 'naive_coefficients': naive[:6]}

    assert add(PLUS, MINUS) == eye(2)
    assert mm(PLUS, PLUS) == PLUS and mm(MINUS, MINUS) == MINUS
    assert mm(PLUS, MINUS) == mm(MINUS, PLUS) == zero(2, 2)
    assert mm(T, PLUS) == mm(PLUS, T) == scale(F(3, 4), PLUS)
    assert mm(T, MINUS) == mm(MINUS, T) == scale(F(1, 4), MINUS)
    assert add(scale(F(3, 4), PLUS), scale(F(1, 4), MINUS)) == T
    summary = M([[1, 1]])
    difference = M([[1, -1]])
    assert mm(summary, T) == scale(F(3, 4), summary)
    assert mm(difference, T) == scale(F(1, 4), difference)
    assert mm(summary, v(1, 0)) == mm(summary, v(0, 1))
    assert mm(R, v(1, 0)) != mm(R, v(0, 1))
    groups['invariant-summaries-and-exercises'] = {'P_plus': PLUS, 'P_minus': MINUS,
        'sum_decay': F(3, 4), 'difference_decay': F(1, 4),
        'hidden_initial_next': F(1, 4), 'checkpoint_restart_error': correct_next-reset_next,
        'cutoff_two_bound': cutoffs[2]['uniform_error_bound'],
        'cutoff_two_first_error': cutoffs[2]['first_error']}
    assert len(groups) == 7
    return {'status': 'PASS', 'finite_example_groups': len(groups), 'groups': groups}


if __name__ == '__main__':
    print(json.dumps(run_audit(), default=str, indent=2))
