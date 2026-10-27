# Paper VII monograph presentation ledger

All nine current retrieved mathematical parts are byte-identical. The editorial work changes the wrapper, reading apparatus, figure presentation, typography, and navigation only.

- The first build found a Hyperref option clash because Bookmark loaded it before the wrapper options. The wrapper now loads Hyperref first, then Bookmark.
- An early atlas build found the letter Å where a calligraphic algebra A was intended. A scoped rendering adapter in atlas_definitions.tex restores the correct mathematical glyph without changing atlas formulas or the protected source parts.
- The finite block-inverse example initially called its positive Schur complement a resolvent at z = 0. The prose now explicitly describes the inverse of H, matching the exact positive fractions. No existing mathematical body was touched.
- The seed-rank figure's full-space annotation touched the bar value 6. The annotation moved left. The exact model data are unchanged.
- Unboxed record anchors could jump to a preceding page. Presentation-only Needspace hooks keep the headings with their anchors. The five unnumbered supplementary statements now receive local phantom anchors. All 147 protected record target pages match their visible records.
- A boxed theorem heading could be isolated at the foot of a page. A wrapper spacing hook keeps theorem and definition headings with the opening of their bodies.
- The first page-map inventory included strong:section:016 from historical assembly metadata. That label is absent from the current retrieved part after the earlier disclosure removal. The current map explicitly excludes that stale metadata entry.
- A local mapper edit caused an indentation error before report output. Correcting the loop indentation restored the full 653-label map.
- Reusing PNG paths could display a cached draft image. Final review uses the fresh qa/final_79283524cb628682 path pinned to the frozen PDF hash. All 153 final pages and 12 full-size detail pages were reviewed.

The historical integration scripts and reports remain under historical_assembly. Current reproduction compiles the authored monograph with build.py and does not rerun historical assembly. Fresh finite checks are separate from inherited formal compiler evidence.
