"""Author: Komorebi P. Exact interval certificates for positive RLC networks.

This module uses only the Python standard library and the package's rational
polynomial routines.  A certificate supplies a rational box and an invertible
rational preconditioner.  It does not supply trusted equations or derivatives.
The checker reconstructs all impedance coefficient equations from the graph.

Branch variables are conductance g=1/R, inverse inductance h=1/L, and
capacitance c=C, in the order of ``branches``.  Port 1 and ground 0 are fixed.
The checked root is an exact real vector, generally not its rational center.
"""
from __future__ import annotations

from fractions import Fraction as F
from itertools import combinations
from math import comb
import hashlib
import json

from exact_polynomials import rational
from real_algebraic import trim, gcd, divmod_poly, mul, sub, iszero


FORMAT = 'komorebi-rlc-interval-v1'
MAX_BRANCHES = 20
MAX_FOREST_SUBSETS = 200000


def _q(value):
    try:
        return rational(value)
    except (TypeError, ValueError, ZeroDivisionError, OverflowError) as exc:
        raise ValueError('An exact finite rational value is required') from exc


def _sequence(value, label):
    if not isinstance(value, (list, tuple)):
        raise ValueError(label + ' must be a list')
    return value


def _positive_integer(value, label, allow_zero=False):
    if not isinstance(value, int) or isinstance(value, bool):
        raise ValueError(label + ' must be an integer')
    if value < (0 if allow_zero else 1):
        raise ValueError(label + ' is out of range')
    return value


def reduce_target(P, Q):
    """Return coprime ascending Fraction coefficients, with monic Q."""
    P = trim([_q(x) for x in _sequence(P, 'P')])
    Q = trim([_q(x) for x in _sequence(Q, 'Q')])
    if not any(P) or not any(Q):
        raise ValueError('Nonzero finite target required')
    common = gcd(P, Q)
    P, rp = divmod_poly(P, common)
    Q, rq = divmod_poly(Q, common)
    if any(rp) or any(rq):
        raise ValueError('Internal target reduction failure')
    scale = Q[-1]
    return [p / scale for p in P], [q / scale for q in Q]


def validate_branches(branches):
    """Return normalized branches and all nodes of a connected physical graph."""
    branches = _sequence(branches, 'branches')
    if not branches or len(branches) > MAX_BRANCHES:
        raise ValueError('Unsupported branch count')
    normalized, seen, nodes = [], set(), {0, 1}
    for row in branches:
        if not isinstance(row, dict) or set(row) != {'type', 'nodes'}:
            raise ValueError('Each variable branch has exactly type and nodes')
        typ = row['type']
        if typ not in ('g', 'h', 'c'):
            raise ValueError('Unknown physical branch type')
        pair = _sequence(row['nodes'], 'branch nodes')
        if len(pair) != 2:
            raise ValueError('Every branch needs two nodes')
        a, b = pair
        _positive_integer(a, 'Node', allow_zero=True)
        _positive_integer(b, 'Node', allow_zero=True)
        if a == b:
            raise ValueError('Self loops are not supported')
        a, b = sorted((a, b))
        key = (typ, a, b)
        if key in seen:
            raise ValueError('Duplicate same-type branches must be merged')
        seen.add(key)
        nodes.update((a, b))
        normalized.append({'type': typ, 'nodes': [a, b]})
    reached = {0}
    while True:
        more = reached.copy()
        for row in normalized:
            a, b = row['nodes']
            if a in reached:
                more.add(b)
            if b in reached:
                more.add(a)
        if more == reached:
            break
        reached = more
    if reached != nodes:
        raise ValueError('All physical material and the input must connect to ground')
    return normalized, sorted(nodes)


def _add_scaled(destination, source, coefficient):
    if not coefficient:
        return
    for monomial, value in source.items():
        value = destination.get(monomial, F(0)) + coefficient * value
        if value:
            destination[monomial] = value
        else:
            destination.pop(monomial, None)


def _forest_components(nodes, branches, selected):
    parent = {a: a for a in nodes}

    def root(a):
        while parent[a] != a:
            a = parent[a]
        return a

    for k in selected:
        a, b = branches[k]['nodes']
        ra, rb = root(a), root(b)
        if ra == rb:
            return None
        parent[ra] = rb
    return {a: root(a) for a in nodes}


def graph_polynomials(branches):
    """Rebuild N(s,x), D(s,x) for Z=N/D from rooted forests and trees.

    Outputs are ascending coefficient lists of sparse multivariate polynomials.
    A sparse polynomial maps an exponent tuple to a Fraction.  All branch
    variables are independent.  Multiplying the Laplacian determinants by
    s**number_of_inductors clears negative powers and gives degrees at most q.
    """
    branches, nodes = validate_branches(branches)
    m, vertices = len(branches), len(nodes)
    count = sum(comb(m, k) for k in (vertices - 2, vertices - 1) if 0 <= k <= m)
    if count > MAX_FOREST_SUBSETS:
        raise ValueError('Exact forest enumeration cap exceeded')
    q = sum(row['type'] != 'g' for row in branches)
    inductors = sum(row['type'] == 'h' for row in branches)
    powers = [{'h': -1, 'g': 0, 'c': 1}[row['type']] for row in branches]
    N, D = [{} for _ in range(q + 1)], [{} for _ in range(q + 1)]
    for size, destination in ((vertices - 1, D), (vertices - 2, N)):
        for selected in combinations(range(m), size):
            components = _forest_components(nodes, branches, selected)
            if components is None:
                continue
            if destination is N and components[0] == components[1]:
                continue
            # A forest with V-1 edges is a tree.  A forest with V-2 edges
            # has exactly two components; separating 0 and 1 roots both.
            exponent = inductors + sum(powers[k] for k in selected)
            if not 0 <= exponent <= q:
                raise ValueError('Internal Laplace-degree bound failure')
            monomial = tuple(int(k in selected) for k in range(m))
            destination[exponent][monomial] = destination[exponent].get(monomial, F(0)) + 1
    if not any(N) or not any(D):
        raise ValueError('No rooted forest or spanning tree found')
    return {'branches': branches, 'nodes': nodes, 'variables': m,
            'storage_count': q, 'numerator': N, 'denominator': D,
            'forest_subsets_examined': count}


def differentiate(poly, variable):
    out = {}
    for monomial, value in poly.items():
        power = monomial[variable]
        if power:
            reduced = list(monomial)
            reduced[variable] -= 1
            key = tuple(reduced)
            out[key] = out.get(key, F(0)) + power * value
    return {key: value for key, value in out.items() if value}


def build_coefficient_system(branches, P, Q, fixed_parameters=None):
    """Build every coefficient of Q*N-P*D, with a canonical reduced target.

    No equation is selected, dropped, or replaced by an approximate sample.
    The coefficient count is reduced_target_degree + storage_count + 1.
    Optional fixed-parameter equations are appended, never substituted for
    impedance equations.  Their indices and positive exact values are checked.
    """
    P, Q = reduce_target(P, Q)
    graph = graph_polynomials(branches)
    n = max(len(P), len(Q)) - 1
    equations = [{} for _ in range(n + graph['storage_count'] + 1)]
    for degree, poly in enumerate(graph['numerator']):
        for j, coefficient in enumerate(Q):
            _add_scaled(equations[degree + j], poly, coefficient)
    for degree, poly in enumerate(graph['denominator']):
        for j, coefficient in enumerate(P):
            _add_scaled(equations[degree + j], poly, -coefficient)
    coefficient_count = len(equations)
    fixed = []
    seen = set()
    if fixed_parameters is not None:
        for row in _sequence(fixed_parameters, 'fixed_parameters'):
            if not isinstance(row, dict) or set(row) != {'index', 'value'}:
                raise ValueError('Each fixed parameter has exactly index and value')
            index = _positive_integer(row['index'], 'Fixed parameter index', allow_zero=True)
            if index >= graph['variables'] or index in seen:
                raise ValueError('Invalid or repeated fixed parameter index')
            value = _q(row['value'])
            if value <= 0:
                raise ValueError('Fixed physical parameters must be positive')
            seen.add(index)
            monomial = tuple(int(i == index) for i in range(graph['variables']))
            equations.append({monomial: F(1), (0,) * graph['variables']: -value})
            fixed.append({'index': index, 'value': value})
    graph.update({'equations': equations,
                  'jacobian': [[differentiate(poly, j) for j in range(graph['variables'])]
                               for poly in equations],
                  'reduced_target_degree': n, 'target': {'P': P, 'Q': Q},
                  'coefficient_equation_count': coefficient_count,
                  'fixed_parameters': fixed})
    return graph


def evaluate_polynomial(poly, values):
    values = [_q(x) for x in values]
    result = F(0)
    for monomial, coefficient in poly.items():
        if len(monomial) != len(values):
            raise ValueError('Polynomial evaluation dimension mismatch')
        term = coefficient
        for power, value in zip(monomial, values):
            if power:
                term *= value ** power
        result += term
    return result


def evaluate_system(system, values):
    return [evaluate_polynomial(poly, values) for poly in system['equations']]


def evaluate_jacobian(system, values):
    return [[evaluate_polynomial(poly, values) for poly in row]
            for row in system['jacobian']]


def _interval_multiply(left, right):
    products = [a * b for a in left for b in right]
    return min(products), max(products)


def _interval_power(interval, exponent):
    if not exponent:
        return F(1), F(1)
    a, b = interval
    if exponent % 2:
        return a ** exponent, b ** exponent
    low = F(0) if a <= 0 <= b else min(a ** exponent, b ** exponent)
    return low, max(a ** exponent, b ** exponent)


def interval_evaluate_polynomial(poly, intervals):
    intervals = [tuple(map(_q, interval)) for interval in intervals]
    if any(len(interval) != 2 or interval[0] > interval[1] for interval in intervals):
        raise ValueError('Ordered interval endpoints required')
    low = high = F(0)
    for monomial, coefficient in poly.items():
        if len(monomial) != len(intervals):
            raise ValueError('Interval polynomial dimension mismatch')
        term = (coefficient, coefficient)
        for exponent, interval in zip(monomial, intervals):
            if exponent:
                term = _interval_multiply(term, _interval_power(interval, exponent))
        low += term[0]
        high += term[1]
    return low, high


def invert_matrix(matrix):
    """Exact Gauss-Jordan inversion.  Singularity is rejected, never rounded."""
    matrix = _sequence(matrix, 'matrix')
    n = len(matrix)
    if n == 0 or any(not isinstance(row, (list, tuple)) or len(row) != n for row in matrix):
        raise ValueError('A nonempty square matrix is required')
    A = [[_q(x) for x in row] + [F(i == j) for j in range(n)] for i, row in enumerate(matrix)]
    for column in range(n):
        pivot = next((row for row in range(column, n) if A[row][column]), None)
        if pivot is None:
            raise ValueError('Singular rational matrix')
        A[column], A[pivot] = A[pivot], A[column]
        value = A[column][column]
        A[column] = [x / value for x in A[column]]
        for row in range(n):
            if row == column:
                continue
            value = A[row][column]
            if value:
                A[row] = [a - value * b for a, b in zip(A[row], A[column])]
    return [row[n:] for row in A]


def _system_digest(system):
    payload = [[[str(c), list(m)] for m, c in sorted(poly.items())] for poly in system['equations']]
    return hashlib.sha256(json.dumps(payload, separators=(',', ':')).encode()).hexdigest()


def verify_interval_circuit(cert, expected_target=None, expected_budget=None):
    """Independently check exact root existence and positivity in a rational box.

    Strict self-mapping plus a weighted infinity-norm contraction establishes
    one unique root in the supplied box.  The root exactly realizes the target.
    A root is not asserted to equal the certificate's rational center.
    """
    if not isinstance(cert, dict) or cert.get('format') != FORMAT:
        raise ValueError('Unknown interval certificate format')
    target = cert.get('target')
    if not isinstance(target, dict) or 'P' not in target or 'Q' not in target:
        raise ValueError('Missing target')
    system = build_coefficient_system(cert.get('branches'), target['P'], target['Q'],
                                      cert.get('fixed_parameters'))
    P, Q = system['target']['P'], system['target']['Q']
    if expected_target is not None:
        if not isinstance(expected_target, dict):
            raise ValueError('Expected target must be a mapping')
        expected_P, expected_Q = reduce_target(expected_target['P'], expected_target['Q'])
        if not iszero(sub(mul(P, expected_Q), mul(Q, expected_P))):
            raise ValueError('Target binding mismatch')
    budget = _positive_integer(cert.get('storage_budget'), 'Storage budget', allow_zero=True)
    if expected_budget is not None:
        _positive_integer(expected_budget, 'Expected budget', allow_zero=True)
        if budget != expected_budget:
            raise ValueError('Budget binding mismatch')
    if system['storage_count'] > budget:
        raise ValueError('Reactive budget exceeded')
    m = system['variables']
    if len(system['equations']) != m:
        raise ValueError('A square full coefficient system is required')
    center = [_q(x) for x in _sequence(cert.get('center'), 'center')]
    radii = [_q(x) for x in _sequence(cert.get('radii'), 'radii')]
    if len(center) != m or len(radii) != m:
        raise ValueError('Box dimension mismatch')
    if any(r <= 0 for r in radii):
        raise ValueError('Every radius must be strictly positive')
    if any(c - r <= 0 for c, r in zip(center, radii)):
        raise ValueError('The entire component box must be strictly positive')
    Y = _sequence(cert.get('preconditioner'), 'preconditioner')
    if len(Y) != m or any(not isinstance(row, (list, tuple)) or len(row) != m for row in Y):
        raise ValueError('Preconditioner dimension mismatch')
    Y = [[_q(x) for x in row] for row in Y]
    invert_matrix(Y)  # A fixed point of x-YF(x) is a root only if Y is invertible.
    F_center = evaluate_system(system, center)
    correction = [abs(sum((y * f for y, f in zip(row, F_center)), F(0))) for row in Y]
    box = [(c - r, c + r) for c, r in zip(center, radii)]
    zero = (0,) * m
    bounds = []
    for i in range(m):
        row_bounds = []
        for j in range(m):
            # Combine the preconditioned polynomial *before* interval
            # evaluation.  This keeps algebraically exact cancellations.
            derivative = {zero: F(1)} if i == j else {}
            for k in range(m):
                _add_scaled(derivative, system['jacobian'][k][j], -Y[i][k])
            a, b = interval_evaluate_polynomial(derivative, box)
            row_bounds.append(max(abs(a), abs(b)))
        bounds.append(row_bounds)
    weighted_rows = [sum((b * r for b, r in zip(row, radii)), F(0)) / radii[i]
                     for i, row in enumerate(bounds)]
    contraction = max(weighted_rows)
    if contraction >= 1:
        raise ValueError('Weighted contraction bound is not strictly below one')
    image_radii = [correction[i] + weighted_rows[i] * radii[i] for i in range(m)]
    margins = [r - image for r, image in zip(radii, image_radii)]
    if any(margin <= 0 for margin in margins):
        raise ValueError('Strict interval self-mapping failed')
    minimum = system['storage_count'] == system['reduced_target_degree']
    return {'status': 'PASS',
            'arithmetic': 'Python standard-library int and Fraction only',
            'certificate_kind': 'exact rational box contraction for the rebuilt full graph identity',
            'root_semantics': 'one unique exact real component vector in the closed box satisfying the full identity and any declared fixed parameters',
            'actual_storage': system['storage_count'],
            'resistors': sum(row['type'] == 'g' for row in system['branches']),
            'reduced_target_degree': system['reduced_target_degree'],
            'global_minimum_proved_by_degree': minimum,
            'variable_count': m, 'coefficient_equation_count': system['coefficient_equation_count'],
            'equation_count': len(system['equations']),
            'fixed_parameter_count': len(system['fixed_parameters']),
            'equations_sha256': _system_digest(system),
            'preconditioner_invertible': True,
            'weighted_contraction_bound': str(contraction),
            'center_correction_bounds': list(map(str, correction)),
            'self_map_margins': list(map(str, margins)),
            'component_intervals': [[str(a), str(b)] for a, b in box],
            'forest_subsets_examined': system['forest_subsets_examined']}


if __name__ == '__main__':
    import argparse
    from pathlib import Path
    parser = argparse.ArgumentParser(description='Replay an exact RLC interval certificate')
    parser.add_argument('certificate', type=Path)
    args = parser.parse_args()
    data = json.loads(args.certificate.read_text())
    print(json.dumps(verify_interval_circuit(data), indent=2))
