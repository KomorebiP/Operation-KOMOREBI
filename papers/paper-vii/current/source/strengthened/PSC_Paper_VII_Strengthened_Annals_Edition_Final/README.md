# Paper VII strengthened Annals edition

## Article

**Title:** Quantum Packet Calculus, Symmetry, Effective Dynamics, and Continuum Towers

**Author:** Komorebi P.

The article develops a finite quantum packet calculus for observable algebras, symmetry sectors, circuit paths, moving projectors, quantum channels, error correction, Feshbach elimination, Euclidean transfer, spectral dimension, constraint closure, and bounded refinement towers.

## Main files

1. `PSC_Paper_VII_Strengthened_Annals_Edition.pdf`
2. `PSC_Paper_VII_Strengthened_Annals_Edition.tex`
3. `PSC_Paper_VII_Strengthened_Annals_Edition.bib`
4. `figures/`
5. `verification/`
6. `legacy/`

## Build

Run the following commands from the package root.

```text
pdflatex -interaction=nonstopmode -halt-on-error PSC_Paper_VII_Strengthened_Annals_Edition.tex
bibtex PSC_Paper_VII_Strengthened_Annals_Edition
pdflatex -interaction=nonstopmode -halt-on-error PSC_Paper_VII_Strengthened_Annals_Edition.tex
pdflatex -interaction=nonstopmode -halt-on-error PSC_Paper_VII_Strengthened_Annals_Edition.tex
```

The installed environment used `/usr/bin/bibtex.original` because its default `bibtex` link was not functional.

## Verification

Run

```text
python verification/verify_paper_vii.py
```

The archived run reports 18,049 checks passed in 15 groups.

## Status

The package is internally complete. Every theorem, proposition, lemma, and corollary has a proof in the manuscript. The finite calculations and source audits passed. This does not replace independent specialist review, historical priority review, or editorial assessment.
