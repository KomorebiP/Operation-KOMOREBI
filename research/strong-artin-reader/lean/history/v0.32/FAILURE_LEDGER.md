# Failure ledger — v0.32

## Verification versus exploration

Only completed fresh source replays and their final all-constant axiom audit
constitute release evidence. Development logs include rejected drafts and are
not promoted to theorem status. All final active sources have passed with
warnings as errors; the prior parent archive is unchanged.

## Rejected development mechanisms / proof engineering

- An earlier interrupted work session did not retain a finished v0.32 checkpoint.
  The current work was reconstructed from the exact v0.31 archive and the stated
  polynomial route. No pass from that lost session is counted here.
- Initial imports guessed nonexistent Mathlib module paths (Basic and matrix
  notation). Actual pinned-source module names were used instead.
- A duplicate unnamed noncomputable scope initially prevented module closure.
- Polynomial power manipulation initially rewrote all exponent occurrences,
  creating an unnecessary Nat subtraction goal. A local exponent equality repaired it.
- Endomorphism-polynomial unit and image arguments required explicit commuting
  factors; no cancellation was performed in the zero-divisor endomorphism ring.
- Matrix conjugation coordinates encountered Pi/Matrix multiplication inference,
  unit-inverse coercions, and reassociation of finite sums. Explicit typed matrices
  and an exact sum interchange resolved these.
- Unipotent examples required the actual ZMod field import, explicit endomorphism
  types, matrix-entry expansion, and characteristic-three coefficient reduction.
- Rejected example drafts had unresolved goals and therefore automatically generated
  placeholder diagnostics. They were not counted; the accepted source and all
  named constants passed the final axiom scan without sorryAx.
- Unused-simp and sequencing linter failures were repaired rather than disabling
  warnings. A dependent mismatch rewrite was replaced by direct use of the
  inherited proved perturbation lemma.
- A large development dependency batch was interrupted by the outer execution
  wrapper. Missing modules were rerun; only observed zero exits were accepted.

These are implementation/verification failures, not counterexamples to the final
mathematical statements. The substantive negative control is the actual E_00
unipotent prescription: the proved norm image excludes it.

## Recorded attempt count

The current development ledger records 47 module attempts, including 19 rejected attempts. Exact diagnostics, source snapshots and hashes are retained under development/.
