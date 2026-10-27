# OSL Hugging Face Operand-Slot Lab v0.3.1

This offline package tests whether sentence training produces reusable operator-like structure in a small executable provenance world. It is the direct successor to v0.2.0.

The v0.2 full run established a useful boundary:

- answer-only training learned partial structure but failed the held `TELL -> INFER` motif and combined OOD tests
- explicit state and equivalence supervision helped substantially
- the old operator-only affine transition did not improve behavior
- its causal assay had zero eligible examples
- random-transformer CKA exceeded trained CKA, invalidating CKA as standalone emergence evidence

v0.3 changes the mechanism that failed. It does not change the negative v0.2 result.

v0.3.1 is a packaging-only hotfix. It moves the PowerShell transcript outside
the immutable source tree and allows the package verifier to ignore only the
known runtime artifacts from earlier runs. The model, datasets, frozen gates,
and experiment logic are unchanged from v0.3.0.

## What is new

- A genuine 24-cell latent workspace: four agents by six facts
- Each slot cross-attends to the story tokens
- Complete event operands are retained at every sampled transition
- Five causal families: observe, tell, imagine, infer, and authorize
- A learned write locator predicts which slot an event changes
- The transition reads the semantic source slot for `TELL` and `INFER`
- Soft free-write training and hard free-write evaluation
- Exact executable prefix and one-step-next state targets
- Separate in-support and OOD causal banks
- `NOT_EVALUABLE` instead of zero when endpoint capacity is insufficient
- All 23 untouched cells are checked after an intervention
- Random-direction, sign-reversal, and shuffled-operand controls
- Strict deterministic eager/math attention by default
- Convergent ridge shortcut baselines
- Source-exact resume and checkpoint identity hashes
- Exact-coverage package and result manifests

## Four matched arms

| Arm | Training signal |
|---|---|
| `answer_only` | Six query answers only |
| `state_supervised` | Query answers plus complete executable state |
| `equivalence` | State supervision plus equivalent-path contrastive loss |
| `slot_operator` | Equivalence supervision plus operand-conditioned free-write transition loss |

The first arm is the emergence test. The final arm is explicitly scaffolded and must not be described as spontaneous emergence.

## Recommended Windows commands

Run these from PowerShell. The launcher automatically uses the active Conda environment when available.

### 1. Smoke test

```powershell
$z=Get-ChildItem "$env:USERPROFILE\Downloads\OSL_HuggingFace_Operand_Slot_Lab_v0.3.1*.zip" | Sort-Object LastWriteTime -Descending | Select-Object -First 1; if (-not $z) { throw "v0.3.1 ZIP not found in Downloads" }; $d=Join-Path "$env:USERPROFILE\Downloads" ("OSL_HF_v031_" + (Get-Date -Format "yyyyMMdd_HHmmss")); Expand-Archive -LiteralPath $z.FullName -DestinationPath $d -Force; & "$d\osl_hf_slot_causal_v0_3\Run_OSL_HF_Test.ps1" -Profile smoke -Python "$env:CONDA_PREFIX\python.exe" -Device cuda
```

### 2. Full experiment

Run this in the same PowerShell window; `$d` was set by the smoke command.

```powershell
& "$d\osl_hf_slot_causal_v0_3\Run_OSL_HF_Test.ps1" -Profile full -Python "$env:CONDA_PREFIX\python.exe" -Device cuda -SkipInstall
```

### 3. Resume an interrupted run

Replace the result directory with the exact path printed by the failed run.

```powershell
& "$d\osl_hf_slot_causal_v0_3\Run_OSL_HF_Test.ps1" -Profile full -Python "$env:CONDA_PREFIX\python.exe" -Device cuda -SkipInstall -Resume -Output "C:\path\to\results_full_YYYYMMDD_HHMMSS"
```

### 4. Confirmatory replication

The confirmatory profile uses a disjoint generator seed and disjoint model seeds.

```powershell
& "$d\osl_hf_slot_causal_v0_3\Run_OSL_HF_Test.ps1" -Profile confirmatory -Python "$env:CONDA_PREFIX\python.exe" -Device cuda -SkipInstall
```

## Output to return

When the run finishes, return:

```text
RETURN_THIS_OSL_HF_RESULTS.zip
```

The compact return ZIP contains metrics, audits, causal cases, figures, configuration, frozen hashes, and the final adjudication. Full model checkpoints stay in the local results directory.

If the launcher fails, return the generated:

```text
FAILED_OSL_HF_V03_*.zip
```

It contains the transcript and any available freeze or dataset audit.

## Profiles

| Profile | Train | Eval per split | Epochs | Seeds | Model |
|---|---:|---:|---:|---:|---|
| smoke | 200 | 50 | 1 | 1 | 1 layer, 64 hidden |
| pilot | 3,000 | 500 | 6 | 2 | 2 layers, 96 hidden |
| full | 12,000 | 2,000 | 10 | 4 | 4 layers, 192 hidden |
| confirmatory | 30,000 | 3,000 | 12 | 5 | 4 layers, 256 hidden |

The full and confirmatory profiles require CUDA by default. `-AllowCPUFull` exists only for an intentional long CPU run.

## Hardware and software

The package targets the user's tested environment:

- Windows 11
- NVIDIA RTX 3070 Ti Laptop GPU, 8 GB
- Python 3.13
- PyTorch 2.12.1+cu126
- Transformers 5.16.1
- scikit-learn 1.9.0

The launcher preserves an existing PyTorch installation. It installs PyTorch only when the import is missing, and installs the remaining pinned dependencies from `requirements.txt`.

## Scientific interpretation

The package distinguishes:

1. behavioral composition
2. formal path equivalence
3. endpoint capacity
4. oracle-addressed slot manipulability
5. learned write localization
6. learned operand-conditioned transition
7. transfer to held syntax and longer compositions

Passing only the oracle-addressed intervention shows that a semantic state is manipulable once its address is supplied. Passing the learned locator and transition shows that the scaffolded operator module learned both where and what to write. Only the answer-only arm bears on spontaneous emergence.

The experiment concerns a bounded synthetic reasoning system. It is not a test of awareness or consciousness.

## Package verification

Verification requires only Python's standard library:

```powershell
& ".\VERIFY_PACKAGE.ps1" -Python "$env:CONDA_PREFIX\python.exe"
```

The smoke test then checks executable semantics, all causal families, workspace dimensions, strict local-write invariance, mixed-precision gradients, and learned-locator gradients.
