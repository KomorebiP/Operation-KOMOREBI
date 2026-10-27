#!/usr/bin/env python3
"""Exact characteristic-zero matrices and cyclotomic commutator algebra.
Finite audits only. The all-depth theorem has a separate written proof.
"""
from __future__ import annotations
import argparse,hashlib,itertools,json
from fractions import Fraction as F
from pathlib import Path

def check(ok,msg):
    if not ok: raise AssertionError(msg)
def add(x,y):return (x[0]+y[0],x[1]+y[1])
def neg(x):return (-x[0],-x[1])
def mul(x,y):return (x[0]*y[0]+5*x[1]*y[1],x[0]*y[1]+x[1]*y[0])
def inv(x):
    n=x[0]*x[0]-5*x[1]*x[1]
    return (F(x[0],n),F(-x[1],n))
def mod7(x):
    x=F(x);check(x.denominator%7!=0,'Not integral at7')
    return (x.numerator%7)*pow(x.denominator,-1,7)%7
def code(x):return mod7(x[0])+7*mod7(x[1])
def inputs(n,h,i):
    D=(7**(n//2+1)*(i%11-5),7**(n//2+1)*((3*i+1)%13-6))
    b=((5*i+2)%17-8,(7*i+3)%19-9)
    c=((11*i+1)%23-11,(13*i+4)%29-14)
    Q=1+7**h*(i%6+1)
    return D,b,c,Q

def build():
    cases=nonrational=half_not_full=0;digest=hashlib.sha256();inp=hashlib.sha256()
    for n in range(1,13):
        m=n//2+1
        for off in range(3):
            h=(n+1)//2+off
            for i in range(60):
                D,b,c,Q=inputs(n,h,i);d=add((1,0),D);bc=mul(b,c)
                a=mul(add((Q,0),(7**n*bc[0],7**n*bc[1])),inv(d))
                check(add(mul(a,d),neg((7**n*bc[0],7**n*bc[1])))==(Q,0),'Exact determinant failure')
                t=add(add(a,d),(-(Q+1),0));T=(t[0]/7**n,t[1]/7**n)
                actual=code(T);expected=code(bc);check(actual==expected,'Deep trace-product failure')
                cases+=1;nonrational+=int(any(x[1]!=0 for x in [D,b,c]))
                if n>m and (D[0]%(7**n) or D[1]%(7**n)):half_not_full+=1
                digest.update(f'{n},{h},{i},{actual},{expected}\n'.encode())
                inp.update(json.dumps([n,h,i,D,b,c,Q],separators=(',',':')).encode()+b'\n')
    # Explicit shallow counterexample: all identities exact over Z.
    a,b,c,d,Q,n=302,1,44,50,8,3
    check(a*d-7**n*b*c==Q,'Shallow control determinant')
    trace=(a+d-Q-1)//7**n
    check((trace%7,b*c%7)==(1,2),'Shallow control disappeared')
    # Largest possible joint image has seven prime-field dimensions.
    total=0;weights=[3,3,3,5,5,5,5]
    for v in itertools.product(range(7),repeat=7):
        recovered=tuple(((w-1)*pow(w-1,-1,7)*x)%7 for w,x in zip(weights,v))
        check(recovered==v,'Commutator image inverse failed');total+=1
    return {'schema':'beal.block67.deep_trace.v1','status':'PASS_DEEP_ALGEBRA',
      'matrix_cases':cases,'nonrational_input_cases':nonrational,'half_precision_not_full_cases':half_not_full,
      'depths':list(range(1,13)),'input_sha256':inp.hexdigest(),'result_sha256':digest.hexdigest(),
      'commutator_vectors':total,'cyclotomic_weights':weights,
      'shallow_control':{'n':3,'Q':8,'matrix':[[302,1],[15092,50]],'trace_correction':1,'product':2},
      'trivial_weight_control':{'weight':1,'T_minus_I':0,'restriction_can_kill_image':True},
      'scope':'Finite ring/linear-algebra checks, not an independent Galois or geometric proof.'}

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--output',type=Path,required=True);a=ap.parse_args();o=build()
    a.output.parent.mkdir(parents=True,exist_ok=True);a.output.write_text(json.dumps(o,indent=2,sort_keys=True)+'\n');print(o['status'],o['matrix_cases'])
if __name__=='__main__':main()
