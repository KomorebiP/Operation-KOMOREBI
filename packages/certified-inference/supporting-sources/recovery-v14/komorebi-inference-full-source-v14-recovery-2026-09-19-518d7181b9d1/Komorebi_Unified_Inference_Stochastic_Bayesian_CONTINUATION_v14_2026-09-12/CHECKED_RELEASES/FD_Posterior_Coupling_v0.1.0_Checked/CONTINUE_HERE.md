# Continue after posterior coupling v0.1.0

The actual-law shared-noise posterior coupling, inexact gain residual cost, noise-floor
majorant, squared stopping implication, and two-model factor certificate are now
closed in this release. Do not repeat those blocks unless an audit inconsistency
requires correction. Read PROOF_NOTE.md and FINAL_VERIFICATION_RECEIPT.json first.

## Strongest next bounded target

Formalize packet-resolved Frobenius/Hilbert-Schmidt energy for the new distribution
certificate under explicit self-adjoint orthogonal-projector geometry. Start with
complete finite orthogonal projections and prove the square-sum identity for a
rectangular residual F (or factor discrepancy) between two Euclidean spaces. Then
transfer it to the residual-only W2 stopping certificate. Establish exact compatible
parent-to-child energy additivity for the fixed residual, not automatic reduction
of the error when an approximation changes.

A parallel lower-risk extension is the four-term covariance comparison identity
from the research-review supplement. It remains an unformalized proposal here.
Do not label it checked merely because the gain-residual identities are checked.

After packet energy, develop computable certified majorants with numerical rounding
control and validity-preserving candidate updates. An acceptance rule can retain a
better certified incumbent, but algorithm termination and strict improvement need
separate proofs. Then pursue finite-horizon filtering kernel recursion.

## Hard boundaries

Use the standard all-plan transport definition in QuadraticTransport.lean. This
release does not prove all metric axioms, existence of an optimal plan, or an
interchange theorem for a different definition. Keep these distinctions explicit.

The arbitrary-gain Gaussian is a valid approximation, not automatically the original
model's exact conditional distribution. Noise floors are supplied mathematical
certificates, not verified eigensolver output. Factor discrepancies require declared
compatible factors; identical distributions can have a positive chosen-coupling cost.

Do not infer self-adjointness from inherited pairwise-annihilating projector records.
Do not claim operator-norm Pythagoras. Do not identify every primitive model error
from a zero posterior error. Explicit posterior versions are pointwise; canonical
versions retain evidence-a.e. qualifications. Preserve positive noise, singular-prior
support, no literature novelty, no nonlinear/Itô/sequential/optimal-refinement claims.

## Rebuild discipline

Use MODULE_ORDER.json and verify_blocks.py, one module per short-lived tool call,
40-second process cap, one thread, warning-as-error. Use --clean only at the start
of an actual rebuild. Keep failed snapshots; audit every final theorem/lemma, not
only selected main statements. Confirm source and direct dependency hashes before
sealing. The pinned runtime is external to the source release and recorded in the
full continuation's LEAN_RUNTIME_METADATA.
