# Catalan constant: the arithmetic still required

Operation Komorebi · Conjecture Series 08 · Komorebi P.  
Reader edition 1.0 · 9 October 2026

This set contains a mathematical reader, a separate visual guide, their editable LaTeX and scientific figures, the three recovered historical audit files, fresh computation records, and source and proof audits.

The edition does not establish the irrationality of Catalan's constant. It distinguishes written recurrence arguments, authenticated external results, finite exact computations, and unresolved uniform bounds. Recent claimed proofs and criticism are identified by exact version. No proof assistant certification is claimed.

## Read

The two final PDFs are under `output/pdf/`. They are self-contained and contain no cross-site file or Library download links. Bibliographic links lead to public primary sources.

The monograph provides the definitions, arguments, source qualifications, failed diagnostic, and remaining obligations. The visual guide explains those same boundaries mainly through exact diagrams and bounded-data plots.

## Reproduce

Python 3.12, matplotlib, numpy, sympy, PyMuPDF, Pillow, a LaTeX distribution with the listed packages, and Poppler were available for this release. Exact versions are recorded in `evidence/BUILD_ENVIRONMENT.json` and the computation manifests. Run from this directory.

```sh
python3 build.py --figures
python3 validate_historical.py
python3 validate_fonts.py
```

The original computation command and independent checks are documented in `evidence/computation/REPORT.md` and their manifests. The default historical run checks 8,006,000 pairs, using exact integer residues modulo 2^128. A modular zero would be unresolved, rather than an exact valuation. None occurred in this run.

`quality_check.py` renders immutable snapshots with system Poppler at 150 dpi and records automated layout diagnostics. `merge_layout_reviews.py` requires actual page inspection records for the same final PDF hash. `validate_release.py` checks the exported files and current evidence. Running an automated layout script alone does not perform visual review.

Rebuilding can change PDF metadata and therefore hashes. Existing release review records apply to the shipped PDFs. New builds require new page inspection records before their full layout validation can pass.

## Evidence

`historical/` preserves the three recovered originals byte for byte. This edition's exposition is newly assembled from that script and checked literature, not a recovered historical proof manuscript. `evidence/SOURCE_RECOVERY.md` records the recovery limit.

`audits/`, `evidence/`, and `literature/` hold separate mathematical, computational, source, and layout checks. Full third-party paper copies are omitted from the distributed bundle. Source records retain bibliographic identities, exact versions, hashes, and locators so readers can acquire them from their original hosts.

The finite scans cannot establish a uniform valuation bound, a denominator saving, or irrationality. The counterexample to a proposed filter sign pattern is a failed diagnostic hypothesis, not a refutation of the cited external theorems.

`MANIFEST.json` records every packaged file's SHA-256 and byte count. The package builder tests archive integrity and verifies member hashes. Current evidence governs scope, rather than historical success labels or file counts.
