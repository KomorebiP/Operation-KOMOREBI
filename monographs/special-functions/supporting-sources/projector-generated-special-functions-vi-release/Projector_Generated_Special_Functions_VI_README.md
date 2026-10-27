# Projector-Generated Special Functions VI

This source package builds the paper

**Meixner Shape Semigroups, Beta-Binomial Packet Refinement, Polynomial Martingales, and Gamma-Sech Berezin Kernels**

by Komorebi P.

## Build

```bash
python projector_generated_special_functions_vi.py
python -m pytest -q
pdflatex -interaction=nonstopmode -halt-on-error Projector_Generated_Special_Functions_VI.tex
pdflatex -interaction=nonstopmode -halt-on-error Projector_Generated_Special_Functions_VI.tex
pdflatex -interaction=nonstopmode -halt-on-error Projector_Generated_Special_Functions_VI.tex
```

Or run:

```bash
python build_all.py
```

## Generated material

The Python program writes:

- 28 vector-PDF figures
- 28 matching PNG figures
- numerical result ledgers
- cumulant and transfer-spectrum tables
- the LaTeX verification table
- the figure index
- the machine-readable manifest

The independent pytest suite contains 21 tests.

## Claim boundary

The paper proves exact results about the positive shape semigroup, Meixner-Pollaczek packet refinement, polynomial transfers, coherent-state frames, and Berezin kernels. It does not prove the signed Mobius coherence estimate and does not prove the Riemann hypothesis.
