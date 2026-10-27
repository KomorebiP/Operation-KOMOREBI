# 10 October 2026 release addendum

This companion retains all mathematical text from the 9 October edition.
The current build resolves installed fonts into a disposable build directory.
It does not download or install dependencies, and no standalone font binaries
are distributed. See `FONT_DEPENDENCIES.json` and the release root
`BUILD_AND_REPLAY.md`. The older build records below remain historical.

The release rechecks the exact source excerpts and body-content sequence.
Pagination within the Lean guide has small line-break changes compared with
the predecessor, while its 94-page count and content are preserved. Current
output hashes belong to `EDITION.json` and `verification/RELEASE_CLOSURE.json`.

---

# Paper VIII visual guide, monograph edition

Author: Komorebi P. Edition date: 9 October 2026.

The maintained entrypoint is `Paper_VIII_Visual_Guide_Final.tex`. The separate guide has a cover, one reading page, and all 32 worked pages. It supplies all 30 editable TikZ vector plates. Two title coordinates were adjusted to avoid crowded labels. Original copies are retained in `historical_assembly/graphics`. Mathematical node labels are unchanged.

Run `python build.py` in this directory. The builder copies the complete source tree into an isolated temporary directory and runs four XeLaTeX passes. Bundled font files, styles, and figure sources make the typesetting reproducible. It does not regenerate examples, source text, figures, or computation evidence. Use `--check-only` for a read-only build, or `--output-directory PATH` for separate compiled products. XeLaTeX is required.

Model and scientific checking code are preserved. Fresh exact, symbolic, vector-generation, and finite replay evidence belongs to the separate run manifests in the release verification directory. Earlier compilation and computation reports are retained as dated evidence in `historical_assembly` and `provenance`. They are not the current PDF layout audit.

`SOURCE_CROSSWALK.json` records the traditional targets for each worked page. `VISUAL_TO_TRADITIONAL_CROSSWALK.json` pins both current PDFs and the final traditional page map, with actual printed and physical page labels recorded separately. `source/update_crosswalk.py` maintains reading references without changing formulas.

`verification/monograph_visual_report.json` at the release root records final source/formula preservation, current build and layout inspection, vector identities, and evidence limitations. The inherited finite Lean contract, four classical inputs, numerical software tests, and historical device measurements remain distinct evidence layers. No fresh Lean compiler run or new hardware timing is claimed.
