#!/usr/bin/env python3
"""Exact finite checks for the coefficient and determinant arguments.

Universal implications are proved in notes/, not inferred from these tests.
The quadratic finite-field coordinates a+b*r use r^2=5. Integral coefficient
coordinates a+b*phi instead use phi^2=phi+1. They are kept separate.
"""
from __future__ import annotations
import argparse
import itertools
import json
from math import isqrt
from pathlib import Path

def need(b: bool, message: str):
    if not b: raise AssertionError(message)

def prime(p: int) -> bool:
    return p>1 and all(p%d for d in range(2,isqrt(p)+1))

def fm(x,y,q):
    a,b=x; c,d=y
    return ((a*c+5*b*d)%q,(a*d+b*c)%q)

def fp(x,n,q):
    if n<0: raise ValueError('Nonnegative exponent required')
    z=(1,0)
    while n:
        if n&1: z=fm(z,x,q)
        x=fm(x,x,q);n//=2
    return z

def im(x,y):
    a,b=x;c,d=y
    return (a*c+b*d,a*d+b*c+b*d)

def add(x,y): return (x[0]+y[0],x[1]+y[1])
def sub(x,y): return (x[0]-y[0],x[1]-y[1])
def scale(x,c): return (c*x[0],c*x[1])
def norm(x):
    a,b=x
    return a*a+a*b-b*b

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args()
    q=13; exponent=(q*q-1)//7; inv2=pow(2,-1,q)
    symbols={name:fp(x,exponent,q) for name,x in {
        'phi':(inv2,inv2),'three':(3,0),'sqrt5':(0,1)}.items()}
    need(symbols['phi']!=(1,0),'Unit symbol must be nonzero')
    need(symbols['three']==symbols['sqrt5']==(1,0),'Rational/generator symbols')
    need(fp(symbols['phi'],7,q)==(1,0),'Unit symbol order seven')
    # Independent brute-force seventh-power image, with no character formula.
    seventh={fp((a,b),7,q) for a in range(q) for b in range(q) if (a,b)!=(0,0)}
    need(len(seventh)==24,'Seventh-power image size')
    need((inv2,inv2) not in seventh and (3,0) in seventh and (0,1) in seventh,
         'Independent Kummer membership test')
    inert=[]
    for p in (13,83,97,167,223):
        need(prime(p) and p%7==6 and pow(5,(p-1)//2,p)==p-1,'Inert prime regime')
        e=(p*p-1)//7
        vals={'three':fp((3,0),e,p),'sqrt5':fp((0,1),e,p)}
        need(all(z==(1,0) for z in vals.values()),'Inert rational-symbol lemma')
        inert.append({'q':p,'symbols':vals})
    qray=1504231
    need(prime(qray),'Historical ray prime is not prime')
    need((qray-1)%7==0 and (qray-1)%49!=0,'Historical h=1')
    ray=[]
    for root in (684240,819991):
        need(root*root%qray==5,'Historical sqrt5 root')
        phi=(1+root)*pow(2,-1,qray)%qray
        vals={'phi':pow(phi,(qray-1)//7,qray),'three':pow(3,(qray-1)//7,qray),
              'sqrt5':pow(root,(qray-1)//7,qray)}
        need(vals['phi']!=1 and vals['three']==vals['sqrt5']==1,'Ray support symbols')
        ray.append({'sqrt5_root':root,'symbols':vals})
    # Local functionals on the SAME global [phi],[3],[sqrt5] coordinates.
    # We anchor each local unit line to the image of the global generator 3.
    forms=[]
    for p in (29,43,71):
        roots=[r for r in range(p) if r*r%p==5]
        degree=1 if roots else 2
        e=(p**degree-1)//7
        if roots:
            place_values=[(r,pow((1+r)*pow(2,-1,p)%p,e,p),pow(r,e,p)) for r in roots]
        else:
            uv=fp((pow(2,-1,p),pow(2,-1,p)),e,p)
            rv=fp((0,1),e,p)
            need(uv[1]==rv[1]==0,'Expected rational seventh symbols at 43')
            place_values=[(None,uv[0],rv[0])]
        z=pow(3,e,p)
        need(z!=1 and pow(z,7,p)==1,'Global generator 3 must span local unit line')
        for root,u,v in place_values:
            j=next(i for i in range(7) if pow(z,i,p)==u)
            k=next(i for i in range(7) if pow(z,i,p)==v)
            forms.append({'q':p,'sqrt5_root':root,'symbol_of_three':z,
                          'phi_symbol':u,'sqrt5_symbol':v,
                          'linear_form_coefficients_phi_three_sqrt5':[j,1,k]})
    need([r['linear_form_coefficients_phi_three_sqrt5'] for r in forms]
         ==[[4,1,5],[3,1,5],[0,1,2],[2,1,0],[5,1,0]],'Compatible local forms')
    ratios=[(a,b) for a in range(7) for b in range(7) if (a,b)!=(0,0)]
    for r in ratios:
        zero29=((r[0]+5)%7,r[1])==(0,0)
        zero43=((r[0]+2)%7,r[1])==(0,0)
        zero71=r==(0,0)
        need(not (zero29 and zero43) and not zero71,'Depth-one simultaneous-support obstruction')
    candidate_counts={'before_good13':49*48,'after_good13':len(ratios),
                      'after_good13_and_good29_and_good43':len([r for r in ratios if r not in ((2,0),(5,0))])}
    samples=[(0,0),(1,0),(0,1),(-1,2),(2,-1)]
    matrix_checks=0
    for n in range(2,6):
        for A,D,b,c in itertools.product(samples,repeat=4):
            a=add((1,0),scale(A,7));d=add((1,0),scale(D,7));lower=scale(c,7**n)
            detI=sub(im(sub((1,0),a),sub((1,0),d)),im(b,lower))
            need(all(z%49==0 for z in detI),'Depth determinant divisibility')
            need(norm(detI)%2401==0,'Norm divisibility')
            matrix_checks+=1
    # n=1 cannot be substituted into the depth>=2 theorem.
    depth1_norm=norm((-7,0));depth2_norm=norm((-49,0))
    need(depth1_norm==49 and depth1_norm%2401!=0 and depth2_norm==2401,'Depth boundary controls')
    # Repeated eigenvalues alone do not force a scalar matrix.
    jordan=[[-13,1],[0,-13]]
    need(jordan[0][1]!=0 and jordan[0][0]+jordan[1][1]==-26
         and jordan[0][0]*jordan[1][1]==169,'Jordan counterexample')
    # A seventh-power equation does not have full weighted-orbit invariance.
    wrong_orbit_example={}
    q=29;sevenths={pow(c,7,q) for c in range(1,q)}
    found=False
    for A,B,u in itertools.product(range(q),range(q),range(1,q)):
        old=(A**3+B**5)%q
        new=((A*pow(u,5,q))**3+(B*pow(u,3,q))**5)%q
        if old in sevenths and new!=0 and new not in sevenths:
            wrong_orbit_example={'q':q,'A':A,'B':B,'u':u,'old_rhs':old,'new_rhs':new}
            found=True;break
    need(found,'Weighted-orbit negative control')
    # Primitive bad-reduction pairs survive, so good-prime sieves are not
    # contradictions for arbitrary C. Each pair has A=-1,B=1,C=0 mod q.
    bad=[{'q':p,'A':p-1,'B':1,'C':0} for p in (13,29,43,71)]
    need(all((r['A']**3+r['B']**5-r['C']**7)%r['q']==0 for r in bad),'Bad-lane control')
    result={'status':'PASS','good13':{'field':'F_13[r]/(r^2-5)','exponent':exponent,
              'symbols':symbols,'independent_seventh_power_image_size':len(seventh)},
            'compatible_local_forms':forms,'projective_kummer_candidate_counts':candidate_counts,
            'inert_zero_symbols':inert,'historical_ray_prime':{'q':qray,'places':ray},
            'exact_integral_matrix_checks':matrix_checks,
            'negative_controls':{'n1_norm':depth1_norm,'n2_sharp_norm':depth2_norm,
                'nonscalar_jordan_matrix':jordan,'orbit_filter_counterexample':wrong_orbit_example,
                'surviving_primitive_bad_residues':bad},
            'analytic_29_bound':{'square_root_comparison':{'q':29,'six_squared':36},'seven_fourth':2401}}
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({'status':'PASS','matrix_cases':matrix_checks,'good13_phi_symbol':symbols['phi']}))

if __name__=='__main__':main()
