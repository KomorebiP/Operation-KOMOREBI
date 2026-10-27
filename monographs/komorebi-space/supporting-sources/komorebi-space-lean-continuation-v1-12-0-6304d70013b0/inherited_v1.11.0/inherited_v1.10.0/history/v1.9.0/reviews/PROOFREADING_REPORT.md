# Consolidated monograph proofreading report

Edition: **Komorebi Space Monograph v1.9.0**. Review date: **12 October 2026**.

**Textual scope completed:** all 29 chapter/appendix source files, the main frontmatter, notation and source concordance, all 80 KS catalogue rows, the sixteen WR status descriptions, bibliography, edition macros, and figure text. All 40 numbered figure sources were reviewed; 38 are included as plates in the monograph. Figures 13 and 14 belong to the retained Visual Guide and were reviewed as figure sources without expanding the claim to a fresh proofreading of that guide.

The work is a complete conservative mathematical proofreading pass over this monograph, with focused checks of the local mathematical issues recorded below. It is **not a new global theorem-by-theorem referee audit**. It introduces no new theorem or formalization. Accepted v1.8.0 Lean evidence is incorporated with its original scope. The old Visual Guide and Lean Guide remain historical companions and were **not newly proofread in full or recertified as current v1.9.0 guides**.

## Final publication acceptance

**Accepted:** the complete 166-page PDF, including its cover and frontmatter. All 166 pages of the first final candidate were visually inspected. The final layout changed thirteen pages; all thirteen were reinspected, and the other 153 final pages are pixel-identical to the inspected pages. The mapping and report hashes are in `audit/FINAL_VISUAL_COVERAGE.json`.

| Final-artifact field | Result |
|---|---|
| Final PDF page count | **166** (cover, four roman-numbered frontmatter pages, and body pages 1–161) |
| Final PDF SHA256 | `c206ccac893366e2747126e584cf9ca9a4131a051e54d8c6109b3b220a44ece4` |
| Final build | `audit/final_candidate_02/receipt.json`: three successful pdfLaTeX passes; final source hashes unchanged during build |
| Final structural check | `reviews/STRUCTURAL_CHECK.json`: PASS; zero reported issues |
| Final rendered-page acceptance | PASS; every final page covered by direct inspection or exact pixel identity with an inspected page |
| Typesetting diagnostics | No unresolved references, overfull boxes, missing glyphs, or blocking font/package warnings; thirteen underfull-line diagnostics retained and visually reviewed |
| Fonts and page geometry | All reported fonts embedded; no extracted words outside page bounds; no rendered unresolved-reference markers |

The earlier full draft had 166 pages and SHA256 `bf3ede62b24958ddc4cc5e52516c2aa7bdff73d4ff84ca5e7c23797095110a85`. Draft reports retain their original findings. Final acceptance follows the final review mapping rather than treating a draft result as final evidence.

## Coverage and supporting records

Each chapter file in the following inventory was read in full by its assigned reviewer, including statements, proofs, examples, displays, captions, local references and scope statements. This inventory counts source files, not the larger number of numbered sections produced by them.

| Source files under `source/chapters/` | Review record |
|---|---|
| `01_views.tex`; `02_obstructions.tex`; `02a_prescription.tex`; `03_towers.tex`; `03a_observation.tex`; `03b_repair_transport.tex` | `PROOFREAD_FOUNDATIONS.md` — six files |
| `04_symmetry.tex`; `04a_boundary_lab.tex`; `04b_phase.tex`; `05_geometry.tex` | `PROOFREAD_SYMMETRY_GEOMETRY.md` and checks JSON — four files |
| `05a_certificates.tex`; `05b_transport_cost.tex`; `05c_iteration.tex`; `05d_floors.tex`; `05e_escape.tex`; `05f_bounded_realization.tex`; `05g_budget_certificates.tex`; `05h_regularized_repair.tex`; `05i_diagonal_regularization.tex`; `05j_inexact_certificates.tex`; `05k_stopping_rules.tex` | `PROOFREAD_ANALYTIC_EXTENSIONS.md` — eleven files |
| `06_cases.tex`; `06_boundaries.tex`; `09_workshop.tex`; `10_hypothesis_atlas.tex`; `12_proof_tools.tex` | `PROOFREAD_WORKSHOP_APPENDICES.md` — five files |
| `07_concordance.tex`; `11_written_extensions.tex` | `EVIDENCE_SYNCHRONIZATION.md` — two files |
| `08_references.tex` | Coordinating editorial pass; current complete bibliography reread for this consolidation — one file |

Additional coverage includes `Komorebi_Space_Monograph.tex` (cover/frontmatter, reading routes, contents inputs and evidence account), the preamble and local publication macros, `edition_stats.tex`, `written_status.tex`, and `claim_table.tex`. The condensed current frontmatter and all ten bibliography entries were reread during consolidation. Local citation keys, source paths, edition scopes and consultation-date wording were checked; this is not a fresh external literature audit.

`STRUCTURAL_FIGURE_REVIEW.md` records all 40 figure sources individually. `BUDGET_FIGURE_CORRECTION.md` records the isolated figure-32 legend correction, unchanged geometry and visual comparison. The `VISUAL_PAGES_*.md` reports identify the actual rendered pages inspected and their draft-bound findings. Reviewer source hashes are checkpoints; later coordinated layout edits do not silently inherit those hashes.

## Significant mathematical corrections and clarifications

These changes affect mathematical wording, hypotheses or proof-branch validity and are disclosed separately from grammar. They were checked locally against the surrounding proof and, where available, the cited frozen Lean source. No proof was replaced by a new argument.

| Location | Correction and reason |
|---|---|
| `01_views.tex`, view-system variance | A functor with domain `Vᵒᵖ` is now called a functor, removing the double variance description “contravariant functor from Vᵒᵖ”. The original restrictions and functor laws are retained. |
| `02_obstructions.tex`, independence of lift | “The two quotients agree” became “the two quotient classes agree”; the proof compares classes in one fixed quotient group. |
| `03_towers.tex`, KS23 | The identity-tower counterexample is explicitly a **real scalar** example, matching the archived formal statement and the Archimedean growth argument. |
| `03_towers.tex`, KS27 | The already present **K=0 branch is handled before** multiplying a strict approximation inequality by K. The remaining branch explicitly assumes K>0. The theorem still includes zero bounds. |
| `03b_repair_transport.tex`, KS66 | The presentation changes are explicitly **bounded linear maps**, matching the actual `ContinuousLinearMap` fields used in the commuting-square and chart proofs. Arbitrary bounded nonlinear maps would not justify the expansions. |
| `05_geometry.tex`, KS45 | The scalar-chain residual equality is restricted to **n≥1**; strict failure of the route-length estimate is stated for **n≥2**. At n=0 there are no edges and the residual norm is zero; at n=1 the competing bounds agree. |
| `05_geometry.tex`, KS46–KS47 | Both defect maps **D and C are explicitly continuous linear maps** into Banach spaces. The closed linear kernels, restrictions and operator-norm estimates require that input and match the cited Lean types. |
| `05h_regularized_repair.tex`, `05k_stopping_rules.tex`, and WR15 appendix summary | The matrix formulas use **orthonormal coordinates in the ambient candidate and residual spaces**, while the full independent kernel basis B remains arbitrary and need not be orthonormal. This makes ordinary transposes represent the appropriate adjoints. The formulas `G=BᵀB`, `g=BG⁻¹q` and `‖g‖²=qᵀG⁻¹q` must not be read as formulas for arbitrary weighted ambient coordinates. The focused audit supplies an exact one-dimensional weighted-metric counterexample to that unrestricted reading. Abstract Hilbert statements and the original Euclidean examples are unchanged. |
| `05j_inexact_certificates.tex`, WR14 | Equality is explicitly at **both optimizers**, `a=a_α` and `z=z_α=r−Ta_α`. Choosing only the optimal dual witness does not make equality hold for an arbitrary primal proposal. The existing proof already imposed both values. |
| `05f_bounded_realization.tex`; `05j_inexact_certificates.tex`; workshop 14 | Positive-index conditions **n≥1** are explicit where reciprocal powers occur. The attainable-diagonal paragraph now says “correction coordinate n” and writes the operator on u, separating the coordinate index from the earlier minimum-correction sequence notation. |
| `06_cases.tex`, reflection caption | “All vectors” became **“all nonzero vectors”** when asserting a nonzero coherent family; the zero anchor yields the zero family. |
| `06_boundaries.tex`, KS57 | “Every answer is y+H” became **“The full answer set is y+H”**. The rank-nullity proof uses the already declared field K in both source and target instead of introducing an undeclared alternative symbol. |
| `10_hypothesis_atlas.tex`, sharp budget exclusion | “A unit dual witness” became **“a dual witness in the unit ball”**, preserving the admissible zero witness in the zero-residual case. |
| `12_proof_tools.tex`, inverse example | The stated endpoints `(ker D)⊥ → ran D` are attributed to **the map to be inverted**, not to its inverse. |
| Figure source 32 / draft Figure 28 | The plotted ellipse is **reachable images** `T(B_M)`, not translated fit residuals `r−T(B_M)`. Only the legend was changed from “Reachable residuals at the fixed budget” to “Reachable images at the fixed budget”. Parameters, geometry, sampling and all other plot pixels outside the legend region were retained. |

The focused checks do not imply that all unedited proof steps have undergone an independent referee audit. The principal statement-block and display-preservation checks in the component reports have their stated local scopes; they are not used to conceal the explicit hypothesis corrections above.

## Grammar, typography, references and presentation

Routine edits corrected a missing article/noun in “a continuous linear map”, the “two element set” noun phrase, a missing sentence-ending period after a display, and the prose “exact identity” for a display containing an inequality. KS73 is referred to as a proposition, matching its declared environment. Workshop headings 10–15 now match the first nine headings. A literal underscore escape was removed from a path passed through the detokenizing `code` macro.

Historical file references now identify the `inherited_v1.7.0/` package location, including the historical claim ledger, replay receipts, evidence archives and atlas data files. The first-draft atlas path finding has been corrected in current source. Current formal-source and accepted-continuation paths retain their appropriate `formal/` and `continuation/` roots. The frontmatter was condensed while retaining the distinctions among printed proofs, numerical evidence and formal declarations.

Figure source `07_cover.tex` has its “Three views” and “Four views” titles moved above the curved composition arrow after the first render exposed a title/arrow collision. Both corrected figures passed final in-document visual inspection. The isolated corrected budget figure was also built twice deterministically and inspected directly.

## Accepted formal and finite evidence: preserved scope

This publication work **did not rerun Lean or the finite Python suites**. The retained aggregate of **197,482 finite checks** is a historical result, not 197,482 new v1.9.0 checks. Likewise the retained regularization and inexact-certificate suite totals, 34,388 and 18,728, are not newly executed in this edition. Rebuilding a figure after a text-label change does not count as rerunning those mathematical evidence suites.

The accepted v1.8.0 records remain the basis for current formal coverage:

| Evidence layer | Exact scope |
|---|---|
| Clean cumulative baseline | **144 targets** from an empty project build: 141 production modules and three roots; **4,842** audited project declarations. |
| Incremental continuation | **Four freshly compiled targets**: three new production modules plus the updated combined root, using verified inherited objects. |
| Final cumulative environment | **144 production modules + three roots = 147 source targets**; fresh full-environment audit of **4,872 declarations**; 1,580 explicit theorem/lemma declarations. Generated/auxiliary declarations are included in the audit count, so it is not a count of independent mathematical results. |
| Controls | Four positive regression files, fourteen compiler-rejection files and two policy-rejection files met their specified outcomes. |
| Complete WR groups | **Six:** WR01, WR02, WR06, WR07, WR13, WR14. |
| Partial WR groups | **Two:** WR09, WR16; the pointwise estimates are formal, while the separate limiting consequences retain written status. |
| Written-only WR groups | **Eight:** WR03–WR05, WR08, WR10–WR12, WR15. |

The publication does not describe the incremental continuation as a second clean rebuild of all 147 final targets. Historical core counts (138 modules, 4,745 audited declarations and 1,507 explicit theorem/lemma declarations) retain their original meanings; new cumulative macros carry the later counts. The historical `EditionWrittenOnly=0` macro concerns the KS catalogue, not the sixteen WR groups.

Appendix D maps ten principal WR01, WR02 and protected-bridge clauses to exact public declaration names. Full types remain in `continuation/FORMAL_COVERAGE.json`. WR01's formal proof uses weak-star compactness and Riesz identification; this does not assign separate formal coverage to the printed weak-subsequence lemma or its proof route. WR02 retains explicit nonempty closed affine nested sets in a common real Hilbert space, and distinguishes affine energy equality from the general convex inequality. The protected bridge retains the actual kernel subtype and the same correction budget.

The accepted compiler, kernel and pinned external dependency caches remain trusted. No independent mathlib source rebuild, proof of equivalence between the Python code and Lean definitions, or new external novelty claim is made.

## Checks, failures and resolved layout work

The completed source passes reread changed passages in context, resolved local references and citation keys, and checked braces, environments and explicit mathematical delimiters. The structural checker recognizes literal inputs plus this project's plate/source macros and excludes historical guides from the monograph reference graph. It is a lexical checker, not a TeX interpreter.

At the final frozen-source checkpoint `2026-10-12T20:40:08.693416+00:00`, `STRUCTURAL_CHECK.json` reports PASS with 73 closure files/input occurrences, 38 monograph plates, 40 figure sources, 317 labels, 107 reference occurrences, 80 KS targets and 80 links, ten bibliography keys, twelve citation occurrences, thirty referenced PDF graphics and zero reported structural issues. `audit/SOURCE_CHANGES.json` and `audit/MANUSCRIPT_CHANGES.diff` bind and disclose the revised source. The three historical companion-driver files are omitted from the new monograph source directory but preserved unchanged under `inherited_v1.7.0/source/`.

Failures and corrections are retained explicitly:

- The first coordinating PDF command used the wrong output-directory location. `audit/build_attempt01.log` records failure to write `Komorebi_Space_Monograph.log`, an emergency stop and no PDF. The path was corrected; `audit/build_attempt02.log` records a successful PDF build. The failed command is not counted as a successful check, and the subsequent full draft and layout passes have their own logs.
- Initial naive delimiter scans misread table row-spacing forms such as `\\[3pt]` and `\\[4pt]` as display openers. The scanner was corrected to distinguish escaped controls, then passed. No manuscript delimiter was altered merely to satisfy a false diagnostic.
- Truncated source/image tool output was reread before coverage was marked complete. In particular, the foundations source review and visual-page review records distinguish successful rereads from incomplete initial output.
- The first full draft exposed the figure-07 title collision and figure-32 set-label error described above. The source corrections and final in-document visual acceptance are complete.
- A first source-callout penalty hook did not resolve the orphaned callouts. A small TeX fixture identified an intervening vertical anchor/color node; the corrected callout starts horizontal mode before that node and places the ending penalty at the environment end. Final images confirm the correction. An initial frontmatter shortening also left a split scope box; further condensation resolved it. These unsuccessful layout attempts are retained in their build receipts.
- Two routine text-edit/search commands failed harmlessly: a regular-expression search treated literal braces as syntax, and one patch matched only part of a long line. A fixed-string search and an exact full-string edit recovered them; no partial manuscript change was accepted from either failed command.
- Draft pagination observations include floats interrupting an example/proof or display sentence, source callouts detached at page tops, a short table introduced across a page turn, and sparse section endings. These are distinguished from clipping or mathematical defects. The final layout fixes the detached callouts, interrupted proof/sentence floats, split insight box and short spill page. Normal section-ending white space and readable continuations remain; they are recorded as acceptable pagination, not concealed as defects.

The completed full-size draft reviews found the WR declaration tables and concordance readable, with no clipping or overlap in their pages. Narrow-cell justification and underfull warnings are not automatically treated as visual defects. The thirteen reflowed final pages were inspected after the last changes; the remaining 153 pages retain exact inspected pixels.

## Closeout boundary

No unresolved substantive textual correction is reported by the component proofreading passes after the listed local fixes and evidence synchronization. That statement is limited to the completed proofreading and focused checks. Final PDF build, exact source identity, and all-page visual coverage are now accepted and recorded above. The inherited Lean sources, accepted v1.8.0 evidence and historical numerical reports are preserved as evidence; this edition's new claims concern editorial review, exact status synchronization and publication checks.
