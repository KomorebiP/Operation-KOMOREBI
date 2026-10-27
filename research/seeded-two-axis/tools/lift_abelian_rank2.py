#!/usr/bin/env python3
"""Finite certificate for a continuous Z_p^r action on (Z/p^n)^2.

Only unconstrained GL_2 lifts are certified. No determinant, ramification,
Galois, or automorphic conditions are imposed. See manuscript K78--K81.
"""
from __future__ import annotations
import argparse
import itertools
import json
from math import isqrt
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from checks.check_profinite_lifting import classify2, commute2, unipotent_modp

def prime(p:int)->bool:
    return p>=2 and all(p%d for d in range(2,isqrt(p)+1))

def certify(data:dict)->dict:
    if not isinstance(data,dict):
        raise ValueError('Input must be a JSON object.')
    p=data.get('p'); n=data.get('n')
    if type(p) is not int or not prime(p):raise ValueError('p must be prime.')
    if type(n) is not int or n<1:raise ValueError('n must be a positive integer.')
    raw=data.get('generators')
    if not isinstance(raw,list) or not raw:raise ValueError('Supply a nonempty generator list.')
    As=[];q=p**n
    for A in raw:
        if isinstance(A,list) and len(A)==2 and all(isinstance(row,list) and len(row)==2 for row in A):
            A=A[0]+A[1]
        if not isinstance(A,list) or len(A)!=4 or any(type(x) is not int for x in A):
            raise ValueError('Each generator must be an integer 2-by-2 matrix.')
        A=tuple(x%q for x in A)
        if not unipotent_modp(A,p):
            raise ValueError('A generator has non-p-power residual order: not an action of Z_p^r.')
        As.append(A)
    if any(not commute2(A,B,q) for A,B in itertools.combinations(As,2)):
        raise ValueError('The supplied matrices do not commute at the requested precision.')
    cert=classify2(tuple(As),p,n)
    result={'source':'Z_p^r','p':p,'n':n,'r':len(As),'rank':2,
            'input_residues':As,'status':'LIFTABLE' if cert['ok'] else 'NOT_LIFTABLE',
            'uniform_horizon':2*n-1,'certificate':cert,
            'proof_status':'Finite certificate interpreted by written manuscript K78--K81; not Lean-certified.',
            'excluded_conditions':['prescribed determinant','geometric local conditions','automorphic realization']}
    if cert['a']<n:result['data_adapted_horizon']=n+cert['a']
    else:result['data_adapted_horizon']=n
    return result

def main()->int:
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('input',type=Path);ap.add_argument('--output',type=Path)
    args=ap.parse_args()
    try:
        result=certify(json.loads(args.input.read_text()))
    except (ValueError,TypeError,OSError,json.JSONDecodeError) as e:
        print(f'Input error: {e}',file=sys.stderr);return 2
    text=json.dumps(result,indent=2)+'\n'
    if args.output:
        args.output.parent.mkdir(parents=True,exist_ok=True);args.output.write_text(text)
    else:print(text,end='')
    return 0
if __name__=='__main__':raise SystemExit(main())
