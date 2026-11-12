"""Exact recognition and certificates for a specified RLC family. Author: Komorebi P.

No optimizer, floating-point fit or numerical root reconstruction is used.
The copied acceptance kernels are unchanged from the authenticated checkpoint.
"""
from __future__ import annotations

from copy import deepcopy
from fractions import Fraction as F
import hashlib
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / 'kernel'))
from interval_family import verify_coefficient_family
from interval_certificate import verify_interval_circuit
from composition_certificate import (_preflight, _target, _q, certificate_node,
    element_node, series_node, parallel_node, make_composition,
    verify_composition_certificate)

MAX_DEGREE = 16  # At most thirteen lifts, inside the existing expression-depth cap.


class OutsideFamily(ValueError):
    """Exact failure of a defining condition of this particular family."""


def trim(p):
    p = list(p)
    while len(p) > 1 and p[-1] == 0:
        p.pop()
    return p


def subtract(p, q):
    return trim([(p[i] if i < len(p) else F(0)) - (q[i] if i < len(q) else F(0))
                 for i in range(max(len(p), len(q)))])


def scale(p, a):
    return trim([a * x for x in p])


def bounded(*vectors):
    for vector in vectors:
        for value in vector:
            _q(value)  # The consumer's exact rational input and bit bounds.


def unlift(U, V):
    """Unique inverse in the positive endpoint chart; no search branches."""
    d = max(len(U), len(V)) - 1
    if len(U) != d + 1 or len(V) != d + 1 or V[-1] != 1 or U[-1] <= 0:
        raise OutsideFamily('Outside the equal-degree positive endpoint chart')
    g = 1 / U[-1]
    H = subtract(V, scale(U, g))
    if len(H) != d or H[-1] <= 0:
        raise OutsideFamily('Endpoint inverse has no positive first remainder')
    h = H[-1]
    L = U[-1] / h
    K = subtract(U, scale([F(0)] + H, L))
    if len(K) != d or K[-1] <= 0:
        raise OutsideFamily('Endpoint inverse has no positive second remainder')
    P, Q = scale(K, 1 / h), scale(H, 1 / h)
    bounded(P, Q, [g, L])
    return P, Q, g, L


def specialize(family, P, Q):
    """Convert a checked uniform family to a target-bound ordinary leaf certificate."""
    coordinates = P + Q[:3]
    if len(P) != 4 or len(Q) != 4 or Q[-1] != 1 or P[-1] <= 0:
        raise OutsideFamily('Reduced core does not have the required cubic normalization')
    center = list(map(_q, family['target_box']['center']))
    radii = list(map(_q, family['target_box']['radii']))
    if any(abs(x - a) > r for x, a, r in zip(coordinates, center, radii)):
        raise OutsideFamily('Reduced cubic core is outside the certified coefficient box')
    cert = {'format': 'komorebi-rlc-interval-v1', 'branches': deepcopy(family['branches']),
            'target': {'P': list(map(str, P)), 'Q': list(map(str, Q))},
            'storage_budget': 3, 'center': deepcopy(family['center']),
            'radii': deepcopy(family['radii']), 'preconditioner': deepcopy(family['preconditioner'])}
    verify_interval_circuit(cert, expected_target=cert['target'], expected_budget=3)
    return cert


def synthesize(target, family=None):
    """Decide membership in the stated family within caps, then emit a checked witness.

    OUTSIDE_CERTIFIED_FAMILY concerns only this particular family. UNKNOWN is
    reserved for resource/acceptance limits. Neither status is an RLC exclusion.
    """
    if family is None:
        family = json.loads((ROOT / 'family.json').read_bytes())
    try:
        _preflight(family)
        verify_coefficient_family(family)
    except (ValueError, KeyError, TypeError, ZeroDivisionError) as exc:
        return {'status': 'INVALID_FAMILY_CERTIFICATE', 'reason': str(exc)}
    try:
        _preflight(target)
        U, V = _target(target)
    except (ValueError, KeyError, TypeError, ZeroDivisionError) as exc:
        return {'status': 'UNKNOWN' if 'limit' in str(exc).lower() else 'INVALID_INPUT', 'reason': str(exc)}
    degree = max(len(U), len(V)) - 1
    if degree > MAX_DEGREE:
        return {'status': 'UNKNOWN', 'reason': 'Degree exceeds the current consumer resource scope', 'maximum_degree': MAX_DEGREE}
    if degree < 3:
        return {'status': 'OUTSIDE_CERTIFIED_FAMILY', 'reason': 'This family starts at reduced degree three', 'not_an_impossibility_result': True}
    original = {'P': list(map(str, U)), 'Q': list(map(str, V))}
    wrappers = []
    try:
        while max(len(U), len(V)) - 1 > 3:
            U, V, g, L = unlift(U, V)
            wrappers.append((g, L))
        leaf = specialize(family, U, V)
    except OutsideFamily as exc:
        return {'status': 'OUTSIDE_CERTIFIED_FAMILY', 'reason': str(exc), 'not_an_impossibility_result': True}
    except (ValueError, ZeroDivisionError) as exc:
        return {'status': 'UNKNOWN', 'reason': 'Exact leaf acceptance or arithmetic limit: ' + str(exc)}
    try:
        expression = certificate_node(leaf)
        for g, L in reversed(wrappers):
            expression = parallel_node(element_node('R', 1 / g), series_node(element_node('L', L), expression))
        cert = make_composition(expression, target=original, budget=degree)
        check = verify_composition_certificate(cert, expected_target=original, expected_budget=degree)
    except ValueError as exc:
        return {'status': 'UNKNOWN', 'reason': 'Consumer acceptance limit: ' + str(exc)}
    return {'status': 'CERTIFIED', 'method': 'exact uniform-family specialization and endpoint inversion',
            'family_sha256': hashlib.sha256(json.dumps(family, sort_keys=True, separators=(',', ':')).encode()).hexdigest(),
            'reduced_degree': degree, 'lifts': len(wrappers),
            'certificate': cert, 'verification': check,
            'scope': 'This certified family within declared resource caps; no arbitrary-target synthesis or minimum resistor claim'}


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('target', type=Path)
    parser.add_argument('--output', type=Path)
    args = parser.parse_args()
    result = synthesize(json.loads(args.target.read_bytes()))
    text = json.dumps(result, indent=2) + '\n'
    if args.output:
        args.output.write_text(text, encoding='utf-8')
    else:
        print(text)
