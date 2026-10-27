#!/usr/bin/env python3
"""Finite q2 exclusion for the unique norm45 form, conditional on a -1 twist.

Does not prove the twist value, local conductor drop, irreducibility, or a
level-lowering theorem. Those are explicit external hypotheses.
"""
import json
from pathlib import Path
from candidate_local_checks import ROOT, clean, fetch_rows, sha


def trim(p):
    p = [a % 7 for a in p]
    while p and p[-1] == 0:
        p.pop()
    return p


def rem(p, q):
    p, q = trim(p), trim(q)
    while p and len(p) >= len(q):
        c = p[-1] * pow(q[-1], -1, 7) % 7
        d = len(p)-len(q)
        for i, a in enumerate(q):
            p[d+i] = (p[d+i]-c*a) % 7
        p = trim(p)
    return p


def gcd(p, q):
    while q:
        p, q = q, rem(p,q)
    return [(a*pow(p[-1],-1,7)) % 7 for a in p]


def main():
    page = ROOT/'source_records/candidate_lmfdb_45_a.html'
    rows = fetch_rows(page)
    traces = [int(r['eigenvalue']) for r in rows if r['norm'] == 4]
    assert traces == [-3]
    assert r'The Hecke eigenvalue field is $\Q$' in clean(page.read_text())
    a = traces[0]
    R = [4,-a,1]
    odd_quadratics = [[4,-1,1],[4,0,1]]
    odd_gcds = [gcd(R,Q) for Q in odd_quadratics]
    assert odd_gcds == [[1],[1]]
    even_roots = [1,4]
    even_values = [(t*t-a*t+4) % 7 for t in even_roots]
    assert even_values == [1,4]
    result = {'status': 'finite_twisted_q2_exclusion_passed',
              'label': '2.2.5.1-45.1-a',
              'norm4_hecke_trace': a,
              'form_polynomial_ascending': R,
              'odd_C_twisted_quadratic_factors_ascending': odd_quadratics,
              'odd_C_gcds_mod7': odd_gcds,
              'even_C_twisted_full_representation_roots_mod7': even_roots,
              'form_polynomial_values_at_even_roots_mod7': even_values,
              'excluded_under_hypotheses': True,
              'hypotheses_not_proved_here': [
                  'quadratic twist unramified at two with Frobenius value -1',
                  'direct normalized residual comparison of the twisted Beal rank-two factor',
                  'weight two, trivial nebentypus, exact level ideal (3sqrt5)',
                  'applicable modularity, irreducibility, and level-lowering hypotheses',
                  'complete LMFDB norm45 space from separately retained search'],
              'source_page_sha256': sha(page),
              'source_search_sha256': sha(ROOT/'source_records/candidate_lmfdb_45_search.html'),
              'script_sha256': sha(Path(__file__)),
              'no_unconditional_diophantine_conclusion': True}
    out = ROOT/'verification/candidate_twisted45.json'
    out.write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({'status':result['status'],'trace':a,
                      'odd_gcds_mod7':odd_gcds,'even_evaluations_mod7':even_values}))


if __name__ == '__main__':
    main()
