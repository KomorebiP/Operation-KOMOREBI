# Quartic and coefficient atlas: focused self-review

EULER-CASE-006 · 29 October 2026 · same-assistant review. Primary verdict:
**proved as written**. The explicitly checked Paper IX all-row theorem is an
external input. This is not independent review or new Lean verification.
Preceding claims retain their separate reviews.

| ID | Claim and adversarial obligation | Result |
|---|---|---|
| C44 | Quartic normalization and odd-denominator rational coefficients | **Passed.** N=4, j=0..3 are fixed. The cleared diagonal formulas are checked separately for all four addresses; they are odd units, including the factor three at j=3. Source constant j! is retained in U, while C_0 uses the signed quartic carrier, not classical signed Euler. |
| C45 | All-row source input, prefix and universal Newton envelope | **Passed with checked source input.** The cited all-row theorem gives valuations >=k at base step one. Exact prefix values cover every exception to c+1+floor(log2 k)<=k: j=0,1 through k=2; j=2 through k=6; j=3 through k=4. Finite translation preserves the envelope and the first difference has exact valuation c. No finite sample is presented as a proof of the source bound. |
| C46 | Exact displacement, nonvanishing and least periods | **Passed.** Positive T expansion is finite; the binomial denominator identity bounds each k>=2 term at least one power above the leading term. It cannot cancel the leading contribution. U gains add v_2(j!). Period iff divisibility follows at every row. r=0 gives period one. The 1024 table is a consequence of the universal law, outside the stated finite period-test range. Compressed n and full degree are distinguished. |
| C47 | Isometry, inverse limit, binary lift and full row witness | **Passed.** The difference law applies to the smaller of two natural arguments. Modulo 2^s it yields a well-defined injection on a finite set of equal size, hence a permutation. Two children differ at exactly the next bit. Compatible residues give the unique Z_2 inverse and preserve the distance formula. All six target rows, diagonal inverse 887, 21 summands, sum 22537=9 modulo 2048, C_2(21)=209 and U_2(21)=418 were recalculated. Rational integrality and division by 32 use adequate prior precision. |
| C48 | Finite Hurwitz modes, Frobenius nilpotence and inverse | **Passed.** The sequence product uses integral binomial coefficients, not factorial division. The additive-mode law is the finite binomial theorem. Vandermonde injectivity and commutativity justify the finite algebra. Total weight one gives x^p=delta and (x-delta)^p=0; the finite geometric sum is a two-sided inverse. Half-cosh requires odd prime; p=2 is not included. |
| C49 | Euler mode weights modulo five and degree-zero obstruction | **Passed.** The cosh source weights sum to one. All five cyclic-convolution entries give the identity, and uniqueness of Hurwitz inverse follows from constant one. Full-index E_n is used. The 0^n term is delta with 0^0=1; dropping it changes E_0. Fourth-power periodicity is asserted only on the positive tail, and no extension to modulo 25 is implied. |
| C50 | Signed Stirling substitution and inverse matrix | **Passed.** Formal chain differentiation yields the signed first-kind recurrence; exponential substitution yields the second-kind recurrence. Both origin-fixing substitutions have linear coefficient one and are mutual inverses. All rows are finite. Matrix orientation is output degree n, input degree k, distinct from the transposed polynomial connection convention in the library. The factorial interpretation is over Q. |
| C51 | Rational transformed Euler series, numerator recurrence and E_8 recovery | **Passed.** exp(log(1+T))=1+T in the formal ring gives the rational identity with constant one. Clearing its quadratic denominator and factorials gives b_n=-n b_(n-1)-binom(n,2)b_(n-2). Initial b_1 is zero because the numerator is 1+T. Every displayed coefficient and the S(8,k) recovery sum gives 1385 exactly. |
| C52 | Transported derivative D+N | **Passed.** Row n uses b_(n+1)+n b_n, with the positive diagonal sign. Matrix products remain finite-row. The row-three direct Stirling check yields 3. Computation of output row 16 retains input degree 17, avoiding an invalid square cutoff. All statements here are formal; adjacent source convergence conditions are not silently assumed. |

Dependencies: checked all-row source theorem + C44 finite recurrence -> C45 ->
C46 -> C47. C48 -> C49. The formal substitution recurrences -> C50 -> C51 and
C52. The finite-field branch and rational factorial branch have distinct
coefficient domains.

Primary run-006 and cross-check-006 completed within their predeclared
contracts. New finite checks cover exact quartic indices 0..47, every declared
difference/displacement, modular coefficients 0..255 modulo 8192, all residue
permutations through eight bits, every unordered pair among inputs 0..31,
period tests through eight bits, all six inverse lifts, modes at p=3,5,7 through
full degree 24, and Stirling/logarithmic data through degree 16 with derivative
input through 17. These finite assertions support implementation agreement.

Cross-check-006 adds 1164 pinned API comparisons: 96 quartic coefficients,
150 modular Hurwitz values, 578 Stirling entries, 51 formal-coordinate values,
and 289 substitution entries. Earlier comparisons remain. The library source
pin is checked before import, and every imported project file is hashed before
and after. Dependency versions are recorded, not bit-for-bit rebuilt.

Mathematical proofreading checked source/target orientation, all index and
precision cutoffs, signed/positive/full/compressed conventions, odd-denominator
reduction, tail-period exceptions, inverse-limit compatibility, formal versus
convergent series, and all new displayed arithmetic. No unresolved obligation
remains in the selected scope. Universal all-row source verification and
same-assistant downstream review remain visibly distinct from bounded runs.
