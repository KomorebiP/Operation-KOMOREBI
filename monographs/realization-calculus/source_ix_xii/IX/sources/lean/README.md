# Euler Congruences — final strengthened Lean guide

Author: Komorebi P. Current release: 20 October 2026. Mathematical baseline retained from the October 10 reading edition.

This guide adds a current claim/coverage chapter to the complete retained Paper IX Lean companion. It distinguishes the compiled historical Nishibuchi completion, the already formalized N=4 all-row/common-step congruences and sharp first-period/isometry results, and the new general-modulus, mixed factorial, higher exactness and analytic-radius proofs that do not yet have compiled Lean endpoints.

The retained guide contains eleven teaching chapters, 47 exact contiguous Lean excerpts comprising 623 raw source lines, the full 1,876-row declaration/source-version catalog under 199 canonical source files, the latest 55-module polynomial dependency map, and a crosswalk for 62 preceding-manuscript statements / 202 source links. The current opening is a twelfth instructional chapter. The current crosswalk resolves all 62 entries against the 232-page final monograph and its current SHA-256. The 202 original formal source links remain unchanged; guide locators resolve in this 139-page reader.

## Build the PDF

From this directory:

```sh
python3 build.py
```

The isolated builder uses XeLaTeX, `SOURCE_DATE_EPOCH=1791590400`, the copied chapters/generated tables/excerpts and packaged publication style, and no Lean runtime. It writes `Paper_IX_Lean_Guide_Final.pdf` here and build logs under `qa/`. `preamble.tex` uses the P052, DejaVu and Latin Modern fonts recorded in the build. Do not substitute pdfLaTeX for XeLaTeX. See the root `FONT_DEPENDENCIES.txt` for the external font requirements and tested selectors.

## Repeat the static evidence review

From this directory in the final package:

```sh
python3 audit_sources.py \
  --source ../../preserved/PRSC_IX_Consolidated_Manuscript \
  --output audit/a_new_static_run
python3 verify_guide.py \
  --source ../../preserved/PRSC_IX_Consolidated_Manuscript
```

The catalog source paths are relative to that preserved root. A path containing `!` identifies an exact ZIP member. The 0.11.0 Nishibuchi completion sources are preserved within the baseline ZIP; later width-four all-row/period/isometry endpoints are under `strengthening/formalization`.

The fresh static reconciliation in `audit/current_reconciliation/` matched 15 inherited frontiers, 644 source hashes, 713 recorded log hashes, all 202 source links, the catalog, and 515 exact strict axiom records at the latest polynomial frontier. The unchanged Python declaration/axiom parser regression was rerun. Twelve retained negative-control logs retain matching recorded rejection diagnostics. Four older affine logs lack a digest in their original report and retain that limit. Historical compiler evidence and old document QA are retained separately; old document hashes and counts do not describe this revised PDF.

No Lean or Lake executable is present and neither was executed for this guide. Historical compilation records use Lean 4.34.0-rc2 and pinned Mathlib revision `aeb72f1e9981b6d35b426b16dca7759be3e7ba06`. The new paper's proof audits and bounded exact computations do not count as new kernel compilation. This release adds no `.lean` proof files and no placeholder theorems for the new results.

The raw `.lean.txt` excerpt assets retain their original source characters. Display `.render.txt` assets only adapt verbatim escaping and otherwise unsupported glyphs; the raw Lean proof files are unchanged. `audit/EXCERPTS.json` records original locators, hashes and ranges. The complete guide verifier checks all 47 excerpt identities, their unique teaching uses, catalog identifiers present in the PDF, embedded fonts, cross-references and layout warnings.

The current chapter does not close unrestricted native presentation invariance, completed/global compatibility, singular persistence, or a universal exact higher-order law for addresses two and three. Previously proved and still open arithmetic subfamilies are separated in the main paper's final theorem register.
