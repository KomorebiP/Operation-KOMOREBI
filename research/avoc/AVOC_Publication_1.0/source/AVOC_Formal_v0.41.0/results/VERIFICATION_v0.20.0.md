# AVOC v0.20.0 — current verification record

## Result

**PASS:** 106/106 current local compilations, 1,020/1,020 theorem axiom reports, 44/44 substantive negative rejections, 22/22 live recovery cases.

- 37 new theorem/lemma declarations in four modules.
- Complete inventory: 1,020 theorem/lemma declarations, 100 non-audit modules, 16,248 non-audit Lean source lines, 459 definition-like declarations.
- 96 inherited non-audit modules are byte-identical to v0.19.
- Counts include helpers and examples; they are not independent-discovery counts.

## Runtime and build scope

Lean 4.34.0-rc2, commit `6a10ac8c22beadecabdbb0919c2b50214762f91d`; mathlib `aeb72f1e9981b6d35b426b16dca7759be3e7ba06`, with all nine dependency pins checked. Python 3.13.5; SQLite 3.46.1. The portable runtime's seven archive parts and assembled compressed archive were checksum-validated before extraction. Local build outputs began empty. External dependency caches were retained; no fresh source rebuild of mathlib is claimed.

The final evidence collector verifies every current local `.lean` source against its recorded successful compilation and current `.olean` output, including current log hashes. Interrupted targets are not counted until rerun successfully. Aggregate and trusted checker/planner/recovery entrypoints are included in the 106.

`AVOC/FullAudit.lean` names exactly all 1,020 declarations. Its current axiom log reports only `propext`, `Classical.choice`, and `Quot.sound`. The independent comment/string-aware source census matches the inventory. The scan distinguishes `.admit` action constructors from the forbidden proof tactic; complete axiom auditing separately detects placeholder/custom-axiom dependencies.

## Negative proofs

All 44 files under `tests/negative` have final nonzero exits, no timeout, substantive Lean errors and no import/setup-only failure. New files:

- `FalseUnfinishedRecovery.lean`
- `FalseRecoveryFromSnapshotAlone.lean`
- `FalseDuplicateCommit.lean`
- `FalseDoubleRecoveryCharge.lean`

Their corresponding mathematical obstruction/idempotence statements are positively proved in the library. A failed attempt alone is not counted as proof of negation.

## Live recovery suite

22 cases each used a fresh protected temporary run and current pinned implementation sources. Real SIGKILL injections covered after intent, after evaluation, after each write group inside the SQLite publication transaction, after committed register/verify/admit/stop, before acknowledgement and after acknowledgement. Additional cases checked duplicate recovery/publication, changed commit records and post-state, candidate/config drift, cooperative locking, unfinished intent, incomplete initialization and forbidden user report bits.

The final source-pinned case records and raw stores/invocation requests are under `results/v0.20.0/recovery_tests/`. `recovery_test_summary.json` names and hashes all 22 case records.

For the recorded admission-after-commit kill, actual admissions remained one, backend checker calls remained three, planner-search calls remained three and conservative nominal fees remained three. Confirmed steps advanced from two to three. A later repeated recovery returned `already_acknowledged` with the same admitted ticket, generation and fees. Recovery-monitor invocations increased because reconciliation performs replay/validation work.

At both injected in-transaction write points, SQLite reopening rolled the store and outcome record back together. The unresolved intent remained, no admission was retained, and recovery returned `aborted_uncommitted`. No automatic repeat checking or invented Bayesian report occurred.

These are finite process-crash tests. They do not establish all hardware power-loss, filesystem or adversarial interleaving behavior, and do not validate LLM performance.

## Evidence locations

- `AUDIT.json`
- `results/v0.20.0/final_local_build_summary.json`
- `results/v0.20.0/axiom_audit_summary.json`
- `results/v0.20.0/source_scan.json`
- `results/v0.20.0/final_negative_summary.json`
- `results/v0.20.0/recovery_test_summary.json`
- `results/v0.20.0/inherited_source_match.json`
- `results/v0.20.0/recovery_demo.json`

The final archive manifest and ZIP integrity checks are separate byte-integrity evidence, not replacements for proofs or physical tests. Historical versioned results are not relabeled as current runs.
