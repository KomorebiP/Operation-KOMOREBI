# Continue Paper I after Block 04

Read VERIFICATION.json first. Its accepted status requires both recorded fresh stages to pass. Read PROGRESS_LEDGER.md and coverage/COVERAGE_108.json next. Keep predecessor/ source-identical.

## Completed mathematical core

The new source lives in source/extension/PaperICompletion4/:

- ResidueQuotient.lean: exact full residue-map kernel pM, surjectivity, canonical residue-ring-linear quotient equivalences and natural transport.
- IntrinsicPrimary.lean: literal power-annihilation primary submodule, equality with Mathlib's principal-ideal primary component, exact inclusion kernel pX_p, Artinian surjectivity by stabilized images, natural X_p/pX_p -> M/pM equivalence.
- GroupedPrimary.lean: literal intrinsic component equals the matching primary coordinates and is equivalent to the grouped product.
- OperatorIntrinsicFormula.lean: actual p(T) interpretation, intrinsic quotient/fibre equality, count for arbitrary primary decompositions of X_p, invariance of every multiplicity, the bounded attained maximum over all monic irreducibles, and both canonical seed-rank equalities.

Do not re-open the primary existence, CRT generator, residue lower-bound, intrinsic kernel or intrinsic-quotient obligations as though they were missing. Their proofs now exist. The original normative contract still has 35 rows and is unchanged.

## Next mathematical target

Prove the geometric-multiplicity formula for arbitrary finite-dimensional operators over an algebraically closed field, including non-diagonalizable operators. The previous self-adjoint result does not discharge that general case.

A shorter route is now available through the global quotient, rather than another analysis of the restricted primary operator. For p = X - C lambda, use the completed equivalence X_p/pX_p ≃ V/pV and identify k[X]/(p) with k by evaluation. Identify the underlying k-submodule pV with the literal range of T - lambda I, using operator_scalarImage_membership. Finite-dimensional rank-nullity then gives

    dim_k V / range(T - lambda I) = dim_k ker(T - lambda I).

Finally, use the proved classification of irreducibles over an algebraically closed field to turn the intrinsic maximum into the maximum eigenspace dimension. Values outside the spectrum are zero. Preserve the empty-spectrum zero-space convention.

This is a proof plan, not a verified Lean result. It still needs actual scalar restriction/transport across the residue-field equivalence and the actual quotient equivalence, rather than an informal equality of dimensions. A valid alternative is to use the kernel of p(T) restricted to X_p, but the global quotient route should need fewer new structures.

Then address the remaining rational-canonical and algebraic-closure scalar-extension clauses of PSC-I-C-CYCLIC-MATRIX. Read its exact six-way statement before selecting the smallest sufficient bridge. Do not assume that a split/self-adjoint theorem proves arbitrary scalar-extension invariance. Do not assume existence of an ordered invariant-factor decomposition from the conditional count theorem alone.

## Other obligations remain

The nonsplit semisimple, module-top/Nakayama, expanded packet/functorial/topological and executable algorithm entries are still tracked separately. Proving the printed single-operator theorem by the stabilized-image route does not retroactively formalize its prose proof's unfinished local-module lemmas. Papers II–XII have not been rerun in this sweep.

## Reproduction

Use the pinned portable Lean runtime specified in VERIFICATION.json. The runtime and authenticated Mathlib cache are external prerequisites. Do not run lake update.

    bash scripts/run_block04.sh /absolute/path/to/runtime /absolute/path/to/new-output

The combined launcher executes the unchanged Block 03 baseline verifier and then the new extension verifier. For this handoff, those two stages were executed individually in evidence/baseline_fresh and evidence/extension_fresh. The combined convenience launcher is syntax-checked rather than represented as a separate third full execution.
