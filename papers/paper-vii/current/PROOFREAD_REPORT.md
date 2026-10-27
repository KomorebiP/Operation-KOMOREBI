# Paper VII: final prose and proofreading report

**Quantum Seeds and Effective Dynamics**  
Komorebi P. · 18 October 2026  
Original project title: *Quantum Seed and Packet Calculus*

This edition completes the requested prose revision and repairs the pagination issues recorded in the preceding proofreading pass. The traditional paper, visual guide and Lean guide have been read as complete works, revised conservatively, rebuilt and reviewed in their rendered form. All mathematical parts, proof completions, formal source snapshots, scientific figures and recovery archives remain in the package.

The reading set contains **286 pages**: **159** in the traditional monograph, **42** in the visual guide and **85** in the Lean and evidence guide. The copies in `papers/`, `publication/pdfs/` and the corresponding `editable/` directories are identical. `EDITION.json` records the final sizes and SHA-256 hashes. The current acceptance record is `verification/final_prose_2026-10-18/RELEASE_VALIDATION.json`.

## Prose decisions

The revision covers all nine mathematical source parts, all 40 worked visual pages, all seven Lean guide chapters, the reading introductions, captions, and the prose generated for navigation and source evidence. Each passage now explains its role in connected sentences where the earlier version used compressed labels or abrupt fragments. Definitions, assumptions, conclusions and the steps between them remain explicit.

Unnecessary semicolons and editorial hyphens have been removed. The remaining punctuation has a specific purpose, such as subtraction, matrix indices, command flags, source identifiers, page ranges or an established name. Exact code excerpts and mathematical formulas were not subjected to a global punctuation replacement. The source review found no unfinished placeholder text in the current authored mathematical parts or guide chapters.

The explanations remain complete without added filler. The reading introductions explain how the parts relate, the visual pages describe what each finite example does establish, and the Lean walkthroughs connect hypotheses to the displayed declarations. Proofs have not been replaced by result summaries. The Lean chapters contain about 655 more prose words than the preceding edition, using the documented count that excludes formulas, code and command blocks. That count is an editorial description, not a measure of mathematical substance. The method is recorded in `verification/final_prose_2026-10-18/reviews/lean/PROSE_WORD_COUNTS.json`.

## Mathematical preservation

All **107 complete proofs** remain. **73 proof bodies are byte-identical** to the retrieved source, and **34 contain reviewed prose changes**. The latter changes improve grammar and explanation while retaining the argument's steps and hypotheses. It would be incorrect to describe all 107 proof bodies as byte-identical after this prose revision.

All **1,795 extracted mathematical spans** in the nine traditional parts remain byte-identical. The comparison also preserves the ordered environment sequence, labels, cross-references, citation commands and statement inventory. There are still **147 statement records**, comprising **142 numbered records** and **five unnumbered supplementary statements**, including **96 theorems, propositions, lemmas or corollaries**. All six supplements and the three earlier alternative proofs remain. These counts overlap across source branches and do not count independent discoveries.

The preservation check binds each complete revised part to the preserved preceding edition plus a closed list of reviewed prose and layout edits. It does not authorize arbitrary changes outside mathematical delimiters. The separate mathematical-span and inventory comparisons use the actual retrieved source. The closed contract and fresh result are `verification/final_prose_2026-10-18/REVIEWED_PART_EDIT_CONTRACT.json` and `verification/final_prose_2026-10-18/SOURCE_PRESERVATION.json`. The previous comparator remains in provenance.

The mathematical expressions in the visual narratives and Lean chapters were also compared against their preserved baselines. The visual report checks the 40 narrative bodies and the paired plate sources. The Lean prose contract covers the full chapters, opening wrapper and narrative generator text. Exact source excerpts and all inherited formal files have separate checks.

## Precision corrections made during the prose review

Independent reading identified a few places where smoother prose still needed a more exact statement of the existing assumptions. The final text incorporates those corrections:

| Passage | Final treatment |
|---|---|
| Hamiltonian reconstruction in the introduction | The transfer operator is described as a **strictly positive contraction**, matching the existing logarithm theorem for a nonnegative Hamiltonian. |
| Recovery normalization example | The outputs are described as **proportional to the same projector**. An unnormalized output is not called a normalized state. |
| Euclidean transfer on coordinate spaces | The state space is **nonzero**. A vector space is always nonempty because it contains zero, so the earlier prose needed this distinction. The corresponding nonempty coordinate-index hypothesis and formal source are unchanged. |
| Coordinates in the several-seed argument | The prose explicitly places the coordinates in the standard product basis before using the rank argument. |
| Complete positivity on V18 | A test of a single density matrix **on the original system** is distinguished from the requirement involving every auxiliary dimension. The qualification avoids an overstatement about ancillary tests. |
| Mode limits on V25 | The heading now explains why the mode regime matters. It does not suggest that fixed modes are the only possible controlled regime. |
| Spectral dimension on V40 | Trace norm convergence applies to the operators and first heat moments. A nonzero limiting heat trace is stated before taking the ratio. |
| Formal and computational evidence | References to archived checks identify their actual earlier dates. The prose does not present them as fresh executions of this edition. |

These are corrections to explanation and the expression of existing hypotheses. They do not introduce new formulas, extend formal coverage or close a physical continuum conjecture. Source review and independent review records are included under `verification/final_prose_2026-10-18/reviews/`.

The six earlier mathematical wording corrections are retained: the finite path ordering, the partition mesh, the interpretation of the approximate recovery defect, the heat-moment ratio, the infrared coefficient convention and the positive-row qualification for several-seed generation. Their original focused review remains under `verification/proofread_2026-10-18/`. That preceding review keeps its own source hashes and date.

## Traditional layout repairs

The introductory reading note now fits on one page. This was achieved by removing redundant vertical gaps and using compact paragraph spacing in that note. No introductory sentence or body text was removed, and the main type size was retained.

The Kraus transfer and plateau subsections now have complete opening prose and remain with the start of their content. The spacetime tower figure is placed before the Euclidean transfer subsection, so it no longer interrupts the theorem. The earlier Kato figure repair is retained. Section and subsection spacing guards keep headings with their opening material, and a word is no longer allowed to break across two pages.

All 65 boxed theorem statements and all 15 boxed definitions are short enough to fit within a page. They are now kept together consistently. This prevents a concluding phrase, a single formula or a hypothesis from being stranded in a continuation strip after reflow. Ordinary multi-page proofs remain complete and readable. The final alternative low-mode proof is kept with its heading and hypotheses. No equation was squeezed or shortened to obtain these breaks.

The complete chronological layout record is `verification/final_prose_2026-10-18/LAYOUT_EDITS.json`. It includes the intermediate local guards and their later consolidation into the style. Candidate reports retain the original observations. The final rendered review identifies the corrected pages by the hash of the accepted PDF.

## Visual guide and integrated atlas

All **40 worked visual pages** and all **38 editable vector plates** remain. The revised standalone narrative bodies agree with the integrated atlas after the intended navigation setup is accounted for. Paired plate sources are identical, and the six edited plate captions are synchronized with the supplied generators. Drawing geometry and mathematical labels from the preceding proofread edition are preserved.

The V27 title was revised to avoid leaving a single word on its own line. The V28 evidence table now uses a concise row label that fits its column naturally. V18, V25 and V40 received the precision corrections described above. All changed pages were inspected in both their standalone and integrated settings, while exact raster comparisons support reuse of previously inspected unchanged bodies.

The earlier scalar-dimension correction on V29, parity-conjugation clarification on V31, array-count correction on V13 and label/arrow repairs on V16, V27 and V38 remain in place. The 12-plate extended generator was executed and reproduced its edited source plates byte for byte. The original 26-plate generator requires SymPy, which was unavailable, so that generator was not rerun. Its edited caption strings were checked against the paired active sources. Generating a plate is a reproducibility check and does not independently establish the mathematics illustrated by it.

The refreshed visual crosswalk retains **80 traditional reading targets**. All **16 internal visual-page references** resolve. Source and navigation checks, generator scope and final rendered acceptance are recorded under `verification/final_prose_2026-10-18/reviews/visual/`.

## Lean and evidence guide

All seven authored chapters were reviewed from beginning to end. The prose explains the exact contracts, the role of the excerpts and the relationship between the formal statements and the traditional paper. The revised chapters remain bound to their preserved baseline by **208 exact reviewed substitutions** across the ten files in the closed prose contract. The checker itself is separately preserved and reviewed.

All **67 contiguous raw UTF-8 excerpts** and all **67 rendered excerpt files** are unchanged. All **121 inherited `.lean` files** across the retained branches are unchanged. The active source inventory still has **25 modules**, **323 named theorem declarations**, **19 scoped finite manuscript items**, **nine dependency pins** and **six separately audited constructed objects**. These are different units and do not add up to a larger theorem-coverage claim.

The short `[Nonempty n]` token now remains on one line. Module names stay with their corresponding source hashes. The earlier inline binder repairs are retained. The cross-reading tables still contain **110 traditional locators**, including both endpoints for the six supplement groups.

The current guide-specific static reconciliation and closed preservation checks passed. Two sets of focused checker controls each accept the correct input and reject two deliberate corruptions, including deletion of a regularity hypothesis, a changed raw excerpt or a forged baseline excerpt. These controls test the checking software. They do not constitute theorem proofs. The earlier 16-method verifier regression suite was not rerun in this prose revision and remains identified with the preceding initial pass.

One inherited formal-source comment uses older wording for the recovery scale. The formal quantifiers are preserved and the current guide explains the scale correctly. The comment erratum remains documented in the preceding focused review. The archived formal source has not been silently rewritten.

## Build, navigation and final acceptance

The current builders use the installed OpenType P052 and Nimbus Sans faces, Latin Modern text and mathematics, and DejaVu Sans Mono where needed for code. The earlier font repair is retained. The guide assembly helper now uses the same installed-font fallback as the PDF builder. No font binaries or new dependencies were added.

Each builder stages its current source tree in isolation, runs four XeLaTeX reference passes, runs BibTeX where required, and emits the PDF once through xdvipdfmx. The deterministic build date is 18 October 2026. All current navigation is regenerated from actual printed page labels and physical PDF positions, without assuming a fixed cover offset.

Final acceptance separates the following evidence:

1. Complete source prose review and independent focused review of meaning-sensitive changes.
2. Closed full-file preservation comparisons, unchanged mathematics and formal excerpts, and unchanged inherited assets.
3. Fresh builds of all three PDFs with final log checks and synchronized PDF copies.
4. Mechanical checks of every page for text bounds, known invalid glyph mappings, links, bookmarks and detached proof markers.
5. Rendered review of the complete reading set. Reports identify pages inspected directly and pages accepted through exact raster equality to a previously inspected candidate. Merely rendering a page is not counted as reviewing it.
6. Isolated replay from the packaged sources, comparing every page's extracted text and page count against the shipped PDFs, with byte identity recorded separately.
7. Agreement among root metadata, page maps, guide crosswalks, accepted source/report hashes and the reading PDFs.
8. Full ZIP membership, CRC and per-file SHA-256 verification after the final manifest is written.

The authoritative current records are `verification/final_prose_2026-10-18/FINAL_PDF_REVIEW.json`, `verification/final_prose_2026-10-18/PDF_PREFLIGHT.json`, `verification/final_prose_2026-10-18/PACKAGED_BUILD_REPLAY.json` and `verification/final_prose_2026-10-18/RELEASE_VALIDATION.json`. The report index distinguishes intermediate candidate findings from final acceptance. Earlier reports are retained unchanged as evidence of their own stage.

## Evidence that remains inherited

**No fresh Lean compiler or kernel run was performed.** Lean, Lake and Elan are absent from the environment, and the retrieved package does not contain the portable compiler kit or compiled interfaces needed for the pinned replay. The compiler and axiom records remain the inherited **6 September 2026 v0.6.0** evidence, pinned to **Lean 4.34.0-rc2** and **Mathlib aeb72f1e9981b6d35b426b16dca7759be3e7ba06**.

Earlier numerical, rational and symbolic reports retain their **9 October** date and bounded scope. They were not rerun during this prose revision. Preserved PASS records have not been presented as new executions, and historical source/PDF hashes have not been silently repointed at revised files.

The five physical continuum targets remain open: anomaly-free refinement, uniform Feshbach control for the proposed tower, Lorentzian reconstruction, an Einstein infrared limit and a positive physical massless spin-two sector. Each finite, bounded or conditional analytic result retains its own assumptions. The present work is a complete editorial revision with the available source and PDF checks, rather than a new claim of universal mathematical correctness.

## Complete package and provenance

The package retains all **784 retrieved source files**, both recovery ZIPs and the **13 comparison-baseline files**, with hashes matching the actual October 11 delivery. That delivery had already removed standalone font files, so this comparison does not claim that an earlier archive was untouched by that step.

The preceding current sources, PDFs, metadata and checkers are preserved under `provenance/pre_final_prose_2026-10-18/`. Earlier preserved states remain available in the same provenance tree. The current source diff, closed edit contracts, review reports, build logs and read-only verification commands accompany all three final PDFs. Only Paper VII was changed.
