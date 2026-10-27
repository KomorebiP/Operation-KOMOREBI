# Machine Societies — v0.6.0

## A Theory of Persistent Plural Computational Organization

**Komorebi P. · 8 October 2026 · 79-page theoretical edition**

Read `Machine_Societies_v0.6.0.pdf`. The complete editable manuscript is `Machine_Societies_v0.6.0.tex`, with vector figures in `figures/`. The bibliography is embedded in the LaTeX source, so no separate BibTeX run is required.

This edition develops distributed institutional history, observable enforcement, fast/slow institutional dynamics, rational information cascades, and adaptive specialization. It includes 50 theorem/proposition statements with prose proofs, 6 definitions, 15 counterexamples, 12 figures, and 50 references. Classical foundations are identified; these counts are not priority claims.

The manuscript is theoretical. Its examples are analytical constructions. The companion exact checks are not results from the author's agent experiments, a proof-kernel build, or evidence that a deployed population is a machine society.

## Files

- `REVISION_NOTES.md`: integrated changes and corrections from v0.5.
- `PROOFREADING_REPORT.md`: actual review scope, outcomes, and limitations.
- `THEOREM_INDEX.md`: numbered theorem/proposition inventory and source labels.
- `validation/finite_checks.json`: exact per-group domains, counts, status, and runtime.
- `validation/computation_manifest.json`: legacy v1 execution record with separately pinned input/output hashes.
- `validation/reference_review.md`: targeted source checks and retrieval limits.
- `validation/pdf_preflight.json`: geometry, text, and final compiler diagnostics.
- `sources/`: frozen source/review lineage. Prior deliverables are not overwritten.
- `SHA256SUMS.txt`: as-delivered inventory.

## Verify the delivered snapshot

From this directory:

```bash
python validation/verify_release.py
```

This verifies release hashes and the stored computation evidence. It does not check the mathematical proofs. **Run this before regenerating evidence files.** Rerunning the checks changes runtime and receipt hashes, so the original inventory describes the shipped snapshot, not a modified working copy.

## Rebuild the PDF

A standard TeX installation must provide `latexmk`, pdfLaTeX, and the packages named in the source, including `newtxtext` and `newtxmath`. No private fonts or external image downloads are required. From this directory:

```bash
bash build.sh
```

On Windows with an appropriate TeX installation:

```powershell
.\build.ps1
```

Both commands target `build/Machine_Societies_v0.6.0.pdf` and leave the delivered root PDF intact. The Bash command was executed in this release; the PowerShell command was inspected but not run on Windows.

## Rerun exact mathematical checks

Python 3.10 or newer is recommended; the recorded interpreter version is in the manifest. The suite itself uses only the standard library.

```bash
python validation/check_finite_models.py
python validation/verify_release.py --manifest-only
```

The run overwrites its finite-check JSON and manifest in `validation/`. Work on a copy to retain the delivered receipts. Expected substantive result: **52 groups, 367,813 assertions, PASS**. Runtime is not expected to be identical. The tests use integers and exact rational arithmetic, without random sampling.

## Regenerate the new figures and inspect the document

The four new plots/diagrams need Matplotlib. The eight inherited PDFs need not be regenerated to build the paper; their earlier generation scripts remain available.

```bash
python figures/generate_v06_figures.py
```

Optional automated document checks require PyMuPDF and Pillow:

```bash
python validation/check_document.py --render review_pages
```

This renders every page and checks source references, PDF page bounds, text markers, and final compiler diagnostics. It does not replace visual inspection. Generated review images are not included in the distribution.

## Review status

This is an in-session authored and proofread theoretical manuscript. It has not undergone independent peer review, Lean verification, a comprehensive priority search, target-venue review, or tagged-accessibility/PDF-A certification. Ten new references received targeted checking with varying full-text access; the retained bibliography was not all refetched. The finite tests are authored alongside the paper and do not independently certify its general theorems or implementation assumptions.
