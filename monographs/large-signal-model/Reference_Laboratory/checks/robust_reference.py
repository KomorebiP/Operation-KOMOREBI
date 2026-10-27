"""Exact replay of robust three-coordinate curved-domain certificates.

Numerical geometry proposals are separate from acceptance. Acceptance uses exact
rational tensor-Bernstein coefficients on a complete subdivision of two rational
semicircle charts and the continuous observation interval. It never substitutes
a sampled positivity test for a polynomial certificate.
"""
from __future__ import annotations
from fractions import Fraction
from math import comb
from typing import Any
import re
import numpy as np
import sympy as sp

U, V = sp.symbols('u v', real=True)
SCHEMA = 'komorebi.robust-lorentz-bernstein.v1'


def rat(x: Any) -> sp.Rational:
    if isinstance(x, (int, sp.Integer, sp.Rational)) and not isinstance(x, bool):
        return sp.Rational(x)
    if not isinstance(x,str) or not re.fullmatch(r'[+-]?\d+(?:/[1-9]\d*)?',x):
        raise ValueError('Only exact integer or rational strings are accepted.')
    return sp.Rational(x)


def mat(x: Any) -> sp.Matrix:
    if not isinstance(x,list) or not x or not all(isinstance(r,list) for r in x):
        raise ValueError('Expected a rectangular matrix list.')
    return sp.Matrix([[rat(y) for y in row] for row in x])


def enc(m: sp.Matrix) -> list[list[str]]:
    return [[str(x) for x in row] for row in m.tolist()]


def poly_matrices(data: Any) -> sp.Matrix:
    if not isinstance(data,list) or not 1 <= len(data) <= 9:
        raise ValueError('Expected degree at most eight.')
    out=sp.zeros(3)
    for k,row in enumerate(data):
        c=mat(row)
        if c.shape!=(3,3): raise ValueError('Expected three-dimensional operators.')
        out+=c*U**k
    return out


def coeff_matrices(m: sp.Matrix) -> list[list[list[str]]]:
    n=max([0]+[int(sp.degree(x,U)) for x in m if x!=0])
    return [enc(m.applyfunc(lambda x:sp.expand(x).coeff(U,k))) for k in range(n+1)]


def base_integral(m: sp.Matrix) -> sp.Matrix:
    return m.applyfunc(lambda x:sp.integrate(x,(U,-1,1))/2)


def root_bernstein(p: sp.Expr) -> list[list[Fraction]]:
    """Exact tensor coefficients on [-1,1]^2, with axes (observation, chart)."""
    p=sp.Poly(sp.expand(p.subs({U:2*U-1,V:2*V-1}, simultaneous=True)),U,V,domain=sp.QQ)
    n=max(0,p.degree(U)); m=max(0,p.degree(V))
    if n>16 or m>8: raise ValueError('Certificate polynomial degree exceeds replay bound.')
    out=[[Fraction(0) for _ in range(m+1)] for _ in range(n+1)]
    for i in range(n+1):
        for j in range(m+1):
            value=sp.S(0)
            for k in range(i+1):
                for l in range(j+1):
                    value+=p.nth(k,l)*sp.Rational(comb(i,k),comb(n,k))*sp.Rational(comb(j,l),comb(m,l))
            out[i][j]=Fraction(int(value.p),int(value.q))
    return out


def half(values: list[Fraction]) -> tuple[list[Fraction],list[Fraction]]:
    layers=[values]
    while len(layers[-1])>1:
        r=layers[-1]; layers.append([(a+b)/2 for a,b in zip(r,r[1:])])
    return [r[0] for r in layers],[r[-1] for r in layers[::-1]]


def split_axis(a: list[list[Fraction]], axis: int):
    n=len(a);m=len(a[0]); lo=[[Fraction(0)]*m for _ in range(n)];hi=[[Fraction(0)]*m for _ in range(n)]
    if axis==0:
        for j in range(m):
            l,h=half([a[i][j] for i in range(n)])
            for i in range(n):lo[i][j]=l[i];hi[i][j]=h[i]
    else:
        for i in range(n):lo[i],hi[i]=half(a[i])
    return lo,hi


def quarters(a):
    l,h=split_axis(a,0);ll,lh=split_axis(l,1);hl,hh=split_axis(h,1)
    return [ll,lh,hl,hh]


def minimum(a): return min(x for row in a for x in row)


def certify_polynomial(p: sp.Expr,max_depth:int=8) -> list[dict]:
    if not 0<=max_depth<=12:raise ValueError('Subdivision depth out of supported range.')
    leaves=[]
    def walk(a,path):
        bound=minimum(a)
        if bound>=0:
            leaves.append({'path':path,'lower_bound':str(bound)})
            return
        # A negative corner is an actual counterexample, not merely a failed bound.
        if min(a[0][0],a[0][-1],a[-1][0],a[-1][-1])<0:
            raise ValueError('Polynomial is negative at a rational subdivision corner.')
        if len(path)>=max_depth:raise ValueError('Certificate withheld at subdivision limit.')
        for j,child in enumerate(quarters(a)):walk(child,path+str(j))
    walk(root_bernstein(p),'')
    return leaves


def replay_polynomial(p: sp.Expr,leaves: Any) -> tuple[int,int]:
    if not isinstance(leaves,list) or not 1<=len(leaves)<=100000:
        raise ValueError('Invalid finite subdivision witness.')
    paths={}
    for leaf in leaves:
        s=leaf.get('path')
        if not isinstance(s,str) or len(s)>12 or any(c not in '0123' for c in s) or s in paths:
            raise ValueError('Invalid or duplicate subdivision path.')
        paths[s]=rat(leaf.get('lower_bound'))
    used=set();coef_checks=0
    prefixes={s[:i] for s in paths for i in range(len(s)+1)}
    def walk(a,path):
        nonlocal coef_checks
        if path in paths:
            actual=minimum(a);claim=paths[path]
            if actual<0 or sp.Rational(actual.numerator,actual.denominator)!=claim:
                raise ValueError('Incorrect or negative Bernstein bound.')
            coef_checks+=sum(len(r) for r in a);used.add(path);return
        if path not in prefixes or len(path)>=12:raise ValueError('Subdivision does not cover the whole square.')
        for j,child in enumerate(quarters(a)):walk(child,path+str(j))
    walk(root_bernstein(p),'')
    if used!=set(paths):raise ValueError('Overlapping or unused subdivision leaves.')
    return len(used),coef_checks


def chart_polynomials(F: sp.Matrix,sign:int,kappa:sp.Rational):
    if sign not in (-1,1):raise ValueError('Invalid semicircle chart.')
    q=1+V**2
    z=sp.Matrix([q,sign*(1-V**2),sign*2*V])
    w=F*z
    f=sp.expand(w[0]-kappa*q)
    g=sp.expand(f*f-w[1]*w[1]-w[2]*w[2])
    return f,g


def propose_geometry(actions: dict[str,sp.Matrix], denominator:int=48) -> tuple[sp.Matrix,dict]:
    """Heuristic noisy ratio/least-squares proposal. No acceptance claims here.

    This routine never imports a predecessor metric or a generating model.
    It rationalizes a numerical center and metric factor. All proposed geometry
    is subsequently verified against the complete supplied operator family.
    """
    if len(actions)!=2 or denominator<1:raise ValueError('Proposal expects two actions.')
    keys=sorted(actions)
    A0=np.array(actions[keys[0]].subs(U,0),dtype=float)
    A1=np.array(actions[keys[1]].subs(U,0),dtype=float)
    ratio=np.linalg.solve(A0.T,A1.T).T
    A=ratio[1:,1:];b=ratio[1:,0]
    center=np.linalg.solve(np.eye(2)-A,b)
    basis=[np.array([[1.,0.],[0.,0.]]),np.array([[0.,1.],[1.,0.]]),np.array([[0.,0.],[0.,1.]])]
    M=np.column_stack([(A.T@h@A-h)[[0,0,1],[0,1,1]] for h in basis])
    M=np.vstack([M,[1.,0.,1.]])
    target=np.array([0.,0.,0.,1.])
    h,*_=np.linalg.lstsq(M,target,rcond=None)
    H0=np.array([[h[0],h[1]],[h[1],h[2]]])
    if np.linalg.eigvalsh(H0)[0]<=0:raise ValueError('No positive noisy metric proposal.')
    candidates=[]
    for name in keys:
        for anchor in [sp.Rational(-1),-sp.Rational(1,2),-sp.Rational(1,3),sp.Rational(0),sp.Rational(1,3),sp.Rational(1,2),sp.Rational(1)]:
            B=np.array(actions[name].subs(U,anchor),dtype=float)
            _,s,_=np.linalg.svd(B)
            if s[0]>0 and abs(B[0,0])>1e-7:
                x=B[1:,0]/B[0,0]
                scale=(x-center)@H0@(x-center)
                if scale>1e-8:candidates.append((s[1]/s[0],name,str(anchor),scale))
    if not candidates:raise ValueError('No scale proposal.')
    quality,anchor_name,anchor,scale=min(candidates)
    H=H0/scale
    L=np.linalg.cholesky(H).T
    rr=lambda x:sp.Rational(str(Fraction(float(x)).limit_denominator(denominator)))
    c=sp.Matrix([rr(v) for v in center]); R=sp.Matrix([[rr(v) for v in row] for row in L])
    if R.det()==0:raise ValueError('Rationalized factor is singular.')
    T=sp.eye(3);T[1:,0]=-R*c;T[1:,1:]=R
    diagnostics={'proposal_only':True,'denominator_limit':denominator,'ratio_mass_row_residual':float(np.linalg.norm(ratio[0]-[1,0,0])),
                 'least_squares_residual':float(np.linalg.norm(M@h-target)), 'metric_system_sigma_min':float(np.linalg.svd(M,compute_uv=False)[-1]),
                 'anchor_action':anchor_name,'anchor':anchor,'rank_one_proxy_ratio':float(quality),
                 'center':enc(c),'factor':enc(R),'metric':enc(R.T*R),'transform':enc(T)}
    return T,diagnostics


def make_certificate(actions: dict[str,sp.Matrix],initial:sp.Matrix,T:sp.Matrix,margin:sp.Rational,
                     mass_error:sp.Rational,spatial_error:sp.Rational,max_depth:int=8) -> dict:
    proofs={}
    for name,B in actions.items():
        F=(T*B*T.inv()).applyfunc(sp.expand)
        proofs[name]={}
        for sign in [1,-1]:
            f,g=chart_polynomials(F,sign,margin)
            proofs[name][str(sign)]={'orientation':certify_polynomial(f,max_depth),'cone_gap':certify_polynomial(g,max_depth)}
    doc={'schema':SCHEMA,'reference_measure':{'support':['-1','1'],'density_wrt_lebesgue':'1/2'},
         'transform_to_lorentz':enc(T),'initial':enc(initial),'mass':['1','0','0'],
         'margin':str(margin),'uncertainty':{'mass_output_bound':str(mass_error),'spatial_output_bound':str(spatial_error),
         'quantifier':'for every observation and every normalized state in the certified domain',
         'exact_integrated_mass_required':True,'statistical_coverage_claimed':False,
         'coefficient_box_radii_in_lorentz_coordinates':['1/4096','1/4096','1/4096']},
         'actions':{k:coeff_matrices(v) for k,v in actions.items()},'proofs':proofs}
    replay_certificate(doc)
    return doc


def replay_certificate(doc:dict) -> dict:
    if doc.get('schema')!=SCHEMA:raise ValueError('Unknown certificate schema.')
    if doc.get('reference_measure')!={'support':['-1','1'],'density_wrt_lebesgue':'1/2'}:raise ValueError('Wrong reference measure.')
    T=mat(doc['transform_to_lorentz']);z=mat(doc['initial'])
    if T.shape!=(3,3) or T.det()==0 or list(T[0,:])!=[1,0,0]:raise ValueError('Invalid mass-preserving coordinate transform.')
    if z.shape!=(3,1) or z[0]!=1:raise ValueError('Initial state has incorrect shape or mass.')
    tz=T*z
    if tz[0]<0 or tz[0]**2-tz[1]**2-tz[2]**2<0:raise ValueError('Initial state outside the proposed cone.')
    if doc.get('mass')!=['1','0','0']:raise ValueError('Invalid mass functional.')
    margin=rat(doc['margin']);unc=doc['uncertainty']
    dm=rat(unc['mass_output_bound']);ds=rat(unc['spatial_output_bound'])
    if min(margin,dm,ds)<0 or margin<dm+ds:raise ValueError('Insufficient robustness margin.')
    if unc.get('exact_integrated_mass_required') is not True or unc.get('statistical_coverage_claimed') is not False:raise ValueError('Unsupported uncertainty claim.')
    if unc.get('quantifier')!='for every observation and every normalized state in the certified domain':raise ValueError('Incorrect uncertainty quantifier.')
    radii=unc.get('coefficient_box_radii_in_lorentz_coordinates')
    if not isinstance(radii,list) or not 1<=len(radii)<=9:raise ValueError('Invalid coefficient uncertainty box.')
    radii=[rat(x) for x in radii]
    if min(radii)<0 or 3*sum(radii)>dm or 6*sum(radii)>ds:raise ValueError('Coefficient box exceeds its claimed output bounds.')
    acts=doc['actions'];proofs=doc['proofs'];leaves=coefs=0
    if not isinstance(acts,dict) or not acts or len(acts)>8 or set(acts)!=set(proofs):raise ValueError('Action/proof mismatch.')
    for name,data in acts.items():
        B=poly_matrices(data)
        if list(base_integral(B)[0,:])!=[1,0,0]:raise ValueError('Integrated mass identity failed.')
        F=(T*B*T.inv()).applyfunc(sp.expand)
        if set(proofs[name])!={'1','-1'}:raise ValueError('Both semicircle charts are required.')
        for sign in [1,-1]:
            f,g=chart_polynomials(F,sign,margin)
            branch=proofs[name][str(sign)]
            if set(branch)!={'orientation','cone_gap'}:raise ValueError('Incomplete positivity witness.')
            for p,label in [(f,'orientation'),(g,'cone_gap')]:
                n,k=replay_polynomial(p,branch[label]);leaves+=n;coefs+=k
    return {'passed':True,'actions':len(acts),'polynomial_witnesses':4*len(acts),'subdivision_leaves':leaves,
            'nonnegative_coefficients_recomputed':coefs,'margin':str(margin),'remaining_margin':str(margin-dm-ds),
            'validity':'all observation values and all finite horizons in the declared uncertainty family',
            'statistical_coverage':False}
