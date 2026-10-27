# Komorebi Space — Lean continuation v1.11.0

This continuation formalizes the complete WR08 regularization alternative and finishes WR09 and WR16. Its acceptance state, exact evidence hashes, and remaining obligations are recorded in `PROGRESS_LEDGER.json` and `VERIFICATION_SUMMARY.json`.

## What changed

| Module | Scope |
| --- | --- |
| `RegularizationLimits.lean` | Fitted images approach the range-closure projection, residual norms approach the floor, the weighted penalty vanishes, and unattained projected data force correction norms to infinity. |
| `RegularizationStrongLimit.lean` | Constructs the unique minimum-norm preimage when attained and proves strong convergence of the full positive-parameter family. |
| `RegularizationNoiseLimits.lean` | Sharp scalar noise coefficient, noisy parameter-choice convergence, and inexact stopping-rule convergence with the complete three-term estimate. |

These modules add 31 explicit theorems and two definitions. The complete project has 151 production modules and three roots, with 1,650 explicit theorem/lemma statements. The new limits use the full right-hand real-parameter filter; WR16 also has the printed sequence statement. The correction spaces, operator and Hilbert norms remain fixed, with no new finite-dimensional, separability, injectivity or closed-range hypotheses.

## Reading the delivered archive

- `formal/` is the complete current source snapshot, including all production modules, roots, pinned dependencies, audit inputs and controls.
- `limits_v1.11.0/` contains the new overlay, exact frozen targets, numbered development attempts, compiler logs, complete exported types, axiom audit, independent reviews, and accepted replay evidence.
- The six release documents at the archive root summarize the current state. The copy under `limits_v1.11.0/` has the same bytes.
- `inherited_v1.10.0/` preserves every file from the accepted predecessor archive unchanged. Its PDF and coverage records describe v1.10.0; this Lean-focused continuation does not relabel that publication.
- `SHA256SUMS.txt` lists the SHA-256 of every payload file. The delivery verification and independent archive review are separate records, avoiding a circular archive hash.

## Verification and reproduction

Read the current `VERIFICATION_SUMMARY.json` for exact run and report identities. The verification uses Lean 4.34.0-rc2 with `-j1 -DwarningAsError=true -DautoImplicit=false`, a fresh project object directory, and the pinned external package caches. All project declarations are audited; only `propext`, `Classical.choice` and `Quot.sound` are permitted. All new declarations, including generated helpers, receive full explicit type exports.

The accepted replay command arguments and original absolute paths are historical provenance. To repeat from an extracted archive, use the separately provided portable runtime and create fresh labels with the scripts in `limits_v1.11.0/integration/`. Pass `inherited_v1.10.0/budget_v1.10.0/integration/runs/clean_budget_01` as the assembler's parent and `limits_v1.11.0/formal` as its overlay. Pass the actual runtime and path-adapter paths to the verifier. The assembler records the new absolute paths for the subsequent postflight. Do not edit an accepted receipt to make its paths look current.

The compiler/kernel and precompiled external dependencies remain trusted; those dependencies are not rebuilt from source. Runtime/source hashes are endpoint checks. The independent mathematical review covers WR08, WR09, WR16 and their required interfaces, not the entire monograph or a refinement of numerical executable code.

## Continue

The remaining principal formalization groups are WR10–WR12 and WR15. `NEXT_RESEARCH_BLOCK.md` gives exact restart obligations and a proposed bounded next target, WR15. Development and verification mistakes are retained with their corrected attempts; the event journal is `limits_v1.11.0/records/EVENTS.jsonl`.
