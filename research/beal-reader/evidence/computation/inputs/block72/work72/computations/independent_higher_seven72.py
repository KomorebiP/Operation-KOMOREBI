#!/usr/bin/env python3
"""Separate B72 checks: phi basis, multiplicative digit lifting, powering limits.
No primary arithmetic module is imported. The input certificate is read only after
all corresponding data have been computed independently.
"""
from __future__ import annotations
import argparse, hashlib, json
from itertools import product
from functools import lru_cache
from pathlib import Path

class PhiRing:
    def __init__(self,m): self.m=m
    def times(self,a,b):
        m=self.m
        return ((a[0]*b[0]+a[1]*b[1])%m,(a[0]*b[1]+a[1]*b[0]+a[1]*b[1])%m)
    def scalar(self,a,b): return (a[0]*b%self.m,a[1]*b%self.m)
    def inverse(self,a):
        d=(a[0]*a[0]+a[0]*a[1]-a[1]*a[1])%self.m
        if d%7==0: raise ValueError('not a unit')
        inv=pow(d,-1,self.m);return ((a[0]+a[1])*inv%self.m,-a[1]*inv%self.m)
    def pow(self,a,n):
        if n<0:return self.pow(self.inverse(a),-n)
        digits=[]
        while n: digits.append(n%3);n//=3
        result=(1,0)
        for d in reversed(digits):
            result=self.times(self.times(result,result),result)
            if d:result=self.times(result,a)
            if d==2:result=self.times(result,a)
        return result

def valuation(n):
    if not n:return 10**9
    v=0
    while n%7==0:n//=7;v+=1
    return v

def phi_input(a,b,m):return ((a-b)%m,2*b%m)
def omega_output(a,m):return [(a[0]+a[1]*pow(2,-1,m))%m,a[1]*pow(2,-1,m)%m]

def power_limit(z,j):
    # log(z^48)/7 from (z^(48*7^j)-1)/7^(j+1) mod7^j.
    m=7**j;R=PhiRing(7**(2*j+1));v=R.pow(z,48*7**j);div=7**(j+1)
    assert (v[0]-1)%div==0 and v[1]%div==0
    return ((v[0]-1)//div%m,v[1]//div%m)

class DigitCoordinates:
    def __init__(self,j):
        self.j=j;self.m=7**j;self.R=PhiRing(7**(j+1))
        self.gx=self.R.pow((0,1),48);self.gy=self.R.pow((3,0),48)
        # Full two-by-two digit map is inverted over F7, not over the coefficient field.
        ax=((self.gx[0]-1)//7)%7;bx=(self.gx[1]//7)%7
        ay=((self.gy[0]-1)//7)%7;by=(self.gy[1]//7)%7
        det=(ax*by-bx*ay)%7;self.invdet=pow(det,-1,7)
        self.map=(ax,bx,ay,by)
        self.powers=[]
        for s in range(j):
            g1=self.R.pow(self.gx,7**s);g2=self.R.pow(self.gy,7**s)
            self.powers.append(([self.R.pow(g1,k) for k in range(7)],[self.R.pow(g2,k) for k in range(7)]))
    @lru_cache(maxsize=None)
    def __call__(self,z):
        target=self.R.pow(z,48);current=(1,0);xx=yy=0
        ax,bx,ay,by=self.map
        for s in range(self.j):
            residual=self.R.times(target,self.R.inverse(current));div=7**(s+1)
            assert (residual[0]-1)%div==0 and residual[1]%div==0
            a=((residual[0]-1)//div)%7;b=(residual[1]//div)%7
            dx=(by*a-ay*b)*self.invdet%7;dy=(-bx*a+ax*b)*self.invdet%7
            xx+=dx*7**s;yy+=dy*7**s
            current=self.R.times(current,self.R.times(self.powers[s][0][dx],self.powers[s][1][dy]))
        assert current==target
        return (xx,yy)

def matmul(a,b,m):
    out=[]
    for i in range(2):
        for j in range(2):out.append(sum(a[2*i+k]*b[2*k+j] for k in range(2))%m)
    return tuple(out)
def hash_data(x):return hashlib.sha256(json.dumps(x,separators=(',',':')).encode()).hexdigest()

def calculate():
    tables=[];coordinate_rows=[];period_rows=[]
    for j in range(1,7):
        m=7**j;get=DigitCoordinates(j);R=get.R
        omega=(-1,2);d=get(omega)[1]
        tables.append({'j':j,'omega_H_coordinate':d,'log3_48_over7':omega_output(power_limit((3,0),j),m),
                       'logphi_48_over7':omega_output(power_limit((0,1),j),m)})
        for a,b in product(range(14),repeat=2):
            if a%7==0 and b%7==0:continue
            coordinate_rows.append([j,a,b,*get(phi_input(a,b,R.m))])
        ka=R.scalar((-1,-3),pow(3375,-1,R.m));kb=R.scalar((-4,3),pow(3375,-1,R.m))
        ab=R.scalar(R.pow((0,1),-4),-1)
        for a,c0 in product([a for a in range(1,15) if a%7],[1,2,3,6,8,9]):
            eps=R.times(R.pow((c0,0),7),R.pow((a,0),-3))
            aa=get(R.times(eps,ka));bb=get(R.times(eps,kb));off=get(ab)
            lam=(7*get((c0,0))[1]-3*get((a,0))[1]-3-5*d)%m
            assert aa==(2%m,lam) and bb==((-2)%m,lam) and off==((-4)%m,0)
            for c in (1,2,7,49):period_rows.append([j,a,c0,c,lam,7*c%m])
    get=DigitCoordinates(2)
    AA=[x for x in range(1,343) if x%7];CC=[x for x in range(1,49) if x%7]
    logs={a:get((a,0))[1] for a in AA}
    qtable=[]
    for a in AA:
        q=(pow(a,6,343)-1)//7
        assert logs[a]==(20*q+28*q*q)%49
        qtable.append([a,q,logs[a]])
    lambdas=[];lt={}
    for a,c0 in product(AA,CC):
        lam=(7*logs[c0]-3*logs[a]-3-5*39)%49;lt[a,c0]=lam
        q=(pow(a,6,343)-1)//7;qc=(pow(c0,6,49)-1)//7
        assert lam==(47+38*q+14*q*q-7*qc)%49
        lambdas.append([a,c0,lam])
    roots={};centralizer_count={};R0=(1,-2,-2,-1)
    for j in (1,2,3):
        m=7**j;found=[]
        # Solve commutation entrywise: c=b, d=a+b; enumerate this independently.
        for a,b in product(range(m),repeat=2):
            s=(a,b,b,(a+b)%m)
            assert matmul(s,R0,m)==matmul(R0,s,m)
            if (2*a+b)%m==0 and matmul(s,s,m)==(5%m,0,0,5%m):found.append(list(s))
        roots[str(j)]=sorted(found);centralizer_count[str(j)]=m*m
        assert len(found)==2
    full49=[]
    for a,b,c in product(range(49),repeat=3):
        s=(a,b,c,-a%49)
        if (a*a+b*c)%49==5 and matmul(s,R0,49)==matmul(R0,s,49):full49.append(list(s))
    assert sorted(full49)==roots['2']
    S=(-13,82,-2,13)
    assert matmul(S,S,49)==(5,0,0,5) and matmul(S,R0,49)!=matmul(R0,S,49)
    pc=[]
    for c in (1,2):
        d=7*c
        assert power_limit((1+7**d,0),d-1)==(0,0)
        bad=omega_output(power_limit((1+7**d,0),d),7**d)
        assert bad!=[0,0]
        pc.append({'c':c,'d':d,'last_certain_j':d-1,'first_uncontrolled_log':bad})
    accepted=[]
    for v,r,a,c0 in product(range(1,7),range(1,7),AA,CC):
        lam=lt[a,c0]
        # Independent residual proportionality determinant, not the squared test.
        epss=[e for e in (-1,1) if (2*e*(r+4)-v*lam)%7==0]
        if not epss:continue
        e=epss[0];scale=v*pow(2*e,-1,49)%49
        U=(0,v);V=(scale*lam%49,0);W=(scale*7%49,0)
        assert U[1]%7==v and V[0]%7==(r+4)%7 and W[0]%7==0 and W[0]!=0
        accepted.append([v,r,a,c0,e,scale,*U,*V,*W])
    aset={(r[0],r[1],r[2],r[3]) for r in accepted}
    patterns=[('A+',3),('A-',4),('B+',3),('B-',4),('C+',1),('C-',6),('D+',1),('D-',6)]
    bounded=[[label,a,c0] for label,v in patterns for a in AA for c0 in CC if (v,6,a,c0) in aset]
    qbounds={label:sorted({a%49 for lab,a,c0 in bounded if lab==label}) for label,v in patterns}
    valcount=0
    for j,c,a,b in product(range(1,7),range(1,50),range(1,7),range(7)):
        m=7**j
        # Coefficient-ring output is kept in omega coordinates, independently of the base ring.
        v0=(7*c*a)%m;v1=(49*c*b)%m
        assert min(valuation(v0),valuation(v1),j)==min(j,1+valuation(c));valcount+=1
    assert all((7*(t+1))%49!=(7*t)%49 for t in range(7))
    rootrows=[]
    for a,c0 in sorted({(a,c0) for _,a,c0 in bounded}):
        target=(7*c0)**7-a**3;b=next(t for t in range(1,7) if (t**5-target)%7==0)
        mod=7
        for level in range(1,18):
            err=((b**5-target)//mod)%7
            delta=-err*pow(5*b**4,-1,7)%7
            b+=delta*mod;mod*=7
            assert (b**5-target)%mod==0
        rootrows.append([a,c0,b])
    assert len(rootrows)==7056
    summary={'schema':'beal.block72.higher_seven.v1','coordinate_tables':tables,
      'unit_coordinate_cases':len(coordinate_rows),'unit_coordinate_sha256':hash_data(coordinate_rows),
      'period_cases':len(period_rows),'period_sha256':hash_data(period_rows),
      'rational_A_mod343_cases':len(qtable),'rational_A_table_sha256':hash_data(qtable),
      'lambda_pair_cases':len(lambdas),'lambda_pairs_sha256':hash_data(lambdas),
      'centralizer_candidates':centralizer_count,'compatible_root_matrices':roots,
      'precision_controls':pc,'higher_lift_input_count':36*294*42,'accepted_local_lifts':len(accepted),
      'accepted_local_lifts_sha256':hash_data(accepted),'bounded_augmented_lifts':len(bounded),
      'bounded_lifts_sha256':hash_data(bounded),'bounded_A_mod49':qbounds,
      'valuation_gauge_cases':valcount,
      'local_root_certificates':len(rootrows),'local_root_sha256':hash_data(rootrows),
      'root_precision':18,'sample_local_roots':rootrows[:4],
      'negative_controls':{'all_eight_patterns_eliminated':False,'principal_unit_at_first_uncontrolled_level_is_power':False,
        'mod7_RM_lift_alone_suffices':False,'uniformizer_term_may_be_dropped_mod49_for_c1':False,
        'global_depth1_line_lifts_mod49':False,'local_J7_is_rational_at7':False},
      'global_realization_claimed':False,'new_frobenius_point_counts':0}
    return summary,{'trace_zero_matrices_mod49':49**3,'uses_primary_arithmetic':False,
                    'method':'phi basis; multiplicative digit coordinates; p-power limit; entrywise centralizers'}

def main():
    p=argparse.ArgumentParser();p.add_argument('--certificate',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args()
    mine,extra=calculate();other=json.loads(a.certificate.read_text())
    if mine!=other:
        keys=sorted(k for k in set(mine)|set(other) if mine.get(k)!=other.get(k))
        raise ValueError('CERTIFICATE_MISMATCH: '+','.join(keys))
    result={'schema':'beal.block72.independent.v1','status':'PASS_FINITE_ASSERTIONS',
            'summary_sha256':hashlib.sha256(json.dumps(mine,sort_keys=True,separators=(',',':')).encode()).hexdigest(),
            'checks':extra,'accepted_local_lifts':mine['accepted_local_lifts'],
            'bounded_augmented_lifts':mine['bounded_augmented_lifts'],
            'proof_scope':'No verification of universal analytic or global representation hypotheses.'}
    a.output.parent.mkdir(parents=True,exist_ok=True);a.output.write_text(json.dumps(result,sort_keys=True,indent=2)+'\n')
    print('PASS independent B72',mine['accepted_local_lifts'],mine['bounded_augmented_lifts'])
if __name__=='__main__':main()
