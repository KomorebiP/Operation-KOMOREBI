# Exact bounded dyadic finite-difference audit

The sequence tested is

\[
C_j(n)=(4n)![t^{4n}]
\left(j!\sum_{m\ge0}\frac{t^{4m}}{(4m+j)!}\right)^{-1},
\qquad 0\le j\le3.
\]

The modular recurrence used was

\[
C_j(0)=1,\qquad
C_j(n)=-\sum_{k<n}\binom{4n}{4k}
\frac{C_j(k)}{\binom{4(n-k)+j}{j}}.
\]

All denominators are odd, so this calculation in `Z/2^4096 Z` loses no precision.
For each nonzero residue its valuation is exact. None of the stored Newton
coefficients was zero modulo the precision. Independent ordinary-series
inversion over rational `Fraction` arithmetic agreed at every index 0 through 16
in all four families.

## Domain and results

- Coefficients: every `j=0,1,2,3`, every index `0<=n<=512`.
- First differences: all `n>=0,H>=1,n+H<=512`.
- Equal-step higher differences: steps
  `1,2,3,4,5,7,8,9,13,16,31,32,63,64,127`, orders through 128 subject to
  `n+k*u<=512`, every admissible base.
- Mixed differences: 71 declared step lists, every admissible base. Their exact
  lists and resulting minima are stored in `run512/results.json`.

All checked assertions passed:

| Assertion | Checks |
|---|---:|
| Independent exact rational inversion | 68 |
| Exact first-shift valuation | 525,312 |
| Stronger higher-difference lower bound | 1,141,424 |
| Stronger mixed-difference lower bound | 139,000 |
| Newton coefficient tests | 2,048 |

The first-difference law was

\[
v_2(C_j(n+H)-C_j(n))=v_2(H)+d_j,
\qquad(d_0,d_1,d_2,d_3)=(1,1,4,2).
\]

The stronger lower bound checked was

\[
v_2(\Delta_{u_1}\cdots\Delta_{u_k} C_j(n))
\ge k+v_2(k!)+\sum_{i=1}^k v_2(u_i)+s_j,
\qquad(s_0,s_1,s_2,s_3)=(0,0,3,1).
\]

Writing `a_k=Delta_1^k C_j(0)`, the following **candidate exact formulas** held
through the declared bound:

\[
v_2(a_k)=k+v_2(k!)=2k-s_2(k),
\qquad j=0,1,\quad1\le k\le512.
\]

For `j=2`, writing `k=4m+s`,

\[
v_2(a_k)=14m+(-1,2,8,9)_s,\qquad3\le k\le512.
\]

The initial `j=2` valuations are `v(a_1)=4`, `v(a_2)=6`.
For `j=0,1,2`, each unit-step difference row had the same minimum valuation as
its Newton coefficient. For `j=3`, this equality fails: at order 28 the Newton
coefficient has valuation 101 while the tested minimum is 99. This is a failure
of that proposed exact extension, not a failure of the lower bound.

These observations do not prove any universal statement. They test the solved
congruence family and do not test the separate residual simplicity problem.

## Reproduction and provenance

The exact command, input/output hashes, software versions, effective resource
limits, and duration are stored in `run512/manifest.json`. Execution took
19.05 seconds. The bounded runner pinned the code, contract, and runner helpers.
`validate_manifest.py run512/manifest.json --root .` passed, including the hash
checks. The computation used no floating-point arithmetic and no randomness.

## A sufficient analytic lemma

The following lemma is a mathematical implication, separate from the finite
tests. Suppose

\[
F(X)=F(0)+\sum_{m\ge1}2^{m+s}b_m X^m,
\qquad b_m\in\mathbf Z_2,
\]

with `s>=0`. For `n,u_1,...,u_k in Z_2`, `k>=1`, and all nonzero steps,

\[
v_2(\Delta_{u_1}\cdots\Delta_{u_k}F(n))
\ge k+v_2(k!)+s+\sum_i v_2(u_i).
\]

To prove it, expand the mixed difference of `X^m`. Each surviving term has
multinomial exponents `n_0+...+n_k=m`, with `n_i>=1` for `i>=1`, and therefore
contains `prod_i u_i`. For the multinomial coefficient,

\[
v_2\left(\frac{m!}{n_0!\cdots n_k!}\right)
\ge v_2(k!)-(m-k),
\]

because `m>=k`, `v_2(m!)>=v_2(k!)`, and
`sum_i v_2(n_i!)<=m-k`. Multiplication by `2^{m+s}` proves the desired bound
term by term. The series converges uniformly on `Z_2`, so summation preserves
the lower bound. A zero step makes the difference zero and is harmless.

One sufficient route to such a series is a universal Newton bound

\[
v_2(a_k)\ge k+v_2(k!)+s\quad(k\ge1).
\]

Indeed,

\[
\sum_{k\ge0}a_k\binom Xk
=\sum_{m\ge0}\left(\sum_{k\ge m}\frac{a_k}{k!}\,
\mathfrak s(k,m)\right)X^m,
\]

where `s(k,m)` are signed Stirling numbers of the first kind. The inner sum
converges with valuation at least `m+s` for `m>=1`. For `j=0,1`, if the
observed equality `v(a_k)=k+v(k!)` were proved universally, the coefficient of
`X^m` divided by `2^m` would be odd. Establishing this Newton bound or the
equivalent sufficient analytic coefficient structure remains proof work.
