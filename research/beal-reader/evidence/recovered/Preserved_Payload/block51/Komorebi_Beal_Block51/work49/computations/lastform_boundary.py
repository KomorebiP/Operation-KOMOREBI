#!/usr/bin/env python3
"""Exact boundary fingerprint for the surviving level-(45) form.

Counts D: y^2=x^6+324x at every odd split good prime in the retained
twenty-row Hecke page. This is a finite arithmetic check, not a Sturm test.
The mathematical identification additionally needs the conductor and CM
modularity proof in notes/last_form.md.
"""
import argparse
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'work48/computations'))
from candidate_local_checks import clean, fetch_rows, sha
sys.path.insert(0, str(ROOT / 'work47/computations'))
from modular_independent_pointcounts import count_poly


def linear(s):
    s = s.replace(' ', '')
    if 'e' not in s:
        return int(s), 0
    m = re.fullmatch(r'([+-]?\d*)e([+-]\d+)?', s)
    assert m, s
    v = {'': 1, '+': 1, '-': -1}.get(m[1])
    if v is None:
        v = int(m[1])
    return int(m[2] or 0), v


def trace_minpoly(u, v, S, P):
    """e^2-S*e+P=0, trace u+v*e; ascending coefficients."""
    if v == 0:
        return [-u, 1]
    return [u*u+S*u*v+P*v*v, -(2*u+S*v), 1]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    pages = {c: ROOT / f'work48/source_records/candidate_lmfdb_2025_{c}.html'
             for c in 'abcdefghijklmn'}
    # Exact field polynomials are authenticated against the retained pages.
    fields = dict(g=(0, -18), h=(-9, 19), i=(0, -8), j=(-3, -9),
                  k=(0, -8), l=(9, 19), m=(3, -9), n=(0, -18))
    expected_strings = dict(g='x^2 - 18', h='x^2 + 9 x + 19',
                            i='x^2 - 8', j='x^2 + 3 x - 9',
                            k='x^2 - 8', l='x^2 - 9 x + 19',
                            m='x^2 - 3 x - 9', n='x^2 - 18')
    records = []
    for c, path in pages.items():
        rows = fetch_rows(path)
        if c in fields:
            assert expected_strings[c] in clean(path.read_text())
        S, P = fields.get(c, (0, 0))
        q11 = [r for r in rows if r['norm'] == 11]
        polys = [trace_minpoly(*linear(r['eigenvalue']), S, P) for r in q11]
        records.append({'suffix': c, 'q11_eigenvalue_minpolys': polys,
                        'page_sha256': sha(path)})
    matches = [r['suffix'] for r in records
               if all(p == [19, -9, 1] for p in r['q11_eigenvalue_minpolys'])]
    assert matches == ['l']
    rows = fetch_rows(pages['l'])
    checks = []
    for q in (11, 19, 29, 31, 41, 59, 61, 71):
        byq = [r for r in rows if r['norm'] == q]
        assert len(byq) == 2
        full = []
        for r in byq:
            u, v = linear(r['eigenvalue'])
            tr = 2*u+9*v
            nm = u*u+9*u*v+19*v*v
            full.append([q*q, -q*tr, 2*q+nm, -tr, 1])
        assert full[0] == full[1]
        actual = count_poly(27 % q, 0, q)
        assert actual == full[0], (q, actual, full)
        checks.append({'q': q, 'hecke_traces': [r['eigenvalue'] for r in byq],
                       'full_frobenius_polynomial': actual,
                       'comparison': 'exact_in_Z_not_only_mod7'})
    assert checks[0]['full_frobenius_polynomial'] == [121, -99, 41, -9, 1]
    # Cross-check the crucial q11 count directly in F11 and F121, with an
    # independent square-set implementation, not the norm-character routine.
    from modular_correlations import point_counts_trace_polynomial
    direct = point_counts_trace_polynomial([0, 324, 0, 0, 0, 0, 1], 11)
    assert direct['jacobian_frobenius_polynomial'] == checks[0]['full_frobenius_polynomial']
    out = {'status': 'exact_boundary_fingerprints_agree',
           'curve': 'y^2=x^6+324*x',
           'all_14_q11_fingerprints': records,
           'unique_q11_form': '2.2.5.1-2025.1-l',
           'q11_independent_count': direct,
           'checks': checks,
           'non_claims': ['finite matching alone is not a modular-form identity',
                          'CM modularity and exact conductor are written external-theorem steps',
                          'no integer solution or Diophantine nonexistence follows'],
           'code_sha256': sha(Path(__file__))}
    args.output.write_text(json.dumps(out, indent=2)+'\n')
    print(json.dumps({'status': out['status'], 'unique_q11_form': out['unique_q11_form'],
                      'odd_good_prime_checks': len(checks)}))


if __name__ == '__main__':
    main()
