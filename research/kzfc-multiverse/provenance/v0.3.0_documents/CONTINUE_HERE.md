# Continue from v0.3.0

Use this archive as the verified predecessor. Read THEORY.md, PROOF_BOUNDARY.md, DEVELOPMENT_FAILURES.md, the active Lean modules, and verification/RESULTS.json before editing.

## Current mathematical position

The previous depth-zero compactness translation is preserved. The finite-prefix derived-reflection candidate fails for the multiplication-by-three integer tower. Its obstruction has a genuinely countable support requirement in the explicit prefix-or-whole test family.

The main forward theorem is FineUltrafilterCompactness.compactness_of_fine_complete, together with small_obstruction_of_no_global and residualSystem_krr0. The existence of the ultrafilter remains a premise.

## Next block, in priority order

1. State an independent set-theoretic compactness notion and prove the link to HasFineCompleteUltrafilter at the correct universe and cardinal bounds. Do not define strong compactness to be the desired conclusion and then call the resulting identity a classification.
2. Formalize the filter construction on P_kappa(I), its kappa-completeness under regularity, and the derivation of a fine complete ultrafilter from an explicitly stated complete-filter extension principle. This gives a concrete upper-bound implication without implementing all infinitary syntax at once.
3. Instantiate the fixed-domain constraint theorem with arbitrary integer linear equations and explicit finite supports. Verify that the required |Z|<kappa condition is present. The multiplication-by-three example must remain a valid regression test at the finite-support scale.
4. Formalize the cokernel-to-R^1-lim identification, or clearly keep that comparison external. The concrete obstruction theorem does not depend on completing this layer.
5. Fix the admissible residual class, semantic support, and permissible translations before asking a new non-flattening or independence question. Then investigate a reverse implication, rather than inferring strength from notation or homological degree.

## Mandatory preservation tests

Rebuild all predecessor results. Re-elaborate all active source files with warnings as errors. Audit axiom dependencies. Reject a false proof and a placeholder. Preserve old proofs byte-for-byte or record and justify every intentional change. No success claim without completed compiler logs.
