# Continue the Lean Euler program from v13

## What to replay first

Read `PROOF_AND_STATUS.md`, `PROOF_BOUNDARY.json`, and the final axiom logs. Run
`scripts/replay.py` with a fresh evidence directory using the pinned portable
runtime. The final compiled source is indexed by `THEOREM_INDEX.json`.

## Highest-value next block

Build a rigorous restricted-series evaluation and preparation/lifting bridge.
Do not substitute the local-ring *formal* Weierstrass theorem (first nonzero
residue coefficient) for the closed-unit-disc *restricted* preparation theorem
(last odd coefficient). Formal series units need not be nonvanishing on the
whole unit disc; `1+X` is the elementary warning.

First prove coefficientwise residue soundness for convergent series and Hasse
jets. That connects the kernel-checked residue models to analytic functions.
Then formalize the finite-index Bernoulli/source coefficient evaluator and its
whole-series precision cutoff, so the actual Euler congruences can be imported
as proved equalities instead of external certificate hypotheses.

## Exact open research targets

The scalar-zero question in terminal129 and the remaining possible double-root
progression at terminal161 remain unsolved. `square_chart_critical_iff` proves
what those zero scalars would mean; it does not prove they are nonzero.

The depressed cubic discriminant module gives an exact polynomial obstruction,
but it applies only after a genuine exact polynomial/chart identification. It
must not be applied to the cubic Taylor truncation of an infinite series.

The synthetic exact triple-root theorem is a permanent negative control. Any
proposed generic nondegeneracy argument using only a simple lower reduction and
nearest-neighbor shape must fail on that non-Euler example.

## Delivery discipline

No custom axioms, sorry, native proof evaluation, or assumed resolution claims.
Keep pending bridge statements in the external status ledger rather than adding
unproved Lean constants. Re-run the full transitive axiom audit after each block.
Preserve the exact hypotheses of each compiled theorem in progress summaries.
