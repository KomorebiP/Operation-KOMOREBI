#!/usr/bin/env python3
"""Exact, offline sequence-candidate generator for Komorebi P.'s OEIS continuation.

No OEIS corpus is redistributed. A candidate ID KOM### is NOT an OEIS A-number.
Python 3.10+, standard library only. Integer arithmetic throughout.
"""
from __future__ import annotations

import argparse
from collections import Counter, deque
import csv
from dataclasses import dataclass, asdict
from fractions import Fraction
from hashlib import sha256
from itertools import combinations
import json
from math import comb, factorial, gcd, isqrt
from pathlib import Path

HERE = Path(__file__).resolve().parent


def block_base(N: int, count: int) -> list[int]:
    """A_N(n) = (Nn)![t^(Nn)]/[sum_q (-1)^q t^(Nq)/(Nq)!]."""
    assert N > 0 and count > 0
    a = [1]
    for n in range(1, count):
        a.append(sum((-1) ** (k+1) * comb(N*n, N*k) * a[n-k]
                     for k in range(1, n+1)))
    return a


def block_power(N: int, r: int, count: int) -> list[int]:
    """(Nn)![t^(Nn)] D_N(t)^(-r), D_N=sum (-1)^q t^(Nq)/(Nq)! ."""
    assert r >= 0
    if r == 0:
        return [1] + [0] * (count-1)
    base = block_base(N, count)
    out = base[:]
    for _ in range(1, r):
        out = [sum(comb(N*n, N*k)*out[k]*base[n-k] for k in range(n+1))
               for n in range(count)]
    return out


def block_logder(N: int, count: int) -> list[int]:
    """(Nn)![t^(Nn)] [-t D_N'(t)/D_N(t)], n >= 0."""
    a = block_base(N, count)
    out = [0]
    for n in range(1, count):
        out.append(sum((-1)**(k+1) * (N*k) * comb(N*n,N*k) * a[n-k]
                       for k in range(1,n+1)))
    return out


def binomial_transform(a: list[int]) -> list[int]:
    return [sum(comb(n,k) * a[k] for k in range(n+1)) for n in range(len(a))]


def inverse_binomial_transform(b: list[int]) -> list[int]:
    return [sum((-1)**(n-k)*comb(n,k)*b[k] for k in range(n+1)) for n in range(len(b))]


def stirling2_table(nmax: int) -> list[list[int]]:
    s = [[1]]
    for n in range(1,nmax+1):
        s.append([0]*(n+1))
        for k in range(1,n+1):
            s[n][k] = (s[n-1][k-1] if k-1 < len(s[n-1]) else 0) + (k*s[n-1][k] if k < len(s[n-1]) else 0)
    return s


def stirling_transform(a: list[int]) -> list[int]:
    s = stirling2_table(len(a)-1)
    return [sum(s[n][k] * a[k] for k in range(n+1)) for n in range(len(a))]


def exact_det(matrix: list[list[int]]) -> int:
    """Fraction-free Bareiss determinant with exact divisibility check."""
    n=len(matrix)
    if n==0: return 1
    M=[row[:] for row in matrix]
    sign=1
    denom=1
    for k in range(n-1):
        if M[k][k]==0:
            row=next((i for i in range(k+1,n) if M[i][k]!=0),None)
            if row is None: return 0
            M[k],M[row]=M[row],M[k]
            sign=-sign
        pivot=M[k][k]
        for i in range(k+1,n):
            for j in range(k+1,n):
                num=M[i][j]*pivot-M[i][k]*M[k][j]
                q,rem=divmod(num,denom)
                assert rem==0, (n,i,j,k)
                M[i][j]=q
        for i in range(k+1,n): M[i][k]=0
        denom=pivot
    return sign*M[-1][-1]


def hankel(a: list[int], count: int, shift: int = 0) -> list[int]:
    assert len(a) >= 2*(count-1)+1+shift
    return [exact_det([[a[i+j+shift] for j in range(n+1)] for i in range(n+1)]) for n in range(count)]


def euler_zigzag(count: int) -> list[int]:
    # For y(t)=sec(t)+tan(t), y'=(y^2+1)/2, y(0)=1.
    e=[1]
    for n in range(count-1):
        t=sum(comb(n,k)*e[k]*e[n-k] for k in range(n+1))+(1 if n==0 else 0)
        assert t%2==0
        e.append(t//2)
    return e


def bell(count: int) -> list[int]:
    a=[1]
    for n in range(count-1):
        a.append(sum(comb(n,k)*a[k] for k in range(n+1)))
    return a


def fubini(count: int) -> list[int]:
    a=[1]
    for n in range(1,count): a.append(sum(comb(n,k)*a[n-k] for k in range(1,n+1)))
    return a


def derangements(count: int) -> list[int]:
    if count==1: return [1]
    a=[1,0]
    for n in range(2,count): a.append((n-1)*(a[-1]+a[-2]))
    return a


def kbonacci(k: int, count: int) -> list[int]:
    assert k>=2
    a=([0]*(k-1)+[1])[:count]
    for n in range(k,count): a.append(sum(a[n-k:n]))
    return a


def catalan(count: int) -> list[int]:
    return [comb(2*n,n)//(n+1) for n in range(count)]


def vp(n: int,p: int) -> int:
    if n==0: raise ValueError('v_p(0) is unbounded and is not an integer sequence value')
    n=abs(n)
    k=0
    while n%p==0:
        n//=p
        k+=1
    return k


def vp_fact(n:int,p:int)->int:
    s=0
    while n:
        n//=p
        s+=n
    return s


def pascal_valuation(n:int,k:int,p:int)->int:
    return vp_fact(n,p)-vp_fact(k,p)-vp_fact(n-k,p)


def pascal_exact_carries(p:int, j:int,count:int)->list[int]:
    return [sum(pascal_valuation(n,k,p)==j for k in range(n+1)) for n in range(count)]


def pascal_row_valuation_sum(p:int,count:int)->list[int]:
    return [sum(pascal_valuation(n,k,p) for k in range(n+1)) for n in range(count)]


def digit_sum_mod(b:int,m:int,r:int,count:int)->list[int]:
    """Base-b words of length n, with leading zeros, whose digit sum is r mod m."""
    a=[1]+[0]*(m-1)
    out=[]
    for _ in range(count):
        out.append(a[r % m])
        tmp=[0]*m
        for old,cnt in enumerate(a):
            for d in range(b):tmp[(old+d)%m]+=cnt
        a=tmp
    return out


def cyclic_subset_count(N:int,residue:int,even_size:bool=False)->int:
    """Subsets of {1,...,N-1}, with sum residue mod N; optional even cardinality."""
    assert N>=1
    if even_size:
        dp=[[0]*N for _ in range(2)]
        dp[0][0]=1
        for a in range(1,N):
            new=[x[:] for x in dp]
            for parity in (0,1):
                for rem in range(N):
                    new[1-parity][(rem+a)%N]+=dp[parity][rem]
            dp=new
        return dp[0][residue%N]
    dp=[1]+[0]*(N-1)
    for a in range(1,N):
        new=dp[:]
        for j,c in enumerate(dp):new[(j+a)%N]+=c
        dp=new
    return dp[residue%N]


def totient_sieve(N:int)->list[int]:
    phi=list(range(N+1))
    for p in range(2,N+1):
        if phi[p]==p:
            for k in range(p,N+1,p):phi[k]-=phi[k]//p
    phi[1]=1
    return phi


def radical_sieve(N:int)->list[int]:
    rad=[1]*(N+1)
    for p in range(2,N+1):
        if rad[p]==1:
            for k in range(p,N+1,p):rad[k]*=p
    return rad


def totient_prefix_stats(count:int)->tuple[list[int],list[int],list[int]]:
    p=totient_sieve(count)
    r=radical_sieve(count)
    freq=Counter()
    seen=set()
    fiber=[]; distinct=[]; slack=[]
    for n in range(1,count+1):
        freq[p[n]]+=1
        seen.add(p[n])
        fiber.append(freq[p[n]])
        distinct.append(len(seen))
        assert n%r[n]==0
        slack.append(n//r[n])
    return fiber,distinct,slack


def collatz_odd_jumps(count:int)->tuple[list[int],list[int]]:
    jumps=[];images=[]
    for n in range(count):
        m=3*(2*n+1)+1
        j=vp(m,2)
        jumps.append(j)
        images.append(m//2**j)
        assert images[-1]%2==1
    return jumps,images


def polyadd(a:list[int],b:list[int])->list[int]:
    return [(a[i] if i<len(a) else 0)+(b[i] if i<len(b) else 0) for i in range(max(len(a),len(b)))]


def polyeval(a:list[int],x:int)->int:
    val=0
    for c in reversed(a): val=val*x+c
    return val


def ladder_poly(count:int)->list[list[int]]:
    """P_0=Q_0=1; P_{n+1}=(1+s)P_n+Q_n; Q_{n+1}=P_n."""
    P=[1];Q=[1]; rows=[]
    for n in range(count):
        assert len(P)==n+1 and P[-1]==1
        rows.append(P)
        P,Q=polyadd(polyadd(P,[0]+P),Q),P
    return rows


def clifford_comp(a:tuple[int,...],b:tuple[int,...])->tuple[int,...]:
    """Signed-axis conjugation action a∘b on Pauli axes X,Y,Z."""
    return tuple((1 if x>0 else -1)*a[abs(x)-1] for x in b)


_I=(1,2,3)
_H=(3,-2,1)
_S=(2,-1,3)
_SINV=(-2,1,3)
_X=(1,-2,-3)


def clifford_states()->set[tuple[int,...]]:
    states={_I}
    queue=deque([_I])
    while queue:
        g=queue.popleft()
        for h in (_H,_S):
            t=clifford_comp(h,g)
            if t not in states:
                states.add(t);queue.append(t)
    return states


def clifford_identity_words(gates:list[tuple[int,...]],count:int)->list[int]:
    states=clifford_states()
    assert len(states)==24
    assert all(x in states for x in gates)
    dp={_I:1}; result=[]
    for _ in range(count):
        result.append(dp.get(_I,0))
        new=Counter()
        for g,w in dp.items():
            for h in gates:
                new[clifford_comp(h,g)]+=w
        dp=dict(new)
        assert sum(dp.values()) == len(gates)**(len(result))
    return result


def sigma(n:int)->int:
    return sum(d for d in range(1,n+1) if n%d==0)


def safe_cosets(n:int,k:int|None)->int:
    # A subgroup H of cyclic group Z/n is specified by |H|=h|n and has n/h cosets.
    return sum(n//h for h in range(1,n+1) if n%h==0 and (k is None or h<=k))


@dataclass
class Candidate:
    code:str
    name:str
    family:str
    offset:int
    terms:list[int]
    definition:str
    research_source:str
    classification:str
    priority:str
    existing_oeis_id:str = ''
    oeis_evidence:str = 'Not searched individually against a current full OEIS corpus'
    note:str = ''


class Catalog:
    def __init__(self)->None:
        self.items:list[Candidate]=[]
    def add(self,name:str,family:str,offset:int,terms:list[int],definition:str,source:str,
            classification:str='exploratory',priority:str='review',known:str='',
            evidence:str='Not searched individually against a current full OEIS corpus',note:str='')->str:
        assert all(type(x) is int for x in terms)
        assert terms and isinstance(offset,int)
        code=f'KOM{len(self.items)+1:03d}'
        self.items.append(Candidate(code,name,family,offset,terms,definition,source,
                                    classification,priority,known,evidence,note))
        return code


def create_catalog()->Catalog:
    c=Catalog()
    old='Original recovered v10_sequence_catalog.csv; exact filtered EGF / OEIS Connection Atlas'
    ext='New parameter specialization of recovered filtered exponential block construction'
    # Known integer families retained for calibration and indexing; NOT novelty claims.
    for N,known in ((2,'A000364'),(3,'A002115'),(4,'A211212'),(5,''),(6,''),(7,''),(8,'')):
        v=block_base(N,19 if N>=6 else 26)
        c.add(f'Generalized Euler reciprocal block N={N}', 'Euler/block',0,v,
              f'D_N(t)=sum_(q>=0) (-1)^q t^(Nq)/(Nq)!; a(n)=(Nn)!*[t^(Nn)] 1/D_N(t).',
              old,'known-OEIS' if known else 'known-family',
              'control', known,
              'Confirmed public OEIS match as of 2026-11-15' if known else 'Column of known OEIS array A181985; no standalone ID claimed',
              'For N>=2 these are N-alternating permutation counts; do not submit as new without provenance review.')
    for name,fn,existing,desc in [
        ('Bell numbers',bell,'A000110','B(0)=1; B(n+1)=sum_(k=0)^n C(n,k) B(k).'),
        ('Ordered Bell / Fubini numbers',fubini,'A000670','F(0)=1; F(n)=sum_(k=1)^n C(n,k)F(n-k).'),
        ('Derangements',derangements,'A000166','D(0)=1,D(1)=0; D(n)=(n-1)(D(n-1)+D(n-2)).'),
        ('Euler up/down numbers',euler_zigzag,'A000111','E(0)=1; for y=sec(t)+tan(t): y\'=(1+y^2)/2.'),
        ('Catalan numbers',catalan,'A000108','C(n)=binom(2n,n)/(n+1).'),
    ]:
        c.add(name,'classical anchor',0,fn(38),desc,
              'Recovered v10_sequence_catalog.csv and OEIS Connection Atlas','known-OEIS','control',existing,
              'Confirmed live official OEIS for Bell, Fubini and Euler zigzag; others indexed in recovered atlas')
    for k,known in [(3,'A000073'),(4,'A000078'),(5,''),(6,'')]:
        c.add(f'{k}-bonacci recurrence (k-1 zeros, then 1)','recurrence',0,kbonacci(k,45),
              f'a(0..{k-2})=0, a({k-1})=1, a(n)=sum_(j=1)^{k} a(n-j) for n>={k}.',
              'Recovered sequence guide and k-bonacci research','known-OEIS' if known else 'known-family',
              'control',known, 'Historically known recurrence; no new-sequence claim')
    # Powers r>1: analytic families (many already known under Mittag-Leffler signed conventions).
    for N,rs in [(2,[2,3]),(3,[2,3]),(4,[2,3]),(5,[2,3]),(6,[2,3]),(7,[2]),(8,[2])]:
        for r in rs:
            c.add(f'Power {r} reciprocal filtered EGF, N={N}','block powers',0,
                block_power(N,r,20 if N>=5 else 26),
                f'D_N(t)=sum_(q>=0) (-1)^q t^(Nq)/(Nq)!; a(n)=(Nn)![t^(Nn)] D_N(t)^(-{r}).',
                ext, 'exploratory','medium',note='Integer coefficients follow from the EGF Hurwitz product; related sign-convention arrays may already exist in OEIS (e.g. Mittag-Leffler inverse-power arrays).')
    for N in range(2,9):
        c.add(f'Logarithmic derivative of reciprocal block N={N}', 'logarithmic derivatives',0,
              block_logder(N,22 if N>=6 else 30),
              f'Let D_N(t)=sum_q (-1)^q t^(Nq)/(Nq)!. a(n)=(Nn)!*[t^(Nn)](-t D_N\'(t)/D_N(t)).',
              ext,'exploratory','high',note='Integrality follows by binomial convolution with the integral reciprocal coefficients; n=0 term is zero.')
    for N in (3,4,5,6):
        c.add(f'Binomial transform of generalized Euler block N={N}','block transforms',0,
              binomial_transform(block_base(N,24)),
              f'a(n)=sum_(k=0)^n binom(n,k) A_{N}(k), where A_N is the reciprocal filtered block.',
              'Derived from exact Komorebi transfer-transform family','exploratory','medium')
    for N in (3,4,5):
        c.add(f'Stirling-2 transform of generalized Euler block N={N}','block transforms',0,
              stirling_transform(block_base(N,23)),
              f'a(n)=sum_(k=0)^n S(n,k) A_{N}(k), S(n,k) Stirling 2nd kind.',
              'Derived from Stirling/Bell/Fubini transfer calculus','exploratory','medium')
    for N in (2,3,4,5):
        count=9
        a=block_base(N,2*(count-1)+2)
        c.add(f'Hankel determinants of generalized Euler block N={N}','Hankel invariants',0,hankel(a,count),
              f'a(n)=det(A_{N}(i+j))_(0<=i,j<=n), A_N from filtered reciprocal.',
              'Derived exact determinant moment invariant from the recovered Euler block research',
              'exploratory','high',note='Only 9 terms computed because determinant size and growth are significant. Signed coefficients are retained.')
    for N,p in [(2,5),(2,13),(3,11),(3,13),(4,3),(4,17),(5,3),(5,7),(6,13),(7,3),(8,13)]:
        a=block_base(N,35 if N<=3 else 27)
        assert all(v>0 for v in a)
        assert any(vp(v,p)>0 for v in a), (N,p)
        c.add(f'p-adic valuation v_{p} of reciprocal block N={N}','p-adic valuations',0,
              [vp(x,p) for x in a],
              f'a(n)=v_{p}(A_{N}(n)), A_N(n) the positive integer generalized Euler reciprocal block.',
              'Euler odd-prime valuations / dyadic lift research','exploratory','high',
              note='Every computed input was nonzero; only finite exact valuations computed, not a uniform valuation formula.')
    for m in (3,4,5,7):
        c.add(f'Binary popcount divisible by {m} among 0<=k<2^n','digit-residue packets',0,
              digit_sum_mod(2,m,0,60),
              f'a(n)=#{{0<=k<2^n : popcount(k) == 0 (mod {m})}}; n=0 includes k=0.',
              'Cyclic projector, polyphase, dyadic packets','classical transform candidate','medium',
              note='Roots-of-unity filter / binomial residue sum. Not a new claim.')
    for b,m,r in [(3,4,0),(3,5,1),(4,5,0),(2,5,1)]:
        c.add(f'Base {b} digit-sum residue {r} modulo {m}, length n','digit-residue packets',0,
              digit_sum_mod(b,m,r,48),
              f'a(n)=# length-n base-{b} digit strings, leading zeros allowed, with digit sum congruent to {r} mod {m}.',
              'Generalized finite cyclic packet projection and refinement','exploratory','medium')
    for r,parity,offset in [(0,False,1),(1,False,2),(0,True,1)]:
        c.add(f'Nonzero-residue subsets, sum={r} mod N'+ (' even cardinality' if parity else ''),
              'cyclic subset-sum packets',offset,
              [cyclic_subset_count(N,r,parity) for N in range(offset,42)],
              f'a(N)=# subsets S of {{1,...,N-1}} with sum(S) == {r} (mod N)'+ (' and |S| even.' if parity else '.'),
              'Smith chart cyclic packet theorem and finite roots-of-unity projection','exploratory','high',
              note='Subset-count DP verified by independent brute-force enumeration for N<=8.')
    for p,j in [(2,1),(2,2),(3,1),(3,2)]:
        c.add(f'Pascal row count, exactly {j} base-{p} carries','p-adic Pascal carries',0,
              pascal_exact_carries(p,j,170),
              f'a(n)=#{{0<=k<=n : v_{p}(binom(n,k))={j}}}. By Kummer these are carry counts.',
              'Dyadic/odd-adic Frobenius carry obstruction and Pascal parity research','exploratory','high',
              note='Finite exact valuations; Kummer digit-carry interpretation is classical.')
    for p in (2,3):
        c.add(f'Sum of v_{p} across Pascal row','p-adic Pascal carries',0,
              pascal_row_valuation_sum(p,170),
              f'a(n)=sum_(k=0)^n v_{p}(binom(n,k)).',
              'Dyadic/odd-adic transfer and Frobenius carry research','exploratory','medium')
    fiber,distinct,slack=totient_prefix_stats(180)
    c.add('Totient prefix-fiber multiplicity at n','totient fibers',1,fiber,
          'a(n)=#{1<=k<=n : phi(k)=phi(n)}; this is a finite-prefix statistic for each n.',
          'Carmichael totient-conjecture packet-transfer attack','exploratory','medium',
          note='Does not compute full phi inverse fibers and does not settle Carmichael.')
    c.add('Number of distinct totient values among 1..n','totient fibers',1,distinct,
          'a(n)=#{phi(k):1<=k<=n}.',
          'Carmichael totient-conjecture packet-transfer attack','exploratory','medium')
    c.add('Exponent slack n/rad(n)','prime-power support',1,slack,
          'a(n)=n/rad(n), rad(n)=product of distinct primes dividing n; a(1)=1.',
          'Carmichael packet-transfer slack E(n) in recovered research note',
          'classical transform candidate','control',note='Classical arithmetic function; not a new discovery.')
    cj,co=collatz_odd_jumps(250)
    c.add('2-adic jump of odd Collatz map','Collatz jump matrix',0,cj,
          'a(n)=v_2(3*(2n+1)+1), n>=0.',
          'Collatz dyadic jump/packet research','classical transform candidate','medium',
          note='Exact pointwise valuation, not a uniform bound or a proof of Collatz.')
    c.add('Accelerated odd Collatz image of 2n+1','Collatz jump matrix',0,co,
          'a(n)=(3*(2n+1)+1)/2^v_2(3*(2n+1)+1); a(n) is odd.',
          'Collatz dyadic jump/packet research','classical transform candidate','medium')
    rows=ladder_poly(70)
    c.add('Ladder polynomial P_n evaluated at s=0','Smith transfer polynomial',0,
          [polyeval(r,0) for r in rows],
          'P_0=Q_0=1; P_(n+1)=(1+s)P_n+Q_n; Q_(n+1)=P_n; a(n)=P_n(0).',
          'Newly extracted transfer-polynomial model inspired by Smith/RLC exact rational solver','classical transform candidate','control',
          note='Fibonacci-shift control. This specific formal recurrence is exploratory, not asserted to equal a published circuit topology.')
    c.add('Ladder polynomial P_n evaluated at s=1','Smith transfer polynomial',0,
          [polyeval(r,1) for r in rows],
          'P_0=Q_0=1; P_(n+1)=(1+s)P_n+Q_n; Q_(n+1)=P_n; a(n)=P_n(1).',
          'Newly extracted transfer-polynomial model inspired by Smith/RLC exact rational solver','classical transform candidate','control',
          note='Pell-type recurrence; not new to OEIS without further comparison.')
    c.add('Squared L2-norm of ladder numerator coefficients','Smith transfer polynomial',0,
          [sum(x*x for x in r) for r in rows[:52]],
          'For polynomial P_n(s) from P_0=Q_0=1; P_(n+1)=(1+s)P_n+Q_n, a(n)=sum_(k=0)^n c(n,k)^2, where c(n,k)=[s^k]P_n(s) (sum of coefficient squares).',
          'Smith/RLC rational transfer-polynomial coefficient invariant, newly constructed','exploratory','high',
          note='Formula means sum_k(c[n,k]^2); see explicit P_n recurrence. It does not assert network realizability or novelty.')
    c.add('Middle coefficient of ladder numerator P_n','Smith transfer polynomial',0,
          [r[len(r)//2-1 if len(r)%2==0 else len(r)//2] for r in rows[:60]],
          'a(n)=[s^floor(n/2)]P_n(s), P_0=Q_0=1, P_(n+1)=(1+s)P_n+Q_n, Q_(n+1)=P_n.',
          'Smith/RLC rational transfer-polynomial coefficient invariant, newly constructed','exploratory','high')
    flatten=[a for r in rows[:23] for a in r]
    c.add('Coefficient triangle of ladder P_n, flattened by rows','Smith transfer polynomial triangle',0,flatten,
          'a(index)=coefficient triangle of P_n(s), rows n>=0, k=0..n, flattened lexicographically (n,k). P_0=Q_0=1; P_(n+1)=(1+s)P_n+Q_n; Q_(n+1)=P_n.',
          'Smith/RLC exact transfer polynomial, newly constructed','exploratory','high',
          note='b-file index is flattened position, not row n. Row offsets provided separately in triangle_metadata.csv.')
    for gates,name in [([_H,_S],'{H,S}'),([_H,_S,_SINV],'{H,S,S^-1}'),([_H,_S,_X],'{H,S,X}')]:
        c.add(f'Single-qubit Clifford identity words in gates {name}','quantum circuit counting',0,
              clifford_identity_words(gates,75),
              f'a(n)=# length-n words in gate alphabet {name} acting as identity on (X,Y,Z) Pauli axes by conjugation, i.e. identity modulo global phase.',
              'Constructed from Komorebi quantum/circuits theme using exact 24-element Clifford action',
              'exploratory','high',
              note='Words are ordered; repeated generators are distinguished; exact group of 24, not arbitrary SU(2) matrices. Classical group combinatorics may already cover these walks.')
    for k in (None,2,3):
        c.add(f'Contractive cyclic residue-coset masks ({"all" if k is None else "subgroup size <= "+str(k)})',
              'Smith cyclic packet masks',1,
              [safe_cosets(n,k) for n in range(1,200)],
              'a(n)=sum_(h|n, '+('all h' if k is None else f'h<={k}')+') n/h; counts distinct cosets of subgroups H in Z/n, with |H|=h.',
              'Exact contractive coset retention in Smith cyclic packet analysis',
              'classical transform candidate','control' if k is None else 'medium',
              'A000203' if k is None else '',
              'Sum-of-divisors identity; publicly known as A000203' if k is None else 'Classical subgroup counting; not individually OEIS checked',
              'Counts only the proven-safe subgroup coset masks, not all arbitrary universal contractive filters.')
    return c


def write_outputs(c:Catalog,out:Path)->dict:
    bdir=out/'bfiles'; drafts=out/'drafts';verify=out/'verification'
    for d in (out,bdir,drafts,verify):d.mkdir(parents=True,exist_ok=True)
    register=[];checksums={}
    for s in c.items:
        fn=f'{s.code}_candidate_bfile.txt'
        path=bdir/fn
        # Consecutive integer indices and a blank final line follow OEIS's format, but no fake b######.txt name.
        content=f'# Candidate {s.code}, NOT an allocated OEIS A-number.\n# {s.name}\n'
        content+=''.join(f'{s.offset+i} {v}\n' for i,v in enumerate(s.terms))+'\n'
        path.write_text(content,encoding='ascii')
        assert path.read_bytes().endswith(b'\n\n')
        assert len(s.terms)==sum(1 for line in path.read_text().splitlines() if line and not line.startswith('#'))
        checksums[fn]=sha256(path.read_bytes()).hexdigest()
        draft=drafts/f'{s.code}.md'
        draft.write_text('\n'.join([
            f'# {s.code}: {s.name}', '', f'**Classification:** {s.classification}',
            f'**Priority:** {s.priority}',
            f'**OEIS ID (only if independently grounded):** {s.existing_oeis_id or "not assigned"}',
            f'**OEIS comparison evidence:** {s.oeis_evidence}',
            f'**Source/inspiration:** {s.research_source}',
            f'**Formula/definition:** {s.definition}',
            f'**Offset:** {s.offset}',
            f'**Number of generated terms:** {len(s.terms)}',
            f'**First terms:** {", ".join(str(v) for v in s.terms[:16])}',
            f'**b-file:** ../bfiles/{fn}',
            '', '**Notes and limitations:** '+(s.note or 'Finite exact terms generated, no OEIS novelty check.'),
            '', 'This is an internal research candidate, not an OEIS submission. Check indexing, priority, and equivalent transforms before submitting.',
            ''],),encoding='utf-8')
        register.append(dict(code=s.code,name=s.name,family=s.family,offset=s.offset,
                            count=len(s.terms),first_12=','.join(str(x) for x in s.terms[:12]),
                            definition=s.definition,research_source=s.research_source,
                            classification=s.classification,priority=s.priority,
                            existing_oeis_id=s.existing_oeis_id,oeis_evidence=s.oeis_evidence,
                            notes=s.note,bfile=f'bfiles/{fn}',bfile_sha256=checksums[fn],
                            draft=f'drafts/{s.code}.md'))
    with (out/'CANDIDATE_REGISTRY.csv').open('w',newline='',encoding='utf-8') as f:
        w=csv.DictWriter(f,fieldnames=list(register[0]));w.writeheader();w.writerows(register)
    (out/'candidate_registry.json').write_text(json.dumps([asdict(s) for s in c.items],indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
    (out/'BFILE_SHA256.json').write_text(json.dumps(checksums,indent=2)+'\n')
    (out/'triangle_metadata.csv').write_text(
        'row_n,first_flat_index,number_of_terms\n'+
        ''.join(f'{n},{n*(n+1)//2},{n+1}\n' for n in range(23)))
    return {'candidate_count':len(c.items),'b_file_count':len(checksums),
            'classifications':dict(Counter(s.classification for s in c.items)),
            'families':dict(Counter(s.family for s in c.items)),
            'counts_by_priority':dict(Counter(s.priority for s in c.items)),
            'total_generated_terms':sum(len(s.terms) for s in c.items)}


def independent_tests(c:Catalog)->dict:
    result={}
    # Match exact recovered numeric catalog for all available A_N rows, by CSV data not reusing code.
    source=HERE.parent/'originals'/'v10_sequence_catalog.csv'
    nchecked=0
    if source.exists():
        with source.open(newline='',encoding='utf-8') as f:
            for row in csv.DictReader(f):
                key=row['key']
                if not key.startswith('A_N_block_N'):continue
                N=int(key.split('_N')[-1])
                numeric=[int(x.strip()) for x in row['values'].split(',')]
                calc=block_base(N,len(numeric))
                assert calc==numeric,(N,calc[:3],numeric[:3])
                nchecked+=len(numeric)
    result['original_catalog_block_entries_exactly_matched']=nchecked
    # Independent Fraction EGF power-inversion control (truncated formal series), small cases.
    fraction_checks=0
    for N in (2,3,4,5):
        degree=6
        D=[Fraction((-1)**i,factorial(N*i)) for i in range(degree+1)]
        for r in (1,2,3):
            g=[Fraction(1)] + [Fraction(0)]*degree
            for _ in range(r):
                h=[Fraction(1)]
                for i in range(1,degree+1):
                    h.append(-sum(D[k]*h[i-k] for k in range(1,i+1)))
                g=[sum(g[j]*h[i-j] for j in range(i+1)) for i in range(degree+1)]
            exact=[g[i]*factorial(N*i) for i in range(degree+1)]
            assert all(x.denominator==1 for x in exact)
            assert [int(x) for x in exact]==block_power(N,r,degree+1)
            fraction_checks+=degree+1
    result['independent_fraction_series_terms']=fraction_checks
    # Log derivative: check t-derivative formal coefficient relation exact for 3 small cases.
    logchecks=0
    for N in (2,3,4,5):
        d=[Fraction((-1)**j,factorial(N*j)) for j in range(7)]
        a=[Fraction(x,factorial(N*i)) for i,x in enumerate(block_base(N,7))]
        for n in range(7):
            term=-sum(Fraction(N*k)*d[k]*a[n-k] for k in range(1,n+1))
            assert term*factorial(N*n)==block_logder(N,7)[n]
            logchecks+=1
    result['independent_log_derivative_terms']=logchecks
    # Inverse binomial formula on recovered source family.
    for N in (2,3,4):
        a=block_base(N,25)
        assert inverse_binomial_transform(binomial_transform(a))==a
    result['binomial_transform_inversions']=3
    # Anchor sequences: Euler zigzag, Fubini, Bell, derangements, k-bonacci, Catalan.
    assert euler_zigzag(13)==[1,1,1,2,5,16,61,272,1385,7936,50521,353792,2702765]
    assert bell(10)==[1,1,2,5,15,52,203,877,4140,21147]
    assert fubini(7)==[1,1,3,13,75,541,4683]
    assert derangements(9)==[1,0,1,2,9,44,265,1854,14833]
    assert kbonacci(3,7)==[0,0,1,1,2,4,7]
    assert catalan(8)==[1,1,2,5,14,42,132,429]
    result['anchor_sequence_families']=6
    # Verify Kummer valuations by brute v_p(binomial(n,k)) for every small row.
    checked=0
    for p in (2,3,5):
        for n in range(45):
            for k in range(n+1):
                assert pascal_valuation(n,k,p)==vp(comb(n,k),p)
                checked+=1
    result['pascal_valuation_vs_direct_binomial_checks']=checked
    # Brute independent subset enumeration for small N.
    checks=0
    for N in range(1,9):
        for residue in (0,1):
            for even in (False,True):
                brute=sum((sum(S)%N==residue%N and (not even or len(S)%2==0))
                          for size in range(N) for S in combinations(range(1,N),size))
                assert brute==cyclic_subset_count(N,residue,even)
                checks+=1
    result['subset_dp_vs_bruteforce_checks']=checks
    # Verify residue class digit sum with brute base words (leading zeros implicit).
    checks=0
    for b,m in ((2,3),(2,5),(3,4),(3,5)):
        for n in range(6):
            nums=range(b**n)
            for r in range(m):
                brute=0
                for num in nums:
                    k=num;s=0
                    for _ in range(n): s+=k%b;k//=b
                    brute+=(s%m==r)
                assert digit_sum_mod(b,m,r,n+1)[n]==brute
                checks+=1
        assert sum(digit_sum_mod(b,m,r,12)[11] for r in range(m))==b**11
    result['digit_sum_dp_vs_bruteforce_checks']=checks
    # Smith recurrence independent evaluations and coefficient-sum checks.
    rows=ladder_poly(18)
    assert rows[:4]==[[1],[2,1],[3,3,1],[5,7,4,1]]
    for n in range(2,len(rows)):
        for s in (0,1,2,3):
            assert polyeval(rows[n],s)==(s+1)*polyeval(rows[n-1],s)+polyeval(rows[n-2],s)
    result['ladder_polynomial_recursion_checks']=64
    # Pauli action 24 element finite group, exact gate identities.
    assert clifford_comp(_H,_H)==_I
    assert clifford_comp(_S,clifford_comp(_S,clifford_comp(_S,_S)))==_I
    assert clifford_comp(_X,_X)==_I
    assert len(clifford_states())==24
    for x in (_H,_S):
        assert x in clifford_states()
    result['clifford_group_order']=len(clifford_states())
    result['clifford_identity_word_cases']=[clifford_identity_words(g,9)[:9] for g in ([_H,_S],[_H,_S,_SINV],[_H,_S,_X])]
    # Totient and coset control, exact finite checks.
    t=totient_sieve(30)
    assert t[1:13]==[1,1,2,2,4,2,6,4,6,4,10,4]
    assert [safe_cosets(n,None) for n in range(1,11)]==[1,3,4,7,6,12,8,15,13,18]
    # Structured candidate record integrity.
    assert len(set(s.code for s in c.items))==len(c.items)
    assert all(s.offset+len(s.terms)>s.offset for s in c.items)
    result['catalog_integrity_count']=len(c.items)
    return result


def main():
    ap=argparse.ArgumentParser(description='Generate exact Komorebi OEIS-related sequence candidates and b-file-like artifacts')
    ap.add_argument('--output',type=Path,default=HERE)
    a=ap.parse_args()
    c=create_catalog()
    tests=independent_tests(c)
    manifest=write_outputs(c,a.output)
    (a.output/'verification'/'GENERATION_TESTS.json').write_text(json.dumps(tests,indent=2)+'\n')
    (a.output/'verification'/'GENERATION_SUMMARY.json').write_text(json.dumps(manifest,indent=2)+'\n')
    print(json.dumps({'manifest':manifest,'tests':tests},indent=2))


if __name__=='__main__':
    main()
