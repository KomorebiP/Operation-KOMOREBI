"""Exact certificates for dyadic tail resolution and valuation distributions.

New code. Original dyadic series arithmetic is in the preserved v4 module.
No floating-point arithmetic enters any scientific assertion.
"""
from __future__ import annotations
from fractions import Fraction
from math import comb
from typing import Any
import dyadic_modular as d


def derivative(poly: list[int]) -> list[int]:
    return [i * poly[i] for i in range(1, len(poly))] or [0]


def bareiss_det(matrix: list[list[int]]) -> int:
    """Exact fraction-free determinant, with row pivoting and checked division."""
    n = len(matrix)
    if n == 0:
        return 1
    if any(len(row) != n for row in matrix):
        raise ValueError('Square matrix required')
    a = [row[:] for row in matrix]
    denominator = 1
    sign = 1
    for k in range(n - 1):
        pivot = next((i for i in range(k, n) if a[i][k]), None)
        if pivot is None:
            return 0
        if pivot != k:
            a[k], a[pivot] = a[pivot], a[k]
            sign = -sign
        p = a[k][k]
        for i in range(k + 1, n):
            for j in range(k + 1, n):
                numerator = p * a[i][j] - a[i][k] * a[k][j]
                assert numerator % denominator == 0
                a[i][j] = numerator // denominator
            a[i][k] = 0
        denominator = p
    return sign * a[-1][-1]


def resultant(f: list[int], g: list[int]) -> int:
    """Sylvester resultant for ascending coefficient arrays over the integers."""
    f, g = d.trim(f), d.trim(g)
    m, n = len(f) - 1, len(g) - 1
    if not any(f) or not any(g):
        return 0
    if n == 0:
        return g[0] ** m
    if m == 0:
        return f[0] ** n
    # Descending coefficient Sylvester matrix.
    rows = []
    for i in range(n):
        rows.append([0] * i + f[::-1] + [0] * (n - 1 - i))
    for i in range(m):
        rows.append([0] * i + g[::-1] + [0] * (m - 1 - i))
    return bareiss_det(rows)


def squarefree_certificate(w: list[int], precision: int) -> dict[str, Any]:
    """A nonzero resultant residue certifies the true dyadic polynomial.

    A zero residue is inconclusive, never evidence of a repeated root.
    For a finite positive D, the theorem uses depth D+1 and precision 2D+2.
    """
    if precision < 1:
        raise ValueError('Positive precision required')
    if not w or w[-1] != 1:
        raise ValueError('Monic polynomial required')
    if len(w) == 1:
        return {'status': 'unit_polynomial', 'degree': 0, 'precision': precision}
    modulus = 1 << precision
    residue = resultant(w, derivative(w)) % modulus
    if residue == 0:
        return {'status': 'inconclusive_resultant', 'degree': len(w) - 1,
                'precision': precision, 'resultant_mod': 0}
    valuation = int(d.v2(residue))
    return {'status': 'squarefree', 'degree': len(w) - 1, 'precision': precision,
            'resultant_mod': residue, 'resultant_valuation': valuation,
            'depth_bound': valuation + 1, 'sufficient_precision': 2 * valuation + 2}


def validate_atlas(data: dict, atlas: list[dict]) -> int:
    """Check disjoint coverage and coefficientwise leaf reductions."""
    if not atlas:
        raise AssertionError('Missing covering')
    mass = Fraction(0)
    p = data['precision']
    for a, leaf in enumerate(atlas):
        if leaf['kind'] not in ('constant', 'simple_root'):
            raise AssertionError(f'Unresolved leaf: {leaf}')
        k, s = leaf['k'], leaf['s']
        assert 0 <= s < 1 << k
        mass += Fraction(1, 1 << k)
        for other in atlas[:a]:
            kk = min(k, other['k'])
            assert (s - other['s']) % (1 << kk) != 0
        content = leaf['value'] if leaf['kind'] == 'constant' else leaf['content']
        assert content < p
        q = d.affine(data['coefficients'], s, 1 << k, 1 << (content + 1))
        assert all(z % (1 << content) == 0 for z in q)
        reduction = d.trim([(z >> content) % 2 for z in q])
        assert reduction == leaf['reduction']
        assert reduction == [1] if leaf['kind'] == 'constant' else reduction in ([0, 1], [1, 1])
    assert mass == 1
    return len(atlas)


def survival(atlas: list[dict], threshold: int) -> Fraction:
    """Haar probability v2(G(x)) >= threshold, for a completed simple atlas."""
    if threshold < 0:
        raise ValueError('Nonnegative threshold required')
    total = Fraction(0)
    for leaf in atlas:
        mass = Fraction(1, 1 << leaf['k'])
        if leaf['kind'] == 'constant':
            if leaf['value'] >= threshold:
                total += mass
        elif leaf['kind'] == 'simple_root':
            total += mass / (1 << max(0, threshold - leaf['content']))
        else:
            raise ValueError('A complete atlas is required')
    return total


def mean_valuation(atlas: list[dict]) -> Fraction:
    total = Fraction(0)
    for leaf in atlas:
        if leaf['kind'] == 'constant':
            local_mean = leaf['value']
        elif leaf['kind'] == 'simple_root':
            local_mean = leaf['content'] + 1
        else:
            raise ValueError('A complete atlas is required')
        total += Fraction(local_mean, 1 << leaf['k'])
    return total


def distribution_record(atlas: list[dict], h_max: int = 16) -> dict:
    """Exact rational generating-function data and eventual survival constant."""
    constants, roots = [], []
    for leaf in atlas:
        if leaf['kind'] == 'constant':
            constants.append({'mass': str(Fraction(1, 1 << leaf['k'])),
                              'valuation': leaf['value']})
        elif leaf['kind'] == 'simple_root':
            roots.append({'mass': str(Fraction(1, 1 << leaf['k'])),
                          'content': leaf['content'], 'offset': leaf['offset']})
        else:
            raise ValueError('A complete atlas is required')
    onset = max([0] + [q['valuation'] + 1 for q in constants]
                + [q['content'] for q in roots])
    constant = sum((Fraction(2) ** q['offset'] for q in roots), Fraction(0))
    return {'constants': constants, 'simple_roots': roots,
            'generating_function_convention': 'sum mass*T^value + sum mass*T^content/(2-T)',
            'mean': str(mean_valuation(atlas)),
            'survival': [str(survival(atlas, h)) for h in range(h_max + 1)],
            'eventual_survival_onset': onset, 'eventual_survival_constant': str(constant)}


def regular_scales(j: int) -> list[tuple[int, int, int, int]]:
    if j < 1:
        raise ValueError('j positive')
    return [(i, j - 1 - i.bit_count() - (j - 1 - i).bit_count(),
             0 if j == 1 else max(i, j - 1 - i).bit_length(),
             j - 1 - i.bit_count() - (j - 1 - i).bit_count()
             + (0 if j == 1 else max(i, j - 1 - i).bit_length()))
            for i in range(j)]


def regular_mean(j: int, delta: int) -> Fraction:
    return sum((Fraction(delta if delta < t else t + 1, 1 << k)
                for i, di, k, t in regular_scales(j)), Fraction(0))
