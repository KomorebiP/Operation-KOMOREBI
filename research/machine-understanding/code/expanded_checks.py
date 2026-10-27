#!/usr/bin/env python3
"""Exact bounded tests of the v0.5 additions; no training or agent experiments."""
from __future__ import annotations
from collections import defaultdict
from datetime import datetime, timezone
from fractions import Fraction as F
from itertools import product, combinations
from pathlib import Path
import argparse, hashlib, json, platform, sys, time
from understanding import (channel, compose, posterior, reconstruct_channel, tv,
                           explanation_graph, color_graph, chromatic_number,
                           Experiment, acquisition, policy_trace)
ROOT = Path(__file__).resolve().parents[1]
REPORT = []
class Group:
    def __init__(self, name, domain):
        self.name, self.domain, self.count = name, domain, 0
        self.started = time.perf_counter()
    def check(self, condition, detail=''):
        self.count += 1
        if not condition: raise AssertionError(f'{self.name}: {detail}')
    def finish(self):
        REPORT.append(dict(name=self.name, domain=self.domain, assertions=self.count,
                           passed=True, runtime_seconds=round(time.perf_counter()-self.started,6)))

def simplex(n, den):
    return [tuple(F(x,den) for x in xs) for xs in product(range(den+1),repeat=n) if sum(xs)==den]

def log_vector(q):
    # Exact formal representation log(q)=sum_p exponent_p log(p).
    out=defaultdict(F)
    for value,sign in ((q.numerator,1),(q.denominator,-1)):
        d=2
        while d*d<=value:
            while value%d==0:
                out[d]+=sign; value//=d
            d+=1
        if value>1:out[value]+=sign
    return {p:c for p,c in out.items() if c}

def add_log(acc, weight, ratio):
    if not weight: return
    if ratio<=0:raise ValueError('A positive-weight logarithm must have positive argument.')
    for p,c in log_vector(ratio).items():acc[p]+=weight*c

def clean(d):return {k:v for k,v in d.items() if v}

def bayes_checks():
    g=Group('all-prior Bayesian sufficiency and stochastic reporting',
            '2 models, 3 observations; row probabilities in halves; all 3-by-2 reporting channels in halves; binary priors in quarters')
    channels = [channel(rows) for rows in product(simplex(2,2),repeat=3)]
    for rows in product(simplex(3,2),repeat=2):
        L=channel(rows)
        for B in channels:
            Q=compose(L,B); rho=reconstruct_channel(L,B)
            all_equal=True
            for p in simplex(2,4):
                zprobs=[sum(p[m]*Q[m][z] for m in range(2)) for z in range(2)]
                for z in range(2):
                    coarse=posterior(p,[Q[m][z] for m in range(2)])
                    if coarse is None: continue
                    mixture=[F(0),F(0)]
                    for o in range(3):
                        mass=sum(p[m]*L[m][o]*B[o][z] for m in range(2))
                        if mass==0:continue
                        fine=posterior(p,[L[m][o] for m in range(2)])
                        all_equal=all_equal and fine==coarse
                        if rho is not None:g.check(fine==coarse)
                        for m in range(2):mixture[m]+=mass/zprobs[z]*fine[m]
                    g.check(tuple(mixture)==coarse,'Coarse posterior is a posterior mixture')
            g.check(all_equal==(rho is not None))
    g.finish()
    g=Group('posterior information loss identity without floating logarithms',
            'All 2-model, 3-outcome likelihoods in halves; deterministic 3-to-2 reports; uniform prior; symbolic rational coefficients of prime logarithms')
    for rows in product(simplex(3,2),repeat=2):
        L=channel(rows);p=(F(1,2),F(1,2))
        for eta in product(range(2),repeat=3):
            B=channel([[int(z==eta[o]) for z in range(2)] for o in range(3)])
            Q=compose(L,B)
            direct,chain=defaultdict(F),defaultdict(F)
            for o in range(3):
                po=sum(p[m]*L[m][o] for m in range(2))
                if not po:continue
                z=eta[o]; pz=sum(p[m]*Q[m][z] for m in range(2))
                for m in range(2):
                    mass=p[m]*L[m][o]
                    if not mass:continue
                    add_log(direct,mass,(L[m][o]/po)/(Q[m][z]/pz))
                    add_log(chain,mass,L[m][o]/po)
            for z in range(2):
                pz=sum(p[m]*Q[m][z] for m in range(2))
                if not pz:continue
                for m in range(2):
                    mass=p[m]*Q[m][z]
                    if mass:add_log(chain,-mass,Q[m][z]/pz)
            g.check(clean(direct)==clean(chain))
    g.finish()
    g=Group('conditional stability and rare-evidence counterexample',
            'All pairs of 4-cell joint laws in quarters; events selecting either observation of a 2-by-2 model/outcome space; rare same-prior examples')
    for P in simplex(4,4):
        for Q in simplex(4,4):
            delta=tv(P,Q)
            for o in range(2):
                u=(P[o],P[2+o]);v=(Q[o],Q[2+o]);a=sum(u);b=sum(v)
                if a and b:
                    cond=tv(tuple(x/a for x in u),tuple(x/b for x in v))
                    g.check(cond<=min(F(1),delta/max(a,b)))
    for d in (8,16,32,64):
        e=F(1,d)
        P=(e,F(1,2)-e,F(0),F(1,2));Q=(F(0),F(1,2),e,F(1,2)-e)
        g.check(tv(P,Q)==2*e)
        g.check(tv((F(1),F(0)),(F(0),F(1)))==1)
    g.finish()
    g=Group('bounded-loss recipient decision certificate',
            'Binary source, approximate and recipient posteriors in quarters; all two-action 0/1 loss tables')
    laws=simplex(2,4)
    for p,q,r in product(laws,repeat=3):
        e=tv(p,q)+tv(q,r)
        for raw in product((0,1),repeat=4):
            losses=(raw[:2],raw[2:]); risk=lambda law,a:sum(law[m]*losses[a][m] for m in range(2))
            a=min(range(2),key=lambda a:risk(r,a))
            regret=risk(p,a)-min(risk(p,b) for b in range(2))
            g.check(regret<=min(F(1),2*e))
            gap=risk(r,1-a)-risk(r,a)
            if gap>2*e:g.check(risk(p,a)<risk(p,1-a))
    g.finish()


def sequential_checks():
    g=Group('sequential noisy correction under a declared adaptive policy',
            '2 models; 2 likelihood experiments; 4 raw outcomes with ancillary flag; horizons 0..4; 3 positive priors; all raw histories')
    kernels=[]
    for accuracy in (F(3,4),F(2,3)):
        kernels.append(channel([[((accuracy if signal==m else 1-accuracy)*flag)
                                 for signal in range(2) for flag in (F(1,3),F(2,3))]
                                for m in range(2)]))
    B=channel([[int(z==o//2) for z in range(2)] for o in range(4)])
    coarse=[compose(L,B) for L in kernels]
    for p0 in (F(1,5),F(1,2),F(4,5)):
        for h in range(5):
            for hist in product(range(4),repeat=h):
                full=(p0,1-p0);reduced=full;zs=[]
                for o in hist:
                    e=sum(zs)%2;z=o//2
                    full=posterior(full,[kernels[e][m][o] for m in range(2)])
                    reduced=posterior(reduced,[coarse[e][m][z] for m in range(2)])
                    zs.append(z);g.check(full==reduced)
    g.finish()
    g=Group('noise, ancillary flags and repeated-readout instrument',
            '5 candidate values of c; correct-read probability 3/4; other values 1/16 each; up to 6 repeated identical reports; exact finite priors')
    L=channel([[F(3,4) if c==y else F(1,16) for y in range(5)] for c in range(5)])
    prior=tuple([F(1,5)]*5)
    raw=channel([[L[c][y]*flag for y in range(5) for flag in (F(1,3),F(2,3))] for c in range(5)])
    keep=channel([[int(z==o//2) for z in range(5)] for o in range(10)])
    g.check(reconstruct_channel(raw,keep) is not None)
    parity=channel([[int(z==y%2) for z in range(2)] for y in range(5)])
    g.check(reconstruct_channel(L,parity) is None)
    reduced=compose(L,parity)
    for n in range(7):
        full=posterior(prior,[L[c][2]**n for c in range(5)])
        co=posterior(prior,[reduced[c][0]**n for c in range(5)])
        g.check(full[2]==F(12**n,12**n+4))
        g.check(co[2]==F(14**n,3*14**n+2*3**n))
        if n>0:g.check(full[2]>co[2])
    g.check(posterior(prior,[L[c][2]**3 for c in range(5)])[2]==F(432,433))
    # Copying one record does not produce a conditionally independent sample.
    p=(F(1,2),F(1,2));ell=(F(1,5),F(4,5))
    single=posterior(p,ell);fake_repeat=posterior(p,[v*v for v in ell])
    g.check(single[1]==F(4,5));g.check(fake_repeat[1]==F(16,17));g.check(single!=fake_repeat)
    g.finish()


def direct_decodable(sender, backgrounds, demands, encoding):
    for b,d in zip(backgrounds,demands):
        table={}
        for m in range(len(sender)):
            key=(encoding[sender[m]],b[m])
            if key in table and table[key]!=d[m]:return False
            table[key]=d[m]
    return True

def graph_checks():
    g=Group('source-access explanation graphs against direct decodability',
            'All 64 simple graphs on 4 cases represented by pairwise-confusable recipients; all binary sender-access maps; all encodings with 1..3 symbols')
    pairs=list(combinations(range(4),2))
    for mask in range(1<<len(pairs)):
        selected=[e for j,e in enumerate(pairs) if mask>>j&1]
        bs=[];ds=[]
        for a,b in selected:
            bs.append(tuple(-1 if m in (a,b) else m for m in range(4)))
            ds.append(tuple(int(m==b) for m in range(4)))
        # A recipient with no demands is permitted even for an empty graph.
        if not bs:bs=[tuple(range(4))];ds=[(0,0,0,0)]
        for send in product(range(2),repeat=4):
            verts,edges=explanation_graph(send,bs,ds)
            for k in range(1,4):
                exists=False
                for enc in product(range(k),repeat=2):
                    dec=direct_decodable(send,bs,ds,enc)
                    graph_ok=all(enc[verts[a]]!=enc[verts[b]] for a,b in edges)
                    g.check(dec==graph_ok)
                    exists=exists or dec
                g.check(exists==(color_graph(len(verts),edges,k) is not None))
    g.finish()
    g=Group('heterogeneous recipients and shared-message obstructions',
            'Five-cycle recipients, XOR side information, and a deliberately hidden sender distinction')
    bs=[];ds=[]
    for i in range(5):
        j=(i+1)%5
        bs.append(tuple(-1 if m in (i,j) else m for m in range(5)))
        ds.append(tuple(int(m==j) for m in range(5)))
        vs,es=explanation_graph(tuple(range(5)),[bs[-1]],[ds[-1]])
        g.check(chromatic_number(len(vs),es)==2)
    vs,es=explanation_graph(tuple(range(5)),bs,ds)
    g.check(chromatic_number(len(vs),es)==3)
    ab=list(product(range(2),repeat=2));send=tuple(a^b for a,b in ab)
    bs=[tuple(a for a,b in ab),tuple(b for a,b in ab)]
    ds=[tuple(b for a,b in ab),tuple(a for a,b in ab)]
    vs,es=explanation_graph(send,bs,ds);g.check(chromatic_number(len(vs),es)==2)
    g.check(direct_decodable(send,bs,ds,(0,1)))
    vs,es=explanation_graph((0,0),[(0,0)],[(0,1)])
    g.check((0,0) in es);g.check(chromatic_number(len(vs),es) is None)
    g.finish()


def brute_policy_cost(target, experiments, initial, horizon):
    # Independently enumerate all full binary-history policies. Recompute each
    # history's possible current states by replay from the initial states.
    histories=[w for h in range(horizon) for w in product(range(2),repeat=h)]
    best=None
    for raw in product(range(len(experiments)),repeat=len(histories)):
        plan=dict(zip(histories,raw));costs=[];valid=True
        for truth in initial:
            hist=();x=truth;cost=F(0)
            while True:
                possible=[]
                for old in initial:
                    z=old;seen=();consistent=True
                    for observed in hist:
                        ex=experiments[plan[seen]]
                        if ex.outcome[z]!=observed:consistent=False;break
                        z=ex.next_state[z];seen+=(observed,)
                    if consistent:possible.append(z)
                if len({target[z] for z in possible})==1:costs.append(cost);break
                if len(hist)==horizon:valid=False;break
                ex=experiments[plan[hist]]
                if ex.allowed is not None and any(not ex.allowed[z] for z in possible):valid=False;break
                observed=ex.outcome[x];x=ex.next_state[x];hist+=(observed,);cost+=ex.cost
            if not valid:break
        if valid:
            worst=max(costs)
            best=worst if best is None else min(best,worst)
    return best

def acquisition_checks():
    g=Group('acquisition Bellman values versus full policy enumeration',
            'All ordered pairs of 16 binary-state deterministic experiments (all transitions and observations); all 3 initial supports; horizon 2; costs 1 and 2')
    actions=[(t,o) for t in product(range(2),repeat=2) for o in product(range(2),repeat=2)]
    for a,b in product(actions,repeat=2):
        es=[Experiment('first',a[0],a[1],F(1)),Experiment('second',b[0],b[1],F(2))]
        for initial in (frozenset([0]),frozenset([1]),frozenset([0,1])):
            value,witness=acquisition((0,1),es,initial,2)
            brute=brute_policy_cost((0,1),es,initial,2)
            g.check(value==brute)
            if value is not None:
                outcomes=[policy_trace(x,witness,es) for x in initial]
                g.check(max(cost for _,cost,_ in outcomes)==value)
                g.check(all(depth<=2 for _,_,depth in outcomes))
    g.finish()
    g=Group('current-state knowledge versus preserved origin information',
            'Two states with one resetting experiment, tagged initial/current product, horizons 0..4; admissibility negative control')
    reset=[Experiment('reset',(0,0),(0,0))]
    for h in range(5):
        cost,_=acquisition((0,1),reset,frozenset([0,1]),h)
        g.check(cost==(None if h==0 else F(1)))
    pairs=list(product(range(2),repeat=2));index={p:i for i,p in enumerate(pairs)}
    tagged=[Experiment('reset',tuple(index[(origin,0)] for origin,current in pairs),(0,0,0,0))]
    for h in range(5):
        cost,_=acquisition(tuple(a for a,b in pairs),tagged,frozenset([index[(0,0)],index[(1,1)]]),h)
        g.check(cost is None)
    es=[Experiment('forbidden distinction',(0,1),(0,1),allowed=(True,False))]
    g.check(acquisition((0,1),es,frozenset([0,1]),2)[0] is None)
    g.finish()
    g=Group('instrument acquisition includes its physical update',
            'All 25 base-record fibres, 125 complete states, J diagnostic cost 2, H/W cost 1, horizon 2')
    states=list(product(range(5),repeat=3));idx={x:i for i,x in enumerate(states)}
    def step(x,u):
        a,b,c=x
        if u=='H':return ((a+b)%5,b,c)
        if u=='W':return (b,a,c)
        return ((a+c)%5,b,c)
    es=[]
    for u in ('H','W','J'):
        ys=[step(x,u) for x in states]
        es.append(Experiment(u,tuple(idx[y] for y in ys),tuple((y[0]+y[1])%5 for y in ys),F(2 if u=='J' else 1)))
    for a,b in product(range(5),repeat=2):
        initial=frozenset(idx[(a,b,c)] for c in range(5))
        value,w=acquisition(tuple(states),es,initial,2)
        g.check(value==2)
        g.check(w['name']=='J')
        for x in initial:
            final,cost,depth=policy_trace(x,w,es)
            g.check(states[final]==step(states[x],'J'))
            g.check((cost,depth)==(F(2),1))
    g.finish()
    g=Group('joint acquisition and explanation without source reconstruction',
            'Binary register pairs; source only observes parity; two recipients know opposite bits; horizons 0..3 and shared artifact bounds 1..2')
    ab=list(product(range(2),repeat=2));read=[Experiment('parity',tuple(range(4)),tuple(a^b for a,b in ab))]
    initial=frozenset(range(4))
    for h in range(4):g.check(acquisition(tuple(ab),read,initial,h)[0] is None)
    bs=[tuple(a for a,b in ab),tuple(b for a,b in ab)];ds=[tuple(b for a,b in ab),tuple(a for a,b in ab)]
    for measured in (False,True):
        leaves=tuple(a^b for a,b in ab) if measured else (0,0,0,0)
        vs,es=explanation_graph(leaves,bs,ds)
        g.check((chromatic_number(len(vs),es)==2) if measured else chromatic_number(len(vs),es) is None)
    g.finish()
    g=Group('public API rejects malformed probability and acquisition contracts',
            'Invalid distribution sums, negative likelihoods, dimensional mismatch, invalid transitions, empty support, negative horizon')
    calls=[lambda:channel([[F(1,3),F(1,3)]]),lambda:posterior((F(1),),(-1,)),
           lambda:compose(channel([[F(1)]]),channel([[F(1)],[F(1)]])),
           lambda:acquisition((0,1),[Experiment('bad',(0,2),(0,1))],frozenset([0,1]),1),
           lambda:acquisition((0,1),[],frozenset(),1),
           lambda:acquisition((0,1),[],frozenset([0]),-1)]
    for call in calls:
        try:call()
        except ValueError:g.check(True)
        else:g.check(False,'Invalid input was accepted')
    g.finish()

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output',type=Path,default=ROOT/'validation'/'expanded_checks.json')
    args=parser.parse_args();started=datetime.now(timezone.utc).isoformat();t=time.perf_counter()
    bayes_checks();sequential_checks();graph_checks();acquisition_checks()
    result=dict(status='passed',started_at_utc=started,runtime_seconds=round(time.perf_counter()-t,6),
                arithmetic='exact integers, fractions.Fraction, formal rational coefficients of prime logarithms',
                python=sys.version,platform=platform.platform(),randomness=False,
                groups=REPORT,group_count=len(REPORT),assertions=sum(r['assertions'] for r in REPORT),
                script_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
                non_claims=['Not universal proofs or empirical agent experiments.',
                            'Cross-check algorithms are project-authored, not independent external replication.',
                            'No verification of unspecified learners, likelihoods or recipient cognition.'])
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({k:result[k] for k in ('status','group_count','assertions','runtime_seconds')},indent=2))
    for r in REPORT:print(f"{r['name']}: {r['assertions']} passed")
if __name__=='__main__':main()
