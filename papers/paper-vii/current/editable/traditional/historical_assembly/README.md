# Paper VII — final traditional edition

Read `Paper_VII_Traditional_Final.pdf` (101 physical pages). The title page is followed by five Roman-numbered front-matter pages and 95 Arabic-numbered reading pages. Parts I, II and III have separate result numbering. The visual guide and Lean/evidence guide are separate deliverables.

This reading edition contains the corrected integrated finite core, the complete strengthened mathematical development (all 79 theorem/proposition/lemma/corollary proof bodies), the mathematical sections of all six formal supplements, and three valid earlier alternative derivations. Counts include overlapping versions and supporting constructions, not distinct novelty claims. The five physical continuum targets remain open.

## Build

Run from any location:

```sh
python /absolute/path/to/traditional/build.py
```

`build.py` resolves all bundled TeX, bibliography and figure files relative to itself and invokes the installed `pdflatex` and `bibtex`. It uses no network and installs nothing. Deterministic defaults are `SOURCE_DATE_EPOCH=1791244800` and `FORCE_SOURCE_DATE=1`; the caller may override them. Output is the named PDF above and the `build/` logs. Intermediate reference files are cleared before each build so a previously interrupted build cannot supply a truncated auxiliary file.

The expected final build has no warnings, missing references, overfull/underfull boxes or duplicate PDF destinations. The bundled PDF preflight reports embedded fonts, valid internal links and no off-page text.

## Navigation and provenance

- `evidence/FINAL_PAGE_MAP.json`: every result, proof, section and source label mapped to final physical/printed pages.
- `evidence/FINAL_THEOREM_AND_SUPPLEMENT_CROSSWALK.md`: all 19 finite items, all 79 strengthened proof records, and supplement section destinations.
- `evidence/ASSEMBLY_MANIFEST.json`: source hashes, selected mathematical ranges and omitted historical metadata paragraphs.
- `evidence/PROOF_BODY_PRESERVATION.json`: all 104 existing explicit proof bodies match after namespace/anchor/whitespace normalization; three retained alternatives are additional.
- `evidence/CORRECTION_LEDGER.md`: exact mathematical qualifications, historical repairs and semantic reconciliation.
- `evidence/PDF_PREFLIGHT.json` and `BUILD_RESULT.json`: build and PDF checks.

The independent audit also confirms all 151 substantive supplementary display/align blocks are retained. The manuscript's 35 original/strengthened vector figures are included. Their original fonts and plotting styles are preserved.

`assemble.py` is the editorial assembly recipe and expects the read-only recovered corpus at `../source/`. It is not a build dependency: the finished conventional source files and assets under `parts/` and `assets/` are complete. `map_pages.py` regenerates crosswalk/preflight evidence after a build and uses the recovered sources only for the independent proof-body comparison. No raw source is modified by these scripts.

This edition does not claim a new Lean compilation. Recorded 323-declaration/25-module formal evidence belongs to the selected v0.6.0 checkpoint; the broader strengthened prose results are kept separate from that count.
