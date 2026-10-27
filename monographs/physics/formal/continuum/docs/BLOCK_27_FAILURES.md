# Block 27 failures and repairs

The following failed development paths were retained as methodological evidence but are not proof evidence.

## Direct normalization of gauge-path quotients

Initial attempts asked `simp` and `group` to normalize link divisions and inverse factors in one step.  They did not close reliably.  The repaired proof first establishes the gauge law for each face path, then cancels the common endpoint factors in the plaquette ratio.

## Monolithic adjacent-path factorization

Direct normalization of three-edge path identities obscured which face was being exchanged.  The repair decomposes each theorem into a two-edge face identity followed by an explicit cancellation/associativity step.  This also makes the geometric orientation auditable.

## Brute-force Bianchi normalization

A single group-normalization attempt did not produce a stable proof of the cube identity.  The final proof follows two adjacent-transposition chains from `XYZ` to `ZYX`; both end at the same path, which is then cancelled.  This proves the identity from the already checked face factorizations.

## Over-expansion of the Hilbert defect

Simplifying the defect inner product expanded the four-spinor product into coordinate sums and made the scalar structure harder to control.  The repair uses the abstract scalar-linearity lemmas for `ip`, followed by ring normalization.

## Redundant closing tactics

Several intermediate proofs contained an `ac_rfl` after `simp` had already closed the goal, producing `no goals to be solved`.  The redundant tactics were removed before the warnings-as-errors build.

## Negative controls

Three false statements are compiled as expected failures:

1. universal equality of the two corner paths in the explicit nonflat cube;
2. treating raw eight-vertex replication as Hilbert-isometric without the one-eighth measure;
3. asserting zero transported-spinor defect for the `-1` plaquette witness.

Each fails with an unsolved mathematical goal rather than an import, parser, or environment failure.
