# Papers V–VIII: collected-core typography sources

These twelve components were built from the active editable trees in the registered frozen releases: Papers V–VII dated 20 October 2026 and Paper VIII dated 21 October 2026. The archive digests are authenticated against the current freeze register in `SOURCE_PRESERVATION_AUDIT.json`. No earlier scientific edition was substituted and no component required PDF fallback.

| Paper | Traditional | Visual guide | Lean guide |
|---|---:|---:|---:|
| V | 135 | 43 | 58 |
| VI | 155 | 44 | 64 |
| VII | 162 | 42 | 84 |
| VIII | 126 | 34 | 91 |

The 1,038 pages use the Physics-derived layout with plum headings, mulberry navigation and muted gold accents. P052 and Nimbus Sans provide the serif and navigation fonts; Latin Modern Math and the established code fonts remain in use. Letter paper and 0.87-inch horizontal margins are retained. Visual guides use 0.80-inch top/bottom margins to preserve the original one-unit-per-page layout. The scientific figure assets retain their original colors. Inherited headers and footers are suppressed for the assembled volume's global folios.

## Rebuild

From this directory run `python3 build_all.py --jobs 2`. This is the current portable entry point. It derives paths from its own location, verifies external font versions, runs four XeLaTeX passes and BibTeX where required, and writes components to `compiled/`. It does not run Lean, scientific programs, or source-data generators. TeX Live 2023/Debian was used for the supplied build. Equivalent four-pass build commands produced the final PDFs; the portable wrapper was syntax-checked and its font resolution/hash checks were checked separately.

Install XeLaTeX/BibTeX, URW Base35, Latin Modern and DejaVu fonts. Every component's `MONOGRAPH_FONT_DEPENDENCIES.json` records exact names and digests. Its recorded absolute font paths are provenance, not rebuild requirements. `build_all.py` resolves dependencies with `kpsewhich`. Font binaries are external dependencies; exclude every `fonts/` directory when packaging these sources. The script stages installed fonts locally for compilation.

The earlier adaptation and retry scripts document the editing process; they are not rebuild entry points. `failed_initial/` and `layout_first/` preserve the initial build failures and superseded layout checks. Only `compiled/` and `QA_CURRENT.json` describe the delivered typography.

## Preservation and navigation

All twelve main document bodies are byte-identical to their frozen editable sources. The only main-file change is a preamble input of `component-layout.tex`. Three generated Lean navigation introductions explicitly call their numeric locators frozen-edition locators. No number, statement, proof, equation, numerical result, Lean excerpt or scientific image was edited. All 54 restored figure PDFs are byte-identical to the selected frozen archive. Exact originals of every edited inherited file are under `before/`, with `CHANGES.diff` and hashes in `SOURCE_PRESERVATION_AUDIT.json`.

The local contents and internal named destinations were rebuilt against current pagination. Fixed page locators in the original prose and navigation tables still refer to the exact frozen traditional reader; this convention appears on each opening page and in the three affected navigation introductions. The collected package supplies `frozen_readers/Paper_<Roman>_Traditional_Final.pdf`. There are no remote-PDF links in these twelve components. The original NIST DLMF URI in Paper V remains unchanged. Local PDF page labels retain the original roman/arabic numbering conventions; the assembly mapping records every numbering reset.

## Validation

Every final build completed successfully. Automated checks cover all 1,038 pages and found zero overfull boxes, missing characters, unresolved references/citations, outside-page text blocks or invalid local destinations. All 163 visual-guide pages were visually reviewed, together with representative covers, contents, mathematics, tables, figures and code pages for all eight traditional/Lean components. Rendered evidence is in `qa_current/` and page selection is recorded in `QA_CURRENT.json`.

Paper VII traditional has three Latin Modern Math bold-shape substitution warnings. The original frozen editable-source build log contains the same three fallbacks; this is documented in `FROZEN_VII_FONT_WARNINGS.json`. No missing glyphs were reported. Ordinary underfull-box diagnostics remain. This is a typography and source-preservation check, not a new proof, scientific computation or Lean validation.

The parent assembly reads `../typeset_v_viii_results.json`; its absolute paths identify the current workspace artifacts. The sources and rebuild entry point are relocatable.
