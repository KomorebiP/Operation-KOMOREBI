# v0.14 development failures and repairs

1. A container pseudo-terminal execution request was unsupported. It did not start a usable asynchronous job. Assembly was rerun synchronously; all seven ZIP-part checks and the combined SHA check passed.
2. A host command limit interrupted the inherited local build while entering OpenWorld. No success was inferred. There were no surviving Lean processes when inspected. That module was rerun, and current-source successful records exist for every final target.
3. The first generic whole-plan upper bound used an addition-monotonicity lemma in a form that did not match the inferred expression orientation. It was replaced by an explicit local arithmetic step. The theorem statement did not change.
4. Three protocol lemmas included an unused DecidableEq section variable. Their declarations now explicitly omit it rather than suppress the warning.
5. Older if_true/if_false and if_pos/if_neg names triggered deprecation warnings under warnings-as-errors. They were replaced by the pinned release's ite_eq_left/ite_eq_right forms.
6. In a concrete posterior calculation, linarith did not identify a definitionally equal unfolded proof-dependent term. The already established equality was passed directly instead of treating these as distinct arithmetic atoms.
7. Aggressively unfolding the optional-receipt channel left a condition with a semireducible decidability instance, causing a rewrite mismatch at the implicit transparency level. The final calculation instead uses proved predictive-probability lemmas and a small kernel-decidable zero channel entry. No theorem was weakened and no placeholder was introduced.
8. The option-sum example initially used the wrong summand order in `change`; it was corrected to the actual none-then-some expansion. One unused simp argument was removed.
9. The first full negative-suite host call hit its outer time cap before all files finished. The remaining files were checked separately; all 21 final logs reach substantive false goals rather than import errors or timeouts. Sliced negative execution is now supported.
10. A rough unanchored declaration regex also matched the English comment 'theorem can'. The final anchored declaration inventory excludes comments, counts 86 new declarations, and checks all 679 exact fully qualified names against Lean's axiom output.

No source proof failure remains unresolved in the delivered five-module block. Empirical/modeling gaps are listed separately in PROOF_BOUNDARY.md. Fresh local compilation is not a fresh source rebuild of mathlib.
