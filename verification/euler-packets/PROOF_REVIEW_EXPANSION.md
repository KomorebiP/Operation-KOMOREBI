# Proof self-review and proofreading: expanded Euler example

**EULER-CASE-002 · 29 October 2026 · same-assistant review**

## Claim card and verdict

The added statements concern rational formal power series, integer sequences
on nonnegative indices, positive integral block lengths, positive odd source
lengths, and prime valuations with the zero-error convention made explicit.
The dyadic congruences are in the ring of rationals with odd denominator.
No p-adic limit, analytic convergence or automated discovery is asserted.

**Primary verdict: proved as written.** This is a focused self-review of the
added claims C11-C18 below. The unchanged C1-C10 calculations were re-read in
context and their exact finite controls rerun. This is not independent review
or a verification of the complete Python implementation.

The expansion starts at collection revision
`9987ef468dcbfa49a256ea6da2b249d577da0a88`. The publication record binds the
reviewed final manuscript and code by content hash. The source-dependent
Bernoulli implication is checked in `LITERATURE_EXTENSION.md`.

## Dependency graph

1. The original quartic bridge is triangular with nonzero diagonal 4^m.
   Solving it recovers the carrier and predicts its second Euler packet.
2. Inclusion-exclusion over forbidden descents at block boundaries gives an
   ordered-composition formula. Formal geometric inversion gives the identical
   formula for the reciprocal coefficients.
3. The proved Euler-polynomial translation law telescopes to a finite power
   sum, including the empty sum and degree-zero boundary.
4. A finite geometric sum, followed by its even part, gives the odd source
   series. Multiplication by sech(pt)^2 gives the finite reconstruction.
   Integer kernel coefficients give the truncation divisibility directly.
5. The explicit dyadic source and hyperbolic factorization give its forward
   and inverse kernels. Rational unit inversion constructs their coefficients.
6. The Bernoulli generating function and a differentiated regular series give
   the exact kernel formula. The checked external denominator theorem supplies
   v_2(B_(2r))=-1 for r>=1. An internal elementary factorization proves every
   dyadic source coefficient is a unit.
7. These exact valuations give each summand weight, the uniform finite-tail
   bound and its one-term sharpness witness. Distinct minimum weights give
   the exact errors of the displayed E_8 row.
8. Finite binomial expansions give the higher-prime corrections. Direct
   one-sided sampling gives the bounded signal obstruction and two-phase repair.

The only added external theorem leaf is the Bernoulli denominator theorem.
All displayed finite sums and matrix/series operations have internal derivations.
No finite calculation is used to establish an infinite family by extrapolation.

## Obligation matrix

| ID | Quantified statement and hypotheses | Review result |
|---|---|---|
| C11 | Reverse quartic bridge for every m>=0, over Q | **Passed.** Isolating the diagonal 4^m gives the stated recursion. The m=0 sum is empty. The fixed numerator and reciprocal constraint are retained when predicting the odd packet. |
| C12 | Permutation count for N>=1, n>0, descents inside blocks and ascents at boundaries | **Passed.** Every subset of forbidden boundary descents merges to one ordered composition. Its sign is (-1)^(n-k), and the multinomial counts the distinct labels without internal ordering multiplicities. The four-block double intersections split into two adjacent cases and one disjoint case. The formal inverse has exactly the same signs and factorials. |
| C13 | Alternating power telescope for m,L>=0 and rational/formal x | **Passed.** Interior terms cancel with opposite signs. Both boundary signs are retained. At L=0 the expression is zero, and at m=0 the odd-window specialization uses 2^(-1) correctly. |
| C14 | Odd-source reconstruction for every positive odd p, every n>=0; finite depth L>=0 | **Passed.** The geometric numerator is 1+exp(2pt) precisely for odd p. Even projection gives cosh(pt)^2 sech(t). Forward and inverse kernels have constant one. Integer Euler coefficients give integer gamma_r. Each omitted term has p^(2r), proving the integer truncation bound even when p is composite. Prime interpretation is separate. |
| C15 | Dyadic reconstruction for n>=0, coefficient ring Q | **Passed.** Both apparent divisions by t^2 have removable zeros. The source and inverse kernel constants are one. J R^(-1)=cosh(t) is equivalent to K R=sech(t). The EGF weights use binomial(2n,2r), and the recurrence for kappa has the correct sign and base case. |
| C16 | v_2(kappa_r)=4r-1 for r>=1; v_2(R_(2n))=0 for n>=0 | **Passed.** Q-zQ' gives the Bernoulli factor with 2^(4r), not 2^(2r). The external theorem is applied only to positive even Bernoulli indices. The source factorization uses n+1=2^d u, u odd, with the empty product at d=0. Its numerator and denominator have equal valuation. |
| C17 | Dyadic tail bound for all n,L>=0, uniform sharpness at n=L+1 | **Passed.** Every omitted r has weight at least 4L+3. There are finitely many terms, and an empty tail is zero. At the first omitted row the binomial and R_0 are one, so the error is exactly kappa_(L+1). For E_8 the nonconstant term weights 5,8,13,15 are distinct, preventing cancellation of the least-weight term in each tail. |
| C18 | Higher-prime residual examples and sampled bounded signals on n>=0 | **Passed.** The corrections at 3 and 5 are 18 and 7590. Their valuations are respectively 2 and 1. The alternating and constant signals agree on the retained even phase but their shifted even phases differ. The two-phase shift sends (b_0,b_1) to (b_1,S_q b_0), and its square advances both lanes once. No inverse shift or Euler DTFT is invoked. |

## Decisive arithmetic and negative controls

- Independently recomputed the two five-term E_8 sums and all ten partial
  sums, errors and valuations, including rational denominators.
- The dyadic first error is 54944/45=2^5*1717/45. The next is
  153344/45=2^8*599/45. The third is -335872/45=-2^13*41/45.
- Verified modular inversion: 45 modulo 32 is 13, whose inverse is 5;
  7381/45 and 1385 both have residue 9.
- Checked that 5/24 cannot be reduced modulo 8, and that the naive even-length
  alternating source has constant zero. These are distinct domain failures.
- Recomputed the reverse carrier through b_3, the s_7 prediction and quartic
  inclusion-exclusion through sixteen letters.
- Rechecked c_5=-58112 and both larger prime corrections against direct Euler
  differences. Additional divisibility in the p=3 input is not attributed to
  the polynomial's coefficients alone.

## Computation and implementation review

The standalone program uses exact integers and Fractions. It compares finite
power sums to independently multiplied formal series, the dyadic reciprocal
to a separate Bernoulli inversion, inclusion-exclusion to rank DP and small
explicit permutations, and direct samples to difference-coordinate kernels.

The fresh primary run is `run-002/manifest.json`. The separate cross-check
reproduces its semantic results, matches the literal page output and compares
605 reciprocal coefficients plus 1,012 local-chart outputs with source-pinned
Komorebi Math. The latter counts are 220 source/kernel/reconstruction values,
528 partial values and errors, and 264 row weights. The full finite ranges are
in the contracts and results. Installed NumPy is version-recorded rather than
rebuilt. Neither these observations nor the library certificate flags replace
the written proofs of C11-C18.

## Proofreading report

- Coverage: the complete maintained worked page, including its original
  derivations, added sections, tables, printed output and source links.
- Routine edits: clarified the temporary scalar extension, defined valuations
  before first use, updated the coordinate overview and reading/evidence routes,
  and kept the distinction between ordinary degree and compressed index.
- Mathematical-token corrections to pre-existing derivations: none.
- Added mathematics: C11-C18 above, explicitly scoped and reviewed rather
  than treated as proofreading changes.
- Unresolved issues: none found within these claims. General Euler-branch
  root classification, performance comparisons and Lean execution remain
  outside this example.
- Validation: the exact primary run and library comparison passed. Final
  publication validation also checks rendered mathematics, links and the
  source-bound downloadable archive.
