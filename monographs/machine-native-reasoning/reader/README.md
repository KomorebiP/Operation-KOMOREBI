# Machine-Native Reasoning: Reviewed Mathematical Core

This reader presents the selected mathematical core of Machine-Native Reasoning, with complete written proofs, the six original Python-generated figures, and a formal correspondence chapter. It is a separately titled companion to the cumulative Lean release. It is not the later 1,155-page prose-refined monograph, whose full editable source and PDF were not recovered during this release audit.

The PDF is `Machine_Native_Reasoning_Reviewed_Core.pdf`. Editable LaTeX, original figures, original finite-check programs, and the preserved source anchor are under `source/`. Source identities are in `SOURCE_PROVENANCE.json`. The manifest under `source/source_original/` describes the recovered historical core archive; it is provenance evidence, not a manifest of this reader directory. `READER_MANIFEST.json` identifies the final reader files. The exact final Lean release record, theorem correspondence, axiom audit, rejection controls, and kernel replays govern the formal acceptance claim. A PDF build does not perform Lean verification.

## Reproduce the reader

From this directory, run:

```sh
python source/build_reader.py --out /absolute/path/to/new-reader-rebuild
```

Use Python 3.10 or later, pdfLaTeX, and Poppler (`pdfinfo` and `pdffonts`). The LaTeX dependencies are `geometry`, `fontenc`, `amsmath`, `amsthm`, `amssymb`, `mathtools`, `mathpazo`, `microtype`, `graphicx`, `float`, `booktabs`, `longtable`, `array`, `enumitem`, `xcolor`, `fancyhdr`, `titlesec`, `needspace`, `etoolbox`, and `hyperref`. The supplied reader was built with pdfTeX from TeX Live 2023. All font subsets are embedded; no standalone fonts are shipped. Font notices are under `licenses/`.

The runner copies the sources into a fresh temporary directory, verifies preservation of the original proof/statement/display spans, reruns the two original exact-check programs, builds the PDF in three passes, checks font embedding and unresolved compiler defects, and records source hashes and logs. Its output directory must be new or empty and outside `source/`. The supplied six figure PDFs are preserved byte-for-byte. Their two original Matplotlib generators are included under `source/code/`; regenerating those historical figures is a separate operation and is not required for a document rebuild. The original figure-data JSON is included under `source/evidence/`. To regenerate in a separate copy of `source/` with Matplotlib installed, run `python code/make_figures.py` followed by `python code/make_admission_figures.py` from that copy. Keep new figure outputs and their review separate from the preserved original PDFs.

## Verification and scope

All 27 written proof spans, 39 statement/counterexample spans, 54 display blocks, and all inline mathematics in `book.tex` are unchanged from the authenticated source. Editorial changes update the title matter, review-status prose, bibliography scope statements, and one chapter transition; they also add the separate formal correspondence chapter. The exact editorial diff and preservation receipt are included.

The original finite checks freshly pass 205,477 assertions in 27 groups. They test stated finite domains and do not replace the written proofs or the Lean gates. The earlier broader source-suite receipts retain their own provenance. `verification/` records the fresh reader build, document checks, rendering review, and exact-check receipts.

Original prose and figures follow the author's CC BY 4.0 policy; original code follows MIT. The release-root full licenses and original attribution apply. The font and external dependency notices retain their own terms.
