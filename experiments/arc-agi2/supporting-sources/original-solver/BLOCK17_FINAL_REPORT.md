# Komorebi PR-LASM — Block 17 final report

Author: Komorebi P.

The preregistered `typed_recent` policy scored **790/1,076 exact outputs (73.42%)** and **734/1,000 whole tasks (73.4%)**. These are unfiltered predictions from the integrated executable solver on exposed public training data.

The preserved G47 retrospective frontier remains **864/1,076 outputs and 804/1,000 tasks**. It was never used as a prediction fallback. No hidden or untouched evaluation set was opened.

## Frozen policy comparison

| Policy | Pass@1 outputs | Pass@2 outputs | Whole tasks | Gains / losses vs live base |
|---|---:|---:|---:|---:|
| base | 267 | 273 | 243 | +0 / −0 |
| recent_control | 267 | 790 | 734 | +518 / −1 |
| typed_agreement | 267 | 779 | 723 | +507 / −1 |
| typed_joint | 663 | 724 | 674 | +534 / −83 |
| typed_recent (primary) | 267 | 790 | 734 | +518 / −1 |
| typed_supported | 267 | 846 | 786 | +574 / −1 |

The primary policy changes 851 output positions relative to the live base. Of those, 196 remain wrong. All are retained in the submission and audit. Its first-attempt changes relative to the live base: 0.

## What the experiment established

The runtime now has a complete path from demonstration grids and test inputs through the live core/Block 2/Block 4 solver, seven native compiler stages for Blocks 6–12, 21 Block 13 entrants, and 48 Block 14–15 entrants. Block 5 supplies the shared execution IR. The dispatcher consumes candidate evidence and live predictions; it does not consult a task-specific success mask.

The combined census contains 12391 candidates across 971 tasks. The candidate-plus-live-base oracle diagnostic contains a correct answer at 868 output positions. The primary policy leaves 78 of those available exact outputs unselected. That diagnostic uses labels after the freeze; it is not a runtime score.

Relative to G47, the primary runtime misses 78 preserved exact outputs and produces 4 exact outputs outside that frontier. Those outside-frontier cases are listed in the evaluation JSON; they have not been silently promoted.

Excluding live-base fallback credit, selected candidates are correct on 520/960 activated output positions. There are 520 exact candidate attempts out of 960 selected candidate attempts, and 410 activated tasks receive no correct candidate. These counts preserve wrong activations.

## Typed repair result

The scoped multiscale codebook veto emitted 1 witness records. Compared with the otherwise identical no-veto control, it produced 0 gains, 0 losses, and 0 changed outputs that remained wrong.

A repair abstention alone does not suppress its ancestor. The veto requires a checked noninjective structural codebook and names the colliding learned keys and program hash. The explicit binary symmetry predicate remains outside its scope. This repair was motivated by a previously exposed failure, so its development is score-seeded.

The additional trace-support control changes the primary result by +56 exact gains and −0 losses. It was added before scoring and does not replace the preregistered primary.

That control scores **846/1,076 outputs (78.62%) and 786/1,000 whole tasks**. It rejects feature-induction candidates whose evidence reports unseen test keys. Its candidate-only accuracy is 576/794 (72.54%); 205 activated tasks still receive no correct selected candidate. Relative to the live base it gains 574 exact outputs and loses 1. This stronger control remains an ablation result, not a retroactive change to the primary policy.

The trace-support control leaves 22 available correct outputs unselected. The candidate-plus-base oracle omits 0 G47 exact outputs. Its higher diagnostic coverage identifies remaining selection failures; it does not provide a label-free way to choose those answers.

## Compute and verification limits

The complete older-bank run is fresh. The unchanged 48-entrant modern bank reuses Block 16’s full live replay census after source, challenge and per-task binding checks. The release also supplies `engine.py scan --include-new` to recompute every bank for arbitrary challenge files. Reusing that census is disclosed; it is not claimed as a new 48,000-call scan.

Elapsed time from the initial start to census completion was approximately 7.89 hours, including interrupted periods. Active scanning used eight workers. Both core entry points use deterministic nominal tier 2.0, including 2,200 composition expansions. Feature induction uses conjunction depth 2, beam width 32 and at most 32 emitted programs. Other compiler limits are inherited. Several higher-budget pre-score attempts were stopped during profiling. Exact task-local feature caching was verified before the budget reductions; the reduced budgets are separately documented and are not asserted to reproduce deeper-search candidates.

The full run recorded 243 failed compiler receipts. They are exposed in the evaluation JSON and fail closed. Verification tiers differ: {'native_compiler_demo_fit': 261, 'not_supplied': 11633, 'verified': 497}. Modern entrants replay serialized programs; earlier interfaces provide native exact-fit executions or recorded training executions. A shared interface does not upgrade their evidence by assertion.

Validation passed 13/13 tests, source authentication, byte-identical fresh-process dispatch, and task-ID/corpus-order invariance. The runtime Python literal-ID scan found 0 matches. Exact feature-cache equivalence was checked against the archived reference candidates. These checks establish the stated implementation properties, not unseen generalization.

Fresh full-bank compiler replay also matched all 3 saved task samples, covering 56 candidates and 231 interface calls. Those records were checked against the completed census. This is sampled compiler replay, separate from the complete fresh dispatch check.

An initial process-stop request did not stop all earlier workers. The execution runner subsequently terminated them; incompatible checkpoints were rejected by source hashes and separated. A later restart also rejected stale checkpoints. The final run uses a separate output path. No such checkpoint entered its completed census.

The final run was later resumed after its worker processes ended between conversation turns. All 336 completed checkpoint records were retained and authenticated under the unchanged code and budget before further compilation. The recorded elapsed time includes this interruption.

At 574 completed records, the scan switched from forked workers to fresh spawned workers through `run_scan.py`. This avoids inheriting the large graph of loaded checkpoints. The frozen engine, policies and search budgets stayed unchanged. Before the switch, the spawned-worker run reproduced the complete three-task sample census byte for byte. The launcher and this comparison have separate authenticated receipts.

Near completion, the execution service disconnected twice. The first recovery preserved live workers and 997 completed records. After the second disconnect, the worker processes had ended; 998 completed records survived and only the remaining two tasks were restarted with unchanged source and budgets. These interruptions are recorded separately and included in elapsed time.

Writing the combined evidence initially exceeded the workspace disk limit, before policy predictions were frozen or scored. The large censuses now use lossless gzip storage. The complete older census passed a byte-exact compression/decompression check, and the storage helpers are authenticated in the prediction freeze. Working records were reclaimed only after their archived bytes were verified. Compiler code, budgets and selection policies did not change during this storage repair.

Obsolete working copies were restored during background synchronization, so closing work moved to a clean directory. All 369 retained files were checked byte for byte, the complete task-record archive was verified, and source authentication passed before the obsolete working directory was retired.

## Geometry-domain repair

The separate micro-schema repair adds dimension preconditions to three operators that paint or recolor in the input frame. Its paired all-corpus check removes 237 original compiler exceptions with zero remaining exceptions and zero changes to candidates from successful original calls. The repaired compiler still activates on the same 26 tasks and emits no new activations. This is a robustness improvement with no coverage gain. Both its primary-parent and trace-support-parent submissions are frozen and evaluated separately under `repair_results/`.

## Reproduction

See `README.md` and `PROTOCOL.md` for commands, budgets and policy definitions. The machine-readable evaluation retains every gain, loss, wrong change, veto witness and unselected exact candidate. The primary submission is `results/submission.json`. The complete release contains the source bank, training challenges, separate evaluation evidence, frozen predictions and validation artifacts.

G47 reference SHA-256: `2f92e4e7b5c790b78b349838bbb6f114f22ec8be80801691175838ac46a67b4f`

Final prediction code hash: `9864bba49f8c395e07ddf3126a1b73bfaffe37ff14d86cdec74fae063120e8a0`

Census content hash: `d2b8dbe90f19a608537282dcbd55da0866fbf9cb408d395e0df72aaf298a8bec`
