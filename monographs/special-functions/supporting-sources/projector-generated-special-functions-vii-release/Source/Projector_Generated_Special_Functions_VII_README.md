# Projector-Generated Special Functions VII

## SU(1,1) Racah Packet Recoupling, Casimir Multiplicity Spaces, Pentagon Coherence, and Bistochastic Quantum Kernels

Author: Komorebi P.

This package contains the seventh paper in the Projector-Generated Special Functions series.

## Main files

- `Projector_Generated_Special_Functions_VII.pdf`
- `Projector_Generated_Special_Functions_VII.tex`
- `projector_generated_special_functions_vii.py`
- `tests/test_special_functions_vii.py`
- `figures/`
- `tables/`
- `results/checks.json`
- `results/manifest.json`

## Reproduction

From the source directory:

```powershell
python projector_generated_special_functions_vii.py
$env:PYTHONPATH = "."
pytest -q
pdflatex -interaction=nonstopmode -halt-on-error Projector_Generated_Special_Functions_VII.tex
pdflatex -interaction=nonstopmode -halt-on-error Projector_Generated_Special_Functions_VII.tex
```

The Python program creates all 30 vector figures, all matching PNG figures, the numerical tables, the exact low-degree matrix, the built-in check ledger, and the machine-readable manifest.

## Verified release state

- 60 PDF pages
- 30 vector-PDF figures
- 30 matching PNG figures
- 13 built-in checks passed
- 20 independent tests passed
- no LaTeX overflow or underflow warnings
- no undefined references
- all fonts embedded
- no visible semicolons in the manuscript
- clean PDF preflight

## Mathematical boundary

Racah polynomials, SU(1,1) recoupling coefficients, 6j symbols, and the abstract pentagon identity are classical. The paper's generated object is the typed packet system that joins lowest-weight projection, pair-Casimir analysis, exact basis synthesis, bistochastic measurement kernels, entropy laws, coupling-tree coherence, and finite Givens compilation.
