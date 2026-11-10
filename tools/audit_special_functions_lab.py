"""Independent dense-series audit for the browser's bounded rational model.

Run: python -B tools/audit_special_functions_lab.py --node NODE [--output result.json]
The tested finite population is explicit; this is not an entire-function proof.
"""
import argparse
from fractions import Fraction as Q
from itertools import product
import json
from math import factorial
from pathlib import Path
import shutil
import subprocess
import time

ROOT = Path(__file__).resolve().parents[1]


def dense(scales, count):
    """Coefficient extraction in all degrees, independently of odd indexing."""
    q, r, a, b = map(Q, scales)
    u, v = [Q(0)], [Q(0)]
    for d in range(2*count-1):
        du = Q(d == 0) + sum((u[i]*v[d-i]*q**i*r**(d-i) for i in range(d+1)), Q(0))
        dv = Q(d == 0) + sum((u[i]*v[d-i]*a**i*b**(d-i) for i in range(d+1)), Q(0))
        u.append(du/(d+1))
        v.append(dv/(d+1))
    return u, v


def audit(node=None):
    node = node or shutil.which('node')
    if not node:
        raise RuntimeError('Node.js is required; use --node /path/to/node.')
    start = time.monotonic()
    cases = [dict(scales=list(s), count=6) for s in product(('1/4','1/2','3/4'), repeat=4)]
    cases += [dict(scales=['1/3','2/3','1/2','3/4'],count=12),
              dict(scales=['1/100','99/100','97/100','89/100'],count=16),
              dict(scales=['99/100']*4,count=16), dict(scales=['1/2']*4,count=1)]
    probe = subprocess.run([node, str(ROOT/'tools/special_functions_lab_probe.mjs')],
                           input=json.dumps(cases), text=True, encoding='utf-8',
                           capture_output=True, check=True, timeout=60)
    result = json.loads(probe.stdout)
    if len(result['rows']) != len(cases):
        raise AssertionError('The probe did not visit the declared population.')
    counts = {}

    def check(name, condition):
        if not condition:
            raise AssertionError(name)
        counts[name] = counts.get(name,0)+1

    for case, observed in zip(cases, result['rows']):
        du, dv = dense(case['scales'],case['count'])
        for label, exact in (('u',du),('v',dv)):
            check('dense_coefficients',list(map(Q,observed[label])) == exact[1::2])
            check('even_coefficients',all(x == 0 for x in exact[::2]))
            for n,value in enumerate(exact[1::2]):
                check('positive_majorant',0 < value <= Q(1,2)**n)
            for sample in observed['samples']:
                x = Q(sample['x'])
                check('exact_evaluation',Q(sample[label]) == sum((c*x**n for n,c in enumerate(exact)),Q(0)))
            if case['scales'] == ['1/2']*4:
                check('sinh_anchor',exact[1::2] == [Q(1,2**n*factorial(2*n+1)) for n in range(case['count'])])
        for bound in observed['bounds']:
            radius = Q(bound['radius']);rho=radius**2/2
            check('tail_formula',Q(bound['value']) == radius*rho**case['count']/(1-rho))
    # A finite omitted-sum check catches count/first-omitted-index errors.
    u,v = dense(['1/3','2/3','1/2','3/4'],12)
    for n in (1,2,6):
        for radius in (Q(0),Q(1,2),Q(1),Q(4,3)):
            rho=radius**2/2; bound=radius*rho**n/(1-rho)
            for values in (u,v):
                check('finite_omitted_sum',0 <= sum((values[2*i+1]*radius**(2*i+1) for i in range(n,12)),Q(0)) <= bound)
    check('default_hand_values', [u[3],v[3],u[5],v[5]] == [Q(2,27),Q(1,8),Q(31,10935),Q(307,46080)])
    return {'status':'passed','parameter_cases':len(cases),'grid_cases':81,
            'assertions':sum(counts.values())+result['controls'],'python_checks':counts,
            'javascript_controls':result['controls'],'node_version':result['node'],
            'largest_probe_ms':round(max(row['elapsed_ms'] for row in result['rows']),3),
            'seconds':round(time.monotonic()-start,3),
            'scope':'Finite exact cross-check of the bounded browser recurrence, evaluations, contributions, tail formula, symmetry, input and serialization controls. No new universal proof or Lean coverage.'}


if __name__ == '__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--node');parser.add_argument('--output',type=Path)
    args=parser.parse_args();report=audit(args.node)
    rendered=json.dumps(report,indent=2)+'\n'
    if args.output:
        args.output.parent.mkdir(parents=True,exist_ok=True)
        args.output.write_text(rendered,encoding='utf-8',newline='\n')
    print(rendered,end='')
