"""Symmetry-complete reactive endpoint skeletons. Author: Komorebi P.

Ports 0 and 1 remain fixed. Arbitrary resistors live on the complete retained
vertex graph and are not enumerated as a finite resistor-value grid.
"""
from functools import lru_cache
from itertools import combinations,permutations,product
import json


@lru_cache(maxsize=200000)
def canonical(edges):
    """Minimize over edge permutations, reversals, and first-occurrence labels."""
    C=[e for e in edges if e[0]=='C'];L=[e for e in edges if e[0]=='L']
    best=None
    for pc in permutations(C):
        for pl in permutations(L):
            order=pc+pl
            for reverse in product((False,True),repeat=len(order)):
                labels={0:0,1:1};rows=[]
                for (kind,u,v),flip in zip(order,reverse):
                    if flip:u,v=v,u
                    for node in (u,v):
                        if node not in labels:labels[node]=len(labels)
                    rows.append((kind,labels[u],labels[v]))
                key=tuple(rows)
                if best is None or key<best:best=key
    return best if best is not None else ()


def vertices(edges):
    return max([1]+[v for _,u,v in edges]+[u for _,u,v in edges])+1


def generate(maximum):
    levels=[{()}]
    for q in range(1,maximum+1):
        current=set()
        for old in levels[-1]:
            n=vertices(old)
            positions=list(combinations(range(n),2))+[(u,n) for u in range(n)]+[(n,n+1)]
            for kind in ('C','L'):
                for u,v in positions:
                    current.add(canonical(old+((kind,u,v),)))
        levels.append(current)
    return levels


def no_parallel_same_kind(edges):
    pairs=[(kind,min(u,v),max(u,v)) for kind,u,v in edges]
    return len(pairs)==len(set(pairs))


def brute_key(edges,n):
    """Independent small-universe check by all internal-vertex permutations."""
    best=None
    for internal in permutations(range(2,n)):
        mapping=(0,1)+internal
        key=tuple(sorted((kind,min(mapping[u],mapping[v]),max(mapping[u],mapping[v])) for kind,u,v in edges))
        if best is None or key<best:best=key
    return best


def main():
    levels=generate(4)
    controls=[]
    for n,q in ((6,2),(5,3),(4,4)):
        universe=[(kind,u,v) for kind in ('C','L') for u,v in combinations(range(n),2)]
        labeled={brute_key(edges,n) for edges in product(universe,repeat=q)}
        independent_keys=[brute_key(edges,n) for edges in levels[q] if vertices(edges)<=n]
        assert len(set(independent_keys))==len(independent_keys),(n,q,'duplicate canonical classes')
        # brute_key retains unused internal labels; include all placements of the
        # representative's used nodes into this independently fixed universe.
        covered=set()
        for edges in levels[q]:
            used=vertices(edges)
            if used>n:continue
            for placement in permutations(range(2,n),used-2):
                mapping=(0,1)+placement
                moved=tuple((kind,mapping[u],mapping[v]) for kind,u,v in edges)
                covered.add(brute_key(moved,n))
        assert covered==labeled,(n,q,len(covered),len(labeled))
        controls.append({'vertices':n,'reactive_edges':q,'labeled_placements':len(universe)**q,
            'independent_isomorphism_classes':len(labeled),'status':'PASS'})
    rows=[]
    for q,level in enumerate(levels):
        mixed=[g for g in level if len({e[0] for e in g})==2]
        rows.append({'budget_exact':q,'classes':len(level),'mixed_classes':len(mixed),
            'mixed_without_parallel_same_kind':sum(no_parallel_same_kind(g) for g in mixed),
            'maximum_retained_vertices':max(map(vertices,level))})
    assert any(vertices(g)==10 for g in levels[4])
    print(json.dumps({'status':'PASS','levels':rows,'independent_finite_controls':controls,
        'coverage':'Written induction on deleting one reactive edge; canonicalization keeps both ports fixed. Every retained resistor edge remains available with a continuous positive value.',
        'non_claims':['No resistor-value discretization','No infeasibility proof for mixed RLC skeletons','Finite comparisons alone are not the universal coverage proof']},indent=2))


if __name__=='__main__':
    if not __debug__:raise RuntimeError('Assertions must remain enabled')
    main()
