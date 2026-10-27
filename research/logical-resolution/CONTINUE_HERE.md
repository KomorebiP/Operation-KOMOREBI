# Continue Logical Resolution v0.2

Read README.md, THEOREM_NOTE.md, FORMALIZATION_COVERAGE.md, PROOF_AUDIT.md,
DEVELOPMENT_FAILURES.md and both manifests before editing. This is the logical
branch, not p-adic Block 16. v0.1 is preserved under history/.

The standard-syntax translation target is CLOSED. Do not repeat it as an open
question or relabel the custom syntax as though the Mathlib adapter were absent.
The quantifier rank axis now has a genuine rank-zero/rank-one counterexample in
one standard model. It does not establish an arbitrary-rank strict hierarchy.

## Next bounded target

Design a finite relational-refinement certificate format that returns either a
verified finite-rank matching certificate or a distinguishing source formula. Use
translate_realize and standard_backForth_preservation to connect the result to
standard Realize. State finite model, operation closure and rank/horizon bounds
explicitly. Include noncommuting operations and avoid silently substituting a
word-length cutoff for an all-word atomic premise.

A different legitimate target is an equality-inclusive partial-isomorphism
interface. It must retain equality patterns of tuples; the old noninjective
quotient theorem does not supply full first-order elementarity.

## Preservation boundaries

* All eight inherited library files must remain byte-preserved in the current tree
  unless an explicit correction is needed and separately documented.
* Target states are exactly X; observation values are relationalized externally.
  Do not describe this as a native many-sorted implementation.
* Quantified exact transport needs surjectivity and relational iff, not only
  forward edge preservation.
* BackForth is proved sufficient, not necessary, for the fragment and allows
  unbounded operation-word atomic tests.
* QF non-elimination is parameter-free, in one fixed language and one model.
* Python is audited, not formally verified. Timeouts and caps are unresolved.
* No full-history rebuild, new discovery policy, benchmark advantage or novelty.

Run distribution integrity before rerunning audits in a clean extraction, then
use `python tools/run_checked.py --runtime RUNTIME_ROOT` for both complete audits.
The runtime/cache is external to the ZIP and must match the exact pins.
