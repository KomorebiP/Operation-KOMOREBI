"""Repair-relative streaming bounds from checked exact fractional cover weights.

The scope is total immutable binary experiments, unit action costs, arbitrary
fixed repair-success sets, and a finite query horizon. Weight construction is
separate from validity checking. No claim to solve fractional cover optimally.
"""
from __future__ import annotations
from collections import Counter
from fractions import Fraction as Q
from itertools import combinations
from typing import Iterable
from repair_calculus import Problem, Experiment, Repair, Tree, check_tree, tree_to_dict


def verify_weights(p:Problem,weights:Iterable[Q])->tuple[tuple[Q,...],dict]:
    raw=tuple(weights)
    if len(raw)!=p.n or any(type(v) not in (int,Q) for v in raw):
        raise ValueError('Exactly one rational weight per state is required.')
    w=tuple(Q(v) for v in raw);count=Counter()
    if any(v<0 for v in w):raise ValueError('Negative weights invalidate monotone prefix bounds.')
    for e in p.experiments:
        if e.cost!=1:raise ValueError('This reference scope uses unit-cost experiments.')
        for x,row in enumerate(e.transitions):
            count['scope_model_reads']+=1
            if row is None or row[0]!=x or row[1] not in (0,1):
                raise ValueError('Weighted certificate requires total immutable binary queries.')
    loads=[]
    for r in p.repairs:
        if r.cost!=1:raise ValueError('This reference scope uses unit-cost repairs.')
        load=Q(0)
        for x in sorted(r.good):load+=w[x];count['repair_weight_entries']+=1
        if load>1:raise ValueError('A repair covers more than one certified weight unit.')
        loads.append(str(load))
    return w,{'counters':dict(count),'repair_loads':loads}


def checked_greedy_weights(p:Problem)->tuple[tuple[Q,...],dict]:
    """A supplied constructive rule, not a learned or optimal dual solver.

    Raise a coordinate by the minimum slack of every repair containing it. This
    maintains all constraints. An uncovered state is assigned weight one; any
    nonnegative weight there is feasible, and one is a conservative finite choice.
    """
    w=[Q(0)]*p.n;loads=[Q(0)]*len(p.repairs);count=Counter()
    for x in range(p.n):
        containing=[]
        for j,r in enumerate(p.repairs):
            count['constructor_membership_checks']+=1
            if x in r.good:containing.append(j)
        amount=min((1-loads[j] for j in containing),default=Q(1))
        w[x]=amount
        for j in containing:loads[j]+=amount;count['constructor_load_updates']+=1
    result,verified=verify_weights(p,w)
    return result,{'construction':dict(count),'verification':verified,
                   'total_mass':str(sum(result,Q(0))),
                   'claim':'Feasible lower-bound certificate, not necessarily an optimal weight assignment.'}


def ordered_weighted_search(p:Problem,horizon:int,weights:Iterable[Q],
                            streaming:bool=True,support:Iterable[int]|None=None)->tuple[Tree|None,dict]:
    if type(horizon) is not int or horizon<0:raise ValueError('Nonnegative finite horizon required.')
    states=tuple(sorted(set(range(p.n) if support is None else support)))
    if not states or not set(states)<=set(range(p.n)):raise ValueError('Invalid support.')
    w,scope=verify_weights(p,weights);counts=Counter()
    def mass(xs):
        total=Q(0)
        for x in xs:total+=w[x];counts['weight_additions']+=1
        return total
    def solve(xs,depth):
        counts['support_visits']+=1;ss=frozenset(xs)
        for ri,r in enumerate(p.repairs):
            counts['repair_subset_tests']+=1
            if ss<=r.good:return Tree('repair',ri)
        if depth==0:return None
        counts['capacity_comparisons']+=1
        if mass(xs)>2**depth:return None
        cap=Q(2**(depth-1))
        for ei,e in enumerate(p.experiments):
            counts['roots_started']+=1
            sides=[[],[]];sums=[Q(0),Q(0)];rejected=False
            for j,x in enumerate(xs):
                row=e.transitions[x];counts['search_model_reads']+=1
                if row is None:raise AssertionError('Checked scope changed.')
                b=row[1];sides[b].append(x);sums[b]+=w[x];counts['weight_additions']+=1
                if streaming:
                    counts['capacity_comparisons']+=1
                    if sums[b]>cap:
                        counts['rejected_prefixes']+=1
                        counts['rows_skipped']+=len(xs)-j-1
                        rejected=True;break
            if rejected:continue
            counts['capacity_comparisons']+=2
            if not sides[0] or not sides[1] or sums[0]>cap or sums[1]>cap:continue
            left=solve(tuple(sides[0]),depth-1)
            if left is None:continue
            right=solve(tuple(sides[1]),depth-1)
            if right is not None:return Tree('query',ei,((0,left),(1,right)))
        return None
    tree=solve(states,horizon)
    checked=None
    if tree is not None:
        cost,size=check_tree(p,states,tree,horizon)
        checked={'work':str(cost),'storage':size}
        # check_tree has both support reconstruction and episode replay. Count
        # their model accesses independently of the search's own counter.
        def check_reads(node,xs):
            if node.kind=='repair':return 0
            e=p.experiments[node.index];bs={}
            for x in xs:bs.setdefault(e.transitions[x][1],[]).append(x)
            return 2*len(xs)+sum(check_reads(c,bs[o]) for o,c in node.children)
        counts['witness_model_reads']=check_reads(tree,states)
    return tree,{'status':'success' if tree is not None else 'infeasible_within_horizon',
                'horizon':horizon,'streaming':streaming,'scope':scope,'counters':dict(counts),
                'witness':checked,'weights':list(map(str,w)),
                'claim':'First valid ordered depth-bounded tree, not an execution/storage Pareto optimum.'}


def paired_repair_problem(groups:int,group_size:int=2)->Problem:
    if groups<1 or groups&(groups-1) or group_size<1:raise ValueError('Power-of-two groups and positive size required.')
    n=groups*group_size
    qs=[Experiment(f'eq_{i}',Q(1),tuple((x,int(x==i)) for x in range(n))) for i in range(n)]
    qs += [Experiment(f'group_bit_{b}',Q(1),tuple((x,((x//group_size)>>b)&1) for x in range(n)))
           for b in range((groups-1).bit_length())]
    repairs=tuple(Repair(f'repair_group_{g}',Q(1),frozenset(range(g*group_size,(g+1)*group_size))) for g in range(groups))
    return Problem(n,tuple(qs),repairs)
