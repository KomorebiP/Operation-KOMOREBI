#!/usr/bin/env python3
"""Exact, finite same-representation trace-product compatibility certificate."""
from __future__ import annotations
import argparse,hashlib,itertools,json,math
from pathlib import Path
S=(197,883,1373,1667)
TESTS=(29,43,71,211,239,491)
ORDER=(29,43,491,211,239)
GEN={197:(1,-1,-1,-1,1,-1),883:(0,0,1,-2,1,2),1373:(0,2,-2,-1,-2,-2),
 1667:(1,-2,1,2,1,2),29:(0,0,0,1,-1,-1),43:(-1,-1,-1,-1,-1,1),
 71:(0,1,-1,-1,1,-1),211:(-2,-2,-2,-2,1,-1),239:(-2,-2,0,-1,-2,1),491:(0,1,-2,2,0,2)}
def need(v,why):
    if not v:raise AssertionError(why)
def cmul(a,b):
    c=[0]*11
    for i,x in enumerate(a):
        for j,y in enumerate(b):c[i+j]+=x*y
    for i in range(10,5,-1):
        for j in range(1,7):c[i-j]-=c[i]
    return c[:6]
def det(a):
    a=[list(x) for x in a];last=1;sgn=1
    for k in range(len(a)-1):
        if not a[k][k]:
            i=next((i for i in range(k+1,len(a)) if a[i][k]),None)
            if i is None:return 0
            a[k],a[i]=a[i],a[k];sgn=-sgn
        p=a[k][k]
        for i in range(k+1,len(a)):
            for j in range(k+1,len(a)):
                n=p*a[i][j]-a[i][k]*a[k][j];need(n%last==0,'Bareiss division')
                a[i][j]=n//last
            a[i][k]=0
        last=p
    return sgn*a[-1][-1]
def norm(a):return det(list(zip(*[cmul(a,[int(i==j) for i in range(6)]) for j in range(6)])))
def ev(a,x,p):
    v=0
    for c in a[::-1]:v=(v*x+c)%p
    return v
ADD=[[((x%7+y%7)%7)+7*((x//7+y//7)%7) for y in range(49)] for x in range(49)]
MUL=[[((x%7*(y%7)+5*(x//7)*(y//7))%7)+7*((x%7*(y//7)+(x//7)*(y%7))%7) for y in range(49)] for x in range(49)]
def dot(a,b):
    v=0
    for x,y in zip(a,b):v=ADD[v][MUL[x][y]]
    return v

def run(pointdata):
    roots={};gens={};logs={};evals={};rows={};kummer={}
    for q,a in GEN.items():
        need(all(q%d for d in range(2,math.isqrt(q)+1)),'Nonprime norm label')
        n=norm(a);need(n==q,'Norm mismatch')
        rs=[r for r in range(2,q) if pow(r,7,q)==1 and ev(a,r,q)==0]
        need(len(rs)==1,'Ambiguous prime generator')
        roots[q]=rs[0];gens[str(q)]={'coefficients':list(a),'norm':n,'root':rs[0]}
    for q in S:
        table={};a=1
        for j in range(q-1):table[a]=j%7;a=2*a%q
        need(len(table)==q-1 and a==1,'2 is not primitive')
        logs[q]=table
    for ell in TESTS:
        rows[ell]=[];evals[str(ell)]={}
        for q in S:
            residues=[ev(GEN[ell],pow(roots[q],b,q),q) for b in range(1,7)]
            need(all(residues),'A test prime lies in the conductor')
            ls=[logs[q][r] for r in residues]
            rows[ell].append(-sum(b*x for b,x in enumerate(ls,1))%7)
            evals[str(ell)][str(q)]={'residues':residues,'logs_base_2_mod7':ls}
        def klog(x):
            symbol=pow(x,(ell-1)//7,ell)
            return next(j for j in range(7) if pow(roots[ell],j,ell)==symbol)
        pr=[x for x in range(ell) if (x*x-x-1)%ell==0]
        if pr:kummer[ell]=[[klog(x),klog(3),klog((2*x-1)%ell)] for x in pr]
        else:kummer[ell]=[[0,2*klog(3)%7,klog(5)]]
    need(rows[71]==[6,2,0,5],'Inherited 71 row mismatch')
    need(all(r[0]!=0 for q in (29,71,491) for r in kummer[q]),'Period-zero controls failed')
    good={p['q']:set(p['trace_defect_set']) for p in pointdata['primes']}
    expected={29:{2},43:{3,4,5},491:{5,12,19,26,33,40,47,13,48},
      211:{0,6,10,45,22,29,24,31},239:{7,42,8,43,9,44,24,31}}
    need(good==expected,'Changed exact trace sets')
    initial=[]
    for u in range(49):
        for c in range(1,49):initial.append(([u,6,1],[c,MUL[4][c],0,0]))
        for a in range(49):
            for b in range(49):
                if a or b:initial.append(([u,1,1],[0,a,b,a]))
    need(len(initial)==119952,'Incorrect reduced candidate count')
    stages=[];current=initial;checkpoints={}
    for q in ORDER:
        kept=[];audit=[]
        for alpha,s in current:
            need(dot(rows[71],s)==0,'71 local-zero lost')
            v=dot(rows[q],s)
            if q==43:v=MUL[2][v]
            products=[MUL[dot(k,alpha)][v] for k in kummer[q]]
            isgood=all(p in good[q] for p in products)
            isbad=all(p==0 for p in products)
            if any(k[0] for k in kummer[q]):isbad=isbad and v==0
            if isgood or isbad:kept.append((alpha,s))
            if q in (211,239):audit.append({'alpha':alpha,'beta':s,'beta_frobenius':v,
                 'products':products,'good_possible':isgood,'bad_possible':isbad})
        stages.append({'q':q,'input_candidates':len(current),'survivors':len(kept)})
        current=kept
        if q in (491,211,239):checkpoints[str(q)]=[{'alpha':a,'beta':s} for a,s in current]
        if audit:checkpoints[str(q)+'_audit']=audit
    need([x['survivors'] for x in stages]==[2402,152,9,1,0],'Unexpected trace-product result')
    # A global diagonal change rescales alpha and beta inversely and preserves products.
    gauge_checks=0
    for z in range(1,49):
        zi=next(x for x in range(1,49) if MUL[z][x]==1)
        alpha=[0,1,1];beta=[0,2,6,2]
        for q in ORDER:
            v=dot(rows[q],beta);v=MUL[2][v] if q==43 else v
            aa=[MUL[z][x] for x in alpha];bb=[MUL[zi][x] for x in beta]
            vv=dot(rows[q],bb);vv=MUL[2][vv] if q==43 else vv
            for k in kummer[q]:need(MUL[dot(k,aa)][vv]==MUL[dot(k,alpha)][v],'Gauge product changed');gauge_checks+=1
    return {'schema':'beal.block62.trace_product.v1','status':'PASS_NO_COMPATIBLE_CANDIDATE',
      'support':list(S),'test_primes':list(TESTS),'sieve_order':list(ORDER),
      'prime_generators':gens,'residue_evaluations':evals,'frobenius_rows':{str(q):rows[q] for q in TESTS},
      'kummer_rows':{str(q):kummer[q] for q in TESTS},'good_trace_sets':{str(q):sorted(good[q]) for q in ORDER},
      'initial_candidate_count':len(initial),'stages':stages,'checkpoints':checkpoints,
      'gauge_product_checks':gauge_checks,
      'overapproximation':'At split places either coefficient-conjugate trace may be chosen independently; even this larger system is empty.',
      'nonclaims':['No exclusion with additional beta ramification','No unconditional depth-one proof','No new Lean certificate']}

def main():
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--pointcounts',type=Path,required=True);ap.add_argument('--output',type=Path,required=True);a=ap.parse_args()
    p=json.loads(a.pointcounts.read_text());need(p['status']=='PASS_FINITE_COUNTS','Unverified point-count input')
    result=run(p);a.output.parent.mkdir(parents=True,exist_ok=True);a.output.write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
    print(json.dumps({'status':result['status'],'initial':result['initial_candidate_count'],'stages':result['stages']}))
if __name__=='__main__':main()
