# Paper VIII strengthened Annals edition

## Article

**Title:** Packet Operator Algorithms, Exact Compilation, and GPU Realization  
**Author:** Komorebi P.

The manuscript develops a finite computational calculus for packet resolved operators. It separates exact operator semantics from device realization, proves algebraic and optimization results for structured representations, and reports a sanitized CPU and GPU measurement corpus with matched output and timing contracts.

## Primary files

- `PSC_Paper_VIII_Strengthened_Annals_Edition.pdf`
- `PSC_Paper_VIII_Strengthened_Annals_Edition.tex`
- `PSC_Paper_VIII_Strengthened_Annals_Edition.bib`

## Package contents

- `figures/` contains twenty two vector PDF figures.
- `psc_packet/` contains the reference implementation and figure generator.
- `verification/` contains deterministic verification, strengthened tests, baseline test results, and machine readable audit records.
- `tables/` contains the sanitized benchmark tables used by the paper.
- `legacy/` preserves the original Paper VIII source release and measured corpus for provenance.
- The Markdown and JSON files in the package root record the mathematical, bibliographic, language, and build audits.

## Rebuild

From the package root, run:

```text
pdflatex -interaction=nonstopmode -halt-on-error PSC_Paper_VIII_Strengthened_Annals_Edition.tex
bibtex PSC_Paper_VIII_Strengthened_Annals_Edition
pdflatex -interaction=nonstopmode -halt-on-error PSC_Paper_VIII_Strengthened_Annals_Edition.tex
pdflatex -interaction=nonstopmode -halt-on-error PSC_Paper_VIII_Strengthened_Annals_Edition.tex
```

On the build environment used for this release, the working `bibtex` link was broken, so `/usr/bin/bibtex.original` was used.

## Verification

```text
cd legacy
python -m pytest -q

cd ..
PYTHONPATH=. python -m pytest -q verification/test_strengthened.py
PYTHONPATH=. python verification/run_full_verification.py
```

Recorded results:

```text
23 baseline tests passed
11 strengthened tests passed
37392 of 37392 deterministic checks passed
```

## Scope

The package establishes internal symbolic consistency, reproducibility of the finite checks, and agreement with the recorded sanitized benchmark corpus. It does not replace independent specialist proof review, source level benchmark replication on the original hardware, or a historical novelty audit.
