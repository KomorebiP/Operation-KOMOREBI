"""Exact nodal boundary controls for the written compactness proof. Author: Komorebi P.

Exhausts 3^5 assignments on ONE declared graph, not all RLC topologies.
The nodal implementation below is separate from the retained certificate kernels.
"""
from fractions import Fraction as F
from itertools import product
import json

EDGES = [(0,1,'R'),(0,2,'R'),(1,2,'R'),(0,2,'L'),(1,2,'C')]
SAMPLES = [F(1,2), F(1), F(2)]


def response(states, s, epsilon=None):
    parent = list(range(3))
    def find(j):
        while parent[j] != j:
            j = parent[j]
        return j
    if epsilon is None:
        for state,(u,v,_) in zip(states, EDGES):
            if state == 'short':
                parent[find(u)] = find(v)
    if find(0) == find(1):
        return F(-1)
    branches = []
    for index,(state,(u,v,kind)) in enumerate(zip(states, EDGES)):
        if epsilon is None and state in {'open','short'}:
            continue
        k = F(index+2,index+3) if state == 'finite' else epsilon if state == 'open' else 1/epsilon
        y = k*(s if kind == 'C' else 1/s if kind == 'L' else 1)
        u,v = find(u),find(v)
        if u != v:
            branches.append((u,v,y))
    reached = {find(1)}
    while True:
        more = reached | {v for u,v,_ in branches if u in reached} | {u for u,v,_ in branches if v in reached}
        if more == reached:
            break
        reached = more
    if find(0) not in reached:
        return F(1)
    nodes = sorted(reached-{find(0)})
    ix = {u:i for i,u in enumerate(nodes)}
    A = [[F(0)]*(len(nodes)+1) for _ in nodes]
    for u,v,y in branches:
        for a,b in ((u,v),(v,u)):
            if a in ix:
                A[ix[a]][ix[a]] += y
                if b in ix:
                    A[ix[a]][ix[b]] -= y
    A[ix[find(1)]][ix[find(1)]] += 1
    A[ix[find(1)]][-1] = 1
    for col in range(len(nodes)):
        pivot = next(i for i in range(col,len(nodes)) if A[i][col])
        A[col],A[pivot] = A[pivot],A[col]
        factor = A[col][col]
        A[col] = [v/factor for v in A[col]]
        for row in range(len(nodes)):
            if row != col:
                factor = A[row][col]
                A[row] = [v-factor*w for v,w in zip(A[row],A[col])]
    return 2*A[ix[find(1)]][-1]-1


def main():
    assert response(['open']*5,F(1)) == 1
    assert response(['short']*5,F(1)) == -1
    counts = 0
    largest_ratio = F(0)
    for states in product(('open','finite','short'),repeat=5):
        for s in SAMPLES:
            boundary = response(states,s)
            assert -1 <= boundary <= 1
            for epsilon in (F(1,17),F(1,101)):
                finite = response(states,s,epsilon)
                error_sum = F(0)
                for state,(_,_,kind) in zip(states,EDGES):
                    phi = s if kind == 'C' else 1/s if kind == 'L' else F(1)
                    if state == 'open':
                        error_sum += epsilon*phi/(1+epsilon*phi)
                    elif state == 'short':
                        error_sum += epsilon/(epsilon+phi)
                error = abs(finite-boundary)
                assert error <= 2*error_sum
                if error_sum:
                    largest_ratio = max(largest_ratio,error/(2*error_sum))
                counts += 1
    print(json.dumps({'status':'PASS','graph_edges':EDGES,'assignments':3**5,
        'positive_real_samples':list(map(str,SAMPLES)),'regularization_values':['1/17','1/101'],
        'exact_boundary_comparisons':counts,'maximum_error_to_proved_bound_ratio':str(largest_ratio),
        'scope':'One five-edge graph with floating components, parallel R/L edges, opens and shorts; not an all-topology enumeration'},indent=2))


if __name__ == '__main__':
    if not __debug__:
        raise RuntimeError('Assertions must remain enabled')
    main()
