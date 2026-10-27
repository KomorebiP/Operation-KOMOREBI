# Local hardware guide

## Recommended environment

- Python 3.11 or newer
- NumPy 1.24–2.x
- PyTorch 2.2 or newer for trained experiment families
- Matplotlib for plots
- Pytest for local validation

Windows launchers use the active Conda environment when `$env:CONDA_PREFIX\python.exe` exists; otherwise they use `python` from `PATH`.

## CPU execution

```toml
[runtime]
device = "cpu"
threads = 8
```

The continuous open-set family is NumPy-based and inexpensive enough for CPU development. Use it first to validate contracts, checkpoints, resume, and intervention logic.

## NVIDIA GPU execution

```toml
[runtime]
device = "cuda"
threads = 4
```

For an 8 GB laptop GPU:

- begin with one seed
- use one GPU worker
- reduce batch size before reducing scientific sequence length
- enable sweep resume
- inspect checkpoints before expanding a grid

```toml
[sweep]
parallel_workers = 8
gpu_workers = 1
resume = true
```

## Checkpoint strategy

For long local runs:

```toml
[continuous]
checkpoint_interval = 64

[run]
checkpoint_keep = 5
```

For trained families, generic optimizer/model checkpointing remains family-specific; inspect the feature contract before assuming `training.checkpoint_interval` is active.

## Determinism

Fixed code, configuration, seed, dependency versions, and numerical backend should reproduce the same logical trajectory. v0.60 includes exact staged-resume versus uninterrupted-trajectory regression tests for both the legacy continuous scaffold and the NumPy fuzzy-to-J family. Bitwise equality across arbitrary CPU, GPU, BLAS, and driver implementations is not guaranteed.
