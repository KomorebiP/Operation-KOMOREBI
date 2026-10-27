# Failure ledger

Twelve rejected development compiler invocations are retained in
`development/FAILURE_INDEX.json`, with the corresponding logs and source hashes.
They are not proof evidence. Some rejected source revisions were subsequently
edited in place; their logs and hashes are retained, not a replayable copy of
every rejected draft.

- The first compiler invocation failed to locate its runtime application. The
  documented portable-runtime path adapter resolved that launch failure.
- Early scalar drafts had a no-progress simplification, a misidentified ordered
  multiplication lemma, and a natural/integer exponent coercion error.
- The derivative formula required the explicit `derivative_X_pow` lemma. An
  unused section variable was removed from a purely numerical horizon bound.
- The diagonal proof required the product-unit import and correct theorem name.
  One control invocation ran before that dependency had compiled and failed to import it.
- Control proofs initially failed to normalize dependent residue-modulus indices,
  literal ring-hom images, and finite residue arithmetic. An overly broad cast
  simplification hit its recursion limit. Explicit rewrites and kernel `decide`
  completed the concrete residue checks.
- Warning-as-error checks rejected unused simplification arguments and redundant
  tactic sequencing. Those drafts were corrected before the accepted replay.

No counterexample to the final scoped theorem was found. The dying-prefix
examples are intentional mathematical controls, not failures of that theorem.
The clean accepted replay is recorded separately under verification/fresh/.
