"""Author: Komorebi P. Target-only module synthesis with exact interval cores.

This bounded constructive search does not decide all-topology realizability.
The proposal layer may use floating point; every accepted leaf and every graft
must pass the independent exact composition verifier. No fixture certificate,
known circuit topology, or generating component values are read by this module.
"""
from __future__ import annotations

from copy import deepcopy
from fractions import Fraction as F
import time

from interval_certificate import reduce_target
from recursive_modules import (
    base_case, both_orientation_sections, one_reactive_endpoint_candidates,
)
from endpoint_extract import extract_shunt_L, extract_series_R_C
from exact_biquadratic_templates import Leaf, Comp
from composition_certificate import (
    certificate_node, element_node, frequency_invert_node, make_composition,
    parallel_node, series_node, verify_circuit,
)


def _degree(P, Q):
    return max(len(P), len(Q)) - 1


def _bound(value, name, minimum):
    if isinstance(value, bool) or not isinstance(value, int) or value < minimum:
        raise ValueError(f'{name} must be an integer at least {minimum}')
    return value


def _expression(cert):
    """Preserve separate leaf parameter contexts; never coerce algebraic fields."""
    if cert.get('format') == 'komorebi-rlc-composition-v1':
        return deepcopy(cert['expression'])
    return certificate_node(cert)


def _module_expression(tree):
    if isinstance(tree, Leaf):
        return element_node(tree.typ, tree.value)
    if isinstance(tree, Comp) and tree.op in ('series', 'parallel'):
        compose = series_node if tree.op == 'series' else parallel_node
        return compose(*[_module_expression(child) for child in tree.children])
    raise ValueError('Unsupported passive module tree')


def _frequency_inverse_target(P, Q):
    """Use one common degree so unequal P/Q degrees retain origin factors."""
    n = _degree(P, Q)
    pp = list(reversed(list(P) + [F(0)] * (n + 1 - len(P))))
    qq = list(reversed(list(Q) + [F(0)] * (n + 1 - len(Q))))
    return reduce_target(pp, qq)


def _endpoint_candidates(P, Q):
    """Exact degree-one reductions, including frequency-inverted endcaps."""
    n = _degree(P, Q)
    for frequency_inverted in (False, True):
        pp, qq = _frequency_inverse_target(P, Q) if frequency_inverted else (P, Q)
        for kind, extractor in (
            ('shunt-R series-L', extract_shunt_L),
            ('series-R shunt-C', extract_series_R_C),
        ):
            try:
                resistor, reactive, cp, cq = extractor(pp, qq)
                cp, cq = reduce_target(cp, cq)
            except (ValueError, ZeroDivisionError):
                continue
            if _degree(cp, cq) != n - 1:
                continue
            yield {
                'kind': kind, 'frequency_inverted': frequency_inverted,
                'resistor_parameter': resistor, 'reactive': reactive,
                'coreP': cp, 'coreQ': cq,
            }


def _attach_endpoint(core, item):
    expression = _expression(core)
    if item['kind'] == 'shunt-R series-L':
        expression = parallel_node(
            element_node('R', 1 / item['resistor_parameter']),
            series_node(element_node('L', item['reactive']), expression),
        )
    else:
        expression = series_node(
            element_node('R', item['resistor_parameter']),
            parallel_node(element_node('C', item['reactive']), expression),
        )
    if item['frequency_inverted']:
        expression = frequency_invert_node(expression)
    return expression


def synthesize_compositional(P, Q, *, max_degree=12, max_states=250,
                            max_budget=None, topology_starts=2,
                            topology_evaluations=600, topology_seed=2026111223,
                            max_topology_calls=16):
    """Recover a minimum-reactive positive circuit from rational P/Q alone.

    Supported grafts are exposed single L/C elements, positive two-element
    endpoint caps, and exact passive simple-pole/quadratic factor modules. An
    eligible degree-three residual may use the bounded interval graph search.
    A cache avoids repeating search for the same normalized residual. Reaching
    any resource cap returns UNKNOWN unless a fully checked circuit was found.
    """
    started = time.perf_counter()
    try:
        max_degree = _bound(max_degree, 'max_degree', 0)
        max_states = _bound(max_states, 'max_states', 1)
        topology_starts = _bound(topology_starts, 'topology_starts', 1)
        topology_evaluations = _bound(topology_evaluations, 'topology_evaluations', 1)
        topology_seed = _bound(topology_seed, 'topology_seed', 0)
        max_topology_calls = _bound(max_topology_calls, 'max_topology_calls', 0)
        if max_budget is not None:
            max_budget = _bound(max_budget, 'max_budget', 0)
        P, Q = reduce_target(P, Q)
    except (ValueError, ZeroDivisionError, TypeError) as exc:
        return {'status': 'INVALID_INPUT', 'reason': str(exc)}

    n = _degree(P, Q)
    if n > max_degree:
        return {'status': 'UNKNOWN', 'reason': f'Conservative max_degree={max_degree} search cutoff',
                'reduced_target_degree': n}
    if max_budget is not None and n > max_budget:
        return {'status': 'UNKNOWN', 'reason': 'Budget is below the exact rational-degree lower bound',
                'reduced_target_degree': n, 'max_budget': max_budget,
                'degree_lower_bound_excludes_requested_budget': True}

    cache = {}
    stats = {'visited_states': 0, 'cache_hits': 0, 'topology_calls': 0,
             'state_limit_reached': False, 'topology_limit_reached': False}
    rejected = []
    graph_searches = []

    def reject(stage, exc):
        # Diagnostics are bounded and cannot control acceptance.
        if len(rejected) < 24:
            rejected.append({'stage': stage, 'reason': str(exc)})

    def accepted_leaf(answer, pp, qq, d):
        if answer.get('status') != 'CERTIFIED_MINIMUM':
            return None
        try:
            checked = verify_circuit(answer['certificate'],
                                     expected_target={'P': pp, 'Q': qq},
                                     expected_budget=d)
            if checked['actual_storage'] != d or checked['reduced_target_degree'] != d:
                raise ValueError('Leaf does not attain the degree lower bound')
        except (ValueError, ZeroDivisionError, TypeError, KeyError) as exc:
            reject('leaf acceptance', exc)
            return None
        return {'certificate': answer['certificate'], 'verification': checked,
                'core_route': answer.get('route'), 'modules': []}

    def graft(expression, child, record, pp, qq, d):
        try:
            cert = make_composition(expression, target={'P': pp, 'Q': qq}, budget=d)
            checked = verify_circuit(cert, expected_target={'P': pp, 'Q': qq},
                                     expected_budget=d)
            if checked['actual_storage'] != d or checked['reduced_target_degree'] != d:
                raise ValueError('Composition does not attain the degree lower bound')
        except (ValueError, ZeroDivisionError, TypeError, KeyError) as exc:
            reject(record, exc)
            return None
        return {'certificate': cert, 'verification': checked,
                'core_route': child['core_route'],
                'modules': [record] + child['modules']}

    def recurse(pp, qq):
        pp, qq = reduce_target(pp, qq)
        key = (tuple(pp), tuple(qq))
        if key in cache:
            stats['cache_hits'] += 1
            return cache[key]
        if stats['visited_states'] >= max_states:
            stats['state_limit_reached'] = True
            return None
        stats['visited_states'] += 1
        d = _degree(pp, qq)
        cache[key] = None

        try:
            basic = base_case(pp, qq)
        except (ValueError, ZeroDivisionError) as exc:
            reject('inherited base proposal', exc)
            basic = {'status': 'UNKNOWN'}
        result = accepted_leaf(basic, pp, qq, d)
        if result is not None:
            cache[key] = result
            return result

        if d == 3 and len(pp) == len(qq) == 4 and pp[-1] > 0:
            if stats['topology_calls'] < max_topology_calls:
                from graph_search_synthesis import find_topology_interval
                stats['topology_calls'] += 1
                answer = find_topology_interval(
                    pp, qq, starts=topology_starts, max_nfev=topology_evaluations,
                    seed=topology_seed,
                )
                graph_searches.append({
                    'target': {'P': list(map(str, pp)), 'Q': list(map(str, qq))},
                    **{k: v for k, v in answer.items() if k not in ('certificate', 'verification')},
                })
                result = accepted_leaf(answer, pp, qq, d)
                if result is not None:
                    cache[key] = result
                    return result
            else:
                stats['topology_limit_reached'] = True
        if d <= 1:
            return None

        for mode, value, cp, cq in one_reactive_endpoint_candidates(pp, qq):
            try:
                cp, cq = reduce_target(cp, cq)
            except (ValueError, ZeroDivisionError):
                continue
            if _degree(cp, cq) != d - 1:
                continue
            child = recurse(cp, cq)
            if child is None:
                continue
            compose = series_node if mode.startswith('series') else parallel_node
            expression = compose(element_node('L' if mode.endswith('L') else 'C', value),
                                 _expression(child['certificate']))
            record = {'type': 'one_reactive_endpoint', 'kind': mode, 'value': str(value)}
            result = graft(expression, child, record, pp, qq, d)
            if result is not None:
                cache[key] = result
                return result

        for item in _endpoint_candidates(pp, qq):
            child = recurse(item['coreP'], item['coreQ'])
            if child is None:
                continue
            record = {'type': 'endpoint', 'kind': item['kind'],
                      'frequency_inverted': item['frequency_inverted'],
                      'reactive': str(item['reactive']),
                      'resistor_parameter': str(item['resistor_parameter'])}
            result = graft(_attach_endpoint(child['certificate'], item), child,
                           record, pp, qq, d)
            if result is not None:
                cache[key] = result
                return result

        try:
            sections = list(both_orientation_sections(pp, qq))
        except (ValueError, ZeroDivisionError) as exc:
            reject('factor module proposals', exc)
            sections = []
        for orientation, tree, cp, cq, record in sections:
            try:
                cp, cq = reduce_target(cp, cq)
            except (ValueError, ZeroDivisionError):
                continue
            if _degree(cp, cq) >= d:
                continue
            child = recurse(cp, cq)
            if child is None:
                continue
            compose = series_node if orientation == 'series' else parallel_node
            expression = compose(_expression(child['certificate']), _module_expression(tree))
            result = graft(expression, child, record, pp, qq, d)
            if result is not None:
                cache[key] = result
                return result
        return None

    result = recurse(P, Q)
    common = {**stats, 'rejected_candidates': rejected, 'interval_graph_searches': graph_searches,
              'search_limits': {'max_degree': max_degree, 'max_states': max_states,
                                'max_topology_calls': max_topology_calls,
                                'topology_starts': topology_starts,
                                'topology_evaluations': topology_evaluations,
                                'topology_seed': topology_seed},
              'elapsed_seconds': time.perf_counter() - started}
    if result is None:
        return {'status': 'UNKNOWN',
                'reason': 'No complete certified decomposition within the declared module/core search limits',
                'scope': 'Incomplete constructive search; no all-topology impossibility conclusion',
                **common}
    try:
        final = verify_circuit(result['certificate'], expected_target={'P': P, 'Q': Q},
                               expected_budget=n)
        if final['actual_storage'] != n or final['reduced_target_degree'] != n:
            raise ValueError('Final certificate does not attain the exact degree lower bound')
    except (ValueError, ZeroDivisionError, TypeError, KeyError) as exc:
        return {'status': 'UNKNOWN', 'reason': 'Final independent certificate verification failed',
                'verification_error': str(exc), **common}
    return {'status': 'CERTIFIED_MINIMUM',
            'route': 'exact passive module composition + independently certified core',
            'minimum_reactive_count': n, **result, 'verification': final, **common}


if __name__ == '__main__':
    import json
    import sys
    from pathlib import Path
    target = json.loads(Path(sys.argv[1]).read_text())
    print(json.dumps(synthesize_compositional(target['P'], target['Q']), indent=2))
