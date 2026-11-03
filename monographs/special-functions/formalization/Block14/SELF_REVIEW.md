# Focused self-review of the main H.1 operator contract

Primary verdict: **proved as written within the registered main H.1 scope**.
Provenance: self-review, not independent review. Source bytes and exact names
are bound by declarations.json and the accepted replay, based on
297118ccc10550500619224d44f168f6491d02e5.

Claim card: all positive real scales, all complex nonzero rows, and all
zero-constant analytic vector inputs. Existence of an arbitrary scalar
functional of the row projection is equivalent to ordered scale-row equality
and a nonzero multiple of (1,-1). The projected field is zero and no constant
invertible complex 2x2 coordinate change has two autonomous rows. Both entire
functions and local analytic germs are registered; contractions and distinct
scale nodes are not assumed.

Dependencies: actual projected field/fiber definitions -> arbitrary-functional
factorization -> explicit entire polynomial values -> three fiber comparisons
-> row sum zero -> linear/quadratic input comparisons -> ordered scale recovery
-> arbitrary-input zero-field converse -> row classification -> determinant
zero -> IsUnit contradiction. Local analytic scaling + entire identity
principle -> local-to-entire implication -> local classification. Earlier
modules have no dependency on this one. Pinned Mathlib leaves are general
factorization, complex analyticity, neighborhood germs and matrix algebra.

| Obligation | Result | Evidence |
| --- | --- | --- |
| Exact operator and forcing | passed | Both field entries retain 1; the common projected constant cancels in fiber comparisons. |
| Arbitrary scalar functional | passed | Function.factorsThrough_iff, with function/germ codomain Nonempty; no ansatz imposed on H. |
| Entire admissible inputs | passed | Every test is entire and zero at zero; scaledInput carries both proofs. |
| Repeated scale nodes | passed | Explicit product polynomial evaluates to one when any factor vanishes; no distinctness assumption. |
| Zero and single-coordinate rows | passed | Zero-row disjunct retained; first-coordinate cancellation requires and proves nonzero from the row guard and sum. |
| Positivity and no contraction | passed | All four scales positive; no scale<1 premise. Positive example (2,3,2,3) is checked. |
| Ordered versus swapped rows | passed | Recovery yields q=a and r=b. A swapped unequal fixture has canonical coincidence but no nonzero autonomy. |
| Fiber identities | passed | Three exact algebraic comparisons force both products with c1+c2 to vanish. |
| Scale recovery | passed | qr=ab and q^2*r=a^2*b suffice; qr>0 allows cancellation. |
| Local input domain and representatives | passed | AnalyticAt at zero, actual Germ quotient, field analytic and representative invariance under eventual equality. |
| Local-to-global bridge | passed | Used only for entire test functions; entire field differentiability and connected complex-plane identity theorem are explicit. |
| Sufficiency on local and entire inputs | passed | Pointwise field cancellation holds for arbitrary functions; yields equality in either domain. |
| Invertibility convention | passed | Actual matrix IsUnit implies nonzero determinant; both autonomous rows force determinant zero. |
| Other transformations | out of scope | Nonlinear coordinates and scalar elimination along a distinguished solution are not excluded. |
| Odd-only and tensor explanatory variants | not addressed | Retained separately in remaining-work inventory. |

All 57 source-bound replay steps pass: fourteen module compilations/audits/
kernel replays and five control files, with the four expected rejections.
The new module's 27 names are all audited. Allowed axioms are only propext,
Classical.choice and Quot.sound; cached imports are not freshly rebuilt.
There is no missing implication in the registered main H.1 target. The
remaining-work inventory records broader manuscript correspondence limits.
