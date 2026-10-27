# Papers V–VIII: collected-core typography sources

These twelve components were built from the active editable trees in the registered frozen releases: Papers V–VII dated 20 October 2026 and Paper VIII dated 21 October 2026. The archive digests are authenticated against the current freeze register in `SOURCE_PRESERVATION_AUDIT.json`. No earlier scientific edition was substituted and no component required PDF fallback.

| Paper | Traditional | Visual guide | Lean guide |
|---|---:|---:|---:|
| V | 135 | 43 | 58 |
| VI | 155 | 44 | 64 |
| VII | 161 | 42 | 84 |
| VIII | 121 | 34 | 98 |

The 1,039 component pages use the Physics-derived layout with plum headings, mulberry navigation and muted gold accents. P052 and Nimbus Sans provide the serif and navigation fonts; Latin Modern Math and the established code fonts remain in use. Letter paper and 0.87-inch horizontal margins are retained. Visual guides use 0.80-inch top/bottom margins to preserve the original one-unit-per-page layout. The scientific figure assets retain their original colors. Inherited headers and footers are suppressed for the assembled volume's global folios.

## Rebuild

From this directory run `python3 build_all.py --jobs 2`. This is the current portable entry point. It derives paths from its own location, verifies external font versions, runs four XeLaTeX passes and BibTeX where required, and writes components to `compiled/`. It does not run Lean, scientific programs, or source-data generators. TeX Live 2023/Debian was used for the supplied build. Equivalent four-pass build commands produced the final PDFs; the portable wrapper was syntax-checked and its font resolution/hash checks were checked separately.

Install XeLaTeX/BibTeX, URW Base35, Latin Modern and DejaVu fonts. Every component's `MONOGRAPH_FONT_DEPENDENCIES.json` records exact names and digests. Its recorded absolute font paths are provenance, not rebuild requirements. `build_all.py` resolves dependencies with `kpsewhich`. Font binaries are external dependencies; exclude every `fonts/` directory when packaging these sources. The script stages installed fonts locally for compilation.

The earlier adaptation and retry scripts document the editing process; they are not rebuild entry points. `failed_initial/` and `layout_first/` preserve the initial build failures and superseded layout checks. `compiled/` holds the current PDFs. `QA_CURRENT.json` describes the earlier typography-only review; the current book-editing evidence is in the editorial report named below.

## Preservation and navigation

The editable text now includes a conservative book-editing pass. It standardizes chapter introductions and named visual-plate references, replaces opaque release references with explicit mathematical reading references, and relocates the six historical verification narratives from Chapter VIII to its formal companion. Statement and proof environments remain unchanged. The source references on the embedded Chapter VIII atlas have been restored from the matching standalone guide so they survive book-level deduplication.

`book_edit_baseline/` preserves every file before its first editorial change. The original frozen readers and raw source archives are separately preserved in the parent package. `../editorial/book_revision/v_viii_report.json` and the accompanying journals record exact coverage, source hashes, moved records, comparison checks, and the current component builds. Earlier typography-only audits describe their own earlier snapshot; they are not assertions that all current prose is byte-identical to the frozen source.

Plate labels are chapter-qualified (for example, Plate VIII.32); their underlying destination IDs are unchanged. Visual source lines name the chapter and result rather than quoting obsolete standalone page numbers. Explicit frozen-reader locations in formal source ledgers remain archival locators and are labelled accordingly. Book-level page inclusion and global navigation are maintained by the parent assembly.

## Validation

The book revision uses `build_all.py` and, for changed subsets, `rebuild_book_components.py`, which invokes the same build function. The build gate checks command return codes, overfull boxes, missing characters, and unresolved citations or references. `REBUILD_RESULT.json` records the current results. The final editorial report records PDF page counts, SHA-256 hashes, proof preservation, exact visual overlap, destination checks, and representative rendered pages.

The 299 explicit proof environments in edited sources and their theorem-like statement environments were compared byte for byte with the pre-edit baseline. No theorem, proof, Lean identifier, exact code excerpt, or scientific figure was altered. Numerical values in Chapter VIII verification narratives were relocated with those records. This is an editorial validation, not a new Lean execution, computation replay, or mathematical correctness audit.

Paper VII's inherited Latin Modern Math bold-shape substitutions remain documented in `FROZEN_VII_FONT_WARNINGS.json`. Earlier complete visual reviews remain in `qa_current/`; the book pass adds representative previews in `../editorial/book_revision/v_viii_preview/`. Authoring-pass scripts document the sequence of edits and should not be rerun on an already edited tree. The supported reproduction entry point is `build_all.py`.
