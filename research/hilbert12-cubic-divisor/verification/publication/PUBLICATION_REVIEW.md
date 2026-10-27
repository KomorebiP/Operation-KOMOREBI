# Independent H12 publication review

Reviewer: `publication_review`, 7 October 2026. **PASS for final traditional source, Markdown and 43-page native layout.** Lean source mapping passes; the separate independent reviewer passes all ten Lean pages. This record is read-only with respect to manuscripts, visual derivatives, numerical inputs and original sources.

## Exact final artifacts

| Artifact | Final SHA-256 | Coverage |
|---|---|---|
| `traditional/H12_Cubic_Divisor_Traditional.pdf` | `b0e1fbcd9b30fda1d75107f6172ee3b5be3f2793ea5c8cec7edb9ff766e696c0` | All 43 pages, individually at native 150 dpi |
| `traditional/H12_Cubic_Divisor_Traditional.tex` | `917663c3c26875b6aebe664e99353e32f08a18064c3985527594b7218021e5dd` | Main and all twelve included section sources read; individual included-file hashes in source check |
| `traditional/H12_Cubic_Divisor_Traditional.md` | `ffe265605dd8193f5994c9f1cadefb3fa9476b0849ad739628f8e4cc621b79a0` | Whole export, five PNG embeds, five canonical caption mappings and explicit cross-reference anchors |
| `lean/H12_Cubic_Divisor_Lean_Guide.pdf` | `002cc5b4fd8d34e381399a10888cb2a6d7b421afce7afb101cc3a8b495bda8ae` | All ten pages independently rendered/viewed at 150 dpi by `numerical_validation` |
| `lean/H12_Cubic_Divisor_Lean_Guide.tex` | `94ae684e01ec21b83cbb33c7b7e0305da87ea13a7e83808b6443ea2107dd95d8` | Full guide, declarations and manuscript/formal coverage read by this reviewer |

## Native page review and actual repair

Every traditional baseline page 1–43 was opened individually at its full 1,275×1,650-pixel resolution. Baseline PDF hash: `95e0c5238810b296966dc5b8ee00455ec1d502acbfbad9da95950651e9af5712`. Neither contact sheets nor page-bound checks substituted for human inspection of equations, tables, annotations, captions, references and page furniture.

The initial page22 had a concrete reading-flow defect: Figure2 separated “For” from “completeness” within an explanatory paragraph. The figure itself was legible. The author moved the environment after the completed paragraph and retained the baseline renders. Final page22 was freshly viewed and passes. Independent byte comparison found precisely page22 changed; every other final PNG is byte-identical to its individually reviewed baseline. Independently rendering all 43 pages directly from the final PDF at 150 dpi gave pixel equality with every final supplied PNG. Pagination remained 43 pages. No remaining overlap, clipping, annotation collision or illegible table/display was observed.

The five embedded figures were inspected on the native pages, including their captions. The all-18-native-visual-figure audit belongs to `claims_audit`, not this reviewer. Its separate final visual-guide-page report must be used for guide coverage; a native-figure pass alone is not a guide-page verdict. The earlier K-COS contact-sheet-only review missed intra-figure collisions, and is not represented as a reliable precedent for these individual-page checks.

## Source and export findings closed

The final source recheck confirms the author's correction of the arithmetic field/function distinction `F₀` versus `F`, the missing `mathscr` package, relocated Epstein/CM references, local Green-quantity notation, and the rendered four-subfield norm table. Literature entries identify the editions actually authenticated. Historical phase/branch bounds remain retained checkpoint evidence, not fresh interval certification. The final integration contains five actual PNGs.

Across thirteen TeX files, the final static check finds 87 labels and no duplicate labels, missing reference targets or missing bibliography keys. All five Markdown images resolve to PNGs. Each balanced source caption exactly matches its canonical export record, and the corresponding converted text occurs in Markdown. There are zero HTML mathematics spans and zero layout div wrappers; every explicit internal Markdown reference has its anchor. Original scalar values, indices and exponents were not repaired through HTML heuristics. These are consistency/portability checks rather than a claim that every Markdown renderer has identical mathematical typography.

The principal and reconstruction transcription audit independently pins the final figure-only source changes and reconstructs the previously audited mathematical section hashes. Proper-math-span preservation of the copied theta/Stark/polarization blocks is reported separately by the author: 384 spans with explicitly declared notation/tag substitutions. The independent source review checks the formulas and their scope without calling manually typeset plaintext an unchanged-token copy.

## Mathematical and evidence boundaries

The restricted theta theorem retains symmetric period matrices with positive-definite imaginary parts and one global zero-free entire prefactor outside the finite rational expression. Counts are unsigned and include multiplicities. Genus minimality concerns the ungrouped absolute product. Fourth-power normal convergence and meromorphic continuation, rather than divisor matching alone, force the cubic exponential. The special cube is an analytic formula, not an arithmetic evaluation.

The Lean catalogue has 453 distinct theorem names across 42 deduplicated modules; the current block has 25 theorems, including 14 inherited and 11 new. The complete module/declaration checks and transitive-axiom reports are distinguished from the resource-incomplete single aggregate import. The guide exposes algebraic, reality, branch, contraction and endpoint hypotheses; it does not manufacture the gamma comparison inputs. This publication reviewer inspected the source/evidence mapping but did not rerun the compiler.

Nine primary-source literature leaves and exact project applications are recorded in `provenance/LITERATURE_CHECK.md/json`. The checked BCG authors' copy supports its proved modulus formula with the stated normalizations; its bytes were not authenticated as the inaccessible exact arXivv2 artifact. The failed fetches are recorded. The inherited arithmetic field/unit/ray/CM-branch inputs were not freshly replayed end to end. Historical directed phase/branch certificates were not rerun. Floating replay is not an interval enclosure. The exact polarized gamma reality and original gamma/arithmetic equality remain open; no novelty or priority claim is made.

## Evidence files

- `FINAL_SOURCE_CHECK.json`: final source, Markdown, caption, link, image and inventory hashes/results.
- `INDEPENDENT_TRADITIONAL_PAGE_QA.json`: all 43 page hashes, native inspection disposition, changed-page scope and fresh final-PDF pixel equivalence.
- `INDEPENDENT_LEAN_PAGE_QA.md/json`: independent ten-page coverage, exact final hash and per-page findings from `numerical_validation`.
- `SOURCE_REVIEW.md`: full source coverage and the eight editorial/provenance findings with final dispositions.
- `../audits/TRADITIONAL_TRANSCRIPTION_AUDIT.md` and `TRADITIONAL_FIGURE_INSERTION_PRESERVATION.json`: independent formula/preserved-section review.
- `../audits/INDEPENDENT_VISUAL_AUDIT.md/json`: independent native visual figures and separately reported final guide status.

No remaining concrete traditional publication defect was found in the frozen bytes above. These passes do not replace the scoped proof, literature, compiler or computational evidence, and do not close the remaining arithmetic assertion.
