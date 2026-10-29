# Proof self-review: Euler packets and residuals

**29 October 2026 · Codex self-review · EULER-CASE-001**

This record concerns C1-C10 in the first published edition, collection revision
`9987ef468dcbfa49a256ea6da2b249d577da0a88`. Its remaining-scope discussion
describes that edition. The added local reconstruction and precision theorems
are reviewed separately in `PROOF_REVIEW_EXPANSION.md`.

## Normalized claim and verdict

For the formal units and coefficient systems defined in the worked page, the
reciprocal recurrences, packet reconstruction and obstruction, Schur elimination,
quartic coefficient bridge, parameter-polynomial identities, Euler-polynomial
reconstruction, residual correction, and integer-sequence transfer laws hold
under their stated hypotheses.

**Primary verdict: proved as written.** This is a self-review of those explicit
elementary algebraic statements. It is not independent review, a proof of every
line of the Python implementation, a new formalization, an empirical discovery
claim, or a novelty certification.

Authoritative statement/proofs: `docs/demonstrations/EULER_PACKETS.md`.
The final publication record binds its exact hash. Base checkpoint:
`3a9b5f89883fbf24247410a56519045e809fbd1a`.

## Dependency graph

1. Rational formal series, the Cauchy product and coefficient comparison imply
   existence/uniqueness of reciprocals of units and the scalar recurrence.
2. Splitting even degrees modulo four gives the rank-two Q[[u]] representation.
   Its product law supplies the carry, multiplication matrix and coarsening witness.
3. Unit constants of C and G allow inverse and Schur calculations. The second
   equation is retained as the reconstruction constraint in elimination.
4. The formal cosine/cosh factorization gives G. Substitution in the quartic
   reciprocal and coefficient comparison give the binomial reconstruction bridge.
5. The formal binomial series defines D_N^(-r) in Q[r][[t]]. Differentiation and
   the same coefficient uniqueness give the polynomial recurrence and addition law.
6. The defined Euler-polynomial generating function, expanded at the midpoint,
   gives reconstruction, shift, derivative and reflection identities.
7. Associativity and commutativity in Q[[t]] give residual squaring. Unit
   multiplication preserves order. This supplies the formal jet certificate.
8. S=I+Delta on one-sided integer sequences gives the finite Newton expansion.
   The sampling intertwiner supplies kernel support and refinement composition.
9. Prime divisibility of intermediate binomial coefficients supplies the integer
   correction polynomial. Its application is separate from reducing rational
   Taylor coefficients modulo a prime.
10. Exponential modes give the FIR response. Inverse-shift formulas are confined
    to two-sided signals.

The OEIS and DLMF references authenticate the classical names, definitions and
finite prefixes. They are not substitutes for the written proofs above. The
finite permutation interpretation is an independent bounded control, not a
load-bearing unproved leaf in those algebraic identities.

## Obligation matrix

| ID | Statement and hypotheses | Verdict and decisive check |
|---|---|---|
| C1 | D_N has constant one, N>=1, n>=0, coefficients over Q | **Passed.** Unit recursion and multiplication give the stated signs, factorials and base value. Compressed n always corresponds to ordinary degree Nn. N=1, r=0 and r=-1 boundaries agree. |
| C2 | Q[[t^2]]=Q[[u]] + t^2 Q[[u]], u=t^4 | **Passed.** Uniqueness is coefficient partition. The return from the second packet contributes uDB. The vector (0,1) has zero first coordinate but first output uD!=0. Thus no map of the first coordinate alone handles all input pairs. |
| C3 | Reciprocal system with second equation DA+CB=0 | **Passed.** C(0)=G(0)=1. Direct multiplication checks both inverse equations. Elimination gives C_eff=C-uDC^(-1)D=G/C, followed by reconstruction of B. It is not asserted as an unconstrained closure on all pairs. |
| C4 | Quartic determinant and bridge, all n>=0 | **Passed.** In Q(i)[[t]], the (1+i)/(1-i) powers cancel degrees 4j+2 and give (-4)^j at degree 4j. Results descend to Q. Substitution in the reduced variable introduces exactly 4^k. The floor in the bridge enforces 4k<=2n. |
| C5 | Reciprocal-power parameter r, N>=1 | **Passed.** Each coefficient receives finitely many composition terms. Signs are (-1)^(n+k), and the leading coefficient is (Nn)!/(n!(N!)^n). The differential recurrence includes the k=n term using the out-of-range binomial convention. The product at r+rho is justified by the same equation and constant term. |
| C6 | Classical Euler polynomials over Q[x] | **Passed.** The midpoint factor is sech(t/2). Signed E_(2k), powers 2^(2k), and the ordinary degree m are retained. Translation, differentiation and reflection follow by coefficient comparison of the defined generating function. |
| C7 | Residual R=1-DB for a formal unit D | **Passed.** Expansion gives R_new=R^2. The identity D^(-1)-B=D^(-1)R proves the order certificate. In Q[t]/(t^32), zero means order at least 32, not identically zero in the full series. No real-variable error or cost estimate is inferred. |
| C8 | Integer sequences on n>=0, M>=1, s>=0, k>=0 | **Passed.** The shift intertwiner follows pointwise. Newton sums are finite at each index. Kernel support is k..Mk+s, with k=0 included. Composition order and offset are ML and s+Mr, checked directly from sampling. |
| C9 | Prime p and integer difference coordinates | **Passed.** For 0<j<p, binomial(p,j)/p is integral. The correction is retained above coarse precision. Composite four is a valid countercontrol. Ordinary rational Taylor coefficients with nonunit denominators are not reduced modulo p. |
| C10 | FIR response on complex exponential modes | **Passed.** Each shift contributes exp(i omega). The causal equality uses two-sided signals, where inverse shifts exist. No convergent DTFT for the Euler sequence is claimed. |

## Adversarial cases and arithmetic

- Recomputed the direct secant recurrence through s_6 and quartic recurrence
  through b_4. The alternative bridge sum for s_6 is
  `1+1980+546480+2154304=2702765`.
- Dropping the second packet gives the degree-four numerator -1 instead of 5.
  The full-equation residual has second constant -1/2. Omitting the carry is
  detected independently by a wrong determinant constant.
- Recomputed the effective operator coefficients `1,-5/24,73/8064` and its
  inverse `1,5/24,277/8064`.
- Checked the first missing inverse coefficient `1385/40320=277/8064` from
  the explicit degree-eight product, including its sign.
- Recomputed the Euler difference triangle and both refinement paths. The
  prime-two correction is `8+2*(-2)=4`, and the false value is detected modulo 8.
- Checked the distinction among s_n, E_(2n), full-index E_m, reciprocal-power
  P_N,n(r), and Euler-polynomial E_m(x).
- During review, restricted the causal inverse-shift formula to two-sided
  signals, and made the retained constraint in Schur elimination explicit.

## Computation audit

The primary v2 run manifest records a completed bounded execution with actual
input hashes before/after and hashed JSON/CSV outputs. The script is standard
library Python with exact integers and Fractions, fixed loops, and no random
sampling. Two scalar-series algorithms, rank DP, explicit small permutations,
the matrix carrier, and direct sampled differences provide different controls.

The secondary check reproduces the semantic results, matches the page's literal
CLI output, checks all displayed Schur coefficients, and compares 605 exact
coefficient values with the pinned mathematical-library source. Its record
observes the imported source hashes before and after. Neither check establishes
universal correctness of Python or substitutes for C1-C10's written arguments.

## Remaining boundaries

No unresolved algebraic gap was found in C1-C10 under these conventions. The
example does not claim a performance advantage, an automated discovery, an
exclusive representation language, a universal Euler divisibility theorem, or
an analytic truncation error bound. Establishing any of those would be a
different target. The review is by the same assistant that developed the page.
