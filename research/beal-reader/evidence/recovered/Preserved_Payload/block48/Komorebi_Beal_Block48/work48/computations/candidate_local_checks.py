#!/usr/bin/env python3
"""Exact checks on authenticated LMFDB HTML and prior point-count certificates.

No Sage/Magma calls; no eval of downloaded code; no new modular-space computation.
"""
import hashlib
import html
import json
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
OLD = ROOT.parent / 'work47' / 'verification' / 'modular_correlations.json'


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def clean(s):
    return ' '.join(html.unescape(re.sub(r'<[^>]+>', ' ', s)).split())


def fetch_rows(path):
    out = []
    for row in re.findall(r'<tr[^>]*>(.*?)</tr>', path.read_text(), re.S):
        cells = [clean(x) for x in re.findall(r'<td[^>]*>(.*?)</td>', row, re.S)]
        if len(cells) == 3 and cells[0].isdigit() and '$[' in cells[1]:
            eigen = cells[2].replace('$', '').replace(r'\phantom{-}', '').strip()
            out.append({'norm': int(cells[0]), 'ideal': cells[1], 'eigenvalue': eigen})
    assert len(out) == 20, (path, len(out))
    return out


def square_frob(q, a):
    return [q*q, -2*q*a, a*a+2*q, -2*a, 1]


def main():
    search = ROOT / 'source_records/candidate_lmfdb_2025_search.html'
    summary = []
    for row in re.findall(r'<tr[^>]*>(.*?)</tr>', search.read_text(), re.S):
        if '2025.1-' not in row:
            continue
        cells = [clean(x) for x in re.findall(r'<td[^>]*>(.*?)</td>', row, re.S)]
        assert len(cells) == 10
        summary.append({'label': '2.2.5.1-'+cells[0],
                        'degree': int(cells[7].replace('$', '')),
                        'CM_flag_displayed': cells[8] == '✓'})
    assert len(summary) == 14
    assert [r['label'][-1] for r in summary if r['CM_flag_displayed']] == list('cdehl')
    old = json.loads(OLD.read_text())
    rows19 = old['q19_weighted_orbit_point_counts']['orbits']
    rows11 = old['q11_complete_smooth_Beal_point_counts']
    forms = []
    expected2 = dict(c=4, d=-4, e=1, h=0, l=0)
    for c in 'cdehl':
        path = ROOT / ('source_records/candidate_lmfdb_2025_'+c+'.html')
        rows = fetch_rows(path)
        bynorm = {q: [r for r in rows if r['norm'] == q] for q in (4, 11, 19)}
        a2 = int(bynorm[4][0]['eigenvalue'])
        assert a2 == expected2[c]
        even_values = [((t*t-a2*t+4) % 7) for t in (-1, -4)]
        assert all(even_values), (c, even_values)
        pol = [v % 7 for v in square_frob(4, a2)]
        parity = []
        for (A, B), trace in (((0, 1), -1), ((1, 0), 0)):
            if pol == [v % 7 for v in square_frob(4, trace)]:
                parity.append([A, B])
        a19 = int(bynorm[19][0]['eigenvalue'])
        assert all(int(r['eigenvalue']) == a19 for r in bynorm[19])
        matches19 = [r for r in rows19 if
                     [v % 7 for v in r['jacobian_frobenius_polynomial']] ==
                     [v % 7 for v in square_frob(19, a19)]]
        boundary19 = a19 % 7 in ((19+1) % 7, -(19+1) % 7)
        if c in 'hl':
            assert parity == [[1, 0]] and a19 == 0
            assert {(r['A'], r['B']) for r in matches19} == {(1, 0)}
            assert not boundary19
            trace_sum = -9 if c == 'h' else 9
            trace_product = 19
            # At either base prime the two coefficient embeddings have
            # trace sum +/-9 and product 19. Discriminant 5 is nonsquare mod7.
            assert pow(5, 3, 7) == 6
            full11 = [121, -11*trace_sum, trace_product+22, -trace_sum, 1]
            matches11 = [r for r in rows11 if
                         [v % 7 for v in r['jacobian_frobenius_polynomial']] ==
                         [v % 7 for v in full11]]
            matched11 = [[r['A'], r['B']] for r in matches11]
            assert matched11 == ([] if c == 'h' else [[5, 0], [6, 0]])
            # The multiplicative comparisons are +/-12 in F7. Neither
            # is a root of X^2 - trace_sum*X + trace_product modulo7.
            boundary11 = [((a*a-trace_sum*a+trace_product) % 7) for a in (12, -12)]
            assert all(boundary11)
        else:
            assert not parity and not matches19
            assert all(int(r['eigenvalue']) == 0 for r in bynorm[11])
            matches11 = [r for r in rows11 if
                         [v % 7 for v in r['jacobian_frobenius_polynomial']] ==
                         [v % 7 for v in square_frob(11, 0)]]
            assert len(matches11) == 10 and all(r['A'] == 0 for r in matches11)
            matched11 = [[r['A'], r['B']] for r in matches11]
            boundary11 = None
        forms.append({'label': '2.2.5.1-2025.1-'+c,
                      'page_sha256': sha(path), 'hecke_rows': rows,
                      'norm4_trace_mod7': a2 % 7,
                      'even_C_polynomial_values_at_minus1_minus4': even_values,
                      'even_C_excluded': True,
                      'compatible_A_B_parity_for_odd_C': parity,
                      'norm19_trace_mod7': a19 % 7,
                      'smooth11_matching_pairs': matched11,
                      'boundary11_trace_polynomial_values_at_plus_minus12': boundary11,
                      'smooth19_matching_orbit_representatives':
                          [[r['A'], r['B']] for r in matches19],
                      'multiplicative19_match': boundary19})
    result = {'status': 'exact_checks_passed_on_imported_Hecke_data',
              'date_checked': '2026-09-19',
              'conditions': ['modular comparison to the named form modulo seven',
                             'determinant equals the cyclotomic character',
                             'Block46 good-reduction Frobenius polynomial for odd C',
                             'Block47 semistable Frobenius eigenvalues for even C',
                             'standard multiplicative-prime comparison for q19'],
              'not_claimed': ['independent computation of the Hilbert form space',
                              'PV-to-LMFDB numerical index dictionary',
                              'elimination of all forms or of the equation'],
              'search_sha256': sha(search), 'search_rows': summary,
              'pointcount_source_sha256': sha(OLD), 'forms': forms}
    dest = ROOT / 'verification/candidate_local_checks.json'
    dest.write_text(json.dumps(result, indent=2)+'\n')
    print(json.dumps({'status': result['status'],
                      'odd_C_excluded': [r['label'] for r in forms if not r['compatible_A_B_parity_for_odd_C']],
                      'even_C_excluded': [r['label'] for r in forms],
                      'all_C_excluded': ['2.2.5.1-2025.1-'+c for c in 'cdeh'],
                      'conditional_B_divisible_by_418': ['2.2.5.1-2025.1-l']}))


if __name__ == '__main__':
    main()
