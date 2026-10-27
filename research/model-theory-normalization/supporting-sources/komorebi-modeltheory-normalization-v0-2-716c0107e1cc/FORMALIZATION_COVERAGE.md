# Formalization coverage: M2 / v0.2

**PASS:** 11 local library modules, 18 expected-outcome tasks and 181 named
library declarations checked in the final cold run. Five new modules add 35
theorem declarations, 24 definitions, one abbreviation and two inductive symbol
types. The complete local library has 102 theorem declarations. These are formal
declaration counts, not independent discoveries.

All six inherited source modules are byte-identical. Accepted local sources
compile with warnings treated as errors. Axiom dependencies contain only
`Classical.choice`, `Quot.sound`, and `propext`. No additional project axiom,
`sorryAx` or `Lean.ofReduceBool` occurs. Five deliberately invalid controls reject;
the positive nested-binder control accepts.

| New module | Checked endpoints |
|---|---|
| TaggedObservationalLanguage | Actual Language/Structure, tagged state/value meanings, pathTerm_realize and observedTerm_realize |
| ObservationalMathlibTranslation | Generic variable/binder environment bridge; translateAux_correct and toMathlib_correct in actual Mathlib satisfaction |
| StandardObservationConsequences | Surjective standard fragment transport, actual quotient, standard_fragment_type_iff, IsQF, global finite-code semantics, standard_behavior_definable |
| StandardLogicalBoundaries | Full-state-equality failure, spurious unguarded witnesses, nonsurjective witness failure, nested binding, empty state sort, non-QF existential |
| PathCompilerBridge | Old path normalizer to standard syntax: compileSource_correct, compileSource_isQF, retraction and exact source-fragment truth agreement |

The target uses Mathlib FirstOrder.Language.Term, BoundedFormula, Formula.Realize,
IsQF and Set.Definable. It is not a locally renamed custom target logic.

Lean: 4.34.0-rc2, commit 6a10ac8c22beadecabdbb0919c2b50214762f91d.
Mathlib: aeb72f1e9981b6d35b426b16dca7759be3e7ba06. The compiled upstream cache
is reused. The eleven local modules, not all of Mathlib, are cold rebuilt.

## Remaining boundary

No unrestricted complete-type/elementarity theorem, quantifier elimination,
theory-wide elimination of imaginaries, matrix-to-logical-code exporter,
verified Python extraction, trained proposer, independently held-out benchmark,
external referee review or literature-novelty verdict is claimed. Standard
parameter-free definability is relative to the declared value-naming language.
