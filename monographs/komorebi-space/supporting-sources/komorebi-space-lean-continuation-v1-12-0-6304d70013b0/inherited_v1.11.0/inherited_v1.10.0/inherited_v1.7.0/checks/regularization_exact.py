#!/usr/bin/env python3
"""Exact regression of written extensions WR01--WR12.

Finite checks audit identities, implementations, enclosures, and counterclaims.
They do not prove weak compactness, infinite convergence, or the written Hilbert
results, and do not supply new Lean coverage. Independent oracles are a 2x2
adjugate formula and SymPy KKT systems in original ambient coordinates.
"""
from __future__ import annotations
from pathlib import Path
from fractions import Fraction as F
from itertools import product
from datetime import datetime, timezone
import importlib.util, json, hashlib
import sympy as sp
ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('budgeted_repair',ROOT/'examples/budgeted_repair.py')
b=importlib.util.module_from_spec(spec);spec.loader.exec_module(b)
count=0
cases={}
controls=[]

def check(value, label):
    global count
    count+=1
    if not value: raise AssertionError(label)

def category(name):cases[name]=cases.get(name,0)+1

def frac(x):return F(int(sp.numer(x)),int(sp.denom(x)))

def add(a,c):return [x+y for x,y in zip(a,c)]

def objective(t,r,a,alpha):return b.norm2(b.sub(r,b.mv(t,a)))+alpha*b.norm2(a)

def negative(label, false_claim):
    check(not false_claim,label)
    controls.append({'label':label,'status':'REJECTED'})

# All 2x2 matrices in {-1,0,1}, all such data, three positive parameters.
for entries in product([-1,0,1],repeat=4):
    t=[[F(entries[0]),F(entries[1])],[F(entries[2]),F(entries[3])]]
    for raw_r in product([-1,0,1],repeat=2):
        r=list(map(F,raw_r));solutions=[]
        for alpha in [F(1,4),F(1),F(4)]:
            out=b.regularize(t,r,alpha);a=out['correction'];v=out['fit_residual']
            x=alpha+t[0][0]**2+t[1][0]**2
            z=alpha+t[0][1]**2+t[1][1]**2
            y=t[0][0]*t[0][1]+t[1][0]*t[1][1]
            c=t[0][0]*r[0]+t[1][0]*r[1]
            d=t[0][1]*r[0]+t[1][1]*r[1]
            det=x*z-y*y
            check(det>0,'positive definite regularized matrix')
            check(a==[(z*c-y*d)/det,(x*d-y*c)/det],'independent 2x2 adjugate oracle')
            check(out['normal_residual']==[0,0],'normal equation')
            check(b.dot(r,v)-alpha*b.norm2(a)==b.norm2(v),'unnormalized supporting witness')
            for h in [[F(0),F(0)],[F(1),F(-1)],[F(1,2),F(2)],[-a[0],-a[1]]]:
                gap=objective(t,r,add(a,h),alpha)-out['objective']
                check(gap==b.norm2(b.mv(t,h))+alpha*b.norm2(h),'quadratic energy identity')
            e=[F(1,3),F(-1,4)]
            pert=b.regularize(t,add(r,e),alpha)
            h=b.sub(pert['correction'],a)
            check(4*alpha*b.norm2(h)<=b.norm2(e),'sharp squared noise upper bound')
            check(b.norm2(b.mv(t,h))<=b.norm2(e),'fitted data nonexpansion')
            solutions.append(out);category('unconstrained_2x2_systems')
        for first,second in zip(solutions,solutions[1:]):
            check(first['correction_norm_squared']>=second['correction_norm_squared'],'parameter norm monotonicity')
            check(first['residual_norm_squared']<=second['residual_norm_squared'],'parameter residual monotonicity')

# Protected ambient calculation, including redundant and fully protective rows.
prescriptions=[[],[[1,0,0]],[[1,-1,0]],[[1,1,1]],[[1,0,0],[2,0,0]],
               [[1,0,0],[0,1,0],[0,0,1]]]
for drow in product([-1,0,1],repeat=3):
    for p in prescriptions:
        for alpha in [F(1,3),F(1),F(3)]:
            f=[F(1),F(-2),F(1,2)]
            out=b.protected_regularize([drow],p,f,alpha)
            a=out['correction'];v=out['fit_residual'];k=out['kernel_dimension']
            check(out['protected_before']==out['protected_after'],'exact protected observable')
            check(all(x==0 for x in out['normal_coordinate_residual']),'restricted normal equation')
            check(out['true_candidate_residual']==v,'fit equals true residual for exact data')
            check(all(x==0 for x in b.mv(b.matrix(p,3),a)),'correction belongs to kernel')
            for coordinates in product([-1,1],repeat=k):
                h=b.mv(out['kernel_basis'],list(map(F,coordinates)))
                gap=objective(b.matrix([drow]),out['target_residual'],add(a,h),alpha)-out['objective']
                check(gap==b.norm2(b.mv(b.matrix([drow]),h))+alpha*b.norm2(h),'protected energy identity with Gram metric')
            # Independent full ambient KKT oracle when P has independent rows.
            if p!=[[1,0,0],[2,0,0]]:
                D=sp.Matrix([drow]);P=sp.Matrix(p) if p else sp.zeros(0,3)
                A=D.T*D+sp.Rational(alpha.numerator,alpha.denominator)*sp.eye(3)
                K=A.row_join(P.T).col_join(P.row_join(sp.zeros(P.rows,P.rows)))
                rhs=(D.T*sp.Matrix(out['target_residual'])).col_join(sp.zeros(P.rows,1))
                oracle=K.inv()*rhs
                check(a==[frac(x) for x in list(oracle)[:3]],'ambient KKT oracle independent of nullspace coordinates')
                category('ambient_KKT_oracles')
            category('protected_systems')

# Minimum-norm nested affine prefixes, independently computed by A^T(AA^T)^-1.
rows=sp.Matrix([[1,1,0],[0,1,1],[1,0,0]])
for rr in product([-2,-1,0,1,2],repeat=3):
    sols=[]
    for n in range(1,4):
        A=rows[:n,:];r=sp.Matrix(rr[:n]);a=A.T*(A*A.T).inv()*r
        sols.append([frac(x) for x in a])
    for n in range(3):
        for m in range(n,3):
            check(b.norm2(b.sub(sols[m],sols[n]))==b.norm2(sols[m])-b.norm2(sols[n]),'nested affine Pythagoras')
    category('nested_affine_problems')

# Robust budget profiles for scalar models have an independent closed form.
for t,r,M,dt,dr in product([F(0),F(1,2),F(2)],[F(-1),F(0),F(3,2)],
                          [F(0),F(1,2),F(2)],[F(-1,4),F(0),F(1,4)],[F(-1,5),F(1,5)]):
    profile=lambda s,y: max(F(0),abs(y)-M*abs(s))
    check(abs(profile(t,r)-profile(t+dt,r+dr))<=abs(dr)+abs(dt)*M,'robust budget bound')
    for z in [F(-1),F(0),F(1)]:
        check(profile(t,r)>= (r+dr)*z-M*abs((t+dt)*z)-abs(dr)-M*abs(dt),'robust dual lower bound')
    category('scalar_uncertainty_cases')

# Exact finite diagonal coordinates and independently bounded omitted windows.
for m in range(1,13):
    for K in [m,2*m,4*m,8*m]:
        enclosure=b.diagonal_enclosure(m,K)
        A,B=enclosure['energy_interval'][0],enclosure['residual_square_interval'][0]
        check(A>=F(m,4),'head lower bound on energy')
        check(A<=F(4*m,3),'finite partial energy below infinite upper bound')
        check(B<=F(2,m),'finite partial residual below infinite upper bound')
        end=3*K+1
        tailA=sum((F(m**4,(m*m+n*n)**2) for n in range(K+1,end)),F(0))
        tailB=sum((F(n*n,(m*m+n*n)**2) for n in range(K+1,end)),F(0))
        check(A+tailA<=enclosure['energy_interval'][1],'finite omitted window inside proved infinite enclosure')
        check(B+tailB<=enclosure['residual_square_interval'][1],'residual omitted window inside enclosure')
        for n in range(1,K+1):
            a=F(m*m,m*m+n*n);v=F(n,m*m+n*n);alpha=F(1,m*m)
            check(F(1,n)*v==alpha*a,'diagonal exact normal coordinate')
            check(F(1,n)-a/n==v,'diagonal true residual')
            attainable=F(m*m,n*(m*m+n*n))
            check(F(1,n)-attainable==v,'attainable bias equals escaping residual')
        category('diagonal_tail_windows')

# Verified finite noise-choice arithmetic (avoid irrational comparisons).
for k in range(1,31):
    # delta=1/k^3 gives m=k^2 exactly; theoretical cube-root rate becomes rational.
    delta=F(1,k**3);m=k*k
    check(delta*m/2<=F(1,k),'noise part below claimed delta^(1/3) coefficient')
    check(F(2,m)==2*F(1,k)**2,'bias-square choice')
    category('noise_parameter_cases')

# Named falsification controls distinguish nearby but false conclusions.
out=b.protected_regularize([[1,0]],[[1,-1]],[1,0],1)
negative('Dropping the nonorthogonal Gram metric leaves the same correction',out['correction']==[F(1,2),F(1,2)])
negative('Nested closed convex sets always satisfy the affine energy identity',F(2-1)**2==F(2)**2-F(1)**2)
negative('A weakly small coordinate sequence is pairwise norm Cauchy',b.norm2([F(1),F(-1)])<F(1))
negative('An unrestricted zero floor forces zero residual at budget zero',max(F(0),F(1)-F(0))==0)
negative('A vanishing weighted penalty bounds correction norms',F(8,4)<=F(4,3))
negative('Increasing correction budget can remove all model-error uncertainty',F(1,10)*10<=F(1,10))
noise=b.regularize([[1]],[1],1)['correction'][0]
negative('A universal noise coefficient of one third suffices at alpha one',noise<=F(1,3))
negative('Positive irreducible residual forces a nonzero correction',b.regularize([[0]],[1],1)['correction']!=[F(0)])
negative('The operator adjoint can ignore protection',b.protected_regularize([[1,1]],[[1,0]],[1,0],1)['correction'][0]!=0)

invalid=[lambda:b.regularize([[1]],[1],0),lambda:b.regularize([[1]],[1],-1),
         lambda:b.regularize([[1,2],[3]],[1,2],1),lambda:b.regularize([[1]],[1,2],1),
         lambda:b.protected_regularize([[1]],[[1,0]],[1],1),
         lambda:b.protected_regularize([[1]],[],[1],0.5),
         lambda:b.diagonal_enclosure(True,4),lambda:b.diagonal_enclosure(3,2),
         lambda:b.rational('1/0'),lambda:b.regularize([[1]],[True],1)]
for i,fn in enumerate(invalid,1):
    try:fn()
    except (ValueError,TypeError,ZeroDivisionError):pass
    else:raise AssertionError(f'Invalid input {i} accepted')
    check(True,f'invalid input {i} rejected');category('input_rejections')

baseline=json.loads((ROOT/'audit/regularization/baseline.json').read_text())
current={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest()
         for p in sorted((ROOT/'formal').rglob('*')) if p.is_file()}
check(current==baseline['formal_files'],'all formal files preserved unchanged')
result={'status':'PASS','executed_utc':datetime.now(timezone.utc).isoformat(),
        'assertions':count,'cases':cases,'false_claim_rejection_controls':controls,
        'formal_files_unchanged':len(current),'scope':'Exact finite arithmetic and independent oracles for written WR extensions. No new Lean run. No inference of infinite-dimensional results from finite tests.'}
(ROOT/'audit/regularization_exact.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps(result,indent=2))
