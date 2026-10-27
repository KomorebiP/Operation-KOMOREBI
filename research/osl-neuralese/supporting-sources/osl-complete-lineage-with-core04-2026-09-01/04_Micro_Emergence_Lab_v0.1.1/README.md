# OSL Micro Emergence Offline Lab v0.1.1

This package is a self-contained, falsification-first experiment for testing whether a small sequence model learns reusable structure from operator-governed stories. It generates its own text from finite executable worlds, computes every answer from exact state transitions, trains a compact transformer from scratch, and evaluates difficult forms of generalization separately.

The experiment runs locally after dependencies are installed. It does not download a corpus, contact a model hub, or load pretrained weights. All run scripts force the common Hugging Face offline environment flags as an additional guard.

This is an operator-learning benchmark. It is not a test of consciousness, awareness, or subjective experience.

## What is included

- Three finite worlds for algebra, provenance, and consumable resources
- Exact program execution and complete finite-state transformation signatures
- Controlled direct, narrative, dialogue, log, and passive renderers
- Separate IID validation and reported IID test shards, plus lexical, held-out pair, held-out triple, law, length, counterfactual, and matched renaming-triplet tests
- Majority, question-conditioned majority, and TF-IDF leakage controls
- A compact PyTorch transformer trained from random initialization
- A deterministic hashed-word tokenizer that preserves unseen nonce identity
- One exhaustive answer ontology derived from every legal state in the declared worlds
- Seven training arms, including matched correct- and scrambled-calibration controls
- Behavioral, algebraic, quotient, and counterfactual analyses
- Deterministic manifests, hashes, checkpoints, predictions, reports, and plain UTF-8 runner logs
- PowerShell entry points for every normal Windows workflow

The seven neural arms are:

| Arm | Signal supplied during training | What it can establish |
|---|---|---|
| `answer_only` | Story, question, and answer only | The only arm eligible for a spontaneous-emergence claim |
| `role_bind_augmented` | Answer supervision on a same-size mixture containing calibrated, episode-local nonce commands | Whether role binding can be learned without formal state or operator labels; not spontaneous emergence |
| `role_bind_scrambled` | The same retained canonical records and token-matched calibration episodes as the augmented arm, but with calibration meanings permuted | Controls for extra text, nonce exposure, and optimization volume |
| `state_supervised` | Answer plus formal final-state pressure | Whether explicit state supervision installs useful structure |
| `equivalence_regularized` | Answer plus equal-transform pressure | Whether quotient-aware pressure improves reusable equivalence |
| `operator_regularized` | Answer plus operator-law pressure | Whether algebraic pressure improves composition |
| `combined` | All implemented structural losses | The strongest engineered symbolic-induction condition |

Version 0.1.1 uses one neural architecture, a from-scratch transformer. The configuration format supports an architecture list so later models can be compared without changing the experiment layout. No GRU and no pretrained transformer are included in this release.

## The recommended next experiment

The previous standard result established engineering integrity but did not establish operator-language emergence. The strongest next test is therefore a focused, crossed-seed comparison rather than a larger single run:

- preserve the untouched `answer_only` arm;
- compare matched correct-calibration and scrambled-calibration arms at exactly the same training-record count, retaining `answer_only` as the spontaneous-emergence boundary;
- freeze one tokenizer and one formal answer ontology, then verify identical parameter shapes and initialized bytes across all three arms;
- use an identical eight-epoch budget and evaluate each final checkpoint, while retaining IID validation as a diagnostic only;
- evaluate on a separate IID test plus balanced hard splits;
- use matched canonical/correct-calibration/scrambled-calibration triplets and evaluation nonce words that never appear in optimization data;
- repeat two dataset seeds by three model seeds; and
- aggregate behavioral gates without turning a PASS into an automatic emergence claim.

From the extracted folder, the single recommended command is:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\RUN_NEXT_OSL_TEST.ps1 -Device cuda
```

It first runs package/dependency checks and one smoke test, then the six confirmatory seed cells and the replication aggregate. Each cell trains all three central arms. On an 8 GB RTX 3070 Ti Laptop GPU, allow roughly 3–7 hours and several GB of free disk space; thermals, driver behavior, and storage speed can move that estimate substantially. Interrupted or completed cells are left on disk. A rerun skips only cells whose completed metadata matches the exact current config and package manifest; aggregation also requires identical dataset hashes across model seeds sharing a data seed. Use a new `-OutputDirectory` for a revised protocol, or explicit `-Force` to regenerate the matrix.

## Requirements

- Windows 11 or Windows 10
- PowerShell 5.1 or newer
- Python 3.10 or newer
- Approximately 2 GB of free disk space for a standard run
- Several GB for the six-cell confirmatory matrix; more for the full preset
- CUDA is optional

Your existing `komorebi-full` environment is the recommended route. Its installed PyTorch CUDA build can be used directly. The lab does not use Numba, so the separate Numba and NumPy version conflict previously seen in that environment is not part of this experiment.

## Extract and enter the package

After extracting the zip into Downloads, open Anaconda PowerShell Prompt and run:

```powershell
Set-Location "$env:USERPROFILE\Downloads\OSL_Micro_Emergence_Offline_Lab_v0.1.1"
```

If Windows added another folder level while extracting, enter the inner folder containing `README.md`, `pyproject.toml`, and the `PowerShell` directory.

## Recommended setup with `komorebi-full`

Activate the environment:

```powershell
conda activate komorebi-full
```

If that environment already contains NumPy, scikit-learn, PyTorch, and matplotlib, no installation step is required for the experiment. Pytest is useful for developer tests but is not required by the runner. The wrappers run from the extracted project root, so `python -m osl_lab.cli` resolves the bundled source directly. You can remain disconnected and go straight to the recommended runner below.

Only use the setup helper when a dependency is actually missing. Without `-Wheelhouse`, pip may contact its configured package index; that setup action is separate from the offline experiment itself.

Install or confirm the project dependencies in the active environment:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\PowerShell\Setup_Environment.ps1 -Environment Current -Profile Full
```

You can target the environment without activating it first:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\PowerShell\Setup_Environment.ps1 -Environment Conda -CondaEnv komorebi-full -Profile Full
```

After the second form, activate `komorebi-full` before using scripts whose default Python command is `python`.

## Alternative isolated virtual environment

Create `.venv`, install dependencies, install this project in editable mode, and run the dependency check:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\PowerShell\Setup_Environment.ps1 -Environment Venv -Profile Full
```

You can activate it:

```powershell
& .\.venv\Scripts\Activate.ps1
```

Or leave it inactive and give each workflow its Python executable:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\PowerShell\Run_Smoke.ps1 -Python .\.venv\Scripts\python.exe -Device auto
```

The virtual environment setup may download Python packages. All experiment runs after setup are local and offline.

For a completely disconnected installation, first place compatible wheels in a local folder and use:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\PowerShell\Setup_Environment.ps1 -Environment Venv -Profile Full -Wheelhouse D:\wheelhouse
```

The wheelhouse must contain compatible wheels for all packages in `requirements.txt` and their dependencies.

## First run

Check the selected device and dependencies:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\PowerShell\Check_Dependencies.ps1 -Device auto
```

Run the complete recommended smoke-plus-confirmatory workflow:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\RUN_NEXT_OSL_TEST.ps1 -Device cuda
```

Use `-Device cuda` to require CUDA. The script will fail clearly if CUDA is unavailable. Use `-Device cpu` for reproducible CPU execution. `auto` selects CUDA when the installed PyTorch build and driver make it available, otherwise CPU.

## Main one-line PowerShell workflows

Run these from the extracted project directory after activating the chosen environment.

### Dependency check

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\PowerShell\Check_Dependencies.ps1 -Device cuda
```

### Smoke pipeline

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\PowerShell\Run_Smoke.ps1 -Device cuda
```

### Standard pipeline

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\PowerShell\Run_Standard.ps1 -Device cuda
```

### Recommended crossed-seed confirmatory pipeline

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\RUN_NEXT_OSL_TEST.ps1 -Device cuda
```

### Full pipeline

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\PowerShell\Run_Full.ps1 -Device cuda
```

### Generate and validate data without training

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\PowerShell\Generate_Only.ps1 -Preset standard
```

### Train one arm on a fresh generated dataset

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\PowerShell\Train.ps1 -Preset standard -Arm answer_only -Device cuda
```

### Train one arm on an existing dataset

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\PowerShell\Train.ps1 -Preset standard -Arm combined -Device cuda -DataDirectory .\results\generate_standard_YYYYMMDD_HHMMSS_PID
```

### Evaluate the most recent run containing data and a checkpoint

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\PowerShell\Evaluate.ps1 -Preset standard -Device cuda
```

### Evaluate a specific completed run

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\PowerShell\Evaluate.ps1 -Preset standard -Device cuda -RunDirectory .\results\standard_YYYYMMDD_HHMMSS_PID
```

If training used a separate generated dataset, specify it as well:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\PowerShell\Evaluate.ps1 -Preset standard -Device cuda -RunDirectory .\results\train_standard_answer_only_YYYYMMDD_HHMMSS_PID -DataDirectory .\results\generate_standard_YYYYMMDD_HHMMSS_PID
```

### Verify the newest run containing data and a checkpoint

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\PowerShell\Verify.ps1 -Preset standard -Device auto
```

### Resume the newest checkpoint co-located with its dataset

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\PowerShell\Resume.ps1 -Preset standard -Arm answer_only -Device cuda
```

### Resume a specific checkpoint

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\PowerShell\Resume.ps1 -Preset standard -Arm answer_only -Device cuda -Checkpoint .\results\standard_YYYYMMDD_HHMMSS_PID\experiments\transformer__answer_only\last_checkpoint.pt -DataDirectory .\results\standard_YYYYMMDD_HHMMSS_PID
```

Replace placeholder run names with the actual directory names under `results`.

## What each preset does

| Preset | Training records per arm | Ordinary hard-split target | Arms | Intended use |
|---|---:|---:|---:|---|
| Smoke | 60 | 12 | 3 | Wiring, import, and output checks only |
| Standard | 20,000 | 2,000 | 6 | One-seed broad arm comparison |
| Confirmatory | 20,000 | 2,000 | 3 × 6 seed cells | Recommended correct-versus-scrambled learned-binding replication, with answer-only boundary |
| Full | 100,000 | 10,000 | 7 | Expensive factorial run after the protocol is frozen |

Renaming evaluation is bundled in complete triplets, so standard/confirmatory use 1,998 records and full uses 9,999. Counterfactual records are also emitted as complete world-query bundles and may slightly exceed the nominal target. `run-all` loops over every architecture and arm listed in the selected configuration. In this release the architecture list contains only `transformer`. The full preset is intentionally expensive. Runtime depends heavily on GPU, driver, sequence lengths, optimization budget, and storage speed. Do not use smoke accuracy as scientific evidence.

## Output layout

Ordinary wrappers create new timestamped directories, so an earlier run is never silently replaced. The recommended confirmatory wrapper instead uses a stable resumable directory, refuses incomplete or protected cells unless `-Force` is explicit, and skips cells already marked complete. A completed run may contain:

```text
results/
  standard_YYYYMMDD_HHMMSS_PID/
    manifest.json
    dataset_manifest.json
    train.jsonl
    renaming_train.jsonl
    renaming_scrambled_train.jsonl
    iid_validation.jsonl
    iid_test.jsonl
    lexical.jsonl
    heldout_pair.jsonl
    heldout_triple.jsonl
    law.jsonl
    length.jsonl
    counterfactual.jsonl
    renaming.jsonl
    validation_report.json
    baseline_results.json
    experiments/
      transformer__answer_only/
        checkpoint.pt
        last_checkpoint.pt
        training_summary.json
        evaluation_results.json
      transformer__role_bind_augmented/
        checkpoint.pt
        last_checkpoint.pt
        training_summary.json
        evaluation_results.json
      transformer__role_bind_scrambled/
        checkpoint.pt
        last_checkpoint.pt
        training_summary.json
        evaluation_results.json
    EVIDENCE_ADJUDICATION.json
    EVIDENCE_ADJUDICATION.md
    soft_quotient_results.json
    reports/
      FINAL_REPORT.md
      SUMMARY.json
      figures/
        accuracy_overview.png
    logs/
      runner_YYYYMMDD_HHMMSS_PID.log
```

The exact set depends on the selected command. PowerShell writes plain UTF-8 logs beneath the new run directory. A `run-all` execution retains the resolved configuration, separate data/model seeds, portable environment information, source snapshots, dataset hashes, checkpoint hashes, predictions, evidence adjudication, and reports. The confirmatory wrapper additionally creates `aggregate/REPLICATION_SUMMARY.json` and `aggregate/REPLICATION_REPORT.md`.

Use `-OutputDirectory` to choose an exact destination. Existing material is protected unless `-Force` is supplied to a command that supports regeneration.

## Direct CLI

The PowerShell scripts are thin wrappers. The equivalent interface is:

```powershell
python -m osl_lab.cli doctor --require-neural --device auto --output-dir .\results\doctor_manual
python -m osl_lab.cli generate --config .\configs\standard.json --output-dir .\results\data_manual
python -m osl_lab.cli validate --config .\configs\standard.json --data-dir .\results\data_manual --output-dir .\results\data_manual
python -m osl_lab.cli baselines --config .\configs\standard.json --data-dir .\results\data_manual --output-dir .\results\baseline_manual
python -m osl_lab.cli train --config .\configs\standard.json --data-dir .\results\data_manual --output-dir .\results\train_manual --device cuda --arm answer_only
python -m osl_lab.cli evaluate --config .\configs\standard.json --data-dir .\results\data_manual --checkpoint .\results\train_manual\checkpoint.pt --output-dir .\results\eval_manual --device cuda
python -m osl_lab.cli quotient --config .\configs\standard.json --data-dir .\results\data_manual --checkpoint .\results\train_manual\checkpoint.pt --output-dir .\results\eval_manual --device cuda
python -m osl_lab.cli report --config .\configs\standard.json --data-dir .\results\data_manual --checkpoint .\results\train_manual\checkpoint.pt --output-dir .\results\eval_manual --device cuda
python -m osl_lab.cli verify --config .\configs\standard.json --data-dir .\results\data_manual --checkpoint .\results\train_manual\checkpoint.pt --output-dir .\results\verify_manual --device auto
python -m osl_lab.cli run-all --preset standard --config .\configs\standard.json --device cuda --output-dir .\results\standard_manual
```

Use the wrappers for normal work because they resolve paths from their own location, set offline guards, create unique output folders, and retain logs.

## Scientific order of operations

1. Verify the frozen package and run smoke.
2. Never report `iid_validation` as test evidence; the confirmatory preset records it diagnostically and evaluates fixed final checkpoints, while broader presets may use it for best-checkpoint selection.
3. Fit frozen majority and TF-IDF controls from the canonical training shard.
4. Run untouched answer-only, matched scrambled-calibration, and matched correct-calibration arms with a shared tokenizer, verified common initialization, fixed budget, and final checkpoints.
5. Evaluate balanced hard splits, matched renaming triplets, calibration-content use, and counterfactual specificity.
6. Repeat the crossed seed matrix and inspect the aggregate, exclusions, and gate pass rates.
7. Treat `role_bind_augmented - role_bind_scrambled` as the primary learned-binding contrast; use answer-only only as the spontaneous-emergence boundary.
8. Inspect failures and revise the theory only after the registered comparison is complete.

The answer-only arm must pass held-out composition, renaming, and causal counterfactual tests before it can count as evidence for spontaneous operator-symbolic induction. High IID accuracy or a clean latent plot is insufficient.

## Configuration

The JSON presets have seven main sections:

- `runtime` controls deterministic local execution and device defaults
- `dataset` matches the exact generator configuration
- `baselines` controls lexical leakage checks
- `training` defines the arm matrix, optimizer, transformer, and loss weights
- `evaluation` defines saved predictions, descriptive bootstrap uncertainty, and behavioral gates
- `replication` freezes the crossed seeds and confirmatory cells
- `quotient` and `report` define structural analysis and output generation

Copy a preset to a new JSON file before changing scientific settings. Preserve the original frozen configurations for comparisons.

## Troubleshooting

If `python` points to the wrong environment, activate `komorebi-full` again or pass an explicit executable with `-Python`.

If CUDA is not detected, run the dependency check with `-Device cuda`. A forced CUDA check fails rather than quietly changing the experiment to CPU. Confirm `nvidia-smi` and `python -c "import torch; print(torch.cuda.is_available())"` in the same environment.

If an 8 GB GPU reports CUDA out of memory, copy the chosen JSON preset and reduce `training.batch_size` before starting a fresh run. Start with 24 for standard or 16 for full; lower it again if necessary. Keep that copied configuration identical across arms and record the change. The lab never silently falls back from a requested CUDA device.

If PowerShell blocks a script, use the provided `powershell -NoProfile -ExecutionPolicy Bypass -File ...` form. This changes policy only for that child process.

If a run stops, keep the run directory. Use `Resume.ps1` with its arm, checkpoint, and data directory. Automatic lookup selects a checkpoint for the requested arm; resume rejects an arm mismatch or, for v0.1.1 format-4 checkpoints, a different ordered effective corpus. It writes into a new directory and preserves the source checkpoint.

If TF-IDF is skipped, install the full requirements. Minimal requirements support generation, validation, exact semantics, and classical baselines but omit neural training and figures.

## Documentation

- `docs/DATASET_SPEC.md` defines worlds, records, renderers, splits, and integrity rules.
- `docs/EXPERIMENT_PROTOCOL.md` defines the preregistered execution and comparison protocol.
- `docs/RESULT_INTERPRETATION.md` defines evidence levels and permitted claims.
- `docs/THEORY_BRIDGE.md` gives the mathematical quotient and soft-intertwiner foundation.
- `docs/NEXT_TEST_DECISION_MAP.md` maps each confirmatory outcome to the next theoretical move.

## License

The code and original documentation are provided under the MIT License. See `LICENSE.txt`.
