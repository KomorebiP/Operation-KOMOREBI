# Paper IX consolidated manuscript review

**Claim:** The consolidated mathematical statements and proof summaries faithfully restate the cited archived results under their stated hypotheses, and retain the open questions and verification limits.

**Verdict: proved as written, within this manuscript-correspondence scope.** The manuscript is scope accurate. No unresolved mathematical gap was found in this review. This is not a fresh Lean run, a new proof of every inherited declaration, or a new authentication of the external paper.

The reviewer worked independently of the section authors. Every main-text section and all 51 labeled theorems, lemmas, propositions, and corollaries were read. Critical raw proof chains and interfaces were inspected directly. Source maps cover all 51 statements; definitions and additional mapped entries bring the combined index to 57. Exact reviewed TeX, map, source, and evidence hashes are in `MANUSCRIPT_REVIEW.json`.

## Decisive mathematical checks

| Block | Checked conclusion and boundary |
|---|---|
| Foundations | Residue selectors, actual EGF coordinate equivalence, characteristic-p Hurwitz rules, triangular denominator clearing, finite reconstruction, unit coordinates, recurrence packets and CRT. Formal series and finite interpolation are not presented as analytic convergence. |
| Nishibuchi | Actual original coefficients are `j!` times the normalized packet. Prime p, positive m, m dividing p−1 or m=2, and 0≤j<mp are retained. The exact degree shift is lcm(2,p−1)p^r. The sufficient threshold is n≥r, with the stated stronger divisor-branch condition. |
| Exceptional dyadic arithmetic | All rows are covered. Original gains (1,1,5,3) include the address factorial. Exact displacement requires positive displacement and gives nonzero differences. Least periods concern packet rows, not arbitrary shifts of the full degree sequence. |
| Classical reconstruction | The odd-length identity is valid for positive odd lengths without primality. The dyadic exponent 4M+3 is uniformly optimal at the first omitted row. Exact individual summand valuations do not determine every tail valuation because cancellation remains possible. |
| Finite lifting | The actual residual and evaluated partial Jacobian give the obstruction. Nonlinear depth is L≥1; the affine case permits L=0. Composite q and q=1 do not inherit prime-field rank formulas. The actual residue lift set, not arbitrary integer representatives, has the stated torsor/count. |
| Towers and charts | Initial surjectivity propagates along one compatible tower. Prescribed parameter results require the actual solved block to be surjective. Endpoint uniqueness is confined to the square case. General continuous charts select a suitable minor and need not preserve the approximate center as an exact root. |
| Weighted deformation | Fraction-field invertibility and an integral p^s inverse certificate are explicit. Strict threshold M>2s, ball depth s+1, displacement M−s, error 2M−3s, and the forcing H(a)+Kv with leading minus sign all match the source. |
| Analytic regularity | Polynomial induction establishes the actual strict derivative. Augmentation gives [[J,K],[0,I]], its inverse gives −J⁻¹K, and the local inverse yields genuinely open U,V with an exact root graph. Integral data are included into Qp; Zp is never treated as a Qp vector space. Continuous supplied selections inherit the same germ. |
| Native boundaries | Changing representatives is distinguished from changing presentations. Appending a zero equation changes the raw cokernel. The shared quotient assumes an actual common correction module. The dense proper integer diagonal is correctly excluded as a continuous equality locus over a Hausdorff target. |

The corresponding dependency chains are: actual coefficient construction → difference estimates → displacement theorem; finite prefix plus universal envelope → Newton dominance → least periods; actual polynomial Taylor expansion → obstruction → compatible tower; inverse certificate → contraction → quantitative motion; actual strict derivative → analytic inverse → local root graph → supplied-selection regularity. No capstone was used as a hypothesis of its own proof summary.

## Findings corrected before freeze

1. The arithmetic inverse series now uses `mathcal P`, distinct from the residue-selector notation P.
2. The nonsingular Riccati propagation paragraph now requires 2≤c<N. The standard window supplies R₁, avoiding an undefined R₀.
3. The local graph proof now explicitly uses the source of the augmented map Φ, whose inverse is g. Its neighborhood is therefore correctly centered at a.

These were exposition corrections. No inherited mathematical Lean source changed.

## Evidence and computation checks

An independent invocation of the supplied evidence-index checker passed: **644 source-hash comparisons and 713 retained-log hash comparisons**. Four older affine logs have no prior digests and were fingerprinted only. The 1,876 declaration rows distinguish source versions and are not a global theorem count.

The four section maps were also resolved directly against nested ZIP members or direct source files. Provided hashes and declared names matched. Every labeled mathematical statement is mapped. This establishes source identity and coverage, not the mathematical truth of a statement by itself.

Exact rational recurrence calculations through packet row six independently reproduced every finite valuation displayed for the four-address Newton prefix. Small residue calculations confirmed the X²−5 and X²+3 obstruction examples. The linear joint control has τ=4 and root −8, while omission or sign reversal of K gives errors −4 and −8, neither divisible by sixteen. These are bounded controls; the universal statements rely on the archived proofs.

The local pinned Mathlib sources were inspected for the analytic inverse and Bernoulli valuation interfaces. Their field, completeness, nonzero and divisibility hypotheses match the uses in the manuscript.

Two preliminary JSON-inspection snippets failed because they assumed uniform record shapes. The final check handled both direct-file and nested-ZIP records and passed. This did not alter mathematical sources or claimed results.

## Verification and access limits

The latest 91-check release concerns the polynomial regularity frontier. It does not freshly rebuild the older arithmetic development. Consolidation preserves earlier successful reports and exact source identities. Overlapping frontier counts are not added. Stale strengthening inventory summary scalars are disclosed, while actual entries and the corresponding 246-name audit remain the reporting basis.

The external Nishibuchi statement comparison rests on the preserved audit of arXiv:2605.10677v2 and its recorded hashes. Fresh official-source retrieval was blocked in the parent access attempt. The full external paper is not redistributed here. The manuscript explicitly distinguishes this limitation from compiler acceptance of unchanged sources. No priority or novelty conclusion is made.

The final PDF is fingerprinted in the JSON to bind it to the reviewed TeX. Visual layout inspection belongs to the parent consolidation check, not this mathematical review. The three current release documents were also scope-checked: their proved/open boundaries, statement-count terminology and verification disclosures agree with the manuscript. Final ZIP preservation and file placement belong to the assembler gate.

## Remaining work

No unresolved correction is required for the consolidated statements reviewed here. General fraction-field singular persistence, the full Native13.2/13.3 program, higher exact arithmetic, historical recovery, and explicit interfaces to some older subtype-valued charts remain open as stated. Their missing implications are not supplied by the verification counts. The cheapest required follow-up after any later mathematical edit is a focused correspondence review of the changed statement and its dependencies, followed by refreshed hashes.
