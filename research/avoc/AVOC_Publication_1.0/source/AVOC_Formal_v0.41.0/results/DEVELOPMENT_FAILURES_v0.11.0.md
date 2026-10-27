# AVOC v0.11.0 — development failures and repairs

These are development-time failures, not hidden successful proofs.

1. **Fiber membership did not close by `simp`.**  The first proof of `mem_valueFiberValues_self` left an existential preimage goal.  Repaired by explicitly supplying the state itself as the `Finset.image` witness.

2. **An assumed nonnegativity hypothesis was unnecessary.**  The first midpoint-decoder proof carried `hη : 0 ≤ η`, but Lean's warning-as-error linter showed it was unused.  The theorem was strengthened by deleting the unnecessary hypothesis; the fiber-diameter premise already supplies everything needed on reachable fibers.

3. **`Nat.find` needed explicit classical decidability.**  The first exact-minimum definition failed to synthesize `DecidablePred (HasValueCenterCoverCard ...)`.  Repaired by making the definition noncomputable and opening a local `classical` proof block; the associated `Nat.find_spec`/`find_min'` theorems were unfolded explicitly.

4. **Example proof scripts contained no-op tactics.**  Two initial `norm_num` calls were rejected by the warning-as-error linter because preceding simplification had already solved the arithmetic.  The no-op tactics were removed.

5. **Greedy helper hypotheses were stronger than required.**  The first greedy exchange lemmas carried an unused radius-nonnegativity hypothesis and an unused center-membership hypothesis.  Both were removed, strengthening the local lemmas while retaining nonnegativity only where finite-cover existence/termination requires it.

6. **Direct compilation of a new dependent module lacked its `.olean`.**  `ExactRateDistortionExamples.lean` initially could not import the just-created exact module.  The module was built through Lake first, then the warnings-as-errors direct check passed.

7. **Clean-build wrapper timeout.**  The first `lake clean; timeout 105s lake build AVOC` tool invocation outlived the UI execution call while its explicit bounded child continued.  No second build was started until the child stopped.  Subsequent slices resumed the same clean build graph.
