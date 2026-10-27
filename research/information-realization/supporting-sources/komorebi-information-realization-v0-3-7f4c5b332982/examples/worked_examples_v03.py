"""Executable examples for the access-aware packet information extension.

Run from any directory with Python 3.10+ and NumPy available. No downloads or
package installation are performed. The pinned Komorebi wheel is zip-imported.
"""
from __future__ import annotations
from fractions import Fraction
from itertools import product
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'src'))
sys.path.insert(0, str(ROOT / 'prior_v0_2' / 'src'))
from packet_information import (
    Matrix, accessible_repair, verify_repair, obstruction_dimension,
    predictive_closure, packet_transfer, leakage_block, minimal_raw_packets,
    finite_profile,
)
from komorebi_adapter import export_haar, native_integer_packets, source_receipt, backend
from access_graph import restricted_success
from information import FiniteModel


def check(value: bool, message: str) -> None:
    if not value:
        raise AssertionError(message)


def shift_matrix(p: int) -> Matrix:
    return Matrix(p, 4, ((0, 1, 0, 0), (0, 0, 1, 0), (0, 0, 0, 1), (1, 0, 0, 0)))


def haar_shift() -> dict:
    p = 5
    A, export = export_haar(4, 1, p=p)
    R = A.take_rows((0, 1))
    U = A.take_rows((2, 3))
    T = shift_matrix(p)
    F = R @ T
    B = packet_transfer(A, T)
    leak = leakage_block(B, (0, 1))
    certificate = accessible_repair(R, F, U)
    check(certificate.feasible and verify_repair(certificate, R, F, U), 'repair certificate')
    check(certificate.deficit_dimension == 1 and leak.rank() == 1, 'one-coordinate leakage')

    # c = d1 - d0. The generic algorithm is allowed to find a nonzero rescaling.
    H = Matrix(p, 2, ((-1, 1),))
    C = H @ U
    D = Matrix(p, 3, ((3, 3, 3), (3, 3, -3)))
    check(D @ R.stack(C) == F, 'manual one-step decoder identity')

    # The augmented state closes exactly, for all future horizons.
    S = R.stack(C)
    M = Matrix(p, 3, ((3, 3, 3), (3, 3, -3), (-1, 1, 0)))
    check(M @ S == S @ T, 'manual closed dynamics identity')
    closure = predictive_closure(R, (T,))
    check(closure.state.rank() == 3 and S.rank() == 3, 'minimal closure rank')

    x = (4, 1, 3, 2)
    packet = native_integer_packets(x, 1, p=p)
    next_x = T.apply(x)
    next_packet = native_integer_packets(next_x, 1, p=p)
    c = H.apply(packet[2:])
    check(packet == (0, 0, 3, 1) and c == (3,), 'concrete packet values')
    decoded = D.apply(packet[:2] + c)
    check(decoded == (4, 1) == next_packet[:2], 'concrete decoded coarse output')

    bad = accessible_repair(R, F, U.take_rows((0,)))
    check(not bad.feasible and verify_repair(bad, R, F, U.take_rows((0,))), 'inaccessible helper')
    raw_coordinates = minimal_raw_packets(R, F, (U.take_rows((0,)), U.take_rows((1,))))
    raw_leaf = minimal_raw_packets(R, F, (U,))
    check(raw_coordinates == (0, 1) and raw_leaf == (0,), 'raw coordinate/leaf distinction')

    trajectory_checks = 0
    all_x = tuple(product(range(p), repeat=4))
    observations = []
    targets = []
    invisible = (1, -1, 1, -1)
    check(not any(S.apply(invisible)), 'persistent unobservable direction')
    for initial in all_x:
        # Real library observation is explicitly extracted. The task decoder
        # receives this tuple and its permitted message, never the full tree.
        native = native_integer_packets(initial, 1, p=p)
        check(native == A.apply(initial), 'native source packet agreement')
        observed, detail = native[:2], native[2:]
        target = F.apply(initial)
        check(D.apply(observed + H.apply(detail)) == target, 'manual decoded state')
        check(certificate.decoder.apply(observed + certificate.encoder.apply(detail)) == target,
              'algorithmic decoded state')
        observations.append(observed)
        targets.append(target)
        state = initial
        reduced = S.apply(initial)
        shifted = tuple((v + z) % p for v, z in zip(initial, invisible))
        for _ in range(12):
            check(reduced[:2] == R.apply(state), 'reduced trajectory output')
            check(R.apply(shifted) == R.apply(state), 'invisible direction remains unobserved')
            state = T.apply(state)
            shifted = T.apply(shifted)
            reduced = M.apply(reduced)
            trajectory_checks += 1
    model = FiniteModel(tuple(observations), tuple(targets))
    check(model.kappa() == 5 and model.bayes_error() == Fraction(4, 5), 'measured task profile')

    horizons = []
    power = Matrix.identity(p, 4)
    cumulative = R
    for h in range(9):
        endpoint = R @ power
        cumulative = cumulative.stack(endpoint)
        endpoint_d = obstruction_dimension(R, endpoint)
        trajectory_d = obstruction_dimension(R, cumulative)
        check(endpoint_d == h % 2, 'endpoint deficit cycle')
        check(trajectory_d == int(h > 0), 'trajectory deficit saturation')
        horizons.append({'horizon': h, 'endpoint_deficit': endpoint_d,
                         'whole_trajectory_deficit': trajectory_d})
        power = power @ T
    return {
        'field': p, 'analysis': A.payload(), 'packet_transfer': B.payload(),
        'leakage': leak.payload(), 'algorithmic_certificate': certificate.payload(),
        'manual_encoder': H.payload(), 'manual_decoder': D.payload(),
        'closed_state': S.payload(), 'closed_transition': M.payload(),
        'closure_certificate': closure.payload(), 'export_receipt': export,
        'worked_state': x, 'packets': packet, 'manual_message': c,
        'shifted_state': next_x, 'decoded_next_coarse': decoded,
        'source_states_checked': len(all_x), 'trajectory_steps_checked': trajectory_checks,
        'native_source_analyses': len(all_x),
        'next_coarse_profile': finite_profile(5, 1),
        'full_source_profile': finite_profile(5, 2),
        'inaccessible_witness': bad.witness,
        'raw_detail_coordinates_needed': len(raw_coordinates),
        'native_detail_leaf_packets_needed': len(raw_leaf),
        'coded_message_coordinates_needed': 1,
        'permanently_unobservable_direction': invisible, 'horizons': horizons,
    }


def partial_budget() -> dict:
    weights = (2, 2, 1, 2, 1, 2, 1, 2, 2)
    states = tuple(product(range(3), repeat=2))
    r = tuple(a for a, b in states)
    f = tuple(b for a, b in states)
    rows = []
    for m in (1, 2, 3):
        optimum, encoder, count = restricted_success(r, f, f, weights, m)
        aware = sum(sum(sorted(weights[3*a:3*a+3], reverse=True)[:m])
                    for a in range(3)) / Fraction(15)
        expected = {1: Fraction(2, 5), 2: Fraction(11, 15), 3: Fraction(1)}[m]
        check(optimum == expected, 'helper-only partial-budget optimum')
        check(aware == {1: Fraction(2, 5), 2: Fraction(4, 5), 3: Fraction(1)}[m],
              'state-aware partial-budget optimum')
        rows.append({'symbols': m, 'state_aware_success': str(aware),
                     'helper_only_success': str(optimum), 'best_helper_encoder': encoder,
                     'encoders_enumerated': count})
    return {'field': 3, 'state_space': 'GF(3)^2', 'weights_by_observation': [weights[i:i+3] for i in (0, 3, 6)],
            'total_weight': 15, 'exact_minimum_alphabet_both_models': 3, 'curves': rows}


def small_energy() -> dict:
    import numpy as np
    module = backend()
    values = []
    for exponent in (0, 4, 12, 24):
        epsilon = 2.0 ** -exponent
        r, task = [], []
        energies = []
        for a, b in product((-1, 1), repeat=2):
            signal = np.array((epsilon*a, -epsilon*a, epsilon*b, -epsilon*b))
            tree = module.haar_packet_analyze(signal, 1, normalized=False)
            low = tuple(float(v) for v in tree.coefficient('0'))
            high = tree.coefficient('1')
            energy = float(np.vdot(high, high).real)
            check(low == (0.0, 0.0) and energy == 8 * epsilon**2, 'energy construction')
            r.append(low)
            task.append((a, b))
            energies.append(energy)
        model = FiniteModel(tuple(r), tuple(task))
        check(model.kappa() == 4 and model.bayes_error() == Fraction(3, 4), 'energy/information separation')
        values.append({'epsilon_power_of_two': -exponent, 'epsilon': epsilon,
                       'native_detail_energy': energies[0], 'missing_bits': 2,
                       'optimal_error': '3/4'})
    singleton = [float(module.entropy_cost(np.array((v,)))) for v in (1., 999.)]
    check(singleton == [0., 0.], 'energy entropy is not amplitude uncertainty')
    return {'scope': 'Noiseless distinguishability; not a robustness claim', 'rows': values,
            'singleton_native_energy_entropies': singleton}


def main() -> None:
    report = {'version': '0.3.0', 'status': 'PASS', 'source_receipt': source_receipt(),
              'haar_shift': haar_shift(), 'restricted_partial_budget': partial_budget(),
              'small_energy': small_energy()}
    out = ROOT / 'reports' / ('worked_examples_v03_optimized.json' if sys.flags.optimize else 'worked_examples_v03.json')
    out.write_text(json.dumps(report, indent=2) + '\n', encoding='utf-8')
    print(json.dumps({'status': report['status'], 'report': str(out),
                      'source_states': report['haar_shift']['source_states_checked'],
                      'trajectory_checks': report['haar_shift']['trajectory_steps_checked']}, indent=2))


if __name__ == '__main__':
    main()
