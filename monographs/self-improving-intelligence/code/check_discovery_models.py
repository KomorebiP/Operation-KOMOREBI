#!/usr/bin/env python3
"""Exact, bounded checks for v0.2. No statistical sampling or agent training."""
from pathlib import Path
from fractions import Fraction as Q
from itertools import product
import json, time
from compiler_improvement import (compile_measured, immutable_binary_guard,
    metered_problem, Meter, tagged_problem, orientation_family, evidence_step)
from repair_calculus import (Problem, Experiment, Repair, Tree, cell_problem,
    relabel_problem, check_tree, tree_from_dict, tree_to_dict)
ROOT=Path(__file__).resolve().parents[1]
GROUPS=[]
COUNT=0

def check(condition, message='finite assertion failed'):
    global COUNT
    COUNT += 1
    if not condition:
        raise AssertionError(message)

def group(name, domain):
    def decorate(f):
        before=COUNT;t=time.perf_counter();f()
        GROUPS.append({'name':name,'domain':domain,'assertions':COUNT-before,
                       'seconds':time.perf_counter()-t,'status':'PASS'})
        return f
    return decorate

def costs(front):
    return {(w.work,w.storage) for w in front}

@group('guarded compiler agrees with exhaustive synthesis',
       'Every pair of total binary immutable query tables on n=1,2,3,4 states, horizon ceil(log2 n), both proposal rules.')
def all_small():
    for n in range(1,5):
        reps=tuple(Repair(str(i),Q(1),frozenset((i,))) for i in range(n))
        for bits in product((0,1),repeat=2*n):
            exps=tuple(Experiment(f'e{j}',Q(1),tuple((x,bits[j*n+x]) for x in range(n))) for j in (0,1))
            p=Problem(n,exps,reps);h=(n-1).bit_length()
            base,_=compile_measured(p,h)
            for rule in ('first','balanced'):
                child,r=compile_measured(p,h,rule)
                check(costs(child)==costs(base))
                for w in child:
                    check(check_tree(p,range(n),w.tree,h)==(w.work,w.storage))
                check(r['status']=='complete')

@group('scope failures cannot authorize a shortcut',
       'Each of 24 query entries of the n=4, q=6 model changed to a destructive transition, nonbinary report, or inadmissible action; horizon 2.')
def guard_failures():
    p0=cell_problem(4)
    for ei in range(len(p0.experiments)):
        for x in range(4):
            for bad in (None,((x+1)%4,0),(x,2)):
                exps=list(p0.experiments);e=exps[ei];rows=list(e.transitions);rows[x]=bad
                exps[ei]=Experiment(e.name,e.cost,tuple(rows));p=Problem(4,tuple(exps),p0.repairs)
                a,_=compile_measured(p,2);b,r=compile_measured(p,2,'balanced')
                check(r['mode']=='fallback');check(costs(a)==costs(b))
    for repairs in ((Repair('all',Q(1),frozenset(range(4))),),
                    tuple(Repair(r.name,Q(2),r.good) for r in p0.repairs)):
        p=Problem(4,p0.experiments,repairs);a,_=compile_measured(p,2);b,r=compile_measured(p,2,'balanced')
        check(r['mode']=='fallback');check(costs(a)==costs(b))

@group('binary family bounds and charged model reads',
       'n=2,4,8,16,32,64 with n+log2(n) queries, all initial states; parent comparison executed only through n=16.')
def family():
    for k in range(1,7):
        n=2**k;p=cell_problem(n);front,r=compile_measured(p,k,'balanced')
        check(r['mode']=='certified_shortcut');check(costs(front)=={(Q(k+1),2*n-1)})
        check(r['table_reads']==n*(n+k)*(k+1)+2*n*k)
        check(r['phase_reads']['guard']==n*(n+k))
        check(r['phase_reads']['proposal']==n*(n+k)*k)
        check(r['phase_reads']['verification']==2*n*k)
        if n<=16:
            base,br=compile_measured(p,k);check(costs(base)==costs(front))
            check(br['table_reads']>=r['table_reads'])

@group('fresh relabelings and report flips',
       'All 32 affine permutations modulo 8, eight patterned binary report flips, reversed operation order; 256 cold-start compilations.')
def relabelings():
    p0=cell_problem(8)
    for a in (1,3,5,7):
        for b in range(8):
            sigma=tuple((a*x+b)%8 for x in range(8))
            for mask in range(8):
                flips=tuple((mask>>(i%3))&1 for i in range(11))
                pp=relabel_problem(p0,sigma,flips)
                p=Problem(8,tuple(reversed(pp.experiments)),pp.repairs)
                fs,r=compile_measured(p,3,'balanced')
                check(r['mode']=='certified_shortcut');check(costs(fs)=={(Q(4),15)})
                check(r['table_reads']==400)
                for w in fs:check(check_tree(p,range(8),w.tree,3)==(w.work,w.storage))

@group('frozen finite method selector',
       'Rules none/first/balanced selected by total table reads on n=4 and n=8; tested unchanged on cold n=16.')
def selection():
    rules=(None,'first','balanced');scores={}
    for rule in rules:
        scores[str(rule)]=sum(compile_measured(cell_problem(n),n.bit_length()-1,rule)[1]['table_reads'] for n in (4,8))
    check(scores=={'None':10256,'first':10380,'balanced':488})
    chosen=min(rules,key=lambda r:scores[str(r)])
    check(chosen=='balanced')
    a,ar=compile_measured(cell_problem(16),4)
    b,br=compile_measured(cell_problem(16),4,chosen)
    check(costs(a)==costs(b));check(ar['table_reads']==576128);check(br['table_reads']==1728)

@group('common hard allowance and incomplete search semantics',
       'Cold n=16, common table-read cap 2000, and caps 0,1,1727,1728 for the shortcut.')
def allowances():
    a,ar=compile_measured(cell_problem(16),4,read_limit=2000)
    b,br=compile_measured(cell_problem(16),4,'balanced',read_limit=2000)
    check(not a and ar['status']=='incomplete' and ar['table_reads']==2000)
    check(costs(b)=={(Q(5),31)} and br['status']=='complete')
    for cap in (0,1,1727,1728):
        _,r=compile_measured(cell_problem(16),4,'balanced',read_limit=cap)
        check(r['status']==('complete' if cap==1728 else 'incomplete'))
        check(r['table_reads']<=cap)

@group('fallback can cost more than the incumbent',
       'Equality-only n=4, horizon 3; binary family n=4 with equality-first candidate; non-power-of-two support of six cells.')
def fallback():
    p=cell_problem(4,bits=False)
    a,ar=compile_measured(p,3);b,br=compile_measured(p,3,'balanced')
    check(costs(a)==costs(b));check(br['mode']=='fallback');check(br['table_reads']>ar['table_reads'])
    p=cell_problem(8)
    a,_=compile_measured(p,3,support=range(6));b,br=compile_measured(p,3,'balanced',support=range(6))
    check(costs(a)==costs(b));check(costs(b)=={(Q(4),11)})

@group('unknown sensor orientation and informative calibration',
       'Two fixed orientation models, both hidden physical states, horizons 0 through 5, reference cost 2 and sense cost 1.')
def orientation():
    for cal in (False,True):
        models=orientation_family(cal);p=tagged_problem(models)
        for h in range(6):
            f,r=compile_measured(p,h,'balanced')
            check(costs(f)==({(Q(4),7)} if cal and h>=2 else set()))
            for w in f:
                check(check_tree(p,range(4),w.tree,h)==(w.work,w.storage))
        for model in models:
            f,_=compile_measured(model,1);check(costs(f)=={(Q(2),3)})

@group('tagged model immutability and model-specific domains',
       'Every pair of partial deterministic binary state/report tables on two states for one experiment, including all valid origins and transitions.')
def product_semantics():
    entries=(None,(0,0),(0,1),(1,0),(1,1))
    reps=(Repair('r0',Q(1),frozenset((0,))),Repair('r1',Q(1),frozenset((1,))))
    for rows in product(entries,repeat=4):
        models=tuple(Problem(2,(Experiment('e',Q(1),tuple(rows[2*t:2*t+2])),),reps) for t in (0,1))
        p=tagged_problem(models)
        for theta in (0,1):
            for x in (0,1):
                out=p.experiments[0].transitions[2*theta+x]
                original=models[theta].experiments[0].transitions[x]
                check(out==(None if original is None else (2*theta+original[0],original[1])))
                if out is not None:check(out[0]//2==theta)
        for ri in (0,1):
            check(p.repairs[ri].good==frozenset((ri,2+ri)))

@group('sequential evidence has nonpositive null drift',
       'All probability triples with denominator 4 on scores -1,0,1; gamma=0,1/3,1/2; four permitted rational bet fractions.')
def null_drift():
    for gamma in (Q(0),Q(1,3),Q(1,2)):
        for a in range(5):
            for b in range(5-a):
                probs=(Q(a,4),Q(b,4),Q(4-a-b,4));mean=sum(p*y for p,y in zip(probs,(-1,0,1)))
                if mean>gamma:continue
                for fraction in (Q(0),Q(1,4),Q(1,2),Q(1)):
                    bet=fraction/(1+gamma)
                    vals=[evidence_step(Q(1),Q(y),bet,gamma) for y in (-1,0,1)]
                    check(min(vals)>=0);check(sum(p*v for p,v in zip(probs,vals))<=1)

def crossing_probability(gamma,delta,depth,rule):
    hit=Q(0)
    p=(1+gamma)/2
    def visit(capital,prob,history):
        nonlocal hit
        if capital>=1/delta:
            hit+=prob;return
        if len(history)==depth:return
        factor=(Q(1,2) if rule==0 else (Q(1) if not history or history[-1]>0 else Q(1,4)))
        bet=factor/(1+gamma)
        for y,py in ((Q(1),p),(Q(-1),1-p)):
            visit(evidence_step(capital,y,bet,gamma),prob*py,history+(y,))
    visit(Q(1),Q(1),())
    return hit

@group('anytime threshold across exact null paths',
       'All binary histories through length 10, null means gamma=0,1/3,1/2, thresholds delta=1/2,1/4,1/8, two predictable bet rules.')
def optional_stopping():
    for gamma,delta,rule in product((Q(0),Q(1,3),Q(1,2)),(Q(1,2),Q(1,4),Q(1,8)),(0,1)):
        previous=Q(0)
        for depth in range(11):
            prob=crossing_probability(gamma,delta,depth,rule)
            check(previous<=prob<=delta);previous=prob

@group('outcome-dependent bets are an invalid audit',
       'Four fair binary observations; choosing bet after the current score yields crossing probability 11/16 at threshold 4.')
def hindsight_bet():
    total=Q(0)
    for ys in product((-1,1),repeat=4):
        cap=Q(1);hit=False
        for y in ys:
            cap=evidence_step(cap,Q(y),Q(1 if y==1 else 0))
            hit |= cap>=4
        if hit:total+=Q(1,16)
    check(total==Q(11,16));check(total>Q(1,4))

@group('typed evidence update rejects invalid parameters',
       'Negative capital; out-of-range score, gamma or bet; boundary zero capital and maximal permitted bet.')
def invalid_evidence():
    for args in ((Q(-1),Q(0),Q(0),Q(0)),(Q(1),Q(2),Q(0),Q(0)),
                 (Q(1),Q(0),Q(-1),Q(0)),(Q(1),Q(0),Q(1),Q(1,2)),
                 (Q(1),Q(0),Q(0),Q(1))):
        try:evidence_step(*args)
        except ValueError:check(True)
        else:check(False)
    check(evidence_step(Q(0),Q(1),Q(1))==0)
    check(evidence_step(Q(1),Q(-1),Q(2,3),Q(1,2))==0)

@group('equal-quantum racing bound',
       'Abstract resumable worker completion times 1 through 40 in either slot, plus a nonterminating competitor; dispatch overhead 0,1,2.')
def racing():
    for a in range(1,41):
        for b in list(range(1,41))+[None]:
            executed=0;done=[0,0]
            while True:
                i=executed%2;done[i]+=1;executed+=1
                if done[0]>=a or (b is not None and done[1]>=b):break
            shortest=a if b is None else min(a,b)
            check(executed<=2*shortest)
            for overhead in (0,1,2):check((1+overhead)*executed<=2*(1+overhead)*shortest)

@group('every table row can be decisive for a universal scope audit',
       'All 24 entries of n=4,q=6 changed in turn to report 2; an auditor skipping that entry cannot distinguish the histories.')
def read_floor():
    p=cell_problem(4);flat=tuple(v for e in p.experiments for v in e.transitions)
    for unseen in range(len(flat)):
        other=list(flat);x=unseen%4;other[unseen]=(x,2)
        check(tuple(v for i,v in enumerate(flat) if i!=unseen)==tuple(v for i,v in enumerate(other) if i!=unseen))
        check(any(v[1] not in (0,1) for v in other))
        es=tuple(Experiment(e.name,e.cost,tuple(other[4*i:4*i+4])) for i,e in enumerate(p.experiments))
        pp=Problem(4,es,p.repairs);m=Meter();cp=metered_problem(pp,m)
        check(immutable_binary_guard(cp,m) is None)

@group('certificate mutation does not create a valid shortcut',
       'Wrong repair, absent report branch, duplicate branch, insufficient depth and insufficient storage on n=8.')
def mutations():
    p=cell_problem(8);fs,_=compile_measured(p,3,'balanced');t=fs[0].tree
    obj=tree_to_dict(t)
    for bad in (Tree('repair',0),Tree('query',t.index,t.children[:1]),
                Tree('query',t.index,(t.children[0],t.children[0]))):
        try:check_tree(p,range(8),bad,3)
        except ValueError:check(True)
        else:check(False)
    for h,budget in ((2,None),(3,(Q(4),14)),(3,(Q(3),15))):
        try:check_tree(p,range(8),t,h,budget)
        except ValueError:check(True)
        else:check(False)
    check(tree_from_dict(obj)==t)

result={'status':'PASS','groups':GROUPS,'group_count':len(GROUPS),'assertions':COUNT,
        'arithmetic':'Exact integers and fractions.Fraction; no random samples.',
        'non_claims':['Not a proof assistant or external replication.',
        'Measured compiler reads are not total CPU cost.',
        'No neural training, learned physical model, or open-ended self-rewriting.',
        'The fair-racing checks concern abstract worker schedules, not a resumable version of the shipped compiler.']}
(ROOT/'validation').mkdir(exist_ok=True)
(ROOT/'validation'/'discovery_checks.json').write_text(json.dumps(result,indent=2)+'\n')
print(f"PASS: {len(GROUPS)} groups; {COUNT:,} exact finite assertions.")
