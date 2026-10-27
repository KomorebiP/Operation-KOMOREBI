# Generic Freeze and Holdout Guide

Create a freeze:

```powershell
.\FREEZE_CONFIG.ps1 -Config .\configs\12_continuous_open_set_runtime.toml -Output .\validation\MY_FREEZE.json
```

The freeze records:

- complete resolved configuration
- strict feature contract
- configuration digest
- stable checkpoint digest
- source/package file hashes
- seed policy

Verify and execute:

```powershell
.\RUN_FROZEN.ps1 -Freeze .\validation\MY_FREEZE.json
```

A frozen run is rejected if a bound source file or configuration digest changes.

This generic mechanism is suitable for local preregistration, but a publication-grade experiment should additionally predeclare endpoints, thresholds, exclusion rules, baseline definitions, and holdout seed-selection policy in a human-readable protocol.
