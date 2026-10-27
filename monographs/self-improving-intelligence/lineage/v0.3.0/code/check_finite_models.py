#!/usr/bin/env python3
"""Exact bounded regression checks, not experiments on trained agents.

All correctness comparisons use integers, finite sets, or Fraction. The record
lists the actual finite domains; the number of assertions is not a sample size.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import platform
import sys
import time
from datetime import datetime, timezone
from fractions import Fraction as F
from functools import lru_cache
from itertools import combinations, product
from pathlib import Path

from repair_calculus import (Experiment, Repair, Problem, Tree, Attempt,
    compile_frontier, check_tree, replay, cell_problem, equality_tree, bit_tree,
    tree_depth, tree_records, tree_from_dict, tree_to_dict, relabel_problem,
    relabel_tree, stable_partition, recursive_progress)

ROOT = Path(__file__).resolve().parents[1]
GROUPS: list[dict] = []
CURRENT: dict = {}

def begin(name: str, domain: str) -> None:
    global CURRENT
    CURRENT = {'name': name, 'domain': domain, 'assertions': 0}
    GROUPS.append(CURRENT)

def require(condition: bool, detail: str = '') -> None:
    CURRENT['assertions'] += 1
    if not condition:
        raise AssertionError(f"{CURRENT['name']}: {detail}")

def rejected(call) -> None:
    try:
        call()
    except (ValueError, TypeError):
        require(True)
    else:
        require(False, 'An invalid certificate or input was accepted.')

def powerset_nonempty(n: int):
    for mask in range(1, 1 << n):
        yield frozenset(i for i in range(n) if mask >> i & 1)

def tv(p, q):
    return sum(abs(x-y) for x,y in zip(p,q))/2

def direct_tree_list(problem: Problem, states: frozenset[int], h: int) -> list[Tree]:
    """Unpruned enumeration of every tree admitted on a support at this depth.

    No frontier compiler, memoization, or Pareto reduction is used. Final cost is
    obtained from separate complete-world replay rather than cost propagation.
    """
    candidates = [Tree('repair',i) for i,r in enumerate(problem.repairs) if states <= r.good]
    if h == 0:
        return candidates
    for ei,e in enumerate(problem.experiments):
        entries = [e.transitions[x] for x in states]
        if None in entries:
            continue
        reports = sorted(set(v[1] for v in entries if v is not None))
        descendants = []
        for o in reports:
            following = frozenset(v[0] for v in entries if v is not None and v[1] == o)
            descendants.append(direct_tree_list(problem, following, h-1))
        for children in product(*descendants):
            candidates.append(Tree('query', ei, tuple(zip(reports,children))))
    return candidates

def independent_frontier(problem: Problem, states, h):
    pairs = set()
    for tree in direct_tree_list(problem, frozenset(states), h):
        work = max(F(replay(problem,tree,x,h+2)['work']) for x in states)
        pairs.add((work, tree_records(tree)))
    return {p for p in pairs if not any(q != p and q[0] <= p[0] and q[1] <= p[1] for q in pairs)}

def test_discrimination():
    begin('transcript_discrimination', 'All two-outcome P,Q on the quarter grid and randomized binary decisions on the quarter grid.')
    grid = [F(i,4) for i in range(5)]
    for p,q in product(grid, repeat=2):
        P,Q = (p,1-p),(q,1-q)
        scores=[]
        for a,b in product(grid, repeat=2):
            score=(P[0]*a+P[1]*b+Q[0]*(1-a)+Q[1]*(1-b))/2
            require(score <= (1+tv(P,Q))/2)
            scores.append(score)
        require(max(scores)==(1+tv(P,Q))/2)

def test_partition():
    begin('stable_partition', 'Every ternary labeling and every single transition function on three states; all state pairs. Pair-orbit comparison is independent of partition refinement.')
    for labels in product(range(3),repeat=3):
        for f in product(range(3),repeat=3):
            blocks=stable_partition(labels,(f,))
            for x,y in product(range(3),repeat=2):
                pair=(x,y); seen=set(); equivalent=True
                while pair not in seen:
                    seen.add(pair)
                    if labels[pair[0]]!=labels[pair[1]]:
                        equivalent=False;break
                    pair=(f[pair[0]],f[pair[1]])
                require((blocks[x]==blocks[y])==equivalent)
    begin('multi_operation_refinement', 'Every binary labeling and ordered pair of transition functions on two states, and all pairs of states.')
    funcs=list(product(range(2),repeat=2))
    for labels in product(range(2),repeat=2):
        for f,g in product(funcs,repeat=2):
            blocks=stable_partition(labels,(f,g))
            for x,y in product(range(2),repeat=2):
                stack=[(x,y)];seen=set();equal=True
                while stack:
                    a,b=stack.pop()
                    if (a,b) in seen:continue
                    seen.add((a,b))
                    if labels[a]!=labels[b]:equal=False;break
                    stack.extend(((f[a],f[b]),(g[a],g[b])))
                require((blocks[x]==blocks[y])==equal)

def test_synthesis():
    begin('synthesis_vs_unpruned_trees', 'All 256 ordered pairs of binary transition/report tables on two states, every nonempty initial support, and horizons 0,1,2. Two unique repairs; experiment costs 1 and 2, repair cost 1.')
    rows=list(product(range(2),repeat=2))
    tables=list(product(rows,repeat=2))
    for t0,t1 in product(tables,repeat=2):
        p=Problem(2,(Experiment('e0',F(1),t0),Experiment('e1',F(2),t1)),
                  (Repair('r0',F(1),frozenset({0})),Repair('r1',F(1),frozenset({1}))))
        for states in powerset_nonempty(2):
            for h in range(3):
                got=compile_frontier(p,states,h)
                require({(w.work,w.storage) for w in got}==independent_frontier(p,states,h))
                for w in got:
                    require(check_tree(p,states,w.tree,h)==(w.work,w.storage))
    begin('partial_domains_and_reset', 'A query illegal in one possible state; a destructive reset; and an immutable-origin variant. Horizons 0 through 3.')
    partial=Problem(2,(Experiment('partial',F(1),((0,0),None)),),
                    (Repair('r0',F(1),frozenset({0})),Repair('r1',F(1),frozenset({1}))))
    reset=Problem(2,(Experiment('reset',F(1),((0,0),(0,0))),),
                  (Repair('r0',F(1),frozenset({0})),))
    # (origin,current) indexed 2*origin+current; reset must retain origin.
    origin=Problem(4,(Experiment('reset',F(1),tuple((2*(x//2),0) for x in range(4))),),
                   (Repair('origin0',F(1),frozenset({0,1})),Repair('origin1',F(1),frozenset({2,3}))))
    for h in range(4):
        require(not compile_frontier(partial,{0,1},h))
        require(bool(compile_frontier(reset,{0,1},h))==(h>0))
        require(not compile_frontier(origin,{1,3},h))
    require(compile_frontier(reset,{0,1},1)[0].work==2)
    begin('repair_relevance_not_full_identification', 'Four equiprobable static states, repair partition {0,1,2}|{3}, two binary queries, horizon 2.')
    exps=(Experiment('repair_split',F(1),tuple((x,int(x==3)) for x in range(4))),
          Experiment('balanced',F(1),tuple((x,int(x>=2)) for x in range(4))))
    p=Problem(4,exps,(Repair('A',F(1),frozenset({0,1,2})),Repair('B',F(1),frozenset({3}))))
    f=compile_frontier(p,range(4),2)
    require((f[0].work,f[0].storage)==(2,3))
    require(f[0].tree.index==0)
    good=Tree('query',0,((0,Tree('repair',0)),(1,Tree('repair',1))))
    bad=Tree('query',1,((0,Tree('repair',0)),(1,good)))
    # The whole good tree has an unreachable 0 branch on {2,3}? Both branches remain possible.
    require(check_tree(p,range(4),bad,2)==(3,5))
    require(check_tree(p,range(4),good,1)==(2,3))
    begin('execution_storage_tradeoff', 'Four static cases, direct four-valued query cost 4, singleton queries cost 1, zero-cost unique repairs, horizon 3.')
    exps=(Experiment('direct',F(4),tuple((x,x) for x in range(4))),)+tuple(
        Experiment(f'eq{i}',F(1),tuple((x,int(x==i)) for x in range(4))) for i in range(4))
    p=Problem(4,exps,tuple(Repair(f'r{i}',F(0),frozenset({i})) for i in range(4)))
    got=compile_frontier(p,range(4),3)
    require({(w.work,w.storage) for w in got}=={(F(4),5),(F(3),7)})
    require(not any(w.work<=3 and w.storage<=5 for w in got))
    require({(w.work,w.storage) for w in got}==independent_frontier(p,range(4),3))

def test_cells_and_transfer():
    begin('hidden_cell_costs', 'Powers of two 2,4,8,16,32; every hidden cell; equality and bit trees. Compiler separately checked at n=2,4,8 with optimal bit depth.')
    for n in (2,4,8,16,32):
        p=cell_problem(n);eq=equality_tree(n);bt=bit_tree(n);k=n.bit_length()-1
        require(check_tree(p,range(n),eq,n-1)==(n,2*n-1))
        require(check_tree(p,range(n),bt,k)==(k+1,2*n-1))
        require(tree_depth(bt)==k)
        for x in range(n):
            require(replay(p,bt,x)['final_state']==x)
            require(replay(p,eq,x)['final_state']==x)
        if n<=8:
            f=compile_frontier(p,range(n),k)
            require({(w.work,w.storage) for w in f}=={(F(k+1),2*n-1)})
            require(not compile_frontier(p,range(n),k-1))
    p=cell_problem(8)
    traces=[replay(p,equality_tree(8),x) for x in range(8)]
    require(sum(len(t['trace']) for t in traces)==35)
    require(sum(F(t['work']) for t in traces)/8==F(43,8))
    require(sum(len(t['trace'])<=3 for t in traces)==3)
    begin('complete_investigation_transport', 'All 32 affine cell permutations i -> a*i+b modulo 8, a odd, all 8 flips of the three bit-report labels; all eight initial cells. Exact common costs, repairs and branch correspondence.')
    p=cell_problem(8);source=bit_tree(8)
    for a in (1,3,5,7):
        for b in range(8):
            sigma=tuple((a*i+b)%8 for i in range(8))
            for mask in range(8):
                flips=(0,)*8+tuple((mask>>i)&1 for i in range(3))
                dest=relabel_problem(p,sigma,flips);tree=relabel_tree(source,flips)
                require(check_tree(dest,range(8),tree,3)==(4,15))
                for i in range(8):
                    s=replay(p,source,i);t=replay(dest,tree,sigma[i])
                    require(t['final_state']==sigma[s['final_state']])
                    require(t['work']==s['work'])
    # Compiler cost sets agree for representative nontrivial transports.
    for b in (1,3):
        dest=relabel_problem(p,tuple((3*i+b)%8 for i in range(8)))
        require({(w.work,w.storage) for w in compile_frontier(dest,range(8),3)}=={(F(4),15)})
    begin('missing_observation_transport', 'Two identical singleton repair sets but a source revealing query and target constant query; horizons 0 through 4.')
    p=Problem(2,(Experiment('q',F(1),((0,0),(1,1))),),
              (Repair('r0',F(1),frozenset({0})),Repair('r1',F(1),frozenset({1}))))
    q=Problem(2,(Experiment('q',F(1),((0,0),(1,0))),),p.repairs)
    for h in range(5):
        require(bool(compile_frontier(p,{0,1},h))==(h>0))
        require(not compile_frontier(q,{0,1},h))

def test_rejections():
    begin('invalid_witnesses', 'Malformed tree nodes, missing/duplicate/extraneous branches, wrong repairs, depth, work/storage bounds, invalid models, and serialization checks.')
    p=cell_problem(8);tree=bit_tree(8)
    bads=[Tree('repair',0),Tree('other',0),Tree('query',999),Tree('repair',99),
          Tree('query',8,()),Tree('query',8,((0,tree.children[0][1]),)),
          Tree('query',8,((0,tree.children[0][1]),(0,tree.children[1][1]))),
          Tree('query',8,tree.children+((2,Tree('repair',0)),)),
          Tree('repair',0,((0,Tree('repair',0)),))]
    for bad in bads:rejected(lambda bad=bad:check_tree(p,range(8),bad,3))
    rejected(lambda:check_tree(p,range(8),tree,2))
    rejected(lambda:check_tree(p,range(8),tree,3,(F(3),15)))
    rejected(lambda:check_tree(p,range(8),tree,3,(F(4),14)))
    require(tree_from_dict(tree_to_dict(tree))==tree)
    rejected(lambda:tree_from_dict(tree_to_dict(tree),depth_limit=1))
    rejected(lambda:tree_from_dict({'kind':'query','index':'x'}))
    rejected(lambda:compile_frontier(p,[],3))
    rejected(lambda:compile_frontier(p,[8],3))
    rejected(lambda:compile_frontier(p,range(8),-1))
    rejected(lambda:cell_problem(3))
    rejected(lambda:Problem(0,(),()))
    rejected(lambda:Problem(1,(Experiment('x',F(-1),((0,0),)),),()))
    rejected(lambda:Problem(1,(Experiment('x',F(1),((1,0),)),),()))
    rejected(lambda:Problem(1,(),(Repair('r',F(1),frozenset({1})),)))
    rejected(lambda:relabel_problem(p,(0,)*8))

def test_error_and_resources():
    begin('selection_and_transfer_margins', 'Three true values on the half grid in [-1,1], all perturbations in {-1/4,0,1/4}; every pair of transferred values on the same grid.')
    vals=[F(i,2) for i in range(-2,3)];err=[F(-1,4),F(0),F(1,4)];eps=F(1,4)
    for truth in product(vals,repeat=3):
        for errors in product(err,repeat=3):
            estimates=tuple(x+e for x,e in zip(truth,errors))
            chosen=max(range(3),key=lambda i:estimates[i])
            require(truth[chosen]>=max(truth)-2*eps)
            for parent in range(3):
                if estimates[chosen]-estimates[parent]>2*eps:
                    require(truth[chosen]>truth[parent])
    for a,b,e,f in product(vals,vals,err,err):
        require((b+f)-(a+e)>=(b-a)-2*eps)
    begin('grammar_dilution', 'Uniform independent sampling with replacement, candidate counts 1..16, budgets 0..10, exactly one useful candidate.')
    for budget in range(11):
        last=F(1)
        for n in range(1,17):
            hit=1-(1-F(1,n))**budget
            require(0<=hit<=1)
            require(hit<=last)
            last=hit
    begin('amortization_and_ceiling', 'Integer startup cost 0..10, positive rational saving 1/4..8/4, 0..20 uses; score interval [0,1] with gamma 1/k for k=1..20; 30 summable increments.')
    for cost,d,n in product(range(11),[F(i,4) for i in range(1,9)],range(21)):
        require((n*d-cost>0)==(F(n)>F(cost)/d))
    for k in range(1,21):
        require((k+1)*F(1,k)>1)
        require(k*F(1,k)==1)
    total=F(0)
    for t in range(1,31):
        old=total;total+=F(1,2**t)
        require(old<total<1)
    begin('conditional_lineage_budget', 'Three rounds with error caps (1/4,1/8,1/16), all 128 history-dependent hazard choices of either zero or that cap.')
    deltas=(F(1,4),F(1,8),F(1,16))
    nodes=[(t,history) for t in range(3) for history in product((0,1),repeat=t)]
    for switches in product((0,1),repeat=len(nodes)):
        hazard={node:deltas[node[0]]*on for node,on in zip(nodes,switches)}
        probs={():F(1)}
        for t in range(3):
            nxt={}
            for history,p in probs.items():
                a=hazard[t,history]
                nxt[history+(0,)]=p*(1-a);nxt[history+(1,)]=p*a
            probs=nxt
        require(sum(probs.values())==1)
        require(sum(p for hist,p in probs.items() if any(hist))<=sum(deltas))

def brute_kernel(actions,safe):
    """Union of safe starts across all deterministic stationary action choices."""
    n=len(actions);good=set()
    choices=[tuple(range(len(actions[z]))) or (None,) for z in range(n)]
    for policy in product(*choices):
        for start in safe:
            todo=[start];seen=set();okay=True
            while todo:
                z=todo.pop()
                if z in seen:continue
                seen.add(z)
                if z not in safe or policy[z] is None:okay=False;break
                todo.extend(s for s,_ in actions[z][policy[z]].outcomes)
            if okay:good.add(start)
    return frozenset(good)

def test_progress():
    begin('recursive_progress_vs_policy_enumeration', 'Two states, two actions per state, all nonempty successor subsets, action-constant progress marks 0 or 1: 1296 models; three nonempty safe sets; horizons and targets 0..2.')
    subsets=[(0,),(1,),(0,1)]
    specs=[tuple((s,p) for s in subset) for subset in subsets for p in (0,1)]
    for packed in product(specs,repeat=4):
        actions=tuple(tuple(Attempt(f'a{i}',packed[2*z+i]) for i in range(2)) for z in range(2))
        for safe in powerset_nonempty(2):
            kernel,table,policy=recursive_progress(actions,safe,2,2)
            require(kernel==brute_kernel(actions,safe))
            @lru_cache(None)
            def can(z,h,k):
                if z not in kernel:return False
                if h==0:return k==0
                return any(all(can(s,h-1,max(0,k-p)) for s,p in a.outcomes) for a in actions[z])
            for h,k,z in product(range(3),range(3),range(2)):
                require((z in table[h,k])==can(z,h,k))
                if h and z in table[h,k]:
                    chosen=actions[z][policy[z,h,k]]
                    require(all(s in table[h-1,max(0,k-p)] for s,p in chosen.outcomes))
    begin('retry_and_dead_end_controls', 'A rejection self-loop with a possible marked successor, and a locally safe transition into a state with no safe continuation; horizons 0..6.')
    retry=((Attempt('try',((0,0),(1,1))),),(Attempt('stay',((1,0),)),))
    for h in range(7):
        k,w,_=recursive_progress(retry,frozenset({0,1}),h,1)
        require(k==frozenset({0,1}))
        require(0 not in w[h,1])
    dead=((Attempt('bad_future',((1,1),)),),(Attempt('exit',((2,0),)),),())
    require(not recursive_progress(dead,frozenset({0,1}),3,1)[0])
    # A genuine two-event chain followed by safe idling.
    chain=((Attempt('first',((1,1),)),),(Attempt('second',((2,1),)),),(Attempt('idle',((2,0),)),))
    kernel,w,policy=recursive_progress(chain,frozenset({0,1,2}),2,2)
    require(0 in w[2,2]);require(0 not in w[1,2]);require(1 in w[1,1])
    require(kernel==frozenset({0,1,2}))
    rejected(lambda:recursive_progress(((Attempt('x',()),),),frozenset({0}),1,1))

def test_continuation():
    begin('operation_continuation', 'Three-register F_5 instrument, all 125 states, every word of H/W/J of length at most four, q=(a+b,b,c), explicit reduced updates.')
    for state in product(range(5),repeat=3):
        for length in range(5):
            for word in product(range(3),repeat=length):
                x=state;z=((x[0]+x[1])%5,x[1],x[2])
                for op in word:
                    a,b,c=x;s,t,u=z
                    if op==0:x=((a+b)%5,b,c);z=((s+t)%5,t,u)
                    elif op==1:x=(b,a,c);z=(s,(s-t)%5,u)
                    else:x=((a+c)%5,b,c);z=((s+u)%5,t,u)
                require(z==((x[0]+x[1])%5,x[1],x[2]))
                require(z[0]==(x[0]+x[1])%5)

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output',type=Path,default=ROOT/'validation'/'finite_checks.json')
    args=parser.parse_args()
    started=datetime.now(timezone.utc).isoformat();clock=time.perf_counter()
    for test in (test_discrimination,test_partition,test_synthesis,test_cells_and_transfer,
                 test_rejections,test_error_and_resources,test_progress,test_continuation):
        test()
    result={'status':'PASS','started_at':started,'runtime_seconds':time.perf_counter()-clock,
            'python':sys.version,'platform':platform.platform(),'arithmetic':'integers, finite sets, fractions.Fraction',
            'randomness':False,'group_count':len(GROUPS),'assertion_count':sum(g['assertions'] for g in GROUPS),
            'groups':GROUPS,'non_claims':['Not neural training or a demonstration of general intelligence.',
            'Not an empirical self-improving compiler. The compiler and model family are supplied.',
            'Finite checks support these implementations; general results rest on the prose proofs.',
            'Project-authored cross-checks are not independent external validation.']}
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(result,indent=2)+'\n')
    print(f"PASS: {result['group_count']} groups, {result['assertion_count']:,} exact assertions in {result['runtime_seconds']:.3f}s")

if __name__=='__main__':main()
