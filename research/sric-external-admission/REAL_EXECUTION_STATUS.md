# Real Execution Status

## Canonical status

`EXTERNAL_EXECUTION_NOT_RUN`

The build environment used for package v0.3.2 reported:

- CPU-only PyTorch available;
- CUDA unavailable;
- Transformers unavailable;
- pinned upstream checkout absent;
- checkpoint absent;
- public dataset absent;
- direct large-object retrieval through the container's external Xet transfer path unavailable.

No attempt was made to substitute a different model or fabricate external metrics. The source lock was corrected and hardened around the public raw file `checkpoint_37`, but the file was not executed. The external checkpoint remains an open empirical test.

## What was executed

- engineered fixture generation;
- engineered pre-audit sealing;
- causal and semantic pipeline on the fixture;
- automated test suite;
- source-lock unit tests;
- recurrence parity fixture;
- chronology and split-isolation tests;
- independent recomputation of fixture means and semantic-basis properties;
- package closure and manifest verification;
- exact revision-pinned asset-plan and minimal-base-snapshot tests.

## What must happen on the user's machine

1. Run `Setup_External_PrOntoQA_Coconut.ps1`.
2. Run the smoke profile.
3. Inspect replay and source verification.
4. Run the primary profile without modifying the frozen config.
5. Preserve the complete `frozen`, `results`, `capture_cache`, and environment records.

## Failure policy

The first real status is the result. An adapter failure permits an adapter-only revision because no semantic claim is yet admissible. Any scientific threshold revision requires a new protocol and new final support.
