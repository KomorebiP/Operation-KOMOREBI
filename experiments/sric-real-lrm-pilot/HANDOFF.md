# Handoff

## Current state

The package is complete as an audit and preregistration artifact. The fake fixture and internal trace-engine tests pass. The real checkpoint has not been executed in the build environment.

## Clearest next command on the user's Windows machine

```powershell
Set-ExecutionPolicy -Scope Process Bypass -Force; .\Setup_External_PrOntoQA_Coconut.ps1
```

After setup finishes:

```powershell
.\Run_Real_LRM_Pilot.ps1 -StageOnly
```

Archive the generated seal, then run:

```powershell
.\Run_Real_LRM_Pilot.ps1 -RunOnly
```

## Decision after the real result

- `ADAPTER_INVALID`: repair only the adapter and issue a new adapter version.
- `LATENT_UNUSED`: preserve as a checkpoint/task obstruction; do not force semantic discovery.
- `LATENT_GENERIC`: investigate generic conditioning and answer preparation.
- `SURFACE_UNSTABLE`: move to context-indexed latent charts.
- `PROCEDURE_SPECIFIC`: begin the separately sealed endogenous semantic-witness block.
