"""Author: Komorebi P. Exact interval kernel checks and rejection controls.

Run ``python src/test_interval_core.py``.  The independent nodal computation
below does not use the checker's tree enumeration or matrix inverse.
"""
from __future__ import annotations

from copy import deepcopy
from fractions import Fraction as F
import hashlib
import json
from pathlib import Path
import random
import time

from interval_certificate import (
    FORMAT, build_coefficient_system, evaluate_jacobian, evaluate_polynomial,
    evaluate_system, graph_polynomials, interval_evaluate_polynomial,
    invert_matrix, verify_interval_circuit,
)


ROOT = Path(__file__).resolve().parents[1]


def nodal_impedance(branches, values, sample):
    """Independent Fraction Gaussian elimination at one positive Laplace value."""
    nodes = sorted({n for b in branches for n in b['nodes']} - {0})
    positions = {node: k for k, node in enumerate(nodes)}
    M = [[F(0) for _ in range(len(nodes) + 1)] for _ in nodes]
    M[positions[1]][-1] = F(1)
    for branch, value in zip(branches, values):
        typ = branch['type']
        y = value if typ == 'g' else value / sample if typ == 'h' else value * sample
        a, b = branch['nodes']
        if a:
            M[positions[a]][positions[a]] += y
        if b:
            M[positions[b]][positions[b]] += y
        if a and b:
            M[positions[a]][positions[b]] -= y
            M[positions[b]][positions[a]] -= y
    for k in range(len(nodes)):
        pivot = next(i for i in range(k, len(nodes)) if M[i][k])
        M[k], M[pivot] = M[pivot], M[k]
        for i in range(k + 1, len(nodes)):
            ratio = M[i][k] / M[k][k]
            for j in range(k, len(nodes) + 1):
                M[i][j] -= ratio * M[k][j]
    solution = [F(0)] * len(nodes)
    for i in range(len(nodes) - 1, -1, -1):
        solution[i] = (M[i][-1] - sum(M[i][j] * solution[j] for j in range(i + 1, len(nodes)))) / M[i][i]
    return solution[positions[1]]


def make_exact_certificate(branches, center, fixed_parameters=None):
    graph = graph_polynomials(branches)
    P = [evaluate_polynomial(p, center) for p in graph['numerator']]
    Q = [evaluate_polynomial(p, center) for p in graph['denominator']]
    system = build_coefficient_system(branches, P, Q, fixed_parameters)
    Y = invert_matrix(evaluate_jacobian(system, center))
    cert = {'format': FORMAT, 'target': {'P': list(map(str, P)), 'Q': list(map(str, Q))},
            'storage_budget': graph['storage_count'], 'branches': branches,
            'center': list(map(str, center)),
            'radii': ['1/100000000'] * len(center),
            'preconditioner': [list(map(str, row)) for row in Y]}
    if fixed_parameters is not None:
        cert['fixed_parameters'] = fixed_parameters
    return cert


def run():
    start = time.perf_counter()
    checks, rejection_checks = [], []

    def passed(name):
        checks.append(name)

    def rejected(name, callback):
        try:
            callback()
        except (ValueError, KeyError, TypeError, ZeroDivisionError):
            rejection_checks.append(name)
            return
        raise AssertionError('Invalid evidence accepted: ' + name)

    # A hand-computable off-center box: F(g)=1-2g, c=0.51, r=0.02,
    # T(g)=0.5, residual correction=0.01, contraction=0.
    resistor = {'format': FORMAT, 'target': {'P': ['2'], 'Q': ['1']},
                'storage_budget': 0, 'branches': [{'type': 'g', 'nodes': [0, 1]}],
                'center': ['51/100'], 'radii': ['1/50'], 'preconditioner': [['-1/2']]}
    report = verify_interval_circuit(resistor, {'P': [2], 'Q': [1]}, 0)
    assert report['weighted_contraction_bound'] == '0'
    assert report['center_correction_bounds'] == ['1/100']
    assert report['self_map_margins'] == ['1/100']
    assert report['global_minimum_proved_by_degree']
    passed('hand_computable_off_center_resistor')

    # Four variables but three full impedance equations.  A fourth exact
    # equation fixes a shunt conductance; no impedance equation is discarded.
    branches = [{'type': 'c', 'nodes': [1, 2]}, {'type': 'g', 'nodes': [1, 2]},
                {'type': 'g', 'nodes': [0, 2]}, {'type': 'g', 'nodes': [0, 1]}]
    fixed = [{'index': 3, 'value': '7'}]
    four = make_exact_certificate(branches, list(map(F, [2, 3, 5, 7])), fixed)
    result = verify_interval_circuit(four)
    assert result['equation_count'] == 4 and result['coefficient_equation_count'] == 3
    assert result['fixed_parameter_count'] == 1 and result['global_minimum_proved_by_degree']
    passed('four_branch_RC_chart_with_all_coefficients_and_one_fixed_parameter')

    # Orthogonal identity check: graph forest polynomials versus direct KCL.
    # Node labels are deliberately nonconsecutive and both parallel branch
    # types and internal dangling material occur in this deterministic sample.
    rng = random.Random(61541)
    graph_cases, samples = [], [F(1, 5), F(1), F(7, 2), F(11)]
    for vertices in range(2, 6):
        labels = [0, 1] + [7 + 3 * k for k in range(vertices - 2)]
        for replicate in range(4):
            edges, seen = [], set()
            for i in range(1, vertices):
                a, b = labels[i], labels[rng.randrange(i)]
                typ = rng.choice(['g', 'h', 'c'])
                edges.append({'type': typ, 'nodes': [a, b]})
                seen.add((typ, *sorted((a, b))))
            for _ in range(replicate + 2):
                a, b = rng.sample(labels, 2)
                typ = rng.choice(['g', 'h', 'c'])
                key = (typ, *sorted((a, b)))
                if key not in seen:
                    edges.append({'type': typ, 'nodes': [a, b]})
                    seen.add(key)
            values = [F(rng.randint(1, 9), rng.randint(1, 7)) for _ in edges]
            polys = graph_polynomials(edges)
            for s in samples:
                N = sum(evaluate_polynomial(poly, values) * s ** j for j, poly in enumerate(polys['numerator']))
                D = sum(evaluate_polynomial(poly, values) * s ** j for j, poly in enumerate(polys['denominator']))
                assert N / D == nodal_impedance(edges, values, s)
            graph_cases.append({'vertices': vertices, 'branches': len(edges), 'samples': len(samples)})
    passed('sixteen_graphs_tree_forest_identity_against_sixty_four_exact_KCL_values')

    # Exact fourth-order finite differences independently check differentiation
    # on degree <=3 graph polynomials, including all seven column positions.
    historical = ROOT / 'certificates/historical_case_1.json'
    if historical.exists():
        hcert = json.loads(historical.read_text())
    else:
        example = json.loads((ROOT / 'examples/sparse_bridge_A.json').read_text())
        edges = example['known_physical_edges']
        spec = [{'type': {'R': 'g', 'L': 'h', 'C': 'c'}[t], 'nodes': [a, b]} for t, a, b, _ in edges]
        vals = [F(v) if t == 'C' else F(1, v) for t, _, _, v in edges]
        hcert = make_exact_certificate(spec, vals)
    verified = verify_interval_circuit(hcert, hcert['target'], hcert['storage_budget'])
    assert verified['coefficient_equation_count'] == 7
    system = build_coefficient_system(hcert['branches'], hcert['target']['P'], hcert['target']['Q'])
    values = [F(2 + j, 3 + j) for j in range(system['variables'])]
    J = evaluate_jacobian(system, values)
    step = F(1, 17)
    for column in range(system['variables']):
        shifted = []
        for delta in [-2, -1, 1, 2]:
            point = values.copy()
            point[column] += delta * step
            shifted.append(evaluate_system(system, point))
        for row in range(len(system['equations'])):
            derivative = (shifted[0][row] - 8 * shifted[1][row] + 8 * shifted[2][row] - shifted[3][row]) / (12 * step)
            assert derivative == J[row][column]
    passed('all_forty_nine_q3_jacobian_entries_match_exact_finite_differences')
    passed('retained_seven_variable_interval_certificate_replays')

    # Interval arithmetic must enclose values through zero, including even and
    # odd powers; these are independent of the circuit's positive-box restriction.
    poly = {(2, 0): F(-3), (0, 3): F(2), (1, 1): F(-7), (0, 0): F(5)}
    intervals = [(F(-2), F(3)), (F(-4), F(2))]
    lo, hi = interval_evaluate_polynomial(poly, intervals)
    for a in range(-2, 4):
        for b in range(-4, 3):
            assert lo <= evaluate_polynomial(poly, [a, b]) <= hi
    passed('signed_interval_powers_enclose_forty_two_integer_points')

    # Equivalent target representations bind to the same exact rational function.
    verify_interval_circuit(resistor, {'P': [2, 2], 'Q': [1, 1]}, 0)
    scaled = deepcopy(resistor)
    scaled['target'] = {'P': ['4', '4'], 'Q': ['2', '2']}
    verify_interval_circuit(scaled, resistor['target'], 0)
    passed('target_binding_accepts_only_exact_equivalence_including_common_factors')

    def mutate(base, path, value):
        obj = deepcopy(base)
        here = obj
        for part in path[:-1]:
            here = here[part]
        here[path[-1]] = value
        return obj

    cases = [
        ('wrong_format', resistor, ['format'], 'other'),
        ('zero_radius', resistor, ['radii', 0], '0'),
        ('negative_radius', resistor, ['radii', 0], '-1'),
        ('box_touches_zero', resistor, ['radii', 0], '51/100'),
        ('floating_center', resistor, ['center', 0], 0.51),
        ('boolean_center', resistor, ['center', 0], True),
        ('zero_preconditioner', resistor, ['preconditioner', 0, 0], '0'),
        ('wrong_preconditioner_sign', resistor, ['preconditioner', 0, 0], '1/2'),
        ('self_map_boundary_equality', resistor, ['radii', 0], '1/100'),
        ('self_map_too_small', resistor, ['radii', 0], '1/1000'),
        ('zero_denominator_target', resistor, ['target', 'Q'], ['0']),
        ('zero_numerator_target', resistor, ['target', 'P'], ['0']),
        ('boolean_node', resistor, ['branches', 0, 'nodes', 1], True),
        ('negative_node', resistor, ['branches', 0, 'nodes', 1], -1),
        ('self_loop', resistor, ['branches', 0, 'nodes'], [0, 0]),
        ('missing_input_port', resistor, ['branches', 0, 'nodes'], [0, 2]),
        ('unknown_branch_type', resistor, ['branches', 0, 'type'], 'R'),
        ('negative_budget', resistor, ['storage_budget'], -1),
        ('boolean_budget', resistor, ['storage_budget'], False),
        ('undersized_reactive_budget', hcert, ['storage_budget'], 2),
        ('corrupt_q3_target', hcert, ['target', 'P', 0], '1234567'),
        ('corrupt_q3_center', hcert, ['center', 0], '10'),
        ('overlarge_q3_box', hcert, ['radii', 0], hcert['center'][0]),
        ('fixed_parameter_wrong_value', four, ['fixed_parameters', 0, 'value'], '8'),
        ('fixed_parameter_negative_value', four, ['fixed_parameters', 0, 'value'], '-7'),
        ('fixed_parameter_out_of_range', four, ['fixed_parameters', 0, 'index'], 4),
        ('fixed_parameter_boolean_index', four, ['fixed_parameters', 0, 'index'], True),
        ('missing_fixed_parameter_nonsquare', four, ['fixed_parameters'], []),
    ]
    for name, base, path, value in cases:
        rejected(name, lambda base=base, path=path, value=value: verify_interval_circuit(mutate(base, path, value)))
    rejected('wrong_expected_target', lambda: verify_interval_circuit(resistor, {'P': [3], 'Q': [1]}))
    rejected('wrong_expected_budget', lambda: verify_interval_circuit(resistor, expected_budget=1))
    duplicated = deepcopy(resistor)
    duplicated['branches'].append(deepcopy(duplicated['branches'][0]))
    rejected('duplicate_same_type_branch', lambda: verify_interval_circuit(duplicated))
    disconnected = deepcopy(resistor)
    disconnected['branches'].append({'type': 'g', 'nodes': [2, 3]})
    rejected('disconnected_physical_material', lambda: verify_interval_circuit(disconnected))
    repeated = deepcopy(four)
    repeated['fixed_parameters'].append(deepcopy(repeated['fixed_parameters'][0]))
    rejected('repeated_fixed_parameter', lambda: verify_interval_circuit(repeated))
    # Supplying an extra alleged equation cannot alter the compiler's system.
    forged = deepcopy(resistor)
    forged['equations'] = []
    forged_report = verify_interval_circuit(forged)
    assert forged_report['equations_sha256'] == report['equations_sha256']
    passed('untrusted_equation_payload_does_not_change_rebuilt_identity')

    inputs = [Path(__file__), ROOT / 'src/interval_certificate.py', ROOT / 'src/real_algebraic.py',
              ROOT / 'src/exact_polynomials.py']
    if historical.exists():
        inputs.append(historical)
    return {'status': 'PASS', 'test_groups': len(checks) + len(rejection_checks),
            'positive_groups': checks, 'rejection_controls': rejection_checks,
            'graph_identity_cases': graph_cases,
            'scope': 'finite exact checker implementation checks; no topology coverage inference',
            'input_sha256': {str(path.relative_to(ROOT)): hashlib.sha256(path.read_bytes()).hexdigest() for path in inputs},
            'elapsed_seconds': time.perf_counter() - start}


if __name__ == '__main__':
    print(json.dumps(run(), indent=2))
