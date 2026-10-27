"""Bounded exact checks for three focused reviews; no Lean or analytic replay.

Run from the collection root: python -B verification/audits/soundness-2026-10-27/check_focused.py
All calculations use standard-library integers. The accompanying report gives
the written arguments; these finite checks do not certify whole manuscripts.
"""
from itertools import product
from math import comb
import json


def multiply(a, b):
    out = [0] * (len(a) + len(b) - 1)
    for i, x in enumerate(a):
        for j, y in enumerate(b):
            out[i + j] += x * y
    return out


def row(m, s, k):
    out = [comb(s, j) for j in range(s + 1)]
    base = [0] + [comb(m, j) for j in range(1, m + 1)]
    for _ in range(k):
        out = multiply(out, base)
    return out


def difference(a, k, s=0, m=1):
    return sum((-1)**(k-j)*comb(k, j)*a[s+m*j] for j in range(k+1))


def euler_checks():
    e = [1]
    for n in range(1, 48):
        e.append(-sum(comb(2*n, 2*j)*e[j] for j in range(n)))
    assert e[:5] == [1, -1, 5, -61, 1385]
    counts = {'sequence_transfers': 0, 'composition_rows': 0, 'prime_rows': 0}
    for a in [e, [(n**3-7*n+3)*(-1)**n for n in range(48)]]:
        c = [difference(a, k) for k in range(48)]
        for m in range(1, 6):
            for s in range(m):
                for k in range(7):
                    assert sum(x*c[r] for r, x in enumerate(row(m,s,k))) == difference(a,k,s,m)
                    counts['sequence_transfers'] += 1
    for m,n in product(range(1,4), repeat=2):
        for s,t,k in product(range(m),range(n),range(5)):
            composed = [0]*(m*n*k+m*t+s+1)
            for j, x in enumerate(row(n,t,k)):
                for r, y in enumerate(row(m,s,j)):
                    composed[r] += x*y
            assert composed == row(m*n,m*t+s,k)
            counts['composition_rows'] += 1
    for p in [2,3,5,7,11]:
        a = row(p,0,1)
        assert a[0] == 0 and a[-1] == 1
        assert all(x % p == 0 for x in a[1:-1])
        counts['prime_rows'] += 1
    assert sum(counts.values()) == 395
    # Explicit constant/identity boundaries and the retained signed-Euler control.
    assert row(1,0,0) == [1] and row(1,0,1) == [0,1]
    assert [difference(e,1,0,m) for m in [1,2,4]] == [-2,4,1384]
    return counts


def eisenstein_mul(x,y):
    a,b=x; c,d=y
    return (a*c-b*d,a*d+b*c-b*d)  # omega^2 = -omega - 1


def cyclic_mul(x,y):
    out=[(0,0)]*7
    for i,a in enumerate(x):
        for j,b in enumerate(y):
            k=(i+j)%7; c,d=eisenstein_mul(a,b)
            out[k]=(out[k][0]+c,out[k][1]+d)
    return out


def gauss_checks():
    chi=[(0,0),(1,0),(0,1),(-1,-1),(-1,-1),(0,1),(1,0)]
    expected=[(12,18)]+[(-2,-3)]*6  # 7J - J*(1+z+...+z^6)
    for r in range(1,7):
        g=[(0,0)]*7
        for k in range(1,7):
            g[(r*k)%7]=chi[k]
        assert cyclic_mul(cyclic_mul(g,g),g) == expected
    assert tuple(map(sum,zip(*expected))) == (0,0)
    assert expected != [(14,21)]+[(0,0)]*6  # 7J alone is not the group-ring result.
    M=((0,1,0),(-4,2,15),(-1,0,4))
    H=((4,-4,15),(-4,1,0),(15,0,0)); u=(1,2,4)
    kernel=[]
    for a in product(range(7), repeat=3):
        if all((sum(M[i][j]*a[j] for j in range(3))-2*a[i])%7 == 0 for i in range(3)):
            kernel.append(a)
            assert sum(u[i]*H[i][j]*a[j] for i in range(3) for j in range(3))%7 == 0
    assert len(kernel) == 7
    return {'nonzero_character_slices':6,'ambient_vectors':343,'fixed_vectors':7,
            'group_ring_cube_coefficients_in_basis_1_omega':expected,
            'specialization_required':'1 + z + ... + z^6 = 0 at a primitive seventh root'}


def retraction_checks():
    # Encode (x,y) by 2*x+y. A scalar h determines P(x,y)=(h,h).
    additive=[]; boolean=[]; equivariant=[]
    for h in product(range(2),repeat=4):
        if h[0] != 0 or h[3] != 1:
            continue
        if not all(h[a^b] == h[a]^h[b] for a,b in product(range(4),repeat=2)):
            continue
        additive.append(h)
        if all(h[a&b] == (h[a]&h[b]) for a,b in product(range(4),repeat=2)):
            boolean.append(h)
        if h[1] == h[2]:
            equivariant.append(h)
    assert len(additive) == len(boolean) == 2 and not equivariant
    return {'all_scalar_maps':16,'additive_retractions':2,'boolean_retractions':2,
            'swap_equivariant_retractions':0}


if __name__ == '__main__':
    print(json.dumps({'status':'PASS','euler':euler_checks(),'gauss':gauss_checks(),
                     'two_world':retraction_checks(),
                     'scope':'Exact finite controls only; no full manuscript, analytic-gamma, novelty, Lean, or hardware certification.'},indent=2))
