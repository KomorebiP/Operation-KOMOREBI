#!/usr/bin/env python3
"""Separate minus-row audit: cyclic norm product, sqrt5 basis, direct symbols."""
from __future__ import annotations
import argparse,json,math
from pathlib import Path

def ck(ok,msg):
    if not ok:raise AssertionError(msg)
def sieve(N):
    p=[True]*(N+1);p[0:2]=[False,False]
    for d in range(2,math.isqrt(N)+1):
        if p[d]:
            for t in range(d*d,N+1,d):p[t]=False
    return p

def mul(x,y,p):return ((x[0]*y[0]+5*x[1]*y[1])%p,(x[0]*y[1]+x[1]*y[0])%p)
def power(x,n,p):
    # left-to-right powering, distinct from the primary right-to-left routine
    z=(1,0)
    for bit in bin(n)[2:]:
        z=mul(z,z,p)
        if bit=='1':z=mul(z,x,p)
    return z

def cyc(a,b):
    out=[(0,0)]*7
    for i,(x,y) in enumerate(a):
        for j,(s,t) in enumerate(b):
            aa,bb=out[(i+j)%7];out[(i+j)%7]=(aa+x*s+y*t,bb+x*t+y*s+y*t)
    return out

def norm13():
    out=[(1,0)]+[(0,0)]*6
    for eps in (1,-1):
        for a in range(1,7):
            fac=[(0,0)]*7;fac[0]=(1,1) if eps==1 else (2,-1);fac[2*a%7]=(1,0);out=cyc(out,fac)
    ck(len(set(out[1:]))==1,'Norm did not reduce moduloPhi7')
    return (out[0][0]-out[1][0],out[0][1]-out[1][1])

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--certificate',type=Path,required=True);ap.add_argument('--output',type=Path,required=True);a=ap.parse_args();d=json.loads(a.certificate.read_text());ck(d['status']=='PASS_MINUS_ROW','Wrong minus status');ck(norm13()==(169,0),'Norm13 failure');ck(d['norm']==169 and d['relative_norm']==[1,0,3,0,1,0],'Changed norm certificate')
    ck(d['prime13_generator']=='1+phi+zeta7^2','Changed prime13 generator')
    # At13, phi=(1+sqrt5)/2 and zeta=8phi=4+4sqrt5.
    z=(4,4);ph=[(7,7),(7,6)];zeros=[]
    for s,t in zip((1,-1),ph):
        for b in range(1,7):
            zz=power(z,2*b,13)
            if ((1+t[0]+zz[0])%13,(t[1]+zz[1])%13)==(0,0):zeros.append([s,b])
    ck(zeros==d['prime13_zero_embeddings'] and d['prime13_zeta_phi_basis']==[0,8],'Changed prime13 factor')
    primes=sieve(10000);eligible2000=[];records=[];terms=0;covchecks=0
    for q in range(11,10001):
        if not primes[q]:continue
        f=1 if q%5 in (1,4) else 2;Q=q**f
        if Q%7!=1:continue
        i2=pow(2,-1,q)
        if f==1:
            rad=[x for x in range(q) if x*x%q==5];pp=sorted({(1+x)*i2%q for x in rad});ck(len(pp)==2,'Wrong split roots')
            ok=all(pow(x,(q-1)//7,q)==1 for x in pp)
        else:ok=power((i2,i2),(Q-1)//7,q)==(1,0)
        if q<=2000 and ok:eligible2000.append([q,f,q%7])
        if f!=1 or not ok:continue
        divs=[l for l in range(2,q) if primes[l] and (q-1)%l==0]
        g=next(g for g in range(2,q) if all(pow(g,(q-1)//l,q)!=1 for l in divs));rt=pow(g,(q-1)//7,q);inverse=pow(rt,-1,q)
        symbols={pow(inverse,(-b)%7,q):b for b in range(7)}
        def sym(v):return symbols[pow(v%q,(q-1)//7,q)]
        vals=[];logs=[];row=0
        for s,t in zip((1,-1),pp):
            for b in range(1,7):
                val=(1+t+pow(inverse,(-2*b)%7,q))%q;ck(val!=0,'Conductor overlaps norm13');e=sym(val);vals.append(val);logs.append(e);row-=s*b*e;terms+=1
        K=[sym(pp[0]),sym(3),sym(2*pp[0]-1)];ratios=[r for r in range(1,7) if (K[1]*r+K[2])%7==0];conj=[]
        for eps in (1,-1):
            for texp in range(1,7):
                val=0
                for s,t in zip((1,-1),pp):
                    base=t if eps==1 else (1-t)%q
                    for b in range(1,7):val-=s*b*sym((1+base+pow(inverse,(-2*texp*b)%7,q))%q)
                ck(val%7==eps*pow(texp,-1,7)*row%7,'Independent twist covariance');conj.append(val%7);covchecks+=1
        records.append({'q':q,'phi_roots':pp,'generator':g,'zeta_root':rt,'values':vals,'logs':logs,'R13_minus':row%7,'natural_row':K,'allowed_ratios':ratios,'conjugate_rows':conj})
    ck(records==d['eligible_split_records'],'Changed minus reciprocal row or eligibility')
    ck(eligible2000==d['eligible_rational_primes_through2000'],'Changed complete small eligibility')
    inertminus=[q for q,f,r in eligible2000 if f==2 and r==6];ck(inertminus==d['inert_minus_through2000']==[307,797,1483],'Changed inert-minus cases')
    allowed=[r for r in records if r['allowed_ratios']];groups={str(r):[s['q'] for s in allowed if r in s['allowed_ratios']] for r in range(1,7)}
    ck(groups==d['ratio_groups'] and len(allowed)==d['number_admissible_split_primes'],'Changed common-ratio conditions');ck(all(s['R13_minus'] for s in allowed),'A single-minus-place survives')
    control={'ramification':[[2269,1],[2521,6]],'natural_ratio':6,'satisfies13_row':True,'global_Frey_realization':False};ck(d['two_place_control']==control,'Changed two-prime control');byq={r['q']:r for r in records};ck((byq[2269]['R13_minus']+6*byq[2521]['R13_minus'])%7==0,'Two-prime relation failed')
    out={'schema':'beal.block67.independent_minus.v1','status':'PASS_INDEPENDENT_MINUS','primary_imports':False,'norm_algorithm':'product of all12 conjugates in cyclic group ring with integral phi basis','residue_basis':'sqrt5 and inverse cyclotomic roots','split_eligible_primes':len(records),'allowed_split_primes':len(allowed),'direct_main_symbols':terms,'conjugate_row_checks':covchecks,'all_geometrically_eligible_primes_through2000':len(eligible2000),'inert_minus_cases':inertminus}
    a.output.parent.mkdir(parents=True,exist_ok=True);a.output.write_text(json.dumps(out,indent=2,sort_keys=True)+'\n');print(out['status'],len(records))
if __name__=='__main__':main()
