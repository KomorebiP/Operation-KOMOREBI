# Adversarial proof audit and proofreading

Scope: all seven new Lean sources; README.md, PROOF.md, RESEARCH_BOUNDARY.md, and the continuation instructions. This is a self-audit, not an independent referee review.

| Risk examined | Evidence / conclusion |
|---|---|
| Accidentally using a scalar derivative | `tangent_eq_sum` preserves A^i X A^(d-1-i); both ordered remainder identities are kernel-checked |
| Ignoring dimension factors in a matrix norm | Submultiplicativity uses the ultrametric finite-sum bound and entrywise sup norm; no real/complex matrix norm is substituted |
| Unproved contraction or complete ball | `remainder_lipschitz`, `precision_contracts`, and the actual complete matrix instance supply these hypotheses |
| Necessity omitted in a sufficient Hensel argument | Both directions of `power_ball_image` and the integral/finite iff theorems are proved |
| Incorrect inverse or merely a residual inverse | Certificate asserts both compositions on a full matrix basis over Q_p; both extend by linearity |
| Wrong precision exponent | Q=p^(-s)B turns radius p^(-m) into B-error divisibility by p^(m+s); strict m>s is retained |
| Root left in Q_p rather than Z_p | Root entries are explicitly constructed in `PadicInt` from their norm bounds |
| Root not proved invertible | Positive-degree unit-target theorem invokes the general monoid unit-of-power fact and constructs a Units witness |
| Hidden all-depth premise | No level-by-level existence premise occurs in the new main theorem |
| Certificate discovery overstated | Exact certificate remains an input; executable inversion is only a two-by-two exact-rational auxiliary |
| Finite calculations promoted to infinite proof | Enumerations corroborate only the stated finite domains; infinite existence comes from Lean |
| Parent evidence implicitly reused as fresh | Parent ZIP is preserved and hash-authenticated; new sources import Mathlib and each other, not historical project modules |

The unipotent square control is mod-2 singular but Q_2-invertible, and its positive root does not commute with the center. The negative target fails the computed criterion. The rational checker explicitly rejects a derivative singular over Q.

Proofread in self-review mode: new mathematical prose and displayed formulas only. Notation was checked against the final theorem types, with B consistently identified as an operator on matrix entries. Mathematical-token changes made by proofreading: none. Unresolved mathematical scope issues are recorded in RESEARCH_BOUNDARY.md; they are not typographical fixes.

The contraction argument is standard. No literature novelty claim is made. The exact pinned Mathlib implementation, rather than the latest online documentation, was used for proof verification.
