# Chapters V–VI prose review — SEALED

Proofread in edit mode using `STYLE.md` and `mathbox:proofread-math` with its detailed checklist. American English and the established local mathematical vocabulary were preserved.

## Scope and coverage

Continuous prose review covered the active final traditional bodies, their embedded plate bodies, both active standalone visual guides (including their front matter), both formal companions and all twenty authored companion chapter files, plus the six component cover/locator wrappers. Duplicated plate prose was read in its canonical standalone source and compared with the embedded copy rather than counted as a second independent reading. The exact file inventory and raw token counts follow below.

The 38 reviewed files contain 96,640 whitespace-delimited TeX tokens before editing (96,516 after). This reproducible source-scope count includes formulas, code, and duplicated atlas text; it is not a count of English words read. Removing the two duplicated atlas files leaves 77,494 raw TeX tokens across the remaining reviewed sources.

Displayed mathematics, code/literal regions, dense generated result/import/dependency/navigation tables, diagram/TikZ bodies, and scientific assets were excluded from language editing. The mathematical prose surrounding equations and theorem statements was read in local context. Dormant assembly inputs (`*_corrected.tex`, `traditional/source/*`, and V visual `pages.tex`/`extensions.tex`) are not inputs of the active final traditional/visual TeX and were left untouched. Archives, evidence/check-run trees, generated catalogs, backups, build scripts, the root build map, and scientific assets were not edited.

## Edits and review

208 exact replacement occurrences are recorded sequentially in `v_vi_journal.json`; the full before/after source diff is `v_vi_changes.patch`. Twenty-one active source files changed. Every reviewed source was backed up under `v_vi_before/` before any edit to that file.

Routine edits correct American spellings, a missing plural verb and complete report clause, awkward tense, ordinary internal Chapter references, plate-range wording, inconsistent technical/eponym spellings, and revision-relative evidence narration. Historical counts, toolchains, timestamps, command examples, evidence limits, and open conjecture status were retained. Changed sentences were reread after editing.

One prose quantifier clarification was specifically reviewed and authorized by the root after inspection of the adjacent interpretation and proof: V traditional, Theorem E6.5 / line 2447 changes “the minimum cost of every admissible pruning” to “the minimum cost among all admissible prunings.” The immediately preceding interpretation defines the least cost among all feasible prunings, and the proof exhausts the stop/split cases. No recurrence, symbolic expression, hypothesis, or intended conclusion changed. This exception is explicitly journaled; no other quantifier wording was changed.

No further unresolved objective language issue is recorded in the reviewed scope. This pass makes no new mathematical correctness or literature-verification claim.

## Preservation and validation

`python editorial/prose_review/v_vi_validate.py` passed. It compares each reviewed source against its backup and records hashes and per-file counts in `v_vi_preservation.json`.

- All 5,487 extracted inline/displayed mathematical regions are byte-identical.
- All 219 extracted code/literal regions and inline literal arguments are byte-identical.
- All 1,006 extracted labels, references, citations, input/graphics paths, counters, and bibliography commands are byte-identical.
- Both embedded plate bodies match their standalone active copies after normalizing their intentional caption wrapper names, V graphics-directory prefix, VI group wrapper, and whitespace.
- No Lean source/excerpt, mathematical checker, figure source/data, or image asset was edited. The extraction comparison is a source-preservation check, not a proof audit or full asset-hash audit.
- No build, PDF edit marker, Lean run, or computational theorem check was run. Root coordinates rebuilding after sealing.

## Exact reviewed source inventory

| Source | Raw TeX words before | Edited |
|---|---:|:---:|
| `source_v_viii/V/editable/traditional/Paper_V_Traditional_Final.tex` | 19,439 | yes |
| `source_v_viii/V/editable/traditional/atlas-pages.tex` | 8,839 | yes |
| `source_v_viii/V/editable/visual_guide/Paper_V_Visual_Guide_Final.tex` | 907 | yes |
| `source_v_viii/V/editable/lean_guide/Paper_V_Lean_Guide_Final.tex` | 419 | no |
| `source_v_viii/V/editable/lean_guide/chapters/01_reading.tex` | 882 | yes |
| `source_v_viii/V/editable/lean_guide/chapters/02_addresses.tex` | 729 | no |
| `source_v_viii/V/editable/lean_guide/chapters/03_filters.tex` | 671 | yes |
| `source_v_viii/V/editable/lean_guide/chapters/04_haar.tex` | 585 | no |
| `source_v_viii/V/editable/lean_guide/chapters/05_edges.tex` | 582 | no |
| `source_v_viii/V/editable/lean_guide/chapters/06_trees.tex` | 1,345 | no |
| `source_v_viii/V/editable/lean_guide/chapters/07_cyclic_smith.tex` | 707 | yes |
| `source_v_viii/V/editable/lean_guide/chapters/08_reproduction.tex` | 1,295 | yes |
| `source_v_viii/V/editable/lean_guide/chapters/09_extension.tex` | 396 | no |
| `source_v_viii/V/editable/visual_guide/source/pages_final.tex` | 8,839 | yes |
| `source_v_viii/VI/editable/traditional/Paper_VI_Traditional_Final.tex` | 22,831 | yes |
| `source_v_viii/VI/editable/traditional/atlas-pages.tex` | 10,307 | yes |
| `source_v_viii/VI/editable/visual_guide/Paper_VI_Visual_Guide_Final.tex` | 113 | yes |
| `source_v_viii/VI/editable/lean_guide/Paper_VI_Lean_Guide_Final.tex` | 379 | yes |
| `source_v_viii/VI/editable/lean_guide/chapters/01_reading.tex` | 806 | yes |
| `source_v_viii/VI/editable/lean_guide/chapters/02_semigroups.tex` | 377 | yes |
| `source_v_viii/VI/editable/lean_guide/chapters/03_probability.tex` | 360 | no |
| `source_v_viii/VI/editable/lean_guide/chapters/04_bayes.tex` | 584 | no |
| `source_v_viii/VI/editable/lean_guide/chapters/05_fractional.tex` | 593 | no |
| `source_v_viii/VI/editable/lean_guide/chapters/06_green_paths.tex` | 354 | yes |
| `source_v_viii/VI/editable/lean_guide/chapters/07_memory.tex` | 549 | no |
| `source_v_viii/VI/editable/lean_guide/chapters/08_holomorphic.tex` | 480 | yes |
| `source_v_viii/VI/editable/lean_guide/chapters/09_survival.tex` | 212 | no |
| `source_v_viii/VI/editable/lean_guide/chapters/10_extensions.tex` | 782 | yes |
| `source_v_viii/VI/editable/lean_guide/chapters/11_reproduction.tex` | 1,110 | yes |
| `source_v_viii/VI/editable/visual_guide/source/front.tex` | 420 | yes |
| `source_v_viii/VI/editable/visual_guide/source/pages.tex` | 6,991 | yes |
| `source_v_viii/VI/editable/visual_guide/source/extensions.tex` | 3,311 | yes |
| `source_v_viii/V/editable/traditional/component-layout.tex` | 77 | no |
| `source_v_viii/V/editable/visual_guide/component-layout.tex` | 82 | no |
| `source_v_viii/V/editable/lean_guide/component-layout.tex` | 64 | no |
| `source_v_viii/VI/editable/traditional/component-layout.tex` | 77 | no |
| `source_v_viii/VI/editable/visual_guide/component-layout.tex` | 82 | no |
| `source_v_viii/VI/editable/lean_guide/component-layout.tex` | 64 | no |

SEALED: no further source mutations by this reviewer after the preservation report.

## Root-requested terminology follow-up — RESEALED

The root requested a final ordinary-narrative paper/article terminology pass before rebuilding. Forty-seven exact replacement occurrences are recorded in `v_vi_terminology_journal.json` and `v_vi_terminology_changes.patch`, with a phase checkpoint in `v_vi_terminology_before/`. Current narrative now uses chapter or, in the E-prefixed extended development, this part so the local organizational referent remains exact. The root-specified V1488 revision-chatter rewrite was applied verbatim; the following Eleven foundational... sentence is unchanged. Exact document titles, metadata labels, historical cross-paper counts, source paths and frozen-reader locator wording remain preserved. Changed sentences were reread; all protected spans and both duplicated plate-body comparisons passed again. No build ran.

A separate explicitly authorized one-sentence VIII traditional abstract correction is recorded in `viii_terminology_followup.json`, with its own pre-edit backup and unchanged mathematical/literal-span comparison. The V–VI 38-file counts do not include that VIII file.
