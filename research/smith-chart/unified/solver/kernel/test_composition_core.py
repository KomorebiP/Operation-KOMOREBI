"""Author: Komorebi P. Independent composition checks and rejection controls.

Run ``python src/test_composition_core.py``.  The rational graph checks below
perform their own Fraction Gaussian elimination and scalar evaluation; they do
not call the composition checker's rational algebra, gluing code, or a legacy
nodal solver.  Finite tests support implementation confidence, not completeness.
"""
from __future__ import annotations

from copy import deepcopy
from fractions import Fraction as F
import hashlib
import json
from pathlib import Path
import random
import time
from unittest.mock import patch

import composition_certificate as cc
from composition_certificate import (
    FORMAT, ALGEBRAIC_FORMAT, INTERVAL_FORMAT, certificate_node, element_node,
    frequency_invert_node, make_composition, parallel_node, series_node,
    verify_circuit, verify_composition_certificate,
)


ROOT = Path(__file__).resolve().parents[1]


def scalar_polynomial(coefficients, sample):
    result = F(0)
    for coefficient in reversed(coefficients):
        result = result * sample + F(coefficient)
    return result


def scalar_target(target, sample):
    return scalar_polynomial(target['P'], sample) / scalar_polynomial(target['Q'], sample)


def scalar_expression(expression, sample):
    """Independent scalar series/parallel semantics, with no polynomial algebra."""
    op = expression['op']
    if op == 'certificate':
        return scalar_target(expression['certificate']['target'], sample)
    if op == 'element':
        value = F(expression['value'])
        return value if expression['type'] == 'R' else value * sample if expression['type'] == 'L' else 1 / (value * sample)
    if op == 'frequency_invert':
        return scalar_expression(expression['child'], 1 / sample)
    values = [scalar_expression(child, sample) for child in expression['children']]
    if op == 'series':
        return sum(values, F(0))
    return 1 / sum((1 / value for value in values), F(0))


def independent_nodal(graph, sample):
    """Compute input impedance from a rebuilt graph using rational elimination.

    This deliberately supports only rational coefficient references and constant
    polynomials in algebraic contexts.  It never substitutes an interval center
    for the exact root represented by a leaf.
    """
    nodes = sorted({n for edge in graph['branches'] for n in edge['nodes']} - {0})
    positions = {node: i for i, node in enumerate(nodes)}
    n = len(nodes)
    matrix = [[F(0) for _ in range(n + 1)] for _ in range(n)]
    matrix[positions[1]][n] = F(1)
    for edge in graph['branches']:
        reference = edge['coefficient']
        if reference['kind'] == 'rational':
            value = F(reference['value'])
        elif reference['kind'] == 'algebraic' and len(reference['polynomial']) == 1:
            value = F(reference['polynomial'][0])
        else:
            raise ValueError('Independent rational nodal check cannot approximate a leaf root')
        typ = edge['type']
        admittance = value if typ == 'g' else value / sample if typ == 'h' else value * sample
        a, b = edge['nodes']
        if a:
            matrix[positions[a]][positions[a]] += admittance
        if b:
            matrix[positions[b]][positions[b]] += admittance
        if a and b:
            matrix[positions[a]][positions[b]] -= admittance
            matrix[positions[b]][positions[a]] -= admittance
    for k in range(n):
        pivot = next(i for i in range(k, n) if matrix[i][k])
        matrix[k], matrix[pivot] = matrix[pivot], matrix[k]
        for i in range(k + 1, n):
            factor = matrix[i][k] / matrix[k][k]
            for j in range(k, n + 1):
                matrix[i][j] -= factor * matrix[k][j]
    solution = [F(0)] * n
    for i in range(n - 1, -1, -1):
        remainder = matrix[i][n] - sum((matrix[i][j] * solution[j] for j in range(i + 1, n)), F(0))
        solution[i] = remainder / matrix[i][i]
    return solution[positions[1]]


def algebraic_resistor_pair(radicand, total):
    """R1=sqrt(d), R2=total-sqrt(d), so the leaf impedance is rational."""
    denominator = total * total - radicand
    return {
        'format': ALGEBRAIC_FORMAT,
        'target': {'P': [str(total)], 'Q': ['1']}, 'storage_budget': 0,
        'field': {'polynomial': [str(-radicand), '0', '1'], 'interval': ['1', '2']},
        'branches': [
            {'type': 'g', 'nodes': [1, 2], 'coefficient': ['0', str(F(1, radicand))]},
            {'type': 'g', 'nodes': [0, 2],
             'coefficient': [str(F(total, denominator)), str(F(1, denominator))]},
        ],
    }


def run():
    start = time.perf_counter()
    positive, rejection = [], []
    nodal_cases = 0
    nodal_samples = 0

    def passed(name):
        positive.append(name)

    def rejected(name, callback):
        try:
            callback()
        except ValueError:
            rejection.append(name)
            return
        raise AssertionError('Invalid evidence was not rejected with ValueError: ' + name)

    def changed(cert, path, value):
        result = deepcopy(cert)
        cursor = result
        for part in path[:-1]:
            cursor = cursor[part]
        cursor[path[-1]] = value
        return result

    def exact_graph_case(expression):
        nonlocal nodal_cases, nodal_samples
        certificate = make_composition(expression)
        result = verify_circuit(certificate, certificate['target'], certificate['storage_budget'])
        # At least n+q+1 distinct positive samples also suffice for a separate
        # rational-function identity check under the graph degree bound.
        count = result['reduced_target_degree'] + result['actual_storage'] + 1
        samples = [F(k) for k in range(1, count + 1)] + [F(2, 3)]
        for sample in samples:
            target = scalar_target(certificate['target'], sample)
            assert independent_nodal(result['rebuilt_graph'], sample) == target
            assert scalar_expression(expression, sample) == target
        nodal_cases += 1
        nodal_samples += len(samples)
        return certificate, result

    # Primitive physical values must be converted to the correct admittance.
    for typ, value, expected_coefficient in [('R', '5/2', '2/5'), ('L', '7/3', '3/7'), ('C', '11/4', '11/4')]:
        _, result = exact_graph_case(element_node(typ, value))
        assert result['rebuilt_graph']['branches'][0]['coefficient']['value'] == expected_coefficient
    passed('physical_R_L_C_values_and_independent_nodal_samples')

    rational_expression = parallel_node(
        series_node(element_node('R', 3), element_node('L', '2/5')),
        series_node(element_node('R', '7/2'), element_node('C', '4/3')),
        element_node('R', '9/4'),
    )
    rational_cert, rational_result = exact_graph_case(rational_expression)
    passed('mixed_series_parallel_graph_independently_checked')

    rng = random.Random(2026111107)

    def random_expression(depth):
        if depth == 0 or rng.randrange(4) == 0:
            return element_node(rng.choice(('R', 'L', 'C')), F(rng.randrange(1, 8), rng.randrange(1, 8)))
        op = rng.randrange(3)
        if op == 0:
            return frequency_invert_node(random_expression(depth - 1))
        children = [random_expression(depth - 1), random_expression(depth - 1)]
        return series_node(children) if op == 1 else parallel_node(children)

    for _ in range(32):
        exact_graph_case(random_expression(3))
    passed('32_seeded_rational_trees_independent_scalar_and_nodal_checks')

    image = json.loads((ROOT / 'certificates/image_baseline_cubic.json').read_text())
    image_result = verify_circuit(image, image['target'], 3)
    assert image_result['actual_storage'] == 3 and image_result['global_minimum_proved_by_degree']
    _, image_outer = exact_graph_case(series_node(certificate_node(image), element_node('L', 2)))
    assert image_outer['actual_storage'] == image_outer['reduced_target_degree'] == 4
    passed('image_pinned_rational_cubic_leaf_and_degree_four_outer_element')

    # Repeat the very same dictionary.  Its two physical copies must not share
    # internal nodes or a parameter occurrence, although the checked data agree.
    image_leaf = certificate_node(image)
    repeated, repeated_result = exact_graph_case({'op': 'parallel', 'children': [image_leaf, image_leaf]})
    contexts = repeated_result['parameter_contexts']
    assert len(contexts) == 2 and contexts[0]['id'] != contexts[1]['id']
    assert contexts[0]['certificate_sha256'] == contexts[1]['certificate_sha256']
    vertices = []
    for context in contexts:
        vertices.append({v for edge in repeated_result['rebuilt_graph']['branches']
                         if edge['coefficient']['context'] == context['id'] for v in edge['nodes']})
    assert vertices[0] & vertices[1] == {0, 1}
    assert repeated_result['physical_branch_count'] == 2 * len(image['branches'])
    assert repeated_result['actual_storage'] == 6 and repeated_result['reduced_target_degree'] == 3
    assert repeated_result['realization_only'] and not repeated_result['global_minimum_proved_by_degree']
    passed('repeated_leaf_occurrences_keep_disjoint_internal_nodes_and_counts')

    # Duplicate branch instances are legal in an assembled physical multigraph.
    _, duplicate_result = exact_graph_case(parallel_node(element_node('C', 2), element_node('C', 3)))
    rows = duplicate_result['rebuilt_graph']['branches']
    assert len(rows) == 2 and rows[0]['nodes'] == rows[1]['nodes'] == [0, 1]
    assert [row['instance'] for row in rows] == [0, 1]
    assert duplicate_result['actual_storage'] == 2 and duplicate_result['reduced_target_degree'] == 1
    assert not duplicate_result['global_minimum_proved_by_degree']
    passed('parallel_duplicates_are_physical_instances_and_cancellation_is_not_minimal')

    loose_budget = make_composition(element_node('L', 2), budget=7)
    loose_result = verify_circuit(loose_budget, expected_budget=7)
    assert loose_result['actual_storage'] == loose_result['reduced_target_degree'] == 1
    assert loose_result['global_minimum_proved_by_degree']
    passed('minimality_uses_actual_storage_not_declared_budget')

    sqrt2 = algebraic_resistor_pair(2, 3)
    sqrt3 = algebraic_resistor_pair(3, 4)
    fields_expression = series_node(
        parallel_node(certificate_node(sqrt2), certificate_node(sqrt3)), element_node('L', 5))
    fields_cert = make_composition(fields_expression, {'P': ['12/7', '5'], 'Q': ['1']}, 1)
    fields_result = verify_circuit(fields_cert)
    fields = fields_result['parameter_contexts']
    assert len(fields) == 2 and fields[0]['field']['polynomial'] != fields[1]['field']['polynomial']
    assert {edge['coefficient']['context'] for edge in fields_result['rebuilt_graph']['branches']
            if edge['coefficient']['kind'] == 'algebraic'} == {'leaf_0', 'leaf_1'}
    assert fields_result['actual_storage'] == fields_result['reduced_target_degree'] == 1
    passed('two_nontrivial_independent_algebraic_fields_are_preserved')

    interval = json.loads((ROOT / 'certificates/historical_case_1.json').read_text())
    interval_result = verify_circuit(interval, interval['target'], 3)
    assert interval_result['status'] == 'PASS'
    interval_expression = series_node(certificate_node(interval), element_node('L', 2))
    exact_outer_target = {'P': [150, 980, 4008, 7012, 3472], 'Q': [175, 810, 1826, 1736]}
    interval_cert = make_composition(interval_expression, exact_outer_target, 4)
    result = verify_circuit(interval_cert, exact_outer_target, 4)
    assert result['actual_storage'] == result['reduced_target_degree'] == 4
    assert result['global_minimum_proved_by_degree']
    assert sum(edge['coefficient']['kind'] == 'interval' for edge in result['rebuilt_graph']['branches']) == 7
    assert all(leaf['result']['status'] == 'PASS' for leaf in result['leaf_results'])
    passed('interval_cubic_plus_outer_L_exact_degree_four_target_and_graph')

    # This certified resistor's center g=0.51 is not its exact root g=0.5.
    off_center = {'format': INTERVAL_FORMAT, 'target': {'P': ['2'], 'Q': ['1']},
                  'storage_budget': 0, 'branches': [{'type': 'g', 'nodes': [0, 1]}],
                  'center': ['51/100'], 'radii': ['1/50'], 'preconditioner': [['-1/2']]}
    off_cert = make_composition(series_node(certificate_node(off_center), element_node('R', 3)))
    off_result = verify_circuit(off_cert, {'P': [5], 'Q': [1]}, 0)
    ref = off_result['rebuilt_graph']['branches'][0]['coefficient']
    assert ref == {'kind': 'interval', 'context': 'leaf_0', 'index': 0}
    assert off_result['parameter_contexts'][0]['definition']['center'] == ['51/100']
    assert off_result['parameter_contexts'][0]['component_intervals'] == [['49/100', '53/100']]
    passed('interval_root_reference_is_preserved_and_center_is_not_a_component_value')

    mixed_context = make_composition(series_node(certificate_node(off_center), certificate_node(sqrt2)))
    mixed_result = verify_circuit(mixed_context, {'P': [5], 'Q': [1]}, 0)
    assert [context['kind'] for context in mixed_result['parameter_contexts']] == ['interval', 'algebraic']
    passed('interval_and_algebraic_contexts_can_coexist_without_field_conversion')

    inv_L, inv_L_result = exact_graph_case(frequency_invert_node(element_node('L', 2)))
    assert inv_L['target'] == {'P': ['2'], 'Q': ['0', '1']}
    assert inv_L_result['rebuilt_graph']['branches'][0]['type'] == 'c'
    assert inv_L_result['rebuilt_graph']['branches'][0]['coefficient']['value'] == '1/2'
    inv_RC, _ = exact_graph_case(frequency_invert_node(parallel_node(element_node('R', 2), element_node('C', 3))))
    assert inv_RC['target'] == {'P': ['0', '2'], 'Q': ['6', '1']}
    passed('frequency_inversion_common_degree_padding_for_both_unequal_degree_orientations')

    twice, twice_result = exact_graph_case(frequency_invert_node(frequency_invert_node(rational_expression)))
    assert twice['target'] == rational_cert['target']
    assert twice_result['rebuilt_graph'] == rational_result['rebuilt_graph']
    passed('frequency_inversion_is_an_involution_on_targets_and_graph_types')

    inv_interval = make_composition(frequency_invert_node(certificate_node(interval)))
    inv_result = verify_circuit(inv_interval,
                                {'P': list(reversed(interval['target']['P'])),
                                 'Q': list(reversed(interval['target']['Q']))}, 3)
    for original, transformed in zip(interval['branches'], inv_result['rebuilt_graph']['branches']):
        assert transformed['type'] == {'g': 'g', 'h': 'c', 'c': 'h'}[original['type']]
        assert transformed['coefficient']['kind'] == 'interval'
    assert inv_result['actual_storage'] == 3
    passed('frequency_inversion_retains_each_interval_parameter_reference')

    scaled = deepcopy(rational_cert)
    scaled['target'] = {key: [str(7 * F(value)) for value in rational_cert['target'][key]] for key in ('P', 'Q')}
    assert verify_circuit(scaled, rational_cert['target'])['status'] == 'PASS'
    passed('target_binding_accepts_exact_rational_function_equivalence')

    forged = deepcopy(rational_cert)
    forged['graph'] = {'nodes': [0, 1], 'branches': []}
    forged['rebuilt_graph'] = {'fabricated': True}
    forged['equations'] = []
    forged['actual_storage'] = 0
    forged['global_minimum_proved_by_degree'] = True
    forged_result = verify_circuit(forged)
    assert forged_result['rebuilt_graph'] == rational_result['rebuilt_graph']
    assert forged_result['actual_storage'] == rational_result['actual_storage']
    assert forged_result['global_minimum_proved_by_degree'] == rational_result['global_minimum_proved_by_degree']
    passed('claimed_graph_equations_counts_and_minimum_flag_are_ignored_and_rebuilt')

    # Target, budget, leaf proof, graph, syntax, and numerical corruption controls.
    rejected('declared_target_mismatch', lambda: verify_circuit(changed(rational_cert, ['target', 'P', 0], '987654321')))
    rejected('external_target_binding_mismatch', lambda: verify_circuit(rational_cert, {'P': [97], 'Q': [1]}))
    rejected('external_budget_binding_mismatch', lambda: verify_circuit(rational_cert, expected_budget=rational_cert['storage_budget'] + 1))
    rejected('declared_budget_below_physical_count', lambda: verify_circuit(changed(rational_cert, ['storage_budget'], 0)))
    rejected('boolean_declared_budget', lambda: verify_circuit(changed(rational_cert, ['storage_budget'], True)))
    rejected('boolean_expected_budget', lambda: verify_circuit(rational_cert, expected_budget=True))
    rejected('corrupted_interval_preconditioner', lambda: verify_circuit(changed(interval_cert, ['expression', 'children', 0, 'certificate', 'preconditioner', 0, 0], '0')))
    rejected('corrupted_interval_target', lambda: verify_circuit(changed(interval_cert, ['expression', 'children', 0, 'certificate', 'target', 'P', 0], '151')))
    rejected('corrupted_algebraic_leaf_coefficient', lambda: verify_circuit(changed(fields_cert, ['expression', 'children', 0, 'children', 0, 'certificate', 'branches', 0, 'coefficient', 1], '1/3')))
    rejected('corrupted_algebraic_root_interval', lambda: verify_circuit(changed(fields_cert, ['expression', 'children', 0, 'children', 0, 'certificate', 'field', 'interval'], ['3', '4'])))
    rejected('boolean_algebraic_node', lambda: verify_circuit(changed(image, ['branches', 0, 'nodes', 0], False)))
    rejected('duplicate_same_type_inside_legacy_leaf', lambda: make_composition(certificate_node(dict(image, branches=image['branches'] + [image['branches'][0]]))))
    rejected('nested_composition_certificate_leaf', lambda: certificate_node(rational_cert))
    rejected('generic_reciprocal_operation_is_absent', lambda: make_composition({'op': 'reciprocal', 'child': element_node('R', 2)}))
    rejected('unknown_operation', lambda: make_composition({'op': 'bridge_dual', 'child': element_node('R', 2)}))
    rejected('extra_expression_graph_payload', lambda: make_composition(dict(element_node('R', 2), graph={})))
    rejected('missing_expression', lambda: verify_composition_certificate({'format': FORMAT, 'target': {'P': [1], 'Q': [1]}, 'storage_budget': 0}))
    rejected('empty_children', lambda: make_composition({'op': 'series', 'children': []}))
    rejected('singleton_children', lambda: make_composition({'op': 'parallel', 'children': [element_node('R', 1)]}))
    rejected('non_mapping_child', lambda: make_composition({'op': 'series', 'children': [element_node('R', 1), 2]}))
    rejected('zero_element', lambda: element_node('R', 0))
    rejected('negative_element', lambda: element_node('L', -1))
    rejected('boolean_element', lambda: element_node('C', True))
    rejected('floating_element', lambda: element_node('R', 0.5))
    rejected('nonfinite_or_exponential_rational_text', lambda: element_node('R', '1e999999999'))
    rejected('zero_rational_denominator', lambda: element_node('R', '1/0'))
    rejected('empty_target_polynomial', lambda: verify_circuit(changed(rational_cert, ['target', 'P'], [])))
    rejected('zero_target_denominator', lambda: verify_circuit(changed(rational_cert, ['target', 'Q'], [0])))
    rejected('floating_target_coefficient', lambda: verify_circuit(changed(rational_cert, ['target', 'P', 0], 1.0)))
    rejected('make_composition_requested_target_mismatch', lambda: make_composition(element_node('R', 2), {'P': [3], 'Q': [1]}))
    rejected('unknown_dispatch_format', lambda: verify_circuit({'format': 'anything-else'}))

    deep = element_node('R', 1)
    for _ in range(cc.MAX_EXPRESSION_DEPTH + 1):
        deep = {'op': 'frequency_invert', 'child': deep}
    rejected('expression_depth_cap', lambda: make_composition(deep))
    full = element_node('R', 1)
    for _ in range(8):
        full = {'op': 'parallel', 'children': [deepcopy(full), deepcopy(full)]}
    rejected('expression_node_cap', lambda: make_composition(full))
    too_many_children = {'op': 'parallel', 'children': [element_node('R', 1)] * (cc.MAX_CHILDREN + 1)}
    rejected('child_arity_cap', lambda: make_composition(too_many_children))
    rejected('storage_budget_cap', lambda: verify_circuit(changed(rational_cert, ['storage_budget'], cc.MAX_STORAGE_BUDGET + 1)))
    rejected('input_integer_bit_cap', lambda: element_node('R', 1 << (cc.MAX_RATIONAL_BITS + 1)))
    rejected('input_rational_text_cap', lambda: element_node('R', '7' * (cc.MAX_RATIONAL_TEXT_LENGTH + 1)))
    large_denominator = 2 ** 2100 + 1
    output_too_large = series_node(element_node('R', F(1, large_denominator)),
                                   element_node('R', F(1, large_denominator + 2)))
    rejected('constructor_rejects_output_target_beyond_portable_input_limits',
             lambda: make_composition(output_too_large))
    rejected('target_degree_cap', lambda: verify_circuit(changed(rational_cert, ['target', 'P'], [1] * (cc.MAX_TARGET_DEGREE + 2))))
    rejected('field_degree_cap', lambda: verify_circuit(changed(image, ['field', 'polynomial'], [1] * (cc.MAX_FIELD_DEGREE + 2))))
    cycle = {'op': 'frequency_invert'}
    cycle['child'] = cycle
    rejected('cyclic_expression_rejected_before_recursion', lambda: make_composition(cycle))
    hidden_cycle = deepcopy(rational_cert)
    hidden_cycle['ignored_graph'] = hidden_cycle
    rejected('cycle_in_ignored_payload_rejected', lambda: verify_circuit(hidden_cycle))
    rejected('ignored_text_payload_is_still_bounded', lambda: verify_circuit(dict(rational_cert, metadata='x' * (cc.MAX_INPUT_STRING_LENGTH + 1))))
    with patch.object(cc, 'MAX_TOTAL_BRANCHES', 2):
        rejected('physical_branch_cap', lambda: make_composition(series_node(element_node('R', 1), element_node('R', 2), element_node('R', 3))))
    with patch.object(cc, 'MAX_GRAPH_NODES', 2):
        rejected('assembled_node_cap', lambda: make_composition(series_node(element_node('R', 1), element_node('R', 2))))
    with patch.object(cc, 'MAX_LEAF_OCCURRENCES', 1):
        rejected('leaf_occurrence_cap', lambda: make_composition(parallel_node(certificate_node(off_center), certificate_node(off_center))))
    with patch.object(cc, 'MAX_RESULT_COEFFICIENT_BITS', 3):
        rejected('computed_coefficient_bit_cap', lambda: make_composition(series_node(element_node('R', 7), element_node('R', 7))))
    with patch.object(cc, 'MAX_INPUT_ITEMS', 10):
        rejected('whole_input_item_cap', lambda: verify_circuit(rational_cert))
    with patch.object(cc, 'MAX_INPUT_TEXT_LENGTH', 10):
        rejected('whole_input_text_cap', lambda: verify_circuit(rational_cert))

    inputs = [Path(__file__), ROOT / 'src/composition_certificate.py',
              ROOT / 'src/algebraic_witness.py', ROOT / 'src/interval_certificate.py',
              ROOT / 'src/real_algebraic.py', ROOT / 'src/exact_polynomials.py',
              ROOT / 'certificates/image_baseline_cubic.json',
              ROOT / 'certificates/historical_case_1.json']
    return {
        'status': 'PASS', 'test_groups': len(positive) + len(rejection),
        'positive_groups': positive, 'rejection_controls': rejection,
        'independent_rational_nodal_cases': nodal_cases,
        'independent_rational_nodal_samples': nodal_samples,
        'scope': 'finite exact implementation checks and rejection controls; no search completeness or novelty claim',
        'input_sha256': {str(path.relative_to(ROOT)): hashlib.sha256(path.read_bytes()).hexdigest() for path in inputs},
        'elapsed_seconds': time.perf_counter() - start,
    }


if __name__ == '__main__':
    print(json.dumps(run(), indent=2))
