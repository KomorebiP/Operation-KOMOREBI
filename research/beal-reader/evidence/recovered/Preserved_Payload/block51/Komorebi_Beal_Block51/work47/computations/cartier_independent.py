"""Exact audit over F_7; standard-library only, deterministic, all 49 pairs.

Sparse symbolic expansion in F_7[x,A,B] is checked against an independent
numerical convolution. Smoothness is checked by Euclid in F_7[x]. Point counts
over F_7 and F_49 independently check the expected L-polynomial mod 7.
"""
import json
from collections import Counter
from itertools import product
from pathlib import Path

P = 7

def smul(a, b):
    c = Counter()
    for i, ai in a.items():
        for j, bj in b.items():
            c[tuple(x+y for x, y in zip(i, j))] += ai*bj
    return {i: ai % P for i, ai in c.items() if ai % P}

f = {(6, 0, 0): 1, (3, 0, 1): 3, (1, 1, 0): 5, (0, 0, 2): 5}
cube = smul(smul(f, f), f)
coeff = {n: {i[1:]: ai for i, ai in cube.items() if i[0] == n}
         for n in (5, 6, 12, 13)}
assert coeff == {5: {(2, 1): 1}, 6: {}, 12: {}, 13: {(1, 0): 1}}

def trim(a):
    while a and a[-1] == 0:
        a.pop()
    return a

def remainder(a, b):
    a = trim(a[:])
    while len(a) >= len(b):
        d = len(a)-len(b)
        c = a[-1]*pow(b[-1], -1, P) % P
        for i, bi in enumerate(b):
            a[i+d] = (a[i+d]-c*bi) % P
        trim(a)
    return a

def squarefree(a):
    b = trim([i*a[i] % P for i in range(1, len(a))])
    while b:
        a, b = b, remainder(a, b)
    return len(a) == 1

def dense_mul(a, b):
    c = [0]*(len(a)+len(b)-1)
    for i, ai in enumerate(a):
        for j, bj in enumerate(b):
            c[i+j] = (c[i+j]+ai*bj) % P
    return c

# Pair (a,b) means a+b*u in F_49 with u^2=3; 3 is nonsquare in F_7.
def add(a, b):
    return ((a[0]+b[0]) % P, (a[1]+b[1]) % P)

def mul(a, b):
    return ((a[0]*b[0]+3*a[1]*b[1]) % P,
            (a[0]*b[1]+a[1]*b[0]) % P)

def eval_poly(co, x):
    z = (0, 0)
    for c in reversed(co):
        z = add(mul(z, x), (c, 0))
    return z

def points(co, elements):
    squares = Counter(mul(y, y) for y in elements)
    # Monic sextic has two rational points at infinity in odd characteristic.
    return 2+sum(squares[eval_poly(co, x)] for x in elements)

fp = [(a, 0) for a in range(P)]
fp2 = list(product(range(P), repeat=2))
rows = []
for A, B in product(range(P), repeat=2):
    co = [5*B*B % P, 5*A % P, 0, 3*B % P, 0, 0, 1]
    co3 = dense_mul(dense_mul(co, co), co)
    assert [co3[n] for n in (5, 6, 12, 13)] == [A*A*B % P, 0, 0, A]
    admitted = (A**3+B**5) % P != 0
    sf = squarefree(co)
    assert sf == admitted
    if not admitted:
        continue
    N1, N2 = points(co, fp), points(co, fp2)
    a1 = N1-P-1
    a2 = (N2-P*P-1+a1*a1)//2
    assert (N2-P*P-1+a1*a1) % 2 == 0
    assert a1 % P == 0
    assert a2 % P == -A**3*B % P
    rank1 = 2 if A*B else (1 if A else 0)
    rank2 = 2 if A*B else 0
    rows.append(dict(A=A, B=B, Cartier_rank=rank1, Cartier_square_rank=rank2,
                     N1=N1, N2=N2, L_coefficients=[1, a1, a2, P*a1, P*P]))

counts = Counter((r['Cartier_rank'], r['Cartier_square_rank']) for r in rows)
assert counts == {(2, 2): 30, (1, 0): 6, (0, 0): 6}
result = dict(arithmetic='exact F_7 and F_49', tested_pairs=49,
              smooth_admitted_pairs=len(rows),
              coefficients={'c5': 'A^2 B', 'c6': '0', 'c12': '0', 'c13': 'A'},
              rank_counts={str(k): v for k, v in counts.items()}, rows=rows,
              non_claims=['Does not prove general Galois or Beal assertions.'])
out = Path('verification/cartier_independent_run/result.json')
out.write_text(json.dumps(result, indent=2)+'\n')
print(json.dumps({k: v for k, v in result.items() if k != 'rows'}, indent=2))
