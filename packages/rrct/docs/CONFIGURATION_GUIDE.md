# Configuration guide

Configurations use TOML or JSON. Omitted values inherit from `rrct_lab.config.DEFAULT_CONFIG`.

## Override syntax

```powershell
.\RUN_CONFIG.ps1 -Config .\configs\12_continuous_open_set_runtime.toml -Set "continuous.steps=4096","workspace.max_packets=12"
```

Arrays and objects use JSON syntax:

```powershell
-Set 'run.tags=["gpu","open-set"]'
```

## Sections

| Section | Purpose |
|---|---|
| `run` | naming, seeds, output, strict contracts, resume, checkpoint retention |
| `runtime` | device, threads, determinism, time and memory limits |
| `experiment` | family, task sizes, agents, event probabilities |
| `features` | mechanism on/off switches |
| `workspace` | dimensions, packets, hierarchy, fuzzy memberships, formation costs |
| `memory` | capacity, compression, provenance thresholds |
| `metacognition` | evidence budgets, uncertainty, probing, abstention |
| `planner` | horizon, risk, authorization |
| `interaction` | bandwidth, rounds, delays, partners and overlap |
| `continuous` | longitudinal event, packet, repair, checkpoint, and resume settings |
| `jspace` | residual width, Jacobian rank, sparse access, moving-frame, event, learning, baseline, and checkpoint settings |
| `training` | optimizer and trainable-family settings |
| `interventions` | causal cuts, shuffles, hardening, and patches |
| `evaluation` | metrics and output settings |
| `sweep` | grid, concurrency, resume, retries, and state |
| `safety` | hard offline boundaries |

## Strict behavior

Nondefault unsupported settings are not silently ignored in strict mode. Use:

```text
python -m rrct_lab contract CONFIG.toml
```

A setting listed as `partial` may be retained for compatibility but is not fully universal. This status is also written into every run bundle.

## Synthetic J-space rank boundary

`persistent_fuzzy_j_workspace` has four independent terminal consumers. Its analytic Jacobian therefore has at most rank four, and strict validation rejects `jspace.frame_rank > 4` rather than silently truncating the request. The optional transformer adapter is a separate measurement path and is not governed by that synthetic four-head bound.
