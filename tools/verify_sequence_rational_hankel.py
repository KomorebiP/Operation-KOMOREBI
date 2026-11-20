"""Finite, independent checks of the SEQ-DH-2026-11-20-001 continuation.

Author: Komorebi P. Emits exact coverage and full-state certificates as JSON.
"""
import argparse
from collections import Counter
from fractions import Fraction as F
from math import comb
from pathlib import Path
import json
import sys
import time

sys.path.insert(0, str(Path(__file__).resolve().parent))
import sequence_rational_hankel as new
from sequence_differential_hankel import (
    derivative_monomial_moment, structured_differential_hankel,
    chebyshev_jet_gram_entry,
)
from test_sequence_differential_hankel import (
    direct_determinant, direct_hankel, chebyshev, multiply, direct_functional,
)


def serialized(value):
    if isinstance(value, F):
        return str(value)
    if isinstance(value, dict):
        return {str(k): serialized(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [serialized(v) for v in value]
    return value


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--output', required=True)
    args = parser.parse_args()
    start = time.perf_counter()
    checks = Counter()
    cases = [
        ([0], [1]), ([1], [0]), ([2], [F(3, 2)]),
        ([1], [1, 1]), ([1], [0, 1]), ([1, 1], [1]),
        ([0, 1], [1]), ([2, -3], [1]),
        ([1, 1], [1, 2, 1]), ([0, 0, 1], [0, 1]),
        ([F(1, 2), -2, 1], [F(2, 3), 0, -1]),
        ([0, 1], [0, 0, 1]), ([1, -1, 2], [0, 0, 0, 1]),
    ]

    def check(kind, condition, context=None):
        checks[kind] += 1
        if not condition:
            raise AssertionError((kind, context))

    for a, c in cases:
        aa, cc, M = new.parameters(a, c)
        actual_minus, actual_plus, expected_minus, expected_plus = (
            new.branch_numerator_values(a, c))
        check('branch_endpoint_identities', actual_minus==expected_minus and
              actual_plus==expected_plus, (a, c))
        H, pole = new.canonical_kernel(a, c)
        if any(aa) and any(cc):
            check('exact_kernel_poles', new.evaluate(H, 1)!=0 and
                  new.evaluate(H, -1)!=0 and pole==2*M, (a, c))
        for n in range(33):
            check('kernel_vs_direct_monomial', new.kernel_moment(n, a, c)==
                  derivative_monomial_moment(n, a, c), (a, c, n))

    # Exhaustive coefficient grids within these declared degree/order bounds.
    # The M>=1 filter is explicit; zero/constant cases were tested above.
    rank_cases = []
    for D in range(4):
        for r in range(4-D):
            if D+r==0:
                continue
            for top_a in (-2, F(1, 3)):
                for top_c in (-1, F(2, 5)):
                    a = [F(3)]*D+[top_a]
                    c = [F(-2)]*r+[top_c]
                    rank_cases.append((a, c))
    for a, c in rank_cases:
        M = new.parameters(a, c)[2]
        for column_start, row_start in ((0, 2*M), (1, 2*M+2), (4, 4+2*M)):
            rows = list(range(row_start, row_start+2*M))
            columns = list(range(column_start, column_start+2*M))
            matrix = [[direct_functional(multiply(chebyshev(i), chebyshev(j)), a, c)
                       for j in columns] for i in rows]
            actual = direct_determinant(matrix)
            predicted = new.separated_minor_formula(rows, columns, a, c)
            check('sharp_rank_minors_from_direct_polynomials', actual==predicted
                  and actual!=0, (a, c, rows, columns))

    band_cases = [([1], [1, 1]), ([1, 1], [1]), ([0, 1], [1]),
                  ([1], [0, 1]), ([1, 1], [1, 2]),
                  ([1, 1], [1, 2, 1]), ([0, 1], [0, 0, 1]),
                  ([F(1, 2), 1], [F(1, 3), -1])]
    for a, c in band_cases:
        aa, cc, M = new.parameters(a, c)
        w = 4*M
        for i in range(2*w+4):
            for j in range(2*w+4):
                if abs(i-j)>w:
                    check('all_boundary_offband_zeros',
                          new.band_entry(i, j, aa, cc)==0, (a, c, i, j))
        for i in range(w+1, 2*w+5):
            for j in range(w+1, 2*w+5):
                check('stationary_toeplitz_tail', new.band_entry(i, j, aa, cc)==
                      new.stationary_diagonal(i-j, aa, cc), (a, c, i, j))
        for d in range(-w-4, w+5):
            if abs(d)>w:
                check('stationary_bandwidth',
                      new.stationary_diagonal(d, aa, cc)==0, (a, c, d))
        for N in range(1, 11):
            transformed = [[new.band_entry(i, j, aa, cc) for j in range(N)]
                           for i in range(N)]
            check('congruence_vs_direct_hankel',
                  direct_determinant(transformed)==4*direct_hankel(a, c, N),
                  (a, c, N))

    # A too-short difference stencil really fails on a boundary row.
    short_tail = chebyshev_jet_gram_entry(0, 9, (F(1),), (F(1), F(1)))-\
                 chebyshev_jet_gram_entry(0, 7, (F(1),), (F(1), F(1)))
    check('short_stencil_counterexample', short_tail==4)
    transfer_cases = [([1], [1, 1]), ([1], [0, 1]),
                      ([1, 1], [1]), ([0, 1], [1]), ([2, -3], [1]),
                      ([F(1, 2), 1], [F(1, 3)]),
                      ([0], [1]), ([1], [0]), ([2], [F(3, 2)])]
    certificates = []
    for a, c in transfer_cases:
        transfer = new.transfer_determinants(a, c, 48)
        schur = structured_differential_hankel(a, c, 48)
        for N, (x, y) in enumerate(zip(transfer, schur)):
            check('transfer_vs_existing_schur', x==y, (a, c, N))
        for N in range(13):
            check('transfer_vs_direct_fraction_free', transfer[N]==
                  direct_hankel(a, c, N), (a, c, N))
        aa, cc, M = new.parameters(a, c)
        if any(aa) and any(cc) and M:
            certificate = new.krylov_certificate(a, c)
            check('full_state_vector_certificates',
                  new.verify_certificate(a, c, certificate), (a, c))
            corrupted = dict(certificate)
            corrupted['coefficients'] = list(certificate['coefficients'])
            corrupted['coefficients'][0] += 1
            check('corrupted_certificates_rejected', not
                  new.verify_certificate(a, c, corrupted), (a, c))
            for change in ({'coefficients': [0], 'order': 0},
                           {'coefficients': []}, {'order': -1},
                           {'start': 0}, {'states': 1}):
                malformed = dict(certificate)
                malformed.update(change)
                check('malformed_certificates_rejected', not
                      new.verify_certificate(a, c, malformed), (a, c, change))
            L = certificate['order']
            coeffs = certificate['coefficients']
            for n in range(certificate['start'], len(transfer)-L):
                check('certified_recurrences_vs_independent_prefix',
                      sum(coeffs[j]*schur[n+j] for j in range(L+1))==0,
                      (a, c, n))
            numerator, denominator = new.certified_rational_ogf(a, c, certificate)
            for n in range(len(transfer)):
                convolution = sum(denominator[j]*schur[n-j]
                                  for j in range(min(n, len(denominator)-1)+1))
                check('rational_ogf_vs_independent_prefix', convolution==
                      (numerator[n] if n<len(numerator) else 0), (a, c, n))
            certificates.append({'weights': a, 'differential': c,
                                 'certificate': certificate,
                                 'ogf_numerator': numerator,
                                 'ogf_denominator': denominator,
                                 'determinant_prefix': transfer[:16]})

    # A higher-width transfer is exercised without constructing its Krylov basis.
    a, c = [1, 1], [1, 2]
    prefix = new.transfer_determinants(a, c, 10)
    for N in range(11):
        check('M2_transfer_vs_direct', prefix[N]==direct_hankel(a, c, N), N)
    try:
        new.transfer_metadata([1, 1], [1, 2, 1], max_states=20000)
    except ValueError as error:
        check('explicit_state_cap', '2704156' in str(error))
    else:
        raise AssertionError('large-state cap was not enforced')

    result = {
        'checkpoint': 'SEQ-DH-2026-11-20-001',
        'outcome': 'implementation and finite assertions verified in the stated ranges',
        'assertions': dict(checks), 'total_assertions': sum(checks.values()),
        'coverage': {
            'kernel_cases': len(cases), 'kernel_indices': [0, 32],
            'rank_parameter_cases': len(rank_cases), 'rank_degree_plus_order': [1, 3],
            'rank_index_sets_per_case': 3, 'band_cases': len(band_cases),
            'boundary_indices_per_case': '0 <= i,j < 2*(4M)+4',
            'transfer_cases': len(transfer_cases), 'transfer_sizes': [0, 48],
            'direct_determinant_sizes': [0, 12],
            'higher_width_case': {'M': 2, 'transfer_states': 12870, 'sizes': [0, 10]},
            'full_state_certificates': len(certificates),
        },
        'short_stencil_obstruction': {'G00_difference_row_0_column_9': str(short_tail),
                                     'required_boundary_stencil': '(1-E^2)^(2M)'},
        'certificates': certificates,
        'elapsed_seconds': time.perf_counter()-start,
        'non_claims': ['finite checks do not prove the universal theorem',
                       'no independent review or Lean execution',
                       'annihilator orders are not asserted minimal',
                       'no historical novelty or efficient worst-case recurrence bound'],
    }
    output = Path(args.output)
    output.write_text(json.dumps(serialized(result), indent=2)+'\n', encoding='utf-8')
    print(json.dumps({'assertions': sum(checks.values()), 'checks': dict(checks),
                      'certificates': [(entry['certificate']['order'],
                                        entry['certificate']['states'])
                                       for entry in certificates],
                      'elapsed_seconds': result['elapsed_seconds']}))


if __name__=='__main__':
    main()
