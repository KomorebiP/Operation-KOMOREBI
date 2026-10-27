# Verification record — v0.8.0

## Current evidence

`audit/current_v080/VERIFICATION.json` records a complete clean build of all 56 proof modules and the root import, an axiom audit of 656 named theorems, and three negative controls. All checks passed. `audit/constructions_v080/CONSTRUCTION_AUDIT.json` separately records a successful audit of all 271 explicitly indexed non-theorem declarations.

The v0.7 baseline was rebuilt successfully first; see `audit/baseline_recheck_v070`. `audit/BASELINE_PRESERVATION.json` verifies that all 50 original proof modules are byte-identical. Root imports, release metadata, indices, documentation and verification version labels were updated. The separate delivery receipt records the fresh extracted-archive replay, source equivalence, and all 57 compiled project hashes.

## Procedure

The verifier deletes its project output directory before compiling, uses one Lean thread, treats warnings as errors, disables automatic implicit variables, and checks the pinned Lean version and mathlib commit. It hashes every positive source before and after the run. Every explicitly indexed theorem must have a reported axiom set. Construction audits cover all indexed definitions, abbreviations and structures separately.

Only `propext`, `Classical.choice`, and `Quot.sound` are permitted. The positive-source scan rejects `sorry`, `admit`, custom axioms, unsafe declarations, `native_decide`, and `implemented_by`. The indexer and lexical scanner are tailored to this project's syntax, not independent general-purpose Lean parsers. Counts exclude generated declarations and imported theorems.

The deliberately invalid files under `tests/negative` are excluded from the positive library. False-statement and placeholder examples must fail compilation. The axiom-injection fixture compiles, but its forbidden dependency must be detected and rejected by the audit.

## Finite rational audit

`checks/computation/infinite_reconstruction_exact.py` uses exact rational arithmetic with Python `fractions.Fraction`, matrix column-vector action, and induced infinity matrix norms. Its fixed MT19937 seed is 80820260927.

The successful run contains 36 variable-dimension finite cascades, 48 dyadic configurations, and 230 sequence/scalar cases, with 8,778 assertions. Three mutation controls reject omission of the coarse term, omission of the restoration gain, and replacing the strict dyadic coordinate threshold by a nonstrict one.

Variable-dimension layers construct C=[I M] and J=[I-MB; B] and verify CJ=I. Depths range from 1 to 6 with six variants at each depth. Dyadic configurations use depths 1 through 8 and compare recursive remainders against independent block-sum formulas. Geometric sequences use q=0,1/4,1/2,3/4,7/8 through depth 32; the scalar half/double example is tested through depth 64.

These bounded assertions are independent implementation checks. Infinite convergence, density and complete reconstruction are not inferred from them; those claims have separate Lean proofs.

## Failures and recovery

There are 26 saved development-attempt records, of which 11 have nonzero or timeout status. See `audit/DEVELOPMENT_FAILURES_v080.json` for the available records and their boundary. The first runtime-restoration launch referred to a directory while it was being renamed and failed. The retry from a stable script path restored the offline runtime successfully. An early foreground tool call timed out, and memory pressure slowed initial Lean imports. An unused optional artifact-service daemon was stopped to free memory; no proof checker or audit was disabled.

New Lean development initially failed on a reserved identifier, dependent family coercions, omitted explicit types, simplifier targets, arithmetic rewrites, and deprecated names rejected by the linter. These were corrected before the complete build. Any diagnostics caused by unfinished declarations belong to failed attempts, not admitted final proofs. Final positive sources contain no proof placeholder.

Failure logs are not a complete recording of every interactive action. Partial compiles, interrupted calls and development attempts are not substitutes for complete verification.

## Trust and scope

Lean 4.34.0-rc2 uses compiler commit `6a10ac8c22beadecabdbb0919c2b50214762f91d`. Mathlib is pinned to `aeb72f1e9981b6d35b426b16dca7759be3e7ba06`. Executable hashes and actual argv are recorded. The compiler/kernel implementation, cached dependencies and three permitted standard axioms remain trusted. No independent kernel implementation, compiler bootstrap audit or complete dependency rebuild is claimed.

The project-local version-1 manifest validator checks required fields and all declared source/output hashes. Its success does not itself authenticate execution or mathematical truth; the execution logs, Lean proof checking and replay are distinct evidence.

The dyadic coordinate theorem concerns the actual retained-detail hierarchy. Ordered convergence, absolute summability and uniform-norm convergence remain explicitly distinguished. No universal sup-norm reconstruction, arbitrary detail-sequence synthesis, orthogonal basis, compression, complexity bound, full pro-category comparison, stack/descent construction or novelty assertion is included.
