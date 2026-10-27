# PowerShell one-liners

## Complete local verification

```powershell
Set-Location "C:\path\to\RRCT_v0.60.0_dev1_PERSISTENT_FUZZY_JSPACE_BRIDGE"; .\RUN_V060_LOCAL_CHECKS.ps1
```

## Persistent fuzzy-to-J bridge

```powershell
.\RUN_FUZZY_JSPACE.ps1
```

## J-space rank/sparsity sweep

```powershell
.\RUN_SWEEP.ps1 -Config .\sweeps\07_jspace_rank_sparsity_frontier.toml
```

## J-space intervention factorial

```powershell
.\RUN_SWEEP.ps1 -Config .\sweeps\08_jspace_intervention_ladder.toml
```

## Existing local transformer probe

```powershell
.\RUN_LOCAL_JSPACE_PROBE.ps1 -Model C:\models\small-local-causal-lm -Prompts .\my_prompts.jsonl -Output .\runs\local_jspace_probe.json -TargetTokenId 123
```

## Legacy oracle-assisted continuous scaffold

```powershell
.\RUN_CONTINUOUS.ps1 -Set "continuous.steps=4096","continuous.checkpoint_interval=64","run.name=continuous_gpu_trial"
```

This family now emits an explicit evaluator-truth-access warning; use it for engineering regression, not evaluator-blind repair evidence.

## Resume

```powershell
.\RESUME_RUN.ps1 -RunDirectory .\runs\continuous_gpu_trial_seed590201
```

## Audit

```powershell
.\AUDIT_RUN.ps1 -RunDirectory .\runs\continuous_gpu_trial_seed590201
```

## Freeze and run

```powershell
.\FREEZE_CONFIG.ps1 -Config .\configs\12_continuous_open_set_runtime.toml -Output .\validation\continuous_freeze.json; .\VERIFY_FREEZE.ps1 -Freeze .\validation\continuous_freeze.json; .\RUN_FROZEN.ps1 -Freeze .\validation\continuous_freeze.json
```

## Resumable parallel sweep

```powershell
.\RUN_SWEEP.ps1 -Config .\sweeps\05_continuous_packet_repair_grid.toml -Set "sweep.parallel_workers=8","sweep.resume=true"
```

## GPU nested training

```powershell
.\RUN_CONFIG.ps1 -Config .\configs\11_gpu_large_nested.toml -Set "runtime.device=cuda","training.steps=2400"
```
