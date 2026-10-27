# Build verification

Release candidate: `0.1.1 hotfix 2`  
Verification date: `2026-08-26`

## Passed in the build environment

- All 17 bundled Python modules compile, and all four JSON presets parse into their dataset and training configuration classes.
- Sixty-two runnable test functions passed through an offline pytest-compatible harness. Two PyTorch model-construction tests were skipped because PyTorch is not installed in this build container.
- Two independent smoke generations were byte-identical across all 12 shards: 208 total records each.
- The integrated non-neural smoke pipeline passed generation, exact validation, all three classical controls, exact/fuzzy quotient analysis, report generation, and project verification. Its evidence adjudication was correctly `INCOMPLETE` because neural execution was deliberately skipped.
- Final standard and confirmatory corpora generated and validated with zero errors, rendered-input overlap, held-out transformation leakage, or nonce-pool overlap. Standard used 20,000 canonical records plus 2,000 matched records in each calibration-control shard; confirmatory used 20,000 plus 4,000 in each control shard. Both used 1,998 complete renaming-evaluation records (666 triplets).
- A separate full-scale hard-split audit passed 10,000 held-out pairs, 10,000 held-out triples, and 9,999 renaming records with exact balance.
- Correct/scrambled training pairs and canonical/correct/scrambled evaluation triplets passed semantic, target-text, render-seed, nuisance-marker, nonce-pool, and exact model-token-multiset checks.
- Three-arm replication tests passed config/package provenance checks, per-data-seed dataset equality checks, partial-run exclusion, crossed-seed strata, and every preregistered H2 threshold direction.
- A completed-run rerun was rejected before mutation, and its `run_metadata.json` remained byte-identical.
- The final manifest rejects missing, changed, duplicate, unsafe, and unexpected files and verifies its checksum companion. Project verification checks every manifested source file.
- Fourteen PowerShell files passed static delimiter and CLI-command scans. Source scans found no local usernames, build paths, model-hub calls, or networking code in experiment execution.

## Target-machine evidence and remaining check

PowerShell, PyTorch, CUDA, and pytest are not installed in this Linux build container. On the Windows CUDA target, the preceding hotfix passed dependency, CUDA, source-manifest, generation, validation, and baseline gates, then completed one forward/backward epoch for all three central arms and the quotient analysis. Its post-training audit correctly exposed a sampled output-label mismatch: the answer-only smoke arm had 19 output rows while each replacement arm had 17.

This hotfix removes that mismatch by deriving one 21-label ontology exhaustively from the legal states of the declared worlds. Structural parity, exact label ordering, and audit-failure regression tests pass here. A complete post-fix CUDA smoke remains the target-machine check before the six confirmatory seed cells begin.

Run this from the extracted folder in the target `komorebi-full` environment:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\RUN_NEXT_OSL_TEST.ps1 -Device cuda
```

This release implements behavioral input counterfactuals, not hidden-state causal interventions. It ships no scientific result and cannot by itself establish E4, E5, general symbolic competence, awareness, or consciousness.
