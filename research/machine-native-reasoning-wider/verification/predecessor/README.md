# Machine-Native Reasoning — First Integrated Working Edition

**Author:** Komorebi P.

This is actual publication work, not merely another outline. The current 57-page PDF contains the full reviewed nine-chapter mathematical core and new integration material. It is **not yet the definitive proposed 30-chapter monograph**.

## Main reading file
`Machine_Native_Reasoning_Working_Edition.pdf` or `book.tex` for source compilation. The PDF is built by `latexmk -pdf book.tex` with newtx text/math and the vector figures in `figures/`.

## Original code and mathematical source
- `sources/core/src/core.tex`: source-frozen original reviewed mathematical core, unchanged.
- `core_chapters.tex`: its verbatim nine-chapter LaTeX body as extracted from the original source.
- `sources/lean15/`: selected authentic, unchanged files from the complete Block 15 Lean archive for source anchoring; this compact handoff does **not** substitute for the full predecessor ZIP.
- `sources/compendium/`: catalog and bridge register of the original 24-document research compilation.
- `realization_prologue.tex`: mathematical connection with Komorebi Space.
- `composition_chapter.tex`: new finite composition theorem, worked example, counterexample.
- `ending_chapter.tex`: expanded Core 8.3 proof with rank and adversarial strategies.
- `frontier_chapter.tex`: accurate nonclaims and future theorem interfaces.
- `figures/make_figures.py`: Python/matplotlib vector figure source.

## Executed tests
```
python formal/check_core83.py
python formal/check_joint_contract.py
python verification/reproduced_core/code/check_core.py
python verification/reproduced_core/code/check_admissions.py
latexmk -pdf -outdir=_build book.tex
```
The core tests use only Python standard-library exact finite arithmetic. The underlying original source integrity was checked before rerunning them. All reported current tests passed. See `PROGRESS_LEDGER.md` for exact counts.

## What remains unfinished
Four selected Lean targets remain (8.3, 2.4, 2.5, 3.2). The pinned Lean 4.34.0-rc2/Mathlib toolchain is not installed in the current execution environment. No newly written chapter was certified by Lean. The original compiled Block 15 archive remains a historical source-specific PASS with manifest verification. The newer joint interface theorem is proof-written and finite-tested, not kernel certified or externally reviewed.

The other 18 chapters in the proposed 30-chapter final architecture require result-by-result admission and composition work; see `editorial/FULL_BOOK_OUTLINE_AND_GAPS.md`. Specialist results are not automatically imported merely because their historical PDFs are preserved.

## Companion archives
The compact edition ZIP preserves editable working text, source maps, figures, exact checks and verification records. An optional larger source archive preserves the five primary original source ZIPs together with the newer Large Signal Model and Komorebi Space reading/source editions. The original 24-paper compilation and the Lean predecessor archive are intentionally left byte-identical inside that larger archive.

**Trust boundary:** PDF rendering, finite checks, ZIP integrity, written proofs, Lean kernel verification, and empirical claims about deployed systems are different evidence types. Do not substitute one for another.
