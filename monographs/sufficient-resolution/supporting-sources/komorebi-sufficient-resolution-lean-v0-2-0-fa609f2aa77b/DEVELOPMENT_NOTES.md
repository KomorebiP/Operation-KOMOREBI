# Development record — v0.2.0

The v0.1.0 archive was extracted, its six sources were inspected, and its complete
source-build/axiom/kernel verifier was rerun successfully before extension. The
runtime was absent in the new container and was restored from the five preserved
Lean_Compact archive parts in Library. Filename search returned no matches; a
metadata listing located the actual accessible parts. The inner combined payload
was identified as XZ before extraction. No alternate Lean or Mathlib version was
substituted.

## Draft failures and corrections

1. The initial narrow import guessed Mathlib.Tactic.Omega, which does not exist in
   the pinned cache. It was replaced by Lean.Elab.Tactic.Omega. The initial product
   import contained legacy IsLinearMap statements, not LinearMap.fst/snd/inl, and
   was replaced by Mathlib.LinearAlgebra.Prod. These were import/API failures.
2. A block-compression definition did not use its section variable, so Lean omitted
   that argument. An explicit parameter was added. This was an elaboration issue.
3. An attempted simplifier rewrite of 1 as 0+1 caused recursion in the all-state
   necessity proof. Direct expansion of the actual one-step map resolved it.
4. The polynomial remainder lemma's polynomial argument was implicit, not an
   explicit function argument. An explicitly typed intermediate equality fixed
   inference. A nested-negation witness was rewritten as a direct contradiction.
5. Expanding the canonical block construction too early prevented rewriting its
   prepared maps. The proof now rewrites the named maps before definitional reduction.
6. The default ext tactic selected scalar/product extensionality lemmas and did not
   consume supplied variable patterns. The rational controls now explicitly invoke
   LinearMap.ext, eliminating the warnings rather than disabling the linter.

All failed drafts' diagnostics and the passing follow-up runs are in
verification/development_v0.2.0/. Cascading messages containing compiler-inserted
placeholder diagnostics in unsuccessful drafts are not production proofs. The
final source contains no admitted theorem, and every final declaration passes the
axiom audit and kernel replay.

No new mathematical counterexample to the stated production claims was found.
The intentional delayed-return example refutes shallow extrapolation, and the
invisible-excursion example distinguishes prepared closure from all-state closure.
Both are checked Lean results and exact-rational Python controls.
