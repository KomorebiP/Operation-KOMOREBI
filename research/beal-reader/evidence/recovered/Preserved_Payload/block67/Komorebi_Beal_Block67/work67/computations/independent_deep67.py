#!/usr/bin/env python3
"""Separate finite quotient-ring audit: theta^2=theta+1, no primary imports."""
from __future__ import annotations
import argparse,hashlib,itertools,json
from pathlib import Path

def ck(ok,msg):
    if not ok:raise AssertionError(msg)
def add(x,y,M):return ((x[0]+y[0])%M,(x[1]+y[1])%M)
def mul(x,y,M):return ((x[0]*y[0]+x[1]*y[1])%M,(x[0]*y[1]+x[1]*y[0]+x[1]*y[1])%M)
def inverse(x,M):
    a,b=x;n=(a*a+a*b-b*b)%M;iv=pow(n,-1,M)
    return ((a+b)*iv%M,-b*iv%M)
def change(x,M):return ((x[0]-x[1])%M,2*x[1]%M)
def wcode(x):return (x[0]+4*x[1])%7+7*(4*x[1]%7)

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--certificate',type=Path,required=True);ap.add_argument('--output',type=Path,required=True);a=ap.parse_args();cert=json.loads(a.certificate.read_text())
    ck(cert['status']=='PASS_DEEP_ALGEBRA','Wrong deep-algebra status');count=nr=partial=0;ih=hashlib.sha256();rh=hashlib.sha256()
    for n in range(1,13):
        m=n//2+1;M=7**(n+1)
        for h in range((n+1)//2,(n+1)//2+3):
            for i in range(60):
                rawD=(7**m*(i%11-5),7**m*((3*i+1)%13-6));rawB=((5*i+2)%17-8,(7*i+3)%19-9);rawC=((11*i+1)%23-11,(13*i+4)%29-14);Q=1+7**h*(i%6+1)
                D=change(rawD,M);b=change(rawB,M);c=change(rawC,M);d=add((1,0),D,M);bc=mul(b,c,M)
                av=mul(add((Q,0),(7**n*bc[0],7**n*bc[1]),M),inverse(d,M),M)
                det=add(mul(av,d,M),(-7**n*bc[0],-7**n*bc[1]),M);ck(det==(Q%M,0),'Finite determinant failed')
                t=add(add(av,d,M),(-(Q+1),0),M);ck(all(x%(7**n)==0 for x in t),'Missing normalized-trace divisibility')
                T=(t[0]//7**n,t[1]//7**n);actual=wcode(T);expected=wcode(bc);ck(actual==expected,'Independent deep trace failed')
                count+=1;nr+=int(any(x[1]!=0 for x in [rawD,rawB,rawC]));partial+=int(n>m and (rawD[0]%(7**n)!=0 or rawD[1]%(7**n)!=0))
                ih.update(json.dumps([n,h,i,rawD,rawB,rawC,Q],separators=(',',':')).encode()+b'\n');rh.update(f'{n},{h},{i},{actual},{expected}\n'.encode())
    ck((count,nr,partial)==(cert['matrix_cases'],cert['nonrational_input_cases'],cert['half_precision_not_full_cases']),'Changed matrix coverage')
    ck(ih.hexdigest()==cert['input_sha256'] and rh.hexdigest()==cert['result_sha256'],'Changed deep-trace digest')
    # Check surjectivity by explicit inverse on every encoded vector, not rational fractions.
    size=7**7;weights=(3,3,3,5,5,5,5)
    for code in range(size):
        t=code;recovered=0;place=1
        for w in weights:
            x=t%7;t//=7;pre=x*pow(w-1,-1,7)%7;image=((w-1)*pre)%7;recovered+=place*image;place*=7
        ck(recovered==code,'Independent commutator inverse')
    ck(cert['commutator_vectors']==size and cert['cyclotomic_weights']==list(weights),'Changed commutator coverage')
    shallow={'n':3,'Q':8,'matrix':[[302,1],[15092,50]],'trace_correction':1,'product':2}
    ck(302*50-15092==8 and (302+50-9)//343%7==1 and 44%7==2,'Independent shallow negative control')
    ck(cert['shallow_control']==shallow,'Changed shallow counterexample')
    ck(cert['trivial_weight_control']=={'weight':1,'T_minus_I':0,'restriction_can_kill_image':True},'Changed trivial-weight control')
    out={'schema':'beal.block67.independent_deep.v1','status':'PASS_INDEPENDENT_DEEP','primary_imports':False,'matrix_cases':count,'nonrational_cases':nr,'partial_diagonal_cases':partial,'depths':list(range(1,13)),'commutator_vectors':size,'result_sha256':rh.hexdigest(),'basis':'theta^2=theta+1 modulo7^(n+1), contrasted with exact Fraction/w primary'}
    a.output.parent.mkdir(parents=True,exist_ok=True);a.output.write_text(json.dumps(out,indent=2,sort_keys=True)+'\n');print(out['status'],count)
if __name__=='__main__':main()
