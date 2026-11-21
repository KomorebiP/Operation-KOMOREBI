# Self-review of the uniform mixed-family extension

Claim: Theorem L and its mixed-linear and generic-minimality corollaries in
UNIFORM_MIXED_RECURRENCE.md. Checkpoint SEQ-DH-2026-11-21-003.
Primary verdict: **proved as written**. This is a separate project self-review
pass, not independent review or Lean formalization.

The theorem quantifies over every characteristic-zero field and every
quartic coefficient list. The application includes all a,b,u,v in P=a+bm,
D=u+v*partial_x. It gives a polynomially defined constant-coefficient
annihilator chi_R(S)^7 from index one, uniform order at most 112. The generic
minimal order is 112 on a specified nonempty Zariski-open set; pointwise
minimality on its exceptional complement is not classified.

## Dependencies and adversarial obligations

| Obligation | Outcome | Evidence |
|---|---|---|
| Actual functional | passed | Explicit even/odd monomial moments; formal integration by parts gives R, including the 6b derivative coefficient |
| General quartic domain | passed | Arbitrary coefficient list, not merely an even or positive surrogate |
| Orthogonality and determinant identity | passed | Theorem K's formal proof does not require even R; size-five singular-boundary handling retained |
| Sixteen bases | passed | Two independent branch choices in each of four rows |
| Degree bound | passed | Degree-eight coefficient determinant; columns coincide at both n0 and n1 before division |
| Polynomial quotient | passed | Roots 0 and1 are distinct; division leaves degree <=6 branch by branch |
| Branch signs and normalization | passed | Generic four-root determinant uses the same H_N and four d_n factors; no parity factor is inserted |
| Trace identity | passed | Power sums factor as product C_k(t_i), equal 2^k Res(R,C_k) |
| Newton recursion | passed | Formal logarithmic derivative derives the stated sign and 1/j factors |
| Leading coefficient zero | passed | Fixed degree-four Sylvester determinant; coefficients polynomial in r0..r4 before specialization |
| Initial indices 2,3,4 | passed | Full coefficient identities in Q[r0,r1,r2,r3], separate SymPy and sparse-polynomial implementations |
| Index-one limit | passed | J=-2x^3+8x; coefficient determinant 2304 gives mu0=r4 |
| No hidden logarithmic terms | passed | F3-F1 vanishes individually on each branch before differentiation |
| Index-zero exception | passed | The exponential continuation is 1/2; residue is (2r4)^112/2 when actual W0=1 |
| Every specialization | passed | Each fixed recurrence residue is a polynomial identity over Q in the quartic coefficients |
| Sample factor | passed | All 17 coefficients match the retained degree-16 factor |
| Sample infinite generating function | passed | New universal theorem plus initial coefficient convolution, corroborating the retained full-state proof |
| Coprimality and degree | passed | Reconstructed 113 numerator coefficients and retained denominator match; prime 1000003 and full Bezout identity checked |
| Uniform optimality | passed | The same mixed-family sample has minimal eventual constant-coefficient order 112 |
| Generic minimality | passed | Fixed-degree resultant is polynomial and nonzero at that sample; reduced denominator degree 112 on a nonempty open set |
| Exceptional pointwise classification | not addressed | Separate research target, not asserted by a uniform bound |
| Higher-degree and higher-order operators | not addressed | The stated mixed application has linear weight and first-order operator |
| Historical novelty | out of scope | No novelty audit |

## Exact evidence and scope

- sequence-uniform-mixed-symbolic-001: completed. Complete symbolic quartic
  boundary identities and the sample resultant/Newton factor.
- sequence-uniform-mixed-replay-001: completed, preserved as the initial
  standard-library replay. No generic-minimality certificate was claimed by
  that run.
- sequence-uniform-mixed-replay-002: completed. Adds reconstruction of the
  sample numerator and verification of the retained degree-preserving modular
  Bezout witness. The v1 code is preserved; the v2 code has a distinct path.

The current replay checks 330 functional moments, 170 direct monomial
determinants and 200 recurrence residues in ten parameter cases. Numeric
agreement alone is not universal evidence: coverage is supplied by the
formal determinant argument, exact polynomial identities and specialization.
The sample numerator comes from actual determinant values, and its match to
the retained full-state certificate gives a cross-check between the new
formula and the old infinite-sequence calculation.

Proofreading scope: the new proof and this review. Definitions, TeX delimiters,
equation references, leading-coefficient conventions and generic-versus-
pointwise scope were checked. No mathematical-token typo corrections were
made. The candidate-to-proved status change follows the audit, not copyediting.

The proposed extension target is reached. A complete classification of orders
on the exceptional locus, and general higher-degree/higher-order mixed
families, remain open. Publication continues through the same authorized
reader PR, now covering both Theorems K and L.
