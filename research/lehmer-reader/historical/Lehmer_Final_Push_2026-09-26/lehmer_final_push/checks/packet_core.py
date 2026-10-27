#!/usr/bin/env python3
"""Exact checks for the packet-tree continuation. Standard library only.

The all-depth claim is proved in RESEARCH_NOTE.md. Bounded assertions below
do not prove Lehmer. Invoke with the desired JSON output path as argv[1].
"""
from collections import Counter, defaultdict
from fractions import Fraction
from itertools import combinations, product
from math import comb, isqrt, prod
from pathlib import Path
import json
import sys

PAIRS = list(combinations(range(5), 2))


def shell(n):
    R = isqrt(10*n)
    lanes = [range(-R+(i+R)%5, R+1, 5) for i in range(3)]
    for x, y, z in product(*lanes):
        rem = 10*n-x*x-y*y-z*z
        s = -x-y-z
        disc = 2*rem-s*s
        if disc < 0:
            continue
        d = isqrt(disc)
        if d*d != disc:
            continue
        for root in ((d, -d) if d else (0,)):
            if (s+root)%2:
                continue
            a = (s+root)//2
            b = s-a
            if a%5 == 3 and b%5 == 4:
                yield (x, y, z, a, b)


def shell_brute(n):
    R = isqrt(10*n)
    lanes = [range(-R+(i+R)%5, R+1, 5) for i in range(4)]
    for first in product(*lanes):
        v = first+(-sum(first),)
        if v[4]%5 == 4 and sum(x*x for x in v) == 10*n:
            yield v


def weight(v):
    answer, rem = divmod(prod(v[i]-v[j] for i, j in PAIRS), 288)
    assert rem == 0
    return answer


def involution(v):
    return tuple(-v[-i%5] for i in range(5))


def sector(v, M):
    def residue(w):
        return tuple(((w[i]-i)//5)%M for i in range(5))
    return min(residue(v), residue(involution(v)))


def q8(v):
    s2, s3, s4, s5 = [sum(x**j for x in v) for j in range(2, 6)]
    return (6273*s2**4-33750*s2*s2*s4-56800*s2*s3*s3
            +69600*s3*s5+45000*s4*s4)


def valuation(n, ell):
    if n == 0:
        return None
    answer = 0
    while n%ell == 0:
        n //= ell
        answer += 1
    return answer


def tau_from_product(N):
    a = [1]+[0]*(N-1)
    for k in range(1, N):
        b = a.copy()
        for j in range(1, min(24, (N-1)//k)+1):
            c = (-1)**j*comb(24, j)
            for i in range(j*k, N):
                b[i] += c*a[i-j*k]
        a = b
    return [0]+a


def tau_triangular(N):
    ts = []
    m = 1
    while m*(m+1)//2 < N:
        ts.append((m*(m+1)//2, (-1)**m*(2*m+1)))
        m += 1
    f = [1]+[0]*(N-1)
    for n in range(1, N):
        total = sum(a*(9*t-n)*f[n-t] for t, a in ts if t <= n)
        f[n], rem = divmod(total, n)
        assert rem == 0
    return [0]+f


# Each coordinate is (slope*M+intercept)/7. The first family starts at k=4.
FAMILIES = {
    1: dict(c=7, minimum_M=16,
            v=[(-20,5),(-10,-8),(-10,-1),(20,16),(20,-12)],
            w=[(15,5),(-10,-8),(25,-1),(-15,16),(-15,-12)]),
    2: dict(c=1, minimum_M=4,
            v=[(-25,-5),(10,2),(-15,4),(15,-4),(15,3)],
            w=[(10,-5),(10,2),(20,4),(-20,-4),(-20,3)]),
    0: dict(c=6, minimum_M=8,
            v=[(-20,-15),(10,-3),(10,4),(20,1),(-20,13)],
            w=[(15,-15),(-25,-3),(10,4),(-15,1),(15,13)]),
}


def threshold(k):
    M = 2**k
    c = {1:7, 2:1, 0:6}[k%3]
    n, rem = divmod(20*M*M+2*M+c, 7)
    assert rem == 0
    assert n == (100*M*M+10*M+36)//35
    return n


def boundary_witness(k):
    if k == 1:
        return (-5,-4,2,-2,9), (5,6,-8,-2,-1)
    fam = FAMILIES[k%3]
    vectors = []
    for name in ['v', 'w']:
        nums = [a*2**k+b for a, b in fam[name]]
        assert all(x%7 == 0 for x in nums)
        vectors.append(tuple(x//7 for x in nums))
    return tuple(vectors)


def symbolic_family_checks():
    records = []
    for kind, fam in FAMILIES.items():
        signs = []
        for name in ['v', 'w']:
            coords = fam[name]
            assert sum(a for a,b in coords) == sum(b for a,b in coords) == 0
            # Coefficients of 49 * norm^2 in increasing powers of M.
            norm = [sum(b*b for a,b in coords),
                    sum(2*a*b for a,b in coords), sum(a*a for a,b in coords)]
            assert norm == [70*fam['c'], 140, 1400]
            sign = 1
            for i,j in PAIRS:
                a, b = coords[i][0]-coords[j][0], coords[i][1]-coords[j][1]
                at_start = a*fam['minimum_M']+b
                assert at_start != 0
                # Each difference keeps this sign for every real M >= minimum_M.
                assert a == 0 or a*at_start > 0
                sign *= 1 if at_start > 0 else -1
            signs.append(sign)
        assert signs[0]*signs[1] == -1
        d = []
        for (a,b),(c,e) in zip(fam['v'], fam['w']):
            assert e == b and (c-a)%35 == 0
            d.append((c-a)//35)
        assert sum(d) == 0 and sum(x*x for x in d) == 4
        records.append(dict(k_mod_3=kind, polynomial_norm_coefficients=norm,
                            stable_signs=signs, difference_vector=d,
                            minimum_M=fam['minimum_M']))
    return records


def main(output):
    stats = Counter()
    tau = tau_triangular(2411)
    assert tau[:513] == tau_from_product(512)
    stats['independent_product_coefficients'] = 512
    first_mixed = {}
    selected = []
    for n in list(range(1,513))+[737,2411]:
        vs = list(shell(n))
        assert len(vs) == len(set(vs))
        if n <= 32:
            assert set(vs) == set(shell_brute(n))
            stats['independent_shell_enumerations'] += 1
        assert sum(map(weight, vs)) == tau[n]
        stats['shell_sum_checks'] += 1
        abc = [0,0,0]
        abc_q = [0,0,0]
        for v in vs:
            assert sum(v) == 0 and sum(x*x for x in v) == 10*n
            assert all(v[i]%5 == i for i in range(5))
            jv = involution(v)
            assert involution(jv) == v and weight(jv) == weight(v)
            w = weight(v)
            assert w%5 == 1
            c = [(v[i]-i)//5 for i in range(5)]
            sign = (-1)**sum(c[i]>c[j] for i,j in PAIRS)
            assert sign == (1 if w>0 else -1)
            odd = sum(x%2 for x in v)
            assert odd in [0,2,4]
            assert (odd == 2) == (n%2 == 1)
            index = {0:0,4:1,2:2}[odd]
            abc[index] += w
            abc_q[index] += w*q8(v)
            stats['packet_checks'] += 1
        a = -1024*tau[n//4] if n%4 == 0 else 0
        b = (-24*tau[n//2] if n%2 == 0 else 0)+a
        c = tau[n] if n%2 else 0
        assert abc == [a,b,c]
        assert abc_q == [0,0,0]
        stats['coarse_split_checks'] += 1
        rows = []
        for k in range(1,7):
            groups = defaultdict(list)
            for v in vs:
                groups[sector(v,2**k)].append(v)
            mixed = [g for g in groups.values() if min(map(weight,g))<0<max(map(weight,g))]
            if mixed and k not in first_mixed:
                first_mixed[k] = n
            if n < threshold(k):
                assert not mixed
            if 2*n < 5*4**k:
                assert all(len({min(v,involution(v)) for v in g}) == 1 for g in groups.values())
            stats['sector_partition_checks'] += 1
            if n in [7,13,19,31,59,79,499,2411]:
                sums = [sum(map(weight,g)) for g in groups.values()]
                vals = {}
                for ell in [2,5,n]:
                    finite = [valuation(x,ell) for x in sums if x]
                    low = min(finite)
                    vals[str(ell)] = dict(minimum=low, multiplicity=finite.count(low))
                rows.append(dict(depth=k, sectors=len(groups), mixed=len(mixed),
                                 positive=sum(x>0 for x in sums), negative=sum(x<0 for x in sums),
                                 zero=sum(x==0 for x in sums), lowest_valuations=vals))
                if n == 7 and k == 1:
                    seven = [dict(sector=list(key), vectors=g, weight_sum=sum(map(weight,g)),
                                  q8_weight_sum=sum(weight(v)*q8(v) for v in g))
                             for key,g in sorted(groups.items())]
        if rows:
            selected.append(dict(n=n,tau=tau[n],tree=rows))
    assert first_mixed == {1:13,2:47,3:186,4:737}
    # Sparse n=737 check supplies a witness, not a brute-force search of 513..736.
    symbolic = symbolic_family_checks()
    witnesses = []
    for k in range(1,65):
        v,w = boundary_witness(k)
        n=threshold(k)
        for u in [v,w]:
            assert sum(u)==0 and sum(x*x for x in u)==10*n
            assert all(u[i]%5==i for i in range(5))
        assert all((v[i]-w[i])%(5*2**k)==0 for i in range(5))
        assert weight(v)*weight(w)<0
        assert sector(v,2**k)==sector(w,2**k)
        stats['boundary_witness_pairs'] += 1
        if k<=12:
            witnesses.append(dict(depth=k,first_mixed_shell=n,v=v,w=w))
    assert [x['weight_sum'] for x in seven]==[-1848,-17248,2352]
    assert sum(x['q8_weight_sum'] for x in seven)==0
    assert all(x['q8_weight_sum']!=0 for x in seven)
    # A known residue-unit obstruction to the proposed uniqueness mechanism.
    p31=next(x for x in selected if x['n']==31)
    assert all(r['lowest_valuations']['2']['multiplicity']>1 for r in p31['tree'])
    assert p31['tree'][1]['sectors']==16
    assert p31['tree'][1]['positive']==p31['tree'][1]['negative']==8
    result=dict(status='PASS',counts=dict(stats),selected_shells=selected,
                seven_sector_obstruction=seven,symbolic_families=symbolic,
                boundary_witnesses=witnesses,
                bounded_first_mixed_observations=first_mixed,
                non_claims=['No proof of Lehmer.','No Lean verification.',
                            'Finite checks do not establish the all-depth theorem.',
                            'The all-depth proof is the separate mathematical argument.'])
    Path(output).parent.mkdir(parents=True,exist_ok=True)
    Path(output).write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(dict(status=result['status'],counts=result['counts']),indent=2))


if __name__=='__main__':
    main(sys.argv[1])
