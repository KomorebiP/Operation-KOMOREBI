# Weighted central-binomial Hankel determinants

**Uniform recurrences and complete mixed-linear order classification**

Komorebi P. Final edition 1.0. 21 November 2026.

## Abstract

We study Hankel determinants built from polynomially weighted central-binomial
moments and first-order differential operators. For quadratic weights with the
identity operator, we prove an explicit uniform constant-coefficient recurrence
of order at most 63 and exhibit a specialization with minimal eventual order
63. For linear weights and arbitrary first-order operators, we prove a uniform
bound of 112, show that it is generically attained, and give a complete finite
algebraic rule for the minimal eventual order at every parameter over a
characteristic-zero field. The classification includes zero parameters,
repeated roots, spectral collisions, and their intersections. Exact portable
certificates support the finite algebraic leaves of the proofs. The empty
determinant is retained separately from recurrences beginning at index one.

This edition consolidates Theorems K, L, M, and N from the completed source
edition. Its mathematical review provenance is project self-review.
Independent review, historical novelty, and Lean formalization are unassessed.

## 1. Results, conventions, and reading guide

Let the coefficient field have characteristic zero. For the mixed linear
family, fix four field elements and define
\[
 \begin{aligned}
 \mu_{2m}&=u(a+bm)\binom{2m}{m},\\
 \mu_{2m+1}&=v(2m+1)(a+bm)\binom{2m}{m},\\
 W_N&=\det(\mu_{i+j})_{0\le i,j<N},\qquad W_0=1.
 \end{aligned}                                                    \tag{E1}
\]
These are the moments obtained by applying the operator
\(\mathcal D=u+v\partial_x\) to the even-moment functional with weight
\(P(m)=a+bm\). The elementary formal binomial expansion
\((1-4z)^{-1/2}=\sum_{m\ge0}\binom{2m}{m}z^m\) explains the
central-binomial kernel. The proofs below work with formal Laurent series;
they require no positive measure or endpoint integrability.

Write \(S\) for the forward shift: \((SW)_N=W_{N+1}\).
An eventual scalar constant-coefficient recurrence of order \(r\) is an
identity \(\sum_{j=0}^r d_jW_{N+j}=0\), with \(d_r=1\), for all
sufficiently large \(N\). Its coefficients belong to the original field.
The minimal eventual order is the least such \(r\); order zero means
eventual vanishing. It is distinct from the size of a transfer matrix or the
degree of an unreduced candidate denominator.

**Main result.** Theorems M and N together determine the minimal eventual
order of (E1) for every \((a,b,u,v)\). Theorem L supplies a uniform bound
of 112 and its generic sharpness. The reduced recurrences in the
classification hold from \(N=1\); the convention \(W_0=1\) is separate.

| Family | Result | Scope of minimality |
|---|---|---|
| \(P(m)=a+bm+cm(m-1)\), identity operator | Theorem K: uniform bound 63 | Sharp at \((a,b,c)=(1,1,1)\); pointwise classification is not asserted |
| Linear weight, first-order operator | Theorem L: uniform bound 112 | Minimal order 112 on a nonempty Zariski-open set |
| Mixed linear family, \(abuv=0\) | Theorem M: complete ordered boundary table | Every zero-parameter intersection included |
| Mixed linear family, \(abuv\ne0\) | Theorem N: exact polynomial-gcd decision rule | Every root multiplicity and spectral collision included |

To classify a mixed-linear parameter, first test whether both weight
coefficients or both operator coefficients are zero; the order is then zero.
For every other point on \(abuv=0\), read the ordered table in
[Theorem M](#final-4-the-coordinate-boundary).
For \(abuv\ne0\), use \(t=b/a\) and \(q=(v/u)^2\), form the
degree-four and degree-sixteen polynomials in
[Theorem N](#final-5-every-nonzero-mixed-parameter), and compute the stated
gcd degrees and collision correction. This is a finite algebraic rule;
it does not require numerical root separation or recurrence fitting.

The quadratic functional developed in [section 2](#final-2-the-formal-functional-and-the-quadratic-bound)
provides the common proof foundation. [Section 3](#final-3-the-uniform-mixed-linear-bound)
then treats general quartic functionals and derives (E1). Sections 4 and 5
complete its boundary and nonzero classifications, respectively.
[Section 6](#final-6-certificates-and-reproduction) explains the certificate
logic and gives one-command reproduction instructions.

The letters K, L, M, and N, and their equation labels, are retained so the
paper can be checked against the archived sources. Subsection references
such as K.6 or N.3 refer within the corresponding theorem section. Auxiliary
symbols are local to their sections: in particular, the polynomial
coefficient \(q\) in K is distinct from the normalized ratio \(q\) in N.
The normalization of \(R\) is restated whenever it changes.

The [exact order explorer](https://komorebip.github.io/Operation-KOMOREBI/sequence-hankel-compression.html#interior-order-calculator)
accepts rational normalized parameters and links to this paper. The theorem
also covers algebraic parameters, including the order-64 triple-root case.
Negative rational \(q\) is interpreted in a quadratic extension containing
its square root; it is not a claim that a negative number is a real square.
