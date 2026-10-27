#!/usr/bin/env python3
"""Separate cyclotomic-column audit in theta^2=d fields and weighted products.
No imports of primary/project arithmetic. Verifies every residue evaluation,
conjugation covariance, representative independence, and integral generator norm.
"""
from __future__ import annotations
import argparse,json,math,itertools,hashlib
from pathlib import Path

def check(x,msg):
    if not x:raise AssertionError(msg)
def divisors(n):
    out=[];d=2
    while d*d<=n:
        if n%d==0:
            out.append(d)
            while n%d==0:n//=d
        d+=1
    if n>1:out.append(n)
    return out
class Quadratic:
    def __init__(self,q):
        self.q=q
        squares={a*a%q for a in range(q)}
        self.d=next(d for d in range(2,q) if d not in squares)
        self.phi=None
        if 5 not in squares:
            s=next(a for a in range(q) if a*a*self.d%q==5)
            self.phi=(pow(2,-1,q),s*pow(2,-1,q)%q)
    def add(self,x,y):return ((x[0]+y[0])%self.q,(x[1]+y[1])%self.q)
    def times(self,x,y):
        a,b=x;c,d=y;q=self.q
        return ((a*c+self.d*b*d)%q,(a*d+b*c)%q)
    def power(self,x,n):
        ans=(1,0)
        for digit in bin(n)[2:]:
            ans=self.times(ans,ans)
            if digit=='1':ans=self.times(ans,x)
        return ans
    def from_phi(self,x):
        a,b=x
        if not b:return (a%self.q,0)
        check(self.phi is not None,'No phi field map')
        return ((a+b*self.phi[0])%self.q,b*self.phi[1]%self.q)
    def eval(self,cs,z):
        total=(0,0);p=(1,0)
        for c in cs:
            total=self.add(total,(c*p[0]%self.q,c*p[1]%self.q));p=self.times(p,z)
        return total

def ringmul(a,b):
    c=[0]*7
    for i,x in enumerate(a):
        for j,y in enumerate(b):c[(i+j)%7]+=x*y
    t=c[6]
    return [x-t for x in c[:6]]
def product_norm(cs):
    out=[1,0,0,0,0,0]
    for j in range(1,7):
        a=[0]*7
        for i,c in enumerate(cs):a[i*j%7]+=c
        b=[x-a[6] for x in a[:6]];out=ringmul(out,b)
    check(out[1:]==[0]*5,'Norm product nonrational')
    return out[0]

def main():
    p=argparse.ArgumentParser();p.add_argument('--fixture',type=Path,required=True);p.add_argument('--certificate',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args()
    d=json.loads(a.fixture.read_text());cert=json.loads(a.certificate.read_text())
    check(cert['status']=='PASS_EXACT_COLUMNS','Bad primary status')
    wanted=sorted(d['inherited_universe']+[307,797,1483]);check(cert['universe']==wanted,'Incomplete conductor universe')
    norms={k:product_norm(v) for k,v in d['generators'].items()};check(all(int(k)==v for k,v in norms.items()),'Wrong test-prime norm')
    rows=[];symbols=0;covariance=0;repchecks=0;unitchecks=0
    for rec in cert['columns']:
        q=rec['q'];f=1 if q%7==1 else 2;F=Quadratic(q);N=q**f
        # Find the prescribed primitive element independently and check its full order.
        it=((j,0) for j in range(2,q)) if f==1 else ((i,j) for j in range(1,q) for i in range(q))
        gg=next(x for x in it if all(F.power(F.from_phi(x),(N-1)//p)!=(1,0) for p in divisors(N-1)))
        check(list(gg)==rec['generator'],'Wrong declared primitive generator')
        g=F.from_phi(gg);z=F.power(g,(N-1)//7)
        check(z==F.from_phi(rec['zeta']),'Wrong residue root')
        roots=[F.power(z,i) for i in range(7)]
        def symbol(x):
            check(x!=(0,0),'Nonunit symbol input')
            return roots.index(F.power(x,(N-1)//7))
        def weighted(cs,multiplier=1,reps=None):
            reps=list(range(1,7)) if f==1 else ([6,2,4] if reps is None else reps)
            product=(1,0)
            for b in reps:product=F.times(product,F.power(F.eval(cs,F.power(z,b*multiplier%7)),b))
            return -symbol(product)%7
        newrows={}
        for ell in d['test_order']:
            if ell==q:continue
            k=str(ell);cs=d['generators'][k];v=weighted(cs);newrows[k]=v
            check(v==rec['rows'][k],'Changed degree-dependent twisted column')
            for b in range(1,7):
                value=F.eval(cs,F.power(z,b))
                check(value==F.from_phi(rec['symbols'][k]['values'][b-1]),'Changed residue value')
                check(symbol(value)==rec['symbols'][k]['logs_mod7'][b-1],'Changed residue logarithm')
                symbols+=1
            for m in range(1,7):
                check(weighted(cs,m)==pow(m,-1,7)*v%7,'Inverse-cyclotomic covariance failed');covariance+=1
            if f==2:
                for reps in itertools.product((1,6),(2,5),(3,4)):
                    check(weighted(cs,reps=reps)==v,'Orbit representative dependence');repchecks+=1
        if f==1:kr=[0,2*symbol((3,0))%7,symbol((5,0))]
        else:kr=[symbol(F.phi),symbol((3,0)),symbol(F.from_phi((q-1,2)))]
        check(kr==rec['kummer'],'Wrong natural residue row')
        rat=(-kr[2]*pow(kr[1],-1,7))%7 if kr[1] else ('all' if not kr[2] else 'none')
        check(rat==rec['ratio'],'Wrong support coefficient ratio')
        # Cyclotomic units (1-zeta^j)/(1-zeta) cannot contribute to chi^-1.
        for j in range(1,7):
            cs=[1]*j
            check(weighted(cs)==0,'Cyclotomic unit projection nonzero');unitchecks+=1
        rows.append({'q':q,'f':f,'theta_squared':F.d,'rows':newrows,'kummer':kr,'ratio':rat})
    check(len(rows)==28,'Wrong number of conductor factors')
    out={'schema':'beal.block68.independent-columns.v1','status':'PASS_SEPARATE_COLUMN_AUDIT','primary_imports':False,'norms':norms,'rows':rows,'direct_symbol_checks':symbols,'conjugation_checks':covariance,'degree_two_representative_checks':repchecks,'cyclotomic_unit_checks':unitchecks,'certificate_sha256':hashlib.sha256(a.certificate.read_bytes()).hexdigest()}
    a.output.parent.mkdir(parents=True,exist_ok=True);a.output.write_text(json.dumps(out,indent=2,sort_keys=True)+'\n');print(out['status'],symbols,covariance,repchecks)
if __name__=='__main__':main()
