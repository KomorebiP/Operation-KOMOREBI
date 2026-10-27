# Reproducibility Record

## Scope

This record covers Paper I v1.2.1 by Komorebi P., released 2026-09-03. It distinguishes manuscript proofs, Lean kernel checks, exact symbolic computations, finite sampled ranges, and floating-point regressions. None of the computational outputs substitutes for an unrestricted proof. The Python companion is v1.1.1 and the Lean component is v1.0.1.

## Tested environment

- OS: Ubuntu 24.04.3 LTS, Linux 6.18.35 x86_64.
- Python: CPython 3.12.13; pip 26.2.1.
- Python packages: NumPy 2.3.5, SymPy 1.14.0, Matplotlib 3.10.8, pytest 9.1.1, setuptools 84.0.0, wheel 0.48.0.
- LaTeX: latexmk 4.83; pdfTeX 1.40.25; TeX Live 2023.
- Lean: 4.34.0-rc2; Lake 5.0.0; Mathlib revision `aeb72f1e9981b6d35b426b16dca7759be3e7ba06`.

The Python direct requirements are in `code/python/requirements.in`; the complete CPython 3.12 resolution used for this run is in `code/python/requirements.lock.txt`. Lean and Mathlib are pinned by `formalization/lean/lean-toolchain` and `formalization/lean/lake-manifest.json`.

## Python commands

From the release root:

```bash
python -m venv .venv
. .venv/bin/activate
python -m pip install -r code/python/requirements.lock.txt
SOURCE_DATE_EPOCH=1788393600 MPLBACKEND=Agg python code/python/run_all.py
python -m pytest -q -W error -p no:cacheprovider --import-mode=importlib code/python/tests
python -m pip wheel code/python --no-deps --no-build-isolation -w code/python/dist
```

The Python v1.1.1 experiment command regenerates all ten figure pairs, `results/numerical_results.json`, `results/numerical_summary.csv`, and `results/run_record.json`. The run record records the manuscript release and Python companion versions in separate fields and hashes every generated numerical and figure output.

## Lean commands

From `formalization/lean/` with Elan/Lean available:

```bash
lake exe cache get
lake --wfail build
python scripts/verify_theorem_map.py
lake env lean -E warning KomorebiVerification/KernelAudit.lean
```

The Lean v1.0.1 public aggregate build completed all 8,883 jobs successfully under a warning-fatal policy. Narrow documented suppressions cover only legacy style and unused-variable lints in stable proof bodies. The standalone checker resolves all 84 unique declarations in the 35-row theorem map and requires exactly one direct `#print axioms` entry for each. The fail-closed namespace audit traverses 1,126 compiled project declarations and rejects project axioms, explicit opaque constants, unsafe declarations, `sorryAx`, and any dependency outside `propext`, `Classical.choice`, and `Quot.sound`. The audit is intentionally not imported by the public aggregate; the runners invoke it as a separate release gate.

Within the completion contract, all 32 revised named statements and three mathematical algorithm specifications are matched by imported declarations classified `Exact` or `Stronger`. This certificate-explicit scope does not include construction of the classical classification data supplied as hypotheses, a verified eigensolver, executable extraction, performance guarantees, elliptic smoothness or genus, the geometric interpretation of the discriminant, or historical-priority claims. The exact declaration map and hypotheses are recorded in `formalization/lean/VERIFICATION_REPORT.md` and the paper's claim-status ledger.

## Paper command

From `paper/`:

```bash
SOURCE_DATE_EPOCH=1788393600 latexmk -pdf -interaction=nonstopmode -halt-on-error Projector_Resolved_Seed_Calculus_I.tex
```

The final `latexmk` build resolves every citation and cross-reference to a fixed point and reports no overfull or underfull boxes.

## Determinism controls

- Main experiment RNG seed: `20260727`.
- Transfer-figure seed: `23`.
- Coordinate-transport figure seed: `91`.
- Reconstruction-test seed: `3`.
- Transport-test seed: `12`.
- Default/orbit rank tolerance: `1e-10`.
- Experiment shift-support threshold: `1e-10`.
- Experiment similarity determinant cutoff: `1e-4`.
- Figure similarity determinant cutoff: `1e-6`.
- Reconstruction assertion: `<1e-12`.
- Transport assertion: `<1e-11`.
- Shift nonzero threshold: `>1e-12`.
- PNG resolution: 220 DPI.
- Reproducible artifact epoch: `SOURCE_DATE_EPOCH=1788393600`
  (2026-09-03 00:00:00 UTC). Both top-level runners preserve an explicitly
  supplied value and otherwise export this release default.

With the fixed source-date epoch, two clean pdfTeX builds of the manuscript
were byte-identical. The numerical JSON and CSV content is deterministic in
the pinned environment.

## Release verification

The canonical checksum file is `SHA256SUMS.txt`; it excludes itself. The ZIP archive has a separate `.zip.sha256` sidecar. Verification is performed after extraction into a fresh directory before delivery.

The top-level `Run_All.ps1` and `Run_All.sh` implement that discipline by
copying the extracted release to a temporary directory and running the Python,
wheel, Lean, map, audit, and LaTeX checks only in that copy. Successful or
failed verification therefore does not rewrite any canonical release member.
