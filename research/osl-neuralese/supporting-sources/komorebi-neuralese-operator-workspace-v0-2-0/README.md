# Komorebi Neuralese Operator Workspace v0.2.0

V0.2 completes the learned-metric plus anonymous-composition block. It includes
the full implementation, three immutable development runs, a prospectively
frozen ten-seed primary run, five cross-seed transport pairs, all checkpoints,
and a fail-closed evidence ledger.

The primary hypothesis **failed overall**: 20 of 26 gates passed. The joint
model substantially improved held-out long-depth execution and locally
near-isometric operator geometry, but its latent norm contracted to roughly
0.0013 of its starting value at depth 128. Absolute algebraic closure and
cross-context patching also missed their thresholds.

## Main result

| Test | Joint model | Shuffled null | Terminal only |
|---|---:|---:|---:|
| D4 depth 64 | 0.8660 | 0.6078 | 0.3402 |
| D4 depth 128 | 0.6105 | 0.3871 | 0.2723 |
| C8 depth 64 | 0.7203 | 0.3078 | 0.1988 |
| P95 G-isometry defect | 0.2128 | 0.3973 | 2.3482 |
| Median G-norm ratio at depth 128 | 0.001281 | approximately 0 | unstable |

The correct composition target beat the shuffled target by 0.2582 at D4 depth
64 and 0.2234 at depth 128. Nevertheless, direct/sequential operator agreement
was only 0.6617 and the intrinsic closure residual was 0.7797, so the learned
dynamics are not an exact operator algebra.

Cross-seed affine transport reached 0.9848 versus 0.1406 for shuffled fitting
and 0.0809 for a random map. A trivial decode-to-state-label then target
re-embedding baseline reached 0.9922, so richer shared Neuralese was not
established.

Read `results/v0.2.0/INTEGRATED_FINDINGS.md` for the complete interpretation.

## What changed from v0.1.1

- Exact 60/20/20 hash-rank partitions of all 40,320 eight-state permutations
- Zero individual-operator overlap between training, development, and test
- Learned determinant-one SPD metric with bounded condition number
- Correct row-table/column-latent composition orientation
- Independently encoded anonymous composition targets
- Stop-gradient and bounded-loss anti-collapse boundary
- Adjacent-depth, singular-value, product-growth, and G-norm audits
- Cross-context patches and on-manifold controls
- Balanced nonzero-depth transport anchors, shuffled fitting, operator
  intertwining, metric pullback, and decode–re-embed baselines
- Ten primary seeds, exact grid checks, frozen code/protocol receipts, and
  bit-identical replay

## Interpretation boundary

The model receives full transition tables and has an explicit 8×8
matrix-operator channel. The exact analytic solution is table transpose plus a
one-hot state. This is a controlled positive-bias assay of stable equivariant
table execution. It is not evidence of spontaneous Neuralese, open-ended
operator discovery, language-model internals, awareness, or consciousness.

## Verify on Windows PowerShell

```powershell
$ErrorActionPreference="Stop"; $Root="$HOME\Downloads\Komorebi_Neuralese_Operator_Workspace_v0.2.0"; Set-Location $Root; python .\verify_package.py
```

## Repeat the frozen primary protocol

```powershell
$ErrorActionPreference="Stop"; $Root="$HOME\Downloads\Komorebi_Neuralese_Operator_Workspace_v0.2.0"; Set-Location $Root; $Out=Join-Path .\local_runs ("primary_"+(Get-Date -Format "yyyyMMdd_HHmmss")); python .\run_experiment.py --protocol .\protocols\V0_2_PRIMARY.json --output-dir $Out --device cpu --threads 4
```

The runner refuses a nonempty output directory. A scientific gate failure does
not erase results or convert an operationally complete run into a software
error.

## Key files

- `protocols/V0_2_PRIMARY.json`: untouched-test primary protocol
- `src/komorebi_neuralese/splits.py`: exhaustive operator partition
- `src/komorebi_neuralese/models.py`: learned metric and model arms
- `src/komorebi_neuralese/train.py`: metric and composition objectives
- `src/komorebi_neuralese/closure.py`: stability, geometry, and intervention battery
- `src/komorebi_neuralese/transport.py`: hardened transport evaluation
- `results/v0.2.0/preregistered_primary/`: complete primary record
- `EVIDENCE_LEDGER.json`: machine-readable claim status

