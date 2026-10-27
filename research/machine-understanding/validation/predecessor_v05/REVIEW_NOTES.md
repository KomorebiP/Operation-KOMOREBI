# Review and validation notes
## Machine Understanding: Representation, Explanation, and Transfer

**Komorebi P. · Operation Komorebi · Version 0.5.0 · 8 October 2026**

## Scope

This is a 41-page expanded theoretical draft, following the 26-page v0.1.0. It develops the three named directions from the first-draft review: noisy correction, acquisition of missing distinctions, and explanations for different recipients. The final integration remains explicit about the distinction between deterministic exact acquisition and noisy posterior concentration.

The eight added statements were reviewed against their explicit assumptions, proofs, examples and executable finite surrogates. The nine predecessor statement/proof pairs were preserved verbatim, their surrounding references were checked, and their exact suite was rerun. This is an internal mathematical and implementation review, not independent peer review, a comprehensive novelty audit, or proof-kernel verification. It is not a claim that an existing neural system realizes the formal model.

## Recorded final inventory

| Item | Result |
|---|---|
| PDF | 41 pages including cover, contents, guide, appendices and references |
| Statements | 17 with prose proofs: eight theorems and nine propositions |
| Added statements | Eight relative to v0.1.0; not eight priority claims |
| Source preservation | All nine predecessor statement/proof pairs unchanged |
| Definitions and counterexamples | Three definitions, ten formal counterexamples |
| Figures | Eight analytical vector figures and eight PNG previews |
| Bibliography | Nineteen entries including the companion monograph; five new public references |
| Exact finite checks | 28 groups and 172,481 assertions passed |
| Predecessor checks | 15 groups and 132,536 assertions rerun |
| New checks | 13 groups and 39,945 assertions passed |
| Source audit | No missing references, duplicate labels, missing/unused bibliography keys or unmatched statement/proof pairs |
| Final LaTeX | No warnings, overfull/underfull boxes, unresolved references or missing-character diagnostics |
| Final PDF | All 41 pages rendered; no out-of-page words or unresolved/replacement text markers found; fonts embedded |
| Fresh rebuild | New source copy rebuilt using Bash; all pages have identical extracted PDF text |
| Fresh finite rerun | Both suites passed again with identical counts; expanded demonstration output identical |

Counts describe document inventory and bounded deterministic checks. They are not independent scientific replications, statistical samples, proof-assistant results or counts of new mathematical discoveries.

## Main mathematical boundaries and review points

**The sender is not omniscient.** The explanation graph is built on the sender's available information, not automatically on complete source states. A self-loop records that no message based on that access can distinguish cases a recipient must distinguish. Multiple backgrounds can require a larger common alphabet than each recipient needs alone. The decoder may be designed once, but the theorem does not prove that it is cheap, learned, mechanistically faithful or psychologically comprehensible.

**Acquisition changes the world.** The support update retains the post-experiment state. Uniform admissibility is checked on every possible state. Histories that matter to future permissions, costs or targets must be represented. A reset can make a current value known without revealing an earlier one. Origin-tagged targets distinguish these tasks. Finite horizon, not an unnoticed timeout, limits the exact acquisition theorem.

**Bayesian preservation refers to the actual joint experiment.** The factorization reconstructs raw observations conditional on the reported record in that same coupling. The existence of an unrelated simulation kernel is not substituted for it. The all-prior criterion is equivalent to one full-support-prior test. Zero-probability observations are not assigned arbitrary posteriors, and impossible report columns are handled explicitly.

**Noise changes the preservation condition.** Deterministic report fibers need proportional nonzero likelihood vectors, not universal injectivity of every raw token. An independent ancillary flag can be removed without changing any posterior. Retaining only parity in the five-valued instrument loses distinctions among three even candidates.

**Average loss and rare-event loss differ.** Expected posterior divergence is conditional mutual information under one prior. It does not bound every realized posterior. The conditional variation bound includes a positive evidence denominator and is sharp for general joint laws. The same-prior rare-event counterexample shows why small unconditional error can coexist with a completely different conditional conclusion.

**The recipient guarantee concerns one actual chain.** The posterior, transmitted approximation and decoded belief have to belong to the same case and loss function. The regret bound assumes bounded common losses, finite available actions and optimal choice under the reconstructed belief. It does not imply preservation of logical zero-risk constraints or justified real-world action under an incorrectly specified model.

**Repeated observations need a provenance model.** Sequential correction assumes fresh observations conditional on the static model and selected experiment. Experiment selection and bounded stopping depend on the retained report history. Duplicating a reading does not create a second independent sample. An undisclosed informative selector or a changing hidden state requires additional modeling.

**The joint theorem is finite and exact.** It combines one admissible deterministic experiment tree with one graph-colorable common artifact. It does not require the sender to reconstruct the full state when complementary recipient backgrounds make a shorter message sufficient. The code implements the constituent graph and acquisition constructions and explicit joint examples. It does not implement a general efficient joint optimizer for stochastic inquiry and arbitrary decoders.

## Implemented domains

The predecessor suite remains unchanged. The expanded suite includes all specified small rational likelihood/reporting channels, exact symbolic information identities, all four-cell quarter-grid joint laws for conditioning comparisons, bounded-loss binary recipient decisions, finite adaptive histories, the five-valued noisy instrument, every graph on four cases with direct encoding comparisons, five-cycle and parity examples, every ordered pair of the declared binary experiment tables, all associated nonempty supports at horizon two, reset/origin variants, and all 25 initial instrument fibers. Each exact domain is recorded in the relevant JSON group.

Graph encodings are checked against separately implemented direct decodability tests. Acquisition dynamic programming is compared with a separately implemented enumeration of full observation-history policies. These alternatives are authored within the same project, so they provide algorithmic cross-checks rather than independent external validation. The information identity uses rational coefficients of prime logarithms, avoiding floating-point cancellation as a correctness criterion.

## Resolved failures and presentation corrections

1. The first new figure export raised `PermissionError` because the plotting process could not write the container-created figures directory. The directory permissions were corrected and all four new vector figures and previews were regenerated successfully. The error was disclosed in the conversation and retained in `validation/development/figure_export_failure.txt`.
2. The first new LaTeX build failed with an extra alignment-tab error: a `split` environment was used for a recurrence with too many alignment columns. It was replaced by `aligned`, with the condition placed explicitly. The failure is preserved in `validation/first_build.log`. Subsequent builds completed without diagnostics.
3. Visual review found a graph annotation encroaching on an edge and a diagnostic root label exceeding its box. The annotations were repositioned and the root box widened. The new figures were regenerated before the final PDF build.
4. A preliminary 43-page layout had a nearly empty appendix continuation and a short second reference page. A repeated nonmathematical paragraph was removed, and bibliography typography was set to 9.5 pt with 11 pt leading and explicit item spacing. The body font was unchanged. The final document is 41 pages; no statement or proof was deleted to force pagination.
5. The reading Markdown exporter initially retained layout-only custom table-column syntax. It was corrected to translate those tables into ordinary column alignments before conversion. Final tables, seventeen proof headings and nineteen numbered references are present.

No mathematical assertion failed in the executed finite suites during this revision. That statement does not certify every possible input outside the declared bounds, and it does not erase the first draft's earlier hypothesis correction documented in its retained review notes.

## Visual and build review

The initial successful 43-page render was inspected in contact sheets. The final document was rendered again. Pixel comparison confirmed that final pages 1 and 3–40 were unchanged from the inspected layout. The changed contents page and new reference page were reviewed separately. Final pages 18, 21, 26 and 33 received full-page mathematical/figure review in addition to those changed pages. The recorded visual scope is in `validation/visual_review.json`.

The fresh build used a new source copy and the supplied Bash script. It reran both suites and the demonstration, rebuilt the PDF and executed the source audit. The resulting PDF has identical extracted text on all 41 pages. Binary PDF identity, Windows execution, PDF/A and tagged accessibility were not certified.

## Reference and provenance limits

The five added references received targeted primary-source review, and four inherited publication records were rechecked. Some primary pages yielded only abstracts or metadata, or failed to return readable full text. Those failures were not counted as full-text review. The itemized account is `validation/reference_review_v05.md`. Earlier review scope remains in `validation/predecessor/reference_review.md`.

The execution manifest follows the legacy v1 record structure and additionally pins inputs before and after execution. The supplied verifier is project-authored. It was executed, but it is not an independently authenticated copy of the plugin validator. The record identifies actual commands, times, versions, per-command 30-second wall limits, outputs, and hashes. No Git revision, external attestation, memory cap, or proof-kernel verification is claimed.

The original v0.1 PDF and source ZIP remain unchanged. This package contains no private conversation transcript, third-party paper full text, standalone font file, or claim of newly run agent experiments. Version 0.5 marks a substantive expanded draft. `FIRST_EDITION_PLAN.md` defines the consolidation still intended before a first-edition freeze and separates it from open-ended research beyond that scope.
