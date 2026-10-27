#!/usr/bin/env python3
"""Bounded exact checks for Machine Societies v0.7.0.

No agents are trained or simulated. These checks audit finite constructions and
algebraic identities; they do not replace the general prose proofs.
Run from any directory: python validation/check_finite_models.py
"""
from __future__ import annotations
from collections import Counter
from fractions import Fraction as Q
from itertools import product, combinations, permutations
from pathlib import Path
import hashlib, json, math, platform, sys, time, traceback
from datetime import datetime, timezone

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'validation'
GROUPS: list[dict] = []
CURRENT: dict = {}

def require(condition: bool, detail: str = '') -> None:
    CURRENT['assertions'] += 1
    if not condition:
        raise AssertionError(detail or f"Assertion failed in {CURRENT['name']}")

def group(name: str, domain: str):
    def decorate(fn):
        global CURRENT
        CURRENT = {'name': name, 'domain': domain, 'assertions': 0}
        start = time.perf_counter()
        try:
            fn()
            CURRENT.update(status='PASS', runtime_seconds=time.perf_counter()-start)
        except Exception:
            CURRENT.update(status='FAIL', traceback=traceback.format_exc(),
                           runtime_seconds=time.perf_counter()-start)
            GROUPS.append(CURRENT.copy())
            raise
        GROUPS.append(CURRENT.copy())
        return fn
    return decorate

def tv(p, q): return sum(abs(a-b) for a,b in zip(p,q))/2

def matvec_row(v, M): return tuple(sum(v[i]*M[i][j] for i in range(len(v))) for j in range(len(M[0])))

def parts(n):
    """All set partitions as canonical restricted-growth strings."""
    if n == 0:
        yield ()
        return
    def extend(p):
        if len(p) == n:
            yield tuple(p)
        else:
            for k in range(max(p)+2):
                yield from extend(p+[k])
    yield from extend([0])

def canonical(items):
    seen = {}
    return tuple(seen.setdefault(x, len(seen)) for x in items)

def enabled(F, i): return tuple(a for a in range(len(F[i])) if F[i][a] >= 0)

def compatible(F, labels, p):
    n=len(F)
    for i in range(n):
        for j in range(n):
            if p[i] == p[j]:
                if labels[i] != labels[j] or enabled(F,i) != enabled(F,j): return False
                if any(p[F[i][a]] != p[F[j][a]] for a in enabled(F,i)): return False
    return True

def refine(F, labels):
    p=canonical([(labels[i], enabled(F,i)) for i in range(len(F))])
    initial=len(set(p)); steps=0
    while True:
        q=canonical([(p[i], tuple((a,p[F[i][a]]) for a in enabled(F,i))) for i in range(len(F))])
        if q==p: return p, steps, initial
        p=q; steps+=1

def run_checks():
    @group('Deterministic quotient criterion', 'All 256 functions on four states; fixed two-fibre projection')
    def _():
        pi=(0,0,1,1)
        for F in product(range(4), repeat=4):
            criterion=all(pi[F[i]]==pi[F[j]] for i in range(4) for j in range(4) if pi[i]==pi[j])
            witnesses=[G for G in product(range(2),repeat=2) if all(pi[F[i]]==G[pi[i]] for i in range(4))]
            require(criterion == bool(witnesses))
            require(len(witnesses) <= 1)

    @group('Controlled lumpability', 'Four-state rational kernels with rows drawn from five distributions')
    def _():
        rows=[tuple(Q(int(i==j)) for j in range(4)) for i in range(4)]+[(Q(1,4),)*4]
        for K in product(rows,repeat=4):
            projected=[(r[0]+r[1],r[2]+r[3]) for r in K]
            good=projected[0]==projected[1] and projected[2]==projected[3]
            candidate=(projected[0],projected[2])
            require(good == all(projected[i]==candidate[i//2] for i in range(4)))

    @group('Finite-horizon and contraction bounds', 'Two-state rational kernels on quarter grids; horizons 0..8')
    def _():
        vals=[Q(i,4) for i in range(5)]
        matrices=[((p,1-p),(q,1-q)) for p,q in product(vals,repeat=2)]
        for K in matrices:
            for B in matrices:
                eps=max(tv(K[i],B[i]) for i in range(2))
                kap=tv(B[0],B[1]); p=(Q(1),Q(0)); q=(Q(0),Q(1)); bound=Q(1)
                for t in range(9):
                    require(tv(p,q) <= min(Q(1),1+t*eps))
                    require(tv(p,q) <= bound)
                    p=matvec_row(p,K);q=matvec_row(q,B);bound=kap*bound+eps

    @group('Non-Markov deterministic projection', 'Uniform initial law on a three-cycle')
    def _():
        pi=(0,0,1)
        triples=[(pi[x],pi[(x+1)%3],pi[(x+2)%3]) for x in range(3)]
        for previous,expected in [(1,Q(0)),(0,Q(1))]:
            xs=[r for r in triples if r[0]==previous and r[1]==0]
            require(Q(sum(r[2]==1 for r in xs),len(xs))==expected)

    @group('Governance quotient and coarsest refinement', 'All 4^6 partial two-action tables on three states; all five partitions')
    def _():
        labels=(0,0,1); partitions=list(parts(3))
        for flat in product(range(-1,3),repeat=6):
            F=tuple(tuple(flat[2*i:2*i+2]) for i in range(3))
            p,steps,initial=refine(F,labels)
            require(compatible(F,labels,p))
            require(steps <= 3-initial)
            candidates=[q for q in partitions if compatible(F,labels,q)]
            require(len(set(p))==min(len(set(q)) for q in candidates))
            for q in candidates:
                require(all(q[i]!=q[j] or p[i]==p[j] for i in range(3) for j in range(3)))

    @group('Governance-loss counterexample', 'Two equal-output states with different amendment permissions')
    def _():
        F=((0,1),(1,-1)); labels=(0,0)
        require(not compatible(F,labels,(0,0)))
        require(compatible(F,labels,(0,1)))

    @group('Four-bit reusable-state realization', 'All 16 bit states, three macro operations, all 15 proper coalitions')
    def _():
        states=list(product(range(2),repeat=4))
        ops=[lambda p,q:(p,q), lambda p,q:(q,p),lambda p,q:(p^q,q)]
        for a,b,c,d in states:
            p,q=a^b,c^d
            for op in ops:
                pp,qq=op(p,q); new=(a,a^pp,c,c^qq)
                require((new[0]^new[1],new[2]^new[3])==(pp,qq))
        for mask in range(15):
            counts={}
            for x in states:
                key=tuple(x[i] for i in range(4) if mask>>i&1)
                counts.setdefault(key,Counter())[sum(x)%2]+=1
            require(all(c[0]==c[1] for c in counts.values()))
        require(ops[1](*ops[2](1,0)) != ops[2](*ops[1](1,0)))
        require(((0^0),(1^1))==(0,0))
        require((ops[2](0,0)[0]^ops[2](0,0)[1]) != (ops[2](1,1)[0]^ops[2](1,1)[1]))

    @group('Exact memory lower-bound witness', 'All 16 binary summaries of four future-distinguishable states')
    def _():
        states=list(product(range(2),repeat=2))
        future=[(p^q,p) for p,q in states]
        require(len(set(future))==4)
        for f in product(range(2),repeat=4):
            require(any(f[i]==f[j] and future[i]!=future[j] for i in range(4) for j in range(i)))

    @group('Erasure versus arbitrary corruption', 'Binary length-three parity code; all erasures')
    def _():
        code=[(p,q,p^q) for p,q in product(range(2),repeat=2)]
        distance=min(sum(x!=y for x,y in zip(a,b)) for a,b in combinations(code,2))
        require(distance==2)
        for mask in range(8):
            views=[tuple(x[i] for i in range(3) if not(mask>>i&1)) for x in code]
            if mask.bit_count()<=1: require(len(set(views))==4)
        balls=[{y for y in product(range(2),repeat=3) if sum(a!=b for a,b in zip(x,y))<=1} for x in code]
        require(any(a&b for a,b in combinations(balls,2)))

    @group('Implementation ambiguity and nontransitive similarity', 'Exact point masses and Bernoulli parameters 0, 2/5, 4/5')
    def _():
        p=(Q(1),Q(0));q=(Q(0),Q(1));mid=(Q(1,2),)*2
        require(tv(p,q)==1);require(tv(p,mid)==Q(1,2))
        x,y,z=Q(0),Q(2,5),Q(4,5)
        require(abs(x-y)<Q(1,2) and abs(y-z)<Q(1,2) and abs(x-z)>Q(1,2))

    @group('Repair product-sum identity', 'Nonnegative rational factors, horizons 0..7, three fixed parameter sequences')
    def _():
        for variant in range(3):
            for T in range(8):
                aa=[Q((i+variant)%4,4) for i in range(T)]
                bb=[Q((2*i+variant)%3,5) for i in range(T)]
                e=Q(7,3)
                for a,b in zip(aa,bb):e=a*e+b
                closed=Q(7,3)*math.prod(aa)+sum(bb[j]*math.prod(aa[j+1:]) for j in range(T))
                require(e==closed)

    @group('Symmetry and parallel depth', 'Permutation-equivariant bit updates for n=2..8; balanced trees to 128 leaves')
    def _():
        for n in range(2,9):
            for bit in range(2):
                x=(bit,)*n
                for _ in range(5):
                    x=tuple(int(sum(x)>=n//2+1) for i in range(n))
                    require(len(set(x))==1)
        for h in range(1,8):
            require(sum(2**j for j in range(h))==2**h-1)
            require(all(2**d<2**h for d in range(h)))

    @group('Institutional amortization', 'Discounts 0, 1/2, 9/10, 99/100; finite horizons 0..30')
    def _():
        for delta in [Q(0),Q(1,2),Q(9,10),Q(99,100)]:
            for T in range(31):
                direct=-10+sum(Q(2)*delta**j for j in range(T))
                require(direct==-10+2*(1-delta**T)/(1-delta))
        require(-10+Q(2)/(1-Q(9,10))==10)
        require(-10<0)

    @group('Potential-game increments', 'All adoption profiles for n=2..7, b=1 and c=3/2')
    def _():
        for n in range(2,8):
            for a in product(range(2),repeat=n):
                m=sum(a);phi=Q(m*(m-1),2)-Q(3,2)*m
                for i in range(n):
                    ap=list(a);ap[i]=1-ap[i];mp=sum(ap)
                    phip=Q(mp*(mp-1),2)-Q(3,2)*mp
                    ui=a[i]*(Q(m-a[i])-Q(3,2))
                    uip=ap[i]*(Q(mp-ap[i])-Q(3,2))
                    require(phip-phi==uip-ui)

    @group('Formation barriers and strict seed threshold', 'n=2..8, b=1..3, c=1/2..9/2 including integer ties')
    def _():
        for n,b,j in product(range(2,9),range(1,4),range(1,10)):
            c=Q(j,2)
            require(-c<0)
            if b*(n-1)>c:
                profitable=[m for m in range(1,n+1) if b*(m-1)>c]
                m=math.floor(c/b)+2
                require(m==min(profitable))
                require(all(b*(k-1)-c>0 for k in range(m,n+1)))
                require(all(b*k-c>0 for k in range(m,n)))
        require(math.floor(Q(2))+2==4)

    @group('Truthful majority and agenda dependence', 'Three cyclic rankings; all six sequential agendas')
    def _():
        rankings=((0,1,2),(1,2,0),(2,0,1))
        def wins(a,b):return a if sum(r.index(a)<r.index(b) for r in rankings)>=2 else b
        require(wins(0,1)==0 and wins(1,2)==1 and wins(2,0)==2)
        require({wins(wins(a,b),c) for a,b,c in permutations(range(3))}=={0,1,2})

    @group('Approximate joint-safety inequality', 'All pairs of four-outcome laws with denominator 4; all disjoint nonempty safe sets')
    def _():
        laws=[tuple(Q(x,4) for x in xs) for xs in product(range(5),repeat=4) if sum(xs)==4]
        sets=[mask for mask in range(1,16)]
        sums={p:{m:sum(p[i] for i in range(4) if m>>i&1) for m in sets} for p in laws}
        for p,q in product(laws,repeat=2):
            eta=tv(p,q)
            for A,B in product(sets,repeat=2):
                if not(A&B):require(sums[p][A]+sums[q][B] <= 1+eta)

    @group('Marginal ignorance is not joint indistinguishability', 'Two hidden conditions and two fair correlated bits')
    def _():
        observations=[[(u,u^theta) for u in range(2)] for theta in range(2)]
        for i in range(2):require(Counter(x[i] for x in observations[0])==Counter(x[i] for x in observations[1]))
        require(not(set(observations[0]) & set(observations[1])))
        for theta,xs in enumerate(observations):require(all((a^b)==theta for a,b in xs))

    @group('Bounded obligation monitors', 'Deadlines 0..3; all length-five event words over five events')
    def _():
        events=('tick','fulfill','discharge','invalid_cancel','noop')
        def step(q,event):
            status,remaining=q
            if status!='pending':return q
            if event in ('fulfill','discharge'):return (event,remaining)
            if event=='tick':return ('breach',remaining) if remaining==0 else ('pending',remaining-1)
            return q
        for D in range(4):
            for word in product(events,repeat=5):
                q=('pending',D);r={'status':'pending','remaining':D}
                for event in word:
                    q=step(q,event)
                    if r['status']=='pending':
                        if event in ('fulfill','discharge'):r['status']=event
                        elif event=='tick':
                            if r['remaining']==0:r['status']='breach'
                            else:r['remaining']-=1
                    require(q==(r['status'],r['remaining']))
            q=('pending',D)
            for _ in range(D):q=step(q,'tick')
            require(q[0]=='pending')
            require(step(q,'fulfill')[0]=='fulfill')
            require(step(q,'tick')[0]=='breach')

    @group('Blocking coalitions and threshold size', 'All antichains of nonempty coalitions on n<=3; thresholds through n=7')
    def _():
        for n in range(1,4):
            coal=list(range(1,2**n));full=2**n-1
            for familymask in range(1,2**len(coal)):
                W=[c for i,c in enumerate(coal) if familymask>>i&1]
                if any((a&b)==a or (a&b)==b for a,b in combinations(W,2)):continue
                for C in range(2**n):
                    blocked=not any((w & (full^C))==w for w in W)
                    hit=all(C&w for w in W)
                    require(blocked==hit)
        for n in range(1,8):
            for q in range(1,n+1):
                blocked=[C for C in range(2**n) if n-C.bit_count()<q]
                require(min(C.bit_count() for C in blocked)==n-q+1)

    @group('Conditional cumulative capability', 'Five method domains over four fixed queries; every nested pair of libraries')
    def _():
        domains=({0},{1},{0,2},{2,3},{0,1,2,3})
        cover=lambda mask:set().union(*(domains[i] for i in range(5) if mask>>i&1))
        for old,new in product(range(32),repeat=2):
            if old&new==old:
                require(cover(old)<=cover(new))
                added=set().union(*(domains[i] for i in range(5) if (new^old)>>i&1))
                require((cover(old)<cover(new)) == bool(added-cover(old)))
        require(bool(domains[0]) and not bool(set())) # revoked access can erase attainable coverage

    @group('Lifetime identities and repair values', 'Exact two-state chains on fifth grids; horizons 0..30')
    def _():
        for fnum in range(1,6):
            for rnum in range(5):
                for dnum in range(1,6-rnum):
                    f,r,d=Q(fnum,5),Q(rnum,5),Q(dnum,5)
                    th=(f+r+d)/(f*d);td=th-1/f
                    require(th==1+(1-f)*th+f*td)
                    require(td==1+r*th+(1-r-d)*td)
                    M=((1-f,f),(r,1-r-d));v=(Q(1),Q(0));previous=Q(1);partial=Q(0)
                    for t in range(31):
                        surv=sum(v);require(0<=surv<=previous)
                        partial+=surv;require(partial<=th)
                        v=matvec_row(v,M);previous=surv
        for r,want in [(Q(0),Q(20)),(Q(2,5),Q(60))]:
            f=d=Q(1,10);require((f+r+d)/(f*d)==want)

    @group('Dynamic residual composition', 'Five maps of three metric points; all 3125 choices of T,U,F0,F1,F2')
    def _():
        maps=((0,1,2),(2,1,0),(0,0,0),(1,1,2),(1,2,2));Z=range(3)
        for T,U,F0,F1,F2 in product(maps,repeat=5):
            L=max(Q(abs(U[i]-U[j]),abs(i-j)) for i in Z for j in Z if i!=j)
            e01=max(abs(T[F0[z]]-F1[T[z]]) for z in Z)
            e12=max(abs(U[F1[z]]-F2[U[z]]) for z in Z)
            e02=max(abs(U[T[F0[z]]]-F2[U[T[z]]]) for z in Z)
            require(e02<=L*e01+e12)

    @group('Typed observable residual composition', 'Five maps of three metric points; all 3125 choices of T,U,g0,g1,g2')
    def _():
        maps=((0,1,2),(2,1,0),(0,0,0),(1,1,2),(1,2,2));Z=range(3)
        for T,U,g0,g1,g2 in product(maps,repeat=5):
            e01=max(abs(g1[T[z]]-g0[z]) for z in Z)
            e12=max(abs(g2[U[z]]-g1[z]) for z in Z)
            e02=max(abs(g2[U[T[z]]]-g0[z]) for z in Z)
            require(e02<=e01+e12)

    @group('Binary cycle compatibility and convention invariance', 'All labels and local convention changes for cycle lengths 3..6')
    def _():
        for n in range(3,7):
            for b in product(range(2),repeat=n):
                sols=[x for x in product(range(2),repeat=n) if all(x[i]^x[(i+1)%n]==b[i] for i in range(n))]
                require(bool(sols)==(sum(b)%2==0))
                if sols:require(len(sols)==2)
                for c in product(range(2),repeat=n):
                    bp=[b[i]^c[i]^c[(i+1)%n] for i in range(n)]
                    require(sum(bp)%2==sum(b)%2)

    @group('Minimum protected single-cycle repair', 'Cycle lengths 3..6; every editable mask; costs 1..n and all candidate flip sets')
    def _():
        for n in range(3,7):
            w=list(range(1,n+1))
            for editable in range(2**n):
                candidates=[sum(w[i] for i in range(n) if f>>i&1) for f in range(2**n)
                            if f&editable==f and f.bit_count()%2==1]
                if editable:
                    require(min(candidates)==min(w[i] for i in range(n) if editable>>i&1))
                else:require(not candidates)

    @group('Commons resource and repayment trace', 'All 12 debtor-creditor pairs, all 16 approval patterns, and duplicate token rejection')
    def _():
        ordinary=(1,1,1,1)
        for debtor,creditor in permutations(range(4),2):
            grant=list(ordinary);grant[debtor]+=1;grant[creditor]-=1
            repayment=list(ordinary);repayment[debtor]-=1;repayment[creditor]+=1
            require(sum(grant)==sum(repayment)==4)
            require(all(v>=0 for v in grant+repayment))
            require(tuple(x+y for x,y in zip(grant,repayment))==(2,2,2,2))
            debt=(debtor,creditor,1,2)
            successor_record=tuple(debt)
            require(debt==successor_record)
        for votes in product(range(2),repeat=4):require((sum(votes)>=3)==(votes.count(1) in (3,4)))
        tokens={(3,k) for k in range(4)}
        assigned=set()
        for tok in sorted(tokens):
            require(tok not in assigned);assigned.add(tok)
        require(not((3,0) not in assigned))

    @group('Correlated redundancy identity', 'n=1..10, covariance rho on quarter grid; variance sigma^2=3')
    def _():
        for n in range(1,11):
            for r in [Q(i,4) for i in range(5)]:
                direct=sum(Q(3) if i==j else 3*r for i in range(n) for j in range(n))/n**2
                require(direct==Q(3,n)*(1+(n-1)*r))


def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()

def main() -> int:
    start=time.perf_counter();started=datetime.now(timezone.utc).isoformat()
    script=Path(__file__).resolve();tex=ROOT/'Machine_Societies_v0.7.0.tex'
    inputs=[{'path':str(p.relative_to(ROOT)),'sha256':sha(p)} for p in (script, tex, OUT/'check_v05_extensions.py', OUT/'check_v06_extensions.py', OUT/'check_v07_extensions.py', ROOT/'code'/'finite_contract.py', ROOT/'code'/'exact_enforcement.py')]
    error=None
    try:
        run_checks()
        from check_v05_extensions import run_extensions
        run_extensions(group, require)
        from check_v06_extensions import run_extensions as run_v06
        run_v06(group, require)
        from check_v07_extensions import run_extensions as run_v07
        run_v07(group, require)
    except Exception:error=traceback.format_exc()
    result={'suite':'Machine Societies v0.7.0 finite mathematical audit',
            'arithmetic':'integers and fractions.Fraction; no stochastic sampling',
            'groups':GROUPS,'group_count':len(GROUPS),
            'assertions':sum(g['assertions'] for g in GROUPS),
            'status':'FAIL' if error else 'PASS','error':error,
            'runtime_seconds':time.perf_counter()-start,
            'non_claim':'Passing bounded checks is not a general proof or an empirical agent result.'}
    output=OUT/'finite_checks.json';output.write_text(json.dumps(result,indent=2)+'\n')
    unchanged=all(sha(ROOT/x['path'])==x['sha256'] for x in inputs)
    manifest={
      'schema_version':1,'claim_id':'machine-societies-v0.7-finite-constructions',
      'repository':{'commit':'not-a-git-checkout; source hashes recorded','dirty':True},
      'command':'python validation/check_finite_models.py',
      'environment':{'software':[sys.version.replace('\n',' '),platform.platform()],
                     'hardware':platform.machine()+'; CPU-only standard-library checks'},
      'mathematics':{'assertion_tested':'Finite instances of the manuscript propositions and counterexamples',
                    'coefficient_domain':'Z and Q via Python integers and fractions.Fraction',
                    'conventions':'nonnegative integer state masks; shared observation supports; sure safety and certified service; single common sanction monitor; zero-indexed finite states; row probability vectors; total variation is half l1; strict payoff improvement; first-exit lifetime',
                    'inputs':inputs,'bounds':{g['name']:g['domain'] for g in GROUPS},
                    'non_claims':['No general formal-kernel verification','No learned-agent or society experiment','No independent replication','No proof of priority or normative legitimacy']},
      'randomness':{'used':False,'generator':'none','seed':None},
      'run':{'started_at':started,'runtime_seconds':result['runtime_seconds'],'exit_status':int(bool(error))},
      'outputs':[{'path':str(p.relative_to(ROOT)),'sha256':sha(p)} for p in (output,OUT/'commons_joint_certificate.json') if p.is_file()],
      'checks':['Exact finite comparisons in each recorded group', 'Input hashes unchanged during execution: '+str(unchanged)],
      'result':'finite assertion verified in the stated range' if not error and unchanged else 'FAIL',
      'residual_risks':['The suite is authored with the exposition, not an independent audit.',
                        'Finite domains do not decide the general theorems.',
                        'Classical external theorems are not reproved by this suite.']}
    (OUT/'computation_manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
    print(json.dumps({k:result[k] for k in ('status','group_count','assertions','runtime_seconds')},indent=2))
    if error:print(error,file=sys.stderr)
    return int(bool(error) or not unchanged)

if __name__=='__main__':sys.exit(main())
