#!/usr/bin/env python3
"""Exact Frey point counts at1051. Derived from the pinned Block62 primary implementation.
Python 3.10+, standard library. Finite assertions only; geometry is inherited.
"""
from __future__ import annotations
import argparse, hashlib, json, math
from pathlib import Path
PRIMES=(1051,)

def require(ok:bool,why:str)->None:
    if not ok: raise AssertionError(why)

def character(a:int,p:int)->int:
    v=pow(a%p,(p-1)//2,p)
    return -1 if v==p-1 else v

def tables(p:int):
    d=next(d for d in range(2,p) if character(d,p)==-1)
    leg=[character(x,p) for x in range(p)]
    base=[(x,pow(x,3,p),pow(x,6,p)) for x in range(p)]
    extension=[]
    for x in range(p):
        for y in range(p):
            a=(x*x+d*y*y)%p;b=2*x*y%p
            c=(a*x+d*b*y)%p;e=(a*y+b*x)%p
            extension.append((x,y,c,e,(c*c+d*e*e)%p,2*c*e%p))
    return d,leg,base,extension

def counts(a:int,b:int,p:int,tabs,degree:int)->int:
    d,leg,base,extension=tabs
    A=12*a%p;B=10*b%p;C=5*b*b%p
    if degree==1:
        return p+2+sum(leg[(x6+B*x3+A*x+C)%p] for x,x3,x6 in base)
    total=0
    for x,y,x3,y3,x6,y6 in extension:
        u=(x6+B*x3+A*x+C)%p;v=(y6+B*y3+A*y)%p
        total+=leg[(u*u-d*v*v)%p]
    return p*p+2+total

def local_polynomial(p:int,n1:int,n2:int,f:int,nu:int):
    s=p+1-n1;n=s*s-p*p-1+n2
    require(n%2==0,'Nonintegral second coefficient')
    b=n//2;rational=[p*p,-p*s,b,-s,1]
    if f==2:s,b=s*s-2*b,b*b-2*p*s*s+2*p*p
    Q=p**f
    return rational,[Q*Q,-nu*Q*s,b,-nu*s,1]

def defect_roots(P:list[int],Q:int)->list[int]:
    """All possible actual (tau-Q-1)/7 mod7; w^2=5, code a+7*b."""
    S=-P[3];D=S*S-4*(P[2]-2*Q)
    require(D>=0 and D%5==0,'Non-RM discriminant in residual locus')
    v=math.isqrt(D//5);require(5*v*v==D,'Nonsquare RM discriminant')
    require((S-2*(Q+1))%7==0 and v%7==0,'Scalar residual precision missing')
    a=((S-2*(Q+1))//7*4)%7;b=(v//7*4)%7
    return sorted({a+7*b,a+7*((-b)%7)})

def run_prime(p:int)->dict:
    require(p in PRIMES and all(p%d for d in range(2,math.isqrt(p)+1)),'Unsupported modulus')
    f=1 if p%5 in (1,4) else 2;Q=p**f
    nu=(1 if Q%5==1 else -1)*character(-3,p)**f
    seventh={pow(c,7,p) for c in range(1,p)}
    eligible={(a,b) for a in range(p) for b in range(p) if (a**3+b**5)%p in seventh}
    todo=set(eligible);covered=set();rows=[]
    scalings=[(pow(u,5,p),pow(u,3,p)) for u in range(1,p)]
    tabs=tables(p);target=[Q*Q,-2*Q*(Q+1),(Q+1)**2+2*Q,-2*(Q+1),1]
    good=set();number2=0
    while todo:
        a,b=min(todo)
        orbit={(a*u5%p,b*u3%p) for u5,u3 in scalings}
        pairs=sorted(orbit&eligible)
        require(not covered.intersection(pairs),'Repeated equation pairs')
        todo.difference_update(orbit);covered.update(pairs)
        n1=counts(a,b,p,tabs,1)
        stage=(f==2 or (nu*(p+1-n1)-2*(Q+1))%7==0)
        row={'representative':[a,b],'admissible_pairs':[list(x) for x in pairs],
             'orbit_size':len(orbit),'N1':n1,'N2':None,'rational_polynomial':None,
             'twisted_polynomial':None,'trace_stage_pass':stage,'residual_pass':False,
             'defect_roots':[]}
        if stage:
            n2=counts(a,b,p,tabs,2);number2+=1
            pq,pv=local_polynomial(p,n1,n2,f,nu)
            residual=all((x-y)%7==0 for x,y in zip(pv,target))
            roots=defect_roots(pv,Q) if residual else []
            row.update(N2=n2,rational_polynomial=pq,twisted_polynomial=pv,
                       residual_pass=residual,defect_roots=roots)
            good.update(roots)
        rows.append(row)
    require(covered==eligible,'Incomplete equation coverage')
    digest=hashlib.sha256()
    for a,b in sorted(eligible):digest.update(f'{a},{b}\n'.encode())
    return {'q':p,'f':f,'Q':Q,'nu':nu,'admissible_pairs':len(eligible),
      'pair_set_sha256':digest.hexdigest(),'degree_one_counts':len(rows),
      'degree_two_counts':number2,'residual_pairs':sum(len(r['admissible_pairs']) for r in rows if r['residual_pass']),
      'trace_defect_set':sorted(good),'rows':rows}

def main():
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--output',type=Path,required=True);a=ap.parse_args()
    out={'schema':'beal.block67.pointcounts.v1','arithmetic':'exact integers and finite fields',
         'curve':'z^2=x^6+10 B x^3+12 A x+5 B^2','coefficient_order':'ascending',
         'coefficient_field':'k=F7[w]/(w^2-5); encode a+b*w as a+7*b',
         'primes':[run_prime(q) for q in PRIMES],'status':'PASS_FINITE_COUNTS'}
    a.output.parent.mkdir(parents=True,exist_ok=True);a.output.write_text(json.dumps(out,indent=2,sort_keys=True)+'\n')
    print(json.dumps({'status':out['status'],'pairs':sum(r['admissible_pairs'] for r in out['primes']),
       'N1':sum(r['degree_one_counts'] for r in out['primes']),'N2':sum(r['degree_two_counts'] for r in out['primes'])}))
if __name__=='__main__':main()
