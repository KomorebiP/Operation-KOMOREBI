# Sufficient Resolution: Visual Guide

Komorebi P. · Final companion edition · 6 October 2026

The 45-page guide develops 42 substantive sections covering the full existing
Sufficient Resolution v0.16.0 program. It includes 18 original vector figures,
99 display equations, and 127 source-anchor occurrences resolving to 122 distinct
Lean declarations. The Markdown edition contains the same equations, figure
captions, links, and declaration anchors as the TeX edition.

`build_guide.py` is the shared content source for TeX and Markdown. It checks
declarations against the adjacent `formal/` source directory in the complete
release. It also reads the traditional claim concordance and emits a CSV/JSON
visual-to-traditional crosswalk covering all 64 consolidated theorem groups.
`guide_content.json` is the generated structured content record.

## Rebuild

From this directory:

```bash
python3 generate_examples_and_figures.py
python3 build_guide.py
pdflatex -interaction=nonstopmode -halt-on-error Sufficient_Resolution_Visual_Guide.tex
pdflatex -interaction=nonstopmode -halt-on-error Sufficient_Resolution_Visual_Guide.tex
pdflatex -interaction=nonstopmode -halt-on-error Sufficient_Resolution_Visual_Guide.tex
python3 validate_guide.py
```

Figure generation requires NumPy and matplotlib. Validation requires PyMuPDF.
The exact checks use Python's standard-library `fractions.Fraction` only.
pdfLaTeX requires the TeX packages listed in the editable source preamble.

## Evidence scope

The generator performs 280 exact rational assertions for displayed finite
examples. Its labels and vector-PDF hashes are in
`validation/visual_example_checks.json`. These assertions concern the examples;
they do not prove all-depth theorems or analytic limits.

The final bounded run's version-2 provenance is in
`validation/visual_computation_20261006/manifest.json`, with its actual result
and logs. Its contract is `validation/visual_computation_contract.json`.
Repeated passes of the same suite are not additional distinct assertions.

Smooth charts evaluate the printed analytic formulas using floating point only
for drawing. The `1/n` singular-mode chart is a finite diagonal illustration,
not a separately instantiated Lean operator with dense nonclosed range.

The generic redundant calibration frame illustrated here, `U(u,v)=u+v` and
`R(x)=(x/2,x/2)`, is a distinct exact finite worked example. It is not presented
as the literal `CalibrationExamples.redundantFrame` definition.

All calibration truth/noise allowances retain their external hypotheses.
Generalized acceptance retains a separate parameter-feasibility obligation.
Exact parameter selection is noncomputable in Lean. Strong consistency concerns
a fixed true source/operator, with valid allowances vanishing. Python code and
parsing are not formally verified by the mathematical theorem declarations.

The guide states two open joins explicitly: deriving an operator-level
calibration truth allowance from individual noisy samples, and stable target-only
prediction directly from the behavioral minimality construction. It makes no
unrestricted nonlinear, physical, positive, integral, or arithmetic recovery claim.
