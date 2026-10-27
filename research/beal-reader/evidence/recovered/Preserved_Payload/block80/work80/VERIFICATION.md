# Verification protocol and evidence

The immutable package contains exact finite results and a manifest of every payload.
Run python -B verify.py --report ../Block80_Replay.json outside the report directory.
The verifier removes the four expected scientific outputs and the generated fixture
in a scratch copy, rebuilds all of them, and compares complete content. It checks
that the two main outputs agree exactly, rather than accepting a cached status flag.
The independent extra output certifies seven direct local self-unit computations
and16 rank checks by separate determinant expansion and complete null bases.

The evaluator self-test uses only SYNTHETIC targets and never reports an arithmetic
p0 or an actual pattern exclusion. It checks image/nonimage classification, affine
origin invariance, strict input validation and the fixed-local primitive formula.

Nine deliberate corruptions test rejection of changed self-column data, omission of
a degree-two component, incorrect inertia scaling, an invented arithmetic origin,
a wrong tangent dimension, a missing unit witness, malformed target coefficients,
a nonimage target labelled solved, and an altered archive payload.

The already observed initial Block79 default replay is retained as
verification/PREDECESSOR_REPLAY.json. New scientific run metadata and input before/
after hashes are in COMPUTATION_MANIFEST.json. The project-local legacy-v1 validator
is explicitly labelled; it is not the full plugin validator. The final ZIP is
extracted into a fresh directory and its own replay and integrity audit are saved
externally. Timings of those final events are not embedded in the immutable ZIP.
No full historical-chain execution is inferred from an immediate-predecessor run.

No computation verifies the analytical Frey geometry or proves Poitou--Tate.
Those are written, source-checked or inherited mathematical dependencies. No new
Frobenius point counts, Lean compilation or independent mathematical review.

## Observed before final archive freeze

The rebuilt development verifier completed in22.181512 seconds, including the
immediate Block79 default replay in16.0563 seconds. All current scientific outputs
and the generated fixture were rebuilt. These observed numbers are in
verification/DEVELOPMENT_REPLAY.json. Final archive replay is recorded externally
after extraction. No full historical-chain replay is claimed.
