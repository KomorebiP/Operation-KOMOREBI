# Operation Komorebi conjecture reader set

Expanded reader edition 1.1, 8 October 2026. Author pseudonym: Komorebi P.

The set contains an expanded traditional monograph and a separate visual guide for each conjecture. Both conjectures remain open. The proofs, exact reductions, finite checks, models, and remaining inputs are distinguished in the documents.

## Four reader documents

- `pdf/Komorebi_Collatz_Conjecture_Piece_v1.1.pdf`: valuation packets, ordered offsets, cylinder admissibility, descent thresholds, exact source comparisons, delayed termination, infinite progression lifts, the full orbit from 27, and the bounded deficit packing proof.
- `pdf/Komorebi_Riemann_Conjecture_Piece_v1.1.pdf`: completion and zero geometry, heat convergence, Laplace residues, local energy, exact Gaussian constants, the physical metric, Hermite resolution, explicit prime cubes, squarefree support, and the signed arithmetic criterion.
- `pdf/Komorebi_Collatz_Visual_Guide_v1.1.pdf`: twenty four distinct visual spreads with exact integer examples, residue geometry, orbit clocks, progression lifts, density and height arguments, and proof dependencies.
- `pdf/Komorebi_Riemann_Visual_Guide_v1.1.pdf`: twenty four distinct visual spreads with zero geometry, Gaussian heat, physical modes, explicit prime cubes, signed support, the absolute majorant barrier, and the remaining estimate.

The guides use Python figures. Each has a reproducible generator, input data, pinned numerical dependencies, and an audit record. Numerical and schematic illustrations are identified at the point where they appear. A hypothetical off axis zero is a model, not an observed zero of zeta.

## Source and audit map

The `collatz/` and `riemann/` folders contain manuscript TeX, bibliography, source registers, and proofreading notes. Their evidence folders retain the selected recovered research records and their original read metadata. Complete and partial source recoveries are distinguished.

The `collatz_visual/` and `riemann_visual/` folders contain the guide TeX, all vector and raster figures, Python source, data, computation manifests, and proofreading notes.

`shared/REVIEW_v1.1.md` pins the four reviewed body revisions. `shared/review_expansion_checks.py`, its final JSON result, and `shared/review_expansion_final_run/manifest.json` preserve the independent controls and their exact scope. The superseded initial run directory is excluded from the release because it predates the extra controls and does not match the final script revision.

`shared/LAYOUT_VALIDATION_v1.1.json` records final page counts, source and PDF hashes, machine checks, and visual inspection. `AUTHORING_REPORT_v1.1.md` records the revision, resolved failures, and remaining boundaries. `MANIFEST.json` lists every archive payload and its SHA256 hash.

`shared/SOURCE_VALIDATION_v1.1.json` checks current labels, citations, environments, and agreement with the four reviewed body hashes. Both the default README and default authoring report describe edition 1.1.

Original edition 1.0 manuscripts, reports, and reader PDFs are retained under `archive/v1.0/`. Shared reports without a 1.1 suffix describe the earlier checkpoint, rather than a new audit of this edition.

This is a reader and reproducibility bundle. It contains selected recovered Lean text and historical reports, rather than a complete portable Lean dependency project. No new Lean replay is claimed.

## Rebuild

Provide Python 3 and the packages pinned in each figure folder. The original shared figure generator additionally needs mpmath 1.3.0. Provide TeX with pdflatex, mathpazo, Helvetica, Courier, amsmath, mathtools, microtype, titlesec, fancyhdr, graphicx, enumitem and hyperref. The guide generators reuse the audited critical line data for their xi panels and do not require a fresh zeta evaluation.

```bash
python collatz_visual/figures.py
python riemann_visual/figures.py
python shared/review_expansion_checks.py
python build.py
```

`python build.py --only collatz` rebuilds one paper. The other choices are `riemann`, `collatz_visual`, and `riemann_visual`. `--figures` regenerates all original and guide figures before compiling.

For optional layout checks, provide PyMuPDF, Pillow, and Poppler's pdftoppm, then run `python quality_check.py`. Every regenerated document still requires visual inspection. After final reports exist, `python package.py` creates and verifies the source archive.

Finite computation supports the declared examples and implementation checks. The universal assertions actually established are carried by the written proofs and their cited classical premises. Universal Collatz descent and the RH signed estimate are not promoted from a finite check count.
