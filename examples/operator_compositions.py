#!/usr/bin/env python3
"""Exact finite calculations for docs/operators/COMPOSITION.md.

Run: python -B examples/operator_compositions.py
An optional --json PATH writes a receipt with rational values encoded as strings.
Importing this module or running without --json writes no files. These six
recipes are separate from the reference chapters and imported catalog fixtures.
"""
from __future__ import annotations

import argparse
from fractions import Fraction as Q
import json
from pathlib import Path
from typing import Iterable, NamedTuple

Scalar = int | Q
Vector = tuple[Q, ...]
Matrix = tuple[Vector, ...]


def rational(value: Scalar) -> Q:
    if isinstance(value, bool) or not isinstance(value, (int, Q)):
        raise TypeError('exact inputs must be integers or Fraction values')
    return Q(value)


def vector(values: Iterable[Scalar]) -> Vector:
    return tuple(rational(value) for value in values)


def matrix(rows: Iterable[Iterable[Scalar]]) -> Matrix:
    result = tuple(vector(row) for row in rows)
    if not result or not result[0] or any(len(row) != len(result[0]) for row in result):
        raise ValueError('a nonempty rectangular matrix is required')
    return result


def dot(left: Vector, right: Vector) -> Q:
    if len(left) != len(right):
        raise ValueError('vector dimensions differ')
    return sum((a * b for a, b in zip(left, right)), Q(0))


def transpose(value: Matrix) -> Matrix:
    return tuple(zip(*value))


def matmul(left: Matrix, right: Matrix) -> Matrix:
    if len(left[0]) != len(right):
        raise ValueError('matrix product dimensions differ')
    columns = transpose(right)
    return tuple(tuple(dot(row, column) for column in columns) for row in left)


def matvec(value: Matrix, argument: Vector) -> Vector:
    return tuple(dot(row, argument) for row in value)


def add(left: Matrix, right: Matrix) -> Matrix:
    if (len(left), len(left[0])) != (len(right), len(right[0])):
        raise ValueError('matrix sum dimensions differ')
    return tuple(tuple(a + b for a, b in zip(row, other)) for row, other in zip(left, right))


def scale(coefficient: Scalar, value: Matrix) -> Matrix:
    coefficient = rational(coefficient)
    return tuple(tuple(coefficient * entry for entry in row) for row in value)


def subtract(left: Matrix, right: Matrix) -> Matrix:
    return add(left, scale(-1, right))


def inverse2(value: Matrix) -> Matrix:
    if (len(value), len(value[0])) != (2, 2):
        raise ValueError('this inverse requires a two-by-two matrix')
    a, b = value[0]
    c, d = value[1]
    determinant = a * d - b * c
    if not determinant:
        raise ValueError('matrix is singular')
    return scale(Q(1) / determinant, matrix(((d, -b), (-c, a))))


def require(condition: bool, assertion: str) -> None:
    """Keep receipt checks active even when Python is run with optimization."""
    if not condition:
        raise AssertionError(assertion)


def middle_chart_bridge() -> dict:
    t = matrix(((1, 2), (0, 1)))
    u = matrix(((1, 0), (1, 1)))
    c = matrix(((2, 0), (0, 1)))
    d = matrix(((1, 1), (0, 1)))
    x = vector((1, 2))
    stored_t = matmul(c, t)
    stored_u = matmul(u, inverse2(d))
    bridge = matmul(d, inverse2(c))
    bridged_composite = matmul(matmul(stored_u, bridge), stored_t)
    physical_composite = matmul(u, t)
    without_bridge = matmul(stored_u, stored_t)
    first_coordinates = matvec(stored_t, x)
    second_coordinates = matvec(bridge, first_coordinates)
    output = matvec(stored_u, second_coordinates)
    wrong_output = matvec(without_bridge, x)
    require(bridged_composite == physical_composite, 'the bridged matrices must agree exactly')
    require(output == matvec(physical_composite, x), 'the displayed path must give the physical output')
    require(wrong_output != output, 'omitting this bridge must change the displayed output')
    return {
        'domain': 'Q^2; invertible middle charts; unchanged initial and final coordinates',
        'inputs': {'T': t, 'U': u, 'C': c, 'D': d, 'x': x},
        'stored_T': stored_t, 'stored_U': stored_u, 'bridge': bridge,
        'physical_intermediate': matvec(t, x),
        'first_coordinates': first_coordinates, 'second_coordinates': second_coordinates,
        'bridged_composite': bridged_composite, 'physical_composite': physical_composite,
        'output': output, 'without_bridge_composite': without_bridge,
        'without_bridge_output': wrong_output,
    }


def coarse_defect() -> dict:
    q = matrix(((1, 1),))
    t = matrix(((2, 0), (0, 3)))
    u = matrix(((3, 0), (0, 2)))
    bar_t, bar_u = Q(2), Q(3)
    x = vector((1, 2))
    e_t = subtract(matmul(q, t), scale(bar_t, q))
    e_u = subtract(matmul(q, u), scale(bar_u, q))
    second_contribution = matmul(e_u, t)
    first_contribution = scale(bar_u, e_t)
    composed_defect = add(second_contribution, first_contribution)
    composite = matmul(u, t)
    direct_defect = subtract(matmul(q, composite), scale(bar_u * bar_t, q))
    require(composed_defect == direct_defect == matrix(((0, 0),)), 'the transported defects must cancel')
    kernel_vector = vector((1, -1))
    kernel_images = {'T': matvec(q, matvec(t, kernel_vector))[0],
                     'U': matvec(q, matvec(u, kernel_vector))[0]}
    require(matvec(q, kernel_vector) == vector((0,)), 'the witness must lie in the observation kernel')
    require(all(value != 0 for value in kernel_images.values()), 'neither stage may descend exactly')
    states = (x, matvec(t, x), matvec(composite, x))
    observed = tuple(matvec(q, state)[0] for state in states)
    candidate = (observed[0], bar_t * observed[0], bar_u * bar_t * observed[0])

    independent_candidate = Q(5)
    extra_term = scale(bar_u * bar_t - independent_candidate, q)
    independent_defect = subtract(matmul(q, composite), scale(independent_candidate, q))
    require(independent_defect == add(composed_defect, extra_term), 'an independent coarse composite needs its discrepancy term')

    variant_u = matrix(((3, 0), (0, 4)))
    variant_e_u = subtract(matmul(q, variant_u), scale(bar_u, q))
    variant_second = matmul(variant_e_u, t)
    variant_defect = add(variant_second, first_contribution)
    variant_direct = subtract(matmul(q, matmul(variant_u, t)), scale(bar_u * bar_t, q))
    naive_defect = add(variant_e_u, e_t)
    require(variant_defect == variant_direct, 'the noncancelling variant must obey the transported law')
    require(matvec(variant_defect, x) != matvec(naive_defect, x), 'plain defect addition must fail in the variant')
    return {
        'domain': 'Q^2 to Q; coordinate-sum observation and fixed scalar candidates',
        'inputs': {'q': q, 'T': t, 'U': u, 'bar_T': bar_t, 'bar_U': bar_u, 'x': x},
        'E_T': e_t, 'E_U': e_u, 'transported_E_U': second_contribution,
        'propagated_E_T': first_contribution, 'E_UT': composed_defect,
        'direct_E_UT': direct_defect, 'composite': composite,
        'states': states, 'observed_summaries': observed, 'coarse_summaries': candidate,
        'kernel_vector': kernel_vector, 'kernel_image_summaries': kernel_images,
        'independent_composite': {
            'candidate': independent_candidate, 'extra_term': extra_term,
            'defect_row': independent_defect, 'defect_at_x': matvec(independent_defect, x)[0],
        },
        'variant': {
            'U': variant_u, 'bar_U': bar_u, 'E_U': variant_e_u,
            'transported_E_U': variant_second, 'E_UT': variant_defect,
            'direct_E_UT': variant_direct, 'defect_at_x': matvec(variant_defect, x)[0],
            'naive_E_UT': naive_defect, 'naive_defect_at_x': matvec(naive_defect, x)[0],
        },
    }


def metric_defect() -> dict:
    identity = matrix(((1, 0), (0, 1)))
    t = matrix(((2, 0), (0, 1)))
    u = matrix(((Q(1, 2), 0), (0, 3)))
    v = vector((1, 1))
    e_t = subtract(matmul(transpose(t), t), identity)
    e_u = subtract(matmul(transpose(u), u), identity)
    pullback = matmul(matmul(transpose(t), e_u), t)
    composite = matmul(u, t)
    direct_defect = subtract(matmul(transpose(composite), composite), identity)
    composed_defect = add(e_t, pullback)
    naive_defect = add(e_t, e_u)
    states = (v, matvec(t, v), matvec(composite, v))
    squared_norms = tuple(dot(state, state) for state in states)
    changes = (squared_norms[1] - squared_norms[0], squared_norms[2] - squared_norms[1])
    evaluated_changes = (dot(v, matvec(e_t, v)), dot(states[1], matvec(e_u, states[1])))
    total_change = dot(v, matvec(composed_defect, v))
    naive_change = dot(v, matvec(naive_defect, v))
    require(composed_defect == direct_defect, 'the metric defect must include the pullback')
    require(changes == evaluated_changes, 'each signed change must use the vector at that stage')
    require(sum(changes, Q(0)) == total_change == squared_norms[-1] - squared_norms[0], 'the signed changes must telescope')
    require(naive_change != total_change, 'the untransported metric defects must give a different answer')
    return {
        'domain': 'Q^2 with Euclidean metrics; signed changes in squared norm',
        'inputs': {'T': t, 'U': u, 'v': v, 'metric': identity},
        'E_T': e_t, 'E_U': e_u, 'pulled_back_E_U': pullback,
        'E_UT': composed_defect, 'direct_E_UT': direct_defect, 'naive_E_UT': naive_defect,
        'states': states, 'squared_norms': squared_norms, 'stage_changes': changes,
        'evaluated_stage_changes': evaluated_changes, 'total_change': total_change,
        'naive_change': naive_change,
    }


def multiply_polynomials(left: Vector, right: Vector) -> Vector:
    result = [Q(0)] * (len(left) + len(right) - 1)
    for i, a in enumerate(left):
        for j, b in enumerate(right):
            result[i + j] += a * b
    return tuple(result)


def falling_polynomial(degree: int) -> Vector:
    result = vector((1,))
    for root in range(degree):
        result = multiply_polynomials(result, vector((-root, 1)))
    return result


def integrate_polynomial(coefficients: Vector) -> Q:
    """Integrate ordinary-power coefficients exactly on [0, 1], with density 1."""
    return sum((coefficient / (degree + 1) for degree, coefficient in enumerate(coefficients)), Q(0))


def moment_covector() -> dict:
    b = matrix(((1, 0, 0, 0), (0, 1, -1, 2), (0, 0, 1, -3), (0, 0, 0, 1)))
    ordinary_moments = vector((1, Q(1, 2), Q(1, 3), Q(1, 4)))
    falling_moments = matmul((ordinary_moments,), b)[0]
    # Construct the basis from products, independently of the stored matrix B.
    polynomials = tuple(falling_polynomial(degree) for degree in range(4))
    columns = tuple(poly + (Q(0),) * (4 - len(poly)) for poly in polynomials)
    basis_integrals = tuple(integrate_polynomial(poly) for poly in polynomials)
    require(columns == transpose(b), 'the synthesis matrix must contain the declared basis polynomials')
    require(falling_moments == basis_integrals, 'every transported moment must equal independent polynomial integration')
    a = vector((0, 1, 3, 1))
    c = matvec(b, a)
    correct_integral = dot(falling_moments, a)
    wrong_integral = dot(ordinary_moments, a)
    require(correct_integral == dot(ordinary_moments, c) == integrate_polynomial(c), 'all correctly typed evaluations must agree')
    require(wrong_integral != correct_integral, 'the unchanged moment row must fail on these stored coefficients')
    return {
        'domain': 'Q[x] of degree at most 3; integration on [0, 1] with density 1',
        'basis_matrix': b, 'basis_polynomials': polynomials, 'ordinary_moments': ordinary_moments,
        'falling_moments': falling_moments, 'independent_basis_integrals': basis_integrals,
        'falling_coefficients': a, 'ordinary_coefficients': c,
        'integral': correct_integral, 'unchanged_row_integral': wrong_integral,
    }


def integrate_atoms(atoms: tuple, integrand) -> Q:
    return sum((weight * rational(integrand(point)) for point, weight in atoms), Q(0))


def marginal(atoms: tuple, coordinate: int) -> tuple:
    nodes = sorted({point[coordinate] for point, _ in atoms})
    return tuple((node, sum((weight for point, weight in atoms if point[coordinate] == node), Q(0)))
                 for node in nodes)


def finite_pushforward() -> dict:
    mu = ((Q(0), Q(1, 2)), (Q(1), Q(1, 2)))
    phi = lambda t: 1 + 2 * t
    nu = tuple((phi(node), weight) for node, weight in mu)
    pushforward_integral = integrate_atoms(nu, lambda y: y * y)
    pullback_integral = integrate_atoms(mu, lambda t: phi(t) ** 2)
    product_atoms = tuple(((y, z), wy * wz) for y, wy in nu for z, wz in nu)
    product_contributions = tuple(weight * y * z for (y, z), weight in product_atoms)
    product_integral = integrate_atoms(product_atoms, lambda point: point[0] * point[1])
    mean = integrate_atoms(nu, lambda z: z)
    partial_integrals = tuple((y, integrate_atoms(nu, lambda z: y * z)) for y, _ in nu)
    iterated_integral = sum((weight * partial for (_, weight), (_, partial) in zip(nu, partial_integrals)), Q(0))
    correlated = tuple(((phi(node), phi(node)), weight) for node, weight in mu)
    correlated_marginals = (marginal(correlated, 0), marginal(correlated, 1))
    correlated_integral = integrate_atoms(correlated, lambda point: point[0] * point[1])
    require(pushforward_integral == pullback_integral, 'the finite pushforward and pullback sums must agree')
    require(all(partial == mean * y for y, partial in partial_integrals), 'partial integration must retain the first coordinate')
    require(sum(product_contributions, Q(0)) == product_integral == iterated_integral, 'the four product atoms must agree with iterated integration')
    require(correlated_marginals == (nu, nu), 'the correlated control must keep both marginals')
    require(correlated_integral != product_integral, 'matching marginals must not erase this correlation')
    return {
        'domain': 'finite rational atomic probability measures; a declared product and a correlated control',
        'source_atoms': mu, 'pushforward_atoms': nu,
        'pushforward_integral': pushforward_integral, 'pullback_integral': pullback_integral,
        'product_atoms': product_atoms, 'product_contributions': product_contributions,
        'partial_integral_slope': mean, 'partial_integrals': partial_integrals,
        'product_integral': product_integral, 'iterated_integral': iterated_integral,
        'correlated_atoms': correlated, 'correlated_marginals': correlated_marginals,
        'correlated_integral': correlated_integral,
    }


class FilterState(NamedTuple):
    previous_input: Q = Q(0)
    previous_output: Q = Q(0)


def filter_chunk(samples: Iterable[Scalar], state: FilterState = FilterState()) -> tuple[Vector, FilterState]:
    """Run the declared recurrence; retain both history values, including on empty input."""
    previous_input = rational(state.previous_input)
    previous_output = rational(state.previous_output)
    output = []
    for sample in samples:
        current_input = rational(sample)
        current_output = current_input + Q(1, 2) * previous_input + Q(1, 3) * previous_output
        output.append(current_output)
        previous_input, previous_output = current_input, current_output
    return tuple(output), FilterState(previous_input, previous_output)


def filter_state() -> dict:
    samples = vector((2, 1, 0, 0))
    output, final_state = filter_chunk(samples)
    split_runs = []
    for cut in range(len(samples) + 1):
        left, saved_state = filter_chunk(samples[:cut])
        right, resumed_final_state = filter_chunk(samples[cut:], saved_state)
        require(left + right == output, f'full-state continuation must preserve outputs at cut {cut}')
        require(resumed_final_state == final_state, f'full-state continuation must preserve final state at cut {cut}')
        split_runs.append({'cut': cut, 'left_output': left, 'saved_state': saved_state._asdict(),
                           'right_output': right, 'final_state': resumed_final_state._asdict()})
    left, saved_state = filter_chunk(samples[:2])
    right, _ = filter_chunk(samples[2:], saved_state)
    reset, _ = filter_chunk(samples[2:])
    output_only, _ = filter_chunk(samples[2:], FilterState(Q(0), saved_state.previous_output))
    input_only, _ = filter_chunk(samples[2:], FilterState(saved_state.previous_input, Q(0)))
    require(all(control != right for control in (reset, output_only, input_only)), 'each cut-two missing-history control must change the output')
    nonzero_state = FilterState(Q(7, 5), Q(-2, 7))
    empty_output, empty_final_state = filter_chunk((), nonzero_state)
    require(empty_output == () and empty_final_state == nonzero_state, 'empty input must preserve a supplied nonzero state')
    return {
        'domain': 'the declared four-input rational stream; exact finite execution, without a stability claim',
        'recurrence_coefficients': {'current_input': Q(1), 'previous_input': Q(1, 2), 'previous_output': Q(1, 3)},
        'input': samples, 'initial_state': FilterState()._asdict(), 'output': output,
        'final_state': final_state._asdict(), 'split_runs': tuple(split_runs),
        'displayed_cut': 2, 'left_output': left, 'continuation_state': saved_state._asdict(),
        'continued_output': right, 'reset_output': reset,
        'output_history_only': output_only, 'input_history_only': input_only,
        'empty_chunk': {'supplied_state': nonzero_state._asdict(), 'output': empty_output,
                        'returned_state': empty_final_state._asdict()},
    }


RECIPES = {
    'middle-chart-bridge': middle_chart_bridge,
    'coarse-defect': coarse_defect,
    'metric-defect': metric_defect,
    'moment-covector': moment_covector,
    'finite-pushforward': finite_pushforward,
    'filter-state': filter_state,
}


def run_recipes() -> dict:
    """Return exact results after each recipe's identities and controls pass."""
    return {name: {'status': 'PASS', **recipe()} for name, recipe in RECIPES.items()}


def json_rational(value):
    if isinstance(value, Q):
        return str(value)
    raise TypeError(f'cannot serialize {type(value).__name__} as an exact result')


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--json', type=Path, help='write an exact result receipt to this explicit path')
    args = parser.parse_args(argv)
    results = run_recipes()
    if args.json is not None:
        receipt = {
            'suite': 'Operator guide composition recipes',
            'arithmetic': 'integers and fractions.Fraction',
            'rational_encoding': 'exact strings: integer or numerator/denominator',
            'scope': 'Six declared finite examples and their controls; no general numerical stability, whole-library execution, or Lean verification claim.',
            'recipe_count': len(results), 'recipes': results,
        }
        args.json.parent.mkdir(parents=True, exist_ok=True)
        args.json.write_text(json.dumps(receipt, default=json_rational, ensure_ascii=False, indent=2, allow_nan=False) + '\n', encoding='utf-8')
    for name in results:
        print('PASS', name)
    print(f'RESULT {len(results)}/{len(RECIPES)} finite composition recipes passed')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
