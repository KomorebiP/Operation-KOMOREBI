"""Exact discriminator for an opposite-sign shape route. Author: Komorebi P."""
from pathlib import Path
from fractions import Fraction as F
from itertools import combinations
from math import prod
import sys,json
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'solver'))
from pure_type_margins import SAMPLES,gamma
rows=[]
for ss in combinations(SAMPLES,4):
    weights=[s/prod(s-t for t in ss if t!=s) for s in ss]
    values=[(1-gamma(s))/(1+gamma(s)) for s in ss]
    residual=sum(w*y for w,y in zip(weights,values))
    assert residual>0
    rows.append({'samples':list(map(str,ss)),'stencil':str(residual)})
assert len(rows)==35
print(json.dumps({'status':'PASS','tested_four_subsets':35,'results':rows,
 'interpretation':'Every tested admittance stencil is positive. A necessary nonnegative stencil for the complementary shunt-C/RL class therefore does not separate this target.',
 'scope':'Only this four-sample shape on the declared seven Laplace samples; not feasibility or impossibility of the complementary class.'},indent=2))
