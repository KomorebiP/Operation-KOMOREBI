#!/usr/bin/env python3
"""Exact finite checks for the fixed-seven period comparison.

Base residue rings use omega^2=5. Coefficient-field elements use the same
arithmetic routines but are distinct mathematical objects; never substitute
one radical for the other in the proof. No external packages are needed.
"""
from __future__ import annotations
import argparse, collections, hashlib, itertools, json
from pathlib import Path

def mul(x, y, m):
    return ((x[0]*y[0]+5*x[1]*y[1])%m,(x[0]*y[1]+x[1]*y[0])%m)
def power(x, n, m):
    if n < 0:
        x=inverse(x,m);n=-n
    out=(1,0)
    while n:
        if n&1:out=mul(out,x,m)
        x=mul(x,x,m);n//=2
    return out
def inverse(x,m):
    d=pow((x[0]*x[0]-5*x[1]*x[1])%m,-1,m)
    return (x[0]*d%m,-x[1]*d%m)
def add(x,y,m):return ((x[0]+y[0])%m,(x[1]+y[1])%m)
def scale(a,x,m):return (a*x[0]%m,a*x[1]%m)
def flog(x):
    """Unit class modulo seventh powers, via (x^48-1)/7 mod7."""
    y=power(x,48,49)
    assert (y[0]-1)%7==0 and y[1]%7==0
    return (((y[0]-1)//7)%7,(y[1]//7)%7)
def mm(a,b):
    return tuple(sum(a[2*i+k]*b[2*k+j] for k in range(2))%7 for i in range(2) for j in range(2))
def normcode(v):return v[0]+7*v[1]
def digest(v):return hashlib.sha256(json.dumps(v,separators=(',',':')).encode()).hexdigest()
def root5_newton(a,c,N):
    target=c**7-a**3
    b=next(b for b in range(1,7) if (b**5-target)%7==0)
    mod=7
    while mod<7**N:
        mod=min(mod*mod,7**N)
        b=(b-(pow(b,5,mod)-target)*pow(5*pow(b,4,mod),-1,mod))%mod
    assert (pow(b,5,7**N)-target)%7**N==0
    return b

def calculate(root:Path):
    units=[(a,b) for a in range(49) for b in range(49) if (a%7,b%7)!=(0,0)]
    logs=collections.Counter(flog(x) for x in units)
    image={power(x,7,49) for x in units}
    kernel={x for x in units if flog(x)==(0,0)}
    assert image==kernel and len(kernel)==48 and set(logs.values())=={48}
    phi=(25,25);omega=(0,1)
    named={name:list(flog(x)) for name,x in [('phi',phi),('3',(3,0)),('sqrt5',omega),('5',(5,0))]}
    assert named=={'phi':[0,5],'3':[6,0],'sqrt5':[3,0],'5':[6,0]}
    u1=[(1+7*a,7*b) for a in range(49) for b in range(49)]
    u2={((1+49*a)%343,49*b%343) for a in range(7) for b in range(7)}
    assert {power(x,7,343) for x in u1}==u2
    assert (8,0) not in image
    R=(1,5,5,6);fiveI=(5,0,0,5)
    mats=list(itertools.product(range(7),repeat=4))
    roots=[s for s in mats if mm(s,s)==fiveI]
    central=[s for s in mats if mm(s,R)==mm(R,s)]
    matched=[s for s in roots if s in central]
    assert len(roots)==42 and len(central)==49
    assert set(matched)=={R,tuple(-x%7 for x in R)}
    # Exact period constants mod49; variable C0 enters to the seventh power.
    den=scale(675,omega,49)
    ka=mul(scale(-1,power(phi,2,49),49),inverse(den,49),49)
    kb=mul(power(phi,-2,49),inverse(den,49),49)
    kab=scale(-1,power(phi,-4,49),49)
    rationals=[a for a in range(1,49) if a%7]
    fermat={str(a):flog((a,0))[0] for a in rationals}
    period_checks=0
    for a,c0 in itertools.product(rationals,repeat=2):
        unit=mul(power((c0,0),7,49),power((a,0),-3,49),49)
        got=[flog(mul(unit,ka,49)),flog(kab),flog(mul(unit,kb,49))]
        Z=(4*fermat[str(a)]+2)%7;X=(0,5)
        expected=[add((Z,0),scale(2,X,7),7),scale(-4,X,7),add((Z,0),scale(-2,X,7),7)]
        assert got==expected
        period_checks+=1
    # Compare actual E-linear classes up to the single permissible nonzero gauge.
    coefficients=[(a,b) for a in range(7) for b in range(7) if (a,b)!=(0,0)]
    accepted=[];gauge_tests=0
    for v,r,a in itertools.product(range(1,7),range(1,7),rationals):
        q=fermat[str(a)]; witnesses=[]
        for sign in (1,-1):
            for c in coefficients:
                gauge_tests+=1
                if mul(c,(0,2*sign%7),7)==(0,v) and mul(c,((3*q+5)%7,0),7)==((r+4)%7,0):
                    witnesses.append([sign,normcode(c)])
        criterion=((2*r+1)**2-v*v*(3*q+5)**2)%7==0
        assert bool(witnesses)==criterion
        if criterion:accepted.append([v,r,a,witnesses])
    assert len(accepted)==396
    source=json.loads((root/'work71/inputs/B70_refinement70.json').read_text())
    patterns=[];seen=set()
    for i,s in enumerate(source['survivors']):
        uc,r,_=s['alpha'];v=uc//7
        allowed=[a for a in rationals if ((2*r+1)**2-v*v*(3*fermat[str(a)]+5)**2)%7==0]
        assert len(allowed)==12
        patterns.append({'predecessor_index':i,'alpha':s['alpha'],'A_mod49':allowed,'fermat_values':sorted({fermat[str(a)] for a in allowed})})
        seen.update(allowed)
    assert len(patterns)==8 and len(seen)==24
    local_roots=[]
    for a in sorted(seen):
        b=root5_newton(a,7,18)
        local_roots.append({'A':a,'C':7,'B_mod_7pow18':b,'B_mod7':b%7,'modulus':7**18,'fermat':fermat[str(a)]})
    return {
      'schema':'beal.block71.fixed_seven.v1',
      'status':'PASS_FINITE_ASSERTIONS_NOT_GLOBAL_REALIZATION',
      'unit_domain':2304,'unit_kernel_size':48,'unit_class_count':49,
      'unit_class_fiber_size':48,'named_unit_classes':named,
      'principal_unit_inputs_mod343':len(u1),'seventh_power_image_mod343':len(u2),
      'root_matrices_tested':len(mats),'root5_matrices':len(roots),'centralizer_size':len(central),'compatible_root_matrices':[list(x) for x in matched],
      'period_unit_pairs':period_checks,'fermat_by_A':fermat,
      'coefficient_A_triples':36*42,'gauge_tests':gauge_tests,'accepted_coefficient_A_triples':len(accepted),'accepted_sha256':digest(accepted),
      'per_A_counts':{str(a):sum(x[2]==a for x in accepted) for a in rationals},
      'bounded_patterns':patterns,'bounded_pattern_A_pairs':sum(len(x['A_mod49']) for x in patterns),
      'eliminated_predecessor_patterns':0,'local_root_certificates':local_roots,
      'negative_controls':{'arbitrary_principal_unit_8_is_seventh_power':False,'unrestricted_R_squared_implies_actual_R':False,
       'all_eight_patterns_eliminated':False,'full_local_J7_rational_at7':False},
      'limits':['Analytic period-to-family comparison is a written proof.','RM action is inherited; no global lattice descent asserted.','B roots are 7-adic, not asserted integers.','No bounded tuple is eliminated by this test.']
    }

def main():
    p=argparse.ArgumentParser();p.add_argument('--root',type=Path,default=Path(__file__).resolve().parents[2]);p.add_argument('--output',type=Path,required=True);a=p.parse_args()
    result=calculate(a.root);a.output.parent.mkdir(parents=True,exist_ok=True)
    a.output.write_text(json.dumps(result,sort_keys=True,indent=2)+'\n');print('PASS',result['accepted_coefficient_A_triples'],'allowed coefficient/A triples')
if __name__=='__main__':main()
