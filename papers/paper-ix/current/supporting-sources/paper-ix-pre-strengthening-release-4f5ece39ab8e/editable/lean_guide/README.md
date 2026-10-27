# Paper IX Lean guide — final companion

Author: Komorebi P. Final date: 6 October 2026.

The 120-page guide contains 11 instructional chapters, 47 exact contiguous Lean excerpts (623 raw source lines), the full 1,876-row named declaration/source-version catalog under 199 canonical source files, the 55-module latest polynomial dependency map, and a crosswalk for all 62 consolidated manuscript statements / 202 source links. The traditional paper pin is SHA-256 `62eea0640e249562e94211724b610b901925e9ee8ea8c5abfdab9a6d04dabe40`.

`Paper_IX_Lean_Guide_Final.tex`, `preamble.tex`, `chapters/`, `generated/`, and `excerpts/` are sufficient to rebuild the PDF:

```sh
python3 build.py
```

The isolated XeLaTeX builder uses `SOURCE_DATE_EPOCH=1791244800` and needs no raw snapshot or Lean runtime. The final PDF's two isolated builds are byte-identical. Its exact hash and page count are in `qa/DOCUMENT_QA.json`.

Source-dependent preparation is separate from PDF compilation:

```sh
python3 audit_sources.py --source /path/to/PRSC_IX_Consolidated_Manuscript
python3 prepare.py --source /path/to/PRSC_IX_Consolidated_Manuscript
python3 build.py
python3 refresh_navigation.py --traditional /path/to/final/traditional
python3 build.py
python3 verify_guide.py --source /path/to/PRSC_IX_Consolidated_Manuscript
```

`prepare.py` restores the raw excerpt selections, basic manuscript chapter destinations, catalogs and frontier table. `refresh_navigation.py` binds the navigation to the frozen traditional PDF and resolves actual guide printed and physical pages. The copied direct-dependency table and `audit/DEPENDENCIES.json` preserve the latest 55-module imports; they were independently checked against raw source and are acyclic. A new source revision requires a new review, source binding and dependency-table regeneration before publication.

The audit freshly reconciles 15 inherited frontiers, 644 source hashes, 713 recorded log hashes, and four legacy affine log fingerprints. The latter four had no digest in their original run report and retain that limit. Latest regularity evidence contains 55 proof modules, eight positive support modules, thirteen statement contracts, and twelve negative controls. Its 515 named audits include 415 theorem commands (322 proof-source, 61 control, 32 contract), 92 definitions and eight abbreviations.

No Lean/Lake compiler was available or executed in this final edition. The compiler/theorem rejection evidence remains inherited. The unchanged Python declaration/axiom parser regression was actually rerun. The active bounded static-source replay is `audit/static_bound_release_run/manifest.json`; the original workspace-root predecessor is preserved, explicitly superseded for path-metadata packaging, in `audit/STATIC_AUDIT_RUN_STATUS.json`. Never rewrite a historical manifest or treat this static run as a fresh kernel run.

`audit/EXCERPTS.json` records exact original source paths, hashes and line ranges. The `.lean.txt` assets retain actual source characters. `.render.txt` only escapes Verbatim command characters and uses math-font glyphs for U+1D4DD and U+1D55C, which the monospaced font lacks; raw source text is unchanged.

The Bernoulli restoration has a classical derivation but no matched dedicated Lean bridge. Native presentation invariance, global/completed compatibility, general singular persistence, and the listed arithmetic extensions remain open. Formal coverage does not extend automatically to all preserved historical texts.
