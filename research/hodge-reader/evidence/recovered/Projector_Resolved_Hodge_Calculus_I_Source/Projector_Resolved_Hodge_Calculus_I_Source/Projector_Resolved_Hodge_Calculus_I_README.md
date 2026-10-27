# Projector-Resolved Hodge Calculus I

## Contents

This release contains the manuscript

**Projector-Resolved Hodge Calculus I: Primitive Hodge Packets, Algebraic Cycle Frames, Polyphase Correspondences, and Divisor-Lowering Reconstruction**

by **Komorebi P.**

The paper develops a projector-resolved research program for the rational Hodge conjecture. It proves a collection of finite reductions and correspondence criteria, validates those criteria on classical geometric families, and isolates the remaining primitive-fourfold obstruction. It does **not** claim a proof of the general Hodge conjecture.

## Main files

- `Projector_Resolved_Hodge_Calculus_I.pdf` — compiled 48-page manuscript
- `Projector_Resolved_Hodge_Calculus_I.tex` — LaTeX source
- `projector_resolved_hodge_calculus.py` — Python figure and verification generator
- `figures/` — 32 vector-PDF and 32 PNG figures
- `results/verification.json` — complete finite-check ledger
- `results/pdf_preflight.json` — PDF preflight report
- `results/layout_audit.json` — page-layout audit
- `tables/checks.csv` and `tables/checks.tex` — verification tables
- `FIGURE_INDEX.md` — figure inventory

## Reproduction

A standard TeX Live installation with `latexmk` is sufficient for the manuscript. Python 3 with NumPy, SciPy, Matplotlib, and mpmath is sufficient for the figures and checks.

From the release directory:

```bash
python projector_resolved_hodge_calculus.py
latexmk -pdf -interaction=nonstopmode -halt-on-error Projector_Resolved_Hodge_Calculus_I.tex
```

A second and third LaTeX pass are handled automatically by `latexmk`.

## Verification summary

- 48 manuscript pages
- 32 original figure pairs
- 18 of 18 finite checks passed
- no PDF preflight warnings
- no out-of-bounds text blocks
- no overfull or underfull LaTeX box warnings
- embedded fonts and document metadata present

## Mathematical boundary

The release distinguishes among:

1. finite linear-algebra identities and packet-reconstruction theorems proved directly
2. conditional algebraization results whose hypotheses are stated explicitly
3. classical validation families used to test the framework
4. open targets, particularly primitive codimension-two saturation on projective fourfolds

The manuscript should not be cited as a proof of the general Hodge conjecture.
