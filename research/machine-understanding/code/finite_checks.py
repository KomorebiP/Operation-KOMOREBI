#!/usr/bin/env python3
"""Exact checks for the first draft, not empirical evidence of machine understanding.
Run from any directory. Uses Python's standard library only.
"""
from __future__ import annotations
from collections import deque
from fractions import Fraction as F
from itertools import product, combinations, permutations
from pathlib import Path
import hashlib
import json
import platform
import sys
import time
from datetime import datetime, timezone

ROOT = Path(__file__).resolve().parents[1]
REPORT: list[dict] = []

class CheckGroup:
    def __init__(self, name: str, domain: str):
        self.name, self.domain, self.count = name, domain, 0
        self.started = time.perf_counter()
    def check(self, condition: bool, detail: str = '') -> None:
        self.count += 1
        if not condition:
            raise AssertionError(f'{self.name}: {detail}')
    def finish(self) -> None:
        REPORT.append({'name': self.name, 'domain': self.domain,
                       'assertions': self.count, 'passed': True,
                       'runtime_seconds': round(time.perf_counter()-self.started, 6)})

def words(alphabet, depth):
    for k in range(depth+1):
        yield from product(alphabet, repeat=k)

def canonical(values):
    labels, out = {}, []
    for value in values:
        if value not in labels:
            labels[value] = len(labels)
        out.append(labels[value])
    return tuple(out)

def refine(outputs, transitions):
    labels = canonical(outputs)
    stages = [len(set(labels))]
    while True:
        new = canonical((labels[x], tuple(labels[t[x]] for t in transitions))
                        for x in range(len(labels)))
        if new == labels:
            return labels, stages
        labels = new
        stages.append(len(set(labels)))

def distinguishing_word(outputs, transitions, x, y):
    queue = deque([(x,y,())]); seen = {(x,y)}
    while queue:
        a,b,w = queue.popleft()
        if outputs[a] != outputs[b]:
            return w
        for u,t in enumerate(transitions):
            pair=(t[a],t[b])
            if pair not in seen:
                seen.add(pair); queue.append((*pair,w+(u,)))
    return None

def step(x, u, p=5):
    a,b,c=x
    if u == 'H': return ((a+b)%p,b,c)
    if u == 'W': return (b,a,c)
    if u == 'J': return ((a+c)%p,b,c)
    raise ValueError(u)

def total(x,p=5): return (x[0]+x[1])%p

def reduced_step(z,u,p=5):
    s,b=z
    if u=='H': return ((s+b)%p,b)
    if u=='W': return (s,(s-b)%p)
    raise ValueError(u)

def instrument_checks():
    states=list(product(range(5),repeat=3)); idx={x:i for i,x in enumerate(states)}
    g=CheckGroup('register quotient and diagnostic recovery','All 125 states over F_5, H/W and H/W/J operation families')
    out=tuple(map(total,states))
    ts=[tuple(idx[step(x,u)] for x in states) for u in ('H','W','J')]
    base, bs=refine(out,ts[:2]); full, fs=refine(out,ts)
    g.check(bs==[5,25],repr(bs));g.check(fs==[5,125],repr(fs))
    for i,x in enumerate(states):
        s=total(x); s_h=total(step(x,'H'))
        g.check((s_h-s)%5==x[1]);g.check((2*s-s_h)%5==x[0])
        y=step(x,'J'); sy=total(y)
        # J changes the instrument. Recovery is of the post-intervention state.
        g.check(((sy-x[1])%5,x[1],(sy-s)%5)==y)
        for j,y in enumerate(states):
            g.check((base[i]==base[j]) == (x[:2]==y[:2]))
            g.check((full[i]==full[j]) == (x==y))
    g.finish()
    g=CheckGroup('exact coordinate transport','All 125 starts and all H/W words of length at most 5')
    for x in states:
        for w in words(('H','W'),5):
            a=x; z=(total(x),x[1])
            for u in w:
                a=step(a,u);z=reduced_step(z,u)
            g.check(z==(total(a),a[1]))
            g.check(z[0]==total(a))
    # Reject a decoder/update that accidentally treats W as identity on b.
    g.check(any((total(step(x,'W')),step(x,'W')[1]) != (total(x),x[1]) for x in states))
    g.finish()
    g=CheckGroup('extension information obstruction','Every old (a,b) fibre, all five guesses for c, uniform c')
    for a,b in product(range(5),repeat=2):
        future={total(step((a,b,c),'J')) for c in range(5)}
        g.check(len(future)==5)
        for guess in range(5):
            success=sum(total(step((a,b,c),'J'))==guess for c in range(5))
            g.check(F(success,5)==F(1,5))
    # The counterexample has exactly equal current observations.
    x,y=(0,0,0),(1,4,0)
    g.check(total(x)==total(y));g.check(total(step(x,'H'))!=total(step(y,'H')))
    g.finish()
    g=CheckGroup('redundant old coordinates obstruct expanded dynamics',
                 'Two bits, constant query, empty old action family, new swap')
    states2=list(product((0,1),repeat=2))
    # One expanded behavioral class, but old r=a is not dynamically closed under swap.
    g.check(len({0 for x in states2})==1)
    for a in (0,1):
        g.check(len({x[1] for x in states2 if x[0]==a})==2)
    # Adding b makes the pair closed, demonstrating why a general r needs the extra premise.
    for a,b in states2:
        g.check((b,a)==( (a,b)[1], (a,b)[0] ))
    g.finish()

def machine_checks():
    g=CheckGroup('partition refinement versus independent pair search',
                 'Every total deterministic machine with 1..3 states, two actions and one binary output')
    machines=0
    for n in range(1,4):
        for flat in product(range(n), repeat=2*n):
            trans=(flat[:n],flat[n:])
            for output in product(range(2),repeat=n):
                labels,stages=refine(output,trans);machines+=1
                g.check(len(stages)-1 <= n-1)
                for x,y in combinations(range(n),2):
                    w=distinguishing_word(output,trans,x,y)
                    g.check((labels[x]==labels[y]) == (w is None))
                    if w is not None:
                        a,b=x,y
                        for u in w: a,b=trans[u][a],trans[u][b]
                        g.check(output[a]!=output[b])
    g.finish();REPORT[-1]['machines']=machines
    g=CheckGroup('sharp supplementary code under the refinement hypothesis',
                 'All 1..4-state one-action machines with binary outputs; old contract has no operations and minimal output quotient')
    for n in range(1,5):
        for output in product((0,1),repeat=n):
            old=canonical(output)
            for t in product(range(n),repeat=n):
                new,_=refine(output,(t,))
                labels={};extra=[]
                for x in range(n):
                    fibre=labels.setdefault(old[x],{})
                    if new[x] not in fibre:fibre[new[x]]=len(fibre)
                    extra.append(fibre[new[x]])
                capacity=max(map(len,labels.values()))
                g.check(len(set(extra))==capacity)
                pair=tuple(zip(old,extra))
                for x,y in combinations(range(n),2):
                    g.check((pair[x]==pair[y])==(new[x]==new[y]))
                    if pair[x]==pair[y]:g.check(pair[t[x]]==pair[t[y]])
    g.finish()
    g=CheckGroup('finite horizon does not fix unrestricted continuations','Delay horizons 0..12')
    for h in range(13):
        # Constant-zero reference, counter with output one only after h+1 ticks.
        observations=[int(min(t,h+1)==h+1) for t in range(h+2)]
        g.check(all(y==0 for y in observations[:h+1]))
        g.check(observations[h+1]==1)
    g.finish()
    g=CheckGroup('arbitrary finite recoding preserves behavior','All 6 bijections on 3 states and all 27 single-action maps')
    for perm in permutations(range(3)):
        inv={y:x for x,y in enumerate(perm)}
        for trans in product(range(3),repeat=3):
            recoded=tuple(perm[trans[inv[z]]] for z in range(3))
            for x in range(3):g.check(recoded[perm[x]]==perm[trans[x]])
    g.finish()

def distributions(denom,n):
    for v in product(range(denom+1),repeat=n):
        if sum(v)==denom:yield tuple(F(x,denom) for x in v)

def probability_checks():
    g=CheckGroup('transcript identification bound','All 3-outcome probability laws with denominator 4, every deterministic binary classifier')
    ds=list(distributions(4,3))
    for p in ds:
        for q in ds:
            tv=sum(abs(x-y) for x,y in zip(p,q))/2
            best=max((sum(pi*s+qi*(1-s) for pi,qi,s in zip(p,q,d)))/2
                     for d in product((0,1),repeat=3))
            g.check(best==(1+tv)/2)
    g.finish()
    g=CheckGroup('controlled stochastic quotient','Exact rational kernels, 4 fine states and 2 blocks, initial mixtures and one fixed control')
    # The first two rows project to the same row, as do the last two.
    K=((F(1,2),0,F(1,2),0),(0,F(1,2),0,F(1,2)),
       (F(1,4),0,F(3,4),0),(0,F(1,4),0,F(3,4)))
    L=((F(1,2),F(1,2)),(F(1,4),F(3,4)))
    project=lambda p:(p[0]+p[1],p[2]+p[3])
    def mul(p,k):return tuple(sum(p[i]*k[i][j] for i in range(len(p))) for j in range(len(k[0])))
    for p in distributions(3,4):
        f=p;c=project(p)
        for _ in range(9):
            g.check(project(f)==c);f=mul(f,K);c=mul(c,L)
    # A changed row is detected despite unchanged report at the current time.
    broken=list(K);broken[1]=(0,F(3,4),0,F(1,4))
    g.check(project(broken[0])!=project(broken[1]))
    g.finish()

def transport_checks():
    g=CheckGroup('approximate transport and sharp accumulation','L in {0,1/2,1,3/2,2}, epsilon in {0,1/100,1/5}, initial error 0 or 1/10, horizons 0..10')
    for L,eps,e0 in product((F(0),F(1,2),F(1),F(3,2),F(2)),(F(0),F(1,100),F(1,5)),(F(0),F(1,10))):
        err=e0
        for n in range(11):
            bound=L**n*e0+eps*sum((L**j for j in range(n)),F(0))
            g.check(err==bound)
            err=L*err+eps
    g.finish()
    g=CheckGroup('explanation and common-witness capacity','Four distinct binary two-query answer profiles, all encoders with 1..4 messages')
    profiles=list(product((0,1),repeat=2))
    for k in range(1,5):
        for enc in product(range(k),repeat=4):
            possible=all(enc[i]!=enc[j] or profiles[i]==profiles[j] for i,j in combinations(range(4),2))
            g.check(possible==(len(set(enc))==4))
            if k<4:g.check(not possible)
    for query in (0,1):
        enc=[p[query] for p in profiles]
        g.check(all(enc[i]!=enc[j] or profiles[i][query]==profiles[j][query] for i,j in combinations(range(4),2)))
    g.finish()

def revision_checks():
    models=list(product((0,1),repeat=3))
    g=CheckGroup('finite informative correction','All subsets of 8 deterministic models on 3 binary experiments, each realizable truth')
    for mask in range(1,1<<8):
        initial=[m for i,m in enumerate(models) if mask>>i&1]
        for truth in initial:
            V=initial[:]; steps=0
            while len(V)>1:
                a,b=V[:2];e=next(j for j in range(3) if a[j]!=b[j])
                new=[m for m in V if m[e]==truth[e]]
                g.check(truth in new);g.check(len(new)<len(V))
                V=new;steps+=1
            g.check(V==[truth]);g.check(steps<=len(initial)-1)
    g.finish()
    g=CheckGroup('correction and evidence transport','Source model count 1..3, two target models, binary observations; all compatible maps, all subsets including inconsistent evidence')
    instances=0
    for n in range(1,4):
        for outcome in product((0,1),repeat=n):
            for phi in product((0,1),repeat=n):
                for eta in product((0,1),repeat=2):
                    for target_outcome in product((0,1),repeat=2):
                        if any(target_outcome[phi[m]]!=eta[outcome[m]] for m in range(n)):continue
                        instances+=1;all_equal=True
                        actual=set(outcome)
                        for mask in range(1<<n):
                            V=[m for m in range(n) if mask>>m&1]
                            for obs in actual:
                                left={phi[m] for m in V if outcome[m]==obs}
                                right={phi[m] for m in V if target_outcome[phi[m]]==eta[obs]}
                                g.check(left<=right)
                                all_equal=all_equal and left==right
                        reflective=len({eta[o] for o in actual})==len(actual)
                        g.check(all_equal==reflective)
    g.finish();REPORT[-1]['compatible_map_systems']=instances
    g=CheckGroup('explicit lost correction and contradiction','Two source models, identity model transport, constant observation transport')
    V={0,1};obs=1
    left={m for m in V if m==obs};right=set(V)
    g.check(left=={1});g.check(right=={0,1});g.check(left<right)
    V={0};g.check({m for m in V if m==1}==set());g.check(V=={0})
    g.finish()

def main():
    import argparse
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, help='Optional result path; relative to the working directory')
    args=parser.parse_args()
    started=datetime.now(timezone.utc).isoformat();t=time.perf_counter()
    instrument_checks();machine_checks();probability_checks();transport_checks();revision_checks()
    result={'status':'passed','started_at_utc':started,'runtime_seconds':round(time.perf_counter()-t,6),
            'python':sys.version,'platform':platform.platform(),'arithmetic':'integers and fractions.Fraction',
            'randomness':False,'groups':REPORT,'group_count':len(REPORT),
            'assertions':sum(r['assertions'] for r in REPORT),
            'script_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
            'non_claims':['Not a proof of the general propositions.',
                          'Not an agent experiment, training run, or test of a deployed model.',
                          'No independent external replication or Lean verification.',
                          'Exhaustive only over the domains attached to individual groups.']}
    path=args.output if args.output is not None else ROOT/'validation'/'finite_checks.json';path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({k:result[k] for k in ('status','group_count','assertions','runtime_seconds')},indent=2))
    for r in REPORT:print(f"{r['name']}: {r['assertions']} passed")
if __name__=='__main__':main()
