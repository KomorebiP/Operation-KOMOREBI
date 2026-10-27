#!/usr/bin/env python3
"""Exact finite tests for normalization and retained dyadic group actions.

No floating arithmetic. F9=F3[u]/(u^2+1); omega is represented in Z[omega].
This is a bounded finite surrogate, not an arithmetic type or H5 certificate.
"""
from itertools import product, permutations
from pathlib import Path
import json
import argparse

F = list(product(range(3), repeat=2))
zero = (0, 0)

def add(a, b):
    return ((a[0]+b[0]) % 3, (a[1]+b[1]) % 3)

def mul(a, b):
    return ((a[0]*b[0]-a[1]*b[1]) % 3, (a[0]*b[1]+a[1]*b[0]) % 3)

def tr(a):
    return 2*a[0] % 3

def frob(a):
    return (a[0], -a[1] % 3)

def group_mul(g, h):
    x, y, z = g
    xx, yy, zz = h
    cocycle = 2*(tr(mul(y, xx))-tr(mul(x, yy))) % 3
    return (add(x, xx), add(y, yy), (z+zz+cocycle) % 3)

def act(g, t):
    x, y, z = g
    return add(t, x), (z+tr(mul(y, t))+2*tr(mul(x, y))) % 3

def omega_sum(exponents):
    counts = [0, 0, 0]
    for e in exponents:
        counts[e % 3] += 1
    # omega^2=-1-omega
    return (counts[0]-counts[2], counts[1]-counts[2])

def scalar_trace(g, acting_frob=False, canonical=False):
    exponents = []
    for t in F:
        out, e = act(g, t)
        if acting_frob:
            out = frob(out)
        if out == t:
            exponents.append(e)
    value = omega_sum(exponents)
    return tuple(-x for x in value) if canonical else value

def check_f9_model():
    G = list(product(F, F, range(3)))
    checked = 0
    for g, h in product(G, repeat=2):
        gh = group_mul(g, h)
        # Compare the monomial operators at all nine basis vectors.
        for t in F:
            out_h, e_h = act(h, t)
            out_g, e_g = act(g, out_h)
            assert act(gh, t) == (out_g, (e_h+e_g) % 3)
        checked += 1
    for g in G:
        phi_g = (frob(g[0]), frob(g[1]), g[2])
        for t in F:
            out, e = act(g, frob(t))
            assert (frob(out), e) == act(phi_g, t)
    perm = [F.index(frob(t)) for t in F]
    inversions = sum(perm[i] > perm[j] for i in range(9) for j in range(i+1, 9))
    det_S = (-1)**inversions
    assert det_S == -1 and (-1)**9*det_S == 1
    assert all(frob(frob(t)) == t for t in F)
    assert scalar_trace((zero, zero, 0), True, True) == (-3, 0)
    fixed = [g for g in G if frob(g[0]) == g[0] and frob(g[1]) == g[1]]
    assert len(fixed) == 27
    for g in fixed:
        expected = omega_sum([g[2]]*3) if g[0] == zero and g[1] == zero else (0, 0)
        actual = scalar_trace(g, True, True)
        assert actual == tuple(-x for x in expected)
    # Independent character norm: only the three center elements have trace 9*omega^z.
    support = [g for g in G if scalar_trace(g) != (0, 0)]
    assert support == [(zero, zero, z) for z in range(3)]
    assert 3*9**2 == len(G)
    return {'group_order':len(G), 'representation_dimension':9,
        'multiplication_pairs_checked':checked, 'basis_vectors_per_pair':9,
        'frobenius_order':2, 'determinant_of_permutation_implementer':det_S,
        'determinant_of_minus_permutation':1, 'canonical_generator_trace':[-3,0],
        'fixed_group_order':27, 'fixed_irrep_dimension':3,
        'glauberman_sign_in_this_model':-1,
        'central_character_caveat':'Under the arithmetic diagonal embedding, Tr_F9/F3(z)=2z, so the matched base central character is squared.'}

# Groups of order8 are pairs (a,b), represented by r^a s^b.
# D8: r^4=s^2=1, sr=r^-1s. Q8: r^4=1, s^2=r^2, sr=r^-1s.
E = list(product(range(4), range(2)))

def mul8(g, h, quaternion):
    a,b = g
    c,d = h
    return ((a + (-1)**b*c + (2*b*d if quaternion else 0)) % 4, (b+d) % 2)

def check_dyadic_lifts():
    output = {}
    for quaternion in (False, True):
        name = 'Q8' if quaternion else 'D8'
        mm = lambda a,b: mul8(a,b,quaternion)
        assert all(mm(mm(a,b),c)==mm(a,mm(b,c)) for a,b,c in product(E,repeat=3))
        # The retained center is {(0,0),(2,0)}. Quotient coordinates are (a mod2,b).
        center = {(0,0),(2,0)}
        nonzero = [(1,0),(0,1),(1,1)]
        beta = {zero:zero,nonzero[0]:nonzero[1],nonzero[1]:nonzero[2],nonzero[2]:nonzero[0]}
        quotient = lambda g:(g[0] % 2,g[1])
        autos = []
        for images in permutations(E[1:]):
            f = {(0,0):(0,0), **dict(zip(E[1:],images))}
            if not all(f[mm(g,h)]==mm(f[g],f[h]) for g,h in product(E,repeat=2)):
                continue
            assert f[(2,0)] == (2,0)
            if all(quotient(f[g])==beta[quotient(g)] for g in E):
                autos.append(f)
        q = {str(v):int(mm(v,v)==(2,0)) for v in nonzero}
        # Quotient commutator forms agree, but square maps differ.
        for g,h in product(E,repeat=2):
            assert (mm(g,h)==mm(h,g)) == ((g[0]*h[1]-h[0]*g[1]) % 2 == 0)
        output[name] = {'lifts_of_prescribed_quotient_3cycle':len(autos),
                       'square_exponents_on_nonzero_cosets':q}
        if quaternion:
            assert len(autos)==4
            assert all(all(f[f[f[g]]]==g for g in E) for f in autos)
        else:
            assert not autos
    return output

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    result = {'status':'PASS', 'arithmetic_domain':'Exact F3/F9 and integer pairs for Z[omega]',
              'f9_frobenius':check_f9_model(), 'dyadic_lift_boundary':check_dyadic_lifts(),
              'non_claims':['No arithmetic kappa attachment is inferred.',
                            'No H5 or original Claim16.2 instance is supplied.',
                            'Finite complex cochain correction does not create an automorphism of a prescribed D8 extension.']}
    out = args.output
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result,indent=2))
