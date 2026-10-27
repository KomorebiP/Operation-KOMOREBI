# Stratified Universality visual companion

Author: Komorebi P. Final companion edition: 6 October 2026.

The 35-page PDF and complete Markdown guide follow finite profiled packet transport, refinement and residuals, holonomy, task-relative behavioral quotients, semantic diamonds, carrier factorization, observer change, and admissibility-relative obstruction. All source anchors identify manuscript results. They are not Lean declaration names.

Included files:

- `Stratified_Universality_Visual_Guide.pdf`: final illustrated companion.
- `Stratified_Universality_Visual_Guide.tex`: editable typesetting source.
- `Stratified_Universality_Visual_Guide.md`: complete Markdown companion with equations, captions, and source anchors.
- `generate_examples_and_figures.py`: exact rational examples and 14 vector figure generators.
- `build_markdown.py`: Markdown export preserving custom captions and source anchors.
- `figures/`: vector PDF figures and PNG previews.
- `validation/visual_example_checks.json`: 137 exact rational assertions, all passing.
- `validation/visual_qa.json`: structural and build checks.

Reproduce with a Python environment containing NumPy and matplotlib, plus pdfLaTeX and Pandoc:

```bash
python generate_examples_and_figures.py
python build_markdown.py
pdflatex -interaction=nonstopmode -halt-on-error Stratified_Universality_Visual_Guide.tex
pdflatex -interaction=nonstopmode -halt-on-error Stratified_Universality_Visual_Guide.tex
pdflatex -interaction=nonstopmode -halt-on-error Stratified_Universality_Visual_Guide.tex
```

Exact algebra uses standard-library `fractions.Fraction`; no SymPy dependency is required. The unipotent-distortion curve uses floating point only to illustrate a proved analytic limit. Finite-grid example checks do not substitute for the manuscript's universal proofs, and the newly written pedagogical examples are not claimed to be Lean-certified.
