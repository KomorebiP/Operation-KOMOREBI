# Five-core packets and a valid auxiliary root-resolution problem for Lehmer

Research continuation, 26 September 2026.

## Claim boundary

This note does not prove that Ramanujan's tau function is nonzero at every prime. It supplies an exact finite packet polynomial, two explicit root-resolution certificates, and a general limitation on the index-prime valuation of individual packets. The hook-length formula, five-core coding, and unweighted five-core count are classical dependencies. No claim of historical priority is made for the repackaging or its consequences. The computations are exact bounded evidence, not a proof for all primes. No Lean compilation was performed.

The preceding research note in the parent folder remains unchanged. In particular, this construction does not restore the refuted claim that tau is a single integral analytic function of its prime index.

## 1. Classical reduction to five-core packets

Write

\[
\Delta(q)=q\prod_{m\ge1}(1-q^m)^{24}=\sum_{n\ge1}\tau(n)q^n.
\]

The Nekrasov--Okounkov identity, in Han's formulation (Theorem 1.2), is

\[
\prod_{m\ge1}(1-q^m)^{z-1}
=\sum_\lambda q^{|\lambda|}\prod_{h\in H(\lambda)}(1-z/h^2).
\]

At z=25, every partition having a hook of length 5 contributes zero. The remaining partitions are precisely the 5-cores. Thus

\[
\tau(n)=\sum_{\substack{\lambda\vdash n-1\\\lambda\text{ a 5-core}}}
\prod_{h\in H(\lambda)}(1-25/h^2).
\]

Han's Theorem 1.1 identifies these cores with

\[
\mathcal V_n=\{v\in\mathbb Z^5: v_i\equiv i\pmod5,\ \sum_i v_i=0,\ \sum_i v_i^2=10n\}.
\]

The exact weight is

\[
W(v)=\frac1{288}\prod_{0\le i<j\le4}(v_i-v_j),
\qquad
\boxed{\tau(n)=\sum_{v\in\mathcal V_n}W(v).}
\]

Here 288=1!2!3!4!, and the sign in Han's formula is positive for t=5.

### Integrality and reduction modulo five

The determinant of the integer-valued binomial basis at the integers v_i gives

\[
\det\left[\binom{v_i}{j}\right]_{0\le i,j\le4}
=\frac{\prod_{i<j}(v_j-v_i)}{\prod_{j=0}^4j!}=W(v).
\]

There are ten reversed differences, so the sign is unchanged. Generalized binomial coefficients at negative integers are integers. Thus W(v) is integral. Distinct coordinate residues imply that every difference is nonzero and prime to 5. Moreover

\[
W(v)\equiv\frac{\prod_{i<j}(i-j)}{288}=1\pmod5.
\]

The Garvan--Kim--Stanton five-core count (equation (5.3)) gives

\[
|\mathcal V_n|=\sum_{d\mid n}\chi_5(d)\frac nd,
\qquad \chi_5(d)=\left(\frac d5\right).
\]

For a prime p, the number of packets is p+chi_5(p). Consequently tau(p)=p+chi_5(p) modulo 5, and for p different from 5 a zero requires p=4 modulo 5. This recovers a congruence, not Lehmer nonvanishing.

## 2. A general index-prime obstruction to a naive termwise filtration

Let p>20 be prime, v in V_p. For i<j,

\[
0<(v_i-v_j)^2\le2(v_i^2+v_j^2)\le20p<p^2.
\]

Thus no difference is divisible by p. Since p does not divide 288,

\[
\boxed{v_p(W(v))=0\quad\text{for every }v\in\mathcal V_p.}
\]

Every individual packet is an index-prime unit. In particular, the representation does not have an increasing termwise p-adic depth analogous to an Euler inverse kernel with explicit p^{2m} factors. Divisibility at p is entirely a cancellation between units. This does not rule out useful groupings or transformations of the packets.

At p=2411, the shell has 2412 packets, all 2411-adic units, while their sum

\[
\tau(2411)=4542041100095889012
\]

has valuation one. This is independently checked below.

## 3. An exact finite auxiliary polynomial

For each v in V_n, write v_i=i+5c_i, with integer c_i. Define

\[
P_n(T)=\sum_{v\in\mathcal V_n}\prod_{i<j}\bigl[(i-j)+T(c_i-c_j)\bigr]
=\sum_{j=0}^{10}B_j(n)T^j\in\mathbb Z[T].
\]

Then

\[
\boxed{P_n(5)=288\tau(n)},\qquad B_0(n)=288|\mathcal V_n|.
\]

The degree is at most ten because each packet is a product of ten linear factors. For fixed n this is an actual integral polynomial. There is no assumption that the family depends analytically on n.

Set

\[
\mu_n=\min_{B_j(n)\ne0}\{j+v_5(B_j(n))\},
\qquad
G_n(U)=5^{-\mu_n}P_n(5U)\in\mathbb Z[U].
\]

Its residual polynomial is nonzero, and

\[
\boxed{v_5(\tau(n))=\mu_n+v_5(G_n(1)).}
\]

We use v_5(0)=infinity. The normalization does not require assuming tau(n) is nonzero, since B_0(n)>0 for every n represented here.

This is a legitimate place to apply local root analysis. The variable U is auxiliary; the original coefficient is recovered at U=1.

## 4. Simple-root certificate at p=499

The exact eleven coefficients B_j, ordered j=0,...,10, are

```
[144000, -360000, 1063040, 28418240, -148872808,
 209474504, 2422451240, 16445000, 8107402848,
 -11893316304, -1160632800]
```

The weighted coefficient valuations are

```
[3, 5, 3, 4, 4, 5, 7, 11, 8, 9, 12]
```

Thus mu_499=3 and

\[
\overline G_{499}(U)=2+3U^2=3(U-1)(U+1)\quad\text{over }\mathbb F_5.
\]

At the relevant point U=1,

\[
G_{499}(1)\equiv10\pmod{25},\qquad G'_{499}(1)\equiv1\pmod5.
\]

The simple root near 1 lifts to rho=16 modulo 25: substituting 1+5d gives 10+5d modulo 25, so d=3 modulo 5. On this residue class the divided difference is a unit; hence

\[
v_5(G_{499}(U))=v_5(U-\rho),\qquad U\equiv1\pmod5.
\]

Since v_5(1-rho)=1,

\[
\boxed{v_5(\tau(499))=4.}
\]

Both simple residual roots were lifted uniquely to 12 base-five digits. The histories are in RESULTS.json. These lifts are finite representations of roots of the auxiliary polynomial, not roots in the prime index.

## 5. Multiple-root obstruction at p=16249

Here the shell has 16250 packets and the coefficients are

```
[4680000, -13320000, -199541600, -26375464320,
 737398074300, -39838758304992, -746041848478320,
 -6990990388478280, 21389931029028020,
 -64003552771660728, 3937759175521630080]
```

Their weighted valuations are

```
[4, 5, 4, 4, 6, 5, 7, 8, 9, 9, 11]
```

Therefore mu_16249=4 and

\[
\overline G_{16249}(U)=3+U^2+U^3=(U-1)^2(U-2)\pmod5.
\]

The relevant residual root U=1 is double, but exact coefficient reduction gives

\[
G_{16249}(1)\equiv15\pmod{25},\qquad G'_{16249}(1)\equiv0\pmod5.
\]

For every y in Z_5, the polynomial Taylor identity has the integral form

\[
G(1+5y)=G(1)+5yG'(1)+25y^2H(y),\qquad H\in\mathbb Z_5[y].
\]

Hence

\[
\boxed{G_{16249}(1+5y)\equiv15\pmod{25}\quad\text{for every }y\in\mathbb Z_5.}
\]

The entire residue class U=1 modulo 5 has valuation exactly one, so its double residual root has no five-adic lift. In particular

\[
\boxed{v_5(\tau(16249))=4+1=5.}
\]

The independent coefficient calculation gives

\[
\tau(16249)=133116215274958169206250.
\]

The universal statement about the residue class follows from the Taylor identity and two exact residues. The 625 sampled y-values in the checker are only a secondary implementation test.

## 6. Comparison cases and limits

| p | Number of packets | mu_p | v_5(G_p(1)) | v_5(tau(p)) |
|---:|---:|---:|---:|---:|
|499|500|3|1|4|
|1249|1250|3|0|3|
|2999|3000|3|1|4|
|4999|5000|3|0|3|
|16249|16250|4|1|5|
|18749|18750|3|0|3|

The p=1249 and p=18749 cases show why the valuation of the unweighted packet count is not itself the answer. Individual packet signs are mixed; positivity is unavailable without a further transformation.

Nothing here establishes that G_p(1) is nonzero for every prime p. That remains equivalent to Lehmer at primes. In particular:

* A degree bound of ten is not a valuation bound. Even the degree-one polynomials U-(1+5^k) take values at U=1 of unbounded finite valuation.
* Arbitrarily deep fixed-modulus divisibility at varying primes is compatible with all individual coefficients being nonzero.
* The exact per-prime local problem is not a uniform theorem about how the family G_p varies with p.
* The p-adic unit lemma prevents importing an automatic index-prime termwise filtration, but not constructing a new grouped filtration.

A proof through this representation would require a uniform arithmetic restriction on the shell moments B_j(p) that excludes U=1 as an exact root. The computations have not supplied that restriction.

## 7. Executed audit

Run:

```
python3 continuation_5core/check_five_core.py
```

Scope: all integers 1<=n<=128, all 303 primes at most 2000, and the additional primes 2411, 2999, 4999, 16249, 18749. There are 405 distinct shell indices and 308 prime shell indices. A separate hook enumeration covers partition sizes 0 through 24.

Results:

* 326585 packet-polynomial checks.
* 405 shell sums agree with independent Jacobi triangular recurrence coefficients.
* 308 prime shell counts agree with the exact divisor-character formula.
* 322378 individual index-prime unit assertions checked.
* 25 independent hook-weight sums agree, with 233 surviving cores and 7105 annihilated noncore partitions.
* Both p=499 simple roots lift uniquely to 12 base-five digits.
* The p=16249 double-root residue class was also checked at 625 representative y-values.
* The defining eta-product coefficients independently agree with the Jacobi recurrence through n=128.

All arithmetic is integer/rational or finite-ring arithmetic. No numerical floating-point approximation enters the mathematical calculations. The retained run passed without assertion failures, in approximately 9.83 seconds. Input file hashes before and after match. The manifest schema validator was not run, and no formal proof assistant was used.

## Sources

See SOURCES.md for exact source statements and convention translation. Classical formulas are not authenticated by the bounded code checks alone.
