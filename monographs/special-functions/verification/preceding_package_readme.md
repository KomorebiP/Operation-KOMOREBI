# Special Functions
## Function families and their structure
### Realization Calculus · Komorebi P.

Open **Special_Functions_Monograph.pdf** for the corrected book. This proofread edition has 134 PDF pages, five parts, seven chapters, ten proof appendices, 32 numbered vector figures, a glossary and a consolidated bibliography. **Design_Preview.pdf** contains 15 representative pages, preserving the book's printed folios.

**Proofreading_Report.pdf** explains the substantive corrections, executed checks, recovered execution timeout and remaining limits. Its editable text is `Proofreading_Report.md`. The full editorial record and exact source diff are in `verification/proofread/`.

## Build the book

From the package root:

```text
python monograph/build.py
```

The PDF is written to `monograph/build/Special_Functions_Monograph.pdf`. Three XeLaTeX passes resolve contents and cross-references. Required: Python 3, XeLaTeX, and the packages named in `monograph/main.tex`. The build uses system URW P052 and Nimbus Sans when present, with TeX Gyre Pagella and Heros fallbacks. DejaVu Sans Mono has a Latin Modern Mono fallback. No font files are bundled. Font substitutions on another machine can change line and page breaks, so inspect a local rebuild.

## Research checks

The original 428 files under `research/` remain byte-identical to the input package. Fresh logs, isolated input snapshots and outputs were added under `research/proofread_runs/`. Research Python APIs and prior manuscripts are provenance, not the production entry point for the new book. The separate companion visual guide retains its previous design.

To rerun the foundation or coupled suites into a new destination under `research/`, use:

```text
python verify_research.py foundation --output-dir local_checks/foundation
python verify_research.py coupled --output-dir local_checks/coupled
```

Install the scientific dependencies required by the original scripts before running them. The foundational suite uses mpmath. The coupled suite and figure generation use NumPy, Matplotlib, mpmath and Pillow. Existing output folders are refused to avoid overwriting evidence. The helper does not impose an aggregate execution deadline. The original foundation runner applies a per-script limit and writes a failure record on failure.

## Fresh verification and its limits

All ten foundation scripts and all three coupled/resolution scripts passed in the current review. Foundation: 19,871 exact assertion statements, 5,576 numerical assertion statements and 61 operational guards. Coupled: 5,272 exact, 26 numerical and 13 operational guards. Combined: 25,143 exact, 5,602 numerical and 74 operational guard assertions. These are counts of executed finite assertions, not independent theorems or exhaustive parameter coverage.

The first foundation orchestration hit the execution environment's time limit after nine passing scripts. The final script was rerun separately against the same isolated input snapshot and passed. This recovered execution failure is retained in the audit. All 14 coupled/resolution figure pairs were regenerated. The production book retains its 32 original vector figure assets unchanged.

No Lean build was performed. Analytic conclusions depend on the written proofs and their hypotheses. Numerical checks are not directed-rounding interval certification. Open type-limit, boundary-regime and minimal-detection questions remain open. This proofreading pass does not establish historical priority or external peer review.

## Audit files

- `verification/proofread/FRESH_VERIFICATION.json`: aggregate execution and publication checks.
- `verification/proofread/editorial_changes.json`: recorded editorial replacements.
- `verification/proofread/source_changes.patch`: exact production-source changes.
- `verification/proofread/MATH_EDIT_REVIEW.json`: mathematical-string comparison aid, not an equivalence proof.
- `verification/proofread/ARCHIVE_REBUILD.json`: independent build from extracted delivery contents.
- `verification/previous_design/`: clearly separated records from the preceding design-only pass.

`MANIFEST.json` and `SHA256SUMS` identify all payload files except the inventory files themselves. No script uploads or publishes the project.
