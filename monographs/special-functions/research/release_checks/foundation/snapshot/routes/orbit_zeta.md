# Orbit spectral zeta family

Base checkpoint: SF-DISCOVERY-001. This is a worked spectral family associated with a classical Mittag-Leffler seed. Historical priority and global meromorphic continuation are not claimed.

## Definition

For an integer N>=2 define

\[
d_N(w)=\sum_{n\ge0}\frac{(-1)^n w^n}{(Nn)!}=E_{N,1}(-w),\qquad D_N(z)=d_N(z^N).
\]

The variable w identifies the N rotations of each nonzero D_N zero. A zero of d_N of multiplicity m corresponds to N distinct zeros of D_N, each of multiplicity m. Count d_N zeros w_j with multiplicity. Fix Arg(w_j) in (-pi,pi], and set

\[
\mathcal Z_N(s)=\sum_j\exp[-s(\log|w_j|+i\operatorname{Arg}w_j)],\qquad \Re s>1/N.
\]

The branch convention is part of this definition. For positive integer s it is immaterial. No simple-zero assumption is needed.

## Convergence and canonical product

For r=|w|, the series gives |d_N(w)|<=exp(r^(1/N)). Since N>=2 its order is at most 1/N<1. Hadamard factorization therefore has genus zero and a constant exponential factor. Since d_N(0)=1,

\[
d_N(w)=\prod_j(1-w/w_j).
\]

The zero-count bound from finite-order factorization gives O_epsilon(R^(1/N+epsilon)) zeros in |w|<R. Thus the zeta series converges absolutely and locally uniformly when Re s>1/N. On compact sets in that half-plane, the bounded arguments contribute only a bounded multiplier. The function is holomorphic there. The sequence is infinite: otherwise the genus-zero product would make the nonpolynomial d_N a polynomial.

This use of Hadamard factorization is an established external theorem, checked against Noam Elkies's Harvard finite-order-function notes, first theorem (https://people.math.harvard.edu/~elkies/M259.02/prod.pdf). The seed identification is exactly NIST DLMF 10.46.3 (https://dlmf.nist.gov/10.46).

## Exact integer values without locating zeros

Logarithmically differentiate the product on a sufficiently small disk about zero:

\[
-w\frac{d_N'(w)}{d_N(w)}=\sum_{k\ge1}\mathcal Z_N(k)w^k.
\]

Let a_n=(-1)^n/(Nn)!, and let b_k=Z_N(k). Multiplying the last series by d_N gives the exact rational triangular law

\[
b_k=-k a_k-\sum_{j=1}^{k-1}a_j b_{k-j}.
\]

In particular

\[
\mathcal Z_N(1)=\frac1{N!},\qquad
\mathcal Z_N(2)=\frac1{(N!)^2}-\frac2{(2N)!},
\]
\[
\mathcal Z_N(3)=\frac1{(N!)^3}-\frac3{N!(2N)!}+\frac3{(3N)!}.
\]

All positive integer values are rational. Their reality/rationality does not imply that the individual zeros are real or positive. This coefficient law is a direct specialization of classical logarithmic-product/Newton identities.

## Worked boundaries

For N=2, w_j=[pi(j+1/2)]^2, j>=0, so

\[
\mathcal Z_2(s)=\pi^{-2s}\zeta(2s,1/2),\qquad \Re s>1/2.
\]

For N=4, D_4(z)=cos(z/sqrt(2))cosh(z/sqrt(2)). The four real/imaginary zeros with the same fourth power form one orbit, so

\[
\mathcal Z_4(s)=(\sqrt2\pi)^{-4s}\zeta(4s,1/2),\qquad \Re s>1/4.
\]

For N=3 the first values are 1/6, 1/40, 53/13440. For N=5 they are 1/120, 5/72576, 997/1743565824. The exact recurrence provides further values.

## What advanced and what remains

The previous all-zero zeta schema had branch, ordering, multiplicity and convergence decisions outstanding. The orbit version fixes these and establishes an initial holomorphic domain and coefficient dictionary. It does not establish global continuation, functional equations or historically new priority. It also does not establish convergence of residue-weighted sums involving negative powers of d_N'(w_j). Repeated zeros make that weighted definition invalid unless replaced by full principal-part data.

Existing hypergeometric zero-zeta theory is a necessary comparison: Byrnes, Jiu, Moll and Vignat, Recursion Rules for the Hypergeometric Zeta Function, arXiv:1305.1892, Definition 1.1 and Section 3 (https://arxiv.org/pdf/1305.1892). That paper studies Kummer-function zeros; this is an adjacent mechanism, not an established equality with this seed.
