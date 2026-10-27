"""Exact finite models for the Paper III visual appendix.

All mathematical data use integers, rational numbers, or symbolic polynomials.
Plotting coordinates are a separate display layer. No theorem in the original
Lean contract is changed or reverified by this module.
"""
from __future__ import annotations
from dataclasses import dataclass
from itertools import product
from typing import Callable, Iterable, Mapping, Sequence
import sympy as sp

@dataclass(frozen=True)
class Edge:
    name: str
    source: int
    target: int
    coefficient: sp.Expr | int


def edge_matrix(vertices: int, edge: Edge) -> sp.Matrix:
    if vertices <= 0 or not (0 <= edge.source < vertices and 0 <= edge.target < vertices):
        raise ValueError('Endpoints must belong to a nonempty finite packet type.')
    out = sp.zeros(vertices)
    out[edge.target, edge.source] = edge.coefficient
    return out


def transfer(vertices: int, edges: Sequence[Edge]) -> sp.Matrix:
    return sum((edge_matrix(vertices, e) for e in edges), sp.zeros(vertices))


def composable(word: Sequence[Edge]) -> bool:
    return all(a.target == b.source for a, b in zip(word, word[1:]))


def word_operator(vertices: int, word: Sequence[Edge]) -> sp.Matrix:
    result = sp.eye(vertices)
    for edge in word:
        result = edge_matrix(vertices, edge) * result
    return result


def word_coefficient(word: Sequence[Edge]) -> sp.Expr:
    value = sp.Integer(1)
    for e in word:
        value = sp.sympify(e.coefficient) * value
    return value


def enumerate_walk_matrix(vertices: int, edges: Sequence[Edge], length: int) -> sp.Matrix:
    """Independent endpoint accumulation, not matrix multiplication."""
    if length < 0:
        raise ValueError('Word length must be nonnegative.')
    if length == 0:
        return sp.eye(vertices)
    out = sp.zeros(vertices)
    for word in product(edges, repeat=length):
        if composable(word):
            out[word[-1].target, word[0].source] += word_coefficient(word)
    return out


def parallel_model():
    edges = (Edge('a', 0, 1, 2), Edge('b', 0, 1, -1),
             Edge('c', 1, 2, 3), Edge('d', 2, 0, 1))
    return {'edges': edges, 'T': transfer(3, edges)}


def diamond_model():
    edges = (Edge('a', 0, 1, 1), Edge('b', 0, 2, 1),
             Edge('c', 1, 3, 1), Edge('d', 2, 3, -1))
    return {'edges': edges, 'T': transfer(5, edges),
            'unsigned': transfer(5, tuple(Edge(e.name,e.source,e.target,1) for e in edges))}


def noncommutative_model():
    a=sp.Matrix([[1,1],[0,1]]); b=sp.Matrix([[1,0],[1,1]])
    le=sp.zeros(6);lf=sp.zeros(6)
    le[2:4,0:2]=a;lf[4:6,2:4]=b
    return {'A':a,'B':b,'BA':b*a,'AB':a*b,'Le':le,'Lf':lf}


def rectangular_model():
    a=sp.Matrix([[1,0],[2,1],[0,3]])
    b=sp.Matrix([[1,-1,2],[0,1,1]])
    c=sp.Matrix([[2,-1]])
    return {'A':a,'B':b,'C':c,'BA':b*a,'CBA':c*b*a,
            'contributions':[[c[0,j]*b[j,k]*a[k,i] for j in range(2) for k in range(3)] for i in range(2)]}


def frame_model():
    frames=[sp.eye(2), sp.Matrix([[1,1],[0,1]]),sp.Matrix([[2,0],[1,1]])]
    vector=sp.Matrix([3,2]);j={(b,a):frames[b].inv()*frames[a] for b in range(3) for a in range(3)}
    return {'F':frames,'x':vector,'J':j,'coordinates':[f.inv()*vector for f in frames]}


def nonlinear_model():
    x,y,u,v=sp.symbols('x y u v')
    f=sp.Matrix([x+y,x*y])
    a=lambda z:sp.Matrix([z[0],z[1]+z[0]**2])
    inv=lambda z:sp.Matrix([z[0],z[1]-z[0]**2])
    fb=a(f.subs({x:u,y:v-u**2},simultaneous=True)).applyfunc(sp.expand)
    return {'x':x,'y':y,'u':u,'v':v,'F':f,'A':a,'S':inv,'Fb':fb}


def scalar_connection(reverse=sp.Rational(1,5)):
    gamma={(a,a):sp.Integer(1) for a in range(3)}
    gamma.update({(1,0):sp.Integer(2),(0,1):sp.Rational(1,2),
                  (2,1):sp.Integer(3),(1,2):sp.Rational(1,3),
                  (2,0):sp.Integer(5),(0,2):reverse})
    return gamma


def loop(gamma: Mapping, a: int,b: int,c: int):
    return gamma[a,c]*gamma[c,b]*gamma[b,a]


def defect(gamma: Mapping,a: int,b: int,c: int):
    return gamma[c,b]*gamma[b,a]-gamma[c,a]


def shear_model():
    h=sp.Matrix([[1,1],[0,1]])
    diag=sp.diag(2,1);mix=sp.Matrix([[1,0],[1,1]])
    p=[sp.diag(1,0),sp.diag(0,1)]
    return {'H':h,'Ob':h-sp.eye(2),'D':diag,'G':mix,'P':p,
            'Hd':diag*h*diag.inv(),'Hm':mix*h*mix.inv(),
            'Q':[mix*z*mix.inv() for z in p]}


def flat_model():
    g=[sp.Integer(1),sp.Integer(2),sp.Integer(3)]
    return {'G':g, 'gamma':{(b,a):g[b]/g[a] for b in range(3) for a in range(3)}}


def block_model():
    h=sp.Matrix([[1,2,0],[0,1,3],[0,0,1]])
    ps=[sp.diag(*(1 if k==i else 0 for k in range(3))) for i in range(3)]
    ob=h-sp.eye(3)
    return {'H':h,'Ob':ob,'P':ps,'blocks':[[p*ob*q for q in ps] for p in ps]}


def candidate_residual(x):
    return sp.Matrix([x*x-1,x-1])


# Tree syntax is immutable tuples, so the data can be inspected without a DSL runtime.
# ('input', label), ('constant', value), ('unary', symbol, child),
# ('binary', symbol, left, right).
Tree = tuple

def inputs(tree: Tree) -> frozenset[str]:
    kind=tree[0]
    if kind=='input': return frozenset([tree[1]])
    if kind=='constant': return frozenset()
    if kind=='unary': return inputs(tree[2])
    if kind=='binary': return inputs(tree[2]) | inputs(tree[3])
    raise ValueError(f'Unknown tree constructor {kind!r}')


def evaluate(tree: Tree, env: Mapping[str,sp.Expr|int],
             unary: Mapping[str,Callable]|None=None,
             binary: Mapping[str,Callable]|None=None):
    unary={'square':lambda x:x*x} if unary is None else unary
    binary={'add':lambda x,y:x+y,'sub':lambda x,y:x-y,'mul':lambda x,y:x*y} if binary is None else binary
    kind=tree[0]
    if kind=='input': return env[tree[1]]
    if kind=='constant': return tree[1]
    if kind=='unary': return unary[tree[1]](evaluate(tree[2],env,unary,binary))
    if kind=='binary': return binary[tree[1]](evaluate(tree[2],env,unary,binary),evaluate(tree[3],env,unary,binary))
    raise ValueError(f'Unknown tree constructor {kind!r}')


def tree_model():
    return ('binary','sub',('binary','add',('unary','square',('input','x')),('constant',3)),('input','y'))


def capstone_model():
    a=sp.Matrix([[1,1],[0,1]]);b=sp.Matrix([[1,0],[1,1]]);c=sp.eye(2)
    gamma={(i,i):sp.eye(2) for i in range(3)}
    gamma.update({(1,0):a,(0,1):a.inv(),(2,1):b,(1,2):b.inv(),(2,0):c,(0,2):c.inv()})
    return {'A':a,'B':b,'C':c,'gamma':gamma,'H':b*a,'Ob':b*a-sp.eye(2)}
