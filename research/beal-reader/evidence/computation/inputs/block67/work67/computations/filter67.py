#!/usr/bin/env python3
"""Refine the frozen complete-P2000 tuples using the actual1051 good/bad test."""
from __future__ import annotations
import argparse,copy,hashlib,json,math
from pathlib import Path
GEN={1051:(-2,-1,2,1,0,-1)}
A=[[(x%7+y%7)%7+7*((x//7+y//7)%7) for y in range(49)] for x in range(49)]
M=[[((x%7)*(y%7)+5*(x//7)*(y//7))%7+7*(((x%7)*(y//7)+(x//7)*(y%7))%7) for y in range(49)] for x in range(49)]
def need(x,msg):
    if not x:raise AssertionError(msg)
def prime(q):return q>=2 and all(q%d for d in range(2,math.isqrt(q)+1))
def factors(n):
    ans=[];q=2
    while q*q<=n:
        if n%q==0:
            ans.append(q)
            while n%q==0:n//=q
        q+=1
    if n>1:ans.append(n)
    return ans
def primitive(q):return next(g for g in range(2,q) if all(pow(g,(q-1)//d,q)!=1 for d in factors(q-1)))
def ev(cs,x,q):
    out=0
    for c in reversed(cs):out=(out*x+c)%q
    return out
def bareiss(a):
    a=[row[:] for row in a];n=len(a);sgn=1;last=1
    for k in range(n-1):
        if a[k][k]==0:
            t=next((t for t in range(k+1,n) if a[t][k]),None)
            if t is None:return 0
            a[k],a[t]=a[t],a[k];sgn=-sgn
        pivot=a[k][k]
        for i in range(k+1,n):
            for j in range(k+1,n):
                v=pivot*a[i][j]-a[i][k]*a[k][j]
                need(v%last==0,'Nonexact integer determinant division');a[i][j]=v//last
        for i in range(k+1,n):a[i][k]=0
        last=pivot
    return sgn*a[-1][-1]
def norm(cs):
    cols=[]
    for i in range(6):
        p=[0]*i+list(cs)+[0]*(5-i)
        for j in range(len(p)-1,5,-1):
            v=p[j]
            for k in range(j-6,j):p[k]-=v
            p[j]=0
        cols.append(p[:6])
    return bareiss([[cols[j][i] for j in range(6)] for i in range(6)])
def fdot(xs,ys):
    z=0
    for x,y in zip(xs,ys):z=A[z][M[x][y]]
    return z
def canon(s):return json.dumps(s,sort_keys=True,separators=(',',':'))
def main():
    ap=argparse.ArgumentParser();ap.add_argument('--inherited',type=Path,required=True);ap.add_argument('--counts',type=Path,required=True);ap.add_argument('--output',type=Path,required=True);a=ap.parse_args()
    old=json.loads(a.inherited.read_text());pc=json.loads(a.counts.read_text())
    need(old['status']=='PASS_FINITE_FILTER' and old['count']==2,'Wrong frozen two-candidate boundary')
    universe=[q for q in range(11,2001) if prime(q) and q%7==1 and q%5 in (2,3)]
    need(universe==old['universe'] and len(universe)==25,'Incomplete frozen conductor universe')
    need(pc['status']=='PASS_FINITE_COUNTS' and [r['q'] for r in pc['primes']]==list(GEN),'Wrong new point-count universe')
    rows={};columns=[];tests=[]
    for q in universe:
        g=primitive(q);z=pow(g,(q-1)//7,q);logs={pow(g,i,q):i%7 for i in range(q-1)}
        need(len(logs)==q-1,'Generator is not primitive');cr={};symbols={}
        for ell,cs in GEN.items():
            vv=[ev(cs,pow(z,b,q),q) for b in range(1,7)];need(all(vv),'Nonunit conductor value')
            ll=[logs[t] for t in vv];cr[str(ell)]=-sum(b*l for b,l in enumerate(ll,1))%7
            symbols[str(ell)]={'values':vv,'log_mod7':ll}
        columns.append({'q':q,'generator':g,'root':z,'rows':cr,'symbols':symbols});rows[q]=cr
    for rec in pc['primes']:
        ell=rec['q'];cs=GEN[ell];need(norm(cs)==ell,'Cyclotomic norm mismatch')
        roots=[r for r in range(2,ell) if pow(r,7,ell)==1 and ev(cs,r,ell)==0]
        need(len(roots)==1,'Prime generator has wrong seventh-root zero');rt=roots[0]
        def symbol(x):return next(k for k in range(7) if pow(rt,k,ell)==pow(x%ell,(ell-1)//7,ell))
        ph=[x for x in range(ell) if (x*x-x-1)%ell==0];need(len(ph)==2,'Test prime must split in K')
        K=[[symbol(x),symbol(3),symbol(2*x-1)] for x in ph]
        pairs=sorted({tuple(r['defect_roots']) for r in rec['rows'] if r['residual_pass']})
        tests.append({'q':ell,'generator':list(cs),'norm':norm(cs),'root':rt,'phi_roots':ph,'kummer_rows':K,'paired_trace_sets':[list(t) for t in pairs]})
    initial=copy.deepcopy(old['survivors'])
    def evaluate(s,test):
        q=test['q'];b=sum(rows[t][str(q)]*x for t,x in zip(s['columns'],s['inertia']))%7
        pp=[M[fdot(kr,s['alpha'])][b] for kr in test['kummer_rows']]
        good=any(all(v in pair for v in pp) for pair in test['paired_trace_sets']);bad=not any(pp)
        return {'beta':b,'products':pp,'good_possible':good,'bad_possible':bad,'pass':good or bad}
    survivors=initial;stages=[]
    for test in tests:
        kept=[];rejected=[]
        for s in survivors:
            e=evaluate(s,test)
            if e['pass']:
                t=copy.deepcopy(s);t['values'][str(test['q'])]=e['beta'];kept.append(t)
            else:rejected.append({'candidate':s,'evaluation':e})
        stages.append({'test':test['q'],'before':len(survivors),'after':len(kept),'retained':sorted(kept,key=canon),'rejected':rejected});survivors=kept
    need(len(survivors)==0,'The declared complete-P2000 exclusion failed')
    need(all(e['evaluation']['beta']==4 and sorted(e['evaluation']['products'])==[9,44] for e in stages[0]['rejected']),'Unexpected decisive products')
    out={'schema':'beal.block67.filter.v1','status':'PASS_FINITE_FILTER','inherited_sha256':hashlib.sha256(a.inherited.read_bytes()).hexdigest(),'counts_sha256':hashlib.sha256(a.counts.read_bytes()).hexdigest(),'universe':universe,'columns':columns,'tests':tests,'initial_count':2,'stages':stages,'count':0,'survivors':[], 'nonclaims':['Depth-one only','Complete stipulated inert1-mod7 conductor','No bound on arbitrary support or all primes below2000']}
    a.output.parent.mkdir(parents=True,exist_ok=True);a.output.write_text(json.dumps(out,indent=2,sort_keys=True)+'\n');print(out['status'],[s['after'] for s in stages])
if __name__=='__main__':main()
