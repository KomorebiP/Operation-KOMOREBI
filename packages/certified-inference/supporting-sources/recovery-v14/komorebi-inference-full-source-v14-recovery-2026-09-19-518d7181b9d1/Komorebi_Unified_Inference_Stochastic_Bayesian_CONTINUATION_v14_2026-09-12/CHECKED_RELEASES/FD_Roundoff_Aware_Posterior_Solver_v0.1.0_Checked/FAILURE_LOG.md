# Failure and verification log

No failed or interrupted run is counted as a successful proof check.

## Corrected draft checks (six completed failures)

1. RoundoffEnergy initially had simplification/API mismatches and redundant tactic
   steps. Explicit rational normalization, the correct order-cancellation lemma,
   and removal of already-solved steps produced the final successful check.
2. RoundoffTracking included unused section typeclass assumptions. They were
   explicitly omitted instead of disabling warning-as-error checking.
3. RoundoffConvergence similarly inherited unused typeclass assumptions in one
   weight-positivity lemma; those assumptions were omitted.
4. RoundedSolverSearch needed the locally defined fallback precision unfolded in
   a finite-list membership proof. The final proof supplies that unfolding.
5. RoundedSolverOrigin initially treated a nested setup/tolerance test as one
   conditional. Its proof was corrected to inspect both tests.
6. The follow-up origin proof needed zeta reduction of the local candidate before
   splitting the inner test. This was added and the entire origin module passed.

Attempted source snapshots, logs and compiler exit records are retained under
`audit/`. None of these was a mathematical counterexample to the claimed result.

## Execution interruptions

The first direct GeneratedRoundedGainRotated invocation reached the outer tool
window without a completed verification receipt. The unchanged source was rerun
as a bounded process that could be observed separately; it completed successfully.
After the quantitative posterior corollary was added, both concrete example
modules and their downstream boundary/audit modules were checked again. The seal
uses only receipts matching their final source and dependency hashes.

An initial request for streaming container execution was rejected because that
feature was unavailable. No Lean process ran in that attempt. Runtime assembly
and subsequent checks used ordinary supported bounded execution. All five runtime
part hashes and the combined archive hash passed during restoration.

## Controls and trust boundaries

Three deliberately invalid Lean controls were rejected: a false natural-number
equality, a placeholder proof, and a dropped-radius enclosure claim. These are
expected rejections, stored separately from active sources.

The active proof sources contain no placeholders, custom axioms, unsafe proof
shortcuts or native evaluation shortcuts. Every active theorem/lemma declaration
was included in the final axiom audit. The final source/log/output/direct-dependency
seal passed.

The external Mathbox manifest-validator executable was not found in the working
filesystem. It was not run. The packaged verifier checks actual successful
compilation receipts and hashes; the computation manifest uses the available
version-1 schema. A passing seal is not itself a new Lean run.

## Corrected release-assembly issue

The first packaging attempt used a fixed root-manifest name, but the predecessor
uses MANIFEST_SHA256.txt rather than SHA256SUMS. Validation stopped before a full
continuation ZIP was produced. The checker was corrected to read the observed
manifest names. An unrelated Path.with_suffix call shortened the versioned focused
ZIP name; explicit suffix appending fixed it. The intermediate wrongly named ZIP
was removed. Both final archives are validated independently after assembly.
No proof source or inherited file was changed by these packaging corrections.
