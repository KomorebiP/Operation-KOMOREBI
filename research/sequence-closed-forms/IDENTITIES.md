# Closed forms for integer sequences: Collections II and III

Author: Komorebi P.  
Source dates: 18–19 November 2026.

This is the public, source-linked companion for 24 exactly generated integer records and eight research families. The underlying research archives are `Komorebi_Closed_Forms_Collection_II_2026-11-18` and `Komorebi_Closed_Forms_Collection_III_2026-11-19`. The notes below give the conventions, derivations for the catalogued records, and the precise boundaries of the checks. Published source derivations are not historical-priority claims. The two source archives contain more general results and longer proofs than the finite catalogue exposes.

## 1. Sparse two-delay coefficients

For positive integers `p,q,r` and integer weights `u,v`, define

```text
C_n = [z^n] (1-u*z^p-v*z^q)^(-r),  C_0=1, C_n=0 for n<0.
```

The formal binomial theorem gives the finite, exact formula

```text
C_n = sum_{i,j >= 0, p*i+q*j=n}
        (r)_(i+j) * u^i * v^j / (i! * j!).
```

It holds for complex `r,u,v` as a formal coefficient identity. Differentiating the generating function and multiplying by `1-u*z^p-v*z^q` gives

```text
n*C_n = u*(n+(r-1)*p)*C_(n-p)
      + v*(n+(r-1)*q)*C_(n-q).
```

The generator uses this exact recurrence for integer specializations. When the delays coincide, replace `u,v` by their sum. Terms at unsupported degrees vanish. Collection II proves a terminating hypergeometric representation for arbitrary positive delays, including zero weights and exceptional parameters; it is not inferred from matching finite terms.

## 2. Padovan normalization and powers

We use `P_0=1, P_1=P_2=0` and `P_n=P_(n-2)+P_(n-3)` for `n>=3`. Hence

```text
P(z)=sum_(n>=0) P_n*z^n = (1-z^2)/(1-z^2-z^3).
```

For each positive integer `r`,

```text
[z^n] P(z)^r = sum_(j=0)^min(r,floor(n/2))
                  (-1)^j * binom(r,j) * C_(n-2j),
C_m = [z^m](1-z^2-z^3)^(-r).
```

This is a finite binomial-convolution identity. The library records `r=1,2` with 24 integer coefficients each. The original Padovan source convention is retained: the first 12 terms of `r=1` are `1,0,0,1,0,1,1,1,2,2,3,4`.

## 3. Four-block logarithmic polynomials

For an indeterminate `a` put `s=x/sqrt(2)` and

```text
V_a(x) = (cosh(s)-a*s*sinh(s))*(cos(s)+a*s*sin(s)).
A_m(a) = 1 - 4*m*a + 2*m*(4*m-1)*a^2.
V_a(x) = sum_(m>=0) (-1)^m A_m(a)*x^(4m)/(4m)!.
```

The last identity follows by applying `1-a*(xD)+(a^2/2)*(xD)*(xD-1)`, where `D=d/dx`, to `cosh(s)*cos(s)`. Define

```text
-V_a'(x)/V_a(x) = sum_(m>=1) T_m(a)*x^(4m-1)/(4m-1)!.
```

Comparing coefficients gives the exact integer-polynomial recurrence

```text
T_m(a) = (-1)^(m+1)*A_m(a)
         + sum_(k=1)^(m-1) (-1)^(k+1)
              *binom(4m-1,4k)*A_k(a)*T_(m-k)(a).
```

The induction establishes `T_m(a)` in `Z[a]`. The leading coefficient is `[a^(2m)]T_m=(4m-1)!/4^(m-1)`. The first polynomials are `T_1=6a^2-4a+1` and `T_2=1260a^4-1680a^3+952a^2-272a+34`. The source archive proves strict positivity for all real `a`; the finite catalogue does not substitute for that proof. The integer record index begins at `m=1`; its underlying analytic source exponent is `4m-1`, not `m`.

## 4. Weighted Hankel determinants

For integer `d>=0`, let

```text
F_d[x^(2m)] = m^fall(d)*binom(2m,m),  F_d[x^(2m+1)]=0,
mu_n = F_d[x^n]+c*n*F_d[x^(n-1)],
W_N^(d)(c)=det(mu_(i+j))_(0<=i,j<N), W_0=1.
```

Here `m^fall(d)` is the falling factorial. The initial singular block satisfies `W_N=0` for `1<=N<=2d`, and

```text
W_(2d+1) = (-1)^d * ((2d)!/d!)^(2d+1).
```

The vanishing follows because the first row has zero entries across that range. At size `2d+1`, reversing the columns gives a triangular matrix with common diagonal `(2d)!/d!` and reversal sign `(-1)^d`. Collection III derives a fixed-size closed form in Chebyshev polynomials that remains valid at coalescing roots, together with the minimal eventual recurrence order. The published records use direct fraction-free integer determinants with `d=0,1` and `c=0,1`.

## 5. Beta-binomial moments and determinants

Let `L>=0`, `a,b>0`, and `s=a+b`. For `0<=k<=L` set

```text
w_k = binom(L,k)*(a)_k*(b)_(L-k)/(s)_L,
M_n = sum_(k=0)^L k^n*w_k,
U_n = (s)_L*M_n = sum_(k=0)^L k^n*binom(L,k)*(a)_k*(b)_(L-k).
```

Here `(a)_j` is the rising factorial and `0^0=1`. Normalization follows from multiplying `(1-z)^(-a)` and `(1-z)^(-b)`. For positive integer `a,b`, the unnormalized `U_n` is an integer.

Let `D_N=det(M_(i+j))`, with `D_0=1`. Collection III proves

```text
D_N = prod_(j=0)^(N-1)
    [j!*(a)_j*(b)_j*L^fall(j)*(s+L)_j / (s)_(N+j-1)].
```

Every determinant beyond size `L+1` vanishes because the measure has `L+1` support points. The library's integer determinant windows are those of `U_n`, so `H_N=(s)_L^N*D_N`. This normalization factor is essential: `D_N` itself need not be an integer.

## 6. Families currently represented only by definitions

Collection II derives formulas for polynomially weighted binomial transforms, and Collection III derives an entire scaling function `{}_0F_3(; -1/2,-1/4,1/4; -t^2/256)`, including its zero structure and reciprocal-zero sums. These two families are linked from the generalized-family index but have **no invented integer catalogue records**. They should not be counted as separate integer sequences until an exact integer specialization is provided and checked.

## 7. Reproduction and claim boundaries

Run `python3 tools/test_sequence_closed_forms.py` from the repository root (Python 3.10 or later). The test suite checks independent finite coefficient sums, ordinary generating-series convolutions, selected logarithmic-series coefficients, determinant identities, integer normalization, all 24 instances, source offsets and family membership. The standard library is sufficient for these catalogued specializations.

The two original publication archives recorded 205,982 and 33,689 exact assertions respectively. Those counts describe the archived, wider verification suites and **are not** the number of assertions in the new repository tests. The archives included independent proof reviews and, for the full results, SymPy dependencies. The sequence search, charts and receipts remain finite windows; no result here claims OEIS novelty, uniqueness, or mathematical priority.

The 24 new records have not yet been run through the pinned historical OEIS bulk snapshot. Their OEIS panels explicitly state **Not yet compared**. The old catalogue's comparison manifest and all preexisting record digests remain unchanged. Record IDs use the `KFOR-CF-` prefix and are local, not OEIS A-numbers.
