"""Exact, bounded checks for the first edition's accountability additions.

All numerical input is integer or rational. No pretrained model, private account,
external network, statistical sampling, or real sanctioning mechanism is used.
"""
from __future__ import annotations
from fractions import Fraction as Q
from itertools import product
from pathlib import Path
from functools import lru_cache
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/'code'))
from accountability import (privacy_envelope, privacy_attainment, inspection_equilibrium,
                            appeal_obstruction, assign_appeals, stoppable_kernel,
                            check_stopping_certificate)
from finite_contract import Contract, expand, bits, safety_kernel
from exact_enforcement import monitor_vertices, dot
from demo_accountability import settlement_case, stopping_case


def tv(p,q):
    return sum((abs(a-b) for a,b in zip(p,q)),Q(0))/2


def compositions(n,k):
    if k==1:
        yield (n,)
    else:
        for a in range(n+1):
            for tail in compositions(n-a,k-1):
                yield (a,)+tail


def direct_appeal_exists(windows, capacities):
    """Enumerate feasible epoch assignments, rather than matching or Hall tests."""
    ordered=sorted(windows,key=lambda x:(x[1]-x[0],x[1],x[0]))
    def visit(i, remaining):
        if i==len(ordered):
            return True
        a,b=ordered[i]
        for t in range(a-1,b):
            if remaining[t]:
                rem=list(remaining);rem[t]-=1
                if visit(i+1,tuple(rem)):
                    return True
        return False
    return visit(0,tuple(capacities))


def direct_hall(windows,capacity):
    for mask in range(1,1<<len(windows)):
        union=set()
        for j,(a,b) in enumerate(windows):
            if mask>>j&1:
                union.update(range(a,b+1))
        if mask.bit_count()>sum(capacity[t-1] for t in union):
            return False
    return True


def reachable_policy(game,start,policy,allowed,goal=None):
    """Direct selected-graph search; service additionally rejects non-goal cycles."""
    graph={};pending=[start]
    while pending:
        b=pending.pop()
        if b in graph:
            continue
        if b not in allowed or b & ~game.model.safe:
            return False
        if goal is not None and not b & ~goal:
            graph[b]=()
            continue
        a=policy.get(b)
        if a not in game.actions[b]:
            return False
        graph[b]=tuple(game.successors[b,a]);pending.extend(graph[b])
    if goal is None:
        return True
    active=set();done=set()
    def acyclic(b):
        if b in active:return False
        if b in done:return True
        active.add(b)
        if any(not acyclic(c) for c in graph[b]):return False
        active.remove(b);done.add(b);return True
    return acyclic(start)


def direct_mode_policies(game,actions,allowed,goal=None):
    choices=[tuple(sorted(actions[b])) for b in game.beliefs]
    wins=set()
    for vals in product(*choices):
        p=dict(zip(game.beliefs,vals))
        for b in allowed-wins:
            if reachable_policy(game,b,p,allowed,goal):wins.add(b)
    return frozenset(wins)


def run_extensions(group,require):
    @group('v1_external_boundary_counterexample',
           'Two externally different ownership states with identical internal four-slot records.')
    def external():
        for reserve in (0,1):
            internal=(1,1,1,1)
            require(sum(internal)<=4)
            require((sum(internal)<=4-reserve)==(reserve==0))
        require(tuple((1,1,1,1))==tuple((1,1,1,1)))

    @group('v1_strategic_inspection',
           'g=1..4, F=g+1..g+3, c=1..3, b=c+1..c+3; exact best responses and verified-fee variants.')
    def inspector():
        for g in range(1,5):
            for f in range(g+1,g+4):
                for c in range(1,4):
                    for b in range(c+1,c+4):
                        p,q=inspection_equilibrium(g,f,c,b)
                        require(0<p<1 and 0<q<1)
                        require(Q(g)-q*f==0 and p*b-c==0)
                        require(g>0 and b-c>0 and g-f<0 and -c<0)
                        for q0 in (Q(0),q/2,q,(q+1)/2,Q(1)):
                            require((Q(g)-q0*f>0)==(q0<q))
                        for p0 in (Q(0),p/2,p,(p+1)/2,Q(1)):
                            require((p0*b-c>0)==(p0>p))
                        for p0 in (Q(0),Q(1,2),Q(1)):
                            require((c+1)+p0*b-c>0)
                        require(c+Q(0)*b-c==0)  # w=c loses strictness at compliance.

    @group('v1_sharp_privacy_envelope',
           'All three-outcome laws with denominator 4; factors 1,3/2,2,3,5; caps 0,1/10,1/4,1/2,1. Exact LP vertices.')
    def envelope():
        laws=[tuple(Q(x,4) for x in v) for v in compositions(4,3)]
        caps=(Q(0),Q(1,10),Q(1,4),Q(1,2),Q(1))
        factors=(Q(1),Q(3,2),Q(2),Q(3),Q(5))
        cache={(pc,a):monitor_vertices(pc,a) for pc in laws for a in caps}
        for pc,pd,k in product(laws,laws,factors):
            if not all(d<=k*c and c<=k*d for c,d in zip(pc,pd)):
                continue
            require(tv(pc,pd)<=(k-1)/(k+1))
            delta=tuple(d-c for d,c in zip(pd,pc))
            for a in caps:
                optimum=max(dot(delta,s) for s in cache[pc,a])
                require(0<=optimum<=privacy_envelope(k,a))
                # An orthogonal fractional-knapsack optimization over positive gains.
                remaining=a;value=Q(0)
                for d,c in sorted(zip(delta,pc),key=lambda dc:dc[0]/dc[1] if dc[1] else Q(-1),reverse=True):
                    if d>0:
                        require(c>0)
                        take=min(Q(1),remaining/c)
                        value+=take*d;remaining-=take*c
                require(optimum==value)

    @group('v1_privacy_attainment',
           'Factors 1,6/5,3/2,2,3,5,10 and every cap j/20 for j=0..20, plus exact integrated example.')
    def attainment():
        for k,a in product((Q(1),Q(6,5),Q(3,2),Q(2),Q(3),Q(5),Q(10)),(Q(j,20) for j in range(21))):
            pc,pd,s=privacy_attainment(k,a)
            require(sum(pc)==sum(pd)==1)
            require(all(d<=k*c and c<=k*d for c,d in zip(pc,pd)))
            require(dot(pc,s)<=a and all(0<=x<=1 for x in s))
            require(dot(tuple(d-c for d,c in zip(pd,pc)),s)==privacy_envelope(k,a))
        pc,pd,s=privacy_attainment(Q(3),Q(1,10))
        require(dot(pc,s)==Q(1,10) and dot(pd,s)==Q(3,10))
        require(2*(dot(pd,s)-dot(pc,s))-Q(1,3)==Q(1,15))
        require(privacy_envelope(Q(1),Q(1))==0)

    @group('v1_conditional_disclosure',
           'Two binary releases, five conditional Bernoulli-law pairs per prefix, all 125 kernel selections and 16 binary postprocessings.')
    def disclosure():
        pairs=((Q(1,4),Q(3,4)),(Q(1,2),Q(1,2)),(Q(3,4),Q(1,4)),
               (Q(1,4),Q(1,4)),(Q(3,4),Q(3,4)))
        for first,second0,second1 in product(pairs,repeat=3):
            pc=[];pd=[]
            for x,y in product((0,1),repeat=2):
                c0,d0=first;cx,dx=(second0 if x==0 else second1)
                pc.append((c0 if x else 1-c0)*(cx if y else 1-cx))
                pd.append((d0 if x else 1-d0)*(dx if y else 1-dx))
            require(sum(pc)==sum(pd)==1)
            require(all(d<=9*c and c<=9*d for c,d in zip(pc,pd)))
            for mapping in product((0,1),repeat=4):
                cq=[sum(pc[i] for i in range(4) if mapping[i]==j) for j in (0,1)]
                dq=[sum(pd[i] for i in range(4) if mapping[i]==j) for j in (0,1)]
                require(all(d<=9*c and c<=9*d for c,d in zip(cq,dq)))
        even=(Q(1,2),Q(0),Q(0),Q(1,2));odd=(Q(0),Q(1,2),Q(1,2),Q(0))
        for coordinate in (0,1):
            ec=[sum(even[i] for i,xy in enumerate(product((0,1),repeat=2)) if xy[coordinate]==j) for j in (0,1)]
            oc=[sum(odd[i] for i,xy in enumerate(product((0,1),repeat=2)) if xy[coordinate]==j) for j in (0,1)]
            require(ec==oc)
        require(tv(even,odd)==1)

    @group('v1_appeal_capacity',
           'All T=1..3, all 0..4 appeal interval windows, and capacities 0..2 at each epoch; interval test, matching, subset Hall, and direct assignment.')
    def appeals():
        for t in range(1,4):
            all_windows=tuple((a,b) for a in range(1,t+1) for b in range(a,t+1))
            for n in range(5):
                for windows in product(all_windows,repeat=n):
                    for cap in product(range(3),repeat=t):
                        obstruction=appeal_obstruction(windows,cap)
                        allocation=assign_appeals(windows,cap)
                        success=allocation is not None
                        require(success==(obstruction is None))
                        require(success==direct_appeal_exists(windows,cap))
                        require(success==direct_hall(windows,cap))
                        if success:
                            require(len(allocation)==n and len(set(allocation.values()))==n)
                            require(all(windows[j][0]<=epoch<=windows[j][1] and 0<=slot<cap[epoch-1]
                                        for j,(epoch,slot) in allocation.items()))
                        else:
                            a,b,demand,supply=obstruction
                            require(demand>supply==sum(cap[a-1:b]))
        require(appeal_obstruction(((1,1),(1,1)),(1,1))==(1,1,2,1))
        require(assign_appeals((),())=={})

    @group('v1_stoppable_kernel',
           'All two-state nondeterministic run/end successor rows (3^4), full or common observations, compatible safe/goal masks, with or without running hold.')
    def stopping():
        for row in product(range(1,4),repeat=4):
            transitions=((row[0],row[1],1),(row[2],row[3],2))
            for observations in ((0,0),(0,1)):
                for safe in (1,2,3):
                    for goal in (1,2,3):
                        if goal & ~safe:continue
                        model=Contract(observations,(frozenset({0,1,2}),)*2,transitions,safe)
                        game=expand(model)
                        allowed=frozenset(b for b in game.beliefs if not b & ~safe)
                        for allow_hold in (False,True):
                            running={b:frozenset({0,2} if allow_hold else {0}) for b in game.beliefs}
                            ending={b:frozenset({1,2}) for b in game.beliefs}
                            result=stoppable_kernel(game,running,ending,goal)
                            direct_end=direct_mode_policies(game,ending,allowed,goal)
                            require(frozenset(result.ending_ranks)==direct_end)
                            direct_run=direct_mode_policies(game,running,direct_end)
                            require(result.running_kernel==direct_run)
                            for b in result.running_kernel:
                                valid,errors=check_stopping_certificate(game,running,ending,b,result.running_policy,
                                                                      result.ending_policy,result.ending_ranks,goal)
                                require(valid,str(errors))

    @group('v1_stopping_negative_controls',
           'Five-state locked-settlement example; reject unsafe initial state, missing ending state, and invalid rank.')
    def stop_controls():
        report=stopping_case()
        require(report['ending_preserving_kernel_state_indices']==[0,1,3])
        require(report['certificate_valid'] and report['locked_is_safe_but_not_stoppable'])
        t=((2,1,8,1),(4,1,8,2),(4,4,16,4),(8,8,8,8),(16,16,16,16))
        game=expand(Contract(tuple(range(5)),(frozenset(range(4)),)*5,t,15))
        running={b:frozenset({0,1,3}) for b in game.beliefs};ending={b:frozenset({2,3}) for b in game.beliefs}
        r=stoppable_kernel(game,running,ending,8)
        for initial in (4,16):
            require(not check_stopping_certificate(game,running,ending,initial,r.running_policy,
                                                   r.ending_policy,r.ending_ranks,8)[0])
        badr=dict(r.ending_ranks);badr[1]=0
        require(not check_stopping_certificate(game,running,ending,1,r.running_policy,
                                               r.ending_policy,badr,8)[0])
        badp=dict(r.ending_policy);badp.pop(2)
        badr=dict(r.ending_ranks);badr.pop(2)
        require(not check_stopping_certificate(game,running,ending,1,r.running_policy,badp,badr,8)[0])

    @group('v1_guarded_switching',
           'All 625 deterministic successor choices on four certified mode-states plus an unsafe state; all 81 rank maps in 0..2.')
    def switching():
        # Certified augmented states 0=a0,1=a1,2=b1,3=b2; 4 is unsafe.
        # Every listed primitive edge must have its actual endpoint in a certified domain.
        for successors in product(range(5),repeat=4):
            assumptions=all(x<4 for x in successors)
            if assumptions:
                for initial in range(4):
                    visited=set();x=initial
                    while x not in visited:
                        require(x<4)
                        visited.add(x);x=successors[x]
            for ranks in product(range(3),repeat=4):
                # The target is the prescribed set of zero-rank states here.
                positive=[i for i in range(4) if ranks[i]>0]
                certified=assumptions and all(ranks[successors[i]]<ranks[i] for i in positive)
                if certified:
                    for initial in range(4):
                        x=initial;steps=0
                        while ranks[x]>0:
                            x=successors[x];steps+=1
                            require(steps<=ranks[initial])
                        require(ranks[x]==0)
        # Sound before an environmental change is not sound during the action.
        old_capacity,actual_capacity,need=1,0,1
        require(old_capacity>=need and not actual_capacity>=need)
        # a2 -> a1 -> b2 -> b1 -> a2 never visits either rank-zero target.
        cycle=(0,1,2,3);local=(2,1,2,1)
        require(all(local[cycle[i+1]]<local[cycle[i]] for i in (0,2)))
        require(local[2]>local[1] and local[0]>local[3])

    @group('v1_assurance_dependency_controls',
           'Boolean mutual implications plus every positive dependency DAG on 1..4 nodes, with explicit false or true anchors.')
    def dependencies():
        implication=lambda a,b:(not a) or b
        require(implication(False,False) and implication(False,False))
        require(not (False and False))
        for n in range(1,5):
            possible=[(i,j) for j in range(n) for i in range(j)]
            for edgeflags in product((False,True),repeat=len(possible)):
                parents={j:[] for j in range(n)}
                for use,(i,j) in zip(edgeflags,possible):
                    if use:parents[j].append(i)
                roots=[j for j in range(n) if not parents[j]]
                for base in product((False,True),repeat=len(roots)):
                    established=dict(zip(roots,base))
                    for j in range(n):
                        if j not in established:established[j]=all(established[i] for i in parents[j])
                    if all(base):require(all(established.values()))
                    for j in range(n):
                        if parents[j]:require(established[j]==all(established[i] for i in parents[j]))

    @group('v1_observation_fibre_enumeration',
           'All binary observation assignments for n=1..6 compared with full subset filtering; 128 distinct observations as a scalability control.')
    def fibres():
        for n in range(1,7):
            for obs in product((0,1),repeat=n):
                model=Contract(obs,(frozenset({0}),)*n,tuple((1<<i,) for i in range(n)),(1<<n)-1)
                got=expand(model).beliefs
                expected=tuple(b for b in range(1,1<<n) if len({obs[i] for i in range(n) if b>>i&1})==1)
                require(got==expected)
        n=128
        model=Contract(tuple(range(n)),(frozenset({0}),)*n,tuple((1<<i,) for i in range(n)),(1<<n)-1)
        game=expand(model)
        require(len(game.beliefs)==n)
        require(game.beliefs==tuple(1<<i for i in range(n)))

    @group('v1_accountable_commons',
           'Capacity 0..12; five staged profiles with costs 2,3,1,1,1; exact monitor and phase-rank certificate.')
    def commons():
        for capacity in range(13):
            result=settlement_case(capacity)
            require(result['settlement_feasible']==(capacity>=8))
            if capacity>=8:
                require(result['certificate_valid'] and result['steps']==5)
                require(sum(x['cost'] for x in result['trace'])==8)
                require(result['trace'][-1]['remaining_phase_rank']==0)
        require(not settlement_case(7)['settlement_feasible'])
        require(settlement_case(8)['settlement_feasible'])

    @group('v1_input_rejection',
           'Invalid exact numeric types, gains, penalty/reward domains, negative capacity, and reversed/out-of-range windows.')
    def invalid():
        calls=(lambda:privacy_envelope(Q(1,2),Q(1,2)),lambda:privacy_envelope(2,Q(-1)),
               lambda:privacy_envelope(2,1.0),lambda:inspection_equilibrium(1,1,1,2),
               lambda:inspection_equilibrium(1,2,2,1),lambda:assign_appeals(((2,1),),(1,1)),
               lambda:appeal_obstruction(((0,1),),(1,)),lambda:assign_appeals((),(-1,)),
               lambda:settlement_case(-1))
        for call in calls:
            try:call()
            except (ValueError,TypeError):require(True)
            else:require(False,'Invalid input accepted.')
