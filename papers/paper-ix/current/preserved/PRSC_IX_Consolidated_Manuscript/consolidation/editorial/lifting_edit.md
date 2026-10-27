# Lifting section proofreading record

Scope: `manuscript/sections/30_lifting.tex`, all 906 original lines, including every statement, proof, example, scope qualification, and formal-source pointer. Final length: 922 lines.

Before SHA-256: `0a6b7b96375a2af8087c95b54ba767d16db1f7fb841f80fe91aa9454e6c71232`

After SHA-256: `83defce02868187bd53ae9088a5b5046b2f05d05c9cfa0f88ab4cd7ce9e2d952`

## Routine edits

- Made the section opening more direct and connected the finite correction problem to towers, parameter charts, and deformation.
- Removed repeated emphasis on “actual” where the polynomial system and its Jacobian were already unambiguous.
- Replaced procedural phrases such as “lower-root-only statements,” “complete interfaces,” and “scope controls” with ordinary mathematical prose while retaining every formal-source pointer.
- Explained recursion in terms of the conditions preserved at each step rather than implementation state.
- Clarified the prose description of the Taylor remainder and the purpose of the sign examples.
- Re-read changed sentences in context and corrected a draft punctuation error in the prescribed-parameter proof before freezing.

## Mathematical clarifications authorized by the parent

1. In Lemma `lem:polynomial-taylor`, replaced “for integer a,u,c” in its integer-divisibility consequence by “when R=Z and a,u,c are integral.” This explicitly specializes the coefficient ring, eliminating the inherited ambiguity. The general ring identity and every coefficient, sign, variable, and exponent remain unchanged.
2. Added an unnumbered paragraph after Corollary `cor:shared-polynomial` that records its already proved affine specialization for every positive integer modulus q and every natural depth L, including L=0. The paragraph specifies affine integer systems, the common lower root, the reductions of their linear parts, separately valid corrections, equality in the common quotient, finiteness, and label independence. It derives the conclusion from the existing affine correction equation and common-correction theorem, without introducing a new argument or an additional theorem claim beyond the checked source.

The affine specialization was checked directly against `source/shared_correction/formalization/AffineSharedCorrection.lean`, SHA-256 `b4e412dbf811a08e0fb673dbf7776e653d1d16c946306fc81e8ddee7bf1687a2`. Its `Komorebi.AffinePair.joint_lift_iff_class_eq` and `Komorebi.AffinePair.finite_affine_pair_compatibility` take natural modulus/depth and only positivity of the modulus; neither primality nor positive depth is assumed. Both source pointers were added to the manuscript.

## Preservation checks

All 546 original mathematical regions remain byte-identical and in their original order; 16 regions were added by the two explicit clarifications, giving 562. All 98 original Lean references, labels, and cross-references remain in order; five references were added, giving 103. All 116 environment tokens remain identical and in the same order. No existing theorem numbering or labels were changed.

The positive-depth hypotheses for nonlinear systems, composite-modulus and modulus-one cases, square uniqueness clauses, exact prescribed coordinates, approximate chart-center caveat, strict weighted thresholds, full uniqueness balls, displacement/error exponents, and distinction between rationally invertible and rationally rank-deficient Jacobians are retained.

## Unresolved local issues

None identified in this conservative proofreading scope. This is not a new independent proof audit of every theorem. The inherited Taylor-specialization ambiguity reported in the initial pass has been resolved explicitly.

## Validation

Completed: full textual read; before/after diff review; exact preservation and order comparison for original mathematical regions and references; exact environment-token comparison; direct affine-source hypothesis check. Existing proofs were not replaced or shortened. Lean source files were not edited, and no new Lean run was required for these manuscript clarifications. The parent is responsible for the combined LaTeX build and visual review.
