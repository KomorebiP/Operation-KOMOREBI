#!/usr/bin/env python3
"""Exact finite checks for B72. Not a verifier of the inherited analytic geometry."""
from __future__ import annotations
import argparse, hashlib, json
from itertools import product
from functools import lru_cache
from pathlib import Path

P=7

def vp(n: int) -> int:
    if n==0: return 10**9
    n=abs(n);v=0
    while n%7==0: n//=7;v+=1
    return v

class Ring:
    """(Z/m)[omega]/(omega^2-5), represented in the base-field omega basis."""
    def __init__(self,m:int): self.m=m
    def add(self,x,y): return ((x[0]+y[0])%self.m,(x[1]+y[1])%self.m)
    def sub(self,x,y): return ((x[0]-y[0])%self.m,(x[1]-y[1])%self.m)
    def scale(self,x,a): return (x[0]*a%self.m,x[1]*a%self.m)
    def mul(self,x,y): return ((x[0]*y[0]+5*x[1]*y[1])%self.m,(x[0]*y[1]+x[1]*y[0])%self.m)
    def inv(self,x):
        d=(x[0]*x[0]-5*x[1]*x[1])%self.m
        if d%7==0: raise ValueError('nonunit inversion')
        t=pow(d,-1,self.m);return (x[0]*t%self.m,-x[1]*t%self.m)
    def power(self,x,n):
        if n<0: return self.power(self.inv(x),-n)
        a=(1,0)
        while n:
            if n&1:a=self.mul(a,x)
            x=self.mul(x,x);n//=2
        return a

@lru_cache(maxsize=None)
def unit_log(z:tuple[int,int],j:int):
    """log(z^48)/7 mod 7^j, with a rigorously bounded exact series."""
    m=7**j;big=Ring(7*m);small=Ring(m)
    y=big.power((z[0]%(7*m),z[1]%(7*m)),48)
    assert (y[0]-1)%7==0 and y[1]%7==0
    t=(((y[0]-1)//7)%m,(y[1]//7)%m)
    acc=(0,0);power=(1,0)
    # For k>=2j+8, k-1-v7(k)>=6k/7-1>j. The omitted tail is zero.
    for k in range(1,2*j+8):
        power=small.mul(power,t);v=vp(k);e=k-1-v
        if e<j:
            coeff=(1 if k%2 else -1)*7**e*pow(k//7**v,-1,m)
            acc=small.add(acc,small.scale(power,coeff))
    return acc

@lru_cache(maxsize=None)
def coords(z,j):
    m=7**j;big=Ring(7*m);phi=(pow(2,-1,7*m),pow(2,-1,7*m))
    lp=unit_log(phi,j);lh=unit_log((3,0),j);l=unit_log(z,j)
    assert lp[0]==0 and lh[1]==0 and lp[1]%7 and lh[0]%7
    return (l[1]*pow(lp[1],-1,m)%m,l[0]*pow(lh[0],-1,m)%m)

@lru_cache(maxsize=None)
def ell(a,j):
    assert a%7
    x,h=coords((a,0),j);assert x==0;return h

def mm(a,b,m):
    return ((a[0]*b[0]+a[1]*b[2])%m,(a[0]*b[1]+a[1]*b[3])%m,
            (a[2]*b[0]+a[3]*b[2])%m,(a[2]*b[1]+a[3]*b[3])%m)

def digest(items):
    return hashlib.sha256(json.dumps(items,separators=(',',':')).encode()).hexdigest()

def main_result():
    tables=[];coordinate_rows=[];period_rows=[]
    for j in range(1,7):
        m=7**j;r=Ring(7*m);om=(0,1);phi=r.scale((1,1),pow(2,-1,7*m))
        h=unit_log((3,0),j);x=unit_log(phi,j);d=coords(om,j)[1]
        tables.append({'j':j,'omega_H_coordinate':d,'log3_48_over7':list(h),'logphi_48_over7':list(x)})
        for a,b in product(range(14),repeat=2):
            if a%7==0 and b%7==0:continue
            cr=coords((a,b),j);coordinate_rows.append([j,a,b,*cr])
        for a,c0 in product([a for a in range(1,15) if a%7],[1,2,3,6,8,9]):
            theta=r.mul(r.power((c0,0),7),r.inv(r.mul((27*a**3%(7*m),0),r.power(om,5))))
            expected=(7*ell(c0,j)-3*ell(a,j)-3-5*d)%m
            assert coords(theta,j)==(0,expected)
            aa=r.scale(r.mul(theta,r.power(phi,2)),-1)
            bb=r.mul(theta,r.power(phi,-2))
            ab=r.scale(r.power(phi,-4),-1)
            actual=[coords(aa,j),coords(bb,j),coords(ab,j)]
            assert actual==[(2%m,expected),((-2)%m,expected),((-4)%m,0)]
            for c in [1,2,7,49]:
                period_rows.append([j,a,c0,c,expected,(7*c)%m])
    qtable=[]
    for a in range(1,343):
        if a%7==0:continue
        q=((a**6-1)//7)%49;formula=(20*q+28*q*q)%49
        assert ell(a,2)==formula
        qtable.append([a,q,formula])
    assert tables[1]['omega_H_coordinate']==39
    lambdas=[]
    for a,c0 in product([x for x in range(1,343) if x%7],[x for x in range(1,49) if x%7]):
        qa=((a**6-1)//7)%49;qc=((c0**6-1)//7)%7
        lam=(47+38*qa+14*qa*qa-7*qc)%49
        assert lam==(7*ell(c0,2)-3*ell(a,2)+47)%49
        lambdas.append([a,c0,lam])
    R=(1,-2,-2,-1);roots={};centralizer_count={}
    for j in (1,2,3):
        m=7**j;found=[]
        for a,b in product(range(m),repeat=2):
            s=((a+b)%m,-2*b%m,-2*b%m,(a-b)%m)
            assert mm(R,s,m)==mm(s,R,m)
            if (s[0]+s[3])%m==0 and mm(s,s,m)==(5%m,0,0,5%m):found.append(list(s))
        roots[str(j)]=sorted(found);centralizer_count[str(j)]=m*m
        assert len(found)==2
    # A lift of an allowed mod7 square root need NOT intertwine periods mod49.
    S=(-13,82,-2,13)
    assert mm(S,S,49)==(5,0,0,5)
    assert all((S[i]-R[i])%7==0 for i in range(4))
    assert mm(S,R,49)!=mm(R,S,49)
    precision_controls=[]
    for c in (1,2):
        d=7*c
        good=unit_log((1+7**d,0),d-1);bad=unit_log((1+7**d,0),d)
        assert good==(0,0) and bad!=(0,0)
        precision_controls.append({'c':c,'d':d,'last_certain_j':d-1,'first_uncontrolled_log':list(bad)})
    # Complete residual-compatible local lifts at j=2: A mod343 and C0 mod49.
    accepted=[];bounded=[]
    for v,r0,a,c0 in product(range(1,7),range(1,7),[x for x in range(1,343) if x%7],[x for x in range(1,49) if x%7]):
        qa=((a**6-1)//7)%7
        signs=[s for s in (-1,1) if (2*r0+1-s*v*(3*qa+5))%7==0]
        if not signs: continue
        lam=lambdas[([x for x in range(1,343) if x%7].index(a))*42+([x for x in range(1,49) if x%7].index(c0))][2]
        eps=signs[0];scale=v*pow(2*eps,-1,49)%49
        U=(0,v);V=(scale*lam%49,0);W=(scale*7%49,0)
        assert V[0]%7==(r0+4)%7 and W[0]%7==0 and W[0]!=0
        accepted.append([v,r0,a,c0,eps,scale,*U,*V,*W])
    # The actual eight patterns: two copies at each signed value +-3 and +-1.
    patterns=[('A+',3),('A-',4),('B+',3),('B-',4),('C+',1),('C-',6),('D+',1),('D-',6)]
    acset={(x[0],x[1],x[2],x[3]) for x in accepted}
    for label,v in patterns:
        for a,c0 in product([x for x in range(1,343) if x%7],[x for x in range(1,49) if x%7]):
            if (v,6,a,c0) in acset:bounded.append([label,a,c0])
    assert len(accepted)==116424 and len(bounded)==28224
    # Actual-lift valuation identity. The gauge is a coefficient-ring unit.
    valchecks=0
    for j,c,a,b in product(range(1,7),range(1,50),range(1,7),range(7)):
        m=7**j;coeff=Ring(m);gauge=(a,7*b%m);W=coeff.scale(gauge,7*c)
        value=min(vp(W[0]),vp(W[1]),j)
        assert value==min(j,1+vp(c));valchecks+=1
    # Formal nonlifting control: no primitive lift (1,7t) is fixed by [[1,0],[7,1]].
    nonlifts=[t for t in range(7) if (7*(t+1)-7*t)%49!=0]
    assert len(nonlifts)==7
    roots_local=[]
    for a,c0 in sorted({(a,c0) for _,a,c0 in bounded}):
        target=(7*c0)**7-a**3
        b=pow(target%7,5,7);prec=1
        while prec<18:
            newprec=min(2*prec,18);mod=7**newprec
            b=(b-(pow(b,5,mod)-target)*pow(5*pow(b,4,mod),-1,mod))%mod
            prec=newprec
        assert (pow(b,5,7**18)-target)%(7**18)==0
        roots_local.append([a,c0,b])
    assert len(roots_local)==7056
    qbounds={}
    for label,v in patterns:
        ar=sorted({a%49 for l,a,c in bounded if l==label});qbounds[label]=ar
    return {'schema':'beal.block72.higher_seven.v1','coordinate_tables':tables,
      'unit_coordinate_cases':len(coordinate_rows),'unit_coordinate_sha256':digest(coordinate_rows),
      'period_cases':len(period_rows),'period_sha256':digest(period_rows),
      'rational_A_mod343_cases':len(qtable),'rational_A_table_sha256':digest(qtable),
      'lambda_pair_cases':len(lambdas),'lambda_pairs_sha256':digest(lambdas),
      'centralizer_candidates':centralizer_count,'compatible_root_matrices':roots,
      'precision_controls':precision_controls,
      'higher_lift_input_count':36*294*42,'accepted_local_lifts':len(accepted),
      'accepted_local_lifts_sha256':digest(accepted),'bounded_augmented_lifts':len(bounded),
      'bounded_lifts_sha256':digest(bounded),'bounded_A_mod49':qbounds,
      'valuation_gauge_cases':valchecks,
      'local_root_certificates':len(roots_local),'local_root_sha256':digest(roots_local),
      'root_precision':18,'sample_local_roots':roots_local[:4],
      'negative_controls':{'all_eight_patterns_eliminated':False,'principal_unit_at_first_uncontrolled_level_is_power':False,
        'mod7_RM_lift_alone_suffices':False,'uniformizer_term_may_be_dropped_mod49_for_c1':False,
        'global_depth1_line_lifts_mod49':False,'local_J7_is_rational_at7':False},
      'global_realization_claimed':False,'new_frobenius_point_counts':0}

def main():
    p=argparse.ArgumentParser();p.add_argument('--output',type=Path,required=True);a=p.parse_args()
    data=main_result();a.output.parent.mkdir(parents=True,exist_ok=True)
    a.output.write_text(json.dumps(data,sort_keys=True,indent=2)+'\n')
    print('PASS primary B72',data['accepted_local_lifts'],data['bounded_augmented_lifts'])
if __name__=='__main__':main()
