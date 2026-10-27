#!/usr/bin/env python3
"""Independent, exact bounded checks for the 48 new sequence/polyphase/tap lessons.

No author generator is imported. All arithmetic is Z or Q; bounds are explicit.
The finite checks are implementation evidence, not universal proofs.
"""
from __future__ import annotations

import argparse
from fractions import Fraction as Q
from math import comb, factorial
from pathlib import Path
import hashlib
import json
import platform

N = 32
records = []
executed_checks = 0
last_record_checks = 0


def check(condition):
    global executed_checks
    if not condition:
        raise AssertionError("Independent exact check failed")
    executed_checks += 1


def record(name, bound, count, derivation, non_claims=None):
    global last_record_checks
    count = executed_checks - last_record_checks
    last_record_checks = executed_checks
    records.append(dict(name=name, arithmetic="exact integers/rationals", bounds=bound,
                        checks=count, status="PASS", structural_derivation=derivation,
                        non_claims=non_claims or ["Finite agreement is not a universal proof."]))


def coeff(a, n):
    return a[n] if 0 <= n < len(a) else 0


def convolution(a, b):
    if not a or not b:
        return []
    c = [0] * (len(a) + len(b) - 1)
    for i, x in enumerate(a):
        for j, y in enumerate(b):
            c[i + j] += x * y
    return c


def inverse_series(a, degree):
    check(a[0] != 0)
    c = [Q(1, a[0])]
    for n in range(1, degree + 1):
        c.append(-sum(Q(coeff(a, k)) * c[n-k] for k in range(1, n+1)) / a[0])
    return c


def exp_series(u, degree):
    check(u[0] == 0)
    c = [Q(1)]
    for n in range(1, degree + 1):
        c.append(sum(k * Q(coeff(u, k)) * c[n-k] for k in range(1, n+1)) / n)
    return c


def sequence_checks():
    f = [0, 1]
    for n in range(2, 2*N + 5):
        f.append(f[-1] + f[-2])
    E, O = f[0::2][:N+1], f[1::2][:N+1]
    v = (0, 1)
    for n in range(N+1):
        check(v == (E[n], O[n]))
        v = (v[0]+v[1], v[0]+2*v[1])
        check(E[n] - 3*coeff(E, n-1) + coeff(E, n-2) == int(n == 1))
        check(O[n] - 3*coeff(O, n-1) + coeff(O, n-2) == int(n == 0)-int(n == 1))
    check(convolution([0,1,1,-1], [1,-1,-1]) == [0,1,0,-3,0,1])
    H = inverse_series([1,-3,1],N)
    for n in range(N+1):
        check(E[n] == coeff(H,n-1))
        check(O[n] == H[n]-coeff(H,n-1))
        check(f[n]-coeff(f,n-1)-coeff(f,n-2) == int(n==1))
    record("Fibonacci two-phase transfer and rational numerators", {"block_n":[0,N]}, 3*(N+1)+1,
           "The two-step companion matrix is B=[[1,1],[1,2]]. Its resolvent on (0,1) has numerator (q,1-q) and determinant 1-3q+q^2. Scalar reconstruction is exact polynomial cross-multiplication.")

    cat = [comb(2*n,n)//(n+1) for n in range(N+1)]
    for n in range(1,N+1):
        check(cat[n] == sum(cat[k]*cat[n-1-k] for k in range(n)))
    check(cat[:6] == [1,1,2,5,14,42])
    record("Catalan quadratic OGF", {"n":[0,N]}, N+1,
           "The coefficient equation of C=1+zC^2 is the Catalan convolution. The binomial closed form is checked independently in the stated range; its standard universal identification is an external source leaf.")

    S = [[0]*(N+1) for _ in range(N+1)]
    S[0][0] = 1
    for n in range(1,N+1):
        for k in range(1,n+1):
            S[n][k] = S[n-1][k-1]+k*S[n-1][k]
    bell = [sum(S[n]) for n in range(N+1)]
    fubini = [sum(factorial(k)*S[n][k] for k in range(n+1)) for n in range(N+1)]
    ez_minus_one = [Q(0)] + [Q(1,factorial(n)) for n in range(1,N+1)]
    bell_egf = exp_series(ez_minus_one,N)
    fubini_egf = inverse_series([Q(1)] + [-x for x in ez_minus_one[1:]],N)
    for n in range(N+1):
        check(bell_egf[n]*factorial(n) == bell[n])
        check(fubini_egf[n]*factorial(n) == fubini[n])
        if n:
            check(bell[n] == sum(comb(n-1,k)*bell[k] for k in range(n)))
            check(fubini[n] == sum(comb(n,k)*fubini[n-k] for k in range(1,n+1)))
    check(bell[:6] == [1,1,2,5,15,52])
    check(fubini[:6] == [1,1,3,13,75,541])
    record("Bell and Fubini EGF normalization", {"n":[0,N]}, 4*(N+1),
           "Bell numbers are sums of Stirling numbers, Fubini numbers are sums of k! S(n,k). Expansion of exp(exp(z)-1) and 1/(2-exp(z)) uses Q coefficients and n! restoration. Universal combinatorial EGF identifications remain external source leaves.")

    der = [sum((-1)**k * (factorial(n)//factorial(k)) for k in range(n+1)) for n in range(N+1)]
    der_egf = convolution([Q((-1)**n,factorial(n)) for n in range(N+1)],[Q(1)]*(N+1))
    for n in range(N+1):
        check(der_egf[n]*factorial(n) == der[n])
        if n >= 2:
            check(der[n] == (n-1)*(der[n-1]+der[n-2]))
    check(der[:6] == [1,0,1,2,9,44])
    record("Derangements EGF and polynomial recurrence", {"n":[0,N]}, 2*(N+1),
           "Inclusion-exclusion is n! sum_{k=0}^n (-1)^k/k!. The product exp(-z)/(1-z) gives precisely that coefficient; the polynomial recurrence follows by grouping the sums.")

    degree = 24
    cos = [Q((-1)**(n//2),factorial(n)) if n%2 == 0 else Q(0) for n in range(degree+1)]
    sin = [Q((-1)**((n-1)//2),factorial(n)) if n%2 else Q(0) for n in range(degree+1)]
    sec = inverse_series(cos,degree)
    tan = convolution(sin,sec)[:degree+1]
    sec_rationals = [sec[2*n]*factorial(2*n) for n in range(degree//2+1)]
    tan_rationals = [tan[2*n-1]*factorial(2*n-1) for n in range(1,degree//2+1)]
    check(all(value.denominator == 1 for value in sec_rationals + tan_rationals))
    secnums = [int(value) for value in sec_rationals]
    tannums = [int(value) for value in tan_rationals]
    check(secnums[:6] == [1,1,5,61,1385,50521])
    check(tannums[:6] == [1,2,16,272,7936,353792])
    for n in range(degree+1):
        check(sec[n] == (Q(secnums[n//2],factorial(n)) if n%2 == 0 else 0))
    check(Q(secnums[2],factorial(4)) != Q(secnums[2],factorial(2)))
    record("Euler/secant and tangent EGF phase indexing", {"degree":[0,degree],"tangent_index":[1,degree//2]}, degree+3,
           "Formal inversion of cos determines sec; tan=sin/cos. Positive secant coefficients occupy original factorials (2n)!; tangent coefficients occupy (2n-1)! with sequence index starting at 1. Phase splitting does not replace these by n!.")

    parts = [1]+[0]*N
    for k in range(1,N+1):
        for n in range(k,N+1):
            parts[n] += parts[n-k]
    pent = [1]
    for n in range(1,N+1):
        total = 0
        k = 1
        while k*(3*k-1)//2 <= n:
            sign = 1 if k%2 else -1
            total += sign*coeff(pent,n-k*(3*k-1)//2)
            total += sign*coeff(pent,n-k*(3*k+1)//2)
            k += 1
        pent.append(total)
    check(parts == pent)
    check(parts[:11] == [1,1,2,3,5,7,11,15,22,30,42])
    record("Partitions product vs pentagonal recurrence", {"n":[0,N]}, N+2,
           "The product enumerator is independent of the pentagonal recurrence. Their equality is bounded evidence; the infinite Euler pentagonal product identity is an external source leaf, not proved by this run.")

    apery = [sum(comb(n,k)**2 * comb(n+k,k)**2 for k in range(n+1)) for n in range(N+1)]
    for n in range(N):
        check((n+1)**3*apery[n+1] == (34*n**3+51*n**2+27*n+5)*apery[n] - n**3*coeff(apery,n-1))
    check(apery[:5] == [1,5,73,1445,33001])
    record("Apery polynomial-coefficient recurrence", {"n":[0,N-1]}, N+1,
           "The defining binomial sum is computed independently; the displayed recurrence is tested exactly including n=0. Its universal creative-telescoping identity is an external source leaf.",
           ["Does not prove the binomial recurrence for all n.","Polynomial recurrence coefficients are not a stationary FIR or constant transfer matrix."])

    for order in (3,4):
        a = [0]*(order-1)+[1]
        for n in range(order,N+1):
            a.append(sum(a[-order:]))
        inv = inverse_series([1]+[-1]*order,N)
        for n in range(N+1):
            check(a[n] == coeff(inv,n-order+1))
        check(a[:order] == [0]*(order-1)+[1])
    record("Tribonacci and tetranacci fixed initials", {"n":[0,N],"orders":[3,4]}, 2*(N+1),
           "With zeros followed by one as initials, the OGF numerator is z^(order-1), denominator 1-z-...-z^order. The recurrence and initials determine the formal series uniquely.")


def additional_sequence_checks():
    fibonacci = [0,1]
    for _ in range(2,N+1):
        fibonacci.append(fibonacci[-1]+fibonacci[-2])
    lucas = [2,1]
    jacob = [0,1]
    for n in range(2,N+1):
        lucas.append(lucas[-1]+lucas[-2])
        jacob.append(jacob[-1]+2*jacob[-2])
    lucas_ogf = convolution([2,-1],inverse_series([1,-1,-1],N))
    jacob_ogf = convolution([0,1],inverse_series([1,-1,-2],N))
    pellx,pelly = [1],[0]
    for n in range(N):
        pellx.append(2*pellx[-1]+3*pelly[-1])
        pelly.append(pellx[-2]+2*pelly[-1])
    for n in range(N+1):
        check(lucas_ogf[n] == lucas[n])
        check(lucas[n]**2-5*fibonacci[n]**2 == 4*(-1)**n)
        check(jacob_ogf[n] == jacob[n] == (2**n-(-1)**n)//3)
        check(pellx[n]**2-3*pelly[n]**2 == 1)
        if n>=2:
            check(pellx[n] == 4*pellx[n-1]-pellx[n-2])
            check(pelly[n] == 4*pelly[n-1]-pelly[n-2])
    record("Lucas/Fibonacci defect, Jacobsthal initials and Pell paired norm", {"n":[0,N]},0,
           "OGF numerators encode the stated seeds. Binet modes phi,psi with phi*psi=-1 give L_n^2-5F_n^2=4(-1)^n. Multiplication by 2+sqrt(3) gives the integer Pell transfer (x,y)->(2x+3y,x+2y), preserves x^2-3y^2, and has characteristic polynomial t^2-4t+1.")

    cb = [comb(2*n,n) for n in range(N+1)]
    cat = [cb[n]//(n+1) for n in range(N+1)]
    for n in range(N):
        check((n+1)*cb[n+1] == 2*(2*n+1)*cb[n])
        check((n+2)*cat[n+1] == 2*(2*n+1)*cat[n])
    squared = convolution(cb,cb)
    for n in range(N+1):
        check(squared[n] == 4**n)
        check(Q(factorial(n),factorial(n)) == 1)
    record("Central binomial/Catalan polynomial ratios and factorial EGF", {"n":[0,N]},0,
           "The polynomial ratios cancel directly from factorial definitions. The central-binomial formal series is (1-4z)^(-1/2), so its square is (1-4z)^(-1). The factorial EGF coefficients are one; this does not replace the factorial OGF coefficients.")

    den = [Q(1,factorial(n+1)) for n in range(N+1)]
    bern_series = inverse_series(den,N)
    bern = [bern_series[n]*factorial(n) for n in range(N+1)]
    check(bern[:8] == [Q(1),Q(-1,2),Q(1,6),Q(0),Q(-1,30),Q(0),Q(1,42),Q(0)])
    for n in range(1,N+1):
        check(sum(comb(n+1,k)*bern[k] for k in range(n+1)) == 0)
    record("Bernoulli B1 sign and EGF inversion", {"n":[0,N]},0,
           "The formal quotient z/(exp(z)-1) is the reciprocal of (exp(z)-1)/z, whose constant term is one. Multiplying the two series gives the coefficient recurrence and forces B1=-1/2.")

    for n in range(64):
        pop = n.bit_count()
        check((2*n).bit_count() == pop)
        check((2*n+1).bit_count() == pop+1)
        check((2*n).bit_count()%2 == pop%2)
        check((2*n+1).bit_count()%2 == 1-pop%2)
        check(sum(comb(n,k)%2 for k in range(n+1)) == 2**pop)
    record("Binary popcount/Thue-Morse/Gould phase recursions", {"n":[0,63]},0,
           "Appending a binary digit proves the popcount and parity recursions. In F2[x], (1+x)^n is the product of (1+x^(2^j)) over set bits, so its odd coefficients correspond bijectively to subsets of set bits, yielding 2^popcount(n).")

    def prime_factors(n):
        factors = []
        p = 2
        while p*p <= n:
            exponent = 0
            while n%p == 0:
                exponent += 1
                n //= p
            if exponent:
                factors.append((p,exponent))
            p += 1
        if n>1:
            factors.append((n,1))
        return factors
    mus = [None]+[0 if any(e>1 for _,e in prime_factors(n)) else (-1)**len(prime_factors(n)) for n in range(1,65)]
    phis = [None]+[sum(1 for k in range(1,n+1) if __import__('math').gcd(k,n)==1) for n in range(1,65)]
    for n in range(1,65):
        divs = [d for d in range(1,n+1) if n%d==0]
        check(sum(mus[d] for d in divs) == int(n==1))
        check(sum(phis[d] for d in divs) == n)
        check(sum(mus[d]*(n//d) for d in divs) == phis[n])
    record("Mobius/totient positive-index divisor relations", {"n":[1,64]},0,
           "Mobius is defined from square-free prime factors, totient independently by gcd counting. Universal divisor identities follow from inclusion-exclusion or partitioning integers by their gcd; no value at n=0 is claimed.")

    squares = [n*n for n in range(11)]
    first = convolution([1,-1],squares)[:11]
    second = convolution([1,-1],first)[:11]
    check(first == [0]+[2*n-1 for n in range(1,11)])
    check(second == [0,1]+[2]*9)
    for n in range(N+1):
        check(sum(range(n+1)) == n*(n+1)//2)
        check(sum(k*(k+1)//2 for k in range(n+1)) == n*(n+1)*(n+2)//6)
        if n>=1:
            check(n*(n+1)//2-(n-1)*n//2 == n)
            check(n*(n+1)*(n+2)//6-(n-1)*n*(n+1)//6 == n*(n+1)//2)
    record("Polynomial sequences and causal finite differences", {"polynomial_n":[0,N],"difference_n":[0,10]},0,
           "Summation telescopes to the triangular/tetrahedral formulas. Difference identities follow by polynomial expansion, with causal boundary residuals kept explicitly.")


def reduce_cyclotomic(a, phi):
    a = list(a)
    d = len(phi)-1
    for n in range(len(a)-1,d-1,-1):
        lead = a[n]
        for k in range(d+1):
            a[n-d+k] -= lead*phi[k]
    return a[:d]+[0]*max(0,d-len(a))


def polyphase_checks():
    f = [0,1]
    for _ in range(2,6*(N+2)+6):
        f.append(f[-1]+f[-2])
    lucas = [2,1]
    for _ in range(2,7):
        lucas.append(lucas[-1]+lucas[-2])
    for M in range(1,7):
        for r in range(M):
            for m in range(N):
                check(f[M*(m+2)+r] == lucas[M]*f[M*(m+1)+r]-(-1)**M*f[M*m+r])
    record("Fibonacci arbitrary-stride jump recurrence", {"stride":[1,6],"all_residues":True,"block_m":[0,N-1]},0,
           "For T=[[0,1],[1,1]], trace(T^M)=L_M and determinant(T^M)=(-1)^M. Cayley-Hamilton for the 2 by 2 matrix T^M yields the displayed two-step recurrence on every residue channel.")

    for M in range(1,7):
        for K in range(1,7):
            for n in range(256):
                r,ell = n%M,(n//M)%K
                child = r+M*ell
                internal = (n//M)//K
                check(child == n%(M*K))
                check(internal == n//(M*K))
                r2,ell2 = n%K,(n//K)%M
                check(r2+K*ell2 == child)
    record("Nested phase refinement and address permutation", {"parent_modulus":[1,6],"child_split":[1,6],"original_n":[0,255]},0,
           "Euclidean division n=M(Kj+ell)+r gives child address r+M ell and internal index j. Reversing M,K reaches the same final address n mod MK, although intermediate labels differ.")

    x = [(-1)**n*(n*n+3*n+1) for n in range(64)]
    kernels = [[1],[0,1],[1,-1],[1,2,1],[-2,0,3,1,-1]]
    count = 0
    for m in range(1,7):
        channels = [x[r::m] for r in range(m)]
        check([channels[n%m][n//m] for n in range(len(x))] == x)
        for h in kernels:
            y = convolution(h,x)
            hc = [h[r::m] for r in range(m)]
            for r in range(m):
                for n,expected in enumerate(y[r::m]):
                    actual = 0
                    for s in range(m):
                        phase = (r-s)%m
                        delay = int(s>r)
                        actual += coeff(convolution(hc[phase],channels[s]),n-delay)
                    check(actual == expected)
                    count += 1
    record("General m-phase FIR routing", {"m":[1,6],"input_length":64,"kernel_lengths":[1,2,3,5]}, count,
           "In y_{mn+r}=sum_j h_j x_{mn+r-j}, residue matching forces h phase (r-s) mod m and one block delay exactly when s>r. This coefficient derivation proves the matrix formula for every finitely supported causal kernel.")

    count = 0
    for h in kernels:
        for g in kernels:
            check(convolution(h,convolution(g,x)) == convolution(convolution(h,g),x))
            count += 1
    record("FIR composition", {"input_length":64,"ordered_kernel_pairs":25},count,
           "Both routes are the same finite double sum; distributivity and finite reindexing prove convolution associativity and polyphase-matrix composition universally.")

    phis = {2:[1,1],3:[1,1,1],4:[1,0,1],5:[1,1,1,1,1],6:[1,-1,1]}
    count = 0
    for m,phi in phis.items():
        for n in range(64):
            for r in range(m):
                p = [0]*m
                for j in range(m):
                    p[(j*(n-r))%m] += 1
                reduced = reduce_cyclotomic(p,phi)
                expected = [m if n%m==r else 0]+[0]*(len(phi)-2)
                check(reduced == expected)
                count += 1
    record("Root-of-unity selector over characteristic zero", {"m":[2,6],"n":[0,63],"all_residues":True},count,
           "For a primitive mth root zeta, m^{-1}sum_j zeta^{j(n-r)} is the residue indicator by the finite geometric sum. Computation uses exact cyclotomic quotient polynomials. The m inverse and primitive root hypotheses are essential.",
           ["No claim in characteristics dividing m.","For EGF input the selected coefficient retains its original n! denominator."])

    count = 0
    for e in range(-7,8):
        for o in range(-7,8):
            a,d = Q(e+o),Q(e-o)
            check((a+d)/2 == e and (a-d)/2 == o)
            check((a*a+d*d)/2 == e*e+o*o)
            count += 1
    record("Haar block sign and normalization", {"even_sample":[-7,7],"odd_sample":[-7,7]},count,
           "With a=(e+o)/sqrt(2), d=(e-o)/sqrt(2), the transpose is the inverse and squared energy is preserved. Exact rational checks represent the common sqrt(2) symbolically by unnormalized sums/differences.",
           ["Block pairing (x_2n,x_{2n+1}) differs from causal taps followed by even downsampling, which pairs (x_2n,x_{2n-1})."])

    yplus = convolution([1,1],x)
    yminus = convolution([1,-1],x)
    for n in range(len(yplus[::2])):
        check(coeff(yplus,2*n) == coeff(x,2*n)+coeff(x,2*n-1))
        check(coeff(yminus,2*n) == coeff(x,2*n)-coeff(x,2*n-1))
    record("Causal Haar pair alignment", {"input_length":64},len(yplus[::2])*2,
           "The causal taps (1,+/-1) followed by even downsampling have channel rows (1,+/-q), before sqrt(2) normalization. This is an exact indexing identity.")


def streaming_resampling_checks():
    x = [(-1)**n*(n+1) for n in range(41)]
    kernels = [[1],[0,1],[1,-1],[1,2,1],[-2,0,3,1,-1]]
    count = 0
    for h in kernels:
        expected = convolution(h,x)[:len(x)]
        for chunk_size in range(1,11):
            history = [0]*(len(h)-1)
            output = []
            for start in range(0,len(x),chunk_size):
                for value in x[start:start+chunk_size]:
                    window = [value]+history
                    output.append(sum(t*v for t,v in zip(h,window)))
                    history = window[:len(h)-1]
            check(output == expected)
            for _ in range(len(h)-1):
                window = [0]+history
                output.append(sum(t*v for t,v in zip(h,window)))
                history = window[:len(h)-1]
            check(output == convolution(h,x))
            count += 1
    record("Streaming FIR state across chunk boundaries", {"input_length":41,"chunk_size":[1,10],"kernel_lengths":[1,2,3,5]},count,
           "The retained state contains the preceding L-1 input samples. Induction on sample count makes each output equal to causal convolution. Both prefix outputs and complete tails after L-1 zero flushes are checked.",
           ["Chunk-local reset is not a correct stateful implementation.","No FFT or floating-point error claim."])

    count = 0
    for L in range(1,6):
        for M in range(1,6):
            for h in kernels:
                up = [0]*(L*(len(x)-1)+1)
                for k,value in enumerate(x):
                    up[L*k] = value
                direct = convolution(h,up)[::M]
                explicit = [sum(coeff(h,M*n-L*k)*value for k,value in enumerate(x))
                            for n in range(len(direct))]
                check(direct == explicit)
                count += 1
    record("Integer-rate rational resampling", {"L":[1,5],"M":[1,5],"input_length":41,"kernel_lengths":[1,2,3,5]},count,
           "Zero insertion puts x_k at Lk. Filtering and selecting output Mn gives y_n=sum_k h_(Mn-Lk)x_k by substitution. The same identity determines phase scheduling.",
           ["An arbitrary finite kernel is not automatically an adequate anti-alias or anti-imaging filter.","This is a discrete algebraic resampling identity, not a continuous reconstruction theorem."])

    e = [3,-1,4,0,2,-5,1,2]
    o = [1,2,-2,4,0,3,-1,5]
    predictors = [[1],[1,-1],[0,2,-3],[Q(1,2),Q(-2,3)]]
    updates = [[0],[0,-1],[2,-1],[Q(-1,4),Q(2,5)]]
    for p in predictors:
        for u in updates:
            pe = convolution(p,e)
            d = [o[n]-coeff(pe,n) for n in range(len(e))]
            ud = convolution(u,d)
            s = [e[n]+coeff(ud,n) for n in range(len(e))]
            eback = [s[n]-coeff(ud,n) for n in range(len(e))]
            peback = convolution(p,eback)
            oback = [d[n]+coeff(peback,n) for n in range(len(e))]
            check(eback == e)
            check(oback == o)
    record("Signed predict/update lifting inversion", {"input_pairs":8,"signed_rational_filter_pairs":16},0,
           "Each triangular step is undone by subtracting its known contribution; reversing step order reconstructs E then O without inverting P or U. The displayed scalar-polynomial matrix has determinant one.")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output",required=True)
    args = parser.parse_args()
    sequence_checks()
    additional_sequence_checks()
    polyphase_checks()
    streaming_resampling_checks()
    result = {"status":"PASS","software":{"python":platform.python_version(),"dependencies":"Python standard library only"},
              "randomness":{"used":False},"families":records,
              "total_checks":sum(r["checks"] for r in records),
              "independence":"No author generator imported; all enumerators constructed independently.",
              "interpretation":"Exact bounded execution plus separately stated structural derivations; no Lean certificate and no inference of universal proof from counts.",
              "script_sha256":hashlib.sha256(Path(__file__).read_bytes()).hexdigest()}
    path = Path(args.output)
    path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps(result,indent=2)+"\n")
    print(json.dumps({"status":result["status"],"families":len(records),"total_checks":result["total_checks"],"output":str(path)}))


if __name__ == "__main__":
    main()
