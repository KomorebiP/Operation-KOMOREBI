# Projector-Generated Special Functions VIII

## q-Hahn Lowest-Weight Packets, q-Racah Recoupling, Askey-Wilson Transfer Functions, and Deformation Geometry

Author: Komorebi P.

## Contents

- `Projector_Generated_Special_Functions_VIII.pdf` is the compiled paper.
- `Projector_Generated_Special_Functions_VIII.tex` is the LaTeX source.
- `projector_generated_special_functions_viii.py` generates all figures, tables, and built-in checks.
- `tests/test_special_functions_viii.py` is the independent test suite.
- `figures/` contains 32 vector-PDF figures and 32 matching PNG files.
- `tables/` contains the numerical certificate tables.
- `results/` contains the check ledger, figure manifest, and PDF preflight record.

## Reproduction

Create a Python environment with NumPy, SciPy, Matplotlib, and Pytest. A standard TeX Live installation with `pdflatex` is also required.

Run:

```powershell
python projector_generated_special_functions_viii.py
python -m pytest -q
pdflatex -interaction=nonstopmode Projector_Generated_Special_Functions_VIII.tex
pdflatex -interaction=nonstopmode Projector_Generated_Special_Functions_VIII.tex
pdflatex -interaction=nonstopmode Projector_Generated_Special_Functions_VIII.tex
```

The generator should report:

```text
Generated 32 figure pairs
Checks passed: 23/23
```

The independent test suite should report:

```text
20 passed
```

## Mathematical scope

The paper proves the finite packet identities stated for the symmetric q-number convention used by the code. It also records classical q-Racah and Askey-Wilson identities in the declared normalizations.

q-Racah polynomials, Askey-Wilson polynomials, quantum-group Clebsch-Gordan coefficients, quantum `6j` symbols, and the abstract pentagon identity are classical. The paper's contribution is the unified packet construction and the derived operational tuple containing projector reduction, q-Casimir atlases, reversible recoupling, measured bistochastic kernels, deformation transport, pentagon certification, and finite compilation.

The quantum-zeta discussion is modular. It does not identify q-Casimir eigenvalues with zeta zeros and does not prove the Riemann hypothesis.
