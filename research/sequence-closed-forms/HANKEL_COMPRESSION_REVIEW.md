# Separate self-review of the compression phase

Author: Komorebi P. Checkpoint: SEQ-DH-2026-11-20-002.
Review provenance: self-review, not independent review or Lean formalization.

Primary verdict: **proved as written** for Theorems G--J in the two adjacent
proof notes, using the explicitly stated exact computational leaves.

## Claims and dependencies

- G: every nonzero parity-definite finite operator admits the stated smaller
  matching representation. Dependencies: the published full banding theorem,
  parity, the block-determinant sign, and the generalized sliding window.
- H: every quadratic falling weight has an order-at-most-126 annihilator from
  n=2. Dependencies: the complete degree-25 block certificate and the exact
  polynomial ideal identity, followed by a seventh-power binomial argument.
- I: P(m)=1+m^2, identity operator, has exact minimal eventual order 63,
  from n=1. Dependencies: full block and product-vector identities, exact
  rational-function comparison and checked coprimality.
- J: P(m)=1+m, operator1+2 partial_x, has exact minimal eventual order112,
  from n=1. Dependencies: all12870 integer state coordinates, early scalar
  identities, exact OGF comparison and checked coprimality.

## Obligation matrix

| Obligation | Outcome | Evidence |
|---|---|---|
| Actual functional and conventions | passed | Explicit monomial moments; falling coefficients retained |
| Even parity sizes and signs | passed | ceil/floor blocks; row and column permutation signs cancel |
| Odd parity signs | passed | Column-block swap gives (-1)^m, odd full size is singular |
| Chebyshev factor4 | passed | Applies at positive full size only; W0 separate |
| Whole boundary, not only interior | passed | Uses the already proved full stencil; block rows start at4M+1 |
| Odd asymmetric window | passed | lower2M, upper2M-1; finite checks include M3 |
| Common even stationary transfer | passed | Both tails equal t_(2(i-j)) |
| Symmetric-square order bound | passed | Separate initial vectors for even and odd subsequences |
| Uniform block certificate completeness | passed | Degree25 homogeneous residues; triangular351-point interpolation proof |
| Degree drops and zero weight | passed | Fixed M2 model and polynomial identity; off-grid checks include both |
| Early block residues | passed | All5616 exact identities at indices1 through8 |
| Uniform tensor polynomial | passed | Full ideal membership over Z[A,p,q,x,y]; seventh-power argument |
| Quadratic infinite OGF | passed | Discovery136-coordinate and separate256-coordinate product identities |
| Mixed characteristic-zero result | passed | Exact integer residual after CRT, not modular success alone |
| Mixed representation independence | passed | Second implementation uses bitmasks and direct monomial Gram entries |
| Scalar minimality | passed | Degree-preserving modular Bezout identities for the already established rational OGFs |
| Recurrence starting indices | passed | Numerator degrees and early residues; mixed residue n0 fails |
| Historical novelty | out of scope | No novelty audit of these refinements |
| General sharp quadratic bound63 | not addressed | Only sample63 and uniform bound126 proved |
| General mixed-parameter minimality | not addressed | Only the specified mixed example112 proved |

## Adversarial checks and corrections

The first interpolation-discovery grid met a degenerate quadratic and failed
the assumed exact order16. That run is preserved as failed. The proposed
quartic was then recovered on a different generic grid. The universal
certificate includes the degenerate parameters and asserts an annihilator,
not minimal order16 at every parameter.

The tensor audit does not reuse the symmetric-product coefficient formula.
It reconstructs ordinary tensor coordinates and monomial initial determinants.
The mixed audit imports neither the discovery transfer nor its numerical
packages. It reconstructs matching signs from bit operations and verifies
the zero second minor against an integer Bareiss determinant.

The proof of the uniform tensor identity uses polynomial ideal membership,
so no separability assumption or root-specialization argument is needed.
The symbol factorization alone was not used to infer a boundary identity.

All fixed-width transfers retain singular cases. Corrupted recurrence
coefficients and malformed block certificates are rejected in the audits.

## Proofreading self-review

Scope: the two new proof notes and this review. Routine prose and TeX
integration were checked; the mathematical development is recorded as new
research, not a typographical correction of the earlier published proofs.
The earlier source notes and all their formulas remain unchanged.
Unresolved mathematical scope is stated in the matrix above.

The final uniform verifier explicitly fixes the four-difference stencil at every
specialization. The first version used an actual-degree helper for its extra
c=0 regression cases; its complete c=1 interpolation grid was unaffected.
The second version removes that off-grid implementation mismatch and reruns
the full certificate. The current uniform evidence is sequence-uniform-quadratic-002.
