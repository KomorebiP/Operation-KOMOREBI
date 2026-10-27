"""Fit and run a controlled stochastic realization using only a saved table.

No hidden generator is imported. Exact population probabilities are supplied in
population_tables.json. Its declared global rank bound is an assumption.
"""
from __future__ import annotations
from pathlib import Path
import json
import sys
import sympy as sp
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'checks'))
from stochastic_reference import fit_core


def main() -> None:
    path=Path(__file__).with_name('population_tables.json')
    data=json.loads(path.read_text(encoding='utf-8'))
    def matrix(raw):
        return sp.Matrix([[sp.Rational(value) for value in row] for row in raw])
    model=fit_core(matrix(data['core']),
                   {tuple(map(int,key.split(','))):matrix(value) for key,value in data['shifted'].items()},
                   matrix(data['initial']),rank_upper_bound=data['rank_upper_bound_assumed'])
    print('Core determinant:',model.core.det())
    print('Initial predictive state:',list(model.initial))
    z=model.initial
    for s in [(0,1),(1,0)]:
        probability,z=model.update(z,s)
        print(f'Action {s[0]}, observation {s[1]}: likelihood={probability}, predictive state={list(z)}')
    print('Two-step word probability:',model.probability(((0,1),(1,0))))
    print('The global rank bound is assumed, not established by a finite table.')
    print('No probability cone or hidden generator was supplied to this learner.')
    (ROOT/'verification'/'observable_example_certificate.json').write_text(
        json.dumps(model.certificate(),indent=2)+'\n',encoding='utf-8')


if __name__=='__main__':
    main()
