# Release audit

## Computational checks

The benchmark runner completed all named checks. It generated:

- 40 vector-PDF figures
- 40 matching PNG figures
- 11 CSV result tables
- one machine-readable JSON result ledger
- one 45-page PDF manuscript

## Document checks

- PDF opens successfully
- 45 rendered pages
- no PDF preflight warnings
- no LaTeX overfull boxes
- no LaTeX underfull boxes
- no undefined references
- no duplicated labels
- all fonts embedded
- no missing figures
- no one-line part or chapter pages

## Claim checks

- exact-model and exploratory results remain separate
- the localized-burst model-order failure is retained
- out-of-dictionary failures are retained
- natural-image results are not promoted to exact theorems
- random dictionary tests are identified as in-model tests
