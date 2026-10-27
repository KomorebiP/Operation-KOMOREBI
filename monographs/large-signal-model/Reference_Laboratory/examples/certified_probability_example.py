"""Learn operators and a finite probability domain from observable tables only."""
from __future__ import annotations
import json
from pathlib import Path
import sys
import sympy as sp
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/'checks'))
from stochastic_reference import fit_core
from cone_reference import search_interval


def load_observable_model():
    data = json.loads((ROOT/'examples'/'population_tables.json').read_text())
    matrix = lambda x: sp.ImmutableMatrix([[sp.Rational(v) for v in row] for row in x])
    return fit_core(matrix(data['core']),
                    {tuple(map(int,k.split(','))): matrix(v) for k,v in data['shifted'].items()},
                    matrix(data['initial']), rank_upper_bound=data['rank_upper_bound_assumed'])


def main():
    model = load_observable_model()
    found = search_interval(model.operators, model.initial, denominator_bound=8)
    if found is None:
        raise RuntimeError('The declared interval grid did not produce a certificate.')
    print(f'Invariant interval: [{found.lower}, {found.upper}]')
    print(f'Candidate checks: {found.tested_candidates}/{found.candidate_count}')
    print('Initial positive weights:', list(found.weights))
    print('Minimum lift entry:', found.report['witness_minimum_entry'])
    print('All-word internal validity: certified by exact finite identities.')
    print('Global rank coverage and population-table correctness remain model assumptions.')
    print('No hidden generator or hidden cone was supplied.')
    (ROOT/'verification').mkdir(exist_ok=True)
    (ROOT/'verification'/'learned_cone_certificate.json').write_text(json.dumps(found.report, indent=2)+'\n')


if __name__ == '__main__':
    main()
