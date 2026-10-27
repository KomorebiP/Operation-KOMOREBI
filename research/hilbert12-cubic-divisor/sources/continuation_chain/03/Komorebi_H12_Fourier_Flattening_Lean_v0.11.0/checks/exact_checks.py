#!/usr/bin/env python3
"""Exact certificates for finite Fourier-orbit antidifferences.

No gamma coefficient, target special value, or unverified periodic point is input.
The analytic all-orbit solvability theorem is proved separately in PROOF.md.
"""
from __future__ import annotations
from fractions import Fraction as Q
from pathlib import Path
from itertools import product
from datetime import datetime, timezone
import json, time, platform, hashlib
import sympy as sp
ROOT=Path(__file__).resolve().parents[1]
M=sp.Matrix([[0,1,0],[-4,2,15],[-1,0,4]])
A=M.T; D=M-sp.eye(3)
V=tuple[int,int,int]
Poly=dict[V,Q]
checks=[]; negatives=[]
def verify(name:str, result:bool, *,negative:bool=False)->None:
    if not bool(result): raise AssertionError(name)
    (negatives if negative else checks).append(name)
def vec(v)->V:return tuple(map(int,v))
def mv(B,v:V)->V:return vec(B*sp.Matrix(v))
def clean(p:Poly)->Poly:return {k:Q(v) for k,v in p.items() if v}
def add(*polys:Poly)->Poly:
    out={}
    for p in polys:
        for k,v in p.items():out[k]=out.get(k,Q(0))+v
    return clean(out)
def neg(p:Poly)->Poly:return {k:-v for k,v in p.items()}
def pullback(p:Poly)->Poly:
    out={}
    for k,v in p.items():out[mv(A,k)]=out.get(mv(A,k),Q(0))+v
    return clean(out)
def coboundary(p:Poly)->Poly:return add(p,neg(pullback(p)))
def orbit(k:V,j:int)->V:return mv(A**j,k)
def block_certificate(seed:V, coeff:dict[int,Q])->dict:
    """Checkable decomposition for one specified, finitely supported orbit.
    h=(g-g∘M)+charge*χ_(A^lo seed). Produces an exact residual even when
    the block has nonzero charge. Does not assert distinct input seeds are
    in distinct orbits, or use a truncated search to decide that issue.
    """
    if seed==(0,0,0):raise ValueError('Nonconstant frequency required')
    coeff={int(j):Q(c) for j,c in coeff.items() if c}
    if not coeff:return {'h':{},'g':{},'residual':{},'charge':Q(0)}
    lo,hi=min(coeff),max(coeff); total=sum(coeff.values(),Q(0))
    adjusted=coeff.copy();adjusted[lo]=adjusted.get(lo,Q(0))-total
    g={};acc=Q(0)
    for j in range(lo,hi+1):
        acc+=adjusted.get(j,Q(0))
        if acc:g[orbit(seed,j)]=acc
    assert acc==0
    h={orbit(seed,j):c for j,c in coeff.items()}
    rem=clean({orbit(seed,lo):total})
    assert add(coboundary(g),rem)==h
    return {'h':h,'g':g,'residual':rem,'charge':total}
def encode(p:Poly):return [{'frequency':k,'coefficient':str(c)} for k,c in sorted(p.items())]

def main():
    start=datetime.now(timezone.utc).isoformat();tic=time.monotonic()
    verify('unimodular original and dual',M.det()==1 and A.det()==1)
    verify('dual inverse exactly integral',A.inv()==sp.Matrix([[8,1,2],[-4,0,-1],[15,0,4]]))
    x=sp.symbols('x'); poly=x**3-6*x**2+12*x-1
    verify('exact characteristic polynomial',A.charpoly(x).as_expr()==poly)
    verify('unit polynomial is shifted pure cubic',sp.expand(poly-((x-2)**3+7))==0)
    verify('eigenvalues avoid 1 and -1',poly.subs(x,1)==6 and poly.subs(x,-1)==-20)
    verify('dual recurrence matrix',A**3-6*A**2+12*A-sp.eye(3)==sp.zeros(3))
    verify('conductor character preserved',(A[2,:]-sp.Matrix([[0,0,1]]))==sp.Matrix([[0,15,3]]))
    inv_num=-6*D.inv()
    verify('integral flat extension numerator',inv_num==sp.Matrix([[3,-3,15],[-3,-3,15],[1,-1,3]]))
    verify('extension solves row equation',inv_num*D==-6*sp.eye(3))
    k=(0,0,1)
    chain=[orbit(k,j) for j in range(-2,4)]
    verify('actual dual orbit chain',chain==[(23,-12,46),(2,-1,4),(0,0,1),(-1,0,4),(-4,-1,16),(-12,-6,49)])
    blocks=[]
    for name,seed,c in [
        ('elementary positive',k,{0:Q(1),1:Q(-1)}),
        ('four tap original',k,{0:Q(1),1:Q(-6),2:Q(12),3:Q(-1)}),
        ('four tap repaired',k,{0:Q(-5),1:Q(-6),2:Q(12),3:Q(-1)}),
        ('negative index rational',(0,0,-1),{-3:Q(2,3),0:Q(-5,7),4:Q(1,21)}),
        ('zero conductor orbit',(0,1,0),{-2:Q(2),0:Q(5),3:Q(-7)})]:
        r=block_certificate(seed,c)
        verify('exact Laurent certificate: '+name,add(coboundary(r['g']),r['residual'])==r['h'])
        blocks.append({'name':name,'seed':seed,'h':encode(r['h']),'g':encode(r['g']),
                       'residual':encode(r['residual']),'charge':str(r['charge'])})
    verify('old recurrence stencil has nonzero Fourier orbit charge',blocks[1]['charge']=='6',negative=True)
    verify('repaired recurrence stencil has zero charge',blocks[2]['charge']=='0')
    verify('repaired primitive is -5,-11,1',block_certificate(k,{0:-5,1:-6,2:12,3:-1})['g']==
        {k:Q(-5),orbit(k,1):Q(-11),orbit(k,2):Q(1)})
    # Exact regression on finite chains. Universal argument: partial-sum identity.
    cases=0
    for length in range(1,6):
        for cs in product(range(-2,3),repeat=length):
            r=block_certificate(k,{j:Q(c) for j,c in enumerate(cs)})
            assert add(coboundary(r['g']),r['residual'])==r['h']
            assert r['charge']==sum(cs)
            cases+=1
    verify('all finite chain regressions',cases==3905)
    # Spectral weighted evaluation at p3 computed in Q[omega]/(omega^2+omega+1).
    w=sp.symbols('w')
    def at_p(p):
        return sp.rem(sum(sp.Rational(c.numerator,c.denominator)*w**(k[2]%3)
                           for k,c in p.items()),w*w+w+1,w)
    g=add({k:Q(2),orbit(k,2):Q(-3)}, {(1,0,0):Q(5,7)})
    h=coboundary(g)
    verify('boundary vanishes at fixed conductor',sp.expand(at_p(h))==0)
    verify('boundary vanishes at zero',sum(h.values(),Q(0))==0)
    # A normalized inversion-symmetric negative control has independent +/- orbits.
    hbad={k:Q(1),(0,0,-1):Q(-1)}
    verify('zero mean does not imply solvability',sum(hbad.values())==0 and at_p(hbad)!=0,negative=True)
    # Rational-coefficient instances of the conjugate-reflection operation.
    def star(p:Poly)->Poly:return {tuple(-x for x in k):c for k,c in p.items()}
    hs={k:Q(1),(0,0,-1):Q(1)}
    verify('real orbit residues need not vanish',star(hs)==hs and len(hs)==2)
    verify('conjugate reflection commutes with coboundary',star(coboundary(g))==coboundary(star(g)))
    hmix=add(hs,coboundary(g))
    verify('antisymmetric logarithm has explicit primitive',
           add(hmix,neg(star(hmix)))==coboundary(add(g,neg(star(g)))))
    verify('conjugate residue pairing has real conductor value',
           sp.expand(at_p(hs)-sum(hs.values()))==-3)
    aa,bb,ss=sp.symbols('aa bb ss',real=True)
    pair=(-sp.Rational(3,2)+sp.I*ss/2)*(aa+sp.I*bb)+(-sp.Rational(3,2)-sp.I*ss/2)*(aa-sp.I*bb)
    verify('general conjugate-pair real-part formula',sp.expand(pair)==-3*aa-ss*bb)
    # Cubic residue constant along every finite checked orbit, including negative powers.
    verify('tested signed orbit residues',all(orbit(k,j)[2]%3==1 for j in range(-15,16)))
    # Construct holomorphic multipliers invisible on all points periodic up to N.
    # If D_j v is integral, adjugates imply Q_N v integral.
    dets=[int((M**j-sp.eye(3)).det()) for j in range(1,7)]
    periodic=[]
    for N in range(1,7):
        QN=int(sp.ilcm(*[abs(d) for d in dets[:N]])) if N>1 else abs(dets[0])
        mats=[QN*(M**j-sp.eye(3)).inv() for j in range(1,N+1)]
        assert all(all(x.q==1 for x in C) for C in mats)
        assert all(C*(M**j-sp.eye(3))==QN*sp.eye(3) for j,C in enumerate(mats,1))
        periodic.append({'N':N,'Q_N':QN,'determinants':dets[:N]})
    verify('all periods through six exact denominator certificate',len(periodic)==6)
    verify('finite periodic probes do not force zero frequency charges',periodic[2]['Q_N']>0,negative=True)
    # Distinguish orbital primitive from wrong orientation or a missing endpoint.
    correct=block_certificate(k,{0:1,1:-1})
    verify('reversed primitive fails',coboundary(neg(correct['g']))!=correct['h'],negative=True)
    bad_end=block_certificate(k,{0:1,1:-6,2:12,3:-1})
    verify('discarded residual fails',coboundary(bad_end['g'])!=bad_end['h'],negative=True)
    (ROOT/'evidence/orbit_certificates.json').write_text(json.dumps(blocks,indent=2)+'\n')
    (ROOT/'evidence/periodic_probe_certificates.json').write_text(json.dumps(periodic,indent=2)+'\n')
    rec={'started_at':start,'runtime_seconds':time.monotonic()-tic,'exit_status':0,
         'assertion_count':len(checks),'negative_control_count':len(negatives),
         'checks':checks,'negative_controls':negatives,'finite_chain_cases':cases,
         'software':{'python':platform.python_version(),'sympy':sp.__version__},
         'bounds':{'chain_coefficients':[-2,2],'chain_lengths':[1,5],
                   'signed_orbit_iterates':[-15,15],'periodic_denominator_certificates_N':[1,6]},
         'scope':'Exact finite Laurent/carry certificates. No gamma multiplier was constructed; no special-value comparison performed.',
         'script_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest()}
    (ROOT/'evidence/exact_results.json').write_text(json.dumps(rec,indent=2)+'\n')
    print(json.dumps(rec,indent=2))
if __name__=='__main__':main()
