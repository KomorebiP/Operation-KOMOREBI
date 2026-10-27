# Paper VII Lean guide

The PDF teaches the current v0.6.0 source through exact contracts and proof walkthroughs. It contains all 19 scoped finite results, all 323 named theorem declarations in 25 modules, and 67 exact contiguous source selections. The cross-reading tables locate all 19 core items and all 79 proof-bearing strengthened statements in the final traditional paper.

Build from the final package root:

```bash
python editable/lean_guide/build.py
python editable/lean_guide/verify_pdf.py
```

The build is self-contained and stages its inputs in a temporary directory. Requirements are Python 3, XeLaTeX, P052, DejaVu Sans/Mono, Latin Modern Math and the TeX packages named in `preamble.tex`. PDF QA additionally requires PyMuPDF, Pillow and `pdffonts`.

Regenerate source-derived tables and exact selections with the preserved source:

```bash
python editable/lean_guide/assemble.py --source source/complete/Paper_VII_Complete_v0.6.0_With_Visual_Appendix/original_snapshot
python editable/lean_guide/build.py
python editable/lean_guide/verify_pdf.py --source source/complete/Paper_VII_Complete_v0.6.0_With_Visual_Appendix/original_snapshot
```

Assembly additionally requires FontTools and fontconfig. The source and inventory counts are intentional fixed expectations for this edition. The cross-reading table is frozen in `generated/traditional_navigation.tex`, with its page-map and PDF binding in `generated/traditional_navigation_provenance.json`. `navigation.py --map PATH` can regenerate that table from a new traditional page map; do not change the binding without verifying the new edition.

Files ending `.lean.txt` retain raw UTF-8. `.render.txt` files use explicit TeX font fallback and escaped TeX control characters for printing. No formal source file is modified. Exact source ranges and hashes are in `generated/excerpts.json` and in the printed excerpt register.

`qa/pdf_checks.json` records PDF parsing, all extracted theorem names, exact excerpt checks, glyph/reference/overflow checks and link bounds. Page contact sheets were generated from every page for visual review. The inherited 6 September 2026 kernel record is distinguished from fresh static, computation and document checks. Lean, Lake and the pinned portable kit were unavailable on the documentation host; none of these scripts claims a new kernel run.
