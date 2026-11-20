# A uniform order-nine recurrence for every linear weight

Author: **Komorebi P.**
Checkpoint: **SEQ-DH-2026-11-20-001-LINEAR**.
Status: proof with an exact finite polynomial-identity certificate; self-reviewed.
Historical novelty: unassessed.

## 1. Uniform statement

Over any characteristic-zero field, define
\[
 \mu_{2m}=(a+bm)\binom{2m}{m},\qquad \mu_{2m+1}=0,
 \qquad W_N=\det[\mu_{i+j}]_{0\le i,j<N},\qquad W_0=1.
\]
Here \(a,b\) are arbitrary, including zero. Let \(S\) be the forward shift:
\((SW)_n=W_{n+1}\).

**Theorem F.** For every \(n\ge1\),
\[
 \boxed{\left[(S-2a)\bigl(S^2-4(a-b)S+4a^2\bigr)\right]^3W_n=0.}  \tag{8}
\]
The order-nine annihilator is monic at every parameter. Its minimal eventual
order is exactly nine at \(a=b=1\), and on a nonempty Zariski-open set of
parameters. It need not be minimal at exceptional parameters.

Equivalently,
\[
 \boxed{\sum_{N\ge0}W_Nz^N=
 \frac{\sum_{j=0}^{9}N_j(a,b)z^j}
 {[(1-2az)(1-4(a-b)z+4a^2z^2)]^3}.}                            \tag{9}
\]
All expressions are polynomial identities in \(a,b\); no root choices or
division by \(a,b\) are required.

The explicit numerator coefficients are

| \(j\) | \(N_j(a,b)\) |
|---|---|
| 0 | \(1\) |
| 1 | \(-17a+12b\) |
| 2 | \(2(64a^2-77ab+24b^2)\) |
| 3 | \(-8(70a^3-105a^2b+51ab^2-7b^3)\) |
| 4 | \(8a(196a^3-315a^2b+168ab^2-30b^3)\) |
| 5 | \(-32a(91a^4-140a^3b+66a^2b^2-8ab^3-2b^4)\) |
| 6 | \(32a^3(112a^3-147a^2b+48ab^2+2b^3)\) |
| 7 | \(-128a^4(2a-b)(11a^2-5ab-b^2)\) |
| 8 | \(640a^7(2a-b)\) |
| 9 | \(-256a^9\) |

For a zeroth-order operator \(c_0\) multiplying the functional, the determinant
becomes \(c_0^N W_N\), and (9) applies with \(z\) replaced by \(c_0z\).
This also includes \(c_0=0\), when only the empty determinant remains.

## 2. Complete polynomial-identity reduction

Use the signed transfer of Theorem A with the **fixed upper bound** \(M=1\),
even at parameters where \(b=0\). Thus the difference stencil is always
\[
 (1-E_{\rm back}^2)^2,\qquad w=4,\qquad K=9,\qquad s=70.
\]
The band and transfer formulas are polynomial in \(a,b\). In particular every
entry of the stationary transfer matrix \(T(a,b)\) is homogeneous of degree
one, and every coordinate of the state vector \(v_9(a,b)\), after nine row
transitions, is homogeneous of degree nine.

Write
\[
 \chi_{a,b}(X)=
 [(X-2a)(X^2-4(a-b)X+4a^2)]^3
   =\sum_{j=0}^{9}\gamma_j(a,b)X^j.
\]
The coefficient \(\gamma_j\) is homogeneous of degree \(9-j\). Therefore
every coordinate of
\[
 \mathcal R(a,b)=\sum_{j=0}^{9}\gamma_j(a,b)T(a,b)^jv_9(a,b)       \tag{10}
\]
is a homogeneous polynomial of degree 18.

The exact certificate evaluates (10), in its **complete 70-state vector**,
at the nineteen points
\[
 (a,b)=(0,1),(1,1),\ldots,(18,1).
\]
Every vector is exactly zero. The verifier performs no numerical rank
test, tolerance comparison, random sampling, or scalar-prefix fitting.
For a polynomial of degree at most 18, nineteen distinct evaluations
determine all coefficients. Hence every coordinate of
\(\mathcal R(a,1)\) is the zero polynomial. Homogeneity then implies
\(\mathcal R(a,b)=0\) identically, including \(b=0\).

Apply \(e^{\mathsf T}T^{n-9}/4\) to (10). Theorem A proves (8) for every
\(n\ge9\).

It remains to check \(1\le n\le8\). Each determinant \(W_N\) is homogeneous
of degree \(N\) in \(a,b\), directly from its defining \(N\)-square matrix.
Thus
\[
 \sum_{j=0}^{9}\gamma_j(a,b)W_{n+j}(a,b)
\]
is homogeneous of degree \(n+9\le17\). The same nineteen evaluation
points give zero for every one of these eight expressions, so the same
polynomial-identity argument proves them at all \(a,b\). This establishes
the exact starting index in (8).

This is a proof by a bounded, complete algebraic certificate. The
universality comes from the explicit degree bounds, not from believing
that a finite sequence prefix continues.

## 3. Numerator and minimality certificates

Let \(D(z)=[(1-2az)(1-4(a-b)z+4a^2z^2)]^3\).
The coefficient of \(z^N\) in \(D(z)\sum W_Nz^N\) vanishes for \(N\ge10\)
by (8). For \(0\le N\le9\), the coefficient is homogeneous of degree \(N\)
in \(a,b\). The code reconstructs all its coefficients from \(N+1\) exact
values at \(b=1\), by Lagrange interpolation. Those reconstructed
coefficients are precisely the numerator table in (9). Direct monomial
determinants at sizes 0 through 17 are separately compared with the Schur
implementation at all nineteen evaluation points.

For \(a=b=1\), the numerator and denominator specialize to
\[
 \begin{aligned}
 N(z)={}&1-5z+22z^2-72z^3+152z^4-224z^5\\
        &{}+480z^6-640z^7+640z^8-256z^9,\\
 D(z)={}&(1-2z)^3(1+4z^2)^3.
 \end{aligned}
\]
The exact Euclidean algorithm in the verifier constructs and checks
polynomials \(U,V\in\mathbb Q[z]\) with
\[
 U(z)N(z)+V(z)D(z)=1.
\]
The rational OGF is therefore reduced, with denominator of degree nine.
Any eventual recurrence of smaller order would supply a denominator of
smaller degree, which is impossible. Thus the eventual order is exactly nine.
The resultant of the general numerator and denominator is consequently a
nonzero polynomial in \(a,b\); away from its zero set and from degree-loss
parameters, the same minimal order holds.

At \(b=0\), (9) reduces after cancellation to
\((1-az)/(1-2az)\), consistent with the constant-weight formula.
At \(a=0\), its denominator reduces to \((1+4bz)^3\).
The unsimplified order-nine annihilator remains valid in both cases.

## 4. Certificate locator and coverage

The exact verifier is tools/verify_sequence_linear_hankel.py. Run it with an
--output JSON filename from the source root. It emits the polynomial numerator,
the complete evaluation range, and the rational Bezout coefficients.
The implementation is tools/sequence_rational_hankel.py; the source download
contains both programs and their defining mathematical notes.

The completed run contains:

- 19 complete vector identities;
- 152 early-index identities;
- 342 independent direct determinant comparisons;
- 115 additional rational or degenerate parameter checks;
- a checked polynomial Bezout identity proving the stated sample minimality.

The degree/homogeneity reduction above is the necessary bridge between those
finite records and the uniform theorem. Its separate self-review is recorded
in the [self-review](RATIONAL_HANKEL_REVIEW.md). There is no independent review
or historical-novelty verdict. The general rationality proof is in
[Rational Hankel tails](RATIONAL_HANKEL_TAILS.md).
