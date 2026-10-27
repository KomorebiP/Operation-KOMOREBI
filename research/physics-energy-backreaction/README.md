# Komorebi Physics: Energy-Conserving Production

A finite-depth backreaction study. Research record dated 21 October 2026.

## Read first

**The original cosmological production benchmark is NOT repaired by this package.**
The finite dynamical model has an exact energy-conservation theorem and a tested implementation.
A separate, conditional Gaussian parameter family preserves a target density without a common
occupation rescaling. The finite model fails the attempted depth-independence test, and the
parameter family does not remove the residual background reservoir or radiative sensitivity.

Read `Energy_Conserving_Production.pdf`. It contains the assumptions, ordinary mathematical
proofs, worked parameter family, numerical tests, counterexamples, and references. The previous
570-page physics book has not been overwritten. This package contains no new Lean certificate.

## Main results

- Original arithmetic reconstructed: raw energy / available crossing energy = 2.6272875374e20.
- Inherited audit: 19 checks passed within their original scope.
- Finite quantum system: conserved mechanical-plus-mode energy; nonnegative occupations;
  energy bound and global existence at a fixed finite positive regulator.
- Independent complex-oscillator implementation agrees with the real kinetic system.
- Principal run: relative sampled energy residual 7.33950678011297e-11.
- Study: 17 configurations, including two deliberately incorrect closed-system controls.
  Eleven gates pass; the attempted physical depth-independence gate fails.
- The abundance-preserving parameter family has lambda = eta0 * epsilon^2 and
  A/mu = (A0/mu0)/sqrt(epsilon). Its nominal Gaussian efficiency epsilon is NOT
  the measured efficiency of the coupled solver.
- A fourth-mass-moment curvature diagnostic remains invariant along that family.
  It is a power-counting diagnostic, not a scheme-independent lower bound.

## Reproduce

Tested environment: Python 3.13.5, NumPy 2.3.5, SciPy 1.17.0, SymPy 1.14.0.
The Python dependencies are external and are not included. `requirements.txt` records
versions actually present in the reference runtime. Source runs are otherwise offline.

From this folder, in PowerShell:

```powershell
$env:OPENBLAS_NUM_THREADS="1"; $env:OMP_NUM_THREADS="1"; $env:MPLBACKEND="Agg"
python code/check_saved_results.py
python code/check_saved_results.py --require-physics
```

The first command should pass. The second deliberately returns **exit code 3**, because
the recorded physical-depth test fails. This distinguishes computational reproduction from
physical acceptance.

To recompute the study into its standard output folder:

```powershell
python code/energy_study.py --full
python code/make_outputs.py
```

`energy_study.py` without `--full` executes only the principal model, symbolic calculations,
and independent oscillator comparison. Do not mistake it for the 17-run study. Full runs may
take several minutes and are CPU dependent. If execution is interrupted, resume with:

```powershell
python code/energy_study.py --full --resume
```

Resume reuses a completed run only when the saved configuration matches and its array exists.
The supplied manifest should be checked before trusting existing results. A normal process exit
from `energy_study.py` means that the calculation finished, not that all scientific tests passed.
Inspect `results/final/verification.json`, or use `check_saved_results.py --require-physics`.

To rerun the inherited benchmark:

```powershell
python code/inherited_verification.py --parent-json inputs/frozen_benchmark.json --output results/baseline_rerun --figures results/baseline_rerun/figures
```

To rebuild the PDF, install an external TeX distribution providing the packages named in
`Energy_Conserving_Production.tex`, then run:

```powershell
pdflatex -interaction=nonstopmode -halt-on-error Energy_Conserving_Production.tex
pdflatex -interaction=nonstopmode -halt-on-error Energy_Conserving_Production.tex
```

No font files are bundled. The package includes final PDF figures, so TeX need not regenerate them.

## Files

`code/energy_study.py`: coupled finite model, independent representation, parameter analysis,
symbolic identities, and validation gates.

`code/inherited_verification.py`: unchanged inherited bridge audit, included for provenance and
its discrete momentum integral. Its plots are historical audit outputs, not the new study's figures.

`code/make_outputs.py`: four research figures and CSV tables generated from the recorded outputs.

`code/check_saved_results.py`: fast independent inspection of saved energy arrays and acceptance status.

`results/final/`: JSON records, CSV tables, and all 17 sampled trajectories. The `.npz` files contain
sampled background and aggregate energy histories plus final mode variables. They do not claim to
store every solver-internal stage or complete intermediate mode covariance matrices.

`results/baseline_rerun/`: inherited audit rerun. `results/*log`: execution and build records.

`PROGRESS_LEDGER_v0.1.0.md`: completed work, failed checks, assumptions, and exact restart point.

`MANIFEST.sha256`: SHA-256 hashes of the distributable files, excluding the manifest itself.

## Limitations that travel with the results

The dynamical runs use modified parameters, not the original lambda = 1 benchmark. They use a
local Minkowski approximation, finite tower depth, finite positive momentum quadrature,
instantaneous incoming vacuum, and a specified q-dependent zero-point subtraction. The derivative
of that subtraction is included in the reaction force. This is a well-defined finite Hamiltonian,
not a completed covariant renormalization of the cosmological theory.

Instantaneous mode energy includes coherent vacuum response. It is not an asymptotic dark-particle
yield. Configurations compared at the same final time need not have reached the same field position
or completed the same crossing. Depth changes the physical regulated Hamiltonian. A physically
specified finite tower need not have depth-independent dynamics, but a regulator-removal claim does.
Neither a physical depth nor such a regulator-removal result is derived here.

## Licensing

Original prose, figures, and data: CC BY 4.0. Original software: MIT.
See `LICENSE` and `LICENSES/`. External libraries and cited literature retain their own terms.

The numerical reference A sets the incoming speed; the actual speed at q = 0 is solved, not imposed. Thus the nominal Gaussian depletion parameter is not a measured dynamical efficiency.
