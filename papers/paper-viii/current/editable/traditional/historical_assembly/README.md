# Paper VIII final traditional companion

**Packet Operator Algorithms, Exact Compilation, and GPU Realization**  
**Komorebi P. — 6 October 2026**

`Paper_VIII_Traditional_Final.pdf` contains the complete strengthened manuscript, with all 85 numbered records and 56 proof bodies, followed by every substantive mathematical body page of all six formal supplements. Original manuscript item numbers remain unchanged. Appendices A–F retain the later constructive arguments and explicit hypothesis boundaries. Historical audit and pending-status passages are dated checkpoint records, superseded where appropriate by the final v0.6.0 scope.

The latest selected checkpoint records 56 of 56 finite manuscript-proved items under its hypotheses, 392 named theorem declarations in 40 active modules (373 Paper VIII and 19 reused foundation), 66 separate construction audits, and four separately tracked classical inputs. This document build does not rerun Lean or GPU benchmarks. Numerical prototype behavior, classical inputs, exact mathematical objects, and historical timing observations are distinguished explicitly.

## Build

From this directory, using an existing TeX distribution with the required packages:

```text
python build.py
python map_pages.py
```

The builder uses only relative editable source and assets. It runs `pdflatex`, `bibtex`, and three final `pdflatex` passes, removes stale auxiliary state, and writes logs under `build/`. It defaults to `SOURCE_DATE_EPOCH=1791244800` and `FORCE_SOURCE_DATE=1`. It requires the existing TeX programs and packages and does not install or download dependencies. `map_pages.py` additionally requires PyMuPDF and validates physical destinations and source conservation.

`assemble.py` is the retained editorial recipe. It reads the unchanged recovered `../source/` corpus to regenerate manuscript and supplement parts; it is unnecessary for ordinary PDF rebuilds. The portable sources are `Paper_VIII_Traditional_Final.tex`, `parts/`, `references.bib`, and `figures/`.

## Evidence

- `evidence/FINAL_PAGE_MAP.json` and `FINAL_THEOREM_MAP.csv`: final result, proof, section, and physical-page maps, with the current PDF hash.
- `evidence/FINAL_THEOREM_AND_SUPPLEMENT_CROSSWALK.md`: readable manuscript and supplement crosswalk.
- `evidence/PROOF_BODY_PRESERVATION.json`: all 56 manuscript proof bodies retained; 50 unchanged after navigation/whitespace normalization and six explicit, independently reviewed repairs. All six full substantive supplement bodies agree after heading/layout/navigation normalization.
- `evidence/CORRECTION_LEDGER.md`: reasons and a direct raw-original-to-final manuscript diff. The JSON assembly-operation records can include intermediate strings; the direct diff records actual final wording.
- `evidence/BUILD_RESULT.json`, `FINAL_DIAGNOSTICS.json`, `PDF_PREFLIGHT.json`, and `PDF_FONTS.txt`: build, navigation, geometry, glyph, and font evidence.
- `evidence/contact_*.png` and `VISUAL_REVIEW.json`: review of every physical page.

No raw recovered source is overwritten. The separate substantive Lean guide explains formal declarations and evidence replay. The separate visual guide provides worked examples and reading routes through the original and later results.
