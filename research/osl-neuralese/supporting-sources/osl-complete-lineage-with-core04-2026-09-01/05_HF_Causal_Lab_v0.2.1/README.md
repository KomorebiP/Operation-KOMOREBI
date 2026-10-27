# OSL Hugging Face causal test v0.2.1

This package tests whether generated operator-world sentences train a randomly initialized Hugging Face transformer to acquire a reusable operator-relevant representation.

It includes an executable semantic generator, balanced query construction, matched supervision arms, structural holdouts, episodic operator renaming, lexical and random-feature controls, formal-state geometry, nuisance orbits, and a calibrated causal intervention test.

Version 0.2.1 repairs the CUDA mixed-precision failure in the operator-regularized arm and adds safe recovery from completed v0.2.0 checkpoints. It does not change the experimental objectives, losses, holdouts, or frozen decision gates.

## Resume the interrupted v0.2.0 full run

The interrupted run saved the first 12 completed checkpoints. After extracting this hotfix over the existing package directory, resume the same output directory:

```powershell
$d="$env:USERPROFILE\Downloads\OSL_HF_v020\osl_hf_causal_v0_2"; $o="$d\results_full_20260826_130233"; & "$d\Run_OSL_HF_Test.ps1" -Profile full -Python "$env:CONDA_PREFIX\python.exe" -Output $o -SkipInstall -Resume
```

Resume mode verifies the original frozen configuration, generator seed, protocol hash, regenerated vocabulary, dataset audit, model structure, and every checkpoint before continuing. It reloads completed models, reruns their evaluations, and trains only missing checkpoints.

The original v0.2.0 checkpoints do not contain epoch histories. Those histories are marked unavailable rather than reconstructed. The final metrics, geometry, nuisance-orbit, and causal audits are recomputed from the saved weights.

## Recommended Windows run

Use a separate Python 3.12 environment. If your current environment already has CUDA-enabled PyTorch, activate it and run:

```powershell
powershell -ExecutionPolicy Bypass -File .\Run_OSL_HF_Test.ps1 -Profile full
```

For a shorter engineering run:

```powershell
powershell -ExecutionPolicy Bypass -File .\Run_OSL_HF_Test.ps1 -Profile pilot
```

For a one-minute functionality check:

```powershell
powershell -ExecutionPolicy Bypass -File .\Run_OSL_HF_Test.ps1 -Profile smoke
```

The runner preserves an existing PyTorch installation. It installs missing requirements, prints CUDA availability, runs source tests including an operator-transition mixed-precision backward pass, executes the experiment, verifies all result checksums, and creates:

```text
RETURN_THIS_OSL_HF_RESULTS.zip
```

Bring that compact ZIP back to ChatGPT. Checkpoints remain in the full local results folder and are intentionally excluded from the return ZIP.

## Profiles

| Profile | Model | Training stories | Seeds | Purpose |
|---|---:|---:|---:|---|
| `smoke` | 1 layer, 64 hidden | 200 | 1 | Functionality only |
| `pilot` | 2 layers, 96 hidden | 3,000 | 2 | Engineering evidence |
| `full` | 4 layers, 192 hidden | 12,000 | 4 | Recommended RTX 3070 Ti study |
| `confirmatory` | 4 layers, 256 hidden | 30,000 | 5 | Larger frozen replication |

The full and confirmatory profiles train four arms. The operator-regularized arm performs additional prefix encodings and takes longer than the other arms.

## Customization

The runner accepts extra experiment arguments:

```powershell
powershell -ExecutionPolicy Bypass -File .\Run_OSL_HF_Test.ps1 -Profile full -ExtraArgs @("--batch-size","32","--arms","answer_only,state_supervised,equivalence")
```

Useful switches include:

```text
--n-train N
--n-val N
--n-eval N
--epochs N
--batch-size N
--layers N
--hidden N
--heads N
--intermediate N
--seeds 11,29,47
--arms answer_only,state_supervised,equivalence,operator_regularized
--causal-calibration N
--causal-test N
--permutations N
--random-directions N
--no-baselines
--no-geometry
--no-causal
--no-checkpoints
--resume
```

Dataset sizes must be divisible by five because every provenance class is exactly balanced.

## Clean environment option

```powershell
conda create -n osl-transformers python=3.12 -y; conda activate osl-transformers; powershell -ExecutionPolicy Bypass -File .\Run_OSL_HF_Test.ps1 -Profile full
```

If PyTorch is absent and you want a specific CUDA wheel source, pass it explicitly:

```powershell
powershell -ExecutionPolicy Bypass -File .\Run_OSL_HF_Test.ps1 -Profile full -TorchIndexUrl "https://download.pytorch.org/whl/cu128"
```

Use the CUDA wheel index appropriate for your installed NVIDIA driver. If CUDA-enabled PyTorch is already present, omit this parameter.

## Interpretation

The package deliberately uses random initialization for the primary claim. Passing behavior alone supports systematic task learning. Strong evidence for an operator abstraction requires held-out composition, same-answer formal triplets, and selective causal intervention to pass together against lexical and random-feature controls.

This experiment concerns a bounded synthetic algebra. It does not test awareness or consciousness.

The seeded CUDA configuration uses PyTorch's warn-only deterministic mode. If PyTorch reports a nondeterministic attention kernel, treat exact bit-for-bit reproducibility as best-effort. Logistic-regression convergence warnings should also be retained when judging the shortcut baselines. A later strict confirmatory run should start cleanly from v0.2.1 rather than from recovered checkpoints.
