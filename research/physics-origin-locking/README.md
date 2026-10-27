# Origin Locking and Cosmological Energy Exchange

This package contains a research supplement, explicit derivations, five reproducible figures, 29 finite dynamical configurations, and verification records. It does not replace the main Komorebi Physics monograph or establish recovery of the original cosmological benchmark.

## Start here

Read `Origin_Locking_and_Cosmological_Energy_Exchange.pdf`, then `VERIFICATION_REPORT.md` and `PROGRESS_LEDGER_v0.3.0.md`. The correction in `notes/CORRECTION_LOCKING_TARGET.md` is substantive: the original density-locked branch is **q=0**, whereas q=±4 are empty-sector tree vacua. The earlier energy cost at q=4 does not rule out locking at the origin.

The current audit reports **19 passing gates and 2 failed gates**. Failed gates are retained, not converted to passes:

1. The deliberately accelerated-expansion calculation remains strongly momentum-cutoff dependent despite fixed-cutoff quadrature convergence.
2. Highly occupied, altered-model long runs fail an absolute mode-hyperboloid check in double precision. Tightening the tolerance did not fix it. Accepted origin runs pass that same criterion.

There is no new Lean compilation. Mathematical statements are ordinary written proofs with independent symbolic checks where specified. Numerical residuals are not certified error bounds.

## Scope

The original finite tower and origin matching are the primary branch. A depth-12 double-well construction is an explicitly different theory used to test matching identities. It is not a physically selected cutoff or a repair of the old cosmological fit. Conditional transport tables freeze instantaneous occupations only as a hypothesis; they do not assert an out-state or discard the remaining scalar kinetic energy.

The expanding model follows a finite, lapse-invariant homogeneous action. Its pressure-work identity and Friedmann constraint are exact at that finite scope. Its subtraction is not completed fourth-order covariant stress-tensor renormalization. The expansion stress tests set H/A=0.02 by changing the gravitational coupling. The inherited physical short-time comparison instead uses H/A≈3.35e-25.

## Reproduce

Python 3.13.5 was used. Create a virtual environment and install `requirements.txt`. All runtime input data are included. TeX is required only for rebuilding the manuscript, not for numerical checks.

From this package root:

```bash
python code/matching.py
python code/locking.py --npz inputs/inherited_origin_trajectory.npz --json inputs/inherited_origin_trajectory.json
python code/audit.py
python code/verify.py --replay
python code/make_figures.py
```

`verify.py` audits the saved files and writes `results/verification.json`. `--replay` also reruns four recorded configurations. Report generation exits normally even when scientific gates fail. To enforce the current criteria as an acceptance command:

```bash
python code/verify.py --replay --strict
```

**Expected exit code: 3**, because the two retained gates fail. Do not interpret that exit as an execution crash or a failure to reproduce this study.

Replay additional configurations into a separate directory without overwriting evidence:

```bash
python code/replay.py --name origin_stress128 --name origin_stress128_cut32 --output replay_check
```

Any name in `results/configurations.csv` can be used. The long altered-model cases are substantially more expensive than the short references. To reproduce all configurations, pass their names individually or script over the CSV. The code rejects overwriting existing replay results.

For stable small-system performance, set `OPENBLAS_NUM_THREADS=1` and `OMP_NUM_THREADS=1` before running. In PowerShell these are `$env:OPENBLAS_NUM_THREADS="1"` and `$env:OMP_NUM_THREADS="1"`. Exact floating-point agreement across platforms is not guaranteed.

## Stored data

Each configuration has JSON parameters and an NPZ result. NPZ records contain all saved scalar diagnostic time series, final mode occupations and coherences, and 21 exact sampled full mode states for independent auditing. Crossing observables are in the JSON. Full continuously sampled mode trajectories are not claimed to be stored. See `notes/DATA_SAMPLING.md` for the noninterpolated delivery reduction. The inherited 39-crossing event data used in conditional transport are included separately and identified by source hashes.

The CSV is an index, not a replacement for the detailed verification report. `MANIFEST_SHA256.txt` identifies delivered bytes and does not certify mathematical truth.

## Build the paper

```bash
cd manuscript
pdflatex -interaction=nonstopmode -halt-on-error origin_locking.tex
pdflatex -interaction=nonstopmode -halt-on-error origin_locking.tex
```

The manuscript uses standard TeX packages including newpx, amsmath, amsthm, microtype, fancyhdr, graphicx, hyperref, and float. Fonts are not redistributed. Numerical figures are created with matplotlib, never generated illustrations.

## Licenses

Original prose and figures are CC BY 4.0. Original software is MIT. See `LICENSE`, `LICENSES/`, and `THIRD_PARTY_NOTICES.md`. Original author credit: Komorebi P. External scientific works are cited, not relicensed or reproduced in full.
