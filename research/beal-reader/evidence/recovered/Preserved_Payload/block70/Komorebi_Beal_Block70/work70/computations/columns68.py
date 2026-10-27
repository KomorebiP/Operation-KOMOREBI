#!/usr/bin/env python3
"""Exact chi^-1 conductor columns, including the three residue-degree-two primes.
Standard library only. Field arithmetic is in the phi basis, phi^2=phi+1.
"""
from __future__ import annotations
import argparse,hashlib,json,math
from pathlib import Path

def need(x,msg):
    if not x: raise ValueError(msg)
def prime(q): return q>=2 and all(q%d for d in range(2,math.isqrt(q)+1))
def factors(n):
    ans=[];d=2
    while d*d<=n:
        if n%d==0:
            ans.append(d)
            while n%d==0:n//=d
        d+=1
    if n>1:ans.append(n)
    return ans
class Field:
    def __init__(self,q,degree):self.q=q;self.degree=degree;self.order=q**degree
    def add(self,x,y):q=self.q;return ((x[0]+y[0])%q,(x[1]+y[1])%q)
    def mul(self,x,y):
        a,b=x;c,d=y;q=self.q
        return ((a*c+b*d)%q,(a*d+b*c+b*d)%q)
    def pow(self,x,n):
        y=(1,0)
        while n:
            if n&1:y=self.mul(y,x)
            x=self.mul(x,x);n>>=1
        return y
    def ev(self,cs,x):
        y=(0,0)
        for a in reversed(cs):y=self.add(self.mul(y,x),(a%self.q,0))
        return y
    def primitive(self):
        fs=factors(self.order-1)
        # In degree two all rational elements are necessarily nonprimitive.
        cand=((a,0) for a in range(2,self.q)) if self.degree==1 else ((a,b) for b in range(1,self.q) for a in range(self.q))
        for g in cand:
            if all(self.pow(g,(self.order-1)//p)!=(1,0) for p in fs):return g
        raise ValueError('No primitive element')

def norm(cs):
    cols=[]
    for i in range(6):
        a=[0]*i+list(cs)+[0]*(5-i)
        for j in range(len(a)-1,5,-1):
            c=a[j]
            for k in range(j-6,j):a[k]-=c
            a[j]=0
        cols.append(a[:6])
    a=[[cols[j][i] for j in range(6)] for i in range(6)];sgn=1;last=1
    for k in range(5):
        if not a[k][k]:
            s=next((j for j in range(k+1,6) if a[j][k]),None)
            if s is None:return 0
            a[k],a[s]=a[s],a[k];sgn=-sgn
        p=a[k][k]
        for i in range(k+1,6):
            for j in range(k+1,6):
                v=p*a[i][j]-a[i][k]*a[k][j];need(v%last==0,'Nonexact norm division');a[i][j]=v//last
        for i in range(k+1,6):a[i][k]=0
        last=p
    return sgn*a[-1][-1]

def column(q,fixture):
    need(prime(q) and q%5 in (2,3) and q%7 in (1,6),'Invalid conductor prime')
    f=1 if q%7==1 else 2;F=Field(q,f);g=F.primitive();z=F.pow(g,(F.order-1)//7)
    need(F.pow(g,F.order-1)==(1,0) and z!=(1,0),'Invalid generator')
    seventh={F.pow(z,i):i for i in range(7)}
    def log(x):
        need(x!=(0,0),'Nonunit evaluation')
        return seventh[F.pow(x,(F.order-1)//7)]
    if f==1:
        l3=2*log((3,0))%7;l5=log((5,0));kr=[0,l3,l5]
        reps=list(range(1,7))
    else:
        kr=[log((0,1)),log((3,0)),log((q-1,2))]
        need(kr==[0,0,0],'New inert-minus-one Kummer class unexpectedly nonzero')
        reps=[1,2,3]
    rat=(-kr[2]*pow(kr[1],-1,7))%7 if kr[1] else ('all' if kr[2]==0 else 'none')
    rows={};symbols={}
    for ell in fixture['test_order']:
        if ell==q:continue
        cs=fixture['generators'][str(ell)]
        vv=[F.ev(cs,F.pow(z,b)) for b in range(1,7)];ll=[log(x) for x in vv]
        if f==2:
            for b in range(1,7):
                need(F.pow(vv[b-1],q)==vv[6-b], 'Frobenius value pairing failed')
                need((ll[b-1]+ll[6-b])%7==0,'Frobenius logarithm pairing failed')
        row=-sum(b*ll[b-1] for b in reps)%7
        need(row==(-pow(f,-1,7)*sum(b*ll[b-1] for b in range(1,7)))%7,'Orbit-average formula failed')
        rows[str(ell)]=row;symbols[str(ell)]={'values':[list(t) for t in vv],'logs_mod7':ll}
    return {'q':q,'residue_degree':f,'generator':list(g),'zeta':list(z),'orbit_representatives':reps,'kummer':kr,'ratio':rat,'rows':rows,'symbols':symbols}

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--fixture',type=Path,required=True);ap.add_argument('--output',type=Path,required=True);a=ap.parse_args()
    d=json.loads(a.fixture.read_text());old=d['inherited_universe'];universe=sorted(old+[307,797,1483]);need(len(universe)==28,'Wrong universe')
    for k,cs in d['generators'].items():need(norm(cs)==int(k),'Wrong integral test-prime norm')
    cc=[column(q,d) for q in universe]
    # Reproduce all old columns at the eight old test primes, not just their support.
    for c in d['inherited_columns']:
        new=next(t for t in cc if t['q']==c['q'])
        need(new['kummer']==c['kummer'] and new['ratio']==c['ratio'],'Inherited Kummer normalization changed')
        for k,v in c['rows'].items():need(new['rows'][k]==v,'Inherited twisted column changed')
    out={'schema':'beal.block68.columns.v1','status':'PASS_EXACT_COLUMNS','fixture_sha256':hashlib.sha256(a.fixture.read_bytes()).hexdigest(),'universe':universe,'columns':cc,'new_primes':[307,797,1483],'new_orbit_factor':2,'test_order':d['test_order'],'generator_norms':{k:norm(v) for k,v in d['generators'].items()},'nonclaims':['No new point counts','Conductor bound 2000 is an explicit restriction','Correct row system is necessary, not a global Frey realization']}
    a.output.parent.mkdir(parents=True,exist_ok=True);a.output.write_text(json.dumps(out,sort_keys=True,indent=2)+'\n')
    print(out['status'])
    for c in cc:
        if c['residue_degree']==2: print(c['q'],c['generator'],c['zeta'],c['rows'])
if __name__=='__main__':main()
