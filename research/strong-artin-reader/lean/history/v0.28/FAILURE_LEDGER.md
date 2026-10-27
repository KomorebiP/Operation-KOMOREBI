# Failure ledger — v0.28

## Mathematical failures retained as checked controls

1. Pairwise simultaneous extendability and equality on all overlaps do not imply a global lift
   matching a whole family. Three order-two subgroup characters of C2 x C2 give a checked example.
2. Order-invertible finite-image lifting does not automatically give literal matching of arbitrary
   local prescriptions. Two kernel-conjugate but noncommuting involutions over Z/9 give a checked
   example. Independent local conjugacies do suffice in the stated theorem.

Neither result refutes Strong Artin. These are counterexamples to intermediate shortcuts.

## Development rejections

- The first continuous-pair module had cocycle representation/coefficient coercion problems,
  insufficient unfolding of restriction, and unused section variables. All were corrected.
- Local mismatch proofs initially mixed definitionally equivalent kernel types and used
  subtraction as though definitionally equal to addition of a negative. Explicit types and
  algebraic rewrites repaired them.
- A redundant change tactic was rejected by warnings-as-errors and removed.
- A kernel-membership simplification needed an explicitly typed q(x)=0 fact.
- The finite example initially lacked coefficient-ring topology instances. Discrete instances
  were supplied locally for that finite test only. The general source remains nondiscrete.
- A matrix-map coercion needed its source and target matrix rings stated explicitly.
- One matrix-notation import used the obsolete guessed path Data/Matrix/Notation. The actual
  pinned source was inspected and LinearAlgebra/Matrix/Notation was used.
- Unused simp arguments and an overlong rewrite list were rejected and fixed.

Raw diagnostics, rejected source hashes, commands and accepted compile attempts are in
`development/ATTEMPTS.jsonl` and `development/logs/`. The final sources are not identical to
rejected drafts. No rejected run is treated as evidence for a theorem.

## Execution interruption

The first full release wrapper expired after recording 12 successful dependency modules and
before recording a new-module verdict. It was not counted as a completed verification.
The same unchanged source tree was resumed in bounded batches of 4, 4 and 2 modules. Every one of
21 source modules and the all-constant audit then had an observed zero exit code and the verifier
reported PASS. A separate extracted-archive replay is recorded outside the release ZIP.

## Scope

The pinned Mathlib compiled cache is reused. This is not an independent-kernel check, full Mathlib
rebuild, or full replay of all historical Strong Artin branches.
