from __future__ import annotations
import math, heapq, json, time, csv
from dataclasses import dataclass, asdict
from itertools import combinations
import mpmath as mp
import sympy as sp

TARGET = mp.mpf('1.6299116841270482')
ALPHA = 1/TARGET
mp.mp.dps = 100
SMALL_PRIMES = list(sp.primerange(2, 500))


def factor(n:int):
    return {int(p):int(e) for p,e in sp.factorint(int(n)).items()}

def rad_from_factor(f):
    return math.prod(f.keys()) if f else 1

def rad(n:int):
    return rad_from_factor(factor(n)) if n>1 else 1

def d_free(n:int,d:int)->bool:
    return all(e<d for e in factor(n).values())

def hensel_roots_ratio(B:int,C:int,d:int,q:int,emax:int):
    if math.gcd(B*C*d,q)!=1: return []
    cinv=pow(C,-1,q)
    roots=[]
    for r in range(1,q):
        if (pow(r,d,q)-B*cinv)%q: continue
        deriv=(C*d*pow(r,d-1,q))%q
        if deriv==0: continue
        rr=r; mod=q; branch=[(1,mod,rr)]
        for e in range(1,emax):
            f=C*pow(rr,d)-B
            if f%mod: raise AssertionError('bad lift')
            t=(-(f//mod)*pow(deriv,-1,q))%q
            rr += t*mod
            mod *= q
            branch.append((e+1,mod,rr))
        roots.append(branch)
    return roots

def cf_convergents_real(x, max_den:int, max_terms=80):
    # handles negative x; standard floor continued fraction
    a=[]; z=mp.mpf(x)
    p0,p1=0,1; q0,q1=1,0
    out=[]
    for _ in range(max_terms):
        ai=int(mp.floor(z)); a.append(ai)
        p=ai*p1+p0; q=ai*q1+q0
        if q>0:
            out.append((p,q,ai))
            if q>max_den: break
        frac=z-ai
        if abs(frac)<mp.mpf('1e-90'): break
        z=1/frac
        p0,p1=p1,p; q0,q1=q1,q
    return out

def upper_rad_trial(n:int, bound_primes=SMALL_PRIMES):
    if n<=1:return 1
    x=n; r=1
    for p in bound_primes:
        if p*p>x: break
        if x%p==0:
            r*=p
            while x%p==0:x//=p
    if x>1:
        # If remaining cofactor is a perfect power, use base radical upper bound.
        pp=sp.perfect_power(x)
        if pp:
            base,exp=pp
            # rad(base) <= base, good upper bound
            r*=int(base)
        else:
            r*=x
    return r

@dataclass
class Candidate:
    B:int; C:int; d:int; q:int; e:int; M:int; root:int
    x:int; y:int; a:int; b:int; c:int
    residual:int; lower_quality:float; approximate_quality:float
    score:float; source:str
    exact_quality:float|None=None
    radical:int|None=None
    fa:str='';fb:str='';fc:str=''


def make_cores(d:int):
    vals={1}
    vals.update(int(p) for p in sp.primerange(2,607))
    ranked=[]
    for n in range(2,6001):
        f=sp.factorint(n)
        if len(f)>3 or any(e>=d for e in f.values()): continue
        r=math.prod(f.keys())
        efficiency=math.log(n)/math.log(r) if r>1 else 1
        if efficiency>1.12: ranked.append((efficiency,n))
    ranked.sort(reverse=True)
    vals.update(n for _,n in ranked[:25])
    return sorted(vals)

def core_pairs(d:int):
    cores=make_cores(d)
    return [(u,1) for u in cores if u!=1]+[(1,u) for u in cores if u!=1]

def preliminary_candidate(B,C,d,q,e,M,r,x,y,source):
    if x<=0 or y<=0 or math.gcd(x,y)!=1:return None
    left=C*pow(x,d); right=B*pow(y,d)
    if left==right:return None
    diff=abs(left-right)
    if diff%M:return None
    g0=math.gcd(left,right)
    if g0>1:
        left//=g0;right//=g0;diff//=g0
    a=diff;b=min(left,right);c=max(left,right)
    if c<=2**63 or math.gcd(a,b)!=1:return None
    if a%q:return None
    residual=a
    while residual%q==0: residual//=q
    # Fast pessimistic radical upper bound, treating x,y,residual as squarefree.
    R_upper=rad(B)*rad(C)*q*max(1,x)*max(1,y)*max(1,residual)
    lower_q=float(mp.log(c)/mp.log(R_upper)) if R_upper>1 else 0.0
    score=float(ALPHA*mp.log(c)-mp.log(R_upper))
    return Candidate(B,C,d,q,e,M,r,x,y,a,b,c,residual,lower_q,lower_q,score,source)

def run(dmin=3,dmax=8):
    t0=time.time();heap=[];uid=0;seen=set()
    stats={'pairs':0,'branches':0,'cf_states':0,'candidates':0,'definite_beats':0}
    primes=[3,5,7,11,13,17,19,23,29,31,37]
    depths=[9,13,17]
    max_den=10**12
    for d in range(dmin,dmax+1):
        pairs=core_pairs(d)
        stats['pairs']+=len(pairs)
        for B,C in pairs:
            alpha=mp.power(mp.mpf(B)/C, mp.mpf(1)/d)
            for q in primes:
                branches=hensel_roots_ratio(B,C,d,q,max(depths))
                for br in branches:
                    by_e={e:(M,r) for e,M,r in br}
                    for e in depths:
                        if e not in by_e:continue
                        M,r=by_e[e];stats['branches']+=1
                        # x = r*y + M*t and t/y approximates (alpha-r)/M.
                        delta=(alpha-r)/M
                        conv=cf_convergents_real(delta,max_den)
                        # Include convergents and a small semiconvergent fan around the last steps.
                        for idx,(t,y,ai) in enumerate(conv):
                            if y<2 or y>max_den:continue
                            x=r*y+M*t
                            stats['cf_states']+=1
                            cand=preliminary_candidate(B,C,d,q,e,M,r,x,y,'convergent')
                            if cand is None:continue
                            key=(cand.a,cand.b,cand.c)
                            if key in seen:continue
                            seen.add(key);stats['candidates']+=1
                            if cand.lower_quality>TARGET:stats['definite_beats']+=1
                            uid+=1
                            item=(cand.score,uid,cand)
                            if len(heap)<8000:heapq.heappush(heap,item)
                            elif item[0]>heap[0][0]:heapq.heapreplace(heap,item)
    arr=[t[2] for t in sorted(heap,reverse=True)]
    # Exact factorization of top candidates, with a time-conscious size cap.
    exact=[]
    for cand in arr[:80]:
        try:
            if max(cand.a.bit_length(),cand.b.bit_length(),cand.c.bit_length())>420:
                exact.append(cand);continue
            fa=factor(cand.a);fb=factor(cand.b);fc=factor(cand.c)
            R=rad_from_factor(fa)*rad_from_factor(fb)*rad_from_factor(fc)
            cand.radical=R
            cand.exact_quality=float(mp.log(cand.c)/mp.log(R))
            cand.fa=' '.join(f'{p}^{e}' for p,e in sorted(fa.items()))
            cand.fb=' '.join(f'{p}^{e}' for p,e in sorted(fb.items()))
            cand.fc=' '.join(f'{p}^{e}' for p,e in sorted(fc.items()))
        except Exception:
            pass
        exact.append(cand)
    exact.sort(key=lambda z:(z.exact_quality if z.exact_quality is not None else z.lower_quality),reverse=True)
    stats.update(elapsed=time.time()-t0,retained=len(arr),exact_factored=sum(x.exact_quality is not None for x in exact))
    return stats,exact

if __name__=='__main__':
    import argparse
    ap=argparse.ArgumentParser();ap.add_argument('--dmin',type=int,default=3);ap.add_argument('--dmax',type=int,default=8);ap.add_argument('--prefix',default='/mnt/data/ABC_Hybrid_Adelic_Search')
    args=ap.parse_args()
    stats,hits=run(args.dmin,args.dmax)
    out={'stats':stats,'target':float(TARGET),'top':[asdict(h) for h in hits[:200]]}
    open(args.prefix+'_RESULTS.json','w').write(json.dumps(out,indent=2)+'\n')
    with open(args.prefix+'_HITS.csv','w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(asdict(hits[0]).keys()));w.writeheader();w.writerows(asdict(h) for h in hits)
    print(json.dumps(stats,indent=2))
    for h in hits[:25]: print(h.exact_quality,h.lower_quality,h.a,h.b,h.c,'B,C,d,q,e=',h.B,h.C,h.d,h.q,h.e,h.source)
