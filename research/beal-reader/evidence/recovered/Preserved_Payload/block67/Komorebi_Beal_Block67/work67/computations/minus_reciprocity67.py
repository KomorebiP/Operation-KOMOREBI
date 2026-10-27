#!/usr/bin/env python3
"""Exact chi^-1 epsilon5 fixed13 row and bounded geometric support audit.
Uses only standard-library integer arithmetic. No sufficiency is asserted.
"""
from __future__ import annotations
import argparse,json,math
from pathlib import Path

def ck(ok,why):
    if not ok:raise AssertionError(why)
def prime(q):return q>=2 and all(q%d for d in range(2,math.isqrt(q)+1))
def factors(n):
    out=[];d=2
    while d*d<=n:
        if n%d==0:
            out.append(d)
            while n%d==0:n//=d
        d+=1
    if n>1:out.append(n)
    return out

def primitive(q):return next(g for g in range(2,q) if all(pow(g,(q-1)//d,q)!=1 for d in factors(q-1)))
def pmul(x,y,p):return ((x[0]*y[0]+x[1]*y[1])%p,(x[0]*y[1]+x[1]*y[0]+x[1]*y[1])%p)
def ppow(x,n,p):
    y=(1,0)
    while n:
        if n&1:y=pmul(y,x,p)
        x=pmul(x,x,p);n//=2
    return y

def bareiss(a):
    a=[r[:] for r in a];sgn=1;last=1
    for k in range(len(a)-1):
        if not a[k][k]:
            j=next((j for j in range(k+1,len(a)) if a[j][k]),None)
            if j is None:return 0
            a[k],a[j]=a[j],a[k];sgn=-sgn
        piv=a[k][k]
        for i in range(k+1,len(a)):
            for j in range(k+1,len(a)):
                z=piv*a[i][j]-a[i][k]*a[k][j];ck(z%last==0,'Nonexact determinant division');a[i][j]=z//last
        for i in range(k+1,len(a)):a[i][k]=0
        last=piv
    return sgn*a[-1][-1]

def normM(cs):
    columns=[]
    for i in range(6):
        v=[0]*i+list(cs)+[0]*(5-i)
        for d in range(10,5,-1):
            for j in range(d-6,d):v[j]-=v[d]
            v[d]=0
        columns.append(v[:6])
    return bareiss([[columns[j][i] for j in range(6)] for i in range(6)])

def build():
    # Norm_{L/M}(1+phi+zeta^2)=1+3zeta^2+zeta^4.
    nm=normM([1,0,3,0,1,0]);ck(nm==169,'Bad norm of prime13 generator')
    p=13;z=(0,8);ck(ppow(z,7,p)==(1,0) and z!=(1,0),'Wrong seventh root at13')
    zeros=[]
    for sign,ph in [(1,(0,1)),(-1,(1,12))]:
        for b in range(1,7):
            zz=ppow(z,2*b,p);v=((1+ph[0]+zz[0])%p,(ph[1]+zz[1])%p)
            if v==(0,0):zeros.append([sign,b])
    ck(zeros==[[1,1],[-1,6]],'Wrong prime13 embeddings')
    split=[];eligible2000=[];inert_minus=[]
    for q in range(11,10001):
        if not prime(q):continue
        f=1 if q%5 in (1,4) else 2;Q=q**f
        if Q%7!=1:continue
        if f==1:
            ph=[x for x in range(q) if (x*x-x-1)%q==0];ck(len(ph)==2,'Split residue roots')
            ok=pow(ph[0],(q-1)//7,q)==1;ck(ok==(pow(ph[1],(q-1)//7,q)==1),'Conjugate eligibility mismatch')
        else:ok=ppow((0,1),(Q-1)//7,q)==(1,0)
        if q<=2000 and ok:
            eligible2000.append([q,f,q%7])
            if f==2 and q%7==6:inert_minus.append(q)
        if f!=1 or not ok:continue
        g=primitive(q);rt=pow(g,(q-1)//7,q);log={pow(g,i,q):i%7 for i in range(q-1)}
        vals=[];powers=[];row=0
        for sign,phv in zip((1,-1),ph):
            for b in range(1,7):
                value=(1+phv+pow(rt,2*b,q))%q;ck(value!=0,'Conductor overlaps13')
                val=log[value];row-=sign*b*val;vals.append(value);powers.append(val)
        K=[log[ph[0]],log[3],log[(2*ph[0]-1)%q]]
        allowed=[r for r in range(1,7) if (K[1]*r+K[2])%7==0]
        # Check every conjugate generator has the expected chi^-1 epsilon5 scaling.
        cov=[]
        for eps in (1,-1):
            for a in range(1,7):
                rr=0
                for s,phv in zip((1,-1),ph):
                    t=phv if eps==1 else (1-phv)%q
                    for b in range(1,7):rr-=s*b*log[(1+t+pow(rt,2*a*b,q))%q]
                ck(rr%7==(eps*pow(a,-1,7)*row)%7,'Wrong minus-twist covariance');cov.append(rr%7)
        split.append({'q':q,'phi_roots':ph,'generator':g,'zeta_root':rt,'values':vals,'logs':powers,'R13_minus':row%7,'natural_row':K,'allowed_ratios':allowed,'conjugate_rows':cov})
    ck(inert_minus==[307,797,1483],'Unexpected small inert-minus eligibility')
    expected=[2269,2521,2731,2969,3571,3739,4481,4831,5741,6091,6329,6581,9521]
    ck([r['q'] for r in split]==expected,'Unexpected bounded split eligibility')
    admissible=[r for r in split if r['allowed_ratios']]
    ck(all(r['R13_minus']!=0 for r in admissible),'A single-minus-place survives the new row in the declared range')
    groups={str(r):[s['q'] for s in admissible if r in s['allowed_ratios']] for r in range(1,7)}
    byq={r['q']:r for r in split}
    ck((byq[2269]['R13_minus']+6*byq[2521]['R13_minus'])%7==0,'Two-place control lost')
    ck(6 in byq[2269]['allowed_ratios'] and 6 in byq[2521]['allowed_ratios'],'Control natural ratios')
    return {'schema':'beal.block67.minus.v1','status':'PASS_MINUS_ROW','bound':10000,'prime13_generator':'1+phi+zeta7^2','relative_norm':[1,0,3,0,1,0],'norm':169,'prime13_zeta_phi_basis':[0,8],'prime13_zero_embeddings':zeros,'eligible_split_records':split,'eligible_rational_primes_through2000':eligible2000,'inert_minus_through2000':inert_minus,'ratio_groups':groups,'number_admissible_split_primes':len(admissible),'two_place_control':{'ramification':[[2269,1],[2521,6]],'natural_ratio':6,'satisfies13_row':True,'global_Frey_realization':False},'scope':'Necessary minus-component row when actual local beta at13 is ZERO. Do not impose solely from all-depth semilinearity.'}

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--output',type=Path,required=True);a=ap.parse_args();o=build();a.output.parent.mkdir(parents=True,exist_ok=True);a.output.write_text(json.dumps(o,indent=2,sort_keys=True)+'\n');print(o['status'],len(o['eligible_split_records']))
if __name__=='__main__':main()
