# Komorebi Workspace Incubator v0.6

Read REPORT.md, RESULTS.json and checks/FAILURES.md first.

This release is an executed adaptive-development continuation, not a J-space
certificate. A phase-local learned retrieval mechanism improves native access
while original working dynamics are held fixed. A known-stress calibration
improves further but degrades some repeated and clean sequential accesses.
The analytic distributed reader is a supervised engineered control, not native
GRU evidence. Original no-wire/localization/partner-transfer gaps remain open.

## What is included

- Two unchanged v0.5 parent checkpoints, and the required unchanged runtime.
- Four main1000-update continuations and two secondary1000-update calibrations.
- One full uninterrupted replay, checkpoints, optimizer/RNG state and training logs.
- Main512-case banks,1024-case frozen new-history confirmation, message/depth tests,
  short native working-reuse tests, and no-reset sequential recall.
- The supervised distributed linear-reader control, coefficients and raw features.
- Twenty-four successor tests, independent integer scoring and exact replay audits.
- Per-command source/input hashes, actual child return codes and retained failures.

This is a278132-parameter model:171602 original parameters plus106530 copied
access-phase parameters. Both agents have independent64-dimensional states and
eight-value message wires. There is no full-state central reader in the neural
repair. The supplied retrieval-phase dispatch is architectural scaffolding.

## Verify the delivered package without retraining

From this directory, using an environment with the recorded dependencies:

    python verify_package.py
    python -m pytest -q checks
    python src/audit_results.py
    python src/audit_additional.py
    python checks/validate_computation_manifest.py checks/COMPUTATION_MANIFEST.json --root .

The audit scripts deterministically regenerate audit JSON. Use a copy of the
release to preserve the original delivery manifest. The local manifest validator
is explicitly not the full canonical Mathbox executable.

Recorded environment: Python3.13.5, PyTorch2.10.0+cpu, NumPy2.3.5. These scripts
run on CPU and do not silently move a model to a GPU. Exact cross-hardware bytes
are not guaranteed. No network access or API key is used. Only load checkpoints
whose provenance you trust; the supplied code uses torch.load(weights_only=False)
for optimizer and RNG records.

## Reproduce the main matched pair

    python src/access_repair.py inputs/v05_A_random.pt --out runs/new_A_access --arm access --seed 330601 --steps 1000 --batch 96 --lr 0.0003
    python src/access_repair.py inputs/v05_A_random.pt --out runs/new_A_joint --arm joint --seed 330601 --steps 1000 --batch 96 --lr 0.0003

For lineage B use inputs/v05_B_random.pt and seed330603. Output directories must
not already exist. --stop N and --resume support an interrupted run. Resume
reproduces computation state and tensor bytes, not necessarily pickle file bytes.
One complete uninterrupted1000-update replay matches checkpoint bytes exactly.

    python src/evaluate_access.py runs/new_A_access/checkpoint.pt --out runs/new_A_access_eval --seed 930601 --n 512

That evaluator's raw parent untrained-length flag uses24, whereas the parent
trained maximum is12. See checks/METADATA_CORRECTIONS.md. New main models use24.

## Reproduce known-stress calibration separately

    python src/calibrate_access.py runs/A_access/checkpoint.pt --out runs/new_A_calibrated --seed 340601 --steps 1000
    python src/evaluate_calibrated.py runs/new_A_calibrated/checkpoint.pt --out runs/new_A_calibrated_eval

For B use the B access checkpoint and seed340603. This phase trains on the formerly
held-out family and length48. Do not call its length48 results OOD generalization.

The exact executed command lists and process receipts are in checks/. Campaign
scripts use explicit original output names and must only be run in a clean copy.
Limit BLAS threads with OMP_NUM_THREADS=1, OPENBLAS_NUM_THREADS=1, MKL_NUM_THREADS=1.
A four-CPU-equivalent quota was used. The full prior ZIP is not duplicated; its
hash, manifest, report, required parent weights and source are retained.

## Current next target

notes/STABLE_ACCESS_NEXT_DESIGN.md is unexecuted. It targets preservation of
future access through repeated cue changes and subsequent working operations.
One-shot recovery, repeated-use stability and localized J-space are different
claims. No self-model or subjective-state inference is made here.
