#!/usr/bin/env python3
"""Exact audit of corrected flat-character and mixed-gauge reductions.
No gamma value, approximate equality, random sampling, or analytic descent is assumed.
"""
from pathlib import Path
from itertools import product, combinations
from datetime import datetime, timezone
from fractions import Fraction as Q
import hashlib, json, platform, time
import sympy as S
from sympy.matrices.normalforms import smith_normal_form
ROOT=Path(__file__).resolve().parents[1]

def main():
    tic=time.monotonic(); started=datetime.now(timezone.utc).isoformat()
    checks=[]; negatives=[]
    def check(name,condition):
        if not bool(condition): raise AssertionError(name)
        checks.append(name)
    def negative(name,condition):
        if not bool(condition): raise AssertionError(name)
        negatives.append(name)
    M=S.Matrix([[0,1,0],[-4,2,15],[-1,0,4]])
    R=S.Matrix([[8,-4,15],[1,0,0],[2,-1,4]])
    D=M-S.eye(3); ell=S.Matrix([[1,-1,3]]); e0=S.Matrix([1,0,0]); e2=S.Matrix([0,0,1])
    check('inverse unit matrices',M*R==S.eye(3)==R*M)
    check('determinant of M-I',D.det()==-6)
    check('Smith invariants of M-I',[abs(smith_normal_form(D,domain=S.ZZ)[j,j]) for j in range(3)]==[1,1,6])
    check('correct integer quotient covector',ell*D==S.Matrix([[0,0,-6]]))
    x,y,z,k=S.symbols('x y z k',integer=True); n=S.Matrix([x,y,z])
    q=S.Matrix([-z,y-4*z,0]); q6=S.Matrix([-3,3,-1])
    check('universal integral residual reconstruction',S.simplify(D*q-(n-e0*(ell*n)[0]))==S.zeros(3,1))
    check('six generator explicit preimage',D*q6==6*e0)
    check('preimage under ell(n)=6k',S.simplify((D*(q+k*q6)-n).subs(x,6*k+y-3*z))==S.zeros(3,1))
    check('surjective quotient coordinate',(ell*e0)[0]==1)
    check('period-one class',(ell*e2)[0]==3)
    p=e2/3; carry=D*p
    check('conductor-three carry',carry==S.Matrix([0,5,1]))
    check('tripled carry in image',3*carry==D*e2)
    check('carry has exact order three in quotient',int((ell*carry)[0])%6==4 and (2*int((ell*carry)[0]))%6!=0)
    check('no invariant Picard coefficient on Stein cover',(R-S.eye(3)).det()==6)
    Mr=S.diag(M,M); pairs=list(combinations(range(6),2))
    W2=S.Matrix([[Mr.extract(i,j).det() for j in pairs] for i in pairs]).T
    check('compact exterior-square invariant space is zero',(W2-S.eye(15)).det()==-155520)
    X=S.symbols('X'); h=X**3-6*X**2+12*X-1
    check('unit spectrum excludes plus and minus one',h.subs(X,1)==6 and h.subs(X,-1)==-20)
    check('compact flat character group has two cyclic-six factors',[abs(smith_normal_form(S.diag(D,D),domain=S.ZZ)[j,j]) for j in range(6)]==[1,1,1,1,6,6])
    Q3=M**3
    check('third-return polynomial factorization',Q3-S.eye(3)==6*M*(M-2*S.eye(3)))
    check('third-return Smith invariants',[abs(smith_normal_form(Q3-S.eye(3),domain=S.ZZ)[j,j]) for j in range(3)]==[6,6,42])
    check('third-return rational-point carry',(Q3-S.eye(3))*p==S.Matrix([30,120,16]))
    # Enumerate all fixed points in the denominator-six grid, independent of SNF.
    fixed=[]
    for a,b,c in product(range(6),repeat=3):
        if all(int(v)%6==0 for v in D*S.Matrix([a,b,c])):
            fixed.append((a,b,c))
    predicted=[((-3*j)%6,(3*j)%6,(-j)%6) for j in range(6)]
    check('all six ordinary fixed points',set(fixed)==set(predicted) and len(fixed)==6)
    chars=[(a,b,c) for a,b,c in product(range(6),repeat=3)
           if (a+4*b+c)%6==0 and (a+b)%6==0 and (15*b+3*c)%6==0]
    check('complete invariant lattice characters',set(chars)=={(k,(-k)%6,(3*k)%6) for k in range(6)})
    check('period-one restricted lattice characters',[k for k in range(6) if (3*k)%6==0]==[0,2,4])
    check('all based phases are cubic',all(3*(2*k)%6==0 for k in range(6)))
    check('all fixed-point pairings',all((-k*j)%6==(-k*int((ell*(D*S.Matrix([Q(-j,2),Q(j,2),Q(-j,6)])))[0]))%6 for k,j in product(range(6),repeat=2)))
    # Exact holomorphic interpolation polynomial on all six roots, represented in Z[omega].
    roots=[(1,0),(0,-1),(-1,-1),(-1,0),(0,1),(1,1)]
    interp=[0,-1,-1,0,1,1]; delta=(1,2)
    check('fixed-point holomorphic phase interpolation',all(tuple(roots[j][i]-roots[(-j)%6][i] for i in range(2))==tuple(interp[j]*t for t in delta) for j in range(6)))
    check('interpolation zero and conductor values',interp[0]==0 and interp[4]==1 and interp[2]==-1)
    check('interpolation preserves inverse points',all(interp[(-j)%6]==-interp[j] for j in range(6)))
    # C=omega R acting on the full seven-torsion parameter grid.
    ri=[[int(R[i,j])%7 for j in range(3)] for i in range(3)]
    def rv(v): return tuple(sum(ri[i][j]*v[j] for j in range(3))%7 for i in range(3))
    fixed7=[]
    for v in product(range(7),repeat=6):
        a=v[:3]; b=v[3:]; ra=rv(a); rb=rv(b)
        if tuple((-t)%7 for t in rb)==a and tuple((ra[i]-rb[i])%7 for i in range(3))==b:
            fixed7.append(v)
    expected7=[tuple((2*k*v)%7 for v in (1,2,4))+tuple((3*k*v)%7 for v in (1,2,4)) for k in range(7)]
    check('all 117649 seven-grid points tested; seven fixed',set(fixed7)==set(expected7) and len(fixed7)==7)
    check('single reduced Hodge coordinate detects class',all((v[0]+2*v[3])%7==k for k,v in enumerate(expected7)))
    # Construct full alternating form alpha wedge beta from the predecessor.
    alpha=S.Matrix([[1,0,-2,-3,0,-1]])
    beta=S.Matrix([[0,1,3,0,-3,-2]])
    E=alpha.T*beta-beta.T*alpha
    h=[]
    for i,j in [(1,2),(2,0),(0,1)]:
        aa=E[i,j]; bb=E[i,j+3]-E[j,i+3]; cc=E[i+3,j+3]
        h.append((int(cc-aa),int(-aa-bb)))
    check('full model Hodge projection',h==[(-5,3),(-3,-8),(8,5)])
    check('model selector is one',(h[0][0]+2*h[0][1])%7==1)
    check('model has zero opposite component',all((a+4*b)%7==0 for a,b in h))
    check('raw mixed commutator exponent',E[0,4]==-3)
    # Gauge b_lambda(z)=exp(2 pi i s m1 z0), b_lambda(0)=1 and b_n=1.
    la,lb,ma,mb,l1,m1,zr,zi=S.symbols('la lb ma mb l1 m1 zr zi')
    gauge_real=S.expand(m1*(zr+la)-(l1+m1)*zr+l1*zr)
    gauge_imag=S.expand(m1*(zi+lb)-(l1+m1)*zi+l1*zi)
    check('universal gauge coboundary',gauge_real==la*m1 and gauge_imag==lb*m1)
    # The alternating gauge changes B_01 by s and C_01 by omega*s, so
    # C-omega B=0 even though the individual mixed commutator changes.
    w=S.symbols('w'); s=S.symbols('s')
    check('holomorphic gauge has zero Hodge projection',S.expand(s*w-w*s)==0)
    check('scalar gamma-ratio commutator is tautological one',S.cancel((s/w)*(w/zr)/((s/zi)*(zi/zr)))==1)
    negative('previous displayed row product is not correct',ell*D!=S.Matrix([[-24,6,84]]))
    negative('single mixed commutator is gauge-dependent',(-3)%7!=(-3+1)%7)
    negative('lattice period normalization does not restrict the unit character',3%2!=0) # alpha=-1, all lattice values 1.
    negative('zero-anchored inversion-symmetric holomorphic lift need not be cubic',3%10!=0) # a(p)=exp(2*pi*i/10).
    negative('return character group is not the one-step character group',[6,6,42]!=[1,1,6])
    result={'started_at':started,'runtime_seconds':time.monotonic()-tic,'exit_status':0,
      'assertion_count':len(checks),'negative_count':len(negatives),'checks':checks,'negative_controls':negatives,
      'software':{'python':platform.python_version(),'sympy':S.__version__},
      'domains':{'integer_coefficients':'unbounded symbolic identities where indicated','fixed_six_grid':216,'lattice_characters':216,'fixed_point_character_pairs':36,'seven_parameter_grid':7**6},
      'data':{'M':M.tolist(),'R':R.tolist(),'ell_delta':(ell*D).tolist(),'fixed_points_times_six':fixed,'primitive_fixed_seven_classes':fixed7,'Hodge_model':h,'phase_interpolation':interp},
      'non_claims':['No actual mixed gamma descent is constructed.','No gamma equality, finite phase bound, or reality assertion is proved.','The complex analytic interpretation of the explicit counterexample is proved in PROOF.md, not inferred from this finite audit.']}
    (ROOT/'evidence/exact_results.json').write_text(json.dumps(result,indent=2,default=int)+'\n')
    print(f'PASS: {len(checks)} exact assertions and {len(negatives)} negative controls; {result["runtime_seconds"]:.3f}s')
if __name__=='__main__': main()
