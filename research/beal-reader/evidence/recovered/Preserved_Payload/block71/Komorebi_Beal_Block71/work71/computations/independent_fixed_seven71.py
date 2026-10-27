#!/usr/bin/env python3
"""Separate checker: phi-basis rings, sixth Fermat quotient, determinants,
and single-digit Hensel lifting. Imports no primary arithmetic."""
from __future__ import annotations
import argparse, collections, hashlib, itertools, json
from pathlib import Path

def times(x,y,m):
    a,b=x;c,d=y
    return ((a*c+b*d)%m,(a*d+b*c+b*d)%m)
def repeated(x,e,m):
    ans=(1,0)
    for _ in range(e):ans=times(ans,x,m)
    return ans
def reciprocal(x,m):
    a,b=x;inv=pow((a*a+a*b-b*b)%m,-1,m)
    return ((a+b)*inv%m,-b*inv%m)
def cls(x):
    u=repeated(x,48,49)
    assert u[0]%7==1 and u[1]%7==0
    return (((u[0]-1)//7)%7,(u[1]//7)%7)
def to_omega(x):return [(x[0]+4*x[1])%7,4*x[1]%7]
def fq(a):return ((pow(a,6,49)-1)//7)%7

def matprod(x,y):
    a,b,c,d=x;e,f,g,h=y
    return ((a*e+b*g)%7,(a*f+b*h)%7,(c*e+d*g)%7,(c*f+d*h)%7)
def require(x,msg):
    if not x:raise AssertionError(msg)
def root_digit(a,N):
    rhs=7**7-a**3
    b=next(t for t in range(1,7) if (t**5-rhs)%7==0)
    modulus=7
    for j in range(1,N):
        nextmod=modulus*7
        valid=[b+modulus*t for t in range(7) if (pow(b+modulus*t,5,nextmod)-rhs)%nextmod==0]
        require(len(valid)==1,'Nonunique Hensel digit')
        b=valid[0];modulus=nextmod
    return b

def run(root,certificate):
    data=json.loads(certificate.read_text())
    us=[(a,b) for a in range(49) for b in range(49) if (a%7,b%7)!=(0,0)]
    fibers=collections.Counter(cls(x) for x in us)
    zeros={x for x in us if cls(x)==(0,0)}
    im={repeated(x,7,49) for x in us}
    require(zeros==im and len(zeros)==48 and len(fibers)==49 and set(fibers.values())=={48},'Bad unit quotient')
    named={n:to_omega(cls(x)) for n,x in [('phi',(0,1)),('3',(3,0)),('sqrt5',(-1,2)),('5',(5,0))]}
    require(named==data['named_unit_classes'],'Changed named unit class')
    require((8,0) not in im,'False principal-unit shortcut')
    u1=[(1+7*a,7*b) for a in range(49) for b in range(49)]
    require({repeated(x,7,343) for x in u1}=={(1+49*a,49*b) for a in range(7) for b in range(7)},'Bad deep-unit power test')
    R=(1,5,5,6)
    roots=[];cent=[]
    for S in itertools.product(range(7),repeat=4):
        if matprod(S,S)==(5,0,0,5):roots.append(S)
        if matprod(S,R)==matprod(R,S):cent.append(S)
    exact=[list(s) for s in roots if s in cent]
    require(exact==data['compatible_root_matrices'] and len(roots)==42 and len(cent)==49,'Changed RM centralizer')
    Sbad=(2,1,1,5)
    require(matprod(Sbad,Sbad)==(5,0,0,5) and matprod(Sbad,R)!=matprod(R,Sbad),'Bad centralizer negative control')
    rats=[a for a in range(1,49) if a%7]
    fermat={str(a):fq(a) for a in rats}
    require(fermat==data['fermat_by_A'],'Changed Fermat quotient')
    # Kappa constants are evaluated via their rational phi-basis formulas.
    d=pow(3375,-1,49)
    ka=(-d%49,-3*d%49);kb=(-4*d%49,3*d%49)
    kab=times((-1,0),repeated(reciprocal((0,1),49),4,49),49)
    ptests=0
    for a,c in itertools.product(rats,repeat=2):
        fac=(pow(c,7,49)*pow(pow(a,3,49),-1,49)%49,0)
        vals=[to_omega(cls(times(fac,ka,49))),to_omega(cls(kab)),to_omega(cls(times(fac,kb,49)))]
        z=(4*fq(a)+2)%7
        require(vals==[[z,3],[0,1],[z,4]],'Changed smoothing-unit class')
        ptests+=1
    # Zero determinant of the two H^1 coordinate vectors, then recover gauge.
    allowed=[];dtests=0
    for v,r,a in itertools.product(range(1,7),range(1,7),rats):
        u=(-v%7,2*v%7) # coefficient vw in phi basis
        h=((r+4)%7,0);z=((3*fq(a)+5)%7,0)
        witnesses=[]
        for sign in (1,-1):
            dtests+=1
            coeff=(-2*sign%7,4*sign%7)
            p=times(u,z,7);q=times(h,coeff,7)
            if p==q:
                c=times(u,reciprocal(coeff,7),7)
                require(c[1]==0,'Gauge not prime-field')
                witnesses.append([sign,c[0]])
        if witnesses:allowed.append([v,r,a,witnesses])
    digest=hashlib.sha256(json.dumps(allowed,separators=(',',':')).encode()).hexdigest()
    require(len(allowed)==396 and digest==data['accepted_sha256'],'Changed complete coefficient/A classification')
    require(data['accepted_coefficient_A_triples']==396,'Changed accepted count')
    require(data['eliminated_predecessor_patterns']==0,'False bounded exclusion')
    perA={str(a):sum(x[2]==a for x in allowed) for a in rats}
    require(perA==data['per_A_counts'],'Changed per-A classification')
    predecessor=json.loads((root/'work71/inputs/B70_refinement70.json').read_text())
    patterns=[];pool=set()
    for i,s in enumerate(predecessor['survivors']):
        v=s['alpha'][0]//7;r=s['alpha'][1]
        aa=[x[2] for x in allowed if x[0]==v and x[1]==r]
        patterns.append({'predecessor_index':i,'alpha':s['alpha'],'A_mod49':aa,'fermat_values':sorted({fq(a) for a in aa})});pool.update(aa)
    require(patterns==data['bounded_patterns'],'Changed surviving-pattern residue sets')
    rows=[]
    for a in sorted(pool):
        b=root_digit(a,18)
        rows.append({'A':a,'C':7,'B_mod_7pow18':b,'B_mod7':b%7,'modulus':7**18,'fermat':fq(a)})
    require(rows==data['local_root_certificates'],'Changed 7-adic root certificate')
    require(data['negative_controls']['full_local_J7_rational_at7'] is False,'False full torsion claim')
    return {'schema':'beal.block71.independent.v1','status':'PASS_SEPARATE_FINITE_IMPLEMENTATION',
       'unit_elements_checked':len(us),'principal_unit_inputs_checked':len(u1),'matrix_elements_checked':7**4,
       'period_unit_pairs':ptests,'coefficient_determinants':dtests,'accepted_coefficient_A_triples':len(allowed),
       'accepted_sha256':digest,'bounded_patterns':len(patterns),'bounded_pattern_A_pairs':sum(len(x['A_mod49']) for x in patterns),
       'eliminated_predecessor_patterns':0,'independent_digit_roots':len(rows),'hensel_digits_per_root':17,
       'radical_conventions':'Base phi^2=phi+1, coefficient phi^2=phi+1 in a distinct copy; outputs expressed in their respective omega/w bases.',
       'limits':['No primary arithmetic imported.','Analytic and representation implications not certified by finite tests.']}

def main():
    p=argparse.ArgumentParser();p.add_argument('--root',type=Path,default=Path(__file__).resolve().parents[2]);p.add_argument('--certificate',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args()
    result=run(a.root,a.certificate);a.output.write_text(json.dumps(result,sort_keys=True,indent=2)+'\n');print('PASS_SEPARATE_FINITE_IMPLEMENTATION')
if __name__=='__main__':main()
