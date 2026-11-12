"""Author: Komorebi P. Exact proof-carrying composition of positive RLC graphs.

The trusted inputs at a leaf are checked by the existing algebraic or rational
interval checker.  Internal nodes use exact rational impedance algebra and
disjoint terminal gluing.  Independent algebraic fields and interval roots stay
in separate, occurrence-specific parameter contexts; no primitive-element
conversion or numerical component approximation is performed.

Wire format: ``komorebi-rlc-composition-v1``.  Polynomial arrays are ascending.
Element values are physical R, L, or C, not branch admittance coefficients.
Only series, parallel, and frequency inversion are supported.  In particular,
there is no unproved graph operation for reciprocal impedance.

All arithmetic and dependencies used by this module are standard-library only.
The explicit caps below are conservative acceptance limits, not completeness
claims.  Extra root-level metadata, graphs, and equations are never trusted.
"""
from __future__ import annotations

from fractions import Fraction
import hashlib
import json
import re

from algebraic_witness import verify_algebraic_circuit
from interval_certificate import verify_interval_circuit, reduce_target
from real_algebraic import add, mul


FORMAT = 'komorebi-rlc-composition-v1'
ALGEBRAIC_FORMAT = 'komorebi-algebraic-circuit-v1'
INTERVAL_FORMAT = 'komorebi-rlc-interval-v1'
LEAF_FORMATS = (ALGEBRAIC_FORMAT, INTERVAL_FORMAT)

# These bounds also apply to the dispatcher before invoking a legacy checker.
MAX_EXPRESSION_DEPTH = 32
MAX_EXPRESSION_NODES = 256
MAX_CHILDREN = 64
MAX_LEAF_OCCURRENCES = 64
MAX_TOTAL_BRANCHES = 256
MAX_GRAPH_NODES = 257
MAX_STORAGE_BUDGET = 256
MAX_TARGET_DEGREE = 64
MAX_ALGEBRAIC_BRANCHES = 64
MAX_FIELD_DEGREE = 32
MAX_COMPONENT_POLYNOMIAL_DEGREE = 64
MAX_RATIONAL_BITS = 4096
MAX_RESULT_COEFFICIENT_BITS = 65536
MAX_RATIONAL_TEXT_LENGTH = 2500
MAX_INPUT_ITEMS = 100000
MAX_INPUT_DEPTH = 128
MAX_INPUT_STRING_LENGTH = 16384
MAX_INPUT_TEXT_LENGTH = 4000000

_RATIONAL_TEXT = re.compile(r'[+-]?[0-9]+(?:/[+-]?[0-9]+)?\Z')


def _preflight(value):
    """Bound the complete supplied object, including ignored metadata.

    Reused objects are counted once *per occurrence*, while cycles are rejected.
    This is deliberately independent of the expression walker: a huge or cyclic
    object cannot hide in an untrusted graph/equations/metadata field.
    """
    active = set()
    items = 0
    text_length = 0

    def visit(obj, depth):
        nonlocal items, text_length
        items += 1
        if items > MAX_INPUT_ITEMS or depth > MAX_INPUT_DEPTH:
            raise ValueError('Input object resource limit exceeded')
        if isinstance(obj, (dict, list, tuple)):
            identity = id(obj)
            if identity in active:
                raise ValueError('Cyclic certificate objects are not supported')
            active.add(identity)
            if isinstance(obj, dict):
                for key, val in obj.items():
                    if not isinstance(key, str):
                        raise ValueError('Certificate object keys must be strings')
                    visit(key, depth + 1)
                    visit(val, depth + 1)
            else:
                for val in obj:
                    visit(val, depth + 1)
            active.remove(identity)
        elif isinstance(obj, str):
            text_length += len(obj)
            if len(obj) > MAX_INPUT_STRING_LENGTH or text_length > MAX_INPUT_TEXT_LENGTH:
                raise ValueError('Input text resource limit exceeded')
        elif isinstance(obj, bool) or obj is None:
            pass  # Allowed as metadata; never accepted as a rational or budget.
        elif isinstance(obj, int):
            if obj.bit_length() > MAX_RATIONAL_BITS:
                raise ValueError('Input integer resource limit exceeded')
        elif isinstance(obj, Fraction):
            if max(obj.numerator.bit_length(), obj.denominator.bit_length()) > MAX_RATIONAL_BITS:
                raise ValueError('Input rational resource limit exceeded')
        else:
            raise ValueError('Only exact JSON-like certificate data are supported')

    visit(value, 0)


def _plain_copy(value):
    """Copy preflighted data and make exact Fraction objects JSON serializable."""
    if isinstance(value, dict):
        return {key: _plain_copy(val) for key, val in value.items()}
    if isinstance(value, (list, tuple)):
        return [_plain_copy(val) for val in value]
    if isinstance(value, Fraction):
        return str(value)
    return value


def _q(value):
    if isinstance(value, bool):
        raise ValueError('An exact integer or rational string is required')
    if isinstance(value, str):
        value = value.strip()
        if len(value) > MAX_RATIONAL_TEXT_LENGTH or not _RATIONAL_TEXT.fullmatch(value):
            raise ValueError('Use bounded integer or numerator/denominator rational text')
    elif not isinstance(value, (int, Fraction)):
        raise ValueError('An exact integer or rational string is required')
    try:
        result = Fraction(value)
    except (ValueError, TypeError, ZeroDivisionError, OverflowError) as exc:
        raise ValueError('Invalid exact rational') from exc
    if max(result.numerator.bit_length(), result.denominator.bit_length()) > MAX_RATIONAL_BITS:
        raise ValueError('Rational coefficient resource limit exceeded')
    return result


def _sequence(value, label, maximum=None, nonempty=False):
    if not isinstance(value, (list, tuple)):
        raise ValueError(label + ' must be a list')
    if (nonempty and not value) or (maximum is not None and len(value) > maximum):
        raise ValueError(label + ' has an unsupported length')
    return value


def _integer(value, label, maximum=None):
    if not isinstance(value, int) or isinstance(value, bool) or value < 0:
        raise ValueError(label + ' must be a nonnegative integer')
    if maximum is not None and value > maximum:
        raise ValueError(label + ' resource limit exceeded')
    return value


def _budget(value):
    return _integer(value, 'Storage budget', MAX_STORAGE_BUDGET)


def _polynomial(value, label, maximum_degree=MAX_TARGET_DEGREE):
    # The explicit degree argument avoids relying on normalization to discard a
    # maliciously large array of zeros.  All input entries are parsed strictly.
    return [_q(x) for x in _sequence(value, label, maximum_degree + 1, True)]


def _check_result(P, Q):
    if max(len(P), len(Q)) - 1 > MAX_TARGET_DEGREE:
        raise ValueError('Reduced target degree resource limit exceeded')
    for x in P + Q:
        if max(x.numerator.bit_length(), x.denominator.bit_length()) > MAX_RESULT_COEFFICIENT_BITS:
            raise ValueError('Computed coefficient resource limit exceeded')
    return P, Q


def _reduce(P, Q):
    # Each binary composition has degree at most the sum of its two child
    # degrees.  Refuse unexpected oversized intermediate data before gcd work.
    if max(len(P), len(Q)) > 2 * MAX_TARGET_DEGREE + 1:
        raise ValueError('Intermediate polynomial resource limit exceeded')
    for x in P + Q:
        if max(x.numerator.bit_length(), x.denominator.bit_length()) > MAX_RESULT_COEFFICIENT_BITS:
            raise ValueError('Intermediate coefficient resource limit exceeded')
    return _check_result(*reduce_target(P, Q))


def _target(value):
    if not isinstance(value, dict) or 'P' not in value or 'Q' not in value:
        raise ValueError('Target must contain ascending P and Q arrays')
    return _reduce(_polynomial(value['P'], 'P', MAX_TARGET_DEGREE),
                   _polynomial(value['Q'], 'Q', MAX_TARGET_DEGREE))


def _serialized_target(P, Q):
    return {'P': list(map(str, P)), 'Q': list(map(str, Q))}


def _same_target(left, right):
    # _target/_reduce make Q monic and cancel the rational gcd.
    return left[0] == right[0] and left[1] == right[1]


def _bound_expected(declared_target, declared_budget, expected_target, expected_budget):
    if expected_target is not None:
        _preflight(expected_target)
        if not _same_target(declared_target, _target(expected_target)):
            raise ValueError('Target binding mismatch')
    if expected_budget is not None and declared_budget != _budget(expected_budget):
        raise ValueError('Budget binding mismatch')


def _prepare_leaf(cert):
    """Strictly bound and normalize the numeric inputs to an existing kernel.

    This does not replace either kernel's proof.  It closes shape/resource gaps
    in their direct APIs before composition invokes them, without changing the
    old source files.  Unknown root-level fields are retained as inert metadata.
    """
    if not isinstance(cert, dict) or cert.get('format') not in LEAF_FORMATS:
        raise ValueError('A certificate leaf must use an existing circuit format')
    out = _plain_copy(cert)
    P, Q = _target(cert.get('target'))
    out['target'] = _serialized_target(P, Q)
    out['storage_budget'] = _budget(cert.get('storage_budget'))
    fmt = cert['format']
    branch_limit = MAX_ALGEBRAIC_BRANCHES if fmt == ALGEBRAIC_FORMAT else 20
    rows = _sequence(cert.get('branches'), 'Leaf branches', branch_limit, True)
    normalized = []
    all_nodes = {0, 1}
    for row in rows:
        fields = {'type', 'nodes', 'coefficient'} if fmt == ALGEBRAIC_FORMAT else {'type', 'nodes'}
        if not isinstance(row, dict) or set(row) != fields:
            raise ValueError('Malformed leaf branch')
        typ = row['type']
        if typ not in ('g', 'h', 'c'):
            raise ValueError('Unknown leaf branch type')
        pair = _sequence(row['nodes'], 'Leaf branch nodes', 2)
        if len(pair) != 2:
            raise ValueError('A branch must have two distinct nodes')
        a, b = (_integer(x, 'Leaf node') for x in pair)
        if a == b:
            raise ValueError('A branch must have two distinct nodes')
        all_nodes.update((a, b))
        entry = {'type': typ, 'nodes': sorted((a, b))}
        if fmt == ALGEBRAIC_FORMAT:
            coeff = row['coefficient']
            if not isinstance(coeff, (list, tuple)):
                coeff = [coeff]
            entry['coefficient'] = list(map(str, _polynomial(
                coeff, 'Algebraic branch coefficient', MAX_COMPONENT_POLYNOMIAL_DEGREE)))
        normalized.append(entry)
    if len(all_nodes) > MAX_GRAPH_NODES:
        raise ValueError('Leaf node count resource limit exceeded')
    out['branches'] = normalized
    if fmt == ALGEBRAIC_FORMAT:
        field = cert.get('field')
        if not isinstance(field, dict) or 'polynomial' not in field or 'interval' not in field:
            raise ValueError('Missing algebraic field definition')
        polynomial = _polynomial(field['polynomial'], 'Field polynomial', MAX_FIELD_DEGREE)
        interval = _sequence(field['interval'], 'Field interval', 2)
        if len(interval) != 2:
            raise ValueError('Field interval must have two endpoints')
        out['field'] = {'polynomial': list(map(str, polynomial)),
                        'interval': [str(_q(x)) for x in interval]}
    else:
        m = len(rows)
        for key in ('center', 'radii'):
            values = _sequence(cert.get(key), key, m)
            if len(values) != m:
                raise ValueError('Leaf box dimension mismatch')
            out[key] = [str(_q(x)) for x in values]
        matrix = _sequence(cert.get('preconditioner'), 'Preconditioner', m)
        if len(matrix) != m:
            raise ValueError('Leaf preconditioner dimension mismatch')
        out['preconditioner'] = []
        for row in matrix:
            values = _sequence(row, 'Preconditioner row', m)
            if len(values) != m:
                raise ValueError('Leaf preconditioner dimension mismatch')
            out['preconditioner'].append([str(_q(x)) for x in values])
        if 'fixed_parameters' in cert:
            fixed = _sequence(cert['fixed_parameters'], 'Fixed parameters', m)
            out['fixed_parameters'] = []
            for row in fixed:
                if not isinstance(row, dict) or set(row) != {'index', 'value'}:
                    raise ValueError('Malformed fixed parameter')
                index = _integer(row['index'], 'Fixed parameter index')
                if index >= m:
                    raise ValueError('Fixed parameter index out of range')
                out['fixed_parameters'].append({'index': index, 'value': str(_q(row['value']))})
    return out, (P, Q)


def _check_leaf(cert):
    prepared, target = _prepare_leaf(cert)
    checker = verify_algebraic_circuit if prepared['format'] == ALGEBRAIC_FORMAT else verify_interval_circuit
    try:
        result = checker(prepared)
    except (KeyError, TypeError, IndexError, ZeroDivisionError, OverflowError) as exc:
        raise ValueError('Malformed or invalid leaf certificate') from exc
    if result.get('status') != 'PASS':
        raise ValueError('Leaf checker did not establish its circuit')
    return prepared, target, result


def _join(left, right, op):
    P, Q = left
    A, B = right
    common_sum = add(mul(P, B), mul(A, Q))
    if op == 'series':
        return _reduce(common_sum, mul(Q, B))
    return _reduce(mul(P, A), common_sum)


def _frequency_inverse(target):
    P, Q = target
    length = max(len(P), len(Q))
    # A common power clears both denominators after s -> 1/s.  Reversing the
    # original unequal-length arrays separately would silently change Z(s).
    P = P + [Fraction(0)] * (length - len(P))
    Q = Q + [Fraction(0)] * (length - len(Q))
    return _reduce(list(reversed(P)), list(reversed(Q)))


class _Assembler:
    def __init__(self):
        self.next_node = 2
        self.expression_nodes = 0
        self.branches = []
        self.contexts = []
        self.leaf_results = []

    def node(self):
        if self.next_node >= MAX_GRAPH_NODES:
            raise ValueError('Assembled graph node resource limit exceeded')
        result = self.next_node
        self.next_node += 1
        return result

    def branch(self, typ, a, b, coefficient):
        if len(self.branches) >= MAX_TOTAL_BRANCHES:
            raise ValueError('Assembled branch resource limit exceeded')
        if a == b:
            raise ValueError('Internal terminal-gluing error: self loop')
        self.branches.append({'instance': len(self.branches), 'type': typ,
                              'nodes': sorted((a, b)), 'coefficient': coefficient})

    def build(self, expression, ground=0, port=1, depth=0, path='$'):
        self.expression_nodes += 1
        if depth > MAX_EXPRESSION_DEPTH or self.expression_nodes > MAX_EXPRESSION_NODES:
            raise ValueError('Expression depth/node resource limit exceeded')
        if not isinstance(expression, dict):
            raise ValueError('Every expression node must be a mapping')
        op = expression.get('op')
        schema = {
            'element': {'op', 'type', 'value'},
            'certificate': {'op', 'certificate'},
            'series': {'op', 'children'},
            'parallel': {'op', 'children'},
            'frequency_invert': {'op', 'child'},
        }
        if not isinstance(op, str) or op not in schema or set(expression) != schema[op]:
            raise ValueError('Unknown operation or malformed expression node')
        if op == 'element':
            typ = expression['type']
            if typ not in ('R', 'L', 'C'):
                raise ValueError('Element type must be R, L, or C')
            value = _q(expression['value'])
            if value <= 0:
                raise ValueError('Every physical element value must be strictly positive')
            coefficient = value if typ == 'C' else 1 / value
            self.branch({'R': 'g', 'L': 'h', 'C': 'c'}[typ], ground, port,
                        {'kind': 'rational', 'value': str(coefficient)})
            if typ == 'R':
                return _reduce([value], [Fraction(1)])
            if typ == 'L':
                return _reduce([Fraction(0), value], [Fraction(1)])
            return _reduce([Fraction(1)], [Fraction(0), value])
        if op == 'certificate':
            if len(self.contexts) >= MAX_LEAF_OCCURRENCES:
                raise ValueError('Certificate leaf occurrence resource limit exceeded')
            cert, target, checked = _check_leaf(expression['certificate'])
            if len(self.branches) + len(cert['branches']) > MAX_TOTAL_BRANCHES:
                raise ValueError('Assembled branch resource limit exceeded')
            context_id = 'leaf_' + str(len(self.contexts))
            digest = hashlib.sha256(json.dumps(cert, sort_keys=True, separators=(',', ':'),
                                              ensure_ascii=True).encode('utf-8')).hexdigest()
            context = {'id': context_id, 'expression_path': path,
                       'certificate_format': cert['format'], 'certificate_sha256': digest}
            if cert['format'] == ALGEBRAIC_FORMAT:
                context.update({'kind': 'algebraic', 'field': _plain_copy(cert['field'])})
            else:
                definition = {key: _plain_copy(cert[key]) for key in
                              ('target', 'branches', 'center', 'radii')}
                if 'fixed_parameters' in cert:
                    definition['fixed_parameters'] = _plain_copy(cert['fixed_parameters'])
                context.update({'kind': 'interval', 'definition': definition,
                                'equations_sha256': checked['equations_sha256'],
                                'component_intervals': checked['component_intervals'],
                                'root_semantics': checked['root_semantics']})
            self.contexts.append(context)
            self.leaf_results.append({'context': context_id, 'expression_path': path,
                                      'certificate_format': cert['format'], 'result': checked})
            # Each occurrence gets fresh internal vertices, even if the caller
            # reused the same Python dictionary or identical certificate text.
            old_nodes = {v for row in cert['branches'] for v in row['nodes']}
            mapping = {0: ground, 1: port}
            for old in sorted(old_nodes - {0, 1}):
                mapping[old] = self.node()
            start = len(self.branches)
            for index, row in enumerate(cert['branches']):
                if cert['format'] == ALGEBRAIC_FORMAT:
                    coefficient = {'kind': 'algebraic', 'context': context_id,
                                   'polynomial': list(row['coefficient'])}
                else:
                    coefficient = {'kind': 'interval', 'context': context_id, 'index': index}
                a, b = row['nodes']
                self.branch(row['type'], mapping[a], mapping[b], coefficient)
            actual = sum(row['type'] != 'g' for row in self.branches[start:])
            if actual != checked['actual_storage']:
                raise ValueError('Leaf checker/physical branch count disagreement')
            return target
        if op == 'frequency_invert':
            start = len(self.branches)
            target = self.build(expression['child'], ground, port, depth + 1, path + '.child')
            for row in self.branches[start:]:
                row['type'] = {'g': 'g', 'h': 'c', 'c': 'h'}[row['type']]
            return _frequency_inverse(target)
        children = _sequence(expression['children'], 'Composition children', MAX_CHILDREN)
        if len(children) < 2:
            raise ValueError('Series/parallel composition needs at least two children')
        if op == 'series':
            # Child i runs from chain[i] (its port) to chain[i+1] (its ground).
            # No other child vertices are identified.
            chain = [port] + [self.node() for _ in range(len(children) - 1)] + [ground]
        target = None
        for i, child in enumerate(children):
            child_ground, child_port = (chain[i + 1], chain[i]) if op == 'series' else (ground, port)
            current = self.build(child, child_ground, child_port, depth + 1,
                                 path + '.children[' + str(i) + ']')
            target = current if target is None else _join(target, current, op)
        return target

    def finish(self, target, budget):
        actual = sum(row['type'] != 'g' for row in self.branches)
        if actual > budget:
            raise ValueError('Reactive budget exceeded')
        nodes = set(range(self.next_node))
        reached = {0}
        while True:
            more = reached.copy()
            for row in self.branches:
                a, b = row['nodes']
                if a in reached:
                    more.add(b)
                if b in reached:
                    more.add(a)
            if more == reached:
                break
            reached = more
        if reached != nodes or 1 not in reached:
            raise ValueError('Rebuilt graph is disconnected')
        P, Q = target
        degree = max(len(P), len(Q)) - 1
        if degree > actual:
            raise ValueError('Internal degree/physical-storage inconsistency')
        minimum = actual == degree
        return {
            'status': 'PASS', 'certificate_format': FORMAT,
            'arithmetic': 'Python standard-library int and Fraction; independently verified exact leaf proofs',
            'target': _serialized_target(P, Q), 'storage_budget': budget,
            'actual_storage': actual, 'resistors': len(self.branches) - actual,
            'physical_branch_count': len(self.branches), 'physical_node_count': len(nodes),
            'reduced_target_degree': degree,
            'global_minimum_proved_by_degree': minimum, 'realization_only': not minimum,
            'proof_scope': 'global reactive minimum by degree equality' if minimum else
                           'exact positive realization; reactive minimality is not established',
            'expression_node_count': self.expression_nodes,
            'leaf_occurrence_count': len(self.contexts),
            'rebuilt_graph': {'terminals': [0, 1], 'nodes': sorted(nodes),
                              'branches': self.branches},
            'parameter_contexts': self.contexts, 'leaf_results': self.leaf_results,
        }


def verify_composition_certificate(cert, expected_target=None, expected_budget=None):
    """Verify every leaf, exact target/budget binding, and a rebuilt graph.

    The optional expected budget binds the declared budget *exactly*.  Physical
    reactive count must be at most that budget.  Minimality depends exclusively
    on equality of the actual count and the final reduced target degree.
    """
    _preflight(cert)
    if not isinstance(cert, dict) or cert.get('format') != FORMAT:
        raise ValueError('Unknown composition certificate format')
    declared = _target(cert.get('target'))
    budget = _budget(cert.get('storage_budget'))
    _bound_expected(declared, budget, expected_target, expected_budget)
    assembler = _Assembler()
    computed = assembler.build(cert.get('expression'))
    if not _same_target(declared, computed):
        raise ValueError('Expression does not realize the declared target')
    return assembler.finish(computed, budget)


def verify_circuit(cert, expected_target=None, expected_budget=None):
    """Dispatch the three supported exact circuit-certificate formats."""
    _preflight(cert)
    if not isinstance(cert, dict):
        raise ValueError('Circuit certificate must be a mapping')
    fmt = cert.get('format')
    if fmt == FORMAT:
        return verify_composition_certificate(cert, expected_target, expected_budget)
    if fmt not in LEAF_FORMATS:
        raise ValueError('Unknown circuit certificate format')
    prepared, target = _prepare_leaf(cert)
    _bound_expected(target, prepared['storage_budget'], expected_target, expected_budget)
    _, _, result = _check_leaf(prepared)
    return dict(result, certificate_format=fmt, target=_serialized_target(*target),
                storage_budget=prepared['storage_budget'],
                realization_only=not result['global_minimum_proved_by_degree'])


def element_node(type, value):
    """Construct one positive physical resistor, inductor, or capacitor."""
    if type not in ('R', 'L', 'C'):
        raise ValueError('Element type must be R, L, or C')
    value = _q(value)
    if value <= 0:
        raise ValueError('Every physical element value must be strictly positive')
    return {'op': 'element', 'type': type, 'value': str(value)}


def certificate_node(cert):
    """Copy an existing algebraic/interval circuit as one independently checked leaf.

    To reuse a composition, insert a copy of its ``expression`` instead; nesting
    a composition certificate inside a certificate leaf is deliberately absent.
    """
    _preflight(cert)
    if not isinstance(cert, dict) or cert.get('format') not in LEAF_FORMATS:
        raise ValueError('A certificate leaf must use an existing circuit format')
    return {'op': 'certificate', 'certificate': _plain_copy(cert)}


def _children_node(op, children):
    if len(children) == 1 and isinstance(children[0], (list, tuple)):
        children = tuple(children[0])
    if not 2 <= len(children) <= MAX_CHILDREN:
        raise ValueError('Series/parallel composition needs two or more bounded children')
    _preflight(children)
    if any(not isinstance(child, dict) for child in children):
        raise ValueError('Every composition child must be an expression mapping')
    return {'op': op, 'children': _plain_copy(children)}


def series_node(*children):
    return _children_node('series', children)


def parallel_node(*children):
    return _children_node('parallel', children)


def frequency_invert_node(child):
    _preflight(child)
    if not isinstance(child, dict):
        raise ValueError('Frequency inversion needs one expression mapping')
    return {'op': 'frequency_invert', 'child': _plain_copy(child)}


def make_composition(expression, target=None, budget=None):
    """Build a portable certificate after checking its full expression.

    Omitted target/budget are computed exactly.  An explicit target must denote
    the same rational impedance; an explicit budget must cover every physical
    reactive branch occurrence.  The returned target is reduced with monic Q.
    This helper is a convenience, not a substitute for a consumer's replay.
    """
    _preflight(expression)
    assembler = _Assembler()
    computed = assembler.build(expression)
    if target is not None:
        _preflight(target)
        if not _same_target(computed, _target(target)):
            raise ValueError('Requested target differs from the composition')
    if budget is None:
        budget = sum(row['type'] != 'g' for row in assembler.branches)
    budget = _budget(budget)
    assembler.finish(computed, budget)
    result = {'format': FORMAT, 'target': _serialized_target(*computed),
              'storage_budget': budget, 'expression': _plain_copy(expression)}
    # Arithmetic can grow a normalized output beyond the accepted wire-input
    # limits even when every input component fits.  Do not emit a purportedly
    # portable certificate that the public replay interface would then reject.
    _preflight(result)
    _target(result['target'])
    return result


if __name__ == '__main__':
    import argparse
    from pathlib import Path

    parser = argparse.ArgumentParser(description='Replay an exact RLC circuit/composition certificate')
    parser.add_argument('certificate', type=Path)
    args = parser.parse_args()
    data = json.loads(args.certificate.read_text())
    print(json.dumps(verify_circuit(data), indent=2))
