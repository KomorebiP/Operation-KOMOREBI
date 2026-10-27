# Reliability, Checkpoint, Resume, and Sweep Guide

## Run lifecycle

Each run maintains:

```text
resolved_config.json
feature_contract.json
run_state.json
checkpoints/latest.json
checkpoints/step_*.json
summary.json
metrics.csv
rows.csv
```

Checkpoint writes use a temporary file, `fsync`, and atomic replacement.

## Exact resume

Use:

```powershell
.\RESUME_RUN.ps1 -RunDirectory PATH_TO_RUN
```

The command reloads the run's resolved configuration, enables resume, validates the checkpoint digest, restores persistent state, and continues from the recorded step.

Changing a scientific setting causes the stable checkpoint digest to mismatch and resume is rejected. `run.resume` and `run.overwrite` themselves are excluded from the stable digest.

## Sweep recovery

The sweep ledger records stable cell IDs and terminal status. With `sweep.resume=true`, completed cells are not executed again.

Recommended local CPU settings:

```toml
[sweep]
parallel_workers = 8
resume = true
retry_failures = 1
fail_fast = false
```

Recommended single-GPU settings:

```toml
[runtime]
device = "cuda"

[sweep]
parallel_workers = 8
gpu_workers = 1
```

## Audit

```powershell
.\AUDIT_RUN.ps1 -RunDirectory PATH_TO_RUN
```

The audit checks required files, configuration/checkpoint digest correspondence, checkpoint integrity, contract presence, and consistency between summary and run-state status.
