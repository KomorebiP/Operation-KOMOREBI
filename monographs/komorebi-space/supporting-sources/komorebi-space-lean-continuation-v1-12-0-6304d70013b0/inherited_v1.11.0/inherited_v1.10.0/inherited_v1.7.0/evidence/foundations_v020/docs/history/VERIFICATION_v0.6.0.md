# Verification record — v0.6.0

## Current evidence

`audit/v06_current/VERIFICATION.json` records a clean build of all 44 proof modules and the root import, the complete axiom audit of 480 explicitly named theorems, and three negative controls. `audit/v06_constructions/CONSTRUCTION_AUDIT.json` audits all 203 indexed non-theorem declarations. All current checks passed.

All 38 v0.5.0 proof modules are unchanged, as recorded in `audit/v06_BASELINE_PRESERVATION.json`. An initial standalone baseline replay was interrupted to control resource use and is **not** counted as a completed verification. The cumulative clean build includes all these unchanged modules.

The separate delivery receipt records the fresh extracted-archive replay and comparison of all 45 compiled project files, including the root import. The archive contains no compiler/runtime cache.

## Verification procedure

The verifier deletes its project output directory, compiles the full dependency order, and records source and compiled-file SHA-256 values. Each Lean invocation uses one thread, warnings as errors, and disabled automatic implicit variables. All indexed theorem declarations are queried with `#print axioms`; a report is required for every requested declaration. Only `propext`, `Classical.choice`, and `Quot.sound` are permitted.

The separate construction audit performs the dependency check for all indexed explicit non-theorems. Generated declarations and imports are not counted as new explicit constructions. The lexical positive-library scan rejects proof placeholders, custom axioms, unsafe declarations, native_decide, and implemented_by after stripping comments. The project-specific declaration indexer is not an independent Lean parser.

The negative fixtures separately test false-statement rejection, proof-placeholder rejection, and detection of an injected custom axiom. The axiom-injection fixture is allowed to compile, but its forbidden dependency must be detected. These intentionally invalid fixtures are excluded from the positive library.

## Independent finite audit

`checks/computation/residual_sampling_exact.py` uses exact rational Fractions and absolute row sums for sup operator norms. It checks 120 variable-dimension candidate configurations, 24 section/defect-map configurations, and 32 stride-gain values. The successful run has **22,135 positive assertions** and three correctly rejected false claims.

The variable-dimension configurations use depths 2, 3, 5, 8 and 12, seeds 0 through 5, and four schedule types. The script compares a recursive block sum against an independently generated closed transported sum, then checks the actual differential identity, norm bounds, repair mismatch, and coordinate reconstruction.

This audit does not prove an infinite theorem. Its role is to test a second implementation, including cancellation and noncommuting rectangular operator composition. The universal statements have Lean proof terms.

## Failures and recovery

An initial interactive session request was rejected by the container interface. A subsequent setup attempt found that the intended work directory had not been created. The directory was then created and the saved five-part runtime was successfully restored and checksum-verified.

A partial baseline build was deliberately stopped to avoid simultaneous resource pressure. Two development tool calls timed out and were not treated as successful checks. An unused artifact-service process occupied substantial memory in the 4 GiB environment; its identity was checked and it was stopped before resuming single-process compilation. These events are recorded under `audit/v06_environment`.

Development compiles failed on dependency-prefix shadowing, deprecated simplification names treated as errors, section arguments omitted by elaboration, dependent-type transparency, and tactic/rewrite elaboration. Those errors were corrected before the clean cumulative build. `audit/v06_development` preserves the available compiler logs, but not a complete source snapshot of every failed attempt. A failed or interrupted process is not represented as a successful proof.

## Trust and interpretation

Lean 4.34.0-rc2 is pinned to compiler commit `6a10ac8c22beadecabdbb0919c2b50214762f91d`. Mathlib is pinned to `aeb72f1e9981b6d35b426b16dca7759be3e7ba06`. The concatenated runtime archive hash is `f7548038f94ea30789ce28fc2ff769c40e9c37d8879ea133e9bea821056342c7`. Each verifier run records the executable hash. The compiler, kernel implementation, permitted axioms, and cached dependencies remain trusted and were not independently rebuilt.

Verification applies to the theorem statements with their explicit hypotheses. The residual accumulation estimate requires contractive bonds and a bounded gap. Cofinal levelwise decay additionally requires unbounded sampling. The repair comparison assumes actual bounded sections of both differentials. The sharp norm theorem concerns the map on all bounded residuals, not surjectivity of the identity-tower differential.

No norm-independent geometry, nonexact eventual quotient, full pro-category equivalence, unrestricted descent, higher obstruction theory, arithmetic correspondence or novelty claim follows merely from these checks.

The manifest uses the existing version-1 evidence format. Its validator checks completeness and declared hashes. It does not authenticate execution or prove mathematics; the compiler logs, negative controls and replay are separate evidence.
