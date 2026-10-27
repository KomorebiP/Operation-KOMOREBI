"""Bounded exact v0.7 tests with independent policy and dual checks.

No randomized sampling, agent learning, external side effects, or hidden data.
The tested ranges are explicitly attached to each assertion group.
"""
from __future__ import annotations
from fractions import Fraction as Q
from itertools import product
from functools import lru_cache
from pathlib import Path
import json
import sys

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/'code'))
from exact_enforcement import (dot, common_monitor, two_deviation_dual,
                               solve_square, vertices)
from finite_contract import (Contract, expand, bits, safety_kernel,
                             service_attractor, check_certificate, image,
                             check_quotient)

CASES=[]


def tv(p,q):
    return sum((abs(a-b) for a,b in zip(p,q)),Q(0))/2


def direct_beliefs(model):
    return tuple(b for b in range(1,1<<model.state_count)
                 if len({model.observations[i] for i in range(model.state_count) if b>>i&1})==1)


def direct_successors(model,b,a):
    if any(a not in model.admissible[i] for i in range(model.state_count) if b>>i&1):
        return None
    buckets={}
    for i in range(model.state_count):
        if b>>i&1:
            for j in range(model.state_count):
                if model.transitions[i][a]>>j&1:
                    obs=model.observations[j]
                    buckets[obs]=buckets.get(obs,0)|(1<<j)
    return tuple(sorted(buckets.values()))


def stationary_succeeds(model,start,policy,goal=None,viable=None):
    """Independent reachable graph traversal, with cycle detection for service."""
    graph={};stack=[start]
    while stack:
        b=stack.pop()
        if b in graph:continue
        if b&~model.safe:return False
        if goal is not None and not b&~goal:
            if viable is not None and b not in viable:return False
            graph[b]=()
            continue
        nxt=direct_successors(model,b,policy[b])
        if nxt is None:return False
        graph[b]=nxt
        stack.extend(nxt)
    if goal is None:return True
    active=set();done=set()
    def cycle(v):
        if v in active:return True
        if v in done:return False
        active.add(v)
        for w in graph[v]:
            if cycle(w):return True
        active.remove(v);done.add(v)
        return False
    return not cycle(start)


def brute_winning(model,goal=None,viable=None):
    beliefs=direct_beliefs(model)
    winners=set()
    for choices in product(range(model.action_count),repeat=len(beliefs)):
        policy=dict(zip(beliefs,choices))
        for b in beliefs:
            if b not in winners and stationary_succeeds(model,b,policy,goal,viable):
                winners.add(b)
    return frozenset(winners)


def commons(c,d):
    profiles=tuple((audit,served) for audit in range(3) for served in range(d+1))
    idle=len(profiles)
    start=frozenset(i for i,(audit,served) in enumerate(profiles)
                    if audit==2 and audit+served<=c)
    trans0=tuple(2 if served==d else 4 for audit,served in profiles)+(4,)
    model=Contract((0,1,2),(start,frozenset({idle}),frozenset({idle})),
                   (trans0,(2,)*(idle+1),(4,)*(idle+1)),3)
    return model,profiles,idle


def run_extensions(group,require):
    @group('v07 Exact linear algebra and explicit enumeration limits',
           'All nonsingular 2x2 integer matrices with entries -1,0,1 and RHS entries -1,0,1; singular control; an explicit enumeration-limit rejection')
    def _():
        for coeff in product((-1,0,1),repeat=4):
            a,b,c,d=map(Q,coeff);det=a*d-b*c
            for y,z in product((-1,0,1),repeat=2):
                result=solve_square(((a,b),(c,d)),(y,z))
                if det:
                    require(result==((d*y-b*z)/det,(a*z-c*y)/det))
                else:require(result is None)
        try:
            vertices([((Q(1),Q(0)),Q(1))]*10,2,max_combinations=1)
        except ValueError:require(True)
        else:require(False,'Excessive enumeration was not rejected.')

    @group('v07 Common-monitor primal versus independent mixture dual',
           'All triples of binary laws with denominator 2; penalties 1,2; caps 0,1/4,1/2,1; four gain vectors; 864 exact LP instances')
    def _():
        laws=tuple((Q(i,2),Q(2-i,2)) for i in range(3))
        gainvecs=((Q(0),Q(0)),(Q(1,4),Q(1,4)),(Q(0),Q(1,2)),(Q(1,4),Q(1,2)))
        for pc,p1,p2 in product(laws,repeat=3):
            for F,alpha,gains in product((Q(1),Q(2)),(Q(0),Q(1,4),Q(1,2),Q(1)),gainvecs):
                value,monitor=common_monitor(pc,(p1,p2),gains,F,alpha)
                dual,mixture=two_deviation_dual(pc,(p1,p2),gains,F,alpha)
                require(value==dual)
                margins=[F*dot(tuple(p-c for p,c in zip(law,pc)),monitor)-g
                         for law,g in zip((p1,p2),gains)]
                require(min(margins)==value)
                require(dot(pc,monitor)<=alpha and all(0<=x<=1 for x in monitor))
                require(sum(mixture)==1 and all(x>=0 for x in mixture))

    @group('v07 Mixture obstruction and rich-audit exact frontier',
           'Formal pairwise counterexample; richer three-outcome audit at all caps k/32, k=0..32; direct zero-gain boundary; all margins exact')
    def _():
        pc=(Q(1,2),Q(1,2));laws=((Q(1),Q(0)),(Q(0),Q(1)))
        value,s=common_monitor(pc,laws,(Q(1,2),Q(1,2)),Q(2),Q(1,2))
        require(value==Q(-1,2));require(s[0]==s[1])
        require(two_deviation_dual(pc,laws,(Q(1,2),)*2,Q(2),Q(1,2))[1]==(Q(1,2),Q(1,2)))
        for law,chosen in zip(laws,((Q(1),Q(0)),(Q(0),Q(1)))):
            require(2*dot(tuple(p-c for p,c in zip(law,pc)),chosen)-Q(1,2)==Q(1,2))
        rich=(Q(3,4),Q(1,8),Q(1,8));richlaws=((Q(0),Q(1),Q(0)),(Q(0),Q(0),Q(1)))
        for k in range(33):
            a=Q(k,32);value,monitor=common_monitor(rich,richlaws,(Q(1),Q(1)),Q(2),a)
            require(value==min(6*a,Q(3,2))-1)
            require(two_deviation_dual(rich,richlaws,(Q(1),Q(1)),Q(2),a)[0]==value)
        require(common_monitor(pc,laws,(Q(0),Q(0)),Q(2),Q(0))[0]==0)

    @group('v07 Robust common-monitor error accounting',
           'Binary exact/estimated laws on quarter grid, all half-grid monitors; selected three-outcome perturbations within 1/8 of rich-audit laws')
    def _():
        laws=tuple((Q(i,4),Q(4-i,4)) for i in range(5))
        hatc=(Q(1,2),Q(1,2));hats=((Q(3,4),Q(1,4)),(Q(1,4),Q(3,4)))
        for pc,p1,p2 in product(laws,repeat=3):
            ec=tv(pc,hatc)
            for s in product((Q(0),Q(1,2),Q(1)),repeat=2):
                require(dot(pc,s)<=dot(hatc,s)+ec)
                for law,hat in zip((p1,p2),hats):
                    e=tv(law,hat)
                    actual=2*dot(tuple(a-b for a,b in zip(law,pc)),s)-Q(1,4)
                    approx=2*dot(tuple(a-b for a,b in zip(hat,hatc)),s)-Q(1,4)
                    require(actual>=approx-2*(ec+e))
        hc=(Q(3,4),Q(1,8),Q(1,8));hd=((Q(0),Q(1),Q(0)),(Q(0),Q(0),Q(1)))
        three=tuple(tuple(Q(v,8) for v in row) for row in product(range(9),repeat=3) if sum(row)==8)
        cs=[p for p in three if tv(p,hc)<=Q(1,8)]
        d1=[p for p in three if tv(p,hd[0])<=Q(1,8)]
        d2=[p for p in three if tv(p,hd[1])<=Q(1,8)]
        s=(Q(0),Q(1),Q(1));alpha=Q(3,8)
        for pc,p1,p2 in product(cs,d1,d2):
            require(dot(pc,s)<=alpha)
            for p in (p1,p2):require(2*dot(tuple(a-b for a,b in zip(p,pc)),s)-1>=0)

    @group('v07 Complete two-state safety catalogue versus policy enumeration',
           'All 81 nonempty-successor tables for 2 states and 2 profiles; both observation partitions; all 4 safe masks; all 16 statewise action-admissibility assignments: 10,368 contracts')
    def _():
        options=tuple(frozenset(bits(mask)) for mask in range(4))
        for entries in product((1,2,3),repeat=4):
            transitions=(entries[:2],entries[2:])
            for obs,safe,allowed in product(((0,0),(0,1)),range(4),tuple(product(options,repeat=2))):
                model=Contract(obs,allowed,transitions,safe)
                game=expand(model);W,policy,layers=safety_kernel(game)
                expected=brute_winning(model)
                require(W==expected)
                require(all(layers[i+1]<layers[i] for i in range(len(layers)-1)))
                require(len(layers)<=len(game.beliefs)+1)
                for b in W:require(check_certificate(game,b,policy)[0])
                @lru_cache(None)
                def horizon(b,k):
                    if b&~safe:return False
                    if not k:return True
                    for a in range(2):
                        nxt=direct_successors(model,b,a)
                        if nxt is not None and all(horizon(x,k-1) for x in nxt):return True
                    return False
                for k,layer in enumerate(layers):
                    require(layer==frozenset(b for b in game.beliefs if horizon(b,k)))
                CASES.append((model,game,W,expected))
        require(len(CASES)==10368)

    @group('v07 Certified progress versus independent cycle exclusion',
           'The preceding 10,368 contracts with every one of 4 completion masks; enumerate stationary policies and reject every reachable nonterminal cycle')
    def _():
        for model,game,W,expected in CASES:
            for goal in range(4):
                ranks,choices=service_attractor(game,W,goal)
                independently=brute_winning(model,goal,expected)
                require(frozenset(ranks)==independently)
                require(all(r<=len(game.beliefs) for r in ranks.values()))
                if ranks:
                    _,safepolicy,_=safety_kernel(game)
                    policy={b:choices.get(b,safepolicy[b]) for b in ranks}
                    # A progress certificate can leave the completed set later. Use
                    # a safety certificate for the suffix instead of silently requiring
                    # all viable suffix states to remain in the finite attractor.
                    for b,r in ranks.items():
                        if r:
                            require(all(ranks[nxt]<r for nxt in game.successors[b,choices[b]]))
                        else:require(not b&~goal)

    @group('v07 Exact quotient transport of safety, successors, and progress',
           '81 two-state successor tables; 2 observation partitions; 4 safe masks; 3 availability patterns; 2 concrete refinements; every coherent concrete support and every completion mask: 3,888 refinements')
    def _():
        projection=(0,0,1);count=0
        avails=((frozenset({0,1}),)*2,(frozenset({0}),frozenset({0,1})),(frozenset({0,1}),frozenset({1})))
        for entries in product((1,2,3),repeat=4):
            for obs,safe,allowed,variant in product(((0,0),(0,1)),range(4),avails,range(2)):
                reduced=Contract(obs,allowed,(entries[:2],entries[2:]),safe)
                pre=lambda mask: sum(1<<i for i,z in enumerate(projection) if mask>>z&1)
                transition=[]
                for i,z in enumerate(projection):
                    row=[]
                    for a in range(2):
                        target=reduced.transitions[z][a]
                        mask=4 if target&2 else 0
                        if target&1:mask|=3 if variant==0 else 1<<((i+a)%2)
                        row.append(mask)
                    transition.append(tuple(row))
                full=Contract(tuple(obs[z] for z in projection),tuple(allowed[z] for z in projection),tuple(transition),pre(safe))
                gf,gr=expand(full),expand(reduced)
                wf,_,_=safety_kernel(gf);wr,_,_=safety_kernel(gr)
                for b in gf.beliefs:
                    bbar=image(b,projection)
                    require((b in wf)==(bbar in wr))
                    require(gf.actions[b]==gr.actions[bbar])
                    for a in gf.actions[b]:
                        require(frozenset(image(q,projection) for q in gf.successors[b,a])==gr.successors[bbar,a])
                for goal in range(4):
                    require(check_quotient(full,reduced,projection,pre(goal),goal)[0])
                    rf,_=service_attractor(gf,wf,pre(goal));rr,_=service_attractor(gr,wr,goal)
                    for b in gf.beliefs:require(rf.get(b)==rr.get(image(b,projection)))
                count+=1
        require(count==3888)

    @group('v07 Information, successor, permission, and goal negative controls',
           'Explicit minimal models violating each transport obligation; immediate-safe amendment with forced later breach; stochastic-completion support counterexample')
    def _():
        # Same public signal; separate profiles work in each hidden state only.
        model=Contract((0,0),(frozenset({0}),frozenset({1})),((1,1),(2,2)),3)
        g=expand(model);W,_,_=safety_kernel(g)
        require(W==frozenset({1,2}));require(3 not in W)
        informed=Contract((0,1),model.admissible,model.transitions,3)
        require(not check_quotient(model,informed,(0,1),3,3)[0])
        empty=Contract((0,),(frozenset(),),((1,),),1)
        permitted=Contract((0,),(frozenset({0}),),((1,),),1)
        require(not check_quotient(empty,permitted,(0,),1,1)[0])
        require(not safety_kernel(expand(empty))[0] and safety_kernel(expand(permitted))[0]==frozenset({1}))
        unsafe=Contract((0,),permitted.admissible,permitted.transitions,0)
        require(not check_quotient(unsafe,permitted,(0,),0,1)[0])
        delayed=Contract((0,1),(frozenset({0}),)*2,((2,),(2,)),1)
        sanitized=Contract((0,1),delayed.admissible,((1,),(2,)),1)
        require(not check_quotient(delayed,sanitized,(0,1),1,1)[0])
        require(1 not in safety_kernel(expand(delayed))[0] and 1 in safety_kernel(expand(sanitized))[0])
        require(not check_quotient(permitted,permitted,(0,),0,1)[0])
        # r, lock, completed, breach. Three profiles: deliver, freeze, wait.
        amendment=Contract((0,1,2,3),(frozenset({0,1}),frozenset({2}),frozenset({2}),frozenset({2})),
                           ((4,2,8),(8,8,8),(4,4,4),(8,8,8)),7)
        ag=expand(amendment);aw,ap,_=safety_kernel(ag)
        require(1 in aw and 2 not in aw and amendment.safe&2)
        require(ap[1]==0)
        probabilistic_support=Contract((0,1),(frozenset({0}),)*2,((3,),(2,)),3)
        pg=expand(probabilistic_support);pw,_,_=safety_kernel(pg);pr,_=service_attractor(pg,pw,2)
        require(pw==frozenset({1,2}) and set(pr)=={2})
        for t in range(9):require(Q(1,2)**t>0)

    @group('v07 Certificate acceptance and deliberate tampering',
           'A valid two-node safety/service witness; omitted successor, inadmissible profile, false goal, invalid public support, missing initial state, negative/nondecreasing/nonnumeric ranks; out-of-range goals; negative state-mask rejection')
    def _():
        model=Contract((0,1),(frozenset({0}),)*2,((2,),(2,)),3)
        g=expand(model);policy={1:0,2:0};ranks={1:1,2:0}
        require(check_certificate(g,1,policy,ranks,2)[0])
        cases=[(1,{1:0},None,None),(1,{1:1,2:0},None,None),(1,policy,{1:0,2:0},2),
               (1,policy,{1:0,2:1},2),(1,policy,{1:-1,2:0},2),
               (3,{3:0},None,None),(1,{2:0},None,None),(1,policy,{1:1},2),
               (1,policy,{1:1,2:"bad"},2),(1,policy,ranks,-1),(1,policy,ranks,4)]
        for initial,pol,rs,goal in cases:require(not check_certificate(g,initial,pol,rs,goal)[0])
        rejected=False
        try:tuple(bits(-1))
        except ValueError:rejected=True
        require(rejected)

    @group('v07 One budget for the complete commons contract',
           'c=0..8 available slots, d=0..5 due service units, full audit/service profile catalogue; exact threshold c>=d+2 and generated c=5,d=3 witness')
    def _():
        for c,d in product(range(9),range(6)):
            model,profiles,idle=commons(c,d);g=expand(model);W,policy,_=safety_kernel(g)
            ranks,choices=service_attractor(g,W,2)
            require((1 in W)==(c>=d+2))
            require((1 in ranks)==(c>=d+2))
            if c>=d+2:
                require(ranks[1]==1)
                chosen=profiles[choices[1]]
                require(chosen==(2,d))
                cert={1:choices[1],2:idle};cert_ranks={1:1,2:0}
                require(check_certificate(g,1,cert,cert_ranks,2)[0])
        model,profiles,idle=commons(5,3);game=expand(model)
        W,policy,_=safety_kernel(game);ranks,choices=service_attractor(game,W,2)
        witness={'model':'One-epoch declared commons variant',
                 'capacity':5,'due_service_units':3,'initial_possibility_mask':1,
                 'goal_state_mask':2,'safe_state_mask':3,
                 'state_names':['pending','completed','breach'],
                 'profiles':[list(x) for x in profiles]+[['idle']],
                 'policy':{str(1):choices[1],str(2):idle},
                 'ranks':{'1':1,'2':0},
                 'common_monitor':['0','1','1'],
                 'compliance_law':['3/4','1/8','1/8'],
                 'deviation_laws':[['0','1','0'],['0','0','1']],
                 'gains':['1','1'],'penalty':'2','false_positive_rate':'1/4',
                 'simultaneous_margin':'1/2',
                 'status':'PASS in the stated finite contract',
                 'non_claims':['No proof of physical audit implementation or estimated observation laws',
                               'No agent experiment or unrestricted institutional synthesis']}
        (ROOT/'validation/commons_joint_certificate.json').write_text(json.dumps(witness,indent=2)+'\n')
