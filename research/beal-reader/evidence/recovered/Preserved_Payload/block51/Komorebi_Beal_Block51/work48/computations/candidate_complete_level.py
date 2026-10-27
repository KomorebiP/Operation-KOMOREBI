#!/usr/bin/env python3
"""Exact all-14-form refinement at level (45), using cached LMFDB data.

No numerical PV indices or CM flags are used in the elimination. All norm4
traces are rational, so those comparisons need no coefficient-field choices.
The one split-coefficient-field correlation retains one embedding throughout.
"""
import hashlib
import json
from pathlib import Path
import sys

from candidate_local_checks import ROOT, OLD, clean, fetch_rows, sha, square_frob

sys.path.insert(0, str(ROOT.parent / 'work47/computations'))
from modular_independent_pointcounts import count_poly


def same_mod7(p, q):
    return [x % 7 for x in p] == [x % 7 for x in q]


def main():
    rows = {}
    sources = []
    for c in 'abcdefghijklmn':
        path = ROOT / ('source_records/candidate_lmfdb_2025_'+c+'.html')
        rows[c] = fetch_rows(path)
        sources.append({'label': c, 'path': str(path.relative_to(ROOT)), 'sha256': sha(path)})
    a4 = {c: int(next(r['eigenvalue'] for r in rows[c] if r['norm'] == 4)) for c in rows}
    assert list(a4.values()) == [0, 3, 4, -4, 1, 0, -2, 0, 3, -2, -3, 0, -2, 2]
    odd_survive = [c for c, a in a4.items() if a % 7 in (0, 6)]
    # With determinant4, two eigenvalues chosen from {-1,-4} must be
    # the distinct pair: repeated products1,16 are not4 modulo7.
    even_survive = [c for c, a in a4.items() if a % 7 == (-5) % 7]
    assert odd_survive == list('afhl') and even_survive == ['n']
    old = json.loads(OLD.read_text())
    a19 = [r for r in rows['a'] if r['norm'] == 19]
    assert [r['eigenvalue'] for r in a19] == ['-5', '-5']
    a19_matches = [r for r in old['q19_weighted_orbit_point_counts']['orbits'] if
                  same_mod7(r['jacobian_frobenius_polynomial'], square_frob(19, -5))]
    assert not a19_matches and (-5) % 7 not in (20 % 7, -20 % 7)

    f29 = [r for r in rows['f'] if r['norm'] == 29]
    assert [r['eigenvalue'] for r in f29] == ['10', '10']
    q = 29
    pending = {(A, B) for A in range(q) for B in range(q) if (A**3+B**5) % q}
    assert len(pending) == 812
    orbits = []
    while pending:
        A, B = min(pending)
        orbit = sorted({(A*pow(u,5,q) % q, B*pow(u,3,q) % q) for u in range(1,q)})
        assert set(orbit) <= pending
        pending.difference_update(orbit)
        poly = count_poly(A, B, q)
        orbits.append({'A': A, 'B': B, 'orbit': orbit,
                       'jacobian_frobenius_polynomial': poly,
                       'matches_f_mod7': same_mod7(poly, square_frob(q,10))})
    assert len(orbits) == 29 and sum(len(r['orbit']) for r in orbits) == 812
    assert not any(r['matches_f_mod7'] for r in orbits)
    assert 10 % 7 not in (30 % 7, -30 % 7)

    npath = ROOT/'source_records/candidate_lmfdb_2025_n.html'
    assert r'\(x^2 - 18\)' in clean(npath.read_text())
    n11 = [r for r in rows['n'] if r['norm'] == 11]
    assert [r['eigenvalue'] for r in n11] == ['-e', 'e']
    nembeddings = []
    for e in range(7):
        if (e*e-18) % 7:
            continue
        traces = [(-e) % 7, e]
        polys = [[x % 7 for x in square_frob(11,a)] for a in traces]
        assert polys[0] != polys[1]
        nembeddings.append({'e_mod7': e, 'ordered_traces': traces,
                            'underlying_full_polynomials': polys,
                            'equal_as_required_for_J_over_Q': False})
    assert [r['e_mod7'] for r in nembeddings] == [2,5]

    result = {'status': 'all_14_orbits_reduce_to_l_under_direct_modular_comparison',
              'level_ideal': '(45)=3^2*(sqrt(5))^2', 'level_norm': 2025,
              'conditional': True,
              'conditions': ['complete LMFDB list of weight-(2,2), trivial-character forms at (45)',
                             'direct normalized residual comparison of the Beal Jacobian rank-two factor to a listed form',
                             'fixed prime and embedding of each coefficient field above seven',
                             'standard multiplicative-prime comparison at eleven, nineteen, twenty-nine'],
              'source_pages': sources, 'norm4_traces': a4,
              'odd_C_norm4_survivors': odd_survive,
              'even_C_norm4_survivors': even_survive,
              'a_exclusion_at19': {'trace': -5, 'smooth_matches': [],
                                  'multiplicative_traces_mod7': [20 % 7, -20 % 7]},
              'f_exclusion_at29': {'trace': 10, 'orbits': orbits,
                                  'smooth_pair_count': 812,
                                  'multiplicative_traces_mod7': [30 % 7, -30 % 7]},
              'n_fixed_embedding_correlation_at11': nembeddings,
              'h_exclusion_reference': 'candidate_local_checks.json',
              'only_survivor': '2.2.5.1-2025.1-l',
              'survivor_conditions': {'C_parity': 'odd', 'A_parity': 'odd',
                                       'B_divisible_by': 418,
                                       'A_C_pairs_mod11': [[5,9],[6,2]]},
              'not_claimed': ['elimination of l', 'other levels exhausted',
                              'PV index dictionary', 'Diophantine nonexistence'],
              'script_sha256': sha(Path(__file__)),
              'pointcount_implementation_sha256': sha(ROOT.parent/'work47/computations/modular_independent_pointcounts.py'),
              'old_pointcount_data_sha256': sha(OLD)}
    out = ROOT/'verification/candidate_complete_level.json'
    out.write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({k:result[k] for k in ['status','odd_C_norm4_survivors','even_C_norm4_survivors','only_survivor','survivor_conditions']}))


if __name__ == '__main__':
    main()
