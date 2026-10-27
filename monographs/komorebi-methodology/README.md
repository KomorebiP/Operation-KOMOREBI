# The Komorebi Methodology
## Mathematical Discovery, Realization, and the Discipline of Proof

**Author:** Komorebi P.  
**Series:** Realization Calculus / Mathematical Essays

This is the reviewed full essay, not an outline. The reader contains **28 physical
pages**, nine chapters, a conclusion, a preface, three reproducible figures, source
notes, and references. The main text contains **7,611 words** under
`texcount -1 -sum essay.tex`, including countable headings. The approved dark-plum
monograph cover, white interior, serif typography, and restrained gold accents remain.

## Read and edit

Start with `Komorebi_Methodology.pdf`.

The essay follows one argument: realization makes a question accessible, obstruction
gives failure mathematical content, admissible correction supplies a constructive
response, verification establishes scope, and mathematical memory supports reuse.
The returning-coordinate example now continues through an exact memory formula and
its all-time induction proof rather than ending at the failed simplification.

Editable files:

- `Komorebi_Methodology.tex`: design, cover, title page, preface, contents, assembly.
- `essay.tex`: nine chapters and conclusion.
- `sources.tex`: source notes, scope, and bibliography.
- `figures.py`: three vector diagrams and their PNG previews.

The PDF contains no administrative checkpoint labels. `PROGRESS_LEDGER.md` and
`audit/REVIEW_REPORT.md` preserve the editorial history separately.

## Verification and its boundaries

The recorded run passes **40/40 exact-check groups with 665 finite cases** and
**17/17 manifest-validator controls**. The former cover exact matrix calculations,
finite factorization and continuation tests, rational memory recurrences, arithmetic
transforms, obstruction witnesses, and the declared proof-field illustration. These
are cases in a test suite, not counts of new mathematical theorems. The validator
controls are separately counted actual command-line executions against isolated
fixtures. They include genuine negative controls and check the intended diagnostics.

The final three-pass typesetting build contains no reported overfull/underfull boxes,
LaTeX warnings, or missing-character messages. All 28 pages were rendered and
reviewed. The structural audit found no out-of-page text spans, unresolved reference
markers, replacement glyphs, invalid internal links, or bookmark-title mismatches.
All 27 bookmarks were checked against their destination pages.

A source-only rebuild under the same installed environment reproduced all 28 pages
with matching extracted text, bookmarks, and rendered pixels at 72 dpi using the same
renderer. Its exact-calculation and integrity-control records also match. This is
reproducibility, not an independent implementation of the tools. PDF byte identity
is not asserted. The visual editorial review used separate 145-dpi page renders.

**No new Lean compilation or corpus-wide formal audit was performed.** The
continuation and memory identities have written proofs. The unbounded tower and
infinite Hilbert-space example also rely on their written arguments, not on finite
tests. Historical Lean records remain attributed to their source documents. The
comparison of research workflows is a proposed study, not a completed experiment.

`audit/CLAIM_MAP.json` connects the major exposition claims to these evidence types.
The source package does not bundle the full companion monographs or Lean projects.

## Verify the delivered package first

In the freshly extracted directory, before creating or rebuilding files, run:

```text
python verify_manifest.py
```

The verifier requires the **complete file inventory** in `MANIFEST_SHA256.txt` and
checks its SHA-256 digests. It rejects empty or incomplete inventories, extra or
missing files, modified payloads, duplicates, and unsafe paths. A metadata file added
by an operating system can therefore trigger a strict unlisted-file diagnostic.
Inspect that diagnostic rather than silently weakening the check.

The previous validator incorrectly accepted an empty manifest. That defect was
reproduced, recorded, and corrected. The original package's nonempty hash check is
not thereby invalidated. See `audit/review_baseline_finding.json`.

Integrity is relative to the supplied manifest. It is **not authentication** of the
author and **not a mathematical correctness proof**. Regeneration changes files and
creates build artifacts, so a delivery manifest is not expected to pass afterward.
Do not overwrite the delivered manifest to disguise those changes.

## Run the standard-library checks

```text
python exact_checks.py
python integrity_checks.py
```

These require Python 3.10 or later but no third-party Python packages or TeX.
Both produce readable and machine-readable records in `audit/`. The integrity
controls use temporary fixtures and do not mutate the delivered inventory.

## Rebuild the PDF

Install the figure dependencies and use the shared build entry point:

```text
python -m pip install -r requirements.txt
python build.py
```

PowerShell: `./build.ps1`. Unix-like shell: `./build.sh`.

`build.py` runs both check suites, regenerates the figures, and performs three
`pdflatex` passes. It preserves compiler output in `audit/build_pass_*.log` and
returns failure when a command or the checked final-log classes fail. Visually inspect
the rebuilt PDF after editorial changes. Command success is not visual review.

Use a TeX distribution providing `newpxtext`, `newpxmath`, `mathtools`, `microtype`,
`tikz`, `tcolorbox`, `titlesec`, `fancyhdr`, `hyperref`, `bookmark`, and dependencies.
The display family is TeX EB Garamond (`EBGaramond-LF`) and the sans-serif family is
TeX Gyre Heros (`qhv`). Install these using TeX Live or MiKTeX. **No font binaries
are distributed in the ZIP.** Fonts embedded in the PDF are part of normal typesetting.

The actual environment is recorded in `audit/build_environment.json`. Dependency
ranges are not a fully locked environment. Different toolchain or font versions may
alter pagination or metadata.

## Optional PDF and reproduction checks

```text
python -m pip install -r requirements-review.txt
python review_pdf.py
python reproduce.py
```

The optional scripts use PyMuPDF. The first checks PDF structure and navigation.
The second starts from sources in a temporary directory with no inherited PDF,
figures, or calculation receipts, rebuilds, and compares to the current reader.
It still uses the same installed tools. Neither is a proof of the essay's
methodological effectiveness or an independent mathematical review.

## Audit records and continuity

`audit/REVIEW_REPORT.md` explains the substantive changes and corrected failures.
`audit/QA_REPORT.json` summarizes current checks. `audit/SOURCE_REGISTER.md` identifies
bibliographic editions and public documentation. `audit/provenance.json` binds the
current source and PDF to the baseline. `PROGRESS_LEDGER.md` states the restart point.

`audit/history/editorial-01/` preserves the first full-essay receipts as **historical**
evidence. Its page counts, hashes, and scope apply to that earlier artifact, not to
this reader. Current evidence is directly under `audit/`.

This package does not change a project-wide licensing decision or relicense
third-party material. The public source PDFs and font distributions are not bundled.
