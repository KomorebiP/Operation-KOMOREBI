# Komorebi Space: Technical Record

Publication edition 1.14.0 · Komorebi P. · 14 October 2026

This record preserves the evidence behind the integrated publication: accepted Lean verification, source identities, theorem correspondence, editorial changes, build results, and visual review. The separate public release contains the complete publication sources, Lean sources, monograph, visual guide, and Lean guide.

## Contents

| Location | Contents |
|---|---|
| `history/Komorebi_Space_Technical_Record_v1.13.0.zip` | The original predecessor technical record, preserved byte for byte. |
| `accepted/Komorebi_Space_Diagonal_Lean_Completion.zip` | The accepted diagonal completion, preserved byte for byte with its original directory structure, proofs, audits, controls, and replay instructions. |
| `publication/Komorebi_Space_Publication_v1.14.0.zip` | The exact accompanying public release, including the books, sources, and verification manifest. |
| `integration/parent_books/` | Predecessor PDFs used for the recorded page comparisons. |
| `integration/records/` | Edition counts, source preservation checks, theorem-map validation, progress ledger, textual changes, and typesetting corrections. |
| `integration/reviews/` | Review reports and the Lean probe used to check the selected theorem map. |
| `integration/build/` | Build logs and reports for `reference_pass`, `final_01`, `final_02`, and `final_03`, together with `integrated_lake_build.log` and `theorem_map_check.log`. |
| `integration/build/rendered_final/` | The final rendered pages retained for review, including all 23 pages of the Lean guide. |

The numbered build directories distinguish successive typesetting runs. The final publication PDFs correspond to `final_03`. Earlier logs and review records retain the source and PDF identities to which their findings apply.

## Verification and scope

The integrated Lake build completed successfully with 3,820 jobs. A separate Lean check resolved all 109 declarations in the selected theorem map with warnings rejected and automatic implicit binders disabled.

The edition contains 160 production modules and four import entrypoints, for 164 source targets. Its source contains 1,846 explicitly written theorem and lemma declarations. The two accepted exported inventories contain 5,321 project declarations, including definitions, instances, structure operations, and generated helpers. The exported count is not a count of distinct mathematical theorems.

All 16 principal analytic result groups identified in the edition's formalization map now have Lean counterparts under their stated hypotheses. The completed diagonal results include the actual infinite Hilbert model and certified tails, the sharp asymptotic over all real budgets, and the literal rounded noise schedule. Independent reviews compare these statements with Proposition 30.1, Theorem 30.2, and Corollary 30.3.

The verification evidence retains two separate audit scopes:

| Accepted audit | Source targets | Exported declarations | Diagnostic controls |
|---|---:|---:|---|
| Preserved general library | 156 | 5,048 | 44: 14 expected successes, 28 elaboration rejections, two axiom-policy rejections |
| Diagonal completion | 8 | 273 | 8: two expected successes, five elaboration rejections, one axiom-policy rejection |

The integrated build and theorem-map check do not constitute a fresh combined replay of those control sets. Recursive axiom dependencies in the accepted audits are restricted to `propext`, `Classical.choice`, and `Quot.sound`. No project axiom or admitted production proof is accepted. The integration preserves the accepted production proof sources.

Coverage applies to the identified theorem statements. Alternate written proof routes, explanatory prose, and illustrations are not automatically separately named formal declarations. This release does not claim to resolve the broader open research targets discussed elsewhere in Operation Komorebi.

## Corrections and reproduction

The accepted diagonal archive retains failed proof attempts, compiler diagnostics, environment failures, and their resolutions. The integration record likewise preserves the first PDF layout findings and the subsequent corrections. These include suppressed spaces in inline Lean expressions and an orphaned final table row. Their corrections changed typesetting rather than mathematical statements or Lean proof terms. The final logs also retain routine underfull-box notices and the Visual Guide’s bookmark-spacing substitutions; neither is described as a warning-free build.

For normal use and rebuilding, start with `lean/README.md`, `lean/lean-toolchain`, and `lean/lake-manifest.json` in the public release. The accepted diagonal archive provides the exact environment identities, strict replay commands, control runner, and documented host compatibility adjustment used for its verification. The historical archive preserves the earlier general-library procedure. Compiler and dependency caches are not bundled.

Use the recorded source and artifact hashes to identify the evidence for a particular revision. Rebuilding in a changed compiler or dependency environment requires a new verification record.

For the final PDF structural and page-comparison check, run `python3 integration/records/verify_final_pdfs.py` with PyMuPDF installed. To reconstruct the source context for other integration scripts, unpack the public archive and place its contents at `integration/publication/`. Existing records retain their original workspace paths as historical provenance.
