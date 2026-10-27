# Projector-Resolved Seed Calculus VIII

## Packet Algorithms and GPU Realization: Dense Operators, Block Transfer, and CUDA

**Author:** Komorebi P.

This release contains the paper, exact finite packet algorithms, reproducible CPU tests, a sanitized measured CPU/GPU benchmark corpus, derived tables, and code-generated figures.

The package distinguishes four questions:

1. how much work is removed by the mathematical representation;
2. how much faster a GPU is on the same representation;
3. whether launch fusion or graph replay improves a standard GPU path;
4. whether transfer, discovery, materialization, or compilation costs erase the gain.

A compressed output is never ranked directly against an explicit matrix output. Device-resident timings and end-to-end timings remain separate. Negative results are retained.

## Reproduce the finite analysis

```powershell
$Work = "$env:USERPROFILE\Downloads\Projector_Seed_Calculus_VIII_Release"
Set-ExecutionPolicy -Scope Process Bypass -Force
& "$Work\Run_All.ps1"
```

To deliberately update already installed dependencies:

```powershell
& "$Work\Run_All.ps1" -Update
```

The supplied benchmark corpus was measured previously on the hardware recorded in the sanitized JSON. The local reproduction script analyzes those measurements and reruns the exact finite CPU certificates. It does not silently claim that a new GPU benchmark was run on another machine.
