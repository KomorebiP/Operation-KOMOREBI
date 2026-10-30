# Source-based extension: focused proof self-review

EULER-CASE-005 · 29 October 2026 · same-assistant review, not independent review.
Verdict: **proved as written** for claims C36–C43 below. Earlier claims retain
their preceding reviews. Source authentication and exact extraction are in
LITERATURE_FIBONACCI.md/.json; execution is separate finite evidence.

| ID | Claim and adversarial obligation | Result |
|---|---|---|
| C36 | Lucas trace, determinant parity, sampled recurrence and selector composition | **Passed.** C^2=C+I gives trace recurrence and independent Lucas initial values. The general two-by-two characteristic identity is verified entrywise, so the specialized argument requires no unverified external Cayley–Hamilton input. Odd/even signs, N=0 and two-value uniqueness are checked. The composed Euler encoding targets the shifted index F_(Nk+j+1). Sampling has no unsupported inverse. |
| C37 | Integral matrix refinement, difference divisibility | **Passed.** Base C^12=I+8 B_0 is exact. Squaring gives B_(a+1)=B_a+2^(a+2)B_a^2. Every coefficient is integral. Matrix differences insert the commuting factor C^H-I, so r repetitions contribute 2^((a+3)r). Positive L and integral observations are explicit. The general prime-power binomial observation requires L>=1; the p-th binomial term has pL>=L+1 and intermediate terms have the extra factor p. |
| C38 | Exact sharpness at n=1 | **Passed.** B_0 modulo two is I, the refinement correction is even, and all B_a^r reduce to I. The observed C^1 state has second coordinate F_1=1. Thus the remaining factor is odd for all a,r>=0, including r=0. This proves the universal sharpness statement rather than extrapolating from samples. |
| C39 | Finite binomial reconstruction and truncation ladder | **Passed.** Expand the integer exponent x of I+2^(a+3)B_a. The sum ends at x, and binomial coefficients are integral. At depth L every omitted term has the claimed factor. L>x is exact. No infinite sum, rational-index interpolation or analytic convergence is asserted. F_37's partials, errors, residues and valuations were recalculated. |
| C40 | Simultaneous 144^r divisibility | **Passed.** C^24-I is exactly 144[[521,322],[322,199]]. Factoring the r-th matrix difference proves the bound for every n,r>=0. The powers of two and three are coprime factors of the same modulus; no invalid direct conversion of residues is used. The 144 factor is labeled a consequence of the source's factor-24 display. |
| C41 | Rectangular derivative conjugacy | **Passed.** C_4^(-1) converts input Fibonacci to Euler degree four, D_E maps dimension five to four, and C_3 converts the output. Direct derivatives of every B_k give the same D_F. Using the Euler matrix on Fibonacci input demonstrably misses a constant. The polynomial finite-support domain is retained. |
| C42 | Typed primitive/change/derivative round trip and reverse boundary | **Passed.** J_F is 5x4 and based at zero. C_4 inverse is 5x5, D_E is 4x5, C_3 is 4x4. Their composite is I_4 by the fundamental theorem for polynomials or exact multiplication. The reverse composite is I_5 minus the outer product of the constant polynomial's column and actual evaluation at zero. The B_2 and constant controls distinguish evaluation from coefficient extraction. |
| C43 | Integral covector transport and value 5/4 | **Passed.** Each covector entry is computed by exact monomial integration on [0,1]. The identity ell_F C_3=ell_E follows by integration of each basis expansion. Both pairings give 5/4 and agree with the direct polynomial integral. This is a scalar observation of the same polynomial, not a change of measure. |

Dependency order: C36 follows the companion identities; C37 -> C38 and C39;
C40 uses the same finite-difference mechanism with its own exact jump. C41 and
C42 use the already proved connection basis and Euler Appell law; C43 uses
their coefficient interpretation. The specialized integral proofs are written
in full even when the source provides a more general statement.

## Finite evidence

Primary run-005 completed under contract-005. Controls cover steps 0..12,
addresses 0..5, packet indices 0..8, dyadic refinements 0..4, scalar difference
bases 0..6 and orders 0..5, binomial reconstructions at addresses 0..3 and coarse
indices 0..6 with every depth, and calculus source degrees 0..8. They include
the wrong parity sign, wrong single-step jump and wrong derivative matrix.

Cross-check-005 reproduces the semantic result and exact displayed CLI, retains
605 reciprocal, 1012 local-chart and 921 earlier Fibonacci comparisons, and adds
3506 pinned API comparisons: 780 packet values, 1560 state coordinates, 68 jump
entries and 1098 calculus matrix entries. Project imports are checked against
the pin and hashed before and after use. Neither bounded run proves the
universal identities or executes Lean. Both accepted run manifests validate.

## Mathematical proofreading

Checked all state orders, address shifts, Lucas parity, empty/zero boundaries,
positive-L and integrality hypotheses, finite binomial range, exact-valuation
claims, all displayed integers, rectangular matrix sizes, inverse direction,
Appell normalization, basepoint primitive, evaluation row and covector variance.
No unresolved obligation remains for C36–C43. Independent review and a global
literature comparison remain separate possible work, not claimed achievements.
