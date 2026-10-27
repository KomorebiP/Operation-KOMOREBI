"""Exact finite illustrations for six v0.2 admissions. Not a proof kernel.

Only fractions, finite tables, and bounded policy trees enter acceptance checks.
The prior check_core.py is not altered. No training or external service is used.
"""
from __future__ import annotations
from fractions import Fraction as F
from pathlib import Path
from itertools import product, combinations
from functools import lru_cache
from collections import defaultdict
import hashlib, json, platform, sys, time, traceback

ROOT=Path(__file__).resolve().parents[1]
GROUPS=[]
CURRENT=None
DATA={}

def ck(v: bool, message: str='') -> None:
    CURRENT['assertions'] += 1
    if not v: raise AssertionError(message or CURRENT['name'])

def group(result: str, name: str, domain: str):
    def run(fn):
        global CURRENT
        CURRENT={'result':result,'name':name,'domain':domain,'assertions':0}
        t=time.perf_counter()
        try:
            fn();CURRENT['status']='PASS'
        except Exception:
            CURRENT['status']='FAIL';CURRENT['traceback']=traceback.format_exc();raise
        finally:
            CURRENT['seconds']=time.perf_counter()-t
            GROUPS.append(dict(CURRENT))
    return run

def canon(seq):
    d={};return tuple(d.setdefault(x,len(d)) for x in seq)

def partitions(n):
    out=[]
    def rec(p):
        if len(p)==n:out.append(tuple(p));return
        for x in range(max(p,default=-1)+2):rec(p+[x])
    rec([]);return out

def simplex(n,den):
    def rec(left,k):
        if k==1:
            yield (F(left,den),);return
        for a in range(left+1):
            for tail in rec(left-a,k-1):yield (F(a,den),)+tail
    return tuple(rec(den,n))

def tv(p,q):
    if len(p)!=len(q):raise ValueError('probability lengths differ')
    return sum((abs(a-b) for a,b in zip(p,q)),F(0))/2

def d_tv(p,q):
    return sum((abs(p.get(k,F(0))-q.get(k,F(0))) for k in p.keys()|q.keys()),F(0))/2

def mm(A,B):
    return tuple(tuple(sum((A[i][k]*B[k][j] for k in range(len(B))),F(0)) for j in range(len(B[0]))) for i in range(len(A)))

def mv(A,p):
    return tuple(sum((a*b for a,b in zip(row,p)),F(0)) for row in A)

def aggregate(p,pi):
    return tuple(sum((v for v,z0 in zip(p,pi) if z0==z),F(0)) for z in range(max(pi)+1))

def bayes(p,l):
    mass=sum((a*b for a,b in zip(p,l)),F(0))
    return None if mass==0 else tuple(a*b/mass for a,b in zip(p,l))

def refine(pi0,Ks,likelihoods):
    pi=canon((pi0[x],tuple(l[x] for l in likelihoods)) for x in range(len(pi0)))
    chain=[pi]
    while True:
        new=canon((pi[x],tuple(sum(K[x][j] for j in range(len(pi)) if pi[j]==b)
                   for K in Ks for b in range(max(pi)+1))) for x in range(len(pi)))
        if new==pi:return pi,chain
        pi=new;chain.append(pi)

def finer(p,q):
    return all(p[x]!=p[y] or q[x]==q[y] for x in range(len(p)) for y in range(len(p)))

def is_closed(pi,Ks,ls):
    n=len(pi)
    return all(pi[x]!=pi[y] or
        (all(l[x]==l[y] for l in ls) and all(
        sum(K[x][j] for j in range(n) if pi[j]==b)==sum(K[y][j] for j in range(n) if pi[j]==b)
        for K in Ks for b in range(max(pi)+1))) for x in range(n) for y in range(n))

# Instrument rows K[a][x][(next_state, report)] use the declared joint law.
def validate(K):
    if not K or not K[0]:raise ValueError('empty instrument')
    n=len(K[0])
    for rows in K:
        if len(rows)!=n:raise ValueError('state dimensions')
        for row in rows:
            if any(v<0 or not (0<=xp<n) or o<0 for (xp,o),v in row.items()):raise ValueError('invalid row')
            if sum(row.values(),F(0))!=1:raise ValueError('unnormalized instrument')

def quotient(K,pi):
    validate(K)
    if len(pi)!=len(K[0]) or set(pi)!=set(range(max(pi)+1)):raise ValueError('not a surjective partition')
    result=[]
    for rows in K:
        coarse=[None]*(max(pi)+1)
        for x,row in enumerate(rows):
            proj=defaultdict(F)
            for (xp,o),w in row.items():proj[(pi[xp],o)] += w
            proj={k:v for k,v in proj.items() if v}
            z=pi[x]
            if coarse[z] is not None and coarse[z]!=proj:raise ValueError('joint fibre mismatch')
            coarse[z]=proj
        result.append(tuple(coarse))
    return tuple(result)

def branches(p,rows):
    n=len(p);raw={}
    for x,px in enumerate(p):
        for (xp,o),w in rows[x].items():
            if o not in raw:raw[o]=[F(0)]*n
            raw[o][xp] += px*w
    out={}
    for o,v in sorted(raw.items()):
        mass=sum(v,F(0))
        if mass:out[o]=(mass,tuple(a/mass for a in v))
    return out

def history_law(K,p,pi,H,choices):
    # Full fine paths are retained internally, then projected. Policy sees reports only.
    full={( (x,),() ):v for x,v in enumerate(p) if v}
    for t in range(H):
        new=defaultdict(F)
        for (states,h),mass in full.items():
            idx=(2**t-1)+sum(o*(2**(t-1-j)) for j,(_,o) in enumerate(h))
            a=choices[idx]
            for (xp,o),w in K[a][states[-1]].items():
                new[(states+(xp,),h+((a,o),))] += mass*w
        full={k:v for k,v in new.items() if v}
    proj=defaultdict(F)
    for (states,h),v in full.items():proj[(tuple(pi[x] for x in states),h)] += v
    return dict(proj)

def sensor(accuracy=F(3,4), with_flip=True):
    X=tuple(product(range(2),repeat=3));index={x:i for i,x in enumerate(X)}
    K=[]
    for a in range(2 if with_flip else 1):
        rows=[]
        for b,s,n in X:
            bb=(1-b) if a else b
            signal=(bb^s) if a else s
            row={}
            for o in range(2):
                nn=n^o^a if with_flip else n
                row[(index[(bb,s,nn)],o)]=accuracy if o==signal else 1-accuracy
            rows.append(row)
        K.append(tuple(rows))
    return tuple(K),tuple(2*b+s for b,s,n in X),X

def binary_sensor(accuracy):
    return tuple(tuple({(x^a,o):(accuracy if o==(x^a) else 1-accuracy) for o in range(2)} for x in range(2)) for a in range(2))

def solve(p,rows,targets,cost,h):
    @lru_cache(None)
    def rec(p,h):
        stop=[sum((p[i] for i,t in enumerate(targets) if t!=d),F(0)) for d in (0,1)]
        vals=[(stop[0],('stop',0)),(stop[1],('stop',1))]
        if h:
            branch=branches(p,rows)
            ans={o:rec(pp,h-1) for o,(_,pp) in branch.items()}
            val=cost+sum((mass*ans[o][0] for o,(mass,_) in branch.items()),F(0))
            vals.append((val,('ask',tuple((o,ans[o][1]) for o in sorted(ans)))))
        best=min(v for v,_ in vals)
        return best,next(tree for v,tree in vals if v==best),tuple(i for i,(v,_) in enumerate(vals) if v==best)
    return rec(tuple(p),h)

@lru_cache(None)
def trees(h):
    st=(('stop',0),('stop',1))
    if not h:return st
    ch=trees(h-1)
    return st+tuple(('ask',((0,l),(1,r))) for l in ch for r in ch)

def eval_tree(tree,p,rows,targets,cost):
    if tree[0]=='stop':return sum((p[i] for i,t in enumerate(targets) if t!=tree[1]),F(0))
    kids=dict(tree[1])
    return cost+sum((mass*eval_tree(kids[o],pp,rows,targets,cost) for o,(mass,pp) in branches(p,rows).items()),F(0))

def main():
 @group('r:positive-packets','Probability components and signed reconstruction',
        'All 2x2 half-grid matrices P with nonnegative P and I-P; exact idempotence. Haar decomposition on nine rational priors and an invertible signed-coordinate change.')
 def _():
    I=((F(1),F(0)),(F(0),F(1)))
    admitted=[]
    for ent in product((F(0),F(1,2),F(1)),repeat=4):
        P=(ent[:2],ent[2:]);Q=tuple(tuple(I[i][j]-P[i][j] for j in range(2)) for i in range(2))
        if all(x>=0 for row in Q for x in row) and mm(P,P)==P and mm(Q,Q)==Q:
            admitted.append(P)
            ck(P[0][1]==P[1][0]==0 and P[0][0] in (0,1) and P[1][1] in (0,1))
    ck(len(admitted)==4)
    av=((F(1,2),F(1,2)),(F(1,2),F(1,2)))
    det=((F(1,2),F(-1,2)),(F(-1,2),F(1,2)))
    T=((1,1),(1,-1));inv=((F(1,2),F(1,2)),(F(1,2),F(-1,2)))
    for p in simplex(2,8):
        u,v=mv(av,p),mv(det,p)
        ck(tuple(a+b for a,b in zip(u,v))==p)
        ck(sum(v)==0)
        for P in admitted:
            transformed=mm(mm(T,P),inv);part=mv(transformed,mv(T,p))
            ck(part[0]>=abs(part[1]))
            ck(part[0]!=0 or part==(0,0))
    p=(F(3,4),F(1,4));u,v=mv(av,p),mv(det,p)
    ck(v==(F(1,4),F(-1,4)))
    clipped=tuple(a+max(F(0),b) for a,b in zip(u,v));clipped=tuple(a/sum(clipped) for a in clipped)
    ck(clipped==(F(3,5),F(2,5)) and clipped!=p)
    DATA['packets']={'belief':[str(x) for x in p],'average':[str(x) for x in u],'detail':[str(x) for x in v],'clipped_normalized':[str(x) for x in clipped]}

 @group('r:joint-refinement','Least simultaneous prediction and update closure',
        'All deterministic one-action maps through three states; every initial partition with at least two blocks; likelihood entries 1/4,1/2,3/4 with complementary report. All half-grid 3-state Markov rows for one fixed likelihood/partition. Independent enumeration of every refining partition.')
 def _():
    for n in (2,3):
        ps=partitions(n)
        for f in product(range(n),repeat=n):
            K=tuple(tuple(F(int(f[x]==j)) for j in range(n)) for x in range(n))
            for ell in product((F(1,4),F(1,2),F(3,4)),repeat=n):
                ls=(ell,tuple(1-x for x in ell))
                for p0 in ps:
                    if max(p0)==0:continue
                    fin,chain=refine(p0,(K,),ls)
                    good=[p for p in ps if finer(p,p0) and is_closed(p,(K,),ls)]
                    ck(fin in good and all(finer(p,fin) for p in good))
                    ck(len(chain)-1<=n-(max(chain[0])+1))
                    for p in simplex(n,2):
                        for l in ls:
                            coarse_l=tuple(l[fin.index(z)] for z in range(max(fin)+1))
                            ck(aggregate(bayes(p,l),fin)==bayes(aggregate(p,fin),coarse_l))
    for K in product(simplex(3,2),repeat=3):
        ls=((F(1,4),F(1,4),F(3,4)),);p0=(0,0,1)
        fin,_=refine(p0,(K,),ls)
        good=[p for p in partitions(3) if finer(p,p0) and is_closed(p,(K,),ls)]
        ck(fin in good and all(finer(p,fin) for p in good))
    f=(0,2,3,3);K=tuple(tuple(F(int(f[x]==j)) for j in range(4)) for x in range(4))
    fin,chain=refine((0,0,0,1),(K,),((F(1),)*4,))
    ck(chain==[(0,0,0,1),(0,0,1,2),(0,1,2,3)])
    K,pi,X=sensor();p0=canon(b^s for b,s,n in X)
    trans=[]
    for rows in K:
        trans.append(tuple(tuple(sum((w for (xp,o),w in row.items() if xp==j),F(0)) for j in range(8)) for row in rows))
    ls=tuple(tuple(F(3,4) if o==s else F(1,4) for b,s,n in X) for o in range(2))
    fin,_=refine(p0,tuple(trans),ls)
    ck(fin==pi and len(set(fin))==4)
    # The one-block boundary deliberately does not force likelihood constancy.
    ck(aggregate(bayes((F(1,2),F(1,2)),(F(1,4),F(3,4))),(0,0))==(F(1),))
    DATA['refinement']={'sensor_before':p0,'sensor_after':fin,'propagation_example':chain}

 @group('r:instrument','Joint instrument, exact filtering, and feedback',
        'Every deterministic instrument on three states with two reports and partition (0,0,1), compared with all deterministic coarse instruments. Exact rational 8-to-4 sensor filtering for all binary feedback trees through horizon three and selected point/midpoint priors. Correlated-marginal and malformed-kernel controls.')
 def _():
    pi=(0,0,1)
    coarse_options=tuple(product(range(2),repeat=2))
    for tab in product(tuple(product(range(3),range(2))),repeat=3):
        K=(tuple({v:F(1)} for v in tab),)
        try:Q=quotient(K,pi);passes=True
        except ValueError:passes=False
        exists=any(all(c[pi[x]]==(pi[tab[x][0]],tab[x][1]) for x in range(3)) for c in product(coarse_options,repeat=2))
        ck(passes==exists)
        if passes:
            for p in simplex(3,2):
                fb=branches(p,K[0]);qb=branches(aggregate(p,pi),Q[0])
                ck(set(fb)==set(qb))
                for o,(m,pp) in fb.items():ck(qb[o]==(m,aggregate(pp,pi)))
    K,pi,X=sensor();Q=quotient(K,pi)
    priors=[]
    for i in range(8):priors.append(tuple(F(int(j==i)) for j in range(8)))
    for i,j in ((0,3),(0,6),(1,7),(2,5)):
        priors.append(tuple(F(1,2) if k in (i,j) else F(0) for k in range(8)))
    priors.append((F(1,8),)*8)
    for p in priors:
        for choices in product(range(2),repeat=7):
            fine=history_law(K,p,pi,3,choices)
            coarse=history_law(Q,aggregate(p,pi),tuple(range(4)),3,choices)
            ck(fine==coarse)
    rows=({(0,0):F(1,2),(2,1):F(1,2)}, {(0,1):F(1,2),(2,0):F(1,2)}, {(2,0):F(1)},{(2,0):F(1)})
    try:quotient((rows,),(0,0,1,1));accepted=True
    except ValueError:accepted=False
    ck(not accepted)
    def marginal(row,which):
        out=defaultdict(F)
        for (x,o),v in row.items():out[(x//2) if which==0 else o]+=v
        return dict(out)
    ck(marginal(rows[0],0)==marginal(rows[1],0))
    ck(marginal(rows[0],1)==marginal(rows[1],1))
    ck(aggregate(branches((F(1),F(0),F(0),F(0)),rows)[1][1],(0,0,1,1))==(F(0),F(1)))
    ck(aggregate(branches((F(0),F(1),F(0),F(0)),rows)[1][1],(0,0,1,1))==(F(1),F(0)))
    for bad in ((({(0,0):F(-1),(0,1):F(2)},),), (({(0,0):F(1,2)},),)):
        try:validate(bad);ok=True
        except ValueError:ok=False
        ck(not ok)
    for p in simplex(2,4):
        ck(bayes(p,(F(1,4),)*2)==bayes(p,(F(3,4),)*2)==p)
    DATA['instrument']={'fine_states':8,'retained_states':4,'checked_feedback_depth':3,'marginal_failure':'identical marginals, opposite conditional next state'}

 @group('r:history-bound','Whole path error and sharp conditional amplification',
        'All pairs of 4-cell quarter-grid probability laws and all nonempty events. Binary controlled sensors with three exact accuracies, three initial beliefs, every horizon-two binary feedback tree; full path total variation and its state/report projections. Same-policy failure control.')
 def _():
    laws=simplex(4,4)
    for p in laws:
        for q in laws:
            delta=tv(p,q)
            for mask in range(1,16):
                inds=[i for i in range(4) if mask>>i&1];a=sum(p[i] for i in inds);b=sum(q[i] for i in inds)
                ck(abs(a-b)<=delta)
                if a and b:
                    cond=tv(tuple(p[i]/a for i in inds),tuple(q[i]/b for i in inds))
                    ck(cond<=min(F(1),delta/max(a,b)))
                if max(a,b)>delta:ck(min(a,b)>0)
    rates=(F(1,4),F(1,2),F(3,4))
    for r,s in product(rates,repeat=2):
        K,Q=binary_sensor(r),binary_sensor(s)
        for p1,q1 in product(rates,repeat=2):
            p,q=(1-p1,p1),(1-q1,q1)
            bound=min(F(1),tv(p,q)+2*abs(r-s))
            for choices in product(range(2),repeat=3):
                P=history_law(K,p,(0,1),2,choices);Qlaw=history_law(Q,q,(0,1),2,choices)
                ck(d_tv(P,Qlaw)<=bound)
    for delta in (F(1,4),F(1,8),F(1,16),F(1,32),F(1,64)):
        p=(1-delta,delta,F(0));q=(1-delta,F(0),delta)
        ck(tv(p,q)==delta and tv((F(1),F(0)),(F(0),F(1)))==1)
    # Identical dynamics, different policies: a zero same-policy bound is inapplicable.
    K=(( {(0,0):F(1)}, ),( {(0,1):F(1)}, ))
    ck(d_tv(history_law(K,(F(1),),(0,),1,(0,)),history_law(K,(F(1),),(0,),1,(1,)))==1)
    DATA['rare_event']={'masses':['1/4','1/8','1/16','1/32','1/64'],'conditional_distance':'1'}

 @group('r:belief-planning','Exact compressed belief decisions and policy enumeration',
        '8-to-4 sensor beliefs with 3 exact observation accuracies, 4 charges, point/midpoint priors and horizons 0..3. Direct enumeration of all 1,446 depth-three binary-observation trees for the calibrated diagonal prior. Exact expected stopping cost and number of reports.')
 def _():
    chosen=None
    for accuracy in (F(1,2),F(3,4),F(1)):
        K,pi,X=sensor(accuracy,with_flip=False);Q=quotient(K,pi)
        targets=tuple(b for b,s,n in X);ztargets=(0,0,1,1)
        priors=[(F(1,8),)*8]
        for i,j in ((0,6),(1,7),(0,7),(2,5),(0,3)):
            priors.append(tuple(F(1,2) if k in (i,j) else F(0) for k in range(8)))
        for cost in (F(0),F(1,20),F(1,5),F(1)):
            for p in priors:
                for h in range(4):
                    fine=solve(p,K[0],targets,cost,h);coarse=solve(aggregate(p,pi),Q[0],ztargets,cost,h)
                    ck(fine==coarse)
    K,pi,X=sensor(F(3,4),False);Q=quotient(K,pi);p=(F(1,2),F(0),F(0),F(0),F(0),F(0),F(1,2),F(0));q=aggregate(p,pi)
    targets=tuple(b for b,s,n in X);cost=F(1,20)
    values=[]
    for h in range(4):
        ans=solve(q,Q[0],(0,0,1,1),cost,h);values.append(ans[0])
        vals=[eval_tree(t,q,Q[0],(0,0,1,1),cost) for t in trees(h)]
        ck(ans[0]==min(vals))
        for t,v in zip(trees(h),vals):ck(eval_tree(t,p,K[0],targets,cost)==v)
    ck(values==[F(1,2),F(3,10),F(3,10),F(11,40)])
    ck(len(trees(3))==1446)
    selected=solve(q,Q[0],(0,0,1,1),cost,3)[1]
    error=eval_tree(selected,q,Q[0],(0,0,1,1),F(0))
    ck(error==F(5,32))
    ck((values[-1]-error)/cost==F(19,8))
    # A non-factorizing permission registry is rejected separately, not by probabilities.
    pi0=(0,0);A=(frozenset({0}),frozenset())
    ck(not all(pi0[x]!=pi0[y] or A[x]==A[y] for x in range(2) for y in range(2)))
    DATA['planning']={'horizons':list(range(4)),'optimal_values':[str(x) for x in values],'expected_reports':str(F(19,8)),'error_probability':str(error),'expected_charge':str(F(19,160)),'policy':selected,'fine_prior':[str(x) for x in p]}

 @group('r:policy-error','Uniform model comparison before optimizing policies',
        'All 38 depth-two binary-calibration trees, observation accuracies 1/2, 3/4, 1 and prior target masses 1/4,1/2,3/4. Paired fixed-tree and optimum regret comparisons at cost 1/20. Three-report exact sensitivity at true accuracy 37/50.')
 def _():
    cost=F(1,20);H=2;B=1+H*cost
    cases=[]
    for accuracy in (F(1,2),F(3,4),F(1)):
        rows=binary_sensor(accuracy)[0]
        for mass in (F(1,4),F(1,2),F(3,4)):
            p=(1-mass,mass)
            vals=[eval_tree(t,p,rows,(0,1),cost) for t in trees(2)]
            cases.append((accuracy,p,vals))
    for a,p,v in cases:
        for b,q,w in cases:
            delta=min(F(1),tv(p,q)+H*abs(a-b))
            for vi,wi in zip(v,w):ck(abs(vi-wi)<=B*delta)
            chosen=min(range(len(w)),key=w.__getitem__)
            ck(v[chosen]-min(v)<=min(B,2*B*delta))
    planned=binary_sensor(F(3,4))[0];actual=binary_sensor(F(37,50))[0];p=(F(1,2),F(1,2))
    selected=solve(p,planned,(0,1),cost,3)[1]
    got=eval_tree(selected,p,actual,(0,1),cost)
    optimum=solve(p,actual,(0,1),cost,3)[0]
    ck(got==F(35861,125000) and got==optimum)
    bound=2*F(23,20)*F(3,100)
    ck(bound==F(69,1000) and got-optimum<=bound)
    DATA['sensitivity']={'true_accuracy':'37/50','planning_accuracy':'3/4','uniform_regret_bound':str(bound),'selected_true_value':str(got),'true_optimum':str(optimum),'model_value':'11/40','zero_regret_in_this_example_is_not_used_as_a_uniform_bound':True}

if __name__=='__main__':
    t=time.perf_counter();before=hashlib.sha256(Path(__file__).read_bytes()).hexdigest();error=None
    try:main()
    except Exception:error=traceback.format_exc()
    report={'status':'PASS' if error is None else 'FAIL','group_count':len(GROUPS),'assertions':sum(g['assertions'] for g in GROUPS),'groups':GROUPS,'seconds':time.perf_counter()-t,'python':sys.version,'platform':platform.platform(),'arithmetic':'exact fractions and finite tables','source_sha256_before':before,'source_sha256_after':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),'error':error,'limits':['Six bounded domains, not six universal computational proofs.','No learning, sampling, external interaction or proof kernel.','Alternative checks are project-authored.']}
    (ROOT/'evidence').mkdir(exist_ok=True)
    (ROOT/'evidence/admission_checks.json').write_text(json.dumps(report,indent=2)+'\n')
    (ROOT/'evidence/admission_examples.json').write_text(json.dumps(DATA,indent=2)+'\n')
    print(json.dumps({k:report[k] for k in ('status','group_count','assertions','seconds')},indent=2))
    if error:print(error,file=sys.stderr);sys.exit(1)
