"""Exact worked models for the Paper II visual appendix.

All mathematical coefficients use integers or SymPy exact rationals. Plot locations
may be floating-point renderings of these data; they are not proof certificates.
Finite examples do not extend the inherited Lean formalization contract.
"""
from __future__ import annotations
from collections import Counter
from itertools import product
from math import prod
import sympy as sp


def residue_projector(size: int, modulus: int, residue: int) -> sp.Matrix:
    if size < 0 or modulus <= 0 or not 0 <= residue < modulus:
        raise ValueError('Require size >= 0, modulus > 0 and 0 <= residue < modulus.')
    return sp.diag(*[int(i % modulus == residue) for i in range(size)]) if size else sp.zeros(0)


def phase_order(size: int, modulus: int) -> list[int]:
    if size < 0 or modulus <= 0:
        raise ValueError('Invalid size or modulus.')
    return [i for r in range(modulus) for i in range(r, size, modulus)]


def reorder(size: int, modulus: int) -> sp.Matrix:
    return sp.eye(size)[phase_order(size, modulus), :]


def cyclic_shift(size: int, amount: int = 1) -> sp.Matrix:
    if size <= 0:
        raise ValueError('A cyclic carrier must be nonempty.')
    return sp.Matrix(size, size, lambda i, j: int(i == (j+amount) % size))


def refinement_model() -> dict:
    n=8
    s=cyclic_shift(n)
    t=sp.eye(n)+2*s+s**2
    p2,p4,p8=(reorder(n,m) for m in (2,4,8))
    j=p4*p2.T
    return {'T':t,'P2':p2,'P4':p4,'P8':p8,'J':j,
            'T2':p2*t*p2.T,'T4':p4*t*p4.T,
            'order2':phase_order(n,2),'order4':phase_order(n,4)}


def fourier_table_mod7() -> list[list[int]]:
    # N=3, omega=2, omega^{-1}=4, 3^{-1}=5, all in F_7.
    return [[5*sum(pow(4,j*k,7)*pow(2,r*k,7) for k in range(3)) % 7
             for r in range(3)] for j in range(3)]


def crt_grid() -> list[list[int]]:
    return [[next(n for n in range(12) if n % 4 == a and n % 3 == b)
             for a in range(4)] for b in range(3)]


def weighted_model() -> dict:
    a=sp.Matrix([[0,2],[0,0]])
    b=sp.Matrix([[0,0],[4,0]])
    d=sp.Matrix([[1,1],[0,1]])
    return {'a':a,'b':b,'A':a+b,'D':d,'Dinv':d.inv(),'T':d*(sp.eye(2)+a+b)}


def weighted_terms(depth: int) -> list[dict]:
    """Written operator words a_1 ... a_n. Rightmost factor acts first."""
    if depth <= 0:
        raise ValueError('Positive precision depth required.')
    m=weighted_model(); ans=[]
    for length in range(depth):
        for word in product('ab',repeat=length):
            wt=sum(1 if e=='a' else 2 for e in word)
            if wt>=depth:
                continue
            value=sp.eye(2)
            for e in word:
                value=value*m[e]
            ans.append({'word':''.join(word),'length':length,'weight':wt,
                        'product':value,'signed':(-1)**length*value})
    return ans


def pruned_inverse(depth: int) -> tuple[sp.Matrix,sp.Matrix]:
    terms=weighted_terms(depth)
    total=sum((t['signed'] for t in terms),sp.zeros(2))
    return total,total*weighted_model()['Dinv']


def matrix_mod(a: sp.Matrix, modulus: int) -> sp.Matrix:
    if modulus <= 0:
        raise ValueError('Positive modulus required.')
    if any(not x.is_Integer for x in a):
        raise ValueError('matrix_mod takes integral entries, not rational inverses.')
    return a.applyfunc(lambda x: int(x) % modulus)


# Distinct edge identities matter. Edges a and b have the same endpoints/weight.
WALK_EDGES=(('l',0,0,1),('a',0,1,2),('b',0,1,2),('r',1,0,1))


def walk_counts(max_weight: int, start: int=0, target: int=1) -> list[int]:
    if max_weight < 0 or start not in (0,1) or target not in (0,1):
        raise ValueError('Invalid weight or vertex.')
    counts=[[0]*(max_weight+1) for _ in range(2)]
    counts[target][0]=1
    for n in range(1,max_weight+1):
        for s in range(2):
            counts[s][n]=sum(counts[v][n-w] for _,u,v,w in WALK_EDGES if u==s and w<=n)
    return counts[start]


def enumerate_walks(weight: int,start: int=0,target: int=1) -> list[str]:
    if weight < 0:
        raise ValueError('Nonnegative weight required.')
    result=[]
    def visit(v:int, remaining:int, word:str)->None:
        if remaining==0:
            if v==target: result.append(word)
            return
        for name,u,nxt,w in WALK_EDGES:
            if u==v and w<=remaining: visit(nxt,remaining-w,word+name)
    visit(start,weight,'')
    return result


def zeta_model() -> dict:
    t=sp.Symbol('t')
    a=sp.Matrix([[t,2*t**2],[t,0]])
    q=sp.expand((sp.eye(2)-a).det())
    adj=(sp.eye(2)-a).adjugate()
    return {'t':t,'A':a,'Q':q,'adjugate':adj,'Z01':sp.cancel(adj[0,1]/q)}


def sign_model() -> dict:
    a=sp.Matrix([[1,1],[0,-1]])
    ep=(sp.eye(2)+a)/2; em=(sp.eye(2)-a)/2
    return {'A':a,'N':sp.eye(2)+a,'Eplus':ep,'Eminus':em,
            'B':sp.Matrix([[1,-1],[0,2]])}


def padic_weight(a: sp.Matrix,p: int) -> int:
    if not sp.isprime(p):
        raise ValueError('The local denominator weight uses a prime.')
    ans=0
    for x in a:
        den=int(sp.denom(x)); s=0
        while den % p == 0:
            den//=p; s+=1
        ans=max(ans,s)
    return ans


def smith_fibres(p: int, depth: int, weights: tuple[int,...]) -> Counter:
    if p <= 1 or depth < 0 or any(s<0 for s in weights):
        raise ValueError('Require p > 1 and nonnegative depths/weights.')
    modulus=p**depth
    if modulus**len(weights)>200000:
        raise ValueError('Exact exhaustive illustration capped at 200000 inputs.')
    return Counter(tuple((p**s*x)%modulus for s,x in zip(weights,xs))
                   for xs in product(range(modulus),repeat=len(weights)))


def smith_count_formula(p: int,depth: int,weights: tuple[int,...],rhs: tuple[int,...])->int:
    if p <= 1 or depth < 0 or any(s<0 for s in weights) or len(weights)!=len(rhs):
        raise ValueError('Invalid diagonal fibre data.')
    modulus=p**depth
    if any((b%modulus)%(p**min(s,depth)) for s,b in zip(weights,rhs)):
        return 0
    return p**sum(min(s,depth) for s in weights)


def smith_transport_model()->dict:
    m=sp.Matrix([[2,2],[0,4]])
    v=sp.Matrix([[1,-1],[0,1]])
    return {'M':m,'V':v,'D':m*v,'rhs':sp.Matrix([2,4]),'modulus':8}


def finite_convolution(x:list[int],h:list[int])->list[int]:
    if not x or not h: return []
    y=[0]*(len(x)+len(h)-1)
    for i,a in enumerate(x):
        for j,b in enumerate(h): y[i+j]+=a*b
    return y


def signal_model()->dict:
    w=sp.Symbol('w')
    x=[1,2,3,4,5,6]; h=[1,2,1]
    e=sum(a*w**i for i,a in enumerate(x[::2]));o=sum(a*w**i for i,a in enumerate(x[1::2]))
    ht=sp.Matrix([[1+w,2*w],[2,1+w]])
    return {'w':w,'x':x,'h':h,'y':finite_convolution(x,h),'e':e,'o':o,'Hphase':ht,
            'out':(ht*sp.Matrix([e,o])).applyfunc(sp.expand)}


def smith_chart_points()->list[dict]:
    points=[]
    for k in range(8):
        theta=sp.pi*k/4
        g=(sp.cos(theta)+sp.I*sp.sin(theta))/2
        z=sp.simplify((1+g)/(1-g))
        points.append({'k':k,'gamma':sp.expand_complex(g),'z':sp.simplify(sp.expand_complex(z))})
    return points


def defect_model()->dict:
    e=sp.Rational(1,16)
    c=sp.Matrix([[1,e],[0,1]])
    tf=tc=sp.diag(1,2)
    return {'epsilon':e,'C':c,'Tf':tf,'Tc':tc,'Delta':c*tf-tc*c}


def infinity_norm(a:sp.Matrix)->sp.Expr:
    return max((sum(abs(x) for x in a.row(i)) for i in range(a.rows)),default=sp.S(0))
