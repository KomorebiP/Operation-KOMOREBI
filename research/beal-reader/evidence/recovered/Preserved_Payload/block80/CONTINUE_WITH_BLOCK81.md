# Continue with Block81

Use Komorebi_Beal_Block80_Restricted_Primitive_Affine_Obstruction_v8.0.0.zip as sole
checkpoint. Preserve the exact Block79 ZIP and nested history. Read README, all
work80 contracts, notes, report, source audit, failures and verification records.
Keep bytecode disabled and place the replay report outside the immutable root:

    python -B verify.py --report ../Block80_Replay.json

--replay-predecessor adds only the immediate Block79 default run, not all history.

NEW BOUNDARY
* The BARE restricted equation dp0=-alpha cup beta has a continuous primitive on
  G_(K,Sigma), Sigma=S_beta plus fixed2,3,5,7 and infinity. No extra ramification
  is necessary. Proof: dual S-unit Sha1=0, finite-S Poitou--Tate, local cup-zero.
  Pointwise p0-values have NOT been computed. This is not geometric Stage-P solvability.
* The exact ordinary localization image is J:k^10->k^24, kernel of fourteen
  S-unit rows. All toric conditions give A=EJ:k^10->k^15.
* Pattern ranks are7,7,8,7; homogeneous dimensions3,3,2,3; left-null dimensions
  8,8,7,8. Pattern C loses its old two plus directions by determinant1. Remaining
  homogeneous inertia is only at307/797/1483 (C only307/1483).
* With a COMMON pointwise semilinear frame, conditional choice bounds are
  343,343,49,343. Do not apply them to unrelated references or to actual existence.
* Beta Frobenius at its OWN ramified plus primes includes the local unit pi_q/q.
  The old twisted inertia also requires the norm scaling to the ordinary generator.
  Both are in RAMIFIED_FROBENIUS.md and the finite certificate.
* For any bare p0 the actual first-stage target t(p0) is explicitly defined in
  AFFINE_OBSTRUCTION.md. The obstruction N*t(p0) is independent of p0 choice.
  NO ACTUAL TARGET OR OBSTRUCTION VALUE HAS BEEN COMPUTED.

NEXT: compute that canonical restricted affine obstruction from an arithmetic
representative/defining extension or a direct relative-duality construction. Use
one common p0 and correctly labelled local generators. The evaluator is ready
for a supplied target, but a synthetic zero target is not an arithmetic origin.
A nonzero coordinate excludes the relevant Stage-P branch. If all vanish, build
its finite family and then impose the q-values/higher lifts. Preserve all auxiliary
upper-q controls, actual period targets, and conductor/depth distinctions.

All eight residual patterns remain. Unrestricted support/depth, minus component,
actual realization, independent upstream acceptance, CM/higher-level branches,
full signature and Beal remain open. No new Lean or independent reviewer.
