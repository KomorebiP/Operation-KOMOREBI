# Block 24 Handoff

## Objective

Execute a source-locked causal-semantic audit of the public multimode GPT-2 Coconut PrOntoQA checkpoint without changing the frozen v0.3.0 scientific gates after result access. Package v0.3.2 hardens setup and terminal-result reporting only.

## Recommended first command

```powershell
.\Setup_External_PrOntoQA_Coconut.ps1
```

If the local Xet transfer fails:

```powershell
.\Setup_External_PrOntoQA_Coconut.ps1 -DisableXet
```

Then:

```powershell
.\Run_Real_LRM_Pilot.ps1 -Profile smoke -Device cuda
```

The smoke run is an adapter and replay qualification. It has semantic escalation disabled.

## Advancement rule

Proceed to `primary` only when:

- source verification passes;
- the checkpoint and base-model hashes are recorded;
- exact replay is below tolerance;
- no cache or token-position discrepancy is observed;
- GPU memory is stable.

## Scientific rule

Do not alter `configs/prontoqa_multimode_coconut_gpt2.json` after staging. If the primary result is negative, preserve it. A new hypothesis requires a new version and seal.

## Returned files to preserve

- `external_runtime/environment.json`
- `external_runtime/runtime_paths.json`
- `frozen/real_primary_preaudit_seal.json`
- donor plans and experiment plan beside the seal
- `results/real_primary_block24.json`
- `results/real_primary_summary.md`
- `results/capture_cache/` if present

## Current package evidence

The engineered positive control passed. The external model has not been executed. No real-model conclusion should be inferred from the fixture.
