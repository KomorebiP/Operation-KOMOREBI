# Komorebi Neuralese Semantic Retraction v0.3.0

Release state: **ARMED, UNSPENT, CAPACITY-GATED**.

This package contains a frozen prospective 2x2 selector-by-section factorial probe, its checkpoint-free tests, the parameter-only checkpoint preflight, the immutable lineage registry, and one newly drawn and sealed calibration/evaluation bank.

The v0.3 project itself contains **no v0.3 learned-checkpoint result**. Its production bank has not been applied to any checkpoint, and no v0.3 evaluation spend receipt or result bundle exists. The nested immutable v0.2 lineage ZIP intentionally contains historical v0.2 spent/aborted artifacts; those are provenance evidence, not v0.3 outputs.

## Current receipts

- Protocol SHA-256: `5959dd5da3a51d656a2391c52c89929ed47c57687a007372b94329a325084c50`
- Design commit SHA-256: `a9c087a49d25aca278f81a0d1c2313c5dd4e1bb9638fce7f774f8412cf3312d4`
- Fresh bank ID: `96f86194dde85e15d55f1b886707bd97f85087cd2f4c7e55ae095e4093d671bc`
- Fresh bank SHA-256: `358db4d74d8728ee88305eede415f8f351fa26d02f1e08efd3dd2ceae9dbda1c`
- Fresh bank seal SHA-256: `025e37ba4d9aba3312b138316d8054ed726e22d3d8dc19105c6c10bd0be698cf`
- Armed receipt SHA-256: `693e2b6698a0f02517f95f7b3637eb8d6d4c14d0b5837a1e11c9fdbf5bfbb272`

## Verified status

- 84/84 checkpoint-free tests pass: 29 factorial, 38 fresh-bank, 14 lifecycle, and 3 projector-semantics tests.
- The full-shape synthetic run passes with 64 calibration and 64 evaluation contexts, 8 prefixes per split, all 127 suffixes through horizon 6, and exact packed-evidence recomputation.
- The parameter-only preflight authenticates all 12 sealed checkpoints and all projector diagnostics without opening either an old evaluation bank or this production bank.
- The fresh bank regenerates exactly from its sealed root, is disjoint across calibration/evaluation splits, and excludes all registered prior-bank contexts and paths.
- The runner-side armed verification materializes the bank successfully without opening a checkpoint.

## Why execution is paused

The learned path requires at least `2,147,483,648` free bytes before physically reserving its result and commit files. The post-arm observation was `1,189,912,576` free bytes, a shortfall of `957,571,072` bytes. Therefore the learned evaluation was not started and the one-use bank remains unspent.

Do not interpret the protocol validator's `learned_execution_unlocked=true` field as a behavioral result: it means only that the frozen protocol and receipts agree. Capacity reservation, checkpoint readiness, spend publication, evaluation, evidence verification, and terminal commit have not occurred.

See `reports/RELEASE_STATUS.md` for the detailed handoff and `reports/SCIENTIFIC_BOUNDARIES.md` for the claim limits.
