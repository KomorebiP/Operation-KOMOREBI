# H12 independent publication source review

Reviewer: `publication_review`. Date: 2026-10-07. Review-only; no manuscript, figure, computational input, or original source was edited by this reviewer. Final source consistency and traditional page QA pass for the frozen bytes identified below. This is an editorial, transcription-scope, citation and publication review; it does not assert a complete formal proof of the analytic or arithmetic research target.

## Source coverage

Read the traditional main TeX and all twelve included section files (2,097 section lines in the inspected preparation revision), the full Lean guide TeX, its claim-coverage mapping, and its declaration inventory. Compared the principal divisor and reconstruction formulas with the original v0.13/v0.14 proofs and the fresh proof audit. The copied theta, Stark, and polarization blocks were checked for notation scope and reference translation. External-source applications are recorded separately in `provenance/LITERATURE_CHECK.md` and `.json`.

The restricted finite-theta theorem explicitly puts one zero-free entire factor outside the finite rational expression. Zero/pole counting is unsigned and counts multiplicities. The genus-three product is defined as separate positive/negative products; the minimal-genus statement concerns an ungrouped absolute construction. Fourth-power regrouping, rather than divisor matching alone, forces the cubic exponential. The special cube is analytic and remains distinct from an arithmetic evaluation. The exact missing polarized reality statement remains visible.

Lean guide source distinguishes its 25 current theorem declarations (14 inherited, 11 new) from 453 distinct theorem names in the 42-module selected continuation source. An independent inventory count found 746 total declarations, 453 theorems, 25 current theorems, 11 new current theorems, and no missing names in `CLAIM_COVERAGE.json`. Definition counts are not called theorem counts. Complex divisor interpretation, disk cardinalities, theta growth/Jensen, products and reconstruction remain ordinary proof obligations. Conditional reality, branch and contraction lemmas retain their actual hypotheses. Fresh compiler/axiom evidence must be assessed separately from this text review.

## Findings delivered to the author

1. Two arithmetic-field notation leftovers in Stark: `F(beta)` and `F_0(X)/F` must use `F_0`, since `F` elsewhere is the gamma scalar function.
2. The imported Stark block uses `mathscr`; the main preamble must provide the command.
3. The Epstein derivation is now a subsection, so its old “Appendix A” reference is wrong. Its last “section 5” reference must identify the relocated CM-products subsection.
4. The principal block promises `H_CM`, but the imported Stark block still uses local `H(z)`. The explanation or notation must be made consistent.
5. The four-subfield norm table contains raw ASCII names (`F0(xi)`, `omega A`, `epsilon2/epsilon1`). These should be typeset as the exact mathematical entries, without changing their values.
6. Bibliography links must identify the editions actually authenticated: Milne `CFTc.pdf`, Tao’s 23 December 2020 notes, and the exact MIT Lecture19 URL. BCG authors’ copy must retain the inaccessible-v2 provenance distinction.
7. Numerical validator confirmed the v0.6 directed positive-real-part and branch certificates were not freshly rerun. Their archived input/evidence bytes were authenticated only. The imported discussion must call them retained historical certificates and remove “rechecked”; the decimals are illustrative archived values.
8. The sole preliminary declared figure path, `figures/08_complex_families.png`, was absent during preparation. Its `IfFileExists` wrapper could silently omit it; final integration must include the intended figure.

All eight findings were corrected by the author and independently rechecked in the final source. The final manuscript includes five PNG figures; every caption was checked against its balanced canonical TeX value, the Markdown conversion record, and the Markdown text. The moved figure's final paragraph placement was also reviewed. No substantive proof replacement was requested by this reviewer. The declared finite-theta grammar, period-matrix hypothesis, and canceled-singularity continuation remain scoped mathematical clarifications rather than being called uniquely forced typos.

## Static checks and final frozen source

Across 13 traditional TeX files, 83 labels were present, with no duplicate labels, unresolved `ref`/`eqref`/`pageref` targets, or missing cited bibliography keys in the inspected preparation revision. This is a textual consistency check, not confirmation of the final compiler log or rendered layout.

The independent final check found 87 labels across the same 13 files, no duplicate labels, no unresolved reference targets, and no missing bibliography keys. Every explicit Markdown internal link has an anchor. All five Markdown image paths resolve to PNG files, the five canonical captions match the export records and converted text, and there are zero HTML mathematics spans or layout div wrappers. Bibliography anchor spans are ordinary identifiers, not HTML mathematics. `FINAL_SOURCE_CHECK.json` pins every included TeX file, each Markdown image, the inventories and compiler summary.

| Artifact | SHA-256 |
|---|---|
| Traditional main TeX | `917663c3c26875b6aebe664e99353e32f08a18064c3985527594b7218021e5dd` |
| Traditional principal section | `058b9221ba7c66df361e903f4b0eb9616389faf949129b8a8ae59c45713032f9` |
| Traditional Markdown | `ffe265605dd8193f5994c9f1cadefb3fa9476b0849ad739628f8e4cc621b79a0` |
| Traditional PDF | `b0e1fbcd9b30fda1d75107f6172ee3b5be3f2793ea5c8cec7edb9ff766e696c0` |
| Lean guide TeX | `94ae684e01ec21b83cbb33c7b7e0305da87ea13a7e83808b6443ea2107dd95d8` |

The Lean source summary was rechecked against `FINAL_REPLAY_AUDIT.json`: 42 selected modules, 453 distinct theorem declarations, 25 current theorems (14 inherited, 11 new). It states complete module/declaration-level type and transitive-axiom checks, with the single aggregate import still incomplete from its resource limit. This reviewer inspected the mapping and evidence summary but did not rerun the compiler. Independent native Lean-page QA was assigned to `numerical_validation` and is recorded separately in `INDEPENDENT_LEAN_PAGE_QA.md/json`.

## Final page closure and limits

Every traditional page 1–43 of baseline PDF `95e0c5238810b296966dc5b8ee00455ec1d502acbfbad9da95950651e9af5712` was individually viewed at native 150 dpi. One concrete reading-flow defect was found on page 22: Figure2 interrupted the phrase “For completeness”. The author moved the figure after the completed paragraph. Final page22 was freshly inspected and passes; all other 42 PNGs are byte-identical to the reviewed baseline. A fresh independent in-memory render of all 43 final PDF pages at 150 dpi is pixel-identical to the final supplied PNGs. Every page's hashes, dimensions and review disposition are recorded in `INDEPENDENT_TRADITIONAL_PAGE_QA.json`.

The five embedded diagrams/captions were inspected in these pages. The independent native-resolution audit of all 18 original visual PNGs belongs to `claims_audit` and is not reattributed to this reviewer. Its guide-page status must be read from its own final report. Proof-audit, transcription, computation, literature and layout evidence remain distinct. The inherited arithmetic inputs and historical phase/branch bounds are not freshly certified by a layout or source-consistency check; the exact polarized gamma reality and original arithmetic equality remain open.

The earlier K-COS contact-sheet review missed intra-figure collisions. This H12 final review therefore requires individual native-resolution page/figure inspection; contact sheets alone cannot support a clean verdict.
