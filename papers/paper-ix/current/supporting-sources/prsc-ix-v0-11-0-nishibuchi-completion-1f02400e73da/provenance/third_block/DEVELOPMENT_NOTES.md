# Development and verification notes

## Third block: weighted dyadic reconstruction (v0.3.0)

The input is the exact v0.2.0 archive recorded in `provenance/third_source.json`. All 13 original Lean modules, the corrected source PDF, and both earlier mathematical supplements were preserved. The portable archive was restored locally. Seven part hashes and the assembled hash matched; the unchanged 13-module second-block verifier also passed a new clean baseline run before this development.

Four new modules complete the recorded scopes of 5.1–5.4. The source is strengthened from integrality to unit status. The manuscript's ordinary beta coefficients and even row indexing are maintained. Explicit normalization bridges connect rational coefficients to actual `ℤ_[2]` elements. No mathematical theorem is assumed as a custom axiom, no admitted proof is permitted, and the error divisibility is not formulated over a field.

Of the **15 captured development checks, eight failed and seven passed**. Every checked source snapshot and compiler diagnostic is retained in `verification/third_development/`. Problems included a subring membership goal needing explicit unfolding, natural/rational valuation casts, finite-sum indexing, formal-series homomorphism normal forms, inverse-coefficient recurrence rewriting, and the cast of the normalized rational error into the completed field. The final proofs repair these engineering issues. The statements were not weakened to assume the reconstruction or congruence conclusion.

A fresh 17-module cumulative build passed with warnings treated as errors, 219 theorem reports, 53 definition reports, all nine dependency pins, and eight deliberately invalid proof controls. The controls include three new errors: omitting the scale `2^(2*m)`, confusing ordinary with exponential beta coefficients, and asserting an additional false precision bound. A failed draft or rejected negative proof is never treated as a partial proof of its intended statement.

The new exact-rational Python mirror uses independent factorial-series inversion, not project Lean extraction. It checks 49 coefficient-integrality/source-unit cases, 97 complete formal-series coefficients, 49 Euler rows and 2,548 truncation depths through degree 96. Of these errors, 1,176 are nonzero and 1,372 are exactly zero. The finite valuation helper rejects zero; exact zero is recorded explicitly rather than assigned finite valuation zero. Forty-eight Bernoulli-formula comparisons are finite checks only. Both older independent Python mirrors were rerun into separately named third-block reports without replacing their historical evidence.

The earlier infrastructure tests were adapted to the larger inventory and their original v0.2.0 copies saved under `provenance/second_block/`. Sixteen new tests bring the total to 49. The old metadata and verifier source are also retained. The five original negative controls remain, with three added. The release's raw evidence distinguishes local Lean proof checking, mirror tests, source preservation and dependency pin checks.

The original historical numerical suite was not rerun. The unnumbered Bernoulli identity, analytic convergence, general 7.5 finite-difference theorem, three classical inputs and two conjectures are not promoted to newly proved claims. Mathlib's compiled cache remains a stated dependency. No new SVD, physics, prime-gap or continuum claim is made.

---

## Earlier preserved notes

# Second-block development and trust boundaries

Author: Komorebi P.

## Actual run sequence

1. The first-block sources were recovered unchanged and checked in a clean directory. This eight-module baseline passed and is retained under `verification/baseline_recheck`.
2. Fifteen captured new-module development invocations produced eight failed and seven successful checks. Failed draft sources (`.lean.txt`), commands, hashes and compiler output remain under `verification/second_development`. The failures involved unavailable names, expression normalization, incomplete proof goals and warnings. They are not proof successes.
3. A preliminary clean cumulative second-block run passed with 162 theorem declarations. Its exact inventory and coverage snapshots are retained under `verification/second_final`. It preceded the explicit row-action theorem connecting the matrix entries to Euler reconstruction.
4. The final source includes that row-action theorem. A separate clean run under `verification/second_release` accepted all 13 modules, 163 theorem declarations, 37 definitions, nine dependency pins and five expected-rejection controls. Only this final 163-theorem run is the authoritative second-block result.
5. All 33 Python unit tests passed after the final inventory update. Independent exact regressions cover 234 reconstruction rows and 2340 truncation depths, alongside both generating-function identities and signed-zigzag coefficients. These are finite mirrors, not executions extracted from Lean.

An initial request for an interactive container session was unsupported. Noninteractive runtime assembly and extraction succeeded. All seven part hashes and the combined archive hash matched, as recorded in `provenance/second_runtime_recovery.log`.

The first two PDF drafts had an overfull module-name paragraph. It was repaired before the final PDF build. The final six-page PDF was rendered and every page visually inspected. Formatting failures are not mathematical proof failures.

## Preserved and changed material

All eight upstream active proof sources, the original corrected manuscript PDF and the first-block supplement PDF/TeX are preserved byte for byte. Their checksums are recorded. Original metadata, README, verifier, launcher and unit-test file are archived in `provenance/first_block`. The active verifier and tests have been extended for the new modules, coverage and controls. Earlier first-block failures are retained as historical evidence and are not new second-block failures.

## Limits

Formal series do not certify analytic convergence. Coefficient-defined zigzag numbers are connected to the actual formal secant-plus-tangent series, not to a new enumerative interpretation. The new integer congruence does not establish the later global finite-difference theorem. Mathlib's cache was reused, not rebuilt. Earlier papers, native Windows, and the original historical numerical package were not tested. No formal proof of prose-to-Lean semantic equivalence is claimed.
