# Real Run Checklist

## Before setup

- [ ] At least 12 GB free disk space for the isolated environment, exact checkpoint, minimal GPT-2 snapshot, caches, and audit outputs.
- [ ] NVIDIA driver operational.
- [ ] Python 3.10, 3.11, or 3.12 installed; the setup script probes `py` and common Python executables automatically.
- [ ] Git available in PowerShell.
- [ ] Network access to GitHub, PyPI, PyTorch wheels, and Hugging Face.

## After setup

- [ ] `runtime_paths.json` exists.
- [ ] upstream commit equals the source lock.
- [ ] source blob verification passes.
- [ ] checkpoint revision and full SHA-256 are recorded.
- [ ] GPT-2 revision, exact required-file list, and local tree SHA-256 are recorded.
- [ ] Asset receipt SHA-256 and transfer mode are recorded.
- [ ] `pip check` passes.
- [ ] CUDA is visible to the isolated environment.

## Smoke run

- [ ] Seal is written before model audit.
- [ ] Exact replay passes all 12 rows.
- [ ] Prompt, suffix, latent positions, and answer mask are stable.
- [ ] No out-of-memory or cache-format error occurs.

## Primary run

- [ ] Configuration file unchanged from the sealed copy.
- [ ] Covariance calibration rows are group-disjoint from audit rows.
- [ ] Donor plans cover every causal audit row once.
- [ ] Explicit CoT remains unavailable before semantic seal.
- [ ] Final semantic orbits are captured only after quotient seal.
- [ ] Complete result and environment records are retained even on failure.

## After result

- [ ] Run `verify-result`.
- [ ] Generate summary.
- [ ] Copy the complete result directory before any exploratory analysis.
- [ ] Do not relabel content specificity as algorithmic procedure specificity.
