# Fourth-block development history

Author: Komorebi P. Release: PRSC VII v0.4.0.

## Captured proof attempts

The three new modules had 13 captured development checks: eight failed and five passed. Every attempted source, command, compiler exit code, timestamp and diagnostic log is retained in `fourth_block_development/`. These candidate files are historical evidence, not additional active release modules.

| Module | Attempts | Failed | Passed |
|---|---:|---:|---:|
| LeakageBound | 5 | 3 | 2 |
| ProjectedCurvature | 4 | 2 | 2 |
| SyndromeRecovery | 4 | 3 | 1 |

Failures involved elaboration, notation tokenization, rewrite orientation, unused/deprecated rewrite warnings, and one simplifier heartbeat limit. The simplifier issue was repaired using explicit finite-sum rewrites. No admitted proof or new axiom was introduced. Some Lean error diagnostics contain internal placeholder terminology, but that does not describe the final active sources.

## Cumulative audit parser failure

The first cumulative run compiled `ProjectedCurvature.lean` with exit code zero, but the verifier reported failure because it recognized only `depends on axioms: [...]`, not Lean's `does not depend on any axioms` output. The missing inventory entry was `KomorebiPaperVII.Curvature.jet_sandwich_zero`, which is axiom-free.

The initial run, all its logs and its failed/incomplete report remain in `fourth_block_initial_audit_parser_failure/`. The pre-fix verifier is preserved in `../provenance/verify_fourth_block_before_empty_axioms_fix.py`. No Lean source was modified to resolve this audit failure.

The parser now records explicitly axiom-free results as empty dependency lists, leaves missing reports missing, preserves unexpected axiom names for allowlist rejection, and rejects duplicate report names. Seven regression tests passed, recorded in `fourth_block_verifier_regression.log`. The verifier hash is now also part of the resume cache key, preventing reuse under changed auditing code.

## Final fresh cumulative run

Following the parser correction, all fifteen modules were recompiled without cached results. All 201 theorem audits passed, and both the false-equality and admitted-placeholder negative controls were rejected. `fourth_block_release_run/SUMMARY.json` is the authoritative final run, including commands, hashes and dependency audits. The historical failure is not converted into a success record.

## Scope

Only manuscript item 5.2 is newly marked fully checked. Items 6.4 and 8.1 remain partial. The five continuum conjectures remain unproved. Earlier papers, original numerical experiments, and imported Mathlib proofs were not independently rebuilt or rechecked in this block.
