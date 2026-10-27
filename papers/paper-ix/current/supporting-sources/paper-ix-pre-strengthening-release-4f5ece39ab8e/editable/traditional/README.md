# Paper IX traditional final edition

Author: Komorebi P. Final edition: 6 October 2026.

Build the final PDF with `python3 build.py` from this directory. This requires an already installed pdflatex distribution and performs no downloads. The root TeX and all component sources are bundled using relative paths. The current mathematical core, full continuation derivations, complete restricted native prose proofs, reconstructed historical manuscript, and eleven complete checkpoint supplements are included.

The current 54 proof blocks and reconstructed historical 82 proof blocks remain. The two current edited proof bodies receive explicit flatness/extraction exposition or a primary Bernoulli source citation. The historical body has five substantive repaired issues, as well as typing/index conventions and local superseded-status notices. Its 14 figure source assets and exact bibliography file remain unavailable; the original captions and 22 citation keys have transparent unavailable-record notices. The exact original July TeX bytes remain unavailable.

`evidence/FINAL_PAGE_MAP.json` resolves all final labels to physical and printed pages. `FINAL_STATEMENT_CROSSWALK.json` preserves the inherited 62-statement/202-source-link map and adds final locators. The assembly manifest and preservation reports distinguish original source hashes from editorial outputs. The mathematical audit and bounded computation reports live in the enclosing edition.

`assemble.py --source-root /absolute/path/to/PRSC_IX_Consolidated_Manuscript` reassembles these TeX fragments from the preserved authoritative collection, using installed Pandoc. `qa.py --source-root /absolute/path/to/PRSC_IX_Consolidated_Manuscript` independently checks proof and supplement conservation, labels, PDF links and bounds, and generates contact sheets. These review scripts require the raw source collection; `build.py` requires only this bundled editable directory.

Lean/Lake were unavailable for this edition. Preserved accepted compiler logs and exact source records supply the inherited Lean evidence. Fresh integer/Fraction finite checks are reported separately and do not certify infinite p-adic limits or analytic regularity.
