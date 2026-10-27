"""Exact finite access-restricted coding; small-instance graph solver.

The graph represents structural zero-error constraints. For approximate repair,
use the separate exhaustive weighted partition routine. A graph's chromatic
number alone does not determine the full Bayes-error tradeoff.
"""
from __future__ import annotations
from dataclasses import dataclass
from fractions import Fraction
from collections import defaultdict
from itertools import product
from typing import Hashable, Sequence


@dataclass(frozen=True)
class AccessGraph:
    values: tuple[Hashable,...]
    neighbors: tuple[frozenset[int],...]
    state_vertices: tuple[int,...]
    impossible_witness: tuple[int,int] | None


def build_access_graph(observations: Sequence[Hashable],targets: Sequence[Hashable],
                       access: Sequence[Hashable]) -> AccessGraph:
    r,f,u=tuple(observations),tuple(targets),tuple(access)
    if not r or len(r)!=len(f) or len(r)!=len(u):
        raise ValueError('nonempty state lists must have equal lengths')
    for v in r+f+u:
        hash(v)
    vals=tuple(dict.fromkeys(u)); ix={v:i for i,v in enumerate(vals)}
    vertices=tuple(ix[v] for v in u)
    neighbors=[set() for _ in vals]
    witness=None
    for i in range(len(r)):
        for j in range(i):
            if r[i]==r[j] and f[i]!=f[j]:
                a,b=vertices[i],vertices[j]
                if a==b:
                    witness=(j,i)
                else:
                    neighbors[a].add(b);neighbors[b].add(a)
    return AccessGraph(vals,tuple(frozenset(n) for n in neighbors),vertices,witness)


def optimal_coloring(graph: AccessGraph, *, max_vertices: int=16) -> tuple[int,...] | None:
    """Small exact DSATUR/backtracking solver, with a declared resource guard."""
    if graph.impossible_witness is not None:
        return None
    n=len(graph.values)
    if n>max_vertices:
        raise ValueError('exact coloring resource guard exceeded')
    if not n:
        raise ValueError('empty access graph is outside the nonempty-state model')
    for bound in range(1,n+1):
        colors=[-1]*n
        def search(assigned: int) -> bool:
            if assigned==n:
                return True
            i=max((i for i in range(n) if colors[i]<0),key=lambda i:(
                len({colors[j] for j in graph.neighbors[i] if colors[j]>=0}),len(graph.neighbors[i]),-i))
            forbidden={colors[j] for j in graph.neighbors[i]}
            used=max(colors)+1
            for c in range(min(bound,used+1)):
                if c not in forbidden:
                    colors[i]=c
                    if search(assigned+1):
                        return True
            colors[i]=-1
            return False
        if search(0):
            return tuple(colors)
    raise ArithmeticError('finite graph could not be colored')


def decode_from_coloring(graph: AccessGraph,colors: Sequence[int],
                         observations: Sequence[Hashable],targets: Sequence[Hashable]) -> dict:
    if graph.impossible_witness is not None or len(colors)!=len(graph.values):
        raise ValueError('invalid coloring or inaccessible task')
    if any(type(c) is not int or c<0 for c in colors):
        raise ValueError('colors must be nonnegative integers')
    if len(observations)!=len(graph.state_vertices) or len(targets)!=len(observations):
        raise ValueError('decoder states do not match graph')
    for i,neighbors in enumerate(graph.neighbors):
        if any(colors[i]==colors[j] for j in neighbors):
            raise ValueError('coloring merges confusable access values')
    decoder={}
    for r,f,v in zip(observations,targets,graph.state_vertices):
        key=(r,colors[v])
        if key in decoder and decoder[key]!=f:
            raise ValueError('coloring does not resolve task')
        decoder[key]=f
    return decoder


def restricted_success(observations: Sequence[Hashable],targets: Sequence[Hashable],
                       access: Sequence[Hashable],weights: Sequence[int],
                       message_alphabet: int, *, max_encoders: int=1_000_000) -> tuple[Fraction,tuple[int,...],int]:
    """Exhaustively optimize a small weighted instance over all access-only encoders.

    Decoder is optimized independently in each (observation,message) cell.
    The count includes message relabelings, intentionally useful as an oracle.
    """
    graph=build_access_graph(observations,targets,access)
    w=tuple(weights)
    if len(w)!=len(observations) or any(type(v) is not int or v<0 for v in w) or not sum(w):
        raise ValueError('weights must be nonnegative integers with positive total')
    if type(message_alphabet) is not int or message_alphabet<1:
        raise ValueError('message alphabet must be a positive integer')
    total_encoders=message_alphabet**len(graph.values)
    if total_encoders>max_encoders:
        raise ValueError('encoder enumeration resource guard exceeded')
    best=-1; best_code=None
    for colors in product(range(message_alphabet),repeat=len(graph.values)):
        cells=defaultdict(lambda:defaultdict(int))
        for r,f,v,weight in zip(observations,targets,graph.state_vertices,w):
            cells[r,colors[v]][f]+=weight
        score=sum(max(cell.values()) for cell in cells.values())
        if score>best:
            best=score;best_code=colors
    return Fraction(best,sum(w)),best_code,total_encoders
