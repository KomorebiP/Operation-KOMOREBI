# Projector-Generated Special Functions IV

## Squarefree Depth-Time Kernels, Universal Gamma Dephasing, Mobius Resolvents, and Signed Pade Packet Models

**Author:** Komorebi P.

This release develops the joint depth-time layer of the projector-generated special-function program. It starts from the signed Mobius transfer, extracts a positive kernel by exact time averaging, derives its squarefree Dirichlet coordinates and universal Gamma asymptotics, then returns to the signed side through a resolvent, a Borel-Riesz bridge, and finite Pade packet models.

The paper proves unconditional results for the positive depth-time kernel. The signed Pade reduction is exact whenever the displayed finite Hankel determinant is nonzero. The Riemann-hypothesis statement remains an equivalent coherence criterion and is not claimed as solved.

## Build

```bash
python projector_generated_special_functions_iv.py --base .
python generate_tables.py
python -m pytest -q
pdflatex -interaction=nonstopmode -halt-on-error Projector_Generated_Special_Functions_IV.tex
pdflatex -interaction=nonstopmode -halt-on-error Projector_Generated_Special_Functions_IV.tex
pdflatex -interaction=nonstopmode -halt-on-error Projector_Generated_Special_Functions_IV.tex
```

Or run:

```bash
python build_all.py
```

## Main outputs

- `Projector_Generated_Special_Functions_IV.pdf`
- `Projector_Generated_Special_Functions_IV.tex`
- `projector_generated_special_functions_iv.py`
- `results/results.json`
- `results/checks.csv`
- `figures/`
- `tables/`

## Verification

The generator reports 18 of 18 built-in checks. The independent suite reports 18 of 18 tests. The final PDF has 55 pages, 28 vector figures, matching PNG figures, embedded fonts, and no PDF preflight warnings.
