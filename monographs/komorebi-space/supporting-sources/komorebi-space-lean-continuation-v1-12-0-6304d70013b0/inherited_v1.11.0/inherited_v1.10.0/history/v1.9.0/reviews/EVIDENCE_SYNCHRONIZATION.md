# Evidence synchronization and proofreading review

Scope: the five assigned LaTeX files were read in full. This was conservative proofreading and synchronization of publication status to the already accepted v1.8.0 formal continuation. No Lean source, theorem proof, compiler record, axiom export, or verification receipt was changed.

## Accepted evidence used

- `continuation/VERIFICATION_SUMMARY.json`, status PASS.
- `continuation/FORMAL_COVERAGE.json`, status PASS, including the actual exported types for the principal WR01, WR02, and protected-bridge clauses.
- The accepted source files in `continuation/formal/KomorebiSpace/` were read to distinguish the formal proof route from the written route.
- `continuation/integration/verification_summary.json` supplies the lexical total of 1,580 explicit theorem/lemma declarations and the separate generated-declaration counts.

## Current status recorded

| Layer | Scope retained in the text |
|---|---|
| Historical v1.2.0 core | 138 production modules, one root, 4,745 audited declarations, 1,507 explicit theorem/lemma declarations. |
| Historical v1.6.0 focused replay | Seven source targets, 223 audited declarations including 97 in the three then-new modules, and 51 new explicit theorem/lemma declarations. |
| Accepted v1.8.0 clean baseline | 141 production modules and three roots, 144 clean compilation targets, 4,842 audited declarations. |
| Accepted v1.8.0 incremental addition | Three new production modules and changed combined root compiled over the verified baseline objects. |
| Accepted final cumulative scope | 144 production modules, three roots, 147 source targets, 4,872 audited declarations. This is not described as a second empty-build compilation of all final targets. |
| Current WR catalogue | Six complete groups, WR01/WR02/WR06/WR07/WR13/WR14; two partial groups, WR09/WR16; eight written-only groups, WR03–WR05/WR08/WR10–WR12/WR15. |

Historical macro meanings were preserved. New `EditionCumulative*`, `EditionContinuation*`, and `EditionWR*` macros carry the later counts. In particular, `EditionWrittenOnly=0` remains the KS catalogue count and must not be interpreted as the WR count.

## Declaration map added to Appendix 11

Namespace prefixes are stated once in the printed appendix. Compact tables identify the following exact public declarations. Full Lean types remain in the evidence JSON rather than filling the monograph with a large type dump.

| Printed clause | Accepted public declaration |
|---|---|
| WR01: budget preserving existence | `KomorebiSpace.BoundedApproximateRealization.exists_solution_of_bounded_residual_tendsto_zero` |
| WR01: equivalence | `KomorebiSpace.BoundedApproximateRealization.mem_range_iff_bounded_approximation` |
| WR01: escape | `KomorebiSpace.BoundedApproximateRealization.norm_tendsto_atTop_of_not_mem_range` |
| WR02: construction | `KomorebiSpace.NestedMinimumCorrections.affineCorrections_spec` |
| WR02: monotone | `KomorebiSpace.NestedMinimumCorrections.nested_affine_norm_monotone` |
| WR02: finite energy | `KomorebiSpace.NestedMinimumCorrections.nested_affine_energy` |
| WR02: equivalence | `KomorebiSpace.NestedMinimumCorrections.nested_affine_intersection_iff_bounded` |
| WR02: strong limit unique minimum and limit energy | `KomorebiSpace.NestedMinimumCorrections.nested_affine_strong_realization` |
| WR02: escape | `KomorebiSpace.NestedMinimumCorrections.nested_affine_escape` |
| protected_bridge: same budget exact protected candidate | `KomorebiSpace.ProtectedBoundedRealization.exists_exact_repair_of_bounded_approximation` |

The text preserves the real Hilbert hypotheses, the same correction budget in WR01, the actual protected kernel, and the explicit nonempty/closed/affine/nested assumptions in WR02. It explains that the formal WR01 route uses weak-star compactness and Riesz identification, whereas the printed proof uses weak subsequence selection. It does not claim that the printed weak-subsequence lemma itself received a separate formal counterpart. The WR02 affine equality is distinguished from the general convex energy inequality.

## File-by-file review

| File | Work completed |
|---|---|
| `source/chapters/07_concordance.tex` | Read the full notation table and prose. Clarified one notation-table phrase, updated six/eight/two coverage, preserved historical replay scopes, added the accepted cumulative and incremental records, and corrected historical package paths. |
| `source/chapters/11_written_extensions.tex` | Read all sixteen group descriptions. Updated WR01 and WR02 evidence, added the ten-clause public declaration map, preserved the remaining limit/diagonal/basis boundaries, retained the parent’s explicit WR15 coordinate convention, and identified numerical suite counts as retained v1.7.0 results. |
| `source/edition_stats.tex` | Read every macro. Retained all historical values and added separate cumulative/continuation/WR macros. Added comments preventing KS/WR and core/cumulative count conflation. |
| `source/written_status.tex` | Read all sixteen labels. Updated WR01–WR02 and current cumulative wording while retaining written-only and partial classifications. |
| `source/claim_table.tex` | Read all eighty rows. No changes needed. Verified unique ordered KS01–KS80 anchors and retained source-module mappings. |

## Mathematical-token policy

This agent did not alter an inherited theorem statement or proof. During coordination, the parent added the explicit orthonormal ambient/residual coordinate convention to the WR15 summary. That clarification is retained: ordinary transpose formulas must not be read as formulas for arbitrary weighted ambient coordinate systems. The new protected-bridge summary adds the already accepted conclusion `Dy=0`, `py=pf`, `norm(f-y)<=M`, transcribed from the exported type. All other mathematical work in this edit concerns status descriptions and exact declaration names, not new theorem development.

## Validation

- Balanced LaTeX environments and unescaped brace nesting in all five files.
- Verified exactly eighty unique KS anchors in unchanged order.
- Verified all ten principal public declaration names from `FORMAL_COVERAGE.json` appear in the appendix map.
- Checked the historical core macros remain 138 / 4,745 / 1,507 and the new cumulative/status macros agree with accepted evidence.
- Re-read both edited appendices in full after changes.
- Full-document typesetting and rendered-page review are owned by the coordinating publication build. At this review checkpoint, that rendering has not yet been inspected by this agent. In particular, the new compact declaration tables need the final visual pass.

## Findings outside assigned ownership

The initial scan found stale status statements in the monograph frontmatter, chapter 05f, and chapter 06. Those were reported to their owners. A later read-only scan showed the frontmatter and chapter 06 updated and the old chapter 05f written-only sentence removed.

The copied sources `source/Komorebi_Space_Visual_Guide.tex` and `source/Komorebi_Space_Lean_Guide.tex` still contain v1.7-era four-complete/ten-written-only wording and WR01–WR02 written-only entries. They are outside this assigned scope. If they are retained only as historical companion sources, their version and status should remain explicit; if they are rebuilt as current companions, they require separate synchronization. The parent has been notified.

The preamble comments about generated statistics and focused WR records were reported to the parent, who owns the preamble. No generator or evidence file was modified here.

## Reviewed file hashes

| File | SHA256 at this checkpoint |
|---|---|
| `source/chapters/07_concordance.tex` | `54b8d2905e8014d1f6f79a48dbe6f82a83b3c6634fa84f08e9a45ac17b6aacba` |
| `source/chapters/11_written_extensions.tex` | `4f1955f6b03f266ef50fd30a17a071052f2226349cd1a119a2464d2c62b6de2c` |
| `source/edition_stats.tex` | `56430d63d26792d799a90edbbb0c074c109c4f1180d65c2c3c4136978a525fa8` |
| `source/written_status.tex` | `8b58be5ee58279f83d70410082f47ef522ab2d3686730d04e3afd279adefaa1d` |
| `source/claim_table.tex` | `a1b4b8b3b8832e5c07f42d93473853d45296b6b049d26fb886bfb5b15567704e` |
