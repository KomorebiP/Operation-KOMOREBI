# Release audit

## Mathematical checks

- 24 built-in checks passed
- 21 independent pytest tests passed
- exact formulas were compared with direct quadrature or independent reconstruction where practical
- one deliberately approximate test concerns the finite-shape Gaussian limit and is reported with its declared tolerance

## Document checks

- 54 pages
- 28 vector-PDF figures
- 28 matching PNG figures
- no overfull boxes
- no underfull boxes
- no undefined references
- no PDF preflight warnings
- all fonts embedded
- no visible semicolons in the manuscript or code listing
- no blank content pages
- no source figures adapted from the external quantum article

## Reproducibility

The source package contains the LaTeX manuscript, Python generator, tests, requirements, build script, generated figures, result ledgers, and documentation. A clean extraction can rebuild the paper with `python build_all.py`.

## Boundary

The release proves the positive shape and coherent-state theory stated in the manuscript. It does not prove RH.

## Clean rebuild

The source archive was extracted into a separate directory and rebuilt with `python build_all.py`. The clean run passed all 24 built-in checks and all 21 independent tests. The rebuilt PDF contains 54 pages. A 150 DPI page comparison reported zero changed pages out of 54.
