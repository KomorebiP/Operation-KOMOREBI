# Block 03 Development Failures and Corrections

Every item below is preserved as diagnostic evidence. None is counted as a
successful verification.

## 1. Portable-runtime extraction command timeout

The seven archived runtime parts passed their individual hashes and reconstructed
the recorded archive hash. The extraction command exceeded its execution cap.
The resulting runtime was nevertheless complete enough to report the recorded
Lean and Lake versions and to execute the project-specific verifier.

Interpretation: environment timeout. It is not evidence that the full runtime
self-test completed. The load-bearing project build and per-file checks were run
separately and completed.

## 2. Prop-valued certificate containing Type-valued realization

Log: `block03_build_attempt01.log`

`SourceBoundCertificate` was initially declared as a `Prop`-valued structure,
but `CertifiedRealization` is a data-bearing `Type`. Lean correctly rejected a
non-proof field in a proposition-valued structure.

Correction: keep `SourceWitnessTheorem` in `Prop`, but make
`SourceBoundCertificate` a `Type`-valued structure.

## 3. Type-valued realization placed directly in a conjunction

Log: `block03_build_attempt02.log`

The countermodel theorem initially attempted to place
`CertifiedRealization ...` directly inside `And`. Lean rejected it because
`CertifiedRealization` is a type of data rather than a proposition.

Correction: use the propositional wrapper `TransportedRealizable` in the
logical theorem and retain the concrete realization object separately.

The same build also produced proposition-as-definition linter warnings.
Correction: declare the proof objects as `theorem` rather than `def`.

## 4. Proposition declared with `def`

Log: `block03_build_attempt04.log`

`cor312CertificateOfSourceWitness` was accepted but produced a linter warning
because its result is a proposition.

Correction: change the declaration to `theorem`. The warning-as-error audit
then passed.

## 5. Boolean observable written as a proposition-valued conditional

Log: `block03_build_attempt06.log`

The positive example used `if b then ...` with `b : Bool` in syntax that Lean
interpreted as a proposition-valued condition.

Correction: define the observable by Boolean pattern matching.

## 6. First Block 03 verifier contract mismatch

Console: `block03_final_console_attempt01.log`

The clean build and all 22 warning-as-error source checks passed, but the
verifier expected the exact documentation substring “not a proof or disproof”.
The document contained the semantically equivalent phrase “a proof or disproof”
in a sentence already governed by “not”. The contract audit failed.

Correction: make the contract marker semantic and less brittle by checking the
phrase “proof or disproof of Corollary 3.12”. The entire final verification was
rerun.

## Successful build progression

- attempt 03: first full build of the initial Block 03 source set
- attempt 05: warning-free build after the Corollary bridge correction
- attempt 07: final source set, including the positive example, built in 24 jobs

The authoritative result is
`verification/block03_final/verification.json`. Superseded logs are retained
only for provenance.
