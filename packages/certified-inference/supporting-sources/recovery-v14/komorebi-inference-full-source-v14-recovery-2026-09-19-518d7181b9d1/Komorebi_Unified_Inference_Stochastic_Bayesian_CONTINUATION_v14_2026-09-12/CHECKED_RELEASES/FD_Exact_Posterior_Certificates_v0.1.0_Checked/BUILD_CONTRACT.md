# Computational and verification contract

## Universal theorem
Exact finite rational model/candidate/packet checks imply the real Gaussian
posterior Wasserstein score/tolerance bounds. The model is factor-coded and the
observation is the exact rational vector embedded into the real Euclidean space.
Finite candidate folds retain valid certificates and do not increase their scores.

## Arithmetic domains
Lean finite exact rational arithmetic, real Euclidean Gaussian measure theory,
and a nonnegative extended-real all-coupling quadratic transport infimum.
Python producer: fractions.Fraction, no binary floating-point input acceptance.
Independent tests: SymPy exact rational matrices and trace identities.

## Verification procedure
Use MODULE_ORDER.json with verify_blocks.py; each invocation calls the actual
pinned Lean process with -j1 -DwarningAsError=true. Maximum 40 seconds per Lean
process. Only RC=0 for final source bytes counts as a successful module check.
The entire active dependency chain has final-source receipts. Per-process logs,
source snapshots, direct dependency hashes, output hashes, commands, versions,
and elapsed times are retained under audit/. Full theorem axiom coverage is
recorded by RationalPosteriorAxiomAudit.lean and AXIOM_AUDIT.json.

## Finite assertions
The independent suite checks twelve constructed model dimension pairs n=1..4,
k=1..3, and 173 exact assertions with 57 negative checks, without randomness.
These are tests, not the proof of universal soundness. Two exported concrete
models separately have kernel-checked posterior-distance conclusions. See
results/FORMAL_INSTANCES.json for their input/source hashes and receipts.

## Failure interpretation
A false check must not acquire a posterior certificate. The negative controls
submit a false arithmetic equality, a placeholder, and a forged certificate claim.
A resource timeout is inconclusive, not a successful rejection. Incorrect imports,
elaboration failures, and linter failures are implementation failures, not
mathematical counterexamples. All corrected attempts remain in the evidence.

## What a pass does not establish
No external parser/serializer correctness; no interval semantics for unknown real
inputs; no verified floating-point runtime; no automatic covariance factorization;
no solver contraction/termination/optimality; no true-error monotonicity at each
accepted proposal; no performance or literature-novelty claim.

The official Mathbox manifest validator executable was unavailable. The supplied
project integrity checker verifies actual final-source receipts, dependency/output
hashes and full axiom coverage. No official-validator execution is claimed.
