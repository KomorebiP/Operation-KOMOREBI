# Komorebi Space publication progress ledger

**Version:** 1.0.0  
**Date:** 10 October 2026  
**Status:** Monograph reader set and source/evidence package completed.

## Authoritative publication baseline

The canonical editable manuscript is `source/Komorebi_Space_Monograph.tex`. It includes the chapters under `source/chapters/`. The two companions share `source/preamble.tex` and the recovered Operation Komorebi publication style. The current source catalogue is generated from `data/claim_specs.tsv` by `checks/build_concordance.py`.

The frozen mathematical inputs are the complete foundation source archive v0.20.0, its replay evidence, the separate focused moving-space source archive v0.32.0, its replay evidence, and the separately identified Hilbert holonomy source. Do not silently replace these with a higher version number belonging to another project.

## Completed in this edition

| Workstream | Result |
|---|---|
| Recovery | Two complete relevant source archives, two corresponding replay archives, and the separately identified Hilbert source recovered. |
| Mathematical exposition | Four-part, seventeen-section monograph with complete definitions, principal proofs, examples, and explicit scope boundaries. |
| Source concordance | 54 principal item IDs. 112 source references resolved for 53 items. One written-only example identified. |
| Integrity | All four archive hashes and CRC checks pass. All 135 source files, counting each tree's root separately, match their own archives and historical source hashes. This is not a deduplicated theorem inventory. |
| Current finite checks | Independent checker: 14,224 assertions. Recovered moving-space checker: 2,767 assertions. Both pass. |
| Visual publication | Fourteen vector figure sources. Main paper uses twelve figures; the visual companion includes all fourteen. |
| Reader set | Monograph 48 pages; visual guide 17 pages; Lean/evidence guide 20 pages. |
| Layout and PDF review | Rendered pages inspected, tables and diagrams checked, reference and overflow warnings cleared, fonts embedded. |
| Handoff | Editable sources, archived evidence, checks, audit logs, build script, hashes, and this ledger included. |

## Important corrections retained in the review record

Two provisional declaration names failed the initial exact-name resolution. They were corrected to the actual declarations `onLimit_comp` and `closed_radius_failure`. A malformed norm token was corrected. The isometric reconstruction estimate was written as an operator-norm upper bound to include the zero-fiber case. A provisional color name prevented one companion build; the actual house color replaced it. An overlong hash line, fragmented contents, and split catalogue entries were corrected during layout review.

Early library retrieval returned irrelevant results or unavailable pagination. Filtered archive metadata retrieval then recovered the actual inputs. The package is not represented as a complete inventory of every historical Komorebi Space release.

## Not executed or not claimed

A new cumulative Lean build and imported-axiom audit were **not run**. The external pinned Lean runtime was not restored. The source trees remain separate, and this edition does not assert that their union compiles. The separately recovered Hilbert source is not assigned verification coverage from the focused archive.

No universal view doctrine, unrestricted semantic essential-surjectivity result, general infinity-stack theory, or unrestricted arithmetic correspondence is claimed. These are mathematical research boundaries, not missing pages in the present monograph.

The dependent-index dyadic reconstruction argument is printed as an explicitly marked proof outline, supported by the identified complete formal source. KS54 is a new written elementary example, not a newly compiled theorem.

## Exact restart point

For publication edits, start from this v1.0.0 package, retain the stable KS identifiers, modify the LaTeX sources and correspondence notes, and run `bash build.sh`. Read `REVIEW_NOTES.md` before changing scope language.

For a new formal-integration block, preserve the four original archives, compare shared modules in the two source trees, select and document a canonical import closure, restore the pinned Lean/mathlib runtime, and run a full build with declaration axiom audits and negative controls. Record that as a distinct formal release, not as a retrospective change to the historical records.
